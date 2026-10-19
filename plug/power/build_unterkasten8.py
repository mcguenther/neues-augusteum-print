#!/usr/bin/env python3
"""Unterkasten (Batteriefach) Stand 8: STL, Prüfbericht, README, ZIP und Bilder nach stl/steckmodul_unterkasten8/.

Geometrie aus `plug/power/kasten8.py` (Erhebung über dem Knopf des Doktorhuts, acht Kordelgänge, Powerbank auf Plateau und eingeklebten Klötzen,
Steckerraum 6,0, Gangfase nach `GANG_FASE_MODUS`, Befestigung mit Heißkleber, keine Eckaussparungen). Der Umriss folgt der Steckplatte
(`build_concept.variant` mit den auseinandergerückten Gebäuden), deshalb wird hier zusätzlich die fertige Steckplatte
`stl/steckmodul_campus/steckplatte_1zu1300.stl` aufgesetzt und geprüft: gleicher Umriss, Zapfen in den Zapfenlöchern, Dockzonen der sechs
Gebäude und des Display-Docks frei vom Kasten. Stand 7 (`stl/steckmodul_unterkasten/`, gedruckt) bleibt unverändert.

Teile (Druckausrichtung = Einbaulage, Hut-Seite auf dem Bett):
  U8_unterkasten.stl   Kasten W × L × 34,8 mm (mit Zapfen 37,3), Gänge und Knopfraum unten offen, kein Support
  U8_auflage.stl       Klotz KLOTZ × KLOTZ × 14,8 (Boden 1,2 bis Plateauhöhe 16,0), drei bis vier Stück drucken; werden erst eingeklebt, wenn die Lage
                       der Powerbank feststeht (Nutzer 20.10., `PB_AUFLAGE["im_kasten"] = False`); Heißkleber nur seitlich, sonst wird der Klotz höher

Aufruf (aus dem Repo-Wurzelverzeichnis, ca. 30 s):
    python3 -m plug.power.build_unterkasten8
Erst `python3 -m plug.campus`, wenn sich die Steckplatte geändert hat.
"""
import os
import zipfile

import trimesh
from shapely.geometry import Polygon

from plug import campus_display as DP
from plug.geom import to_tm
from plug.power import kasten8 as K8
from plug.power import params as PP

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(HERE, "stl", "steckmodul_unterkasten8")
PREV = os.path.join(HERE, "vorschau", "steckmodul_unterkasten8")
PLATE = os.path.join(HERE, "stl", "steckmodul_campus", "steckplatte_1zu1300.stl")
NAME = "U8_unterkasten"
SPIEL_ZAPFEN = PP.PIN_PLAN["clr"]       # 0,15 Gleitspiel der Zapfen in den Zapfenlöchern
KLOTZ = 8.0                             # E  Kante der Auflage-Klötze (kleiner als die angeformten Auflagen bis 12 × 12: an der Stelle Nordost ist zwischen den Gängen nur 9,3 frei)


class Report:
    def __init__(self):
        self.lines = []

    def __call__(self, s=""):
        print(s)
        self.lines.append(s)


def vol(a, b):
    return float((a ^ b).volume())


def zusammenbau(r, rep):
    """Steckplatte auf den Kasten setzen und prüfen. Rückgabe (Anzahl Fehler, Platte als Manifold in Kastenkoordinaten, Zeilen (Text, ok, Wert))."""
    import generate as G
    uk, H = r["uk"], r["H"]
    plate_raw = DP.load_stl(PLATE)
    b = plate_raw.bounding_box()
    plate = plate_raw.translate([-b[0], -b[1], H - b[2]])          # Plattenkoordinaten (SW-Ecke 0), Unterseite auf der Oberkante des Kastens
    pw, pl = b[3] - b[0], b[4] - b[1]
    kb = uk.bounding_box()
    kw, kl = kb[3] - kb[0], kb[4] - kb[1]
    bad, rows = 0, []

    def chk(txt, ok, val):
        nonlocal bad
        bad += (not ok)
        rows.append((txt, bool(ok), val.strip()))
        rep("  %-86s %10s  %s" % (txt, val, "ok" if ok else "FEHLER"))

    rep("\nZusammenbau mit der Steckplatte (%s, %.2f × %.2f × %.2f mm):" % (os.path.relpath(PLATE, HERE), pw, pl, b[5] - b[2]))
    chk("Umriss Kasten %.2f × %.2f gegen Platte %.2f × %.2f (Abweichung höchstens 0,05)" % (kw, kl, pw, pl),
        abs(kw - pw) <= 0.05 and abs(kl - pl) <= 0.05 and abs(kb[0]) <= 0.05 and abs(kb[1]) <= 0.05, "%+.2f/%+.2f" % (kw - pw, kl - pl))
    v0 = vol(plate, uk)
    chk("Platte aufgesetzt, Zapfen in den Zapfenlöchern: Überschneidung (mm³)", v0 < 0.05, "%.3f" % v0)
    d = SPIEL_ZAPFEN * 0.6
    for dx, dy, txt in ((d, 0, "Osten"), (-d, 0, "Westen"), (0, d, "Norden"), (0, -d, "Süden")):
        vv = vol(plate.translate([dx, dy, 0]), uk)
        chk("Kontrolle: Platte %.2f nach %s verschoben, Zapfen haben noch Spiel (mm³)" % (d, txt), vv < 0.05, "%.3f" % vv)
    vv = vol(plate.translate([0.5, 0, 0]), uk)
    chk("Kontrolle: Platte 0,5 nach Osten verschoben stößt an die Zapfen (mm³, muss > 0)", vv > 0.05, "%.2f" % vv)
    vv = vol(plate.translate([0, 0, -0.2]), uk)
    chk("Kontrolle: Platte 0,2 tiefer stößt auf Wand und Stützen (mm³, muss > 0)", vv > 0.05, "%.0f" % vv)
    zonen = [(dk["title"], Polygon(dk["zone"])) for dk in r["docks"]] + [("Display-Dock", DP.dock_zone())]
    for name, z in zonen:
        vz = vol(G.extrude(z, H - DP.STECKERRAUM, H), uk)
        chk("Dockzone %s %.1f × %.1f (Steckerraum %.1f unter der Platte) frei vom Kasten (mm³)" % (
            name, z.bounds[2] - z.bounds[0], z.bounds[3] - z.bounds[1], DP.STECKERRAUM), vz < 0.05, "%.3f" % vz)
    return bad, plate, rows


