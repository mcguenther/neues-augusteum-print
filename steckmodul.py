#!/usr/bin/env python3
"""Steckmechanismus für beleuchtete Gebäude: Prototyp (Dock-Platte, Steckmodul, Würfel).

Konzept (Plan: stecker/PLAN.md):
  * Grundplatte: flache Aussparung für die Gebäudegrundfläche (wie bisher) und darunter ein
    schmaler Dock-Schacht. Am Schachtboden steht der Header (Stiftleiste mit Hülse) nach oben.
  * Steckmodul: gedrucktes Standardteil. Zapfen (taucht in den Schacht, trägt die Buchse mit
    Kabeln), Kragen und Kopf mit LED-Fläche. Es rastet von unten in den Gebäudeboden.
  * Gebäude (hier: Würfel): hohl, Boden mit genormtem Modulloch.
  * Der Schacht ist tiefer, als der Header hoch ist: Der Zapfen steckt erst GUIDE mm im Schacht,
    bevor die Steckverbinder Kontakt bekommen.

Alle Maße in mm. Koordinaten im gesteckten Zustand: z = 0 ist der Gebäudeboden (= Boden der
Aussparung in der Platte), +z nach oben, x entlang der Pin-Reihe, Steckerachse bei x = y = 0.

Halte-Varianten (jeweils A, B, C, an Platte und Modul unabhängig kombinierbar):
  Platte (Header):  A Presssitz mit Crush-Rippen · B Platinen-Sandwich mit 2 Schrauben · C Heißkleber
  Modul (Buchse):   A Presssitz mit Crush-Rippen · B Kabel-Zugentlastung (S-Führung) · C Heißkleber

Aufruf:
    python3 steckmodul.py     # STL nach stl/steckmodul/, Prüfbericht, stecker/daten.json
"""
import base64
import json
import os

import manifold3d as m3d
import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "stl", "steckmodul")
DOC = os.path.join(HERE, "stecker")

# --------------------------------------------------------------------------
# Steckverbinder JST XH 2,5 mm, 4-polig (Datenblatt eXH, Werte in stecker/PLAN.md).
# hdr = Header auf der Platte (Hülse mit Stiften), hsg = Buchsengehäuse XHP-4 mit Kabel.
# x = Pin-Reihe, y = quer. hsg_d_front = Tiefe des Teils, das in die Hülse taucht;
# hsg_d = Tiefe des hinteren Teils (Stufe), der über der Hülse bleibt.
# --------------------------------------------------------------------------
PITCH = 2.5
HDR_W, HDR_D, HDR_H = 12.4, 5.75, 7.0       # B4B-XH-A: Breite, Tiefe, Höhe über Platine
TAIL = 3.4                                   # Pins unter dem Header-Körper
HSG_W, HSG_D, HSG_D_FRONT, HSG_H = 10.7, 5.7, 4.1, 7.75   # XHP-4
ENGAGE = 4.95                                # Einstecktiefe (9,8 gesteckt − 7,0 − (7,75 − 4,95) …)
WIRE_D = 1.6                                 # Ader mit Isolation

# Passungen (FDM, 0,4er Düse) – zentral, damit sie nach dem Toleranztest angepasst werden
SLIDE = 0.20          # Spiel pro Seite: Zapfen im Schacht
CLR = 0.30            # Spiel pro Seite: Header-Hülse im Zapfen
SNUG = 0.10           # Spiel pro Seite: Gehäuse in der Tasche
RIB = 0.15            # Übermaß der Crush-Rippen pro Seite
WALL = 1.2            # Wandstärke an Tragstellen
CH = 1.0              # Einführfase

GUIDE = 3.0           # Zapfen steckt mind. so tief im Schacht, bevor die Kontakte greifen
POCKET_DEPTH = 1.0    # flache Aussparung der Gebäudegrundfläche (wie generate.py)
POCKET_CLEAR = 0.25   # Spiel pro Seite der Gebäude-Aussparung (wie generate.py)
SEAT = 2.0            # Header-Körper sitzt so tief unter dem Schachtboden-Oberrand
FLOOR_T = 3.0         # Schachtboden
CABLE_H = 5.0         # Kabelraum unter dem Schachtboden
BASE_GAP = 0.5        # Luft zwischen Zapfenunterseite und Schachtboden (gesteckt)
PCB = (22.0, 11.0, 1.6)   # Lochraster-Platine unter dem Header (Variante B)
PCB_SCREW_X = 9.5
SCREW_D = 1.7         # Pilotloch für M2-Blechschraube / Gewindeformer

