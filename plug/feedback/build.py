#!/usr/bin/env python3
"""Testbogen für den ersten Nachtdruck: baut plug/feedback/page.html aus template.html.

Die Seite führt Schritt für Schritt durch die Serien aus `plug/series.py` (Dateien in stl/steckmodul_night1/): Anleitung, Zeichnung
mit Schieberegler (so wird gesteckt), Formular (Auswahl und Freitext) und am Ende ein Ergebnistext zum Kopieren. Maße der Zeichnungen
kommen aus `dims()` (plug/institute.py), die Spielwerte aus plug/series.py.

Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m plug.feedback.build      # schreibt plug/feedback/page.html
"""
import base64
import io
import json
import os

from PIL import Image

from plug import dupont as sd
from plug import institute as I
from plug import series as SR

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))          # plug/
ROOT = os.path.dirname(HERE)
TEMPLATE = os.path.join(HERE, "feedback", "template.html")
OUT = os.path.join(HERE, "feedback", "page.html")
PREV = os.path.join(ROOT, "vorschau", "steckmodul_night1")


def de(x, n=2):
    return ("%.*f" % (n, x)).replace(".", ",")


def img_uri(name, width):
    im = Image.open(os.path.join(PREV, name)).convert("RGB")
    im = im.resize((width, int(im.size[1] * width / im.size[0])), Image.LANCZOS)
    b = io.BytesIO()
    im.save(b, "JPEG", quality=86, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()


# --------------------------------------------------------------------------
# Zeichnungen (SVG, z nach oben, Maße in mm → px)
# --------------------------------------------------------------------------
class G:
    def __init__(self, S, ox, oy):
        self.S, self.ox, self.oy, self.o = S, ox, oy, []

    def X(self, x):
        return self.ox + x * self.S

    def Z(self, z):
        return self.oy - z * self.S

    def rect(self, x0, x1, z0, z1, cls):
        self.o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" class="%s"/>' % (
            self.X(x0), self.Z(z1), (x1 - x0) * self.S, (z1 - z0) * self.S, cls))

    def poly(self, pts, cls):
        self.o.append('<polygon points="%s" class="%s"/>' % (" ".join("%.1f,%.1f" % (self.X(x), self.Z(z)) for x, z in pts), cls))

    def text(self, x, z, s, cls="dl", anchor="middle"):
        self.o.append('<text x="%.1f" y="%.1f" class="%s" text-anchor="%s">%s</text>' % (self.X(x), self.Z(z), cls, anchor, s))

    def line(self, x0, z0, x1, z1, cls="dim"):
        self.o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="%s"/>' % (self.X(x0), self.Z(z0), self.X(x1), self.Z(z1), cls))

    def group(self, gid, move=None, cls=""):
        """Beginnt eine Gruppe; move = (dx0, dz0, dx1, dz1) in mm (z nach oben): Startlage → Endlage, vom Schieberegler gesteuert."""
        a = ' id="%s"' % gid if gid else ""
        if move:
            a += ' data-move="%.1f,%.1f,%.1f,%.1f" transform="translate(%.1f,%.1f)"' % (
                move[0] * self.S, -move[1] * self.S, move[2] * self.S, -move[3] * self.S, move[0] * self.S, -move[1] * self.S)
        self.o.append('<g%s class="%s">' % (a, cls))

    def end(self):
        self.o.append("</g>")

    def svg(self, w, h, label):
        return '<svg viewBox="0 0 %d %d" role="group" aria-label="%s" class="dgsvg">%s</svg>' % (w, h, label, "".join(self.o))


def svg_k():
    """Kontakt-Tiefe: Winkelleiste, Plättchen t, Buchse wird aufgedrückt (Frontansicht, Buchse halbtransparent, Pins davor)."""
    g = G(14.0, 225, 392)
    START = sd.HDR_UP + 2.0 + 4.0                        # Unterkante der Buchse beim Start: 4 mm über den Pinspitzen
    for k, t in enumerate(SR.K_T):
        e = sd.HDR_UP - t
        g.group("", cls="var" + ("" if k == 1 else " off"))
        g.o[-1] = g.o[-1].replace('class="var', 'data-group="K" data-var="%s" class="var' % de(t, 1), 1)
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


