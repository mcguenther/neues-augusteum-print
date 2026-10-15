#!/usr/bin/env python3
"""Entscheidungen nach Nachtdruck 1: baut plug/decision/page.html aus template.html.

Jede Entscheidung: Befund aus dem Testbogen, Deutung, Entscheidung mit Vorher/Nachher-Zeichnung (Maße aus dims() und
plug/series2.py), geänderte Konstanten, Auswahl zum Zustimmen. Unten ein Text zum Kopieren.

Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m plug.decision.build      # schreibt plug/decision/page.html
"""
import json
import math
import os

from plug import dupont as sd
from plug import institute as I
from plug import series2 as N2
from plug.feedback.build import G

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(HERE)
TEMPLATE = os.path.join(HERE, "decision", "template.html")
OUT = os.path.join(HERE, "decision", "page.html")


def de(x, n=2):
    return ("%.*f" % (n, x)).replace(".", ",")


def tag(g, x, z, txt, cls="lbl", anchor="start"):
    g.text(x, z, txt, cls, anchor)


# --------------------------------------------------------------------------
# Zeichnungen
# --------------------------------------------------------------------------
def svg_k():
    """Einstecktiefe je Plättchen: Nacht 1 (grau, ohne Kontakte getestet) und Nacht 2 (neu, dünner)."""
    W, ox, sx = 560, 150, 62.0
    rows = [("Nacht 1", t, "old") for t in (1.2, 1.8, 2.4)] + [("Nacht 2", t, "new") for t in N2.K2_T]
    o = []
    y0, rh = 46, 26
    H = y0 + rh * len(rows) + 46
    # Bereich vor dem Kontakt (geschätzt)
    c = sd.TERM_OFF + sd.CONTACT
    o.append('<rect x="%.1f" y="%d" width="%.1f" height="%d" class="zone"/>' % (ox, y0 - 14, c * sx, rh * len(rows) + 8))
    o.append('<text x="%.1f" y="%d" class="lbls" text-anchor="middle">noch kein Kontakt (geschätzt bis %s mm)</text>' % (ox + c * sx / 2, y0 - 20, de(c, 1)))
    for k in range(0, 7):
        x = ox + k * sx
        o.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" class="grid"/>' % (x, y0 - 14, x, y0 + rh * len(rows) - 6))
        o.append('<text x="%.1f" y="%d" class="tick" text-anchor="middle">%d</text>' % (x, y0 + rh * len(rows) + 10, k))
    o.append('<text x="%.1f" y="%d" class="lbls" text-anchor="middle">Einstecktiefe E in mm (Pin steckt so tief in der Buchse)</text>' % (ox + 3 * sx, y0 + rh * len(rows) + 30))
    o.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" class="mark"/>' % (ox + sd.HDR_UP * sx, y0 - 14, ox + sd.HDR_UP * sx, y0 + rh * len(rows) - 6))
    o.append('<text x="%.1f" y="%d" class="lbls" text-anchor="end">Pin ganz: %s</text>' % (ox + sd.HDR_UP * sx - 4, y0 - 20, de(sd.HDR_UP)))
    last = None
    for i, (grp, t, kind) in enumerate(rows):
        y = y0 + i * rh
        if grp != last:
            o.append('<text x="10" y="%d" class="lblb">%s</text>' % (y + 12, grp))
            last = grp
        e = N2.e_of(t)
        o.append('<text x="%d" y="%d" class="lbl" text-anchor="end">t %s</text>' % (ox - 8, y + 12, de(t, 1)))
        o.append('<rect x="%.1f" y="%d" width="%.1f" height="%d" rx="3" class="bar-%s"/>' % (ox, y, e * sx, rh - 8, kind))
        o.append('<text x="%.1f" y="%d" class="lbl">%s</text>' % (ox + e * sx + 6, y + 12, de(e)))
    return '<svg viewBox="0 0 %d %d" role="img" aria-label="Einstecktiefe je Plättchendicke, alte und neue Serie" class="dsvg">%s</svg>' % (W, H, "".join(o))


