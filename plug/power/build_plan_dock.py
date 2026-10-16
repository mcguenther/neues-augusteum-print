#!/usr/bin/env python3
"""Plan Test-Dock "Steckerraum" als HTML mit Zeichnungen: plug/power/plan_dock.html.

Idee des Nutzers (2026-10-16): keine Nische, kein Schlitz, kein Steg; die Winkelleiste steckt 1 mm tief in der Platte, 1 mm ragt unten heraus, darunter
ein durchgehender Raum (Powerbank, Stecker, Adern). Die Lötenden liegen auf einer Stufe auf der Unterseite der Platte. Gedruckt mit der Unterseite auf dem
Bett und Support unter dem Muldenboden. Werte stehen in `PROP` (nach Regel 8 nicht in `parts.py`).
    python3 -m plug.power.build_plan_dock
"""
import os

from plug import dupont as sd
from plug.power import build_concept as BC
from plug.power import params as PP
from plug.testcase import params as TP

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "plan_dock.html")
de = lambda x, n=1: ("%.*f" % (n, x)).replace(".", ",")

D = PP.stack()
PROP = dict(
    POCKET_T=1.0,          # Tiefe der Tasche für die Leiste in der Platte; 1,0 mm vom Körper ragen heraus
    GAP=3.4,               # Luft zwischen Platte und Powerbank (Leiste 1,0 + Draht und Lötstelle + 0,6 Spiel), Test mit 3,4 und 2,4
    GAP_TIGHT=2.4,
    PIN_H=2.5,             # Zapfen, 1 mm länger als in Steckprobe 2 (Nutzer: wackelt)
    HOLE_D=2.8,            # Tiefe des Zapfenlochs
    TAIL_Y0=D["y_tail"],   # Ende der Lötenden
    SLOT_END=PP.SLOT_END,  # Ende der Stufe
)
PLATE_T = D["F"] + TP.CEIL_T + PROP["POCKET_T"]      # 11,6
Z_UNDER = -PLATE_T                                   # Unterseite der Platte
Z_HB, Z_BM = D["z_hb"], D["z_bm"]                    # Körper oben -10,6, Mitte -11,6
Z_BB = Z_BM - sd.HDR_BODY / 2                        # Körper unten -12,6
STEP_Z = D["step"]                                   # Stufendecke -11,08
YB, HD = D["yb"], BC.DK["hd"]
HW = BC.DK["hw"]
Y_SLOT = D["yb"] - HD - TP.BODY_EXT_T                # -4,92
Y_POCK1 = 1.6                                        # Tasche reicht bis hinter die Pins
PY0 = PP.SLOT_END - 6.0
PY1 = D["yc"] + TP.BOX_L / 2 + TP.S2_MARGIN
PX = TP.BOX_W / 2 + TP.S2_MARGIN
POSTS = [(-8.5, 8.0), (8.5, 8.0), (-8.5, 30.0), (8.5, 30.0)]
PIN_X = sd.pin_x()


class Svg:
    def __init__(self, x0, y0, x1, y1, s, pad=16):
        self.x0, self.y0, self.s, self.pad = x0, y0, s, pad
        self.w, self.h = (x1 - x0) * s + 2 * pad, (y1 - y0) * s + 2 * pad
        self.o = []

    def X(self, x):
        return self.pad + (x - self.x0) * self.s

    def Y(self, y):                                  # y nach unten
        return self.pad + (y - self.y0) * self.s

    def rect(self, x0, y0, x1, y1, cls, extra=""):
        self.o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" class="%s" %s/>' % (self.X(x0), self.Y(y0), (x1 - x0) * self.s, (y1 - y0) * self.s, cls, extra))

    def line(self, x0, y0, x1, y1, cls):
        self.o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="%s"/>' % (self.X(x0), self.Y(y0), self.X(x1), self.Y(y1), cls))

    def poly(self, pts, cls):
        self.o.append('<polyline points="%s" class="%s"/>' % (" ".join("%.1f,%.1f" % (self.X(x), self.Y(y)) for x, y in pts), cls))

    def circ(self, x, y, r, cls):
        self.o.append('<circle cx="%.1f" cy="%.1f" r="%.1f" class="%s"/>' % (self.X(x), self.Y(y), r * self.s, cls))

    def text(self, x, y, s, cls="lab", anchor="start", dy=0):
        self.o.append('<text x="%.1f" y="%.1f" class="%s" text-anchor="%s">%s</text>' % (self.X(x), self.Y(y) + dy, cls, anchor, s))

    def svg(self, ident, label):
        return '<svg id="%s" viewBox="0 0 %.0f %.0f" role="img" aria-label="%s" class="fig">%s</svg>' % (ident, self.w, self.h, label, "".join(self.o))


