#!/usr/bin/env python3
"""STL für die erste Passform-Runde (City-Hochhaus, 1:1300, Steckplatte 14,6 mm flach) nach stl/steckmodul_footfit/.

Teile (Plan: plug/footfit/plan.html, Einstellungen vom Nutzer abgenickt):
  H1_stummel_hochhaus.stl   Hohlgebäude 06_city_hochhaus_1zu1300_fase2.stl (Fuß 14,2, Boden 1,2, Schacht V2R, Wand 0,8, Fuß-Fase 2,0) bei HOEHE mm über der
                            Plattenoberfläche abgeschnitten, Fuß unten auf dem Bett, Lage wie in der Platte (nur verschoben)
  H2_kassette_V2R.stl       Probeteil Kassette V2R (Konzept aus plug/testcase/variants.py, Tasche unten am Bett; Streifen, Adern und Buchse sind Kaufteile)
Prüfungen: dicht, Kassette im Schacht ohne Kollision, Stummel in der echten Steckplatte (Spiel 0,10, Kontrolle mit Versatz), Überhang je Lage.

Aufruf (aus dem Wurzelverzeichnis):  python3 -m plug.footfit.build_stub [--hoehe 25]    (ca. 1 min)
"""
import argparse
import math
import os
import subprocess
import sys
import zipfile

import manifold3d as m3d
import numpy as np
import trimesh
from shapely.geometry import Polygon

from plug import campus as C
from plug.fit_test.generator import overhangs
from plug.geom import to_bed, to_tm, vol_int
from plug.testcase import params as P
from plug.testcase import variants as V

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(HERE, "stl", "steckmodul_footfit")
PREV = os.path.join(HERE, "vorschau", "steckmodul_footfit")
MODEL = os.path.join(HERE, "stl", "steckmodul_campus", "gebaeude", "06_city_hochhaus_1zu1300_fase2.stl")
PLATE = os.path.join(HERE, "stl", "steckmodul_campus", "steckplatte_1zu1300.stl")
SLUG = "06_city_hochhaus"
LAYER, UEBERHANG_T = 0.2, 0.25


def load(path):
    tm = trimesh.load(path)
    tm.merge_vertices()
    return m3d.Manifold(m3d.Mesh(vert_properties=np.asarray(tm.vertices, np.float32), tri_verts=np.asarray(tm.faces, np.uint32)))


def layer_poly(man, z):
    g = None
    for ring in man.slice(z).to_polygons():
        r = Polygon(ring).buffer(0)
        g = r if g is None else g.symmetric_difference(r)
    return g


def ueberhang(man, step=LAYER, tol=UEBERHANG_T):
    """Lagenweise: Material, das weiter als tol über das der Lage darunter hinausragt (flacher als gut 45°); Brücke (ringsum Material) oder Kragstück."""
    b = man.bounding_box()
    prev, res, z = None, dict(bruecke_mm2=0.0, bruecke_mm=0.0, krag_mm2=0.0, krag_mm=0.0, stellen=[]), b[2] + step / 2
    while z < b[5]:
        m = layer_poly(man, z)
        if prev is not None and m is not None and not m.is_empty:
            u = m.difference(prev.buffer(tol, quad_segs=4))
            u = u.buffer(-0.05).buffer(0.05) if not u.is_empty else u
            rand = m.boundary.buffer(0.03)
            for g in getattr(u, "geoms", [u]):
                if g.is_empty or g.area < 0.2:
                    continue
                lo, hi = tol, 40.0
                for _ in range(8):
                    mid = (lo + hi) / 2
                    lo, hi = (lo, mid) if g.difference(prev.buffer(mid, quad_segs=4)).buffer(-0.05).is_empty else (mid, hi)
                art = "krag" if g.boundary.intersection(rand).length > 0.5 else "bruecke"
                res[art + "_mm2"] += g.area
                res[art + "_mm"] = max(res[art + "_mm"], lo)
                if lo > 1.0:
                    c = g.representative_point()
                    res["stellen"].append((art, round(z - b[2], 1), round(g.area, 1), round(lo, 1), round(c.x, 1), round(c.y, 1)))
        prev = m if m is not None else prev
        z += step
    return {k: (round(v, 2) if isinstance(v, float) else v) for k, v in res.items()}


