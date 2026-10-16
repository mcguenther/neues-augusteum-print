#!/usr/bin/env python3
"""Planungsseite Stand 2 für die Fadenführung: Variante A als „halbe Pille mit Steg“ (offene Tasche an der Plattenunterseite statt Tunnel).

Maße aus plug/thread/params.py (`pill()`), Einfädelprobe aus reach.json bzw. reach.py, Passprüfung im echten Modell aus fit.json (plug/thread/fit.py).
Die Zeichnungen sind Schemazeichnungen im Maßstab, noch keine STL. Stand 1 (Vergleich der Varianten A bis D) liegt als Archiv in build_plan1.py / plan1.html.

Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m plug.thread.build_plan      # schreibt plug/thread/plan.html
"""
import json
import math
import os

from shapely.geometry import Point
from shapely.geometry import box as sbox
from shapely.ops import unary_union

from plug.feedback.build import G
from plug.thread import build_plan1 as B1
from plug.thread import params as P
from plug.thread import reach as R
from plug.thread.build_plan1 import de, decision_card, fig, pts, stepper, thick, thread_line

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TEMPLATE = os.path.join(HERE, "plan.template.html")
OUT = os.path.join(HERE, "plan.html")


def load(name):
    try:
        with open(os.path.join(HERE, name), encoding="utf-8") as f:
            return json.load(f)
    except OSError:
        return {}


FIT = load("fit.json")


_RT = load("reach.json")
NEEDLE = {a: _RT.get("pille%.1f|1.2" % a, d) for a, d in ((3.0, 10), (4.5, 12))}   # längste gerade Nadel, Ø 1,2 (Rechnung: `python3 -m plug.thread.reach --pill`)


# --------------------------------------------------------------------------
# Zeichnungen
# --------------------------------------------------------------------------
def pill_polys(air):
    """Tasche (frei) und Steg im Schnitt x–z."""
    d = P.pill(air)
    base, steg, _, _, _ = R.pill_geom(air)
    return d, base, steg


def svg_pill_section(air=3.0, thread=True, needle=None, hook=None, hat=True, label="", loop=False):
    """Schnitt x–z durch Tasche und Steg (Plattendicke voll). needle/hook: Linienzüge (x, z) für Nadel bzw. Haken."""
    S = 15.0
    d, region, steg = pill_polys(air)
    zt, zb = P.PLATE_T + 1.0, -9.0
    g = G(S, 16 * S + 8, zt * S + 8)
    g.rect(-16, 16, 0, P.PLATE_T, "d-slab")
    g.rect(-16, 16, zb, zb + 1.6, "d-hat")
    g.poly(pts(region), "d-void")
    g.poly(pts(steg), "d-slab")
    hf = d["steg_w"] / 2
    xa = -(hf + d["gap0"] / 2)
    if thread:
        cc, rr = (0.0, d["steg_top"] - hf), hf + 0.15
        arc = [(cc[0] + rr * math.cos(math.radians(a)), cc[1] + rr * math.sin(math.radians(a))) for a in (165, 140, 115, 90, 65, 40, 15)]
        thread_line(g, [(xa, zb + 1.6)] + arc + [(-xa, zb + 1.6)], "d-threads" if loop else "d-thread")
    if needle:
        for a, b in zip(needle[:-1], needle[1:]):
            thick(g, a, b, P.NEEDLE_D)
    if hook:
        g.o.append('<polyline points="%s" class="d-needle" style="stroke-width:2.4;fill:none;stroke-linejoin:round"/>' % " ".join("%.1f,%.1f" % (g.X(x), g.Z(z)) for x, z in hook))
    # Maße
    z0, z1 = d["steg_top"], d["ceil"]
    g.o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="dimn"/>' % (g.X(0), g.Z(z0), g.X(0), g.Z(z1)))
    g.text(0.4, (z0 + z1) / 2 - 0.2, "Luft %s" % de(d["air"], 1), "dln", "start")
    g.o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="dimn"/>' % (g.X(d["length"] / 2 + 1.5), g.Z(0), g.X(d["length"] / 2 + 1.5), g.Z(d["ceil"])))
    g.text(d["length"] / 2 + 1.8, d["ceil"] / 2, "Decke %s" % de(d["ceil"], 1), "dln", "start")
    g.text(0, 1.6, "Steg %s breit" % de(d["steg_w"], 1), "dls")
    xm = d["length"] / 2 + d["chamfer"]
    g.o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="dimn"/>' % (g.X(-xm), g.Z(-0.6), g.X(-hf + d["steg_chamfer"]), g.Z(-0.6)))
    g.text((-xm - hf + d["steg_chamfer"]) / 2, -1.5, "Eingang A %s mm weit" % de(d["gap_mouth"], 1), "dln")
    g.o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="dimn"/>' % (g.X(hf - d["steg_chamfer"]), g.Z(-0.6), g.X(xm), g.Z(-0.6)))
    g.text((xm + hf - d["steg_chamfer"]) / 2, -1.5, "Ausgang B %s mm weit" % de(d["gap_mouth"], 1), "dln")
    g.text(-xm - 0.2, 2.4, "Fase %s × 45°" % de(d["chamfer"], 1), "dls", "end")
    g.text(-hf - 0.3, 0.5 + 0.0, "Fase %s" % de(d["steg_chamfer"], 1), "dls", "end")
    g.text(0, P.PLATE_T - 2.3, "Material über der Decke: %s" % de(d["roof"], 1), "dls")
    g.text(-15.6, -3.0, "Eckaussparung", "dls", "start")
    g.text(-15.6, zb + 0.5, "Hut (Stoff)", "dls", "start")
    g.text(xa, 2.0, "A", "dlb")
    g.text(-xa, 2.0, "B", "dlb")
    return g.svg(int(32 * S + 16), int((zt - zb) * S + 16), label or "Schnitt durch die Tasche mit Steg")


