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


# --------------------------------------------------------------------------
# Passprobe (Version 6): Winkelleiste. Eine Reihe mit drei Feldern, Variante = angenommene Körperhöhe h = 2,0 / 1,8 / 1,6 mm.
# Der Körper liegt mit der Oberseite an der Decke (Unterseite des Muldenbodens), die Pin-Mitte liegt h/2 darunter. Das Lötende soll
# flach auf der Stufe liegen (= Decke des Lötendenschlitzes, beim Druck der Schlitzboden): Stufe = Pin-Oberseite = zb − h/2 + PIN_SQ/2.
# Das ist der einzige Unterschied zwischen den Feldern; Spiel, Löcher und Pinlage sind fest (Soll).
# --------------------------------------------------------------------------
PP_VAR = (2.0, 1.8, 1.6)                     # angenommene Körperhöhe je Feld (links nach rechts)
PP_CLR = sd.SNUG_HDR                         # Spiel je Seite der Körpertasche (x und y), fest
PP_HOLE = sd.HOLE                            # Lochdurchmesser, fest
PP_PITCH = 13.0                              # Feldabstand
PP_X = tuple((i - 1) * PP_PITCH for i in range(3))
PP_FLOOR = sd.CEIL                           # Decke über dem Körper (wie der Muldenboden in der Platte)
PP_UNDER = 1.2                               # Platz unter dem Körper
PP_H = round(PP_FLOOR + 2.0 + PP_UNDER, 1)   # Plattendicke (Körper 2,0 angenommen, = CEIL + 2,0 + 1,2)
PP_YOFF = sd.HDR_T / 2 + sd.RA_BACK + sd.PIN_SQ / 2   # Pin-Mitte hinter der Körpermitte (Soll)
PP_HCH = 0.3                                 # Senkung (45°) an den Löchern auf der Schriftseite = Bettseite beim Druck
PP_CH = 0.5                                  # Einlauffase (45°) am Taschenrand
PP_SLOT_X = abs(sd.pin_x()[0]) + sd.PIN_SQ / 2 + 0.8   # halbe Breite von Schacht und Lötendenschlitz
PP_WALL = 1.8
PP_BACK = sd.HDR_T / 2 + PP_CLR + sd.RA_TAIL + 0.9   # Lötendenschlitz reicht so weit hinter die Körpermitte (-y)
PP_FWD = PP_YOFF + sd.PIN_SQ / 2 + 0.8                # Schacht reicht so weit vor die Körpermitte (+y)
PP_TXT = 3.4                                # Schrifthöhe (fett, dazu 0,15 mm Verbreiterung, 0,6 mm tief graviert)
_lab = 1.4 + PP_TXT / 2                      # Beschriftung ganz unten
_yb = _lab + PP_TXT / 2 + 1.5 + PP_BACK
PP_L = round(_yb + PP_FWD + 1.4, 1)
PP_W = round((len(PP_X) - 1) * PP_PITCH + 2 * (sd.HDR_W / 2 + PP_CLR + PP_WALL), 1)
PP_LAB = round(_lab - PP_L / 2, 2)           # y der Beschriftung
PP_YB = round(_yb - PP_L / 2, 2)             # y der Körpermitte


def pp_step(h):
    """Stufenhöhe über dem Plattenunterrand (Konstruktionslage, Taschenseite unten) für die Körperhöhe h; Luft 0."""
    return sd.step_z(PP_H - PP_FLOOR, h, clr=0.0)


def pp_label(h):
    return ("%.1f" % h).replace(".", ",")


