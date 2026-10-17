#!/usr/bin/env python3
"""Archiv, Stand 1 des Plans (Vergleich der Varianten A bis D, Empfehlung C): baut plug/thread/plan1.html aus plan.template.html.
Der aktuelle Plan (Stand 2, Variante A als halbe Pille mit Steg) steht in build_plan.py.

Alle Maße kommen aus plug/thread/params.py (Vorschläge, ungetestet). Die Zeichnungen sind Schemazeichnungen im Maßstab, gerechnet aus denselben Werten,
keine Ausgabe einer STL (es gibt noch keine). Die Zahlen der Einfädelprobe stehen in plug/thread/reach.json (Erzeugung: `python3 -m plug.thread.reach --write`).

Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m plug.thread.build_plan1     # schreibt plug/thread/plan1.html
"""
import json
import math
import os

from plug.feedback.build import G
from plug.thread import params as P
from plug.thread import reach as R

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TEMPLATE = os.path.join(HERE, "plan.template.html")
OUT = os.path.join(HERE, "plan1.html")


def de(x, n=2):
    return ("%.*f" % (n, x)).replace(".", ",")


def reach_table():
    try:
        with open(R.JSON, encoding="utf-8") as f:
            return json.load(f)
    except OSError:
        return {}


RT = reach_table()


def reach_len(key, nd=1.2):
    v = RT.get("%s|%.1f" % (key, nd))
    return v


def pts(poly):
    return list(poly.exterior.coords)


# --------------------------------------------------------------------------
# abgeleitete Zahlen
# --------------------------------------------------------------------------
def wedge(v):
    """Keil zwischen den Schenkeln des V: Basis und Höhe (mm) und Wand über dem Scheitel."""
    hs = v["apex"] * v["slope"]
    th = math.atan2(1.0, v["slope"])
    off = v["leg_d"] / 2 / math.sin(th)
    base = max(0.0, 2 * (hs - off))
    height = max(0.0, v["apex"] * (1 - off / hs))
    return dict(hs=hs, base=base, height=height, roof=P.PLATE_T - (v["apex"] + v["leg_d"] / 2))


def notch_sizes():
    a = P.A
    hsa = a["apex"] * a["slope"]
    b = P.B
    hsb = b["apex"] * b["slope"]
    c = P.C
    pad = 4.0
    return dict(
        A=(2 * (hsa + a["entry_r"]) + 2 * 0.4, 2 * a["entry_r"] + 2 * 0.4),
        B=(2 * (hsb + b["groove_w"] / 2 / math.sin(math.atan2(1, b["slope"]))) + 2 * 0.4, 6.0),
        C=(c["spacing"] + 2 * c["entry_r"] + 2 * pad, c["run"] + c["entry_r"] + pad),
        D=(P.D["shaft_d"] + 2 * 2.0, P.D["shaft_d"] + 2 * 2.0))


# --------------------------------------------------------------------------
# Zeichnungen
# --------------------------------------------------------------------------
def thread_line(g, points, cls="d-thread"):
    g.o.append('<polyline points="%s" class="%s"/>' % (" ".join("%.1f,%.1f" % (g.X(x), g.Z(z)) for x, z in points), cls))


def thick(g, p0, p1, d, cls="d-needle"):
    g.o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="%s" style="stroke-width:%.1f"/>' % (g.X(p0[0]), g.Z(p0[1]), g.X(p1[0]), g.Z(p1[1]), cls, d * g.S))


def svg_tunnel(v, key=None, nd=1.2, needle=True, bars=True, label="", support=False):
    """Schnitt durch den geschlossenen V-Kanal (x entlang der V-Achse, z Höhe über der Plattenunterseite) mit Faden-Weg, Keil und einer 45-mm-Nadel."""
    S = 17.0
    zt, zb = 10.0, -6.0
    g = G(S, 13 * S + 8, zt * S + 8)
    hs = v["apex"] * v["slope"]
    r = v["leg_d"] / 2
    w = wedge(v)
    g.rect(-13, 13, 0, zt, "d-slab")
    g.rect(-13, -R.FREE_X, zb, 0, "d-under")
    g.rect(R.FREE_X, 13, zb, 0, "d-under")
    g.poly(pts(R.tunnel(v["leg_d"], v["apex"], v["slope"], v["entry_r"])), "d-void")
    if support:
        g.poly(pts(R.tunnel(v["leg_d"], v["apex"], v["slope"], v["entry_r"])), "d-sup")
    thread_line(g, [(-hs - 0.6, zb), (-hs, 0.0), (0.0, v["apex"]), (hs, 0.0), (hs + 0.6, zb)])
    if needle:
        n = math.hypot(hs, v["apex"])
        u = (hs / n, v["apex"] / n)
        tip = (0.0 + (r - nd / 2) * u[0], v["apex"] + (r - nd / 2) * u[1])
        ln = (tip[1] - zb) / u[1]
        tail = (tip[0] - ln * u[0], tip[1] - ln * u[1])
        thick(g, tail, tip, nd)
        g.o.append('<circle cx="%.1f" cy="%.1f" r="9" class="d-stop"/>' % (g.X(tip[0] + 0.5 * u[0]), g.Z(tip[1] + 0.5 * u[1])))
        g.text(-12.7, 8.4, "Nadel stößt am Scheitel an", "dlw", "start")
        g.text(-12.7, 7.4, "(Spitze kann nicht um die Kurve)", "dls", "start")
    if w["height"] > 0.3:
        g.text(0, w["height"] / 2 - 0.2, "Keil", "dlb")
        g.text(0, w["height"] / 2 - 1.0, "trägt den Zug", "dls")
    g.text(12.7, -2.6, "Unterkasten", "dls", "end")
    g.text(-12.7, -2.6, "Unterkasten", "dls", "start")
    g.text(0, zb + 0.5, "Faden von unten", "dln")
    g.text(12.7, zt - 0.8, "Platte (oben abgeschnitten)", "dls", "end")
    h = int((zt - zb) * S + 16)
    if bars:
        h += 70
        _bars(g, h - 62, key, nd)
    return g.svg(int(26 * S + 16), h, label or "Schnitt durch den V-Kanal")


def _bars(g, y0, key, nd):
    """Balken: längste Nadel, die sich durchführen lässt, gegen eine 45-mm-Nadel (eigener Maßstab 4 px je mm)."""
    sc = 4.0
    ln = reach_len(key, nd) if key else None
    g.o.append('<text x="8" y="%.0f" class="dls">längste Nadel, die durchkommt</text>' % (y0 + 12))
    x0 = 190.0
    g.o.append('<rect x="%.0f" y="%.0f" width="%.1f" height="10" class="bar-g"/>' % (x0, y0 + 3, max(0.0, (ln or 0)) * sc))
    g.o.append('<text x="%.0f" y="%.0f" class="dlb">%s</text>' % (x0 + max(0, (ln or 0)) * sc + 6, y0 + 12, ("%d mm" % ln) if ln else "keine"))
    g.o.append('<text x="8" y="%.0f" class="dls">Stopfnadel (45 mm)</text>' % (y0 + 36))
    g.o.append('<rect x="%.0f" y="%.0f" width="%.1f" height="10" class="bar-m"/>' % (x0, y0 + 27, 45 * sc))
    g.o.append('<text x="%.0f" y="%.0f" class="dls">45 mm</text>' % (x0 + 45 * sc + 6, y0 + 36))


