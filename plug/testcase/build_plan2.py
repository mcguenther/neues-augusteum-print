#!/usr/bin/env python3
"""Planungsseite für Steckprobe 2: baut plug/testcase/plan2.html aus plan.template.html (gleicher Stil wie plan.html).

Alle Maße kommen aus plug/testcase/params.py (Stand Steckprobe 1) plus den vorgeschlagenen Änderungen in `PROP`. Nach dem Abnicken wandern die Werte in params.py.

Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m plug.testcase.build_plan2      # schreibt plug/testcase/plan2.html
"""
import json
import math
import os

from plug import dupont as sd
from plug import series2 as N2
from plug.feedback.build import G
from plug.testcase import build_plan as BP
from plug.testcase import params as P
from plug.testcase.build_plan import de, decision_card

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TEMPLATE = os.path.join(HERE, "plan.template.html")
OUT = os.path.join(HERE, "plan2.html")

# Vorschläge für Steckprobe 2 (nach dem Abnicken in params.py übernehmen)
PROP = dict(
    HSG_TOL=0.60,            # Taschenhöhe 14,60: Buchse ist etwa 14,55 hoch (Tasche 14,45 + 0,10 stand sie heraus)
    BUCHSE=14.55,            # aus Steckprobe 1 abgeleitet, nicht gemessen
    SHAFT_EXTRA=0.30,        # Schacht tiefer als die Kassette hoch ist (Kassette ragte 0,2 heraus)
    EF_CH=0.5,               # Fase an Bettkanten und Schachteingang
    SLOT_END=-8.0,           # Schlitz für die Lötenden 1 mm länger (vorher -7,0)
    STAMP_AIR=1.2,           # Luft zwischen Stempel und Körper bei geschlossenem Deckel
    LEG_D=2.2,               # Kanal für den Faden
    APEX=3.4,                # Scheitel des V-Kanals über der Plattenunterseite
    SLOPE=0.75,              # Überhang je Schicht / Schichthöhe wie Platte B (0,15 / 0,2): Kanal etwa 53° zur Waagerechten
    ENTRY_R=2.0,             # Einführtrichter an der Unterseite (Radius am Bett)
    LASCHE_X=15.6,           # Mitte der Laschen (x); Wand zum Plattenrand und zur Mulde mindestens 1,4 mm
    LASCHE_Y=6.0,            # Mitte des V (y) vom Plattenrand
)


def half_span():
    """Abstand Eintritt bis Scheitel in y."""
    return PROP["APEX"] * PROP["SLOPE"]


def kass_top():
    return sd.HSG_H + PROP["HSG_TOL"] + N2.SEAT_RISE + P.PODEST_T


def shaft_depth():
    return kass_top() + PROP["SHAFT_EXTRA"]


