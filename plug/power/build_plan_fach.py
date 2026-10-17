#!/usr/bin/env python3
"""Plan Fachprobe Powerbank als HTML mit Zeichnungen: plug/power/plan_fach.html.

Gleiche Seitenform wie die Konzeptseite (CSS aus plug/power/concept.template.html). Die Zeichnungen entstehen aus der Fach-Geometrie in
plug/power/build_concept.py und plug/power/fachprobe.py. Nach Regel 2 im Logbuch gibt es erst nach dem Abnicken STL.
    python3 -m plug.power.build_plan_fach
"""
import os

from plug.power import build_concept as BC
from plug.power import fachprobe as FA
from plug.power import params as PP

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "plan_fach.html")
de = lambda x, n=1: ("%.*f" % (n, x)).replace(".", ",")
S = 5.6                                          # Pixel je mm


class Svg:
    def __init__(self, x0, y0, x1, y1, pad=14):
        self.x0, self.y1, self.pad, self.y0f = x0, y1, pad, y0
        self.w, self.h = (x1 - x0) * S + 2 * pad, (y1 - y0) * S + 2 * pad
        self.o = []

    def X(self, u):
        return self.pad + (u - self.x0) * S

    def Y(self, v):                              # v nach unten
        return self.pad + (v - self.y0f) * S

    def rect(self, u0, v0, u1, v1, cls, extra=""):
        self.o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" class="%s" %s/>' % (
            self.X(u0), self.Y(v0), (u1 - u0) * S, (v1 - v0) * S, cls, extra))

    def poly(self, pts, cls):
        self.o.append('<polygon points="%s" class="%s"/>' % (" ".join("%.1f,%.1f" % (self.X(u), self.Y(v)) for u, v in pts), cls))

    def line(self, u0, v0, u1, v1, cls):
        self.o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="%s"/>' % (self.X(u0), self.Y(v0), self.X(u1), self.Y(v1), cls))

    def text(self, u, v, s, cls="", anchor="start", dy=0):
        self.o.append('<text x="%.1f" y="%.1f" class="%s" text-anchor="%s">%s</text>' % (self.X(u), self.Y(v) + dy, cls, anchor, s))

    def svg(self, ident, label):
        return '<svg id="%s" viewBox="0 0 %.0f %.0f" role="img" aria-label="%s" class="fig">%s</svg>' % (ident, self.w, self.h, label, "".join(self.o))


