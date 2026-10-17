#!/usr/bin/env python3
"""Plan 4 Display-Gebäude: Entwurf nach der Modulprobe (2026-10-17): robustere Aufnahme (Kappe statt dünner Decke) und Zapfen mit langer Verjüngung.
Nur Entwurf, keine STL.   python3 -m plug.display.build_plan4  ->  plug/display/plan4.html"""
import os

from plug.display import params as D
from plug.display.build_plan import CONCEPT_TEMPLATE, CSS_EXTRA
from plug.display.build_plan3 import CSS3

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "plan4.html")
de = lambda x, n=1: ("%.*f" % (n, x)).replace(".", ",")
P = D.DISP

CSS4 = """
.p4 { display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 280px)); gap: 14px; }
.p4 figure { margin: 0; display: flex; flex-direction: column; gap: 6px; min-width: 0; }
.p4 figcaption { font-size: .85rem; color: var(--muted); }
.p4 figcaption b { color: var(--fg); }
.fig .sup { fill: none; stroke: var(--accent); stroke-width: 1; stroke-dasharray: 3 2; }
.fig .holeL { stroke: var(--edge); stroke-width: 1.2; fill: none; }
.fig .holeE { stroke: var(--accent); stroke-width: 1; stroke-dasharray: 3 2; fill: none; }
.fig .peg4 { fill: var(--c-cut2); stroke: var(--edge); stroke-width: .8; fill-opacity: .9; }
.p4 svg { height: auto; min-width: 0 !important; width: 100% !important; max-width: 280px !important; } .p4 svg text { font-size: 11px; fill: var(--fg); }
"""


def svg(w, h, body, label):
    return f'<svg class="fig" viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="{label}" style="max-width:{w}px;overflow:hidden">{body}</svg>'


def head_section(kind):
    """Schnitt durch den Kopf, oberer Ausschnitt, Rückseite links, Front rechts (mm, 14 px je mm). z 0 = Oberkante."""
    s = 14
    X = lambda x: 20 + x * s
    Z = lambda z: 20 + z * s
    rear, pocket, bl = 3.6, 5.1, 1.2
    xr, xf = rear, rear + pocket        # Taschenrückwand, Taschenfront
    roof = 1.2 if kind in ("ist", "rampe", "liegt") else 0
    lip = 1.6
    o = []
    top = 0.0
    if kind == "kappe":
        top = lip
    # Rückwand
    o.append(f'<rect class="foot" x="{X(0)}" y="{Z(top)}" width="{rear * s}" height="{(12 - top) * s}"/>')
    # Seitenschnitt: Tasche unten Boden
    o.append(f'<rect class="foot" x="{X(0)}" y="{Z(12)}" width="{(xf) * s}" height="{1.4 * s}"/>')
    if kind == "ist":
        o.append(f'<rect class="foot" x="{X(0)}" y="{Z(0)}" width="{xf * s}" height="{roof * s}"/>')
        o.append(f'<rect class="sup" x="{X(xr)}" y="{Z(roof)}" width="{pocket * s}" height="{1.6 * s}"/>')
    if kind == "rampe":
        o.append(f'<polygon class="foot" points="{X(xr)},{Z(0)} {X(xf)},{Z(0)} {X(xf)},{Z(5.1 + roof)} {X(xr)},{Z(roof)}"/>'.replace(f"{X(xf)},{Z(5.1 + roof)}", f"{X(xf)},{Z(roof)}"))
        o.append(f'<polygon class="foot" points="{X(0)},{Z(0)} {X(xr)},{Z(0)} {X(xr)},{Z(roof)} {X(0)},{Z(roof)}"/>')
        # Dach liegt über der Rampe: Dreieck Hohlraum
        o.append(f'<polygon class="void2" points="{X(xr)},{Z(roof)} {X(xf)},{Z(roof)} {X(xf)},{Z(roof + 5.1)}"/>')
    if kind == "kappe":
        o.append(f'<rect class="blende" x="{X(xf)}" y="{Z(0)}" width="{bl * s}" height="{13.4 * s}"/>')
        o.append(f'<rect class="blende" x="{X(0.8)}" y="{Z(0)}" width="{(xf - 0.8) * s}" height="{lip * s}"/>')
    else:
        o.append(f'<rect class="blende" x="{X(xf)}" y="{Z(0)}" width="{bl * s}" height="{13.4 * s}"/>')
    # Modul
    mt = 0.3 + roof if kind != "kappe" else lip + 0.3
    o.append(f'<rect class="pcb" x="{X(xr + 0.3)}" y="{Z(mt)}" width="{4.5 * s * 0.55}" height="{(12 - mt) * s}"/>')
    names = dict(ist="so gedruckt", kappe="Kappe (empfohlen)", rampe="Rampe 45°", liegt="liegend")
    o.append(f'<text x="{X(0)}" y="{Z(13.4) + 16}">{names[kind]}</text>')
    return svg(280, 250, "".join(o), "Schnitt durch den Kopf, " + names[kind])