# --------------------------------------------------------------------------
# Zeichnungen
# --------------------------------------------------------------------------
def svg_corner():
    """Schnitt durch eine Ecke der Platte: Faden von unten durch den Deckel, schräg durch die Lasche und wieder nach unten."""
    S = 17.0
    ox = 78
    g = G(S, ox, 8.0 * S + 20)
    hz, r, ld, sl = PROP["APEX"], PROP["ENTRY_R"], PROP["LEG_D"], PROP["SLOPE"]
    ya = PROP["LASCHE_Y"]
    ye1, ye2 = ya - half_span(), ya + half_span()
    xl, xr = ye1 - r - 0.2, ye2 + r + 0.2          # Ausschnitt im Deckel
    W = 15.0
    g.rect(-0.6, W, -4.4, -2.4, "d-bld")
    g.text(W - 0.4, -3.2, "Hut (Stoff)", "dl", "end")
    g.rect(0.0, xl, -P.LID_T_T, 0.0, "d-lid")
    g.rect(xr, W, -P.LID_T_T, 0.0, "d-lid")
    g.text(W - 0.4, -1.1, "Deckel", "dls", "end")
    g.rect(0.0, W, 0.0, 7.4, "d-slab")
    g.text(W - 0.4, 6.5, "Platte", "dlb", "end")
    for ye in (ye1, ye2):
        g.poly([(ye - r, -0.01), (ye + r, -0.01), (ye + ld / 2, 1.5), (ye - ld / 2, 1.5)], "d-void")
    for (xa, za), (xb, zb) in (((ye1, 0.0), (ya, hz)), ((ya, hz), (ye2, 0.0))):
        g.o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" style="stroke:var(--field);stroke-width:%.1f;stroke-linecap:round"/>' % (
            g.X(xa), g.Z(za), g.X(xb), g.Z(zb), ld * S))
    dy = 3.4 * sl                                   # Fortsetzung der Schenkel nach unten in den Hut
    g.o.append('<path d="M%.1f,%.1f L%.1f,%.1f L%.1f,%.1f L%.1f,%.1f L%.1f,%.1f" fill="none" style="stroke:var(--f-wire);stroke-width:2.2;stroke-dasharray:5 3;stroke-linecap:round;stroke-linejoin:round"/>' % (
        g.X(ye1 - dy), g.Z(-3.4), g.X(ye1), g.Z(0.0), g.X(ya), g.Z(hz), g.X(ye2), g.Z(0.0), g.X(ye2 + dy), g.Z(-3.4)))
    g.text(ya - 1.2, hz + 2.5, "Lasche (Material über dem Kanal)", "dls")
    g.text(ya - 1.2, hz + 1.8, "Scheitel %s mm über der Unterseite" % de(hz, 1), "dls")
    g.text(ye1 - dy, -4.9, "Faden von unten", "dln", "middle")
    g.text(ye2 + dy, -4.9, "Faden nach unten", "dln", "middle")
    g.text(ye2 + r + 0.5, 0.6, "Trichter", "dls", "start")
    g.text(-0.5, 3.7, "Plattenrand", "dls", "end")
    return g.svg(int(ox + W * S + 12), int(12.9 * S + 28), "Schnitt durch eine Plattenecke: Faden läuft von unten schräg durch die Lasche und wieder nach unten")


def svg_under():
    """Blick von unten auf Platte und Deckel: Fensterschlitz in der Mitte, vier Eck-Laschen mit Trichtern und Deckelausschnitten."""
    d = P.dims()
    S = 8.5
    pw, pl = P.plate_size()
    ph0 = d["yc"] - P.BOX_L / 2 - P.PLATE_MARGIN
    ph1 = ph0 + pl
    r, hs = PROP["ENTRY_R"], half_span()
    g = G(S, pw / 2 * S + 18, ph1 * S + 24)
    g.rect(-pw / 2, pw / 2, ph0, ph1, "d-lid")
    yc1, yc2 = ph0 + PROP["LASCHE_Y"], ph1 - PROP["LASCHE_Y"]
    for sx in (-1, 1):
        for yc in (yc1, yc2):
            x = sx * PROP["LASCHE_X"]
            g.rect(x - r - 0.3, x + r + 0.3, yc - hs - r - 0.3, yc + hs + r + 0.3, "d-void")
            for yy in (yc - hs, yc + hs):
                g.o.append('<circle cx="%.1f" cy="%.1f" r="%.1f" class="d-dash"/>' % (g.X(x), g.Z(yy), r * S))
            g.o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="d-wire" style="stroke-width:2"/>' % (g.X(x), g.Z(yc - hs), g.X(x), g.Z(yc + hs)))
    g.rect(-7.0, 7.0, BP.LID_WIN[0], BP.LID_WIN[1], "d-void")
    g.o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" class="d-dash"/>' % (
        g.X(-BP.KABEL_HX), g.Z(BP.KABEL_Y1), 2 * BP.KABEL_HX * S, (BP.KABEL_Y1 - BP.LOETRAUM_Y0) * S))
    yb = d["yb"]
    for sx in (-1, 1):
        g.rect(*sorted((sx * 2.4, sx * 5.3)), yb - 0.88, yb + 0.88, "d-body")
    g.text(0, (BP.LID_WIN[0] + BP.LID_WIN[1]) / 2 - 0.3, "Fenster für die Kabel", "dls")
    g.text(0, yb + 2.2, "Stempel (Anschlag)", "dls")
    g.text(-BP.KABEL_HX + 0.6, BP.KABEL_Y1 - 1.2, "Kabelraum", "dls", "start")
    g.text(PROP["LASCHE_X"], yc2 - hs - r - 1.6, "Lasche", "dlb")
    g.text(0, ph1 + 1.0, "Unterseite von unten gesehen", "dls")
    g.text(0, ph0 - 1.6, "Kante bei den Lötenden", "dls")
    return g.svg(int(pw * S + 36), int(pl * S + 50), "Blick von unten: Deckel mit Fenster und vier Eck-Laschen mit Faden-Trichtern")


