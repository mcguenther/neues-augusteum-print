#!/usr/bin/env python3
"""Planungsseite Kassetten-Varianten: baut plug/testcase/plan3.html aus plan.template.html (gleicher Stil wie plan.html und plan2.html).

Anlass: Kassette v4 (13,5 × 29,4, Streifen flach) passt im Maßstab 1:1500 nicht in Seminargebäude, City-Hochhaus und Paulinum.
V1 = Streifen quer auf einer Wand (niedrig, 17,2 breit), V2 = Streifen hochkant auf einer Wand (schlank, 13 breit, hoch).
Maße aus plug/testcase/variants.py, Passstudie aus plug/testcase/variants_fit.json (erzeugt von plug/testcase/fit_study.py).

Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m plug.testcase.variants        # Bild vorschau/steckmodul_testcase/varianten_v1_v2.png
    python3 -m plug.testcase.build_plan3     # schreibt plug/testcase/plan3.html
"""
import json
import math
import os

from shapely.geometry import Polygon

from plug import dupont as sd
from plug.feedback.build import G
from plug.testcase import build_plan as BP
from plug.testcase import params as P
from plug.testcase import variants as V
from plug.testcase.build_plan import de, decision_card

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TEMPLATE = os.path.join(HERE, "plan.template.html")
OUT = os.path.join(HERE, "plan3.html")
FIT = json.load(open(os.path.join(HERE, "variants_fit.json"), encoding="utf-8"))
META = FIT["_meta"]
LABEL = {"v4": "Kassette v4", "V1": "V1 (quer)", "V2": "V2 (hochkant)", "V2R": "V2 mit Rücken-LED"}
WALL = META["wall_min"]
F = P.dims()["F"]                      # Fußhöhe: Plattenoberseite liegt F über der Kassettenunterkante
BUCHSE = 14.55
NAMES = {"01_paulinum": "Paulinum", "02_neues_augusteum": "Neues Augusteum", "03_hoersaalgebaeude": "Hörsaalgebäude",
         "04_seminargebaeude": "Seminargebäude", "05_institutsgebaeude": "Institutsgebäude", "06_city_hochhaus": "City-Hochhaus"}
KEYS = ("v4", "V1", "V2", "V2R")


def outer(k):
    a, b = META["cassettes"][k]
    return a + 2 * WALL, b + 2 * WALL


def bad_out():
    """Rücken-Chip am hinteren Blatt (V2): so weit ragt er hinter die Schachtwand."""
    d = V.dims("V2")
    return d["y1"] + V.BLATT_T + V.STRIP_T - (d["depth"] + 0.06)


def need_height(k):
    """Kleinste Gebäudehöhe über der Platte: Kassettenoberkante über der Platte (Fuß 10,2) plus Dach 1,2."""
    return V.min_height(k)


# --------------------------------------------------------------------------
# Zeichnungen
# --------------------------------------------------------------------------
def svg_fit(scale, name):
    """Grundriss mit den drei Außenrechtecken (Kassette + Spiel + 1,2 Wand): grün = passt, rot gestrichelt = passt nicht."""
    row = FIT["%s/%s" % (scale, name)]
    poly = Polygon(row["poly"])
    turn = poly.bounds[3] - poly.bounds[1] > 1.5 * (poly.bounds[2] - poly.bounds[0])       # lange Gebäude um 90° gedreht zeichnen
    tf = (lambda x, y: (y, -x)) if turn else (lambda x, y: (x, y))
    pts_uv = [tf(x, y) for x, y in row["poly"]]
    u0, u1 = min(p[0] for p in pts_uv), max(p[0] for p in pts_uv)
    v0, v1 = min(p[1] for p in pts_uv), max(p[1] for p in pts_uv)
    S = min(300.0 / (u1 - u0), 220.0 / (v1 - v0), 7.0)
    pad = 10
    W, H = (u1 - u0) * S + 2 * pad, (v1 - v0) * S + 2 * pad
    sx = lambda x, y: pad + (tf(x, y)[0] - u0) * S
    sy = lambda x, y: pad + (v1 - tf(x, y)[1]) * S
    panels = []
    for k in KEYS:
        o = ['<svg viewBox="0 0 %d %d" role="img" aria-label="%s: %s" class="dgsvg">' % (W, H, NAMES[name], k)]
        o.append('<polygon points="%s" class="d-bld"/>' % " ".join("%.1f,%.1f" % (sx(x, y), sy(x, y)) for x, y in row["poly"]))
        a, b = outer(k)
        pl = row["place"][k]
        if pl is None:                             # passt nicht: im Schwerpunkt, Längsachse wie das kleinste umschließende Rechteck
            c = poly.centroid
            mrr = list(poly.minimum_rotated_rectangle.exterior.coords)
            e = [(math.dist(mrr[i], mrr[i + 1]), math.degrees(math.atan2(mrr[i + 1][1] - mrr[i][1], mrr[i + 1][0] - mrr[i][0]))) for i in range(2)]
            ang = max(e)[1]
            if a < b:
                ang -= 90.0
            pl = (c.x, c.y, ang)
        cx, cy, ang = pl
        r = math.radians(ang)
        pts = []
        for ux, uy in ((-a / 2, -b / 2), (a / 2, -b / 2), (a / 2, b / 2), (-a / 2, b / 2)):
            pts.append((cx + ux * math.cos(r) - uy * math.sin(r), cy + ux * math.sin(r) + uy * math.cos(r)))
        fits = row["walls"][k] is not None and row["walls"][k] >= WALL
        sty = "fill:color-mix(in srgb,var(--new) 30%,transparent);stroke:var(--new);stroke-width:1.6" if fits else \
              "fill:color-mix(in srgb,var(--warn) 22%,transparent);stroke:var(--warn);stroke-width:1.6;stroke-dasharray:5 3"
        o.append('<polygon points="%s" style="%s"/>' % (" ".join("%.1f,%.1f" % (sx(x, y), sy(x, y)) for x, y in pts), sty))
        o.append('</svg>')
        wv = row["walls"][k]
        cap = "%s: %s × %s mm außen, %s" % (LABEL[k], de(a, 1), de(b, 1),
                                           "passt nicht" if wv is None else ("passt, Wand bis %s" % de(wv, 1) if fits else "Wand nur %s" % de(wv, 1)))
        panels.append('<figure class="fig"><div class="figbox">%s</div><figcaption>%s</figcaption></figure>' % ("".join(o), cap))
    return '<div class="three">%s</div>' % "".join(panels)