def _passprobe_con():
    """Platte in Konstruktionslage: Taschenseite bei z = 0 (offen), Schriftseite bei z = PP_H, y nach oben wie in der Draufsicht."""
    from steckmodul import box, cyl, diff
    import manifold3d as m3d
    blk = box(-PP_W / 2, PP_W / 2, -PP_L / 2, PP_L / 2, 0, PP_H)
    cuts = []
    zb = PP_H - PP_FLOOR                              # Oberkante der Körpertasche = Unterseite des Muldenbodens
    yb = PP_YB
    hw, hd = sd.HDR_W / 2 + PP_CLR, sd.HDR_T / 2 + PP_CLR

    def chamfer(w, d, cx, cy):                        # Trichter am Taschenrand, unten (z=0) um PP_CH weiter
        cs = m3d.CrossSection.square((w + 2 * PP_CH, d + 2 * PP_CH), center=True)
        f = m3d.Manifold.extrude(cs, PP_CH + 0.01, scale_top=(w / (w + 2 * PP_CH), d / (d + 2 * PP_CH)))
        return f.translate([cx, cy, -0.01])

    def cone(hd_, cx, cy):                            # Senkung am Loch, an der Schriftseite z = PP_H um PP_HCH weiter
        return m3d.Manifold.cylinder(PP_HCH + 0.01, hd_ / 2, hd_ / 2 + PP_HCH + 0.01, 32).translate([cx, cy, PP_H - PP_HCH])
    for h, x in zip(PP_VAR, PP_X):
        cuts.append(box(x - hw, x + hw, yb - hd, yb + hd, -0.01, zb))                                  # Körper
        cuts.append(chamfer(2 * hw, 2 * hd, x, yb))
        cuts.append(box(x - PP_SLOT_X, x + PP_SLOT_X, yb, yb + PP_FWD, -0.01, zb))                    # Schacht (Knick, Pins)
        cuts.append(box(x - PP_SLOT_X, x + PP_SLOT_X, yb - PP_BACK, yb, -0.01, pp_step(h)))           # Lötenden, Decke = Stufe
        for px_ in sd.pin_x():
            cuts.append(cyl(PP_HOLE / 2, zb - 0.01, PP_H + 0.01, cx=x + px_, cy=yb + PP_YOFF, n=32))
            cuts.append(cone(PP_HOLE, x + px_, yb + PP_YOFF))
    try:
        import generate

        def label(text, x, y, size=PP_TXT):
            cs = generate.text_cross_section(text, size, 0.0, -size / 2, anchor="center")
            if cs is not None:
                cs = cs.offset(0.15, m3d.JoinType.Round).translate((x, y))     # fetter
                cuts.append(m3d.Manifold.extrude(cs, 0.7).translate([0, 0, PP_H - 0.6]))
        for h, x in zip(PP_VAR, PP_X):
            label(pp_label(h), x, PP_LAB)
    except Exception as e:
        print("  (Beschriftung übersprungen: %s)" % e)
    return diff(blk, *cuts)


def passprobe():
    """Flache Platte mit drei Feldern (Körperhöhe 2,0 / 1,8 / 1,6 mm). Je Feld: Tasche für den Körper (HDR_W+0,2 × HDR_T+0,2 mm, von der
    Taschenseite offen, 45°-Einlauffase), Schacht für Knick und senkrechte Pins, Schlitz für die 3-mm-Lötenden nach -y mit der Stufe
    in Höhe zb − h/2 + PIN_SQ/2, darüber der Muldenboden mit vier Löchern.
    Rückgabe in Druckausrichtung: Schriftseite auf dem Bett (um die x-Achse umgedreht), Taschen offen nach oben, keine Brücken."""
    return _passprobe_con().rotate([180.0, 0.0, 0.0]).translate([0.0, 0.0, PP_H])