def bilder(r, plate):
    import preview
    os.makedirs(PREV, exist_ok=True)
    tm = to_tm(r["uk"])
    preview.render([(tm, "#b9a98a")], size=(900, 1300), azim=-90, elev=89).save(os.path.join(PREV, NAME + "_oben.png"))
    preview.render([(tm, "#b9a98a")], size=(900, 1300), azim=90, elev=-89, light_from_view=True).save(os.path.join(PREV, NAME + "_unten.png"))
    preview.render([(tm, "#b9a98a")], size=(1100, 900), azim=-55, elev=35).save(os.path.join(PREV, NAME + "_schraeg.png"))
    pt = to_tm(plate.translate([0, 0, 25.0]))
    preview.render([(tm, "#b9a98a"), (pt, "#9aa7b4")], size=(1100, 1000), azim=-55, elev=28).save(os.path.join(PREV, "zusammenbau_auseinander.png"))


def write_readme(r, g, zeit):
    txt = """UNTERKASTEN (BATTERIEFACH) STAND 8
==================================
Kasten %(W).2f x %(L).2f x %(H).1f mm (mit Zapfen %(Hz).1f), passt unter die Steckplatte mit den auseinandergerückten Gebäuden
(stl/steckmodul_campus/steckplatte_1zu1300.stl, gleicher Umriss). Mit Platte %(tot).1f mm hoch. Befestigung mit Heißkleber, keine Fäden.

Teile:
  U8_unterkasten.stl   Kasten, Hut-Seite unten aufs Bett (so wie in der Datei), kein Support   ca. %(g).0f g
  U8_auflage.stl       Auflage-Klotz %(k).0f x %(k).0f x %(kh).1f mm für die Powerbank, 3 bis 4 Stück drucken (je ca. 1 g)

Auflagen: Die Powerbank liegt auf dem Plateau über dem Knopf (z = 16,0) und auf Klötzen gleicher Höhe, sonst kippt sie (Schwerpunkt etwa 30 mm
neben der Knopfmitte). Die Klötze sind nicht angeformt: erst die Lage der Powerbank festlegen, dann zwei bis drei Klötze unter ihre Ecken auf den
Boden kleben (Heißkleber nur seitlich an den Fuß, nicht darunter, sonst steht die Powerbank höher als das Plateau). Nicht auf die Gänge stellen.

Innen: Erhebung über dem Knopf des Huts (Knopf 11 bis 12 mm hoch, Raum Ø 25 x 13,0, 45°-Anstieg, Decke Ø 20 bei 15,5, Plateau Ø 28 bei 16,0),
acht Kordelgänge 8 x 5 mit Fase innen (Wand 0,8, Decke 0,48 = 3 Lagen x 0,16), Powerbank auf Plateau und Klötzen bei z = 16,0,
Steckerraum 6,0 darüber, Fenster in der Nordwand, Hauptschalter-Loch in der Westwand (Mitte 17,4 über dem Boden), zwei Zapfen für die Platte.

Druck: PLA, Schicht 0,16 mm (die Decken 0,48 sind 3 Lagen), Support aus, Gyroid 10 %% wie plug/slicer.md, Brücken-Einstellungen normal.
Zeit geschätzt: normal %(normal).1f h, schnell %(schnell).1f h, bei deinem Drucker (Nacht 1: 47 g in 2,5 h) etwa %(nacht1).1f h.
Kritisch beim ersten Druck: Decke über dem Knopf (Brücke 19,4 mm bei z 15,7) und die dünnen Gangdecken; dasselbe prüft die Kordelprobe K4.
Prüfung: pruefbericht.txt. Übersicht mit 3D: plug/power/uebersicht8.html
"""
    kb = r["uk"].bounding_box()
    open(os.path.join(OUT, "README.txt"), "w", encoding="utf-8").write(txt % dict(
        W=kb[3] - kb[0], L=kb[4] - kb[1], H=r["H"], Hz=kb[5] - kb[2], tot=r["total"], g=g, k=KLOTZ, kh=r["z_pb"] - PP.UK_FLOOR, **zeit))


