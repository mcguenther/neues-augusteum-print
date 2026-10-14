#!/usr/bin/env python3
"""Steckmechanismus mit 2,54-mm-Dupont-Teilen: Prototyp (Plan: stecker/dupont/PLAN.md).

Konzept:
  * Grundplatte: tiefe Mulde je Gebäude (Fuß taucht ein). Unter dem Muldenboden steht ein
    Steckerteil mit 4 Stiften nach oben; die Stifte ragen durch Löcher im Muldenboden.
      Dock A  abgewinkelte Stiftleiste, Lötenden waagrecht in den Kabelraum (Hauptlösung)
      Dock B  gerade Stiftleiste, Lötenden senkrecht nach unten
      Dock C  Dupont-Gehäuse mit Male-Crimp-Pins, ganz ohne Löten
    Jedes Teil wird von unten eingeschoben, der Muldenboden hält es gegen Zug, ein Stempel im
    Deckel gegen den Steckdruck.
  * Gebäude: Fuß (Grundfläche nach unten verlängert) mit Trichterplatte unten. Darüber steht das
    Dupont-Buchsengehäuse 1×4 senkrecht in einer Tasche, die Adern laufen oben über das Gehäuse zur
    LED, die flach auf dem Kammerboden liegt.
      Hauptlösung "Pause": Druck hält an der Oberkante der Tasche an, Gehäuse+Adern+LED werden als
      fertige Einheit eingelegt, danach überdruckt ein Riegel Gehäuse und Adern.
      Rückfallebene "Kassette": Gehäuse und LED sitzen in einer gedruckten Kassette, die von unten
      in den Fuß geschoben und von einem Schieber (zugleich Trichterplatte) gehalten wird.

Alle Maße in mm. Koordinaten im gesteckten Zustand: z = 0 ist die Plattenoberseite = Unterkante des
sichtbaren Gebäudes, +z nach oben, x entlang der Pin-Reihe, y quer. Die Mulde ist um (0, 0) zentriert,
die Pin-Reihe liegt bei y = HY.

Aufruf:
    python3 steckmodul_dupont.py   # STL nach stl/steckmodul_dupont/, Prüfbericht, Vorschau,
                                   # stecker/dupont/daten.json
    python3 stecker/dupont/baue_ansicht.py   # -> stecker/dupont/ansicht.html
"""
import json
import math
import os

import manifold3d as m3d
import numpy as np

from steckmodul import box, cbox, cyl, union, diff, frustum, to_tm, encode   # gemeinsame Werkzeuge

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "stl", "steckmodul_dupont")
DOC = os.path.join(HERE, "stecker", "dupont")
PREV = os.path.join(HERE, "vorschau", "steckmodul_dupont")

# --------------------------------------------------------------------------
# Kaufteile. Quelle je Wert: B = belegt (Zeichnung), M = gemessen am eigenen Teil, A = abgeleitet, S = geschätzt.
# Mit der Schieblehre nachmessen und hier eintragen (Passprobe: stl/steckmodul_dupont/passprobe.stl).
# --------------------------------------------------------------------------
PITCH = 2.54          # B  Raster
NPIN = 4
HSG_W = 10.16         # B  Gehäuse 1×4: Breite n·2,54 (Pololu-Zeichnung, ±0,3)
HSG_T = 2.54          # B  Gehäuse: Dicke
HSG_H = 14.00         # B  Gehäuse: Höhe 14,00 ±0,25
HSG_TOL = 0.25        # B  Plus-Toleranz der Höhe (Tasche wird so viel höher)
HSG_HOLE = 1.0        # S  Eintrittsöffnung je Kammer in der Steckseite
HSG_LATCH = 8.3       # B  Rastzungen-Zone ab Kabelseite (Pololu: 8,30)
TERM_L = 11.7         # B  Female-Crimp-Pin Länge (Pololu-Zeichnung)
TERM_BOX = 1.6        # B  Kontaktkasten 1,6 × 1,6
TERM_BOX_L = 4.5      # B  Kontaktkasten Länge
TERM_OFF = 0.5        # S  Kontaktkasten beginnt so weit hinter der Steckseite
CONTACT = 1.5         # S  Stift muss so tief in der Buchse stecken, bis die Feder anliegt
PIN_SQ = 0.64         # B  Vierkant der Stifte
HDR_W = NPIN * PITCH + 0.5   # M  Leistenstück, 4 Pins abgebrochen: Körper gemessen etwa 0,5 mm länger (Abbruchrest), Passprobe v4
HDR_BODY = 2.54       # B  Kunststoffkörper (Würth WR-PHD: 2,54 ±0,15)
HDR_UP = 7.0          # M  Steckseite über dem Körper: gemessen 7 ±0,5 (Datenblatt 6,0 ±0,2), Passprobe v4
HDR_TAIL = 3.0        # B  gerade Leiste: Lötende unter dem Körper (3,0 ±0,2)
RA_BACK = 1.0         # M  Winkelleiste: gerader Pin zwischen Körper und Biegung: gemessen 1 ±0,5 (Datenblatt 1,5 ±0,2)
RA_TAIL = 3.0         # B  Winkelleiste: Lötende ragt über die Körperseite hinaus (3,0 ±0,2)
MPIN_UP = 6.0         # S  Male-Crimp-Pin: so weit ragt der Stift aus dem Gehäuse
WIRE_D = 1.0          # S  Ader des Flachbandkabels (28 AWG, Isolation ≈ 0,9)
LED_W, LED_L, LED_T = 10.0, 16.7, 2.2   # WS2812B-Streifenstück (60 LED/m): Breite, Länge, Dicke
LED_FPC = 0.3         # S  Streifen ohne Chip (Folie + Klebeband)
PADS = ("GND", "DIN", "5V")  # Lötpads von −x nach +x, Din-Ende zum Gehäuse, Chip oben (am Streifen prüfen!)
PAD_X = 3.5           # S  Abstand der äußeren Pads von der Streifenmitte

# Passungen (FDM, 0,4er Düse)
CLR = 0.25            # Spiel je Seite: Fuß in der Mulde (Führungsband)
RELIEF = 0.30         # zusätzliches Spiel unter dem Führungsband (gegen Klemmen)
BAND = 5.0            # Höhe des engen Führungsbands unter der Muldenfase
SNUG = 0.22           # Spiel je Seite: Gehäuse/Leiste in der Tasche (Passprobe v4: Gehäuse 0,25 sitzt gut, darf etwas kleiner)
RIB = 0.12            # Übermaß der Crush-Rippen
HOLE = 1.25           # Stiftloch (Muldenboden, Trichterhals); Vierkant-Diagonale 0,91. Passprobe v4: 1,2 mit 0,3-Senkung geht ohne Kraft
FUNNEL_D = 2.4        # Trichteröffnung unten
WALL = 1.2
CH_F = 0.8            # 45°-Fase unten am Fuß
CH_P = 1.0            # 45°-Fase oben an der Mulde
FOOT_R = 0.5          # Rundung der senkrechten Fußkanten (Muldenecken drucken nicht scharf)
GUIDE = 3.0           # Fuß steckt so lang gerade in der Mulde, bevor eine Stiftspitze den Fuß erreicht
CEIL = 1.2            # Muldenboden über dem Steckerteil (hält es gegen Zug); dicker als 0,8, weil die Stifte mit 7 mm sonst zu tief in die Buchse reichen
FUNNEL_T = 1.0        # Trichterplatte unter dem Gehäuse (= Schieber bei der Kassette)

# Druck
LAYER = 0.2           # Schichthöhe, auch erste Schicht
WIRE_GAP = 0.2        # Luft über den Adern bis zur ersten Schicht nach der Pause
LED_GAP = 0.2         # Luft über dem LED-Chip bis zur Pausenebene
RIEGEL_T = 1.2        # Riegel über Gehäuse und Adern
LED_REC = 0.4         # LED liegt so tief in einer Mulde im Kammerboden
GROOVE = (1.2, 1.2)   # Querrinne für die DETECT-Brücke (Breite, Tiefe)
GAP_L = 1.6           # Abstand Sockel – LED (Platz für die Querrinne)