def svg_n():
    """Schieber in die Nut (Draufsicht, Platte liegt wie gedruckt, Schieber gleitet von der offenen Seite bis zum Nutende)."""
    S = 7.0
    g = G(S, 106, 156)
    hx, hy = 11.0, 18.0
    g.o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" class="d-slab" rx="3"/>' % (g.X(-hx), g.Z(hy), 2 * hx * S, 2 * hy * S))
    g.o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" class="d-groove"/>' % (g.X(-9.05), g.Z(17.165), (hx + 9.05) * S + 1, 2 * 17.165 * S))
    g.o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" class="d-shaft"/>' % (g.X(-7.85 - 0.2), g.Z(14.865), 2 * 8.05 * S, 2 * 14.865 * S))
    g.line(-9.05, 18.5, -9.05, -18.5, "dimr")
    g.text(-11.0, -21.2, "Nutende (Anschlag)", "dl", "start")
    g.text(hx + 4.0, 21.0, "Nut offen", "dl")
    g.group("N-mov", move=(26.0, 0, 0, 0))
    g.o.append('<polygon points="%s" class="d-key"/>' % " ".join("%.1f,%.1f" % (g.X(x), g.Z(y)) for x, y in
                                                                  [(-9.05, 17.0), (11.0, 17.0), (11.0, -17.0), (-9.05, -17.0)]))
    for px in sd.pin_x():
        g.o.append('<circle cx="%.1f" cy="%.1f" r="%.1f" class="d-hole"/>' % (g.X(px), g.Z(-11.975), 0.7 * S))
    g.o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" class="d-hole"/>' % (g.X(10.3), g.Z(3.0), 1.0 * S, 6.0 * S))
    g.text(0.9, 8.0, "Schieber", "dlb")
    g.text(0.9, 5.2, "Gravur nach oben", "dl")
    g.end()
    return g.svg(440, 320, "Schieber gleitet in die Nut der Platte")


def svg_s():
    """Kassette in den Schacht (Schnitt längs y, Platte liegt wie gedruckt, Schieber in der Nut, Kassette sinkt auf den Schieber)."""
    d = I.dims()
    S = 11.5
    g = G(S, 250, 372)
    F = 9.0
    rel = 6.0
    for k, c in enumerate(SR.S_CLR):
        g.group("", cls="var" + ("" if k == len(SR.S_CLR) - 1 else " off"))
        g.o[-1] = g.o[-1].replace('class="var', 'data-group="S" data-var="%s" class="var' % de(c), 1)
        sh = 14.665 + c * rel
        g.poly([(-18, 0), (-16.165, 0), (-17.165, 1.0), (-sh, 1.0), (-sh, F), (-18, F)], "d-slab")
        g.poly([(18, 0), (16.165, 0), (17.165, 1.0), (sh, 1.0), (sh, F), (18, F)], "d-slab")
        g.text(0, -3.2, "Spiel %s mm je Seite (%d× überzeichnet)" % (de(c), rel), "dl")
        g.end()
    g.poly([(-16.015, 0), (16.015, 0), (17.015, 1.0), (-17.015, 1.0)], "d-key")
    g.text(0, 0.35, "Schieber", "dls")
    g.group("S-mov", move=(0, 13.0, 0, 0))
    g.rect(-14.665, 14.665, 1.0, 1.0 + 13.6, "d-kass")
    g.rect(-14.665, -9.285, 1.0, 1.0 + 15.05, "d-kass")
    g.rect(-11.975 - 1.49, -11.975 + 1.49, 1.0, 1.0 + 14.25, "d-pocket")
    g.text(2.0, 1.0 + 6.5, "Kassette (C)", "dlb")
    g.text(-11.975, 1.0 + 16.2, "Tasche unten offen", "dls")
    g.end()
    g.text(0, -1.3, "Platte S, Nut-Seite unten", "dl")
    return g.svg(500, 420, "Kassette sinkt in den Schacht der Boden-Platte auf den Schieber")


