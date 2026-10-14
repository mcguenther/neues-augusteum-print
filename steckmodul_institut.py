#!/usr/bin/env python3
"""Institutsgebäude mit Kassette (Dupont-Plan B, Rückfallebene) und Dock A in der Platte.

Baut auf steckmodul_dupont.py auf (Kaufteile, Höhenkette, Kassette, Schieber-Idee), nutzt aber
den echten Grundriss des Institutsgebäudes (Laserscan, siehe generate.py):

  * Gebäude: sichtbarer Körper aus dem Laserscan + Fuß (Grundriss nach unten verlängert, unten
    gefast) + Lichtkammer (Wand 1,2 mm, Dach 1,2 mm, folgt den Dachhöhen) + Lichtfenster.
  * Kassette: Buchse, Adern und LED-Streifen liegen auf einer gedruckten Kassette. Die Ablage für
    den Streifen ist großzügig (SEAT_W × SEAT_L), damit nicht nur ein Streifenstück passt.
    Die Kassette wird von unten in einen Schacht im Fuß geschoben.
  * Schieber (Trichterplatte): gleitet quer durch die lange Wand in eine Schwalbenschwanz-Nut und
    hält die Kassette. Solange das Gebäude in der Mulde steckt, sperrt die Muldenwand den Schieber.
  * Platte: Mulde nach dem Fußumriss, Dock A (abgewinkelte Stiftleiste), Federzunge in der langen
    Muldenwand, Deckel mit Stempel.

Koordinaten wie im Dupont-Plan: z = 0 ist die Plattenoberseite = Unterkante des sichtbaren Gebäudes.
Das Gebäude ist so gedreht, dass seine lange gerade Wand bei +x liegt und die Längsachse in y.
Die Pin-Reihe läuft entlang x bei (PX, PY).

Aufruf:
    python3 steckmodul_institut.py      # STL, Prüfbericht, Vorschau, stecker/institut/daten.json
    python3 stecker/institut/baue_ansicht.py
"""
import json
import math
import os

import numpy as np
import manifold3d as m3d
import shapely
from shapely import affinity
from shapely.geometry import Point
from shapely.geometry.polygon import orient

import steckmodul_dupont as sd
from steckmodul import box, cbox, cyl, union, diff, to_tm, encode

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "stl", "steckmodul_institut")
DOC = os.path.join(HERE, "stecker", "institut")
PREV = os.path.join(HERE, "vorschau", "steckmodul_institut")

SCALE = 1000                    # Maßstab 1:1000 (bei 1:1500 ist der Hauptbalken nur etwa 15 mm breit)
SLUG = "05_institutsgebaeude"

# Großzügige LED-Ablage auf der Kassette
SEAT_W, SEAT_L = 13.0, 21.0     # Ablage: Breite (x), Länge (y) ab dem Pad-Ende nahe der Buchse
SEAT_M = 0.15                   # Spiel um die Ablage in der Bodenöffnung
STRIPS = {
    "60": dict(name="60 LED/m, 10 mm breit, 1 LED", W=10.0, L=16.7, chips=[8.35]),
    "144": dict(name="144 LED/m, 12 mm breit, 2 LEDs", W=12.0, L=13.9, chips=[3.45, 10.4]),
}

MARGIN = 6.0                    # Plattenrand um die Mulde
WIN_STEP, WIN_W, WIN_H = 6.0, 3.6, 4.5   # Lichtfenster: Abstand, Breite, Höhe
WIN_ROWS = (9.0, 15.0)    # Unterkanten der Fensterreihen über der Plattenoberseite
WIN_T = 0.4                     # Restwand im Fenster
LAYER = sd.LAYER


# --------------------------------------------------------------------------
# Gebäude laden und ausrichten
# --------------------------------------------------------------------------
def load_building():
    import generate
    solid, fp, info = generate.source_models("laserscan", 1000.0 / SCALE)[SLUG]
    fp = orient(fp.simplify(0.2, preserve_topology=True), 1.0)
    pts = list(fp.exterior.coords)[:-1]
    n = len(pts)
    L, i = max((math.dist(pts[k], pts[(k + 1) % n]), k) for k in range(n))
    p0, p1 = pts[i], pts[(i + 1) % n]
    rot = 90.0 - math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))   # längste Kante zeigt nach +y
    fp = affinity.rotate(fp, rot, origin=(0, 0))                           # CCW: Kante liegt dann bei +x
    solid = solid.rotate([0, 0, rot])
    x0, y0, x1, y1 = fp.bounds
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    fp = affinity.translate(fp, -cx, -cy)
    solid = solid.translate([-cx, -cy, 0])
    return solid, fp, dict(long_edge=L, rot=rot)