# Würfel / Platte
CUBE = 30.0
CUBE_H = 24.0         # sichtbare Höhe
SHELL = 1.2
ROOF = 1.2
KEY = 3.0             # Kodier-Ecke (−x, −y)
DOCK_PITCH = 36.0
VARIANTS = ("A", "B", "C")
LID_T = 2.0
SCREW_PILOT, SCREW_CLR = 2.5, 3.2      # M3-Blechschraube / Gewindeformer
TONGUE = dict(L=10.0, t=1.2, z0=-5.0, z1=-1.2, gap=0.6, bump=0.5)   # Federzunge in der Muldenwand
KASS_CLR = 0.2        # Kassette im Fußschacht
KEY_CLR = 0.15        # Schieber in der Schwalbenschwanz-Nut

# Gebäude (Laserscan 1:1500, B × T × H in mm, aus dem ersten Plan)
BUILDINGS = [("Paulinum", 39.6, 24.6, 39.2), ("Neues Augusteum", 42.1, 51.9, 25.0),
             ("Hörsaalgebäude", 55.1, 90.7, 16.4), ("Seminargebäude", 26.3, 66.7, 18.8),
             ("Institutsgebäude", 70.3, 29.9, 21.1), ("City-Hochhaus", 31.3, 30.4, 96.4),
             ("Moritzbastei", 44.6, 43.0, 6.1)]


def layer_up(v):
    return math.ceil(v / LAYER - 1e-6) * LAYER


def layer_down(v):
    return math.floor(v / LAYER + 1e-6) * LAYER


def keyed_cs(w, d, key):
    pts = [(-w / 2 + key, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2), (-w / 2, -d / 2 + key)]
    return m3d.CrossSection([pts])


def ext(cs, z0, z1):
    return m3d.Manifold.extrude(cs, z1 - z0).translate([0, 0, z0])


def keyed(w, d, z0, z1, key, cx=0.0, cy=0.0):
    return ext(keyed_cs(w, d, key), z0, z1).translate([cx, cy, 0])


def ccw(pts):
    a = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]))
    return pts if a > 0 else pts[::-1]


def prism_x(pts, x0, x1):
    """Profil in (y, z), entlang x extrudiert."""
    return m3d.Manifold.extrude(m3d.CrossSection([ccw(pts)]), x1 - x0).rotate([90, 0, 90]).translate([x0, 0, 0])


def prism_y(pts, y0, y1):
    """Profil in (x, z), entlang y extrudiert."""
    return m3d.Manifold.extrude(m3d.CrossSection([ccw(pts)]), y1 - y0).rotate([90, 0, 0]).translate([0, y1, 0])


def capsule(a, b, r, n=10):
    s = m3d.Manifold.sphere(r, n)
    return m3d.Manifold.batch_hull([s.translate(list(a)), s.translate(list(b))])


def vol_int(a, b):
    return (a ^ b).volume()


# --------------------------------------------------------------------------
# Maßkette
# --------------------------------------------------------------------------
def pin_x():
    """x der Pins 1..4 (1 GND, 2 DIN, 3 +5 V, 4 DETECT). Pin 1 liegt auf der Seite des GND-Pads."""
    xs = [(i - 1.5) * PITCH for i in range(NPIN)]
    return xs if PADS[0] == "GND" else xs[::-1]


def pad_x(name):
    return {PADS[0]: -PAD_X, PADS[1]: 0.0, PADS[2]: PAD_X}[name]


def dims():
    g1 = HDR_UP - CEIL                       # Hub, bei dem die Stiftspitze die Fußunterseite erreicht
    F = layer_up(g1 + GUIDE + CH_F + CH_P)   # Fußhöhe = Muldentiefe
    z_hb = -F - CEIL                         # Oberkante Leistenkörper (Dock A, B) bzw. Steckseite (C)
    z_tip = z_hb + HDR_UP                    # Stiftspitzen
    z_face = -F + FUNNEL_T                   # Steckseite der Buchse im Gebäude
    E = z_tip - z_face                       # Einstecktiefe der Stifte in der Buchse
    z_ht = z_face + HSG_H                    # Kabelseite der Buchse (nominal)
    z_pt = z_ht + HSG_TOL                    # Taschenoberkante (für die längste Buchse)
    z_cav = -F + layer_up(z_pt + WIRE_D + WIRE_GAP + F)          # Pausenebene
    z_s = -F + layer_down(z_cav - LED_GAP - LED_T + F)           # LED-Unterseite
    z_floor = z_s + LED_REC                  # Kammerboden
    pause_mm = z_cav + F                     # Druckhöhe über dem Bett
    # Grundriss der Einheit (Gehäuse + Sockel + Rinne + LED) entlang y, mittig im Würfel
    pk_w, pk_d = HSG_W + 2 * SNUG, HSG_T + 2 * SNUG
    sock_w, sock_d = pk_w + 2 * WALL, pk_d + 2 * WALL
    total = sock_d + GAP_L + LED_L + 0.3
    HY = -total / 2 + sock_d / 2
    LY0 = HY + sock_d / 2 + GAP_L            # LED-Anfang (Pad-Ende)
    # Platte
    z_bb = z_hb - HDR_BODY                   # Unterkante Leistenkörper
    z_bend = z_bb - RA_BACK                  # Winkelleiste: Biegung / Lötenden
    z_tailB = z_bb - HDR_TAIL                # gerade Leiste: Ende der Lötstifte
    z_mcb = z_hb - HSG_H                     # Dock C: Kabelseite des Gehäuses
    z_lt = layer_down(min(z_bend - 3.0, z_tailB - 3.5, z_mcb - 4.0))   # Deckel-Oberseite
    return dict(
        g1=g1, F=F, z_hb=z_hb, z_tip=z_tip, z_face=z_face, E=E, z_ht=z_ht, z_pt=z_pt, z_cav=z_cav,
        z_s=z_s, z_floor=z_floor, z_riegel=z_cav + RIEGEL_T, z_notch=z_ht - 1.0,
        guide=F - g1 - CH_F - CH_P, contact_lift=E - CONTACT, chamfer_lift=F,
        pause_mm=pause_mm, pause_layer=int(round(pause_mm / LAYER)),
        led_top=z_s + LED_T, wire_top=z_ht + WIRE_D,
        pk_w=pk_w, pk_d=pk_d, sock_w=sock_w, sock_d=sock_d, HY=HY, LY0=LY0, LY1=LY0 + LED_L,
        z_bb=z_bb, z_bend=z_bend, z_tailB=z_tailB, z_mcb=z_mcb, z_lt=z_lt, z_lb=z_lt - LID_T,
        pw=CUBE + 2 * CLR, plate_t=0 - (z_lt - LID_T),
        # Kassette: gleiche Höhen wie die Pause-Variante (Schieber = Trichterplatte)
        z_kt=z_s + LED_REC, z_kceil=z_pt + CEIL)


# --------------------------------------------------------------------------
# Kaufteile als Platzhalter
# --------------------------------------------------------------------------
def housing_part(z0, flip=False):
    """Dupont-Gehäuse 1×4, Steckseite bei z0 (unten) bzw. bei z0 oben, wenn flip (Dock C)."""
    d = dims()
    HY = d["HY"]
    body = cbox(HSG_W, HSG_T, 0, HSG_H, cy=0)
    cut = []
    for x in [(i - 1.5) * PITCH for i in range(NPIN)]:
        cut.append(cbox(HSG_HOLE, HSG_HOLE, -0.01, 0.6, cx=x))           # Eintrittsöffnung
        cut.append(cbox(1.8, 1.8, 0.6, HSG_H + 0.01, cx=x))              # Kammer
        cut.append(cbox(1.4, 0.35, HSG_H - HSG_LATCH, HSG_H - 1.0, cx=x, cy=-HSG_T / 2 + 0.17))  # Rastfenster (−y)
    h = diff(body, *cut)
    if flip:
        h = h.mirror([0, 0, 1]).translate([0, 0, z0])
    else:
        h = h.translate([0, 0, z0])
    return h.translate([0, HY, 0])


def terminals_part(z0, male=False, flip=False):
    """Crimpkontakte in den Kammern (nur Darstellung): Female = Kasten + Crimpzone, Male = Stift."""
    d = dims()
    parts = []
    for x in pin_x():
        if male:
            p = union([cbox(PIN_SQ, PIN_SQ, -MPIN_UP, 0.6, cx=x), cbox(1.5, 1.5, 0.8, 6.0, cx=x),
                       cbox(1.0, 1.0, 6.0, 11.5, cx=x)])
        else:
            box_ = diff(cbox(1.5, 1.5, TERM_OFF, TERM_OFF + TERM_BOX_L, cx=x),
                        cbox(1.0, 1.0, TERM_OFF - 0.01, TERM_OFF + TERM_BOX_L + 0.01, cx=x))
            p = union([box_, cbox(1.2, 1.2, TERM_OFF + TERM_BOX_L, TERM_OFF + TERM_L, cx=x)])
        parts.append(p)
    t = union(parts)
    t = t.mirror([0, 0, 1]).translate([0, 0, z0]) if flip else t.translate([0, 0, z0])
    return t.translate([0, d["HY"], 0])