# Würfel / Gebäudeboden
CUBE = 30.0
CUBE_H = 24.0
SHELL = 1.2
FLOOR = 2.4           # Gebäudeboden (Kragennische + Rest)
COLLAR_T = 1.2
KEY = 3.0             # Kodier-Fase einer Ecke (Würfel, Aussparung, Zapfen)

# LED-Streifenstück (WS2812B 5050, 60 LED/m): Breite, Länge je LED, Dicke
LED_W, LED_L, LED_T = 10.0, 16.7, 2.2
LED_SLOT = 4.0        # offener Schlitz neben dem Streifen, in dem die Kabel auf die Pads gehen
ARM_T, ARM_SLIT, BARB = 1.2, 0.8, 0.7   # Schnappnasen am Kopf
DOCK_PITCH = 36.0
VARIANTS = ("A", "B", "C")


def box(x0, x1, y0, y1, z0, z1):
    return m3d.Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])


def cbox(w, d, z0, z1, cx=0.0, cy=0.0):
    return box(cx - w / 2, cx + w / 2, cy - d / 2, cy + d / 2, z0, z1)


def cyl(r, z0, z1, cx=0.0, cy=0.0, n=20):
    return m3d.Manifold.cylinder(z1 - z0, r, r, n).translate([cx, cy, z0])


def union(parts):
    parts = [p for p in parts if p is not None]
    return m3d.Manifold.batch_boolean(parts, m3d.OpType.Add)


def diff(a, *bs):
    for b in bs:
        a = a - b
    return a


def frustum(w, d, z0, z1, grow, cx=0.0, cy=0.0):
    """Pyramidenstumpf: unten (z0) w×d, oben (z1) je Seite um `grow` größer (Einführfase)."""
    cs = m3d.CrossSection([[(-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2)]])
    sc = ((w + 2 * grow) / w, (d + 2 * grow) / d)
    return m3d.Manifold.extrude(cs, z1 - z0, 0, 0.0, sc).translate([cx, cy, z0])


def keyed(w, d, z0, z1, key, cx=0.0, cy=0.0):
    """Quader mit abgeschrägter Ecke (−x, −y) als Kodierung."""
    pts = [(-w / 2 + key, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2), (-w / 2, -d / 2 + key)]
    return m3d.Manifold.extrude(m3d.CrossSection([pts]), z1 - z0).translate([cx, cy, z0])


def to_tm(man):
    mesh = man.to_mesh()
    return trimesh.Trimesh(vertices=np.asarray(mesh.vert_properties)[:, :3],
                           faces=np.asarray(mesh.tri_verts), process=False)


# --------------------------------------------------------------------------
# Maßkette (z, gesteckt; Gebäudeboden = 0)
# --------------------------------------------------------------------------
def dims():
    P = ENGAGE + GUIDE                  # Zapfenlänge unter dem Gebäudeboden
    D = P + BASE_GAP                    # Schachttiefe unter dem Aussparungsboden
    seat = -D - SEAT                    # Unterkante Header-Körper
    hood_top = seat + HDR_H             # Oberkante Header-Hülse
    face = hood_top - ENGAGE            # Buchsenstirn (gesteckt)
    rear = face + HSG_H                 # Buchsenrückseite, Kabelabgang
    cav_w, cav_d = HDR_W + 2 * CLR, HDR_D + 2 * CLR
    peg_w, peg_d = cav_w + 2 * WALL, cav_d + 2 * WALL
    head_w = LED_L + LED_SLOT
    head_d = LED_W + 2 * (ARM_T + ARM_SLIT)
    return dict(
        E=ENGAGE, P=P, D=D, seat=seat, hood_top=hood_top, face=face, rear=rear,
        guide=P - ENGAGE, contact_lift=ENGAGE,
        plate_top=POCKET_DEPTH, plate_bottom=-D - FLOOR_T - CABLE_H,
        cav_w=cav_w, cav_d=cav_d, peg_w=peg_w, peg_d=peg_d,
        shaft_w=peg_w + 2 * SLIDE, shaft_d=peg_d + 2 * SLIDE,
        pk_w=HSG_W + 2 * SNUG, pk_d=HSG_D + 2 * SNUG,
        collar_w=head_w + 3.0, collar_d=head_d + 3.0,
        head_w=head_w, head_d=head_d, head_top=FLOOR + 2.6)


