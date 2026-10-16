#!/usr/bin/env python3
"""Fahrplan der Testdrucke für die Kassette: baut plug/roadmap/page.html aus template.html.

Die Seite zeigt, welche Passungen der Kassette in welcher Reihenfolge zu prüfen sind, welche unabhängig voneinander
laufen, was erst im Verbund geht und wie die erste Stunde (anwesend) und die Nacht (unbeaufsichtigt) belegt werden.

Zahlen kommen aus dem Generator (`dims()` in plug/dupont.py und plug/institute.py, Konstanten aus plug/parts.py) und aus
der Tabelle PARTS unten. Die Mengen (g) der vorhandenen STL sind per Voxelmodell geschätzt (3 Wände, 15 % Füllung,
4 Deck-/Bodenschichten), die neuen Coupons aus einem Grobentwurf; die Zeiten folgen einem einfachen Modell (PROFILE).
Der Slicer hat Vorrang vor all diesen Schätzungen.

Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m plug.roadmap.build      # schreibt plug/roadmap/page.html
"""
import os

from plug import dupont as sd
from plug import institute as I

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))          # plug/
TEMPLATE = os.path.join(HERE, "roadmap", "template.html")
OUT = os.path.join(HERE, "roadmap", "page.html")


def de(x, n=1):
    return ("%.*f" % (n, x)).replace(".", ",")


# --------------------------------------------------------------------------
# Material und Zeit (Schätzung)
# --------------------------------------------------------------------------
# g = extrudiertes PLA in g, layers = Schichten (0,2 mm), new = STL existiert noch nicht.
# K, N, S, R, FM stammen aus plug/series.py (Werte aus dessen Ausgabe), die übrigen aus den Probestück-STL bzw. Entwurf.
PARTS = {
    "K":  dict(g=1.0,  layers=12,  new=False),   # 3 Distanzplättchen 1,2 / 1,8 / 2,4 mm (K_contact_spacers.stl)
    "C":  dict(g=3.6,  layers=76,  new=False),   # Kassette (C_cassette.stl = 2_kassette.stl)
    "R":  dict(g=4.0,  layers=71,  new=False),   # 4 Buchsenhülsen 0,08 / 0,12 / 0,16 / 0,20 (R_sleeves.stl)
    "N":  dict(g=4.0,  layers=5,   new=False),   # 4 Schieber 0,05 / 0,10 / 0,15 / 0,20 (N_sliders.stl)
    "S":  dict(g=11.9, layers=45,  new=False),   # 4 Boden-Platten 0,05 / 0,10 / 0,15 / 0,20 (S_floor_slabs.stl)
    "D":  dict(g=2.1,  layers=21,  new=False),   # 0_passprobe.stl (v6)
    "L":  dict(g=3.0,  layers=20,  new=True),    # Entwurf: 3 Wandstreifen 0,4 / 0,8 / 1,2 mm
    "FM": dict(g=19.7, layers=55,  new=False),   # 3 Mulden-Ringe 0,10 / 0,15 / 0,20 (FM_mulde_rings.stl)
    "V1": dict(g=7.2,  layers=110, new=False),   # 1_probestueck.stl (Gebäude), Kassette und Schieber kommen aus C und N
    "V2": dict(g=14.8, layers=111, new=False),   # 4_platte.stl + 5_deckel.stl
}
# Durchsatz in g/h, Overhead je Schicht in s, Start (Aufheizen, Einmessen) in min bei einem neuen Job / bei einem Folgejob
PROFILE = {
    "normal":  dict(rate=9.0,  layer=5.0, start=5.0, follow=2.0),
    "schnell": dict(rate=25.0, layer=2.0, start=3.0, follow=1.0),
}


def minutes(key, prof="normal"):
    p, pr = PARTS[key], PROFILE[prof]
    return p["g"] / pr["rate"] * 60.0 + p["layers"] * pr["layer"] / 60.0


def job(keys, prof="normal", first=True):
    pr = PROFILE[prof]
    return sum(minutes(k, prof) for k in keys) + (pr["start"] if first else pr["follow"])