def svg_section(var):
    """Schnitt längs y durch die Mitte (x = 0): Unterbau, Buchse, Blatt, Streifen mit Chip, Plattenoberseite, Maße."""
    d = V.dims(var)
    S = 13.0 if var == "V1" else 11.0
    zmax = d["top"] + 3.5
    g = G(S, 78, 14 + zmax * S)
    depth, zb, y1, zp, z0, sh, top = d["depth"], d["z_b"], d["y1"], d["zp"], d["z0"], d["sh"], d["top"]
    c = 0.06
    g.rect(-3.0, -c, 0.0, F, "d-bld")
    g.rect(depth + c, depth + 3.0, 0.0, F, "d-bld")
    g.text(-3.4, F / 2, "Fuß", "dls", "end")
    g.rect(0.0, depth, 0.0, zb, "d-kass")
    g.rect(d["y_p0"], y1, -0.01, zp, "d-void")
    g.rect(d["y_p0"], y1, zp - 0.01, zb + 0.01, "d-void")
    g.rect(d["ypin"] - sd.HSG_T / 2, d["ypin"] + sd.HSG_T / 2, 0.0, BUCHSE, "d-hsg")
    g.rect(y1, y1 + V.BLATT_T, zb - 0.01, top, "d-kass")
    g.rect(y1 - V.FPC, y1, z0, z0 + sh, "d-led")
    zc = z0 + sh / 2
    g.rect(y1 - V.STRIP_T, y1 - V.FPC, zc - V.CHIP / 2, zc + V.CHIP / 2, "d-led")
    g.o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="d-dash"/>' % (g.X(-6.5), g.Z(F), g.X(depth + 7.5), g.Z(F)))
    g.text(depth + 7.7, F - 0.3, "Plattenoberseite", "dls", "start")
    if var == "V2":
        pts = V.wire_path("V2", 1)
        g.o.append('<polyline points="%s" fill="none" class="d-wire"/>' % " ".join("%.1f,%.1f" % (g.X(p[1]), g.Z(p[2])) for p in pts))
    # Licht
    g.o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="dimn" style="stroke-width:2"/>' % (g.X(y1 - V.STRIP_T - 0.2), g.Z(zc), g.X(-2.6), g.Z(zc)))
    g.text(-2.8, zc + 0.9, "Licht", "dln", "end")
    # Maße
    xr = depth + 3.4
    g.line(xr, 0.0, xr, zb, "dimn")
    g.text(xr + 0.3, zb / 2, "Unterbau %s" % de(zb), "dln", "start")
    g.line(xr, z0, xr, z0 + sh, "dimn")
    g.text(xr + 0.3, z0 + sh / 2 + 0.4, "Streifen %s" % de(sh, 1), "dln", "start")
    g.text(xr + 0.3, z0 + sh / 2 - 0.8, "(LED-Mitte %s über der Platte)" % de(zc - F, 1), "dls", "start")
    g.line(xr, zb, xr, z0, "dimn")
    g.text(xr + 0.3, zb + d["room"] / 2 - 0.3, "Adern %s" % de(d["room"], 1), "dls", "start")
    g.line(xr, 0.0, xr, 0.0, "dimn")
    g.line(0.0, -1.2, depth, -1.2, "dimn")
    g.text(depth / 2, -2.3, "%s tief" % de(depth), "dln")
    g.text(depth / 2, zb / 2, "Kassette", "dlb")
    g.text(depth + 1.0 + V.BLATT_T, top + 0.9, "Blatt %s dick, bis %s" % (de(V.BLATT_T, 1), de(top)), "dls", "start")
    g.text(0.2 - 3.4, zb - 3.0, "Buchse", "dls", "end")
    g.o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="dim" style="stroke-width:.6"/>' % (g.X(-3.3), g.Z(zb - 3.2), g.X(d["ypin"] - 1.2), g.Z(zb - 3.2)))
    return g.svg(int(78 + (depth + 3.8) * S + 215), int(14 + zmax * S + 40), "Schnitt der Kassette %s mit Streifen und Maßen" % var)