def svg_wall_b():
    """B: Ansicht von außen auf die Seitenwand mit der Λ-Nut, daneben der Schnitt durch die Nut."""
    b = P.B
    S = 18.0
    hs = b["apex"] * b["slope"]
    th = math.atan2(1.0, b["slope"])
    half = b["groove_w"] / 2 / math.sin(th)
    g = G(S, 11 * S, 10.5 * S + 8)
    g.rect(-11, 11, 0, 10.0, "d-slab")
    g.rect(-11, -9, -3.5, 0, "d-under")
    g.rect(9, 11, -3.5, 0, "d-under")
    # Nut als Λ-Streifen um die Mittellinie
    cl = [(-hs - 1.5 * b["slope"], -0.5), (0.0, b["apex"]), (hs + 1.5 * b["slope"], -0.5)]
    from shapely.geometry import LineString
    groove = LineString(cl).buffer(b["groove_w"] / 2, join_style=1, cap_style=2)
    from shapely.geometry import box as sbox
    groove = groove.intersection(sbox(-11, 0, 11, 10))
    g.poly(pts(groove), "d-open")
    thread_line(g, [(-hs - 0.2, 0.0), (0.0, b["apex"]), (hs + 0.2, 0.0)], "d-threads")
    g.text(0, b["apex"] + b["groove_w"] / 2 + 0.9, "Λ-Nut, Tiefe %s" % de(b["depth"], 1), "dls")
    g.text(0, b["apex"] / 2 - 0.4, "Wand bleibt", "dls")
    g.text(0, -2.2, "Eckaussparung unten", "dls")
    g.text(-10.8, 9.0, "Seitenwand von außen", "dls", "start")
    g.o.append('<g></g>')
    return g.svg(int(22 * S + 8), int(13.6 * S + 16), "Ansicht von außen auf die Seitenwand mit der Λ-Nut und dem Faden")


def svg_groove_b_section():
    b = P.B
    S = 14.0
    g = G(S, 2.0 * S + 8, 10.5 * S + 8)
    g.rect(0, 12, 0, 10, "d-slab")
    g.rect(0, b["depth"], b["apex"] - b["groove_w"] / 2, b["apex"] + b["groove_w"] / 2, "d-open")
    g.o.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="var(--f-wire)" stroke="none"/>' % (g.X(b["depth"] * 0.5), g.Z(b["apex"]), 0.4 * S))
    g.text(b["depth"] + 0.5, b["apex"] + 0.2, "Nut %s breit, %s tief" % (de(b["groove_w"], 1), de(b["depth"], 1)), "dls", "start")
    g.text(-0.3, 10.2, "außen", "dls", "end")
    g.text(0, -0.9, "Schnitt durch die Nut am Scheitel", "dls", "start")
    return g.svg(int(15 * S), int(13 * S), "Schnitt durch die Nut")


def c_geom():
    """Schnitt durch eine Schrägbohrung von C: y vom Wand-Außenrand nach innen, z Höhe über der Plattenunterseite."""
    from shapely.geometry import LineString, Polygon
    from shapely.geometry import box as sbox
    c = P.C
    ax = lambda t: (c["run"] * (1 - t), c["rise"] * t)
    line = LineString([ax(-0.6), ax(1.6)])
    hole = line.buffer(c["hole_d"] / 2, cap_style=2).intersection(sbox(0, -2, 20, P.PLATE_T))
    er = c["entry_r"]
    cone = Polygon([(c["run"] - er, 0), (c["run"] + er, 0), (c["run"] + c["hole_d"] / 2, 1.5), (c["run"] - c["hole_d"] / 2, 1.5)])
    from shapely.ops import unary_union
    return ax, unary_union([hole, cone]).intersection(sbox(0, -0.01, 20, P.PLATE_T))


def svg_c_section(tip_t=None, hole_no=1, needle_vertical=False, thread_mode="none", label=""):
    """C im Schnitt entlang einer Bohrung. tip_t: Lage der Nadelspitze auf der Bohrungsachse (1 = Austritt außen, 0 = Trichter, <0 = unten heraus)."""
    c = P.C
    S = 12.0
    zt, zb = P.PLATE_T + 3.0, -18.0
    g = G(S, 9 * S + 8, zt * S + 8)
    ax, hole = c_geom()
    g.rect(0, 16, 0, P.PLATE_T, "d-slab")
    g.rect(0, 16, zb, zb + 2.0, "d-hat")
    g.rect(14.5, 16, -P.UK_H, 0, "d-under")
    g.poly(pts(hole), "d-void")
    g.text(15.2, -7.2, "Unterkasten", "dls", "end")
    g.text(15.8, zb + 0.6, "Hut (Stoff)", "dls", "end")
    hat = (c["run"] + 1.5, zb + 2.0)
    n = math.hypot(c["run"], c["rise"])
    d = (c["run"] / n, -c["rise"] / n)
    if thread_mode in ("a", "done"):
        thread_line(g, [hat, (c["run"], 0.0), ax(1.0), (-2.5, c["rise"] + 0.2)], "d-thread")
    if thread_mode == "wait":
        thread_line(g, [(-2.5, c["rise"] + 0.2), ax(1.0)], "d-thread")
    if tip_t is not None:
        tip = ax(tip_t)
        tail = (tip[0] - 17 * d[0], tip[1] - 17 * d[1])
        thick(g, tail, tip, P.NEEDLE_D)
    if needle_vertical:
        thick(g, (hat[0], zb + 7.0), (hat[0], zb + 1.0), P.NEEDLE_D)
    g.text(-0.3, 4.5, "außen", "dls", "end")
    g.text(c["run"] + 5.0, 1.6, "Trichter R %s" % de(c["entry_r"], 1), "dls", "start")
    g.text(c["run"] + 5.0, -2.0, "Eckaussparung", "dls", "start")
    g.text(2.0, P.PLATE_T + 0.7, "Loch %d · Ø %s · %d°" % (hole_no, de(c["hole_d"], 1), round(P.angle_c())), "dlb", "start")
    return g.svg(int(25 * S + 16), int((zt - zb) * S + 16), label or "Schnitt durch eine Schrägbohrung")


