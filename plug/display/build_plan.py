#!/usr/bin/env python3
"""Plan Display-Gebäude als HTML mit Zeichnungen: plug/display/plan.html.

Idee des Nutzers (2026-10-17): Ein OLED-Display (INA226-Messwerte als Rolling-Plot) auf einem eigenen Fuß mit Mulde, steckbar wie ein Gebäude,
senkrecht, möglichst nah am Boden, nach Osten gerichtet, am Ostrand, nicht vor den Gebäuden. Plan ohne STL, erst nach dem Abnicken.
    python3 -m plug.display.build_plan [--cache layout.json]

Die Platte (Grundrisse, Docks, Powerbank-Fach, ESP-Feld) kommt aus `plug.power.build_concept.variant(1300)` (ca. 25 s). Mit `--cache datei.json`
wird das Ergebnis dort abgelegt bzw. von dort gelesen.
"""
import argparse
import json
import math
import os

from shapely.geometry import Polygon, box

from plug.display import figures as F
from plug.display import layout as L
from plug.display import params as D

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "plan.html")
CONCEPT_TEMPLATE = os.path.join(HERE, "..", "power", "concept.template.html")
de = lambda x, n=1: ("%.*f" % (n, x)).replace(".", ",")


def load(cache):
    if cache and os.path.exists(cache):
        return json.load(open(cache))
    from plug.power import build_concept as BC
    v = BC.variant(1300)
    v["meshes"] = None
    if cache:
        json.dump(v, open(cache, "w"), default=float)
    return v


CSS_EXTRA = """
.fig { width: 100%; height: auto; display: block; min-width: 520px; }
.fig text { font-family: var(--font); fill: var(--fg); font-size: 11.5px; }
.fig .mut { fill: var(--muted); } .fig .ok { fill: var(--ok); font-weight: 600; } .fig .num { font-family: var(--mono); font-size: 10.5px; }
.fig .plate { fill: var(--c-plate); stroke: var(--edge); stroke-width: .8; }
.fig .foot { fill: var(--c-bld); stroke: var(--edge); stroke-width: .7; }
.fig .void { fill: var(--panel); stroke: var(--edge); stroke-width: .5; stroke-dasharray: 3 2; }
.fig .kass { fill: var(--c-under); stroke: var(--edge); stroke-width: .7; }
.fig .pcb { fill: var(--c-elec); stroke: var(--edge); stroke-width: .7; }
.fig .aa { stroke: var(--accent-fill); stroke-width: 3; fill: none; }
.fig .body { fill: var(--c-port); stroke: var(--edge); stroke-width: .6; }
.fig .pin { stroke: var(--accent-fill); stroke-width: 1.6; }
.fig .tail { stroke: var(--accent-fill); stroke-width: 2.4; stroke-linecap: round; fill: none; }
.fig .wire { stroke: var(--c-thread); stroke-width: 2.2; fill: none; stroke-linecap: round; }
.fig .dim { stroke: var(--fg); stroke-width: .8; fill: none; } .fig .okl { stroke: var(--ok); stroke-width: 2.4; }
.fig .tablel { stroke: var(--muted); stroke-width: .8; stroke-dasharray: 4 3; }
#wiring { min-width: 700px; }
.fig.sec { min-width: 0; max-width: 100%; }
#wiring .ln-ig { stroke: var(--muted); }
#wiring .blk { fill: var(--panel); stroke: var(--edge); stroke-width: 1; }
#wiring .blk.hot { stroke: var(--accent-fill); stroke-width: 2; }
#wiring .blk.disp { stroke: var(--c-cut2); stroke-width: 2; }
#wiring .bt { font-weight: 600; font-size: 13px; }
#wiring .ln { fill: none; stroke-width: 2.2; stroke-linejoin: round; }
#wiring .v5 { stroke: var(--accent-fill); } #wiring .v3 { stroke: var(--c-elec); } #wiring .i2c { stroke: var(--c-cut2); } #wiring .sig { stroke: var(--muted); stroke-dasharray: 4 3; }
#wiring .v5s { fill: var(--accent-fill); } #wiring .v3s { fill: var(--c-elec); } #wiring .i2s { fill: var(--c-cut2); } #wiring .sgs { fill: var(--muted); }
.mapgrid { display: grid; grid-template-columns: minmax(0, 380px) minmax(0, 1fr); gap: 20px; align-items: start; }
@media (max-width: 860px) { .mapgrid { grid-template-columns: 1fr; } }
#map { width: 100%; height: auto; display: block; background: var(--canvas); border-radius: 6px; }
#map .plate { fill: var(--c-plate); stroke: var(--edge); stroke-width: .8; }
#map .bld { fill: var(--c-bld); stroke: var(--edge); stroke-width: .5; fill-opacity: .85; }
#map .hof { fill: var(--c-hof); stroke: var(--edge); stroke-width: .4; fill-opacity: .85; }
#map .pb { fill: none; stroke: var(--c-pb); stroke-width: 1.2; stroke-dasharray: 5 3; }
#map .win { fill: var(--c-pb); fill-opacity: .55; }
#map .esp { fill: var(--c-elec); fill-opacity: .25; stroke: var(--c-elec); stroke-width: 1; stroke-dasharray: 4 2; }
#map .v { fill: var(--c-thread); fill-opacity: .55; }
#map .dock { fill: var(--c-niche); fill-opacity: .3; stroke: var(--c-niche); stroke-width: .8; }
#map .post { fill: var(--c-under); fill-opacity: .35; } #map .post.gone { fill: var(--warn); fill-opacity: .5; }
#map .lbl { fill: var(--edge); fill-opacity: .12; stroke: var(--edge); stroke-opacity: .35; stroke-width: .6; stroke-dasharray: 3 2; }
#map text { font-family: var(--font); font-size: 9.5px; fill: var(--fg); } #map text.mut { fill: var(--muted); }
#map .mulde { fill: var(--accent-fill); fill-opacity: .55; stroke: var(--edge); stroke-width: 1; }
#map .mulde.no { fill: var(--warn); fill-opacity: .5; }
#map .zone { fill: none; stroke: var(--accent); stroke-width: 1.2; stroke-dasharray: 4 3; }
#map .slab { fill: var(--c-cut2); fill-opacity: .6; }
#map .cab { fill: none; stroke: var(--c-thread); stroke-width: 1.6; stroke-dasharray: 5 3; }
#map .eye { fill: none; stroke: var(--fg); stroke-width: 1; }
.ro { display: flex; flex-direction: column; gap: 14px; min-width: 0; }
.ro .kv { display: grid; grid-template-columns: auto 1fr; gap: 4px 14px; font-size: .92rem; }
.ro .kv dt { color: var(--muted); } .ro .kv dd { margin: 0; font-family: var(--mono); font-variant-numeric: tabular-nums; }
.stat { font-size: 1rem; font-weight: 600; padding: 8px 12px; border: 1px solid; border-radius: 6px; }
.stat.ok { color: var(--ok); } .stat.no { color: var(--warn); }
.ro ul { font-size: .9rem; }
.dec { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; }
.dec .card.rec { box-shadow: inset 0 3px 0 var(--accent-fill); }
.dec h3 .tag { font-family: var(--mono); font-size: .72rem; color: var(--accent); letter-spacing: .06em; margin-right: 8px; }
.opts { display: flex; flex-direction: column; gap: 8px; }
.opt { border: 1px solid var(--line); border-radius: 6px; padding: 8px 10px; display: flex; flex-direction: column; gap: 2px; font-size: .92rem; }
.opt.pick { border-color: var(--accent-fill); background: color-mix(in srgb, var(--accent-fill) 12%, transparent); }
.opt b { font-weight: 600; } .opt .num2 { color: var(--muted); font-size: .8rem; }
.figs3 { display: flex; flex-direction: column; gap: 16px; }
.figs3 .card { display: grid; grid-template-columns: minmax(0, 440px) minmax(0, 1fr); gap: 8px 24px; align-items: start; }
.figs3 .card h3 { grid-column: 1 / -1; }
.figs3 .scroll { grid-column: 1; }
.figs3 .card > p { grid-column: 2; align-self: center; font-size: 1rem; }
@media (max-width: 760px) { .figs3 .card { grid-template-columns: 1fr; } .figs3 .scroll, .figs3 .card > p { grid-column: 1; } }
.ro ul:empty { display: none; }
.figs3 .card.rec { box-shadow: inset 0 3px 0 var(--accent-fill); }
.todo { counter-reset: t; list-style: none; padding: 0; }
.todo li { counter-increment: t; padding-left: 2.2em; position: relative; }
.todo li::before { content: counter(t); position: absolute; left: 0; top: 0; width: 1.6em; height: 1.6em; border-radius: 50%; background: var(--accent-fill); color: var(--on-accent); font-family: var(--mono); font-size: .8rem; display: grid; place-items: center; }
"""