# --------------------------------------------------------------------------
# Steckmodul (Varianten für die Buchsenhaltung)
# --------------------------------------------------------------------------
def module(variant):
    d = dims()
    P, rear, ht = d["P"], d["rear"], d["head_top"]
    cav_top = d["hood_top"] + 0.4
    hw, hd = d["head_w"], d["head_d"]
    body = union([keyed(d["peg_w"], d["peg_d"], -P, 0.01, KEY),
                  cbox(d["collar_w"], d["collar_d"], 0, COLLAR_T),
                  cbox(hw, hd, COLLAR_T - 0.01, ht)])

    cut = [cbox(d["cav_w"], d["cav_d"], -P - 0.01, cav_top),                 # Kammer für die Hülse
           frustum(d["cav_w"], d["cav_d"], -P - 0.01, -P + CH, CH).mirror([0, 0, 1])
           .translate([0, 0, -2 * P - 0.02 + CH]),                           # Einführfase unten
           cbox(d["pk_w"], d["pk_d"], cav_top - 0.01, rear)]                  # Gehäusetasche
    # Kabelweg: senkrechter Kanal bis in eine Rinne unter dem Streifen, Rinne bis zum Schlitz
    chan_w = 4 * WIRE_D + 0.4
    cut.append(cbox(chan_w, 2.4, rear - 0.01, ht - 1.6))
    trench_x0 = -hw / 2
    cut.append(box(trench_x0 - 0.01, 0.5 + chan_w / 2 - 2.0, -chan_w / 2, chan_w / 2, ht - 2.4, ht + 0.01))
    cut.append(box(trench_x0 - 0.01, trench_x0 + LED_SLOT, -hd / 2 + ARM_T + ARM_SLIT, hd / 2 - ARM_T - ARM_SLIT,
                   COLLAR_T, ht + 0.01))                                       # offener Schlitz
    # Schnappnasen: Federarme an den ±y-Seiten des Kopfes
    ax0, ax1 = -hw / 2 + LED_SLOT + 1.0, hw / 2 - 1.0
    for sy in (-1, 1):
        y_in = sy * (hd / 2 - ARM_T - ARM_SLIT)
        y_out = sy * (hd / 2 - ARM_T)
        cut.append(box(ax0, ax1, min(y_in, y_out) , max(y_in, y_out), COLLAR_T + 0.6, ht + 0.01))
    barbs = []
    for sy in (-1, 1):
        zc = FLOOR + 0.1                                  # Rastfläche unter dem Gebäudeboden-Oberrand
        prof = [(0, zc), (BARB, zc), (0, zc + 1.5)]
        wedge = m3d.Manifold.extrude(m3d.CrossSection([prof]), ax1 - ax0 - 3.0)
        # (y, z)-Profil -> x-Extrusion
        wedge = wedge.rotate([90, 0, 90]).translate([ax0 + 1.5, sy * hd / 2, 0])
        if sy < 0:
            wedge = wedge.mirror([0, 1, 0]).translate([0, 0, 0])
            wedge = wedge.translate([0, 0, 0])
        barbs.append(wedge)

    extra = []
    xr = d["pk_w"] / 2 - SNUG
    if variant == "A":     # Presssitz: je 2 Crush-Rippen pro Längsseite
        for sx in (-1, 1):
            for z0 in (cav_top + 0.2, rear - 1.2):
                extra.append(cbox(0.6, 2.4, z0, z0 + 1.0, cx=sx * (xr - RIB + 0.3 - 0.0)))
    if variant == "B":     # Zugentlastung: zwei Querstifte im Kanal, Kabel laufen S-förmig darum
        for cx_, z0 in ((-1.8, rear + 1.0), (1.8, rear + 2.4)):
            extra.append(m3d.Manifold.cylinder(2.8, 0.55, 0.55, 14).rotate([-90, 0, 0]).translate([cx_, -1.4, z0]))
    if variant == "C":     # Heißkleber: seitliche Fenster in die Tasche
        for sx in (-1, 1):
            cut.append(cbox(2.2, 3.0, cav_top + 0.4, rear, cx=sx * (d["pk_w"] / 2 + 0.6)))
    mod = diff(body, *cut)
    return union([mod] + extra + barbs), d