def svg_c_outside(state="done", needle_hole=None, label=""):
    """C von außen: zwei Austritte mit der Rille dazwischen. state: none, one (Faden aus Loch 1 in der Rille), both."""
    c = P.C
    S = 14.0
    ex = P.exit_span()
    g = G(S, 15 * S + 8, 15.0 * S + 8)
    g.rect(-13, 13, 0, P.PLATE_T, "d-slab")
    g.rect(-13, -11.5, -2.5, 0, "d-under")
    g.rect(11.5, 13, -2.5, 0, "d-under")
    gz0, gz1 = ex["lo"], ex["lo"] + c["groove_w"]
    tz = gz0 + 0.9                                  # der Faden ruht auf der unteren Kante der Rille
    g.rect(-c["spacing"] / 2, c["spacing"] / 2, gz0, gz1, "d-open")
    for s in (-1, 1):
        x = s * c["spacing"] / 2
        g.o.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" class="d-void" style="stroke:var(--ink)"/>' % (g.X(x), g.Z(c["rise"]), c["hole_d"] / 2 * S, ex["height"] / 2 * S))
    x1, x2 = -c["spacing"] / 2, c["spacing"] / 2
    if state == "one":
        thread_line(g, [(x1, c["rise"]), (x1 + 0.4, tz), (x1 + 2.6, tz)], "d-thread")
    if state == "both":
        thread_line(g, [(x1, c["rise"]), (x1 + 0.4, tz), (x2 - 0.4, tz), (x2, c["rise"])], "d-threads")
    if needle_hole:
        x = (x1, x2)[needle_hole - 1]
        thick(g, (x, c["rise"]), (x, c["rise"] + 8.5), P.NEEDLE_D)
    g.text(0, P.PLATE_T + 0.7, "Rille %s tief, der Faden liegt auf ihrer unteren Kante" % de(c["groove_depth"], 1), "dls")
    g.text(0, -1.6, "Eckaussparung (Blick hinein)", "dls")
    g.text(12.7, P.PLATE_T - 1.0, "Seitenwand von außen", "dls", "end")
    g.o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="dimn"/>' % (g.X(x1), g.Z(2.0), g.X(x2), g.Z(2.0)))
    g.text(0, 2.5, "Abstand %s" % de(c["spacing"], 1), "dln")
    g.o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="dimn"/>' % (g.X(x2 + 3.4), g.Z(0.0), g.X(x2 + 3.4), g.Z(c["rise"])))
    g.text(x2 + 3.8, c["rise"] / 2, "Achse %s" % de(c["rise"], 1), "dln", "start")
    return g.svg(int(30 * S + 16), int(17.5 * S + 16), label or "Seitenwand von außen mit zwei Austritten und der Rille")


def svg_d():
    """D: Eckschacht im Unterkasten und Fenster mit Steg in der Plattenunterseite (Schnitt)."""
    S = 18.0
    d = P.D
    ww, wd, wh = d["window"]
    g = G(S, 2 * S + 8, (P.PLATE_T + 1) * S + 8)
    g.rect(0, 18, 0, P.PLATE_T, "d-slab")
    cx = 9.0
    g.rect(cx - ww / 2, cx + ww / 2, 0, wh, "d-void")
    g.rect(0, cx - d["shaft_d"] / 2, -9.0, 0, "d-under")
    g.rect(cx + d["shaft_d"] / 2, 18, -9.0, 0, "d-under")
    g.rect(0, 18, -11.0, -9.0, "d-hat")
    zc = wh - 2.0 - d["bar_d"] / 2 - 0.3
    g.o.append('<circle cx="%.1f" cy="%.1f" r="%.1f" class="d-slab" style="stroke:var(--ink)"/>' % (g.X(cx), g.Z(zc), d["bar_d"] / 2 * S))
    gx = d["shaft_d"] / 2 - 1.0
    thread_line(g, [(cx - gx, -10.0), (cx - gx, zc), (cx - 1.9, zc + 1.9), (cx + 1.9, zc + 1.9), (cx + gx, zc), (cx + gx, -10.0)])
    g.text(cx, 4.3, "Steg Ø %s" % de(d["bar_d"], 1), "dls")
    g.text(cx, wh + 0.9, "Fenster %s × %s × %s" % (de(ww, 0), de(wd, 0), de(wh, 0)), "dls")
    g.text(cx, -4.5, "Schacht Ø %s im Eckpfosten" % de(d["shaft_d"], 0), "dls")
    g.text(cx, -10.7, "Hut", "dls")
    return g.svg(int(22 * S + 8), int((P.PLATE_T + 12.5) * S + 8), "Schnitt: Eckschacht und Fenster mit Steg")


# --------------------------------------------------------------------------
# Bausteine der Seite
# --------------------------------------------------------------------------
def fig(svg, caption, cls="s460"):
    return '<figure class="fig"><div class="figbox %s">%s</div><figcaption>%s</figcaption></figure>' % (cls, svg, caption)


def stepper(sid, frames, names):
    """frames: Liste von (html, Beschriftung). Ein Regler schaltet zwischen den Schritten um."""
    fr = "".join('<div class="fr"%s>%s<p class="cap">%s</p></div>' % ("" if i == 0 else " hidden", h, c) for i, (h, c) in enumerate(frames))
    return ('<div class="stepper" id="%s"><div class="dgctl"><label for="%s-r">Schritt <input type="range" class="stp" id="%s-r" min="0" max="%d" step="1" value="0" data-names="%s" aria-label="Schritt wählen"></label>'
            '<output>%s</output></div>%s</div>' % (sid, sid, sid, len(frames) - 1, "|".join(names), names[0], fr))


def badge(kind, text):
    return '<span class="badge b-%s">%s</span>' % (kind, text)


def head():
    return ('<header class="top"><p class="kicker">Steckmechanismus · nach Steckprobe 2 (r4)</p><h1>Fadenführung an den Plattenecken</h1>'
            '<p class="lead">Plan für ein eigenes Testteil. Der Faden ging durch keines der beiden V-Kanäle. Hier steht, warum das so war, welche vier Wege es gibt, '
            'welchen ich empfehle und wie der Faden dann eingefädelt wird. Gelesen vorher: <code>plug/logbook/lessons.md</code>, <code>current.md</code>, '
            '<code>tasks/faden-v-ueberarbeiten.md</code>, <code>rounds/r4_steckprobe2/summary.md</code>. <b>Es gibt noch keine STL.</b></p>'
            '<ul class="sum">'
            '<li><b>Befund:</b> Das V war ein geschlossener, gebogener Tunnel. Eine gerade Nadel kommt durch so eine Kurve nicht, auch nicht bei Ø 4 mm: gerechnet höchstens %s mm lang, eine Stopfnadel hat 45 mm.</li>'
            '<li><b>Wirkung des Fadens:</b> Der Faden liegt über dem Keil zwischen den Schenkeln und zieht ihn nach unten. Die Decke über dem Kanal trägt nichts.</li>'
            '<li><b>Empfehlung C:</b> zwei gerade Schrägbohrungen von der Eckaussparung zur Seitenwand, die Scheitelstrecke liegt in einer Rille außen. Jeder Nadelgang ist gerade; nichts an der Oberseite.</li>'
            '<li><b>Test:</b> ein Druck mit drei Eckmustern (A, B, C) aus Plattenecke und Unterkasten-Ecke. Neue Werte nur in <code>plug/thread/params.py</code>.</li></ul></header>'
            % (reach_len("A", 1.2) or "6"))