def hcs(poly):
    import generate
    return generate.cross_section(poly)


def ext(cs, z0, z1):
    return m3d.Manifold.extrude(cs, z1 - z0).translate([0, 0, z0])


def rounded(cs):
    return cs.offset(-sd.FOOT_R, m3d.JoinType.Round).offset(sd.FOOT_R, m3d.JoinType.Round)


# --------------------------------------------------------------------------
# Lage der Einheit, Maße
# --------------------------------------------------------------------------
def layout(fp):
    """Pin-Reihe (PX, PY): Mitte des Hauptbalkens auf halber Länge. Wand-x der langen Wand bei PY."""
    x0, y0, x1, y1 = fp.bounds
    py = (y0 + y1) / 2
    from shapely.geometry import LineString
    seg = fp.intersection(LineString([(x0 - 1, py), (x1 + 1, py)]))
    xa, xb = seg.bounds[0], seg.bounds[2]
    return dict(PX=(xa + xb) / 2, PY=py, xwall=xb, xwest=xa, bar=xb - xa, bbox=(x0, y0, x1, y1))


def dims():
    d = dict(sd.dims())
    HY, sock_w, sock_d = d["HY"], d["sock_w"], d["sock_d"]
    cw = max(sock_w, SEAT_W + 0.3 + 2 * sd.WALL)            # Kassettenbreite (x)
    d.update(
        cass_w=cw, cass_y0=HY - sock_d / 2, cass_y1=d["LY0"] + SEAT_L + 0.15 + sd.WALL,
        seat_w=SEAT_W, seat_l=SEAT_L, seat_x0=-SEAT_W / 2, seat_x1=SEAT_W / 2,
        seat_y0=d["LY0"] - 0.15, seat_y1=d["LY0"] + SEAT_L)
    d["z_lt"] = sd.layer_down(d["z_bend"] - 3.0)             # nur Dock A: Platte so dünn wie möglich
    d["z_lb"] = d["z_lt"] - sd.LID_T
    d["plate_t"] = -d["z_lb"]
    d["cass_len"] = d["cass_y1"] - d["cass_y0"]
    d["hb"] = d["cass_len"] / 2 + 1.5                        # halbe Schieberbreite (unten, ohne Spiel)
    d["x_in"] = -(cw / 2 + sd.KASS_CLR + 1.0)                # innere Kante der Nut (lokales x)
    return d


# --------------------------------------------------------------------------
# Fuß und Mulde aus dem Grundriss (Fasen in Schichtstufen von 0,2 mm)
# --------------------------------------------------------------------------
def foot_solid(cs, F):
    r = rounded(cs)
    n = int(round(sd.CH_F / LAYER))
    parts = [ext(r.offset(-(sd.CH_F - LAYER * (k + 0.5)), m3d.JoinType.Round), -F + LAYER * k,
                 -F + LAYER * (k + 1) + 0.01) for k in range(n)]
    parts.append(ext(r, -F + sd.CH_F, 0.01))
    return union(parts)


def pocket_cuts(cs, F):
    r = rounded(cs)
    zb = -sd.CH_P - sd.BAND
    out = [ext(r.offset(sd.CLR + sd.RELIEF, m3d.JoinType.Round), -F, zb + 0.01),
           ext(r.offset(sd.CLR, m3d.JoinType.Round), zb, -sd.CH_P + 0.01)]
    n = int(round(sd.CH_P / LAYER))
    for k in range(n):
        out.append(ext(r.offset(sd.CLR + LAYER * (k + 0.5), m3d.JoinType.Round), -sd.CH_P + LAYER * k,
                       -sd.CH_P + LAYER * (k + 1) + 0.01))
    out.append(ext(r.offset(sd.CLR + sd.CH_P + 0.2, m3d.JoinType.Round), -0.01, 0.01 + 0.2))
    return out