def header_part(variant):
    """A: Winkelleiste (Stifte hoch, Lötenden nach +y), B: gerade Leiste, C: Male-Crimp im Gehäuse."""
    d = dims()
    HY, z_hb, z_bb = d["HY"], d["z_hb"], d["z_bb"]
    if variant == "C":
        return union([housing_part(z_hb, flip=True), terminals_part(z_hb, male=True, flip=True)])
    body = cbox(HDR_W, HDR_BODY, z_bb, z_hb, cy=HY)
    pins = []
    for x in pin_x():
        if variant == "A":
            zb = d["z_bend"]
            pins.append(cbox(PIN_SQ, PIN_SQ, zb - PIN_SQ / 2, d["z_tip"], cx=x, cy=HY))
            pins.append(box(x - PIN_SQ / 2, x + PIN_SQ / 2, HY - PIN_SQ / 2, HY + HDR_BODY / 2 + RA_TAIL,
                            zb - PIN_SQ / 2, zb + PIN_SQ / 2))
        else:
            pins.append(cbox(PIN_SQ, PIN_SQ, d["z_tailB"], d["z_tip"], cx=x, cy=HY))
    return union([body] + pins)


def wire_paths():
    """Adern im Gebäude: aus der Buchse nach oben, über den Sockel zur LED. DETECT läuft in der
    Querrinne unter den anderen Adern zum GND-Pad."""
    d = dims()
    HY, r = d["HY"], WIRE_D / 2
    zw = d["z_ht"] + r                       # Ader liegt auf der Kabelseite der Buchse
    y_out = HY + d["sock_d"] / 2 + 0.4       # hinter dem Sockel
    y_pad = d["LY0"] + 1.2
    z_pad = d["z_s"] + LED_FPC + r
    y_g = HY + d["sock_d"] / 2 + 0.2 + GROOVE[0] / 2
    z_g = d["z_floor"] - GROOVE[1] + r + 0.05
    names = ("GND", "DIN", "5V")
    paths = []
    for i, x in enumerate(pin_x()):
        start = (x, HY, d["z_ht"] - 0.6)
        if i < 3:
            px = pad_x(names[i])
            paths.append([start, (x, HY, zw), (x, y_out, zw), (px, y_pad, z_pad)])
        else:
            gx = pad_x("GND")
            paths.append([start, (x, HY, zw), (x, y_g, zw), (x, y_g, z_g), (gx, y_g, z_g),
                          (gx + 0.6, y_g + 0.6, z_pad), (gx + 0.6, y_pad + 0.6, z_pad)])
    return paths


def wires_part(shift=(0, 0, 0)):
    segs = []
    for path in wire_paths():
        for a, b in zip(path[:-1], path[1:]):
            segs.append(capsule(np.add(a, shift), np.add(b, shift), WIRE_D / 2 * 0.95))
    return union(segs)


def led_part(z_s=None):
    d = dims()
    z_s = d["z_s"] if z_s is None else z_s
    y0 = d["LY0"]
    strip = box(-LED_W / 2, LED_W / 2, y0, y0 + LED_L, z_s, z_s + LED_FPC)
    chip = cbox(5.0, 5.0, z_s + LED_FPC, z_s + LED_T, cy=y0 + LED_L / 2)
    pads = [cbox(2.0, 1.6, z_s + LED_FPC, z_s + LED_FPC + 0.05, cx=pad_x(n), cy=y0 + 1.0) for n in PADS]
    return union([strip, chip] + pads)


# --------------------------------------------------------------------------
# Gebäude (Würfel) mit Fuß
# --------------------------------------------------------------------------
def foot_solid(F):
    cs = keyed_cs(CUBE, CUBE, KEY).offset(-FOOT_R, m3d.JoinType.Round).offset(FOOT_R, m3d.JoinType.Round)
    fp = ext(cs, -F, 0.01)
    return fp ^ frustum(CUBE - 2 * CH_F, CUBE - 2 * CH_F, -F, 0.01, F + 0.01)   # 45°-Fase unten


def z_detent():
    """Höhe der Rastnut am Fuß bzw. der Federnase in der Mulde (gesteckt)."""
    return (TONGUE["z0"] + TONGUE["z1"]) / 2


def funnel_holes(z0, cy):
    """Trichter in der Trichterplatte: unten FUNNEL_D, nach (FUNNEL_D−HOLE)/2 auf HOLE, 45°."""
    h = (FUNNEL_D - HOLE) / 2
    out = []
    for x in pin_x():
        cone = m3d.Manifold.cylinder(h + 0.01, FUNNEL_D / 2 + 0.01, HOLE / 2, 24).translate([x, cy, z0 - 0.01])
        out.append(cone)
        out.append(cyl(HOLE / 2, z0, z0 + FUNNEL_T + 0.02, cx=x, cy=cy, n=24))
    return out


def unit_cuts(riegel=True):
    """Tasche (mit Aderraum), Kerbe, Trichter, Querrinne, LED-Mulde, Pin-1-Kerbe."""
    d = dims()
    HY = d["HY"]
    cuts = [cbox(d["pk_w"], d["pk_d"], d["z_face"], d["z_cav"] + (0 if riegel else 5.0), cy=HY)]
    xw = abs(pin_x()[0]) + WIRE_D / 2 + 0.6
    cuts.append(box(-xw, xw, HY + d["pk_d"] / 2 - 0.01, HY + d["sock_d"] / 2 + 0.01, d["z_notch"],
                    d["z_cav"] + (0 if riegel else 5.0)))
    cuts += funnel_holes(-d["F"], HY)
    y_g0 = HY + d["sock_d"] / 2 + 0.2
    gx = sorted([pin_x()[3], pad_x("GND")])
    cuts.append(box(gx[0] - 0.9, gx[1] + 0.9, y_g0, y_g0 + GROOVE[0], d["z_floor"] - GROOVE[1], d["z_floor"] + 0.01))
    cuts.append(box(-LED_W / 2 - 0.15, LED_W / 2 + 0.15, d["LY0"] - 0.15, d["LY1"] + 0.15, d["z_s"],
                    d["z_floor"] + 0.01))
    # Pin-1-Marke: Kerbe oben in der −y-Wand des Sockels über Pin 1
    zt = d["z_riegel"] if riegel else d["z_cav"]
    cuts.append(prism_y([(pin_x()[0] - 0.8, zt + 0.01), (pin_x()[0] + 0.8, zt + 0.01), (pin_x()[0], zt - 0.8)],
                        HY - d["sock_d"] / 2 - 0.01, HY - d["pk_d"] / 2 - 0.3))
    return cuts


def unit_ribs():
    """Crush-Rippen in der Gehäusetasche: Stirnseiten (±x) und glatte Seite (+y). Die −y-Seite mit
    den Rastfenstern bleibt frei, damit die Zungen die Kontakte nicht entriegeln."""
    d = dims()
    HY, zf = d["HY"], d["z_face"]
    ribs = []
    for sx in (-1, 1):
        ribs.append(cbox(2 * RIB + 0.2, 0.6, zf + 2.0, zf + 11.0, cx=sx * (d["pk_w"] / 2 - RIB + 0.1), cy=HY))
    for x in (-2.54, 2.54):
        ribs.append(cbox(0.6, 2 * RIB + 0.2, zf + 2.0, zf + 11.0, cx=x, cy=HY + d["pk_d"] / 2 - RIB + 0.1))
    return ribs


def sockel_solid(z_top):
    d = dims()
    return cbox(d["sock_w"], d["sock_d"], d["z_s"] - 0.01, z_top, cy=d["HY"])


def light_windows():
    cut = []
    for cx_, cy_, axis in ((0, -1, "y"), (0, 1, "y"), (-1, 0, "x"), (1, 0, "x")):
        for z0, t in ((10.0, 0.4), (16.0, 0.8)):
            if axis == "y":
                cut.append(cbox(6.0, SHELL - t + 0.01, z0, z0 + 4.5, cy=cy_ * (CUBE / 2 - SHELL + (SHELL - t) / 2)))
            else:
                cut.append(cbox(SHELL - t + 0.01, 6.0, z0, z0 + 4.5, cx=cx_ * (CUBE / 2 - SHELL + (SHELL - t) / 2)))
    return cut