def svg_c():
    """Buchse in die Kassette (von unten, Kabelseite zuerst) und LED-Streifen in die Ablage (von oben). Schnitt längs y."""
    d = I.dims()
    S = 10.5
    g = G(S, 36, 277)
    y0 = d["HY"] - d["cass_y0"]                          # Tasche bei 2,69 mm
    g.rect(0, d["cass_len"], 0, 13.6, "d-kass")
    g.rect(0, d["sock_d"], 0, 15.05, "d-kass")
    g.rect(y0 - 1.49, y0 + 1.49, 0, 14.25, "d-pocket")
    g.rect(d["seat_y0"] - d["cass_y0"], d["seat_y1"] - d["cass_y0"], 13.2, 13.6, "d-pocket")
    g.text(d["cass_len"] / 2 + 3, 6.0, "Kassette (C)", "dlb")
    g.text(y0, 16.8, "Tasche", "dls")
    g.text(d["seat_y0"] - d["cass_y0"] + 0.5, 11.6, "Ablage oben (Vertiefung)", "dl", "start")
    g.group("C-buchse", move=(0, -17.5, 0, 0))
    g.rect(y0 - 1.27, y0 + 1.27, 0, 14.0, "d-hsg")
    for k in range(1):
        g.rect(y0 - 0.5, y0 + 0.5, 0.5, 5.5, "d-term")
    g.rect(y0 - 0.3, y0 + 0.3, 14.0, 15.3, "d-wire")
    g.text(y0, -1.0, "Buchse, Kabel nach oben", "dls")
    g.end()
    g.group("C-led", move=(0, 8.0, 0, 0))
    ya, yb = d["seat_y0"] - d["cass_y0"] + 0.5, d["seat_y0"] - d["cass_y0"] + 0.5 + 16.7
    g.rect(ya, yb, 13.25, 13.55, "d-led")
    g.rect((ya + yb) / 2 - 2.5, (ya + yb) / 2 + 2.5, 13.55, 14.8, "d-led")
    g.text((ya + yb) / 2, 16.3, "LED-Streifen, Chips nach oben", "dls")
    g.end()
    return g.svg(400, 500, "Buchse von unten in die Kassette, LED-Streifen von oben in die Ablage")


def svg_r():
    """Buchse in eine Hülse (Schnitt quer zur Buchse)."""
    S = 18.0
    g = G(S, 110, 398)
    c = 0.12
    pd = 2.54 + 2 * c
    g.rect(-pd / 2 - 1.2, pd / 2 + 1.2, 0, 1.0, "d-slab")
    g.rect(-pd / 2 - 1.2, -pd / 2, 1.0, 14.25, "d-slab")
    g.rect(pd / 2, pd / 2 + 1.2, 1.0, 14.25, "d-slab")
    g.rect(-pd / 2, pd / 2, 0, 1.0, "d-pocket")
    g.group("R-mov", move=(0, 6.0, 0, 0))
    g.rect(-1.27, 1.27, 1.0, 15.0, "d-hsg")
    for x in (-0.6,):
        g.rect(x - 0.35, x + 0.35, 1.5, 6.5, "d-term")
    g.end()
    g.text(0, -0.8, "Hülse mit Platte", "dl")
    g.text(3.0, 12.0, "Buchse", "dls", "start")
    return g.svg(240, 430, "Buchse wird in eine Hülse gedrückt")


def svg_d():
    """Winkelleiste in die Passprobe (Taschenseite oben, Pins zeigen nach unten durch den Boden, Schnitt längs y)."""
    S = 22.0
    g = G(S, 235, 270)
    g.poly([(-9.5, 0), (3.5, 0), (3.5, 4.0), (-9.5, 4.0)], "d-slab")
    # Hohlräume: Körpertasche, Schacht, Lötendenschlitz (Boden 1,48), Pinloch
    g.rect(-3.42, 1.12, 0.8, 4.01, "d-pocket")
    g.rect(-7.32, -3.42, 1.48, 4.01, "d-pocket")
    g.rect(-0.7, 0.7, -0.01, 0.8, "d-pocket")
    g.group("D-mov", move=(0, 8.0, 0, 0))
    g.rect(-3.32, -1.32, 0.8, 2.8, "d-body")
    g.rect(-7.32, 0.32, 1.48, 2.12, "d-pin")
    g.rect(-0.32, 0.32, -4.88, 2.12, "d-pin")
    g.end()
    g.text(-8.8, 5.6, "Platte D, Taschen nach oben", "dl", "start")
    g.text(2.2, -2.4, "Pins treten unten aus", "dls", "start")
    g.text(-6.4, 0.9, "Stufe fürs Lötende", "dls")
    return g.svg(450, 400, "Winkelleiste wird in die Passprobe gesetzt")


def svg_fm():
    """Fuß in den Mulden-Ring (Schnitt längs y)."""
    S = 9.5
    g = G(S, 220, 316)
    g.poly([(-23, 0), (23, 0), (23, 11.0), (-23, 11.0)], "d-slab")
    g.poly([(-18.3, 1.2), (18.3, 1.2), (18.3, 5.0), (19.5, 11.0), (-19.5, 11.0), (-18.3, 5.0)], "d-pocket")
    g.group("FM-mov", move=(0, 13.0, 0, 0))
    g.rect(-18.0, 18.0, 1.2, 1.2 + 9.8, "d-bld")
    g.rect(-18.0, 18.0, 1.2 + 9.8, 1.2 + 9.8 + 5.0, "d-bld")
    g.text(0, 1.2 + 5.0, "Fuß des Probestücks", "dlb")
    g.text(0, 1.2 + 12.0, "Gebäude", "dl")
    g.end()
    g.text(0, -1.4, "Ring FM, Boden unten", "dl")
    return g.svg(440, 360, "Fuß des Probestücks wird in den Mulden-Ring gesetzt")