def hm(m):
    m = int(round(m))
    return "%d:%02d" % (m // 60, m % 60)


CORE = ("K", "N", "S", "C")                 # erste Nachtplatte (Kern)
EXTRA = ("R", "D", "FM")                      # optional: R und D sind teilweise schon getestet, FM ist das schwerste Teil
T_START = 30.0                                # Slicen, Anordnen, Starten
T_CORE1 = T_START + job(CORE)
T_ALL1 = T_CORE1 + sum(minutes(k) for k in EXTRA)
G_CORE = sum(PARTS[k]["g"] for k in CORE)
G_ALL = G_CORE + sum(PARTS[k]["g"] for k in EXTRA)


def total(keys, prof="normal"):
    return sum(minutes(k, prof) for k in keys) + PROFILE[prof]["start"]


# --------------------------------------------------------------------------
# Abbildung A: Schnitt längs y durch die Pin-Reihe (Maße aus dem Generator)
# --------------------------------------------------------------------------
def section_svg():
    d = I.dims()
    yc = (d["cass_y0"] + d["cass_y1"]) / 2          # Kassette liegt im Probestück mittig
    wy = lambda y: y - yc                           # lokal -> Welt (Probestück)
    F, HY = d["F"], wy(d["HY"])
    ypin = HY
    S = 12.0                                        # px je mm
    YMIN, YMAX, ZTOP, ZBOT = -24.55, 24.55, 12.0, d["z_lb"]
    X0, Y0 = 34.0, 26.0
    W = (YMAX - YMIN) * S + 2 * X0
    H = (ZTOP - ZBOT) * S + Y0 + 22.0
    Y = lambda y: X0 + (y - YMIN) * S
    Z = lambda z: Y0 + (ZTOP - z) * S
    out = []

    def rect(y0, y1, z0, z1, cls, extra=""):
        out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" class="%s"%s/>' % (
            Y(y0), Z(z1), (y1 - y0) * S, (z1 - z0) * S, cls, extra))

    def poly(pts, cls):
        out.append('<polygon points="%s" class="%s"/>' % (" ".join("%.1f,%.1f" % (Y(y), Z(z)) for y, z in pts), cls))

    def line(pts, cls, w=None):
        out.append('<polyline points="%s" class="%s"%s fill="none"/>' % (
            " ".join("%.1f,%.1f" % (Y(y), Z(z)) for y, z in pts), cls, (' stroke-width="%.1f"' % w) if w else ""))

    def text(y, z, s, cls="lab", anchor="middle", dx=0.0, dy=0.0):
        out.append('<text x="%.1f" y="%.1f" class="%s" text-anchor="%s">%s</text>' % (Y(y) + dx, Z(z) + dy, cls, anchor, s))

    def badge(y, z, letter, ty, tz):
        """Marke mit kurzer Leitlinie zum Ziel (ty, tz)."""
        out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="lead"/>' % (Y(y), Z(z), Y(ty), Z(tz)))
        out.append('<circle cx="%.1f" cy="%.1f" r="2.6" class="dot"/>' % (Y(ty), Z(tz)))
        out.append('<circle cx="%.1f" cy="%.1f" r="10.5" class="tagc"/>' % (Y(y), Z(z)))
        out.append('<text x="%.1f" y="%.1f" class="tagt%s" text-anchor="middle">%s</text>' % (
            Y(y), Z(z) + 4.2, " sm" if len(letter) > 1 else "", letter))

    # Platte, Deckel und ihre Hohlräume
    rect(YMIN, YMAX, d["z_lt"], 0.0, "p-plate")
    rect(YMIN, YMAX, ZBOT, d["z_lt"], "p-lid")
    rect(-18.25, 18.25, -F, 0.0, "hole")                                         # Mulde
    yb = wy(d["y_b"])
    hd = sd.HDR_T / 2 + sd.SNUG_HDR
    zs = sd.step_z(d["z_hb"])
    rect(yb - hd, ypin + sd.PIN_SQ / 2 + 0.8, d["z_bb"], d["z_hb"], "hole")      # Körpertasche + Schacht
    rect(yb - hd - sd.RA_TAIL - 0.9, yb, d["z_bb"], zs, "hole")                  # Lötendenschlitz
    rect(wy(d["HY"] - 8.5), wy(d["HY"] + 9.0), d["z_lt"], d["z_bb"], "hole")    # Kabelraum
    rect(ypin - sd.HOLE / 2, ypin + sd.HOLE / 2, d["z_hb"], -F, "hole")          # Pinloch im Muldenboden
    # Gebäude mit Fuß
    rect(-18.0, 18.0, -F, 12.0, "p-bld")
    rect(-16.8, 16.8, d["z_kt"] + 1.2, 12.0 - 1.2, "hole")                       # Kammer
    rect(wy(d["seat_y0"] - 0.15), wy(d["seat_y1"] + 0.15), d["z_kt"], d["z_kt"] + 1.2, "hole")   # Bodenöffnung (LED)
    c = sd.KASS_CLR
    rect(wy(d["cass_y0"]) - c, wy(d["cass_y1"]) + c, -F, d["z_kt"], "hole")      # Schacht
    rect(ypin - d["sock_d"] / 2 - c, ypin + d["sock_d"] / 2 + c, d["z_kt"], d["z_kceil"] + 0.3, "hole")   # Sockeldurchbruch
    hb = d["hb"]
    poly([(-hb, -F), (hb, -F), (hb + sd.FUNNEL_T, -F + sd.FUNNEL_T), (-hb - sd.FUNNEL_T, -F + sd.FUNNEL_T)], "hole")   # Nut
    # Lichtfenster: von innen ausgespart, außen bleibt die Restwand WIN_T (0,4 mm)
    for sgn in (-1, 1):
        a, b = sorted((sgn * 16.8, sgn * (18.0 - I.WIN_T)))
        rect(a, b, 6.6, 10.6, "hole")
    # Kassette
    rect(wy(d["cass_y0"]), wy(d["cass_y1"]), -F + sd.FUNNEL_T, d["z_kt"], "p-kass")
    rect(ypin - d["sock_d"] / 2, ypin + d["sock_d"] / 2, d["z_kt"], d["z_kceil"], "p-kass")
    rect(ypin - d["pk_d"] / 2, ypin + d["pk_d"] / 2, -F + sd.FUNNEL_T, d["z_pt"], "hole")       # Buchsentasche
    rect(wy(d["seat_y0"]), wy(d["seat_y1"]), d["z_s"], d["z_kt"], "hole")                       # Ablage
    # Schieber mit Trichter
    kc = sd.KEY_CLR
    poly([(-hb + kc, -F), (hb - kc, -F), (hb - kc + sd.FUNNEL_T, -F + sd.FUNNEL_T), (-hb + kc - sd.FUNNEL_T, -F + sd.FUNNEL_T)], "p-key")
    h = (sd.FUNNEL_D - sd.HOLE) / 2
    poly([(ypin - sd.FUNNEL_D / 2, -F), (ypin + sd.FUNNEL_D / 2, -F), (ypin + sd.HOLE / 2, -F + h), (ypin + sd.HOLE / 2, -F + sd.FUNNEL_T),
          (ypin - sd.HOLE / 2, -F + sd.FUNNEL_T), (ypin - sd.HOLE / 2, -F + h)], "hole")
    # Buchse mit Kontaktkasten
    rect(ypin - sd.HSG_T / 2, ypin + sd.HSG_T / 2, d["z_face"], d["z_ht"], "p-hsg")
    rect(ypin - sd.TERM_BOX / 2, ypin + sd.TERM_BOX / 2, d["z_face"] + sd.TERM_OFF, d["z_face"] + sd.TERM_OFF + sd.TERM_BOX_L, "p-term")
    # LED (60/m) mit Chip, Adern
    y0 = wy(d["LY0"])
    rect(y0, y0 + 16.7, d["z_s"], d["z_s"] + sd.LED_FPC, "p-led")
    rect(y0 + 8.35 - 2.5, y0 + 8.35 + 2.5, d["z_s"] + sd.LED_FPC, d["z_s"] + sd.LED_T, "p-led")
    zw = d["z_kceil"] - 0.6 + sd.WIRE_D / 2
    line([(ypin, d["z_ht"] - 0.6), (ypin, zw), (ypin + d["sock_d"] / 2 + 0.4, zw), (y0 + 1.2, d["z_s"] + sd.LED_FPC + 0.5)], "p-wire", w=sd.WIRE_D * S * 0.75)
    # Stiftleiste Dock A: Körper, Lötende, senkrechter Pin
    rect(yb - sd.HDR_T / 2, yb + sd.HDR_T / 2, d["z_bb"], d["z_hb"], "p-pin")
    zm = d["z_bm"]
    rect(yb - sd.HDR_T / 2 - sd.RA_TAIL, ypin + sd.PIN_SQ / 2, zm - sd.PIN_SQ / 2, zm + sd.PIN_SQ / 2, "p-pin")
    rect(ypin - sd.PIN_SQ / 2, ypin + sd.PIN_SQ / 2, zm - sd.PIN_SQ / 2, d["z_tip"], "p-pin")
    # Beschriftung
    text(-21.4, -3.0, "Platte", "lab")
    text(0.0, (d["z_lt"] + ZBOT) / 2, "Deckel", "lab", dy=4)
    text(-11.7, -14.4, "Kabelraum", "lab sm", dy=4)
    text(2.5, -5.2, "Kassette", "lab", dy=4)
    text(8.0, -F + sd.FUNNEL_T / 2, "Schieber", "lab sm", dy=3.5)
    text(ypin, 8.0, "Buchse", "lab sm", dy=0)
    text(y0 + 8.35, 8.2, "LED", "lab sm", dy=0)
    text(0.0, 10.0, "Kammer im Gebäude", "lab sm", dy=0)
    text(-21.4, 4.0, "Gebäude", "lab", dy=0)
    text(-21.4, 2.6, "mit Fuß", "lab sm", dy=0)

    # Marken (Test-IDs)
    badge(ypin + 5.2, 1.6, "C", ypin + d["pk_d"] / 2 + 0.1, 1.6)                       # Buchse in der Tasche
    badge(1.2, 1.2, "C", 1.2, d["z_s"])                                                # LED-Ablage
    badge(ypin + 5.2, -6.8, "K", ypin + 0.35, -6.8)                                    # Stift in der Buchse
    badge(10.0, -3.8, "S", wy(d["cass_y1"]) + c / 2, -3.8)                              # Lücke Kassette/Schacht
    badge(21.5, -9.3, "N", hb - kc + sd.FUNNEL_T * 0.5, -F + sd.FUNNEL_T * 0.5)        # Schwalbenschwanz
    badge(21.5, -4.6, "FM", 18.12, -4.6)                                                # Fuß in der Mulde
    badge(-21.4, -9.3, "D", yb - hd, (d["z_bb"] + d["z_hb"]) / 2)                      # Körpertasche der Leiste
    badge(-21.4, 8.6, "L", -17.8, 8.6)                                            # Lichtfenster
    return ('<svg viewBox="0 0 %.0f %.0f" role="group" aria-label="Schnitt durch das Probestück mit den Fugen" class="sec">%s</svg>'
            % (W, H, "".join(out)))


