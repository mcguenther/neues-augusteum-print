#!/usr/bin/env python3
"""Planungsseite für den kompletten Testfall (Kassette v4, Mini-Gebäude, Mini-Grundplatte): baut plug/testcase/plan.html aus plan.template.html.

Alle Maße kommen aus plug/testcase/params.py (und damit aus plug/dupont.py, plug/series2.py). Die Zeichnungen sind Schemazeichnungen der
geplanten Teile, noch keine Ausgabe der STL-Geometrie.

Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m plug.testcase.build_plan      # schreibt plug/testcase/plan.html
"""
import base64
import io
import json
import math
import os

import shapely
from PIL import Image

from plug import dupont as sd
from plug import institute as I
from plug import series2 as N2
from plug.feedback.build import G
from plug.testcase import kassette as KA
from plug.testcase import params as P

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TEMPLATE = os.path.join(HERE, "plan.template.html")
OUT = os.path.join(HERE, "plan.html")
PREV = os.path.join(ROOT, "vorschau", "steckmodul_testcase")

LOETRAUM_Y0 = -12.0     # Kabelraum und Lötenden-Schlitz reichen so weit nach −y (kein Wand-Ende direkt hinter den Spitzen)
KABEL_Y1 = 9.0          # Kabelraum nach +y
LID_WIN = (-12.0, -4.0)  # Fenster im Deckel über den Lötenden


def de(x, n=2):
    return ("%.*f" % (n, x)).replace(".", ",")


