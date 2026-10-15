#!/usr/bin/env python3
"""Testbogen für den Testfall Kassette: baut plug/testcase/feedback.html aus feedback.template.html.

Führt Schritt für Schritt durch die Teile aus plug/testcase/build.py (stl/steckmodul_testcase/): Anleitung, Zeichnung mit Regler,
Formular (Auswahl und Freitext) und ein Ergebnistext zum Kopieren. Maße kommen aus plug/testcase/params.py.

Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m plug.testcase.build_feedback      # schreibt plug/testcase/feedback.html
"""
import base64
import io
import json
import math
import os

from PIL import Image

from plug import dupont as sd
from plug import series2 as N2
from plug.feedback.build import G, R_FIT, R_YN, de, fld, opts, render_field
from plug.feedback.build_night2 import E_FIT, E_HOLD, GOOD3, K_PASS
from plug.testcase import build_plan as BP
from plug.testcase import params as P

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TEMPLATE = os.path.join(HERE, "feedback.template.html")
OUT = os.path.join(HERE, "feedback.html")
PREV = os.path.join(ROOT, "vorschau", "steckmodul_testcase")


def img_uri(name, width):
    im = Image.open(os.path.join(PREV, name)).convert("RGB")
    im = im.resize((width, int(im.size[1] * width / im.size[0])), Image.LANCZOS)
    b = io.BytesIO()
    im.save(b, "JPEG", quality=86, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()


def variant_group(g, gname, var, shown):
    g.o.append('<g data-group="%s" data-var="%s" class="var%s">' % (gname, var, "" if shown else " off"))


# --------------------------------------------------------------------------
# Zeichnungen
# --------------------------------------------------------------------------
def kass_shape(g, k, tol):
    """Kassette v4 im Schnitt (x = 0), y' / z' wie in der Konstruktion."""
    y0, y1, zp, top, L = k["y_p0"], k["y1"], k["zp"], k["top"], k["L"]
    r = P.FILLET_T
    arc = [(y1 + r + r * math.cos(a), top - r + r * math.sin(a)) for a in [math.pi / 2 + j * math.pi / 2 / 12 for j in range(13)]]
    g.poly([(y1, 0), (L, 0), (L, top), (y1 + r, top)] + arc[1:] + [(y1, 0)], "d-kass")
    g.rect(0, y0, 0, top, "d-kass")
    e = P.ENTRY_CH_T
    g.poly([(y0 - e, -0.01), (y1 + e, -0.01), (y1, e), (y1, 0), (y0, 0), (y0, e)], "d-void")
    g.rect(y0, y1, zp - 0.01, top + 0.01, "d-void")


def svg_bestuecken():
    """Kassette wird von oben über die auf dem Tisch stehende Buchse gestülpt; Variante = Kassette 1 oder 2."""
    k = P.kass_dims()
    S, LIFT = 10.0, 9.0
    top, L, yb = k["top"], k["L"], k["ypin"]
    g = G(S, 28, (top + LIFT + 4.5) * S)
    g.rect(-1.5, L + 2.0, -1.4, 0.0, "d-slab")
    g.text(L / 2, -2.8, "flacher Tisch", "dls")
    g.group("K-mov", move=(0, LIFT, 0, 0))
    for var, tol, shown, nm in (("1", P.HSG_TOL_SAFE, False, "Kassette 1 (Luft 0,45)"), ("2", P.HSG_TOL_TIGHT, True, "Kassette 2 (Luft 0,15)")):
        variant_group(g, "KB", var, shown)
        kt = P.kass_dims(tol)
        kass_shape(g, kt, tol)
        g.text(L / 2 + 2, top / 2, "%s: Tasche %s hoch" % (nm, de(sd.HSG_H + tol, 2)), "dlb")
        g.end()
    g.end()
    g.rect(yb - 1.27, yb + 1.27, 0, sd.HSG_H, "d-hsg")
    g.rect(yb - 0.5, yb + 0.5, 0.5, 5.5, "d-term")
    g.o.append('<polyline points="%.1f,%.1f %.1f,%.1f" class="d-wire"/>' % (g.X(yb), g.Z(sd.HSG_H), g.X(yb), g.Z(top + LIFT + 1.5)))
    g.text(yb + 2.4, sd.HSG_H + 3.0, "Buchse steht mit der Steckseite auf dem Tisch,", "dls", "start")
    g.text(yb + 2.4, sd.HSG_H + 1.8, "die Adern gehen durch den Schlitz", "dls", "start")
    return g.svg(420, int((top + LIFT + 4.5) * S + 34), "Kassette wird über die auf dem Tisch stehende Buchse gestülpt")


def svg_press():
    """Kassette wird von unten ins Mini-Gebäude gedrückt, offene Seite voran; Variante = Gebäude A oder B (Spiel 8× überzeichnet)."""
    d = P.dims()
    F = d["F"]
    S, LIFT, EX = 9.0, 14.0, 8.0
    yc = d["yc"]
    fy0, fy1 = yc - P.BOX_L / 2, yc + P.BOX_L / 2
    ztop = d["box_top"]
    ox = -fy0 * S + 20
    oy = (ztop + 3.0) * S
    g = G(S, ox, oy)
    zk = -F + d["kass_h"]
    ch, e = sd.CH_F, 0.8
    c, cr = P.KASS_CLR_T * EX, P.KASS_RELIEF * EX
    sy0, sy1 = d["y_kass0"] - c, d["y_kass1"] + c
    for var, shown in (("A", True), ("B", False)):
        variant_group(g, "EB", var, shown)
        g.poly([(fy0 + ch, -F), (fy1 - ch, -F), (fy1, -F + ch), (fy1, ztop), (fy0, ztop), (fy0, -F + ch)], "d-bld")
        if var == "A":
            pts = [(sy0 - e, -F - 0.01), (sy1 + e, -F - 0.01), (sy1, -F + e), (sy1, zk), (sy0, zk), (sy0, -F + e)]
            txt = "Gebäude A: Spiel %s über die ganze Tiefe (%d× überzeichnet)" % (de(P.KASS_CLR_T), EX)
        else:
            ry0, ry1 = d["y_kass0"] - cr, d["y_kass1"] + cr
            z8 = -F + P.KASS_FIT_LEN
            pts = [(sy0 - e, -F - 0.01), (sy1 + e, -F - 0.01), (sy1, -F + e), (sy1, z8), (ry1, z8), (ry1, zk), (ry0, zk), (ry0, z8), (sy0, z8), (sy0, -F + e)]
            txt = "Gebäude B: %s mm Passzone mit %s, darüber %s Luft (%d× überzeichnet)" % (de(P.KASS_FIT_LEN, 0), de(P.KASS_CLR_T), de(P.KASS_RELIEF), EX)
        g.poly(pts, "d-void")
        g.rect(d["y_kass0"] + N2.E_LIP, d["y_kass1"] - N2.E_LIP, zk - 0.01, ztop + 0.01, "d-void")
        g.text(yc, ztop + 1.3, txt, "dlb")
        g.end()
    g.group("E-mov", move=(0, -LIFT, 0, 0))
    g.rect(d["y_kass0"], d["y_kass1"], -F, zk, "d-kass")
    g.rect(d["y_kass0"] + 1.2, d["y_kass0"] + 1.2 + P.kass_dims()["pk_d"], -F - 0.01, -F + sd.HSG_H + 0.2, "d-void")
    g.text(d["y_kass1"] - 9.0, -F + d["kass_h"] / 2, "Kassette", "dlb")
    g.text(d["y_kass1"] - 9.0, -F + d["kass_h"] / 2 - 1.6, "offene Seite voran", "dls")
    g.end()
    g.text(fy1 - 0.6, ztop - 0.7, "Anschlagrand", "dls", "end")
    return g.svg(int(38 * S + 60), int(oy + (F + LIFT + 2.5) * S), "Kassette wird von unten ins Mini-Gebäude gedrückt")


def svg_dock():
    """Winkelleiste wird von unten (durch den Kabelraum) in die Platte geschoben; Schnitt längs y, linker Teil der Platte."""
    d = P.dims()
    F, zhb, zbb, zlt = d["F"], d["z_hb"], d["z_bb"], d["z_lt"]
    S, LIFT = 9.0, 10.0
    yc = d["yc"]
    fy0 = yc - P.BOX_L / 2
    ph0, ph1 = BP.plate_y() if hasattr(BP, "plate_y") else (fy0 - P.PLATE_MARGIN, 14.0)
    ph0 = fy0 - P.PLATE_MARGIN
    yr = 14.0
    g = G(S, -ph0 * S + 22, 20 + (2.0 * S))
    clr, rel, cp, bd = P.MULDE_CLR_T, sd.RELIEF, sd.CH_P, sd.BAND
    g.rect(ph0, yr, zlt, 0.0, "d-slab")
    g.poly([(fy0 - clr - rel, -F), (yr + 0.5, -F), (yr + 0.5, 0.01), (fy0 - clr - cp, 0.01), (fy0 - clr, -cp), (fy0 - clr, -cp - bd), (fy0 - clr - rel, -cp - bd)], "d-void")
    yb, hd = d["yb"], sd.HDR_T / 2 + sd.SNUG_HDR
    g.rect(yb - hd - P.BODY_EXT_T, yb + hd, zbb, zhb, "d-void")
    g.rect(yb, 0.32 + 0.8, zbb, zhb, "d-void")
    g.rect(BP.LOETRAUM_Y0, yb - hd - P.BODY_EXT_T + 0.01, zbb, d["step"], "d-void")
    g.rect(BP.LOETRAUM_Y0, BP.KABEL_Y1, zlt, zbb, "d-void")
    g.rect(-sd.HOLE / 2, sd.HOLE / 2, zhb, -F + 0.01, "d-void")
    g.o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" class="d-dash"/>' % (g.X(ph0), g.Z(zlt), (yr - ph0) * S, P.LID_T_T * S))
    g.text((ph0 + yr) / 2 + 2.0, zlt - 1.5, "Deckel kommt danach, mit Fenster", "dls")
    g.group("W-mov", move=(0, -LIFT, 0, 0))
    g.rect(yb - sd.HDR_T / 2, yb + sd.HDR_T / 2, zbb, zhb, "d-body")
    g.rect(d["y_tail"], 0.32, d["z_bm"] - 0.32, d["z_bm"] + 0.32, "d-pin")
    g.rect(-0.32, 0.32, d["z_bm"] - 0.32, d["z_tip"], "d-pin")
    g.text(d["y_tail"] - 0.5, d["z_bm"] + 1.2, "Lötenden", "dl", "end")
    g.end()
    g.text(ph0 + 0.4, zhb + 0.9, "Muldenboden", "dls", "start")
    g.text(ph0 + 0.4, 1.4, "Mulde", "dls", "start")
    g.text(BP.LOETRAUM_Y0 + 1.0, zlt + 1.0, "Kabelraum", "dls", "start")
    return g.svg(int((yr - ph0) * S + 50), int(20 + 2 * S + (-zlt + LIFT + 2.5) * S), "Winkelleiste wird von unten in die Platte geschoben")


def svg_luft():
    """Drei Fälle: Buchse bündig, an den Schultern von Kassette 2, an den Schultern von Kassette 1."""
    tip = sd.HDR_UP - P.CEIL_T
    cases = [("Buchse bündig", 0.0, "ok"), ("Kassette 2, an den Schultern", P.HSG_TOL_TIGHT, "ok"), ("Kassette 1, an den Schultern", P.HSG_TOL_SAFE, "bad")]
    S, yb, H = 22.0, 205.0, 7.4
    o = []
    for i, (nm, gap, kind) in enumerate(cases):
        x0 = 14 + i * 222
        e = tip - gap
        o.append('<text x="%.1f" y="22" class="dlb">%s</text>' % (x0, nm))
        o.append('<rect x="%.1f" y="%.1f" width="14" height="%.1f" class="d-kass"/>' % (x0, yb - H * S, H * S))
        o.append('<rect x="%.1f" y="%.1f" width="14" height="%.1f" class="d-kass"/>' % (x0 + 166, yb - H * S, H * S))
        o.append('<rect x="%.1f" y="%.1f" width="120" height="%.1f" class="d-hsg"/>' % (x0 + 24, yb - H * S, (H - gap) * S))
        o.append('<rect x="%.1f" y="%.1f" width="12" height="%.1f" class="d-pin"/>' % (x0 + 78, yb - tip * S, tip * S + 20))
        o.append('<rect x="%.1f" y="%.1f" width="194" height="22" class="d-slab"/>' % (x0 - 7, yb, ))
        o.append('<text x="%.1f" y="%.1f" class="dls">Platte</text>' % (x0, yb + 15))
        ya, yt = yb - gap * S, yb - tip * S
        o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="%s"/>' % (x0 + 120, ya, x0 + 120, yt, "dimn" if kind == "ok" else "dlw-line"))
        o.append('<text x="%.1f" y="%.1f" class="%s">E = %s</text>' % (x0 + 126, (ya + yt) / 2 + 4, "dln" if kind == "ok" else "dlw", de(e)))
        o.append('<text x="%.1f" y="%.1f" class="dl">Luft unter der Buchse: %s mm</text>' % (x0, yb + 44, de(gap)))
        o.append('<text x="%.1f" y="%.1f" class="dls">%s</text>' % (x0, yb + 60, "stabiler Bereich" if kind == "ok" else "Aussetzer-Bereich"))
    return '<svg viewBox="0 0 680 290" role="img" aria-label="Luft unter der Buchse kostet Einstecktiefe" class="dgsvg">%s</svg>' % "".join(o)


# --------------------------------------------------------------------------
# Schritte
# --------------------------------------------------------------------------
STEPS = []


def add(sid, title, tag, lead, instr, diagrams, fields, edata=None, optional=False, calc=None):
    STEPS.append(dict(id=sid, title=title, tag=tag, lead=lead, instr=instr, diagrams=diagrams or [], fields=fields, optional=optional, calc=calc))


def steps():
    d = P.dims()
    add("p", "Vorbereiten", "0", "Alles hinlegen und die Kaufteile messen. Besonders wichtig ist die Höhe der Buchsen.",
        ["Teile auslegen und am Bild erkennen: <b>Kassette 1</b> hat eine Kerbe an der Seite (Luft über der Buchse 0,45), <b>Kassette 2</b> hat zwei Kerben (Luft 0,15). Die Gebäude tragen <code>GEB A</code> und <code>GEB B</code> (1 bzw. 2 Punkte), die Platte <code>PLATTE</code>.",
         "Mit der Schieblehre die <b>Höhe</b> von mehreren Dupont-Gehäusen messen (Soll 14,0): Kassette 2 passt nur, wenn die Buchse höchstens <b>14,15</b> mm hoch ist. Dazu den kürzesten senkrechten Pin der Winkelleiste und die Breite der Buchse (Soll 10,16).",
         "Bereitlegen: Winkelleiste, Buchse mit gecrimpten Adern (am besten zwei), LED-Streifen 10 mm, 4 Schrauben M3, Multimeter, ein <b>flacher Tisch</b> (Glas oder Brett)."],
        [("img", "teile.png", "Alle Teile in Druckausrichtung: Kassetten (orange), Gebäude (beige), Platte (blaugrau), Deckel (grün).")],
        [fld("p-hmin", "Höhe der Buchsengehäuse in mm: kleinster Wert", "text", ph="z. B. 14,0"),
         fld("p-hmax", "Höhe der Buchsengehäuse in mm: größter Wert", "text", ph="z. B. 14,2"),
         fld("p-pin", "Kürzester senkrechter Pin in mm", "text", ph="z. B. 6,9"),
         fld("p-bw", "Breite der Buchse in mm (kleinster bis größter Wert)", "text", ph="z. B. 10,1 bis 10,3"),
         fld("p-cr", "Sind die Kontakte an der Buchse gecrimpt (Adern dran)?", "select", R_YN("ja, alle 4", "nein, nur das leere Gehäuse")),
         fld("p-mm", "Multimeter mit Durchgangsprüfung vorhanden?", "select", R_YN("ja", "nein")),
         fld("p-scr", "Vier Schrauben M3 vorhanden?", "select", R_YN("ja", "nein, Deckel provisorisch"))])
    add("q", "Druckqualität ansehen", "1", "Bevor etwas gesteckt wird: die gedruckten Teile kurz prüfen. Diese Befunde gehören zum Ergebnis.",
        ["Jedes Teil von oben, unten und von der Seite ansehen. Mit dem Fingernagel die <b>Kanten am Bett</b> fühlen, besonders am <b>Schachteingang</b> der Gebäude (Fase 0,4).",
         "<b>Platte</b> von unten ansehen: der Muldenboden (0,4 mm, zwei Schichten) und die Decke des Kabelraums sind Brücken. Glatt oder durchgehängt?",
         "Erhabene Schrift und Kerben prüfen, die Pin-Löcher im Muldenboden und in den Kassetten (Fase beidseitig) mit einem Pin oder einer Nadel antasten."],
        [],
        [fld("q-all", "Welche Dateien wurden gedruckt?", "text", ph="z. B. alles"),
         fld("q-floor", "Muldenboden 0,4 über der Winkelleiste (Platte von unten)", "select", GOOD3("glatt, Löcher offen", "leicht durchgehängt", "stark durchgehängt oder Löcher zu", "Fehldruck")),
         fld("q-room", "Decke des Kabelraums", "select", GOOD3("glatt", "leicht durchgehängt", "stark durchgehängt", "Fehldruck")),
         fld("q-thick", "Thick bridges eingeschaltet?", "select", R_YN("ja", "nein", "weiß nicht")),
         fld("q-foot", "Elefantenfuß am Schachteingang und an der Fußunterkante", "select", GOOD3("sauber, Fase hat gewirkt", "leichter Wulst", "starker Wulst, musste entgratet werden")),
         fld("q-text", "Erhabene Schrift und Kerben", "select", GOOD3("gut lesbar und fühlbar", "lesbar, aber flach", "schlecht lesbar")),
         fld("q-hole", "Pin-Löcher offen", "select", GOOD3("alle offen", "einzelne zu", "viele zu")),
         fld("q-time", "Druckzeit insgesamt in Stunden", "text", ph="z. B. 2"),
         fld("q-fil", "Drucker und Filament", "text", ph="z. B. Bambu A1, PLA schwarz")])
    add("K", "Kassette bestücken", "K", "Die Buchse muss unten bündig mit der Kassette sitzen. Dafür wird die Kassette von oben über die Buchse gestülpt, nicht die Buchse von unten hineingeschoben.",
        ["Buchse mit der <b>Steckseite auf den flachen Tisch</b> stellen, Adern nach oben. Die Adern durch den <b>Schlitz</b> der Kassette fädeln.",
         "Kassette von oben über die Buchse stülpen, bis sie <b>auf dem Tisch steht</b>. Im Bild den Regler ziehen und die Kassette wählen.",
         "Mit <b>Kassette 2</b> anfangen. Geht keine Buchse hinein, ist sie zu hoch: dann nur Kassette 1 verwenden und das hier notieren.",
         "Prüfen: Sitzt die Buchse unten bündig? Wackelt sie? Dasselbe mit Kassette 1."],
        [("svg", "bestuecken", "Kassette 2: Tasche 14,15 hoch, nur 0,15 Luft über der Buchse. Kassette 1 ist die sichere Reserve.")],
        [fld("K-p2", "Passt eine Buchse in Kassette 2?", "select", GOOD3("ja, alle Buchsen", "nur einige", "keine, zu hoch")),
         fld("K-in2", "Kassette 2 über die Buchse stülpen", "select", R_FIT),
         fld("K-fl2", "Kassette 2: Buchse unten bündig", "select", GOOD3("bündig", "steht etwas heraus", "sitzt zu hoch, nicht bündig zu bekommen")),
         fld("K-ho2", "Kassette 2: Halt der Buchse in der Tasche", "select", GOOD3("fest", "locker", "fällt heraus")),
         fld("K-in1", "Kassette 1 über die Buchse stülpen", "select", R_FIT),
         fld("K-fl1", "Kassette 1: Buchse unten bündig", "select", GOOD3("bündig", "steht etwas heraus", "sitzt zu hoch, nicht bündig zu bekommen")),
         fld("K-ho1", "Kassette 1: Halt der Buchse in der Tasche", "select", GOOD3("fest", "locker", "fällt heraus"))])
    add("E", "Kassette einpressen", "E", "Hält die Kassette im Mini-Gebäude, wenn sie von unten eingedrückt wird? Gebäude A hat 0,06 Spiel über die ganze Tiefe, Gebäude B nur auf den ersten 8 mm.",
        ["Gebäude hinstellen, <b>Fuß unten</b> (so wie gedruckt). Die bestückte Kassette mit der <b>offenen Seite (Tasche, flache Oberseite) voran</b> von unten ansetzen. Im Bild den Regler ziehen und das Gebäude wählen.",
         "Mit dem Daumen eindrücken, bis sie am <b>Anschlagrand</b> anliegt. Wie viel Kraft? Dann das Gebäude umdrehen und schütteln: bleibt sie sitzen?",
         "Mit dem Daumen wieder herausdrücken: wie schwer geht das? Dasselbe mit Gebäude B.",
         "Nach dem Eindrücken prüfen, ob die Buchse noch bündig an der Fußunterkante sitzt oder durch die Kraft nach oben gerutscht ist."],
        [("svg", "press", "Gebäude A links, Gebäude B über die Auswahl. Das Spiel ist in der Zeichnung 8× überzeichnet.")],
        [fld("E-A", "Gebäude A (0,06 durchgehend): Sitz der Kassette", "select", E_FIT),
         fld("E-A-hold", "Gebäude A: Halt beim Umdrehen und Schütteln", "select", E_HOLD),
         fld("E-A-out", "Gebäude A: Herausdrücken", "select", opts([("", "– nicht geprüft –"), ("a", "mit dem Daumen leicht"), ("b", "nur mit kräftigem Druck"), ("c", "kaum")])),
         fld("E-B", "Gebäude B (Passzone 8 mm): Sitz der Kassette", "select", E_FIT),
         fld("E-B-hold", "Gebäude B: Halt beim Umdrehen und Schütteln", "select", E_HOLD),
         fld("E-B-out", "Gebäude B: Herausdrücken", "select", opts([("", "– nicht geprüft –"), ("a", "mit dem Daumen leicht"), ("b", "nur mit kräftigem Druck"), ("c", "kaum")])),
         fld("E-flush", "Buchse nach dem Eindrücken noch bündig an der Fußunterkante", "select", GOOD3("ja", "um 0,1 bis 0,2 hochgerutscht", "deutlich hochgerutscht", "nicht geprüft"))],
        calc="E")
    add("M", "Gebäude in die Mulde", "M", "Passt der L-Fuß in die Mulde mit Spiel 0,10? Gibt es nur eine Lage?",
        ["Platte mit der <b>Mulde nach oben</b> hinstellen. Das Gebäude (mit der Kassette darin oder ohne) von oben in die Mulde setzen: zuerst mit dem <b>Ausschnitt an der Ecke</b> richtig herum.",
         "Sinkt es mit Fingerdruck bis zum Boden? Wackelt es, wenn du oben anfasst und kippst?",
         "Dann um 180° gedreht ausprobieren: es soll <b>nicht</b> hineingehen."],
        [("svgcall", "top", "Draufsicht: L-förmiger Fuß in der Mulde mit Spiel 0,10, gestrichelt die Mulden-Fase.")],
        [fld("M-fit", "Fuß in der Mulde", "select", R_FIT),
         fld("M-key", "Nur eine Lage möglich (gedreht geht es nicht)", "select", GOOD3("ja, nur eine Lage", "geht auch gedreht, mit Kraft", "geht gedreht ohne Kraft")),
         fld("M-seat", "Sitz bis zum Boden", "select", GOOD3("sinkt bis zum Boden", "klemmt in den Ecken", "klemmt an einer Wand")),
         fld("M-wob", "Wackeln des Gebäudes in der Mulde", "select", GOOD3("kein spürbares Wackeln", "leichtes Wackeln", "wackelt deutlich"))])
    add("W", "Winkelleiste und Platte", "W", "Sitzt die Winkelleiste in der Platte, und ist hinter den Lötenden Platz?",
        ["Platte umdrehen, sodass die <b>Unterseite</b> mit dem Kabelraum oben liegt. Die Winkelleiste mit den <b>Pins zuerst</b> durch den Kabelraum in die Tasche schieben: Pins durch den Muldenboden, die Lötenden nach hinten. Im Bild den Regler ziehen.",
         "Liegt der Körper flach, treten die vier Pins gerade aus den Löchern, liegt das Lötende frei unter der Stufe?",
         "<b>Deckel</b> mit den vier Schrauben M3 schließen. Die Stempel sollen den Körper halten, das Fenster liegt über den Lötenden.",
         "Kabel an die Lötenden halten: Ist hinter den Spitzen Platz, und laufen sie nach unten durch das Fenster?"],
        [("svg", "dock", "Schnitt durch den linken Teil der Platte. Der Deckel kommt nach der Winkelleiste.")],
        [fld("W-body", "Körper in der Tasche", "select", GOOD3("liegt flach, sitzt fest", "leicht schief", "kippt oder wackelt")),
         fld("W-pins", "Pins treten gerade aus den Löchern", "select", GOOD3("ja, alle vier", "einzelne schief", "klemmen")),
         fld("W-step", "Lötende unter der Stufe", "select", GOOD3("liegt frei und flach", "streift die Stufe", "klemmt")),
         fld("W-lid", "Deckel schließt mit vier Schrauben", "select", GOOD3("ja, ohne Probleme", "mit Nacharbeit", "geht nicht")),
         fld("W-room", "Platz hinter den Lötenden", "select", GOOD3("genug, Kabel gehen nach unten weg", "knapp", "zu wenig")),
         fld("W-hold", "Winkelleiste hält beim Hin- und Herwackeln", "select", GOOD3("fest", "leichtes Spiel", "locker"))])
    add("S", "Stecken", "S", "Der Kern des Tests: Treffen die Pins die Buchse ohne Trichter, und wie weit rutscht die Buchse dabei nach oben?",
        ["Bestückte Kassette ins Gebäude drücken (Schritt E), Gebäude auf die Platte setzen, bis es unten anliegt. Im Bild den Regler ziehen.",
         "Beim Aufstecken beobachten: gehen alle vier Pins gleichzeitig hinein, oder muss man suchen oder rütteln?",
         "Gebäude wieder abziehen und die <b>Unterkante der Buchse</b> gegen die Fußunterkante des Gebäudes halten: Steht die Buchse bündig, oder ist sie nach oben gerutscht? Den Abstand mit der Schieblehre oder einer Fühlerlehre in mm schätzen (bündig = 0).",
         "Das Ganze mit <b>Kassette 2</b> und mit <b>Kassette 1</b> (jeweils in einem Gebäude, das gut hielt)."],
        [("svg", "section", "Schnitt längs durch die Pin-Reihe: Regler zieht das Gebäude ab."), ("svgcall", "luft", "Luft unter der Buchse kostet Einstecktiefe.")],
        [fld("S-hit", "Pins treffen die Buchse", "select", GOOD3("ohne Kraft, alle vier gleichzeitig", "mit leichtem Suchen oder Rütteln", "verkantet, einzelne Pins bleiben hängen", "geht nicht")),
         fld("S-force", "Kraft zum Aufstecken", "select", GOOD3("leicht", "mittel", "viel")),
         fld("S-luft-2", "Kassette 2: Abstand Buchsenunterkante zur Fußunterkante in mm (bündig = 0)", "text", ph="z. B. 0,1"),
         fld("S-luft-1", "Kassette 1: Abstand Buchsenunterkante zur Fußunterkante in mm (bündig = 0)", "text", ph="z. B. 0,3"),
         fld("S-seat", "Gebäude nach dem Aufstecken", "select", GOOD3("sitzt fest, kein Wackeln", "leichtes Wackeln", "wackelt deutlich"))],
        calc="S")
    add("D", "Durchgang und Abziehen", "D", "Hält der Kontakt stabil, und bleibt alles beim zehnmaligen Abziehen an seinem Platz?",
        ["Multimeter auf Durchgang: eine Spitze an das <b>Lötende</b> der Winkelleiste (waagrechter Pin hinten), die andere an die Ader des passenden Kontakts. Das für alle vier Pins.",
         "Dabei das Gebäude seitlich um etwa 0,5 mm schieben und leicht kippen. Bleibt der Durchgang stabil? Mit Kassette 2 und mit Kassette 1.",
         "Dann das Gebäude <b>zehnmal</b> abziehen und wieder aufstecken. Dabei achten: Bleibt die Kassette im Gebäude? Bleibt die Buchse in der Kassette? Gibt es danach noch Durchgang?"],
        [],
        [fld("D-2", "Kassette 2: Durchgang", "select", K_PASS),
         fld("D-1", "Kassette 1: Durchgang", "select", K_PASS),
         fld("D-kass", "Nach 10× Abziehen: Kassette bleibt im Gebäude", "select", GOOD3("ja, immer", "rutscht ein Stück heraus", "kommt heraus")),
         fld("D-buchse", "Nach 10× Abziehen: Buchse bleibt in der Kassette", "select", GOOD3("ja, immer", "rutscht etwas nach unten mit", "kommt mit den Pins heraus")),
         fld("D-dg", "Durchgang nach 10× Abziehen", "select", GOOD3("unverändert stabil", "wird schlechter", "bricht ab")),
         fld("D-pull", "Kraft zum Abziehen des Gebäudes aus der Mulde", "select", GOOD3("leicht", "mittel, hält gut", "sehr fest"))])
    add("L", "Adern, LED und Licht", "L", "Laufen die Adern im Bogen über das Podest, liegt die LED flach? Optional leuchtet sie.",
        ["Adern der Buchse durch den Schlitz nach oben führen und im <b>Bogen über die gerundete Kante</b> auf das Podest legen (Bild unten, rot).",
         "<b>LED-Streifen 10 mm</b> auf das Podest legen (Chips nach oben, Pads zur Buchse hin). Das Gebäudefenster ist 11,2 mm breit, der 12-mm-Streifen passt dort nicht.",
         "Optional: Controller an die Lötenden anschließen und die LED leuchten lassen (Pin 1 GND, 2 DIN, 3 +5 V, 4 DETECT)."],
        [("img", "kassette_v4.png", "Kassette v2 (oben links) und v4 (rechts), unten im Schnitt: rot die berechnete Ader.")],
        [fld("L-wire", "Adern über die runde Kante", "select", GOOD3("liegen im Bogen, kein Knick", "leichter Knick", "knicken stark", "keine Adern dran")),
         fld("L-led", "LED-Streifen auf dem Podest", "select", GOOD3("liegt flach, passt gut", "knapp", "passt nicht")),
         fld("L-win", "LED durch das Gebäudefenster sichtbar", "select", GOOD3("ja, frei", "Rand verdeckt etwas", "nein")),
         fld("L-light", "Licht (optional)", "select", opts([("", "– nicht geprüft –"), ("a", "leuchtet stabil"), ("b", "flackert beim Wackeln"), ("c", "leuchtet nicht")]))],
        optional=True)
    add("z", "Abschluss", "Σ", "Zum Schluss ein Gesamteindruck. Danach unten den Text kopieren und mir schicken.",
        ["Überlege, welche Kassette und welches Gebäude du weiterverwenden würdest und was als Nächstes passiert."],
        [],
        [fld("z-kass", "Welche Kassette?", "select", opts([("", "– bitte wählen –"), ("2", "Kassette 2 (Luft 0,15)"), ("1", "Kassette 1 (Luft 0,45)"), ("x", "keine, Tasche überarbeiten")])),
         fld("z-geb", "Welcher Schacht?", "select", opts([("", "– bitte wählen –"), ("A", "A: 0,06 durchgehend"), ("B", "B: Passzone 8 mm"), ("x", "keiner, Spiel überarbeiten")])),
         fld("z-boden", "Muldenboden 0,4", "select", opts([("", "– bitte wählen –"), ("a", "reicht, so lassen"), ("b", "auf 0,6 erhöhen"), ("c", "dünner nötig")])),
         fld("z-next", "Was als Nächstes", "select", opts([("", "– bitte wählen –"), ("a", "Konstanten übernehmen, Probestück und Institut umbauen"), ("b", "Federzunge testen"),
                                                            ("c", "Licht-Wandstreifen"), ("d", "Testfall nachbessern und noch einmal drucken")]))])


def render_diagram(step):
    out = []
    for kind, key, cap in step["diagrams"]:
        if kind == "img":
            out.append('<figure class="dg"><img src="%s" alt="%s" loading="lazy"><figcaption>%s</figcaption></figure>' % (img_uri(key, 900), cap, cap))
            continue
        if kind == "svgcall":
            svg = dict(top=BP.svg_top, luft=svg_luft)[key]()
            out.append('<figure class="dg"><div class="dgbox">%s</div><figcaption>%s</figcaption></figure>' % (svg, cap))
            continue
        svg = dict(bestuecken=svg_bestuecken, press=svg_press, dock=svg_dock, section=BP.svg_section)[key]()
        ctl = ""
        if key == "bestuecken":
            ctl += ('<label class="sel">Kassette <select class="dgvar" data-group="KB"><option value="1">1 (Luft 0,45)</option><option value="2" selected>2 (Luft 0,15)</option></select></label>'
                    '<label class="rng">Kassette absenken <input type="range" class="dgr" min="0" max="100" value="0" data-for="K-mov" aria-label="Kassette absenken"></label>')
        elif key == "press":
            ctl += ('<label class="sel">Gebäude <select class="dgvar" data-group="EB"><option value="A" selected>A</option><option value="B">B</option></select></label>'
                    '<label class="rng">Kassette eindrücken <input type="range" class="dgr" min="0" max="100" value="0" data-for="E-mov" aria-label="Kassette eindrücken"></label>')
        elif key == "dock":
            ctl += '<label class="rng">Winkelleiste einschieben <input type="range" class="dgr" min="0" max="100" value="0" data-for="W-mov" aria-label="Winkelleiste einschieben"></label>'
        else:
            ctl += '<label class="rng">Gebäude aufstecken <input type="range" class="dgr" min="0" max="100" value="100" data-for="T-mov" aria-label="Gebäude aufstecken"></label>'
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