def klotz(r):
    """Auflage-Klotz für die Powerbank (Bett z = 0): KLOTZ × KLOTZ, so hoch wie vom Kastenboden bis zum Plateau, Bettkante gefast."""
    from shapely.geometry import box
    from plug.power import build_concept as BC
    return BC.slab_ch(box(0, 0, KLOTZ, KLOTZ), 0.0, r["z_pb"] - PP.UK_FLOOR, PP.CH_BED)


def build():
    """Kasten im Vorgabe-Modus bauen, prüfen, Zusammenbau prüfen. Rückgabe (Ergebnis von kasten8.build, Platte, Fehlerzahl, Bericht)."""
    rep = Report()
    v = K8.stand7()
    K8.modus(PP.GANG_FASE_MODUS)
    r = K8.build(v)
    r["docks"] = [d for d in v["docks"] if d["ok"]]
    W, L = v["plate"]
    rep("Unterkasten Stand 8 (Gangfase %s): Umriss %.2f × %.2f, Kasten %.1f hoch (+%.1f zu Stand 7), mit Platte %.1f; Knopf Ø %.0f × %.1f (gemessen 11 bis 12)" % (
        r["modus"], W, L, r["H"], r["plus"], r["total"], PP.HUT_KNOPF["d"], PP.HUT_KNOPF["h"]))
    bad = 0
    rep("\nPrüfung des Kastens (plug/power/kasten8.py):")
    for name, ok, txt in r["checks"]:
        bad += (not ok)
        rep("  %-32s %-5s %s" % (name, "ok" if ok else "FEHLT", txt))
    b2, plate, r["fit"] = zusammenbau(r, rep)
    r["klotz"] = klotz(r)
    passt = [not a.buffer(-KLOTZ / 2, join_style=2).is_empty for a in r["auflagen"]]
    rep("\nAuflage-Klötze (eigenes Teil, eingeklebt): %.0f × %.0f × %.1f (Boden %.1f bis Plateau %.1f); an den vorgeschlagenen Stellen der Auflagen passt ein Klotz: %d von %d" % (
        KLOTZ, KLOTZ, r["z_pb"] - PP.UK_FLOOR, PP.UK_FLOOR, r["z_pb"], sum(passt), len(passt)))
    b2 += sum(not x for x in passt)
    r["plate_dims"] = tuple(round(float(x), 2) for x in plate.bounding_box())
    return r, plate, bad + b2, rep


def main():
    r, plate, bad, rep = build()
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith((".stl", ".zip", ".txt")):
            os.remove(os.path.join(OUT, f))
    tm = to_tm(r["uk"])
    tm.export(os.path.join(OUT, NAME + ".stl"))
    tm2 = trimesh.load(os.path.join(OUT, NAME + ".stl"))
    g = r["grams"][0]
    zeit = r["zeit"]
    rep("\nTeile (Druckausrichtung, Bett z = 0 = Hut-Seite):")
    rep("  %-20s %6.2f × %6.2f × %5.2f mm  %6.1f cm³  ≈ %3.0f g  dicht=%s  Teile=%d" % (
        NAME + ".stl", *tm2.extents, tm2.volume / 1000.0, g, tm2.is_watertight, len(r["uk"].decompose())))
    rep("  Zeit: normal ≈ %.1f h, schnell ≈ %.1f h, bei deinem Drucker (Nacht 1: 47 g in 2,5 h) ≈ %.1f h" % (zeit["normal"], zeit["schnell"], zeit["nacht1"]))
    bad += (not tm2.is_watertight)
    tk = to_tm(r["klotz"])
    tk.export(os.path.join(OUT, "U8_auflage.stl"))
    rep("  %-20s %6.2f × %6.2f × %5.2f mm  %6.2f cm³  dicht=%s  (3 bis 4 Stück)" % ("U8_auflage.stl", *tk.extents, tk.volume / 1000.0, tk.is_watertight))
    bad += (not tk.is_watertight)
    rep("-> %s" % ("keine Kollisionen" if not bad else "%d Fehler!" % bad))
    with open(os.path.join(OUT, "pruefbericht.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(rep.lines) + "\n")
    write_readme(r, g, zeit)
    zpath = os.path.join(OUT, "unterkasten8.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for f in (NAME + ".stl", "U8_auflage.stl", "README.txt", "pruefbericht.txt"):
            z.write(os.path.join(OUT, f), f)
    print("%s: %.0f kB" % (os.path.relpath(zpath, HERE), os.path.getsize(zpath) / 1024))
    bilder(r, plate)
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
