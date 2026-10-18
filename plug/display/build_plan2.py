#!/usr/bin/env python3
"""Plan 2 Display-Gebäude: Aufbau und Zusammenbau des Körpers E2b als HTML mit Zeichnungen: plug/display/plan2.html.

Stand nach den Fotos des Moduls und dem Wunsch des Nutzers (2026-10-17): mindestens 4 mm Luft über der Kassette für die Adern, Block einstufig,
alles muss sich zusammensetzen lassen. Plan ohne STL, erst nach dem Abnicken.
    python3 -m plug.display.build_plan2
"""
import os

from plug.display import body
from plug.display import figures2 as F
from plug.display import layout as L
from plug.display import params as D
from plug.display.build_plan import CSS_EXTRA, CONCEPT_TEMPLATE, load

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "plan2.html")
de = lambda x, n=1: ("%.*f" % (n, x)).replace(".", ",")
B = body.dims()
P = D.DISP

CSS2 = """
.fig .notch { fill: var(--panel); stroke: var(--edge); stroke-width: .5; }
.fig .glass { fill: color-mix(in srgb, var(--c-port) 55%, var(--panel)); stroke: var(--edge); stroke-width: .5; }
.fig .aa2 { fill: color-mix(in srgb, var(--accent-fill) 40%, var(--panel)); stroke: var(--accent); stroke-width: .8; }
.fig .win2 { fill: none; stroke: var(--ok); stroke-width: 1.2; stroke-dasharray: 4 2; }
.fig .hole { fill: var(--panel); stroke: var(--edge); stroke-width: .7; }
.fig .pin { fill: var(--accent-fill); stroke: var(--accent-fill); stroke-width: 1.6; }
.fig .lid { fill: var(--accent-fill); stroke: var(--edge); stroke-width: .7; fill-opacity: .85; }
.fig .lidv { fill: var(--accent-fill); stroke: var(--accent); stroke-width: 1; fill-opacity: .25; }
.fig .blende { fill: var(--c-cut2); stroke: var(--edge); stroke-width: .7; fill-opacity: .8; }
.fig .ghost { fill: none; stroke: var(--muted); stroke-width: .8; stroke-dasharray: 3 2; }
.fig .arrow { stroke: var(--warn); stroke-width: 2; fill: none; }
.fig .arrowhead { fill: var(--warn); }
.fig .inv { fill: var(--panel); }
.fig text.inv { fill: var(--panel); }
.steps { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; }
.steps .card { gap: 8px; }
.steps .card h3 .n { font-family: var(--mono); color: var(--accent); margin-right: 8px; }
.twofig { display: grid; grid-template-columns: minmax(0, 1.25fr) minmax(0, 1fr); gap: 16px; align-items: start; }
@media (max-width: 860px) { .twofig { grid-template-columns: 1fr; } }
.twofig svg { max-width: 100%; }
.part { display: grid; grid-template-columns: auto 1fr; gap: 2px 12px; }
.sw { display: inline-block; width: 12px; height: 12px; border-radius: 2px; margin-right: 8px; vertical-align: -1px; border: 1px solid color-mix(in srgb, var(--edge) 40%, transparent); }
"""


