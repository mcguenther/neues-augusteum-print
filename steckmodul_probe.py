#!/usr/bin/env python3
"""Probedruck für die Kassette: kleines Probestück statt ganzem Institutsgebäude.

Das Probestück ist ein Ausschnitt des Hauptbalkens (22,0 mm breit wie beim Institutsgebäude 1:1000),
nur 36 mm lang und 12 mm hoch über der Plattenoberseite. Kassette, Schieber, Schacht, Nut, Fuß und
Platte sind dieselben wie beim Institutsgebäude (Generator: steckmodul_institut.py).

Aufruf:
    python3 steckmodul_probe.py    # STL + LIESMICH + ZIP nach stl/steckmodul_probe/, Prüfbericht, Vorschau
"""
import os
import shutil
import zipfile

import numpy as np
import shapely
from shapely.geometry.polygon import orient

import steckmodul_dupont as sd
import steckmodul_institut as I
from steckmodul import to_tm

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "stl", "steckmodul_probe")
PREV = os.path.join(HERE, "vorschau", "steckmodul_probe")

PROBE_W, PROBE_L, PROBE_H, PROBE_KEY = 22.0, 36.0, 12.0, 4.0   # Breite (x), Länge (y), Höhe über der Platte, Kodier-Ecke
WIN_ROWS, WIN_H = (6.6,), 4.0                                   # eine Fensterreihe, Restwand 0,4 mm


def probe_source():
    w, l, k = PROBE_W, PROBE_L, PROBE_KEY
    poly = orient(shapely.Polygon([(-w / 2 + k, -l / 2), (w / 2, -l / 2), (w / 2, l / 2), (-w / 2, l / 2),
                                   (-w / 2, -l / 2 + k)]), 1.0)
    return I.ext(I.hcs(poly), 0, PROBE_H), poly, dict(probe=True)