def img_uri(name, width):
    im = Image.open(os.path.join(PREV, name)).convert("RGB")
    im = im.resize((width, int(im.size[1] * width / im.size[0])), Image.LANCZOS)
    b = io.BytesIO()
    im.save(b, "JPEG", quality=86, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()


# --------------------------------------------------------------------------
# Zeichnung 1: Zusammenbau im Schnitt (längs y durch die Pin-Reihe), Regler setzt das Gebäude auf
# --------------------------------------------------------------------------
def svg_section():
    d, k = P.dims(), P.kass_dims()
    S = 9.0
    LIFT = 9.0
    oy = (d["box_top"] + LIFT) * S + 22
    g = G(S, 138, oy)
    F, zhb, zbb, zlt = d["F"], d["z_hb"], d["z_bb"], d["z_lt"]
    yc = d["yc"]
    fy0, fy1 = yc - P.BOX_L / 2, yc + P.BOX_L / 2
    ph0, ph1 = fy0 - P.PLATE_MARGIN, fy1 + P.PLATE_MARGIN
    clr, rel = P.MULDE_CLR_T, sd.RELIEF
    yb, ytail, hd = d["yb"], d["y_tail"], sd.HDR_T / 2 + sd.SNUG_HDR
    # --- Grundplatte
    g.rect(ph0, ph1, zlt, 0.0, "d-slab")
    cp, bd = sd.CH_P, sd.BAND
    mulde = [(fy0 - clr - rel, -F), (fy1 + clr + rel, -F), (fy1 + clr + rel, -cp - bd), (fy1 + clr, -cp - bd), (fy1 + clr, -cp),
             (fy1 + clr + cp, 0.01), (fy0 - clr - cp, 0.01), (fy0 - clr, -cp), (fy0 - clr, -cp - bd), (fy0 - clr - rel, -cp - bd)]
    g.poly(mulde, "d-void")
    g.rect(yb - hd - P.BODY_EXT_T, yb + hd, zbb, zhb, "d-void")                         # Körpertasche (+1,5 zum Lötende)
    g.rect(yb, sd.HDR_T * 0 + 0.32 + 0.8, zbb, zhb, "d-void")                          # Schacht für Knick und Pin
    g.rect(LOETRAUM_Y0, yb - hd - P.BODY_EXT_T + 0.01, zbb, d["step"], "d-void")       # Lötendenschlitz, nach hinten offen
    g.rect(LOETRAUM_Y0, KABEL_Y1, zlt, zbb, "d-void")                                  # Kabelraum
    g.rect(-sd.HOLE / 2, sd.HOLE / 2, zhb, -F + 0.01, "d-void")                         # Stiftloch im Muldenboden
    # --- Deckel mit Fenster und Stempel
    g.rect(ph0, ph1, zlt - P.LID_T_T, zlt, "d-lid")
    g.rect(LID_WIN[0], LID_WIN[1], zlt - P.LID_T_T - 0.01, zlt + 0.01, "d-void")
    g.rect(yb - 0.6, yb + 0.6, zlt, zbb, "d-lid")
    # --- Winkelleiste
    g.rect(yb - sd.HDR_T / 2, yb + sd.HDR_T / 2, zbb, zhb, "d-body")
    g.rect(ytail, 0.32, d["z_bm"] - 0.32, d["z_bm"] + 0.32, "d-pin")
    g.o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" class="d-open"/>' % (
        g.X(ytail - 4.0), g.Z(d["z_bm"] + 1.3), 4.0 * S, 2.6 * S))                      # freier Raum hinter den Lötenden
    g.text(ytail - 2.0, d["z_bm"] - 1.9, "frei", "dln")
    # --- Gebäude, Kassette, Buchse, Adern, LED: bewegt
    g.group("T-mov", move=(0, LIFT, 0, 0))
    g.o[-1] = g.o[-1].replace('transform="translate(0.0,%.1f)"' % (-LIFT * S), 'transform="translate(0.0,0.0)"')
    ch = sd.CH_F
    ztop = d["box_top"]
    g.poly([(fy0 + ch, -F), (fy1 - ch, -F), (fy1, -F + ch), (fy1, ztop), (fy0, ztop), (fy0, -F + ch)], "d-bld")
    sy0, sy1 = d["y_kass0"] - P.KASS_CLR_T, d["y_kass1"] + P.KASS_CLR_T
    zk = -F + d["kass_h"]
    e = P.ENTRY_CH_T
    g.poly([(sy0 - e, -F - 0.01), (sy1 + e, -F - 0.01), (sy1, -F + e), (sy1, zk), (sy0, zk), (sy0, -F + e)], "d-void")
    g.rect(sy0 + N2.E_LIP, sy1 - N2.E_LIP, zk - 0.01, ztop + 0.01, "d-void")             # Fenster über der Kassette
    # Kassette v4 (Schnitt x = 0)
    y0k = d["y_kass0"]
    X = lambda yl: y0k + yl
    Z = lambda zl: -F + zl
    y1l, top, zp = k["y1"], k["top"], k["zp"]
    r = P.FILLET_T
    arc = [(y1l + r + r * math.cos(a), top - r + r * math.sin(a)) for a in [math.pi / 2 + j * math.pi / 2 / 12 for j in range(13)]]
    g.poly([(X(y1l), Z(0)), (X(k["L"]), Z(0)), (X(k["L"]), Z(top)), (X(y1l + r), Z(top))] + [(X(a), Z(b)) for a, b in arc[1:]] + [(X(y1l), Z(0))], "d-kass")
    g.rect(X(0), X(k["y_p0"]), Z(0), Z(top), "d-kass")
    g.poly([(X(k["y_p0"] - e), Z(-0.01)), (X(y1l + e), Z(-0.01)), (X(y1l), Z(e)), (X(y1l), Z(0)), (X(k["y_p0"]), Z(0)), (X(k["y_p0"]), Z(e))], "d-void")
    g.rect(X(k["y_p0"]), X(y1l), Z(zp - 0.01), Z(top + 0.01), "d-void")
    g.rect(-1.27, 1.27, -F, -F + sd.HSG_H, "d-hsg")                                      # Buchse, Steckseite bündig mit dem Fuß
    g.rect(-0.5, 0.5, -F + 0.5, -F + 5.5, "d-term")
    ya = X(k["seat0"] + N2.SEAT_TOL)
    g.rect(ya, ya + 16.7, Z(top), Z(top) + 0.3, "d-led")
    g.rect(ya + 6.0, ya + 11.0, Z(top) + 0.3, Z(top) + 1.5, "d-led")
    wp = KA.wire_points(k)
    g.o.append('<polyline points="%s" class="d-wire"/>' % " ".join("%.1f,%.1f" % (g.X(X(a)), g.Z(Z(b))) for a, b in wp))
    g.text(X(k["L"] / 2 + 2), Z(zp * 0.55), "Kassette v4", "dlb")
    g.text(X(k["L"] - 0.5), ztop + 1.1, "Podest %s mm über der Tasche" % de(N2.SEAT_RISE + P.PODEST_T, 1), "dls", "end")
    g.end()
    # Pins stehen in der Platte, ragen in die Buchse
    g.rect(-0.32, 0.32, d["z_bm"], d["z_tip"], "d-pin")
    # Maße
    g.line(3.2, -F, 3.2, d["z_tip"], "dimn")
    g.line(2.6, -F, 3.8, -F, "dimn")
    g.line(2.6, d["z_tip"], 3.8, d["z_tip"], "dimn")
    g.text(4.2, (-F + d["z_tip"]) / 2 - 0.3, "E = %s mm" % de(d["E"]), "dln", "start")
    xr = ph1 + 2.2

    def label(z_true, z_lab, txt, cls="dl"):
        g.line(ph1 + 0.1, z_true, xr - 0.3, z_lab, "dim")
        g.text(xr, z_lab - 0.3, txt, cls, "start")
    label(ztop - 0.6, ztop - 0.6, "Anschlagrand %s mm (Kammerboden)" % de(P.STOP_T, 1))
    label(-F + d["kass_h"] / 2, -F + d["kass_h"] / 2, "Kassette v4, %s mm hoch" % de(d["kass_h"], 2))
    label(-F + 0.3, -8.0, "Fußunterkante = Buchse bündig")
    label(-F - 0.2, -10.2, "Muldenboden %s mm" % de(P.CEIL_T, 1), "dlb")
    label(d["z_bm"], -12.4, "Winkelleiste, Körper 2,0")
    label(zlt + 1.0, -14.8, "Kabelraum, offen nach unten")
    label(zlt - 1.0, -18.0, "Mini-Deckel %s mm mit Fenster" % de(P.LID_T_T, 1))
    g.text(ph0, zlt - P.LID_T_T - 1.3, "Mini-Grundplatte, Mulde %s mm tief" % de(F, 1), "dlb", "start")
    return g.svg(720, int(oy + 20.6 * S), "Zusammenbau im Schnitt: Mini-Gebäude mit Kassette wird in die Mini-Grundplatte gesteckt")


# --------------------------------------------------------------------------
# Zeichnung 2: Draufsicht (x nach rechts, y nach oben)
# --------------------------------------------------------------------------
def poly_pts(g, poly):
    return " ".join("%.1f,%.1f" % (g.X(x), g.Z(y)) for x, y in poly.exterior.coords)