def detent_cut():
    zd = z_detent()
    w = TONGUE["bump"] + 0.15
    return prism_y([(CUBE / 2 + 0.01, zd - w - 0.1), (CUBE / 2 - w + 0.05, zd), (CUBE / 2 + 0.01, zd + w + 0.1)],
                   -CUBE / 2 + 4.0, CUBE / 2 - 4.0)


def cube_pause():
    """Hauptlösung: Würfel mit Fuß, Gehäusetasche, Riegel (wird nach der Pause gedruckt)."""
    d = dims()
    F = d["F"]
    body = union([keyed(CUBE, CUBE, 0, CUBE_H, KEY), foot_solid(F)])
    chamber = keyed(CUBE - 2 * SHELL, CUBE - 2 * SHELL, d["z_floor"], CUBE_H - ROOF, KEY - 0.4)
    m = diff(body, chamber)
    m = union([m, sockel_solid(d["z_riegel"])])
    m = diff(m, *(unit_cuts(True) + light_windows() + [detent_cut()]))
    return union([m] + unit_ribs())


def unit_block(riegel):
    """Pausenprobe (riegel=True, mit Pause drucken) bzw. Montagelehre (riegel=False): Ausschnitt um
    Sockel und LED-Mulde, gleiche Höhen wie im Gebäude."""
    d = dims()
    HY = d["HY"]
    y0, y1 = HY - d["sock_d"] / 2 - 2.0, d["LY1"] + 2.0
    m = box(-8.5, 8.5, y0, y1, -d["F"], d["z_floor"])
    m = union([m, sockel_solid(d["z_riegel"] if riegel else d["z_cav"])])
    m = diff(m, *unit_cuts(riegel))
    return union([m] + unit_ribs())


# ---- Rückfallebene: Kassette von unten, Schieber als Trichterplatte ----
def kass_outline():
    d = dims()
    HY = d["HY"]
    y0 = HY - d["sock_d"] / 2
    y1 = d["LY1"] + 0.15 + WALL
    return -d["sock_w"] / 2, d["sock_w"] / 2, y0, y1


def key_half(clr):
    """Schwalbenschwanz-Schieber, gleitet entlang y: unten halbe Breite, oben je Seite FUNNEL_T mehr (45°)."""
    x0, x1, y0, y1 = kass_outline()
    return (x1 - x0) / 2 + 1.5 - clr


def key_prism(clr, y0, y1, z_extra=0.0):
    d = dims()
    F, hb = d["F"], key_half(clr)
    prof = [(-hb, -F - z_extra), (hb, -F - z_extra), (hb + FUNNEL_T, -F + FUNNEL_T), (-hb - FUNNEL_T, -F + FUNNEL_T)]
    return prism_y(prof, y0, y1)


def schieber():
    d = dims()
    F = d["F"]
    k = key_prism(KEY_CLR, -CUBE / 2, CUBE / 2)
    k = k ^ ext(keyed_cs(CUBE, CUBE, KEY).offset(-FOOT_R, m3d.JoinType.Round).offset(FOOT_R, m3d.JoinType.Round),
                -F - 1, -F + FUNNEL_T + 1)
    k = k ^ frustum(CUBE - 2 * CH_F, CUBE - 2 * CH_F, -F, 0.01, F + 0.01)
    k = diff(k, *funnel_holes(-F, d["HY"]))
    # Griffkerbe an der +y-Stirn
    k = diff(k, cbox(6.0, 1.0, -F - 0.01, -F + 0.5, cy=CUBE / 2 - 0.5))
    return k


def kassette():
    d = dims()
    HY, zk0 = d["HY"], -d["F"] + FUNNEL_T
    x0, x1, y0, y1 = kass_outline()
    body = box(x0, x1, y0, y1, zk0, d["z_kt"])
    body = union([body, cbox(d["sock_w"], d["sock_d"], zk0, d["z_kceil"], cy=HY)])
    cut = [cbox(d["pk_w"], d["pk_d"], zk0 - 0.01, d["z_pt"], cy=HY),                    # Gehäusetasche, unten offen
           cbox(abs(pin_x()[0]) * 2 + WIRE_D + 0.3, WIRE_D + 0.3, d["z_pt"] - 0.01, d["z_kceil"] + 0.01, cy=HY)]  # Aderschlitz
    y_g0 = HY + d["sock_d"] / 2 + 0.2
    gx = sorted([pin_x()[3], pad_x("GND")])
    cut.append(box(gx[0] - 0.9, gx[1] + 0.9, y_g0, y_g0 + GROOVE[0], d["z_kt"] - GROOVE[1], d["z_kt"] + 0.01))
    cut.append(box(-LED_W / 2 - 0.15, LED_W / 2 + 0.15, d["LY0"] - 0.15, d["LY1"] + 0.15, d["z_s"], d["z_kt"] + 0.01))
    # Aderweg über die +y-Wand der Tasche zur LED
    xw = abs(pin_x()[0]) + WIRE_D / 2 + 0.6
    cut.append(box(-xw, xw, HY - 0.6, HY + d["sock_d"] / 2 + 0.01, d["z_kceil"] - 0.6, d["z_kceil"] + 0.01))
    k = diff(body, *cut)
    return union([k] + unit_ribs()), (zk0, d["z_kceil"])


def kass_wire_paths():
    d = dims()
    HY, r = d["HY"], WIRE_D / 2
    zw = d["z_kceil"] - 0.6 + r
    y_out = HY + d["sock_d"] / 2 + 0.4
    y_pad = d["LY0"] + 1.2
    z_pad = d["z_s"] + LED_FPC + r
    y_g = HY + d["sock_d"] / 2 + 0.2 + GROOVE[0] / 2
    z_g = d["z_kt"] - GROOVE[1] + r + 0.05
    paths = []
    for i, x in enumerate(pin_x()):
        start = (x, HY, d["z_ht"] - 0.6)
        if i < 3:
            px = pad_x(("GND", "DIN", "5V")[i])
            paths.append([start, (x, HY, zw), (x, y_out, zw), (px, y_pad, z_pad)])
        else:
            gx = pad_x("GND")
            paths.append([start, (x, HY, zw), (x, y_g, zw), (x, y_g, z_g), (gx, y_g, z_g),
                          (gx + 0.6, y_g + 0.6, z_pad), (gx + 0.6, y_pad + 0.6, z_pad)])
    return paths


def kass_wires_part():
    segs = []
    for path in kass_wire_paths():
        for a, b in zip(path[:-1], path[1:]):
            segs.append(capsule(a, b, WIRE_D / 2 * 0.95))
    return union(segs)


def cube_kassette():
    d = dims()
    F = d["F"]
    x0, x1, y0, y1 = kass_outline()
    body = union([keyed(CUBE, CUBE, 0, CUBE_H, KEY), foot_solid(F)])
    zf = d["z_kt"]
    chamber = keyed(CUBE - 2 * SHELL, CUBE - 2 * SHELL, zf + 1.2, CUBE_H - ROOF, KEY - 0.4)
    c = KASS_CLR
    groove = key_prism(0.0, -CUBE, CUBE, z_extra=0.01)
    cuts = [chamber, groove,
            box(x0 - c, x1 + c, y0 - c, y1 + c, -F, zf),                                    # Schacht
            box(-LED_W / 2 - 0.15, LED_W / 2 + 0.15, d["LY0"] - 1.6, d["LY1"] + 0.15, zf - 0.01, zf + 1.21),  # Fenster
            cbox(d["sock_w"] + 2 * c, d["sock_d"] + 2 * c, zf - 0.01, d["z_kceil"] + 0.3, cy=d["HY"]),  # Sockel ragt durch
            ]
    m = diff(body, *(cuts + light_windows() + [detent_cut()]))
    return m


# --------------------------------------------------------------------------
# Platte mit drei Docks und Deckel
# --------------------------------------------------------------------------
def dock_room(variant, d):
    top = {"A": d["z_bb"], "B": d["z_bb"], "C": d["z_mcb"]}[variant]
    return top


def pocket_cuts(cx, d):
    F, pw = d["F"], d["pw"]
    zb = -CH_P - BAND
    return [keyed(pw, pw, zb, 0.01, KEY, cx=cx),
            frustum(pw, pw, -CH_P, 0.01, CH_P + 0.01, cx=cx),
            keyed(pw + 2 * RELIEF, pw + 2 * RELIEF, -F, zb + 0.01, KEY, cx=cx)]