def svg_rueck(kind):
    """Schnitt längs y mit Schachtwänden (gestrichelt): kind = "bad" (Rücken-Streifen am hinteren Blatt) oder "V2R" (Blatt in der Mitte, oben nach vorn versetzt)."""
    S = 11.0
    var = "V2R" if kind == "V2R" else "V2"
    d = V.dims(var)
    depth, zb, zp = d["depth"], d["z_b"], d["zp"]
    top = d["top"] if kind == "V2R" else d["top"] + V.R_JUMP
    zmax = top + 3.0
    g = G(S, 70, 12 + zmax * S)
    c = 0.06
    g.rect(-2.6, -c, 0.0, F, "d-bld")
    g.rect(depth + c, depth + 2.6, 0.0, F, "d-bld")
    g.rect(0.0, depth, 0.0, zb, "d-kass")
    g.rect(d["y_p0"], d["y1"], -0.01, zb + 0.01, "d-void")
    g.rect(d["ypin"] - sd.HSG_T / 2, d["ypin"] + sd.HSG_T / 2, 0.0, BUCHSE, "d-hsg")
    if kind == "V2R":
        zj, jog, yb = d["z_j"], d["jog"], d["yb"]
        g.rect(d["y1"], d["y1"] + V.BLATT_T, zb - 0.01, zj + 0.01, "d-kass")
        g.poly([(d["y1"], zj), (d["y1"] + V.BLATT_T, zj), (yb + V.BLATT_T, zj + jog), (yb, zj + jog)], "d-kass")
        g.rect(yb, yb + V.BLATT_T, zj + jog - 0.01, top, "d-kass")
        yf, yr = yb, yb + V.BLATT_T
    else:
        g.rect(d["y1"], d["y1"] + V.BLATT_T, zb - 0.01, top, "d-kass")
        yf, yr = d["y1"], d["y1"] + V.BLATT_T
    z0, sh = d["z0"], d["sh"]
    zc = z0 + sh / 2
    g.rect(yf - V.FPC, yf, z0, z0 + sh, "d-led")
    g.rect(yf - V.STRIP_T, yf - V.FPC, zc - V.CHIP / 2, zc + V.CHIP / 2, "d-led")
    g.rect(yr, yr + V.FPC, z0, z0 + sh, "d-led")
    g.rect(yr + V.FPC, yr + V.STRIP_T, zc - V.CHIP / 2, zc + V.CHIP / 2, "d-led")
    g.o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="d-dash"/>' % (g.X(-4.0), g.Z(F), g.X(depth + 4.0), g.Z(F)))
    g.text(depth + 4.2, F - 0.3, "Platte", "dls", "start")
    for y in (-c, depth + c):                              # Schachtwände über die ganze Höhe
        g.o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" style="stroke:var(--warn);stroke-width:1.4;stroke-dasharray:6 4"/>' % (g.X(y), g.Z(0), g.X(y), g.Z(top + 1.5)))
    yb_chip = yr + V.STRIP_T
    if kind == "bad":
        g.text(depth + 0.6, zc + 4.2, "ragt %s aus dem Schacht" % de(yb_chip - depth - c, 1), "dlw", "start")
        g.text(depth + 0.6, zc + 3.1, "(Rücken-LED, von unten", "dlw", "start")
        g.text(depth + 0.6, zc + 2.2, "nicht durchzuschieben)", "dlw", "start")
    else:
        for y, lab in ((yf - V.STRIP_T, "vorderer Chip"), (yb_chip, "hinterer Chip")):
            pass
        pts = V.wire_path("V2R", 1)
        g.o.append('<polyline points="%s" fill="none" class="d-wire"/>' % " ".join("%.1f,%.1f" % (g.X(q[1]), g.Z(q[2])) for q in pts))
        wr = sd.WIRE_D / 2
        jp = [(yf - V.FPC - wr - 0.1, z0 + sh - 1.5), (yf - V.FPC - wr - 0.1, top + 0.3), (yf + V.BLATT_T / 2, top + 0.4), (yr + V.FPC + wr + 0.1, top + 0.3), (yr + V.FPC + wr + 0.1, z0 + sh - 1.5)]
        g.o.append('<polyline points="%s" fill="none" class="d-wire"/>' % " ".join("%.1f,%.1f" % (g.X(a), g.Z(b)) for a, b in jp))
        g.text(yf + V.BLATT_T / 2, top + 1.6, "Verkettung über die Kante", "dls")
        g.text(depth + 0.8, zj + jog / 2 + 0.2, "Versatz 45°", "dls", "start")
        g.line(yf - V.STRIP_T, zc + 6.0, yb_chip, zc + 6.0, "dimn")
        g.text((yf - V.STRIP_T + yb_chip) / 2, zc + 6.6, "%s von Chip zu Chip" % de(yb_chip - (yf - V.STRIP_T), 1), "dln")
        g.text(depth + 0.8, zc - 0.4, "Luft %s vorn und hinten" % de(min(yf - V.STRIP_T, depth - yb_chip), 1), "dls", "start")
    g.text(depth / 2, zb / 2, "Unterbau %s tief" % de(depth, 2), "dlb")
    return g.svg(int(70 + (depth + 3.0) * S + 160), int(12 + zmax * S + 18), "Schnitt: Schachtwände gestrichelt, %s" % ("Rücken-LED ragt aus dem Schacht" if kind == "bad" else "Blatt versetzt, beide Streifen im Schacht"))


# --------------------------------------------------------------------------
# Inhalt
# --------------------------------------------------------------------------
def head():
    o = V.outlines()
    return ('<header class="top"><p class="kicker">Steckmechanismus · Kassette</p><h1>Kassette V2: Höhe und zweite LED</h1>'
            '<p class="lead">Stand 2: V2 (Streifen hochkant auf einem Blatt über der Buchse) ist die bevorzugte Variante. Diese Seite beantwortet zwei Fragen: Passt V2 von der Höhe in die Gebäude, '
            'und geht eine zweite LED auf der Rückseite? Darunter steht weiter der erste Plan mit V1 und v4 als Vergleich. Konzepte, keine STL.</p>'
            '<ul class="sum"><li><b>Höhe:</b> V2 braucht Gebäude ab %s mm. Bei 1:1500 reicht das nur für City-Hochhaus und Paulinum; bei 1:1000 kommt Neues Augusteum dazu (Institutsgebäude knapp nicht, 0,9 mm Wand). Seminar- und Hörsaalgebäude sind zu niedrig.</li>'
            '<li><b>Rücken-LED:</b> Du hast recht, so wie V2 jetzt gezeichnet ist, schiebt sie sich von unten nicht durch den Schacht (der hintere Chip ragt %s mm heraus). Dein Vorschlag, das Blatt oben nach vorn zu versetzen, geht, wenn der Unterbau auf %s mm Tiefe wächst.</li>'
            '<li><b>Mit zweiter LED:</b> %s × %s × %s mm, Gebäude ab %s mm hoch: bei 1:1500 nur das City-Hochhaus, bei 1:1000 Paulinum, Neues Augusteum und Hochhaus.</li>'
            '<li><b>Seminargebäude</b> (1:1500) ist ein eigenes Problem: Dach nur etwa 16,4 mm hoch und schmal; dafür braucht es eine niedrige Variante (siehe Karte „Seminargebäude“).</li></ul></header>'
            % (de(need_height("V2"), 1), de(bad_out(), 1), de(V.R_DEPTH, 1),
               de(o["V2R"]["w"], 1), de(o["V2R"]["d"], 1), de(o["V2R"]["h"], 1), de(need_height("V2R"), 1)))