# --------------------------------------------------------------------------
# Abbildung B: Abhängigkeiten
# --------------------------------------------------------------------------
NODES = [
    # id, domain, x, y, w, h, Titel, Zeilen
    ("K",  "gate",  170, 130, 140, 64, "Kontakt-Tiefe", ["Gate, nur Höhen"]),
    ("C",  "kass",  370,  40, 180, 64, "Kassette bestücken", ["Buchse · Adern · LED"]),
    ("N",  "key",   370, 130, 180, 64, "Schieber ↔ Nut", ["KEY_CLR 0,05–0,20"]),
    ("D",  "plate", 370, 250, 180, 64, "Podest + Deckel", ["Dock A, Stufe"]),
    ("FM", "bld",   370, 340, 180, 64, "Fuß ↔ Mulde", ["Ringe CLR 0,10–0,20"]),
    ("L",  "led",   370, 430, 180, 64, "Licht durch Wand", ["0,4 · 0,8 · 1,2 mm"]),
    ("S",  "kass",  620,  40, 170, 64, "Kassette ↔ Schacht", ["KASS_CLR 0,05–0,20"]),
    ("V1", "join",  850,  60, 140, 84, "Gebäude trocken", ["Kassette + Schieber", "im Gebäude, ohne Pins"]),
    ("V2", "join",  850, 280, 140, 84, "Stecken mit Pins", ["Platte, Deckel,", "Winkelleiste"]),
]
# (von, nach, Art, Pfad); Art: hard = Ergebnis ändert die Geometrie des Nachfolgers, soft = nur Höhen bzw. schwach
EDGES = [
    ("M",  "K",  "hard", "M130,162 H168"),
    ("M",  "C",  "hard", "M130,72 H368"),
    ("M",  "FM", "hard", "M130,372 H368"),
    ("K",  "N",  "soft", "M310,162 H368"),
    ("C",  "S",  "hard", "M550,72 H618"),
    ("S",  "V1", "hard", "M790,72 H820 V80 H848"),
    ("N",  "V1", "hard", "M550,162 H830 V124 H848"),
    ("V1", "V2", "hard", "M920,144 V278"),
    ("D",  "V2", "hard", "M550,282 H700 V300 H848"),
    ("FM", "V2", "hard", "M550,372 H730 V322 H848"),
    ("L",  "V2", "soft", "M550,462 H760 V344 H848"),
]