def svg_pill_yz(air=3.0):
    """Schnitt y–z durch den Steg: Steg überbrückt die Taschenbreite, Decke rundum gerundet."""
    S = 17.0
    d = P.pill(air)
    w2 = d["width"] / 2
    wall = P.WALL_MIN
    g = G(S, (w2 + wall + 1.5) * S + 8, (P.PLATE_T + 1.0) * S + 8)
    g.rect(-w2 - wall - 1.5, w2 + wall + 1.5, 0, P.PLATE_T, "d-slab")
    fr = d["fillet"]
    z0, z1 = d["steg_top"], d["ceil"]
    air_poly = unary_union([sbox(-w2, z0, w2, z0 + 0.01), sbox(-w2 + fr, z0, w2 - fr, z1),
                            Point(-w2 + fr, z1 - fr).buffer(fr, 48).intersection(sbox(-w2, z1 - fr, -w2 + fr, z1)),
                            Point(w2 - fr, z1 - fr).buffer(fr, 48).intersection(sbox(w2 - fr, z1 - fr, w2, z1)), sbox(-w2, z0, w2, z1 - fr)])
    g.poly(pts(air_poly), "d-void")
    g.o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="dimn"/>' % (g.X(-w2), g.Z(-1.0), g.X(w2), g.Z(-1.0)))
    g.text(0, -1.9, "Tasche %s breit" % de(d["width"], 0), "dln")
    g.text(0, z0 / 2 - 0.2, "Steg (voll, bis zu beiden Wänden)", "dls")
    g.text(0, (z0 + z1) / 2 - 0.2, "Luft", "dls")
    g.text(0, z1 + 0.9, "Rundung R %s" % de(fr, 0), "dls")
    g.text(-w2 - wall - 1.3, P.PLATE_T - 0.9, "Wand %s" % de(wall, 1), "dls", "start")
    return g.svg(int((2 * (w2 + wall + 1.5)) * S + 16), int((P.PLATE_T + 3.0) * S + 16), "Schnitt quer durch den Steg")


def svg_pill_below(air=3.0):
    """Blick von unten auf die Plattenecke: Tasche, Steg, Eckaussparung im Unterkasten."""
    S = 11.0
    d = P.pill(air)
    L, W = d["length"], d["width"]
    ML, MW = d["mouth_l"], d["mouth_w"]
    wall = P.WALL_MIN
    cw, ch = ML + 2 * wall + 8.0, MW + 2 * wall + 8.0
    g = G(S, 10, ch * S + 10)
    g.rect(0, cw, 0, ch, "d-slab")
    cx, cy = wall + ML / 2, wall + MW / 2
    nx0, ny0, nx1, ny1 = cx - ML / 2 - P.NOTCH_PAD, cy - MW / 2 - P.NOTCH_PAD, cx + ML / 2 + P.NOTCH_PAD, cy + MW / 2 + P.NOTCH_PAD
    g.o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" class="d-dash"/>' % (g.X(max(0.0, nx0)), g.Z(ny1), (nx1 - max(0.0, nx0)) * S, (ny1 - max(0.0, ny0)) * S))
    g.rect(cx - ML / 2, cx + ML / 2, cy - MW / 2, cy + MW / 2, "d-open")
    g.rect(cx - L / 2, cx + L / 2, cy - W / 2, cy + W / 2, "d-void")
    g.rect(cx - d["steg_w"] / 2 - d["steg_chamfer"], cx + d["steg_w"] / 2 + d["steg_chamfer"], cy - W / 2, cy + W / 2, "d-open")
    g.rect(cx - d["steg_w"] / 2, cx + d["steg_w"] / 2, cy - W / 2, cy + W / 2, "d-slab")
    xa = cx - d["steg_w"] / 2 - d["gap0"] / 2
    thread_line(g, [(xa, cy), (cx + d["steg_w"] / 2 + d["gap0"] / 2, cy)], "d-threads")
    g.text(cx, cy + W / 2 + 0.6, "Tasche %s × %s, Mündung mit Fase (grün) %s × %s" % (de(L, 0), de(W, 0), de(ML, 0), de(MW, 0)), "dls")
    g.text(cx, ny1 + 0.9, "Eckaussparung im Unterkasten (gestrichelt) %s × %s" % (de(d["notch_l"], 0), de(d["notch_w"], 0)), "dls")
    g.text(0.4, 0.5, "Ecke der Platte", "dls", "start")
    return g.svg(int(cw * S + 20), int((ch + 3.0) * S + 20), "Blick von unten auf die Plattenecke")