def peg(kind):
    """Zapfen im Sackloch, Spitze links, 40 px je mm. hole = Soll, gedruckt etwa 0,12 kleiner (waagerechtes Loch)."""
    s = 30
    cy = 55
    L, entry = 4.4, 2.6
    spec = dict(ist=(2.4, 2.4, 0.4, 2.5, 1.6), p1=(1.8, 2.4, 2.2, 2.6, None), p2=(1.8, 2.5, 2.2, 2.6, None), p3=(1.6, 2.4, 2.4, 2.6, "ribs"))[kind]
    r0, r1, lt, hole, ex = spec
    r0, r1 = r0 / 2, r1 / 2
    if kind == "ist":
        r0 = r1 - 0.4
    x0 = 0.2
    X = lambda x: 20 + x * s
    pts = [(x0, r0), (x0 + lt, r1), (L, r1)]
    poly = [(X(x), cy - r * s) for x, r in pts] + [(X(x), cy + r * s) for x, r in reversed(pts)]
    o = [f'<polygon class="peg4" points="{" ".join("%.1f,%.1f" % q for q in poly)}"/>']
    if ex == "ribs":
        for a in (-1, 1):
            o.append(f'<rect x="{X(1.4)}" y="{cy + (a * (r1 + 0.1) - 0.1) * s - (0 if a > 0 else 0.0)}" width="{1.8 * s}" height="{0.2 * s}" class="peg4"/>')
    h = hole / 2
    for a in (-1, 1):
        o.append(f'<line class="holeL" x1="{X(0)}" x2="{X(entry)}" y1="{cy + a * h * s}" y2="{cy + a * h * s}"/>')
        o.append(f'<line class="holeE" x1="{X(0)}" x2="{X(entry)}" y1="{cy + a * (h - 0.12) * s}" y2="{cy + a * (h - 0.12) * s}"/>')
    o.append(f'<line class="holeL" x1="{X(0)}" x2="{X(0)}" y1="{cy - h * s}" y2="{cy + h * s}"/>')
    o.append(f'<text x="{X(0)}" y="{cy + h * s + 26}">Loch Ø {de(hole, 2)}</text>')
    return svg(180, 120, "".join(o), "Zapfen " + kind)