# --------------------------------------------------------------------------
# Auswahllisten
# --------------------------------------------------------------------------
def opts(lst):
    return [{"v": v, "t": t} for v, t in lst]


R_SLIDE = opts([("", "– noch nicht getestet –"), ("1", "1 · klemmt, bewegt sich nicht"), ("2", "2 · schwergängig, nur mit Kraft"),
                ("3", "3 · gleitet leicht, kein Spiel"), ("4", "4 · gleitet leicht, minimales Spiel"), ("5", "5 · locker, fällt heraus")])
R_FIT = opts([("", "– noch nicht getestet –"), ("1", "1 · passt nicht hinein"), ("2", "2 · nur mit Kraft"),
              ("3", "3 · geht mit Fingerdruck, kein spürbares Spiel"), ("4", "4 · geht leicht, minimales Spiel"), ("5", "5 · wackelt deutlich")])
R_YN = lambda a, b, c="": opts([("", "– bitte wählen –"), ("a", a), ("b", b)] + ([("c", c)] if c else []))

K_PASS = opts([("", "– noch nicht getestet –"), ("alle", "alle 4 Kontakte stabil, auch beim Wackeln"),
               ("aus", "mit Aussetzern beim Wackeln"), ("teil", "nur 1 bis 3 Kontakte"), ("kein", "kein Durchgang")])
K_PULL = opts([("", "– nicht geprüft –"), ("leicht", "Buchse fällt fast von selbst ab"), ("mittel", "hält, lässt sich leicht abziehen"), ("fest", "hält fest")])


def fld(fid, label, kind="select", options=None, ph="", hint=""):
    return dict(id=fid, label=label, kind=kind, opts=options or [], ph=ph, hint=hint)


def series_fields(step, vals, prefix, scale, word):
    return [fld("%s-%s" % (step, de(v)), "%s %s mm" % (prefix, de(v)), "select", scale) for v in vals]


STEPS = []


def add(sid, title, tag, lead, instr, diagram, fields, series=None, kdata=None, optional=False, extra=""):
    STEPS.append(dict(id=sid, title=title, tag=tag, lead=lead, instr=instr, diagram=diagram, fields=fields, series=series,
                      kdata=kdata, optional=optional, extra=extra))