# --------------------------------------------------------------------------
# Würfel (Gebäude-Stellvertreter)
# --------------------------------------------------------------------------
def cube():
    d = dims()
    body = keyed(CUBE, CUBE, 0, CUBE_H, KEY)
    inner = keyed(CUBE - 2 * SHELL, CUBE - 2 * SHELL, FLOOR, CUBE_H - SHELL, KEY - 0.4)
    cut = [inner,
           cbox(d["head_w"] + 0.3, d["head_d"] + 0.3, -0.01, FLOOR + 0.01),      # Modulloch
           cbox(d["collar_w"] + 0.4, d["collar_d"] + 0.4, -0.01, COLLAR_T + 0.05)]  # Kragennische
    # Lichtfenster: auf 0,4 mm abgedünnte Wandstellen (Test, wie viel Licht durchkommt)
    for cx_, cy_, axis in ((0, -1, "y"), (0, 1, "y"), (-1, 0, "x"), (1, 0, "x")):
        for z0, t in ((9.0, 0.4), (16.0, 0.8)):
            if axis == "y":
                cut.append(cbox(6.0, SHELL - t + 0.01, z0, z0 + 5.0, cx=0, cy=cy_ * (CUBE / 2 - SHELL + (SHELL - t) / 2)))
            else:
                cut.append(cbox(SHELL - t + 0.01, 6.0, z0, z0 + 5.0, cx=cx_ * (CUBE / 2 - SHELL + (SHELL - t) / 2), cy=0))
    return diff(body, *cut)


# --------------------------------------------------------------------------
# Dock-Platte mit drei Docks (Header-Halterung A, B, C)
# --------------------------------------------------------------------------
def dock_cuts(variant, cx):
    d = dims()
    D, seat = d["D"], d["seat"]
    sw, sd = d["shaft_w"], d["shaft_d"]
    z_fl = -D - FLOOR_T
    cuts = []
    # Aussparung der Gebäudegrundfläche (mit Kodier-Ecke) + Schacht mit Einführfase
    cuts.append(keyed(CUBE + 2 * POCKET_CLEAR, CUBE + 2 * POCKET_CLEAR, -0.0, POCKET_DEPTH + 0.01, KEY, cx=cx))
    cuts.append(keyed(sw, sd, -D, 0.01, KEY, cx=cx))
    cuts.append(frustum(sw, sd, -CH, 0.0, CH, cx=cx).translate([0, 0, 0.0]))
    # Kabelraum unter dem Schachtboden und Rinne zur vorderen Plattenkante
    cuts.append(cbox(26.0, 15.0, d["plate_bottom"] - 0.01, z_fl + 0.01, cx=cx))
    cuts.append(box(cx - 3.0, cx + 3.0, -40.0, 0.0, d["plate_bottom"] - 0.01, d["plate_bottom"] + 3.0))
    hole_x = [(i - 1.5) * PITCH for i in range(4)]
    if variant == "A":     # Tasche mit Crush-Rippen, Stiftlöcher durch den Boden
        cuts.append(cbox(HDR_W + 0.2, HDR_D + 0.2, seat, seat + SEAT + 0.01, cx=cx))
        for hx in hole_x:
            cuts.append(cyl(0.6, z_fl - 0.01, seat + 0.01, cx=cx + hx))
    elif variant == "B":   # Fenster durch den Boden, Platine mit 2 Schrauben von unten
        cuts.append(cbox(HDR_W + 0.3, HDR_D + 0.3, z_fl - 0.01, seat + SEAT + 0.01, cx=cx))
        cuts.append(cbox(PCB[0] + 0.3, PCB[1] + 0.3, z_fl - 0.01, seat, cx=cx))
        for sx in (-1, 1):
            cuts.append(cyl(SCREW_D / 2, seat - 0.01, seat + 5.0, cx=cx + sx * PCB_SCREW_X))
    else:                  # C: Tasche locker, Klebefenster zum Kabelraum
        cuts.append(cbox(HDR_W + 0.6, HDR_D + 0.6, seat, seat + SEAT + 0.01, cx=cx))
        for hx in hole_x:
            cuts.append(cyl(0.6, z_fl - 0.01, seat + 0.01, cx=cx + hx))
        for sx in (-1, 1):
            cuts.append(cbox(2.0, 4.0, z_fl - 0.01, seat + 0.01, cx=cx + sx * (HDR_W / 2 + 1.3)))
    return cuts


