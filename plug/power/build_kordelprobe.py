#!/usr/bin/env python3
"""Probeteil K4 Kordelprobe (Mitte des Unterkastens Stand 8): STL, README, ZIP, Prüfbericht und Bilder nach stl/steckmodul_kordelprobe/.

Teile (Druckausrichtung, Boden auf dem Bett):
  K4_scheibe.stl       Scheibe Ø 70 × 6,2: Boden 1,2, Teller Ø 54,4 bis 2,6, Knopfraum Radius 26 × 1,4 mit 45°-Wand, acht Höcker 10,4 breit
                       mit Gängen 8 × 5 (obere Kanten 1,5 × 45°) bis zum Rand, Ring 2,4 breit mit dem Dach über den Gängen; Geometrie wie im Kasten
  K4_deckplatte.stl    Platte 70 × 70 × 3, flach: liegt auf den Höckern und steht für Steckplatte und Powerbank, die auf die Kordel gelegt werden
Prüft am echten Hut (Knopf Ø 22 × 1,2, Kordel 3 × 5): Knopf im Raum, Kordel in jedem der acht Gänge, Brücken ohne Support, Auflegen und Kleben.
Plan: plug/power/plan_kasten8.html (Abschnitt K4); Werte in plug/power/params.py, Geometrie in plug/power/kasten8.py.
Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m plug.power.build_kordelprobe
"""
import os
import zipfile

import manifold3d as m3d
from shapely import affinity
from shapely.geometry import Point, box as sbox
from shapely.ops import unary_union

import generate as G
from plug.fit_test.generator import overhangs
from plug.geom import box as mbox
from plug.geom import to_bed, to_tm, vol_int
from plug.power import build_concept as BC
from plug.power import kasten8 as K8
from plug.power import params as PP

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(HERE, "stl", "steckmodul_kordelprobe")
PREV = os.path.join(HERE, "vorschau", "steckmodul_kordelprobe")
D = 70.0                      # Scheibe Ø 70
WALL = PP.UK_WALL             # Ring wie die Außenwand des Kastens
H = K8.GANG_Z                 # Höhe 6,2 = Oberkante der Höcker
PLATE = (70.0, 70.0, 3.0)     # Deckplatte
CH = PP.CH_BED


class Report:
    def __init__(self):
        self.lines = []

    def __call__(self, s=""):
        print(s)
        self.lines.append(s)


def scheibe():
    """Scheibe wie ein Ausschnitt des Kastens: Boden und Ring wie die Wand, Teller, Höcker, Knopfraum und Gänge ausgeschnitten."""
    c = (0.0, 0.0)
    outline = Point(c).buffer(D / 2, 128)
    inner = outline.buffer(-WALL)
    kuppel = Point(c).buffer(K8.R_KNOPF + PP.KORDEL_DACH, 128).intersection(inner)
    hw = PP.KORDEL_GANG["w"] / 2 + PP.KORDEL_DACH
    hoecker = G.union([G.extrude(sbox(0, -hw, D, hw).intersection(inner), PP.UK_FLOOR - 0.01, H).rotate([0, 0, k * 45.0]) for k in range(8)])
    shell = BC.slab_ch(outline, 0, H, CH) - G.extrude(inner, PP.UK_FLOOR, H + 1)
    solid = G.union([shell, G.extrude(kuppel, PP.UK_FLOOR - 0.01, K8.KNOPF_Z), hoecker])
    gc = K8.gaenge_cut(c, PP.KORDEL_GANG["w"], PP.KORDEL_GANG["h"], PP.KORDEL_GANG["fase"], PP.KORDEL_GANG["n"], laenge=D / 2 + 2)
    kc = K8.knopf_cut(c, K8.R_KNOPF, K8.KNOPF_H)
    strips = unary_union([affinity.rotate(sbox(0, -PP.KORDEL_GANG["w"] / 2, D, PP.KORDEL_GANG["w"] / 2), k * 45.0, origin=(0, 0)) for k in range(8)])
    mouth = BC.mouth_ch(unary_union([Point(c).buffer(K8.R_KNOPF), strips]), 0, CH)
    return solid - G.union([kc, gc, mouth]), gc, kc, mouth


def deckplatte():
    return BC.slab_ch(sbox(-PLATE[0] / 2, -PLATE[1] / 2, PLATE[0] / 2, PLATE[1] / 2), 0, PLATE[2], CH)