def svg_top():
    d, k = P.dims(), P.kass_dims()
    S = 9.0
    g = G(S, 201, 372)
    yc = d["yc"]
    pw, pl = P.plate_size()
    ph0, ph1 = yc - P.BOX_L / 2 - P.PLATE_MARGIN, yc + P.BOX_L / 2 + P.PLATE_MARGIN
    g.rect(-pw / 2, pw / 2, ph0, ph1, "d-slab")
    fp = shapely.Polygon([(x, y + yc) for x, y in P.footprint()])
    mouth = fp.buffer(P.MULDE_CLR_T + sd.CH_P, join_style=2)
    mulde = fp.buffer(P.MULDE_CLR_T + sd.RELIEF, join_style=2)
    g.o.append('<polygon points="%s" class="d-dash"/>' % poly_pts(g, mouth))
    g.o.append('<polygon points="%s" class="d-void"/>' % poly_pts(g, mulde))
    g.o.append('<polygon points="%s" class="d-bld"/>' % poly_pts(g, fp))
    # Kassette im Schacht
    x0, y0 = -k["cw"] / 2, d["y_kass0"]
    g.rect(x0 - P.KASS_CLR_T, x0 + k["cw"] + P.KASS_CLR_T, y0 - P.KASS_CLR_T, y0 + k["L"] + P.KASS_CLR_T, "d-void")
    g.rect(x0, x0 + k["cw"], y0, y0 + k["L"], "d-kass")
    g.rect(-N2.WIRE_W / 2, N2.WIRE_W / 2, y0 + k["y_p0"], y0 + k["y1"], "d-void")                  # Aderschlitz
    g.rect(-5.0, 5.0, y0 + k["seat0"] + N2.SEAT_TOL, y0 + k["seat0"] + N2.SEAT_TOL + 16.7, "d-led")   # LED-Streifen
    g.o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" class="d-dash"/>' % (
        g.X(-k["pk_w"] / 2), g.Z(y0 + k["y_p0"] + k["pk_d"]), k["pk_w"] * S, k["pk_d"] * S))      # Tasche darunter
    # Winkelleiste und Pins
    yb, ytail, hd = d["yb"], d["y_tail"], sd.HDR_T / 2 + sd.SNUG_HDR
    hw = sd.HDR_W / 2 + sd.SNUG_HDR
    px = abs(sd.pin_x()[0]) + sd.PIN_SQ / 2 + 0.8
    g.o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" class="d-dash"/>' % (
        g.X(-hw), g.Z(yb + hd), 2 * hw * S, (2 * hd + P.BODY_EXT_T) * S * 1.0))                    # Körpertasche (nach unten +1,5 verlängert)
    g.o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" class="d-open"/>' % (
        g.X(-px), g.Z(yb - hd - P.BODY_EXT_T + 0.01), 2 * px * S, (LOETRAUM_Y0 * -1 + (yb - hd - P.BODY_EXT_T)) * S))   # offen nach −y
    g.rect(-sd.HDR_W / 2, sd.HDR_W / 2, yb - sd.HDR_T / 2, yb + sd.HDR_T / 2, "d-body")
    for x in sd.pin_x():
        g.rect(x - 0.32, x + 0.32, ytail, 0.32, "d-pin")
        g.o.append('<circle cx="%.1f" cy="%.1f" r="%.1f" class="d-pin"/>' % (g.X(x), g.Z(0.0), 0.5 * S * 0.9))
    # Kabelraum, Schrauben
    g.o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" class="d-dash"/>' % (g.X(-9.0), g.Z(KABEL_Y1), 18.0 * S, (KABEL_Y1 - LOETRAUM_Y0) * S))
    for sx in (-1, 1):
        for sy in (ph0 + 3.0, ph1 - 3.0):
            g.o.append('<circle cx="%.1f" cy="%.1f" r="%.1f" class="d-screw"/>' % (g.X(sx * (pw / 2 - 2.8)), g.Z(sy), 1.6 * S * 0.5))
    # Beschriftung
    xr = pw / 2 + 1.0
    g.text(xr, ph1 - 1.0, "Mini-Grundplatte", "dlb", "start")
    g.text(xr, ph1 - 2.6, "%s × %s mm" % (de(pw, 0), de(pl, 0)), "dls", "start")
    g.text(xr, d["yc"] + 17.0, "Mulde, L-Form, Spiel %s" % de(P.MULDE_CLR_T), "dl", "start")
    g.text(xr, y0 + k["L"] - 4.0, "LED-Streifen auf dem Podest", "dl", "start")
    g.text(xr, y0 + 4.5, "Aderschlitz und Tasche", "dl", "start")
    g.text(xr, 0.0, "Pin-Reihe, 4 Pins", "dl", "start")
    g.text(xr, yb - 0.5, "Winkelleiste", "dl", "start")
    g.text(xr, -8.0, "Lötenden frei, Kabelraum", "dln", "start")
    g.text(xr, -11.0, "Deckel mit Fenster", "dls", "start")
    g.text(-pw / 2, ph0 - 1.0, "Pin-Seite, Lötenden zeigen nach unten", "dls", "start")
    g.text(-pw / 2, ph1 + 0.8, "LED-Ende", "dls", "start")
    return g.svg(580, 532, "Draufsicht: Mini-Grundplatte mit L-förmiger Mulde, Kassette, Winkelleiste und freier Lötseite")