def sec_befund():
    rows = [("Faden geht durch keines der V (53° und 40°)", "Kanal Ø 2,2 zu eng; Faden bleibt im untertauchenden Teil stecken", "L32"),
            ("Trichter (Öffnungen) in Ordnung", "Trichter bleiben, werden eher größer", "L32"),
            ("„Ist ja auch ein Overhang“: Einfädeln scheitert an der Decke des Kanals", "Support ist erlaubt; Böschungsrücksichten entfallen", "L32, L33"),
            ("Nutzer: mindestens 1 mm mehr, besser Ø 3,2 oder mehr", "hier Ø 3,6 bis 4,0, plus die Frage, ob ein Tunnel überhaupt sein muss", "L32"),
            ("Winkel 53° gegen 40° nicht entschieden", "entfällt als Frage: bei gerader Bohrung zählt der Winkel nicht für das Einfädeln", "–"),
            ("Faden zunächst oben austretend geplant", "Eintritt, Austritt und Zugänglichkeit im Schnitt zeigen (hier: Einfädel-Regler)", "L29"),
            ("Plan ohne Maßkette für den Einfädelvorgang", "Worst-Case-Tabelle unten, Nadel und Faden als Rückfrage", "L23, L24")]
    trs = "".join('<tr><td>%s</td><td>%s</td><td class="n">%s</td></tr>' % r for r in rows)
    vor = ('<ul class="q"><li>Platte wird an einen Doktorhut <b>genäht</b>: vier Fäden an den Ecken, der Boden wird nach unten genäht und drückt die Oberplatte auf den Unterkasten. <b>Keine Schrauben.</b></li>'
           '<li>Der Faden tritt <b>nicht an der Oberseite</b> aus. Er kommt von unten, läuft durch einen breiten Trichter und wieder nach unten.</li>'
           '<li><b>Support ist erlaubt</b> (der Nutzer bereinigt einmal). Kleine Überhänge sind kein Grund mehr, einen Kanal eng zu halten.</li>'
           '<li>Nicht angefasst: <code>plug/testcase/build2.py</code>, Dock-Nische, Zapfen, Schachttiefe. Alles Neue liegt in <code>plug/thread/</code>.</li></ul>')
    return ('<section class="sec"><h2>Ausgangslage</h2><div class="tw"><table class="t"><thead><tr><th>Befund aus Steckprobe 2</th><th>Folge für diesen Plan</th><th>Lehre</th></tr></thead><tbody>%s</tbody></table></div>%s</section>' % (trs, vor))


def sec_why():
    old = P.OLD
    fig1 = fig(svg_tunnel(old, key="alt", label="Der alte V-Kanal im Schnitt mit einer Nadel, die am Scheitel anstößt"),
               "Der alte Kanal (Ø 2,2, Scheitel 3,4) im Maßstab. Der Faden (rot gestrichelt) liegt über dem Keil. Die Nadel geht den linken Schenkel hinauf und stößt an der Decke an; weiter kommt die Spitze nicht, ohne dass sich die Nadel biegt.")
    names = ["alt: Ø 2,2", "A: Ø 4,0", "A: Ø 5,0", "A: steil 70°"]
    keys = [("alt", P.OLD), ("A", P.A), ("A5", dict(P.A, leg_d=5.0)), ("A70", dict(P.A, slope=0.36))]
    frames = []
    for (key, v), nm in zip(keys, names):
        ln = reach_len(key, 1.2)
        txt = "<b>%s</b> · Schenkel %d° zur Waagerechten · Scheitel %s mm · " % (nm, round(P.slope_deg(v["slope"])), de(v["apex"], 1))
        txt += ("längste Nadel, die sich durchführen lässt: <b>%d mm</b>" % ln) if ln else "schon eine 2-mm-Nadel kommt nicht durch"
        frames.append((fig(svg_tunnel(v, key=key, needle=False, label="V-Kanal " + nm), "", "s460"), txt))
    st = stepper("kanal", frames, names)
    tab = []
    for key, nm, v in R.ROWS:
        cells = []
        for _, nd in P.NEEDLES:
            val = reach_len(key, nd)
            cells.append('<td class="c">%s</td>' % (("%d mm" % val) if val else "keine"))
        tab.append("<tr><td>%s</td><td class=\"n\">Ø %s · %d°</td>%s</tr>" % (nm, de(v["leg_d"], 1), round(P.slope_deg(v["slope"])), "".join(cells)))
    hdr = "".join("<th>%s Ø %s</th>" % (n, de(d, 1)) for n, d in P.NEEDLES)
    return ('<section class="sec"><h2>Warum das V nicht ging</h2><div class="two">%s<div style="display:flex;flex-direction:column;gap:10px">'
            '<p class="note">Das V ist ein <b>geschlossener, gebogener Tunnel</b>. Der Faden selbst ist biegsam, aber er muss von einer Nadel oder einem Draht geführt werden, und die sind gerade. '
            'Der Tunnel knickt am Scheitel um mehr als 100°. Ich habe nachgerechnet, wie lang eine gerade Nadel höchstens sein darf, damit die Spitze von der einen Mündung zur anderen kommt.</p>'
            '<p class="note">Ergebnis: <b>keine übliche Nähnadel passt durch irgendein V</b> dieser Größe. Mehr Durchmesser hilft nur wenig, ein steilerer Winkel etwas mehr, aber eine 45-mm-Stopfnadel nie. '
            'Der Nutzer hat also zu Recht „mehr Spiel“ verlangt, doch mehr Spiel allein löst das Einfädeln nicht.</p></div></div>'
            '<h3>Regler: Kanalform und längste Nadel</h3>%s'
            '<div class="tw"><table class="t"><thead><tr><th>Kanalform</th><th>Maße</th>%s</tr></thead><tbody>%s</tbody></table></div>'
            '<p class="note">Rechnung im Schnitt (<code>plug/thread/reach.py</code>): Nadel als Strecke mit Durchmesser, Spitze bleibt im Kanal, Zusammenhang im Raum Spitze × Winkel, Raster 0,2 mm, Angaben auf 2 mm genau. '
            'Quer zur Schnittebene ist der Kanal nur so breit wie in der Ebene, die Nadel kann dort nicht ausweichen; das ist die ungünstigste Ebene, also eine ehrliche Obergrenze.</p></section>'
            % (fig1, st, hdr, "".join(tab)))