def passprobe_leiste(h=2.0, field=0):
    """Winkelleiste (Körper, vier Pins) so eingesetzt, wie sie in Feld `field` sitzen soll (Konstruktionslage, Körper mit Körperhöhe h an der Decke)."""
    from steckmodul import box, union
    zb = PP_H - PP_FLOOR
    zm = zb - h / 2
    x0, yb, T, q = PP_X[field], PP_YB, sd.HDR_T, sd.PIN_SQ
    parts = [box(x0 - sd.HDR_W / 2, x0 + sd.HDR_W / 2, yb - T / 2, yb + T / 2, zb - h, zb)]
    for px_ in sd.pin_x():
        x = x0 + px_
        parts.append(box(x - q / 2, x + q / 2, yb - T / 2 - sd.RA_TAIL, yb + PP_YOFF + q / 2, zm - q / 2, zm + q / 2))
        parts.append(box(x - q / 2, x + q / 2, yb + PP_YOFF - q / 2, yb + PP_YOFF + q / 2, zm - q / 2, zm - q / 2 + sd.HDR_LEG))
    return union(parts)


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
    tmp = to_tm(passprobe())
    tmp.export(os.path.join(OUT, "0_passprobe.stl"))
    print("  %-44s %6.1f × %6.1f × %6.1f mm  %5.1f cm³  dicht=%s" % (
        "stl/steckmodul_probe/0_passprobe.stl", *tmp.extents, tmp.volume / 1000.0, tmp.is_watertight))
    pp_ov = overhangs(passprobe(), "0_passprobe")
    print("  Passprobe: Überhänge flacher als 45°: %.1f mm², waagerechte Decken: %s" % (
        pp_ov["steep_area"], "; ".join("z=%.1f: %.0f mm²" % f[:2] for f in pp_ov["flat"]) or "keine"))
    print("  Passprobe: Felder h = %s mm, Stufe %s mm unter der Decke (Pin-Mitte h/2 unter der Decke), Löcher %.1f mm, Spiel %.2f mm, Platte %.1f × %.1f × %.1f mm" % (
        " / ".join("%.1f" % h for h in PP_VAR), " / ".join("%.2f" % (PP_H - PP_FLOOR - pp_step(h)) for h in PP_VAR),
        PP_HOLE, PP_CLR, PP_W, PP_L, PP_H))
    old = os.path.join(OUT, "6_passprobe_optional.stl")
    if os.path.exists(old):
        os.remove(old)

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
    import trimesh
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
    pp = to_tm(passprobe())                            # Druckausrichtung: Schriftseite unten, Taschen offen nach oben
    im = preview.render([(pp, "#b9bfc4")], size=(1500, 900), azim=-70, elev=50); im.save(os.path.join(PREV, "passprobe_schraeg.png"))
    pp2 = pp.copy()                                    # wie ein Buch um die lange Kante umgedreht: Schriftseite oben
    pp2.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0]))
    im = preview.render([(pp2, "#b9bfc4")], size=(1500, 900), azim=-90, elev=89); im.save(os.path.join(PREV, "passprobe_schriftseite.png"))
    # Querschnitt durch den ersten Pin des Feldes h = 2,0 mit eingesetzter Leiste (Konstruktionslage: Schriftseite oben, Taschen unten)
    xc = PP_X[0] + sd.pin_x()[0]
    plate = sd.xcut(_passprobe_con(), xc)
    leiste = sd.xcut(passprobe_leiste(PP_VAR[0], 0), xc)
    im = preview.render([(to_tm(plate), "#b9bfc4"), (to_tm(leiste), "#2d3236")], size=(1500, 900), azim=0, elev=0)
    im.save(os.path.join(PREV, "passprobe_schnitt.png"))
    print("Vorschau: %s" % os.path.relpath(PREV, HERE))