def dock_ribs(variant, cx):
    if variant != "A":
        return []
    d = dims()
    seat = d["seat"]
    ribs = []
    for sx in (-1, 1):                      # Rippen an den langen Wänden (±y)
        for hx in (-3.0, 3.0):
            ribs.append(cbox(0.6, 2 * RIB + 0.1, seat, seat + SEAT, cx=cx + hx,
                             cy=sx * ((HDR_D + 0.2) / 2 - RIB / 2 - 0.0)))
    for sx in (-1, 1):                      # und je eine an den kurzen Wänden (±x)
        ribs.append(cbox(2 * RIB + 0.1, 0.6, seat, seat + SEAT, cx=cx + sx * ((HDR_W + 0.2) / 2 - RIB / 2), cy=0))
    return ribs


def plate():
    d = dims()
    xs = [(i - 1) * DOCK_PITCH for i in range(3)]
    half_x = xs[-1] + CUBE / 2 + POCKET_CLEAR + 6.0
    half_y = CUBE / 2 + POCKET_CLEAR + 6.0
    block = box(-half_x, half_x, -half_y, half_y, d["plate_bottom"], d["plate_top"])
    cuts = []
    for v, cx in zip(VARIANTS, xs):
        cuts += dock_cuts(v, cx)
    # Rinne nach vorne (−y): die Dock-Rinnen laufen bis zur Kante
    cuts = [c for c in cuts]
    plate_ = diff(block, *cuts)
    ribs = []
    for v, cx in zip(VARIANTS, xs):
        ribs += dock_ribs(v, cx)
    plate_ = union([plate_] + ribs)
    # Kennbuchstaben A, B, C an der Vorderkante (graviert)
    try:
        import generate
        letters = []
        for v, cx in zip(VARIANTS, xs):
            cs = generate.text_cross_section(v, 4.0, cx, -half_y + 1.2, anchor="center")
            if cs is not None:
                letters.append(m3d.Manifold.extrude(cs, 0.6).translate([0, 0, d["plate_top"] - 0.4]))
        plate_ = diff(plate_, *letters)
    except Exception as e:  # Gravur ist nur Zierde
        print("  (Gravur übersprungen: %s)" % e)
    return plate_, xs, d


# --------------------------------------------------------------------------
# Nicht gedruckte Bauteile (Darstellung + Kollisionsprüfung)
# --------------------------------------------------------------------------
def pin_x():
    return [(i - 1.5) * PITCH for i in range(4)]


def header_part():
    """B4B-XH-A: Hülse mit Stiften, Körperunterkante bei z = seat."""
    d = dims()
    seat, top = d["seat"], d["hood_top"]
    body = cbox(HDR_W, HDR_D, seat, top)
    body = body - cbox(HSG_W + 0.3, HSG_D_FRONT + 0.3, seat + 1.0, top + 0.01)
    pins = [cbox(0.64, 0.64, seat - TAIL, top - 1.6, cx=x) for x in pin_x()]
    return union([body] + pins)