def sec_height():
    rows = []
    for k in ("V2", "V2R"):
        for sc, lab in (("1zu1500", "1:1500"), ("1zu1000", "1:1000")):
            ok, no = [], []
            for name in NAMES:
                r = FIT["%s/%s" % (sc, name)]
                (ok if combined(r, k).startswith("✓") else no).append("%s (%s)" % (NAMES[name], de(r["height"], 1)))
            rows.append("<tr><td><b>%s</b></td><td>%s</td><td class=\"n\">%s</td><td>%s</td><td>%s</td></tr>" % (LABEL[k], lab, de(need_height(k), 1), ", ".join(ok) or "–", ", ".join(no)))
    tab = ('<div class="tw"><table class="t"><thead><tr><th>Variante</th><th>Maßstab</th><th>braucht</th><th>passt (Gebäudehöhe)</th><th>passt nicht</th></tr></thead><tbody>%s</tbody></table></div>' % "".join(rows))
    return ('<section class="sec"><h2>Frage 1: Passt V2 von der Höhe in die Gebäude?</h2>%s'
            '<p class="note">Der Fuß taucht %s mm in die Platte, darüber steht die Kassette; V2 ragt %s mm über die Platte und braucht darüber %s mm Dach. Das sind %s mm Gebäudehöhe. '
            'Die Rechnung nimmt die Dachform aus dem Laserscan: Das Seminargebäude ist laut Scan 18,8 mm hoch, hat aber nur eine kleine Dachaufsicht; die geschlossene Dachfläche liegt bei etwa 16,4 mm.</p>'
            '<p class="risk"><b>Ergebnis:</b> V2 ist eine Variante für hohe Gebäude (City-Hochhaus, Paulinum, bei 1:1000 auch Neues Augusteum). Für Seminar-, Institut- und Hörsaalgebäude bei 1:1500 reicht die Höhe nicht. '
            'Hebel, um niedriger zu werden: 144-LED/m-Streifen (13,9 statt 16,7 lang, aber 12 breit) spart 2,8 mm; Dach über der Kassette dünner (0,8 statt 1,2) spart 0,4 mm; der Fuß (%s) ist durch die Pin-Länge festgelegt.</p></section>'
            % (tab, de(F, 1), de(V.dims("V2")["top"] - F, 1), de(P.STOP_T, 1), de(need_height("V2"), 1), de(F, 1)))


def sec_rueck():
    d2, dr = V.dims("V2"), V.dims("V2R")
    o = V.outlines()
    f1 = ('<figure class="fig"><div class="figbox s460">%s</div><figcaption>So geht es nicht: Streifen auf dem Rücken des hinteren Blatts. Der Chip ragt %s mm hinter die Schachtwand (rot gestrichelt), der Streifen allein schon %s.</figcaption></figure>'
          % (svg_rueck("bad"), de(bad_out(), 1), de(d2["y1"] + V.BLATT_T + V.FPC - (d2["depth"] + 0.06), 1)))
    f2 = ('<figure class="fig"><div class="figbox s460">%s</div><figcaption>Dein Vorschlag, V2R: Das Blatt steigt zuerst an der hinteren Wand, springt dann mit 45° nach vorn in die Mitte und trägt beide Streifen. Beide Chips liegen innerhalb der Schachtwände.</figcaption></figure>'
          % svg_rueck("V2R"))
    chain = [("vorderer Chip bis hinterer Chip", de(V.BLATT_T + 2 * V.STRIP_T, 1), "Chip 1,9 + Folie 0,3 je Seite + Blatt 1,2"),
             ("Unterbau (Schacht ohne Spiel)", de(V.R_DEPTH, 1), "Luft %s vorn und hinten" % de((V.R_DEPTH - (V.BLATT_T + 2 * V.STRIP_T)) / 2, 1)),
             ("Blatt oben, Vorderseite bei y", de(V.R_BLADE_Y, 1), "Mitte des Unterbaus: %s" % de(V.R_DEPTH / 2, 1)),
             ("Versatz des Blatts nach vorn", de(dr["jog"], 2), "45°, also %s mm Höhe" % de(dr["jog"], 2)),
             ("Streifenunterkante über der Schulterfläche", de(dr["room"], 2), "Ader-Luft ab dem Versatz"),
             ("Oberkante des Blatts", de(dr["top"], 1), "Streifenende + 0,25 + %s für die Verkettungsadern" % de(V.R_JUMP, 1))]
    trs = "".join('<tr><td>%s</td><td class="n">%s</td><td>%s</td></tr>' % c for c in chain)
    return ('<section class="sec"><h2>Frage 2: Zweite LED auf der Rückseite</h2>'
            '<p>Du hast richtig vermutet. Die Kassette wird mit dem Streifenende voran von unten durch den Schacht im Fuß geschoben (Fuß %s mm), also muss jeder Querschnitt der Kassette durch diesen Schacht passen. '
            'Mit dem Blatt hinten säße der Rücken-Streifen bei y %s bis %s und damit hinter der Schachtwand. Das Blatt nach oben zu verlängern hilft dafür nicht, es muss in y in die Mitte.</p>'
            '<div class="two">%s%s</div>'
            '<p class="note">Der Versatz (Dein Gedanke) geht, ist aber knapp: Chip-Seite zu Chip-Seite sind %s mm (2 × 2,2 Streifen + 1,2 Blatt). Der bisherige Unterbau (%s tief) ist dafür um %s mm zu flach, und die Streifendicke (2,2) ist nicht belegt. '
            'Darum wächst der Unterbau auf %s mm Tiefe (+%s), die Pins und die Buchse bleiben unverändert vorn. Außenmaß dann %s × %s mm.</p>'
            '<div class="tw"><table class="t"><thead><tr><th>Größe</th><th>mm</th><th>Bemerkung</th></tr></thead><tbody>%s</tbody></table></div>'
            '<p class="note"><b>Verkettung statt zweier Adersätze:</b> Der WS2812B-Streifen hat an beiden Enden Pads. Der vordere Streifen bekommt die Adern von der Buchse (unten, DIN), sein oberes Ende (DOUT) geht mit drei kurzen Adern über die Oberkante des Blatts zum oberen Ende des hinteren Streifens, '
            'der dafür um 180° gedreht aufgeklebt wird. So gibt es nur einen Satz Adern durch den Schlitz. Zwei LEDs in Reihe an einem Controller-Ausgang sind kein Problem; der Streifen braucht etwa doppelt so viel Strom (bis etwa 120 mA bei Weiß).</p>'
            '<p class="risk"><b>Nachteile:</b> Das Blatt wird %s mm höher als bei V2 (Verkettung über die Kante, Versatz), das Gebäude muss ab %s mm hoch sein. Der Versatz ist ein 45°-Überhang über dem Aderschlitz (druckbar, aber ungetestet). '
            'Das Blatt steht frei und trägt jetzt zwei Streifen: L06 (dünn und hoch) gilt verschärft.</p>'
            '<figure class="fig"><img alt="V2 mit Rücken-LED: vorn, hinten, im Schnitt" src="%s"><figcaption>V2R, Konzept: von vorn (Streifen A mit Adern), von hinten (Streifen B), im Schnitt. Orange: Kassette, weiß: Buchse, gelb: Streifen, rot: Adern.</figcaption></figure></section>'
            % (de(F, 1), de(d2["y1"] + V.BLATT_T, 1), de(d2["y1"] + V.BLATT_T + V.STRIP_T, 1), f1, f2, de(V.BLATT_T + 2 * V.STRIP_T, 1), de(d2["depth"], 2), de((V.BLATT_T + 2 * V.STRIP_T) - d2["depth"], 2),
               de(V.R_DEPTH, 1), de(V.R_DEPTH - d2["depth"], 2), de(o["V2R"]["w"], 1), de(o["V2R"]["d"], 1), trs,
               de(dr["top"] - d2["top"], 1), de(need_height("V2R"), 1), BP.img_uri("variante_v2r.png", 1000)))