def svg_n_old():
    """Schnitt durch die Wand, wo der Schieber hinausgeht: Nut mit durchhängender 34-mm-Decke und Fäden."""
    g = G(8.0, 160, 118)
    g.rect(-19, 19, 0, 9.0, "p-slab")
    g.poly([(-16.165, -0.01), (16.165, -0.01), (17.165, 1.0), (-17.165, 1.0)], "p-void")
    # Durchhang der Decke (Bogen) und Fäden
    pts = " ".join("%.1f,%.1f" % (g.X(y), g.Z(1.0 - 0.75 * math.cos(y / 17.165 * math.pi / 2))) for y in [i * 0.5 - 17.0 for i in range(69)])
    g.o.append('<polyline points="%s" class="sag"/>' % pts)
    for y in (-10, -5, -1, 4, 9, 13):
        g.o.append('<path d="M%.1f,%.1f q2,6 -1,12" class="thread"/>' % (g.X(y), g.Z(0.4)))
    g.poly([(-16.0, -1.2), (16.0, -1.2), (17.0, -0.2), (-17.0, -0.2)], "p-key")
    g.text(0, -2.8, "Schieber passt nicht hinein", "lblw")
    g.text(0, 10.4, "Brücke 34 mm über der Nut", "lblb")
    return g.svg(320, 150, "Alte Nut: Decke hängt durch, Fäden")


def svg_n_new():
    """Bodenplatte zum Eindrücken: Vertiefung mit 1,5 mm Rand um den Schacht, kurzer Überhang, keine Brücke."""
    g = G(8.0, 160, 118)
    sh = 15.165 + N2.KASS_CLR2                           # halbe Schachtlänge (Kassette v2)
    rm = sh + N2.B_MARGIN
    for s in (-1, 1):
        g.poly([(s * 19, 0), (s * rm, 0), (s * rm, 1.0), (s * sh, 1.0), (s * sh, 9.0), (s * 19, 9.0)], "p-slab")
    g.poly([(-rm + 0.15, -1.6), (rm - 0.15, -1.6), (rm - 0.15, -0.6), (-rm + 0.15, -0.6)], "p-key")
    for yy in (-15.0, 15.0):
        g.o.append('<path d="M%.1f,%.1f v-12 m-5,6 l5,-6 l5,6" class="arrow"/>' % (g.X(yy), g.Z(-1.9) + 10))
    g.text(-sh + 0.6, 4.6, "Schacht", "lbls", "start")
    g.text(0, 10.4, "Rand 1,5 mm, kurzer Überhang statt Brücke", "lblb")
    g.text(0, -3.3, "Platte von unten eindrücken", "lblw")
    return g.svg(320, 150, "Neue Bodenplatte: Vertiefung mit Rand, Platte wird eingedrückt")


def kass_profile(new):
    """Seitenprofil der Kassette (y–z, Unterkante z = 0) für Zeichnungen: Kennwerte alt bzw. neu."""
    d = I.dims()
    if not new:
        pk_d, zp = d["pk_d"], sd.HSG_H + sd.HSG_TOL
        y_p0 = d["HY"] - d["cass_y0"] - pk_d / 2
        seat0, seat1 = d["seat_y0"] - d["cass_y0"], d["seat_y1"] - d["cass_y0"]
        return dict(pk_d=pk_d, zp=zp, y_p0=y_p0, seat0=seat0, seat1=seat1, top=d["z_kt"] - d["z_face"],
                    sock=d["sock_d"], sock_top=d["z_kceil"] - d["z_face"], L=d["cass_len"], zs=d["z_s"] - d["z_face"])
    pk_d = sd.HSG_T + 2 * N2.SNUG2
    zp = sd.HSG_H + N2.HSG_TOL2
    y_p0 = sd.WALL
    seat0 = y_p0 + pk_d + sd.WALL + N2.GAP_L2
    seat1 = seat0 + I.SEAT_L + 2 * N2.SEAT_TOL
    zs = zp + N2.SEAT_RISE
    return dict(pk_d=pk_d, zp=zp, y_p0=y_p0, seat0=seat0, seat1=seat1, top=zs + sd.LED_REC, sock=None, sock_top=None,
                L=seat1 + sd.WALL, zs=zs)