def sec_options():
    a, b, c, dd = P.A, P.B, P.C, P.D
    wa = wedge(a)
    nz = notch_sizes()
    ex = P.exit_span()
    figA = fig(svg_tunnel(a, key="A", nd=1.2, support=False, label="Option A: weiter V-Kanal"),
               "A: Ø %s, Scheitel %s, Schenkel %d°, Trichter R %s. Die Nadel stößt weiterhin an (grün: Nadel, die durchkäme, nur %s mm lang)." % (de(a["leg_d"], 1), de(a["apex"], 1), round(P.slope_deg(a["slope"])), de(a["entry_r"], 1), reach_len("A", 1.2) or "–"))
    optA = ('<article class="sec"><h2><span class="badge b-mid">A</span> Weiterer V-Kanal, geschlossen</h2><div class="two">%s<div class="note" style="display:flex;flex-direction:column;gap:8px">'
            '<p>Der Tunnel des Nutzers, nur größer: Ø %s statt 2,2, Scheitel %s statt 3,4, Trichter R %s. Keine Überhangrücksicht mehr; mit 53° ist er ohnehin steiler als 45° und braucht keinen Support.</p>'
            '<p><b>Einfädeln:</b> nur mit Fädelhilfe (steifer Angelschnur-Anfang oder Draht-Öse, durch den Tunnel schieben, Faden hinterherziehen). Eine Nadel passt nicht.</p>'
            '<p><b>Nachteil:</b> Der Keil schrumpft, wenn der Kanal wächst: nur %s mm Basis und %s mm Höhe. Support im gebogenen Tunnel wäre mühsam auszuräumen.</p></div></div></article>'
            % (figA, de(a["leg_d"], 1), de(a["apex"], 1), de(a["entry_r"], 1), de(wa["base"], 1), de(wa["height"], 1)))
    figB1, figB2 = svg_wall_b(), svg_groove_b_section()
    optB = ('<article class="sec"><h2><span class="badge b-mid">B</span> Halboffene Rinne (Λ-Nut außen)</h2><div class="two"><div style="display:flex;flex-direction:column;gap:10px">%s%s</div>'
            '<div class="note" style="display:flex;flex-direction:column;gap:8px">'
            '<p>Dieselbe Λ-Bahn, aber als Nut in der Seitenwand, nach außen offen. Der Faden wird <b>eingelegt</b>, nichts wird gefädelt. Der Keil ist hier die Wand selbst und damit am stärksten.</p>'
            '<p><b>Nachteil:</b> Die Nut hält den Faden nur durch den Zug; im Schlaffzustand kann er herausspringen. Ein Λ von etwa %s × %s mm ist von außen sichtbar. Ohne Trichter, die Eckaussparung kann kleiner sein.</p>'
            '<p>Kein Support, keine Fädelhilfe, keine Nadelbahn. Der Faden läuft zwar „nach unten wieder heraus“, aber er verläuft sichtbar außen.</p></div></div></article>'
            % (fig(figB1, "B: Blick von außen auf die Seitenwand."), fig(figB2, "B: Schnitt durch die Nut."), de(2 * (b["apex"] * b["slope"] + 2.5), 0), de(b["apex"] + 2.5, 0)))
    figC1 = svg_c_section(tip_t=0.45, hole_no=1, thread_mode="none", label="C: Schnitt durch eine Schrägbohrung mit Nadel")
    figC2 = svg_c_outside(state="both", label="C: Seitenwand von außen")
    optC = ('<article class="sec"><h2><span class="badge b-ok">C</span> Zwei gerade Schrägbohrungen, Scheitel außen (Empfehlung)</h2><div class="two"><div style="display:flex;flex-direction:column;gap:10px">%s%s</div>'
            '<div class="note" style="display:flex;flex-direction:column;gap:8px">'
            '<p>Aus dem V werden zwei <b>gerade</b> Bohrungen Ø %s, %d° zur Waagerechten. Jede beginnt mit einem Trichter an der Plattenunterseite in der Eckaussparung und endet an der Seitenwand, %s mm über der Unterkante. '
            'Zwischen den beiden Austritten liegt der Faden in einer flachen Rille (%s mm tief) auf der Außenseite und ruht auf deren unterer Kante. Dort zieht er den Steg zwischen den Bohrungen (%s mm breit) nach unten; das ist der Keil.</p>'
            '<p><b>Einfädeln:</b> jeder Nadelgang ist eine gerade Linie. Die Nadel wird von außen durch das Loch geschoben und kommt unten im Eckausschnitt heraus (Regler weiter unten). Kippspielraum der Nadel im Loch: %s° bei Stopfnadel, %s° bei Nähnadel.</p>'
            '<p><b>Nachteil:</b> Etwa %s mm Faden liegen außen in der Rille, etwa %s mm über der Unterkante der Platte. Die Eckaussparung wird größer (etwa %s × %s mm). Kein Support nötig: Bohrung steiler als 45°, Rille %s mm tief.</p></div></div></article>'
            % (fig(figC1, "C: Schnitt durch Bohrung 1; die Nadel kommt von außen oben und taucht nach unten ein."), fig(figC2, "C: Blick von außen: zwei Austritte, Rille, Faden."),
               de(c["hole_d"], 1), round(P.angle_c()), de(c["rise"], 1), de(c["groove_depth"], 1), de(c["spacing"] - c["hole_d"], 1),
               de(P.tilt_tolerance(c["hole_d"], 1.6, math.hypot(c["run"], c["rise"])), 0), de(P.tilt_tolerance(c["hole_d"], 0.8, math.hypot(c["run"], c["rise"])), 0),
               de(c["spacing"], 0), de(P.exit_span()["lo"] + 0.9, 1), de(nz["C"][0], 0), de(nz["C"][1], 0), de(c["groove_depth"], 1)))
    optD = ('<article class="sec"><h2><span class="badge b-no">D</span> Faden von unten durch die Ecke des Unterkastens</h2><div class="two">%s<div class="note" style="display:flex;flex-direction:column;gap:8px">'
            '<p>Der Faden läuft in einem senkrechten Schacht (Ø %s) im Eckpfosten des Unterkastens nach oben und legt sich in der Plattenunterseite über einen Steg (Ø %s) im Fenster (%s × %s × %s). Der Unterkasten bleibt außen geschlossen, der Faden ist nirgends zu sehen.</p>'
            '<p><b>Nachteil:</b> Alles passiert blind in einem geschlossenen Schacht. Eine Nadel kommt nicht um den Steg; gebraucht werden Pinzette oder Häkelnadel. Das Fenster ist eine Brücke über %s mm (Support erlaubt, aber schwer zu putzen). Mehr Material, Schacht und Fenster müssen genau übereinander liegen.</p>'
            '<p>Nur als Vergleich aufgenommen; nicht für den Test vorgesehen.</p></div></div></article>'
            % (fig(svg_d(), "D: Schnitt durch Eckpfosten und Plattenunterseite."), de(dd["shaft_d"], 0), de(dd["bar_d"], 0), de(dd["window"][0], 0), de(dd["window"][1], 0), de(dd["window"][2], 0), de(dd["window"][0], 0)))
    return optA + optB + optC + optD