def write_readme(P, vols):
    d, L = P["d"], P["L"]
    pp_vol = to_tm(passprobe()).volume / 1000.0
    txt = f"""PROBEDRUCK KASSETTE (Plan B, Dupont-Teile) – Institutsgebäude-Ausschnitt
=========================================================================

Was ist das?
  Ein kleines Probestück ({PROBE_W:.0f} × {PROBE_L:.0f} mm, {PROBE_H:.0f} mm sichtbare Höhe + {d['F']:.1f} mm Fuß). Es ist ein Ausschnitt
  des Hauptbalkens vom Institutsgebäude (1:1000) mit denselben Maßen für Fuß, Schacht, Nut, Kassette und Schieber.
  Damit prüfst du die Kassette mit Schieber, das Stecken in die Platte und das Licht durch die dünne Wand.

Dateien (alle in Druckausrichtung, einfarbig, keine Stützen nötig)
  1_probestueck.stl   Gebäude mit Fuß: Fuß nach unten auf das Druckbett, Dach oben    ({vols['1_probestueck']:.1f} cm³)
  2_kassette.stl      Kassette: steht aufrecht, Buchsentasche unten offen              ({vols['2_kassette']:.1f} cm³)
  3_schieber.stl      Schieber (Trichterplatte, 1 mm dick): liegt flach                ({vols['3_schieber']:.1f} cm³)
  4_platte.stl        Mini-Platte mit Mulde, Dock A und Federzunge                     ({vols['4_platte']:.1f} cm³)
  5_deckel.stl        Deckel mit zwei Stempeln (Stempel zeigen nach oben)              ({vols['5_deckel']:.1f} cm³)
  0_passprobe.stl     Passprobe Winkelleiste (flach, {pp_vol:.1f} cm³): drei Felder mit Stufenhöhe für Körperhöhe 2,0 / 1,8 / 1,6 mm; Schriftseite aufs Bett
                      (Anleitung: stecker/probe/passprobe.html). Nicht Teil des Probestücks, sondern vorher zu drucken.

  Reihenfolge: zuerst 0 (Passprobe), dann 3 und 2 (klein, schnell), dann 1, dann 4 und 5.

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
  - Dupont-Gehäuse 1×4 mit 4 gecrimpten Adern (Buchse), 1 Stück Winkelstiftleiste mit 4 Pins aus dem Set (Körper nicht über 4 Pins hinaus abbrechen, Rest feilen)
  - ein Stück WS2812B-Streifen (60/m 10 mm oder 144/m 12 mm), optional zum Anlöten
  - 4 Blechschrauben M3 × 8 für den Deckel (oder den Deckel mit etwas Heißkleber fixieren)

Ablauf
  1. Teile mit den echten Kaufteilen anprobieren (Buchse in die Kassette, Leiste in die Platte). Passt etwas nicht: Maße im Generator ändern.
  2. Buchse in die Tasche der Kassette drücken (Steckseite zur offenen Unterseite), Adern in den Schlitz legen,
     Streifen auf die Ablage kleben und anlöten.
  3. Kassette von unten in den Schacht des Probestücks schieben. Schieber seitlich (durch die lange Wand, +x) in die Nut
     schieben, bis er anschlägt. Er schließt bündig mit der Wand ab.
  4. Winkelleiste von unten in die Platte schieben: die senkrechten Pins zeigen nach oben und durch die Löcher im Muldenboden, der
     Körper liegt neben den Pins, die 3-mm-Lötenden zeigen von den Pins weg in den Kabelraum. Deckel anschrauben.
  5. Probestück in die Mulde stecken. Die abgeschrägte Ecke zeigt, wie herum es passt.

Was du messen sollst
  - Schieber: gleitet er leicht, ohne zu klemmen, und schließt er bündig ab?
  - Kassette: sitzt sie ohne Spiel im Schacht? Anschlag oben erreicht?
  - Stecken: Kraft zum Einstecken (Ziel unter 10 N) und zum Herausziehen (Ziel 3 bis 8 N); hebt die Mini-Platte mit?
  - Kontakt: LED leuchtet, DETECT-Pin liest LOW (Stifte stecken {d['E']:.1f} mm in der Buchse; Kontaktpunkt ist geschätzt)
  - Licht: leuchtet die 0,4-mm-Wand gleichmäßig? (Fenster zeigen nach außen auf allen vier Seiten)

Maße zum Nachschauen
  Kassette {d['cass_w']:.1f} × {d['cass_len']:.1f} mm, Ablage {I.SEAT_W:.1f} × {I.SEAT_L:.1f} mm, Schacht +0,2 mm je Seite,
  Nut 45° mit 0,15 mm Spiel, Schieber 1,0 mm, Fuß {d['F']:.1f} mm, Mulde 0,25 mm Spiel im Führungsband.
"""
    with open(os.path.join(OUT, "LIESMICH.txt"), "w", encoding="utf-8") as f:
        f.write(txt)


if __name__ == "__main__":
    main()
