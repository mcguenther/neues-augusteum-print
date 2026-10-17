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
from plug.testcase import variants as V

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
    d["x_fe"] = d["x_be"] + D.FOOT_EXT                         # vordere Kante des Fußes (nach Osten verlängert)
    d["win_top"] = d["z_top"] - D.WIN_TOP_GAP                  # Oberkante des Kabelfensters (Rundbogen)
    d["z_cass"] = D.KASS_TOP
    d["z_rear"] = D.KASS_TOP + D.AIR + D.LID_T                # Oberkante hinten über der Kassette (4,5 Luft plus Deckel)
    d["z_pins"] = d["mb"] + P["hdr_edge"]
    d["wall"] = D.WALL
    d["z_s"] = d["z_cass"] + D.SHAFT_EXTRA                     # Schachtdecke: darüber beginnt die 45°-Schräge des Anschlags
    d["ledge"] = ledge_depth(d)                                # Höhe der Schräge bis zur Öffnung
    d["z_ledge"] = d["z_s"] + d["ledge"] + D.DECKEL_T          # Oberseite des Anschlagrands = Boden der Kammer über dem Hals
    return d


def shaft_rect(d):
    """Schacht im Grundriss (x, y), shapely."""
    return sbox(d["x_s0"], -D.KASS_W / 2, d["x_s1"], D.KASS_W / 2)


def opening(d):
    """Öffnung über dem Anschlag (Grundriss): Aderschlitz der Kassette mit Spiel FREI_T, vereinigt mit dem Schacht um ANSCHLAG_T verkleinert."""
    k = V.dims("V2")
    sx = (d["x_s0"] + d["x_s1"]) / 2
    win = sbox(sx - k["pk_d"] / 2 - D.FREI_T, -k["slot"] / 2 - D.FREI_T, sx + k["pk_d"] / 2 + D.FREI_T, k["slot"] / 2 + D.FREI_T)
    return win.union(shaft_rect(d).buffer(-D.ANSCHLAG_T, join_style=2))


def ledge_depth(d):
    """Höhe der 45°-Schräge: so lange, bis der verkleinerte Schacht in der Öffnung liegt (Schritte 0,1 wie bei den Gebäuden)."""
    rect, win, depth = shaft_rect(d), opening(d), 0.0
    while not rect.buffer(-depth, join_style=2).difference(win).buffer(-1e-3).is_empty and depth < 6.0:
        depth += 0.1
    return round(depth, 1)


def ext_poly(poly, z0, z1):
    """shapely-Polygon (auch mit Löchern, auch Vielfaches) zwischen z0 und z1."""
    from shapely.geometry.polygon import orient
    loops = []
    for q in getattr(poly, "geoms", [poly]):
        q = orient(q, 1.0)
        loops.append([(float(x), float(y)) for x, y in q.exterior.coords][:-1])
        loops += [[(float(x), float(y)) for x, y in r.coords][:-1] for r in q.interiors]
    return g.ext(m3d.CrossSection(loops), z0, z1)


def ledge_cut(d):
    """Schnittkörper über dem Schachtende: Schräge in 0,1-mm-Stufen von der Schachtfläche auf die Öffnung, darüber die Öffnung bis in die Kammer."""
    rect, win = shaft_rect(d), opening(d)
    zs, parts, t = d["z_s"], [], 0.0
    while t < d["ledge"] - 1e-9:
        parts.append(ext_poly(rect.buffer(-(t + 0.05), join_style=2).union(win), zs + t - 0.005, zs + t + 0.105))
        t += 0.1
    parts.append(ext_poly(win, zs - 0.01, d["z_ledge"] + 0.6))
    return g.union(parts)


def profile_side(d):
    """Außenprofil in (x, z): Front senkrecht, oben der Kopf, dahinter die Schräge vom Kopfdach hinunter zur Oberkante über der Kassette."""
    return [(0.0, d["z_hb"]), (0.0, d["z_top"]), (d["x_back"], d["z_top"]), (d["x_bw"], d["z_rear"]), (d["x_bw"], d["z_hb"])]


def profile_plan(d):
    """Grundriss in (x, y): Kopf in voller Breite, dahinter Kante für Kante schmaler bis zur Breite der Kassette."""
    w, n = d["W"] / 2, d["NW"] / 2
    return [(0.0, -w), (0.0, w), (d["x_back"], w), (d["x_be"], n), (d["x_bw"], n), (d["x_bw"], -n), (d["x_be"], -n), (d["x_back"], -w)]