def main():
    rep = Report()
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(PREV, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith((".stl", ".zip", ".txt")):
            os.remove(os.path.join(OUT, f))
    sch, gc, kc, _ = scheibe()
    plate = deckplatte()
    parts = {"K4_scheibe": sch, "K4_deckplatte": plate}
    rep("Probeteil K4 Kordelprobe: Scheibe Ø %.0f × %.1f, Deckplatte %.0f × %.0f × %.0f" % (D, H, *PLATE))
    rep("Maße: Knopfraum Radius %.0f (Ø %.0f) × %.1f mit 45°-Wand, Knopf Ø %.0f × %.1f, Gänge %.0f × %.0f mit Fase %.1f, Kordel %.0f × %.0f, Teller bis %.1f, Höcker %.1f hoch" % (
        K8.R_KNOPF, 2 * K8.R_KNOPF, K8.KNOPF_H, PP.HUT_KNOPF["d"], PP.HUT_KNOPF["h"], PP.KORDEL_GANG["w"], PP.KORDEL_GANG["h"], PP.KORDEL_GANG["fase"],
        PP.KORDEL["b"], PP.KORDEL["h"], K8.KNOPF_Z, H))
    rep("\nTeile (Druckausrichtung, Bett z = 0):")
    info = {}
    bad = 0
    for name, man in parts.items():
        tm = to_tm(man)
        tm.export(os.path.join(OUT, name + ".stl"))
        g, nl = BC.grams(man)[0], int(round(tm.extents[2] / 0.2))
        comps = len(man.decompose())
        ov = overhangs(man, name)
        info[name] = dict(g=g, layers=nl)
        ok = bool(tm.is_watertight) and comps == 1
        bad += not ok
        rep("  %-18s %5.1f × %5.1f × %4.1f mm  %5.1f cm³  ≈ %2.0f g  dicht=%s  Teile=%d" % (name + ".stl", *tm.extents, tm.volume / 1000.0, g, tm.is_watertight, comps))
        rep("      waagerechte Decken: %s   Überhang flacher als 45° zur Senkrechten: %.0f mm²" % (
            "; ".join("z=%.1f: %.0f mm² (%.1f × %.1f)" % f for f in sorted(ov["flat"], key=lambda t: -t[1])[:5]) or "keine", ov["steep_area"]))

    rep("\nPrüfung (Überschneidungsvolumen, mm³; muss 0 sein):")

    def chk(txt, val, limit=0.05):
        nonlocal bad
        ok = val < limit
        bad += not ok
        rep("  %-62s %8.2f  %s" % (txt, val, "ok" if ok else "FEHLER"))

    kn = PP.HUT_KNOPF
    knopf = m3d.Manifold.cylinder(kn["h"], kn["d"] / 2, kn["d"] / 2, 64)
    chk("Knopf Ø %.0f × %.1f im Knopfraum (Luft oben %.1f)" % (kn["d"], kn["h"], kn["luft"]), vol_int(knopf, sch))
    cb, ch_ = PP.KORDEL["b"], PP.KORDEL["h"]
    kord = G.union([K8.prism_y_x([(-cb / 2, 0.05), (cb / 2, 0.05), (cb / 2, ch_), (-cb / 2, ch_)], 0.0, D / 2 - 0.1).rotate([0, 0, k * 45.0]) for k in range(8)])
    chk("Kordel %.0f × %.0f in allen 8 Gängen bis zum Rand" % (cb, ch_), vol_int(kord, sch))
    chk("Gangprofil (8 × 5 mit Fase) frei", vol_int(K8.gaenge_cut((0.0, 0.0), PP.KORDEL_GANG["w"] - 0.04, PP.KORDEL_GANG["h"] - 0.04, PP.KORDEL_GANG["fase"], 8, z0=0.01, laenge=D / 2 - 0.1), sch))
    ow, oa, oz = K8.ueberhang(sch, zmax=H)
    rep("  Überhang je 0,2-mm-Lage (45° getragen): breiteste freie Decke %.1f mm (Sternmitte), Gangdecken 5,0 mm" % ow)
    if ow > 15.0:
        bad += 1
    # Deckplatte liegt auf den Höckern: Kontakt, keine Überschneidung
    lieg = plate.translate([0, 0, H])
    chk("Deckplatte auf den Höckern (liegt nur auf)", vol_int(lieg, sch))
    rep("  Deckplatte über den Gängen: Luft für die Kordel %.1f mm hoch (Gang %.1f, Kordel %.1f)" % (PP.KORDEL_GANG["h"] - PP.KORDEL["h"], PP.KORDEL_GANG["h"], PP.KORDEL["h"]))
    rep("  -> %s" % ("keine Kollisionen" if not bad else "%d Fehler!" % bad))

    from plug.roadmap import build as rb
    for name in info:
        for prof, pr in rb.PROFILE.items():
            mins = info[name]["g"] / pr["rate"] * 60.0 + info[name]["layers"] * pr["layer"] / 60.0 + pr["start"]
            rep("%s: Material ≈ %.0f g, Zeit %s ≈ %.0f min" % (name, info[name]["g"], prof, mins))
    for name in info:
        rep("%s bei deinem Drucker (Nacht 1: 47 g in 2,5 h) ≈ %.0f min" % (name, info[name]["g"] / 47.0 * 2.5 * 60))
    with open(os.path.join(OUT, "pruefbericht.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(rep.lines) + "\n")
    write_readme(info)
    zpath = os.path.join(OUT, "kordelprobe.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(os.listdir(OUT)):
            if f.endswith(".stl") or f == "README.txt":
                z.write(os.path.join(OUT, f), f)
    rep("%s: %.0f kB" % (os.path.relpath(zpath, HERE), os.path.getsize(zpath) / 1024))
    images()
    return bad


def images():
    """Bilder mit dem Software-Renderer: Scheibe schräg und von unten, Scheibe mit Deckplatte."""
    import subprocess
    import sys
    py = sys.executable
    base = os.path.join(OUT, "K4_scheibe.stl")
    out = PREV
    subprocess.run([py, "preview.py", base, "--azim", "-60", "--elev", "40", "--out", out], cwd=HERE, check=False)
    subprocess.run([py, "preview.py", base, "--azim", "-60", "--elev", "-55", "--out", out + "/unten"], cwd=HERE, check=False)


def write_readme(info):
    txt = """K4 KORDELPROBE (Mitte des Unterkastens, Stand 8)
================================================
Probeteil zum Plan plug/power/plan_kasten8.html (Abschnitt K4). Noch nichts gedruckt, alle Werte sind Planwerte.

Teile:
  K4_scheibe.stl      Scheibe Ø 70 x 6,2 mm, Boden auf das Bett, kein Support (siehe pruefbericht.txt)     ca. %(s).0f g
  K4_deckplatte.stl   Platte 70 x 70 x 3 mm, flach, Unterseite auf das Bett                                  ca. %(d).0f g

Was die Scheibe zeigt: Knopfraum Radius 26 (Ø 52) x 1,4 mit 45-Grad-Wand, acht Gänge 8 x 5 mm mit 1,5 x 45-Grad-Fasen an den oberen Kanten
(Decke 5 mm breit), Höcker 10,4 mm breit, Ring wie die Außenwand. Der Knopf des Huts (Ø 22 x 1,2) soll im Raum sitzen, die Kordel (3 x 5 mm)
in jeden der acht Gänge passen.

Ablauf:
  1. Scheibe über den Knopf auf den Hut legen (Mitte auf Mitte), Kordel in einen Gang legen, Scheibe ankleben (Heißkleber auf dem Boden
     zwischen den Gängen, nicht in die Gänge und nicht in den Knopfraum).
  2. Deckplatte auf die Höcker legen: so wie später Steckplatte und Powerbank auf die Kordel. Lässt sich die Kordel noch bewegen?
  3. Kordel nacheinander in mehrere andere Gänge legen (O, NO, N ...), jedes Mal ohne zu klemmen?
Fragen für den Testbogen: Sitzt der Knopf im Raum? Berührt die Decke in der Sternmitte (etwa 13 mm frei) den Knopf, hängt sie durch?
Ist die Gangdecke sauber, die Fase oben und unten gut? Hält Heißkleber? Ist die Kordel zu steif für den Knick am Gangausgang?

Druck: PLA, 0,2 mm Schicht, Support aus, Gyroid 10 %% wie plug/slicer.md. Zeiten im Prüfbericht (Schätzung): Scheibe etwa 35 min, Deckplatte etwa 45 min (fast massiv) bei deinem Drucker.
"""
    open(os.path.join(OUT, "README.txt"), "w", encoding="utf-8").write(txt % dict(s=info["K4_scheibe"]["g"], d=info["K4_deckplatte"]["g"]))


if __name__ == "__main__":
    raise SystemExit(main())
