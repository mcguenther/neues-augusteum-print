#!/usr/bin/env python3
"""Zweiter Nachtdruck: Änderungen aus dem Ergebnis von Nacht 1 und den Antworten auf das Entscheidungsdokument
(plug/decision/page.html).

Ergebnis Nacht 1 (Kurzfassung, Wortlaut im Chat):
  K  kein stabiler Durchgang (Kontakte waren gecrimpt): 1,2 mm Aussetzer, ab 1,8 nichts → dünner testen, nur bis 1,0
  N  alle vier Schieber klemmen; Decke über der Nut stark durchgehängt (34 mm Brücke), Fäden in der Nut, Elefantenfuß ≈ 0,2 mm
  S  0,15 ideal, 0,20 minimales Spiel
  C  Buchse nur mit Kraft (0,22 + Rippen), geht nicht ganz hinein; Adern knicken; Ablage 1 mm weiter weg von der Tasche
  R  0,20 ohne Rippen ideal
  D  überall schief; Körper liegt vermutlich auf der Stufe auf
  FM nicht getestet (Fuß-Lehre fehlte)
  Druck: schwarzes PLA, Gravur schlecht lesbar, Elefantenfuß ≈ 0,2 mm, Bambu, 2,5 h für alles

Antworten auf die Entscheidungen:
  K  einverstanden, aber nur bis 1,0 mm (über 1,2 bringt nichts)        → Plättchen 0,4 / 0,6 / 0,8 / 1,0
  N  Schieber noch einmal probieren; dazu die Frage, ob man die Kassette einfach einpressen kann
     → N: Schieber mit mehr Spiel (0,20 bis 0,50) und Luft über dem Schieber, eine Platte wie im Gebäude (mit Brücke),
          eine umgedreht gedruckt (ohne Brücke, nur die Passung)
     → E: Kassette v3 mit eingebauter Trichterplatte als Boden, in einen Schacht eingepresst (Presspassung 0,06 / 0,09 / 0,12)
  S  einverstanden (0,15)
  C  einverstanden, aber die LED-Ablage braucht keine Tasche → oben eine flache Fläche
  D  Tasche pauschal +1,5 mm, stattdessen die Körperhöhe variieren (2,0 / 1,8 / 1,6 wie in v6)
  FM einverstanden, Druck einverstanden

Oben stehen die Parameter (gemeinsame Quelle für Entscheidungsdokument und STL), darunter die Geometrie.

Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m plug.series2      # STL, README.txt und ZIP nach stl/steckmodul_night2/, Vorschau nach vorschau/steckmodul_night2/
"""
from plug import dupont as sd

# ---- Entscheidungen aus Nacht 1 (neue Sollwerte, gelten ab jetzt für die Kassette)
KASS_CLR2 = 0.15       # S: 0,15 „mit Fingerdruck, kein Spiel“, 0,20 „minimales Spiel“ (alt 0,20)
SNUG2 = 0.20           # R: Hülse 0,20 ohne Rippen „ziemlich perfekt“ (alt 0,22 mit Rippen 0,12: „nur mit Kraft“)
RIB2 = 0.0             # keine Crush-Rippen mehr in der Buchsentasche
HSG_TOL2 = 0.45        # C: Tasche 0,2 mm höher, die Buchse ging nicht ganz hinein (alt 0,25)
ENTRY_CH = 0.4         # neue Regel: 45°-Einführfase an jeder Öffnung, in die etwas gesteckt wird
EF_CH = 0.3            # neue Regel: Fase an Bettkanten von Steckteilen (Elefantenfuß ≈ 0,2 mm)
RAISE = 0.6            # Höhe der erhabenen Schrift

# ---- Kassette v2 (Oberseite flach, Ablage höher, Übergang rund, Ablage 1 mm weiter weg)
SEAT_RISE = 0.5        # flache Oberseite (LED-Fläche) liegt so weit über der Taschenoberkante (alt: Ablage 1,05 darunter)
GAP_L2 = sd.GAP_L + 1.0   # Abstand Tasche → LED-Fläche 1 mm größer (C: „1 mm mehr Abstand Richtung Tasche“)
FILLET = 1.5           # Rundung der Kante zwischen Tasche und LED-Fläche
WIRE_W = 9.2           # Breite des Aderschlitzes über der Tasche (vier Adern im 2,54-Raster, Ader 1,0); daneben die Schultern
SEAT_TOL = 0.25        # LED-Fläche je Seite größer als der Streifen (C/LED: „Toleranz einplanen“)

# ---- N: Schieber noch einmal, mit mehr Spiel und Luft über dem Schieber (die Brücke bleibt, siehe README)
N2_CLR = (0.20, 0.30, 0.40, 0.50)   # Spiel je Seite (waagerecht gemessen) zwischen Schieber und Nut
N2_HEAD = 0.4          # Luft über dem Schieber: die Decke darf so weit durchhängen, ohne dass er klemmt
N2_OVER = 0.8          # Hinterschnitt des Schwalbenschwanzes je Seite über die Schieberdicke (≈ 39° zur Senkrechten)
P_H = 8.0              # Höhe der Prüfkörper (N-Platten, E-Körper)

# ---- E: Kassette v3 zum Einpressen (Boden = Trichterplatte, Buchse von oben)
E_CLR = (0.06, 0.09, 0.12)   # Spiel je Seite im Schacht (Nacht 1: 0,10 „nur mit Kraft“, 0,05 passte nicht)
E_FLOOR = sd.FUNNEL_T  # Boden der Kassette v3 mit den Trichtern (1,0)
E_STOP = 1.0           # Anschlag oben im Schacht (Kammerboden im Gebäude), hier ein Rand
E_LIP = 1.2            # Breite des Anschlagrands
E_WALL = 2.5           # Wand der E-Körper um den Schacht