def previews():
    for name, azim in (("H1_stummel_hochhaus", -50), ("H2_kassette_V2R", -50)):
        subprocess.run([sys.executable, os.path.join(HERE, "preview.py"), os.path.join(OUT, name + ".stl"), "--azim", str(azim), "--elev", "35", "--out", PREV],
                       check=True, cwd=HERE, stdout=subprocess.DEVNULL)


def write_readme(info, hoehe, mins):
    txt = f"""PASSFORM-STUMMEL CITY-HOCHHAUS (erste Passform-Runde, 1:1300, Steckplatte 14,6 mm flach)
=====================================================================================

Teile (je 1 Stück, beide in einem Druck auf einem Bett):
  H1_stummel_hochhaus.stl  Hohlgebäude City-Hochhaus, oben bei {hoehe:.0f} mm über der Plattenoberfläche abgeschnitten (gesamt {hoehe + 14.2:.1f} mm hoch),
                           unten Fuß 14,2 mm mit Boden 1,2 mm, Schacht für Kassette V2R, Wand 0,8 mm, Fase unten 2,0 mm (45°), Spiel zur Mulde 0,10 mm je Seite
  H2_kassette_V2R.stl      Probeteil Kassette V2R (Konzept, noch nie gedruckt): 13,0 x 6,4 x 36,9 mm

Druckausrichtung (so liegen die Dateien schon): Stummel mit dem Fuß unten auf dem Bett (Schacht öffnet am Bett), Kassette mit der Tasche unten.
Einstellungen wie bisher: Bambu A1, schwarzes PLA, Düse 0,4, Schichthöhe 0,2, Wände 2 oder mehr (die Wand ist 0,8 mm = 2 Bahnen), Füllung egal,
KEIN Support, Thick bridges an. Kein Brim nötig. Rand ohne Elefantenfuß-Kompensation lassen, die Fase ist schon eingerechnet.
Druckzeit geschätzt (nicht kalibriert) etwa {mins:.0f} min. Bitte die echte Zeit aus dem Slicer melden.

Prüfbericht: pruefbericht.txt (dicht, keine Kollisionen, Stummel in der Mulde der echten Steckplatte, Überhang je Lage).

Ablauf
  1. Stummel von Hand in die Mulde des Hochhauses auf der Steckplatte setzen (die Lage ist durch den Umriss festgelegt; Fuß-Fase 2,0 mm soll ihn fangen).
     Fühlen: geht er ohne Kraft hinein, hakt er an einer Ecke, klemmt er, wackelt er, sitzt er auf dem Muldenboden auf?
  2. Herausziehen: wie fest (1 locker bis 5 fest)?
  3. Unten am Stummel auf Elefantenfuß / Wulst achten (klemmt er dort?).
  4. Kassette V2R mit der Tasche voran von unten in den Schacht des Stummels pressen (nicht in die Platte gesteckt): Sitz (1 lose bis 5 fest),
     Wand um den Schacht gerissen? Die Kassette soll bündig mit der Fußunterkante abschließen.
  5. Kassette mit Buchse bestücken und den Stummel wieder in die Platte stecken: treffen die Pins die Buchse?
     (LED-Streifen und Adern sind in dieser Runde nicht nötig.)
  6. Das Abschneiden oben ist offen: der Stummel ist dünnwandig (0,8 mm) und weicher als das ganze Gebäude; das ist so gewollt.

Ergebnis bitte als Text im Chat melden (Testbogen kommt nach dem Druck).
"""
    open(os.path.join(OUT, "README.txt"), "w", encoding="utf-8").write(txt)