def page(v):
    plate = L.Plate(v)
    sc = L.scan(plate, ("E2", "E2D"))
    iv = lambda e: ", ".join("y %s bis %s" % (de(a, 0), de(b, 0)) for a, b in sc[e]["intervals"])
    head = open(CONCEPT_TEMPLATE, encoding="utf-8").read().split('<div class="wrap">')[0]
    head = head.replace("<title>Powerbank in der Grundplatte</title>", "<title>Plan Display-Gebäude Aufbau</title>").replace("</style>", CSS_EXTRA + CSS2 + "</style>")
    w = B["W"]
    d = B["depth"]
    steps = "".join(
        '<div class="card"><h3><span class="n">%d</span>%s</h3>%s<p class="small">%s</p></div>' % (i + 1, st["t"], ('<div class="scroll">%s</div>' % F.step_fig(i)) if st["fig"] else "", st["d"])
        for i, st in enumerate(F.STEPS))
    body_html = f"""<div class="wrap">
<header>
  <div class="kicker">Steckmechanismus · Display-Gebäude · Plan 2, noch nicht abgenickt</div>
  <h1>Display-Gebäude: Aufbau und Zusammenbau</h1>
  <p class="lead">Der Block hinter dem Display ist jetzt einstufig und lässt mindestens {de(D.AIR_MIN, 0)} mm Luft über der Kassette, damit die Adern dort umbiegen können. Das Modul wurde aus deinen Fotos ausgemessen. Dieser Plan zeigt, aus welchen Teilen der Körper besteht und in welcher Reihenfolge man ihn zusammensetzt. Erst nach deinem Okay entstehen STL.</p>
</header>

<section aria-labelledby="h-ans">
  <h2 id="h-ans">Kurz</h2>
  <div class="answer">
    <div class="rec"><span class="lbl">Luft über der Kassette</span><span class="big">{de(D.AIR)} mm</span>
      <span class="small">Mindestens {de(D.AIR_MIN, 0)} mm, im Plan 0,5 mm mehr. Dort liegen die Adern in einer Schleife, bevor sie im Kanal nach unten zum Modul laufen.</span></div>
    <div class="rec"><span class="lbl">Block, eine Stufe</span><span class="big">{de(B['z_block'])} mm</span>
      <span class="small">Der Block um die Kassette steht gleichmäßig {de(B['z_block'])} mm über der Platte. Der Deckel liegt bündig im Dach. Es gibt keinen Kragen mehr.</span></div>
    <div class="rec"><span class="lbl">Teile</span><span class="big">4 gedruckt</span>
      <span class="small">Körper, Frontblende, Kassette, Deckel. Das Modul geht von vorn hinein, die Frontblende hält es. Kein Teil braucht Support, wenn der Körper steht.</span></div>
    <div><span class="lbl">Adern</span><span class="big">{de(D.WIRE_LEN, 0)} mm</span>
      <span class="small">Der Weg im Körper ist {de(B['wire_len'])} mm lang. Die übrigen 30 mm brauchst du zum Anlöten, danach schiebst du sie in die Kammer.</span></div>
  </div>
</section>

<section aria-labelledby="h-mod">
  <h2 id="h-mod">Das Modul aus den Fotos</h2>
  <p>Der Maßstab kommt aus zwei Dingen auf dem Rückseitenfoto: dem Pinraster (4 Pins mit 2,54 mm, der Header ist 10,2 mm lang) und dem Lochabstand, den ein veröffentlichter Halter für dieses 1,3-Zoll-Modul mit 30,3 × 28,4 mm angibt. Beide ergeben 31,3 und 31,2 Pixel je Millimeter. Die Genauigkeit liegt bei etwa 0,5 mm. Eine Schieblehre hast du nicht, deshalb sind Dicke und Feinmaße über eine kleine Passprobe zu klären (letzter Abschnitt).</p>
  <div class="twofig">
    <div class="card"><h3>Vorderansicht in Einbaulage (Pins unten)</h3><div class="scroll">{F.module_front()}</div>
      <p class="small muted">Grün die Platine, grau das Glas, gelb die aktive Fläche, grün gestrichelt das Sichtfenster in der Frontblende ({de(P['aa_w'] + 2 * D.WINDOW_MARGIN)} × {de(P['aa_h'] + 2 * D.WINDOW_MARGIN)} mm).</p></div>
    <div class="card"><h3>Was die Fotos zeigen</h3>
      <div class="scroll"><table>
        <thead><tr><th>Maß</th><th>Wert</th><th>Quelle</th></tr></thead>
        <tbody>
          <tr><td>Platine</td><td class="num">{de(P['pcb_w'])} × {de(P['pcb_h'])}</td><td class="src">Foto ± 0,5</td></tr>
          <tr><td>Löcher</td><td class="num">Ø {de(P['hole_d'])}, {de(P['hole_dx'])} × {de(P['hole_dy'])}</td><td class="src">Foto, Halter 30,3 × 28,4</td></tr>
          <tr><td>Glas</td><td class="num">{de(P['panel_w'])} × {de(P['panel_h'])}</td><td class="src">Datenblatt</td></tr>
          <tr><td>Aktive Fläche</td><td class="num">{de(P['aa_w'], 2)} × {de(P['aa_h'], 2)}</td><td class="src">Datenblatt</td></tr>
          <tr><td>Aktive Fläche bis Pinkante</td><td class="num">{de(P['aa_bottom'])}</td><td class="src">Foto</td></tr>
          <tr><td>Aktive Fläche bis Gegenkante</td><td class="num">{de(P['aa_top'])}</td><td class="src">Foto</td></tr>
          <tr><td>Pin-Reihe bis Kante</td><td class="num">{de(P['hdr_edge'])}</td><td class="src">Foto</td></tr>
          <tr><td>Ausschnitt (FPC)</td><td class="num">{de(P['notch_w'])} × {de(P['notch_d'])}</td><td class="src">Foto</td></tr>
          <tr><td>Dicke ohne Header</td><td class="num">≈ {de(P['mod_t'])}</td><td class="src">Zeichnung Schwestermodul: Glas 1,7 + Platine 1,0 + Bauteile 1,2</td></tr>
        </tbody></table></div></div>
  </div>
  <ul class="small">
    <li><b>Header sitzt hinten.</b> Der Kunststoff (2,5 mm) liegt auf der Rückseite, die Pins sind vorn verlötet und ragen nach hinten. Mit aufgestecktem Dupont-Gehäuse brauchte das Modul etwa 12 mm Tiefe hinter der Platine. Deshalb löten wir die Adern nach dem Auslöten des Headers direkt an.</li>
    <li><b>Pins am unteren Ende:</b> Die Beschriftung VDD GND SCK SDA steht für Pins oben. In Einbaulage sind sie unten, das Bild wird per Software um 180° gedreht (zum Beispiel U8g2 mit Drehung R2).</li>
    <li><b>Adresse:</b> Auf der Rückseite sitzen zwei Paare Lötplätze „1 (VDD) 1 (GND) 2 (VDD) 2 (GND)“. Sie wählen vermutlich die I²C-Adresse. Ein Scan zeigt 0x3C oder 0x3D.</li>
    <li><b>Spannungsregler:</b> Neben C9 sitzt ein SOT-23-Bauteil, vermutlich ein Regler. Das wäre ein Grund, dass die Herstellerseite „3 bis 5 V“ nennt. Wir bleiben bei 3,3 V vom ESP, das geht mit und ohne Regler. Belegt ist das Bauteil nicht, ich korrigiere damit meine Aussage aus Plan 1, die Platine habe keinen Regler.</li>
  </ul>
</section>

<section aria-labelledby="h-aufb">
  <h2 id="h-aufb">Aufbau im Schnitt und von oben</h2>
  <p>Links der Längsschnitt mitten durch die Stele, das Display schaut nach rechts (Osten). Der Schnitt geht durch das Kabelfenster der Rückwand, deshalb ist die Rückwand dort offen. Rechts die Draufsicht. Der Körper steht {de(B['z_top'])} mm über der Platte, steckt {de(-B['foot'])} mm tief in der Mulde und ist {de(w)} × {de(d)} mm groß.</p>
  <div class="twofig">
    <div class="card"><h3>Längsschnitt, zusammengebaut</h3><div class="scroll">{F.section(ident="sec-main", label="Schnitt A–A")}</div>
      <p class="small muted">Gelb der Deckel, violett die Frontblende, dunkelblau die Kassette, grün das Modul, rot die Adern. Die Adern laufen aus der Kassette nach oben, biegen in der Kammer ({de(D.AIR)} mm Luft) in den Kanal und gehen unten durch das Kabelfenster von hinten ans Modul. Orange unter der Platte: Winkelleiste mit Lötenden.</p></div>
    <div class="card"><h3>Grundriss</h3><div class="scroll">{F.plan_view()}</div>
      <p class="small muted">Von oben: vorn die Frontblende mit dem Sichtfenster, dahinter die Tasche mit dem Modul, die Rückwand mit dem Kabelfenster, der Kanal ({de(D.CHAN)} mm), der Schacht der Kassette und der Deckel über Kammer und Kanal.</p></div>
  </div>
  <div class="card"><h3>Die wichtigen Höhen und Maße</h3>
    <div class="scroll"><table>
      <thead><tr><th>Maß</th><th>Wert (mm)</th><th>Herkunft</th></tr></thead>
      <tbody>
        <tr><td>Kassettenoberkante über der Platte</td><td class="num">{de(B['z_cass'])}</td><td class="src">Maßkette Campus, Fuß 14,2 + 2,9 = Kassette 17,1</td></tr>
        <tr class="sel"><td>Luft über der Kassette bis zum Deckel</td><td class="num">{de(D.AIR)} (mindestens {de(D.AIR_MIN)})</td><td class="src">Nutzer, 0,5 Reserve</td></tr>
        <tr><td>Deckel, bündig im Blockdach</td><td class="num">{de(B['z_lid0'])} bis {de(B['z_block'])}</td><td class="src">E, {de(D.LID_T)} dick</td></tr>
        <tr><td>Kanal hinter der Rückwand (Tiefe)</td><td class="num">{de(D.CHAN)}</td><td class="src">S, vier Adern 28 AWG</td></tr>
        <tr><td>Kabelfenster in der Rückwand</td><td class="num">{de(D.SLIT_W)} breit, z {de(B['win_back'][0])} bis {de(B['win_back'][1])}</td><td class="src">E</td></tr>
        <tr><td>Unterkante des Moduls</td><td class="num">{de(B['mb'])} (Taschenboden {de(B['z_floor'])})</td><td class="src">A aus Fenster 1,5 und Foto</td></tr>
        <tr><td>Sichtfenster über der Platte</td><td class="num">{de(B['wb'])} bis {de(B['wt'])}</td><td class="src">Nutzer: nah am Boden</td></tr>
        <tr><td>Oberkante des Körpers</td><td class="num">{de(B['z_top'])}</td><td class="src">Modul 33,0 + 0,3 + Dach 1,2</td></tr>
        <tr><td>Tasche für das Modul</td><td class="num">{de(P['pcb_w'] + 2 * D.CLR)} × {de(P['mod_t'] + 2 * D.CLR)}</td><td class="src">Platine + 0,3 Spiel je Seite</td></tr>
      </tbody></table></div></div>
</section>

<section aria-labelledby="h-teile">
  <h2 id="h-teile">Die Teile</h2>
  <div class="scroll"><table>
    <thead><tr><th>Teil</th><th>Maße</th><th>Drucklage</th><th>Anmerkung</th></tr></thead>
    <tbody>
      <tr><td><b>1 Körper</b></td><td class="num">{de(w)} × {de(d)} × {de(B['height_total'])}</td><td>stehend, Fußunterseite auf dem Bett</td><td>Fuß mit Fußfase, Block, Rückwand mit Kabelfenster, Tasche, Kopfdach. Die Tasche überbrückt oben nur {de(P['mod_t'] + 2 * D.CLR)} mm, das Kabelfenster {de(D.SLIT_W)} mm. Schachtanschlag 0,5 mm. Kein Support.</td></tr>
      <tr><td><b>2 Frontblende</b></td><td class="num">{de(w)} × {de(B['z_top'] - B['blende_bottom'])} × {de(D.BLENDE_T)}</td><td>liegend, Außenseite unten</td><td>Das Sichtfenster ist ein glattes Loch ({de(P['aa_w'] + 2 * D.WINDOW_MARGIN)} × {de(P['aa_h'] + 2 * D.WINDOW_MARGIN)}). Klickt von vorn auf die Tasche. Gut in schwarz, weil sie die sichtbare Front ist.</td></tr>
      <tr><td><b>3 Kassette</b></td><td class="num">{de(D.KASS_W)} × {de(D.KASS_D)} × 17,1</td><td>stehend, wie die Kassetten der Gebäude</td><td>Unterbau der V2 ohne Blatt und Streifen: Buchsentasche, Aderschlitz, Schultern. Ist neu zu zeichnen, der Entwurf der V2 ist ungetestet.</td></tr>
      <tr><td><b>4 Deckel</b></td><td class="num">{de(B['lid'][1] - B['lid'][0] + 1.2)} × {de(D.KASS_W + 2.0)} × {de(D.LID_T)}</td><td>liegend</td><td>Schließt Kammer und Kanal, liegt bündig im Dach, zwei kleine Haken oder Zapfen halten ihn.</td></tr>
      <tr><td>Kaufteile</td><td colspan="3">Modul, Dupont-Buchse 4-polig mit Kontakten, vier Silikon-Adern 28 AWG, 55 mm, Winkelleiste für das Dock (wie bei den Gebäuden).</td></tr>
    </tbody></table></div>
</section>

<section aria-labelledby="h-zus">
  <h2 id="h-zus">Zusammenbau in sechs Schritten</h2>
  <div class="card"><h3>Explosion</h3><div class="scroll">{F.exploded()}</div>
    <p class="small muted">Die Kassette kommt von unten, der Deckel von oben, Modul und Frontblende von vorn. Alle vier Bewegungen gehen gerade, nichts muss gedreht oder verklemmt werden.</p></div>
  <div class="steps">{steps}</div>
  <div class="card"><h3>Später das Modul wechseln</h3>
    <p class="small">Frontblende abnehmen, das Modul herausziehen, die Adern ablöten. Den Deckel brauchst du nur, wenn die Kassette heraus soll: Die zieht man von unten aus dem Schacht, wenn der Körper nicht in der Platte steckt.</p></div>
</section>

<section aria-labelledby="h-kab">
  <h2 id="h-kab">Kabelweg und Platz</h2>
  <ul>
    <li><b>Weg:</b> Kassettenoberkante, {de(D.AIR / 2)} mm nach oben, {de(abs(B['wire'][1][0] - B['wire'][2][0]))} mm nach vorn (Osten, zum Kanal), {de(B['wire'][2][1] - B['wire'][3][1])} mm im Kanal nach unten, {de(abs(B['wire'][3][0] - B['xh']))} mm durch das Kabelfenster zum Modul. Zusammen {de(B['wire_len'])} mm.</li>
    <li><b>Biegungen:</b> Zwei Knicke von etwa 90° mit Radius ab 3 mm. Silikon-Litze 28 AWG (Ø etwa 1,0 mm) verträgt das. Das Bündel aus vier Adern misst 2,5 mm und passt in den Kanal ({de(D.CHAN)} mm) und die Kammer ({de(D.AIR)} mm).</li>
    <li><b>Reserve:</b> Beim Einschieben des Moduls sammeln sich etwa 30 mm Ader in der Kammer. Zwei bis drei Schleifen passen in {de(D.AIR)} × 12 mm. Wenn das zu eng ist, hilft eine Kante mit 45° im Deckel (kein Quetschen) oder kürzere Adern.</li>
    <li><b>Platz im Unterkasten:</b> Das Dock braucht wie bei den anderen Gebäuden 14,9 × 11,1 mm unter der Platte und den Steckerraum von 3,5 mm. Die vier Adern vom ESP-Feld laufen dort im Unterkasten (siehe Plan 1).</li>
  </ul>
</section>

<section aria-labelledby="h-chain">
  <h2 id="h-chain">Maßkette im Worst-Case</h2>
  <div class="scroll"><table>
    <thead><tr><th>Maß</th><th>Soll</th><th>Worst-Case</th><th>Ergebnis</th><th>Quelle</th></tr></thead>
    <tbody>
      <tr><td>Luft über der Kassette</td><td class="num">{de(D.AIR)}</td><td class="num">Kassettenoberkante ± 0,2: 4,3 bis 4,7</td><td><span class="pill ok">≥ 4</span></td><td class="src">Nutzer, A</td></tr>
      <tr><td>Breite der Tasche</td><td class="num">{de(P['pcb_w'] + 2 * D.CLR)} für Platine {de(P['pcb_w'])}</td><td class="num">Platine 35,8: Spiel 0,05</td><td><span class="pill mid">Passprobe</span></td><td class="src">Foto ± 0,5</td></tr>
      <tr><td>Tiefe der Tasche</td><td class="num">{de(P['mod_t'] + 2 * D.CLR)} für Modul {de(P['mod_t'])}</td><td class="num">Modul 5,0: Spiel 0,05</td><td><span class="pill mid">Passprobe</span></td><td class="src">S, Dicke ungemessen</td></tr>
      <tr><td>Fenster gegen aktive Fläche</td><td class="num">Rand {de(D.WINDOW_MARGIN)} je Seite</td><td class="num">Modul ± 0,5 verschoben: Rand −0,1 bis 0,9</td><td><span class="pill mid">Passprobe</span></td><td class="src">M, Foto</td></tr>
      <tr><td>Unterkante des Moduls</td><td class="num">{de(B['mb'])}, Fuß bis {de(B['foot'])}</td><td class="num">Fuß unter dem Taschenboden 6,6</td><td><span class="pill ok">frei</span></td><td class="src">A</td></tr>
      <tr><td>Mulde der Platte</td><td class="num">{de(w)} × {de(d)} × 14,2, Spiel 0,1 je Seite</td><td class="num">Druckmaß ± 0,1</td><td><span class="pill mid">Kippen ungetestet</span></td><td class="src">Plan Campus</td></tr>
      <tr><td>Höhe des Körpers im Druck</td><td class="num">{de(B['height_total'])}</td><td class="num">Bett 250</td><td><span class="pill ok">frei</span></td><td class="src">A</td></tr>
      <tr><td>Schacht für die Kassette</td><td class="num">{de(D.KASS_W)} × {de(D.KASS_D)}, Wand 1,2</td><td class="num">Spiel 0,06 je Seite wie bei den Kassetten der Steckprobe</td><td><span class="pill mid">V2 ungetestet</span></td><td class="src">Plan Campus</td></tr>
    </tbody></table></div>
</section>

<section aria-labelledby="h-risk">
  <h2 id="h-risk">Was beim Bau schiefgehen kann</h2>
  <ul>
    <li><b>Dünne Wände:</b> Die Seitenwände der Tasche sind 1,2 mm dick und bis {de(B['z_top'])} mm hoch. Sie hängen am Kopfdach und an der Rückwand und sollten stehen. Wenn sie wackeln, 1,6 mm nehmen (Körper wird 1,6 mm breiter).</li>
    <li><b>Haken der Frontblende:</b> Dünne Haken in PLA brechen leicht. PETG oder zwei Schrauben M2 sind die Rückfälle.</li>
    <li><b>Modulmaße:</b> Dicke und Lage der aktiven Fläche sind ± 0,5 mm genau. Ohne Schieblehre klärt das die Passprobe.</li>
    <li><b>Adern quetschen:</b> Beim Aufsetzen des Deckels dürfen keine Adern zwischen Deckel und Block liegen. Ein Zapfen im Deckel hält sie unten.</li>
    <li><b>Mulde groß:</b> {de(w)} × {de(d)} × 14,2 ist die größte Mulde der Platte. Kippen und Klemmen sind noch nicht getestet, wie bei der Campus-Platte insgesamt.</li>
    <li><b>Kassette:</b> Die Version ohne Streifen gibt es nur als Konzept. Sie ist der Unterbau der V2, deren Einpressen noch nicht gedruckt wurde.</li>
  </ul>
</section>

<section aria-labelledby="h-dec">
  <h2 id="h-dec">Entscheidungen</h2>
  <div class="dec">
    <div class="card rec"><h3><span class="tag">A</span> Anschluss am Modul</h3><div class="opts">
      <div class="opt pick"><b>Header auslöten, Adern von hinten durch die Löcher</b><span class="num2">Flach, Kanal {de(D.CHAN)} mm. Empfohlen. Du brauchst Entlötlitze.</span></div>
      <div class="opt"><b>Header bleibt, Adern an die Pinenden</b><span class="num2">Kanal etwa 10 mm statt {de(D.CHAN)}; der Körper wird etwa 6 mm tiefer.</span></div>
      <div class="opt"><b>Dupont-Buchse auf den Header</b><span class="num2">Tauschbar, aber etwa 17 mm Kanal; der Körper wird 13 mm tiefer, passt nur noch bei {iv('E2D')}.</span></div></div></div>
    <div class="card rec"><h3><span class="tag">B</span> Frontblende</h3><div class="opts">
      <div class="opt pick"><b>Schnapphaken, schwarz, liegend gedruckt</b><span class="num2">Fenster als glattes Loch, keine Brücke. Empfohlen.</span></div>
      <div class="opt"><b>Zwei Schrauben M2</b><span class="num2">stabiler, mehr Handarbeit.</span></div>
      <div class="opt"><b>Aufkleben</b><span class="num2">einfachster Druck, Modul nicht mehr wechselbar.</span></div></div></div>
    <div class="card"><h3><span class="tag">C</span> Luft über der Kassette</h3><div class="opts">
      <div class="opt pick"><b>{de(D.AIR)} mm</b><span class="num2">{de(D.AIR_MIN, 0)} mm Mindestmaß plus 0,5 Reserve. Block {de(B['z_block'])} hoch. Empfohlen.</span></div>
      <div class="opt"><b>{de(D.AIR_MIN, 0)} mm</b><span class="num2">Block {de(D.KASS_TOP + D.AIR_MIN + D.LID_T)} hoch, knapp für zwei Schleifen.</span></div>
      <div class="opt"><b>6 mm</b><span class="num2">Block {de(D.KASS_TOP + 6 + D.LID_T)} hoch, viel Platz, aber höher als nötig.</span></div></div></div>
    <div class="card"><h3><span class="tag">D</span> Deckel</h3><div class="opts">
      <div class="opt pick"><b>Reibsitz mit zwei Haken</b><span class="num2">Bündig im Dach, abnehmbar. Die Deckplatte der Fachprobe wackelte, deshalb Haken statt nur aufgelegt.</span></div>
      <div class="opt"><b>Eine Schraube M2</b><span class="num2">Gewinde in 1,2 mm Wand nur schneidend.</span></div>
      <div class="opt"><b>Kleben</b><span class="num2">Kammer nicht mehr zugänglich.</span></div></div></div>
    <div class="card"><h3><span class="tag">E</span> Wand der Tasche</h3><div class="opts">
      <div class="opt pick"><b>1,2 mm</b><span class="num2">{de(w)} breit. Wie bei allen Wänden um Kassette und Modul.</span></div>
      <div class="opt"><b>1,6 mm</b><span class="num2">{de(w + 0.8)} breit, steifer. Rückfall, falls die Wände wackeln.</span></div></div></div>
    <div class="card"><h3><span class="tag">F</span> Fenster</h3><div class="opts">
      <div class="opt pick"><b>Unterkante {de(D.GAP_FRONT)} mm, Rand {de(D.WINDOW_MARGIN)} mm</b><span class="num2">Nah am Boden, passend zum Wunsch.</span></div>
      <div class="opt"><b>Unterkante 1,0 mm</b><span class="num2">noch tiefer, Modul sitzt 0,5 mm tiefer im Fuß.</span></div></div></div>
  </div>
</section>

<section aria-labelledby="h-next">
  <h2 id="h-next">Nächster Schritt: ein Passdruck</h2>
  <p>Nach deinem Okay würde ich einen Satz bauen, mit dem du alles zusammensetzen und stecken kannst, ohne Schieblehre:</p>
  <ol class="todo">
    <li><b>Modulprobe:</b> eine kleine Platte mit drei Taschen (Tiefe {de(P['mod_t'] + 2 * D.CLR - 0.6)}, {de(P['mod_t'] + 2 * D.CLR)}, {de(P['mod_t'] + 2 * D.CLR + 0.6)} mm) und vier Stiften im Lochraster {de(P['hole_dx'])} × {de(P['hole_dy'])}. Das Modul zeigt, welche Tasche passt, ob die Löcher stimmen und wie das Fenster zur aktiven Fläche liegt.</li>
    <li><b>Körper mit Frontblende, Kassette und Deckel</b> (alle vier Teile) und eine <b>Mini-Platte</b> mit Mulde und Dock wie bei der Steckprobe. Dort prüfst du den Zusammenbau in den sechs Schritten, das Stecken und den I²C-Scan am ESP.</li>
    <li>Ein <b>Testbogen</b> als Formular (wie bei den anderen Runden) fragt nur fühlbare oder Ja/Nein-Punkte ab: Haken klicken, Modul sitzt, Adern passen, Deckel bündig, Mulde kippt.</li>
  </ol>
  <p class="small muted">Alle Maße der Platine sind aus den Fotos abgeleitet, die Dicke aus der Zeichnung eines Schwestermoduls. Die Werte stehen in <code>plug/display/params.py</code>, die Körperabmessungen in <code>plug/display/body.py</code>. Plan 1 (Lage am Ostrand) bleibt unverändert gültig.</p>
</section>
</div>
"""
    return head + body_html


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache")
    a = ap.parse_args()
    html = page(load(a.cache))
    open(OUT, "w", encoding="utf-8").write(html)
    print("geschrieben:", OUT, "%.0f KB" % (len(html) / 1024))


if __name__ == "__main__":
    main()