def page():
    head = open(CONCEPT_TEMPLATE, encoding="utf-8").read().split('<div class="wrap">')[0]
    head = head.replace("<title>Powerbank in der Grundplatte</title>", "<title>Plan 4 Display-Aufnahme und Zapfen</title>\n<meta name=\"description\" content=\"Entwurf nach der Modulprobe: Kappe statt dünner Decke, Zapfen mit langer Verjüngung\">")
    head = head.replace("</style>", CSS_EXTRA + CSS3 + CSS4 + "</style>")
    pocket_h = P["pcb_h"] + D.CLR
    html = f"""<div class="wrap">
<header>
  <div class="kicker">Steckmechanismus · Display-Gebäude · Plan 4, Entwurf, noch keine STL</div>
  <h1>Aufnahme und Zapfen nach der Modulprobe</h1>
  <p class="lead">Das Modul passt mit 0,4 mm Luft, die Tasche sitzt. Zwei Dinge sind noch zu lösen: Die dünne Decke über dem Modul löst sich beim Druck vom Support, und die Zapfen kommen nur etwa 0,5 mm ins Sackloch. Hier steht, was ich ändern würde, mit Zeichnungen und einer Testlehre, bevor der Körper neu entsteht.</p>
</header>

<section>
  <h2>Maße nach deiner Rückmeldung</h2>
  <div class="scroll"><table>
    <thead><tr><th>Maß</th><th>Modulprobe</th><th>Neu</th><th>Grund</th></tr></thead>
    <tbody>
      <tr><td>Luft in der Breite je Seite</td><td class="num">0,40</td><td class="num">{de(D.CLR_W, 2)}</td><td>Nutzer: horizontal minimal zu viel Spiel</td></tr>
      <tr><td>Modulhöhe (Annahme)</td><td class="num">34,05</td><td class="num">{de(P['pcb_h'], 2)}</td><td>Nutzer: 33,8 reicht vermutlich</td></tr>
      <tr><td>Taschenhöhe (0,3 Luft oben)</td><td class="num">34,35</td><td class="num">{de(pocket_h, 2)}</td><td>folgt aus der Modulhöhe</td></tr>
      <tr><td>Taschenbreite</td><td class="num">36,10</td><td class="num">{de(P['pcb_w'] + 2 * D.CLR_W, 2)}</td><td>35,3 plus 2 × {de(D.CLR_W, 2)}</td></tr>
    </tbody></table></div>
</section>

<section>
  <h2>Aufnahme robuster: die Decke weglassen</h2>
  <p>Die Decke über der Tasche ist nur 1,2 mm dick und überbrückt 5,1 mm nach vorn ins Leere. Der Support klebt daran, beim Lösen verzieht sie sich. Vier Wege:</p>
  <div class="p4">
    <figure>{head_section('ist')}<figcaption><b>So gedruckt.</b> Decke 1,2 dünn, Support in der Tasche.</figcaption></figure>
    <figure>{head_section('kappe')}<figcaption><b>A Kappe.</b> Die Aufnahme ist oben offen, die Blende bekommt eine Lippe 1,6 × 5,1 mm als Dach. Kein Support, nichts Dünnes über Luft.</figcaption></figure>
    <figure>{head_section('rampe')}<figcaption><b>B Rampe.</b> Dach mit 45° nach vorn ansteigend, trägt sich selbst. Der Kopf wird etwa 5 mm höher.</figcaption></figure>
    <figure>{head_section('liegt')}<figcaption><b>C Liegend drucken.</b> Rückseite auf dem Bett, kein Support. Die Sacklöcher werden dann senkrecht gedruckt und fallen anders aus als im Körper.</figcaption></figure>
  </div>
  <p class="small muted">Empfehlung A. Die Lippe liegt auf den Seitenwänden, Zapfen und Blende halten sie, im Notfall ein Tropfen Kleber. Mit A entfällt der Support im Körper ganz, die Blende bleibt flach druckbar (Lippe steht als Rippe nach oben).</p>
</section>

<section>
  <h2>Zapfen: lange, flache Verjüngung</h2>
  <p>Was du gefühlt hast, passt zur Zeichnung: Die Fase war nur 0,4 mm lang. Danach steht der volle Durchmesser im Loch, das waagerecht gedruckt etwa 0,1 mm enger ausfällt als gezeichnet. Dicke Zapfen (Ø 2,5) im Loch Ø 2,5 hatten deshalb keine Chance. Die Kraft muss sich über viele Lagen aufbauen und erst am Ende ihren Höchstwert erreichen.</p>
  <div class="p4">
    <figure>{peg('ist')}<figcaption><b>So gedruckt.</b> Ø 2,4, Fase 0,4, Loch Ø 2,5: Klemmen nach 0,5 mm.</figcaption></figure>
    <figure>{peg('p1')}<figcaption><b>P1 (empfohlen).</b> Spitze Ø 1,8, Kegel über 2,2 mm (11 Lagen, 0,03 mm je Lage) auf Ø 2,4, Loch Ø 2,6. Kraft erst auf den letzten Millimetern.</figcaption></figure>
    <figure>{peg('p2')}<figcaption><b>P2 fester.</b> Wie P1, Kegel endet bei Ø 2,5. Greift stärker, wenn P1 zu locker ist.</figcaption></figure>
    <figure>{peg('p3')}<figcaption><b>P3 Quetschrippen.</b> Kernzapfen Ø 2,4 mit zwei 0,2 mm hohen Rippen. Die Rippen geben nach, das Loch muss nicht auf 0,05 stimmen. Aufwendiger zu drucken.</figcaption></figure>
  </div>
  <p class="small muted">Schwarz: Loch wie gezeichnet, orange gestrichelt: so klein fällt es waagerecht gedruckt etwa aus (Schätzung, 0,12 weniger).</p>
  <p>Das Loch bekommt wieder eine Einführfase von 0,3 mm und bleibt 2,6 tief; der Zapfen reicht 2,4 hinein.</p>
</section>

<section>
  <h2>Zapfenlehre statt gleich der ganzen Aufnahme</h2>
  <p>Damit der nächste Druck sitzt, schlage ich eine kleine Lehre vor (etwa 15 min), gedruckt in der Lage wie der Körper (Löcher waagerecht): ein Block mit fünf Sacklöchern Ø 2,50 / 2,55 / 2,60 / 2,65 / 2,70, 2,6 tief, und eine Leiste mit drei Zapfen nach P1 mit Enddurchmesser 2,3 / 2,4 / 2,5. Du probierst jeden Zapfen in jedem Loch und meldest, welche Paarung am Ende Druck braucht, aber nicht klemmt. Danach stehen Loch und Zapfen fest.</p>
</section>

<section>
  <h2>Entscheidungen</h2>
  <div class="dec">
    <div class="card rec"><h3><span class="tag">M</span> Decke über dem Modul</h3><div class="opts">
      <div class="opt pick"><b>A Kappe an der Blende</b><span class="num2">kein Support, robust. Empfohlen.</span></div>
      <div class="opt"><b>B Rampe 45°</b><span class="num2">Kopf 5 mm höher.</span></div>
      <div class="opt"><b>C liegend drucken</b><span class="num2">nur für die Probe, Löcher anders.</span></div></div></div>
    <div class="card rec"><h3><span class="tag">N</span> Zapfenform</h3><div class="opts">
      <div class="opt pick"><b>P1 lange Verjüngung</b><span class="num2">erst Lehre, dann übernehmen. Empfohlen.</span></div>
      <div class="opt"><b>P2 Kegel bis Ø 2,5</b><span class="num2">falls P1 zu locker.</span></div>
      <div class="opt"><b>P3 Quetschrippen</b><span class="num2">unempfindlich gegen Lochmaß.</span></div></div></div>
    <div class="card"><h3><span class="tag">O</span> Reihenfolge</h3><div class="opts">
      <div class="opt pick"><b>Lehre, dann Aufnahme mit Kappe</b><span class="num2">Lehre und Aufnahme-Probe zusammen drucken, 25 min.</span></div>
      <div class="opt"><b>Gleich der ganze Körper mit integrierter Kassette</b><span class="num2">schneller, aber Zapfenmaß ungeprüft.</span></div></div></div>
  </div>
</section>
</div>
"""
    return head + html


if __name__ == "__main__":
    h = page()
    open(OUT, "w", encoding="utf-8").write(h)
    print("geschrieben:", OUT, "%.0f KB" % (len(h) / 1024))