def schnitt():
    """Längsschnitt durch die Pin-Reihe (x = 0): y nach rechts (Lötenden links), z nach unten."""
    y0, y1 = -14.0, 12.0
    z_top, z_tab = 1.5, -(PLATE_T + PROP["GAP"]) - 2.2
    g = Svg(y0, -z_top, y1, -z_tab, 22.0)
    Z = lambda z: -z                                        # z nach unten zeichnen
    r = lambda a0, z0, a1, z1, c, e="": g.rect(a0, Z(z1), a1, Z(z0), c, e)
    r(y0, Z_UNDER, y1, 0.0, "plate")                         # Platte
    r(-6.95, -D["F"], y1, 0.0, "foot")                       # Gebäudefuß in der Mulde (Rand der Mulde bei y -6,95)
    r(Y_SLOT, Z_UNDER, Y_POCK1, Z_HB, "void")                # Tasche, 1,0 tief
    r(PP.SLOT_END, Z_UNDER, Y_SLOT, STEP_Z, "void")          # Stufe für die Lötenden
    r(YB - HD, Z_BB, YB + HD, Z_HB, "body")                  # Körper der Leiste: 1,0 in der Tasche, 1,0 heraus
    g.line(PROP["TAIL_Y0"], Z(Z_BM), 0.0, Z(Z_BM), "tail")  # Lötende
    g.line(0.0, Z(Z_BM), 0.0, Z(D["z_tip"]), "tail")       # senkrechter Pin
    g.poly([(PROP["TAIL_Y0"], Z(Z_BM)), (PROP["TAIL_Y0"] - 1.2, Z(Z_BM - 1.9)), (y0 + 1.0, Z(Z_BM - 1.9))], "wire")
    zt = -(PLATE_T + PROP["GAP"])
    g.line(y0, Z(zt), y1, Z(zt), "table")
    g.text(y0 + 0.4, Z(zt) , "Tisch, steht für die Oberkante der Powerbank", "lab mut", dy=15)
    g.line(y1 - 3.0, Z(Z_UNDER), y1 - 3.0, Z(zt), "dimn")
    g.text(y1 - 3.4, (Z(Z_UNDER) + Z(zt)) / 2, "Luft %s" % de(PROP["GAP"]), "lab ok", "end", dy=4)
    g.text(y1 - 0.5, -1.0, "Plattenoberseite", "lab mut", "end", dy=-4)
    g.text(1.5, Z(-3.5), "Gebäudefuß in der Mulde", "lab", "start", dy=0)
    g.text(y0 + 0.4, Z(-4.5), "Platte %s" % de(PLATE_T), "lab mut", "start", dy=0)
    g.text(y0 + 0.4, Z(-6.0), "Muldenboden %s" % de(TP.CEIL_T), "lab mut", "start", dy=0)
    g.text(YB, Z(Z_BB) + 0.0, "Körper 2,0: 1,0 in der Tasche, 1,0 heraus", "lab", "middle", dy=18)
    g.text(PROP["TAIL_Y0"] - 0.6, Z(Z_BM - 1.9), "Draht", "lab wirec", "end", dy=14)
    g.text(-7.4, Z(Z_UNDER + 0.7), "Stufe", "lab", "end", dy=3)
    g.text(Y_POCK1 + 1.2, Z(Z_UNDER), "Tasche 1,0 tief (Support)", "lab mut", "start", dy=11)
    return g.svg("sect", "Längsschnitt durch das neue Dock")


