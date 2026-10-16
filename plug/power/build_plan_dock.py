#!/usr/bin/env python3
"""Plan Test-Dock "Steckerraum" als HTML mit Zeichnungen: plug/power/plan_dock.html.

Idee des Nutzers (2026-10-16): keine Nische, kein Schlitz, kein Steg, keine Tasche, keine Stufe: die Unterseite der Platte ist flach, die Winkelleiste
liegt mit ihrem Körper einfach daran (aufgeklebt), darunter ein durchgehender Raum (Powerbank, Stecker, Adern). Gedruckt mit der Unterseite auf dem Bett,
kein Support. Werte stehen in `PROP` (nach Regel 8 nicht in `parts.py`).
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
    POCKET_T=0.0,          # keine Tasche: der Körper (2,0) liegt unter der flachen Plattenunterseite
    WIRE_DEPTH=2.9,        # Draht und Lötstelle reichen etwa so weit unter die Plattenunterseite (Tail 1,0 + 0,32 + Draht 1,6), S geschätzt
    GAP=3.5,               # Luft zwischen Platte und Powerbank (2,9 + 0,6 Spiel), Test mit 3,5 und 2,5
    GAP_TIGHT=2.5,
    PIN_H=2.5,             # Zapfen, 1 mm länger als in Steckprobe 2 (Nutzer: wackelt)
    HOLE_D=2.8,            # Tiefe des Zapfenlochs
    TAIL_Y0=D["y_tail"],   # Ende der Lötenden
)
PLATE_T = D["F"] + TP.CEIL_T + PROP["POCKET_T"]      # 10,6
Z_UNDER = -PLATE_T                                   # Unterseite der Platte
Z_HB, Z_BM = D["z_hb"], D["z_bm"]                    # Körper oben -10,6, Mitte -11,6
Z_BM = Z_UNDER - sd.HDR_BODY / 2                     # Tail unter der Platte: Körper hängt ganz unter der flachen Unterseite
Z_HB = Z_UNDER                                       # Körper oben liegt an der Platte
Z_BB = Z_UNDER - sd.HDR_BODY                         # Körper unten -12,6
YB, HD = D["yb"], BC.DK["hd"]
HW = BC.DK["hw"]
PY0 = D["y_tail"] - 5.0
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
    y0, y1 = -12.0, 12.0
    zt = -(PLATE_T + PROP["GAP"])
    g = Svg(y0, -1.5, y1, -(zt - 2.0), 24.0)
    Z = lambda z: -z
    r = lambda a0, z0, a1, z1, c: g.rect(a0, Z(z1), a1, Z(z0), c)
    r(y0, Z_UNDER, y1, 0.0, "plate")                         # Platte, Unterseite flach
    r(-6.95, -D["F"], y1, 0.0, "foot")                       # Gebäudefuß in der Mulde
    r(YB - HD, Z_BB, YB + HD, Z_UNDER, "body")               # Körper der Leiste, ganz unter der Platte
    g.line(PROP["TAIL_Y0"], Z(Z_BM), 0.0, Z(Z_BM), "tail")  # Lötende
    g.line(0.0, Z(Z_BM), 0.0, Z(D["z_tip"]), "tail")       # senkrechter Pin
    g.poly([(PROP["TAIL_Y0"], Z(Z_BM)), (PROP["TAIL_Y0"] - 1.0, Z(Z_BM - 1.9)), (y0 + 1.0, Z(Z_BM - 1.9))], "wire")
    g.line(y0, Z(zt), y1, Z(zt), "table")
    g.text(y0 + 0.3, Z(zt), "Tisch, steht für die Oberkante der Powerbank", "lab mut", dy=14)
    g.line(y1 - 2.5, Z(Z_UNDER), y1 - 2.5, Z(zt), "dimn")
    g.text(y1 - 2.9, (Z(Z_UNDER) + Z(zt)) / 2, "Luft %s" % de(PROP["GAP"]), "lab ok", "end", dy=4)
    g.text(y1 - 0.4, 0.0, "Plattenoberseite", "lab mut", "end", dy=-5)
    g.text(1.2, Z(-4.0), "Gebäudefuß in der Mulde", "lab", "start")
    g.text(y0 + 0.4, Z(-5.0), "Platte %s" % de(PLATE_T), "lab mut", "start")
    g.text(y0 + 0.4, Z(-6.2), "Muldenboden %s" % de(TP.CEIL_T), "lab mut", "start")
    g.text(YB + 3.0, Z(Z_UNDER - 1.2), "Körper 2,0, aufgeklebt", "lab", "start", dy=3)
    g.text(PROP["TAIL_Y0"] - 0.5, Z(Z_BM - 1.9), "Draht", "lab wirec", "end", dy=13)
    g.text(PROP["TAIL_Y0"], Z(Z_BM), "Lötende", "lab", "end", dy=-6)
    return g.svg("sect", "Längsschnitt durch das neue Dock")


def unten():
    """Ansicht von unten (Unterseite der Platte, wie im Slicer): x nach rechts, y nach oben."""
    g = Svg(-PX, -PY1, PX, -PY0, 9.0)
    Y = lambda y: -y
    R = lambda x0, y0, x1, y1, c: g.rect(x0, Y(y1), x1, Y(y0), c)
    R(-PX, PY0, PX, PY1, "plate")
    R(-12.0, -6.95, 12.0, 31.05, "mulde")
    R(-HW, YB - HD, HW, YB + HD, "bodyo")
    for x in PIN_X:
        g.circ(x, Y(0.0), 0.7, "hole")
    for x in PIN_X:
        g.line(x, Y(0.0), x, Y(PROP["TAIL_Y0"]), "tailo")
    for x, y in POSTS:
        g.circ(x, Y(y), 2.15, "post")
    g.text(HW + 1.0, Y(YB), "Körper 10,9 × 2,2 (aufgeklebt)", "lab", "start", dy=4)
    g.text(HW + 1.0, Y(0.0), "4 Pin-Löcher Ø 1,4", "lab", "start", dy=4)
    g.text(HW + 1.0, Y(PROP["TAIL_Y0"]), "Lötenden", "lab", "start", dy=4)
    g.text(0, Y(20.0), "Mulde (oben)", "lab mut", "middle")
    g.text(0, Y(PY0), "Plattenrand (vorn)", "lab mut", "middle", dy=-4)
    g.text(-8.5, Y(8.0), "Zapfenloch", "lab", "middle", dy=-14)
    return g.svg("below", "Ansicht der Plattenunterseite mit Pin-Löchern und aufgeklebtem Körper")


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
.fig .bodyo { fill: color-mix(in srgb, var(--c-port) 30%, transparent); stroke: var(--c-port); stroke-width: 1.2; stroke-dasharray: 3 2; }
.fig .tailo { stroke: var(--accent-fill); stroke-width: 1.4; }
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
  <h1>Test-Dock mit flacher Unterseite</h1>
  <p class="lead">Alles auf einer Höhe, ohne Tasche, Stufe, Schlitz, Nische und Steg: Die Unterseite der Platte ist flach, die Winkelleiste liegt mit dem Körper einfach daran und wird aufgeklebt. Darunter gibt es nur einen offenen Raum, in dem später auch die Powerbank liegt. Dieser Plan beschreibt ein kleines Test-Dock dafür. Erst nach deinem Okay entstehen STL.</p>
</header>

<section aria-labelledby="h-ans">
  <h2 id="h-ans">Empfehlung</h2>
  <div class="answer">
    <div class="rec"><span class="lbl">Teile</span><span class="big">1 Platte + 8 Füße</span>
      <span class="small">Mini-Oberplatte <span class="num">{de(2 * PX, 1)} × {de(PY1 - PY0, 1)} × {de(PLATE_T)} mm</span> mit Mulde und vier Pin-Löchern, dazu zwei Sätze Füße ({de(PROP['GAP'])} und {de(PROP['GAP_TIGHT'])} mm) mit Zapfen. Gebäude und Kassette bleiben die aus Steckprobe 2.</span></div>
    <div><span class="lbl">Ohne Support</span><span class="big">Platte nur flach</span>
      <span class="small">Der Muldenboden (0,4 mm) sind die ersten Schichten auf dem Bett, nichts hängt frei. Brücke und Support entfallen ganz.</span></div>
    <div><span class="lbl">Der Tisch ist die Powerbank</span><span class="big">Luft {de(PROP['GAP'])} mm</span>
      <span class="small">Die Platte steht auf den Füßen über dem Tisch. Der Tisch steht für die Oberkante der Powerbank. So prüfst du Leiste, Lötstelle und Draht, ohne die Powerbank zu brauchen.</span></div>
    <div><span class="lbl">Aufwand</span><span class="big">≈ 10 g</span>
      <span class="small">Etwa 0,5 h auf deinem Drucker (überschlagen). Die Platte ist {de(2.0)} mm dünner als in Steckprobe 2.</span></div>
  </div>
</section>

<section aria-labelledby="h-fig">
  <h2 id="h-fig">So sieht das Dock aus</h2>
  <div class="card"><h3>Längsschnitt durch die Pin-Reihe</h3><div class="scroll">{schnitt()}</div>
    <p class="small muted">Der Körper (dunkel) hängt mit seiner ganzen Höhe von 2,0 mm unter der flachen Plattenunterseite. Die Lötenden (orange) laufen auf halber Körperhöhe nach links, der Draht (rot) hängt in die Luft. Die senkrechten Pins gehen durch den 0,4 mm dicken Muldenboden in die Buchse im Gebäudefuß. Die Füße stehen vor und hinter dem Schnitt.</p></div>
  <div class="card"><h3>Ansicht der Plattenunterseite (wie im Slicer)</h3><div class="scroll">{unten()}</div>
    <p class="small muted">Die Unterseite ist eben. Die gestrichelte Fläche zeigt, wo der Körper der Leiste aufgeklebt wird; die vier Pin-Löcher sind die einzigen Öffnungen, dazu vier Zapfenlöcher für die Füße.</p></div>
</section>

<section aria-labelledby="h-chain">
  <h2 id="h-chain">Maßkette im Worst-Case</h2>
  <div class="scroll"><table>
    <thead><tr><th>Maß</th><th>Soll</th><th>Worst-Case</th><th>Ergebnis</th><th>Quelle</th></tr></thead>
    <tbody>
    <tr><td>Plattendicke</td><td class="num">Mulde {de(D['F'])} + Muldenboden {de(TP.CEIL_T)} = {de(PLATE_T)}</td><td class="num">Druckmaß ± 0,1</td><td><span class="pill ok">2,0 dünner</span></td><td class="src">bewährt (F, Boden)</td></tr>
    <tr><td>Einstecktiefe E</td><td class="num">{de(D['E'], 2)} (Körper oben liegt an der Platte, z {de(Z_HB)})</td><td class="num">Muldenboden 0,4 bis 0,5: E ≥ 5,18</td><td><span class="pill ok">wie Steckprobe 2</span></td><td class="src">bewährt (r4 S, D)</td></tr>
    <tr><td>Körper der Leiste</td><td class="num">2,0 ganz unter der Platte, aufgeklebt</td><td class="num">Kleber 0,0 bis 0,3 Spalt: E bis 5,28 − 0,3 = 4,98</td><td><span class="pill mid">Kleber dünn halten</span></td><td class="src">bewährt (HDR_BODY), Kleber neu</td></tr>
    <tr><td>Lötenden</td><td class="num">auf halber Körperhöhe, z {de(Z_BM, 2)}, frei</td><td class="num">keine Stufe, kein Spiel nötig</td><td><span class="pill ok">frei</span></td><td class="src">neu</td></tr>
    <tr><td>Draht und Lötstelle</td><td class="num">bis etwa {de(PROP['WIRE_DEPTH'])} unter der Plattenunterseite</td><td class="num">Luft {de(PROP['GAP'])}: 0,6 Reserve; {de(PROP['GAP_TIGHT'])}: Draht liegt auf</td><td><span class="pill mid">Test mit zwei Füßen</span></td><td class="src">S geschätzt, ungemessen</td></tr>
    <tr><td>Gesamthöhe der Platte (hochgerechnet)</td><td class="num">{de(PLATE_T)} + {de(PROP['GAP'])} + Powerbank 12,6 + Boden 1,2 = {de(PLATE_T + PROP['GAP'] + 12.6 + 1.2)}</td><td class="num">Steckprobe 2: 27,0</td><td><span class="pill ok">etwa gleich</span></td><td class="src">A abgeleitet</td></tr>
    <tr><td>Zapfen</td><td class="num">Ø 4,0, Höhe {de(PROP['PIN_H'])}, Loch Ø 4,3, {de(PROP['HOLE_D'])} tief</td><td class="num">Gleitspiel 0,15 (bewährt), 1 mm länger</td><td><span class="pill mid">zu prüfen</span></td><td class="src">E, r4 U: 1,5 wackelte</td></tr>
    </tbody>
  </table></div>
</section>

<section aria-labelledby="h-dec">
  <h2 id="h-dec">Entscheidungen</h2>
  <div class="dec">
    <div class="card rec"><h3><span class="tag">A</span>Halt der Leiste</h3>
      <div class="opts">
        <div class="opt pick"><b>Aufkleben, erst Sekundenkleber, dann Heißkleber (empfohlen)</b><span>Ohne Tasche hält nur der Kleber. Beim Aufstecken schiebt der Druck die Leiste von der Platte weg, deshalb muss er das halten. Der Testbogen fragt beides nacheinander ab.</span></div>
        <div class="opt"><b>Doppelseitiges Klebeband</b><span>Sauber und dünn, aber weich: E könnte beim Aufstecken nachgeben.</span></div>
        <div class="opt"><b>Flache Tasche (0,4 mm) als Ausrichtung</b><span>Gibt Lage und seitlichen Halt, aber wieder Support unter dem Muldenboden. Erst, wenn die Lage der Leiste ein Problem wird.</span></div>
      </div></div>
    <div class="card rec"><h3><span class="tag">B</span>Füße und Luft</h3>
      <div class="opts">
        <div class="opt pick"><b>Zwei Sätze Füße: {de(PROP['GAP'])} und {de(PROP['GAP_TIGHT'])} mm (empfohlen)</b><span>Je vier Füße 6 × 6 mm mit Zapfen 2,5. Du probierst erst {de(PROP['GAP'])}, dann {de(PROP['GAP_TIGHT'])}, und siehst, ab wann der Draht am Tisch aufliegt.</span></div>
        <div class="opt"><b>Nur {de(PROP['GAP'])} mm</b><span>Weniger Teile, aber die untere Grenze der Luft bliebe ungeprüft.</span></div>
      </div></div>
    <div class="card"><h3><span class="tag">C</span>Alles auf gleicher Höhe</h3>
      <div class="opts">
        <div class="opt pick"><b>Keine Tasche, keine Stufe, keine Nische (entschieden)</b><span>Die Leiste liegt flach an der Unterseite. Mehr Luft darunter (Körper 2,0 statt 1,0 sichtbar), dafür 1 mm dünnere Platte und kein Support.</span></div>
      </div></div>
    <div class="card"><h3><span class="tag">D</span>Was nicht zum Test gehört</h3>
      <div class="opts">
        <div class="opt pick"><b>Faden-V und Powerbank-Fach</b><span>Fadenführung macht der andere Chat, das Fach steht in der Fachprobe. Dieses Dock zeigt nur Leiste, Lötenden, Kleber und Zapfen.</span></div>
      </div></div>
  </div>
</section>

<section aria-labelledby="h-risk">
  <h2 id="h-risk">Druck und Risiken</h2>
  <div class="scroll"><table>
    <thead><tr><th>Teil</th><th>Ausrichtung</th><th>Hinweise</th></tr></thead>
    <tbody>
    <tr><td>Mini-Oberplatte</td><td>Unterseite auf dem Bett, Mulde oben</td><td>Kein Support, keine Brücke. Muldenboden = erste zwei Schichten. Die vier Pin-Löcher (Ø 1,4) brauchen am Bett eine Fase von 0,15 gegen den Elefantenfuß (L02). Bettkanten mit Fase 0,5.</td></tr>
    <tr><td>Füße (2 × 4)</td><td>stehend, Zapfen oben</td><td>6 × 6 mm Querschnitt (L06), Zapfen Ø 4,0 × {de(PROP['PIN_H'])}; Satz {de(PROP['GAP'])} mit einer Kerbe, Satz {de(PROP['GAP_TIGHT'])} mit zwei.</td></tr>
    <tr><td>Gebäude, Kassette</td><td>aus Steckprobe 2</td><td>unverändert wiederverwenden, kein Neudruck.</td></tr>
    </tbody>
  </table></div>
  <p class="small muted">Hauptrisiko: die Leiste lässt sich beim zehnmaligen Aufstecken und Abziehen vom Kleber lösen. Berücksichtigte Lehren: L02 Lochmündungen, L05 keine Brücke (hier gar keine Hohlräume), L06 keine freistehenden Stifte, L07 Druckausrichtung je Teil, L08 ungemessene Werte markiert, L24 nur fühlbare oder ja/nein-Felder, L25 Variante und ZIP-Version im Ergebnistext, L27 neue Werte nur in <code>plug/power/params.py</code>.</p>
</section>

<section aria-labelledby="h-test">
  <h2 id="h-test">Was der Testbogen danach abfragt</h2>
  <ul>
    <li>Platte ansehen: Muldenboden glatt, vier Pin-Löcher offen (Fase gewirkt)?</li>
    <li>Leiste mit Sekundenkleber an die flache Unterseite kleben, Pins durch die Löcher: liegt sie flach, sitzt sie gerade?</li>
    <li>Gebäude aufstecken und abziehen, zehn Mal: hält der Kleber? Dann dasselbe mit Heißkleber.</li>
    <li>Draht anlöten und die Platte auf die Füße {de(PROP['GAP'])} und dann {de(PROP['GAP_TIGHT'])} setzen: hängt etwas am Tisch an?</li>
    <li>Zapfen in den Löchern: Sitz 1 bis 5.</li>
    <li>Durchgang für alle vier Pins mit dem Multimeter.</li>
  </ul>
</section>

<section>
  <h2>Nächster Schritt</h2>
  <p>Wenn dir die Empfehlung passt (A: aufkleben, B: zwei Füße-Sätze, C: alles auf gleicher Höhe), baue ich STL, README, ZIP, Prüfbericht und den Testbogen. Sonst nenne mir die Änderungen.</p>
</section>
</div>
"""
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(head + body)
    print("geschrieben: %s (%d kB)" % (os.path.relpath(OUT), os.path.getsize(OUT) // 1024))


if __name__ == "__main__":
    page()