def frames_thread(air=3.0):
    d = P.pill(air)
    hf = d["steg_w"] / 2
    xa = -(hf + d["gap0"] / 2)
    zb = -9.0 + 1.6
    tipx, tipz = -hf - 0.5, d["steg_top"] + 1.6
    f = []
    f.append((svg_pill_section(air, thread=False, needle=[(xa - 3.0, zb - 0.0), (xa - 1.0, zb + 5.0)], label="Schritt 0"),
              "<b>Ausgangslage.</b> Der Faden kommt bei Punkt A aus dem Hut, die Nadel hängt am freien Ende unter dem linken Spalt."))
    f.append((svg_pill_section(air, thread=True, needle=[(xa - 4.2, zb), (tipx - 0.5, tipz)], label="Schritt 1"),
              "<b>Schritt 1.</b> Nadel durch den linken Spalt hinauf, bis die Spitze über dem Steg in der Luft steht. Der Spalt ist %s mm breit, die Nadel braucht nur gerade nach oben und leicht zum Steg hin." % de(d["gap_top"], 1)))
    f.append((svg_pill_section(air, thread=True, needle=[(xa - 4.2, zb), (tipx - 0.5, tipz)], hook=[(hf + 6.0, zb), (hf + 1.6, tipz - 0.3), (hf - 0.4, tipz + 0.2), (-hf + 0.9, tipz + 0.5), (-hf + 0.4, tipz - 0.1)], label="Schritt 2"),
              "<b>Schritt 2.</b> Gebogener Draht (Büroklammer) oder Pinzette durch den rechten Spalt, über den Steg, hinter den Faden an der Nadelspitze."))
    f.append((svg_pill_section(air, thread=True, loop=True, hook=[(hf + 1.5, zb + 2.5), (hf + 4.0, zb)], label="Schritt 3"),
              "<b>Schritt 3.</b> Haken ziehen: Der Faden folgt über den Steg und kommt im rechten Spalt nach unten heraus. Nadel hängt jetzt unter dem rechten Spalt."))
    f.append((svg_pill_section(air, thread=True, loop=True, needle=[(-xa, zb + 0.4), (-xa, zb - 0.1)], label="Schritt 4"),
              "<b>Schritt 4.</b> Nadel senkrecht durch den Hut bei Punkt B, Faden straff ziehen und im Hut verknoten. Der Zug drückt die Platte über den Steg auf den Unterkasten."))
    return f