def steps():
    d = I.dims()
    E = d["E"]
    add("p", "Vorbereiten", "0", "Alles hinlegen und die Kaufteile messen. Das dauert 5 Minuten und macht die späteren Ergebnisse belastbar.",
        ["Teile auf einem Tisch ausbreiten und mit dem Bild unten erkennen: Jedes Teil trägt <b>Buchstabe und Spiel in mm</b>, dazu <b>Punkte</b> "
         "(1 Punkt = engste bzw. dünnste Variante, mehr Punkte = mehr Spiel).",
         "Mit der Schieblehre die <b>Breite</b> von mehreren Dupont-Gehäusen messen (Soll 10,16 mm, streut um ±0,3) und den <b>kürzesten senkrechten Pin</b> "
         "einer Winkelleiste (Soll 7,0 mm, bis zur Außenkante der Biegung).",
         "Wo die Schrift steht: <code>S</code> und <code>FM</code> an der langen Außenseite, <code>N</code>, <code>K</code> und <code>R</code> oben, <code>D</code> auf der Unterseite (Bettseite) mit Dreieck, Quadrat und Kreis."],
        "img:beschriftung",
        [fld("p-bw", "Breite der Dupont-Gehäuse in mm (kleinster und größter Wert)", "text", ph="z. B. 10,1 bis 10,3"),
         fld("p-pin", "Kürzester senkrechter Pin in mm", "text", ph="z. B. 6,9"),
         fld("p-led", "LED-Streifen: Breite in mm", "text", ph="10 oder 12"),
         fld("p-cr", "Sind die Kontakte an der Buchse gecrimpt (Adern dran)?", "select", R_YN("ja, alle 4", "nein, nur das leere Gehäuse")),
         fld("p-mm", "Multimeter mit Durchgangsprüfung vorhanden?", "select", R_YN("ja", "nein"))])
    add("q", "Druckqualität ansehen", "1", "Vor dem Zusammenstecken die gedruckten Teile kurz prüfen. Diese Befunde gehören auch zum Ergebnis.",
        ["Jedes Teil einmal von oben, unten und von der Seite ansehen, Elefantenfuß mit dem Fingernagel fühlen.",
         "Bei <code>S</code> die Platte umdrehen und die <b>Decke über der Nut</b> von unten ansehen: Ist sie glatt oder hängt sie durch? "
         "(Das ist die Brücke von etwa 34 mm; sie ist im echten Probestück genauso.)",
         "Schieber <code>N</code> auf den Tisch legen: liegt er flach oder wippt er? Mit einem Lineal prüfen."],
        None,
        [fld("q-all", "Welche Dateien wurden gedruckt?", "text", ph="z. B. K, N, S, C (R, D, FM nicht)"),
         fld("q-bridge", "Decke über der Nut bei S", "select", opts([("", "– bitte wählen –"), ("a", "glatt, sauber"), ("b", "leicht durchgehängt"),
                                                                    ("c", "stark durchgehängt"), ("d", "Fehldruck")])),
         fld("q-warp", "Schieber N: flach?", "select", opts([("", "– bitte wählen –"), ("a", "flach"), ("b", "leicht verzogen"), ("c", "stark verzogen"), ("d", "fehlt")])),
         fld("q-hole", "Pin-Löcher (K, N, D) mit Fase auf beiden Seiten", "select", opts([("", "– bitte wählen –"), ("a", "alle offen, Fase gut"),
                                                                                         ("b", "einzelne zugequollen"), ("c", "viele zu")])),
         fld("q-text", "Gravur und Punkte", "select", opts([("", "– bitte wählen –"), ("a", "gut lesbar"), ("b", "lesbar, aber flach"), ("c", "schlecht lesbar")])),
         fld("q-foot", "Elefantenfuß an der Unterseite", "select", opts([("", "– bitte wählen –"), ("a", "sauber"), ("b", "leichter Wulst"), ("c", "starker Wulst, musste entgratet werden")])),
         fld("q-time", "Druckzeit insgesamt in Stunden", "text", ph="z. B. 2,5"),
         fld("q-fil", "Drucker und Filament", "text", ph="z. B. Bambu A1, PLA beige")])
    add("K", "Kontakt-Tiefe", "K", "Das Wichtigste zuerst: Hält der Kontakt bei nur %s mm Einstecktiefe? Das entscheidet über alle Höhen." % de(E),
        ["Winkelleiste so hinstellen, dass die <b>Pins nach oben</b> zeigen (Körper unten).",
         "<b>Plättchen K</b> auf die Pins stecken, bis es auf dem Körper liegt. Starte mit <b>1,8</b> (Sollwert). Die Gravur zeigt nach oben.",
         "Dupont-Buchse (mit gecrimpten Kontakten) <b>mit der Steckseite nach unten</b> auf die Pins drücken, bis sie auf dem Plättchen aufliegt. Im Bild den Regler ziehen.",
         "Multimeter auf Durchgang: eine Spitze an das <b>Lötende</b> der Leiste (der waagrechte Pin hinten), die andere an die Ader des passenden Kontakts. Das für alle 4 Pins.",
         "Die Buchse dabei <b>seitlich um etwa 0,5 mm schieben</b> und leicht kippen. Bleibt der Durchgang stabil?",
         "Dann mit <b>2,4</b> wiederholen (Einstecktiefe %s mm, deckt den kürzesten Pin ab), und mit <b>1,2</b> (%s mm) nur, wenn 1,8 nicht hält." % (de(sd.HDR_UP - 2.4), de(sd.HDR_UP - 1.2))],
        "svg:k",
        [fld("K-%s-pass" % de(t, 1), "Plättchen %s mm (E = %s mm): Durchgang" % (de(t, 1), de(sd.HDR_UP - t)), "select", K_PASS) for t in SR.K_T]
        + [fld("K-%s-pull" % de(t, 1), "Plättchen %s mm: Halt der Buchse" % de(t, 1), "select", K_PULL) for t in SR.K_T],
        kdata=dict(ts=[de(t, 1) for t in SR.K_T]))
    add("N", "Schieber in die Nut", "N", "Welcher der vier Schieber gleitet leicht, ohne zu klemmen und ohne zu wackeln?",
        ["Eine Platte <code>S</code> (egal welche, die Nut ist bei allen gleich) auf den Tisch legen, <b>Gravurseite nach oben</b>: so wurde sie gedruckt, die Nut liegt unten.",
         "Einen Schieber <code>N</code> mit der <b>Gravur nach oben</b> von der Seite einschieben, an der die Nut <b>offen</b> ist, bis er am geschlossenen Nutende anschlägt. Im Bild den Regler ziehen.",
         "Gleitet er mit leichtem Fingerdruck? Wackelt er quer? Kippt er nach oben? Beim Hochhalten der Platte: fällt er heraus?",
         "Mit allen vier Schiebern wiederholen (0,05 bis 0,20). Dazu je einen Dupont-Stift durch die vier Trichterlöcher stecken."],
        "svg:n",
        series_fields("N", SR.N_CLR, "Schieber", R_SLIDE, "") + [
            fld("N-out", "Fällt ein Schieber beim Hochhalten heraus?", "select", opts([("", "– bitte wählen –"), ("a", "nein, keiner"), ("b", "ja, die lockeren"), ("c", "ja, alle")])),
            fld("N-pin", "Dupont-Stift durch die Trichterlöcher", "select", opts([("", "– bitte wählen –"), ("a", "geht überall leicht"), ("b", "geht nur teilweise"), ("c", "geht nicht")]))],
        series=dict(name="N (KEY_CLR)", vals=[de(v) for v in SR.N_CLR], ids=["N-%s" % de(v) for v in SR.N_CLR]))
    add("S", "Kassette in den Schacht", "S", "Die Lücke zwischen Kassette und Gebäude: bei welchem Schachtspiel sinkt die Kassette ein und wackelt noch nicht?",
        ["Platte <code>S</code> auf den Tisch legen (Nut unten). Den <b>Schieber</b> einschieben, der bei N am besten ging.",
         "Die <b>Kassette</b> <code>C</code> von oben in den Schacht setzen, mit der <b>offenen Tasche nach unten</b>. Sie steht auf dem Schieber, wie im Gebäude. Im Bild den Regler ziehen.",
         "Sinkt sie ohne Kraft ein? Oben an der Kassette anfassen und leicht hin und her kippen: wie viel Spiel spürst du?",
         "Mit den vier Platten (0,05 bis 0,20) wiederholen."],
        "svg:s",
        series_fields("S", SR.S_CLR, "Platte", R_FIT, ""),
        series=dict(name="S (KASS_CLR)", vals=[de(v) for v in SR.S_CLR], ids=["S-%s" % de(v) for v in SR.S_CLR]))
    add("C", "Kassette bestücken", "C", "Passen Buchse, Adern und LED-Streifen in die Kassette, ohne dass etwas klemmt oder wackelt?",
        ["Kassette so hinstellen, wie sie gedruckt wurde: <b>Tasche unten offen</b>.",
         "<b>Buchse mit dem Kabelende zuerst von unten</b> in die Tasche schieben. Die Steckseite bleibt unten bündig. Die Adern laufen durch den Schlitz oben nach außen. Im Bild den oberen Regler ziehen.",
         "Sitzt sie ohne Werkzeug fest? Wackelt sie? Ist die Seite mit den Rastfenstern (zur Gebäudemitte abgewandt) frei?",
         "<b>LED-Streifen</b> von oben in die Ablage legen (Chips nach oben, Pads zur Buchse). Im Bild den unteren Regler ziehen. Passen 10 und 12 mm Breite?"],
        "svg:c",
        [fld("C-in", "Buchse in der Tasche", "select", R_FIT),
         fld("C-wire", "Adern im Aderschlitz", "select", opts([("", "– bitte wählen –"), ("a", "passen leicht"), ("b", "knapp, aber ok"), ("c", "klemmen"), ("d", "keine Adern dran")])),
         fld("C-led10", "LED-Streifen 10 mm in der Ablage", "select", opts([("", "– bitte wählen –"), ("a", "passt gut"), ("b", "knapp"), ("c", "passt nicht"), ("d", "nicht probiert")])),
         fld("C-led12", "LED-Streifen 12 mm in der Ablage", "select", opts([("", "– bitte wählen –"), ("a", "passt gut"), ("b", "knapp"), ("c", "passt nicht"), ("d", "nicht probiert")]))])
    add("R", "Buchsenhülsen", "R", "Optional: Buchse in Hülsen mit Spiel 0,08 bis 0,20. Passprobe Runde 2 hat 0,25 bis 0,33 schon geprüft, hier geht es nur um den Bereich darunter.",
        ["Dieselbe Buchse in jede der vier Hülsen drücken (von einer Seite, die Hülse ist durchgehend). Im Bild den Regler ziehen.",
         "Mit zwei bis drei verschiedenen Buchsen probieren, weil das Gehäuse bis ±0,3 mm streut."],
        "svg:r",
        series_fields("R", SR.R_SNUG, "Hülse", R_FIT, ""),
        series=dict(name="R (SNUG)", vals=[de(v) for v in SR.R_SNUG], ids=["R-%s" % de(v) for v in SR.R_SNUG]), optional=True)
    add("D", "Passprobe Winkelleiste", "D", "Optional: bestätigt die Stufe für das Lötende. Die Passprobe wurde nie gedruckt, das Probestück passt aber schon mit Körperhöhe 2,0.",
        ["Passprobe mit den <b>Taschen nach oben</b> hinlegen (Schrift und Symbole sind auf der Unterseite, die Pins treten dort aus).",
         "Winkelleiste mit den <b>Pins zuerst</b> in eines der drei Felder setzen, bis der Körper am Boden der Tasche liegt. Im Bild den Regler ziehen.",
         "Liegt das Lötende (der waagrechte Pin) flach auf der Stufe? Treten die vier Pins gerade aus den Löchern? Wackelt der Körper?",
         "Felder: Dreieck = 2,0, Quadrat = 1,8, Kreis = 1,6. Das Feld, in dem das Lötende flach aufliegt, entspricht der Körperhöhe."],
        "svg:d",
        [fld("D-2.0-st", "Dreieck (Körperhöhe 2,0): Lötende auf der Stufe", "select", opts([("", "– nicht getestet –"), ("a", "liegt flach auf"), ("b", "leicht schief"), ("c", "Körper fällt zu tief"), ("d", "steht zu hoch")])),
         fld("D-1.8-st", "Quadrat (1,8): Lötende auf der Stufe", "select", opts([("", "– nicht getestet –"), ("a", "liegt flach auf"), ("b", "leicht schief"), ("c", "Körper fällt zu tief"), ("d", "steht zu hoch")])),
         fld("D-1.6-st", "Kreis (1,6): Lötende auf der Stufe", "select", opts([("", "– nicht getestet –"), ("a", "liegt flach auf"), ("b", "leicht schief"), ("c", "Körper fällt zu tief"), ("d", "steht zu hoch")])),
         fld("D-body", "Körper in der Tasche (Feld 2,0)", "select", R_FIT),
         fld("D-pins", "Pins treten gerade aus den Löchern", "select", opts([("", "– bitte wählen –"), ("a", "ja, alle vier"), ("b", "einzelne schief"), ("c", "klemmen")]))],
        optional=True)
    add("F", "Fuß in den Mulden-Ring", "FM", "Optional, größtes Teil: Wie viel Spiel braucht der Fuß in der Mulde? Das ist der größte Einzelanteil im Wackeln.",
        ["Einen Ring <code>FM</code> auf den Tisch legen. Als Fuß dient das <b>gedruckte Gebäude-Probestück</b> (<code>1_probestueck</code>), falls noch vorhanden.",
         "Fuß <b>mit der abgeschrägten Ecke zur abgeschrägten Ecke</b> des Rings ausrichten und von oben einsetzen. Im Bild den Regler ziehen.",
         "Sinkt er ohne Klemmen bis zum Boden? Wackelt er, wenn du am Gebäude hin und her kippst?",
         "Alle drei Ringe (0,10 / 0,15 / 0,20) probieren. Es gibt noch keine Federzunge."],
        "svg:fm",
        series_fields("FM", SR.FM_CLR, "Ring", R_FIT, ""),
        series=dict(name="FM (CLR)", vals=[de(v) for v in SR.FM_CLR], ids=["FM-%s" % de(v) for v in SR.FM_CLR]), optional=True)