def svg_c(new):
    p = kass_profile(new)
    g = G(11.0, 22, 196)
    if not new:
        g.rect(0, p["L"], 0, p["top"], "p-kass")
        g.rect(0, p["sock"], 0, p["sock_top"], "p-kass")
        g.rect(p["y_p0"], p["y_p0"] + p["pk_d"], -0.01, p["zp"], "p-void")
        g.rect(p["y_p0"] + p["pk_d"] / 2 - 0.65, p["y_p0"] + p["pk_d"] / 2 + 0.65, p["zp"] - 0.01, p["sock_top"] + 0.01, "p-void")
        g.rect(p["seat0"], p["seat1"], p["top"] - sd.LED_REC, p["top"] + 0.01, "p-void")
        # Rippen (Übermaß) als Markierung
        g.rect(p["y_p0"] + p["pk_d"] - 0.24, p["y_p0"] + p["pk_d"], 2.0, 11.0, "p-rib")
        yb = p["y_p0"] + p["pk_d"] / 2
        g.rect(yb - 1.27, yb + 1.27, 0, sd.HSG_H, "p-hsg")
        wire = [(yb, sd.HSG_H), (yb, p["sock_top"] - 0.3), (p["sock"] + 0.3, p["sock_top"] - 0.3), (p["seat0"] + 1.4, p["top"] - sd.LED_REC + 0.8)]
        g.o.append('<polyline points="%s" class="wire"/>' % " ".join("%.1f,%.1f" % (g.X(y), g.Z(z)) for y, z in wire))
        g.rect(p["seat0"] + 0.4, p["seat0"] + 0.4 + 16.7, p["top"] - sd.LED_REC, p["top"] - sd.LED_REC + 0.3, "p-led")
        g.text(p["sock"] + 0.6, p["sock_top"] + 1.0, "Knick", "lblw", "start")
        g.text(p["L"] / 2 + 3, 7.0, "Nacht 1", "lblb")
        g.text(p["y_p0"] + p["pk_d"] + 0.4, 6.5, "Rippen", "lblw", "start")
    else:
        zp, zs, top = p["zp"], p["zs"], p["top"]
        y1 = p["y_p0"] + p["pk_d"]
        r = N2.FILLET
        # rechter Körper: Ablage und Aderkanal auf Höhe zs, Kante zur Tasche mit Radius r gerundet
        cy, cz = y1 + r, zs - r
        arc = [(cy + r * math.cos(a), cz + r * math.sin(a)) for a in [math.pi / 2 + k * math.pi / 2 / 10 for k in range(11)]]
        g.poly([(y1, 0), (p["L"], 0), (p["L"], top), (p["seat1"], top), (p["seat1"], zs)] + arc + [(y1, 0)], "p-kass")
        g.rect(0, p["y_p0"], 0, top, "p-kass")                                      # linke Wand
        g.o.append('<polygon points="%s" class="p-void"/>' % " ".join("%.1f,%.1f" % (g.X(y), g.Z(z)) for y, z in
                   [(p["y_p0"] - N2.ENTRY_CH, -0.01), (y1 + N2.ENTRY_CH, -0.01), (y1, N2.ENTRY_CH), (y1, 0.0), (p["y_p0"], 0.0), (p["y_p0"], N2.ENTRY_CH)]))
        yb = p["y_p0"] + p["pk_d"] / 2
        g.rect(yb - 1.27, yb + 1.27, 0, sd.HSG_H, "p-hsg")
        g.o.append('<path d="M%.1f,%.1f C%.1f,%.1f %.1f,%.1f %.1f,%.1f L%.1f,%.1f" class="wire"/>' % (
            g.X(yb), g.Z(sd.HSG_H), g.X(yb), g.Z(zs + 1.0), g.X(y1), g.Z(zs + 0.9), g.X(y1 + r + 0.5), g.Z(zs + 0.75),
            g.X(p["seat0"] + 1.4), g.Z(zs + 0.75)))
        g.rect(p["seat0"] + 0.4, p["seat0"] + 0.4 + 16.7, zs, zs + 0.3, "p-led")
        g.text(p["L"] / 2 + 3, 7.0, "Nacht 2", "lblb")
        # Maße
        g.line(p["seat0"], zs - 0.6, y1 + 1.2, zs - 0.6, "dimn")
        g.text((p["seat0"] + y1) / 2 + 0.6, zs - 2.0, "+1 mm", "lbln")
        g.text(p["seat1"] - 1, zs + 1.4, "Ablage %s mm über Taschenoberkante" % de(N2.SEAT_RISE, 1), "lbln", "end")
        g.text(y1 + r + 0.3, zs - 3.4, "rund R %s" % de(r, 1), "lbln", "start")
        g.text(yb, -1.6, "Fase %s" % de(N2.ENTRY_CH, 1), "lbln")
    return g.svg(390, 230, "Kassette %s im Schnitt" % ("neu" if new else "alt"))


