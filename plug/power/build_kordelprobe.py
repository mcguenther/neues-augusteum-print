#!/usr/bin/env python3
"""Probeteil K4 Kordelprobe (Mitte des Unterkastens Stand 8): STL, README, ZIP, Prüfbericht und Bilder nach stl/steckmodul_kordelprobe/.

Teil (Druckausrichtung, Dach nach oben, Bett unten):
  K4_stern.stl    Stern aus acht Höckern 10,4 breit und 6,2 hoch mit den Gängen 8 × 5 (obere Kanten 1,5 × 45°), in der Mitte der Knopfraum
                  (Ø 25, Wand senkrecht bis 1,4, darüber 45° bis 5, Dach Ø 18). Ohne Boden und ohne Randwand: nur das, was die Kordel
                  und der Knopf brauchen; Geometrie wie im Kasten. Eine Deckplatte entfällt: zum Auflegen taugt die Powerbank selbst.
Prüft am echten Hut (Knopf Ø 22 × 1,2, Kordel 3 × 5): Knopf im Raum, Kordel auf dem Knopf und in jedem der acht Gänge, Brücken ohne Support, Kleben.
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
D = 70.0                      # Stern Ø 70 (Gänge 35 mm vom Mittelpunkt)
H = K8.GANG_Z                 # Höhe 6,2 = Oberkante der Höcker
CH = PP.CH_BED


class Report:
    def __init__(self):
        self.lines = []

    def __call__(self, s=""):
        print(s)
        self.lines.append(s)


def stern():
    """Stern wie ein Ausschnitt des Kastens, aber ohne Boden und Ring: Dach über dem Knopfraum, acht Höcker, Knopfraum und Gänge ausgeschnitten."""
    c = (0.0, 0.0)
    hw = PP.KORDEL_GANG["w"] / 2 + PP.KORDEL_DACH
    kuppel = Point(c).buffer(K8.R_KNOPF + PP.KORDEL_DACH, 128)
    hoecker = G.union([G.extrude(sbox(0, -hw, D / 2, hw), 0.0, H).rotate([0, 0, k * 45.0]) for k in range(8)])
    solid = G.union([G.extrude(kuppel, 0.0, H), hoecker])
    gc = K8.gaenge_cut(c, PP.KORDEL_GANG["w"], PP.KORDEL_GANG["h"], PP.KORDEL_GANG["fase"], PP.KORDEL_GANG["n"], laenge=D / 2 + 2)
    kc = K8.knopf_cut(c, K8.R_KNOPF, K8.KNOPF_H)
    strips = unary_union([affinity.rotate(sbox(0, -PP.KORDEL_GANG["w"] / 2, D, PP.KORDEL_GANG["w"] / 2), k * 45.0, origin=(0, 0)) for k in range(8)])
    mouth = BC.mouth_ch(unary_union([Point(c).buffer(K8.R_KNOPF), strips]), 0, CH)
    return solid - G.union([kc, gc, mouth])


def main():
    rep = Report()
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(PREV, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith((".stl", ".zip", ".txt")):
            os.remove(os.path.join(OUT, f))
    sch = stern()
    parts = {"K4_stern": sch}
    rep("Probeteil K4 Kordelprobe: Stern Ø %.0f × %.1f, ohne Boden und ohne Randwand" % (D, H))
    rep("Maße: Knopfraum Radius %.1f (Ø %.0f), Wand senkrecht bis %.1f, 45° bis %.1f (Dach Ø %.0f), Knopf Ø %.0f × %.1f, Gänge %.0f × %.0f mit Fase %.1f, Kordel %.0f × %.0f, Höcker %.1f breit und %.1f hoch" % (
        K8.R_KNOPF, 2 * K8.R_KNOPF, K8.KNOPF_H0, K8.KNOPF_H, 2 * (K8.R_KNOPF - (K8.KNOPF_H - K8.KNOPF_H0)), PP.HUT_KNOPF["d"], PP.HUT_KNOPF["h"],
        PP.KORDEL_GANG["w"], PP.KORDEL_GANG["h"], PP.KORDEL_GANG["fase"], PP.KORDEL["b"], PP.KORDEL["h"], PP.KORDEL_GANG["w"] + 2 * PP.KORDEL_DACH, H))
    rep("\nTeil (Druckausrichtung, Bett z = 0):")
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
    chk("Knopf Ø %.0f × %.1f im Knopfraum (seitlich %.1f, oben %.1f Luft)" % (kn["d"], kn["h"], K8.R_KNOPF - kn["d"] / 2, K8.KNOPF_H0 - kn["h"]), vol_int(knopf, sch))
    cb, ch_ = PP.KORDEL["b"], PP.KORDEL["h"]
    kord = G.union([K8.prism_y_x([(-cb / 2, 0.05), (cb / 2, 0.05), (cb / 2, ch_), (-cb / 2, ch_)], 0.0, D / 2 - 0.1).rotate([0, 0, k * 45.0]) for k in range(8)])
    chk("Kordel %.0f × %.0f in allen 8 Gängen bis zum Rand" % (cb, ch_), vol_int(kord, sch))
    kord_kn = G.union([K8.prism_y_x([(-cb / 2, kn["h"]), (cb / 2, kn["h"]), (cb / 2, kn["h"] + ch_), (-cb / 2, kn["h"] + ch_)], 0.0, D / 2 - 0.1).rotate([0, 0, k * 45.0]) for k in range(8)])
    chk("Kordel auf dem Knopf (bis %.1f hoch) und weiter in allen 8 Gängen" % (kn["h"] + ch_), vol_int(kord_kn, sch))
    chk("Gangprofil (8 × 5 mit Fase) frei", vol_int(K8.gaenge_cut((0.0, 0.0), PP.KORDEL_GANG["w"] - 0.04, PP.KORDEL_GANG["h"] - 0.04, PP.KORDEL_GANG["fase"], 8, z0=0.01, laenge=D / 2 - 0.1), sch))
    ow, oa, oz = K8.ueberhang(sch, zmax=H)
    rep("  Überhang je 0,2-mm-Lage (45° getragen): breiteste freie Decke %.1f mm (Dach über dem Knopfraum), Gangdecken 5,0 mm" % ow)
    if ow > 20.0:
        bad += 1
    rep("  Platte oder Powerbank auf den Höckern: Luft für die Kordel %.1f mm hoch (Gang %.1f, Kordel %.1f)" % (PP.KORDEL_GANG["h"] - PP.KORDEL["h"], PP.KORDEL_GANG["h"], PP.KORDEL["h"]))
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
    """Bilder mit dem Software-Renderer: Stern schräg von oben und von unten."""
    import subprocess
    import sys
    base = os.path.join(OUT, "K4_stern.stl")
    subprocess.run([sys.executable, "preview.py", base, "--azim", "-60", "--elev", "40", "--out", PREV], cwd=HERE, check=False)
    subprocess.run([sys.executable, "preview.py", base, "--azim", "-60", "--elev", "-55", "--out", PREV + "/unten"], cwd=HERE, check=False)


def write_readme(info):
    txt = """K4 KORDELPROBE (Mitte des Unterkastens, Stand 8)
