#!/usr/bin/env python3
"""Passprobe Winkelleiste (Version 6): flache Platte mit drei Feldern, Körperhöhe 2,0 / 1,8 / 1,6 mm.

Geometrie, Konstanten (PP_*) und Vorschaubilder der Passprobe. Sie prüft nur die Winkelleiste (Körper neben den
senkrechten Pins, siehe plug/fit_test/angled_pin.html): zwei Zeilen Taschenspiel, drei Spalten Pinlage.
Kaufteilmaße kommen aus plug/dupont.py (bzw. plug/parts.py). Anleitung als Seite: python3 -m plug.fit_test.build_page
(baut plug/fit_test/page.html aus page.template.html). `python3 -m plug.sample` ruft write_stl() und previews() auf
und legt die Datei als stl/steckmodul_probe/0_passprobe.stl ins Probedruck-ZIP.

Aufruf:
    python3 -m plug.fit_test.generator    # nur Passprobe: STL nach stl/steckmodul_probe/, Vorschau nach vorschau/steckmodul_probe/
"""
import os

import numpy as np

from plug import dupont as sd
from plug.geom import box, cyl, diff, union, to_tm

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))     # Repo-Wurzel
OUT = os.path.join(HERE, "stl", "steckmodul_probe")
PREV = os.path.join(HERE, "vorschau", "steckmodul_probe")

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


def write_stl(out=OUT):
    """Schreibt 0_passprobe.stl nach `out` und gibt die Prüfzeilen aus (dicht, Überhänge, Felder)."""
    os.makedirs(out, exist_ok=True)
    tmp = to_tm(passprobe())
    tmp.export(os.path.join(out, "0_passprobe.stl"))
    print("  %-44s %6.1f × %6.1f × %6.1f mm  %5.1f cm³  dicht=%s" % (
        "stl/steckmodul_probe/0_passprobe.stl", *tmp.extents, tmp.volume / 1000.0, tmp.is_watertight))
    pp_ov = overhangs(passprobe(), "0_passprobe")
    print("  Passprobe: Überhänge flacher als 45°: %.1f mm², waagerechte Decken: %s" % (
        pp_ov["steep_area"], "; ".join("z=%.1f: %.0f mm²" % f[:2] for f in pp_ov["flat"]) or "keine"))
    print("  Passprobe: Felder h = %s mm, Stufe %s mm unter der Decke (Pin-Mitte h/2 unter der Decke), Löcher %.1f mm, Spiel %.2f mm, Platte %.1f × %.1f × %.1f mm" % (
        " / ".join("%.1f" % h for h in PP_VAR), " / ".join("%.2f" % (PP_H - PP_FLOOR - pp_step(h)) for h in PP_VAR),
        PP_HOLE, PP_CLR, PP_W, PP_L, PP_H))
    return tmp


def previews(prev=PREV):
    """Vorschaubilder passprobe_schraeg, passprobe_schriftseite und passprobe_schnitt nach `prev`."""
    import preview
    import trimesh
    os.makedirs(prev, exist_ok=True)
    pp = to_tm(passprobe())                            # Druckausrichtung: Schriftseite unten, Taschen offen nach oben
    im = preview.render([(pp, "#b9bfc4")], size=(1500, 900), azim=-70, elev=50); im.save(os.path.join(prev, "passprobe_schraeg.png"))
    pp2 = pp.copy()                                    # wie ein Buch um die lange Kante umgedreht: Schriftseite oben
    pp2.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0]))
    im = preview.render([(pp2, "#b9bfc4")], size=(1500, 900), azim=-90, elev=89); im.save(os.path.join(prev, "passprobe_schriftseite.png"))
    # Querschnitt durch den ersten Pin des Feldes h = 2,0 mit eingesetzter Leiste (Konstruktionslage: Schriftseite oben, Taschen unten)
    xc = PP_X[0] + sd.pin_x()[0]
    plate = sd.xcut(_passprobe_con(), xc)
    leiste = sd.xcut(passprobe_leiste(PP_VAR[0], 0), xc)
    im = preview.render([(to_tm(plate), "#b9bfc4"), (to_tm(leiste), "#2d3236")], size=(1500, 900), azim=0, elev=0)
    im.save(os.path.join(prev, "passprobe_schnitt.png"))


if __name__ == "__main__":
    write_stl()
    previews()