# ---- K: dünnere Plättchen (Kontakte gecrimpt), Einstecktiefe 5,28 bis 4,68 mm
K2_T = (0.4, 0.6, 0.8, 1.0)

# ---- D: Körpertasche pauschal 1,5 mm zum Lötende hin länger, Körperhöhe variiert wie in v6
D2_EXT = 1.5
D2_H = (2.0, 1.8, 1.6)

# ---- FM: Fuß-Lehre (Unterseite des Probestücks) für die schon gedruckten Mulden-Ringe
LEHRE_CAP = 2.0        # Deckel über dem Fuß

# ---- nur noch für das Entscheidungsdokument (Vorschlag Bodenplatte, nicht umgesetzt)
B_MARGIN = 1.5
B_CLR = (0.05, 0.10, 0.15, 0.20)
D2_EXT_DOC = (0.5, 1.0, 1.5)


def e_of(t):
    """Einstecktiefe der Pins in der Buchse bei Plättchendicke t."""
    return sd.HDR_UP - t


# ==========================================================================
# Geometrie
# ==========================================================================
import math
import os
import zipfile

import manifold3d as m3d

from plug import institute as I
from plug import sample as S
from plug import series as SR
from plug.fit_test import generator as pp
from plug.fit_test.generator import overhangs
from plug.geom import box, cbox, ccw, cyl, union, diff, ext, prism_x, to_bed, to_tm, vol_int, xcut, ycut

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "stl", "steckmodul_night2")
PREV = os.path.join(HERE, "vorschau", "steckmodul_night2")
de = SR.de


def emboss_top(cs, x, y, z_top, h=RAISE):
    return m3d.Manifold.extrude(cs.translate((x, y)), h + 0.01).translate([0, 0, z_top - 0.01])


def emboss_side(cs, x, z, y_face, h=RAISE):
    """Erhabene Schrift auf einer senkrechten Fläche bei y = y_face, Außenseite nach −y, lesbar von −y."""
    m = m3d.Manifold.extrude(cs, h + 0.01).rotate([90, 0, 0])            # (x, v, e) -> (x, -e, v)
    return m.translate([x, y_face + 0.01, z])


def notches_x(n, y0, z0, z1, x_face, pitch=2.4, w=1.2, depth=0.6):
    """n senkrechte V-Kerben in der Fläche x = x_face (Außenseite +x), ab y0 in +y-Richtung (Rang zum Fühlen)."""
    out = []
    for k in range(n):
        yc = y0 + k * pitch
        tri = m3d.CrossSection([[(x_face + 0.01, yc - w / 2), (x_face + 0.01, yc + w / 2), (x_face - depth, yc)]])
        out.append(ext(tri, z0, z1))
    return out


def notches_y(n, x0, z0, z1, y_face, pitch=2.4, w=1.2, depth=0.6):
    """n senkrechte V-Kerben in der Fläche y = y_face (Außenseite −y), ab x0 in +x-Richtung."""
    out = []
    for k in range(n):
        xc = x0 + k * pitch
        tri = m3d.CrossSection([[(xc - w / 2, y_face - 0.01), (xc + w / 2, y_face - 0.01), (xc, y_face + depth)]])
        out.append(ext(tri, z0, z1))
    return out


def chamfer_hole(w, d, z, ch, down=True, cx=0.0, cy=0.0):
    """Einführfase einer rechteckigen Öffnung w × d in der Ebene z, dort um ch je Seite größer.
    down=True: Öffnung unten (Fase reicht von z nach oben), sonst Öffnung oben (Fase reicht von z nach unten)."""
    big = m3d.CrossSection.square((w + 2 * ch + 0.02, d + 2 * ch + 0.02), center=True)
    sc = (w / (w + 2 * ch + 0.02), d / (d + 2 * ch + 0.02))
    m = m3d.Manifold.extrude(big, ch + 0.01, 0, 0.0, sc)
    if down:
        return m.translate([cx, cy, z - 0.01])
    return m.mirror([0, 0, 1]).translate([cx, cy, z + 0.01])


def chamfered_block(w, d, h, ch_bot, ch_top, r=0.3):
    """Quader w × d × h (z 0..h), unten Fase ch_bot, oben Fase ch_top, senkrechte Kanten gerundet."""
    cs = m3d.CrossSection.square((w, d), center=True).offset(-r, m3d.JoinType.Round).offset(r, m3d.JoinType.Round)
    parts = [ext(cs, ch_bot, h - ch_top)]
    if ch_bot > 0:
        parts.append(m3d.Manifold.extrude(cs.offset(-ch_bot, m3d.JoinType.Round), ch_bot + 0.01, 0, 0.0,
                                          (w / (w - 2 * ch_bot), d / (d - 2 * ch_bot))))
    if ch_top > 0:
        parts.append(m3d.Manifold.extrude(cs, ch_top + 0.01, 0, 0.0, ((w - 2 * ch_top) / w, (d - 2 * ch_top) / d)).translate([0, 0, h - ch_top - 0.01]))
    return union(parts)


def hole_ch(x, y, z0, z1, d, ch_bot, ch_top, n=32):
    """Senkrechtes Loch d mit 45°-Fasen ch_bot unten (z0) und ch_top oben (z1)."""
    out = [cyl(d / 2, z0 - 0.01, z1 + 0.01, cx=x, cy=y, n=n)]
    if ch_bot > 0:
        out.append(m3d.Manifold.cylinder(ch_bot + 0.01, d / 2 + ch_bot + 0.01, d / 2, n).translate([x, y, z0 - 0.01]))
    if ch_top > 0:
        out.append(m3d.Manifold.cylinder(ch_top + 0.01, d / 2, d / 2 + ch_top + 0.01, n).translate([x, y, z1 - ch_top]))
    return out


