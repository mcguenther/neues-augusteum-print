#!/usr/bin/env python3
"""Probeteil K4 Kordelprobe (Mitte des Unterkastens Stand 8): STL, README, ZIP, Prüfbericht und Bilder nach stl/steckmodul_kordelprobe/.

Teil (Druckausrichtung: Bett unten = Hut-Seite, Erhebung nach oben):
  K4_stern_F-aussen.stl, K4_stern_F-innen.stl   Stern Ø 70 aus acht Höckern mit den Gängen (F-aussen: freies Rechteck 8 × 4, darüber 45°-Dachschrägen 1,5,
                  Höcker 11,4 × 7,7; F-innen: Fase 1,5 in den oberen Ecken, Höcker 10,4 × 6,2), in der Mitte die Erhebung über dem Knopf: Hohlraum am Bett Ø 39,4 auf Gang-Höhe, ab 8,7 mm vor dem
                  Knopfkörper 45°-Anstieg, Knopfraum Ø 25 × 13,0 frei (1 mm Luft über dem Knopf), flache Decke Ø 20 bei 15,5, Plateau Ø 28 bei 16,0.
                  Ohne Boden, Randwand und Deckplatte: nur das, was die Kordel und der Knopf brauchen; Geometrie wie im Kasten.
Prüft am echten Hut (Knopf Ø 22 × 12,0, Höhe noch Annahme; Kordel 3 × 5): Knopf im Raum, Kordel vom Knopffuß in jeden der acht Gänge,
Decken ohne Support, Kleben. Plan: plug/power/plan_kasten8.html (Abschnitt K4); Werte in plug/power/params.py, Geometrie in plug/power/kasten8.py.
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
H = K8.KNOPF_Z                # Höhe 15,9 = Plateau der Erhebung (Höcker 7,7)
CH = PP.CH_BED


class Report:
    def __init__(self):
        self.lines = []

    def __call__(self, s=""):
        print(s)
        self.lines.append(s)


def stern():
    """Stern wie ein Ausschnitt des Kastens, aber ohne Boden und Ring: acht Höcker, Erhebung über dem Knopf, Hohlraum und Gänge ausgeschnitten."""
    c = (0.0, 0.0)
    hw = K8.GANG_W / 2 + K8.WAND
    hoecker = G.union([G.extrude(sbox(0, -hw, D / 2, hw), 0.0, K8.GANG_Z).rotate([0, 0, k * 45.0]) for k in range(8)])
    solid = G.union([K8.erhebung_solid(c, 0.0), hoecker])
    gc = K8.gaenge_cut(c, K8.GANG_W, K8.GANG_H, K8.FASE, PP.KORDEL_GANG["n"], laenge=D / 2 + 2)
    kc = K8.knopf_cut(c)
    strips = unary_union([affinity.rotate(sbox(0, -K8.GANG_W / 2, D, K8.GANG_W / 2), k * 45.0, origin=(0, 0)) for k in range(8)])
    mouth = BC.mouth_ch(unary_union([Point(c).buffer(K8.R_RAMPE, 128), strips]), 0, PP.CH_MUENDUNG) if PP.CH_MUENDUNG > 0 else None
    return solid - G.union([x for x in (kc, gc, mouth) if x is not None])


NAME = {"innen": "K4_stern_F-innen", "aussen": "K4_stern_F-aussen"}
ERST = "aussen"               # zuerst drucken: Rechteck 8 × 4 ganz frei, kostet am Kasten keine Höhe


def main():
    rep = Report()
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(PREV, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith((".stl", ".zip", ".txt")):
            os.remove(os.path.join(OUT, f))
    for d in (PREV, os.path.join(PREV, "unten")):
        if os.path.isdir(d):
            for f in os.listdir(d):
                if f.startswith("K4_stern") and f.endswith(".png"):
                    os.remove(os.path.join(d, f))
    rep("Probeteil K4 Kordelprobe: Stern Ø %.0f × %.1f (Gangfase %s), ohne Boden, Randwand und Deckplatte, ohne Fase an den Mündungen; Bett unten (Hut-Seite)" % (D, H, PP.GANG_FASE_MODUS))
    rep("Maße: Knopf Ø %.0f × %.1f (Höhe Annahme, vom Nutzer zu bestätigen), Kordel %.0f × %.0f unten seitlich am Knopffuß; Knopfraum Ø %.0f × %.1f, Anstieg 45° ab Radius %.1f (%.1f vor dem Knopfkörper), Decke Ø %.0f bei %.1f, Plateau Ø %.0f bei %.1f" % (
        PP.HUT_KNOPF["d"], PP.HUT_KNOPF["h"], PP.KORDEL["b"], PP.KORDEL["h"], 2 * K8.R_RAUM, K8.H_RAUM, K8.R_RAMPE, K8.R_RAMPE - K8.R_KN, 2 * K8.R_DECKE, K8.KNOPF_TOP, 2 * K8.R_PLATEAU, K8.KNOPF_Z))
    info = {}
    bad = 0
    kn = PP.HUT_KNOPF
    cb, ch_ = PP.KORDEL["b"], PP.KORDEL["h"]

    def chk(txt, val, limit=0.05):
        nonlocal bad
        ok = val < limit
        bad += not ok
        rep("  %-66s %8.2f  %s" % (txt, val, "ok" if ok else "FEHLER"))

    def kord(z0, z1, r0, r1):
        return G.union([K8.prism_y_x([(-cb / 2, z0), (cb / 2, z0), (cb / 2, z1), (-cb / 2, z1)], r0, r1).rotate([0, 0, k * 45.0]) for k in range(8)])

    for m in (PP.GANG_FASE_MODUS,):
        K8.modus(m)
        name = NAME[m]
        sch = stern()
        rep("\n%s (Gangfase %s)" % (name + ".stl", m))
        if m == "aussen":
            rep("  Gänge: freies Rechteck %.0f × %.0f, Dachschrägen %.1f × 45° darüber (Decke %.0f breit bei %.1f), Höcker %.1f breit und %.1f hoch, Wand seitlich %.1f" % (
                K8.GANG_W, K8.GANG_H, K8.FASE, K8.GANG_W - 2 * K8.FASE, K8.GANG_H + K8.FASE, K8.GANG_W + 2 * K8.WAND, K8.GANG_Z, K8.WAND))
        else:
            rep("  Gänge: %.0f × %.0f mit Fase %.1f × 45° in den oberen Ecken (Decke %.0f breit bei %.1f), Höcker %.1f breit und %.1f hoch, Wand seitlich %.1f" % (
                K8.GANG_W, K8.GANG_H, K8.FASE, K8.GANG_W - 2 * K8.FASE, K8.GANG_H, K8.GANG_W + 2 * K8.WAND, K8.GANG_Z, K8.WAND))
        tm = to_tm(sch)
        tm.export(os.path.join(OUT, name + ".stl"))
        g, nl = BC.grams(sch)[0], int(round(tm.extents[2] / 0.2))
        comps = len(sch.decompose())
        ov = overhangs(sch, name)
        ok = bool(tm.is_watertight) and comps == 1
        bad += not ok
        rep("  %5.1f × %5.1f × %4.1f mm  %5.1f cm³  ≈ %2.0f g  dicht=%s  Teile=%d" % (*tm.extents, tm.volume / 1000.0, g, tm.is_watertight, comps))
        rep("  waagerechte Decken: %s   Überhang flacher als 45° zur Senkrechten: %.0f mm²" % (
            "; ".join("z=%.1f: %.0f mm²" % f[:2] for f in sorted(ov["flat"], key=lambda t: -t[1])[:4]) or "keine", ov["steep_area"]))
        knopf = m3d.Manifold.cylinder(kn["h"], kn["d"] / 2, kn["d"] / 2, 64)
        chk("Knopf Ø %.0f × %.1f im Raum (seitlich %.1f, oben %.1f Luft)" % (kn["d"], kn["h"], K8.R_RAUM - K8.R_KN, K8.H_RAUM - kn["h"]), vol_int(knopf, sch))
        raum = m3d.Manifold.cylinder(K8.H_RAUM - 0.03, K8.R_RAUM - 0.02, K8.R_RAUM - 0.02, 96).translate([0, 0, 0.01])
        chk("Knopfraum Ø %.0f × %.1f frei" % (2 * K8.R_RAUM, K8.H_RAUM), vol_int(raum, sch))
        chk("Kordel %.0f × %.0f vom Knopffuß in allen 8 Gängen bis zum Rand" % (cb, ch_), vol_int(kord(0.05, ch_, K8.R_KN, D / 2 - 0.1), sch))
        rect = vol_int(K8.gaenge_cut((0.0, 0.0), K8.GANG_W - 0.04, K8.GANG_H - 0.02, 0.0, 8, z0=0.01, laenge=D / 2 - 0.1), sch)
        if m == "aussen":
            chk("volles Rechteck %.0f × %.0f frei in allen 8 Gängen" % (K8.GANG_W, K8.GANG_H), rect)
        else:
            chk("Gangprofil %.0f × %.0f mit Fase %.1f frei" % (K8.GANG_W, K8.GANG_H, K8.FASE),
                vol_int(K8.gaenge_cut((0.0, 0.0), K8.GANG_W - 0.04, K8.GANG_H - 0.02, K8.FASE - 0.02, 8, z0=0.01, laenge=D / 2 - 0.1), sch))
            rep("  (volles Rechteck 8 × 4 nicht frei: die gefasten Ecken nehmen %.0f mm³ weg, die Kordel passt trotzdem)" % rect)
        det = []
        ow, oa, oz = K8.ueberhang(sch, zmax=H + 0.3, detail=det)
        br = K8.brueckenbereiche(det, (0.0, 0.0))
        rep("  Überhang je 0,2-mm-Lage (45° getragen): breiteste freie Decke %.1f mm (höchstens 20); %s" % (ow, "; ".join("%s %.1f mm bei z %.1f" % t for t in br)))
        if ow > 20.0:
            bad += 1
        info[name] = dict(g=g, layers=nl, gz=K8.GANG_Z, wand=K8.WAND, bruecke=ow, br=br)
    K8.modus(PP.GANG_FASE_MODUS)
    rep("\nWände: seitlich %.1f, Decke über Gängen und Knopfraum %.2f (3 Lagen × 0,16), keine Fase unten an den Mündungen; Powerbank oder Buch auf dem Plateau lässt die Kordel frei" % (PP.KORDEL_WAND, PP.KORDEL_DACH))
    rep("-> %s" % ("keine Kollisionen" if not bad else "%d Fehler!" % bad))

    from plug.roadmap import build as rb
    for name in info:
        t = ", ".join("%s ≈ %.0f min" % (prof, info[name]["g"] / pr["rate"] * 60.0 + info[name]["layers"] * pr["layer"] / 60.0 + pr["start"]) for prof, pr in rb.PROFILE.items())
        rep("%s: Material ≈ %.0f g, Zeit %s, bei deinem Drucker (Nacht 1: 47 g in 2,5 h) ≈ %.0f min" % (name, info[name]["g"], t, info[name]["g"] / 47.0 * 2.5 * 60))
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
    """Bilder mit dem Software-Renderer: beide Sterne schräg von oben und von unten."""
    import subprocess
    import sys
    for name in (NAME[PP.GANG_FASE_MODUS],):
        base = os.path.join(OUT, name + ".stl")
        subprocess.run([sys.executable, "preview.py", base, "--azim", "-60", "--elev", "40", "--out", PREV], cwd=HERE, check=False)
        subprocess.run([sys.executable, "preview.py", base, "--azim", "-60", "--elev", "-55", "--out", PREV + "/unten"], cwd=HERE, check=False)


def write_readme(info):
    i = info[NAME[PP.GANG_FASE_MODUS]]
    txt = """K4 KORDELPROBE (Mitte des Unterkastens, Stand 8)