def meta_line(key):
    p = PARTS[key]
    return "%s g · %d min" % (de(p["g"]), round(minutes(key)))


def graph_svg():
    o = []
    o.append('<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
             '<path d="M0,1 L9,5 L0,9 z" class="ahp"/></marker></defs>')
    for x, t in ((20, "0 · Messen"), (170, "1 · Gate"), (370, "2 · einzeln, parallel"), (620, "3 · braucht C"), (850, "4 · Verbund")):
        o.append('<text x="%d" y="22" class="colh">%s</text>' % (x, t))
    for a, b, kind, path in EDGES:
        o.append('<path d="%s" class="edge %s" data-from="%s" data-to="%s" marker-end="url(#ah)"/>' % (path, kind, a, b))
    # Messen als hohe Leiste
    o.append('<g class="node meas" data-id="M"><a href="#t-M"><rect x="20" y="40" width="110" height="454" rx="6"/>'
             '<circle cx="38" cy="60" r="11" class="bd"/><text x="38" y="64.2" class="bdt" text-anchor="middle">M</text>'
             '<text x="54" y="64" class="nt">Messen</text>'
             '<text x="34" y="92" class="ns mono">0 g · ≈ 20 min</text>'
             + "".join('<text x="34" y="%d" class="ns">%s</text>' % (126 + 22 * i, s) for i, s in enumerate(
                 ("Buchsengehäuse", "Winkelleiste", "LED-Streifen", "Ader + Crimp", "alte Probeteile")))
             + '<text x="34" y="262" class="ns dim2">speist K, C, FM</text></a></g>')
    for nid, dom, x, y, w, h, title, lines in NODES:
        new = nid in ("L",)
        cls = "node %s%s" % (dom, " neu" if new else "")
        o.append('<g class="%s" data-id="%s"><a href="#t-%s">' % (cls, nid, nid))
        o.append('<rect x="%d" y="%d" width="%d" height="%d" rx="6"/>' % (x, y, w, h))
        o.append('<circle cx="%d" cy="%d" r="11" class="bd"/><text x="%d" y="%.1f" class="bdt%s" text-anchor="middle">%s</text>' % (
            x + 18, y + 21, x + 18, y + 21 + 4.2, " sm" if len(nid) > 1 else "", nid))
        o.append('<text x="%d" y="%d" class="nt">%s</text>' % (x + 36, y + 25, title))
        yy = y + 42
        for ln in lines:
            o.append('<text x="%d" y="%d" class="ns">%s</text>' % (x + 12, yy, ln))
            yy += 15
        if nid in PARTS:
            mt = meta_line(nid)
            if nid in ("V1", "V2"):
                mt = "%s g · %d min" % (de(PARTS[nid]["g"]), round(minutes(nid)))
            o.append('<text x="%d" y="%d" class="ns mono">%s</text>' % (x + 12, y + h - 9, mt))
        o.append('</a></g>')
    # Legende
    ly = 524
    o.append('<path d="M20,%d H58" class="edge hard" marker-end="url(#ah)"/><text x="66" y="%d" class="ns">Ergebnis ändert die Geometrie des Nachfolgers</text>' % (ly - 4, ly))
    o.append('<path d="M370,%d H408" class="edge soft" marker-end="url(#ah)"/><text x="416" y="%d" class="ns">ändert nur Höhen, schwach</text>' % (ly - 4, ly))
    o.append('<rect x="640" y="%d" width="26" height="12" rx="3" class="legneu"/><text x="674" y="%d" class="ns">gestrichelt: STL gibt es noch nicht</text>' % (ly - 12, ly))
    return '<svg viewBox="0 0 1000 540" role="group" aria-label="Abhängigkeiten der Tests" class="graph">%s</svg>' % "".join(o)