JS = r"""
const DATA = __DATA__;
const S = 3.2, W = DATA.plate[0], Ln = DATA.plate[1];
const NS = 'http://www.w3.org/2000/svg';
const X = x => x * S, Y = y => (Ln - y) * S;
const el = (tag, attrs, parent) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); (parent || svg).appendChild(e); return e; };
const svg = document.getElementById('map');
svg.setAttribute('viewBox', `0 0 ${W * S + 16} ${Ln * S + 16}`);
const g = el('g', {transform: 'translate(8,8)'}, svg);
const poly = (pts, cls, parent) => el('polygon', {points: pts.map(p => X(p[0]).toFixed(1) + ',' + Y(p[1]).toFixed(1)).join(' '), class: cls}, parent || g);
const rect = (x0, y0, x1, y1, cls, parent) => poly([[x0, y0], [x1, y0], [x1, y1], [x0, y1]], cls, parent);
const txt = (x, y, s, cls, anchor) => { const t = el('text', {x: X(x), y: Y(y), class: cls || '', 'text-anchor': anchor || 'middle'}, g); t.textContent = s; return t; };

rect(0, 0, W, Ln, 'plate');
rect(0, 0, W, DATA.label_y, 'lbl'); txt(W / 2 - 8, DATA.label_y / 2 - 2, 'Schrift und Nordpfeil (erhaben)', 'mut');
DATA.buildings.forEach(b => { poly(b.poly, 'bld'); });
poly(DATA.hof, 'hof');
poly(DATA.fach, 'pb'); poly(DATA.window, 'win');
txt(57, 98, 'Powerbank im Unterkasten', 'mut');
poly(DATA.elec, 'esp'); txt(33, 70, 'ESP-Feld', 'mut');
DATA.notches.forEach(n => poly(n, 'v'));
DATA.docks.forEach(d => poly(d.zone, 'dock'));
const postEls = DATA.posts.map(p => ({p, el: poly(p.r, 'post')}));
const lab = {
  '01_paulinum': [88, 168], '02_neues_augusteum': [82, 140], '03_hoersaalgebaeude': [30, 40], '04_seminargebaeude': [27, 150],
  '05_institutsgebaeude': [60, 207], '06_city_hochhaus': [82, 70]};
DATA.buildings.forEach(b => { const p = lab[b.slug]; if (p) txt(p[0], p[1], b.title.split(' ')[0], 'mut'); });
txt(W - 3, Ln + 0, '', '');
// Ost-Pfeil
const eye = el('g', {}, g);
const east = el('text', {x: X(W) - 2, y: -1, class: 'mut', 'text-anchor': 'end'}, g); east.textContent = 'Osten, Blickrichtung des Displays →';

const ov = el('g', {}, g);
const ui = {
  design: () => document.querySelector('input[name=design]:checked').value,
  mode: () => document.querySelector('input[name=mode]:checked').value,
  yc: document.getElementById('yc'), ycv: document.getElementById('ycv'),
  stat: document.getElementById('stat'), why: document.getElementById('why'), kv: document.getElementById('kv'),
  showposts: document.getElementById('showposts')
};
const f1 = x => x.toFixed(1).replace('.', ',');
function current() {
  const d = ui.design(), m = ui.mode(), D_ = DATA.scan[d];
  if (m === 'sw') return D_.sw;
  if (m === 'ne') return D_.ne;
  return D_.ost.find(r => r.yc === +ui.yc.value);
}
function draw() {
  const d = ui.design(), m = ui.mode(), r = current(), dd = DATA.designs[d];
  ui.yc.disabled = m !== 'ost';
  ui.ycv.textContent = m === 'ost' ? f1(+ui.yc.value) : f1(r.yc);
  ov.replaceChildren();
  const x0 = r.xe - dd.depth, x1 = r.xe, y0 = r.yc - dd.w / 2, y1 = r.yc + dd.w / 2;
  const sd = d === 'E1' ? dd.depth : dd.slab;
  rect(x0, y0, x1, y1, 'mulde' + (r.ok ? '' : ' no'), ov);
  rect(r.xe - sd, y0, r.xe, y1, 'slab', ov);
  const z = r.zone;
  rect(z[0], z[1], z[2], z[3], 'zone', ov);
  const t = el('text', {x: X(x0) - 4, y: Y(r.yc) + 3, class: 'mut', 'text-anchor': 'end'}, ov); t.textContent = d + ' · ' + f1(dd.depth) + ' × ' + f1(dd.w);
  const e = DATA.elec_c;
  el('polyline', {points: [X(r.xp) + ',' + Y(r.yc), X(r.xp - (r.tail === 'E' ? -1 : 1) * 6) + ',' + Y(r.yc), X(e[0]) + ',' + Y(e[1])].join(' '), class: 'cab'}, ov);
  let gone = 0;
  postEls.forEach(({p, el: pe}) => {
    const hit = ui.showposts.checked && p.b[0] < z[2] + 0 && p.b[2] > z[0] && p.b[1] < z[3] && p.b[3] > z[1];
    pe.setAttribute('class', 'post' + (hit ? ' gone' : '')); if (hit) gone++;
    pe.style.display = ui.showposts.checked ? '' : 'none';
  });
  ui.stat.className = 'stat ' + (r.ok ? 'ok' : 'no');
  ui.stat.textContent = r.ok ? 'Passt: Mulde, Dockzone und Abstände frei' : 'Passt nicht';
  ui.why.innerHTML = r.ok ? '' : r.why.map(w => '<li>' + w + '</li>').join('');
  const names = DATA.names;
  ui.kv.innerHTML = [
    ['Mulde (Fuß)', f1(dd.w) + ' × ' + f1(dd.depth) + ' mm, 14,2 tief'],
    ['Lage', 'Ostkante x = ' + f1(r.xe) + ', Mitte y = ' + f1(r.yc) + ' mm'],
    ['Abstand zur Ostkante', f1(W - r.xe) + ' mm'],
    ['Lötenden zeigen nach', r.tail === 'E' ? 'Osten' : 'Westen'],
    ['Kabel zum ESP-Feld', '≈ ' + Math.round(r.to_esp) + ' mm Luftlinie (Adern etwa ' + Math.round(r.to_esp * 1.3 + 30) + ' mm)'],
    ['Stützen im Weg', gone + ' (entfallen im Unterkasten)'],
    ['Fenster über der Platte', f1(dd.win_bottom) + ' bis ' + f1(dd.win_bottom + dd.win_h) + ' mm'],
    ['Höhe gesamt', f1(dd.top) + ' mm'],
    ['Davor (Osten)', (r.sight > 0 ? 'Gebäude verdecken das Fenster bis ' + Math.round(r.sight) + '° Blickwinkel' : 'nichts, Fenster frei sichtbar')],
    ['Dahinter (Westen)', r.behind.map(s => names[s]).join(', ') || 'nur Platte']
  ].map(p => '<dt>' + p[0] + '</dt><dd>' + p[1] + '</dd>').join('');
}
document.querySelectorAll('input[name=design], input[name=mode], #yc, #showposts').forEach(i => i.addEventListener('input', draw));
draw();
"""