def sec_compare():
    nz = notch_sizes()
    ex = P.exit_span()
    rows = [("Einfädeln mit gerader Nadel", badge("no", "nein") + " nur Fädelhilfe", badge("ok", "entfällt") + " Faden wird eingelegt", badge("ok", "ja") + " jeder Gang gerade", badge("no", "nein") + " blind"),
            ("Faden sichtbar", "nur unten an den Mündungen", "Λ außen, etwa %s mm hoch" % de(P.B["apex"] + 2.5, 0), "%s mm außen, %s mm über der Unterkante" % (de(P.C["spacing"], 0), de(P.exit_span()["lo"] + 0.9, 1)), "nirgends"),
            ("Faden hält im Lauf", "ja (Tunnel)", badge("mid", "nur durch Zug"), "ja (Bohrungen), Rille führt", "ja (Schacht)"),
            ("Keil / tragender Teil", "klein: %s × %s mm" % (de(wedge(P.A)["base"], 1), de(wedge(P.A)["height"], 1)), "Wand (voll)", "Steg zwischen den Bohrungen, %s mm breit" % de(P.C["spacing"] - P.C["hole_d"], 1), "Steg Ø %s auf %s mm" % (de(P.D["bar_d"], 0), de(P.D["window"][0], 0))),
            ("Eckaussparung im Unterkasten", "etwa %s × %s mm" % (de(nz["A"][0], 0), de(nz["A"][1], 0)), "etwa %s × %s mm" % (de(nz["B"][0], 0), de(nz["B"][1], 0)), "etwa %s × %s mm" % (de(nz["C"][0], 0), de(nz["C"][1], 0)), "keine, Schacht %s × %s mm" % (de(nz["D"][0], 0), de(nz["D"][1], 0))),
            ("Druck", "kein Support nötig, Tunnel schwer zu putzen", "kein Support", "kein Support", "Brücke 12 mm, Support")]
    trs = "".join("<tr><td><b>%s</b></td>%s</tr>" % (r[0], "".join("<td>%s</td>" % c for c in r[1:])) for r in rows)
    return ('<section class="sec"><h2>Vergleich</h2><div class="tw"><table class="t"><thead><tr><th>Kriterium</th><th>A V weit</th><th>B Rinne</th><th>C Schrägbohrungen</th><th>D Eckschacht</th></tr></thead><tbody>%s</tbody></table></div>'
            '<p class="note"><b>Empfehlung C.</b> Es ist der einzige Weg, bei dem sich die Nadel in jedem Schritt geradeaus führen lässt, und er braucht weder Support noch Fädelhilfe. '
            'Der Preis: ein kurzes Stück Faden außen in der Rille und eine größere Eckaussparung. Wenn der Faden gar nicht sichtbar sein darf, bleibt A mit Fädelhilfe; deshalb druckt der Test A und B mit. Nutzer-Entscheidung unten (Karte S).</p></section>' % trs)


def c_frames():
    c = P.C
    f = []
    f.append((svg_c_section(tip_t=1.9, hole_no=1, thread_mode="none", label="C, Schritt 0"), "<b>Ausgangslage.</b> Nadel mit Faden (Knoten am Ende, Ø %s mm als Annahme) von außen an Loch 1." % de(P.KNOT_D, 0),
              svg_c_outside("none", label="C außen, Schritt 0")))
    f.append((svg_c_section(tip_t=0.45, hole_no=1, thread_mode="wait", label="C, Schritt 1"), "<b>Schritt 1.</b> Nadel von außen durch Loch 1 nach unten, schräg, genau auf der Achse (Spielraum %s°)." % de(P.tilt_tolerance(c["hole_d"], 1.6, math.hypot(c["run"], c["rise"])), 0),
              svg_c_outside("none", 1, label="C außen, Schritt 1")))
    f.append((svg_c_section(tip_t=None, hole_no=1, needle_vertical=True, thread_mode="a", label="C, Schritt 2"), "<b>Schritt 2.</b> Die Spitze kommt im Eckausschnitt heraus. Nadel ganz durchziehen, dann senkrecht durch den Hut (Punkt A) nach unten stechen; Faden folgt von der Rille bis in den Hut.",
              svg_c_outside("one", label="C außen, Schritt 2")))
    f.append((svg_c_section(tip_t=0.45, hole_no=2, thread_mode="wait", label="C, Schritt 3"), "<b>Schritt 3.</b> Faden in die Rille legen, Nadel von außen durch Loch 2, wieder schräg nach unten.",
              svg_c_outside("one", 2, label="C außen, Schritt 3")))
    f.append((svg_c_section(tip_t=None, hole_no=2, needle_vertical=True, thread_mode="done", label="C, Schritt 4"), "<b>Schritt 4.</b> Spitze im Eckausschnitt, Nadel durch den Hut am Punkt B, Faden straff ziehen und im Hut verknoten. Der Zug drückt die Platte auf den Unterkasten.",
              svg_c_outside("both", label="C außen, Schritt 4")))
    return f


def sec_thread():
    frames = [('<div class="vs">%s%s</div>' % (fig(s, "Schnitt durch das Loch", "s460"), fig(o, "Blick von außen", "s460")), cap) for s, cap, o in c_frames()]
    st = stepper("einfaedeln", frames, ["0 Start", "1 Loch 1", "2 Hut A", "3 Loch 2", "4 fertig"])
    return ('<section class="sec"><h2>Einfädeln bei Empfehlung C</h2>'
            '<p class="note">Fünf Schritte, nur gerade Nadelgänge. Die Nadel kommt zweimal von außen (an der Seitenwand ist immer Platz) und zweimal senkrecht durch den Hut; die Eckaussparung muss nur so groß sein, dass die Spitze unter dem Trichter herauskommt und man sie greifen kann. '
            'Dass der Hut von unten zugänglich ist (Griff durch die Kopföffnung), ist eine Annahme, siehe Rückfragen.</p>%s'
            '<p class="note"><b>Zum Vergleich A:</b> Fädelhilfe (steife Schnur oder Draht, 0,4 bis 0,5 mm, als Schlaufe oder mit Faden verknotet) von einer Mündung zur anderen durch den Tunnel schieben, Faden anschließen und nachziehen. '
            'Das geht, braucht aber Gefühl und einen glatten Kanal; die Stufen des Drucks halten die Schnur auf.</p></section>' % st)