def foot_poly(d):
    """Grundriss des Fußes (unter dem Kopf, in der Mulde): Schachtsäule plus Verlängerung nach vorn, Kodierecke vorn Süd."""
    n = d["NW"] / 2
    xb, xf, k = d["x_bw"], d["x_fe"], D.KEY
    return [(xb, -n), (xf - k, -n), (xf, -n + k), (xf, n), (xb, n)]


def chamfered_prism(pts, z0, z1, ch):
    """Prisma über dem Grundriss `pts` (gegen den Uhrzeigersinn) mit Fase je Kante an der Unterkante z0 (45°)."""
    base = g.ext(_cs(pts), z0, z1)
    n = len(pts)
    for i in range(n):
        a, b, c = np.array(pts[i], float), np.array(pts[(i + 1) % n], float), ch[i]
        if c <= 0:
            continue
        e = b - a
        nrm = np.array([e[1], -e[0]]) / np.hypot(*e)               # Außennormale
        n3 = np.array([nrm[0], nrm[1], -1.0]) / math.sqrt(2.0)
        p0 = np.array([a[0] - nrm[0] * c, a[1] - nrm[1] * c, z0])
        base = base.trim_by_plane((-n3).tolist(), float(np.dot(-n3, p0)))
    return base


def window_poly(d):
    """Kabelfenster in (y, z): Langloch mit Rundbogen oben, unten Ecken R 1,5; vom Taschenboden bis fast unter das Kopfdach."""
    hw = D.WIN_W / 2
    z0, z1 = d["mb"], d["win_top"]
    from shapely.geometry import Point
    shape = sbox(-hw, z0, hw, z1 - hw).union(Point(0, z1 - hw).buffer(hw, quad_segs=16))
    shape = shape.buffer(-1.5).buffer(1.5, quad_segs=8)
    return shape


def chamber_plan(d):
    """Grundriss der Kammer: am Schacht so breit wie dieser, zum Kabelfenster hin bis WIN_W (bleibt innerhalb der Wand 1,2)."""
    r, f = D.KASS_W / 2, D.CHAMBER_FRONT_W / 2
    return [(d["x_bw"] - 1.0, -r), (d["x_be"], -r), (d["x_back"] + 0.05, -f), (d["x_back"] + 0.05, f), (d["x_be"], r), (d["x_bw"] - 1.0, r)]


def chamber_poly(d, r=None):
    """Kabelkammer in der Biegeebene (x, z): hinter der Rückwand, unter der Schräge (Wand 1,2), über Kassette und Boden; Innenkanten gerundet."""
    r = D.ROUND_R if r is None else r
    prof = Polygon(profile_side(d))
    inner = prof.buffer(-D.WALL, join_style=2)
    c = inner.intersection(sbox(d["x_bw"], d["z_hb"], d["x_back"], d["z_top"]))
    c = c.difference(sbox(d["x_bw"] - 1, d["z_hb"] - 1, d["x_be"], d["z_ledge"]))                     # Anschlagrand über dem Hals; die Adern gehen durch die Öffnung
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


def _xcyl(r, x0, x1, y, z, n=24):
    """Zylinder mit Achse in x von x0 nach x1 (x1 < x0 möglich), Mitte (y, z)."""
    lo, hi = min(x0, x1), max(x0, x1)
    c = m3d.Manifold.cylinder(hi - lo, r, r, n).rotate([0, 90, 0])      # Achse nach +x? (z -> x)
    bb = c.bounding_box()
    return c.translate([lo - bb[0], y, z])


def _xcone(r_lo, r_hi, x0, x1, y, z, n=24):
    """Kegelstumpf mit Achse in x: Radius r_lo bei x0 (kleineres x), r_hi bei x1."""
    c = m3d.Manifold.cylinder(x1 - x0, r_lo, r_hi, n).rotate([0, 90, 0])
    bb = c.bounding_box()
    return c.translate([x0 - bb[0], y, z])


def peg_centres(d):
    """Lage der vier Zapfen (y, z) = Befestigungslöcher des Moduls."""
    hz = [d["mb"] + P["hole_edge"], d["mb"] + P["hole_edge"] + P["hole_dy"]]
    hy = [-P["hole_dx"] / 2, P["hole_dx"] / 2]
    return [(y, z) for y in hy for z in hz]