def svg_kassette():
    """Höhen: Kassette, Buchse bündig, Schacht und Anschlagrand (längs durch die Tasche, z nach oben)."""
    S = 11.0
    top, tol, depth = kass_top(), PROP["HSG_TOL"], shaft_depth()
    g = G(S, 70, 20 + 19.5 * S)
    stop = P.STOP_T
    w = 13.5
    g.rect(-2.2, 0.0, 0.0, depth, "d-bld")
    g.rect(w, w + 2.2, 0.0, depth, "d-bld")
    g.rect(-2.2, w + 2.2, depth, depth + stop, "d-bld")
    g.rect(1.2, w - 1.2, depth - 0.01, depth + stop + 0.01, "d-void")
    g.rect(0.0, w, 0.0, top, "d-kass")
    g.rect(1.2, w - 1.2, -0.01, sd.HSG_H + tol, "d-void")
    g.rect(1.3, w - 1.3, 0.0, PROP["BUCHSE"], "d-hsg")
    g.line(-3.6, 0.0, -3.6, depth, "dimn")
    g.text(-3.9, depth / 2, "Schacht %s" % de(depth), "dln", "end")
    g.line(w + 3.6, 0.0, w + 3.6, top, "dimn")
    g.text(w + 3.9, top / 2 + 1.0, "Kassette %s" % de(top), "dln", "start")
    g.text(w + 3.9, top / 2 - 0.4, "Tasche %s" % de(sd.HSG_H + tol), "dls", "start")
    g.text(w + 3.9, top / 2 - 1.6, "Buchse etwa %s" % de(PROP["BUCHSE"]), "dls", "start")
    g.line(w, top + 0.15, w + 3.4, top + 0.15, "dimn")
    g.text(w + 3.9, top + 0.15 - 0.35, "Luft %s" % de(PROP["SHAFT_EXTRA"]), "dlb", "start")
    g.text(w / 2, depth + stop / 2 - 0.35, "Anschlagrand %s" % de(stop, 1), "dls")
    g.text(w / 2, -0.9, "bündig mit der Fußunterkante", "dls")
    return g.svg(440, int(20 + 19.5 * S + 24), "Kassette im Schacht mit Höhen")


# --------------------------------------------------------------------------
# Inhalt
# --------------------------------------------------------------------------
def head():
    return ('<header class="top"><p class="kicker">Steckmechanismus · nach Steckprobe 1</p><h1>Steckprobe 2</h1>'
            '<p class="lead">Plan für den nächsten Druck. Die Steckprobe 1 hat gezeigt, dass Kassette, Einpressen, Mulde und Pin-Treffer ohne Trichter funktionieren und '
            'Kontakt da ist. Hier stehen die Korrekturen, die Befestigung mit Faden statt Schrauben und die Entscheidungen, die du abnicken sollst. '
            'Vorher gelesen: <code>plug/logbook/lessons.md</code> und <code>current.md</code>.</p>'
            '<ul class="sum"><li><b>Kassette:</b> Tasche %s hoch (Buchse stand bei 14,45 noch heraus), Schacht %s tief (Kassette ragte 0,2 heraus).</li>'
            '<li><b>Faden:</b> von unten durch einen Trichter, schräg durch eine Lasche in der Platte und wieder nach unten; keine Schrauben, nichts an der Oberseite.</li>'
            '<li><b>Winkelleiste:</b> Körper darf nicht kippen (Rippen an der hinteren Taschenwand), Deckel-Stempel nur noch als Anschlag mit %s Luft.</li>'
            '<li><b>Platte B</b> bleibt die Basis, Fase 0,5, Schlitz für die Lötenden 1 mm länger.</li></ul></header>'
            % (de(sd.HSG_H + PROP["HSG_TOL"]), de(shaft_depth()), de(PROP["STAMP_AIR"], 1)))