def sec_verstanden():
    return ('<section class="sec"><h2>Erster Plan: so habe ich V1 und V2 verstanden</h2><ul class="q">'
            '<li><b>V1:</b> Der Streifen wird um 90° gekippt und steht auf der langen Kante (16,7 mm waagerecht, 10 mm hoch). Er klebt auf einer Wand.</li>'
            '<li><b>V2:</b> Der Streifen steht hochkant (10 mm breit, 16,7 mm senkrecht) auf einer flacheren, dünnen Wand. Die Kassette ist nur die Buchse mit dieser Wand, deshalb schlank.</li>'
            '<li>Die Wand ist ein <b>Blatt</b>, das die hintere Taschenwand nach oben fortsetzt; der Streifen sitzt <b>über der Buchse</b>, die LED blickt nach vorn. '
            'So liegt die LED über der Platte und die Adern kommen ohne Durchbruch zu den Pads.</li></ul></section>')


def combined(r, k):
    """Passt die Kassette in Grundriss UND Höhe? (Schnitt in der nötigen Höhe, Wand ab 1,2)"""
    need = r["need"][k]
    if r["height"] < need:
        return "✗ zu niedrig (%s)" % de(need, 1)
    wf, wh = r["walls"][k], r["walls_h"][k]
    if wf is None or wf < WALL:
        return "✗ Grundriss"
    if wh is None or wh < WALL:
        return "✗ oben zu schmal" if wh is None else "✗ oben Wand %s" % de(wh, 1)
    return "✓ Wand %s" % de(min(wh, 3.9), 1)


def sec_befund():
    rows = []
    for name in NAMES:
        r15, r10 = FIT["1zu1500/" + name], FIT["1zu1000/" + name]
        cells = "".join('<td class="n">%s<br><span style="color:var(--muted)">1:1000: %s</span></td>' % (combined(r15, k), combined(r10, k)) for k in KEYS)
        rows.append('<tr><td><b>%s</b></td><td class="n">%s<br><span style="color:var(--muted)">1:1000: %s</span></td>%s</tr>' % (
            NAMES[name], de(r15["height"], 1), de(r10["height"], 1), cells))
    thead = ('<tr><th>Gebäude</th><th>Höhe 1:1500</th>%s</tr>' % "".join("<th>%s<br>ab %s mm hoch</th>" % (LABEL[k], de(need_height(k), 1)) for k in KEYS))
    tab = '<div class="tw"><table class="t"><thead>%s</thead><tbody>%s</tbody></table></div>' % (thead, "".join(rows))
    figs = ""
    for name in ("04_seminargebaeude", "06_city_hochhaus"):
        figs += '<h3>%s, Maßstab 1:1500 (Grundriss)</h3>%s' % (NAMES[name], svg_fit("1zu1500", name))
    return ('<section class="sec"><h2>Passt es in die Gebäude? (Grundriss und Höhe zusammen)</h2>'
            '<p class="note">Rechnung: größtes Rechteck (beliebig gedreht und verschoben) im Schnitt des Laserscan-Gebäudes <b>in der Höhe, die die Kassette braucht</b>. Außenmaß = Kassette + 0,06 Spiel je Seite + Wand um den Schacht, '
            'ab %s mm Wand gilt „passt“. Mindesthöhe = Kassettenoberkante über der Platte (Fuß %s) plus %s Dach. Die Dachform am Einbauort ist darin berücksichtigt, soweit der Schnitt sie zeigt.</p>%s'
            '<p class="note">Die Bilder zeigen nur den Grundriss unten (2 mm über dem Boden): grün passt, rot gestrichelt passt nicht.</p>%s</section>'
            % (de(WALL, 1), de(F, 1), de(P.STOP_T, 1), tab, figs))


def sec_base():
    b = V.base()
    rows = [("Buchsentasche", "%s × %s, Tasche %s hoch, 0,20 Spiel je Seite" % (de(b["pk_w"]), de(b["pk_d"]), de(b["zp"])), "bewährt (r1 R, r2 C, r3 K), Höhe 14,60 aus dem Plan Steckprobe 2"),
            ("Schultern und Aderschlitz", "0,5 dick, Schlitz %s breit über die ganze Taschentiefe" % de(b["slot"], 1), "wie v4"),
            ("Einpressen", "0,06 Spiel je Seite, durchgehend, Schacht = Kassette + 0,3", "bewährt (r3 E), Schachttiefe L12"),
            ("Maße von Tasche zur Pin-Reihe", "Pin-Reihe bei y = %s von der Vorderseite" % de(b["ypin"]), "damit bleiben Dock, Winkelleiste und Mulde unverändert"),
            ("Fase unten", "0,5 am Bett und am Schachteingang", "Plan Steckprobe 2")]
    trs = "".join("<tr><td><b>%s</b></td><td>%s</td><td>%s</td></tr>" % r for r in rows)
    return ('<section class="sec"><h2>Was gleich bleibt (Unterbau)</h2><div class="tw"><table class="t"><thead><tr><th>Teil</th><th>Wert</th><th>Status</th></tr></thead><tbody>%s</tbody></table></div>'
            '<p class="note">Neu sind nur das Blatt über der Schulterfläche und der Streifen darauf. Es gibt keine Podest-Rundung mehr: die Adern laufen nicht mehr flach über eine Kante, sondern '
            'senkrecht aus dem Schlitz (V2) bzw. bogenförmig seitlich (V1). Die LED-Fläche der v4 entfällt, die Kassette wird vorn kürzer (%s statt %s mm tief).</p></section>'
            % (trs, de(b["depth"], 1), de(P.kass_dims()["L"], 1)))