# --------------------------------------------------------------------------
# Abbildung C: Zeitplan
# --------------------------------------------------------------------------
def time_svg():
    X0, W = 130.0, 840.0                       # 0:00 bis 9:00 linear
    t = lambda m: X0 + m / 540.0 * W
    PY0, PH, DY0 = 64, 40, 134
    o = []
    o.append('<defs><pattern id="hat" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
             '<line x1="0" y1="0" x2="0" y2="6" class="hatl"/></pattern></defs>')
    o.append('<text x="%.0f" y="11" class="colh">Stunden ab jetzt</text>' % X0)
    for h_ in range(0, 10):
        o.append('<line x1="%.1f" y1="30" x2="%.1f" y2="176" class="grid"/><text x="%.1f" y="27" class="tick" text-anchor="middle">%d:00</text>' % (t(h_ * 60), t(h_ * 60), t(h_ * 60), h_))
    o.append('<text x="8" y="89" class="lane">Drucker</text><text x="8" y="159" class="lane">Du</text>')

    def blk(xa, xb, y0, cls, label, small=False):
        o.append('<rect x="%.1f" y="%d" width="%.1f" height="%d" rx="4" class="%s"/>' % (xa, y0, xb - xa, PH, cls))
        if label and xb - xa > 18:
            o.append('<text x="%.1f" y="%d" class="bl%s" text-anchor="middle">%s</text>' % ((xa + xb) / 2, y0 + 24, " sm" if small else "", label))

    blk(t(T_START), t(T_CORE1), PY0, "b-print night", "Kern: K · N · S · C")
    o.append('<rect x="%.1f" y="%d" width="%.1f" height="%d" rx="4" class="b-opt"/>' % (t(T_CORE1), PY0, t(T_ALL1) - t(T_CORE1), PH))
    o.append('<rect x="%.1f" y="%d" width="%.1f" height="%d" rx="4" class="b-hat"/>' % (t(T_CORE1), PY0, t(T_ALL1) - t(T_CORE1), PH))
    o.append('<text x="%.1f" y="%d" class="bl sm" text-anchor="start">optional: R · D · FM</text>' % (t(T_ALL1) + 8, PY0 + 24))
    o.append('<text x="%.1f" y="%d" class="note" text-anchor="start">Kern ≈ %s g, fertig gegen %s</text>' % (t(T_START), PY0 + PH + 15, de(G_CORE, 0), hm(T_CORE1)))
    o.append('<text x="%.1f" y="%d" class="note" text-anchor="end">mit FM ≈ %s g, fertig gegen %s</text>' % (t(540), PY0 + PH + 15, de(G_ALL, 0), hm(T_ALL1)))
    blk(t(0), t(T_START + 30), DY0, "b-you", "Start", True)
    blk(t(T_START + 30), t(540), DY0, "b-off", "offline")
    o.append('<text x="%.1f" y="196" class="note" text-anchor="start">Start: Slicen, Vorschau ansehen (Brücken, Gravuren), starten, erste Schichten beobachten. Zeitwerte für einen normalen Drucker (Schätzung).</text>' % X0)
    o.append('<text x="%.1f" y="214" class="note" text-anchor="start">Morgen: K zuerst (Durchgang), dann N, S, R, FM nach Gefühl, je Serie ENG und WEIT notieren. Danach V1, dann V2.</text>' % X0)
    return '<svg viewBox="0 0 1000 226" role="group" aria-label="Zeitplan der ersten Nacht" class="time">%s</svg>' % "".join(o)