# --------------------------------------------------------------------------
# Zeichnung 3: Einstecktiefe E (Messung und Testfall)
# --------------------------------------------------------------------------
def svg_stack():
    W, ox, sx = 520, 190, 62.0
    rows = [("Nacht 2, gemessen", 0.4, "ok", "stabil"), ("Nacht 2, gemessen", 0.6, "ok", "stabil"), ("Nacht 2, gemessen", 0.8, "bad", "Aussetzer"),
            ("Nacht 2, gemessen", 1.0, "bad", "Aussetzer"), ("Aufbau bisher", 1.8, "old", "Schieber + Muldenboden 0,8 + 1,0"),
            ("Testfall", P.CEIL_T, "new", "nur Muldenboden")]
    y0, rh = 40, 26
    H = y0 + rh * len(rows) + 46
    o = []
    for kk in range(0, 7):
        x = ox + kk * sx
        o.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" class="grid"/>' % (x, y0 - 12, x, y0 + rh * len(rows) - 6))
        o.append('<text x="%.1f" y="%d" class="tick" text-anchor="middle">%d</text>' % (x, y0 + rh * len(rows) + 10, kk))
    o.append('<text x="%.1f" y="%d" class="dls" text-anchor="middle">Einstecktiefe E in mm (Pin steckt so tief in der Buchse)</text>' % (ox + 3 * sx, y0 + rh * len(rows) + 30))
    o.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" class="mark"/>' % (ox + sd.HDR_UP * sx, y0 - 12, ox + sd.HDR_UP * sx, y0 + rh * len(rows) - 6))
    o.append('<text x="%.1f" y="%d" class="dls" text-anchor="end">Pin ganz: %s</text>' % (ox + sd.HDR_UP * sx - 4, y0 - 18, de(sd.HDR_UP)))
    last = None
    for i, (grp, t, kind, note) in enumerate(rows):
        y = y0 + i * rh
        e = sd.HDR_UP - t
        if grp != last:
            o.append('<text x="8" y="%d" class="dlb">%s</text>' % (y + 12, grp))
            last = grp
        o.append('<text x="%d" y="%d" class="dl" text-anchor="end">t %s</text>' % (ox - 8, y + 12, de(t, 1)))
        o.append('<rect x="%.1f" y="%d" width="%.1f" height="%d" rx="3" class="bar-%s"/>' % (ox, y, e * sx, rh - 8, kind))
        o.append('<text x="%.1f" y="%d" class="dl">E %s · %s</text>' % (ox + e * sx + 6, y + 12, de(e), note))
    return '<svg viewBox="0 0 %d %d" role="img" aria-label="Einstecktiefe, Messung und Testfall" class="dsvg">%s</svg>' % (W + 160, H, "".join(o))


# --------------------------------------------------------------------------
# Inhalt
# --------------------------------------------------------------------------
def est_weights():
    d = P.dims()
    k = P.kass_dims()
    fp = shapely.Polygon(P.footprint())
    area = fp.area
    pw, pl = P.plate_size()
    g_k = 3.9
    v_bld = (area * d["box_h"] - (k["cw"] + 2 * P.KASS_CLR_T) * (k["L"] + 2 * P.KASS_CLR_T) * d["kass_h"]) / 1000.0
    g_b = v_bld * 1.24 * 0.75
    mulde = (area + fp.length * 0.4) * d["F"] / 1000.0
    v_p = (pw * pl * d["plate_t"]) / 1000.0 - mulde - 18 * 21 * 3.6 / 1000.0
    g_p = v_p * 1.24 * 0.55
    g_l = pw * pl * P.LID_T_T / 1000.0 * 1.24 * 0.9
    return dict(kass=g_k, bld=g_b, plate=g_p, lid=g_l, total=2 * g_k + 2 * g_b + g_p + g_l)


def head():
    d = P.dims()
    return ('<header class="top"><p class="kicker">Steckmechanismus · nach Nachtdruck 2</p><h1>Testfall Kassette</h1>'
            '<p class="lead">Ein kompletter Aufbau in einem Druck: Kassette v4, ein Mini-Gebäude, das sie aufnimmt, und eine Mini-Grundplatte mit Winkelleiste. '
            'Damit wird zusammen geprüft, was einzeln schon passt: Einpressen, Mulde, Pin-Treffer ohne Trichter, Durchgang, Abziehen. '
            'Probestück und Institutsgebäude bleiben vorerst unverändert; die neuen Werte stehen in <code>plug/testcase/params.py</code>.</p>'
            '<ul class="sum"><li><b>Kein Schieber, kein Trichterboden.</b> Die Pins gehen vom Muldenboden (%s mm) direkt in die Buchse: E = %s mm statt 3,88.</li>'
            '<li><b>Kassette eingepresst</b> (Spiel %s), Anschlag oben am Kammerboden, er kostet keine Pin-Länge.</li>'
            '<li><b>Lötseite frei:</b> hinter den Lötenden steht keine Wand, der Kabelraum ist offen.</li></ul></header>'
            % (de(P.CEIL_T, 1), de(d["E"]), de(P.KASS_CLR_T)))


def sec_questions():
    return ('<section class="sec"><h2>Was der Testfall klärt</h2><ul class="q">'
            '<li>Hält die eingepresste Kassette im Mini-Gebäude, wenn der Schacht wie im echten Gebäude am Druckbett öffnet?</li>'
            '<li>Passt das Mini-Gebäude mit L-förmigem Fuß in die Mulde (Spiel %s) und findet es nur in einer Lage hinein?</li>'
            '<li>Treffen die Pins die Buchse, obwohl kein Trichter mehr führt?</li>'
            '<li>Bleibt die Buchse in der Kassette, wenn das Gebäude abgezogen wird, und bleibt der Durchgang bei E = %s mm stabil?</li>'
            '<li>Laufen die Adern über das Podest ohne Knick, liegt der LED-Streifen flach?</li>'
            '<li>Ist an der Lötseite Platz genug, um Kabel an die Lötenden zu bringen?</li></ul></section>' % (de(P.MULDE_CLR_T), de(P.dims()["E"])))