def sec_befund():
    rows = [
        ("Buchse steht in Kassette 1 minimal heraus; 14,15 passt keine", "Tasche auf %s; nur eine Variante" % de(sd.HSG_H + PROP["HSG_TOL"]), "L13, L17"),
        ("Kassette ragt nach dem Einpressen 0,2 mm unten heraus", "Schacht %s mm tiefer als die Kassette, Gebäude entsprechend höher" % de(PROP["SHAFT_EXTRA"], 1), "L12"),
        ("Schacht B (Passzone) zu lose", "entfällt; nur A mit 0,06 durchgehend", "L10"),
        ("Leichter Wulst am Bett trotz Fase 0,4", "Fase %s an Bettkanten und Schachteingang" % de(PROP["EF_CH"], 1), "L03"),
        ("Körper kippt oder wackelt, Deckel schließt nicht, Stempel stoßen an", "Rippen an der hinteren Taschenwand; Stempel als Anschlag mit Luft; Heißkleber als Ausweg", "L21"),
        ("Schrauben nicht vorhanden", "Faden-Laschen statt Schrauben", "L28"),
        ("Zu wenig Platz hinter den Lötenden", "Schlitz 1 mm länger; für den echten Boden eigenes Konzept", "L20"),
        ("Brücken bei Platte A", "Platte B (Trichter) bleibt Basis, A entfällt", "L05"),
    ]
    trs = "".join('<tr><td>%s</td><td>%s</td><td class="n">%s</td></tr>' % r for r in rows)
    return ('<section class="sec"><h2>Aus Steckprobe 1 folgt</h2><div class="tw"><table class="t"><thead><tr><th>Befund</th><th>Änderung</th><th>Lehre</th></tr></thead><tbody>%s</tbody></table></div></section>' % trs)


def sec_faden():
    fig1 = ('<figure class="fig"><div class="figbox s460">%s</div><figcaption>Schnitt durch eine Ecke der Platte (nur die unteren 7,4 mm). Der Faden (rot) kommt aus dem Hut, geht durch den Ausschnitt im Deckel in den Trichter, '
            'schräg durch die Lasche und auf der anderen Seite wieder nach unten in den Hut.</figcaption></figure>' % svg_corner())
    fig2 = ('<figure class="fig"><div class="figbox s460">%s</div><figcaption>Blick von unten. In jeder Ecke ein Paar Trichter (gestrichelte Kreise) mit dem Faden (rot) dazwischen, im Deckel ein Ausschnitt darüber. '
            'Mittig das Fenster für die Kabel und der Kabelraum der Platte (gestrichelt), die Stempel als dunkle Flächen.</figcaption></figure>' % svg_under())
    return ('<section class="sec"><h2>Befestigung mit Faden</h2><div class="two">%s%s</div>'
            '<p class="note">Der Faden tritt nicht an der Oberseite aus. Er läuft in jeder der vier Ecken von unten schräg (etwa 53° zur Waagerechten) in die Platte, über einen Scheitel in %s mm Höhe und wieder schräg nach unten heraus. '
            'Die Lasche ist das Material über dem Kanal. Beide Eintritte haben einen breiten Trichter (Radius %s mm an der Unterseite), damit Nadel und Faden leicht treffen. '
            'Das Material über dem Kanal trägt den Zug, weil die Platte beim Nähen an den Hut gezogen wird; der Deckel liegt dazwischen und wird mit angedrückt. '
            'Der Kanal hat %s mm Durchmesser. Er steigt wie die Böschungen der Platte B (0,15 mm Überhang je Schicht), ist also ohne Support druckbar; die Wände zum Plattenrand und zur Mulde bleiben mindestens 1,4 mm dick.</p>'
            '<p class="risk"><b>Zu klären:</b> Der Deckel braucht an den vier Ecken Ausschnitte über den Trichtern; dort liegt er nicht mehr zwischen Platte und Hut. Ist das in Ordnung?</p></section>'
            % (fig1, fig2, de(PROP["APEX"], 1), de(PROP["ENTRY_R"], 1), de(PROP["LEG_D"], 1)))