def tongue_cuts(cx, d):
    """Federzunge in der +x-Muldenwand: waagrechter Biegebalken (in der XY-Ebene)."""
    T = TONGUE
    xw = cx + d["pw"] / 2
    y0, y1 = -T["L"] / 2, T["L"] / 2
    zl = T["z0"] - T["gap"]
    return [box(xw + T["t"], xw + T["t"] + 0.8, y0 - 0.8, y1 + 0.8, zl, 0.01),        # Spalt hinter der Zunge
            box(xw - 0.01, xw + T["t"] + 0.01, y1, y1 + 0.8, zl, 0.01),               # freies Ende
            box(xw - 0.01, xw + T["t"] + 0.01, y0 - 0.8, y1 + 0.8, zl, T["z0"]),      # Spalt unter der Zunge
            box(xw - 0.01, xw + T["t"] + 0.01, y0 - 0.8, y1 + 0.8, T["z1"], 0.01)]    # über der Zunge offen


def tongue_bump(cx, d):
    T = TONGUE
    xw = cx + d["pw"] / 2
    zd = z_detent()
    b = T["bump"]
    return prism_y([(xw + 0.05, zd - b - 0.05), (xw - b, zd), (xw + 0.05, zd + b + 0.05)], -T["L"] / 2 + 1.0, T["L"] / 2 - 0.5)


def dock_cuts(variant, cx, d):
    HY, F = d["HY"], d["F"]
    cuts = pocket_cuts(cx, d) + tongue_cuts(cx, d)
    for x in pin_x():                                         # Stiftlöcher im Muldenboden
        cuts.append(cyl(HOLE / 2, d["z_hb"] - 0.01, -F + 0.01, cx=cx + x, cy=HY, n=20))
    room_top = dock_room(variant, d)
    if variant in ("A", "B"):
        cuts.append(cbox(HDR_W + 2 * SNUG, HDR_BODY + 2 * SNUG, d["z_bb"] - 0.01, d["z_hb"], cx=cx, cy=HY))
    else:
        cuts.append(cbox(HSG_W + 2 * SNUG, HSG_T + 2 * SNUG, d["z_mcb"] - 0.01, d["z_hb"], cx=cx, cy=HY))
    cuts.append(box(cx - 9.0, cx + 9.0, HY - 5.0, HY + 9.0, d["z_lt"] - 0.01, room_top))          # Kabelraum
    return cuts


def dock_ribs(variant, cx, d):
    HY = d["HY"]
    ribs = []
    if variant in ("A", "B"):
        z0, z1, w, t = d["z_bb"], d["z_hb"], HDR_W, HDR_BODY
    else:
        z0, z1, w, t = d["z_mcb"] + 1.0, d["z_hb"] - 1.0, HSG_W, HSG_T
    for sx in (-1, 1):
        ribs.append(cbox(2 * RIB + 0.2, 0.6, z0, z1, cx=cx + sx * (w / 2 + SNUG - RIB + 0.1), cy=HY))
    for x in (-2.54, 2.54):
        ribs.append(cbox(0.6, 2 * RIB + 0.2, z0, z1, cx=cx + x, cy=HY + t / 2 + SNUG - RIB + 0.1))
    return ribs


def plate_extent():
    xs = [(i - 1) * DOCK_PITCH for i in range(3)]
    half_x = xs[-1] + CUBE / 2 + CLR + RELIEF + 6.0
    half_y = CUBE / 2 + CLR + RELIEF + 6.0
    return xs, half_x, half_y


def screw_xy():
    xs, hx, hy = plate_extent()
    return [(sx * (hx - 4.5), sy * (hy - 4.5)) for sx in (-1, 1) for sy in (-1, 1)]


def plate(with_bump=True):
    d = dims()
    xs, hx, hy = plate_extent()
    blk = box(-hx, hx, -hy, hy, d["z_lt"], 0.0)
    cuts = []
    for v, cx in zip(VARIANTS, xs):
        cuts += dock_cuts(v, cx, d)
        # Rinne vom Kabelraum zur hinteren Kante (+y)
        cuts.append(box(cx - 4.0, cx + 4.0, d["HY"], hy + 0.01, d["z_lt"] - 0.01, d["z_lt"] + 4.0))
    for x, y in screw_xy():
        cuts.append(cyl(SCREW_PILOT / 2, d["z_lt"] - 0.01, d["z_lt"] + 9.0, cx=x, cy=y))
    p = diff(blk, *cuts)
    add = []
    for v, cx in zip(VARIANTS, xs):
        add += dock_ribs(v, cx, d)
        if with_bump:
            add.append(tongue_bump(cx, d))
    p = union([p] + add)
    try:
        import generate
        letters = []
        for v, cx in zip(VARIANTS, xs):
            cs = generate.text_cross_section(v, 4.0, cx, -hy + 1.0, anchor="center")
            if cs is not None:
                letters.append(m3d.Manifold.extrude(cs, 0.6).translate([0, 0, -0.4]))
        p = diff(p, *letters)
    except Exception as e:  # Gravur ist nur Zierde
        print("  (Gravur übersprungen: %s)" % e)
    return p, xs


def lid():
    d = dims()
    xs, hx, hy = plate_extent()
    l = box(-hx, hx, -hy, hy, d["z_lb"], d["z_lt"])
    posts = []
    for v, cx in zip(VARIANTS, xs):
        if v in ("A", "B"):
            top, xi, xo = d["z_bb"], HDR_W / 2 - 0.75, HDR_W / 2 + 0.6
        else:
            top, xi, xo = d["z_mcb"], HSG_W / 2 - 0.63, HSG_W / 2 + 0.8
        for sx in (-1, 1):
            posts.append(box(cx + min(sx * xi, sx * xo), cx + max(sx * xi, sx * xo), d["HY"] - 1.0, d["HY"] + 1.0,
                             d["z_lt"] - 0.01, top))
    l = union([l] + posts)
    return diff(l, *[cyl(SCREW_CLR / 2, d["z_lb"] - 0.01, d["z_lt"] + 0.01, cx=x, cy=y) for x, y in screw_xy()])


# --------------------------------------------------------------------------
# Passprobe
# --------------------------------------------------------------------------
def passprobe():
    """Gehäusetaschen (0,0/0,1/0,2 Spiel), Leistentaschen, Stiftlöcher 1,0/1,1/1,2, Trichter."""
    blk = box(-31, 31, -14, 14, 0, 9)
    cuts = []
    for i, c in enumerate((0.0, 0.1, 0.2)):
        x = -20 + i * 20
        cuts.append(cbox(HSG_W + 2 * c, HSG_T + 2 * c, 2.0, 9.01, cx=x, cy=-8))
        cuts.append(cbox(HDR_W + 2 * c, HDR_BODY + 2 * c, 9 - HDR_BODY, 9.01, cx=x, cy=0))
        for j, hd in enumerate((1.0, 1.1, 1.2)):                 # Lochreihe, durchgehend
            cuts.append(cyl(hd / 2, -0.01, 9.01, cx=x - 5 + j * 5, cy=8, n=24))
        # Kerbe als Spielmarke: 0, 1 oder 2 Striche
        for k in range(i):
            cuts.append(cbox(0.6, 3.0, 8.4, 9.01, cx=x + 7 + k * 1.2, cy=-12.4))
    return diff(blk, *cuts)