def sec_assembly():
    d = P.dims()
    fig = ('<figure class="fig mv"><div class="figbox s700">%s</div><div class="dgctl"><label class="rng">Gebäude aufstecken '
           '<input type="range" class="dgr" min="0" max="100" value="100" data-for="T-mov" aria-label="Gebäude aufstecken"></label>'
           '<button type="button" class="play">Abspielen</button></div>'
           '<figcaption>Schnitt längs durch die Pin-Reihe. Schema der geplanten Teile mit den Maßen aus params.py; Regler zieht das Gebäude ab.</figcaption></figure>' % svg_section())
    return ('<section class="sec"><h2>Aufbau im Schnitt</h2>%s'
            '<p class="note">Die Buchse liegt bündig an der Fußunterkante, die Pins gehen durch den %s mm dicken Muldenboden und %s mm tief in die Buchse. '
            'Der Anschlagrand oben ist der Tiefenanschlag der Kassette; er liegt auf der anderen Seite der Buchse und nimmt keine Pin-Länge weg. '
            'Hinter den Lötenden (links) stehen keine Wand und keine Stufe, der Raum ist zum Kabelraum offen.</p></section>' % (fig, de(P.CEIL_T, 1), de(d["E"])))


def sec_top():
    fig = '<figure class="fig"><div class="figbox s560">%s</div><figcaption>Draufsicht von der Gebäudeseite. Gestrichelt: Mulden-Fase, Tasche der Buchse, Körpertasche der Winkelleiste und Kabelraum darunter.</figcaption></figure>' % svg_top()
    fp = P.footprint()
    return ('<section class="sec"><h2>Draufsicht</h2><div class="two">%s<div style="display:flex;flex-direction:column;gap:10px">'
            '<h3>Grundriss</h3><p class="note">Das Mini-Gebäude folgt einem Grundriss ohne Kodierecke: %s × %s mm mit einem Ausschnitt von %s × %s mm an einer Ecke. '
            'Die konkave Ecke zeigt wie bei echten Gebäuden, ob Mulde und Fuß in den Ecken klemmen, und der Fuß passt nur in einer Lage.</p>'
            '<h3>Lötseite</h3><p class="note">Der Schlitz für die Lötenden ist nicht mehr 0,9 mm hinter der Spitze zu Ende. Er läuft %s mm weiter nach hinten in den Kabelraum, '
            'der nach unten offen ist; der Deckel hat dort ein Fenster. So können die Kabel gerade aus dem Lötende heraus und nach unten wegführen.</p>'
            '<h3>Stufe</h3><p class="note">Das Lötende liegt unter einer Stufe, ausgelegt für Körperhöhe %s (2,0 und 1,8 lagen in der Passprobe flach, 1,6 nicht). '
            'Die Körpertasche ist %s mm länger zum Lötende hin.</p></div></div></section>'
            % (fig, de(P.BOX_W, 0), de(P.BOX_L, 0), de(P.NOTCH_W, 1), de(P.NOTCH_L, 0), de(abs(LOETRAUM_Y0 - P.dims()["y_tail"]), 1),
               de(P.STEP_H_T, 1), de(P.BODY_EXT_T, 1)))


def sec_parts():
    d, k, w = P.dims(), P.kass_dims(), est_weights()
    pw, pl = P.plate_size()
    rows = [
        ("Kassette v4", "2 ×", "%s × %s × %s" % (de(k["cw"], 1), de(k["L"], 1), de(k["top"], 2)),
         "Tasche %s × %s × %s, unten offen, Podest, Rundung R %s, flache LED-Fläche; eine bestücken, eine als Reserve" % (de(k["pk_w"]), de(k["pk_d"]), de(k["zp"]), de(P.FILLET_T, 1)),
         "Tasche unten auf dem Bett", "%s g je" % de(w["kass"], 0)),
        ("Mini-Gebäude A", "1 ×", "%s × %s × %s" % (de(P.BOX_W, 0), de(P.BOX_L, 0), de(d["box_h"], 2)),
         "L-Fuß (%s mm hoch, Fase 0,8), Schacht %s durchgehend, Einführfase %s, Fenster und Anschlagrand oben" % (de(d["F"], 1), de(P.KASS_CLR_T), de(P.ENTRY_CH_T, 1)),
         "Fuß am Bett, Schacht öffnet zum Bett", "%s g" % de(w["bld"], 0)),
        ("Mini-Gebäude B", "1 ×", "wie A", "Schacht nur die ersten %s mm mit %s, dahinter %s Luft (Einpresskraft bei 17 mm Tiefe)" % (de(P.KASS_FIT_LEN, 0), de(P.KASS_CLR_T), de(P.KASS_RELIEF)),
         "wie A", "%s g" % de(w["bld"], 0)),
        ("Mini-Grundplatte", "1 ×", "%s × %s × %s" % (de(pw, 0), de(pl, 0), de(d["plate_t"], 1)),
         "L-Mulde %s tief mit Fase 1,0, Muldenboden %s mit 4 Stiftlöchern, Dock A (Körpertasche +%s, Stufe für %s), Kabelraum offen, 4 Schraublöcher" % (
             de(d["F"], 1), de(P.CEIL_T, 1), de(P.BODY_EXT_T, 1), de(P.STEP_H_T, 1)),
         "Mulde oben, Unterseite am Bett (Muldenboden als Brücke)", "%s g" % de(w["plate"], 0)),
        ("Mini-Deckel", "1 ×", "%s × %s × %s" % (de(pw, 0), de(pl, 0), de(P.LID_T_T, 1)),
         "Stempel gegen den Steckdruck, Fenster über den Lötenden, 4 Schrauben M3", "flach", "%s g" % de(w["lid"], 0)),
    ]
    trs = "".join("<tr><td><b>%s</b></td><td class=\"n\">%s</td><td class=\"n\">%s</td><td>%s</td><td>%s</td><td class=\"n\">%s</td></tr>" % r for r in rows)
    buy = ("Kaufteile: Winkelleiste (4 Pins), Dupont-Buchse mit gecrimpten Adern, LED-Streifen 10 mm, 4 Schrauben M3. "
           "Für den Lichttest zusätzlich ein Controller an den Lötenden.")
    return ('<section class="sec"><h2>Bauteile</h2><div class="tw"><table class="t"><thead><tr><th>Teil</th><th>Anzahl</th><th>Maße in mm</th><th>Inhalt</th><th>Druck</th><th>Material</th></tr></thead><tbody>%s</tbody></table></div>'
            '<p class="note">%s Gesamt etwa %s g, bei deinem Drucker (47 g in 2,5 h) rund %s Stunden. Schätzung aus Volumen und Füllfaktor, genaue Werte nach dem Erzeugen.</p></section>'
            % (trs, buy, de(w["total"], 0), de(w["total"] / 47.0 * 2.5, 1)))