def sec_kassette():
    top, tol = kass_top(), PROP["HSG_TOL"]
    e0 = P.dims()["E"]
    rows = [("Buchse bündig eingesetzt (Tisch-Methode)", de(e0), "Luft 0"),
            ("Buchse bis an die Schultern gerutscht", de(e0 - (tol - (PROP["BUCHSE"] - sd.HSG_H))), "Luft %s" % de(sd.HSG_H + tol - PROP["BUCHSE"])),
            ("Zum Vergleich: Kassette 1 aus Steckprobe 1", de(e0 - 0.45), "Luft 0,45")]
    trs = "".join('<tr><td>%s</td><td class="n">%s mm</td><td class="n">%s</td></tr>' % r for r in rows)
    fig = '<figure class="fig"><div class="figbox s460">%s</div><figcaption>Kassette im Schacht (Schnitt, Höhen in mm). Die Buchse sitzt bündig, die Kassette steht unten bündig mit der Fußunterkante.</figcaption></figure>' % svg_kassette()
    return ('<section class="sec"><h2>Kassette und Schacht</h2><div class="two">%s<div style="display:flex;flex-direction:column;gap:10px">'
            '<p class="note">Die echte Buchse ist etwa %s mm hoch (aus Steckprobe 1: Tasche 14,45, die Buchse stand noch 0,1 mm heraus). Das Nachmessen entfällt, das Delta reicht. '
            'Die Tasche bekommt %s, also etwa 0,05 mm Luft. Die Kassette wird dadurch %s hoch, der Schacht %s tief (0,3 mehr), das Mini-Gebäude %s hoch.</p>'
            '<div class="tw"><table class="t"><thead><tr><th>Fall</th><th>Einstecktiefe E</th><th></th></tr></thead><tbody>%s</tbody></table></div>'
            '<p class="note">Die Luft von 0,3 mm im Schacht über der Kassette nimmt die Höhentoleranz auf. Steht die Kassette unten noch heraus, drückt sie der Muldenboden beim Aufsetzen bis bündig. '
            'Stabil gemessen ist E bis 5,08.</p></div></div></section>'
            % (fig, de(PROP["BUCHSE"]), de(sd.HSG_H + tol), de(top), de(shaft_depth()), de(shaft_depth() + P.STOP_T), trs))