def unten():
    """Ansicht von unten (Unterseite der Platte, wie im Slicer): x nach rechts, y nach oben."""
    g = Svg(-PX, -PY1, PX, -PY0, 9.0)
    Y = lambda y: -y
    R = lambda x0, y0, x1, y1, c, e="": g.rect(x0, Y(y1), x1, Y(y0), c, e)
    R(-PX, PY0, PX, PY1, "plate")
    R(-12.0, -6.95, 12.0, 31.05, "mulde")
    R(-HW, Y_SLOT, HW, Y_POCK1, "sup")
    R(-4.93, PP.SLOT_END, 4.93, Y_SLOT, "step")
    R(-HW, Y_SLOT, HW, Y_POCK1, "sup")
    R(-HW + 0.4, YB - HD, HW - 0.4, YB + HD, "body")
    for x in PIN_X:
        g.circ(x, Y(0.0), 0.7, "hole")
        g.circ(x, Y(0.0), 0.7, "hole")
    for x, y in POSTS:
        g.circ(x, Y(y), 2.15, "post")
    g.text(HW + 1.0, Y(-3.3), "Körper 10,9 × 2,2", "lab", "start", dy=4)
    g.text(HW + 1.0, Y(0.8), "Tasche mit Support", "lab", "start", dy=4)
    g.text(5.6, Y(-6.5), "Stufe (massiv)", "lab", "start", dy=4)
    g.text(0, Y(0.0), "4 Pin-Löcher Ø 1,4", "lab", "middle", dy=-8)
    g.text(0, Y(20.0), "Mulde (oben)", "lab mut", "middle", dy=0)
    g.text(0, Y(PY0), "Plattenrand (vorn)", "lab mut", "middle", dy=-4)
    g.text(-8.5, Y(8.0), "Zapfenloch", "lab", "middle", dy=-14)
    return g.svg("below", "Ansicht der Plattenunterseite mit Tasche, Stufe und Support")


CSS_EXTRA = """
.fig { width: 100%; height: auto; display: block; min-width: 560px; }
.fig text { font-family: var(--font); fill: var(--fg); font-size: 11.5px; }
.fig .mut { fill: var(--muted); } .fig .ok { fill: var(--ok); font-weight: 600; } .fig .inv { fill: var(--panel); } .fig .wirec { fill: var(--c-thread); }
.fig .plate { fill: var(--c-plate); stroke: var(--edge); stroke-width: .8; }
.fig .foot { fill: var(--c-bld); stroke: var(--edge); stroke-width: .6; }
.fig .void { fill: var(--panel); stroke: var(--edge); stroke-width: .6; stroke-dasharray: 3 2; }
.fig .body { fill: var(--c-port); stroke: var(--edge); stroke-width: .6; }
.fig .tail { stroke: var(--accent-fill); stroke-width: 3; stroke-linecap: round; fill: none; }
.fig .wire { stroke: var(--c-thread); stroke-width: 3; fill: none; stroke-linecap: round; stroke-linejoin: round; }
.fig .table { stroke: var(--fg); stroke-width: 1.4; }
.fig .dimn { stroke: var(--ok); stroke-width: 1.8; }
.fig .mulde { fill: none; stroke: var(--muted); stroke-width: 1; stroke-dasharray: 5 3; }
.fig .sup { fill: color-mix(in srgb, var(--c-niche) 40%, var(--panel)); stroke: var(--c-niche); stroke-width: 1; stroke-dasharray: 3 2; }
.fig .step { fill: var(--c-plate); stroke: var(--edge); stroke-width: 1.2; }
.fig .hole { fill: var(--panel); stroke: var(--edge); stroke-width: .8; }
.fig .post { fill: var(--panel); stroke: var(--edge); stroke-width: .8; }
#sect text { font-size: 7.4px; } #below text { font-size: 5.4px; } #below { min-width: 0; max-width: 560px; }
.dec { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; }
.dec .card.rec { box-shadow: inset 0 3px 0 var(--accent-fill); }
.dec h3 .tag { font-family: var(--mono); font-size: .72rem; color: var(--accent); letter-spacing: .06em; margin-right: 8px; }
.opts { display: flex; flex-direction: column; gap: 8px; }
.opt { border: 1px solid var(--line); border-radius: 6px; padding: 8px 10px; display: flex; flex-direction: column; gap: 2px; font-size: .92rem; }
.opt.pick { border-color: var(--accent-fill); background: color-mix(in srgb, var(--accent-fill) 12%, transparent); }
.opt b { font-weight: 600; }
.opt .num { color: var(--muted); font-size: .8rem; }
"""