def peg_hole(d, y, z):
    """Sackloch in der Rückwand von der Taschenrückseite aus, mit Einführfase am Eingang."""
    r, x0 = D.PEG_HOLE_D / 2, d["x_slot0"]
    return _xcyl(r, x0 + 0.05, x0 - D.PEG_HOLE_T, y, z) + _xcone(r, r + D.PEG_HOLE_CH, x0 - D.PEG_HOLE_CH, x0 + 0.05, y, z)


def peg(d, y, z, dia=None):
    """Zapfen der Frontblende von der Rückseite der Blende bis kurz vor den Grund des Sacklochs, Spitze gefast."""
    r = (dia or D.PEG_D) / 2
    x_tip = d["x_slot0"] - D.PEG_HOLE_T + D.PEG_TIP_GAP
    return _xcyl(r, d["x_blende"] + 0.05, x_tip + D.PEG_TAPER_L, y, z) + _xcone(D.PEG_TIP_D / 2, r, x_tip, x_tip + D.PEG_TAPER_L + 0.01, y, z)


def make_blende(d, dia=None, kappe=False):
    """Frontblende (Weltlage) mit Sichtfenster und vier Zapfen vom Durchmesser dia (Standard PEG_D)."""
    wy = P["aa_w"] / 2 + D.WINDOW_MARGIN
    blende = g.box(d["x_blende"], 0.0, -d["W"] / 2, d["W"] / 2, d["z_hb"], d["z_top"]) - g.box(d["x_blende"] - 0.05, 0.05, -wy, wy, d["wb"], d["wt"])
    if kappe:
        top = d["mb"] + P["pcb_h"] + D.CLR                      # Oberkante der Tasche
        lip = g.box(d["x_slot0"] - 1.0, d["x_blende"] + 0.01, -d["W"] / 2, d["W"] / 2, top, top + D.LIP_T)
        blende = blende - g.box(d["x_blende"] - 1, 1, -500, 500, top + D.LIP_T, 500) + lip      # Blende endet oben mit der Lippe
    return blende + g.union([peg(d, y, z, dia) for y, z in peg_centres(d)])


def lid_frame(d):
    """Punktfunktion P(u, v) in (x, z): u entlang der Schräge vom oberen Ende (Kopfdach) nach unten, v von außen (0) nach innen (Deckeldicke)."""
    pts, (nx, nz) = lid_poly(d)
    ax, az = pts[0]
    bx, bz = pts[1]
    L = math.hypot(bx - ax, bz - az)
    dx, dz = (bx - ax) / L, (bz - az) / L
    return (lambda u, v: (ax + u * dx - v * nx, az + u * dz - v * nz)), L


def _cs(poly_pts):
    return m3d.CrossSection([g.ccw([(float(x), float(y)) for x, y in poly_pts])])


def _poly_cs(poly):
    return _cs(list(poly.exterior.coords)[:-1])


def rounded_rect(y0, y1, z0, z1, r, n=8):
    return Polygon(sbox(y0 + r, z0 + r, y1 - r, z1 - r).buffer(r, quad_segs=n).exterior.coords)


def kassette_k0(d):
    """Kassette K0: Unterbau der V2 (plug/testcase/variants.py) ohne Blatt, in der Lage im Schacht (Weltlage; lokal x -> y, lokal y -> x)."""
    k = V.dims("V2")
    m = V.kassette("V2").trim_by_plane([0, 0, -1], -k["z_b"])          # Blatt abschneiden: nur Unterbau bis zur Schulterfläche
    m = m.translate([0.0, -k["depth"] / 2, 0.0]).rotate([0.0, 0.0, 90.0])
    return m.translate([(d["x_s0"] + d["x_s1"]) / 2, 0.0, d["foot"]])


