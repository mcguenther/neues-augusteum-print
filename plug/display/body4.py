"""Display-Körper E4 (Plan 3): Kopf ganz über der Platte, Hals = Halter der Kassette, Rückenkeil mit rundem Kabelraum und schrägem Rückdeckel.

Lokaler Rahmen: x = 0 an der Ostfläche des Körpers (Display schaut nach +x), nach Westen negativ; y quer, Mitte 0; z = 0 Plattenoberfläche.
Erzeugt Maße (`dims`), 2D-Profile (`profiles`) und Volumenkörper (`parts`, manifold3d) aller Teile für die Ansichten.
Alle Maße sind Planwerte, nichts davon ist gedruckt.
"""
import math

import manifold3d as m3d
import numpy as np
from shapely.geometry import Polygon, box as sbox
from shapely.ops import unary_union

from plug import geom as g
from plug.display import layout as L
from plug.display import params as D

P = D.DISP


def dims():
    d = {}
    d["W"] = L.W_FOOT                                         # Breite des Kopfs (y)
    d["NW"] = D.KASS_W + 2 * D.WALL                           # Breite des Halses (y)
    d["KD"] = L.KD                                            # Tiefe des Halses (x) = Schacht + Wände
    d["mb"] = D.WIN_BOTTOM - L.BELOW_WINDOW                   # Unterkante der Platine
    d["z_hb"] = d["mb"] - D.FLOOR_T                           # Unterkante des Kopfs über der Platte
    d["z_top"] = d["mb"] + P["pcb_h"] + D.CLR + D.TOP_CAP     # Oberkante
    d["wb"], d["wt"] = D.WIN_BOTTOM, D.WIN_BOTTOM + L.WIN_H
    d["slot_t"] = P["mod_t"] + 2 * D.CLR
    d["x_blende"] = -D.BLENDE_T                               # Rückseite der Frontblende
    d["x_slot1"] = d["x_blende"]
    d["x_slot0"] = d["x_slot1"] - d["slot_t"]
    d["x_back"] = d["x_slot0"] - D.BACK                       # Rückseite der Rückwand
    d["x_mf"] = -(D.BLENDE_T + D.CLR)                         # Glasfront des Moduls
    d["x_pcb0"], d["x_pcb1"] = d["x_mf"] - D.GLASS_T - P["pcb_t"], d["x_mf"] - D.GLASS_T     # Platine (x_pcb1 = Vorderseite)
    d["x_hdr"] = d["x_pcb0"] - P["hdr_t"]                     # Rückseite des Header-Kunststoffs
    d["x_tip"] = d["x_mf"] - D.PIN_TIP                        # Stiftspitzen
    d["x_be"] = d["x_tip"] - D.PIN_CLEAR                      # Ostkante des Halses
    d["x_bw"] = d["x_be"] - d["KD"]                           # Westkante des Halses = Tiefe des Körpers
    d["pe"] = -(d["x_be"] + d["x_bw"]) / 2                    # Pin-Reihe / Mitte der Kassette von der Ostfläche
    d["depth"] = -d["x_bw"]
    d["x_s0"], d["x_s1"] = -(d["pe"] + D.KASS_D / 2), -(d["pe"] - D.KASS_D / 2)             # Schacht
    d["foot"] = -14.2
    d["z_cass"] = D.KASS_TOP
    d["z_rear"] = D.KASS_TOP + D.AIR + D.LID_T                # Oberkante hinten über der Kassette (4,5 Luft plus Deckel)
    d["z_pins"] = d["mb"] + P["hdr_edge"]
    d["wall"] = D.WALL
    return d


def profile_side(d):
    """Außenprofil in (x, z): Front senkrecht, oben der Kopf, dahinter die Schräge vom Kopfdach hinunter zur Oberkante über der Kassette."""
    return [(0.0, d["z_hb"]), (0.0, d["z_top"]), (d["x_back"], d["z_top"]), (d["x_bw"], d["z_rear"]), (d["x_bw"], d["z_hb"])]


def profile_plan(d):
    """Grundriss in (x, y): Kopf in voller Breite, dahinter Kante für Kante schmaler bis zur Breite der Kassette."""
    w, n = d["W"] / 2, d["NW"] / 2
    return [(0.0, -w), (0.0, w), (d["x_back"], w), (d["x_be"], n), (d["x_bw"], n), (d["x_bw"], -n), (d["x_be"], -n), (d["x_back"], -w)]


def chamber_poly(d, r=None):
    """Kabelkammer in der Biegeebene (x, z): hinter der Rückwand, unter der Schräge (Wand 1,2), über Kassette und Boden; Innenkanten gerundet."""
    r = D.ROUND_R if r is None else r
    prof = Polygon(profile_side(d))
    inner = prof.buffer(-D.WALL, join_style=2)
    c = inner.intersection(sbox(d["x_bw"], d["z_hb"], d["x_back"], d["z_top"]))
    c = c.difference(sbox(d["x_bw"] - 1, d["z_hb"] - 1, d["x_be"], d["z_cass"]))                      # über der Kassette bis zur Oberkante; der Schacht ist anders
    c = c.difference(sbox(d["x_bw"] - 1, d["z_hb"] - 1, d["x_back"] + 1, d["mb"]))                    # Boden bis zur Plattenunterkante
    c = c.buffer(-r).buffer(r)
    if c.geom_type != "Polygon":
        c = max(c.geoms, key=lambda q: q.area)
    return c