def svg_d(ext):
    """Passprobe: Körpertasche und Stufe fürs Lötende (Schnitt längs y, Taschenseite oben). ext = Verlängerung zum Lötende."""
    g = G(24.0, 250, 150)
    hd = sd.HDR_T / 2 + sd.SNUG_HDR
    g.rect(-9.0, 3.5, 0, 4.0, "p-slab")
    g.rect(-hd - ext, hd, 0.8, 4.01, "p-void")                      # Körpertasche
    g.rect(-hd - ext - sd.RA_TAIL - 0.9 + ext, -hd - ext, 1.48, 4.01, "p-void")   # Lötendenschlitz (kürzer um ext)
    g.rect(hd, 2.32 + 0.32 + 0.8, 0.8, 4.01, "p-void")
    if ext == 0:
        # realer Körper etwas länger (Abbruchrest, Grat): liegt auf der Stufenkante, kippt
        ang = -9.0
        cx, cz = -0.2, 1.8 + 0.35
        body = [(-1.25, -1.0), (1.25, -1.0), (1.25, 1.0), (-1.25, 1.0)]
        rot = lambda p: (cx + p[0] * math.cos(math.radians(ang)) - p[1] * math.sin(math.radians(ang)),
                         cz + p[0] * math.sin(math.radians(ang)) + p[1] * math.cos(math.radians(ang)))
        g.poly([rot(p) for p in body], "p-body")
        g.text(-4.5, 5.0, "Körper liegt auf der Stufe auf → schief", "lblw")
    else:
        g.rect(-1.25, 1.25, 0.8, 2.8, "p-body")
        g.rect(-1.25 - sd.RA_TAIL, -1.0, 1.48, 2.12, "p-pin")
        g.text(-4.5, 5.0, "Tasche %s mm länger, Körper liegt flach" % de(ext, 1), "lbln")
    g.text(-6.2, 0.4, "Stufe", "lbls")
    return g.svg(400, 180, "Passprobe Tasche")


def svg_fm():
    g = G(6.5, 180, 112)
    g.poly([(-23, 0), (23, 0), (23, 11.0), (-23, 11.0)], "p-slab")
    g.poly([(-18.3, 1.2), (18.3, 1.2), (18.3, 5.0), (19.5, 11.0), (-19.5, 11.0), (-18.3, 5.0)], "p-void")
    g.poly([(-18, 1.2), (18, 1.2), (18, 11.0 + N2.LEHRE_CAP), (-18, 11.0 + N2.LEHRE_CAP)], "p-bld")
    g.poly([(-16, 3.2), (16, 3.2), (16, 11.0 + N2.LEHRE_CAP + 0.01), (-16, 11.0 + N2.LEHRE_CAP + 0.01)], "p-void2")
    g.text(0, 7.5, "Fuß-Lehre (neu)", "lblb")
    g.text(0, -1.6, "Mulden-Ring aus Nacht 1", "lbl")
    return g.svg(360, 140, "Fuß-Lehre im Mulden-Ring")