class Report:
    def __init__(self):
        self.lines = []

    def __call__(self, txt):
        print(txt)
        self.lines.append(txt)


def main(hoehe):
    import json
    rep = Report()
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(PREV, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith((".stl", ".zip", ".txt")):
            os.remove(os.path.join(OUT, f))
    d = P.dims_plan()
    F, T = d["F"], C.plate_thickness(d)
    p = json.load(open(C.CACHE % P.SCALE_PLAN))[SLUG]
    yc = C.foot_local("V2R", 0.0).centroid.y

    full = load(MODEL)
    stub_w = full.trim_by_plane([0, 0, -1], -hoehe)                  # Weltlage, z = 0 Plattenoberseite, behalten wird z <= hoehe
    kas = V.kassette("V2R")
    def place_k(m):
        return m.translate([0, 0, -F]).translate([0.0, d["y_kass0"] - yc, 0.0]).rotate([0.0, 0.0, p["angle"]]).translate([p["cx"], p["cy"], 0.0])
    kas_w = place_k(kas)

    rep("Passform-Stummel City-Hochhaus: Höhe über der Platte %.1f mm (gesamt %.1f mm mit Fuß %.1f), Spiel 0,10, Fuß-Fase 2,0, Wand 0,8, Kassette V2R (Probeteil)" % (hoehe, hoehe + F, F))
    rep("Quelle: %s (Hohlgebäude aus Branch jolly-pascal, Fuß-Fase nach plug/footfit/buildings_fuss_fase.patch)" % os.path.relpath(MODEL, HERE))

    # Teile in Druckausrichtung: Stummel mit dem Fuß auf dem Bett (nur verschoben), Kassette mit der Tasche am Bett
    b = stub_w.bounding_box()
    stub = stub_w.translate([-(b[0] + b[3]) / 2, -(b[1] + b[4]) / 2, 0.0])
    stub = to_bed(stub)
    parts = {"H1_stummel_hochhaus": stub, "H2_kassette_V2R": to_bed(kas)}
    rep("\nTeile (Druckausrichtung, Bett z = 0):")
    info = {}
    for name, man in parts.items():
        tm = to_tm(man)
        tm.export(os.path.join(OUT, name + ".stl"))
        ov = overhangs(man, name)
        ue = ueberhang(man)
        info[name] = dict(tm=tm, ue=ue)
        rep("  %-22s %6.1f × %6.1f × %5.1f mm  %5.2f cm³  dicht=%s (Manifold: %s)" % (name + ".stl", *tm.extents, tm.volume / 1000.0, tm.is_watertight, man.status().name))
        rep("      waagerechte Decken: %s" % ("; ".join("z=%.1f: %.0f mm² (%.1f × %.1f)" % f for f in sorted(ov["flat"], key=lambda t: -t[1])[:4]) or "keine"))
        rep("      Lagenprüfung (Überhang je 0,2 mm über %.2f): Brücken %.2f mm² (bis %.2f mm), Kragstücke %.2f mm² (bis %.2f mm), Stellen über 1 mm: %s" % (
            UEBERHANG_T, ue["bruecke_mm2"], ue["bruecke_mm"], ue["krag_mm2"], ue["krag_mm"], ue["stellen"] or "keine"))

    rep("\nPrüfung der Passungen (Überschneidungsvolumen, mm³; muss 0 sein):")
    bad = 0

    def chk(txt, v, limit=0.05):
        nonlocal bad
        ok = v <= limit
        bad += (not ok)
        rep("  %-72s %9.3f  %s" % (txt, v, "ok" if ok else "KOLLISION"))
    chk("Kassette V2R im Schacht des Stummels", vol_int(kas_w, stub_w))
    plate = load(PLATE)
    st_plate = stub_w.translate([0, 0, T])                            # Plattenrahmen: Platte reicht von 0 bis T, Muldenboden 0,4 unten
    chk("Stummel in der Mulde der Steckplatte (Spiel 0,10)", vol_int(st_plate, plate))
    chk("Kontrolle: Stummel 0,12 mm in +x verschoben stößt an der Mulde an", 0.0 if vol_int(st_plate.translate([0.12, 0, 0]), plate) > 0.05 else 1.0)
    chk("Kontrolle: Stummel 0,12 mm in +y verschoben stößt an der Mulde an", 0.0 if vol_int(st_plate.translate([0, 0.12, 0]), plate) > 0.05 else 1.0)
    kas_dick = place_k(kas.scale([1.0 + 0.2 / 12.96, 1.0, 1.0]))
    chk("Kontrolle: Kassette 0,2 mm breiter (kein Spiel mehr) stößt im Schacht an", 0.0 if vol_int(kas_dick, stub_w) > 0.05 else 1.0)
    rep("  Kassette unten bündig mit der Fußunterkante: Unterkante Kassette z=%.2f, Fußunterkante z=%.2f" % (kas_w.bounding_box()[2], stub_w.bounding_box()[2]))
    rep("  -> %s" % ("keine Kollisionen" if not bad else "%d Kollisionen!" % bad))

    ts = info["H1_stummel_hochhaus"]["tm"]
    rep("\nStummel: Fläche der ersten Lage (Bett) %.0f mm², Fase unten 2,0 mm: Außenmaß am Bett %.1f × %.1f mm, ab 2,0 mm Höhe %.1f × %.1f mm" % (
        layer_poly(stub, 0.1).area, *(lambda g: (g.bounds[2] - g.bounds[0], g.bounds[3] - g.bounds[1]))(max(layer_poly(stub, 0.1).geoms, key=lambda g: g.area) if hasattr(layer_poly(stub, 0.1), "geoms") else layer_poly(stub, 0.1)),
        *(lambda g: (g.bounds[2] - g.bounds[0], g.bounds[3] - g.bounds[1]))(max(layer_poly(stub, 2.5).geoms, key=lambda g: g.area) if hasattr(layer_poly(stub, 2.5), "geoms") else layer_poly(stub, 2.5))))
    # Zeitschätzung wie auf der Planseite (Pfadlänge = Fläche / 0,42, 60 mm/s, Zuschlag 1,5 s, Mindestzeit 6 s, Start 6 min); nicht kalibriert
    b2 = stub.bounding_box()
    sec, z = 0.0, 0.1
    while z < b2[5]:
        g = layer_poly(stub, z)
        sec += max((g.area / 0.42) / 60.0 + 1.5, 6.0) if g is not None else 0.0
        z += LAYER
    zk, zz = 0.0, 0.1
    kb = parts["H2_kassette_V2R"].bounding_box()
    while zz < kb[5]:
        g = layer_poly(parts["H2_kassette_V2R"], zz)
        zk += max((g.area / 0.42) / 60.0 + 1.5, 6.0) if g is not None else 0.0
        zz += LAYER
    mins = (sec + zk) / 60.0 + 6.0
    rep("Druckzeit geschätzt (nicht kalibriert): Stummel %.0f min, Kassette %.0f min, zusammen auf einem Bett etwa %.0f min" % (sec / 60.0 + 6.0, zk / 60.0 + 6.0, mins))
    with open(os.path.join(OUT, "pruefbericht.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(rep.lines) + "\n")
    previews()
    write_readme(info, hoehe, mins)
    zpath = os.path.join(OUT, "passform_stummel_hochhaus.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(os.listdir(OUT)):
            if f.endswith(".stl") or f in ("README.txt", "pruefbericht.txt"):
                z.write(os.path.join(OUT, f), f)
    rep("%s: %.0f kB" % (os.path.relpath(zpath, HERE), os.path.getsize(zpath) / 1024))
    return bad, info, hoehe


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--hoehe", type=float, default=25.0)
    a = ap.parse_args()
    bad, info, h = main(a.hoehe)
    sys.exit(1 if bad else 0)