================================================
Probeteil zum Plan plug/power/plan_kasten8.html (Abschnitt K4). Noch nichts gedruckt, alle Werte sind Planwerte.

Teil:
  K4_stern.stl    Stern Ø 70 x 6,2 mm, ohne Boden und ohne Randwand, Dach nach oben, kein Support (siehe pruefbericht.txt)     ca. %(s).0f g

Was der Stern zeigt: acht Höcker 10,4 mm breit mit Gängen 8 x 5 mm (obere Kanten 1,5 x 45 Grad gefast, Decke 5 mm breit) und in der Mitte
der Knopfraum Ø 25 (Wand senkrecht bis 1,4, darüber 45 Grad bis 5, Dach Ø 18). Er ist so hoch wie die Gänge, damit die Kordel auf dem
Knopf (1,2 + 3 = 4,2) in jede Richtung wegführen kann. Der Knopf des Huts (Ø 22 x 1,2) soll im Raum sitzen.

Ablauf:
  1. Stern mit der Mitte auf den Knopf legen, Kordel vom Knopf in einen Gang legen.
  2. Stern mit Heißkleber auf dem Hut ankleben (nur auf die Unterseite der Höcker, nicht in die Gänge und nicht in den Knopfraum).
  3. Powerbank (oder ein Buch) auf die Höcker legen, wie später Steckplatte und Powerbank: lässt sich die Kordel noch bewegen?
  4. Kordel nacheinander in andere Gänge legen (O, NO, N ...), jedes Mal ohne zu klemmen?
Fragen für den Testbogen: Sitzt der Knopf im Raum (1,5 mm Luft je Seite)? Hängt das Dach über dem Knopfraum (etwa 18 mm frei) durch und
berührt die Kordel? Ist die Gangdecke sauber, sind die Fasen gut? Hält Heißkleber? Ist die Kordel zu steif für den Knick am Gangausgang?

Druck: PLA, 0,2 mm Schicht, Support aus, Gyroid 10 %% wie plug/slicer.md. Der Stern ist klein, ein paar Gramm und wenige Minuten.
"""
    open(os.path.join(OUT, "README.txt"), "w", encoding="utf-8").write(txt % dict(s=info["K4_stern"]["g"]))


if __name__ == "__main__":
    raise SystemExit(main())