def svg_label():
    """Beschriftung: erhaben statt graviert, Rang als Kerben in der Kante, Fase an der Bettkante."""
    o = []
    o.append('<rect x="20" y="30" width="200" height="70" rx="4" class="blk"/>')
    o.append('<text x="120" y="76" class="engr" text-anchor="middle">S 0,10</text>')
    o.append('<text x="120" y="122" class="lbls" text-anchor="middle">Nacht 1: graviert, in Schwarz kaum zu sehen</text>')
    o.append('<rect x="280" y="30" width="200" height="70" rx="4" class="blk"/>')
    o.append('<text x="380" y="78" class="rais" text-anchor="middle">S 0,10</text>')
    for k in range(2):
        o.append('<path d="M%d,30 l5,9 l5,-9 z" class="notch"/>' % (296 + k * 14))
    o.append('<path d="M280,92 l8,8 h-8 z" class="cham"/><path d="M480,92 l-8,8 h8 z" class="cham"/>')
    o.append('<text x="380" y="122" class="lbls" text-anchor="middle">Nacht 2: erhaben 0,6 mm, Kerben = Rang, Fase unten</text>')
    return '<svg viewBox="0 0 500 132" role="img" aria-label="Beschriftung alt und neu" class="dsvg">%s</svg>' % "".join(o)