def draufsicht():
    u_min, u_max = BC.U0 - FA.WALL - 14, BC.U1 + FA.WALL + 16
    v_min, v_max = BC.V0 - FA.WALL - 4, BC.V1 + FA.WALL + 10
    g = Svg(u_min, v_min, u_max, v_max)
    ub, _ = FA.region("B")
    # Außenform A (gestrichelt) und B (voll)
    for var, cls in (("A", "pa"), ("B", "pb")):
        x0, y0, x1, y1 = FA.outer(var).bounds
        g.rect(x0, y0, x1, y1, "wall " + cls)
    g.rect(BC.U0, BC.V0, BC.U1, BC.V1, "air")
    g.rect(BC.U0, BC.V0, ub, BC.V1, "air b")
    # Kabelkanal
    g.rect(BC.BU0 - PP.PB_CLR, BC.KV0, BC.U1, BC.V1, "chan")
    # Powerbank (A voll, B bis ub)
    g.rect(BC.BU0, BC.BV0, BC.BU0 + PP.PB_L, BC.BV0 + PP.PB_W, "pbk")
    g.rect(BC.BU0, BC.BV0, ub, BC.BV0 + PP.PB_W, "pbk b")
    # Zaun
    fence = BC.fach_parts(BC.Frame(0, 0, 0, 1))["fence"]
    for p in (fence.geoms if hasattr(fence, "geoms") else [fence]):
        g.poly(list(p.exterior.coords), "fence")
    # Fenster in der Vorderwand
    g.rect(BC.U0 - FA.WALL, BC.WIN[0], BC.U0, BC.WIN[1], "win")
    # Steckerraum: USB-A Stecker
    ua = BC.BVC + PP.PB_PORT_V["usb_a"]
    plug_end = BC.BU0 - 25.0
    g.rect(plug_end, ua - 7.5, BC.BU0, ua + 7.5, "plug")
    # Anschlüsse an der Stirnseite der Powerbank
    for key, lab in (("leds", "LEDs"), ("micro", "micro-USB"), ("usb_c", "USB-C"), ("usb_a", "USB-A")):
        v = BC.BVC + PP.PB_PORT_V[key]
        hw = BC.PORT_HALF[key]
        g.rect(BC.BU0, v - hw, BC.BU0 + 2.2, v + hw, "port")
    # Beschriftungen
    for key, lab in (("leds", "LEDs"), ("micro", "micro-USB"), ("usb_c", "USB-C")):
        v = BC.BVC + PP.PB_PORT_V[key]
        g.text(BC.BU0 + 3.5, v, lab, "lab", dy=4)
    g.text(BC.BU0 + 3.5, BC.BVC + PP.PB_PORT_V["usb_a"], "USB-A (Stecker liegt im Steckerraum)", "lab", dy=4)
    g.text(plug_end + 1.0, ua, "Stecker 25 mm", "lab mut", dy=4)
    g.text(BC.U0 - FA.WALL - 1.0, BC.WIN[1] + 4.0, "Fenster", "lab", "end", dy=4)
    g.text((BC.U0 + BC.BU0) / 2, BC.V1 + FA.WALL + 7.0, "Steckerraum %s mm" % de(PP.PB_PLUG, 0), "lab mut", "middle", dy=0)
    g.text(BC.BU0 + 24, 0, "Powerbank %s × %s mm" % (de(PP.PB_L, 0), de(PP.PB_W, 0)), "lab bold", "start", dy=4)
    g.text(ub + 1.5, BC.V1 + FA.WALL + 7.0, "Variante B endet hier, die Powerbank ragt heraus", "lab mut", "start", dy=0)
    g.line(ub, BC.V0 - FA.WALL - 1.5, ub, BC.V1 + FA.WALL + 1.5, "cut")
    g.text(BC.U1 + 1.0, BC.KV0 + 3, "Kabelkanal", "lab mut", "end", dy=4)
    # Maßlinien
    yb = BC.V0 - FA.WALL - 2.6
    g.line(BC.U0 - FA.WALL, yb, ub, yb, "dim")
    g.text((BC.U0 - FA.WALL + ub) / 2, yb, "B: %s mm" % de(FA.sizes("B")[0], 1), "lab", "middle", dy=-3)
    g.line(BC.U0 - FA.WALL, yb - 0, BC.U1 + FA.WALL, yb - 0, "dim a")
    g.text(BC.U1 + FA.WALL, yb, "A: %s mm" % de(FA.sizes("A")[0], 1), "lab mut", "end", dy=13)
    xr = BC.U1 + FA.WALL + 3.2
    g.line(xr, BC.V0 - FA.WALL, xr, BC.V1 + FA.WALL, "dim")
    g.text(xr + 1.0, 0, "%s mm" % de(FA.sizes("A")[1], 1), "lab", "start", dy=4)
    return g.svg("plan", "Draufsicht auf Fach, Powerbank, Fenster und Steckerraum")


def schnitt():
    """Längsschnitt in der Mitte des Fachs: u nach rechts, z nach oben."""
    u0, u1 = BC.U0 - FA.WALL - 2, BC.BU0 + 40
    zmax = FA.TOP + FA.PLATE_T + 4
    H = zmax
    S2 = 7.0
    pad = 16
    w = (u1 - u0) * S2 + 2 * pad
    h = H * S2 + 2 * pad + 18
    X = lambda u: pad + (u - u0) * S2
    Z = lambda z: pad + (H - z) * S2
    o = []
    def r(a0, z0, a1, z1, cls):
        o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" class="%s"/>' % (X(a0), Z(z1), (a1 - a0) * S2, (z1 - z0) * S2, cls))
    def t(a, z, s, cls="lab", anchor="start", dy=0):
        o.append('<text x="%.1f" y="%.1f" class="%s" text-anchor="%s">%s</text>' % (X(a), Z(z) + dy, cls, anchor, s))
    def ln(a0, z0, a1, z1, cls):
        o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" class="%s"/>' % (X(a0), Z(z0), X(a1), Z(z1), cls))
    pb0 = BC.BU0
    # Boden und Deckplatte
    r(BC.U0 - FA.WALL, 0, u1, FA.ZF, "wall")
    r(BC.U0 - FA.WALL, FA.TOP, u1, FA.TOP + FA.PLATE_T, "lid")
    # Powerbank
    pz0, pz1 = FA.ZF, FA.ZF + PP.PB_T
    r(pb0, pz0, pb0 + 40, pz1, "pbk")
    # Maße
    dx = pb0 + 41.5
    ln(dx, 0, dx, FA.TOP, "dim")
    t(dx + 1.2, FA.TOP / 2, "%s mm" % de(FA.TOP), "lab", dy=4)
    ln(pb0 + 30, pz1, pb0 + 30, FA.TOP, "dimn")
    t(pb0 + 31, FA.TOP + 0.2, "Luft %s mm" % de(PP.PB_CLR_Z), "lab ok", dy=-18)
    t(pb0 + 20, (pz0 + pz1) / 2, "Powerbank %s mm" % de(PP.PB_T), "lab", "middle", dy=4)
    t(pb0 + 20, -0.4, "Boden %s mm" % de(FA.ZF), "lab mut", "middle", dy=10)
    t(pb0 + 20, FA.TOP + 1.0, "Deckplatte %s mm" % de(FA.PLATE_T, 0), "lab", "middle", dy=4)
    t(BC.U0 - FA.WALL, FA.TOP - 2.2, "Fenster: hier fehlt im Schnitt die Vorderwand", "lab mut", "start", dy=0)
    t(BC.U0 - FA.WALL + 4, FA.ZF + 6.0, "Steckerraum %s mm: Stecker und Kabel" % de(PP.PB_PLUG, 0), "lab", "start", dy=4)
    return '<svg id="sect" viewBox="0 0 %.0f %.0f" role="img" aria-label="Längsschnitt durch Steckerraum und Powerbank" class="fig">%s</svg>' % (w, h, "".join(o))