# --------------------------------------------------------------------------
# Karten
# --------------------------------------------------------------------------
def build_cards():
    d = I.dims()
    E, F = d["E"], d["F"]
    cards = [
        dict(id="M", dom="meas", title="Messen", stage="Stufe 0", when="vor dem Druck",
             q="Was lässt sich messen? Spalte unter 0,5 mm nicht, Bauteile schon. Darum gibt es Serien mit eingravierter Spielzahl; die Hand ist das Messgerät.",
             rows=[
                 ("Kaufteile",
                  "<b>5 Buchsengehäuse</b>: Breite × Dicke × Höhe (Soll 10,16 × 2,54 × 14,00, laut Zeichnung ±0,3 und +0,25). "
                  "<b>Winkelleiste</b>: den kürzesten senkrechten Pin von 5 Stück (Soll 7,0 ±0,5; daraus E = %s bis %s mm). "
                  "<b>LED-Streifen</b>: Breite, Dicke mit Chip, Pad-Reihenfolge ab DIN-Seite (der Code nimmt GND, DIN, 5V an, im Generator steht „am Streifen prüfen“). "
                  "<b>Ader mit Crimp</b>: Isolationsdurchmesser (Code 1,0)." % (de(E - 0.5, 2), de(E + 0.5, 2))),
                 ("Fugen",
                  "Nicht messen, sondern fühlen: je Serie die engste Variante, die ohne Gewalt passt (ENG), und die weiteste, die noch nicht merklich wackelt (WEIT). "
                  "Die Gehäusebreite der benutzten Buchse dazu notieren, sie streut um ±0,3."),
                 ("Erfolg", "Messblatt für die Kaufteile, ENG und WEIT je Serie."),
             ],
             meta=["0 g", "≈ 20 min", "kein STL"], waits="–",
             known="Laut STATUS ist das Probestück komplett gedruckt und „passt, wackelt überall“; Einzelwerte liegen nicht vor und lassen sich am fertigen Teil auch nicht messen."),
        dict(id="K", dom="gate", title="Kontakt-Tiefe", stage="Stufe 1 · Gate", when="Nacht 1",
             q="Hält der Dupont-Kontakt bei nur %s mm Einstecktiefe? Der Kontaktpunkt ist mit ≈ 1,5 mm geschätzt, der Pin hat ±0,5." % de(E, 2),
             rows=[
                 ("Teile", "<code>K_contact_spacers.stl</code>: drei Plättchen <b>t = 1,2 / 1,8 / 2,4 mm</b> mit vier Löchern im 2,54-Raster, bettseitig mit Senkung."),
                 ("Aufbau",
                  "Winkelleiste → Plättchen t → Buchse. E = %s − t, also %s / %s / %s mm. "
                  "t = 1,8 ist Muldenboden %s + Schieber %s im Gebäude. Mit dem kürzesten Pin aus M." % (de(sd.HDR_UP, 2), de(sd.HDR_UP - 1.2, 2), de(sd.HDR_UP - 1.8, 2),
                                                                                           de(sd.HDR_UP - 2.4, 2), de(sd.CEIL), de(sd.FUNNEL_T))),
                 ("Messen", "Durchgang jedes Kontakts beim Wackeln (±0,5 mm seitlich, leicht kippen), Auszugskraft mit Federwaage."),
                 ("Erfolg / sonst",
                  "<b>Hält bei 2,4:</b> Reserve für kurze Pins, nichts ändern. <b>Hält ab 1,8:</b> so lassen, kürzesten Pin prüfen. "
                  "<b>Hält nur bei 1,2:</b> <code>CEIL</code> und <code>FUNNEL_T</code> auf 0,6, F = 10,0, alle Höhen neu (N, V1, V2). "
                  "<b>Hält nirgends:</b> Dupont-Kontakt ungeeignet, JST-Archiv."),
             ],
             meta=["%s g" % de(PARTS["K"]["g"]), "≈ %d min" % round(minutes("K")), "STL vorhanden"], waits="M (Pinlänge)",
             known="Offen. Laut STATUS ist der Kontaktpunkt geschätzt und der Test steht aus. Ändert nur Höhen (Fußhöhe F = %s, Schieberdicke), nie seitliche Passungen." % de(F)),
        dict(id="C", dom="kass", title="Kassette bestücken", stage="Stufe 2", when="Nacht 1",
             q="Passen die echten Kaufteile in die Kassette, ohne dass etwas klemmt oder wackelt? Ganz ohne Gebäude. Die gedruckte Kassette ist zugleich die Lehre für S.",
             rows=[
                 ("Teile", "<code>C_cassette.stl</code> (wie im Probestück, %s cm³, steht aufrecht, Buchsentasche unten offen). "
                           "Optional dazu <code>R_sleeves.stl</code>: vier Buchsenhülsen 0,08 / 0,12 / 0,16 / 0,20 ohne Rippen. Passprobe Runde 2 hat 0,25 bis 0,33 schon geprüft (0,25 „sitzt sehr gut“), die Hülsen decken nur den Bereich darunter ab." % de(5.8)),
                 ("Ablauf", "Wie später im Bau: Buchse mit der Steckseite zur offenen Unterseite eindrücken, Adern in den Aderschlitz und über die +y-Wand zur LED, "
                            "Streifen in die Ablage %s × %s, DETECT-Brücke in die Querrinne." % (de(I.SEAT_W), de(I.SEAT_L))),
                 ("Fühlen", "Buchse in jede Hülse: ENG und WEIT notieren, mit zwei bis drei Buchsen (Gehäusebreite ±0,3). In der Kassette: Einpresskraft von Hand? "
                            "Wackelt die Buchse (Spiel %s je Seite, Rippen %s)? Rastfenster-Seite (−y) frei? Beide Streifenbreiten (10 und 12 mm) passen? Adern ohne Quetschstelle?"
                  % (de(sd.SNUG, 2), de(sd.RIB, 2))),
                 ("Erfolg / sonst", "Buchse sitzt ohne Werkzeug und ohne spürbares Spiel. Ergebnis der Hülsen wird <code>SNUG</code>; Rippen (<code>RIB</code>) danach getrennt."),
             ],
             meta=["%s g" % de(PARTS["C"]["g"] + PARTS["R"]["g"]), "≈ %d min" % round(minutes("C") + minutes("R")), "STL vorhanden"], waits="M (Buchse, Streifen)",
             known="Buchse in einer Tasche mit 0,25 Spiel „sitzt sehr gut“ (Passprobe Runde 2, ohne Rippen). Rippen, Aderweg und Ablage sind im Probestück mitgedruckt, ohne Einzelwerte."),
        dict(id="N", dom="key", title="Schieber ↔ Nut", stage="Stufe 2", when="Nacht 1",
             q="Gleitet der %s mm dicke Schieber leicht, hält er die Kassette, und bleibt er flach?" % de(sd.FUNNEL_T),
             rows=[
                 ("Teile", "<code>N_sliders.stl</code>: vier Schieber in echter Breite (%s mm) mit <code>KEY_CLR</code> 0,05 / 0,10 / 0,15 / 0,20, Trichterlöchern und Griffkerbe wie im Probestück. "
                           "Die Nut ist in den Boden-Platten aus S (<code>S_floor_slabs.stl</code>), bei allen gleich." % de(2 * (d["hb"] - sd.KEY_CLR + sd.FUNNEL_T))),
                 ("Fühlen", "Welcher Schieber gleitet mit leichtem Fingerdruck? Fällt er beim Hochhalten von selbst heraus? Planheit mit Lineal (Verzug bei 1 mm Dicke). "
                            "Geht ein Dupont-Stift durch alle Trichterlöcher?"),
                 ("Erfolg / sonst", "Kleinstes Spiel, das noch leicht gleitet, wird <code>KEY_CLR</code>. Verzogen: Brim, langsamere erste Schicht. "
                                    "Fällt heraus: Raste am Schieber (im Entwurf sperrt nur die Muldenwand im gesteckten Zustand)."),
             ],
             meta=["%s g" % de(PARTS["N"]["g"]), "≈ %d min" % round(minutes("N")), "STL vorhanden"], waits="K (Schieberdicke)",
             known="Mit 0,15 im Probestück mitgedruckt, ohne Einzelwerte. Die Decke über der Nut ist im Probestück eine Brücke (20 × 34 mm, 209 mm²), die README nannte nur das Dach als Brücke."),
        dict(id="D", dom="plate", title="Podest + Deckel", stage="Stufe 2", when="Nacht 1, optional",
             q="Dein Gedanke stimmt: Platte und Deckel sehen nur die Winkelleiste, nicht das Gebäude. Sind sie für sich prüfbar?",
             rows=[
                 ("Teile", "<code>0_passprobe.stl</code> (Passprobe v6, vorhanden, nicht gedruckt): Stufenhöhe für Körperhöhe 2,0 / 1,8 / 1,6. "
                           "Platte und Deckel (<code>4_platte.stl</code>, <code>5_deckel.stl</code>) nur drucken, wenn die alten fehlen; sonst messen."),
                 ("Messen", "Körper in der Tasche (Spiel %s je Seite), Lötende liegt flach unter der Stufe, Pins kommen gerade durch die 1,4-Löcher. "
                            "Pin-Lage gegen die Buchse prüfen: Buchse direkt aufstecken, treffen alle vier Pins? Deckelstempel halten den Körper gegen Druck."
                  % de(sd.SNUG_HDR)),
                 ("Erfolg / sonst", "Pins stehen im Raster und senkrecht. Lötende nicht flach: <code>STEP_CLR</code>. Körper wackelt: Heißkleber ist akzeptiert."),
             ],
             meta=["%s g" % de(PARTS["D"]["g"]), "≈ %d min" % round(minutes("D")), "STL vorhanden"], waits="–",
             known="Passprobe Runden 1 bis 4 und das Probestück sind ausgewertet („passt mit 2,0“). Offen ist nur die Stufenhöhe."),
        dict(id="FM", dom="bld", title="Fuß ↔ Mulde", stage="Stufe 2", when="Nacht 1, optional",
             q="Wie viel von „wackelt überall“ kommt vom Fuß in der Mulde? Das ist mit ±0,25 der größte Einzelanteil in der Ausrichtung der Pins.",
             rows=[
                 ("Teile", "<code>FM_mulde_rings.stl</code>: drei Ringe mit der Mulde des Probestücks (Führungsband, Relief, Einlauffase, Kodierecke) und <code>CLR</code> 0,10 / 0,15 / 0,20. "
                           "Als Fuß dient das bereits gedruckte Probestück-Gebäude (<code>1_probestueck.stl</code>)."),
                 ("Fühlen", "Fuß in jeden Ring stellen: Welcher lässt ihn ohne Klemmen bis zum Boden sinken, bei welchem wackelt er? ENG und WEIT notieren."),
                 ("Erfolg", "Kleinstes Spiel ohne Klemmen wird <code>CLR</code>. Federzunge, Rast und Haltekraft (3 bis 8 N) sind nicht Teil dieser Serie."),
             ],
             meta=["%s g" % de(PARTS["FM"]["g"]), "≈ %d min" % round(minutes("FM")), "STL vorhanden"], waits="–",
             known="Probestück gedruckt, „passt, wackelt“. Federzunge und Kräfte nicht gemessen. Schwerstes Teil der ersten Nacht."),
        dict(id="L", dom="led", title="Licht durch die Wand", stage="Stufe 2", when="Nacht, wenn Controller da",
             q="Wie viel Wand lässt die LED noch durchscheinen, und zwar mit dem Filament, das wirklich für die Gebäude vorgesehen ist?",
             rows=[
                 ("Aufbau", "Wandstreifen 0,4 / 0,8 / 1,2 mm mit Fenster 6 × 4,5, je in den Gebäudefarben (Beige, Blaugrau, Graphit). Die WS2812B leuchtet nur mit Datensignal, "
                            "du brauchst also Controller oder Testprogramm."),
                 ("Erfolg", "Gleichmäßig hell, Fensterrand nicht als Rahmen zu sehen. Der Slicer muss die 0,4-mm-Wand wirklich drucken (Vorschau prüfen)."),
             ],
             meta=["%s g" % de(PARTS["L"]["g"]), "≈ %d min" % round(minutes("L")), "STL neu"], waits="–",
             known="Im Probestück als 0,4-mm-Fenster mitgedruckt; nicht als Problem gemeldet, keine Einzelangaben."),
        dict(id="S", dom="kass", title="Kassette ↔ Schacht", stage="Stufe 3", when="Nacht 1",
             q="Die Lücke zwischen Kassette und Gebäude: Wie klein darf <code>KASS_CLR</code> (jetzt %s je Seite) werden, ohne zu klemmen? Das Spiel geht 1:1 in die Pin-Ausrichtung ein." % de(sd.KASS_CLR, 2),
             rows=[
                 ("Teile", "<code>S_floor_slabs.stl</code>: vier Boden-Platten, die Unterseite des Probestücks 1:1 (Fußumriss, Schacht, Schwalbenschwanz-Nut), 9 mm hoch, "
                           "Schachtspiel 0,05 / 0,10 / 0,15 / 0,20 je Seite. Lehre ist die Kassette aus C (%s × %s)." % (de(d["cass_w"]), de(d["cass_len"]))),
                 ("Fühlen", "Kassette von oben in den Schacht setzen, auf dem Schieber stehend wie im Gebäude. Welche Platte lässt sie ohne Kraft einsinken, bei welcher wackelt sie spürbar?"),
                 ("Erfolg / sonst", "Kleinstes Spiel, bei dem die Kassette noch von selbst einsinkt, wird <code>KASS_CLR</code> (Druckabweichung etwa ±0,1 mitdenken). "
                                    "Das ist nur die Seitenpassung; Anschlag, Sockel durch den Kammerboden und Fenster prüft V1."),
             ],
             meta=["%s g" % de(PARTS["S"]["g"]), "≈ %d min" % round(minutes("S")), "STL vorhanden"], waits="C (Lehre)",
             known="Mit 0,2 im Probestück mitgedruckt („wackelt“), ohne Zahl."),
        dict(id="V1", dom="join", title="Gebäude trocken", stage="Stufe 4", when="Tag 2",
             q="Passt alles zwischen Kassette und Gebäude zusammen, bevor Pins ins Spiel kommen?",
             rows=[
                 ("Teile", "Gebäude <code>1_probestueck.stl</code> (vorhanden, entfällt, wenn das alte noch da ist), Kassette aus C, Schieber aus N, mit den Spielwerten aus S und N."),
                 ("Prüfen", "Kassette von unten einschieben, Anschlag, Sockel ragt durch den Kammerboden, LED in der Bodenöffnung, Schieber einschieben und bündig, Gesamtwackeln mit der Fühlerlehre. "
                            "Zum Schluss als Pin-Lehre ein männlicher Dupont-Stecker von unten durch alle vier Trichterlöcher: trifft er die Buchsenöffnung?"),
                 ("Erfolg", "Alles montiert sich ohne Gewalt, Restspiel gesamt unter etwa 0,3 mm."),
             ],
             meta=["%s g" % de(PARTS["V1"]["g"]), "≈ %d min" % round(minutes("V1")), "STL vorhanden"], waits="C, S, N (K)",
             known="Als Ganzes einmal gedruckt, ohne Einzelwerte."),
        dict(id="V2", dom="join", title="Stecken mit Pins", stage="Stufe 4", when="Tag 2",
             q="Greift der Mechanismus, wenn alles zusammenkommt?",
             rows=[
                 ("Teile", "<code>4_platte.stl</code> + <code>5_deckel.stl</code> (vorhanden, entfallen, wenn die alten da sind), Winkelleiste gelötet."),
                 ("Prüfen", "Pin-Fang im ungünstigsten Fall: das Gebäude beim Stecken gegen jede der vier Muldenwände drücken. Durchgang, DETECT liest LOW, LED leuchtet. "
                            "Stecken unter 10 N, Ziehen 3 bis 8 N, hebt die Mini-Platte nicht mit. Licht auf allen vier Seiten."),
                 ("Erfolg", "Kontakt in jeder Seitenlage, Ziehen im Zielbereich."),
             ],
             meta=["%s g" % de(PARTS["V2"]["g"]), "≈ %d min" % round(minutes("V2")), "STL vorhanden"], waits="V1, D, FM (L)",
             known="Als Ganzes einmal gedruckt, Kontakt und Kräfte nicht einzeln gemessen."),
    ]
    html = []
    for c in cards:
        rows = "".join("<dt>%s</dt><dd>%s</dd>" % (k, v) for k, v in c["rows"])
        meta = "".join('<span class="chip%s">%s</span>' % (" neu" if m.startswith("STL neu") else (" ok" if m.startswith("STL vorh") else ""), m) for m in c["meta"])
        html.append(
            '<article class="card %s" id="t-%s"><header><span class="bd">%s</span><h3>%s</h3><span class="stage">%s · %s</span></header>'
            '<p class="q">%s</p><dl>%s</dl><p class="known"><b>Stand:</b> %s</p>'
            '<footer><span class="chips">%s</span><span class="waits">wartet auf: %s</span></footer></article>'
            % (c["dom"], c["id"], c["id"], c["title"], c["stage"], c["when"], c["q"], rows, c["known"], meta, c["waits"]))
    return "\n".join(html)