def funnels(y, z0, t):
    """Trichterplatte z0..z0+t: unten Trichter FUNNEL_D → HOLE (45°), oben Fase CHAMF, Pin-Reihe bei y."""
    h = (sd.FUNNEL_D - sd.HOLE) / 2
    out = []
    for px in sd.pin_x():
        out.append(m3d.Manifold.cylinder(h + 0.01, sd.FUNNEL_D / 2 + 0.01, sd.HOLE / 2, 32).translate([px, y, z0 - 0.01]))
        out += hole_ch(px, y, z0, z0 + t, sd.HOLE, 0.0, SR.CHAMF)
    return out


def big_label(text, rank, size):
    return SR.mark_cs(text, rank, size)


# --------------------------------------------------------------------------
# Kassette v2 (unten offen, Schultern oben) und v3 (Trichterboden, Tasche oben offen)
# Konstruktion: Unterkante z = 0, Mitte x = 0, y = 0 an der Taschenseite
# --------------------------------------------------------------------------
def kass2_dims(floor=False):
    zf = E_FLOOR if floor else 0.0
    pk_w, pk_d = sd.HSG_W + 2 * SNUG2, sd.HSG_T + 2 * SNUG2
    zp = zf + sd.HSG_H + HSG_TOL2                 # Taschenoberkante (v2: Unterseite der Schultern)
    top = zp + SEAT_RISE                          # flache Oberseite = LED-Fläche
    y_p0 = sd.WALL
    y1 = y_p0 + pk_d
    seat0 = y1 + sd.WALL + GAP_L2                 # LED-Streifen beginnt hier (Din-Ende zur Tasche)
    seat1 = seat0 + I.SEAT_L + 2 * SEAT_TOL
    L = seat1
    cw = max(pk_w + 2 * sd.WALL, I.SEAT_W + 2 * SEAT_TOL)
    return dict(zf=zf, pk_w=pk_w, pk_d=pk_d, zp=zp, zs=top, top=top, y_p0=y_p0, y1=y1, seat0=seat0, seat1=seat1, L=L, cw=cw,
                ypin=y_p0 + pk_d / 2)


def kassette2(floor=False, centered=False):
    k = kass2_dims(floor)
    L, cw, top, zf = k["L"], k["cw"], k["top"], k["zf"]
    body = chamfered_block(cw, L, top, EF_CH, ENTRY_CH).translate([0, L / 2, 0])
    if not floor:
        cuts = [cbox(k["pk_w"], k["pk_d"], -0.01, k["zp"], cy=k["ypin"]),                                # Tasche, unten offen
                chamfer_hole(k["pk_w"], k["pk_d"], 0.0, ENTRY_CH, True, cy=k["ypin"]),                  # Einführfase unten
                box(-WIRE_W / 2, WIRE_W / 2, k["y_p0"], k["y1"], k["zp"] - 0.01, top + 0.01)]            # Aderschlitz, daneben Schultern
    else:
        cuts = [cbox(k["pk_w"], k["pk_d"], zf, top + 0.01, cy=k["ypin"]),                                # Tasche, oben offen
                chamfer_hole(k["pk_w"], k["pk_d"], top, ENTRY_CH, False, cy=k["ypin"])]                 # Einführfase oben
        cuts += funnels(k["ypin"], 0.0, zf)                                                            # Boden = Trichterplatte
    # Rundung der Kante Tasche → LED-Fläche (entlang x über die Schlitzbreite)
    r, y1 = FILLET, k["y1"]
    arc = [(y1 + r + r * math.cos(a), top - r + r * math.sin(a)) for a in [math.pi / 2 + j * math.pi / 2 / 16 for j in range(17)]]
    prof = [(y1 - 0.01, top - r), (y1 - 0.01, top + 0.01), (y1 + r, top + 0.01)] + arc[1:-1] + [(y1, top - r)]
    cuts.append(prism_x(prof, -WIRE_W / 2, WIRE_W / 2))
    # Querrinne für die DETECT-Brücke (Pin 4 zum GND-Pad) vor dem LED-Streifen
    gx = sorted([sd.pin_x()[3], sd.pad_x("GND")])
    cuts.append(box(gx[0] - 0.9, gx[1] + 0.9, k["seat0"] - 1.7, k["seat0"] - 0.5, top - sd.GROOVE[1], top + 0.01))
    m = diff(body, *cuts)
    if centered:
        m = m.translate([0, -L / 2, 0])
    return m


def housing_in(k, centered=True):
    """Dupont-Buchse (Nennmaß) so, wie sie in der Kassette sitzt (v2: oben an den Schultern, v3: auf dem Boden)."""
    yc = k["ypin"] - (k["L"] / 2 if centered else 0.0)
    z0 = k["zf"] if k["zf"] > 0 else k["zp"] - sd.HSG_H
    return sd.housing_part(z0).translate([0, -sd.dims()["HY"] + yc, 0])


# --------------------------------------------------------------------------
# N: Platte mit Schacht und Schwalbenschwanz-Nut, Schieber (Konstruktionslage wie im Gebäude, Unterkante z = 0)
# --------------------------------------------------------------------------
def n2_dims():
    k = kass2_dims()
    hx, hy = k["cw"] / 2 + KASS_CLR2, k["L"] / 2 + KASS_CLR2
    hb = k["L"] / 2 + 1.5                                  # halbe Schieberbreite unten (ohne Spiel)
    bx = S.PROBE_W / 2
    by = max(S.PROBE_L / 2, hb + N2_OVER + 3.0)
    return dict(hx=hx, hy=hy, hb=hb, x_in=-(hx + 1.0), bx=bx, by=by, ypin=k["ypin"] - k["L"] / 2)