# --------------------------------------------------------------------------
# Prüfungen
# --------------------------------------------------------------------------
def checks(parts):
    d = dims()
    out = []

    def ck(name, a, b, limit=0.05, note=None):
        v = vol_int(a, b)
        ok = v <= limit
        out.append((name, v, ok if note is None else True, note))
        return v

    xs = parts["xs"]
    for v, cx in zip(VARIANTS, xs):
        sh = lambda m: m.translate([cx, 0, 0])
        pl, hd, li = parts["plate"], sh(parts["header"][v]), parts["lid"]
        mov = {"Würfel": sh(parts["cube"]), "Buchse": sh(parts["housing"]), "Adern": sh(parts["wires"]),
               "LED": sh(parts["led"])}
        t = "Dock %s, gesteckt: " % v
        for n, m in mov.items():
            ck(t + n + " ↔ Platte", m, pl)
            ck(t + n + " ↔ Steckerteil", m, hd)
            ck(t + n + " ↔ Deckel", m, li)
        ck(t + "Steckerteil ↔ Platte", hd, pl, note="Rippen-Übermaß" if True else None)
        ck(t + "Steckerteil ↔ Deckel", hd, li)
        ck(t + "Deckel ↔ Platte", li, pl)
        ck(t + "Adern ↔ Würfel", mov["Adern"], mov["Würfel"])
        ck(t + "LED ↔ Würfel", mov["LED"], mov["Würfel"])
        ck(t + "Adern ↔ LED", mov["Adern"], mov["LED"], limit=2.0, note="Lötstellen")
        ck(t + "Buchse ↔ Würfel", mov["Buchse"], mov["Würfel"], note="Rippen-Übermaß")
        ck(t + "Adern ↔ Buchse", mov["Adern"], mov["Buchse"], limit=1.5, note="Adern stecken in der Buchse")
        # Kassette (Rückfallebene)
        k = {"Würfel K": sh(parts["cube_k"]), "Kassette": sh(parts["kass"]), "Schieber": sh(parts["key"]),
             "Buchse": sh(parts["housing"]), "LED": sh(parts["led"]), "Adern K": sh(parts["wires_k"])}
        t = "Dock %s, Kassette: " % v
        for a in ("Würfel K", "Kassette", "Schieber", "LED", "Adern K"):
            ck(t + a + " ↔ Platte", k[a], pl)
            ck(t + a + " ↔ Steckerteil", k[a], hd)
        ck(t + "Kassette ↔ Würfel K", k["Kassette"], k["Würfel K"])
        ck(t + "Schieber ↔ Würfel K", k["Schieber"], k["Würfel K"])
        ck(t + "Schieber ↔ Kassette", k["Schieber"], k["Kassette"])
        ck(t + "Buchse ↔ Würfel K", k["Buchse"], k["Würfel K"])
        ck(t + "Buchse ↔ Kassette", k["Buchse"], k["Kassette"], note="Rippen-Übermaß")
        ck(t + "LED ↔ Würfel K", k["LED"], k["Würfel K"])
        ck(t + "LED ↔ Kassette", k["LED"], k["Kassette"])
        ck(t + "Adern K ↔ Würfel K", k["Adern K"], k["Würfel K"])
        ck(t + "Adern K ↔ Kassette", k["Adern K"], k["Kassette"])
    return out


def insertion_checks(parts):
    """Beim Stecken: bewegte Teile (Gebäude + Einbauten) gegen Platte (ohne Federnase) und Stecker."""
    d = dims()
    lifts = [("über der Mulde", d["F"] + 2.0), ("Fase fängt", d["F"]), ("Fase zu Ende", d["F"] - CH_F - CH_P),
             ("Stiftspitze an der Trichterplatte", d["g1"]), ("Stift erreicht die Buchse", d["E"]),
             ("elektrischer Kontakt", d["contact_lift"]), ("1 mm vor Anschlag", 1.0), ("gesteckt", 0.0)]
    out = []
    pl = parts["plate_nobump"]
    for v, cx in zip(VARIANTS, parts["xs"]):
        hd = parts["header"][v].translate([cx, 0, 0])
        for lab, g in lifts:
            for mname, mov in (("Pause", ["cube", "housing", "wires", "led"]),
                               ("Kassette", ["cube_k", "kass", "key", "housing", "wires_k", "led"])):
                tot_p = tot_h = 0.0
                for n in mov:
                    m = parts[n].translate([cx, 0, g])
                    if n in ("housing",):
                        tot_h += vol_int(m, hd)
                        tot_p += vol_int(m, pl)
                        continue
                    tot_p += vol_int(m, pl)
                    tot_h += vol_int(m, hd)
                out.append((v, mname, lab, g, tot_p, tot_h))
    # Federnase: gewollte Überdeckung während des Steckens
    bump = [vol_int(parts["cube"].translate([0, 0, g]), tongue_bump(0, d)) for _, g in lifts]
    return out, lifts, bump


# --------------------------------------------------------------------------
# Kräfte (Abschätzung; Kontaktkräfte sind für Kit-Teile nicht belegt)
# --------------------------------------------------------------------------
E_PLA = 3500.0        # N/mm², Biegemodul PLA (PETG ≈ 2000)
MU = 0.3              # Reibwert PLA/PLA
PIN_PULL = (0.3, 1.0)   # S  Haltekraft je Stift in einer Dupont-Buchse, N
PIN_PUSH = (1.0, 2.0)   # S  Steckkraft je Stift, N


def forces():
    T = TONGUE
    b, t, L = T["z1"] - T["z0"], T["t"], T["L"]
    delta = T["bump"] - CLR                      # Auslenkung der Federzunge beim Vorbeigleiten
    I = b * t ** 3 / 12
    Fn = 3 * E_PLA * I * delta / L ** 3          # Normalkraft der Zunge
    a = math.radians(45)
    Fax = Fn * (math.tan(a) + MU) / (1 - MU * math.tan(a))   # axiale Kraft über die 45°-Flanke
    eps = 3 * t * delta / (2 * L ** 2)
    pins_pull = (NPIN * PIN_PULL[0], NPIN * PIN_PULL[1])
    pins_push = (NPIN * PIN_PUSH[0], NPIN * PIN_PUSH[1])
    return dict(tongue_n=round(Fn, 2), tongue_ax=round(Fax, 2), tongue_eps=round(eps * 100, 2),
                tongue_delta=round(delta, 2), pins_pull=pins_pull, pins_push=pins_push,
                hold=(round(pins_pull[0] + Fax, 1), round(pins_pull[1] + Fax, 1)),
                insert=(round(pins_push[0] + Fax, 1), round(pins_push[1] + Fax, 1)))


# --------------------------------------------------------------------------
# Gebäudetabelle
# --------------------------------------------------------------------------
def building_table():
    d = dims()
    need_xy = (d["sock_w"] + 2 * 2.0, d["LY1"] - (d["HY"] - d["sock_d"] / 2) + 2 * 2.0)
    rows = []
    for name, bw, bt, bh in BUILDINGS:
        row = dict(name=name)
        for sc, f in (("1500", 1.0), ("1000", 1.5)):
            W, T, H = bw * f, bt * f, bh * f
            air = H - ROOF - d["z_cav"]                     # Luft über der Pausenebene unter dem Dach
            fits_xy = min(W, T) >= need_xy[0] and max(W, T) >= need_xy[1]
            if not fits_xy:
                st = "nein"
            elif air >= 6.0:
                st = "passt"
            elif air >= 2.0:
                st = "knapp"
            else:
                st = "nein"
            F_need = d["F"] + max(0.0, 2.0 - air)            # Fuß, mit dem es knapp passt (Luft 2 mm)
            row[sc] = dict(W=round(W, 1), T=round(T, 1), H=round(H, 1), air=round(air, 1), status=st,
                           F_need=round(layer_up(F_need), 1), xy=fits_xy)
        rows.append(row)
    return rows, need_xy


# --------------------------------------------------------------------------
# Ausgabe
# --------------------------------------------------------------------------
def half(man, y):
    return man - box(-500, 500, y, 500, -500, 500)


def to_bed(man):
    b = man.bounding_box()
    return man.translate([0, 0, -b[2]])


def print_parts(parts):
    """Druckausrichtung: Platte und Würfel wie gesteckt (Unterseite auf dem Bett), Deckel mit Stempeln
    nach oben, Kassette aufrecht, Schieber flach."""
    return dict(
        platte_ABC=to_bed(parts["plate"]), deckel=to_bed(parts["lid"]),
        wuerfel_pause=to_bed(parts["cube"]), wuerfel_kassette=to_bed(parts["cube_k"]),
        kassette=to_bed(parts["kass"]), schieber=to_bed(parts["key"]),
        pausenprobe=to_bed(unit_block(True)), montagelehre=to_bed(unit_block(False)),
        passprobe=to_bed(passprobe()))


def build_parts():
    d = dims()
    p, xs = plate(True)
    pnb, _ = plate(False)
    kass, _ = kassette()
    return dict(
        xs=xs, plate=p, plate_nobump=pnb, lid=lid(), header={v: header_part(v) for v in VARIANTS},
        cube=cube_pause(), housing=union([housing_part(d["z_face"]), terminals_part(d["z_face"])]),
        housing_only=housing_part(d["z_face"]), terms=terminals_part(d["z_face"]),
        wires=wires_part(), led=led_part(), cube_k=cube_kassette(), kass=kass, key=schieber(),
        wires_k=kass_wires_part())


def xcut(man, xc):
    """Querschnitt: alles mit x > xc weg (Blick von +x)."""
    return man - box(xc, 500, -500, 500, -500, 500)