CSS_EXTRA = """
.fig { width: 100%; height: auto; display: block; min-width: 640px; }
.fig text, .fig .lab { font-family: var(--font); font-size: 12px; fill: var(--fg); }
.fig .mut { fill: var(--muted); }
#sect .lab { font-size: 7.6px; }
#plan .lab { font-size: 10.6px; } .fig .bold { font-weight: 700; } .fig .ok { fill: var(--ok); font-weight: 600; }
.fig .inv { fill: var(--panel); }
.fig .wall { fill: var(--c-under); stroke: var(--edge); stroke-width: .8; }
.fig .wall.pa { fill: color-mix(in srgb, var(--c-under) 40%, transparent); stroke-dasharray: 5 4; }
.fig .air { fill: var(--panel); stroke: none; }
.fig .air.b { fill: var(--panel); }
.fig .chan { fill: color-mix(in srgb, var(--line) 65%, var(--panel)); stroke: none; }
.fig .pbk { fill: var(--c-pb); stroke: var(--edge); stroke-width: 1; }
.fig .pbk.b { fill: var(--c-pb); }
.fig .fence { fill: var(--c-plate); stroke: var(--edge); stroke-width: .6; }
.fig .rail { fill: var(--c-plate); stroke: var(--edge); stroke-width: .6; }
.fig .win { fill: color-mix(in srgb, var(--c-niche) 35%, var(--panel)); stroke: var(--c-niche); stroke-width: 1; stroke-dasharray: 3 2; }
.fig .plug { fill: color-mix(in srgb, var(--c-port) 18%, transparent); stroke: var(--c-port); stroke-width: 1; }
.fig .port { fill: var(--c-port); stroke: none; }
.fig .cut { stroke: var(--warn); stroke-width: 1.2; stroke-dasharray: 5 3; }
.fig .dim { stroke: var(--fg); stroke-width: 1; fill: none; } .fig .dim.a { stroke: var(--muted); stroke-dasharray: 4 3; }
.fig .dimn { stroke: var(--ok); stroke-width: 1.6; }
.fig .lid { fill: var(--c-plate); stroke: var(--edge); stroke-width: .8; }
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
    head = head.replace("<title>Powerbank in der Grundplatte</title>", "<title>Plan Fachprobe Powerbank</title>")
    head = head.replace("</style>", CSS_EXTRA + "</style>")
    mA, mB = FA.masses("A"), FA.masses("B")
    gA, gB = sum(mA.values()), sum(mB.values())
    tA, tB = gA / 47.0 * 2.5, gB / 47.0 * 2.5
    sA, sB = FA.sizes("A"), FA.sizes("B")
    h_ok = FA.TOP - FA.ZF - 13.0
    body = f"""<div class="wrap">
<header>
  <div class="kicker">Steckmechanismus · Fachprobe Powerbank · Plan, noch nicht abgenickt</div>
  <h1>Fachprobe Powerbank</h1>
  <p class="lead">Ein kleiner Ausschnitt des Unterkastens zeigt, ob die echte Powerbank mit Fenster, Stecker und Kabel so ins Fach passt, wie das Konzept es annimmt. Alle Maße der Powerbank sind bisher Datenblatt oder Schätzung. Erst nach deinem Okay entstehen STL.</p>