def lid_poly(d):
    """Der Rückdeckel in (x, z): die schräge Wand zwischen der Außenschräge und dem Innenraum (Parallelogramm, 1,2 dick)."""
    prof = Polygon(profile_side(d))
    inner = prof.buffer(-D.WALL, join_style=2)
    band = prof.difference(inner)
    band = band.intersection(sbox(d["x_bw"] - 0.01, d["z_rear"] - 3.0, d["x_back"] + 0.01, d["z_top"] + 1))
    # nur die Schrägwand, ohne Rück- und Kopfwand
    ax, az = d["x_back"], d["z_top"]
    bx, bz = d["x_bw"], d["z_rear"]
    nx, nz = (bz - az), -(bx - ax)                              # Normale der Schräge, nach oben/Westen
    l = math.hypot(nx, nz)
    nx, nz = nx / l, nz / l
    if nz < 0:
        nx, nz = -nx, -nz
    t = D.WALL
    # Parallelogramm zwischen den Endpunkten der Schräge, außen = Schräge, innen = um 1,2 versetzt
    pts = [(ax, az), (bx, bz), (bx - nx * t * 0 - nx * t, bz - nz * t), (ax - nx * t, az - nz * t)]
    return pts, (nx, nz)


def _cs(poly_pts):
    return m3d.CrossSection([g.ccw([(float(x), float(y)) for x, y in poly_pts])])


def _poly_cs(poly):
    return _cs(list(poly.exterior.coords)[:-1])


def rounded_rect(y0, y1, z0, z1, r, n=8):
    return Polygon(sbox(y0 + r, z0 + r, y1 - r, z1 - r).buffer(r, quad_segs=n).exterior.coords)