def compact_scan(sc):
    out = {}
    for e, d in sc.items():
        keep = lambda r: dict(r)
        out[e] = dict(ost=[keep(r) for r in d["ost"]], sw=keep(d["sw"]), ne=keep(d["ne"]))
    return out


def page(v):
    plate = L.Plate(v)
    sc = L.scan(plate)
    ex = plate.elec.centroid
    b2 = lambda r: Polygon(r[0]).bounds
    posts = [dict(r=[[round(x, 1), round(y, 1)] for x, y in p["r"]], b=[round(c, 1) for c in Polygon(p["r"]).bounds]) for p in v["posts"]]
    designs = {e: dict(depth=round(L.DESIGNS[e]["depth"], 1), w=round(L.DESIGNS[e]["w"], 1), slab=round(L.SLAB, 1), win_bottom=sc[e]["win_bottom"],
                       win_h=round(L.WIN_H * (math.cos(math.radians(D.TILT_DEG)) if e == "E3" else 1), 1), top=sc[e]["top"]) for e in sc}
    pol = lambda p: [[round(x, 1), round(y, 1)] for x, y in (p[0] if isinstance(p[0][0], list) else p)]
    data = dict(
        plate=v["plate"], label_y=D.LABEL_Y - 2.0, elec_c=[round(ex.x, 1), round(ex.y, 1)],
        buildings=[dict(slug=b["slug"], title=b["title"], poly=pol(b["poly"])) for b in v["buildings"]],
        hof=pol(v["hof"]), fach=pol(v["fach_poly"]), window=pol(v["window"]), elec=pol(v["elec"]),
        notches=[pol(x["notch"]) for x in v["vs"]], docks=[dict(zone=pol(d["zone"])) for d in v["docks"] if d["ok"]],
        posts=posts, designs=designs, scan=compact_scan(sc),
        names={b["slug"]: b["title"].split(" ")[0] for b in v["buildings"]})
    names = data["names"]
    e2 = sc["E2"]
    y_a = e2["intervals"][0][0]
    r_a = next(r for r in e2["ost"] if r["yc"] == y_a)
    zone_a = box(*r_a["zone"])
    gone = sum(1 for p in posts if box(*p["b"]).intersects(zone_a))
    head = open(CONCEPT_TEMPLATE, encoding="utf-8").read().split('<div class="wrap">')[0]
    head = head.replace("<title>Powerbank in der Grundplatte</title>", "<title>Plan Display-Gebäude</title>").replace("</style>", CSS_EXTRA + "</style>")
    I = lambda e: sc[e]["intervals"]
    iv = lambda e: ", ".join("y %s bis %s" % (de(a, 0), de(b, 0)) for a, b in I(e))
    d1, d2, d3, d2d = (L.DESIGNS[k] for k in ("E1", "E2", "E3", "E2D"))
    esp_a = r_a["to_esp"]
    posts_txt = ("Keine der 6 × 6 mm großen Stützen im 40-mm-Raster steht in der Dockzone. Der Generator lässt Stützen in Dockzonen ohnehin weg." if gone == 0 else
                 "%d der 6 × 6 mm großen Stützen im 40-mm-Raster liegen in der Dockzone und entfallen, der Generator lässt sie wie bei den anderen Docks weg." % gone)
    posts_short = "Keine Stütze steht im Weg." if gone == 0 else "%d Stützen entfallen für die Dockzone." % gone
    body = f"""<div class="wrap">
<header>
  <div class="kicker">Steckmechanismus · Display-Gebäude · Plan, noch nicht abgenickt</div>
  <h1>Display-Gebäude für Leistung und Verbrauch</h1>
  <p class="lead">Ein senkrecht stehendes OLED auf einem eigenen Fuß mit Mulde, steckbar wie ein Gebäude, nah am Boden, nach Osten gerichtet, am Ostrand und nicht vor den Gebäuden. Es zeigt als Rolling-Plot die Leistung und den Verbrauch, gemessen mit dem INA226. Dieser Plan vergleicht drei Entwürfe und mehrere Lagen. Erst nach deinem Okay entstehen STL.</p>
</header>

<section aria-labelledby="h-ans">
  <h2 id="h-ans">Kurz</h2>
  <div class="answer">
    <div class="rec"><span class="lbl">Spannung</span><span class="big">3,3 V</span>
      <span class="small">Direkt vom 3,3-V-Pin des ESP, kein Wandler. Das Panel verträgt laut Datenblatt höchstens 3,5 V, die 5 V der Platte dürfen nicht an die Platine.</span></div>
    <div class="rec"><span class="lbl">Lage</span><span class="big">Südost-Ecke</span>
      <span class="small">Am Ostrand, Mitte {de(y_a, 0)} mm von der Südkante, etwa 5 mm über der Schrift. Dort steht nichts davor, die Platte hat Platz bis zu den Gebäuden.</span></div>
    <div class="rec"><span class="lbl">Entwurf</span><span class="big">E2, {de(d2['w'])} × {de(d2['depth'])}</span>
      <span class="small">Display vorn, Block mit Kassette dahinter. Das Sichtfenster beginnt {de(sc['E2']['win_bottom'])} mm über der Platte, der Fuß nimmt die untere Platinenhälfte auf. Höhe gesamt {de(sc['E2']['top'])} mm.</span></div>
    <div><span class="lbl">Kabel</span><span class="big">≈ {de(esp_a * 1.3 + 30, 0)} mm</span>
      <span class="small">Vier Adern vom Display-Dock zum ESP-Feld im Unterkasten, ohne die Powerbank zu kreuzen. {posts_short}</span></div>
  </div>
</section>

<section aria-labelledby="h-mod">
  <h2 id="h-mod">Das Display ist ein 1,3-Zoll-Modul</h2>
  <p>Die Recherche zum Aufdruck „GME12864-70“ ergab: Das ist laut Hersteller ein nacktes <b>1,3-Zoll-Panel</b> (128 × 64 Pixel, Controller CH1116G, kompatibel zum SH1106) mit FPC. Dein Teil sitzt auf einer Platine. Die Platine misst auf dem Foto etwa 35 mm in der Breite, das passt zu den 35,5 × 32 mm des Schwestermoduls GME12864-79. Damit ist die Anzeige größer als beim 0,96-Zoll-Modul, das ich zuerst angenommen hatte: Die aktive Fläche hat <span class="num">{de(D.DISP['aa_w'], 2)} × {de(D.DISP['aa_h'], 2)} mm</span> statt 21,7 × 10,9 mm. Für den Rolling-Plot ist das ein klarer Gewinn.</p>
  <div class="two">
    <div class="card"><h3>Was belegt ist (Datenblatt GME12864-70)</h3>
      <ul class="small">
        <li>Panel 34,5 × 23,0 × 1,45 mm, aktive Fläche 29,42 × 14,70 mm, Pixel 0,21 mm.</li>
        <li>VDD1 1,65 bis 3,5 V. Die Herstellerseite nennt „3 bis 5 V“, das widerspricht dem Datenblatt. Ohne sichtbaren Spannungsregler auf der Platine bleibt es bei 3,3 V.</li>
        <li>RAM 132 × 64: Die Treiber-Einstellung „SH1106 128×64“ (U8g2) passt, falls das Bild 2 Pixel verschoben ist, den Spaltenversatz setzen.</li>
        <li>Pinfolge am Header, wie du gelesen hast: VDD, GND, SCK, SDA.</li>
      </ul></div>
    <div class="card"><h3>Was noch geschätzt ist: bitte messen</h3>
      <ul class="small">
        <li>Platine Breite, Höhe und Dicke, dazu die Gesamtdicke von der Panelfront bis zur Platinenrückseite (Plan rechnet mit 35,5 × 32 × 4,5).</li>
        <li>Lochabstand und Lochdurchmesser (auf dem Foto sind oben zwei Löcher zu sehen, geschätzt 31 mm Abstand).</li>
        <li>Abstand von der Oberkante der Platine bis zur aktiven Fläche (Plan: 5,0).</li>
        <li>Lage und Höhe der Pinleiste, und ob auf der Vorderseite ein Regler sitzt. Ein Foto der Vorderseite hilft.</li>
      </ul></div>
  </div>
</section>

<section aria-labelledby="h-el">
  <h2 id="h-el">Elektrik: 3,3 V reichen, der INA226 braucht einen kleineren Shunt</h2>
  <div class="card"><h3>Blockschaltbild</h3><div class="scroll">{F.wiring()}</div>
    <p class="small muted">Der INA226 sitzt mit seinem Shunt in der 5-V-Leitung zwischen Powerbank und allem Übrigen. Er und das OLED hängen an derselben I²C-Leitung des ESP (Adressen 0x40 und 0x3C). Beide bekommen 3,3 V vom ESP. Das Display-Dock führt vier Adern: GND, SDA, SCL, 3,3 V, ohne den Pegelwandler der LED-Docks.</p></div>
  <div class="two">
    <div class="card"><h3>Warum kein Spannungswandler</h3>
      <ul class="small">
        <li>Das OLED zieht etwa 20 mA, der INA226 etwa 0,4 mA. Der 3,3-V-Regler eines DevKits liefert 800 mA und der ESP selbst braucht bis etwa 0,5 A in Sendespitzen. Reserve bleibt.</li>
        <li>I²C läuft am ESP mit 3,3 V. Mit 3,3 V am Display liegen die Pull-ups des Moduls ebenfalls auf 3,3 V. Mit 5 V würden sie die ESP-Pins mit 5 V belasten.</li>
        <li>Das Display-Dock bekommt eigene Adern vom ESP und nicht die 5 V der LED-Docks. Falsch stecken ist durch die eigene Mulde ausgeschlossen.</li>
        <li>Die 4 Adern über die Dupont-Kontakte sind kurz (etwa {de(esp_a * 1.3 + 30, 0)} mm). Bei 100 kHz bis 400 kHz ist das unkritisch. Pull-ups 4,7 kΩ am ESP-Feld fest einbauen, damit die Leitung auch ohne gestecktes Display definierte Pegel hat.</li>
      </ul></div>
    <div class="card"><h3>INA226: Shunt und Messbereich</h3>
      <div class="scroll"><table>
        <thead><tr><th>Shunt</th><th>Bereich</th><th>Auflösung</th><th>Abfall bei 1 A</th></tr></thead>
        <tbody>
          <tr><td class="num">0,1 Ω ab Werk</td><td class="num">bis 0,82 A</td><td class="num">25 µA</td><td class="num">100 mV</td></tr>
          <tr class="sel"><td class="num">0,05 Ω, 2 parallel</td><td class="num">bis 1,64 A</td><td class="num">50 µA</td><td class="num">50 mV</td></tr>
        </tbody></table></div>
      <p class="small muted">Spitze geschätzt (S): 9 LEDs à 60 mA = 0,54 A (Paulinum, Neues Augusteum, Hörsaal je 1; Seminar, Institut, Hochhaus je 2), dazu der ESP bis etwa 0,5 A. Das sind etwa 1,0 A und damit mehr als 0,82 A. Mit dem ab Werk aufgelöteten 0,1 Ω wäre die Messung bei Vollweiß übersteuert. Empfehlung: einen zweiten 0,1-Ω-Widerstand parallel löten und im Programm den Shunt auf 0,05 Ω setzen. Der Abfall von 50 mV liegt unter der Toleranz der LED-Versorgung. Die Powerbank begrenzt bei 2,1 A.</p></div>
  </div>
  <div class="card"><h3>Belegung der vier Adern am Display-Dock</h3>
    <div class="scroll"><table>
      <thead><tr><th>Pin am Dock</th><th>Signal</th><th>Quelle am ESP</th><th>Anmerkung</th></tr></thead>
      <tbody>
        <tr><td class="num">1</td><td>GND</td><td>GND</td><td class="src">außen, so hat die Masse beim Stecken zuerst Kontakt (Annahme)</td></tr>
        <tr><td class="num">2</td><td>SDA</td><td>GPIO 21</td><td class="src">Standard-I²C des ESP32</td></tr>
        <tr><td class="num">3</td><td>SCL</td><td>GPIO 22</td><td class="src">Standard-I²C des ESP32</td></tr>
        <tr><td class="num">4</td><td>VDD 3,3 V</td><td>3V3</td><td class="src">außen; die Reihenfolge am Display ist VDD, GND, SCK, SDA, die Kassette legt die Adern passend</td></tr>
      </tbody></table></div>
    <p class="small muted">Die Kassette hat dieselbe 4-polige Dupont-Buchse wie bei den Gebäuden. Weil die Adern in der Kassette frei belegt werden, spielt die Pinfolge des Moduls keine Rolle.</p></div>
</section>

<section aria-labelledby="h-map">
  <h2 id="h-map">Wohin auf die Platte</h2>
  <p>Die Karte zeigt die Platte 1:1300 (115,6 × 220,8 mm) von oben, Norden oben, Osten rechts, wie in Konzept Stand 6. Das Display blickt immer nach Osten. Wähle Entwurf und Lage; der Schieber verschiebt die Stele am Ostrand von Süden nach Norden. Orange gestrichelt ist die Dockzone unter der Platte, violett die Stele über der Platte, rot gestrichelt die Adern zum ESP-Feld.</p>
  <div class="mapgrid">
    <div class="card"><svg id="map" role="img" aria-label="Draufsicht der Platte mit Lage der Display-Stele"></svg>
      <div class="legend"><span style="--sw: var(--c-bld)">Gebäude</span><span style="--sw: var(--c-hof)">Innenhof</span><span style="--sw: var(--c-elec)">ESP-Feld</span><span style="--sw: var(--c-niche)">Dockzonen</span><span style="--sw: var(--c-thread)">Fadenkerbe</span><span style="--sw: var(--c-cut2)">Stele</span></div></div>
    <div class="ro">
      <div class="card"><h3>Entwurf</h3>
        <div class="seg" role="radiogroup" aria-label="Entwurf">
          <input type="radio" name="design" id="dE1" value="E1"><label for="dE1">E1 kompakt <span class="dims">{de(d1['depth'])} tief</span></label>
          <input type="radio" name="design" id="dE2" value="E2" checked><label for="dE2">E2 Display vorn <span class="dims">{de(d2['depth'])} tief</span></label>
          <input type="radio" name="design" id="dE3" value="E3"><label for="dE3">E3 Pult 15° <span class="dims">{de(d3['depth'])} tief</span></label>
          <input type="radio" name="design" id="dE2D" value="E2D"><label for="dE2D">E2 mit Dupont <span class="dims">{de(d2d['depth'])} tief</span></label>
        </div>
        <h3>Lage</h3>
        <div class="seg" role="radiogroup" aria-label="Lage">
          <input type="radio" name="mode" id="mOst" value="ost" checked><label for="mOst">Ostrand, Schieber</label>
          <input type="radio" name="mode" id="mSW" value="sw"><label for="mSW">Südwest, links neben der Schrift</label>
          <input type="radio" name="mode" id="mNE" value="ne"><label for="mNE">Nordost-Ecke</label>
        </div>
        <div class="field"><label for="yc">Mitte der Stele von der Südkante</label><span class="num"><span id="ycv">37</span> mm</span>
          <input type="range" id="yc" min="20" max="110" step="1" value="{int(y_a)}"></div>
        <label class="small"><input type="checkbox" id="showposts" checked> Stützen des Unterkastens zeigen (rot = im Weg)</label>
      </div>
      <div class="card"><div class="stat ok" id="stat" role="status"></div><ul id="why"></ul><dl class="kv" id="kv"></dl></div>
    </div>
  </div>
  <div class="two">
    <div class="card"><h3>Was am Ostrand geht</h3>
      <div class="scroll"><table>
        <thead><tr><th>Entwurf</th><th>frei am Ostrand (Mitte von Süden)</th></tr></thead>
        <tbody>
          <tr><td>E1 kompakt, 8,0 tief</td><td class="num">{iv('E1')}</td></tr>
          <tr class="sel"><td>E2 Display vorn, 19,9 tief</td><td class="num">{iv('E2')}</td></tr>
          <tr><td>E3 Pult 15°, 25,3 tief</td><td class="num">{iv('E3')}</td></tr>
          <tr><td>E2 mit Dupont, 32,9 tief</td><td class="num">{iv('E2D')}</td></tr>
        </tbody></table></div>
      <p class="small muted">Der Streifen endet im Norden am Hochhaus-Bogen (der Entwurf ragt 20 bis 33 mm nach Westen) und im Süden an der Fadenkerbe und der Schrift. Nur E1 reicht bis in die Lücke zwischen Hochhaus und Neuem Augusteum (y {de(I('E1')[0][1], 0)}). Nirgends steht ein Gebäude vor dem Display: Das Sichtfenster ist von Osten aus jeder Höhe frei.</p></div>
    <div class="card"><h3>Warum „links neben der Schrift“ und die Nordost-Ecke nicht gehen</h3>
      <ul class="small">
        <li><b>Südost-Ecke (von Osten gesehen links):</b> geht. Das ist die Lage direkt über dem Nordpfeil und der Schrift, mit etwa 5 mm Abstand zur Schrift.</li>
        <li><b>Südwest-Ecke (links auf der Karte, neben der Schrift):</b> die Stele ist {de(d2['w'])} mm breit. Zwischen dem Rand (3,5 mm) und dem Hörsaalgebäude (mit 2 mm Wand) bleiben bei dieser Breite nur 7,5 mm Tiefe, E1 braucht 8,0 und E2 {de(d2['depth'])} mm. Außerdem stünde das Hörsaalgebäude unmittelbar vor dem Fenster, nach Osten blickend wäre das Display verdeckt.</li>
        <li><b>Nordost-Ecke:</b> zwischen Paulinum und Fadenkerbe bleiben 24 mm frei, die Stele braucht {de(d2['w'])} mm.</li>
        <li>Wenn die Südwest-Ecke wichtig ist, ginge dort nur ein Display, das nach Süden zur Schrift blickt.</li>
      </ul></div>
  </div>
</section>

<section aria-labelledby="h-ent">
  <h2 id="h-ent">Drei Entwürfe im Schnitt</h2>
  <p>Blick von Süden, das Display schaut nach rechts (Osten). Grün ist die Platine, die gelbe Linie die aktive Fläche, rot die Adern. Die Platte liegt bei 0, die Mulde reicht {de(14.2)} mm tief.</p>
  <div class="figs3">
    <div class="card"><h3><span class="meta">E1</span> Stele auf der Kassette</h3><div class="scroll">{F.section('E1')}</div>
      <p class="small">Das Modul sitzt ganz über der Kassette. Die untere Platinenhälfte ist sichtbar, das Fenster beginnt {de(sc['E1']['win_bottom'])} mm über der Platte. Kleinste Fläche ({de(d1['depth'])} × {de(d1['w'])}), die Adern sind kurz. Kommt nicht nah an den Boden.</p></div>
    <div class="card rec"><h3><span class="meta">E2</span> Display vorn, Block dahinter</h3><div class="scroll">{F.section('E2')}</div>
      <p class="small">So hast du es beschrieben. Das untere Drittel der Platine ist im Fuß versenkt, das Fenster beginnt {de(sc['E2']['win_bottom'])} mm über der Platte. Dahinter steht der Block mit der Kassette, dazwischen ein 4 mm breiter Kabelraum für die angelöteten Adern. Der Kabelraum ist oben offen und wird von einem Deckel geschlossen.</p></div>
    <div class="card"><h3><span class="meta">E3</span> Pult, 15° geneigt</h3><div class="scroll">{F.section('E3')}</div>
      <p class="small">Wie E2, aber um 15° nach hinten geneigt. Das ist besser von oben lesbar, wenn man auf die Platte herabsieht. Es ist nicht mehr senkrecht und {de(d3['depth'] - d2['depth'])} mm tiefer als E2.</p></div>
  </div>
  <div class="card"><h3>Vergleich</h3>
    <div class="scroll"><table>
      <thead><tr><th>Entwurf</th><th>Mulde B × T</th><th>Fenster über Platte</th><th>Höhe gesamt</th><th>Kabelraum</th><th>Lage am Ostrand</th></tr></thead>
      <tbody>
        <tr><td>E1 kompakt</td><td class="num">{de(d1['w'])} × {de(d1['depth'])}</td><td class="num">{de(sc['E1']['win_bottom'])} bis {de(sc['E1']['win_bottom'] + L.WIN_H)}</td><td class="num">{de(sc['E1']['top'])}</td><td>keiner, Adern gerade nach oben</td><td class="num">{iv('E1')}</td></tr>
        <tr class="sel"><td>E2 Display vorn</td><td class="num">{de(d2['w'])} × {de(d2['depth'])}</td><td class="num">{de(sc['E2']['win_bottom'])} bis {de(sc['E2']['win_bottom'] + L.WIN_H)}</td><td class="num">{de(sc['E2']['top'])}</td><td>4 mm, Adern angelötet</td><td class="num">{iv('E2')}</td></tr>
        <tr><td>E3 Pult 15°</td><td class="num">{de(d3['w'])} × {de(d3['depth'])}</td><td class="num">{de(sc['E3']['win_bottom'])} bis {de(sc['E3']['win_bottom'] + L.WIN_H * math.cos(math.radians(D.TILT_DEG)))}</td><td class="num">{de(sc['E3']['top'])}</td><td>4 mm</td><td class="num">{iv('E3')}</td></tr>
      </tbody></table></div></div>
</section>

<section aria-labelledby="h-in">
  <h2 id="h-in">Innen: Platz für die Kabel</h2>
  <ul>
    <li><b>Dock:</b> Die Winkelleiste wird wie bei den Gebäuden unter die flache Plattenunterseite geklebt (Körper 2,0 mm, Lötenden 6,3 mm nach Westen). Die Dockzone ist 14,9 × 11,1 mm und bleibt frei von Stützen.</li>
    <li><b>Steckerraum:</b> Unter der Platte liegen 3,5 mm Luft. Die vier Adern vom ESP-Feld hängen dort ab und laufen quer über den leeren Boden des Unterkastens (17,4 mm hoch). Im Südosten liegt keine Powerbank und kein anderes Dock.</li>
    <li><b>Stützen:</b> {posts_txt}</li>
    <li><b>Im Fuß:</b> Die Adern gehen vom Display über den 4 mm breiten Kabelraum nach oben zur Kassette (etwa 25 mm lang, Silikon-Litze 28 AWG). Der Raum ist offen und wird von einem Deckel geschlossen, damit sich das Modul wechseln lässt.</li>
    <li><b>Dupont am Display:</b> Wer das Modul steckbar halten will, braucht hinter der Platine etwa 17 mm statt 4 mm. Dann wird E2 {de(d2d['depth'])} mm tief und passt nur noch bei {iv('E2D')}.</li>
  </ul>
</section>

<section aria-labelledby="h-vor">
  <h2 id="h-vor">Gehäuse anderer Leute</h2>
  <p>Die Recherche hat zehn passende Gehäuse für OLEDs gefunden. Wir übernehmen Ideen und konstruieren das Teil selbst, deshalb spielt die Lizenz nur beim Anschauen eine Rolle. Gelesen wurden die Beschreibungen, nicht die STL-Dateien.</p>
  <div class="scroll"><table>
    <thead><tr><th>Modell</th><th>Urheber, Lizenz</th><th>Bauform</th><th>Was wir mitnehmen</th></tr></thead>
    <tbody>
      <tr><td><a href="https://www.printables.com/model/1632052">Desktop case for 0.96 inch OLED</a></td><td>prwiley, CC BY</td><td>Frontplatte, Korpus, Rückdeckel; OLED mit 2-mm-Schrauben an der Frontplatte</td><td>Rückdeckel mit Reibsitz und Öffnung unten für die Dupont-Kabel</td></tr>
      <tr><td><a href="https://www.printables.com/model/1172417">Gridfinity 1x1 OLED</a></td><td>JimleeQ, CC BY-SA</td><td>Frontplatte, M2-Senkschrauben, Panel per Click-Fit in Rippen</td><td>Kabelschlitz oben, Buchsen bündig in der Fläche</td></tr>
      <tr><td><a href="https://www.printables.com/model/1634063">0.96 SSD1306 Snap-Fit Mounting Frame</a></td><td>POLYMXS, CC BY-NC</td><td>Frontrahmen, Modul von hinten eingeklickt, vorn nur die Pixelfläche sichtbar</td><td>Schnapphaken statt Schrauben</td></tr>
      <tr><td><a href="https://www.printables.com/model/407846">1.3 inch OLED display stand</a></td><td>Ravenwreck, CC BY-NC-SA</td><td>Ständer hoch oder quer für 1,3 Zoll, Kabeldurchführung seitlich</td><td>Lochraster 27 × 26,5 mm, Ø 1,5 mm als Vergleich für dein Modul</td></tr>
      <tr><td><a href="https://www.printables.com/model/59743">Simple holder 1.3 inch 128x64</a></td><td>maximilliampere, CC BY-NC</td><td>Halter mit 4 Schrauben von vorn, Gewichte im Boden</td><td>Lochraster 30,3 × 28,4 mm (SH1106)</td></tr>
      <tr><td><a href="https://www.printables.com/model/549344">OLED 0.96" Display Case</a></td><td>erin, CC BY</td><td>Panel in 22-mm-Bohrung, Schraubring, 4-poliger XH-Stecker innen</td><td>Zugentlastung der Adern mit Heißkleber</td></tr>
    </tbody></table></div>
  <p class="small muted">Nicht prüfbar waren Thingiverse, MakerWorld und Cults3D (Zugriff gesperrt). Eine Halterung nach dem Muster „von vorn mit Fenster, Modul von hinten eingeschoben, Rückdeckel“ kommt in mehreren Modellen vor und liegt unserem E2 am nächsten. Die Lochlage des Moduls schwankt von Charge zu Charge, deshalb kommt der Plan mit Spiel und Messung aus.</p>
</section>

<section aria-labelledby="h-chain">
  <h2 id="h-chain">Maßkette im Worst-Case (E2 in der Südost-Ecke)</h2>
  <div class="scroll"><table>
    <thead><tr><th>Maß</th><th>Soll</th><th>Worst-Case</th><th>Ergebnis</th><th>Quelle</th></tr></thead>
    <tbody>
      <tr><td>Breite der Mulde</td><td class="num">35,5 + 2 × (0,3 + 1,2) = {de(d2['w'])}</td><td class="num">Platine 36,0: Spiel 0,05 bis 0,55</td><td><span class="pill mid">messen</span></td><td class="src">S, Schwestermodul −79</td></tr>
      <tr><td>Tiefe der Mulde</td><td class="num">{de(L.SLAB)} + 4,0 + {de(L.KD)} = {de(d2['depth'])}</td><td class="num">Modulpaket 5,0 statt 4,5: +0,5</td><td><span class="pill mid">messen</span></td><td class="src">S</td></tr>
      <tr><td>Fußtiefe</td><td class="num">14,2, Muldenboden 0,4</td><td class="num">Druckmaß ± 0,1</td><td><span class="pill ok">bewährt</span></td><td class="src">Plan Campus</td></tr>
      <tr><td>Unterkante der Platine</td><td class="num">{de(sc['E2']['mod_b'])} unter der Platte, Boden darunter {de(14.2 + sc['E2']['mod_b'])}</td><td class="num">Platine 32,3: Fenster 0,3 höher</td><td><span class="pill ok">frei</span></td><td class="src">A</td></tr>
      <tr><td>Fenster</td><td class="num">{de(sc['E2']['win_bottom'])} bis {de(sc['E2']['win_bottom'] + L.WIN_H)} über der Platte, Rand 0,4 um die aktive Fläche</td><td class="num">Abstand Rand bis aktive Fläche 5,0 ± 0,5: Rand 0 bis 0,9</td><td><span class="pill mid">messen, Rand klein</span></td><td class="src">S</td></tr>
      <tr><td>Kassette</td><td class="num">V2-Unterbau 13,2 × 5,6, ohne Streifen, Oberkante 2,9 über der Platte</td><td class="num">wie V2</td><td><span class="pill mid">V2 ungetestet</span></td><td class="src">E, Konzept r4</td></tr>
      <tr><td>Abstand zur Plattenkante</td><td class="num">4,1 (verlangt 3,5)</td><td class="num">Randfase 1,5 + Wand 2,0</td><td><span class="pill ok">frei</span></td><td class="src">E</td></tr>
      <tr><td>Abstand zur Schrift</td><td class="num">Mulde ab y = {de(y_a - d2['w'] / 2)}, Schrift bis y ≈ 13</td><td class="num">Schrift 0,6 erhaben</td><td><span class="pill ok">frei</span></td><td class="src">A, aus generate.py</td></tr>
    </tbody></table></div>
</section>

<section aria-labelledby="h-dec">
  <h2 id="h-dec">Entscheidungen</h2>
  <div class="dec">
    <div class="card rec"><h3><span class="tag">A</span> Entwurf</h3><div class="opts">
      <div class="opt pick"><b>E2 Display vorn, Block dahinter</b><span class="num2">{de(d2['w'])} × {de(d2['depth'])} mm, Fenster ab {de(sc['E2']['win_bottom'])}, senkrecht, wie beschrieben. Empfohlen.</span></div>
      <div class="opt"><b>E1 kompakt</b><span class="num2">{de(d1['w'])} × {de(d1['depth'])} mm, Fenster ab {de(sc['E1']['win_bottom'])}; lässt sich weit nach Norden schieben, aber nicht tief unten.</span></div>
      <div class="opt"><b>E3 Pult 15°</b><span class="num2">{de(d3['depth'])} mm tief, besser von oben lesbar, nicht senkrecht.</span></div></div></div>
    <div class="card rec"><h3><span class="tag">B</span> Lage</h3><div class="opts">
      <div class="opt pick"><b>Südost-Ecke, Mitte bei y = {de(y_a, 0)} mm</b><span class="num2">Am Ostrand, über der Schrift, nichts davor. Empfohlen.</span></div>
      <div class="opt"><b>Ostrand weiter nördlich (nur E1)</b><span class="num2">bis y = {de(I('E1')[0][1], 0)} mm, dann steht die Stele vor dem Hochhaus-Bogen.</span></div>
      <div class="opt"><b>Südwest oder Nordost</b><span class="num2">geht nicht, siehe Karte.</span></div></div></div>
    <div class="card"><h3><span class="tag">C</span> Anschluss am Display</h3><div class="opts">
      <div class="opt pick"><b>Adern direkt anlöten</b><span class="num2">Kabelraum 4 mm. Empfohlen, wenn das Modul nicht oft herauskommt.</span></div>
      <div class="opt"><b>Dupont-Buchse auf den Header</b><span class="num2">Modul tauschbar, Stele wird {de(d2d['depth'])} mm tief und passt nur bis y = {de(I('E2D')[0][1], 0)}.</span></div>
      <div class="opt"><b>Winkelleiste auf die Platine</b><span class="num2">etwa 8 mm Kabelraum, ungeplant, Löten am Modul nötig.</span></div></div></div>
    <div class="card"><h3><span class="tag">D</span> Halt des Moduls</h3><div class="opts">
      <div class="opt pick"><b>Schnapphaken und Rückdeckel</b><span class="num2">Kein Lochraster nötig, unempfindlich gegen Lochlage. Vorschlag.</span></div>
      <div class="opt"><b>Zwei Schrauben M2</b><span class="num2">nur mit gemessener Lochlage; die Löcher sind auf dem Foto etwa 3 mm groß.</span></div>
      <div class="opt"><b>Klemmen und kleben</b><span class="num2">einfachster Druck, Modul schwer zu wechseln.</span></div></div></div>
    <div class="card"><h3><span class="tag">E</span> Shunt des INA226</h3><div class="opts">
      <div class="opt pick"><b>0,05 Ω (zweiten 0,1-Ω-Widerstand parallel)</b><span class="num2">bis 1,64 A. Empfohlen.</span></div>
      <div class="opt"><b>0,1 Ω lassen</b><span class="num2">bis 0,82 A, Helligkeit im Programm begrenzen.</span></div></div></div>
    <div class="card"><h3><span class="tag">F</span> Neigung</h3><div class="opts">
      <div class="opt pick"><b>senkrecht</b><span class="num2">wie gewünscht; der OLED hat einen weiten Blickwinkel.</span></div>
      <div class="opt"><b>10° bis 15° nach hinten</b><span class="num2">nur bei E3.</span></div></div></div>
  </div>
</section>

<section aria-labelledby="h-next">
  <h2 id="h-next">Nächste Schritte</h2>
  <ol class="todo">
    <li><b>Du:</b> Modul messen (Liste oben) und ein Foto der Vorderseite schicken. Entscheidungen A bis F abnicken.</li>
    <li><b>Danach ich:</b> Werte in <code>plug/display/params.py</code> festschreiben, Generator <code>plug/display/build.py</code> für die Stele, ein Probestück (Mini-Platte mit Mulde und Dock, die Stele, Deckel) mit Prüfbericht, Testbogen.</li>
    <li><b>Platte:</b> <code>plug/campus.py</code> um das siebte Dock erweitern (Mulde, vier Pin-Löcher), im Unterkasten die Stützen aus der Dockzone nehmen, ESP-Feld für ESP, INA226 und Pull-ups planen.</li>
    <li><b>Schaltplan:</b> eigene Seite mit Stückliste und Programmgerüst (Rolling-Plot, 128 Werte, Leistung und Wh).</li>
  </ol>
  <p class="small muted">Alle Modulmaße sind geschätzt (S) oder aus dem Datenblatt des Schwestermoduls. Gebäudehöhen für die Sichtlinie sind die jeweils höchsten Punkte, das ist konservativ. Quellen der Recherche: <a href="https://goldenmorninglcd.com/wp-content/uploads/2024/05/GME12864-70.pdf">Datenblatt GME12864-70</a>, <a href="https://goldenmorninglcd.com/oled-display/1.3-inch-oled-128x64-ch1116g-sh1106-gme12864-70/">Produktseite</a>.</p>
</section>
</div>
<script>{JS.replace('__DATA__', json.dumps(data, default=float, separators=(',', ':')))}</script>
"""
    # Hinweis: Reste des Konzept-Stylesheets (Umschalter etc.) kommen aus dem Kopf der Konzeptseite
    return head + body


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache")
    a = ap.parse_args()
    v = load(a.cache)
    html = page(v)
    open(OUT, "w", encoding="utf-8").write(html)
    print("geschrieben:", OUT, "%.0f KB" % (len(html) / 1024))


if __name__ == "__main__":
    main()