</header>

<section aria-labelledby="h-ans">
  <h2 id="h-ans">Empfehlung</h2>
  <div class="answer">
    <div class="rec"><span class="lbl">Umfang</span><span class="big">Variante B</span>
      <span class="small">Nur das Anschlussende des Fachs, <span class="num">{de(sB[0])} × {de(sB[1])} × {de(FA.TOP)} mm</span>. Die Powerbank steckt {de(FA.LB, 0)} mm tief im Fach, der Rest ragt hinten heraus. Das reicht für Fenster, Stecker, Kabel und die Luft nach oben. Die Länge von 90 mm prüfst du am Gerät mit dem Lineal.</span></div>
    <div><span class="lbl">Teile</span><span class="big">2 Stück</span>
      <span class="small">Fach (Unterkasten-Ausschnitt) und Deckplatte 2 mm. Keine Schablone (entschieden).</span></div>
    <div><span class="lbl">Aufwand</span><span class="big">≈ {de(gB, 0)} g</span>
      <span class="small">Etwa {de(tB + 0.2)} h auf deinem Drucker. Variante A (ganzes Fach, <span class="num">{de(sA[0])} × {de(sA[1])} mm</span>) wären ≈ {de(gA, 0)} g und {de(tA + 0.2)} h.</span></div>
    <div><span class="lbl">Du brauchst</span><span class="big">Powerbank + Kabel</span>
      <span class="small">Die Intenso XS5000 und das USB-A-Kabel mit geradem Stecker, das später dranhängt. Messen musst du nichts; alles wird gefühlt oder mit ja/nein beantwortet.</span></div>
  </div>
</section>

<section aria-labelledby="h-fig">
  <h2 id="h-fig">So sieht die Probe aus</h2>
  <div class="card">
    <h3>Draufsicht (Deckplatte abgenommen)</h3>
    <div class="scroll">{draufsicht()}</div>
    <p class="small muted">Dunkel: Wände und Zaun des Unterkastens. Orange gestrichelt: Fenster in der Vorderwand. Gestrichelt: Variante A, die um den hinteren Teil des Fachs länger wäre.</p>
  </div>
  <div class="card">
    <h3>Längsschnitt durch Steckerraum und Powerbank</h3>
    <div class="scroll">{schnitt()}</div>
    <p class="small muted">Die Deckplatte steht für die Oberplatte. Das Fenster in der Vorderwand ist oben offen und wird von ihr geschlossen.</p>
  </div>
</section>

<section aria-labelledby="h-chain">
  <h2 id="h-chain">Maßkette im Worst-Case</h2>
  <div class="scroll"><table>
    <thead><tr><th>Maß</th><th>Soll</th><th>Worst-Case</th><th>Ergebnis</th><th>Quelle</th></tr></thead>
    <tbody>
    <tr><td>Höhe im Fach</td><td class="num">Boden {de(FA.ZF)} + Powerbank {de(PP.PB_T)} + Luft {de(PP.PB_CLR_Z)} = {de(FA.TOP)}</td><td class="num">Powerbank 13,0 (Anleitung rundet auf 13): Luft {de(h_ok)}</td><td><span class="pill ok">bleibt Luft</span></td><td class="src">B Datenblatt, ungemessen</td></tr>
    <tr><td>Breite im Fach</td><td class="num">{de(PP.PB_W, 0)} + 2 × {de(PP.PB_CLR)} = {de(PP.PB_W + 2 * PP.PB_CLR, 0)}</td><td class="num">63,5 + Druckabweichung 0,2: 0,15 je Seite</td><td><span class="pill ok">passt</span></td><td class="src">B Datenblatt, ungemessen</td></tr>
    <tr><td>Fenster</td><td class="num">v {de(BC.WIN[0])} bis {de(BC.WIN[1])} ab Mitte, 2 mm Zugabe</td><td class="num">Lage der Anschlüsse ± 2 mm</td><td><span class="pill mid">knapp</span></td><td class="src">S geschätzt</td></tr>
    <tr><td>Steckerraum</td><td class="num">{de(PP.PB_PLUG, 0)} mm</td><td class="num">gerader USB-A-Stecker 25 mm + Biegung</td><td><span class="pill mid">offen</span></td><td class="src">S geschätzt</td></tr>
    </tbody>
  </table></div>
</section>