def sec_changes():
    d = P.dims()
    old = sd.dims()
    rows = [
        ("Muldenboden CEIL", "0,8", de(P.CEIL_T, 1), "K: Durchgang stabil bei t 0,4 und 0,6, bei 0,8 Aussetzer"),
        ("Trichterplatte / Schieber", "1,0", "entfällt", "nimmt Pin-Länge weg; Schacht ohne Nut, keine 34-mm-Brücke"),
        ("Einstecktiefe E", de(old["E"]), de(d["E"]), "folgt aus den beiden Zeilen oben"),
        ("Fußhöhe F (Mulde)", de(old["F"], 1), de(d["F"], 1), "folgt aus E (Pin-Spitze erreicht den Fuß später)"),
        ("Kassette im Schacht KASS_CLR", "0,20", de(P.KASS_CLR_T), "E: 0,06 geht gut hinein und sitzt fest (eingepresst)"),
        ("Fuß in der Mulde CLR", "0,25", de(P.MULDE_CLR_T), "FM: 0,10 und 0,15 gut, 0,20 wackelt"),
        ("Buchsentasche SNUG", "0,22", de(N2.SNUG2), "R und C: 0,20 passt"),
        ("Crush-Rippen RIB", "0,12", "keine", "R: ohne Rippen ideal"),
        ("Taschenhöhe HSG_TOL", "0,25", de(N2.HSG_TOL2), "C: Buchse geht ganz hinein"),
        ("Podest über Taschenoberkante", "−1,05", "+%s" % de(N2.SEAT_RISE + P.PODEST_T, 1), "C: Adern knicken stark"),
        ("Rundung zur Tasche", "–", "R %s" % de(P.FILLET_T, 1), "Adern laufen im Bogen"),
        ("Stufe für Körperhöhe", "2,0", de(P.STEP_H_T, 1), "D: 2,0 und 1,8 liegen flach, 1,6 nicht"),
        ("Körpertasche zum Lötende", "+0", "+%s" % de(P.BODY_EXT_T, 1), "D: Körper liegt flach"),
        ("Fase an Bettkanten", "0,3", de(P.EF_CH_T, 1), "Druck: leichter Wulst blieb"),
        ("Einführfase an Öffnungen", "–", de(P.ENTRY_CH_T, 1), "Schachteingang am Bett gleicht zugleich den Elefantenfuß aus"),
        ("Federzunge", "ja", "vorerst nicht", "bei Spiel 0,10 vielleicht unnötig"),
    ]
    trs = "".join("<tr><td>%s</td><td class=\"n\">%s</td><td class=\"n\"><b>%s</b></td><td>%s</td></tr>" % r for r in rows)
    return ('<section class="sec"><h2>Änderungen gegenüber dem Stand heute</h2><div class="tw"><table class="t"><thead><tr><th>Größe</th><th>alt</th><th>Testfall</th><th>Grund</th></tr></thead><tbody>%s</tbody></table></div>'
            '<p class="note"><code>plug/parts.py</code> bleibt unverändert, bis Probestück und Institutsgebäude umgebaut werden; sie rechnen noch mit Schieber und Trichterplatte.</p></section>' % trs)


def sec_chain():
    d = P.dims()
    rows = [("Pin-Länge über dem Körper (HDR_UP)", de(sd.HDR_UP)), ("− Muldenboden", de(P.CEIL_T, 1)), ("= Einstecktiefe E", de(d["E"])),
            ("Fußhöhe F (Mulde)", de(d["F"], 1)), ("Kassette v4", de(d["kass_h"], 2)), ("+ Anschlagrand", de(P.STOP_T, 1)),
            ("= Mini-Gebäude gesamt (Fuß unten)", de(d["box_h"], 2)), ("Platte ohne Deckel", de(d["plate_t"], 1))]
    trs = "".join("<tr><td>%s</td><td class=\"n\">%s mm</td></tr>" % r for r in rows)
    return ('<section class="sec"><h2>Maßkette und Einstecktiefe</h2><div class="two"><div><div class="tw"><table class="t"><thead><tr><th>Größe</th><th>Wert</th></tr></thead><tbody>%s</tbody></table></div>'
            '<p class="note">Reserve: stabil gemessen bis E = %s (Plättchen 0,6). Der Testfall liegt mit E = %s zwei Zehntel darüber. '
            'Der kürzeste echte Pin ist noch nicht gemessen; ist er kürzer als der Nennwert %s, schrumpft die Reserve entsprechend.</p></div>'
            '<figure class="fig"><div class="figbox s560">%s</div><figcaption>Einstecktiefe je Aufbau; Farbe zeigt das Ergebnis aus Nacht 2.</figcaption></figure></div></section>'
            % (trs, de(sd.HDR_UP - 0.6), de(d["E"]), de(sd.HDR_UP), svg_stack()))