def sec_parts():
    w = BP.est_weights()
    d = P.dims()
    pw, pl = P.plate_size()
    top = kass_top()
    rows = [("Kassette v5", "2 ×", "%s × %s × %s" % (de(P.kass_dims()["cw"], 1), de(P.kass_dims()["L"], 1), de(top, 2)), "Tasche %s, Podest, Fase %s; eine bestücken, eine Reserve" % (de(sd.HSG_H + PROP["HSG_TOL"]), de(PROP["EF_CH"], 1)), "%s g je" % de(w["kass"], 0)),
            ("Mini-Gebäude A", "1 ×", "%s × %s × %s" % (de(P.BOX_W, 0), de(P.BOX_L, 0), de(shaft_depth() + P.STOP_T, 2)), "Schacht 0,06 durchgehend, %s tief", "%s g" % de(w["bld"], 0)),
            ("Mini-Grundplatte B2", "1 ×", "%s × %s × %s" % (de(pw, 0), de(pl, 0), de(d["plate_t"], 1)), "Platte B mit Lasche-Kanälen in den vier Ecken, Rippen an der hinteren Taschenwand, Schlitz 1 mm länger, ohne Schraublöcher", "%s g" % de(w["plate"], 0)),
            ("Mini-Deckel 2", "1 ×", "%s × %s × %s" % (de(pw, 0), de(pl, 0), de(P.LID_T_T, 1)), "Fenster, vier Eck-Ausschnitte, Stempel als Anschlag mit %s Luft" % de(PROP["STAMP_AIR"], 1), "%s g" % de(w["lid"], 0))]
    rows[1] = (rows[1][0], rows[1][1], rows[1][2], rows[1][3] % de(shaft_depth()), rows[1][4])
    trs = "".join('<tr><td><b>%s</b></td><td class="n">%s</td><td class="n">%s</td><td>%s</td><td class="n">%s</td></tr>' % r for r in rows)
    tot = 2 * w["kass"] + w["bld"] + w["plate"] + w["lid"]
    return ('<section class="sec"><h2>Was gedruckt wird</h2><div class="tw"><table class="t"><thead><tr><th>Teil</th><th>Anzahl</th><th>Maße in mm</th><th>Inhalt</th><th>Material</th></tr></thead><tbody>%s</tbody></table></div>'
            '<p class="note">Gesamt etwa %s g, bei deinem Drucker (47 g in 2,5 h) rund %s Stunden. Mini-Gebäude B, Kassette 2 und Platte A entfallen. Zum Funktionstest (LED, Controller) '
            'brauchst du nur die Kaufteile; Kassette, LED und Adern bestückst du wie in Schritt L des letzten Testbogens.</p></section>' % (trs, de(tot, 0), de(tot / 47.0 * 2.5, 1)))


def sec_risks():
    risks = [("Faden-Kanal im Druck.", "Ein Kanal mit 2,2 mm Durchmesser und 0,15 mm Überhang je Schicht (wie Platte B) mit Trichtern ist ohne Support druckbar, aber der Scheitel ist eine kleine Rundung mit Treppenstufen. Der Faden darf an den Stufen nicht scheuern: Kanal innen glatt nacharbeiten oder die Treppe feiner schneiden."),
             ("Deckel an den Ecken.", "Ausschnitte über den Trichtern schwächen die Ecken des Deckels; der Deckel hat 2,0 mm und ist am Rand sonst unverändert."),
             ("Körper-Halt.", "Rippen an der hinteren Taschenwand sind eine Vermutung (Körper hat in der um 1,5 mm verlängerten Tasche Spiel in y). Der Heißkleber-Weg bleibt Ausweg."),
             ("Buchsenhöhe.", "Die Tasche 14,60 passt nur über Buchsen bis etwa 14,6. Höhere Buchsen gehen nicht hinein; für diesen Fall dient die zweite Kassette (Karte „Taschenhöhe“, Variante C)."),
             ("Stempel.", "Nur noch Anschlag gegen den Steckdruck; die Haltekraft gegen Druck von oben liegt dann bei der Reibung der Rippen oder beim Heißkleber.")]
    return '<section class="sec"><h2>Risiken</h2>%s</section>' % "".join('<p class="risk"><b>%s</b> %s</p>' % r for r in risks)