def housing_part():
    """XHP-4: vorderer Teil (in der Hülse) 4,1 tief, hinterer Teil (Stufe) 5,7 tief."""
    d = dims()
    front = cbox(HSG_W, HSG_D_FRONT, d["face"], d["hood_top"])
    front = diff(front, *[cbox(0.7, 0.7, d["face"] - 0.01, d["hood_top"] - 1.5, cx=x) for x in pin_x()])
    rear = cbox(HSG_W, HSG_D, d["hood_top"], d["rear"])
    return union([front, rear])


def wire_paths():
    d = dims()
    ht, hw = d["head_top"], d["head_w"]
    x_slot = -hw / 2 + LED_SLOT / 2
    x_pad = -hw / 2 + LED_SLOT + 1.2
    paths = []
    for i, x in enumerate(pin_x()):
        y = (i - 1.5) * WIRE_D
        r = WIRE_D / 2
        paths.append([(x * 0.64, 0, d["rear"] + 0.05), (x * 0.64, 0, ht - 1.2), (x * 0.64 + 0.0, y, ht - 1.2),
                      (x_slot, y, ht - 1.2), (x_slot, y, ht + 1.6), (x_pad, y, ht + LED_T + 0.35)])
    return paths


def wires_mesh():
    parts = []
    for path in wire_paths():
        for a, b in zip(path[:-1], path[1:]):
            if np.linalg.norm(np.subtract(a, b)) < 1e-6:
                continue
            parts.append(trimesh.creation.cylinder(radius=WIRE_D / 2 * 0.8, segment=[a, b], sections=10))
            parts.append(trimesh.creation.icosphere(radius=WIRE_D / 2 * 0.8, subdivisions=1).apply_translation(b))
    return trimesh.util.concatenate(parts)


def led_part():
    d = dims()
    ht, hw = d["head_top"], d["head_w"]
    x0 = -hw / 2 + LED_SLOT
    strip = box(x0, x0 + LED_L, -LED_W / 2, LED_W / 2, ht, ht + 0.5)
    chip = cbox(5.0, 5.0, ht + 0.5, ht + LED_T, cx=x0 + LED_L / 2)
    return union([strip, chip])


def pcb_part(cx=0.0):
    d = dims()
    return cbox(PCB[0], PCB[1], d["seat"] - PCB[2], d["seat"], cx=cx)


def screws_part():
    d = dims()
    seat = d["seat"]
    parts = []
    for sx in (-1, 1):
        parts.append(cyl(1.0, seat - PCB[2] - 1.0, seat + 4.0, cx=sx * PCB_SCREW_X))
        parts.append(cyl(1.7, seat - PCB[2] - 1.8, seat - PCB[2] - 1.0, cx=sx * PCB_SCREW_X))
    return union(parts)


def vol_int(a, b):
    return (a ^ b).volume() if False else (a - (a - b)).volume()


def checks(plate_man, xs, mods, cube_man):
    """Kollisions- und Maßprüfung im gesteckten Zustand (Dock 0 / Modul A als Beispiel)."""
    d = dims()
    out = []

    def ck(name, a, b, limit=0.5):
        v = vol_int(a, b)
        out.append((name, v, v <= limit))
        return v

    res = {}
    for v, cx in zip(VARIANTS, xs):
        pl = plate_man
        for mv in VARIANTS:
            m = mods[mv].translate([cx, 0, 0])
            c = cube_man.translate([cx, 0, 0])
            hdr = header_part().translate([cx, 0, 0])
            hsg = housing_part().translate([cx, 0, 0])
            tag = "Dock %s / Modul %s" % (v, mv)
            ck(tag + ": Modul ↔ Platte", m, pl)
            ck(tag + ": Modul ↔ Würfel", m, c)
            ck(tag + ": Würfel ↔ Platte", c, pl)
            ck(tag + ": Header ↔ Modul", hdr, m)
            ck(tag + ": Buchse ↔ Header", hsg, hdr)
            ck(tag + ": Buchse ↔ Platte", hsg, pl)
            # Rippen dürfen die Buchse berühren (Pressung)
            r = vol_int(hsg, m)
            out.append((tag + ": Buchse ↔ Modul (Rippen-Übermaß)", r, True))
            if v == "B":
                ck(tag + ": Platine ↔ Platte", pcb_part(cx), pl)
    return out