def sec_kassette():
    return ('<section class="sec"><h2>Kassette v4</h2><figure class="fig"><img src="{{IMG_KASSETTE}}" alt="Kassette v2 und v4, außen und im Schnitt mit Buchse und Ader" loading="lazy">'
            '<figcaption>Oben links v2, rechts v4. Unten Schnitt durch die Mitte: v2 mit 0,5 mm Absatz, v4 mit Podest %s mm über der Tasche. Rot: eine Ader auf dem berechneten Weg, '
            'senkrecht aus der Buchse und im Bogen über die gerundete Kante (Abstand zur Rundung %s mm).</figcaption></figure>'
            '<p class="note">Buchse (Nennmaß) in der Tasche: keine Überschneidung. Die Schultern liegen jetzt %s mm dick über der Buchse. Der Aderschlitz ist %s mm breit wie in v2.</p></section>'
            % (de(N2.SEAT_RISE + P.PODEST_T, 1), de(KA.wire_clearance(P.kass_dims()), 2), de(N2.SEAT_RISE + P.PODEST_T, 1), de(N2.WIRE_W, 1)))


def sec_risks():
    risks = [
        ("Pin-Treffer ohne Trichter.", "Eintritt der Buchse 1,0, Pin 0,64: je Seite 0,18 Luft. Die Toleranzen summieren sich im ungünstigen Fall auf etwa 0,36 (Mulde 0,10, Kassette 0,06, Buchse in der Tasche bis 0,20). "
         "Die Buchse darf sich in der Tasche etwas bewegen und zentriert sich vielleicht selbst. Das zeigt erst dieser Test. Fallback: Taschenspiel verkleinern oder eine dünne Führungsplatte (0,4) im Boden."),
        ("Muldenboden 0,4 als Brücke.", "Zwei Schichten über der Körpertasche (etwa 11 × 4 mm). Die Überhangprüfung beim Erzeugen entscheidet; Fallback 0,6 (E = 5,08, noch stabil)."),
        ("Einpresskraft.", "Im Test E waren 7 mm Berührung. Im Mini-Gebäude sind es 17 mm, die Kraft wird mehr als doppelt. Darum Variante B mit Passzone von 8 mm."),
        ("Halt der Buchse beim Abziehen.", "Ohne Boden hält nur die Reibung in der Tasche. Der Zug der Pins ist schwach, das Feld im Testbogen war aber leer. Hier wird es geprüft."),
        ("Elefantenfuß.", "Das Gebäude steht mit dem Schacht-Eingang am Bett. Die Fase %s am Eingang soll den Wulst ausgleichen; bleibt er, auf 0,5." % de(P.ENTRY_CH_T, 1)),
        ("Reserve bei E.", "Echte Pin-Länge noch nicht gemessen (Nennwert %s)." % de(sd.HDR_UP)),
    ]
    return ('<section class="sec"><h2>Risiken</h2>%s</section>' % "".join('<p class="risk"><b>%s</b> %s</p>' % r for r in risks))


def sec_checks():
    rows = [
        ("1", "Kassette von unten ins Mini-Gebäude drücken", "nur mit Daumendruck, schlägt am Rand an, sitzt fest, Buchse bündig mit der Fußunterkante"),
        ("2", "Mini-Gebäude in die Mulde setzen", "mit Fingerdruck, kein spürbares Spiel, nur in einer Lage, sinkt bis zum Boden"),
        ("3", "Pins durch den Muldenboden in die Buchse", "ohne Kraft, kein Verkanten, alle vier gehen gleichzeitig ein"),
        ("4", "Durchgang mit Multimeter, dabei wackeln", "alle vier Kontakte stabil"),
        ("5", "Gebäude zehnmal abziehen und wieder aufstecken", "Kassette und Buchse bleiben, Durchgang bleibt"),
        ("6", "Adern und LED", "kein Knick über dem Podest, LED-Streifen liegt flach"),
        ("7", "Lötseite", "Lötenden frei, Kabel lassen sich anlöten und nach unten führen, Deckel mit Fenster schließt"),
        ("8", "Licht (optional)", "LED leuchtet, wenn ein Controller an den Lötenden hängt"),
    ]
    trs = "".join("<tr><td class=\"n\">%s</td><td>%s</td><td>%s</td></tr>" % r for r in rows)
    return ('<section class="sec"><h2>Prüfablauf nach dem Druck</h2><div class="tw"><table class="t"><thead><tr><th>Nr.</th><th>Handgriff</th><th>Soll</th></tr></thead><tbody>%s</tbody></table></div>'
            '<p class="note">Danach gibt es einen Testbogen mit Formular wie bei den beiden Nächten davor.</p></section>' % trs)