# --------------------------------------------------------------------------
# Seite
# --------------------------------------------------------------------------
def head():
    return ('<header class="top"><p class="kicker">Steckmechanismus · Fadenführung · Stand 2</p><h1>Fadenführung an den Plattenecken</h1>'
            '<p class="lead">Nach deiner Rückmeldung: Der Faden ließ sich nicht einschieben, weil der Kanal zugeschmoddert war. Du willst Variante A probieren und sie robust bauen: '
            'eine Tasche wie eine halbe Pille mit einem Steg in der Mitte, die Decke schön rund, etwa 3 mm Luft über dem Steg. Hier steht die Form, ob sie ins Modell passt und wie der Faden hineinkommt. '
            '<b>Es gibt noch keine STL.</b> Der erste Plan (Vergleich der Varianten A bis D) liegt als Archiv in <code>plug/thread/plan1.html</code>.</p>'
            '<ul class="sum">'
            '<li><b>Form:</b> offene Tasche an der Plattenunterseite, %s × %s mm, Decke %s mm hoch, Steg %s breit und %s hoch, <b>%s mm Luft</b> darüber. Kein Tunnel mehr: Die Tasche ist von unten ganz offen, nichts kann zuschmoddern.</li>'
            '<li><b>Fase:</b> ringsum am Taschenrand %s × 45° und am Steg-Fuß %s × 45°. Eingang und Ausgang sind dadurch an der Plattenunterseite %s mm weit (ohne Fase %s), die Nadelspitze findet sie von selbst.</li>'
            '<li><b>Passt ins Modell:</b> ja. Die Tasche samt Fase braucht in der Platte %s × %s mm und %s mm Decke; die Platte ist %s mm dick. An allen vier Ecken der echten Platte frei, bei 1:1000 und 1:1300.</li>'
            '<li><b>Einfädeln:</b> Eine gerade Nadel kommt auch hier nur etwa %s mm weit um den Steg. Dafür ist alles offen: Nadel hinauf, Haken oder Pinzette zieht den Faden über den Steg.</li>'
            '<li><b>Test:</b> zwei Eckmuster in einem Druck, Luft 3,0 und 4,5 mm. Neue Werte nur in <code>plug/thread/params.py</code>.</li></ul></header>'
            % (de(P.pill()["length"], 0), de(P.PILL["width"], 0), de(P.pill()["ceil"], 1), de(P.PILL["steg_w"], 0), de(P.PILL["steg_top"], 1), de(P.PILL["air"], 1),
               de(P.PILL["chamfer"], 1), de(P.PILL["steg_chamfer"], 1), de(P.pill()["gap_mouth"], 1), de(P.pill()["gap0"], 1),
               de(P.pill()["mouth_l"] + 2 * P.WALL_MIN, 1), de(P.pill()["mouth_w"] + 2 * P.WALL_MIN, 1), de(P.pill()["roof"], 1), de(P.PLATE_T, 1), NEEDLE[3.0]))


