#!/usr/bin/env python3
"""Testbogen für den zweiten Nachtdruck: baut plug/feedback/page_night2.html aus template_night2.html.

Wie der Bogen zu Nacht 1 (plug/feedback/build.py), aber für die Teile aus plug/series2.py (stl/steckmodul_night2/): Anleitung, Zeichnung mit
Schieberegler, Formular (Auswahl und Freitext) und ein Ergebnistext zum Kopieren. Maße der Zeichnungen und die Varianten kommen aus
plug/series2.py, die Zeichenhilfen und Auswahllisten aus plug/feedback/build.py.

Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m plug.feedback.build_night2      # schreibt plug/feedback/page_night2.html
"""
import base64
import io
import json
import math
import os

from PIL import Image

from plug import dupont as sd
from plug import institute as I
from plug import series2 as N2
from plug.feedback.build import G, R_FIT, R_SLIDE, R_YN, de, fld, opts, render_field

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))          # plug/
ROOT = os.path.dirname(HERE)
TEMPLATE = os.path.join(HERE, "feedback", "template_night2.html")
OUT = os.path.join(HERE, "feedback", "page_night2.html")
PREV = os.path.join(ROOT, "vorschau", "steckmodul_night2")


def img_uri(name, width):
    im = Image.open(os.path.join(PREV, name)).convert("RGB")
    im = im.resize((width, int(im.size[1] * width / im.size[0])), Image.LANCZOS)
    b = io.BytesIO()
    im.save(b, "JPEG", quality=86, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()


def variant_group(g, gname, var, shown):
    """Beginnt eine Gruppe, die der Variantenwahl folgt (data-group / data-var, ausgeblendet über .off)."""
    g.o.append('<g data-group="%s" data-var="%s" class="var%s">' % (gname, var, "" if shown else " off"))


# --------------------------------------------------------------------------
# Zeichnungen (SVG, z nach oben, Maße in mm → px)
# --------------------------------------------------------------------------
def svg_k():
    """Kontakt-Tiefe: Winkelleiste, Plättchen t, Buchse wird aufgedrückt (Front, Buchse halbtransparent, Pins davor)."""
    g = G(14.0, 225, 392)
    START = sd.HDR_UP + 2.0 + 4.0
    for k, t in enumerate(N2.K2_T):
        e = N2.e_of(t)
        variant_group(g, "K", de(t, 1), k == 2)
        g.rect(-5.33, 5.33, 0, 2.0, "d-body")
        g.rect(-7.25, 7.25, 2.0, 2.0 + t, "d-gold")
        g.group("", move=(0, START - (2.0 + t), 0, 0))
        g.rect(-5.08, 5.08, 2.0 + t, 2.0 + t + sd.HSG_H, "d-hsg")
        for x in sd.pin_x():
            g.rect(x - 0.9, x + 0.9, 2.0 + t + 0.6, 2.0 + t + sd.HSG_H - 0.4, "d-slot")
            g.rect(x - 0.8, x + 0.8, 2.0 + t + 0.5, 2.0 + t + 5.0, "d-term")
        g.end()
        for x in sd.pin_x():
            g.rect(x - 0.32, x + 0.32, 1.0, 2.0 + sd.HDR_UP, "d-pin")
        g.line(-8.6, 2.0 + t, -8.6, 2.0 + sd.HDR_UP)
        g.line(-9.1, 2.0 + t, -8.1, 2.0 + t)
        g.line(-9.1, 2.0 + sd.HDR_UP, -8.1, 2.0 + sd.HDR_UP)
        g.text(-9.4, 2.0 + t + e / 2 - 0.3, "E = %s mm" % de(e), "dlb", "end")
        g.text(0, -1.0, "Winkelleiste", "dl")
        g.text(8.0, 2.0 + t / 2 - 0.2, "Plättchen %s" % de(t, 1), "dl", "start")
        g.end()
    return g.svg(450, 420, "Buchse wird über Plättchen auf die Pins der Winkelleiste gedrückt")


def svg_c():
    """Kassette v2 (Schnitt längs y durch die Mitte): Buchse von unten bis an die Schultern, Adern über die runde Kante, LED auf die flache Oberseite."""
    k = N2.kass2_dims()
    S = 11.0
    g = G(S, 36, 215)
    y0, y1, zp, top, L, r = k["y_p0"], k["y1"], k["zp"], k["top"], k["L"], N2.FILLET
    yb = k["ypin"]
    cy, cz = y1 + r, top - r
    arc = [(cy + r * math.cos(a), cz + r * math.sin(a)) for a in [math.pi / 2 + j * math.pi / 2 / 12 for j in range(13)]]
    g.poly([(y1, 0), (L, 0), (L, top), (y1 + r, top)] + arc[1:] + [(y1, 0)], "d-kass")
    g.rect(0, y0, 0, top, "d-kass")
    ch = N2.ENTRY_CH
    g.poly([(y0 - ch, -0.01), (y1 + ch, -0.01), (y1, ch), (y1, 0.0), (y0, 0.0), (y0, ch)], "d-pocket")
    g.rect(y0, y1, zp - 0.01, top + 0.01, "d-pocket")
    g.text(L / 2 + 3, 7.0, "Kassette v2", "dlb")
    g.text(y1 + r + 0.2, top + 1.0, "runde Kante", "dls", "start")
    g.text(y0 + 0.1, zp + 1.8, "Aderschlitz", "dls", "end")
    g.text(L - 0.6, top + 1.0, "flache Oberseite", "dls", "end")
    # Adern: gestrichelter Weg über die runde Kante (Hinweis, der Regler bewegt nur die Buchse)
    g.o.append('<path d="M%.1f,%.1f L%.1f,%.1f C%.1f,%.1f %.1f,%.1f %.1f,%.1f L%.1f,%.1f" class="d-wirehint"/>' % (
        g.X(yb), g.Z(zp), g.X(yb), g.Z(top + 0.8), g.X(yb), g.Z(top + 1.6), g.X(y1 + 0.6), g.Z(top + 1.1), g.X(y1 + r + 1.2), g.Z(top + 0.5),
        g.X(k["seat0"] + 1.5), g.Z(top + 0.5)))
    g.group("C-buchse", move=(0, -17.5, 0, 0))
    g.rect(yb - 1.27, yb + 1.27, 0, sd.HSG_H, "d-hsg")
    g.rect(yb - 0.5, yb + 0.5, 0.5, 5.5, "d-term")
    g.rect(yb - 0.3, yb + 0.3, sd.HSG_H, sd.HSG_H + 1.6, "d-wire")
    g.text(yb, -1.0, "Buchse, Adern nach oben", "dls")
    g.end()
    g.group("C-led", move=(0, 8.0, 0, 0))
    ya = k["seat0"] + N2.SEAT_TOL
    g.rect(ya, ya + 16.7, top, top + 0.3, "d-led")
    g.rect(ya + 6.0, ya + 11.0, top + 0.3, top + 1.5, "d-led")
    g.text(ya + 8.3, top + 3.5, "LED-Streifen, Chips nach oben", "dls")
    g.end()
    return g.svg(400, 430, "Buchse von unten in die Kassette v2, LED-Streifen von oben auf die flache Fläche")


def svg_n():
    """Schieber in die Nut (Draufsicht, Nutseite oben, Schieber gleitet von der offenen Seite bis zum Nutende)."""
    n = N2.n2_dims()
    S = 7.0
    g = G(S, 106, 168)
    hx, hy = n["bx"], n["by"]
    wt = n["hb"] + N2.N2_OVER
    g.o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" class="d-slab" rx="3"/>' % (g.X(-hx), g.Z(hy), 2 * hx * S, 2 * hy * S))
    g.o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" class="d-groove"/>' % (g.X(n["x_in"]), g.Z(wt), (hx - n["x_in"]) * S + 1, 2 * wt * S))
    g.o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" class="d-shaft"/>' % (g.X(-n["hx"]), g.Z(n["hy"]), 2 * n["hx"] * S, 2 * n["hy"] * S))
    g.line(n["x_in"], hy + 1.5, n["x_in"], -hy - 1.5, "dimr")
    g.text(n["x_in"] - 0.4, -hy - 3.6, "Nutende (Anschlag)", "dl", "start")
    g.text(hx + 4.0, hy + 2.8, "Nut offen", "dl")
    g.text(0, n["hy"] + 1.5, "Schacht", "dls")
    g.group("N-mov", move=(26.0, 0, 0, 0))
    g.o.append('<polygon points="%s" class="d-key"/>' % " ".join("%.1f,%.1f" % (g.X(x), g.Z(y)) for x, y in
                                                                  [(n["x_in"] + 0.2, wt - 0.5), (hx + 1.0, wt - 0.5), (hx + 1.0, -wt + 0.5), (n["x_in"] + 0.2, -wt + 0.5)]))
    for px in sd.pin_x():
        g.o.append('<circle cx="%.1f" cy="%.1f" r="%.1f" class="d-hole"/>' % (g.X(px), g.Z(n["ypin"]), 0.7 * S))
    g.o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" class="d-hole"/>' % (g.X(hx - 0.5), g.Z(4.0), 0.8 * S, 8.0 * S))
    g.text(0.9, 8.0, "Schieber", "dlb")
    g.text(0.9, 5.2, "Trichter-Seite nach oben", "dl")
    g.end()
    return g.svg(440, 340, "Schieber gleitet in die Nut der Platte")


def svg_e():
    """Kassette v3 wird von oben in den E-Körper gepresst (Schnitt längs y, Körper wie gedruckt: Anschlagrand unten, Kassette öffnet nach unten)."""
    k = N2.kass2_dims(True)
    S = 10.0
    g = G(S, 215, 355)
    rel = 12                                                          # Spiel überzeichnet
    L, top, zf = k["L"], k["top"], k["zf"]
    st = N2.E_STOP
    for i, c in enumerate(N2.E_CLR):
        hy = L / 2 + c * rel
        variant_group(g, "E", de(c), i == 1)
        for s in (-1, 1):
            g.poly([(s * (hy + N2.E_WALL), 0), (s * (hy - N2.E_LIP), 0), (s * (hy - N2.E_LIP), st), (s * hy, st), (s * hy, N2.P_H), (s * (hy + N2.E_WALL), N2.P_H)], "d-slab")
        g.text(0, -1.6, "Körper E, Spiel %s mm je Seite (%d× überzeichnet)" % (de(c), rel), "dl")
        g.end()
    g.text(0, st / 2 - 0.3, "Anschlagrand", "dls")
    g.group("E-mov", move=(0, 14.0, 0, 0))
    yp = L / 2 - k["ypin"]                                            # Pin-Reihe, nach dem Umdrehen
    g.rect(-L / 2, L / 2, st, st + top, "d-kass")
    g.rect(yp - k["pk_d"] / 2, yp + k["pk_d"] / 2, st - 0.01, st + top - zf, "d-pocket")
    g.rect(yp - 1.27, yp + 1.27, st + top - zf - sd.HSG_H, st + top - zf, "d-hsg")
    g.poly([(yp - sd.FUNNEL_D / 2, st + top - zf + 0.01), (yp + sd.FUNNEL_D / 2, st + top - zf + 0.01), (yp + sd.HOLE / 2, st + top - 0.4), (yp + sd.HOLE / 2, st + top + 0.01), (yp - sd.HOLE / 2, st + top + 0.01), (yp - sd.HOLE / 2, st + top - 0.4)], "d-pocket")
    g.text(-L / 4, st + top - 3.0, "Kassette v3", "dlb")
    g.text(yp, st + top + 1.4, "Trichterboden", "dls")
    g.text(-L / 2 + 0.4, st + 2.0, "offene Seite voran", "dls", "start")
    g.end()
    return g.svg(440, 385, "Kassette v3 wird von oben in den E-Körper gepresst, offene Seite voran")


def svg_d():
    """Winkelleiste in die Passprobe v7 (Taschenseite oben, Pins zeigen nach unten durch den Boden, Schnitt längs y), Tasche +1,5 mm zum Lötende."""
    S = 22.0
    g = G(S, 235, 270)
    ext = N2.D2_EXT
    g.poly([(-9.5, 0), (3.5, 0), (3.5, 4.0), (-9.5, 4.0)], "d-slab")
    g.rect(-3.42 - ext, 1.12, 0.8, 4.01, "d-pocket")
    g.rect(-7.32, -3.42 - ext, 1.48, 4.01, "d-pocket")
    g.rect(-0.7, 0.7, -0.01, 0.8, "d-pocket")
    g.line(-3.42 - ext, 4.5, -3.42, 4.5, "dimr")
    g.text(-3.42 - ext / 2, 4.9, "+%s mm" % de(ext, 1), "dlb")
    g.group("D-mov", move=(0, 8.0, 0, 0))
    g.rect(-3.32, -1.32, 0.8, 2.8, "d-body")
    g.rect(-7.32, 0.32, 1.48, 2.12, "d-pin")
    g.rect(-0.32, 0.32, -4.88, 2.12, "d-pin")
    g.end()
    g.text(-8.8, 6.0, "Platte D, Taschen nach oben", "dl", "start")
    g.text(2.2, -2.4, "Pins treten unten aus", "dls", "start")
    g.text(-6.1, 0.9, "Stufe fürs Lötende", "dls")
    return g.svg(450, 400, "Winkelleiste wird in die Passprobe v7 gesetzt")


def svg_fm():
    """Fuß-Lehre im Mulden-Ring (Schnitt längs y)."""
    S = 9.5
    g = G(S, 220, 316)
    g.poly([(-23, 0), (23, 0), (23, 11.0), (-23, 11.0)], "d-slab")
    g.poly([(-18.3, 1.2), (18.3, 1.2), (18.3, 5.0), (19.5, 11.0), (-19.5, 11.0), (-18.3, 5.0)], "d-pocket")
    g.group("FM-mov", move=(0, 13.0, 0, 0))
    g.rect(-18.0, 18.0, 1.2, 1.2 + 9.8, "d-bld")
    g.rect(-18.0, 18.0, 1.2 + 9.8, 1.2 + 9.8 + N2.LEHRE_CAP, "d-bld")
    g.rect(-16.0, 16.0, 3.2, 1.2 + 9.8 + N2.LEHRE_CAP + 0.01, "d-pocket")
    g.text(0, 1.2 + 4.5, "Fuß-Lehre", "dlb")
    g.text(0, 1.2 + 12.5, "oben offen, leicht", "dl")
    g.end()
    g.text(0, -1.4, "Ring FM, Boden unten", "dl")
    return g.svg(440, 360, "Fuß-Lehre wird in den Mulden-Ring gesetzt")


# --------------------------------------------------------------------------
# Auswahllisten
# --------------------------------------------------------------------------
K_PASS = opts([("", "– noch nicht getestet –"), ("alle", "alle 4 Kontakte stabil, auch beim Wackeln"),
               ("aus", "mit Aussetzern beim Wackeln"), ("teil", "nur 1 bis 3 Kontakte"), ("kein", "kein Durchgang")])
K_PULL = opts([("", "– nicht geprüft –"), ("leicht", "Buchse fällt fast von selbst ab"), ("mittel", "hält, lässt sich leicht abziehen"), ("fest", "hält fest")])
E_FIT = opts([("", "– noch nicht getestet –"), ("1", "1 · geht nicht ganz hinein"), ("2", "2 · nur mit sehr viel Kraft"),
              ("3", "3 · kräftiger Daumendruck, sitzt fest (ideal)"), ("4", "4 · leichter Druck, sitzt noch"), ("5", "5 · lose, wackelt oder fällt heraus")])
E_HOLD = opts([("", "– noch nicht getestet –"), ("fest", "hält beim Umdrehen und Schütteln"), ("knapp", "hält, rutscht beim Schütteln etwas"), ("lose", "fällt heraus")])
E_OUT = opts([("", "– nicht geprüft –"), ("a", "lässt sich mit dem Daumen leicht herausdrücken"), ("b", "nur mit kräftigem Druck"), ("c", "kaum herauszubekommen")])
E_PIN = opts([("", "– nicht geprüft –"), ("ja", "Kassette bleibt sitzen, Leiste lässt sich abziehen"), ("mit", "Kassette rutscht ein Stück mit"), ("nein", "Kassette kommt mit heraus")])
GOOD3 = lambda a, b, c, d=None: opts([("", "– bitte wählen –"), ("a", a), ("b", b), ("c", c)] + ([("d", d)] if d else []))

STEPS = []


def add(sid, title, tag, lead, instr, diagram, fields, series=None, kdata=None, edata=None, optional=False):
    STEPS.append(dict(id=sid, title=title, tag=tag, lead=lead, instr=instr, diagram=diagram, fields=fields, series=series or [],
                      kdata=kdata, edata=edata, optional=optional))


def sfields(prefix, vals, label, scale):
    return [fld("%s-%s" % (prefix, de(v)), "%s %s mm" % (label, de(v)), "select", scale) for v in vals]


def steps():
    add("p", "Vorbereiten", "0", "Alles hinlegen und die Kaufteile messen. Das dauert 5 Minuten und macht die Ergebnisse belastbar.",
        ["Teile auf einem Tisch ausbreiten und mit dem Bild unten erkennen. Jedes Teil trägt <b>Buchstabe und Maß</b> als <b>erhabene</b> Schrift, dazu <b>Kerben</b> in einer Kante "
         "(1 Kerbe = engste bzw. dünnste Variante, mehr Kerben = mehr Spiel bzw. dicker). Die Schieber tragen die Schrift unten.",
         "Mit der Schieblehre die <b>Breite</b> von mehreren Dupont-Gehäusen messen (Soll 10,16 mm, streut um ±0,3) und den <b>kürzesten senkrechten Pin</b> "
         "einer Winkelleiste (Soll 7,0 mm).",
         "Für K brauchst du <b>Buchsen mit gecrimpten Kontakten und Adern</b>. Für C eine Buchse mit Adern und ein LED-Streifenstück. Für E die Winkelleiste."],
        "img:teile",
        [fld("p-bw", "Breite der Dupont-Gehäuse in mm (kleinster und größter Wert)", "text", ph="z. B. 10,1 bis 10,3"),
         fld("p-pin", "Kürzester senkrechter Pin in mm", "text", ph="z. B. 6,9"),
         fld("p-led", "LED-Streifen: Breite in mm", "text", ph="10 oder 12"),
         fld("p-cr", "Sind die Kontakte an der Buchse gecrimpt (Adern dran)?", "select", R_YN("ja, alle 4", "nein, nur das leere Gehäuse")),
         fld("p-mm", "Multimeter mit Durchgangsprüfung vorhanden?", "select", R_YN("ja", "nein"))])
    add("q", "Druckqualität ansehen", "1", "Vor dem Zusammenstecken die gedruckten Teile kurz prüfen. Diese Befunde gehören zum Ergebnis.",
        ["Jedes Teil von oben, unten und von der Seite ansehen. Mit dem Fingernagel die <b>Kanten am Bett</b> fühlen: Die neue 0,3-mm-Fase soll den Wulst weg haben.",
         "<b>Platte N A</b> (Nut unten gedruckt) von unten ansehen: Die <b>Decke über der Nut</b> ist wieder die lange Brücke, jetzt aber mit „Thick bridges“. Glatt oder durchgehängt?",
         "<b>Erhabene Schrift</b> und <b>Kerben</b>: lesbar bzw. fühlbar? Besonders im schwarzen PLA war die Gravur in Nacht 1 schlecht zu sehen.",
         "Dünne Plättchen K und Schieber N auf den Tisch legen: flach oder wippen sie?"],
        None,
        [fld("q-all", "Welche Dateien wurden gedruckt?", "text", ph="z. B. alles, ohne FM"),
         fld("q-bridge", "Decke über der Nut bei Platte N A", "select", GOOD3("glatt, sauber", "leicht durchgehängt", "stark durchgehängt", "Fehldruck")),
         fld("q-thick", "Thick bridges in Bambu Studio eingeschaltet?", "select", R_YN("ja", "nein", "weiß nicht")),
         fld("q-warp", "Schieber N und Plättchen K: flach?", "select", GOOD3("flach", "leicht verzogen", "stark verzogen", "fehlt")),
         fld("q-hole", "Pin-Löcher (K, N, D) mit Fase", "select", GOOD3("alle offen, Fase gut", "einzelne zugequollen", "viele zu")),
         fld("q-text", "Erhabene Schrift", "select", GOOD3("gut lesbar", "lesbar, aber flach", "schlecht lesbar")),
         fld("q-notch", "Kerben als Rang", "select", GOOD3("gut zu fühlen und zu sehen", "nur zu sehen", "kaum zu erkennen")),
         fld("q-foot", "Elefantenfuß an der Unterseite", "select", GOOD3("sauber, Fase hat gewirkt", "leichter Wulst", "starker Wulst, musste entgratet werden")),
         fld("q-time", "Druckzeit insgesamt in Stunden", "text", ph="z. B. 2,5"),
         fld("q-fil", "Drucker und Filament", "text", ph="z. B. Bambu A1, PLA schwarz")])
    add("K", "Kontakt-Tiefe", "K", "Das Wichtigste zuerst: Bis zu welcher Plättchendicke hält der Kontakt stabil? Das legt die Höhen von Muldenboden und Trichterplatte fest.",
        ["Winkelleiste so hinstellen, dass die <b>Pins nach oben</b> zeigen (Körper unten).",
         "<b>Plättchen K</b> auf die Pins stecken, bis es auf dem Körper liegt. Starte mit <b>0,8</b>. Die Schrift zeigt nach oben.",
         "Dupont-Buchse <b>mit gecrimpten Kontakten</b>, Steckseite nach unten, auf die Pins drücken, bis sie auf dem Plättchen aufliegt. Im Bild den Regler ziehen.",
         "Multimeter auf Durchgang: eine Spitze an das <b>Lötende</b> der Leiste (der waagrechte Pin hinten), die andere an die Ader des passenden Kontakts. Das für alle 4 Pins.",
         "Die Buchse dabei <b>seitlich um etwa 0,5 mm schieben</b> und leicht kippen. Bleibt der Durchgang stabil?",
         "Mit <b>0,6</b> und <b>0,4</b> wiederholen, wenn 0,8 nicht hält; mit <b>1,0</b>, wenn 0,8 hält. In Nacht 1 hielt weder 1,8 noch 2,4, bei 1,2 gab es Aussetzer."],
        "svg:k",
        [fld("K-%s-pass" % de(t, 1), "Plättchen %s mm (E = %s mm): Durchgang" % (de(t, 1), de(N2.e_of(t))), "select", K_PASS) for t in N2.K2_T]
        + [fld("K-%s-pull" % de(t, 1), "Plättchen %s mm: Halt der Buchse" % de(t, 1), "select", K_PULL) for t in N2.K2_T],
        kdata=dict(ts=[de(t, 1) for t in N2.K2_T], up=sd.HDR_UP))
    add("C", "Kassette v2 bestücken", "C", "Passt die Buchse jetzt ganz hinein, laufen die Adern ohne Knick, und liegt der LED-Streifen gut auf der flachen Oberseite?",
        ["Kassette v2 so hinstellen, wie sie gedruckt wurde: <b>Tasche unten offen</b>, flache Oberseite oben.",
         "<b>Buchse mit dem Kabelende zuerst von unten</b> in die Tasche schieben, bis sie oben an den zwei <b>Schultern</b> anliegt. Die Adern laufen durch den Schlitz nach oben. Im Bild den oberen Regler ziehen.",
         "Sitzt sie ohne Werkzeug fest? Geht sie jetzt <b>ganz</b> hinein (in Nacht 1 fehlte etwas)? Wackelt sie?",
         "Adern über die <b>runde Kante</b> auf die flache Oberseite legen. Knicken sie, oder liegen sie in einem Bogen?",
         "<b>LED-Streifen</b> auf die flache Fläche legen (Chips nach oben, Pads zur Buchse, Din-Ende zur Tasche hin). Im Bild den unteren Regler ziehen. Passen 10 und 12 mm in Breite und Länge?"],
        "svg:c",
        [fld("C-in", "Buchse in der Tasche", "select", R_FIT),
         fld("C-full", "Buchse liegt ganz an den Schultern an", "select", GOOD3("ja, ganz hinein", "fehlt etwa 0,1 bis 0,3 mm", "fehlt deutlich")),
         fld("C-hold", "Halt der Buchse ohne Werkzeug", "select", GOOD3("fest", "locker", "fällt heraus")),
         fld("C-wire", "Adern über die runde Kante", "select", GOOD3("liegen im Bogen, kein Knick", "leichter Knick", "knicken stark", "keine Adern dran")),
         fld("C-led10", "LED-Streifen 10 mm auf der Oberseite", "select", GOOD3("passt gut", "knapp", "passt nicht", "nicht probiert")),
         fld("C-led12", "LED-Streifen 12 mm auf der Oberseite", "select", GOOD3("passt gut", "knapp", "passt nicht", "nicht probiert")),
         fld("C-len", "Abstand Tasche zu LED-Streifen (1 mm mehr als in Nacht 1)", "select", GOOD3("passt jetzt", "noch zu knapp", "zu viel Abstand")),
         fld("C-side", "Rastfenster-Seite der Buchse frei", "select", R_YN("ja", "nein")),
         fld("C-flat", "Oberseite als LED-Fläche", "select", GOOD3("eben, gut", "Kante oder Delle stört", "Schultern stören"))])
    add("N", "Schieber noch einmal", "N", "Gleitet der Schieber mit mehr Spiel und Luft über sich? Platte B (ohne Brücke) trennt die Passung von der Brücke von Platte A.",
        ["Platte so legen, dass die <b>Nut oben offen</b> ist: <code>N B</code> liegt schon so, <code>N A</code> einmal umdrehen.",
         "Einen Schieber mit der <b>Trichter-Seite (Kegel) nach oben</b> von der <b>offenen</b> Seite einschieben, bis er am Nutende anschlägt. Im Bild den Regler ziehen.",
         "Gleitet er mit leichtem Fingerdruck? Wackelt er quer? Dasselbe in <b>B</b> (ohne Brücke) und in <b>A</b> (mit Brücke), mit allen vier Schiebern (0,20 bis 0,50).",
         "Dann die Platte umdrehen (Nut unten), den Schieber festhalten und die <b>Kassette v2</b> von oben in den Schacht setzen, <b>Tasche nach unten</b>: sie steht auf dem Schieber wie im Gebäude. Einen Dupont-Stift durch die vier Trichterlöcher stecken."],
        "svg:n",
        sfields("NB", N2.N2_CLR, "B (ohne Brücke), Schieber", R_SLIDE) + sfields("NA", N2.N2_CLR, "A (mit Brücke), Schieber", R_SLIDE) + [
            fld("N-sag", "Decke von A: Fäden oder Durchhang in der Nut", "select", GOOD3("nichts zu sehen", "einzelne Fäden", "viele Fäden, bremst den Schieber")),
            fld("N-cmp", "Unterschied A zu B", "select", GOOD3("kein Unterschied", "A etwas schwergängiger", "A klemmt, B geht")),
            fld("N-out", "Fällt ein Schieber beim Hochhalten heraus?", "select", GOOD3("nein, keiner", "ja, die lockeren", "ja, alle")),
            fld("N-kass", "Kassette v2 auf dem Schieber im Schacht", "select", GOOD3("steht fest und plan", "wackelt", "klemmt")),
            fld("N-pin", "Dupont-Stift durch die Trichterlöcher", "select", GOOD3("geht überall leicht", "geht nur teilweise", "geht nicht"))],
        series=[dict(name="N B (Schieber, ohne Brücke)", vals=[de(v) for v in N2.N2_CLR], ids=["NB-%s" % de(v) for v in N2.N2_CLR]),
                dict(name="N A (Schieber, mit Brücke)", vals=[de(v) for v in N2.N2_CLR], ids=["NA-%s" % de(v) for v in N2.N2_CLR])])
    add("E", "Kassette einpressen", "E", "Hält die Kassette v3 durch Klemmung im Schacht, ohne Schieber? Die Trichterplatte ist hier als Boden in der Kassette.",
        ["<b>Buchse</b> von oben in die Kassette v3 drücken (Tasche oben offen), Steckseite nach unten, bis sie auf dem Trichterboden steht. Die Adern laufen nach oben.",
         "<b>E-Körper</b> hinstellen wie gedruckt (Anschlagrand unten, Schrift an der langen Seite). Die Kassette mit der <b>offenen Seite (Tasche, flache Oberseite) voran</b> von oben einsetzen, bis sie am Rand anschlägt. Im Bild den Regler ziehen und die Spielvariante wählen.",
         "Wie viel Kraft braucht das Einsetzen? Dann den Körper <b>umdrehen und schütteln</b>: bleibt die Kassette sitzen? Mit dem Daumen von der Trichterseite wieder herausdrücken: wie schwer geht das?",
         "Mit allen drei Körpern (0,06 / 0,09 / 0,12). Danach mit der <b>Winkelleiste</b>: Pins von der Trichterseite durch die Trichter in die Buchse stecken und die Leiste abziehen. Bleibt die Kassette sitzen? Im Gebäude zieht dieser Zug an der Buchse."],
        "svg:e",
        sfields("E", N2.E_CLR, "Körper", E_FIT)
        + [fld("E-%s-hold" % de(c), "Körper %s mm: Halt beim Umdrehen und Schütteln" % de(c), "select", E_HOLD) for c in N2.E_CLR]
        + [fld("E-%s-out" % de(c), "Körper %s mm: Herausdrücken" % de(c), "select", E_OUT) for c in N2.E_CLR]
        + [fld("E-%s-pin" % de(c), "Körper %s mm: Halt beim Abziehen der Winkelleiste" % de(c), "select", E_PIN) for c in N2.E_CLR]
        + [fld("E-cmp", "Einpressen oder Schieber: was fühlt sich besser an?", "select", GOOD3("Einpressen", "Schieber", "beides ok", "keines überzeugt"))],
        series=[dict(name="E (Spiel Kassette v3 im Schacht)", vals=[de(v) for v in N2.E_CLR], ids=["E-%s" % de(v) for v in N2.E_CLR])],
        edata=dict(vals=[de(v) for v in N2.E_CLR]))
    add("D", "Passprobe v7", "D", "Der Körper liegt jetzt in einer um 1,5 mm längeren Tasche. Welche Körperhöhe trägt das Lötende flach auf der Stufe?",
        ["Passprobe mit den <b>Taschen nach oben</b> hinlegen (Zahlen und Zeichen sind auf der Unterseite, die Pins treten dort aus). Zwei Kerben an der Kante: v7.",
         "Winkelleiste mit den <b>Pins zuerst</b> in eines der drei Felder setzen, bis der Körper am Boden der Tasche liegt. Im Bild den Regler ziehen.",
         "Liegt der Körper flach in der Tasche? Liegt das Lötende (der waagrechte Pin) flach auf der Stufe? Treten die vier Pins gerade aus den Löchern?",
         "Felder: Dreieck = Stufe für Körperhöhe 2,0, Quadrat = 1,8, Kreis = 1,6. Der Körper selbst ist 2,0 hoch, die Felder sagen, welche Stufe das Lötende trägt."],
        "svg:d",
        [fld("D-%s-%s" % (de(h, 1), k), "%s (%s): %s" % (n_, de(h, 1), lab), "select", sel)
         for h, n_ in zip(N2.D2_H, ("Dreieck", "Quadrat", "Kreis"))
         for k, lab, sel in (("body", "Körper liegt flach in der Tasche", GOOD3("ja", "leicht schief", "kippt")),
                             ("st", "Lötende auf der Stufe", GOOD3("liegt flach auf", "leicht schief", "fällt zu tief", "steht zu hoch")))]
        + [fld("D-pins", "Pins treten gerade aus den Löchern", "select", GOOD3("ja, alle vier", "einzelne schief", "klemmen")),
           fld("D-body", "Körper in der Tasche: Spiel", "select", R_FIT)])
    add("F", "Fuß-Lehre im Mulden-Ring", "FM", "Die Fuß-Lehre ersetzt das fehlende Probestück. Wie viel Spiel braucht der Fuß in der Mulde?",
        ["Einen Mulden-Ring aus Nacht 1 (<code>FM</code>) auf den Tisch legen, Boden unten.",
         "Fuß-Lehre <b>mit der abgeschrägten Ecke zur abgeschrägten Ecke</b> des Rings ausrichten und von oben einsetzen. Im Bild den Regler ziehen.",
         "Sinkt sie ohne Klemmen bis zum Boden? Wackelt sie, wenn du an der Lehre hin und her kippst?",
         "Alle drei Ringe (0,10 / 0,15 / 0,20). Es gibt noch keine Federzunge."],
        "svg:fm",
        sfields("FM", (0.10, 0.15, 0.20), "Ring", R_FIT),
        series=[dict(name="FM (CLR)", vals=[de(v) for v in (0.10, 0.15, 0.20)], ids=["FM-%s" % de(v) for v in (0.10, 0.15, 0.20)])], optional=True)
    add("z", "Abschluss", "Σ", "Zum Schluss ein Gesamteindruck. Danach unten den Text kopieren und mir schicken.",
        ["Überlege, welche Halterung für die Kassette im Gebäude besser ist und was als Nächstes gedruckt werden soll."],
        None,
        [fld("z-hold", "Halt der Kassette im Gebäude", "select", opts([("", "– bitte wählen –"), ("n", "Schieber (N)"), ("e", "Einpressen (E)"),
                                                                          ("b", "beides geht, das einfachere zählt"), ("x", "keines überzeugt")])),
         fld("z-worst", "Schlechteste Fuge", "select", opts([("", "– bitte wählen –"), ("K", "K Kontakt-Tiefe"), ("N", "N Schieber"), ("E", "E Einpressen"),
                                                                ("C", "C Kassette v2"), ("D", "D Passprobe"), ("FM", "FM Fuß ↔ Mulde"), ("x", "keine, alles gut")])),
         fld("z-next", "Was als Nächstes", "select", opts([("", "– bitte wählen –"), ("a", "Konstanten übernehmen, Gebäude trocken bauen (Probestück neu)"),
                                                            ("b", "Feinabstufung der guten Varianten"), ("c", "Federzunge und Rast"),
                                                            ("d", "Licht-Wandstreifen"), ("e", "erst Kontakt-Tiefe klären")]))])


def render_diagram(step):
    dg = step["diagram"]
    if not dg:
        return ""
    if dg.startswith("img:"):
        return ('<figure class="dg"><img src="{{IMG_TEILE}}" alt="Alle gedruckten Teile von Nacht 2 mit Beschriftung" loading="lazy">'
                '<figcaption>Alle Teile der ZIP: K gelb, C orange, N grün, E sandfarben, D grau, Fuß-Lehre blau.</figcaption></figure>')
    key = dg[4:]
    svg = dict(k=svg_k, c=svg_c, n=svg_n, e=svg_e, d=svg_d, fm=svg_fm)[key]()
    ctl = ""
    if key == "k":
        ctl += ('<label class="sel">Plättchen <select class="dgvar" data-group="K">%s</select></label>' %
                "".join('<option value="%s"%s>%s mm</option>' % (de(t, 1), " selected" if i == 2 else "", de(t, 1)) for i, t in enumerate(N2.K2_T)))
        ctl += '<label class="rng">Buchse aufdrücken <input type="range" class="dgr" min="0" max="100" value="0" data-for="K-ALL" aria-label="Buchse aufdrücken"></label>'
    elif key == "e":
        ctl += ('<label class="sel">Spiel <select class="dgvar" data-group="E">%s</select></label>' %
                "".join('<option value="%s"%s>%s mm</option>' % (de(c), " selected" if i == 1 else "", de(c)) for i, c in enumerate(N2.E_CLR)))
        ctl += '<label class="rng">Kassette einpressen <input type="range" class="dgr" min="0" max="100" value="0" data-for="E-mov" aria-label="Kassette einpressen"></label>'
    elif key == "c":
        ctl += '<label class="rng">1 · Buchse von unten <input type="range" class="dgr" min="0" max="100" value="0" data-for="C-buchse" aria-label="Buchse einschieben"></label>'
        ctl += '<label class="rng">2 · LED von oben <input type="range" class="dgr" min="0" max="100" value="0" data-for="C-led" aria-label="LED auflegen"></label>'
    else:
        gid = dict(n="N-mov", d="D-mov", fm="FM-mov")[key]
        lab = dict(n="Schieber einschieben", d="Leiste einsetzen", fm="Lehre einsetzen")[key]
        ctl += '<label class="rng">%s <input type="range" class="dgr" min="0" max="100" value="0" data-for="%s" aria-label="%s"></label>' % (lab, gid, lab)
    ctl += '<button type="button" class="play" data-play="1">Abspielen</button>'
    extra = ""
    img = dict(n=("{{IMG_SCHIEBER}}", "Schnitt: Schieber in der Nut mit Luft darüber, daneben längs mit Kassette"),
               e=("{{IMG_EINPRESSEN}}", "Schnitt: Kassette v3 eingepresst im E-Körper"),
               c=("{{IMG_KASSETTE}}", "Kassette v2 und v3 mit Buchse"))
    if key in img:
        extra = '<img class="sect" src="%s" alt="%s" loading="lazy">' % img[key]
    return '<figure class="dg" data-key="%s"><div class="dgbox">%s</div><div class="dgctl">%s</div>%s</figure>' % (key, svg, ctl, extra)


def build_steps_html():
    out, nav, spec = [], [], []
    for st in STEPS:
        instr = "".join("<li>%s</li>" % x for x in st["instr"])
        form = "".join(render_field(f) for f in st["fields"])
        opt = ' <span class="opt">optional</span>' if st["optional"] else ""
        out.append(
            '<section class="step" id="s-%s" data-step="%s"><header><span class="tg">%s</span><h2>%s%s</h2><span class="done" aria-hidden="true"></span></header>'
            '<p class="lead">%s</p><div class="cols"><ol class="how">%s</ol>%s</div>'
            '<form class="fb" onsubmit="return false"><h3>Feedback</h3><div class="grid">%s'
            '<label class="fld wide" for="f-%s-free"><span>Notizen, Auffälligkeiten (Freitext)</span><textarea id="f-%s-free" data-fid="%s-free" rows="2" placeholder="alles, was nicht in die Auswahl passt"></textarea></label>'
            '</div></form></section>' % (st["id"], st["id"], st["tag"], st["title"], opt, st["lead"], instr, render_diagram(st), form, st["id"], st["id"], st["id"]))
        nav.append('<a href="#s-%s" data-nav="%s" title="%s">%s</a>' % (st["id"], st["id"], st["title"], st["tag"]))
        spec.append(dict(id=st["id"], tag=st["tag"], title=st["title"], optional=st["optional"],
                         items=[dict(id=f["id"], label=f["label"], kind=f["kind"],
                                     map={x["v"]: x["t"] for x in f["opts"] if x["v"]}) for f in st["fields"]] + [dict(id=st["id"] + "-free", label="Notizen", kind="text", map={})],
                         series=st["series"], kdata=st["kdata"], edata=st["edata"]))
    return "\n".join(out), "".join(nav), spec


def main():
    steps()
    html, nav, spec = build_steps_html()
    with open(TEMPLATE, encoding="utf-8") as f:
        page = f.read()
    rep = {"{{STEPS}}": html, "{{NAV}}": nav, "{{SPEC}}": json.dumps(spec, ensure_ascii=False),
           "{{IMG_TEILE}}": img_uri("teile.png", 900), "{{IMG_SCHIEBER}}": img_uri("schieber_schnitt.png", 900),
           "{{IMG_EINPRESSEN}}": img_uri("einpressen_schnitt.png", 760), "{{IMG_KASSETTE}}": img_uri("kassette_v2_v3.png", 760)}
    for k, v in rep.items():
        page = page.replace(k, v)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(page)
    print("geschrieben: %s (%d kB), %d Schritte, %d Felder" % (os.path.relpath(OUT, ROOT), os.path.getsize(OUT) / 1024, len(STEPS),
                                                              sum(len(s["fields"]) for s in STEPS)))


if __name__ == "__main__":
    main()