def parts(d=None):
    """Volumenkörper aller Teile (manifold3d, Weltlage: x Osten, z oben) und Hilfsdaten für die Ansicht."""
    d = d or dims()
    side = g.prism_y(profile_side(d), -50.0, 50.0)
    plan = g.ext(_cs(profile_plan(d)), d["z_hb"] - 0.01, d["z_top"] + 0.01)
    env = plan ^ side
    # Hals: Säule von der Fußunterkante mit Fase (wie bei den Gebäuden) bis in den Kopf
    fp = foot_poly(d)
    cx = (d["x_be"] + d["x_bw"]) / 2
    ch_edges = [D.FOOT_CH_SIDE, D.FOOT_CH_FRONT, D.FOOT_CH_FRONT, D.FOOT_CH_SIDE, D.FOOT_CH_SIDE]     # Süd, Kodierecke, Ost, Nord, West
    foot = chamfered_prism(fp, d["foot"], d["z_hb"] + 1.0, ch_edges)
    body = env + foot
    # Modultasche: von vorn offen, Tiefe = Modul plus Spiel, Höhe bis unter das Kopfdach
    hw = P["pcb_w"] / 2 + D.CLR_W
    pocket = g.box(d["x_slot0"], 0.05, -hw, hw, d["mb"], d["mb"] + P["pcb_h"] + D.CLR)
    # Kabelfenster in der Rückwand mit gerundeten Ecken (Pins und Header gehen hindurch)
    win = window_poly(d)
    window = g.prism_x(list(win.exterior.coords)[:-1], d["x_back"] - 0.05, d["x_slot0"] + 0.05)
    # Kammer: Profil gerundet, quer so breit wie der Schacht
    ch_poly = chamber_poly(d)
    chamber = g.prism_y(list(ch_poly.exterior.coords)[:-1], -D.CHAMBER_FRONT_W / 2, D.CHAMBER_FRONT_W / 2) ^ \
        g.ext(_cs(chamber_plan(d)), d["z_hb"] - 1.0, d["z_top"] + 1.0)
    # Schacht für die Kassette mit Einführfase am Fuß; oben der Anschlag (45°-Schräge) und die Öffnung für die Adern
    sx = (d["x_s0"] + d["x_s1"]) / 2
    shaft = g.union([g.box(d["x_s0"], d["x_s1"], -D.KASS_W / 2, D.KASS_W / 2, d["foot"] - 0.01, d["z_s"]),
                     g.frustum(D.KASS_D + 2 * D.ENTRY_CH, D.KASS_W + 2 * D.ENTRY_CH, d["foot"] - 0.01, d["foot"] + D.ENTRY_CH, -D.ENTRY_CH, cx=sx)])
    ledge = ledge_cut(d)
    # Rückdeckel: Öffnung im Körper (mit Spiel), Deckel selbst
    lid_pts, normal = lid_poly(d)
    lid = g.prism_y(lid_pts, -D.LID_W / 2, D.LID_W / 2)
    lid_cut = g.prism_y(lid_pts, -D.LID_W / 2 - D.SPILL, D.LID_W / 2 + D.SPILL)
    # Rastnasen am Rand des Deckels und passende Nuten im Körper (je Seite zwei)
    Pf, Lslope = lid_frame(d)
    bu, bt, bh, bl = D.BUMP["u"], D.BUMP["t"], D.BUMP["h"], D.BUMP["len"]
    v0 = (D.WALL - bt) / 2
    bumps, grooves = [], []
    for u0 in bu:
        for sgn in (-1, 1):
            q = [Pf(u0, v0), Pf(u0 + bl, v0), Pf(u0 + bl, v0 + bt), Pf(u0, v0 + bt)]
            y0, y1 = sorted((sgn * (D.LID_W / 2 - 0.01), sgn * (D.LID_W / 2 + bh)))
            bumps.append(g.prism_y(q, y0, y1))
            qg = [Pf(u0 - 0.3, v0 - 0.15), Pf(u0 + bl + 0.3, v0 - 0.15), Pf(u0 + bl + 0.3, v0 + bt + 0.15), Pf(u0 - 0.3, v0 + bt + 0.15)]
            yg0, yg1 = sorted((sgn * (D.LID_W / 2 + D.SPILL - 0.01), sgn * (D.LID_W / 2 + D.BUMP["groove"])))
            grooves.append(g.prism_y(qg, yg0, yg1))
    lid = lid + g.union(bumps)
    lid_cut = lid_cut + g.union(grooves)
    # die Öffnung im Körper reicht von der Schrägwand bis in die Kammer (Kammer ist darunter schon frei)
    front_rebate = g.box(d["x_blende"], 0.1, -d["W"] / 2 - 0.1, d["W"] / 2 + 0.1, d["z_hb"] - 0.1, d["z_top"] + 0.1)      # die Frontblende steht vor dem Körper
    # Sacklöcher für die Zapfen der Frontblende (Lage der Befestigungslöcher des Moduls)
    hy = [-P["hole_dx"] / 2, P["hole_dx"] / 2]
    peg_holes = g.union([peg_hole(d, y, z) for y, z in peg_centres(d)])
    body = body - pocket - window - chamber - shaft - ledge - lid_cut - front_rebate - peg_holes
    lid = lid ^ env
    # Frontblende: liegt in Ost-Fläche, Fenster als Loch
    blende = make_blende(d)
    # Kassette (vereinfacht) und Modul
    cas = kassette_k0(d)
    mb = d["mb"]
    glass_z0 = mb + 6.7                                   # Glas sitzt 6,7 über der Pin-Kante (Foto, Platine 33,0 hoch: 33,0 - 3,3 - 23,0)
    pcb = g.box(d["x_pcb0"], d["x_pcb1"], -P["pcb_w"] / 2, P["pcb_w"] / 2, mb, mb + P["pcb_h"]) - \
        g.box(d["x_pcb0"] - 0.05, d["x_pcb1"] + 0.05, -P["notch_w"] / 2, P["notch_w"] / 2, mb + P["pcb_h"] - P["notch_d"], mb + P["pcb_h"] + 0.1)
    pcb = pcb - g.union([_xcyl(P["hole_d"] / 2, d["x_pcb0"] - 0.1, d["x_pcb1"] + 0.1, y, z) for y in (-P["hole_dx"] / 2, P["hole_dx"] / 2)
                         for z in (mb + P["hole_edge"], mb + P["hole_edge"] + P["hole_dy"])])
    glass = g.box(d["x_mf"] - D.GLASS_T, d["x_mf"], -P["panel_w"] / 2, P["panel_w"] / 2, glass_z0, glass_z0 + P["panel_h"])
    aa = g.box(d["x_mf"] - 0.02, d["x_mf"] + 0.05, -P["aa_w"] / 2, P["aa_w"] / 2, mb + P["aa_bottom"], mb + P["aa_bottom"] + P["aa_h"])
    hdr = g.box(d["x_hdr"], d["x_pcb0"], -4 * P["hdr_pitch"] / 2, 4 * P["hdr_pitch"] / 2, d["z_pins"] - 1.27, d["z_pins"] + 1.27)
    pins = g.union([g.box(d["x_tip"], d["x_pcb0"] - 0.1, (i - 1.5) * P["hdr_pitch"] - 0.32, (i - 1.5) * P["hdr_pitch"] + 0.32, d["z_pins"] - 0.32, d["z_pins"] + 0.32)
                    for i in range(4)])
    # Platte (Ausschnitt) mit Mulde, Pin-Löchern und Winkelleiste darunter
    pe = d["pe"]
    pl = g.box(-62.0, 4.1, -45.0, 45.0, -14.6, 0.0)
    mu_poly = Polygon(foot_poly(d)).buffer(D.CLR_MULDE, join_style=2)
    mulde = g.ext(_poly_cs(mu_poly), -14.2, 0.1)
    holes = g.union([g.cyl(0.7, -15.0, -13.9, cx=-pe, cy=(i - 1.5) * 2.54) for i in range(4)])
    plate = pl - mulde - holes
    lei = g.box(-pe - 1.0, -pe + 1.0, -5.45, 5.45, -16.6, -14.6)
    lpins = g.union([g.box(-pe - 0.32, -pe + 0.32, (i - 1.5) * 2.54 - 0.32, (i - 1.5) * 2.54 + 0.32, -16.0, -8.9) for i in range(4)])
    tails = g.union([g.box(-pe - 6.3, -pe, (i - 1.5) * 2.54 - 0.32, (i - 1.5) * 2.54 + 0.32, -16.0, -15.4) for i in range(4)])
    # Weg der Adern (x, z) mit Schleife in der Kammer, von der Kassettenoberkante zu den Stiftspitzen
    wire = [(cx, d["z_cass"]), (cx - 0.7, 6.5), (cx + 1.3, 10.5), (cx + 5.8, 15.5), (cx + 9.5, 12.5), (cx + 9.8, 8.0), (cx + 8.3, 4.8), (d["x_tip"] - 0.6, d["z_pins"])]
    return dict(body=body, lid=lid, blende=blende, cassette=cas, pcb=pcb, glass=glass, aa=aa, header=hdr, pins=pins, plate=plate,
                leiste=lei + lpins + tails), dict(chamber=ch_poly, wire=wire, normal=normal, lid_pts=lid_pts, d=d)