def add_final():
    add("z", "Abschluss", "Σ", "Zum Schluss ein Gesamteindruck. Danach unten den Text kopieren und mir schicken.",
        ["Überlege, welche Fuge am schlechtesten war und was als Nächstes gedruckt werden soll."], None,
        [fld("z-worst", "Schlechteste Fuge", "select", opts([("", "– bitte wählen –"), ("K", "K Kontakt-Tiefe"), ("N", "N Schieber ↔ Nut"), ("S", "S Kassette ↔ Schacht"),
                                                                ("C", "C Kassette bestücken"), ("FM", "FM Fuß ↔ Mulde"), ("x", "keine, alles gut")])),
         fld("z-next", "Was als Nächstes", "select", opts([("", "– bitte wählen –"), ("a", "Zwischenwerte der Serien, die gut waren"), ("b", "Federzunge und Rast"),
                                                            ("c", "Licht-Wandstreifen"), ("d", "Gebäude trocken (V1) mit den neuen Werten"),
                                                            ("e", "erst Kontakt-Tiefe klären"), ("f", "Probestück mit neuen Werten komplett neu")]))])


def render_field(f):
    if f["kind"] == "select":
        o = "".join('<option value="%s">%s</option>' % (x["v"], x["t"]) for x in f["opts"])
        ctl = '<select id="f-%s" data-fid="%s">%s</select>' % (f["id"], f["id"], o)
    else:
        ctl = '<input type="text" id="f-%s" data-fid="%s" placeholder="%s" autocomplete="off">' % (f["id"], f["id"], f["ph"])
    return '<label class="fld" for="f-%s"><span>%s</span>%s</label>' % (f["id"], f["label"], ctl)