# --------------------------------------------------------------------------
def main():
    d = I.dims()
    with open(TEMPLATE, encoding="utf-8") as f:
        page = f.read()
    rep = {
        "{{FIG_GRAPH}}": graph_svg(),
        "{{FIG_SECTION}}": section_svg(),
        "{{FIG_TIME}}": time_svg(),
        "{{CARDS}}": build_cards(),
        "{{G_CORE}}": de(G_CORE, 0),
        "{{G_ALL}}": de(G_ALL, 0),
        "{{H_CORE}}": de(job(CORE) / 60.0),
        "{{H_CORE_FAST}}": de(job(CORE, "schnell") / 60.0),
        "{{H_ALL}}": de((job(CORE) + sum(minutes(k) for k in EXTRA)) / 60.0),
        "{{H_ALL_FAST}}": de((job(CORE, "schnell") + sum(minutes(k, "schnell") for k in EXTRA)) / 60.0),
        "{{CORE_END}}": hm(T_CORE1),
        "{{E}}": de(d["E"], 2),
        "{{F}}": de(d["F"]),
        "{{KASS_CLR}}": de(sd.KASS_CLR, 2),
        "{{KEY_CLR}}": de(sd.KEY_CLR, 2),
        "{{SNUG}}": de(sd.SNUG, 2),
        "{{RIB}}": de(sd.RIB, 2),
        "{{CLR}}": de(sd.CLR, 2),
        "{{SEAT}}": "%s × %s mm" % (de(I.SEAT_W), de(I.SEAT_L)),
    }
    for k, v in rep.items():
        page = page.replace(k, v)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(page)
    print("geschrieben: %s (%d kB)" % (os.path.relpath(OUT, os.path.dirname(HERE)), os.path.getsize(OUT) / 1024))
    print("Kern %s g, %s h, fertig um %s; mit FM %s g, fertig um %s" % (de(G_CORE), de(job(CORE) / 60.0), hm(T_CORE1), de(G_ALL), hm(T_ALL1)))

if __name__ == "__main__":
    main()