def chamber(solid, z0, H):
    """Lichtkammer: je Höhe der um die Wandstärke geschrumpfte Querschnitt des Gebäudes in 1,2 mm
    höherer Lage, damit Wand und Dach überall mindestens 1,2 mm dick bleiben."""
    slabs, z = [], z0
    while z < H - sd.ROOF - 0.2:
        cs = solid.slice(z + sd.ROOF + 0.1).offset(-sd.SHELL, m3d.JoinType.Round)
        if cs.area() > 1.0:
            slabs.append(ext(cs, z, z + LAYER + 0.01))
        z += LAYER
    return union(slabs)


def light_windows(fp):
    """Fenster als auf WIN_T abgedünnte Wandstellen entlang der geraden Wände."""
    cs_fp = hcs(fp)
    ring = cs_fp.offset(-WIN_T, m3d.JoinType.Round) - cs_fp.offset(-sd.SHELL - 0.01, m3d.JoinType.Round)
    pts = list(orient(fp, 1.0).exterior.coords)[:-1]
    rects = []
    for i in range(len(pts)):
        a, b = np.array(pts[i]), np.array(pts[(i + 1) % len(pts)])
        L = float(np.linalg.norm(b - a))
        if L < 10.0:
            continue
        u = (b - a) / L
        nrm = np.array([-u[1], u[0]])                        # nach innen (CCW)
        n = int((L - 4.0) // WIN_STEP) + 1
        t0 = (L - (n - 1) * WIN_STEP) / 2
        for k in range(n):
            c = a + u * (t0 + k * WIN_STEP) + nrm * 0.8
            hu, hn = WIN_W / 2, 0.6
            corners = [c - u * hu - nrm * hn, c + u * hu - nrm * hn, c + u * hu + nrm * hn, c - u * hu + nrm * hn]
            rects.append(m3d.CrossSection([[tuple(p) for p in corners]]))
    mask = m3d.CrossSection.batch_boolean(rects, m3d.OpType.Add)
    cutcs = ring ^ mask
    return [ext(cutcs, z0, z0 + WIN_H) for z0 in WIN_ROWS]


# --------------------------------------------------------------------------
# Kassette, Schieber
# --------------------------------------------------------------------------
def cass_outline(d):
    w = d["cass_w"] / 2
    return -w, w, d["cass_y0"], d["cass_y1"]


def kassette(d):
    """Wie sd.kassette(), aber mit großzügiger Ablage für den LED-Streifen und breiterem Körper."""
    HY, zk0 = d["HY"], -d["F"] + sd.FUNNEL_T
    x0, x1, y0, y1 = cass_outline(d)
    body = box(x0, x1, y0, y1, zk0, d["z_kt"])
    body = union([body, cbox(d["sock_w"], d["sock_d"], zk0, d["z_kceil"], cy=HY)])
    cut = [cbox(d["pk_w"], d["pk_d"], zk0 - 0.01, d["z_pt"], cy=HY),
           cbox(abs(sd.pin_x()[0]) * 2 + sd.WIRE_D + 0.3, sd.WIRE_D + 0.3, d["z_pt"] - 0.01, d["z_kceil"] + 0.01, cy=HY)]
    y_g0 = HY + d["sock_d"] / 2 + 0.2
    gx = sorted([sd.pin_x()[3], sd.pad_x("GND")])
    cut.append(box(gx[0] - 0.9, gx[1] + 0.9, y_g0, y_g0 + sd.GROOVE[0], d["z_kt"] - sd.GROOVE[1], d["z_kt"] + 0.01))
    cut.append(box(d["seat_x0"], d["seat_x1"], d["seat_y0"], d["seat_y1"], d["z_s"], d["z_kt"] + 0.01))   # Ablage
    xw = abs(sd.pin_x()[0]) + sd.WIRE_D / 2 + 0.6
    cut.append(box(-xw, xw, HY - 0.6, HY + d["sock_d"] / 2 + 0.01, d["z_kceil"] - 0.6, d["z_kceil"] + 0.01))
    k = diff(body, *cut)
    return union([k] + sd.unit_ribs())


def slider_prof(d, clr, z_extra=0.0):
    F, hb, T = d["F"], d["hb"] - clr, sd.FUNNEL_T
    yc = (d["cass_y0"] + d["cass_y1"]) / 2
    return [(yc - hb, -F - z_extra), (yc + hb, -F - z_extra), (yc + hb + T, -F + T), (yc - hb - T, -F + T)]


def slider(d, xout, foot_local):
    """Schieber (Trichterplatte), gleitet entlang +x aus der langen Wand heraus."""
    k = sd.prism_x(slider_prof(d, sd.KEY_CLR), d["x_in"], xout + 1.0)
    k = k ^ foot_local
    k = diff(k, *sd.funnel_holes(-d["F"], d["HY"]))
    k = diff(k, cbox(1.0, 6.0, -d["F"] - 0.01, -d["F"] + 0.5, cx=xout - 0.2, cy=(d["cass_y0"] + d["cass_y1"]) / 2))
    return k


# --------------------------------------------------------------------------
# Zusammenbau in Weltkoordinaten
# --------------------------------------------------------------------------
def tf(L):
    """Lokal (Pin-Reihe bei x=0, y=HY) -> Welt."""
    d = sd.dims()
    return lambda m: m.translate([L["PX"], L["PY"] - d["HY"], 0])


def build_all():
    solid, fp, info = load_building()
    L = layout(fp)
    d = dims()
    T = tf(L)
    F, HY = d["F"], d["HY"]
    cs = hcs(fp)
    foot = foot_solid(cs, F)
    xout_local = L["xwall"] - L["PX"]

    # ---- Gebäude ----
    body = union([solid, foot])
    zc = d["z_kt"] + 1.2
    H = solid.bounding_box()[5]
    ch = chamber(solid, zc, H)
    x0, x1, y0, y1 = cass_outline(d)
    c = sd.KASS_CLR
    groove = sd.prism_x(slider_prof(d, 0.0, 0.01), d["x_in"], xout_local + 6.0)
    cuts = [ch, T(groove),
            T(box(x0 - c, x1 + c, y0 - c, y1 + c, -F - 0.01, d["z_kt"])),                       # Schacht
            T(box(d["seat_x0"] - SEAT_M, d["seat_x1"] + SEAT_M, d["seat_y0"] - 1.45, d["seat_y1"] + SEAT_M,
                  d["z_kt"] - 0.01, d["z_kt"] + 1.21)),                                          # Bodenöffnung (LED)
            T(cbox(d["sock_w"] + 2 * c, d["sock_d"] + 2 * c, d["z_kt"] - 0.01, d["z_kceil"] + 0.3, cy=HY))]
    zd = sd.z_detent()
    w = sd.TONGUE["bump"] + 0.15
    xw = L["xwall"]
    cuts.append(sd.prism_y([(xw + 0.01, zd - w - 0.1), (xw - w + 0.05, zd), (xw + 0.01, zd + w + 0.1)],
                           L["PY"] - 8.0, L["PY"] + 8.0))
    cuts += light_windows(fp)
    building = diff(body, *cuts)

    # ---- Kassette, Schieber, Kaufteile ----
    kass = T(kassette(d))
    foot_local = foot.translate([-L["PX"], -(L["PY"] - HY), 0])      # Fuß in lokalen Koordinaten
    sl = T(slider(d, xout_local, foot_local))
    housing = T(sd.housing_part(d["z_face"]))
    terms = T(sd.terminals_part(d["z_face"]))
    wires = T(sd.kass_wires_part())
    leds = {k: T(led_part(d, s)) for k, s in STRIPS.items()}
    header = T(sd.header_part("A"))

    # ---- Platte, Deckel ----
    plate, lid, screws = plate_and_lid(L, d, cs, F)
    plate_nb = plate_and_lid(L, d, cs, F, bump=False)[0]
    return dict(L=L, d=d, solid=solid, fp=fp, building=building, kass=kass, key=sl, housing=housing, terms=terms,
                wires=wires, leds=leds, header=header, plate=plate, plate_nb=plate_nb, lid=lid, screws=screws, info=info,
                H=H, chamber=ch)


def led_part(d, s):
    """LED-Streifenstück auf der Ablage: Din-Ende zur Buchse, Chips nach oben."""
    z_s = d["z_s"]
    y0 = d["LY0"]
    strip = box(-s["W"] / 2, s["W"] / 2, y0, y0 + s["L"], z_s, z_s + sd.LED_FPC)
    chips = [cbox(5.0, 5.0, z_s + sd.LED_FPC, z_s + sd.LED_T, cy=y0 + c) for c in s["chips"]]
    pads = [cbox(2.0, 1.6, z_s + sd.LED_FPC, z_s + sd.LED_FPC + 0.05, cx=sd.pad_x(n), cy=y0 + 1.0) for n in sd.PADS]
    return union([strip] + chips + pads)


def screw_points(plate_poly, pocket_poly):
    x0, y0, x1, y1 = plate_poly.bounds
    ok = plate_poly.buffer(-3.5).difference(pocket_poly.buffer(3.5))
    out = []
    for cx, cy in ((x0, y0), (x0, y1), (x1, y0), (x1, y1)):
        best, bd = None, 1e9
        for gx in np.arange(x0, x1, 1.0):
            for gy in np.arange(y0, y1, 1.0):
                if ok.contains(Point(gx, gy)):
                    dd = (gx - cx) ** 2 + (gy - cy) ** 2
                    if dd < bd:
                        best, bd = (gx, gy), dd
        out.append(best)
    return out


def plate_and_lid(L, d, cs, F, bump=True):
    PX, PY, HY = L["PX"], L["PY"], d["HY"]
    off = sd.CLR + sd.RELIEF + MARGIN
    pcs = rounded(cs).offset(off, m3d.JoinType.Round)
    blk = ext(pcs, d["z_lt"], 0.0)
    T = tf(L)
    cuts = pocket_cuts(cs, F)
    xwall_p = L["xwall"] + sd.CLR
    cuts += [c.translate([0, PY, 0]) for c in sd.tongue_cuts(0.0, dict(pw=2 * xwall_p))]
    for x in sd.pin_x():                                                  # Dock A
        cuts.append(T(cyl(sd.HOLE / 2, d["z_hb"] - 0.01, -F + 0.01, cx=x, cy=HY, n=20)))
    cuts.append(T(cbox(sd.HDR_W + 2 * sd.SNUG, sd.HDR_BODY + 2 * sd.SNUG, d["z_bb"] - 0.01, d["z_hb"], cy=HY)))
    cuts.append(T(box(-9.0, 9.0, HY - 5.0, HY + 9.0, d["z_lt"] - 0.01, d["z_bb"])))
    ppoly = shapely.Polygon(np.array(pcs.to_polygons()[0]))
    ymax = ppoly.bounds[3]
    cuts.append(box(PX - 4.0, PX + 4.0, PY, ymax + 0.01, d["z_lt"] - 0.01, d["z_lt"] + 4.0))     # Rinne zur Kante
    pts = screw_points(ppoly, shapely.Polygon(np.array(rounded(cs).to_polygons()[0])))
    for x, y in pts:
        cuts.append(cyl(sd.SCREW_PILOT / 2, d["z_lt"] - 0.01, d["z_lt"] + 9.0, cx=x, cy=y))
    p = diff(blk, *cuts)
    add = [T(r) for r in sd.dock_ribs("A", 0.0, d)]
    if bump:
        add.append(sd.tongue_bump(0.0, dict(pw=2 * xwall_p)).translate([0, PY, 0]))
    p = union([p] + add)
    # Deckel mit Stempeln unter den Stirnseiten der Leiste
    lid = ext(pcs, d["z_lb"], d["z_lt"])
    xi, xo = sd.HDR_W / 2 - 0.75, sd.HDR_W / 2 + 0.6
    posts = [T(box(min(sx * xi, sx * xo), max(sx * xi, sx * xo), HY - 1.0, HY + 1.0, d["z_lt"] - 0.01, d["z_bb"]))
             for sx in (-1, 1)]
    lid = union([lid] + posts)
    lid = diff(lid, *[cyl(sd.SCREW_CLR / 2, d["z_lb"] - 0.01, d["z_lt"] + 0.01, cx=x, cy=y) for x, y in pts])
    return p, lid, pts


# --------------------------------------------------------------------------
# Prüfungen
# --------------------------------------------------------------------------
def vi(a, b):
    return (a ^ b).volume()


def checks(P):
    """Überschneidungsvolumina im gesteckten Zustand (mm³)."""
    pl, lid, hd = P["plate_nb"], P["lid"], P["header"]
    rows = []

    def ck(name, a, b, limit=0.5, note=""):
        v = vi(a, b)
        rows.append((name, v, v <= limit or bool(note), note))

    ck("Gebäude ↔ Platte", P["building"], pl)
    ck("Gebäude ↔ Deckel", P["building"], lid)
    ck("Gebäude ↔ Stiftleiste", P["building"], hd)
    ck("Kassette ↔ Gebäude", P["kass"], P["building"])
    ck("Schieber ↔ Gebäude", P["key"], P["building"])
    ck("Schieber ↔ Kassette", P["key"], P["kass"])
    ck("Schieber ↔ Platte", P["key"], pl)
    ck("Schieber ↔ Stiftleiste", P["key"], hd)
    ck("Kassette ↔ Platte", P["kass"], pl)
    ck("Kassette ↔ Stiftleiste", P["kass"], hd)
    ck("Buchse ↔ Stiftleiste", P["housing"], hd)
    ck("Buchse ↔ Platte", P["housing"], pl)
    ck("Buchse ↔ Gebäude", P["housing"], P["building"])
    ck("Buchse ↔ Kassette (Crush-Rippen)", P["housing"], P["kass"], limit=6.0, note="Übermaß der Rippen")
    ck("Stiftleiste ↔ Platte", hd, pl, limit=40.0, note="Rippen der Leistentasche")
    for k, led in P["leds"].items():
        ck("LED %s/m ↔ Kassette" % k, led, P["kass"])
        ck("LED %s/m ↔ Gebäude" % k, led, P["building"])
    ck("Adern ↔ Gebäude", P["wires"], P["building"])
    ck("Adern ↔ Schieber", P["wires"], P["key"])
    ck("Kontakte ↔ Stiftleiste", P["terms"], hd)
    return rows


def insertion_checks(P):
    """Beim Stecken: bewegte Teile (Gebäude, Kassette, Schieber, Buchse) gegen Platte und Leiste."""
    d = P["d"]
    mov = union([P["building"], P["kass"], P["key"]])
    inner = union([P["kass"], P["key"], P["housing"], P["terms"]])
    pl = union([P["plate_nb"], P["lid"]])
    out = []
    for lab, g in (("Hub 0", 0.0), ("Hub 1", 1.0), ("Hub 3", 3.0), ("Kontakt (Stift erreicht Kontakt)", d["contact_lift"]),
                   ("Stift an der Trichterplatte", d["g1"]), ("Fase zu Ende", d["F"] - d["guide"] + 0.0),
                   ("Fuß an der Muldenkante", d["F"]), ("darüber", d["F"] + 2.0)):
        m = mov.translate([0, 0, g])
        out.append((lab, g, vi(m, pl), vi(inner.translate([0, 0, g]), P["header"])))
    return out


# --------------------------------------------------------------------------
# Ausgabe
# --------------------------------------------------------------------------
def to_bed(man):
    b = man.bounding_box()
    return man.translate([0, 0, -b[2]])


def files(P):
    L, d = P["L"], P["d"]
    key = to_bed(P["key"])
    return dict(gebaeude=to_bed(P["building"]), kassette=to_bed(P["kass"]), schieber=key,
                platte=to_bed(P["plate"]), deckel=to_bed(P["lid"]))


def build_data(P, fl):
    L, d = P["L"], P["d"]
    xc = L["PX"] + sd.pin_x()[1]
    yc = L["PY"]

    def trip(man, cuts=("x", "y")):
        out = dict(full=encode(to_tm(man)))
        if "x" in cuts:
            out["cutx"] = encode(to_tm(sd.xcut(man, xc)))
        if "y" in cuts:
            out["cuty"] = encode(to_tm(sd.ycut(man, yc)))
        return out

    parts = dict(plate=trip(P["plate"]), lid=trip(P["lid"]), building=trip(P["building"]), kass=trip(P["kass"]),
                 key=trip(P["key"]), housing=trip(P["housing"]), terms=trip(P["terms"]), wires=trip(P["wires"]),
                 header=trip(P["header"]), led60=trip(P["leds"]["60"]), led144=trip(P["leds"]["144"]))
    return dict(parts=parts, xcut=xc, ycut=yc)


def previews(P):
    import preview
    os.makedirs(PREV, exist_ok=True)
    L, d = P["L"], P["d"]
    col = dict(building="#ece5d2", plate="#8fa3b8", lid="#6f819a", kass="#e3862a", key="#6bbf78", housing="#f4f1e8",
               terms="#caa13a", wires="#c8423b", header="#2d3236", led="#ffe9a0")
    xc = L["PX"] + sd.pin_x()[1]

    def scene(f, lift=0.0, ex=0.0, dx=0.0, dz_k=0.0):
        mv = lift + 24 * ex
        parts = [(to_tm(f(P["plate"])), col["plate"]), (to_tm(f(P["lid"].translate([0, 0, -14 * ex]))), col["lid"]),
                 (to_tm(f(P["header"])), col["header"])]
        parts.append((to_tm(f(P["building"].translate([0, 0, mv + 30 * ex]))), col["building"]))
        parts.append((to_tm(f(P["kass"].translate([0, 0, mv + dz_k]))), col["kass"]))
        parts.append((to_tm(f(P["key"].translate([dx, 0, mv]))), col["key"]))
        parts.append((to_tm(f(P["housing"].translate([0, 0, mv + dz_k]))), col["housing"]))
        parts.append((to_tm(f(P["terms"].translate([0, 0, mv + dz_k]))), col["terms"]))
        parts.append((to_tm(f(P["wires"].translate([0, 0, mv + dz_k]))), col["wires"]))
        parts.append((to_tm(f(P["leds"]["60"].translate([0, 0, mv + dz_k]))), col["led"]))
        return parts
    cutx = lambda m: sd.xcut(m, xc)
    im = preview.render(scene(cutx), size=(1500, 820), azim=62, elev=18); im.save(os.path.join(PREV, "schnitt_laengs.png"))
    cuty = lambda m: sd.ycut(m, L["PY"])
    im = preview.render(scene(cuty), size=(1500, 820), azim=-62, elev=18); im.save(os.path.join(PREV, "schnitt_quer.png"))
    # Zusammenbau von unten: Kassette (mit Buchse, Adern, LED) unter dem Gebäude, Schieber daneben
    b = [(to_tm(P["building"]), col["building"]),
         (to_tm(P["kass"].translate([0, 0, -26])), col["kass"]), (to_tm(P["housing"].translate([0, 0, -26])), col["housing"]),
         (to_tm(P["terms"].translate([0, 0, -26])), col["terms"]), (to_tm(P["wires"].translate([0, 0, -26])), col["wires"]),
         (to_tm(P["leds"]["60"].translate([0, 0, -26])), col["led"]), (to_tm(P["key"].translate([30, 0, 0])), col["key"])]
    im = preview.render(b, size=(1500, 900), azim=-60, elev=-32); im.save(os.path.join(PREV, "zusammenbau_unten.png"))
    b2 = [(to_tm(P["building"]), col["building"]), (to_tm(P["key"]), col["key"])]
    im = preview.render(b2, size=(1500, 900), azim=-55, elev=-38); im.save(os.path.join(PREV, "unterseite.png"))
    im = preview.render([(to_tm(P["plate"]), col["plate"]), (to_tm(P["header"]), col["header"])], size=(1500, 820), azim=-50, elev=40)
    im.save(os.path.join(PREV, "platte.png"))
    im = preview.render(scene(lambda m: m, ex=0.9), size=(1500, 1000), azim=-60, elev=26); im.save(os.path.join(PREV, "explosion.png"))
    im = preview.render([(to_tm(P["building"]), col["building"])], size=(1500, 900), azim=-55, elev=28); im.save(os.path.join(PREV, "gebaeude.png"))
    print("Vorschau: %s" % os.path.relpath(PREV, HERE))


def build():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(DOC, exist_ok=True)
    P = build_all()
    L, d = P["L"], P["d"]
    print("Institutsgebäude 1:%d: Grundriss %.1f × %.1f mm, Hauptbalken %.1f mm breit, Höhe %.1f mm (ohne Fuß)" % (
        SCALE, 2 * L["bbox"][2], 2 * L["bbox"][3], L["bar"], P["H"]))
    print("Pin-Reihe bei x=%.1f, y=%.1f; Kassette %.1f × %.1f mm, Ablage %.1f × %.1f mm; Fuß %.1f mm" % (
        L["PX"], L["PY"], d["cass_w"], d["cass_len"], SEAT_W, SEAT_L, d["F"]))
    fl = files(P)
    for name, man in fl.items():
        tm = to_tm(man)
        tm.export(os.path.join(OUT, name + ".stl"))
        print("  %-48s %6.1f × %6.1f × %6.1f mm  dicht=%s" % (
            os.path.relpath(os.path.join(OUT, name + ".stl"), HERE), *tm.extents, tm.is_watertight))
    bad = 0
    print("\nKollisionsprüfung gesteckt (Überschneidungsvolumen):")
    for name, v, ok, note in checks(P):
        if not ok:
            bad += 1
        print("  %-42s %8.2f mm³  %s" % (name, v, ("ok (%s)" % note if note else "ok") if ok else "KOLLISION"))
    print("\nBeim Stecken (Hub g über dem Sitz):")
    ins = insertion_checks(P)
    for lab, g, vp, vh in ins:
        ok = vp <= 0.5 and vh <= 0.5
        if not ok:
            bad += 1
        print("  %-36s g=%5.2f  Platte %6.2f  Stiftleiste %6.2f  %s" % (lab, g, vp, vh, "ok" if ok else "KOLLISION"))
    print("  -> %s" % ("keine Kollisionen" if not bad else "%d Kollisionen!" % bad))
    return P, fl, ins


def write_data(P, fl, ins, checks_rows):
    L, d = P["L"], P["d"]
    data = build_data(P, fl)
    bw = L["bar"]
    bbox = L["bbox"]
    data.update(
        dims={k: round(float(v), 3) for k, v in d.items()},
        layout={k: (round(float(v), 3) if not isinstance(v, tuple) else [round(float(x), 2) for x in v])
                for k, v in L.items()},
        scale=SCALE,
        params=dict(SEAT_W=SEAT_W, SEAT_L=SEAT_L, SEAT_M=SEAT_M, SHELL=sd.SHELL, ROOF=sd.ROOF, CH_F=sd.CH_F,
                    CH_P=sd.CH_P, CLR=sd.CLR, RELIEF=sd.RELIEF, BAND=sd.BAND, KEY_CLR=sd.KEY_CLR,
                    KASS_CLR=sd.KASS_CLR, FUNNEL_T=sd.FUNNEL_T, HOLE=sd.HOLE, FUNNEL_D=sd.FUNNEL_D,
                    WALL=sd.WALL, LED_T=sd.LED_T, GAP_L=sd.GAP_L, HSG_W=sd.HSG_W, HSG_T=sd.HSG_T,
                    pin_x=sd.pin_x(), PADS=list(sd.PADS), WIN_STEP=WIN_STEP, WIN_W=WIN_W, WIN_H=WIN_H,
                    WIN_T=WIN_T, WIN_ROWS=list(WIN_ROWS), MARGIN=MARGIN),
        strips=STRIPS,
        building=dict(W=round(2 * bbox[2], 1), T=round(2 * bbox[3], 1), H=round(float(P["H"]), 1),
                      bar=round(bw, 1), bar_1500=round(bw * 1000.0 / 1500.0, 1),
                      wall_beside=round((bw - d["cass_w"] - 2 * sd.KASS_CLR) / 2, 2),
                      wall_beside_1500=round((bw * 1000.0 / 1500.0 - d["cass_w"] - 2 * sd.KASS_CLR) / 2, 2),
                      need_bar=round(d["cass_w"] + 2 * sd.KASS_CLR + 2 * 2.0, 1),
                      slider_len=round(L["xwall"] - L["PX"] - d["x_in"] + 1.0, 1),
                      windows_per_row=0),
        sizes={n: [round(float(v), 1) for v in to_tm(m).extents] for n, m in fl.items()},
        insertion=[dict(label=l, g=round(g, 2), plate=round(vp, 2), header=round(vh, 2)) for l, g, vp, vh in ins],
        checks=[dict(name=n, v=round(float(v), 2), ok=bool(ok), note=note) for n, v, ok, note in checks_rows])
    path = os.path.join(DOC, "daten.json")
    with open(path, "w") as f:
        json.dump(data, f, separators=(",", ":"))
    print("\n%s: %.0f kB" % (os.path.relpath(path, HERE), os.path.getsize(path) / 1024))


if __name__ == "__main__":
    P, fl, ins = build()
    write_data(P, fl, ins, checks(P))
    previews(P)