def sec_chain():
    a, c = P.A, P.C
    n = P.NEEDLE_D
    rows = [("Kanal, alt (Steckprobe 2)", de(P.OLD["leg_d"], 1), de(P.hole_eff(P.OLD["leg_d"]), 1), de((P.hole_eff(P.OLD["leg_d"]) - n) / 2, 2), "Stopfnadel kommt nicht durch; mit Faden allein (doppelt 0,8) bleibt 0,5 je Seite"),
            ("A, Kanal", de(a["leg_d"], 1), de(P.hole_eff(a["leg_d"]), 1), de((P.hole_eff(a["leg_d"]) - n) / 2, 2), "Platz, aber die Kurve bleibt gesperrt"),
            ("C, Bohrung", de(c["hole_d"], 1), de(P.hole_eff(c["hole_d"]), 1), de((P.hole_eff(c["hole_d"]) - n) / 2, 2), "Kippspielraum %s° (Bohrungslänge %s mm)" % (de(P.tilt_tolerance(c["hole_d"], n, math.hypot(c["run"], c["rise"])), 0), de(math.hypot(c["run"], c["rise"]), 1))),
            ("Trichter C am Bett", de(2 * c["entry_r"], 1), de(2 * c["entry_r"] - P.PRINT_LOSS, 1), "–", "Spitze muss ±%s mm treffen; ein Trichter fängt sie ein" % de(c["entry_r"] - P.PRINT_LOSS / 2, 1))]
    trs = "".join('<tr><td><b>%s</b></td><td class="n">%s</td><td class="n">%s</td><td class="n">%s</td><td>%s</td></tr>' % r for r in rows)
    ex = P.exit_span()
    z = [("Austritt der Bohrung C an der Wand", "Ellipse %s hoch, von %s bis %s mm über der Unterkante" % (de(ex["height"], 1), de(ex["lo"], 1), de(ex["hi"], 1))),
         ("Wand über dem Austritt", "%s mm bis zur Oberseite (Regel: mindestens 2,0); sie trägt keinen Zug, sie soll nur beim Druck nicht durchscheinen" % de(ex["lip"], 1)),
         ("Wand über dem Scheitel bei A", "%s mm" % de(wedge(P.A)["roof"], 1)),
         ("Wand zum Plattenrand bei A", "%s mm (Regel: mindestens %s)" % (de(P.A["wall"], 1), de(P.WALL_MIN, 1))),
         ("Zugkraft je Ecke", "20 N angenommen (ungemessen, S); sie geht über die Kante der Rille in massives Plattenmaterial (Steg %s mm, dahinter voll). Der Faden scheuert an den Kanten: Austritte und Rillenkante mit R %s runden" % (de(P.C["spacing"] - P.C["hole_d"], 1), de(P.C["edge_r"], 1)))]
    trs2 = "".join("<tr><td><b>%s</b></td><td>%s</td></tr>" % r for r in z)
    return ('<section class="sec"><h2>Maßkette im Worst-Case</h2><p class="note">Worst-Case: Der Kanal ist im Druck um bis zu %s mm enger als gezeichnet (Wulst, Stufen, Stützreste; L02, L03), die Nadel ist die dickste Annahme (Stopfnadel Ø %s mm, ungemessen).</p>'
            '<div class="tw"><table class="t"><thead><tr><th>Stelle</th><th>Nenn-Ø</th><th>im Druck</th><th>Luft je Seite zur Nadel</th><th>Bewertung</th></tr></thead><tbody>%s</tbody></table></div>'
            '<div class="tw"><table class="t"><thead><tr><th>Material und Last</th><th>Wert</th></tr></thead><tbody>%s</tbody></table></div></section>' % (de(P.PRINT_LOSS, 1), de(n, 1), trs, trs2))


def sec_questions():
    q = [("Nadel und Faden", "Welche Nadel (Nähnadel 0,8, Sticknadel 1,2, Stopfnadel 1,6 mm?) und welchen Faden nimmst du, einfach oder doppelt? Ich rechne mit Stopfnadel 1,6 und doppeltem Faden 0,8 mm."),
         ("Zugang zum Hut", "Kommst du mit der Hand von unten in den Hut (Kopföffnung), um den Faden dort zu verknoten? Oder wird von oben genäht und die Knoten liegen außen?"),
         ("Reihenfolge", "Wird zuerst der Unterkasten auf den Hut gesetzt und erst dann die Platte gefädelt, oder liegen Platte und Unterkasten schon zusammen?"),
         ("Sichtbarkeit", "Darf auf jeder Ecke ein Stück Faden (etwa %s mm) außen in der Rille liegen? Die Antwort entscheidet zwischen C und A." % de(P.C["spacing"], 0))]
    li = "".join("<li><b>%s.</b> %s</li>" % x for x in q)
    return ('<section class="sec"><h2>Rückfragen (L29)</h2><ul class="q">%s</ul><p class="note">Mit den Antworten wähle ich die Maße im Testbogen nach; ohne Antwort gelten die genannten Annahmen.</p></section>' % li)


def sec_test():
    nz = notch_sizes()
    rows = [("F1-A", "Plattenecke 30 × 24 × 12,6 + Unterkasten-Ecke (hohl, 14,4)", "V Ø %s, Scheitel %s, Trichter R %s, Eckaussparung %s × %s" % (de(P.A["leg_d"], 1), de(P.A["apex"], 1), de(P.A["entry_r"], 1), de(nz["A"][0], 0), de(nz["A"][1], 0))),
            ("F1-B", "Plattenecke + Unterkasten-Ecke", "Λ-Nut %s breit, %s tief, Eckaussparung %s × %s" % (de(P.B["groove_w"], 1), de(P.B["depth"], 1), de(nz["B"][0], 0), de(nz["B"][1], 0))),
            ("F1-C", "Plattenecke + Unterkasten-Ecke", "Bohrungen Ø %s, %d°, Abstand %s, Rille %s tief, Eckaussparung %s × %s" % (de(P.C["hole_d"], 1), round(P.angle_c()), de(P.C["spacing"], 0), de(P.C["groove_depth"], 1), de(nz["C"][0], 0), de(nz["C"][1], 0)))]
    trs = "".join('<tr><td><b>%s</b></td><td>%s</td><td>%s</td></tr>' % r for r in rows)
    return ('<section class="sec"><h2>Was gedruckt würde (nach dem Abnicken)</h2>'
            '<p class="note">Ein Druck, drei Eckmuster. Je Muster zwei Teile: die Plattenecke (Unterseite am Druckbett, wie im echten Teil) und eine Unterkasten-Ecke mit der Eckaussparung zum Daraufstellen. Kein Gebäude, kein Dock, keine Zapfen. '
            'Unterlage: ein Stück Filz oder Pappe als „Hut“. Material insgesamt etwa 25 g, etwa 1,5 Stunden.</p>'
            '<div class="tw"><table class="t"><thead><tr><th>Teil</th><th>Inhalt</th><th>Besonderheit</th></tr></thead><tbody>%s</tbody></table></div>'
            '<p class="note">Dazu: <code>plug/thread/build.py</code> (STL, README, ZIP, Prüfbericht mit dicht, Kollisionen und Überhängen), Testbogen mit Zeichnungen, Reglern und Ergebnistext. '
            'Fragen im Testbogen: Faden einfädeln (ja, mit Mühe, nein) je Schritt; kräftig am Faden ziehen (Ecke bleibt?); Faden verrutscht oder springt heraus; gefällt die sichtbare Rille; welche Variante; welche ZIP (Datum, L35). Variante immer abfragen (L25).</p></section>' % trs)