def page():
    head = open(os.path.join(HERE, "concept.template.html"), encoding="utf-8").read().split('<div class="wrap">')[0]
    head = head.replace("<title>Powerbank in der Grundplatte</title>", "<title>Plan Test-Dock Steckerraum</title>").replace("</style>", CSS_EXTRA + "</style>")
    body = f"""<div class="wrap">
<header>
  <div class="kicker">Steckmechanismus · Test-Dock · Plan, noch nicht abgenickt</div>
  <h1>Test-Dock mit durchgehendem Steckerraum</h1>
  <p class="lead">Die Winkelleiste steckt nur noch 1 mm tief in der Platte und ragt 1 mm heraus. Darunter gibt es keine Nische und keinen Steg mehr, nur einen offenen Raum, in dem später auch die Powerbank liegt. Die Lötenden liegen auf einer Stufe. Dieser Plan beschreibt ein kleines Test-Dock dafür. Erst nach deinem Okay entstehen STL.</p>
</header>

<section aria-labelledby="h-ans">
  <h2 id="h-ans">Empfehlung</h2>
  <div class="answer">
    <div class="rec"><span class="lbl">Teile</span><span class="big">1 Platte + 8 Füße</span>
      <span class="small">Mini-Oberplatte <span class="num">{de(2 * PX, 1)} × {de(PY1 - PY0, 1)} × {de(PLATE_T)} mm</span> mit Mulde und neuem Dock, dazu zwei Sätze Füße (3,4 und 2,4 mm) mit Zapfen. Gebäude und Kassette bleiben die aus Steckprobe 2.</span></div>
    <div><span class="lbl">Der Tisch ist die Powerbank</span><span class="big">Luft {de(PROP['GAP'])} mm</span>
      <span class="small">Die Platte steht auf den Füßen über dem Tisch. Der Tisch steht für die Oberkante der Powerbank. So prüfst du Leiste, Lötstelle und Draht, ohne die Powerbank zu brauchen.</span></div>
    <div><span class="lbl">Geprüft wird</span><span class="big">5 Dinge</span>
      <span class="small">Leiste in der flachen Tasche, Lötenden auf der Stufe, saubere Pin-Löcher mit Support, Halt der Leiste beim Aufstecken, Zapfen mit 2,5 mm Länge.</span></div>
    <div><span class="lbl">Aufwand</span><span class="big">≈ 12 g</span>
      <span class="small">Etwa 0,7 h auf deinem Drucker. Support sehr klein, nur 1 mm hoch unter dem Muldenboden.</span></div>
  </div>
</section>

<section aria-labelledby="h-fig">
  <h2 id="h-fig">So sieht das Dock aus</h2>
  <div class="card"><h3>Längsschnitt durch die Pin-Reihe</h3><div class="scroll">{schnitt()}</div>
    <p class="small muted">Die Lötenden (orange) laufen auf Höhe der Plattenunterseite nach links und liegen in der Stufe, der Körper (dunkel) ragt 1,0 mm unter der Platte heraus. Der Draht (rot) hängt unter der Stufe in die Luft. Die Füße stehen vor und hinter dem Schnitt und sind nicht zu sehen.</p></div>
  <div class="card"><h3>Ansicht der Plattenunterseite (wie im Slicer)</h3><div class="scroll">{unten()}</div>
    <p class="small muted">Die orange gestrichelte Fläche ist die Tasche für die Leiste, sie wird mit Support gefüllt, damit der Muldenboden mit den Pin-Löchern sauber druckt. Die Stufe ist massiv. Vier Zapfenlöcher für die Füße.</p></div>
</section>

<section aria-labelledby="h-chain">
  <h2 id="h-chain">Maßkette im Worst-Case</h2>
  <div class="scroll"><table>
    <thead><tr><th>Maß</th><th>Soll</th><th>Worst-Case</th><th>Ergebnis</th><th>Quelle</th></tr></thead>
    <tbody>
    <tr><td>Plattendicke</td><td class="num">Mulde {de(D['F'])} + Muldenboden {de(TP.CEIL_T)} + Tasche {de(PROP['POCKET_T'])} = {de(PLATE_T)}</td><td class="num">Druckmaß ± 0,1</td><td><span class="pill ok">1,0 dünner</span></td><td class="src">bewährt (F, Boden), neu (Tasche)</td></tr>
    <tr><td>Einstecktiefe E</td><td class="num">{de(D['E'], 2)} (Körper oben bleibt z {de(Z_HB)})</td><td class="num">Muldenboden 0,4 bis 0,5: E ≥ 5,18</td><td><span class="pill ok">wie Steckprobe 2</span></td><td class="src">bewährt (r4 S, D)</td></tr>
    <tr><td>Körper der Leiste</td><td class="num">2,0: 1,0 in der Tasche, 1,0 darunter</td><td class="num">Tasche mit Spiel 0,1 je Seite</td><td><span class="pill ok">passt</span></td><td class="src">bewährt (HDR_BODY)</td></tr>
    <tr><td>Lötenden auf der Stufe</td><td class="num">Tail z {de(Z_BM, 2)} ± 0,32, Stufendecke z {de(STEP_Z, 2)}</td><td class="num">Spiel oben 0,2 (bewährt für Körper 1,8 und 2,0)</td><td><span class="pill ok">liegt flach</span></td><td class="src">bewährt (r2 D)</td></tr>
    <tr><td>Draht und Lötstelle</td><td class="num">bis etwa 1,9 unter der Plattenunterseite</td><td class="num">Luft 3,4: 1,5 Reserve; 2,4: 0,5</td><td><span class="pill mid">Test mit zwei Füßen</span></td><td class="src">S geschätzt, ungemessen</td></tr>
    <tr><td>Zapfen</td><td class="num">Ø 4,0, Höhe {de(PROP['PIN_H'])}, Loch Ø 4,3, {de(PROP['HOLE_D'])} tief</td><td class="num">Gleitspiel 0,15 (bewährt), 1 mm länger</td><td><span class="pill mid">zu prüfen</span></td><td class="src">E, r4 U: 1,5 wackelte</td></tr>
    </tbody>
  </table></div>
</section>

<section aria-labelledby="h-dec">
  <h2 id="h-dec">Entscheidungen</h2>
  <div class="dec">
    <div class="card rec"><h3><span class="tag">A</span>Halt der Leiste beim Aufstecken</h3>
      <div class="opts">
        <div class="opt pick"><b>Erst nur Rippen, dann mit Kleber (empfohlen)</b><span>Rippen an den Stirnseiten und hinten (0,12 und 0,25 Übermaß) halten die Leiste in der Tasche. Der Testbogen fragt zuerst ohne, dann mit einem Tropfen Heißkleber am herausragenden Körper.</span></div>
        <div class="opt"><b>Nur Rippen</b><span>Kein Kleber; reicht vielleicht nicht, wenn der Aufsteckdruck die Leiste nach unten schiebt.</span></div>
        <div class="opt"><b>Hinterschnitt (Clip)</b><span>Haltenasen in der Tasche; druckt mit Support, mehr Aufwand, erst wenn A nicht reicht.</span></div>
      </div></div>
    <div class="card rec"><h3><span class="tag">B</span>Füße und Luft</h3>
      <div class="opts">
        <div class="opt pick"><b>Zwei Sätze Füße: 3,4 und 2,4 mm (empfohlen)</b><span>Je vier Füße 6 × 6 mm mit Zapfen 2,5. Du probierst erst 3,4, dann 2,4, und siehst, wie knapp Draht und Lötstelle werden.</span></div>
        <div class="opt"><b>Nur 3,4 mm</b><span>Weniger Teile, aber die untere Grenze der Luft bliebe ungeprüft.</span></div>
      </div></div>
    <div class="card"><h3><span class="tag">C</span>Stufe und Nische</h3>
      <div class="opts">
        <div class="opt pick"><b>Stufe wie Steckprobe 1, keine Nische (entschieden)</b><span>Rille {de(abs(PP.SLOT_END - Y_SLOT))} mm lang, 0,52 tief, Breite wie der Schlitz. Die Nische von Steckprobe 2 (12 × 9,5 mm) entfällt, weil unter der Platte alles offen ist.</span></div>
      </div></div>
    <div class="card"><h3><span class="tag">D</span>Was nicht zum Test gehört</h3>
      <div class="opts">
        <div class="opt pick"><b>Faden-V und Powerbank-Fach</b><span>Fadenführung macht der andere Chat, das Fach steht in der Fachprobe. Dieses Dock zeigt nur Leiste, Lötenden, Support, Halt und Zapfen.</span></div>
      </div></div>
  </div>
</section>

<section aria-labelledby="h-risk">
  <h2 id="h-risk">Druck und Risiken</h2>
  <div class="scroll"><table>
    <thead><tr><th>Teil</th><th>Ausrichtung</th><th>Hinweise</th></tr></thead>
    <tbody>
    <tr><td>Mini-Oberplatte</td><td>Unterseite auf dem Bett, Mulde oben</td><td>Tasche (1,0) und Stufe (0,52) sind Hohlräume direkt am Bett unter dem 0,4 mm dicken Muldenboden. Support: automatisch, Überhangwinkel 30°, Schnittstelle sauber (Abstand 0,1), nur auf der Bauplatte. Die Stufe bleibt massiv. Danach die vier Pin-Löcher mit einer Nadel oder einem 1,2-mm-Bohrer freimachen (Risiko: Supportreste in den Löchern).</td></tr>
    <tr><td>Füße (2 × 4)</td><td>stehend, Zapfen oben</td><td>6 × 6 mm Querschnitt (L06), Zapfen Ø 4,0 × {de(PROP['PIN_H'])}; Satz 3,4 mit einer Kerbe, Satz 2,4 mit zwei.</td></tr>
    <tr><td>Gebäude, Kassette</td><td>aus Steckprobe 2</td><td>unverändert wiederverwenden, kein Neudruck.</td></tr>
    </tbody>
  </table></div>
  <p class="small muted">Berücksichtigte Lehren: L02 Lochmündungen (Fase beidseitig, am Bett durch Support ersetzt), L05 Muldenboden nicht frei über einer Tasche drucken (jetzt Support), L06 keine freistehenden Stifte, L07 Druckausrichtung je Teil, L08 ungemessene Werte markiert, L24 nur fühlbare oder ja/nein-Felder, L25 Variante und ZIP-Version im Ergebnistext, L27 neue Werte nur in <code>plug/power/params.py</code>, L31 Support ist erlaubt.</p>
</section>

<section aria-labelledby="h-test">
  <h2 id="h-test">Was der Testbogen danach abfragt</h2>
  <ul>
    <li>Support entfernt: Muldenboden glatt, vier Pin-Löcher offen oder mit Resten?</li>
    <li>Leiste einsetzen: sitzt sie in der Tasche, liegen Körper und Lötenden flach, wackelt sie?</li>
    <li>Gebäude aufstecken und abziehen, zehn Mal: bleibt die Leiste sitzen (ohne Kleber), dann mit einem Tropfen Kleber.</li>
    <li>Draht anlöten und die Platte auf die Füße 3,4 und dann 2,4 setzen: hängt etwas am Tisch an?</li>
    <li>Zapfen in den Löchern: Sitz 1 bis 5.</li>
    <li>Durchgang für alle vier Pins mit dem Multimeter.</li>
  </ul>
</section>

<section>
  <h2>Nächster Schritt</h2>
  <p>Wenn dir die Empfehlung passt (A: erst Rippen, dann Kleber; B: zwei Füße-Sätze; C: Stufe ohne Nische), baue ich STL, README, ZIP, Prüfbericht und den Testbogen. Sonst nenne mir die Änderungen.</p>
</section>
</div>
"""
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(head + body)
    print("geschrieben: %s (%d kB)" % (os.path.relpath(OUT), os.path.getsize(OUT) // 1024))


if __name__ == "__main__":
    page()