def n2_profile(clr, head, ef, groove):
    """Querschnitt (y, z) der Nut (groove=True, Spiel 0, Mündungsfase ef) bzw. des Schiebers (Spiel clr, Bettfase ef)."""
    n = n2_dims()
    T = sd.FUNNEL_T
    w = lambda z: n["hb"] - clr + N2_OVER * z / T
    s = 1.0 if groove else -1.0
    zb = -0.01 if groove else 0.0
    half = [(w(ef) + s * ef, zb), (w(ef), ef), (w(T), T)]
    if head > 0:
        half.append((w(T), T + head))
    right = half
    left = [(-y, z) for y, z in reversed(half)]
    return right + left


def n2_slab(flip=False):
    """Platte wie die Unterseite des Gebäudes: Schacht für Kassette v2 (Spiel 0,15), Nut mit Luft über dem Schieber.
    flip=True: in Druckausrichtung umgedreht (Nut oben offen, keine Brücke)."""
    n = n2_dims()
    m = chamfered_block(2 * n["bx"], 2 * n["by"], P_H, EF_CH, EF_CH if flip else 0.0, r=sd.FOOT_R)
    cuts = [box(-n["hx"], n["hx"], -n["hy"], n["hy"], -0.01, P_H + 0.01),
            chamfer_hole(2 * n["hx"], 2 * n["hy"], P_H, ENTRY_CH, False),                     # Einführfase oben (Kassette von oben)
            prism_x(n2_profile(0.0, N2_HEAD, EF_CH, True), n["x_in"], n["bx"] + 6.0)]
    m = diff(m, *cuts)
    if flip:
        m = m.rotate([180, 0, 0]).translate([0, 0, P_H])
    lab = emboss_side(big_label("N " + ("B" if flip else "A"), 0, 4.4), 0.0, P_H * 0.5, -n["by"])
    return union([m, lab])


def n2_slider(c, rank):
    """Schieber: Schwalbenschwanz mit Spiel c, Trichter unten, Fasen, Griffkerbe, Rang als Kerben am Griffende, Schrift unten."""
    n = n2_dims()
    T = sd.FUNNEL_T
    x0, x1 = n["x_in"] + c, n["bx"] + 1.0
    k = prism_x(n2_profile(c, 0.0, EF_CH, False), x0, x1)
    wt = n["hb"] - c + N2_OVER
    cuts = funnels(n["ypin"], 0.0, T)
    for s in (-1, 1):                                                               # Ecken vorn angefast (Einführung)
        cuts.append(ext(m3d.CrossSection([ccw([(x0 - 0.01, s * (wt + 0.01)), (x0 + 1.2, s * (wt + 0.01)), (x0 - 0.01, s * (wt - 1.2))])]), -0.01, T + 0.01))
    cuts.append(cbox(0.8, 8.0, T - 0.5, T + 0.01, cx=x1 - 0.5))                    # Griffkerbe im Überstand
    cuts += notches_x(rank, 3.0, -0.01, T + 0.01, x1, pitch=2.0, w=1.0, depth=0.5)
    lab = big_label("N " + de(c), rank, 3.6).mirror((1, 0))                        # unten, von unten lesbar
    cuts.append(m3d.Manifold.extrude(lab.translate(((x0 + n["bx"]) / 2, 5.5)), 0.41).translate([0, 0, -0.01]))
    return diff(k, *cuts)


# --------------------------------------------------------------------------
# E: Körper mit Schacht zum Einpressen der Kassette v3 (Druckausrichtung: Anschlagrand auf dem Bett, Kassette von oben)
# --------------------------------------------------------------------------
def e_dims(c):
    k = kass2_dims(True)
    hx, hy = k["cw"] / 2 + c, k["L"] / 2 + c
    return dict(hx=hx, hy=hy, ox=hx + E_WALL, oy=hy + E_WALL)


def e_body(c, rank):
    e = e_dims(c)
    m = chamfered_block(2 * e["ox"], 2 * e["oy"], P_H, EF_CH, 0.3)
    iw, idp = 2 * (e["hx"] - E_LIP), 2 * (e["hy"] - E_LIP)
    cuts = [box(-e["hx"], e["hx"], -e["hy"], e["hy"], E_STOP, P_H + 0.01),
            chamfer_hole(2 * e["hx"], 2 * e["hy"], P_H, ENTRY_CH, False),                 # Einführfase (Kassette kommt von oben)
            cbox(iw, idp, -0.01, E_STOP + 0.01),                                        # Öffnung im Anschlagrand
            chamfer_hole(iw, idp, 0.0, EF_CH, True)]
    cuts += notches_x(rank, -e["oy"] + 4.0, 1.0, P_H + 0.01, e["ox"])
    m = diff(m, *cuts)
    return union([m, emboss_side(big_label("E " + de(c), 0, 4.0), 0.0, P_H * 0.55, -e["oy"])])


def kass3_in_body(c):
    """Kassette v3 so, wie sie im E-Körper (Druckausrichtung) bis zum Anschlag eingepresst ist."""
    k = kass2_dims(True)
    return kassette2(True, True).rotate([180, 0, 0]).translate([0, 0, E_STOP + k["top"]])