def sec_var(var):
    d = V.dims(var)
    if var == "V1":
        title = "Variante 1: Streifen quer auf der Wand"
        txt = ('<p>Der Streifen steht auf der langen Kante (%s waagerecht, %s hoch) und klebt mit seiner Folie auf dem Blatt. Das Blatt ist %s breit wie der Unterbau, %s dick '
               'und setzt die hintere Taschenwand nach oben fort. Die Streifenunterkante liegt %s über der Schulterfläche; dort laufen die Adern.</p>'
               '<p><b>Adernweg:</b> Die Adern kommen senkrecht aus dem Schlitz, laufen unter dem Streifen seitlich in x zum Pad-Ende (4 bis 8 mm) und steigen an der Streifenkante zu den Pads. '
               'Die Pads liegen quer zur Streifenbreite, die Adern verdrillen sich dabei etwas; bei 28 AWG einzeln geführt unkritisch, aber ungetestet.</p>'
               '<p><b>Vorteile:</b> niedrig (%s statt %s bei V2), LED-Mitte %s über der Platte. <b>Nachteile:</b> 17,2 breit, Unterbau muss durchgehend 17,2 breit sein, weil das Blatt beim Einpressen '
               'von unten durch den Schacht muss.</p>')
        txt = txt % (de(V.STRIP_L, 1), de(V.STRIP_W, 1), de(d["w"], 1), de(V.BLATT_T, 1), de(d["room"], 1), de(V.dims("V1")["top"], 1), de(V.dims("V2")["top"], 1), de(d["z0"] + d["sh"] / 2 - F, 1))
    else:
        title = "Variante 2: Streifen hochkant auf der Wand"
        txt = ('<p>Der Streifen steht hochkant (%s breit, %s senkrecht). Das Blatt ist %s breit, so breit wie die Buchse samt Wänden, und %s dick. '
               'Das Pad-Ende liegt unten über dem Schlitz, die Adern gehen gerade nach oben und treffen die Pads ohne Querführung.</p>'
               '<p><b>Vorteile:</b> nur %s × %s Grundfläche, Adern ohne Verdrillung, Mast lässt sich nach oben verlängern (LED höher im Turm). '
               '<b>Nachteile:</b> hoch (%s), das Blatt steht frei %s mm über dem Unterbau und ist nur %s dick; in Druckrichtung quer zu den Schichten das schwächste Stück.</p>')
        txt = txt % (de(V.STRIP_W, 1), de(V.STRIP_L, 1), de(d["w"], 2), de(V.BLATT_T, 1), de(d["w"], 1), de(d["depth"], 1), de(d["top"], 1), de(d["top"] - d["z_b"], 1), de(V.BLATT_T, 1))
    fig = ('<figure class="fig"><div class="figbox s460">%s</div><figcaption>Schnitt durch die Mitte (Maße in mm, Platte gestrichelt). Die LED blickt nach links (grüner Pfeil).</figcaption></figure>' % svg_section(var))
    return ('<section class="sec"><h2>%s</h2><div class="two"><div style="display:flex;flex-direction:column;gap:10px">%s</div>%s</div></section>' % (title, txt, fig))


def sec_images():
    return ('<section class="sec"><h2>Bilder der Konzepte</h2><figure class="fig"><img alt="V1 und V2: Schrägansicht oben, Schnitt unten" src="%s">'
            '<figcaption>Links V1 (Streifen quer), rechts V2 (Streifen hochkant); gleicher Maßstab. Oben schräg, unten im Schnitt durch die Mitte. Orange: Kassette, weiß: Buchse, gelb: Streifen mit Chip, rot: Adern.</figcaption></figure></section>'
            % BP.img_uri("varianten_v1_v2.png", 1000))


def sec_compare():
    o = V.outlines()
    d = {k: V.dims(k) for k in ("V1", "V2", "V2R")}
    rows = [("Grundfläche außen", *["%s × %s" % (de(o[k]["w"], 1), de(o[k]["d"], 1)) for k in KEYS]),
            ("Höhe der Kassette", *[de(o[k]["h"], 1) if k != "v4" else de(V.base()["z_b"] + P.PODEST_T, 1) for k in KEYS]),
            ("Mindesthöhe Gebäude", *[de(need_height(k), 1) for k in KEYS]),
            ("LED-Mitte über der Platte", de(V.base()["z_b"] + P.PODEST_T - F, 1), *[de(d[k]["z0"] + d[k]["sh"] / 2 - F, 1) for k in ("V1", "V2", "V2R")]),
            ("LEDs", "1, nach oben", "1, nach vorn", "1, nach vorn", "2, vorn und hinten"),
            ("Adernweg", "flach über Rundung", "seitlich, verdrillt", "gerade nach oben", "gerade nach oben, Verkettung über die Blattkante"),
            ("Überhänge im Druck", "keine", "keine", "keine; Blatt frei stehend", "45°-Versatz des Blatts; Blatt frei stehend"),
            ("Geeignet für (1:1500)", *[", ".join(NAMES[n] for n in NAMES if combined(FIT["1zu1500/" + n], k).startswith("✓")) or "–" for k in KEYS])]
    trs = "".join('<tr><td><b>%s</b></td>%s</tr>' % (r[0], "".join('<td class="n">%s</td>' % c for c in r[1:])) for r in rows)
    return ('<section class="sec"><h2>Vergleich</h2><div class="tw"><table class="t"><thead><tr><th></th>%s</tr></thead><tbody>%s</tbody></table></div>'
            '<p class="note">„Geeignet für“ folgt der Tabelle oben (Grundriss und Höhe zusammen, 1:1500). Bei 1:1000 geht V2 zusätzlich in Neues Augusteum und Paulinum (Institutsgebäude knapp nicht).</p></section>'
            % ("".join("<th>%s</th>" % LABEL[k] for k in KEYS), trs))