DECISIONS = [
    dict(id="F", tag="Fuß", title="Fußform des Mini-Gebäudes", rec="B",
         text="Echte Gebäude folgen ihrem Grundriss. Der Fuß soll das auch testen.",
         opts=[("A", "Rechteck 22 × 36 mit abgeschrägter Kodierecke, wie das Probestück (bewährt, aber keine echte Form)"),
               ("B", "L-Form 24 × 38 mit Ausschnitt 3,5 × 9 an einer Ecke (konkave Ecke, nur eine Lage möglich)"),
               ("C", "Ausschnitt aus einem echten Grundriss, zugeschnitten (aufwendiger, später)")]),
    dict(id="S", tag="Schacht", title="Spiel im Schacht des Mini-Gebäudes", rec="C",
         text="Im Test E waren es 7 mm Berührung, im Mini-Gebäude 17 mm.",
         opts=[("A", "nur Gebäude A: 0,06 durchgehend"), ("B", "nur Gebäude B: Passzone 8 mm mit 0,06, dahinter 0,20"),
               ("C", "beide drucken (A und B), je etwa {bld} g")]),
    dict(id="P", tag="Podest", title="Form des Podests in der Kassette", rec="A",
         text="Die Adern sollen im Bogen statt im Knick zur LED laufen.",
         opts=[("A", "ganze Oberseite 2 mm höher, Rundung R 2,5 (einfach, wie im Bild)"),
               ("B", "nur die LED-Fläche als Podest, Schultern über der Buchse bleiben niedrig, Rampe dazwischen")]),
    dict(id="L", tag="Lötseite", title="Raum hinter den Lötenden", rec="A",
         text="Dort sollen Kabel anschließen, keine Wand direkt hinter der Spitze.",
         opts=[("A", "Kabelraum offen nach unten, Deckel mit Fenster (wie im Bild)"),
               ("B", "seitlicher Kanal zum Plattenrand (3,6 hoch, 12 breit)"), ("C", "wie bisher, Wand 0,9 mm hinter der Spitze")]),
    dict(id="D", tag="Deckel", title="Halt der Winkelleiste in der Mini-Platte", rec="A",
         text="Beim Aufstecken drückt das Gebäude die Pins nach unten.",
         opts=[("A", "Mini-Deckel mit Stempeln und 4 Schrauben M3 (wie die große Platte)"), ("B", "ohne Deckel, Winkelleiste mit Heißkleber fixiert")]),
    dict(id="Z", tag="Zunge", title="Federzunge in der Mulde", rec="A",
         text="Bei Spiel 0,10 vielleicht unnötig; kostet bei der L-Form eine gerade Wand.",
         opts=[("A", "weglassen, erst ohne testen"), ("B", "mitdrucken (niedrige Priorität)")]),
    dict(id="R", tag="Reserve", title="Muldenboden-Reserve", rec="A",
         text="E = 5,28 hat zwei Zehntel Reserve zur gemessenen Grenze.",
         opts=[("A", "nur eine Platte mit 0,4"), ("B", "zusätzlich zweite Platte mit 0,6 als Rückfall (E = 5,08), +{plate} g")]),
]


def decision_card(dd):
    w = est_weights()
    dd = dict(dd, opts=[(k, t.replace("{bld}", de(w["bld"], 0)).replace("{plate}", de(w["plate"], 0))) for k, t in dd["opts"]])
    opts = "".join('<div><b>%s</b><span>%s%s</span></div>' % (k, t, "  <span class=\"rec\">(Empfehlung)</span>" if k == dd["rec"] else "") for k, t in dd["opts"])
    sel = "".join('<option value="%s">%s%s</option>' % (k, k, " (Empfehlung)" if k == dd["rec"] else "") for k, _ in dd["opts"])
    return ('<article class="dec" id="d-%s"><header><span class="tg">%s</span><h2>%s</h2></header><div class="txt"><p>%s</p><div class="opts">%s</div></div>'
            '<div class="vote"><label class="ok" for="a-%s"><span>Deine Wahl</span><select id="a-%s" data-did="%s"><option value="">– bitte wählen –</option>%s'
            '<option value="x">andere (Notiz)</option></select></label>'
            '<label class="ok wide" for="n-%s"><span>Notiz</span><input type="text" id="n-%s" data-nid="%s" placeholder="optional"></label></div></article>'
            % (dd["id"], dd["tag"], dd["title"], dd["text"], opts, dd["id"], dd["id"], dd["id"], sel, dd["id"], dd["id"], dd["id"]))


def main():
    sections = "".join([sec_questions(), sec_assembly(), sec_top(), sec_parts(), sec_changes(), sec_chain(), sec_kassette(), sec_risks(), sec_checks()])
    sections += '<section class="top"><h2>Entscheidungen</h2><p class="lead">Mit der Empfehlung ist der Plan rund; Abweichungen bitte hier markieren.</p></section>'
    sections += "\n".join(decision_card(x) for x in DECISIONS)
    spec = [dict(id=x["id"], tag=x["tag"], title=x["title"]) for x in DECISIONS]
    with open(TEMPLATE, encoding="utf-8") as f:
        page = f.read()
    rep = {"{{HEAD}}": head(), "{{SECTIONS}}": sections, "{{SPEC}}": json.dumps(spec, ensure_ascii=False),
           "{{IMG_KASSETTE}}": img_uri("kassette_v4.png", 900)}
    for kk, v in rep.items():
        page = page.replace(kk, v)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(page)
    print("geschrieben: %s (%d kB)" % (os.path.relpath(OUT, ROOT), os.path.getsize(OUT) / 1024))


if __name__ == "__main__":
    main()