# --------------------------------------------------------------------------
# Inhalt
# --------------------------------------------------------------------------
def decisions():
    d = I.dims()
    pk_old = kass_profile(False)
    pk_new = kass_profile(True)
    D = []
    D.append(dict(
        id="K", title="Kontakt-Tiefe: Test wiederholen, mit Kontakten und dünneren Plättchen", tag="K", status="Rückfrage",
        found="Kein stabiler Durchgang, bei 1,2 mm Aussetzer, bei 1,8 und 2,4 nichts. Die Buchse hielt kaum. Laut Vorbereitung war es <b>das leere Gehäuse, ohne Kontakte</b>.",
        why="Halt und Kontakt kommen nur von den Federn der Crimp-Kontakte. Ein leeres Gehäuse hält nicht und leitet nicht, deshalb sagt dieser Test über die Einstecktiefe noch nichts aus. "
            "Dein Vorschlag, dünner zu testen, ist trotzdem richtig: Hält der Kontakt erst ab etwa 4,5 mm, müssen Muldenboden und Trichterplatte dünner werden.",
        decision="K mit <b>eingesetzten Kontakten</b> wiederholen (gecrimpt, oder zum Test nur die Kontakte ohne Ader einschieben und von oben mit der Messspitze an die Krallen). "
                 "Plättchen <b>0,6 / 0,9 / 1,2 / 1,5 / 1,8 mm</b>, also E = 5,08 bis 3,88 mm.",
        consts=[("Plättchen", "1,2 / 1,8 / 2,4", "0,6 / 0,9 / 1,2 / 1,5 / 1,8"), ("CEIL + FUNNEL_T", "0,8 + 1,0", "offen, folgt aus K")],
        figs=[("Einstecktiefe je Plättchen", svg_k())],
        ask="Waren beim Test Kontakte im Gehäuse? Wenn ja, steckt der Kontaktpunkt tiefer als angenommen, und die dünnen Plättchen werden noch wichtiger."))
    D.append(dict(
        id="N", title="Schieber in der Nut ersetzen durch Bodenplatte zum Eindrücken", tag="N → B", status="Empfehlung",
        found="Alle vier Schieber klemmten, keiner ließ sich einschieben. Die Decke über der Nut hing stark durch, unten lösten sich Fäden. Elefantenfuß etwa 0,2 mm.",
        why="Drei Ursachen addieren sich. (1) Die Nut läuft durch die Wand nach außen, darüber liegt eine <b>Brücke von 34 mm</b>, die durchhängt und Fäden in die Nut hängt. "
            "(2) Die Nut öffnet zum Bett und der Schieber liegt auf dem Bett: Der Elefantenfuß macht beide um je etwa 0,2 mm breiter bzw. enger. "
            "(3) 0,05 bis 0,20 mm Spiel ist für eine 20 mm lange Gleitpassung zu knapp; gedruckte Schiebeführungen brauchen meist 0,2 bis 0,4 mm je Seite. "
            "Mehr Spiel allein löst die Brücke nicht. Üblich bei gedruckten Deckeln von unten ist ein Einsatz in einer Vertiefung, gehalten durch Klemmung, ohne Durchbruch in der Wand.",
        decision="Statt Schieber: <b>Bodenplatte</b> (Trichterplatte, 1 mm) in einer Vertiefung unter dem Schacht. Die Vertiefung ist %s mm breiter als der Schacht, ihr Rand ist nur ein kurzer Überhang. "
                 "Platte von unten eindrücken, Halt durch Klemmung, Griffkerbe zum Lösen, Fasen an Platte und Vertiefung. Prüfkörper mit Spiel <b>0,05 / 0,10 / 0,15 / 0,20</b> je Seite. "
                 "Im Gebäude sperrt der Muldenboden die Platte zusätzlich." % de(N2.B_MARGIN, 1),
        consts=[("Halterung", "Schieber in Schwalbenschwanz-Nut", "Bodenplatte in Vertiefung"), ("KEY_CLR", "0,15", "entfällt"), ("B_CLR (neu)", "–", "0,05 bis 0,20, Ergebnis offen")],
        figs=[("Nacht 1: Schnitt durch die Wand", svg_n_old()), ("Nacht 2: Schnitt durch den Schacht", svg_n_new())],
        alt="Alternative: Schieber behalten mit 0,3 bis 0,5 mm Spiel und 0,5 mm mehr Luft unter der Decke. Die Brücke bleibt dann bestehen."))
    D.append(dict(
        id="S", title="Schachtspiel 0,20 → 0,15 mm, mit Einführfase", tag="S", status="Entscheidung",
        found="0,05 passt nicht, 0,10 nur mit Kraft, <b>0,15 ideal</b>, 0,20 minimales Spiel.",
        why="0,15 ist die engste Variante ohne Kraft. Eine Fase an der Schachtöffnung erleichtert das Einsetzen, ohne das Spiel zu vergrößern.",
        decision="<code>KASS_CLR</code> = <b>0,15</b>, Einführfase %s mm an der Schachtöffnung." % de(N2.ENTRY_CH, 1),
        consts=[("KASS_CLR", "0,20", "0,15"), ("Einführfase", "–", "0,4 an jeder Steckstelle")], figs=[]))
    D.append(dict(
        id="C", title="Kassette v2: Tasche, Ablage, runder Aderweg", tag="C + R", status="Entscheidung",
        found="Buchse nur mit Kraft und nicht ganz hinein. Adern knicken stark zwischen Taschenoberkante und Ablage. LED-Streifen 10 und 12 mm passen in der Breite, in der Länge fehlt 1 mm Richtung Tasche. "
              "Hülse R mit <b>0,20 ohne Rippen</b>: ziemlich perfekt.",
        why="Die Rippen (0,12 Übermaß) machten die Tasche enger als jede Hülse; 0,20 ohne Rippen passt. Die Ablage lag %s mm <i>unter</i> der Taschenoberkante, dazwischen eine scharfe Kante: Die Adern mussten hoch, über die Kante und wieder hinunter." % de(abs(pk_old["zs"] - pk_old["zp"])),
        decision="<ul><li>Tasche: Spiel <b>0,20</b> je Seite, <b>keine Rippen</b>, <b>0,2 mm höher</b>, Einführfase %s unten.</li>"
                 "<li>Ablage <b>%s mm über</b> der Taschenoberkante, Kante zur Tasche <b>rund (R %s)</b>, Aderkanal %s mm breit und oben offen. Die Enden der Buchse stoßen links und rechts an zwei Schultern an.</li>"
                 "<li>Ablage <b>1 mm weiter weg</b> von der Tasche, je Seite %s mm Luft (Toleranz für den 10-mm-Streifen).</li></ul>"
                 % (de(N2.ENTRY_CH, 1), de(N2.SEAT_RISE, 1), de(N2.FILLET, 1), de(N2.WIRE_W, 1), de(N2.SEAT_TOL)),
        consts=[("SNUG", "0,22", "0,20"), ("RIB", "0,12", "0 (keine)"), ("HSG_TOL (Taschenhöhe)", "0,25", "0,45"), ("GAP_L (Tasche → Ablage)", de(sd.GAP_L, 1), de(N2.GAP_L2, 1)),
                ("Ablage zur Taschenoberkante", "−%s" % de(abs(pk_old["zs"] - pk_old["zp"])), "+%s" % de(N2.SEAT_RISE, 1)),
                ("Kassette: Länge", de(pk_old["L"], 1), de(pk_new["L"], 1)),
                ("Oberkante Ablage über Unterkante", de(pk_old["top"], 1), de(pk_new["top"], 1))],
        figs=[("Nacht 1: Ader muss hoch, über die Kante und wieder runter", svg_c(False)), ("Nacht 2: Ablage höher, Kante rund, 1 mm mehr Abstand", svg_c(True))],
        note="Folge für das Gebäude (später, nicht in dieser Nacht): Die Kassette wird %s mm höher, Kammerboden und Fenster rücken mit." % de(pk_new["top"] - pk_old["top"], 1)))
    D.append(dict(
        id="D", title="Passprobe: Körpertasche zum Lötende hin verlängern", tag="D", status="Test",
        found="In allen drei Feldern schief. Dein Verdacht: Der Kunststoffkörper liegt ein wenig auf der Stufe fürs Lötende auf.",
        why="Der echte Körper ist durch den Abbruchrest und Grate etwas länger als 2,0 mm. Liegt seine Kante auf der Stufe, kippt die ganze Leiste.",
        decision="Neue Passprobe mit drei Feldern: Tasche <b>0,5 / 1,0 / 1,5 mm</b> länger zum Lötende hin, Stufe entsprechend kürzer. Körperhöhe bleibt 2,0.",
        consts=[("Körpertasche Richtung Lötende", "+0", "+0,5 / +1,0 / +1,5 (Ergebnis offen)")],
        figs=[("Nacht 1", svg_d(0)), ("Nacht 2 (Beispiel +1,0)", svg_d(1.0))]))
    D.append(dict(
        id="FM", title="Fuß-Lehre für die Mulden-Ringe", tag="FM", status="Ergänzung",
        found="Nicht getestet, weil unklar war, was das Gebäude-Probestück ist.",
        why="Die Ringe sind schon gedruckt. Es fehlt nur ein Fuß in Originalform.",
        decision="<b>Fuß-Lehre</b> in die ZIP: Fuß des Probestücks (22 × 36 mm, Kodierecke, Fase unten), oben offen und leicht. Ringe aus Nacht 1 weiterverwenden.",
        consts=[], figs=[("Fuß-Lehre im Ring", svg_fm())]))
    D.append(dict(
        id="G", title="Druck allgemein: Beschriftung, Elefantenfuß, Brücken", tag="Druck", status="Regel",
        found="Schwarzes PLA, Gravur schlecht lesbar. Elefantenfuß etwa 0,2 mm. Die einzige lange Brücke (S) ist misslungen.",
        why="Gravuren in Schwarz verschwinden; erhabene Schrift und Kerben in der Kante fangen Licht und lassen sich fühlen.",
        decision="<ul><li>Beschriftung <b>erhaben</b> (0,6 mm) auf Flächen, die nicht passen müssen, sonst Kerben in der Kante; <b>Rang als Kerben</b> (1 Kerbe = engste Variante).</li>"
                 "<li><b>Fase %s</b> an den Bettkanten aller Steckteile, <b>Einführfase %s</b> an jeder Öffnung.</li><li>Keine Brücken über 10 mm.</li></ul>" % (de(N2.EF_CH, 1), de(N2.ENTRY_CH, 1)),
        consts=[], figs=[("Beschriftung alt und neu", svg_label())]))
    return D