def render_diagram(step):
    dg = step["diagram"]
    if not dg:
        return ""
    if dg.startswith("img:"):
        name = dg[4:]
        return ('<figure class="dg"><img src="{{IMG_%s}}" alt="Gedruckte Serien mit Beschriftung: K, N, R von oben; S und FM von der Außenseite" loading="lazy">'
                '<figcaption>Beschriftung der Teile: Buchstabe, Spiel in mm, Punkte als Rang.</figcaption></figure>' % name.upper())
    key = dg[4:]
    svg = dict(k=svg_k, n=svg_n, s=svg_s, c=svg_c, r=svg_r, d=svg_d, fm=svg_fm)[key]()
    ctl = ""
    if key == "k":
        ctl += ('<label class="sel">Plättchen <select class="dgvar" data-group="K">%s</select></label>' %
                "".join('<option value="%s"%s>%s mm</option>' % (de(t, 1), " selected" if t == 1.8 else "", de(t, 1)) for t in SR.K_T))
        ctl += '<label class="rng">Buchse aufdrücken <input type="range" class="dgr" min="0" max="100" value="0" data-for="%s" aria-label="Buchse aufdrücken"></label>' % "K-ALL"
    elif key == "s":
        ctl += ('<label class="sel">Schachtspiel <select class="dgvar" data-group="S">%s</select></label>' %
                "".join('<option value="%s"%s>%s mm</option>' % (de(c), " selected" if c == SR.S_CLR[-1] else "", de(c)) for c in SR.S_CLR))
        ctl += '<label class="rng">Kassette absenken <input type="range" class="dgr" min="0" max="100" value="0" data-for="S-mov" aria-label="Kassette absenken"></label>'
    elif key == "c":
        ctl += '<label class="rng">1 · Buchse von unten <input type="range" class="dgr" min="0" max="100" value="0" data-for="C-buchse" aria-label="Buchse einschieben"></label>'
        ctl += '<label class="rng">2 · LED von oben <input type="range" class="dgr" min="0" max="100" value="0" data-for="C-led" aria-label="LED einlegen"></label>'
    else:
        gid = dict(n="N-mov", r="R-mov", d="D-mov", fm="FM-mov")[key]
        lab = dict(n="Schieber einschieben", r="Buchse eindrücken", d="Leiste einsetzen", fm="Fuß einsetzen")[key]
        ctl += '<label class="rng">%s <input type="range" class="dgr" min="0" max="100" value="0" data-for="%s" aria-label="%s"></label>' % (lab, gid, lab)
    ctl += '<button type="button" class="play" data-play="1">Abspielen</button>'
    extra = ""
    if key == "s":
        extra = '<img class="sect" src="{{IMG_SCHNITT}}" alt="Schnitt: Kassette auf dem Schieber in der Platte" loading="lazy">'
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
                         series=st["series"], kdata=st["kdata"]))
    return "\n".join(out), "".join(nav), spec


def main():
    steps()
    add_final()
    html, nav, spec = build_steps_html()
    with open(TEMPLATE, encoding="utf-8") as f:
        page = f.read()
    rep = {"{{STEPS}}": html, "{{NAV}}": nav, "{{SPEC}}": json.dumps(spec, ensure_ascii=False),
           "{{IMG_BESCHRIFTUNG}}": img_uri("beschriftung.png", 760), "{{IMG_SCHNITT}}": img_uri("schnitt_platte_schieber_kassette.png", 900)}
    for k, v in rep.items():
        page = page.replace(k, v)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(page)
    print("geschrieben: %s (%d kB), %d Schritte, %d Felder" % (os.path.relpath(OUT, ROOT), os.path.getsize(OUT) / 1024, len(STEPS),
                                                              sum(len(s["fields"]) for s in STEPS)))


if __name__ == "__main__":
    main()