# --------------------------------------------------------------------------
# K: Kontakt-Plättchen, D: Passprobe v7, FM: Fuß-Lehre
# --------------------------------------------------------------------------
def contact2():
    W, D, gap = 14.5, 14.0, 3.0
    parts = []
    n = len(K2_T)
    for i, t in enumerate(K2_T):
        cx = (i - (n - 1) / 2) * (W + gap)
        m = box(cx - W / 2, cx + W / 2, -D / 2, D / 2, 0, t)
        ch = min(SR.CHAMF, t / 2 - 0.05)
        cuts = []
        for px in sd.pin_x():
            cuts += hole_ch(cx + px, 4.6, 0.0, t, sd.HOLE, ch, ch)
        cuts += notches_y(i + 1, cx - W / 2 + 2.0, -0.01, t + 0.01, -D / 2, pitch=2.0, w=1.0, depth=0.5)
        m = diff(m, *cuts)
        parts.append(union([m, emboss_top(big_label("K " + de(t, 1), i + 1, 4.0), cx, -0.6, t, h=0.5)]))
    return union(parts)


def fitprobe7():
    """Passprobe v7: wie v6 drei Felder mit Körperhöhe 2,0 / 1,8 / 1,6 (Stufe), Körpertasche um D2_EXT zum Lötende verlängert."""
    blk = box(-pp.PP_W / 2, pp.PP_W / 2, -pp.PP_L / 2, pp.PP_L / 2, 0, pp.PP_H)
    zb = pp.PP_H - pp.PP_FLOOR
    yb = pp.PP_YB
    hw, hd = sd.HDR_W / 2 + pp.PP_CLR, sd.HDR_T / 2 + pp.PP_CLR
    e = D2_EXT
    cuts = []
    for h, x in zip(D2_H, pp.PP_X):
        cuts.append(box(x - hw, x + hw, yb - hd - e, yb + hd, -0.01, zb))                                   # Körper, länger zum Lötende
        big = m3d.CrossSection.square((2 * hw + 2 * pp.PP_CH, 2 * hd + e + 2 * pp.PP_CH), center=True)
        f = m3d.Manifold.extrude(big, pp.PP_CH + 0.01, 0, 0.0, (2 * hw / (2 * hw + 2 * pp.PP_CH), (2 * hd + e) / (2 * hd + e + 2 * pp.PP_CH)))
        cuts.append(f.translate([x, yb - e / 2, -0.01]))
        cuts.append(box(x - pp.PP_SLOT_X, x + pp.PP_SLOT_X, yb, yb + pp.PP_FWD, -0.01, zb))               # Schacht (Knick, Pins)
        cuts.append(box(x - pp.PP_SLOT_X, x + pp.PP_SLOT_X, yb - pp.PP_BACK, yb - hd - e + 0.01, -0.01, pp.pp_step(h)))   # Stufe (kürzer)
        for px_ in sd.pin_x():
            cuts += SR.pin_hole(x + px_, yb + pp.PP_YOFF, zb, pp.PP_H)
    import generate
    for k, (h, x) in enumerate(zip(D2_H, pp.PP_X)):
        cs = generate.text_cross_section(pp.pp_label(h), pp.PP_TXT, 0.0, -pp.PP_TXT / 2, anchor="center").offset(0.3, m3d.JoinType.Round)
        cuts.append(m3d.Manifold.extrude(cs.translate((x - 1.4, pp.PP_LAB)), pp.PP_DEPTH + 0.01).translate([0, 0, pp.PP_H - pp.PP_DEPTH]))
        r = 1.25
        sym = [m3d.CrossSection([[(-r * 1.15, -r * 0.8), (r * 1.15, -r * 0.8), (0, r * 1.25)]]),
               m3d.CrossSection.square((2 * r, 2 * r), center=True), m3d.CrossSection.circle(r * 1.1, 32)][k]
        cuts.append(m3d.Manifold.extrude(sym.translate((x + 5.0, pp.PP_LAB + 0.3)), pp.PP_DEPTH + 0.01).translate([0, 0, pp.PP_H - pp.PP_DEPTH]))
    cuts += notches_y(2, -pp.PP_W / 2 + 3.0, -0.01, pp.PP_H + 0.01, -pp.PP_L / 2)        # zwei Kerben: v7 (v6 hat keine)
    m = diff(blk, *cuts)
    return m.rotate([180.0, 0.0, 0.0]).translate([0.0, 0.0, pp.PP_H])


def foot_gauge():
    """Fuß-Lehre: Unterseite des Probestücks (Fußumriss mit Kodierecke, 0,8-mm-Fase in Schichtstufen), oben offen."""
    d = I.dims()
    F = d["F"]
    poly = S.probe_source()[1]
    cs = I.hcs(poly)
    foot = I.foot_solid(cs, F)
    cap = ext(I.rounded(cs), -0.01, LEHRE_CAP)
    m = union([foot, cap])
    inner = ext(I.rounded(cs).offset(-2.0, m3d.JoinType.Round), -F + 1.2, LEHRE_CAP + 0.01)
    m = diff(m, inner)
    lab = emboss_top(big_label("FUSS", 0, 5.0).rotate(90), 0.0, 0.0, -F + 1.2, h=0.6)
    return to_bed(union([m, lab]))


# --------------------------------------------------------------------------
def row(ms, gap=SR.GAP):
    """Teile in einer Reihe entlang x (je auf das Bett gelegt)."""
    out, x = [], 0.0
    for m in ms:
        m = to_bed(m)
        b = m.bounding_box()
        out.append(m.translate([x - b[0], -(b[1] + b[4]) / 2, 0]))
        x += b[3] - b[0] + gap
    return union(out)