def parts(d=None):
    """Volumenkörper aller Teile (manifold3d, Weltlage: x Osten, z oben) und Hilfsdaten für die Ansicht."""
    d = d or dims()
    side = g.prism_y(profile_side(d), -50.0, 50.0)
    plan = g.ext(_cs(profile_plan(d)), d["z_hb"] - 0.01, d["z_top"] + 0.01)
    env = plan ^ side
    # Hals: Säule von der Fußunterkante mit Fase (wie bei den Gebäuden) bis in den Kopf
    ch = D.FOOT_CH
    cx = (d["x_be"] + d["x_bw"]) / 2
    foot = g.union([g.frustum(d["KD"] - 2 * ch, d["NW"] - 2 * ch, d["foot"], d["foot"] + ch, ch, cx=cx),
                    g.box(d["x_bw"], d["x_be"], -d["NW"] / 2, d["NW"] / 2, d["foot"] + ch - 0.01, d["z_hb"] + 1.0)])
    body = env + foot
    # Modultasche: von vorn offen, Tiefe = Modul plus Spiel, Höhe bis unter das Kopfdach
    hw = P["pcb_w"] / 2 + D.CLR
    pocket = g.box(d["x_slot0"], 0.05, -hw, hw, d["mb"], d["mb"] + P["pcb_h"] + D.CLR)
    # Kabelfenster in der Rückwand mit gerundeten Ecken (Pins und Header gehen hindurch)
    win = rounded_rect(-D.SLIT_W / 2, D.SLIT_W / 2, d["mb"], d["mb"] + 8.0, 1.5)
    window = g.prism_x(list(win.exterior.coords)[:-1], d["x_back"] - 0.05, d["x_slot0"] + 0.05)
    # Kammer: Profil gerundet, quer so breit wie der Schacht
    ch_poly = chamber_poly(d)
    chamber = g.prism_y(list(ch_poly.exterior.coords)[:-1], -D.KASS_W / 2, D.KASS_W / 2)
    # Schacht für die Kassette mit Einführfase am Fuß und Anschlag oben
    sx = (d["x_s0"] + d["x_s1"]) / 2
    shaft = g.union([g.box(d["x_s0"], d["x_s1"], -D.KASS_W / 2, D.KASS_W / 2, d["foot"] - 0.01, d["z_cass"] + 0.3),
                     g.frustum(D.KASS_D, D.KASS_W, d["foot"] - 0.01, d["foot"] + D.FOOT_CH * 0.5, D.FOOT_CH * 0.5, cx=sx)])
    # Öffnung für die Adern über dem Anschlag
    gap = g.box(d["x_s0"] + 1.2, d["x_s1"] - 1.2, -5.0, 5.0, d["z_cass"] - 0.9, d["z_cass"] + 1.0)
    # Rückdeckel: Öffnung im Körper (mit Spiel), Deckel selbst
    lid_pts, normal = lid_poly(d)
    lid = g.prism_y(lid_pts, -D.LID_W / 2, D.LID_W / 2)
    lid_cut = g.prism_y(lid_pts, -D.LID_W / 2 - D.SPILL, D.LID_W / 2 + D.SPILL)
    # die Öffnung im Körper reicht von der Schrägwand bis in die Kammer (Kammer ist darunter schon frei)
    front_rebate = g.box(d["x_blende"], 0.1, -d["W"] / 2 - 0.1, d["W"] / 2 + 0.1, d["z_hb"] - 0.1, d["z_top"] + 0.1)      # die Frontblende steht vor dem Körper
    body = body - pocket - window - chamber - shaft - gap - lid_cut - front_rebate
    lid = lid ^ env
    # Frontblende: liegt in Ost-Fläche, Fenster als Loch
    wb, wt = d["wb"], d["wt"]
    wy = P["aa_w"] / 2 + D.WINDOW_MARGIN
    blende = g.box(d["x_blende"], 0.0, -d["W"] / 2, d["W"] / 2, d["z_hb"], d["z_top"]) - g.box(d["x_blende"] - 0.05, 0.05, -wy, wy, wb, wt)
    # Kassette (vereinfacht) und Modul
    cas = g.box(d["x_s0"] + 0.06, d["x_s1"] - 0.06, -D.KASS_W / 2 + 0.06, D.KASS_W / 2 - 0.06, d["foot"], d["z_cass"])
    mb = d["mb"]
    glass_z0 = mb + P["pcb_h"] - 3.3 - P["panel_h"]
    pcb = g.box(d["x_pcb0"], d["x_pcb1"], -P["pcb_w"] / 2, P["pcb_w"] / 2, mb, mb + P["pcb_h"]) - \
        g.box(d["x_pcb0"] - 0.05, d["x_pcb1"] + 0.05, -P["notch_w"] / 2, P["notch_w"] / 2, mb + P["pcb_h"] - P["notch_d"], mb + P["pcb_h"] + 0.1)
    glass = g.box(d["x_mf"] - D.GLASS_T, d["x_mf"], -P["panel_w"] / 2, P["panel_w"] / 2, glass_z0, glass_z0 + P["panel_h"])
    aa = g.box(d["x_mf"] - 0.02, d["x_mf"] + 0.05, -P["aa_w"] / 2, P["aa_w"] / 2, mb + P["aa_bottom"], mb + P["aa_bottom"] + P["aa_h"])
    hdr = g.box(d["x_hdr"], d["x_pcb0"], -4 * P["hdr_pitch"] / 2, 4 * P["hdr_pitch"] / 2, d["z_pins"] - 1.27, d["z_pins"] + 1.27)
    pins = g.union([g.box(d["x_tip"], d["x_pcb0"] - 0.1, (i - 1.5) * P["hdr_pitch"] - 0.32, (i - 1.5) * P["hdr_pitch"] + 0.32, d["z_pins"] - 0.32, d["z_pins"] + 0.32)
                    for i in range(4)])
    # Platte (Ausschnitt) mit Mulde, Pin-Löchern und Winkelleiste darunter
    pe = d["pe"]
    pl = g.box(-62.0, 4.1, -45.0, 45.0, -14.6, 0.0)
    mulde = g.box(d["x_bw"] - 0.1, d["x_be"] + 0.1, -d["NW"] / 2 - 0.1, d["NW"] / 2 + 0.1, -14.2, 0.1)
    holes = g.union([g.cyl(0.7, -15.0, -13.9, cx=-pe, cy=(i - 1.5) * 2.54) for i in range(4)])
    plate = pl - mulde - holes
    lei = g.box(-pe - 1.0, -pe + 1.0, -5.45, 5.45, -16.6, -14.6)
    lpins = g.union([g.box(-pe - 0.32, -pe + 0.32, (i - 1.5) * 2.54 - 0.32, (i - 1.5) * 2.54 + 0.32, -16.0, -8.9) for i in range(4)])
    tails = g.union([g.box(-pe - 6.3, -pe, (i - 1.5) * 2.54 - 0.32, (i - 1.5) * 2.54 + 0.32, -16.0, -15.4) for i in range(4)])
    # Weg der Adern (x, z) mit Schleife in der Kammer, von der Kassettenoberkante zu den Stiftspitzen
    wire = [(cx, d["z_cass"]), (cx - 0.7, 7.5), (cx + 1.3, 12.5), (cx + 5.8, 16.5), (cx + 9.5, 13.0), (cx + 9.8, 8.0), (cx + 8.3, 4.8), (d["x_tip"] - 0.6, d["z_pins"])]
    return dict(body=body, lid=lid, blende=blende, cassette=cas, pcb=pcb, glass=glass, aa=aa, header=hdr, pins=pins, plate=plate,
                leiste=lei + lpins + tails), dict(chamber=ch_poly, wire=wire, normal=normal, lid_pts=lid_pts, d=d)