# --------------------------------------------------------------------------
# Ausgabe
# --------------------------------------------------------------------------
def print_orient(man, d):
    """Modul zum Drucken: Kopf (LED-Fläche) auf das Druckbett, Zapfen zeigt nach oben."""
    return man.rotate([180, 0, 0]).translate([0, 0, d["head_top"]])


def passprobe():
    """Kleiner Test für die Passungen: Buchsen-Taschen und Header-Taschen mit 0,0/0,1/0,2 mm Spiel."""
    blk = box(-30, 30, -12, 12, 0, 8)
    cuts = []
    for i, c in enumerate((0.0, 0.1, 0.2)):
        x = -20 + i * 20
        cuts.append(cbox(HSG_W + 2 * c, HSG_D + 2 * c, 2.0, 8.01, cx=x, cy=-6))
        cuts.append(cbox(HDR_W + 2 * c, HDR_D + 2 * c, 2.0, 8.01, cx=x, cy=6))
    return diff(blk, *cuts)


def encode(tm):
    v = np.asarray(tm.vertices, np.float32)
    f = np.asarray(tm.faces, np.uint32)
    return dict(v=base64.b64encode(v.tobytes()).decode(), i=base64.b64encode(f.tobytes()).decode(),
                n=int(len(f)))


def half(man):
    return man - box(-500, 500, 0, 500, -500, 500)


def previews():
    """Vorschaubilder nach vorschau/steckmodul/ (siehe CLAUDE.md: Bilder werden mit committet)."""
    import preview
    out = os.path.join(HERE, "vorschau", "steckmodul")
    os.makedirs(out, exist_ok=True)
    d = dims()
    plate_man, xs, _ = plate()
    mods = {v: module(v)[0] for v in VARIANTS}
    col = dict(plate="#8fa3b8", module="#e3862a", cube="#ece5d2", header="#2d3236", housing="#f4f1e8",
               pcb="#3f8f5e", led="#ffe9a0", wire="#c8423b")

    def scene(cut, dock=0, mv="A", lift=0.0, ex=0.0):
        f = half if cut else (lambda m: m)
        parts = [(to_tm(f(plate_man)), col["plate"])]
        for i, x in enumerate(xs):
            parts.append((to_tm(f(header_part().translate([x, 0, ex * -0.0]))), col["header"]))
        parts.append((to_tm(f(pcb_part(xs[1]).translate([0, 0, -8 * ex]))), col["pcb"]))
        parts.append((to_tm(f(screws_part().translate([xs[1], 0, -15 * ex]))), "#9aa0a6"))
        x = xs[dock]
        z = lift + 22 * ex
        parts.append((to_tm(f(mods[mv].translate([x, 0, z]))), col["module"]))
        parts.append((to_tm(f(cube().translate([x, 0, z + 34 * ex]))), col["cube"]))
        parts.append((to_tm(f(housing_part().translate([x, 0, z - 14 * ex]))), col["housing"]))
        parts.append((to_tm(f(led_part().translate([x, 0, z + 15 * ex]))), col["led"]))
        if ex == 0:
            parts.append((wires_mesh().apply_translation([x, 0, z]), col["wire"]))
        return parts

    im = preview.render(scene(True), size=(1300, 640), azim=118, elev=24)
    im.save(os.path.join(out, "schnitt_gesteckt.png"))
    im = preview.render(scene(True, dock=1, mv="B", lift=d["E"]), size=(1300, 640), azim=118, elev=24)
    im.save(os.path.join(out, "schnitt_kontakt.png"))
    im = preview.render(scene(False, ex=0.9), size=(1300, 760), azim=125, elev=28)
    im.save(os.path.join(out, "explosion.png"))
    # Druckplatte: alle Druckteile nebeneinander
    plate_tm = to_tm(plate_man)
    items = [(plate_tm, col["plate"])]
    for i, v in enumerate(VARIANTS):
        m = to_tm(print_orient(mods[v], d).translate([-30 + 30 * i, -60, 0]))
        items.append((m, col["module"]))
    items.append((to_tm(cube().translate([50, -62, 0])), col["cube"]))
    items.append((to_tm(passprobe().translate([0, 52, 0])), "#b9bfc4"))
    for m, _ in items[:1]:
        m.apply_translation([0, 0, -d["plate_bottom"]])
    im = preview.render(items, size=(1300, 760), azim=-35, elev=32)
    im.save(os.path.join(out, "druckteile.png"))
    parts = [(to_tm(half(mods[v]).translate([i * 28, 0, 0])), col["module"]) for i, v in enumerate(VARIANTS)]
    im = preview.render(parts, size=(1300, 520), azim=125, elev=25)
    im.save(os.path.join(out, "module_schnitt.png"))
    print("Vorschau: vorschau/steckmodul/ (5 Bilder)")