def build():
    k2, k3, n = kass2_dims(), kass2_dims(True), n2_dims()
    parts = {}
    parts["K_contact_spacers_v2"] = contact2()
    kc = kassette2()
    parts["C_cassette_v2_x2"] = row([kc, kc], 6.0)
    parts["N_slabs_A_B"] = row([n2_slab(False), n2_slab(True)])
    sliders = [n2_slider(c, i + 1) for i, c in enumerate(N2_CLR)]
    pitch = 2 * (n["hb"] + N2_OVER) + 4.0
    parts["N_sliders_v2"] = union([s.rotate([0, 0, 90]).translate([i * pitch, 0, 0]) for i, s in enumerate(sliders)])
    parts["E_cassette_v3_x2"] = row([kassette2(True), kassette2(True)], 6.0)
    ebodies = [e_body(c, i + 1) for i, c in enumerate(E_CLR)]
    parts["E_bodies"] = row(ebodies)
    parts["D_fitprobe_v7"] = fitprobe7()
    parts["FM_foot_gauge"] = foot_gauge()
    return parts, sliders, ebodies


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(PREV, exist_ok=True)
    for f in os.listdir(OUT):                                     # alte STL (z. B. vom verworfenen Bodenplatten-Entwurf) entfernen
        if f.endswith(".stl"):
            os.remove(os.path.join(OUT, f))
    k2, k3, n = kass2_dims(), kass2_dims(True), n2_dims()
    print("Kassette v2: %.2f × %.2f × %.2f mm, Tasche %.2f × %.2f × %.2f, LED-Fläche ab y=%.2f, Schlitz %.1f, Schultern je %.2f × %.1f" % (
        k2["cw"], k2["L"], k2["top"], k2["pk_w"], k2["pk_d"], k2["zp"], k2["seat0"], WIRE_W, (k2["pk_w"] - WIRE_W) / 2, SEAT_RISE))
    print("Kassette v3: %.2f × %.2f × %.2f mm, Boden %.1f mit Trichtern, Tasche oben offen" % (k3["cw"], k3["L"], k3["top"], E_FLOOR))
    print("N: Platte %.1f × %.1f × %.1f, Schacht %.2f × %.2f, Schieber %.2f breit (unten, Spiel 0), Nut oben %.2f, Luft %.1f" % (
        2 * n["bx"], 2 * n["by"], P_H, 2 * n["hx"], 2 * n["hy"], 2 * n["hb"], 2 * (n["hb"] + N2_OVER), N2_HEAD))

    parts, sliders, ebodies = build()
    print("\nTeile (Druckausrichtung, Bett z = 0):")
    info = {}
    for name, man in parts.items():
        man = to_bed(man)
        parts[name] = man
        tm = to_tm(man)
        tm.export(os.path.join(OUT, name + ".stl"))
        g, nl = SR.estimate(man)
        ov = overhangs(man, name)
        info[name] = dict(tm=tm, g=g, layers=nl)
        print("  %-26s %6.1f × %6.1f × %5.1f mm  %5.1f cm³  ≈ %4.1f g  dicht=%s" % (name + ".stl", *tm.extents, tm.volume / 1000.0, g, tm.is_watertight))
        print("      waagerechte Decken: %s   Überhang flacher als 45°: %.0f mm²" % (
            "; ".join("z=%.1f: %.0f mm² (%.1f × %.1f)" % f for f in sorted(ov["flat"], key=lambda t: -t[1])[:3]) or "keine", ov["steep_area"]))

    # --- Prüfungen
    print("\nPrüfung der Passungen (Überschneidungsvolumen, mm³; muss 0 sein):")
    bad = 0

    def chk(txt, v, limit=0.05):
        nonlocal bad
        ok = v <= limit
        bad += (not ok)
        print("  %-66s %8.3f  %s" % (txt, v, "ok" if ok else "KOLLISION"))
    kv2 = kassette2(centered=True)
    kv3 = kassette2(True, True)
    chk("Buchse (Nennmaß) in der Tasche der Kassette v2 (an den Schultern)", vol_int(housing_in(k2), kv2))
    chk("Buchse (Nennmaß) in der Tasche der Kassette v3 (auf dem Boden)", vol_int(housing_in(k3), kv3))
    chk("Kontrolle: Buchse 0,1 höher stößt in v2 an die Schultern", 0.0 if vol_int(housing_in(k2).translate([0, 0, 0.1]), kv2) > 0.05 else 1.0)
    slab = n2_slab(False)
    kin = kv2.translate([0, 0, sd.FUNNEL_T])                       # Kassette liegt auf dem Schieber
    chk("Kassette v2 im Schacht der Platte N (auf dem Schieber)", vol_int(kin, slab))
    for c, s in zip(N2_CLR, sliders):
        chk("Schieber %s in der Nut der Platte N" % de(c), vol_int(s, slab))
        chk("Schieber %s unter der Kassette v2" % de(c), vol_int(s, kin))
    chk("Kontrolle: Schieber mit Spiel −0,05 stößt in der Nut an", 0.0 if vol_int(n2_slider(-0.05, 1), slab) > 0.05 else 1.0)
    for c, b in zip(E_CLR, ebodies):
        chk("Kassette v3 im E-Körper %s (bis zum Anschlag)" % de(c), vol_int(kass3_in_body(c), b))
    chk("Kontrolle: Kassette v3 im E-Körper bei Spiel −0,05 stößt an", 0.0 if vol_int(kass3_in_body(0), e_body(-0.05, 1)) > 0.05 else 1.0)
    hz = housing_in(k2).bounding_box()
    print("  Buchse in v2: oben z=%.2f (Schultern ab z=%.2f); in v3 unten z=%.2f, oben %.2f unter der Oberkante" % (
        hz[5], k2["zp"], k3["zf"], k3["top"] - (k3["zf"] + sd.HSG_H)))
    print("  -> %s" % ("keine Kollisionen" if not bad else "%d Kollisionen!" % bad))

    tot = sum(i_["g"] for i_ in info.values())
    from plug.roadmap import build as rb
    for prof, pr_ in rb.PROFILE.items():
        mins = sum(i_["g"] / pr_["rate"] * 60.0 + i_["layers"] * pr_["layer"] / 60.0 for i_ in info.values()) + pr_["start"]
        print("Material ≈ %.0f g, Zeit %s ≈ %.1f h" % (tot, prof, mins / 60.0))
    print("Bei deinem Drucker (Nacht 1: 47 g in 2,5 h) ≈ %.1f h" % (tot / 47.0 * 2.5))
    previews(parts, sliders, ebodies)
    write_readme(info, tot)
    zpath = os.path.join(OUT, "night2_series.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(os.listdir(OUT)):
            if f.endswith(".stl") or f == "README.txt":
                z.write(os.path.join(OUT, f), f)
    print("%s: %.0f kB" % (os.path.relpath(zpath, HERE), os.path.getsize(zpath) / 1024))
    return bad


def previews(parts, sliders, ebodies):
    import preview
    from PIL import Image
    col = dict(K="#d9b24a", C="#e3862a", N="#6bbf78", E="#c9b68a", D="#b9bfc4", FM="#8fa3b8")
    tms = {name: to_tm(man) for name, man in parts.items()}
    pos, need = SR.pack([(nm, float(t.extents[0]), float(t.extents[1])) for nm, t in tms.items()], bed=(170.0, 400.0))
    items = []
    for name, tm in tms.items():
        x, y = pos[name]
        tm.apply_translation([x - tm.bounds[0][0], y - tm.bounds[0][1], 0])
        items.append((tm, col[name.split("_")[0]]))
    preview.render(items, size=(1500, 1100), azim=-60, elev=50).save(os.path.join(PREV, "teile.png"))
    for f in ("kassette_v2.png", "bodenplatte_schnitt.png"):     # Bilder des verworfenen Entwurfs
        p = os.path.join(PREV, f)
        if os.path.exists(p):
            os.remove(p)
    # Kassette v2 und v3: schräg von oben und im Schnitt durch die Tasche (x = 0) mit Buchse
    k2, k3 = kass2_dims(), kass2_dims(True)
    tiles = []
    for fl, kk in ((False, k2), (True, k3)):
        kas = kassette2(fl, True)
        h = housing_in(kk)
        tiles.append(preview.render([(to_tm(kas), "#e3862a")], size=(700, 520), azim=-55, elev=38))
        tiles.append(preview.render([(to_tm(xcut(kas, 0.0)), "#e3862a"), (to_tm(xcut(h, 0.0)), "#f4f1e8")], size=(700, 520), azim=0, elev=0))
    sheet = Image.new("RGB", (1400, 1040), "white")
    for i, t in enumerate(tiles):
        sheet.paste(t, ((i % 2) * 700, (i // 2) * 520))
    sheet.save(os.path.join(PREV, "kassette_v2_v3.png"))
    # N: Schnitt durch die Wand (x = 8, Nut mit Luft und Schieber) und längs durch die Pin-Reihe
    n = n2_dims()
    slab, sl = n2_slab(False), sliders[1]
    kin = kassette2(centered=True).translate([0, 0, sd.FUNNEL_T])
    a = preview.render([(to_tm(xcut(slab, 8.0)), "#c9b68a"), (to_tm(xcut(sl, 8.0)), "#6bbf78")], size=(800, 520), azim=0, elev=0)
    b = preview.render([(to_tm(ycut(slab, n["ypin"])), "#c9b68a"), (to_tm(ycut(sl, n["ypin"])), "#6bbf78"),
                        (to_tm(ycut(kin, n["ypin"])), "#e3862a"), (to_tm(ycut(housing_in(kass2_dims()).translate([0, 0, sd.FUNNEL_T]), n["ypin"])), "#f4f1e8")],
                       size=(800, 520), azim=-90, elev=15)
    sheet = Image.new("RGB", (1600, 520), "white"); sheet.paste(a, (0, 0)); sheet.paste(b, (800, 0))
    sheet.save(os.path.join(PREV, "schieber_schnitt.png"))
    # E: Körper mit eingepresster Kassette v3 (Druckausrichtung), geschnitten durch die Pin-Reihe
    c = E_CLR[1]
    kk = kass3_in_body(c)
    hb = housing_in(k3).rotate([180, 0, 0]).translate([0, 0, E_STOP + k3["top"]])
    yp = -(k3["ypin"] - k3["L"] / 2)
    im = preview.render([(to_tm(ycut(ebodies[1], yp)), "#c9b68a"), (to_tm(ycut(kk, yp)), "#e3862a"), (to_tm(ycut(hb, yp)), "#f4f1e8")],
                        size=(1000, 620), azim=-70, elev=20)
    im.save(os.path.join(PREV, "einpressen_schnitt.png"))
    print("Vorschau: %s" % os.path.relpath(PREV, HERE))


def write_readme(info, tot):
    g = {k_: info[k_]["g"] for k_ in info}
    k2, k3 = kass2_dims(), kass2_dims(True)
    txt = f"""ZWEITER NACHTDRUCK (nach deinen Antworten auf plug/decision/page.html)
=======================================================================

Dateien (alle in Druckausrichtung, keine Stützen)
  K_contact_spacers_v2.stl  4 Plättchen 0,4 / 0,6 / 0,8 / 1,0 mm (E = {de(e_of(0.4))} bis {de(e_of(1.0))} mm)   ≈ {de(g['K_contact_spacers_v2'], 1)} g
  C_cassette_v2_x2.stl      2 × Kassette v2: Tasche 0,20 ohne Rippen, 0,2 höher, oben flach, runde Kante, LED 1 mm weiter weg   ≈ {de(g['C_cassette_v2_x2'], 1)} g
  N_slabs_A_B.stl           2 Platten mit Schacht 0,15 und Nut: A wie im Gebäude (mit Brücke), B umgedreht (ohne Brücke)   ≈ {de(g['N_slabs_A_B'], 1)} g
  N_sliders_v2.stl          4 Schieber, Spiel 0,20 / 0,30 / 0,40 / 0,50, Luft {de(N2_HEAD, 1)} mm darüber   ≈ {de(g['N_sliders_v2'], 1)} g
  E_cassette_v3_x2.stl      2 × Kassette v3 zum Einpressen: Boden mit Trichtern, Buchse von oben   ≈ {de(g['E_cassette_v3_x2'], 1)} g
  E_bodies.stl              3 Körper mit Schacht 0,06 / 0,09 / 0,12 für Kassette v3, Anschlagrand   ≈ {de(g['E_bodies'], 1)} g
  D_fitprobe_v7.stl         Passprobe: Tasche +1,5 zum Lötende, Körperhöhe 2,0 / 1,8 / 1,6 (Dreieck / Quadrat / Kreis)   ≈ {de(g['D_fitprobe_v7'], 1)} g
  FM_foot_gauge.stl         Fuß-Lehre für die Mulden-Ringe aus Nacht 1   ≈ {de(g['FM_foot_gauge'], 1)} g
  Zusammen ≈ {de(tot, 0)} g; bei deinem Drucker (Nacht 1: 47 g in 2,5 h) etwa {de(tot / 47.0 * 2.5, 1)} h.
  Reicht die Zeit nicht: FM weglassen, dann eine der beiden v2-Kassetten.

Kennzeichnung
  Schrift erhaben (0,5 bis 0,6 mm), Rang als Kerben in einer Kante: 1 Kerbe = engste bzw. dünnste Variante.
  K: Schrift oben, Kerben an der unteren Kante. N-Schieber: Kerben am Griffende, Schrift unten (gespiegelt, von unten lesbar).
  N-Platten: „N A“ bzw. „N B“ an der langen Seite. E-Körper: Schrift an der langen Seite, Kerben an der kurzen.
  Passprobe v7: Zahl und Zeichen unten graviert, zwei Kerben an der Kante (v6 hat keine).

Slicer wie Nacht 1 (Bambu, PLA, 0,2 mm, 3 Wände, 15 % Füllung, keine Stützen). Steckstellen haben 0,4-mm-Einführfasen,
Bettkanten der Steckteile 0,3-mm-Fasen gegen den Elefantenfuß.
  Platte N A hat über der Nut wieder eine Brücke ({de(2 * (n2_dims()['hb'] + N2_OVER), 0)} mm quer). Bitte in Bambu Studio
  „Thick bridges“ (Qualität → Brücken, „Dicke Brücken“) für dieses Teil EINSCHALTEN und die Brückenlüftung auf 100 %.
  Das ist wie im Gebäude; der Schieber hat jetzt {de(N2_HEAD, 1)} mm Luft darüber, damit eine leicht hängende Decke nicht klemmt.
  Platte N B ist dieselbe Platte umgedreht: Die Nut liegt oben offen, es gibt keine Brücke. Damit trennen wir Passung und Brücke.

So wird geprüft
  K  Winkelleiste, Plättchen auf den Körper, Buchse mit gecrimpten Kontakten bis aufs Plättchen. Durchgang beim Wackeln?
     Welches Plättchen ist das dickste, das noch stabil Kontakt gibt?
  C  Buchse von unten in die Tasche, bis sie oben an den zwei Schultern anliegt. Adern aus dem Schlitz über die runde Kante
     auf die flache Oberseite, LED-Streifen darauf (Din-Ende zur Buchse). Knicken die Adern noch?
  N  Erst in Platte B (ohne Brücke), dann in Platte A (mit Brücke): Welcher Schieber gleitet mit Fingerdruck, welcher wackelt?
     Dann Kassette v2 von oben in den Schacht, sie steht auf dem Schieber. Geht ein Pin durch alle vier Trichter?
     Unterschied A/B = Einfluss der Brücke.
  E  Buchse von oben in eine Kassette v3, bis auf den Boden. Kassette mit dem Boden voran in einen E-Körper drücken, bis
     sie am Rand anschlägt (der Rand liegt auf dem Bett, die Kassette kommt von oben). Welche hält beim Umdrehen und Schütteln,
     welche lässt sich mit dem Daumen noch herausdrücken? Mit Winkelleiste: Pins von unten durch die Trichter stecken und
     wieder abziehen, bleibt die Kassette sitzen? (Der Körper ist nur {de(P_H, 0)} mm hoch, im Gebäude wäre es mehr Länge.)
  D  Winkelleiste in jedes Feld: Liegt der Körper flach in der Tasche? Kommen die Pins gerade heraus? Welche Stufe trägt das Lötende?
  FM Fuß-Lehre in die Mulden-Ringe aus Nacht 1 (0,10 / 0,15 / 0,20), abgeschrägte Ecke zur abgeschrägten Ecke.

Maße
  Kassette v2: {de(k2['cw'], 1)} × {de(k2['L'], 1)} × {de(k2['top'], 2)} mm, Tasche {de(k2['pk_w'])} × {de(k2['pk_d'])} × {de(k2['zp'])} mm,
  Schultern je {de((k2['pk_w'] - WIRE_W) / 2)} mm breit und {de(SEAT_RISE, 1)} mm dick. Kassette v3: {de(k3['cw'], 1)} × {de(k3['L'], 1)} × {de(k3['top'], 2)} mm.
"""
    with open(os.path.join(OUT, "README.txt"), "w", encoding="utf-8") as f:
        f.write(txt)


if __name__ == "__main__":
    import sys
    sys.exit(1 if main() else 0)