def overhangs(man, name, min_area=4.0):
    """Nach unten zeigende Flächen über dem Bett: flach (Brücken) und steil (> 45°, brauchen Stützen)."""
    tm = to_tm(man)
    n = tm.face_normals
    c = tm.triangles_center
    a = tm.area_faces
    z0 = tm.bounds[0][2]
    rows = []
    steep = (n[:, 2] < -0.72) & (n[:, 2] > -0.95) & (c[:, 2] > z0 + 0.05)         # Überhang flacher als 45° (nicht waagerecht)
    flat = (n[:, 2] <= -0.95) & (c[:, 2] > z0 + 0.05)
    out = dict(name=name, steep_area=float(a[steep].sum()), flat=[])
    zs = np.round(c[flat, 2] / 0.1) * 0.1
    for z in sorted(set(zs.tolist())):
        sel = np.where(flat)[0][zs == z]
        pts = tm.triangles[sel].reshape(-1, 3)
        ext = pts.max(axis=0) - pts.min(axis=0)
        area = float(a[sel].sum())
        if area >= min_area:
            out["flat"].append((round(float(z - z0), 1), round(area, 1), round(float(ext[0]), 1), round(float(ext[1]), 1)))
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(PREV, exist_ok=True)
    P = I.build_all(probe_source(), win_rows=WIN_ROWS, win_h=WIN_H, screw_ring=(2.3, 4.8), center_cassette=True)
    L, d = P["L"], P["d"]
    fl = I.files(P)
    names = [("gebaeude", "1_probestueck"), ("kassette", "2_kassette"), ("schieber", "3_schieber"),
             ("platte", "4_platte"), ("deckel", "5_deckel")]
    print("Probestück %.1f × %.1f mm, %.1f mm sichtbare Höhe + %.1f mm Fuß; Platte %.1f mm dick mit Deckel" % (
        PROBE_W, PROBE_L, PROBE_H, d["F"], d["plate_t"]))
    print("Kassette %.1f × %.1f mm, Schieber läuft %.1f mm, Wand neben dem Schacht %.2f mm" % (
        d["cass_w"], d["cass_len"], L["xwall"] - L["PX"] - d["x_in"] + 1.0,
        (L["bar"] - d["cass_w"] - 2 * sd.KASS_CLR) / 2))
    vols = {}
    for key, fname in names:
        tm = to_tm(fl[key])
        tm.export(os.path.join(OUT, fname + ".stl"))
        vols[fname] = tm.volume / 1000.0
        print("  %-44s %6.1f × %6.1f × %6.1f mm  %5.1f cm³  dicht=%s" % (
            os.path.relpath(os.path.join(OUT, fname + ".stl"), HERE), *tm.extents, vols[fname], tm.is_watertight))
    shutil.copy(os.path.join(HERE, "stl", "steckmodul_dupont", "passprobe.stl"), os.path.join(OUT, "6_passprobe_optional.stl"))

    bad = 0
    print("\nKollisionsprüfung gesteckt (Überschneidungsvolumen):")
    for name, v, ok, note in I.checks(P):
        if not ok:
            bad += 1
        if (not ok) or note:
            print("  %-42s %8.2f mm³  %s" % (name, v, ("ok (%s)" % note) if ok else "KOLLISION"))
    for lab, g, vp, vh in I.insertion_checks(P):
        ok = vp <= 0.5 and vh <= 0.5
        if not ok:
            bad += 1
    print("  -> %s (gesteckt und an 8 Hubhöhen)" % ("keine Kollisionen" if not bad else "%d Kollisionen!" % bad))

    print("\nÜberhänge (Druckausrichtung, nach unten zeigende Flächen über dem Bett):")
    for key, fname in names:
        o = overhangs(fl[key], fname)
        fl_txt = "; ".join("z=%.1f: %.0f mm² (%.1f × %.1f)" % f for f in sorted(o["flat"], key=lambda t: -t[1])[:4])
        print("  %-16s flacher als 45°: %5.1f mm²   waagerechte Decken: %s" % (fname, o["steep_area"], fl_txt or "keine"))

    previews(P, fl)
    write_readme(P, vols)
    zpath = os.path.join(OUT, "probedruck_kassette.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(os.listdir(OUT)):
            if f.endswith(".stl") or f == "LIESMICH.txt":
                z.write(os.path.join(OUT, f), f)
    print("\n%s: %.0f kB" % (os.path.relpath(zpath, HERE), os.path.getsize(zpath) / 1024))
    return P


def previews(P, fl):
    import preview
    L, d = P["L"], P["d"]
    col = dict(building="#ece5d2", plate="#8fa3b8", lid="#6f819a", kass="#e3862a", key="#6bbf78", housing="#f4f1e8",
               terms="#caa13a", wires="#c8423b", header="#2d3236", led="#ffe9a0")
    cut = lambda m: sd.ycut(m, L["PY"])
    parts = [(to_tm(cut(P[k])), col[c]) for k, c in (("plate", "plate"), ("lid", "lid"), ("header", "header"), ("building", "building"),
                                                  ("kass", "kass"), ("key", "key"), ("housing", "housing"), ("terms", "terms"),
                                                  ("wires", "wires"))]
    parts.append((to_tm(cut(P["leds"]["60"])), col["led"]))
    im = preview.render(parts, size=(1300, 800), azim=-62, elev=20); im.save(os.path.join(PREV, "schnitt_quer.png"))
    xc = L["PX"] + sd.pin_x()[1]
    cutx = lambda m: sd.xcut(m, xc)
    parts = [(to_tm(cutx(P[k])), col[c]) for k, c in (("plate", "plate"), ("lid", "lid"), ("header", "header"), ("building", "building"),
                                                   ("kass", "kass"), ("key", "key"), ("housing", "housing"), ("terms", "terms"),
                                                   ("wires", "wires"))]
    parts.append((to_tm(cutx(P["leds"]["60"])), col["led"]))
    im = preview.render(parts, size=(1300, 800), azim=62, elev=18); im.save(os.path.join(PREV, "schnitt_laengs.png"))
    # Zusammenbau von unten
    b = [(to_tm(P["building"]), col["building"])]
    for k, c in (("kass", "kass"), ("housing", "housing"), ("terms", "terms"), ("wires", "wires")):
        b.append((to_tm(P[k].translate([0, 0, -22])), col[c]))
    b.append((to_tm(P["leds"]["60"].translate([0, 0, -22])), col["led"]))
    b.append((to_tm(P["key"].translate([26, 0, 0])), col["key"]))
    im = preview.render(b, size=(1300, 900), azim=-58, elev=-30); im.save(os.path.join(PREV, "zusammenbau_unten.png"))
    # Druckteile nebeneinander, Druckausrichtung
    items, x = [], 0.0
    for key, c in (("gebaeude", "building"), ("kassette", "kass"), ("schieber", "key"), ("platte", "plate"), ("deckel", "lid")):
        tm = to_tm(fl[key])
        w = tm.extents[0]
        tm.apply_translation([x - tm.bounds[0][0], -tm.extents[1] / 2 - tm.bounds[0][1], 0])
        items.append((tm, col[c]))
        x += w + 10
    im = preview.render(items, size=(1500, 700), azim=-30, elev=30); im.save(os.path.join(PREV, "druckteile.png"))
    print("Vorschau: %s" % os.path.relpath(PREV, HERE))


def write_readme(P, vols):
    d, L = P["d"], P["L"]
    txt = f"""PROBEDRUCK KASSETTE (Plan B, Dupont-Teile) – Institutsgebäude-Ausschnitt
=========================================================================

Was ist das?
  Ein kleines Probestück ({PROBE_W:.0f} × {PROBE_L:.0f} mm, {PROBE_H:.0f} mm sichtbare Höhe + {d['F']:.0f} mm Fuß). Es ist ein Ausschnitt
  des Hauptbalkens vom Institutsgebäude (1:1000) mit denselben Maßen für Fuß, Schacht, Nut, Kassette und Schieber.
  Damit prüfst du die Kassette mit Schieber, das Stecken in die Platte und das Licht durch die dünne Wand.

Dateien (alle in Druckausrichtung, einfarbig, keine Stützen nötig)
  1_probestueck.stl   Gebäude mit Fuß: Fuß nach unten auf das Druckbett, Dach oben    ({vols['1_probestueck']:.1f} cm³)
  2_kassette.stl      Kassette: steht aufrecht, Buchsentasche unten offen              ({vols['2_kassette']:.1f} cm³)
  3_schieber.stl      Schieber (Trichterplatte, 1 mm dick): liegt flach                ({vols['3_schieber']:.1f} cm³)
  4_platte.stl        Mini-Platte mit Mulde, Dock A und Federzunge                     ({vols['4_platte']:.1f} cm³)
  5_deckel.stl        Deckel mit zwei Stempeln (Stempel zeigen nach oben)              ({vols['5_deckel']:.1f} cm³)
  6_passprobe_optional.stl  Taschen für Buchse und Stiftleiste mit 0,0 / 0,1 / 0,2 mm Spiel

  Reihenfolge: zuerst 3 und 2 (klein, schnell), dann 1, dann 4 und 5.

Material: alle fünf Teile zusammen {sum(v for v in vols.values()):.0f} cm³ (bei 100 % Füllung etwa {sum(v for v in vols.values())*1.24:.0f} g PLA,
  mit 15 % Füllung deutlich weniger). Nur das Dach des Probestücks ist eine Brücke (19,6 mm breit), alles andere ist ≤ 14 mm.

Slicer-Einstellungen (Düse 0,4 mm)
  Schichthöhe 0,2 mm, PLA oder PETG, Wände 3 Linien (= 1,2 mm), Füllung 15 %, Brückenerkennung an.
  Die Lichtfenster sind nur 0,4 mm dick (eine einzige Linie). Der Slicer muss dünne Wände drucken: Beim neuen
  Wandgenerator „Arachne“ (PrusaSlicer 2.6 und neuer, Bambu Studio, Cura) geht das von selbst, sonst die Option
  „Dünne Wände erkennen“ bzw. „Lücken zwischen Wänden füllen“ einschalten. Im Slicer-Vorschaubild prüfen, ob die Fenster da sind.
  Keine Stützen. Falls ein Slicer die Brücke im Dach (19,6 mm breit) bemängelt: das ist eine Brücke, keine Stütze nötig.
  Schieber: ohne Rand/Brim drucken, langsam (erste Schicht 20 mm/s), er ist nur 1 mm dick und kann sich verziehen.
  Kassette und Schieber nach dem Druck an den Kanten entgraten (Elefantenfuß), dann erst zusammenstecken.

Was du zusätzlich brauchst
  - Dupont-Gehäuse 1×4 mit 4 gecrimpten Adern (Buchse), 1 Stück Winkelstiftleiste mit 4 Pins aus dem Set
  - ein Stück WS2812B-Streifen (60/m 10 mm oder 144/m 12 mm), optional zum Anlöten
  - 4 Blechschrauben M3 × 8 für den Deckel (oder den Deckel mit etwas Heißkleber fixieren)

Ablauf
  1. Passprobe (6) mit den echten Teilen prüfen. Falls Buchse oder Leiste nicht passen: Maße im Generator ändern.
  2. Buchse in die Tasche der Kassette drücken (Steckseite zur offenen Unterseite), Adern in den Schlitz legen,
     Streifen auf die Ablage kleben und anlöten.
  3. Kassette von unten in den Schacht des Probestücks schieben. Schieber seitlich (durch die lange Wand, +x) in die Nut
     schieben, bis er anschlägt. Er schließt bündig mit der Wand ab.
  4. Leiste von unten in die Platte schieben (Pins zeigen nach oben, Lötenden in den Kabelraum), Deckel anschrauben.
  5. Probestück in die Mulde stecken. Die abgeschrägte Ecke zeigt, wie herum es passt.

Was du messen sollst
  - Schieber: gleitet er leicht, ohne zu klemmen, und schließt er bündig ab?
  - Kassette: sitzt sie ohne Spiel im Schacht? Anschlag oben erreicht?
  - Stecken: Kraft zum Einstecken (Ziel unter 10 N) und zum Herausziehen (Ziel 3 bis 8 N); hebt die Mini-Platte mit?
  - Kontakt: LED leuchtet, DETECT-Pin liest LOW (Stifte stecken 4,2 mm in der Buchse; Kontaktpunkt ist geschätzt)
  - Licht: leuchtet die 0,4-mm-Wand gleichmäßig? (Fenster zeigen nach außen auf allen vier Seiten)

Maße zum Nachschauen
  Kassette {d['cass_w']:.1f} × {d['cass_len']:.1f} mm, Ablage {I.SEAT_W:.1f} × {I.SEAT_L:.1f} mm, Schacht +0,2 mm je Seite,
  Nut 45° mit 0,15 mm Spiel, Schieber 1,0 mm, Fuß {d['F']:.1f} mm, Mulde 0,25 mm Spiel im Führungsband.
"""
    with open(os.path.join(OUT, "LIESMICH.txt"), "w", encoding="utf-8") as f:
        f.write(txt)


if __name__ == "__main__":
    main()