def build():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(DOC, exist_ok=True)
    d = dims()
    plate_man, xs, _ = plate()
    mods = {v: module(v)[0] for v in VARIANTS}
    cube_man = cube()

    print("Maßkette (mm, gesteckt, Gebäudeboden z=0):")
    for k in ("E", "P", "D", "guide", "seat", "hood_top", "face", "rear", "plate_bottom", "plate_top"):
        print("  %-14s %7.2f" % (k, d[k]))
    print("  Platte %.1f × %.1f × %.1f mm, Zapfen %.1f × %.1f × %.2f mm, Schacht %.1f × %.1f mm" % (
        2 * (xs[-1] + CUBE / 2 + POCKET_CLEAR + 6), CUBE + 2 * POCKET_CLEAR + 12,
        d["plate_top"] - d["plate_bottom"], d["peg_w"], d["peg_d"], d["P"], d["shaft_w"], d["shaft_d"]))

    files = [("dock_platte_ABC.stl", plate_man), ("wuerfel.stl", cube_man), ("passprobe.stl", passprobe())]
    files += [("steckmodul_%s.stl" % v, print_orient(m, d)) for v, m in mods.items()]
    for name, man in files:
        tm = to_tm(man)
        tm.export(os.path.join(OUT, name))
        print("  %-46s %6.1f × %6.1f × %6.1f mm  dicht=%s" % (
            os.path.relpath(os.path.join(OUT, name), HERE), *tm.extents, tm.is_watertight))

    print("\nKollisionsprüfung (Überschneidungsvolumen, gesteckt):")
    bad = 0
    for name, v, ok in checks(plate_man, xs, mods, cube_man):
        if not ok:
            bad += 1
        if (not ok) or "Rippen" in name or "Dock A / Modul A" in name:
            print("  %-52s %8.2f mm³  %s" % (name, v, "ok" if ok else "KOLLISION"))
    print("  -> %s" % ("keine Kollisionen" if not bad else "%d Kollisionen!" % bad))

    # Daten für die HTML-Ansicht: Vollkörper und Halbschnitt (y ≤ 0)
    def pair(man):
        return dict(full=encode(to_tm(man)), cut=encode(to_tm(half(man))))
    data = dict(
        dims={k: (round(float(v), 3)) for k, v in d.items()},
        xs=xs,
        params=dict(CUBE=CUBE, CUBE_H=CUBE_H, HDR_W=HDR_W, HDR_D=HDR_D, HDR_H=HDR_H, HSG_W=HSG_W, HSG_D=HSG_D,
                    HSG_H=HSG_H, ENGAGE=ENGAGE, GUIDE=GUIDE, SLIDE=SLIDE, CLR=CLR, SNUG=SNUG, RIB=RIB,
                    WALL=WALL, LED_W=LED_W, LED_L=LED_L, FLOOR=FLOOR, COLLAR_T=COLLAR_T),
        parts=dict(
            plate=pair(plate_man), cube=pair(cube_man),
            module={v: pair(m) for v, m in mods.items()},
            header=pair(header_part()), housing=pair(housing_part()), led=pair(led_part()),
            pcb=pair(pcb_part()), screws=pair(screws_part()),
            wires=dict(full=encode(wires_mesh()), cut=encode(wires_mesh())),
        ))
    with open(os.path.join(DOC, "daten.json"), "w") as f:
        json.dump(data, f, separators=(",", ":"))
    print("\nstecker/daten.json: %.0f kB" % (os.path.getsize(os.path.join(DOC, "daten.json")) / 1024))
    return data


if __name__ == "__main__":
    build()
    previews()
