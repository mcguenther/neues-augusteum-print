#!/usr/bin/env python3
"""Testbogen für Steckprobe 2: baut plug/testcase/feedback2.html aus feedback2.template.html.

Führt Schritt für Schritt durch die Teile aus plug/testcase/build2.py (stl/steckmodul_testcase2/): Anleitung, Zeichnung mit Regler (die Zeichnungen
des neuen Zwei-Lagen-Aufbaus stehen schon vor dem Druck), Formular und ein Ergebnistext zum Kopieren. Maße kommen aus plug/testcase/params.py,
plug/power/params.py und build2.py.

Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m plug.testcase.build_feedback2      # schreibt plug/testcase/feedback2.html
"""
import base64
import io
import json
import math
import os

import shapely
from PIL import Image

from plug import dupont as sd
from plug import series2 as N2
from plug.feedback.build import G, R_FIT, R_YN, de, fld, opts, render_field
from plug.feedback.build_night2 import E_FIT, E_HOLD, GOOD3, K_PASS
from plug.power import params as PP
from plug.testcase import build2 as B2
from plug.testcase import build_feedback as FB
from plug.testcase import kassette as KA
from plug.testcase import params as P

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TEMPLATE = os.path.join(HERE, "feedback2.template.html")
OUT = os.path.join(HERE, "feedback2.html")
PREV2 = os.path.join(ROOT, "vorschau", "steckmodul_testcase2")
PREV1 = os.path.join(ROOT, "vorschau", "steckmodul_testcase")

D, H, DK = B2.D, B2.H, B2.DK
F = D["F"]
FY0, FY1 = D["yc"] - P.BOX_L / 2, D["yc"] + P.BOX_L / 2
ZK = -F + D["kass_h"] + P.SHAFT_EXTRA_T            # Schachtende
ZTOP = ZK + P.STOP_T                                # Oberkante Gebäude
WALL, ZF, DECK, BOT = PP.UK_WALL, B2.ZF, B2.DECK, H["uk_bot"]