def ycut(man, yc):
    """Längsschnitt durch die Pin-Reihe: alles mit y < yc weg (Blick von −y)."""
    return man - box(-500, 500, -500, yc, -500, 500)


def previews(parts):
    import preview
    from PIL import Image, ImageDraw
    os.makedirs(PREV, exist_ok=True)
    d = dims()
    HY = d["HY"]
    xc_l = pin_x()[1]
    col = dict(plate="#8fa3b8", lid="#6f8196", cube="#ece5d2", header="#2d3236", housing="#3a3f44",
               term="#c9a227", led="#ffe9a0", wire="#c8423b", kass="#e3862a", key="#4f9c6b", probe="#b9bfc4")
    xs = parts["xs"]
    R = lambda items, size, azim, elev: preview.render(items, size=size, azim=azim, elev=elev, light_from_view=True)

    def crop(m, cx, w=24.0):
        return m ^ box(cx - w, cx + w, -60, 60, -100, 100)

    def scene(dock="A", g=0.0, cut="x", kass=False, ex=0.0):
        cx = xs[VARIANTS.index(dock)]
        if cut == "x":
            f = lambda m: xcut(m, cx + xc_l)
        elif cut == "y":
            f = lambda m: ycut(m, HY)
        else:
            f = lambda m: m
        sh = lambda m, dz=0.0: m.translate([cx, 0, g + dz])
        out = [(to_tm(f(crop(parts["plate"], cx))), col["plate"]),
               (to_tm(f(crop(parts["lid"], cx).translate([0, 0, -10 * ex]))), col["lid"]),
               (to_tm(f(parts["header"][dock].translate([cx, 0, -5 * ex]))), col["header"])]
        if kass:
            out += [(to_tm(f(sh(parts["cube_k"], 30 * ex))), col["cube"]),
                    (to_tm(f(sh(parts["kass"], 8 * ex))), col["kass"]),
                    (to_tm(f(sh(parts["key"], 2 * ex))), col["key"]),
                    (to_tm(f(sh(parts["housing_only"], 5 * ex))), col["housing"]),
                    (to_tm(f(sh(parts["terms"], 5 * ex))), col["term"]),
                    (to_tm(f(sh(parts["wires_k"], 5 * ex))), col["wire"]),
                    (to_tm(f(sh(parts["led"], 12 * ex))), col["led"])]
        else:
            out += [(to_tm(f(sh(parts["cube"], 30 * ex))), col["cube"]),
                    (to_tm(f(sh(parts["housing_only"], 5 * ex))), col["housing"]),
                    (to_tm(f(sh(parts["terms"], 5 * ex))), col["term"]),
                    (to_tm(f(sh(parts["wires"], 5 * ex))), col["wire"]),
                    (to_tm(f(sh(parts["led"], 12 * ex))), col["led"])]
        return [(m, c) for m, c in out if len(m.faces)]

    def save(im, name, title, sub):
        preview.caption(im, title, sub).save(os.path.join(PREV, name))

    save(R(scene("A"), (1300, 900), 28, 14), "schnitt_gesteckt.png",
         "Gesteckt, Querschnitt durch Pin 2 (Dock A Winkelleiste, Gebäude mit Druckpause)",
         "Fuß %.1f mm in der Mulde · Stift %.1f mm in der Buchse · Riegel hält Buchse und Adern · LED liegt am Kammerboden"
         % (d["F"], d["E"]))
    save(R(scene("A", cut="y"), (1300, 900), -62, 14), "schnitt_pinreihe.png",
         "Gesteckt, Längsschnitt durch die Pin-Reihe (Dock A)",
         "Trichterplatte unter der Buchse, Stiftlöcher im Muldenboden, Lötenden der Winkelleiste im Kabelraum")
    save(R(scene("A", g=d["E"]), (1300, 900), 28, 14), "schnitt_kontakt.png",
         "Stiftspitzen erreichen die Buchse (Hub %.1f mm über dem Sitz)" % d["E"],
         "Der Fuß steckt da schon %.1f mm in der Mulde, die Trichter haben die Stifte gefangen" % (d["F"] - d["E"]))
    cx0 = xs[0]
    ex = [(to_tm(xcut(crop(parts["plate"], cx0), cx0 + xc_l)), col["plate"]),
          (to_tm(crop(parts["lid"], cx0).translate([0, 0, -12])), col["lid"]),
          (to_tm(parts["header"]["A"].translate([cx0, 0, 0])), col["header"]),
          (to_tm(parts["housing_only"].translate([cx0, 0, 22])), col["housing"]),
          (to_tm(parts["wires"].translate([cx0, 0, 22])), col["wire"]),
          (to_tm(parts["led"].translate([cx0, 0, 30])), col["led"]),
          (to_tm(xcut(parts["cube"], xc_l).translate([cx0, 0, 52])), col["cube"])]
    save(R(ex, (1200, 1150), 35, 18), "explosion.png",
         "Explosion: Deckel, Platte mit Winkelleiste, Buchse mit Adern, LED, Gebäude (Schnitte)",
         "Buchse, Adern und LED sind eine vorgefertigte Einheit, die beim Druck eingelegt wird")
    save(R(scene("C", kass=True), (1300, 900), 28, 14), "kassette_schnitt.png",
         "Rückfallebene: Kassette von unten, Schieber als Trichterplatte (Dock C)",
         "Kassette orange, Schieber grün; Buchse, Adern und LED wie in der Hauptlösung")
    panels = []
    for v, cx in zip(VARIANTS, xs):
        items = [(to_tm(xcut(crop(parts["plate"], cx, 17.5), cx + xc_l)), col["plate"]),
                 (to_tm(xcut(crop(parts["lid"], cx, 17.5), cx + xc_l)), col["lid"]),
                 (to_tm(xcut(parts["header"][v].translate([cx, 0, 0]), cx + xc_l)), col["header"])]
        panels.append(R(items, (520, 560), 28, 12))
    W = Image.new("RGB", (1560, 600), (250, 250, 248))
    dr = ImageDraw.Draw(W)
    for i, (im, t) in enumerate(zip(panels, ("A  Winkelleiste, gelötet", "B  gerade Leiste, gelötet",
                                             "C  Male-Crimp-Gehäuse, lötfrei"))):
        W.paste(im, (520 * i, 0))
        dr.text((520 * i + 20, 562), t, fill=(30, 30, 30), font=preview.font(22, True))
    save(W, "docks_schnitt.png", "Die drei Docks im Querschnitt durch Pin 2",
         "Muldenboden hält gegen Zug, Stempel im Deckel gegen den Steckdruck; Kabelraum nach hinten offen")
    # Montageablauf
    zc = d["z_cav"]
    below = parts["cube"] ^ box(-50, 50, -50, 50, -50, zc)
    lift = 9.0
    unit = [(to_tm(parts["housing_only"].translate([0, 0, lift])), col["housing"]),
            (to_tm(parts["wires"].translate([0, 0, lift])), col["wire"]),
            (to_tm(parts["led"].translate([0, 0, lift])), col["led"])]
    im1 = R([(to_tm(below), col["cube"])] + unit, (700, 640), -62, 38)
    im2 = R([(to_tm(below), col["cube"]), (to_tm(parts["housing_only"]), col["housing"]),
             (to_tm(parts["wires"]), col["wire"]), (to_tm(parts["led"]), col["led"])], (700, 640), -62, 38)
    im3 = R([(to_tm(xcut(parts["cube"], xc_l)), col["cube"]), (to_tm(xcut(parts["housing_only"], xc_l)), col["housing"]),
             (to_tm(xcut(parts["terms"], xc_l)), col["term"]),
             (to_tm(xcut(parts["wires"], xc_l)), col["wire"]), (to_tm(xcut(parts["led"], xc_l)), col["led"])],
            (700, 640), 25, 12)
    W = Image.new("RGB", (2100, 640), (250, 250, 248))
    for i, im in enumerate((im1, im2, im3)):
        W.paste(im, (700 * i, 0))
    dr = ImageDraw.Draw(W)
    for i, t in enumerate(("1  Pause bei %.2f mm: Einheit einlegen" % d["pause_mm"],
                           "2  Eingelegt: alles unter der Pausenebene", "3  Weitergedruckt: Riegel und Dach (Schnitt)")):
        dr.text((700 * i + 20, 600), t, fill=(30, 30, 30), font=preview.font(22, True))
    save(W, "montage_pause.png", "Druckpause: Buchse, Adern und LED werden eingelegt und überdruckt",
         "Pause nach Schicht %d (%.2f mm über dem Bett), die erste Schicht danach ist der Riegel" % (
             d["pause_layer"], d["pause_mm"]))
    pp = print_parts(parts)
    layout = [("platte_ABC", (0, 0), col["plate"]), ("deckel", (0, 62), col["lid"]),
              ("wuerfel_pause", (-45, -62), col["cube"]), ("wuerfel_kassette", (-8, -62), col["cube"]),
              ("kassette", (24, -62), col["kass"]), ("schieber", (52, -62), col["key"]),
              ("pausenprobe", (78, -62), col["probe"]), ("montagelehre", (100, -62), col["probe"]),
              ("passprobe", (0, 112), col["probe"])]
    items = []
    for n, (x, y), c in layout:
        m = pp[n]
        b = m.bounding_box()
        items.append((to_tm(m.translate([x - (b[0] + b[3]) / 2, y - (b[1] + b[4]) / 2, 0])), c))
    save(R(items, (1400, 1100), -60, 40), "druckteile.png",
         "Druckteile in Druckausrichtung (keine Stützen)",
         "Platte, Deckel, Würfel Pause, Würfel Kassette, Kassette, Schieber, Pausenprobe, Montagelehre, Passprobe")
    print("Vorschau: %s (8 Bilder)" % os.path.relpath(PREV, HERE))