def sec_diag():
    rows = [("Faden ließ sich in keines der V-Kanäle einschieben", "Der Kanal (Ø 2,2) war im Druck zugeschmoddert; Wulst und Stufen machen aus 2,2 mm schnell weniger als 1,8 (L02, L03)", "Hohlräume groß und offen bauen: kleinste freie Maße deutlich über 3 mm"),
            ("Ein geschlossener, gebogener Tunnel", "Auch frei gedruckt kommt keine übliche Nadel um den Scheitel: gerechnet höchstens 6 mm lang bei Ø 4,0", "Wo es geht, offen bauen (hier: Tasche von unten offen)"),
            ("Nutzer: Variante A probieren, super robust", "Halbe Pille mit Steg in der Mitte, runde Decke, etwa 3 mm Luft über dem Steg, wenn es ins Modell passt", "Größe der Tasche und Platz im Modell prüfen (unten)"),
            ("Support ist erlaubt", "Trotzdem ohne Support planen: Support in einer Tasche mit 3 mm Luft würde selbst zuschmoddern", "Decke rund und selbsttragend, Brücke nur 5 mm")]
    trs = "".join("<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % r for r in rows)
    return ('<section class="sec"><h2>Was sich geändert hat</h2><div class="tw"><table class="t"><thead><tr><th>Befund</th><th>Deutung</th><th>Folge</th></tr></thead><tbody>%s</tbody></table></div>'
            '<p class="note">Neue Lehre für das Logbuch (steht noch in <code>plug/thread/README.md</code>, weil dieser Chat nur in <code>plug/thread/</code> schreibt): Kanäle und Löcher unter etwa 3 mm schließen sich im Druck; '
            'Fadenwege als offene Taschen mit mindestens 5 mm freiem Maß bauen.</p></section>' % trs)


def sec_form():
    d = P.pill(3.0)
    fig1 = fig(svg_pill_section(3.0, thread=True, loop=True, label="Schnitt durch die halbe Pille mit Steg"),
               "Schnitt längs durch die Tasche (Plattendicke %s mm). Weiß: die offene Tasche mit runder Decke. Der Steg steht in der Mitte, der Faden (rot) kommt bei A aus dem Hut, geht über die Steg-Kante und bei B wieder zum Hut." % de(P.PLATE_T, 1))
    fig2 = fig(svg_pill_yz(3.0), "Schnitt quer durch den Steg: Er überbrückt die ganze Taschenbreite und sitzt an beiden Wänden fest. Die Decke ist an den Kanten gerundet (R %s)." % de(d["fillet"], 0))
    fig3 = fig(svg_pill_below(3.0), "Blick von unten auf eine Plattenecke: Tasche, Steg und die Eckaussparung im Unterkasten (gestrichelt, nach außen offen).")
    names = ["Luft 3,0", "Luft 4,5"]
    frames = []
    for air in (3.0, 4.5):
        dd = P.pill(air)
        frames.append((fig(svg_pill_section(air, thread=True, loop=True, label="Luft %s" % de(air, 1)), "", "s460"),
                       "<b>Luft %s mm</b> · Decke %s · Länge %s · Material über der Decke %s mm · seitlicher Spalt in Höhe der Stegkante %s mm · längste gerade Nadel um den Steg: etwa %s mm" % (
                           de(air, 1), de(dd["ceil"], 1), de(dd["length"], 0), de(dd["roof"], 1), de(dd["gap_top"], 1), NEEDLE[air])))
    rows = [("Taschenlänge am Boden", de(d["length"], 1), "2 × Endrundung + Stegbreite"),
            ("Endrundung (Viertelkreis bis zum Boden)", "R %s" % de(d["r"], 1), "= Deckenhöhe, die Decke ist rund"),
            ("Deckenhöhe", de(d["ceil"], 1), "Steg %s + Luft %s" % (de(d["steg_top"], 1), de(d["air"], 1))),
            ("Steg", "%s × %s" % (de(d["steg_w"], 1), de(d["steg_top"], 1)), "oben voll gerundet (R %s), durchgehend von Wand zu Wand" % de(d["steg_w"] / 2, 1)),
            ("Taschenbreite", de(d["width"], 1), "Decke an den Wänden mit R %s gerundet" % de(d["fillet"], 0)),
            ("Fase am Taschenrand (Ein- und Ausgänge)", "%s × 45°" % de(d["chamfer"], 1), "ringsum an der Mündung; gleicht auch den Elefantenfuß am Bett aus (L03)"),
            ("Fase am Steg-Fuß", "%s × 45°" % de(d["steg_chamfer"], 1), "erweitert beide Eingänge zusätzlich"),
            ("Eingang A und Ausgang B an der Mündung", "%s weit" % de(d["gap_mouth"], 1), "Rand bis Steg-Fuß; ohne Fase %s" % de(d["gap0"], 1)),
            ("Spalt links und rechts vom Steg", "%s am Boden, %s oben" % (de(d["gap0"], 1), de(d["gap_top"], 1)), "weit genug für Finger, Pinzette, Nadel"),
            ("Mündung samt Fase", "%s × %s" % (de(d["mouth_l"], 0), de(d["mouth_w"], 0)), "Tasche + 2 × Fase"),
            ("Eckaussparung im Unterkasten", "%s × %s" % (de(d["notch_l"], 0), de(d["notch_w"], 0)), "Mündung + %s mm ringsum, nach außen offen" % de(P.NOTCH_PAD, 0))]
    trs = "".join('<tr><td><b>%s</b></td><td class="n">%s</td><td>%s</td></tr>' % r for r in rows)
    return ('<section class="sec"><h2>Die halbe Pille mit Steg</h2><div class="two">%s%s</div>%s'
            '<p class="note">Der Faden ruht oben auf dem Steg und zieht ihn nach unten; das ist der Keil aus dem ersten Plan, jetzt als Steg von Wand zu Wand mit %s mm × %s mm Querschnitt. '
            'Die Tasche öffnet sich ganz nach unten in die Eckaussparung, es gibt keinen Tunnel, keinen Trichter und keine Stelle unter 3 mm. Gedruckt wird die Plattenunterseite am Bett, wie bisher.</p>'
            '<h3>Regler: Luft über dem Steg</h3>%s'
            '<div class="tw"><table class="t"><thead><tr><th>Maß</th><th>mm</th><th>Bemerkung</th></tr></thead><tbody>%s</tbody></table></div></section>'
            % (fig1, fig2, fig3, de(d["steg_w"], 0), de(d["steg_top"], 1), stepper("luft", frames, names), trs))


def fit_cells(rs):
    """Je Ecke das Ergebnis; sind alle vier gleich, steht es einmal da."""
    cells = ["–" if r is None else "frei, %s mm von der Ecke" % de(r["shift"], 1) for r in rs]
    return "alle vier Ecken: " + cells[0] if len(set(cells)) == 1 else " · ".join(cells)


def sec_fit():
    d3, d45 = P.pill(3.0), P.pill(4.5)
    rows = []
    for scale in ("1:1000", "1:1300"):
        row = FIT.get(scale)
        if not row:
            continue
        for name, label in (("alt", "altes V (Steckprobe 2)"), ("pille3", "Pille, Luft 3,0"), ("pille45", "Pille, Luft 4,5")):
            rows.append("<tr><td>%s</td><td>%s × %s</td><td>%s</td><td>%s</td></tr>" % (scale, de(row["plate"][0], 0), de(row["plate"][1], 0), label, fit_cells(row[name])))
    chain = [("Plattendicke", "%s" % de(P.PLATE_T, 1), ""),
             ("Decke der Tasche, Luft 3,0 / 4,5", "%s / %s" % (de(d3["ceil"], 1), de(d45["ceil"], 1)), ""),
             ("Material über der Decke", "%s / %s" % (de(d3["roof"], 1), de(d45["roof"], 1)), "Regel mindestens 2,0; die Oberseite trägt Gebäude und Mulden, nichts scheint durch"),
             ("Platz im Grundriss (gefaste Mündung + Wand %s)" % de(P.WALL_MIN, 1), "%s × %s / %s × %s" % (de(d3["mouth_l"] + 2 * P.WALL_MIN, 1), de(d3["mouth_w"] + 2 * P.WALL_MIN, 1), de(d45["mouth_l"] + 2 * P.WALL_MIN, 1), de(d45["mouth_w"] + 2 * P.WALL_MIN, 1)), "an einer Ecke, lange Seite parallel zur Kante; die Wand zählt ab dem Rand der Fase"),
             ("Unterkasten", "Eckaussparung %s × %s / %s × %s" % (de(d3["notch_l"], 0), de(d3["notch_w"], 0), de(d45["notch_l"], 0), de(d45["notch_w"], 0)), "Wand 2,4 mm bleibt rundum; die Aussparung ist nach außen offen")]
    trs2 = "".join('<tr><td><b>%s</b></td><td class="n">%s</td><td>%s</td></tr>' % r for r in chain)
    return ('<section class="sec"><h2>Passt das ins Modell?</h2>'
            '<p class="note"><b>Ja.</b> Geprüft mit dem Umriss und den gesperrten Flächen der echten Platte (Mulden der Gebäude mit Spiel, Vertiefung des Innenhofs, je %s mm Wand), wie das Konzept die V-Kanäle setzt: '
            'Die Tasche samt Fase sitzt an allen vier Ecken frei, etwa 2 bis 3,5 mm von der Ecke weg (Eckenrundung, an einer Ecke liegt ein Gebäude näher). Auch die große Variante mit 4,5 mm Luft passt. Code: <code>plug/thread/fit.py</code>.</p>'
            '<div class="tw"><table class="t"><thead><tr><th>Maßstab</th><th>Platte in mm</th><th>Form</th><th>Ecken der Platte</th></tr></thead><tbody>%s</tbody></table></div>'
            '<div class="tw"><table class="t"><thead><tr><th>Maß</th><th>Wert in mm</th><th>Bemerkung</th></tr></thead><tbody>%s</tbody></table></div></section>' % (de(P.WALL_MIN, 1), "".join(rows), trs2))


def sec_thread():
    st = stepper("einfaedeln", [(fig(s, "", "s460"), c) for s, c in frames_thread(3.0)], ["0 Start", "1 Nadel hoch", "2 Haken", "3 Faden über den Steg", "4 Hut, Knoten"])
    return ('<section class="sec"><h2>Einfädeln</h2>'
            '<p class="note">Der Faden muss über den Steg. Eine gerade Nadel schafft das nicht allein: gerechnet kommt eine Nadel mit Ø 1,2 mm nur etwa %s mm weit um den Steg (Luft 3,0), bei 4,5 mm Luft %s mm. '
            'Das ist kein Problem, weil die Tasche offen ist. Die Nadel bringt den Faden über den Steg, ein Haken oder eine Pinzette zieht ihn auf der anderen Seite herunter. '
            'Alternativ geht es ganz ohne Nadel: Faden an den Haken knoten oder einhängen, Haken von unten über den Steg schieben und herunterziehen.</p>%s'
            '<p class="note">Rechnung: <code>python3 -m plug.thread.reach --pill</code>, gerade Nadel als Strecke im Schnitt, Spitze bleibt in der Tasche. Quer zum Schnitt hat die Nadel in der 10 mm breiten Tasche zusätzlich Platz; die Zahl ist eine vorsichtige Untergrenze.</p></section>' % (NEEDLE[3.0], NEEDLE[4.5], st))


def sec_chain():
    d = P.pill(3.0)
    w = P.hole_eff
    rows = [("Luft über dem Steg", de(d["air"], 1), de(d["air"] - P.PRINT_LOSS, 1), "Faden doppelt %s: Platz; Stopfnadel %s: Platz (Decke darf sich bis 0,4 absenken)" % (de(P.THREAD_D, 1), de(P.NEEDLE_D, 1))),
            ("Spalt neben dem Steg (oben)", de(d["gap_top"], 1), de(d["gap_top"] - P.PRINT_LOSS, 1), "weit über jeder Nadel"),
            ("Tasche, Breite quer zum Steg", de(d["width"], 1), de(d["width"] - P.PRINT_LOSS, 1), "Pinzettenspitze passt"),
            ("Steg, Breite", de(d["steg_w"], 1), de(d["steg_w"] + P.PRINT_LOSS / 2, 1), "Steg wird durch Wulst eher breiter; Luft sinkt dadurch nicht, da nur die Decke zählt")]
    trs = "".join('<tr><td><b>%s</b></td><td class="n">%s</td><td class="n">%s</td><td>%s</td></tr>' % r for r in rows)
    load = ("20 N Zug je Ecke (angenommen, ungemessen, S) am Steg %s × %s mm, Spannweite %s mm: Biegespannung etwa %s MPa, Schub an den Enden etwa %s MPa; "
            "die Schichten liegen waagerecht, der Steg wird entlang der Schichten gezogen (Zugseite unten, quer zur Druckrichtung nicht belastet). Gedrucktes PLA hält ein Vielfaches."
            % (de(d["steg_w"], 0), de(d["steg_top"], 1), de(d["width"], 0), de(20 * d["width"] / 4 / (d["steg_w"] * d["steg_top"] ** 2 / 6), 1), de(20 / (2 * d["steg_w"] * d["steg_top"]), 1)))
    return ('<section class="sec"><h2>Maßkette im Worst-Case</h2><p class="note">Im Druck kann jedes freie Maß um bis zu %s mm kleiner werden (Wulst, Stufen; L02, L03). Das kleinste freie Maß der Tasche ist die Luft über dem Steg.</p>'
            '<div class="tw"><table class="t"><thead><tr><th>Stelle</th><th>Nenn mm</th><th>im Druck mm</th><th>Bewertung</th></tr></thead><tbody>%s</tbody></table></div>'
            '<p class="note">Last: %s</p></section>' % (de(P.PRINT_LOSS, 1), trs, load))


def sec_test():
    rows = []
    for name, air in (("F2-P3", 3.0), ("F2-P45", 4.5)):
        d = P.pill(air)
        pw, pl = math.ceil(d["mouth_l"] + 2 * P.WALL_MIN + 6), math.ceil(d["mouth_w"] + 2 * P.WALL_MIN + 6)
        rows.append((name, "Plattenecke %d × %d × %s mit Tasche, Luft %s (Decke %s), Fase %s und %s" % (pw, pl, de(P.PLATE_T, 1), de(air, 1), de(d["ceil"], 1), de(d["chamfer"], 1), de(d["steg_chamfer"], 1)),
                     "Unterkasten-Ecke, hohl 14,4 hoch, Eckaussparung %s × %s" % (de(d["notch_l"], 0), de(d["notch_w"], 0))))
    trs = "".join('<tr><td><b>%s</b></td><td>%s</td><td>%s</td></tr>' % r for r in rows)
    return ('<section class="sec"><h2>Was gedruckt würde (nach dem Abnicken)</h2>'
            '<p class="note">Ein Druck, zwei Eckmuster mit je zwei Teilen: Plattenecke (Unterseite am Druckbett, ohne Support, Thick bridges an) und Unterkasten-Ecke zum Daraufstellen. Kein Gebäude, kein Dock, keine Zapfen. '
            'Als „Hut“ dient ein Stück Filz oder Pappe unter dem Eckmuster. Material etwa 25 g, etwa 1,5 Stunden.</p>'
            '<div class="tw"><table class="t"><thead><tr><th>Teil</th><th>Plattenecke</th><th>Unterkasten</th></tr></thead><tbody>%s</tbody></table></div>'
            '<p class="note">Dazu <code>plug/thread/build.py</code> mit STL, README, ZIP und Prüfbericht (dicht, Überhänge, Luft unter der Decke gemessen) und ein Testbogen. Fragen im Testbogen: Faden mit Nadel und Haken über den Steg (ja, mit Mühe, nein); '
            'ohne Nadel mit Haken; kräftig am Faden ziehen (hält?); Faden hakt an Steg oder Decke; Decke unten sauber oder durchgehängt; welche Luft (3,0 oder 4,5); welche ZIP (Datum, L33); Variante immer nennen (L25).</p></section>' % trs)


def sec_risks():
    risks = [("Fase und Wand zum Plattenrand.", "Die Fase (%s mm) frisst Rand: Die Wand von %s mm zählt ab dem Rand der Fase, die Platte braucht deshalb etwas mehr Grundriss (gerechnet, passt). Am Steg-Fuß bleibt der Steg unten %s mm breit statt %s, seine Befestigung liegt an den Wänden und ist davon nicht betroffen." % (de(P.PILL["chamfer"], 1), de(P.WALL_MIN, 1), de(P.PILL["steg_w"] - 2 * P.PILL["steg_chamfer"], 1), de(P.PILL["steg_w"], 1))),
             ("Decke hängt durch.", "Über dem Steg liegt eine Brücke von nur 5 mm, die Viertelkreise laufen in den letzten 2 bis 3 mm flach aus. Sinkt die Decke um 0,4 mm, bleiben 2,6 mm Luft. Der Prüfbericht rechnet die Überhänge; Support wird nicht gesetzt, weil er in der engen Luft selbst zuschmoddert."),
             ("Faden scheuert.", "Steg-Oberkante ist voll gerundet (R 2,5), die Decke rund. Wenn der Faden an Schichtstufen hakt, kurz mit einem Stück Faden oder Schleifpapier durchziehen."),
             ("Einfädeln bleibt Handarbeit.", "Die Nadel allein kommt nicht um den Steg; Haken oder Pinzette gehören dazu. Der Test fragt, ob das mit deinem Werkzeug geht."),
             ("Eckaussparung schwächt die Ecke des Unterkastens.", "%s × %s mm bei Wand 2,4 mm; das Eckstück bleibt hohl und kann bei Bedarf verstärkt werden." % (de(P.pill()["notch_l"], 0), de(P.pill()["notch_w"], 0))),
             ("Nadel, Faden und Zugang zum Hut ungemessen.", "Die Rechnung nimmt Stopfnadel 1,6 und doppelten Faden 0,8 an (L08); der Ablauf nimmt an, dass du den Faden im Hut verknoten kannst.")]
    return '<section class="sec"><h2>Risiken</h2>%s</section>' % "".join('<p class="risk"><b>%s</b> %s</p>' % r for r in risks)


DECISIONS = [
    dict(id="M", tag="Fase", title="Größe der Fase an Ein- und Ausgang", rec="A",
         text="Du wolltest ordentlich Fase, damit man gut trifft. 45° druckt ohne Support und gleicht den Elefantenfuß am Bett aus.",
         opts=[("A", "2,0 mm am Taschenrand, 1,0 mm am Steg-Fuß (Empfehlung)"), ("B", "3,0 mm am Taschenrand, 1,5 mm am Steg-Fuß (Mündung 26 × 16, Eingang 12,0 mm weit)"), ("C", "1,5 mm und 0,5 mm (kleiner)")]),
    dict(id="L", tag="Luft", title="Luft über dem Steg", rec="C",
         text="Du hast etwa 3 mm genannt. Beide Größen passen ins Modell; der Test kann beide zeigen.",
         opts=[("A", "nur 3,0 mm (Decke 7,5)"), ("B", "nur 4,5 mm (Decke 9,0)"), ("C", "beide, ein Druck mit zwei Eckmustern (Empfehlung)")]),
    dict(id="D", tag="Druck", title="Support in der Tasche", rec="A",
         text="Support würde in der engen Luft über dem Steg selbst zuschmoddern. Die Decke ist rund und selbsttragend.",
         opts=[("A", "ohne Support, Thick bridges an (Empfehlung)"), ("B", "mit Support nur unter der Decke, einmal herausziehen")]),
    dict(id="N", tag="Werkzeug", title="Womit fädelst du?", rec="A",
         text="Das bestimmt den Testbogen, nicht die Geometrie.",
         opts=[("A", "Nadel und gebogener Draht oder Pinzette"), ("B", "nur Nadel, ohne Haken"), ("C", "andere (bitte in die Notiz)")]),
    dict(id="F", tag="Freigabe", title="Plan so abnicken und STL bauen?", rec="A",
         text="Wenn ja, erzeuge ich STL, README, ZIP und Prüfbericht für die beiden Eckmuster.",
         opts=[("A", "ja, bauen"), ("B", "noch nicht, Änderungen in der Notiz")]),
]


def main():
    sections = "".join([sec_diag(), sec_form(), sec_fit(), sec_thread(), sec_chain(), sec_test(), sec_risks()])
    sections += '<section class="top"><h2>Entscheidungen</h2><p class="lead">Fünf kurze Karten. Mit den Empfehlungen ist der Plan rund.</p></section>'
    sections += "\n".join(decision_card(x) for x in DECISIONS)
    spec = [dict(id=x["id"], tag=x["tag"], title=x["title"]) for x in DECISIONS]
    with open(TEMPLATE, encoding="utf-8") as f:
        page = f.read()
    page = page.replace("faden-plan-v1", "faden-plan-v2")
    for k, v in {"{{HEAD}}": head(), "{{SECTIONS}}": sections, "{{SPEC}}": json.dumps(spec, ensure_ascii=False)}.items():
        page = page.replace(k, v)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(page)
    print("geschrieben: %s (%d kB)" % (os.path.relpath(OUT, ROOT), os.path.getsize(OUT) / 1024))


if __name__ == "__main__":
    main()