PLAN = [
    ("K", "Kontakt-Plättchen", "5 Plättchen 0,6 bis 1,8 mm", "≈ 2 g"),
    ("B", "Bodenplatte-Prüfkörper", "4 Körper mit Schacht 0,15 und Vertiefung, 4 Platten 0,05 bis 0,20", "≈ 12 g"),
    ("C", "Kassette v2", "2 Stück (eine zum Bestücken, eine als Lehre für B)", "≈ 8 g"),
    ("D", "Passprobe v7", "3 Felder, Tasche +0,5 / +1,0 / +1,5", "≈ 2 g"),
    ("FM", "Fuß-Lehre", "für die Mulden-Ringe aus Nacht 1", "≈ 4 g"),
]


def card(dd):
    figs = "".join('<figure class="fig"><div class="figbox">%s</div><figcaption>%s</figcaption></figure>' % (svg, cap) for cap, svg in dd["figs"])
    consts = ""
    if dd["consts"]:
        consts = '<table class="ct"><thead><tr><th>Größe</th><th>Nacht 1</th><th>Nacht 2</th></tr></thead><tbody>%s</tbody></table>' % "".join(
            "<tr><td>%s</td><td>%s</td><td><b>%s</b></td></tr>" % c for c in dd["consts"])
    extra = ""
    if dd.get("alt"):
        extra += '<p class="alt"><b>Alternative:</b> %s</p>' % dd["alt"].replace("Alternative: ", "")
    if dd.get("note"):
        extra += '<p class="note">%s</p>' % dd["note"]
    if dd.get("ask"):
        extra += '<p class="ask"><b>Rückfrage:</b> %s</p>' % dd["ask"]
    sel = ('<label class="ok" for="a-%s"><span>Deine Meinung</span><select id="a-%s" data-did="%s"><option value="">– bitte wählen –</option>'
           '<option value="ok">einverstanden</option><option value="mod">einverstanden, mit Änderung (Notiz)</option><option value="no">nicht einverstanden</option></select></label>'
           '<label class="ok wide" for="n-%s"><span>Notiz</span><input type="text" id="n-%s" data-nid="%s" placeholder="optional"></label>') % (dd["id"], dd["id"], dd["id"], dd["id"], dd["id"], dd["id"])
    return ('<article class="dec" id="d-%s"><header><span class="tg">%s</span><h2>%s</h2><span class="st st-%s">%s</span></header>'
            '<div class="cols"><div class="txt"><p><b>Befund.</b> %s</p><p><b>Deutung.</b> %s</p><div class="dcs"><b>Entscheidung.</b> %s</div>%s%s</div>'
            '<div class="figs">%s</div></div><div class="vote">%s</div></article>') % (
        dd["id"], dd["tag"], dd["title"], dd["status"].lower().replace("ü", "ue"), dd["status"], dd["found"], dd["why"], dd["decision"], consts, extra, figs, sel)


def main():
    D = decisions()
    cards = "\n".join(card(x) for x in D)
    plan = "".join("<tr><td><b>%s</b></td><td>%s</td><td>%s</td><td class=\"num\">%s</td></tr>" % p for p in PLAN)
    spec = [dict(id=x["id"], tag=x["tag"], title=x["title"]) for x in D]
    with open(TEMPLATE, encoding="utf-8") as f:
        page = f.read()
    for k, v in {"{{CARDS}}": cards, "{{PLAN}}": plan, "{{SPEC}}": json.dumps(spec, ensure_ascii=False)}.items():
        page = page.replace(k, v)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(page)
    print("geschrieben: %s (%d kB), %d Entscheidungen" % (os.path.relpath(OUT, ROOT), os.path.getsize(OUT) / 1024, len(D)))


if __name__ == "__main__":
    main()