================================================
Probeteil zum Plan plug/power/plan_kasten8.html (Abschnitt K4). Noch nichts gedruckt, alle Werte sind Planwerte.

Teil: K4_stern_F-innen.stl, Stern Ø 70 x %(h).1f mm, ohne Boden und ohne Randwand, Bett unten = Hut-Seite, kein Support (siehe pruefbericht.txt)   ca. %(g).0f g
Gänge 8 x 4 mit Fase 1,5 in den oberen Ecken (Decke 5 breit bei 4,0; die Kordel 5 x 3 passt, 1 mm Luft in der Höhe), Wand 0,8, Decke 3 Lagen
x 0,16 = 0,48, keine Fase unten an den Mündungen. In der Mitte die Erhebung für den Knopf: am Hut ein Hohlraum Ø 43 auf Gang-Höhe 4, ab 10,5 mm
vor dem Knopf steigt die Decke mit 45 Grad an, der Knopfraum Ø 25 x 13,0 (1 mm Luft über dem Knopf) ist überall frei (nichts davon beschnitten), oben eine flache Decke
Ø 20 bei 15,5, darüber das Plateau Ø 28 bei %(pz).1f. Annahme: Knopf Ø 22 x 12 mm hoch (bitte nachmessen); die Kordel 3 x 5 kommt unten
seitlich am Knopffuß heraus.