def sec_risks():
    risks = [("C: Wand über dem Austritt.", "Nur %s mm zwischen Austritt und Oberseite. Sie trägt keinen Zug; wird sie im Druck zu dünn, wandert der Austritt tiefer oder die Bohrung wird kleiner." % de(P.exit_span()["lip"], 1)),
             ("C: Faden scheuert.", "Der Faden läuft über die untere Kante der Rille und die Austrittsränder. Kanten werden mit R 1,0 gerundet; der Test fragt, ob der Faden hakt."),
             ("C: Faden außen.", "Das Stück in der Rille ist von der Seite zu sehen. Wenn das nicht geht, bleibt A mit Fädelhilfe."),
             ("C: Eckaussparung.", "Etwa %s × %s mm schwächt die Ecke des Unterkastens. Er hat 2,4 mm Wand; ein Eckstück dort kann nachträglich verstärkt werden." % (de(notch_sizes()["C"][0], 0), de(notch_sizes()["C"][1], 0))),
             ("Nadel und Faden ungemessen.", "Alle Spielräume rechnen mit Annahmen (L08). Die Rückfrage oben und der Testbogen klären es."),
             ("Hut-Zugang ungeklärt.", "Das Verknoten im Hut ist angenommen. Wird von oben genäht, ändert sich der Ablauf; die Geometrie bleibt."),
             ("Einfädelrechnung ist 2D.", "Sie gilt für den Schnitt durch den Kanal. Für C gibt es keine Kurve, dort zählt nur der Kippspielraum.")]
    return '<section class="sec"><h2>Risiken</h2>%s</section>' % "".join('<p class="risk"><b>%s</b> %s</p>' % r for r in risks)


DECISIONS = [
    dict(id="V", tag="Variante", title="Was wird gebaut und gedruckt?", rec="A",
         text="Empfohlen wird C. Weil die Wahl von deinen Antworten abhängt, druckt der Test alle drei geeigneten Wege.",
         opts=[("A", "Drei Eckmuster: A (V weit), B (Rinne), C (Schrägbohrungen); danach entscheiden"), ("B", "Nur C"), ("C", "Nur A (V weit, mit Fädelhilfe), keine Änderung am Konzept"), ("D", "Alle vier, auch D (Eckschacht)")]),
    dict(id="S", tag="Sichtbar", title="Darf Faden außen in einer Rille liegen?", rec="A",
         text="C und B führen Faden außen an der Seitenwand (C: etwa 9 mm, rund 4,5 mm über der Unterkante). Oben tritt nichts aus.",
         opts=[("A", "ja, ein kurzes Stück außen ist in Ordnung"), ("B", "nein, der Faden muss ganz verdeckt sein (dann A mit Fädelhilfe)"), ("C", "egal, erst im Test entscheiden")]),
    dict(id="N", tag="Nadel", title="Welche Nadel nimmst du?", rec="C",
         text="Das legt Loch- und Kanaldurchmesser fest. Ich rechne mit der dicksten Annahme.",
         opts=[("A", "Nähnadel, etwa 0,8 mm"), ("B", "Sticknadel, etwa 1,2 mm"), ("C", "Stopfnadel, etwa 1,6 mm (Annahme)"), ("D", "andere (bitte in die Notiz)")]),
    dict(id="K", tag="Aussparung", title="Eckaussparung im Unterkasten", rec="A",
         text="Bei C wächst sie auf etwa %s × %s mm, damit die Spitze unten herauskommt und man sie greifen kann." % (de(notch_sizes()["C"][0], 0), de(notch_sizes()["C"][1], 0)),
         opts=[("A", "so groß wie nötig (Empfehlung)"), ("B", "kleiner, die Spitze wird mit Pinzette gegriffen"), ("C", "größer, nach der ganzen Ecke offen")]),
    dict(id="T", tag="Testteil", title="Umfang des Testteils", rec="A",
         text="Das Eckmuster zeigt nur die Fadenführung, ohne Gebäude und Dock.",
         opts=[("A", "Plattenecke und Unterkasten-Ecke je Variante (Empfehlung)"), ("B", "nur die Plattenecken, ohne Unterkasten"), ("C", "zusätzlich eine Plattenecke mit Doppelloch für zwei Fäden")]),
]


def decision_card(dd):
    opts = "".join('<div><b>%s</b><span>%s%s</span></div>' % (k, t, '  <span class="rec">(Empfehlung)</span>' if k == dd["rec"] else "") for k, t in dd["opts"])
    sel = "".join('<option value="%s">%s%s</option>' % (k, k, " (Empfehlung)" if k == dd["rec"] else "") for k, _ in dd["opts"])
    return ('<article class="dec" id="d-%s"><header><span class="tg">%s</span><h2>%s</h2></header><div class="txt"><p>%s</p><div class="opts">%s</div></div>'
            '<div class="vote"><label class="ok" for="a-%s"><span>Deine Wahl</span><select id="a-%s" data-did="%s"><option value="">– bitte wählen –</option>%s'
            '<option value="x">andere (Notiz)</option></select></label>'
            '<label class="ok wide" for="n-%s"><span>Notiz</span><input type="text" id="n-%s" data-nid="%s" placeholder="optional"></label></div></article>'
            % (dd["id"], dd["tag"], dd["title"], dd["text"], opts, dd["id"], dd["id"], dd["id"], sel, dd["id"], dd["id"], dd["id"]))


def main():
    sections = "".join([sec_befund(), sec_why(), sec_options(), sec_compare(), sec_thread(), sec_chain(), sec_questions(), sec_test(), sec_risks()])
    sections += '<section class="top"><h2>Entscheidungen</h2><p class="lead">Mit den Empfehlungen ist der Plan rund. Abweichungen bitte markieren, danach erzeuge ich STL, README, ZIP und Prüfbericht.</p></section>'
    sections += "\n".join(decision_card(x) for x in DECISIONS)
    spec = [dict(id=x["id"], tag=x["tag"], title=x["title"]) for x in DECISIONS]
    with open(TEMPLATE, encoding="utf-8") as f:
        page = f.read()
    for k, v in {"{{HEAD}}": head(), "{{SECTIONS}}": sections, "{{SPEC}}": json.dumps(spec, ensure_ascii=False)}.items():
        page = page.replace(k, v)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(page)
    print("geschrieben: %s (%d kB)" % (os.path.relpath(OUT, ROOT), os.path.getsize(OUT) / 1024))


if __name__ == "__main__":
    main()