def img_uri(path, width):
    im = Image.open(path).convert("RGB")
    im = im.resize((width, int(im.size[1] * width / im.size[0])), Image.LANCZOS)
    b = io.BytesIO()
    im.save(b, "JPEG", quality=86, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()


def var_group(g, gname, var, shown):
    g.o.append('<g data-group="%s" data-var="%s" class="var%s">' % (gname, var, "" if shown else " off"))


def assembled(g, gid, shown_assembled=False):
    """Beginnt eine Gruppe mit Regler; Startlage = zusammengebaut, wenn shown_assembled."""
    return None


# --------------------------------------------------------------------------
# Teile im Längsschnitt (x = 0): y waagerecht, z senkrecht
# --------------------------------------------------------------------------
def draw_under(g, window=True):
    yb, at, gs = D["yb"], PP.ANSCHLAG["t"], PP.ANSCHLAG["gusset"]
    g.rect(B2.PY0, B2.PY1, BOT, ZF, "d-under")
    g.rect(B2.PY1 - WALL, B2.PY1, ZF, DECK, "d-under")
    if window:
        g.rect(B2.PY0, B2.PY0 + WALL, ZF, DECK, "d-open")                                # Kabelfenster in der Vorderwand (x = 0 liegt im Fenster)
    else:
        g.rect(B2.PY0, B2.PY0 + WALL, ZF, DECK, "d-under")
    g.rect(yb - at / 2, yb + at / 2, ZF, H["stamp_top"], "d-under")                      # Steg-Anschlag unter dem Körper
    g.poly([(yb + at / 2, ZF), (yb + at / 2 + gs, ZF), (yb + at / 2, H["stamp_top"] - 2.0)], "d-under")


def draw_top_plate(g):
    """Oberplatte mit Mulde, Dock (Körpertasche, Pinschacht, Schlitz, Kabelnische), Pinloch; Winkelleiste folgt getrennt."""
    zhb, zbb = D["z_hb"], D["z_bb"]
    yb, hd = D["yb"], sd.HDR_T / 2 + sd.SNUG_HDR
    clr, rel, cp, bd = P.MULDE_CLR_T, sd.RELIEF, sd.CH_P, sd.BAND
    g.rect(B2.PY0, B2.PY1, DECK, 0.0, "d-slab")
    mulde = [(FY0 - clr - rel, -F), (FY1 + clr + rel, -F), (FY1 + clr + rel, -cp - bd), (FY1 + clr, -cp - bd), (FY1 + clr, -cp),
             (FY1 + clr + cp, 0.01), (FY0 - clr - cp, 0.01), (FY0 - clr, -cp), (FY0 - clr, -cp - bd), (FY0 - clr - rel, -cp - bd)]
    g.poly(mulde, "d-void")
    g.rect(DK["y_slot"], yb + hd, DECK - 0.01, zhb, "d-void")                            # Körpertasche, nach unten offen
    g.rect(yb, 0.32 + 0.8, DECK - 0.01, zhb, "d-void")                                   # Platz für Knick und Pin
    g.rect(DK["slot_end"], DK["y_slot"] + 0.01, DECK - 0.01, D["step"], "d-void")        # Lötendenschlitz
    g.rect(DK["niche_end"], DK["y_slot"] + 0.01, DECK - 0.01, H["z_slot"], "d-void")     # Kabelnische
    g.rect(-sd.HOLE / 2, sd.HOLE / 2, zhb, -F + 0.01, "d-void")                          # Stiftloch im Muldenboden


def draw_header(g):
    yb = D["yb"]
    g.rect(yb - sd.HDR_T / 2, yb + sd.HDR_T / 2, D["z_bb"], D["z_hb"], "d-body")
    g.rect(D["y_tail"], 0.32, D["z_bm"] - 0.32, D["z_bm"] + 0.32, "d-pin")
    g.rect(-0.32, 0.32, D["z_bm"] - 0.32, D["z_tip"], "d-pin")


def draw_building(g, with_labels=True):
    """Gebäude, Kassette (Schnitt x = 0), Buchse, LED, Ader; Fußunterkante bei −F."""
    k = P.kass_dims()
    ch = sd.CH_F
    g.poly([(FY0 + ch, -F), (FY1 - ch, -F), (FY1, -F + ch), (FY1, ZTOP), (FY0, ZTOP), (FY0, -F + ch)], "d-bld")
    sy0, sy1 = D["y_kass0"] - P.KASS_CLR_T, D["y_kass1"] + P.KASS_CLR_T
    e = P.ENTRY_CH_T
    g.poly([(sy0 - e, -F - 0.01), (sy1 + e, -F - 0.01), (sy1, -F + e), (sy1, ZK), (sy0, ZK), (sy0, -F + e)], "d-void")
    g.rect(sy0 + N2.E_LIP, sy1 - N2.E_LIP, ZK - 0.01, ZTOP + 0.01, "d-void")
    y0k = D["y_kass0"]
    X = lambda yl: y0k + yl
    Z = lambda zl: -F + zl
    y1l, top, zp, r = k["y1"], k["top"], k["zp"], P.FILLET_T
    arc = [(y1l + r + r * math.cos(a), top - r + r * math.sin(a)) for a in [math.pi / 2 + j * math.pi / 2 / 12 for j in range(13)]]
    g.poly([(X(y1l), Z(0)), (X(k["L"]), Z(0)), (X(k["L"]), Z(top)), (X(y1l + r), Z(top))] + [(X(a), Z(b)) for a, b in arc[1:]] + [(X(y1l), Z(0))], "d-kass")
    g.rect(X(0), X(k["y_p0"]), Z(0), Z(top), "d-kass")
    g.poly([(X(k["y_p0"] - e), Z(-0.01)), (X(y1l + e), Z(-0.01)), (X(y1l), Z(e)), (X(y1l), Z(0)), (X(k["y_p0"]), Z(0)), (X(k["y_p0"]), Z(e))], "d-void")
    g.rect(X(k["y_p0"]), X(y1l), Z(zp - 0.01), Z(top + 0.01), "d-void")
    g.rect(-1.27, 1.27, -F, -F + sd.HSG_H, "d-hsg")
    g.rect(-0.5, 0.5, -F + 0.5, -F + 5.5, "d-term")
    ya = X(k["seat0"] + N2.SEAT_TOL)
    g.rect(ya, ya + 16.7, Z(top), Z(top) + 0.3, "d-led")
    g.rect(ya + 6.0, ya + 11.0, Z(top) + 0.3, Z(top) + 1.5, "d-led")
    wp = KA.wire_points(k)
    g.o.append('<polyline points="%s" class="d-wire"/>' % " ".join("%.1f,%.1f" % (g.X(X(a)), g.Z(Z(b))) for a, b in wp))
    if with_labels:
        g.text(X(k["L"] / 2 + 2), Z(zp * 0.55), "Kassette", "dlb")


def labels_section(g, show_dock=True):
    g.text(B2.PY0 + 0.4, BOT + 0.6, "Unterkasten, hohl", "dlb", "start")
    g.text(B2.PY0 + 0.6, DECK - 3.3, "Kabelfenster", "dls", "start")
    g.text(B2.PY1 - 0.5, DECK + 1.2, "Oberplatte %s mm" % de(-DECK, 1), "dlb", "end")
    if show_dock:
        g.text(DK["niche_end"] + 0.4, DECK - 1.2, "Kabelnische", "dls", "start")
        g.text(D["yb"] - 6.8, ZF + 5.0, "Steg", "dls", "end")


def svg_section2(mode):
    """mode 'aufbau': Oberplatte und Gebäude fahren auseinander (Regler A-ALL); mode 'stecken': nur das Gebäude (Regler T-mov)."""
    S, LT, LB = 7.2, 8.0, 24.0
    oy = (ZTOP + (LT + LB if mode == "aufbau" else 12.0) + 3.0) * S
    g = G(S, -B2.PY0 * S + 20, oy)
    draw_under(g)
    if mode == "aufbau":
        g.group("A-top", move=(0, LT, 0, 0))
        draw_top_plate(g)
        draw_header(g)
        labels_section(g)
        g.end()
        g.group("A-bld", move=(0, LT + LB, 0, 0))
        draw_building(g)
        g.end()
        cap = "Zwei-Lagen-Aufbau im Schnitt durch die Pinreihe"
    else:
        draw_top_plate(g)
        draw_header(g)
        labels_section(g)
        g.group("T-mov", move=(0, 12.0, 0, 0))
        g.o[-1] = g.o[-1].replace('transform="translate(0.0,%.1f)"' % (-12.0 * S), 'transform="translate(0.0,0.0)"')
        draw_building(g)
        g.end()
        g.line(3.2, -F, 3.2, D["z_tip"], "dimn")
        g.text(4.0, (-F + D["z_tip"]) / 2 - 0.3, "E = %s mm" % de(D["E"]), "dln", "start")
        cap = "Gebäude aufgesteckt, Regler zieht es ab"
    return g.svg(int((B2.PY1 - B2.PY0) * S + 44), int(oy + (-BOT + 3.0) * S), cap)


def svg_bestuecken():
    k = P.kass_dims()
    S, LIFT = 10.0, 9.0
    top, L, yb = k["top"], k["L"], k["ypin"]
    g = G(S, 28, (top + LIFT + 4.5) * S)
    g.rect(-1.5, L + 2.0, -1.4, 0.0, "d-slab")
    g.text(L / 2, -2.8, "flacher Tisch", "dls")
    g.group("K-mov", move=(0, LIFT, 0, 0))
    FB.kass_shape(g, k, P.HSG_TOL_SAFE)
    g.text(L / 2 + 2, top / 2, "Kassette: Tasche %s hoch" % de(k["zp"], 2), "dlb")
    g.end()
    g.rect(yb - 1.27, yb + 1.27, 0, sd.HSG_H, "d-hsg")
    g.rect(yb - 0.5, yb + 0.5, 0.5, 5.5, "d-term")
    g.o.append('<polyline points="%.1f,%.1f %.1f,%.1f" class="d-wire"/>' % (g.X(yb), g.Z(sd.HSG_H), g.X(yb), g.Z(top + LIFT + 1.5)))
    return g.svg(420, int((top + LIFT + 4.5) * S + 34), "Kassette wird über die auf dem Tisch stehende Buchse gestülpt")


def svg_press():
    S, LIFT = 9.0, 14.0
    yc = D["yc"]
    ox, oy = -FY0 * S + 20, (ZTOP + 3.0) * S
    g = G(S, ox, oy)
    ch, e, c = sd.CH_F, P.ENTRY_CH_T, P.KASS_CLR_T * 8
    sy0, sy1 = D["y_kass0"] - c, D["y_kass1"] + c
    g.poly([(FY0 + ch, -F), (FY1 - ch, -F), (FY1, -F + ch), (FY1, ZTOP), (FY0, ZTOP), (FY0, -F + ch)], "d-bld")
    g.poly([(sy0 - e, -F - 0.01), (sy1 + e, -F - 0.01), (sy1, -F + e), (sy1, ZK), (sy0, ZK), (sy0, -F + e)], "d-void")
    g.rect(D["y_kass0"] + N2.E_LIP, D["y_kass1"] - N2.E_LIP, ZK - 0.01, ZTOP + 0.01, "d-void")
    g.text(yc, ZTOP + 1.3, "Spiel %s über die ganze Tiefe (8× überzeichnet), Schacht %s tief" % (de(P.KASS_CLR_T), de(D["kass_h"] + P.SHAFT_EXTRA_T, 2)), "dlb")
    g.group("E-mov", move=(0, -LIFT, 0, 0))
    g.rect(D["y_kass0"], D["y_kass1"], -F, -F + D["kass_h"], "d-kass")
    g.rect(D["y_kass0"] + 1.2, D["y_kass0"] + 1.2 + P.kass_dims()["pk_d"], -F - 0.01, -F + sd.HSG_H + 0.2, "d-void")
    g.text(D["y_kass1"] - 9.0, -F + D["kass_h"] / 2, "Kassette", "dlb")
    g.text(D["y_kass1"] - 9.0, -F + D["kass_h"] / 2 - 1.6, "offene Seite voran", "dls")
    g.end()
    g.rect(FY1 - 6.0, FY1 - 0.01, ZK, ZTOP, "d-dash0")
    g.text(FY1 - 0.6, ZTOP - 0.7, "Anschlagrand %s" % de(P.STOP_T, 1), "dls", "end")
    g.text(FY1 - 0.6, ZK + 0.35 - 2.0, "0,3 Luft über der Kassette", "dls", "end")
    return g.svg(int((FY1 - FY0) * S + 60), int(oy + (F + LIFT + 2.5) * S), "Kassette wird von unten ins Mini-Gebäude gedrückt")


def svg_dock():
    """Winkelleiste wird von unten in die Oberplatte geschoben (Platte liegt umgedreht, Mulde unten gezeichnet wie im Bau, Schnitt längs y)."""
    S, LIFT = 9.0, 9.0
    y0, y1 = B2.PY0, 16.0
    g = G(S, -y0 * S + 20, 20 + 2.0 * S)
    zhb, zbb = D["z_hb"], D["z_bb"]
    yb, hd = D["yb"], sd.HDR_T / 2 + sd.SNUG_HDR
    clr, rel, cp, bd = P.MULDE_CLR_T, sd.RELIEF, sd.CH_P, sd.BAND
    g.rect(y0, y1, DECK, 0.0, "d-slab")
    g.poly([(FY0 - clr - rel, -F), (y1 + 0.5, -F), (y1 + 0.5, 0.01), (FY0 - clr - cp, 0.01), (FY0 - clr, -cp), (FY0 - clr, -cp - bd), (FY0 - clr - rel, -cp - bd)], "d-void")
    g.rect(DK["y_slot"], yb + hd, DECK - 0.01, zhb, "d-void")
    g.rect(yb, 0.32 + 0.8, DECK - 0.01, zhb, "d-void")
    g.rect(DK["slot_end"], DK["y_slot"] + 0.01, DECK - 0.01, D["step"], "d-void")
    g.rect(DK["niche_end"], DK["y_slot"] + 0.01, DECK - 0.01, H["z_slot"], "d-void")
    g.rect(-sd.HOLE / 2, sd.HOLE / 2, zhb, -F + 0.01, "d-void")
    g.group("W-mov", move=(0, -LIFT, 0, 0))
    draw_header(g)
    g.text(D["y_tail"] - 0.5, D["z_bm"] + 1.2, "Lötenden", "dl", "end")
    g.end()
    g.text(DK["niche_end"] + 0.5, DECK + 1.45, "Kabelnische %s × %s mm" % (de(DK["niche_w"], 0), de(DK["y_slot"] - DK["niche_end"], 0)), "dls", "start")
    g.text(y0 + 0.4, 1.4, "Mulde", "dls", "start")
    g.text(y0 + 0.4, zhb + 0.9, "Muldenboden", "dls", "start")
    g.text(DK["y_slot"] - 0.4, zhb + 0.9 + 1.6, "Körpertasche mit Rippen", "dls", "end")
    g.o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="dimn"/>' % (g.X(DK["niche_end"]), g.Z(DECK - 1.2), g.X(DK["y_slot"]), g.Z(DECK - 1.2)))
    return g.svg(int((y1 - y0) * S + 50), int(20 + 2 * S + (-DECK + LIFT + 3.0) * S), "Winkelleiste wird von unten in die Oberplatte geschoben")


def svg_zapfen():
    """Querschnitt (x–z) bei y = 8: Oberplatte wird auf den Unterkasten gesetzt, Zapfen in das Loch."""
    S, LIFT = 9.0, 8.0
    px = B2.PX
    xz = B2.post_positions()[0][0]
    g = G(S, px * S + 20, (LIFT + 3.0 + 2.0) * S + 4)
    pin, ch = PP.PIN, PP.CH_PIN
    g.rect(-px, px, BOT, ZF, "d-under")
    g.rect(-px, -px + WALL, ZF, DECK, "d-under")
    g.rect(px - WALL, px, ZF, DECK, "d-under")
    for x in (-8.5, 8.5):
        g.rect(x - PP.POST[0] / 2, x + PP.POST[0] / 2, ZF, DECK, "d-under")
    g.poly([(xz - pin["d"] / 2, DECK), (xz + pin["d"] / 2, DECK), (xz + pin["d"] / 2, DECK + pin["h"] - ch), (xz + pin["d"] / 2 - ch, DECK + pin["h"]),
            (xz - pin["d"] / 2 + ch, DECK + pin["h"]), (xz - pin["d"] / 2, DECK + pin["h"] - ch)], "d-under")
    g.group("Z-mov", move=(0, LIFT, 0, 0))
    g.rect(-px, px, DECK, DECK + 4.0, "d-slab")
    hole = pin["d"] / 2 + pin["clr"]
    g.rect(xz - hole, xz + hole, DECK - 0.01, DECK + pin["h"] + 0.3, "d-void")
    g.text(0, DECK + 2.0, "Oberplatte (Ausschnitt)", "dls")
    g.end()
    g.text(xz + 3.0, DECK + 2.2 - LIFT * 0, "Zapfen Ø %s, Loch Ø %s (Spiel %s)" % (de(pin["d"], 1), de(pin["d"] + 2 * pin["clr"], 1), de(pin["clr"])), "dls", "start")
    g.text(0, BOT + 0.7, "Unterkasten mit Stützen", "dls")
    return g.svg(int(2 * px * S + 44), int((LIFT + 3.0 + 2.0) * S + 4 + (-BOT + 1.5) * S), "Oberplatte wird auf den Unterkasten gesetzt, Zapfen greift in das Loch")


def svg_faden():
    """Schnitt durch eine Ecke entlang des V: Variante 53° (Plan) oder 40° (flacher). Faden von unten, über die Lasche, nach unten."""
    S = 11.0
    vs = sorted(B2.vs_placed(), key=lambda v: v["c"][1])[:2]                # die zwei vorderen V (links 53°, rechts 40°)
    byslope = {round(v["slope"], 2): v for v in vs}
    ld, r, apex = P.V_LEG_D, P.V_ENTRY_R, P.V_APEX
    zb, zT = DECK - 7.5, DECK + 7.5
    g = G(S, 20, (zT + 2.0) * S)
    for var, sl, shown in (("53", P.V_SLOPE_A, True), ("40", P.V_SLOPE_B, False)):
        v = byslope[round(sl, 2)]
        tc = v["c"][1] - B2.PY0
        hs = apex * sl
        e1, e2 = tc - hs, tc + hs
        nend = e2 + r + PP.NOTCH_PAD
        t1 = nend + 8.0
        var_group(g, "FV", var, shown)
        g.rect(0, t1, DECK, zT, "d-slab")
        g.rect(nend, t1, BOT + 0.0, DECK, "d-under")
        g.rect(nend + WALL, t1, ZF, DECK - 0.01, "d-void")
        g.rect(0, t1, zb, DECK - 3.0 - 2.0, "d-hat")
        for e in (e1, e2):
            g.poly([(e - r, DECK - 0.01), (e + r, DECK - 0.01), (e + ld / 2, DECK + 1.5), (e - ld / 2, DECK + 1.5)], "d-void")
        for a, b in ((e1, tc), (e2, tc)):
            g.o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="d-vline" style="stroke-width:%.1f"/>' % (g.X(a), g.Z(DECK), g.X(b), g.Z(DECK + apex), ld * S))
        g.o.append('<polyline points="%s" class="d-thread"/>' % " ".join("%.1f,%.1f" % (g.X(x), g.Z(z)) for x, z in
                                                                         [(e1 - 1.6, zb + 1.0), (e1, DECK), (tc, DECK + apex), (e2, DECK), (e2 + 1.6, zb + 1.0)]))
        ang = math.degrees(math.atan2(1.0, sl))
        over = 0.2 * sl
        g.text(0.3, DECK + apex + 1.7, "Lasche, Scheitel %s über der Unterseite" % de(apex, 1), "dls", "start")
        g.text(0.3, DECK + apex + 3.2, "%d° zur Waagerechten, Überhang %s mm je Schicht" % (round(ang), de(over, 2)), "dlb", "start")
        g.text(0.5, zb + 0.4, "Hut", "dls", "start")
        g.text(nend + WALL + 0.5, (BOT + DECK) / 2, "Unterkasten (hohl)", "dls", "start")
        g.text(0.3, DECK - 2.6, "Eckaussparung", "dls", "start")
        g.end()
    return g.svg(int(38 * S), int(20 + (zT - zb + 2.0) * S), "Schnitt durch eine Ecke mit dem Faden-V")


def svg_luft():
    """Luft unter der Buchse kostet Einstecktiefe: bündig, an den Schultern (Tasche 14,60), Vergleich Steckprobe 1."""
    tip = sd.HDR_UP - P.CEIL_T
    cases = [("Buchse bündig", 0.0, "ok"), ("an den Schultern", P.HSG_TOL_SAFE - 0.55, "ok"), ("Steckprobe 1 (Grenze)", 0.45, "bad")]
    S, yb, Hh = 22.0, 205.0, 7.4
    o = []
    for i, (nm, gap, kind) in enumerate(cases):
        x0 = 14 + i * 222
        e = tip - gap
        o.append('<text x="%.1f" y="22" class="dlb">%s</text>' % (x0, nm if len(nm) < 26 else nm[:24] + "…"))
        o.append('<rect x="%.1f" y="%.1f" width="14" height="%.1f" class="d-kass"/>' % (x0, yb - Hh * S, Hh * S))
        o.append('<rect x="%.1f" y="%.1f" width="14" height="%.1f" class="d-kass"/>' % (x0 + 166, yb - Hh * S, Hh * S))
        o.append('<rect x="%.1f" y="%.1f" width="120" height="%.1f" class="d-hsg"/>' % (x0 + 24, yb - Hh * S, (Hh - gap) * S))
        o.append('<rect x="%.1f" y="%.1f" width="12" height="%.1f" class="d-pin"/>' % (x0 + 78, yb - tip * S, tip * S + 20))
        o.append('<rect x="%.1f" y="%.1f" width="194" height="22" class="d-slab"/>' % (x0 - 7, yb))
        o.append('<text x="%.1f" y="%.1f" class="dls">Muldenboden</text>' % (x0, yb + 15))
        ya, yt = yb - gap * S, yb - tip * S
        o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="%s"/>' % (x0 + 120, ya, x0 + 120, yt, "dimn" if kind == "ok" else "dlw-line"))
        o.append('<text x="%.1f" y="%.1f" class="%s">E = %s</text>' % (x0 + 126, (ya + yt) / 2 + 4, "dln" if kind == "ok" else "dlw", de(e)))
        o.append('<text x="%.1f" y="%.1f" class="dl">Luft unter der Buchse: %s mm</text>' % (x0, yb + 44, de(gap)))
        o.append('<text x="%.1f" y="%.1f" class="dls">%s</text>' % (x0, yb + 60, "stabiler Bereich" if kind == "ok" else "Grenzbereich"))
    return '<svg viewBox="0 0 680 290" role="img" aria-label="Luft unter der Buchse kostet Einstecktiefe" class="dgsvg">%s</svg>' % "".join(o)


def svg_mulde_top():
    """Draufsicht: L-förmiger Fuß in der Mulde mit Spiel 0,10, gestrichelt die Muldenfase."""
    S = 9.0
    g = G(S, 201, 372)
    fp = B2.foot_poly()
    pw, pl_ = 2 * B2.PX, B2.PY1 - B2.PY0
    g.rect(-pw / 2, pw / 2, B2.PY0, B2.PY1, "d-slab")
    mouth = fp.buffer(P.MULDE_CLR_T + sd.CH_P, join_style=2)
    mulde = fp.buffer(P.MULDE_CLR_T + sd.RELIEF, join_style=2)
    pts = lambda poly: " ".join("%.1f,%.1f" % (g.X(x), g.Z(y)) for x, y in poly.exterior.coords)
    g.o.append('<polygon points="%s" class="d-dash"/>' % pts(mouth))
    g.o.append('<polygon points="%s" class="d-void"/>' % pts(mulde))
    g.o.append('<polygon points="%s" class="d-bld"/>' % pts(fp))
    k = P.kass_dims()
    x0, y0 = -k["cw"] / 2, D["y_kass0"]
    g.rect(x0, x0 + k["cw"], y0, y0 + k["L"], "d-kass")
    g.text(0, fp.bounds[1] - 2.2, "Fuß mit Fußfase %s, Mulde mit Fase %s" % (de(sd.CH_F, 1), de(sd.CH_P, 1)), "dls")
    return g.svg(int((pw + 4) * S + 160), int((pl_ + 3) * S + 20), "Draufsicht: Fuß in der Mulde")


# --------------------------------------------------------------------------
# Schritte
# --------------------------------------------------------------------------
STEPS = []


def add(sid, title, tag, lead, instr, diagrams, fields, optional=False, calc=None):
    STEPS.append(dict(id=sid, title=title, tag=tag, lead=lead, instr=instr, diagrams=diagrams or [], fields=fields, optional=optional, calc=calc))


R_V = GOOD3("leicht", "mit Mühe", "nicht möglich")


def steps():
    k = P.kass_dims()
    add("a", "Aufbau ansehen (vor dem Druck)", "0", "Der neue Zwei-Lagen-Aufbau, noch bevor etwas gedruckt ist. Hier siehst du, wie die Teile zusammenpassen, und kannst Einwände loswerden.",
        ["Im Bild den <b>Regler</b> ziehen: Unterkasten unten (hohl, mit Steg), darüber die Oberplatte mit Mulde und Dock, darüber das Gebäude mit der Kassette.",
         "Achte auf die <b>Kabelnische</b> hinter den Lötenden (Oberplatte, 1,6 mm hoch) und den freien Raum darunter, auf den <b>Steg</b> unter dem Körper der Winkelleiste (1,2 mm Luft) und auf die <b>Fasen</b> (Fuß 0,8, Mulde 1,0, Bettkanten 0,5).",
         "Die Oberplatte sitzt mit zwei <b>Zapfen</b> auf dem Unterkasten; der Faden hält beides zusammen. An den vier Ecken liegt je ein <b>Faden-V</b>: links 53°, rechts 40° (Beschriftung „53“ und „40“ an der Vorderseite)."],
        [("svg", "aufbau", "Schnitt durch die Pinreihe: Regler zieht Oberplatte und Gebäude auseinander."), ("img", PREV2 + "/zusammenbau_schraeg.png", "Schräg: Unterkasten, Oberplatte, Winkelleiste, Gebäude mit Kassette (auseinandergezogen)."),
         ("img", PREV2 + "/platte_unterkasten.png", "Oberplatte von unten (links oben und unten) mit Nische, Winkelleiste und Faden-V; Unterkasten von oben (rechts oben) und aufgesetzt (rechts unten).")],
        [fld("a-ok", "So drucken?", "select", opts([("", "– bitte wählen –"), ("a", "ja, so drucken"), ("b", "ja, aber mit Anmerkung (Freitext)"), ("c", "nein, vorher ändern (Freitext)")]))],
        optional=True)
    add("p", "Vorbereiten", "1", "Alles hinlegen und die Kaufteile bereitlegen. Die Höhe der Buchsen muss nicht mehr gemessen werden.",
        ["Teile auslegen: die <b>Kassette</b> (nur eine, keine Reserve), das <b>Gebäude</b> (<code>GEB S2</code>), die <b>Oberplatte</b> (<code>S2 OBEN</code>, vorn „53“ und „40“) und der <b>Unterkasten</b> (<code>UK S2</code>).",
         "Bereitlegen: Winkelleiste, Buchse mit gecrimpten Adern, LED-Streifen 10 mm, <b>Faden und Nadel</b>, Heißkleber, Multimeter, ein <b>flacher Tisch</b>. Schrauben werden nicht gebraucht."],
        [("img", PREV2 + "/teile.png", "Alle Teile in Druckausrichtung: Kassette (orange), Gebäude (beige), Oberplatte (hellblau), Unterkasten (blaugrau).")],
        [fld("p-cr", "Sind die Kontakte an der Buchse gecrimpt (Adern dran)?", "select", R_YN("ja, alle 4", "nein, nur das leere Gehäuse")),
         fld("p-mm", "Multimeter mit Durchgangsprüfung vorhanden?", "select", R_YN("ja", "nein")),
         fld("p-thr", "Faden und Nadel vorhanden?", "select", R_YN("ja", "nein"))])
    add("q", "Druckqualität ansehen", "2", "Bevor etwas gesteckt wird: die gedruckten Teile kurz prüfen. Diese Befunde gehören zum Ergebnis.",
        ["Jedes Teil von oben, unten und von der Seite ansehen. Mit dem Fingernagel die <b>Kanten am Bett</b> fühlen, besonders am <b>Schachteingang</b> des Gebäudes und an den Mündungen der Oberplatte (Fase 0,5).",
         "<b>Oberplatte von unten:</b> Muldenboden (0,4 mm) über der Körpertasche, die <b>Kabelnische</b> (Decke 1,6 mm über dem Bett) und die <b>vier Faden-V</b>: glatt oder durchgehängt?",
         "<b>Faden-V links 53°</b> und <b>rechts 40°</b> mit einer Nadel oder einem Draht durchfahren: Ist der Kanal offen, ohne Fäden und Wulst? Beim 40°-V ist der Überhang größer (0,24 statt 0,15 mm je Schicht).",
         "Unterkasten: Steg, Streben, Stützen, Zapfen und Eckaussparungen ansehen; nichts abgebrochen? Erhabene Schrift und Kerben antasten."],
        [],
        [fld("q-all", "Welche Dateien wurden gedruckt?", "text", ph="z. B. alles"),
         fld("q-floor", "Oberplatte: Muldenboden und Pin-Löcher (von unten)", "select", GOOD3("glatt, Löcher offen", "leicht durchgehängt", "stark durchgehängt oder Löcher zu", "Fehldruck")),
         fld("q-niche", "Kabelnische: Decke", "select", GOOD3("glatt", "leicht durchgehängt", "stark durchgehängt", "Fehldruck")),
         fld("q-v53", "Faden-V links (53°): Kanal", "select", GOOD3("sauber und offen", "Stufen, aber durchgängig", "zu, Fäden oder Wulst", "Fehldruck")),
         fld("q-v40", "Faden-V rechts (40°, flacher): Kanal", "select", GOOD3("sauber und offen", "Stufen, aber durchgängig", "zu, Fäden oder Wulst", "Fehldruck")),
         fld("q-foot", "Elefantenfuß an Schachteingang, Fußunterkante und Bettkanten (Fase 0,5)", "select", GOOD3("sauber, Fase hat gewirkt", "leichter Wulst", "starker Wulst, musste entgratet werden")),
         fld("q-ub", "Unterkasten: Steg, Stützen, Zapfen", "select", GOOD3("alles heil und gerade", "Steg oder Strebe verbogen", "etwas abgebrochen")),
         fld("q-text", "Erhabene Schrift und Kerben", "select", GOOD3("gut lesbar und fühlbar", "lesbar, aber flach", "schlecht lesbar")),
         fld("q-time", "Druckzeit insgesamt in Stunden", "text", ph="z. B. 2,5"),
         fld("q-fil", "Drucker und Filament", "text", ph="z. B. Bambu A1, PLA schwarz")])
    add("K", "Kassette bestücken", "K", "Die Buchse muss unten bündig mit der Kassette sitzen. Dafür wird die Kassette von oben über die Buchse gestülpt, nicht die Buchse von unten hineingeschoben.",
        ["Buchse mit der <b>Steckseite auf den flachen Tisch</b> stellen, Adern nach oben. Die Adern durch den <b>Schlitz</b> der Kassette fädeln.",
         "Kassette von oben über die Buchse stülpen, bis sie <b>auf dem Tisch steht</b>. Im Bild den Regler ziehen.",
         "Prüfen: Passt die Buchse (Tasche 14,60)? Sitzt sie unten bündig? Wackelt sie?"],
        [("svg", "bestuecken", "Die Buchse steht mit der Steckseite auf dem Tisch, die Adern gehen durch den Schlitz. Tasche %s hoch: etwa 0,05 mm Luft über der Buchse." % de(k["zp"], 2))],
        [fld("K-p", "Passt eine Buchse in die Kassette?", "select", GOOD3("ja, alle Buchsen", "nur einige", "keine, zu hoch")),
         fld("K-in", "Kassette über die Buchse stülpen", "select", R_FIT),
         fld("K-fl", "Buchse unten bündig", "select", GOOD3("bündig", "steht etwas heraus", "sitzt zu hoch, nicht bündig zu bekommen")),
         fld("K-ho", "Halt der Buchse in der Tasche", "select", GOOD3("fest", "locker", "fällt heraus"))])
    add("E", "Kassette einpressen", "E", "Hält die Kassette im Mini-Gebäude, wenn sie von unten eingedrückt wird? Schacht 0,06 durchgehend, jetzt 0,3 mm tiefer als die Kassette.",
        ["Gebäude hinstellen, <b>Fuß unten</b>. Die bestückte Kassette mit der <b>offenen Seite (Tasche, flache Oberseite) voran</b> von unten ansetzen. Im Bild den Regler ziehen.",
         "Mit dem Daumen eindrücken, bis sie am <b>Anschlagrand</b> anliegt. Wie viel Kraft? Dann das Gebäude umdrehen und schütteln: bleibt sie sitzen?",
         "Mit dem Daumen wieder herausdrücken: wie schwer geht das?",
         "Nach dem Eindrücken die Unterkante der Buchse und der Kassette gegen die Fußunterkante halten: bündig, oder ragt die Kassette heraus (Steckprobe 1: 0,2 mm)?"],
        [("svg", "press", "Das Spiel ist in der Zeichnung 8× überzeichnet.")],
        [fld("E-A", "Sitz der Kassette im Schacht", "select", E_FIT),
         fld("E-A-hold", "Halt beim Umdrehen und Schütteln", "select", E_HOLD),
         fld("E-A-out", "Herausdrücken", "select", opts([("", "– nicht geprüft –"), ("a", "mit dem Daumen leicht"), ("b", "nur mit kräftigem Druck"), ("c", "kaum")])),
         fld("E-flush", "Kassette und Buchse unten an der Fußunterkante", "select", GOOD3("bündig", "Kassette 0,1 bis 0,2 zurückgesetzt (Luft oben, gewollt)", "Kassette ragt heraus", "Buchse hochgerutscht"))],
        calc="E")
    add("M", "Gebäude in die Mulde", "M", "Passt der L-Fuß in die Mulde mit Spiel 0,10, und führt die Fase ihn hinein?",
        ["Oberplatte mit der <b>Mulde nach oben</b> hinstellen. Das Gebäude (mit oder ohne Kassette) von oben in die Mulde setzen: zuerst mit dem <b>Ausschnitt an der Ecke</b> richtig herum.",
         "Gleitet der Fuß dank Fußfase und Muldenfase von selbst hinein? Sinkt er mit Fingerdruck bis zum Boden? Wackelt er?",
         "Dann um 180° gedreht ausprobieren: es soll <b>nicht</b> hineingehen."],
        [("svgcall", "top", "Draufsicht: L-förmiger Fuß in der Mulde mit Spiel 0,10, gestrichelt die Muldenfase.")],
        [fld("M-fit", "Fuß in der Mulde", "select", R_FIT),
         fld("M-ch", "Führung durch die Fasen", "select", GOOD3("gleitet von selbst hinein", "braucht etwas Ausrichten", "hakt an der Kante")),
         fld("M-key", "Nur eine Lage möglich (gedreht geht es nicht)", "select", GOOD3("ja, nur eine Lage", "geht auch gedreht, mit Kraft", "geht gedreht ohne Kraft")),
         fld("M-seat", "Sitz bis zum Boden", "select", GOOD3("sinkt bis zum Boden", "klemmt in den Ecken", "klemmt an einer Wand")),
         fld("M-wob", "Wackeln des Gebäudes in der Mulde", "select", GOOD3("kein spürbares Wackeln", "leichtes Wackeln", "wackelt deutlich"))])
    add("W", "Winkelleiste und Dock", "W", "Sitzt die Winkelleiste in der Oberplatte, und ist hinter den Lötenden genug Platz, damit die Adern nach unten fallen?",
        ["Oberplatte umdrehen, sodass die <b>Unterseite</b> oben liegt. Die Winkelleiste mit den <b>Pins zuerst</b> in die Tasche schieben: Pins durch den Muldenboden, Lötenden nach hinten in den Schlitz. Im Bild den Regler ziehen.",
         "Liegt der Körper flach, treten die vier Pins gerade aus den Löchern, drücken die <b>Rippen</b> den Körper nach vorn? Kippt er, wenn du mit dem Finger von unten dagegendrückst? Notfalls ein Tropfen Heißkleber.",
         "Adern an die Lötenden halten (oder anlöten) und nach unten hängen lassen: Ist in der <b>Kabelnische</b> (24 × 19 mm) genug Platz, und fallen sie frei nach unten?"],
        [("svg", "dock", "Schnitt durch die Pinreihe: Körpertasche, Schlitz und die Kabelnische (1,6 mm hoch).")],
        [fld("W-body", "Körper in der Tasche", "select", GOOD3("liegt flach, sitzt fest", "leicht schief", "kippt oder wackelt")),
         fld("W-ribs", "Rippen (Stirnseiten und hinten)", "select", GOOD3("halten den Körper ohne Kippen", "Körper sitzt, aber mit Spiel", "klemmen oder helfen nicht")),
         fld("W-pins", "Pins treten gerade aus den Löchern", "select", GOOD3("ja, alle vier", "einzelne schief", "klemmen")),
         fld("W-step", "Lötende unter der Stufe", "select", GOOD3("liegt frei und flach", "streift die Stufe", "klemmt")),
         fld("W-niche", "Platz hinter den Lötenden (Kabelnische)", "select", GOOD3("genug, Adern fallen frei nach unten", "knapp", "zu wenig")),
         fld("W-glue", "Heißkleber nötig, damit der Körper hält?", "select", R_YN("nein", "ja, ein Tropfen")),
         fld("W-hold", "Winkelleiste hält beim Hin- und Herwackeln", "select", GOOD3("fest", "leichtes Spiel", "locker"))])
    add("U", "Oberplatte auf den Unterkasten", "U", "Passen Zapfen, Steg und Eckaussparungen? Bis hierher ohne Faden, nur mit den Händen.",
        ["Unterkasten auf den Tisch legen, die Oberplatte (Winkelleiste drin) mit der Unterseite nach unten darübersetzen: <b>Zapfen in die Löcher</b>. Im Bild den Regler ziehen.",
         "Liegt die Oberplatte rundum flach auf? Wackelt sie seitlich? Dann von der Seite durch die Eckaussparungen und das Kabelfenster schauen: Ist unter dem Körper der Winkelleiste etwa 1 mm Luft zum <b>Steg</b>, und stößt nichts an?",
         "Die Adern der Lötenden durch die Nische nach unten und aus dem <b>Kabelfenster</b> in der Vorderwand führen."],
        [("svg", "zapfen", "Schnitt quer bei y = 8: Zapfen mit Fase in einem Loch mit 0,15 Spiel."), ("img", PREV2 + "/zusammenbau_schnitt.png", "Schnitt durch die Pinreihe, zusammengebaut (links) und auseinandergezogen (rechts).")],
        [fld("U-pin", "Zapfen in den Löchern", "select", R_FIT),
         fld("U-flat", "Oberplatte liegt flach auf", "select", GOOD3("rundum flach, kein Spalt", "kleiner Spalt an einer Stelle", "klafft")),
         fld("U-wob", "Seitliches Wackeln der Teile gegeneinander", "select", GOOD3("kein spürbares Wackeln", "leichtes Spiel", "wackelt deutlich")),
         fld("U-step", "Steg unter dem Körper (1,2 mm Luft)", "select", GOOD3("Luft sichtbar, nichts stößt an", "streift den Körper", "stößt an, Oberplatte sitzt nicht")),
         fld("U-win", "Kabelfenster und Eckaussparungen", "select", GOOD3("Kabel gehen frei heraus", "knapp", "zu klein")),
         fld("U-cable", "Adern: hängen sie ohne Knick durch die Nische nach unten", "select", GOOD3("ja, ohne Knick", "leichter Knick", "knicken stark"))])
    add("F", "Faden an den Ecken", "F", "Der Test der beiden Winkel: Läuft der Faden durch das V, und zieht er die Oberplatte auf den Unterkasten?",
        ["Im Bild die Variante wählen. Den Faden mit einer Nadel (oder einem Draht als Schlaufe) <b>von unten in einen Trichter</b> stecken, durch den Kanal über die Lasche ziehen und durch den anderen Trichter wieder heraus.",
         "Das an einem V <b>links (53°)</b> und an einem V <b>rechts (40°)</b>. Wie leicht lässt sich einfädeln? Läuft der Faden glatt, oder kratzt er an den Stufen im Kanal?",
         "Oberplatte auf den Unterkasten setzen, die Fadenenden durch die <b>Eckaussparungen</b> nach unten hängen lassen und an zwei Ecken (je einer pro Winkel) <b>anziehen</b>, etwa an einem Stück Karton als Hut. Zieht der Faden die Oberplatte fest auf den Unterkasten?"],
        [("svg", "faden", "Schnitt durch eine Ecke. Der Überhang je Schicht ist beim 40°-V größer: Das ist der Druck-Test."), ("img", PREV2 + "/faden_v.png", "Schnitt durch das V links (53°) und rechts (40°) im Modell.")],
        [fld("F-53-in", "V links (53°): Einfädeln", "select", R_V),
         fld("F-53-fr", "V links (53°): Faden beim Ziehen", "select", GOOD3("läuft glatt", "kratzt an Stufen", "klemmt")),
         fld("F-40-in", "V rechts (40°, flacher): Einfädeln", "select", R_V),
         fld("F-40-fr", "V rechts (40°): Faden beim Ziehen", "select", GOOD3("läuft glatt", "kratzt an Stufen", "klemmt")),
         fld("F-best", "Welcher Winkel gefällt besser?", "select", opts([("", "– bitte wählen –"), ("a", "40° (flacher)"), ("b", "53°"), ("c", "kein Unterschied")])),
         fld("F-pull", "Anziehen: Oberplatte auf dem Unterkasten", "select", GOOD3("zieht fest auf, hält", "bleibt ein Spalt", "gibt nach oder reißt aus")),
         fld("F-notch", "Faden in der Eckaussparung", "select", GOOD3("hängt frei", "streift die Wand", "verklemmt"))])
    add("S", "Stecken", "S", "Der Kern des Tests: Treffen die Pins die Buchse ohne Trichter, und wie weit rutscht die Buchse dabei nach oben?",
        ["Bestückte Kassette ins Gebäude drücken (Schritt E), Gebäude auf die Oberplatte setzen, bis es unten anliegt. Im Bild den Regler ziehen.",
         "Beim Aufstecken beobachten: gehen alle vier Pins gleichzeitig hinein, oder muss man suchen oder rütteln?",
         "Gebäude wieder abziehen und die <b>Unterkante der Buchse</b> gegen die Fußunterkante des Gebäudes halten: bündig, oder nach oben gerutscht? Abstand in mm schätzen (bündig = 0)."],
        [("svg", "stecken", "Schnitt längs durch die Pin-Reihe: Regler zieht das Gebäude ab."), ("svgcall", "luft", "Luft unter der Buchse kostet Einstecktiefe.")],
        [fld("S-hit", "Pins treffen die Buchse", "select", GOOD3("ohne Kraft, alle vier gleichzeitig", "mit leichtem Suchen oder Rütteln", "verkantet, einzelne Pins bleiben hängen", "geht nicht")),
         fld("S-force", "Kraft zum Aufstecken", "select", GOOD3("leicht", "mittel", "viel")),
         fld("S-luft", "Abstand Buchsenunterkante zur Fußunterkante in mm (bündig = 0)", "text", ph="z. B. 0,1"),
         fld("S-seat", "Gebäude nach dem Aufstecken", "select", GOOD3("sitzt fest, kein Wackeln", "leichtes Wackeln", "wackelt deutlich")),
         fld("S-base", "Oberplatte beim Aufstecken", "select", GOOD3("bleibt liegen, nichts biegt sich", "federt sichtbar", "hebt sich mit ab"))],
        calc="S")
    add("D", "Durchgang und Abziehen", "D", "Hält der Kontakt stabil, und bleibt alles beim zehnmaligen Abziehen an seinem Platz?",
        ["Multimeter auf Durchgang: eine Spitze an das <b>Lötende</b> der Winkelleiste (waagrechter Pin hinten in der Nische), die andere an die Ader des passenden Kontakts. Für alle vier Pins.",
         "Dabei das Gebäude seitlich um etwa 0,5 mm schieben und leicht kippen. Bleibt der Durchgang stabil?",
         "Dann das Gebäude <b>zehnmal</b> abziehen und wieder aufstecken. Bleibt die Kassette im Gebäude, die Buchse in der Kassette, die Oberplatte auf dem Unterkasten? Gibt es danach noch Durchgang?"],
        [],
        [fld("D-1", "Durchgang", "select", K_PASS),
         fld("D-kass", "Nach 10× Abziehen: Kassette bleibt im Gebäude", "select", GOOD3("ja, immer", "rutscht ein Stück heraus", "kommt heraus")),
         fld("D-buchse", "Nach 10× Abziehen: Buchse bleibt in der Kassette", "select", GOOD3("ja, immer", "rutscht etwas nach unten mit", "kommt mit den Pins heraus")),
         fld("D-base", "Nach 10× Abziehen: Oberplatte und Unterkasten", "select", GOOD3("bleiben fest zusammen", "Spiel entsteht", "lösen sich")),
         fld("D-dg", "Durchgang nach 10× Abziehen", "select", GOOD3("unverändert stabil", "wird schlechter", "bricht ab")),
         fld("D-pull", "Kraft zum Abziehen des Gebäudes aus der Mulde", "select", GOOD3("leicht", "mittel, hält gut", "sehr fest"))])
    add("L", "Adern, LED und Licht", "L", "Laufen die Adern im Bogen über das Podest, liegt die LED flach? Optional leuchtet sie.",
        ["Adern der Buchse durch den Schlitz nach oben führen und im <b>Bogen über die gerundete Kante</b> auf das Podest legen.",
         "<b>LED-Streifen 10 mm</b> auf das Podest legen (Chips nach oben, Pads zur Buchse hin).",
         "Optional: Controller an die Lötenden in der Nische anschließen und die LED leuchten lassen (Pin 1 GND, 2 DIN, 3 +5 V, 4 DETECT)."],
        [],
        [fld("L-wire", "Adern über die runde Kante", "select", GOOD3("liegen im Bogen, kein Knick", "leichter Knick", "knicken stark", "keine Adern dran")),
         fld("L-led", "LED-Streifen auf dem Podest", "select", GOOD3("liegt flach, passt gut", "knapp", "passt nicht")),
         fld("L-light", "Licht (optional)", "select", opts([("", "– nicht geprüft –"), ("a", "leuchtet stabil"), ("b", "flackert beim Wackeln"), ("c", "leuchtet nicht")]))],
        optional=True)
    add("z", "Abschluss", "Σ", "Zum Schluss ein Gesamteindruck. Danach unten den Text kopieren und mir schicken.",
        ["Überlege, ob der Zwei-Lagen-Aufbau so für die große Platte taugt und was als Nächstes passiert."],
        [],
        [fld("z-aufbau", "Zwei-Lagen-Aufbau (Oberplatte auf Unterkasten)", "select", opts([("", "– bitte wählen –"), ("a", "taugt, so für die große Platte"), ("b", "taugt mit Änderungen (Freitext)"), ("c", "taugt nicht")])),
         fld("z-niche", "Kabelnische", "select", opts([("", "– bitte wählen –"), ("a", "reicht, so lassen"), ("b", "größer"), ("c", "kleiner reicht")])),
         fld("z-v", "Faden-V", "select", opts([("", "– bitte wählen –"), ("a", "53° behalten"), ("b", "40° nehmen"), ("c", "anderer Winkel oder anderes Konzept (Freitext)")])),
         fld("z-boden", "Muldenboden 0,4", "select", opts([("", "– bitte wählen –"), ("a", "reicht, so lassen"), ("b", "auf 0,6 erhöhen"), ("c", "dünner nötig")])),
         fld("z-next", "Was als Nächstes", "select", opts([("", "– bitte wählen –"), ("a", "Fachprobe Powerbank"), ("b", "Werte nach plug/parts.py, große Platte im Generator bauen"),
                                                            ("c", "Steckprobe 3 mit Änderungen"), ("d", "Kassetten-Redesign einarbeiten")]))])


def render_diagram(step):
    out = []
    for kind, key, cap in step["diagrams"]:
        if kind == "img":
            out.append('<figure class="dg"><img src="%s" alt="%s"><figcaption>%s</figcaption></figure>' % (img_uri(key, 900), cap, cap))
            continue
        if kind == "svgcall":
            svg = dict(top=svg_mulde_top, luft=svg_luft)[key]()
            out.append('<figure class="dg"><div class="dgbox">%s</div><figcaption>%s</figcaption></figure>' % (svg, cap))
            continue
        svg = dict(aufbau=lambda: svg_section2("aufbau"), stecken=lambda: svg_section2("stecken"), bestuecken=svg_bestuecken, press=svg_press,
                   dock=svg_dock, zapfen=svg_zapfen, faden=svg_faden)[key]()
        ctl = ""
        if key == "aufbau":
            ctl = '<label class="rng">Zusammenbau <input type="range" class="dgr" min="0" max="100" value="0" data-for="A-ALL" aria-label="Zusammenbau"></label>'
        elif key == "bestuecken":
            ctl = '<label class="rng">Kassette absenken <input type="range" class="dgr" min="0" max="100" value="0" data-for="K-mov" aria-label="Kassette absenken"></label>'
        elif key == "press":
            ctl = '<label class="rng">Kassette eindrücken <input type="range" class="dgr" min="0" max="100" value="0" data-for="E-mov" aria-label="Kassette eindrücken"></label>'
        elif key == "dock":
            ctl = '<label class="rng">Winkelleiste einschieben <input type="range" class="dgr" min="0" max="100" value="0" data-for="W-mov" aria-label="Winkelleiste einschieben"></label>'
        elif key == "zapfen":
            ctl = '<label class="rng">Oberplatte aufsetzen <input type="range" class="dgr" min="0" max="100" value="0" data-for="Z-mov" aria-label="Oberplatte aufsetzen"></label>'
        elif key == "faden":
            ctl = '<label class="sel">Winkel <select class="dgvar" data-group="FV"><option value="53" selected>links: 53° (Plan)</option><option value="40">rechts: 40° (flacher)</option></select></label>'
        else:
            ctl = '<label class="rng">Gebäude aufstecken <input type="range" class="dgr" min="0" max="100" value="100" data-for="T-mov" aria-label="Gebäude aufstecken"></label>'
        if key != "faden":
            ctl += '<button type="button" class="play" data-play="1">Abspielen</button>'
        out.append('<figure class="dg" data-key="%s"><div class="dgbox">%s</div><div class="dgctl">%s</div><figcaption>%s</figcaption></figure>' % (key, svg, ctl, cap))
    return "".join(out)


def build_steps_html():
    out, nav, spec = [], [], []
    for st in STEPS:
        instr = "".join("<li>%s</li>" % x for x in st["instr"])
        form = "".join(render_field(f) for f in st["fields"])
        opt = ' <span class="opt">optional</span>' if st["optional"] else ""
        dg = render_diagram(st)
        out.append(
            '<section class="step" id="s-%s" data-step="%s"><header><span class="tg">%s</span><h2>%s%s</h2><span class="done" aria-hidden="true"></span></header>'
            '<p class="lead">%s</p><div class="cols"><ol class="how">%s</ol><div style="display:flex;flex-direction:column;gap:12px;min-width:0">%s</div></div>'
            '<form class="fb" onsubmit="return false"><h3>Feedback</h3><div class="grid">%s'
            '<label class="fld wide" for="f-%s-free"><span>Notizen, Auffälligkeiten (Freitext)</span><textarea id="f-%s-free" data-fid="%s-free" rows="2" placeholder="alles, was nicht in die Auswahl passt"></textarea></label>'
            '</div></form></section>' % (st["id"], st["id"], st["tag"], st["title"], opt, st["lead"], instr, dg, form, st["id"], st["id"], st["id"]))
        nav.append('<a href="#s-%s" data-nav="%s" title="%s">%s</a>' % (st["id"], st["id"], st["title"], st["tag"]))
        spec.append(dict(id=st["id"], tag=st["tag"], title=st["title"], optional=st["optional"],
                         items=[dict(id=f["id"], label=f["label"], kind=f["kind"],
                                     map={x["v"]: x["t"] for x in f["opts"] if x["v"]}) for f in st["fields"]] + [dict(id=st["id"] + "-free", label="Notizen", kind="text", map={})],
                         calc=st["calc"]))
    return "\n".join(out), "".join(nav), spec


def main():
    steps()
    html, nav, spec = build_steps_html()
    with open(TEMPLATE, encoding="utf-8") as f:
        page = f.read()
    for k, v in {"{{STEPS}}": html, "{{NAV}}": nav, "{{SPEC}}": json.dumps(spec, ensure_ascii=False)}.items():
        page = page.replace(k, v)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(page)
    print("geschrieben: %s (%d kB), %d Schritte, %d Felder" % (os.path.relpath(OUT, ROOT), os.path.getsize(OUT) / 1024, len(STEPS),
                                                              sum(len(s["fields"]) for s in STEPS)))


if __name__ == "__main__":
    main()