Ablauf:
  1. Stern mit der Mitte über den Knopf setzen, Kordel vom Knopffuß in einen Gang legen.
  2. Stern mit Heißkleber auf dem Hut ankleben (nur auf die Unterseite der Höcker, nicht in die Gänge und nicht in die Mitte).
  3. Powerbank (oder ein Buch) auf das Plateau legen: drückt es auf den Knopf? Lässt sich die Kordel noch bewegen?
  4. Kordel nacheinander in andere Gänge legen (O, NO, N ...), jedes Mal ohne zu klemmen?
Fragen für den Testbogen: Wie hoch ist der Knopf wirklich (12 mm?), passt er in den Raum (1,5 mm Luft je Seite, 1 mm oben)? Hält die dünne
Decke (0,48) und hängt die Decke über dem Knopf (etwa 20 mm frei) durch? Sind Gangdecken und Fasen sauber? Halten die Wände mit 0,8?
Hält Heißkleber? Ist die Kordel zu steif für den Knick am Gangausgang?

Druck: PLA, 0,16 mm Schicht, Support aus, Gyroid 10 %% wie plug/slicer.md, Bett unten wie in der Datei (Erhebung oben).
"""
    open(os.path.join(OUT, "README.txt"), "w", encoding="utf-8").write(txt % dict(g=i["g"], h=K8.KNOPF_Z, pz=K8.KNOPF_Z))


if __name__ == "__main__":
    raise SystemExit(main())