def sec_chain():
    d1, d2 = V.dims("V1"), V.dims("V2")
    b = V.base()
    rows = [("Buchse bündig mit der Fußunterkante", "z = 0", "wie v4 (Tisch-Methode)"),
            ("Taschenoberkante", "z = %s" % de(b["zp"]), "Buchse etwa %s, Luft 0,05" % de(BUCHSE)),
            ("Schulterfläche = Unterbau", "z = %s" % de(b["z_b"]), "0,5 Schulter"),
            ("Plattenoberseite (Fuß)", "z = %s" % de(F), "liegt im Unterbau, LED darüber"),
            ("V1: Streifen von … bis", "%s … %s" % (de(d1["z0"]), de(d1["z0"] + d1["sh"])), "Luft für Adern %s" % de(d1["room"], 1)),
            ("V1: Blattoberkante", "z = %s" % de(d1["top"]), "Schacht 0,3 darüber; Dach 1,2 darüber → Gebäude mindestens %s hoch" % de(need_height("V1"), 1)),
            ("V2: Streifen von … bis", "%s … %s" % (de(d2["z0"]), de(d2["z0"] + d2["sh"])), "Luft für Adern %s" % de(d2["room"], 1)),
            ("V2: Blattoberkante", "z = %s" % de(d2["top"]), "Gebäude mindestens %s hoch" % de(need_height("V2"), 1))]
    trs = "".join('<tr><td>%s</td><td class="n">%s</td><td>%s</td></tr>' % r for r in rows)
    return ('<section class="sec"><h2>Maßkette in z (gesteckt)</h2><div class="tw"><table class="t"><thead><tr><th>Größe</th><th>Wert</th><th>Bemerkung</th></tr></thead><tbody>%s</tbody></table></div>'
            '<p class="note">Der Streifen hängt nicht von der Einstecktiefe ab. E bleibt wie bei v4 5,28 (Worst-Case 5,23); die Kette der Pins ändert sich nicht, weil der Unterbau gleich ist. '
            'Anschlag nach oben: eine Leiste im Schacht über dem Unterbau, vorn etwa 1,7 mm tief; Blatt und Streifen laufen durch einen Durchlass dahinter (y ab 1,8). Der Chip ragt bis y = %s vor.</p></section>'
            % (trs, de(d1["y_face"], 2)))


def sec_risks():
    risks = [("Adernweg V1.", "Seitlicher Weg unter dem Streifen und Verdrillen zu den Pads ist nicht belegt. Wenn er knickt oder nicht lötbar ist, entfällt V1 oder die Pads wandern: dann Streifen um 180° drehen (Pad-Ende links/rechts), oder V2 auch für das Seminargebäude prüfen (zu hoch)."),
             ("Blatt dünn und hoch (L06).", "V2: 1,2 × 13 mm Querschnitt, 17 mm frei, Biegung quer zu den Schichten. Beim Kleben und Einpressen darf es nicht abbrechen. Vorschlag: 1,6 dick mit Hohlkehle am Fuß; im Test ein Blatt mit 1,2 und eins mit 1,6."),
             ("Seitlicher Lichtfleck.", "Die LED blickt nach vorn auf die Wand des Gebäudes; im schmalen Seminargebäude sind es nur wenige Millimeter bis dahin (Hotspot). Lichtkammer oberhalb des Fußes so groß wie möglich, Wand am Fenster 0,4. Erst am echten Gebäude zu beurteilen."),
             ("Seminargebäude 1:1500.", "Dach nur etwa 16,4 mm hoch und höchstens etwa 14 mm breit: V1 braucht %s Höhe, V2 %s, v4 passt nicht in den Grundriss. Eine flache Variante (Streifen neben der Buchse, Grundfläche etwa 31 × 10,5, Höhe 8,1) käme gerade auf 1,0 mm Wand. Offen, siehe Karte." % (de(need_height("V1"), 1), de(need_height("V2"), 1))),
             ("Streifendicke.", "Die 2,2 mm des Streifens (Folie 0,3 plus Chip) sind nicht belegt; bei der Rücken-LED zählt sie doppelt. Vor der STL am echten Streifen messen (Schieblehre: Folie, Chip)."),
             ("Streifen kleben.", "Das Klebeband des Streifens haftet auf PLA, aber nicht nachgemessen; eine Lage Kreppband als Rückfall."),
             ("12-mm-Streifen.", "Bei V1 würde der Streifen 12 hoch (Blatt 2 mm höher), bei V2 12,5 breit: passt gerade auf 12,96. Im Standard bleibt es bei 10 mm.")]
    return '<section class="sec"><h2>Risiken</h2>%s</section>' % "".join('<p class="risk"><b>%s</b> %s</p>' % r for r in risks)


def sec_test():
    return ('<section class="sec"><h2>Vorschlag für den Probedruck</h2><ul class="q">'
            '<li><b>Kassetten:</b> V2 einseitig ×2 (Blatt 1,2 und 1,6) und V2R ×1 (zwei Streifen). Kennzeichnung mit Kerben (2 = V2, 3 = V2R).</li>'
            '<li><b>Mini-Gebäude:</b> hoher Mini-Turm auf dem bisherigen L-Fuß (24 × 38), damit er in die vorhandene Mulde der Mini-Grundplatte B passt; Schacht für den jeweiligen Unterbau (5,34 bzw. 6,4 tief), darüber Lichtkammer mit Dach.</li>'
            '<li><b>Geprüft wird:</b> Einpressen mit Blatt und Streifen (geht der Rücken-Streifen mit durch?), Kleben, Adernweg, Verkettung, Licht, Abziehen. Dock und Pins bleiben wie in Steckprobe 2.</li>'
            '<li><b>Vorher messen:</b> Dicke des Streifens (Folie und Chip), Länge des Stücks, Lage der Pads.</li></ul></section>')