def build():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(DOC, exist_ok=True)
    d = dims()
    parts = build_parts()

    print("Maßkette (mm, gesteckt, Plattenoberseite z = 0):")
    for k in ("F", "g1", "E", "contact_lift", "guide", "z_hb", "z_tip", "z_face", "z_ht", "z_pt", "z_cav",
              "z_s", "z_floor", "z_riegel", "z_lt", "z_lb", "plate_t"):
        print("  %-14s %7.2f" % (k, d[k]))
    print("  Pausenebene: %.2f mm über dem Bett = Oberkante Schicht %d (bei %.1f mm Schichthöhe);"
          " Pause VOR Schicht %d (Oberkante %.2f mm)" % (d["pause_mm"], d["pause_layer"], LAYER,
                                                        d["pause_layer"] + 1, d["pause_mm"] + LAYER))

    files = print_parts(parts)
    for name, man in files.items():
        tm = to_tm(man)
        tm.export(os.path.join(OUT, name + ".stl"))
        print("  %-48s %6.1f × %6.1f × %6.1f mm  dicht=%s" % (
            os.path.relpath(os.path.join(OUT, name + ".stl"), HERE), *tm.extents, tm.is_watertight))

    print("\nKollisionsprüfung gesteckt (Überschneidungsvolumen):")
    bad = 0
    res = checks(parts)
    for name, v, ok, note in res:
        if not ok:
            bad += 1
        if (not ok) or note or name.startswith("Dock A, gesteckt"):
            print("  %-60s %7.2f mm³  %s" % (name, v, ("ok (%s)" % note if note else "ok") if ok else "KOLLISION"))
    print("\nBeim Stecken (Hub g über dem Sitz; bewegt gegen Platte / Steckerteil):")
    ins, lifts, bump = insertion_checks(parts)
    for v, mname, lab, g, vp, vh in ins:
        ok = vp <= 0.05 and vh <= 0.05
        if not ok:
            bad += 1
        if v == "A" or not ok:
            print("  Dock %s %-9s %-36s g=%5.2f  Platte %6.2f  Stecker %6.2f  %s" % (
                v, mname, lab, g, vp, vh, "ok" if ok else "KOLLISION"))
    print("  Federnase gegen Fuß (gewollt, Zunge weicht aus): " +
          ", ".join("%.1f" % b for b in bump) + " mm³")
    print("  -> %s" % ("keine Kollisionen" if not bad else "%d Kollisionen!" % bad))

    fo = forces()
    print("\nKräfte (Abschätzung): Federzunge %.2f N normal, %.2f N axial (Dehnung %.2f %%); Stifte halten %.1f–%.1f N,"
          " Gebäude hält %.1f–%.1f N, Stecken %.1f–%.1f N" % (fo["tongue_n"], fo["tongue_ax"], fo["tongue_eps"],
                                                           *fo["pins_pull"], *fo["hold"], *fo["insert"]))
    rows, need_xy = building_table()
    print("\nGebäude (Luft = Höhe − Dach − Pausenebene; passt ≥ 6, knapp ≥ 2 mm):")
    for r in rows:
        print("  %-18s 1:1500 %-6s (Luft %5.1f)   1:1000 %-6s (Luft %5.1f)" % (
            r["name"], r["1500"]["status"], r["1500"]["air"], r["1000"]["status"], r["1000"]["air"]))

    xc_l = pin_x()[1]

    def pair(man):
        return dict(full=encode(to_tm(man)), cut=encode(to_tm(xcut(man, xc_l))))

    xs = parts["xs"]
    rows_ins = [dict(dock=v, mode=m, label=l, g=round(g, 2), plate=round(vp, 2), header=round(vh, 2))
                for v, m, l, g, vp, vh in ins]
    data = dict(
        dims={k: round(float(v), 3) for k, v in d.items()},
        xs=xs, xcut=xc_l,
        params=dict(PITCH=PITCH, HSG_W=HSG_W, HSG_T=HSG_T, HSG_H=HSG_H, HSG_TOL=HSG_TOL, TERM_L=TERM_L,
                    TERM_BOX=TERM_BOX, TERM_BOX_L=TERM_BOX_L, CONTACT=CONTACT, PIN_SQ=PIN_SQ, HDR_BODY=HDR_BODY,
                    HDR_UP=HDR_UP, HDR_TAIL=HDR_TAIL, RA_BACK=RA_BACK, RA_TAIL=RA_TAIL, MPIN_UP=MPIN_UP,
                    WIRE_D=WIRE_D, LED_W=LED_W, LED_L=LED_L, LED_T=LED_T, LED_FPC=LED_FPC, CLR=CLR, RELIEF=RELIEF,
                    BAND=BAND, SNUG=SNUG, RIB=RIB, HOLE=HOLE, FUNNEL_D=FUNNEL_D, WALL=WALL, CH_F=CH_F, CH_P=CH_P,
                    GUIDE=GUIDE, CEIL=CEIL, FUNNEL_T=FUNNEL_T, LAYER=LAYER, WIRE_GAP=WIRE_GAP,
                    LED_GAP=LED_GAP, RIEGEL_T=RIEGEL_T, CUBE=CUBE, CUBE_H=CUBE_H, ROOF=ROOF, KEY=KEY,
                    LID_T=LID_T, TONGUE_L=TONGUE["L"], TONGUE_T=TONGUE["t"], BUMP=TONGUE["bump"],
                    z_detent=z_detent(), KEY_CLR=KEY_CLR, KASS_CLR=KASS_CLR,
                    PADS=list(PADS), pin_x=pin_x()),
        forces=forces(),
        plate_t_by_dock={v: round(-(layer_down({"A": d["z_bend"] - 3.0, "B": d["z_tailB"] - 3.5,
                                                 "C": d["z_mcb"] - 4.0}[v]) - LID_T), 1) for v in VARIANTS},
        buildings=rows, need_xy=[round(v, 1) for v in need_xy],
        lifts=[dict(label=l, g=round(g, 3)) for l, g in lifts], insertion=rows_ins,
        sizes={n: [round(float(v), 1) for v in to_tm(m).extents] for n, m in files.items()},
        parts=dict(
            plate=dict(full=encode(to_tm(parts["plate"])),
                       cut=[encode(to_tm(xcut(parts["plate"], cx + xc_l))) for cx in xs]),
            lid=dict(full=encode(to_tm(parts["lid"])),
                     cut=[encode(to_tm(xcut(parts["lid"], cx + xc_l))) for cx in xs]),
            header={v: pair(parts["header"][v]) for v in VARIANTS},
            cube=pair(parts["cube"]), cube_k=pair(parts["cube_k"]), kass=pair(parts["kass"]),
            key=pair(parts["key"]), housing=pair(parts["housing_only"]), terms=pair(parts["terms"]),
            wires=pair(parts["wires"]), wires_k=pair(parts["wires_k"]), led=pair(parts["led"])))
    with open(os.path.join(DOC, "daten.json"), "w") as f:
        json.dump(data, f, separators=(",", ":"))
    print("\n%s: %.0f kB" % (os.path.relpath(os.path.join(DOC, "daten.json"), HERE),
                            os.path.getsize(os.path.join(DOC, "daten.json")) / 1024))
    return parts


if __name__ == "__main__":
    previews(build())