<section aria-labelledby="h-dec">
  <h2 id="h-dec">Entscheidungen</h2>
  <div class="dec">
    <div class="card rec"><h3><span class="tag">A</span>Umfang der Probe</h3>
      <div class="opts">
        <div class="opt pick"><b>B: Anschlussende (empfohlen)</b><span class="num">{de(sB[0])} × {de(sB[1])} mm, ≈ {de(gB, 0)} g</span><span>Prüft alles, was geschätzt ist. Die Powerbank ragt hinten heraus.</span></div>
        <div class="opt"><b>A: ganzes Fach</b><span class="num">{de(sA[0])} × {de(sA[1])} mm, ≈ {de(gA, 0)} g</span><span>Zusätzlich Länge, Zaun hinten, Kabelkanal bis zum Ende. Doppelt so viel Material.</span></div>
      </div></div>
    <div class="card"><h3><span class="tag">B</span>Messschablone</h3>
      <div class="opts">
        <div class="opt pick"><b>Entfällt (entschieden)</b><span>Das Fach muss nur zusammenpassen und gut sitzen; Anschlusslagen müssen nicht abgelesen werden.</span></div>
      </div></div>
    <div class="card"><h3><span class="tag">C</span>Taste der Powerbank</h3>
      <div class="opts">
        <div class="opt pick"><b>Entfällt (entschieden)</b><span>Der Mikrocontroller zieht alle 5 s kurz Strom, damit die Powerbank anbleibt. Das Fenster bleibt über LEDs, micro-USB und USB-C.</span></div>
      </div></div>
    <div class="card"><h3><span class="tag">D</span>Deckplatte</h3>
      <div class="opts">
        <div class="opt pick"><b>Volle Platte 2 mm</b><span class="num">≈ {de(mB['lid'], 0)} g</span><span>Zeigt die Luft über der Powerbank und schließt das Fenster nach oben.</span></div>
        <div class="opt"><b>Nur ein Streifen über Fenster und Steckerraum</b><span class="num">≈ 3 g</span><span>Spart Material, zeigt die Luft über der Powerbank nur am Anschlussende.</span></div>
      </div></div>
  </div>
</section>

<section aria-labelledby="h-risk">
  <h2 id="h-risk">Druck und Risiken</h2>
  <div class="scroll"><table>
    <thead><tr><th>Teil</th><th>Ausrichtung</th><th>Hinweise</th></tr></thead>
    <tbody>
    <tr><td>Fach</td><td>Boden auf dem Bett, offen nach oben, Fenster oben offen</td><td>Keine Brücke. Bettkanten mit Fase {de(PP.CH_BED)}. Der Zaun {de(PP.FENCE[0])} × {de(PP.FENCE[1], 0)} ist eine lange Wand auf dem Boden, kein freistehender Stift (L06).</td></tr>
    <tr><td>Deckplatte</td><td>flach</td><td>Fase {de(PP.CH_BED)} am Bett. Keine Löcher.</td></tr>
    </tbody>
  </table></div>
  <p class="small muted">Berücksichtigte Lehren: L04 keine Brücke, L06 keine freistehenden Stifte, L07 Druckausrichtung je Teil, L08 ungemessene Werte sind markiert, L24 nur fühlbare oder ja/nein-Felder, L25 die Variante steht im Ergebnistext, L27 neue Werte nur in <code>plug/power/params.py</code>.</p>
</section>

<section aria-labelledby="h-test">
  <h2 id="h-test">Was der Testbogen danach abfragt</h2>
  <ul>
    <li>Powerbank ins Fach legen: sitzt sie ohne Zwang, wackelt sie, schleift sie am Zaun?</li>
    <li>Deckplatte auflegen: liegt sie flach, berührt sie die Powerbank?</li>
    <li>Fenster: sind die LEDs sichtbar, kommst du an micro-USB und USB-C?</li>
    <li>USB-A-Stecker einstecken: passt er in den Steckerraum, liegt das Kabel im Kanal ohne Knick?</li>
  </ul>
</section>

<section>
  <h2>Nächster Schritt</h2>
  <p>Wenn dir die Empfehlung passt (A: B, B: keine Schablone, C: Taste entfällt, D: volle Platte), baue ich STL, README, ZIP, Prüfbericht und den Testbogen. Sonst nenne mir die Änderungen.</p>
</section>
</div>
"""
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(head + body)
    print("geschrieben: %s (%d kB)" % (os.path.relpath(OUT), os.path.getsize(OUT) // 1024))


if __name__ == "__main__":
    page()