DECISIONS = [
    dict(id="F", tag="Faden", title="Fadenführung an den Ecken", rec="A", text="Kein Faden an der Oberseite; breite Einführung unten, schräg durch eine Lasche, schräg nach unten heraus.",
         opts=[("A", "V-Kanal in der Platte (etwa 53° zur Waagerechten, Scheitel 3,4 über der Unterseite), Trichter unten, Ausschnitte im Deckel (wie im Bild)"),
               ("B", "Laschen als Ohren außen an der Platte (ragen über den Rand), gleicher V-Kanal"),
               ("C", "gerade Löcher durch Platte und Deckel, Faden tritt oben aus (nicht gewünscht, nur zum Vergleich)")]),
    dict(id="T", tag="Tasche", title="Taschenhöhe der Kassette", rec="A", text="Die Buchse ist etwa 14,55 hoch; jede Luft darüber kostet Einstecktiefe, wenn sie hochrutscht.",
         opts=[("A", "eine Höhe: 14,60, zwei gleiche Kassetten (eine Reserve)"), ("B", "14,55 (kaum Luft, riskant bei Streuung)"),
               ("C", "zwei Höhen: 14,60 und 14,70 als Rückfall")]),
    dict(id="S", tag="Schacht", title="Schachttiefe", rec="A", text="Die Kassette ragte nach dem Einpressen 0,2 mm heraus (Brücke über dem Schacht hängt, Rundung).",
         opts=[("A", "Kassettenhöhe + 0,3 (Luft oben, der Muldenboden drückt sie bündig)"), ("B", "Kassettenhöhe + 0,2"), ("C", "Kassettenhöhe + 0,4")]),
    dict(id="K", tag="Körper", title="Halt des Winkelleistenkörpers", rec="A", text="Der Körper kippt in der um 1,5 mm verlängerten Tasche und hängt ohne Halt von unten.",
         opts=[("A", "zwei Rippen an der hinteren Taschenwand (0,25 mm Übermaß) drücken ihn nach vorn, dazu die Rippen an den Stirnseiten wie bisher"),
               ("B", "keine Änderung an der Tasche; Klecks Heißkleber beim Einbau"), ("C", "beides: Rippen und Klecks")]),
    dict(id="D", tag="Deckel", title="Stempel im Deckel", rec="A", text="Die Stempel stießen beim Aufsetzen an; mehr als 1 mm Luft wird verlangt.",
         opts=[("A", "Stempel bleiben als Anschlag gegen den Steckdruck, 1,2 mm Luft zum Körper, Spitze mit 45°-Fase; notfalls abschneiden"),
               ("B", "ohne Stempel, nur Deckel und Heißkleber"), ("C", "Stempel wie bisher (nicht empfohlen)")]),
    dict(id="E", tag="Fase", title="Fase an Bettkanten und Schachteingang", rec="A", text="Der leichte Wulst blieb mit 0,4.",
         opts=[("A", "0,5"), ("B", "0,6"), ("C", "bleibt 0,4")]),
    dict(id="L", tag="Lötraum", title="Schlitz hinter den Lötenden", rec="A", text="Für diese Probe reicht wenig; für den echten Boden kommt ein eigenes Konzept mit freiem Kabelraum.",
         opts=[("A", "Schlitz 1 mm länger (Ende bei −8,0), sonst unverändert"), ("B", "unverändert"), ("C", "deutlich länger, mit Support drucken")]),
]


def main():
    sections = "".join([sec_befund(), sec_faden(), sec_kassette(), sec_parts(), sec_risks()])
    sections += '<section class="top"><h2>Entscheidungen</h2><p class="lead">Mit den Empfehlungen ist der Plan rund. Abweichungen bitte markieren, danach erzeuge ich die STL.</p></section>'
    sections += "\n".join(decision_card(x) for x in DECISIONS)
    spec = [dict(id=x["id"], tag=x["tag"], title=x["title"]) for x in DECISIONS]
    with open(TEMPLATE, encoding="utf-8") as f:
        page = f.read()
    page = (page.replace("<title>Planung Testfall Kassette</title>", "<title>Planung Steckprobe 2</title>")
                .replace("testfall-plan-v1", "steckprobe2-plan-v1").replace("PLANUNG TESTFALL KASSETTE · ANTWORT", "PLANUNG STECKPROBE 2 · ANTWORT"))
    for k, v in {"{{HEAD}}": head(), "{{SECTIONS}}": sections, "{{SPEC}}": json.dumps(spec, ensure_ascii=False)}.items():
        page = page.replace(k, v)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(page)
    print("geschrieben: %s (%d kB)" % (os.path.relpath(OUT, ROOT), os.path.getsize(OUT) / 1024))


if __name__ == "__main__":
    main()