DECISIONS = [
    dict(id="R", tag="Rücken-LED", title="Wie kommt die zweite LED auf den Rücken?", rec="A", text="Der Rücken-Streifen muss von unten durch den Schacht (Chip zu Chip %s mm)." % de(V.BLATT_T + 2 * V.STRIP_T, 1),
         opts=[("A", "Blatt in der Mitte, oben 45° nach vorn versetzt (Dein Vorschlag), Unterbau %s tief" % de(V.R_DEPTH, 1)),
               ("B", "Blatt bleibt hinten, Unterbau wird %s tief (einfach, aber 1,4 mm mehr Grundfläche, kein Versatz)" % de(V.dims("V2")["y1"] + V.BLATT_T + V.STRIP_T + 0.4, 1)),
               ("C", "Blatt nur 0,8 dick, Unterbau bleibt 5,34 (Luft nur 0,26, Blatt zu dünn, nicht empfohlen)"),
               ("D", "keine zweite LED")]),
    dict(id="K", tag="Verkettung", title="Wie wird der zweite Streifen gespeist?", rec="A", text="Der WS2812B-Streifen hat an beiden Enden Pads.",
         opts=[("A", "Verkettung: DOUT des vorderen Streifens über die Blattkante zu DIN des hinteren (um 180° gedreht), nur ein Satz Adern"),
               ("B", "Fenster im Blatt statt über die Kante (Blatt %s niedriger, aber am Fenster schwächer)" % de(V.R_JUMP, 1)),
               ("C", "zweiter Satz Adern aus dem Schlitz, am Blattrand vorbei (mehr Platz im Schacht nötig)")]),
    dict(id="A", tag="Varianten", title="Welche Kassetten gibt es?", rec="A", text="V2 passt nur in hohe Gebäude; v4 und V1 decken niedrige ab.",
         opts=[("A", "V2 (einseitig oder mit Rücken-LED) für Hochhaus und Paulinum; v4 für Hörsaalgebäude; V1 entfällt; Seminar und Institut folgen mit einer flachen Variante"),
               ("B", "V2 und V1 beide behalten"),
               ("C", "nur V2, niedrige Gebäude bekommen vorerst keine LED")]),
    dict(id="W", tag="Seminargebäude", title="Seminargebäude bei 1:1500", rec="A", text="Dach nur etwa 16,4 mm, Breite etwa 14 mm: weder v4 noch V1 noch V2 passen.",
         opts=[("A", "flache Variante V3: Streifen flach neben der Buchse (etwa 31 × 10,5, Höhe 8,1), später planen"),
               ("B", "Seminargebäude nur bei 1:1000 mit LED (dort passt v4)"),
               ("C", "Dach des Seminargebäudes im Modell höher machen (nicht empfohlen, Maßstab)")]),
    dict(id="T", tag="Blatt", title="Dicke des Blatts", rec="B", text="Das Blatt steht frei und ist quer zu den Schichten schwach (L06); bei zwei Streifen verschärft.",
         opts=[("A", "1,2 mm (drei Wände)"), ("B", "1,6 mm (vier Wände) mit Hohlkehle R 1 am Fuß"), ("C", "1,6 mm und zwei Rippen links und rechts (45°)")]),
    dict(id="H", tag="LED-Höhe", title="Höhe der LED im Hochhaus", rec="A", text="Im Hochhaus (96 mm) liegt die LED mit dem Standardmast tief (LED-Mitte etwa 15 mm über der Platte).",
         opts=[("A", "Streifen direkt über dem Unterbau, für den Probedruck"), ("B", "Mast verlängerbar (Parameter), später für das echte Hochhaus"),
               ("C", "gleich einen längeren Mast drucken (LED-Mitte etwa 25 über der Platte)")]),
    dict(id="S", tag="Streifen", title="Streifenlänge", rec="A", text="Der 144-LED/m-Streifen ist kürzer (13,9), aber 12 breit.",
         opts=[("A", "60 LED/m, 10 breit, 16,7 lang"), ("B", "144 LED/m, 12 breit, 13,9 lang: 2,8 mm niedriger, Blatt 12,5 breit (passt auf 12,96)")]),
    dict(id="P", tag="Probe", title="Probedruck", rec="A", text="Siehe „Vorschlag für den Probedruck“.",
         opts=[("A", "V2 einseitig (Blatt 1,2 und 1,6) und V2R plus Mini-Turm auf dem bisherigen L-Fuß"), ("B", "nur die Kassetten, ohne Gebäude (Einpressen nicht prüfbar)"),
               ("C", "erst Steckprobe 2 drucken, danach diesen Probedruck")]),
]


def main():
    sections = "".join([sec_height(), sec_rueck(), sec_befund(), sec_verstanden(), sec_base(), sec_images(), sec_var("V2"), sec_var("V1"), sec_compare(), sec_chain(), sec_risks(), sec_test()])
    sections += '<section class="top"><h2>Entscheidungen</h2><p class="lead">Mit den Empfehlungen ist der Plan rund. Danach erzeuge ich die STL.</p></section>'
    sections += "\n".join(decision_card(x) for x in DECISIONS)
    spec = [dict(id=x["id"], tag=x["tag"], title=x["title"]) for x in DECISIONS]
    with open(TEMPLATE, encoding="utf-8") as f:
        page = f.read()
    page = (page.replace("<title>Planung Testfall Kassette</title>", "<title>Kassette V2</title>")
                .replace("testfall-plan-v1", "varianten-plan-v2").replace("PLANUNG TESTFALL KASSETTE · ANTWORT", "KASSETTE V2 · ANTWORT"))
    page = page.replace("</style>", ".three{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(200px,1fr))}"
                        ".three .figbox svg{max-width:300px}</style>", 1)
    for k, v in {"{{HEAD}}": head(), "{{SECTIONS}}": sections, "{{SPEC}}": json.dumps(spec, ensure_ascii=False)}.items():
        page = page.replace(k, v)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(page)
    print("geschrieben: %s (%d kB)" % (os.path.relpath(OUT, ROOT), os.path.getsize(OUT) / 1024))


if __name__ == "__main__":
    main()
