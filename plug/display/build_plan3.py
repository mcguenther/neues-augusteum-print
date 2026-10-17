#!/usr/bin/env python3
"""Plan 3 Display-Gebäude: Körper E4 (Kopf über der Platte, Hals = Halter der Kassette, Rückenkeil mit rundem Kabelraum) als HTML mit
3D-Ansicht (Explosions- und Abziehregler, Aufschneiden) und Zeichnungen: plug/display/plan3.html.

Rückmeldung des Nutzers (2026-10-17): Header bleibt am Modul, 3 bis 4 cm Ader müssen im Körper Platz finden (runder Kanal, keine Kanten),
Schräge über der Kassette bis zur Oberkante, Display höher (5 bis 10 mm), Kopf ganz über der Platte mit der Kassette als Fuß, Breite nur am Display,
Fase unten wie bei den Gebäuden, Support ist erlaubt. Plan ohne STL, erst nach dem Abnicken.
    python3 -m plug.display.build_plan3 [--cache layout.json]
"""
import argparse
import base64
import json
import math
import os

import numpy as np
from shapely.geometry import Polygon, box
from shapely.ops import polylabel

from plug.display import body4
from plug.display import figures3 as F3
from plug.display import layout as L
from plug.display import layout4 as L4
from plug.display import params as D
from plug.display.build_plan import CONCEPT_TEMPLATE, CSS_EXTRA, load
from plug.geom import to_tm

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "plan3.html")
de = lambda x, n=1: ("%.*f" % (n, x)).replace(".", ",")
P = D.DISP

CSS3 = """
.fig .foot { fill: var(--c-bld); stroke: var(--edge); stroke-width: .6; }
.fig .foot2 { fill: color-mix(in srgb, var(--c-bld) 55%, var(--panel)); stroke: var(--edge); stroke-width: .5; stroke-dasharray: 3 2; }
.fig .foot3 { fill: none; stroke: var(--edge); stroke-width: .8; stroke-dasharray: 4 2; }
.fig .lid { fill: var(--accent-fill); stroke: var(--edge); stroke-width: .6; fill-opacity: .9; }
.fig .blende { fill: var(--c-cut2); stroke: var(--edge); stroke-width: .6; fill-opacity: .85; }
.fig .kass { fill: var(--c-under); stroke: var(--edge); stroke-width: .6; }
.fig .pcb { fill: var(--c-elec); stroke: var(--edge); stroke-width: .6; }
.fig .glass { fill: color-mix(in srgb, var(--c-port) 60%, var(--panel)); stroke: var(--edge); stroke-width: .5; }
.fig .aa3 { fill: var(--accent-fill); stroke: none; }
.fig .hdr { fill: var(--c-port); stroke: var(--edge); stroke-width: .5; }
.fig .pin3 { fill: var(--accent-fill); stroke: var(--accent); stroke-width: .5; }
.fig .wire { stroke: var(--c-thread); stroke-width: 2.2; fill: none; stroke-linecap: round; stroke-linejoin: round; }
.fig .inv { fill: var(--panel); } .fig text.inv { fill: var(--panel); } .fig text.onfill { fill: #fff; }
.view3 { display: grid; grid-template-columns: minmax(0, 1fr) 260px; gap: 16px; align-items: start; }
@media (max-width: 900px) { .view3 { grid-template-columns: 1fr; } }
.stage3 { position: relative; width: 100%; aspect-ratio: 4 / 3; max-width: 100%; background: var(--canvas); border-radius: 6px; overflow: hidden; touch-action: none; }
.stage3 canvas { width: 100%; height: 100%; display: block; cursor: grab; }
.stage3 .tag { position: absolute; left: 10px; top: 10px; font-family: var(--mono); font-size: .8rem; background: color-mix(in srgb, var(--panel) 85%, transparent); color: var(--fg); padding: 3px 8px; border-radius: 4px; pointer-events: none; }
.side3 { display: flex; flex-direction: column; gap: 12px; min-width: 0; }
.side3 .field label { font-size: .92rem; }
.side3 .parts { display: flex; flex-direction: column; gap: 4px; font-size: .9rem; }
.side3 .parts label { display: flex; gap: 8px; align-items: center; cursor: pointer; }
.side3 .parts i { display: inline-block; width: 12px; height: 12px; border-radius: 2px; border: 1px solid color-mix(in srgb, var(--edge) 40%, transparent); }
.side3 .row { display: flex; flex-wrap: wrap; gap: 6px; }
.side3 .row button { font: inherit; font-size: .85rem; border: 1px solid var(--line); background: var(--panel); color: var(--fg); border-radius: 6px; padding: 4px 10px; cursor: pointer; }
.side3 .row button[aria-pressed=true] { background: var(--accent-fill); color: var(--on-accent); border-color: var(--accent-fill); }
.twofig { display: grid; grid-template-columns: minmax(0, 1.3fr) minmax(0, 1fr); gap: 16px; align-items: start; }
@media (max-width: 860px) { .twofig { grid-template-columns: 1fr; } }
.twofig svg { max-width: 100%; }
.qa { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 16px; }
.qa .card { gap: 6px; }
.qa .card h3 { font-size: 1rem; }
.qa .card p { font-size: .93rem; }
.qa .yes { font-family: var(--mono); font-size: .74rem; letter-spacing: .06em; color: var(--ok); text-transform: uppercase; }
.qa .mid { font-family: var(--mono); font-size: .74rem; letter-spacing: .06em; color: var(--mid); text-transform: uppercase; }
.mapcol { display: grid; grid-template-columns: minmax(0, 220px) minmax(0, 1fr); gap: 16px; align-items: start; }
@media (max-width: 720px) { .mapcol { grid-template-columns: 1fr; } }
.mini { width: 100%; height: auto; display: block; background: var(--canvas); border-radius: 6px; max-width: 240px; }
.mini .plate { fill: var(--c-plate); stroke: var(--edge); stroke-width: .6; }
.mini .bld { fill: var(--c-bld); stroke: var(--edge); stroke-width: .4; fill-opacity: .85; }
.mini .hof { fill: var(--c-hof); fill-opacity: .85; }
.mini .lbl { fill: var(--edge); fill-opacity: .12; }
.mini .v { fill: var(--c-thread); fill-opacity: .55; }
.mini .env { fill: var(--c-cut2); fill-opacity: .55; stroke: var(--c-cut2); stroke-width: 1; }
.mini .neck { fill: var(--accent-fill); stroke: var(--edge); stroke-width: .6; }
.mini .dock { fill: var(--c-niche); fill-opacity: .35; stroke: var(--c-niche); stroke-width: .6; }
"""


def b64(man):
    tm = to_tm(man)
    return base64.b64encode(np.asarray(tm.triangles, dtype="<f4").tobytes()).decode()


def mini_map(v, pl, xe, yc):
    S = 1.6
    W, Ln = v["plate"]
    pts = lambda poly: " ".join("%.1f,%.1f" % (x * S + 4, (Ln - y) * S + 4) for x, y in poly.exterior.coords)
    o = ['<rect x="4" y="4" width="%.1f" height="%.1f" class="plate"/>' % (W * S, Ln * S)]
    o.append('<rect x="4" y="%.1f" width="%.1f" height="%.1f" class="lbl"/>' % ((Ln - D.LABEL_Y + 2) * S + 4, W * S, (D.LABEL_Y - 2) * S))
    for b in pl.buildings.values():
        o.append('<polygon points="%s" class="bld"/>' % pts(b["poly"]))
    o.append('<polygon points="%s" class="hof"/>' % pts(pl.hof))
    for n in pl.notches:
        o.append('<polygon points="%s" class="v"/>' % pts(n.intersection(box(0, 0, W, Ln))))
    z, _ = L4.zone_at(xe, yc, "W")
    o.append('<polygon points="%s" class="dock"/>' % pts(z))
    o.append('<polygon points="%s" class="env"/>' % pts(L4.env_at(xe, yc)))
    o.append('<polygon points="%s" class="neck"/>' % pts(L4.mulde_at(xe, yc)))
    return '<svg class="mini" viewBox="0 0 %.0f %.0f" role="img" aria-label="Lage des Körpers E4 auf der Platte">%s</svg>' % (W * S + 8, Ln * S + 8, "".join(o))


JS = r"""
const DATA = __DATA__;
const b64 = (s) => { const bin = atob(s), u = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i); return new Float32Array(u.buffer); };
const css = (n) => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const canvas = document.getElementById('cv3'), stage = document.getElementById('stage3');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 2));
renderer.localClippingEnabled = true;
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(32, 1, 0.5, 4000);
camera.up.set(0, 0, 1);
scene.add(new THREE.HemisphereLight(0xffffff, 0x7a8696, 1.0));
const sun = new THREE.DirectionalLight(0xffffff, 0.6); scene.add(sun);
const fill = new THREE.DirectionalLight(0xffffff, 0.3); scene.add(fill);
const plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);   // behält y >= 0, die Schnittfläche zeigt nach Süden
const dark = () => { const t = document.documentElement.getAttribute('data-theme'); return t ? t === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches; };
const parts = {};
DATA.parts.forEach((p) => {
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(b64(p.tris), 3));
  g.computeVertexNormals();
  const m = new THREE.Mesh(g, new THREE.MeshStandardMaterial({ color: p.pal[0], roughness: 0.75, metalness: 0.0, side: THREE.DoubleSide }));
  scene.add(m); parts[p.id] = { m, p };
});
const wireMats = DATA.wire.colors.map((c) => new THREE.MeshStandardMaterial({ color: c[0], roughness: 0.6 }));
let wireMeshes = [];
const ui = { expl: document.getElementById('expl'), pull: document.getElementById('pull'), cut: document.getElementById('cut'), tag: document.getElementById('tag3') };
function offsets() {
  const e = +ui.expl.value / 100, pl = +ui.pull.value / 100;
  const off = {};
  DATA.parts.forEach((p) => {
    const o = [p.dir[0] * p.dist * e, p.dir[1] * p.dist * e, p.dir[2] * p.dist * e];
    if (p.id !== 'plate' && p.id !== 'leiste') o[2] += DATA.pull * pl;
    off[p.id] = o;
  });
  return { off, e, pl };
}
function wires(off, e, pl) {
  wireMeshes.forEach((w) => { scene.remove(w); w.geometry.dispose(); });
  wireMeshes = [];
  const base = DATA.wire.path, n = base.length;
  const S = [base[0][0], base[0][1]], E = [base[n - 1][0], base[n - 1][1]];
  const dc = off.cassette, dm = off.pcb;
  const k = Math.min(1, e * 2.2);
  DATA.wire.y.forEach((y, wi) => {
    const pts = base.map((q, i) => {
      const u = i / (n - 1);
      const ax = q[0], az = q[1] + DATA.pull * pl;
      const sx = S[0] + dc[0], sz = S[1] + dc[2], ex = E[0] + dm[0], ez = E[1] + dm[2];
      const tx = sx + (ex - sx) * u, tz = sz + (ez - sz) * u;
      return new THREE.Vector3(ax + (tx - ax) * k, y, az + (tz - az) * k);
    });
    const g = new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 90, 0.5, 6, false);
    const m = new THREE.Mesh(g, wireMats[wi]); scene.add(m); wireMeshes.push(m);
  });
}
function apply() {
  const { off, e, pl } = offsets();
  const cut = ui.cut.checked;
  DATA.parts.forEach((p) => {
    const o = off[p.id], mm = parts[p.id].m;
    mm.position.set(o[0], o[1], o[2]);
    mm.visible = document.getElementById('v_' + p.id).checked;
    mm.material.clippingPlanes = cut ? [plane] : [];
  });
  wires(off, e, pl);
  wireMats.forEach((m) => { m.clippingPlanes = cut ? [plane] : []; });
  const wv = document.getElementById('v_wire').checked; wireMeshes.forEach((w) => { w.visible = wv; });
  ui.tag.textContent = (cut ? 'aufgeschnitten · ' : '') + (e > 0.02 ? 'auseinander ' + Math.round(e * 100) + ' %' : 'zusammengebaut') + (pl > 0.02 ? ' · gezogen ' + Math.round(pl * DATA.pull) + ' mm' : '');
  draw();
}
function theme() {
  renderer.setClearColor(css('--canvas'));
  const d = dark() ? 1 : 0;
  DATA.parts.forEach((p) => parts[p.id].m.material.color.set(p.pal[d]));
  wireMats.forEach((m, i) => m.color.set(DATA.wire.colors[i][d]));
  draw();
}
const cam = { t: new THREE.Vector3(-12, 0, 8), d: 190, az: -38, el: 24 };
function place() {
  const a = cam.az * Math.PI / 180, e = cam.el * Math.PI / 180;
  camera.position.set(cam.t.x + cam.d * Math.cos(e) * Math.cos(a), cam.t.y + cam.d * Math.cos(e) * Math.sin(a), cam.t.z + cam.d * Math.sin(e));
  camera.lookAt(cam.t);
  sun.position.copy(camera.position).add(new THREE.Vector3(60, -40, 120)); fill.position.copy(camera.position).add(new THREE.Vector3(-80, 60, 20));
}
function draw() { place(); renderer.render(scene, camera); }
function resize() { const w = stage.clientWidth, h = stage.clientHeight; renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix(); draw(); }
let anim = null;
function goTo(v) {
  const from = { x: cam.t.x, y: cam.t.y, z: cam.t.z, d: cam.d, az: cam.az, el: cam.el };
  let daz = v.az - from.az; daz = ((daz + 540) % 360) - 180;
  const t0 = performance.now(), dur = matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : 600;
  cancelAnimationFrame(anim);
  const step = (now) => {
    const k = dur ? Math.min(1, (now - t0) / dur) : 1, s = k * k * (3 - 2 * k);
    cam.t.set(from.x + (v.t[0] - from.x) * s, from.y + (v.t[1] - from.y) * s, from.z + (v.t[2] - from.z) * s);
    cam.d = from.d + (v.d - from.d) * s; cam.az = from.az + daz * s; cam.el = from.el + (v.el - from.el) * s;
    draw(); if (k < 1) anim = requestAnimationFrame(step);
  };
  anim = requestAnimationFrame(step);
}
const views = document.getElementById('views3');
DATA.views.forEach((v, i) => {
  const b = document.createElement('button'); b.type = 'button'; b.textContent = v.name; b.setAttribute('aria-pressed', i === 0);
  b.onclick = () => { [...views.children].forEach((c, j) => c.setAttribute('aria-pressed', j === i)); goTo(v); };
  views.appendChild(b);
});
const plist = document.getElementById('plist');
DATA.parts.concat([{ id: 'wire', label: 'Adern', pal: DATA.wire.colors[0] }]).forEach((p) => {
  const l = document.createElement('label');
  l.innerHTML = '<input type="checkbox" id="v_' + p.id + '" checked><i style="background:' + p.pal[0] + '"></i>' + p.label;
  l.firstChild.addEventListener('input', apply); plist.appendChild(l);
});
['expl', 'pull', 'cut'].forEach((k) => ui[k].addEventListener('input', apply));
const ptrs = new Map(); let pinch = 0;
canvas.addEventListener('contextmenu', (e) => e.preventDefault());
canvas.addEventListener('pointerdown', (e) => { canvas.setPointerCapture(e.pointerId); ptrs.set(e.pointerId, [e.clientX, e.clientY]); pinch = 0; cancelAnimationFrame(anim); });
canvas.addEventListener('pointerup', (e) => ptrs.delete(e.pointerId));
canvas.addEventListener('pointercancel', (e) => ptrs.delete(e.pointerId));
canvas.addEventListener('pointermove', (e) => {
  if (!ptrs.has(e.pointerId)) return;
  const prev = ptrs.get(e.pointerId); ptrs.set(e.pointerId, [e.clientX, e.clientY]);
  const dx = e.clientX - prev[0], dy = e.clientY - prev[1];
  if (ptrs.size === 2) {
    const [p, q] = [...ptrs.values()]; const dist = Math.hypot(p[0] - q[0], p[1] - q[1]);
    if (pinch) cam.d = Math.min(600, Math.max(30, cam.d * pinch / dist));
    pinch = dist; panBy(dx / 2, dy / 2);
  } else if (e.shiftKey || e.buttons === 2) panBy(dx, dy);
  else { cam.az -= dx * 0.4; cam.el = Math.max(-89, Math.min(89, cam.el + dy * 0.4)); }
  draw();
});
function panBy(dx, dy) {
  const k = cam.d * 0.0016, a = cam.az * Math.PI / 180, e = cam.el * Math.PI / 180;
  const right = new THREE.Vector3(-Math.sin(a), Math.cos(a), 0);
  const up = new THREE.Vector3(-Math.sin(e) * Math.cos(a), -Math.sin(e) * Math.sin(a), Math.cos(e));
  cam.t.addScaledVector(right, -dx * k).addScaledVector(up, dy * k);
}
canvas.addEventListener('wheel', (e) => { e.preventDefault(); cam.d = Math.min(600, Math.max(30, cam.d * Math.exp(e.deltaY * 0.0012))); draw(); }, { passive: false });
new ResizeObserver(resize).observe(stage);
matchMedia('(prefers-color-scheme: dark)').addEventListener('change', theme);
new MutationObserver(theme).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
theme(); apply(); goTo(DATA.views[0]);
"""


def page(v):
    d = body4.dims()
    parts, aux = body4.parts(d)
    pl = L4.Plate4(v)
    sc = L4.scan4(pl)
    iv = sc["intervals"]
    ivs = ", ".join("y %s bis %s" % (de(a, 0), de(b, 0)) for a, b in iv)
    y_mid = (iv[0][0] + iv[0][1]) / 2 if iv else 47.0
    # Kammer: größter Kreis und Luft
    ch = aux["chamber"]
    pt = polylabel(ch, tolerance=0.05)
    r_max = ch.exterior.distance(pt)
    from shapely.geometry import LineString
    xs = d["x_s0"] + 1.5
    seg = ch.intersection(LineString([(xs, d["z_cass"] - 1), (xs, d["z_top"] + 1)]))
    air_rear = seg.bounds[3] - d["z_cass"] if not seg.is_empty else 0.0
    # Länge einer Ader bei Löten mit 35 mm Abstand vor der Ostfläche: Hals-Mitte bis Ostfläche plus 35 plus 5 für die Höhe
    solder_len = d["pe"] + 35.0 + 5.0
    straight = math.hypot(-d["x_tip"] + d["x_s0"] / 2 + d["x_s1"] / 2 + 0.6, d["z_pins"] - d["z_cass"])
    reserve = solder_len - straight
    head = open(CONCEPT_TEMPLATE, encoding="utf-8").read().split('<div class="wrap">')[0]
    head = head.replace("<title>Powerbank in der Grundplatte</title>", "<title>Plan 3 Display-Gebäude</title>\n<meta name=\"description\" content=\"Display-Körper mit Kopf über der Platte, Rückenkeil und 3D-Ansicht\">")
    head = head.replace("</style>", CSS_EXTRA + CSS3 + "</style>")
    nx, nz = aux["normal"]
    pal = dict(
        body=("#e6dfcb", "#cfc7b0"), lid=("#f0a21a", "#f2b441"), blende=("#5b4a7a", "#8d73b8"), cassette=("#5f7086", "#7d8ea6"),
        pcb=("#2f7d4f", "#4c9a69"), glass=("#3a3f44", "#59616a"), aa=("#f4c36a", "#f2b441"), header=("#1f2326", "#8a9299"), pins=("#d4a017", "#e3b54a"),
        plate=("#8fa3b8", "#5d7087"), leiste=("#2d3236", "#8a9299"))
    labels = dict(body="Körper", lid="Rückdeckel", blende="Frontblende", cassette="Kassette", pcb="Modul, Platine", glass="Modul, Glas", aa="aktive Fläche",
                  header="Header", pins="Pins", plate="Platte (Ausschnitt)", leiste="Winkelleiste")
    dirs = dict(body=(0, 0, 0, 0), lid=(nx, 0, nz, 30.0), blende=(1, 0, 0, 30.0), cassette=(0, 0, -1, 28.0),
                pcb=(1, 0, 0, 60.0), glass=(1, 0, 0, 60.0), aa=(1, 0, 0, 60.0), header=(1, 0, 0, 60.0), pins=(1, 0, 0, 60.0), plate=(0, 0, 0, 0), leiste=(0, 0, 0, 0))
    order = ["plate", "leiste", "body", "cassette", "lid", "blende", "glass", "pcb", "aa", "header", "pins"]
    data = dict(
        parts=[dict(id=k, label=labels[k], tris=b64(parts[k]), pal=list(pal[k]), dir=list(dirs[k][:3]), dist=dirs[k][3]) for k in order],
        pull=34.0,
        wire=dict(path=[[round(x, 2), round(z, 2)] for x, z in F3._smooth(aux["wire"], 8)], y=[-1.9, -0.65, 0.65, 1.9],
                  colors=[["#d9423b", "#ff7a6e"], ["#2b2b2b", "#aab0b6"], ["#e3c030", "#f0d060"], ["#3b82d9", "#6aa5f0"]]),
        views=[dict(name="Schräg hinten", t=[-12, 0, 8], d=190, az=-140, el=26), dict(name="Schräg vorn", t=[-12, 0, 8], d=190, az=-38, el=24),
               dict(name="Vorn", t=[-12, 0, 12], d=170, az=0, el=6), dict(name="Seite, Schnitt", t=[-12, 0, 8], d=170, az=-90, el=2),
               dict(name="Von oben", t=[-12, 0, 0], d=190, az=0, el=88)])
    sec = F3.section(parts, aux, d)
    plan = F3.plan(parts, aux, d)
    mini = mini_map(v, pl, L.EAST_XE, y_mid)
    html = f"""<div class="wrap">
<header>
  <div class="kicker">Steckmechanismus · Display-Gebäude · Plan 3, noch nicht abgenickt</div>
  <h1>Display-Gebäude: Kopf über der Platte</h1>
  <p class="lead">Das Display sitzt jetzt ganz über der Platte, der Fuß in der Mulde ist nur noch der Halter der Kassette. Hinter dem Display wächst ein Rückenkeil mit rundem Kabelraum, den ein schräger Rückdeckel schließt. Die Pins bleiben am Modul. Dieser Plan hat eine 3D-Ansicht zum Auseinandernehmen und zum Aufschneiden. Erst nach deinem Okay entstehen STL.</p>
</header>

<section aria-labelledby="h-3d">
  <h2 id="h-3d">3D-Ansicht zum Auseinandernehmen</h2>
  <p>Ziehen dreht die Ansicht, Umschalt oder rechte Maustaste verschiebt sie, das Mausrad zoomt. Mit dem ersten Regler fasst du die Teile einzeln heraus (Kassette nach unten, Rückdeckel schräg, Frontblende und Modul nach vorn), mit dem zweiten ziehst du den ganzen Körper aus der Platte. Die Adern zeigen eine Schleife von etwa 32 mm als Beispiel; die Kammer hat Platz für mehr, die echte Lage entsteht beim Einschieben.</p>
  <div class="view3">
    <div class="card"><div class="stage3" id="stage3"><canvas id="cv3" aria-label="3D-Ansicht des Display-Körpers"></canvas><div class="tag" id="tag3"></div></div></div>
    <div class="card side3">
      <div><b class="small">Ansicht</b><div class="row" id="views3" role="group" aria-label="Ansicht"></div></div>
      <div class="field"><label for="expl">Auseinandernehmen</label><span class="num" id="explv"></span><input type="range" id="expl" min="0" max="100" step="1" value="0"></div>
      <div class="field"><label for="pull">Aus der Platte ziehen</label><span class="num" id="pullv"></span><input type="range" id="pull" min="0" max="100" step="1" value="0"></div>
      <label class="small"><input type="checkbox" id="cut"> Aufschneiden (Schnitt durch die Mitte, Ansicht von Süden)</label>
      <div><b class="small">Teile</b><div class="parts" id="plist"></div></div>
    </div>
  </div>
</section>

<section aria-labelledby="h-qa">
  <h2 id="h-qa">Deine Punkte, kurz beantwortet</h2>
  <div class="qa">
    <div class="card"><span class="yes">sinnvoll</span><h3>Gehäuse ganz über die Platte, Fuß = Halter der Kassette</h3>
      <p>Ja, das ist der Vorschlag E4. In die Platte taucht nur der Hals: Mulde <span class="num">{de(d['NW'] + 0.2)} × {de(d['KD'] + 0.2)}</span> statt {de(d['W'])} × 19,9. Der Unterbau bleibt wie bei den anderen Docks. Die Adern liegen höher und müssen sich kaum biegen. Der Preis: Der Kopf hängt in der Luft (Support beim Druck) und darf nicht über Hof, Gebäude und Schrift ragen. Er hält an der Kassette im Dock, wiegt aber nur wenige Gramm.</p></div>
    <div class="card"><span class="yes">gelöst</span><h3>3 bis 4 cm Ader müssen irgendwohin</h3>
      <p>In den Rückenkeil: Hinter der Rückwand des Moduls liegt eine Kammer, die nach oben mit der Schräge wächst. Der größte Kreis darin hat einen Radius von <span class="num">{de(r_max)} mm</span>. Eine Schleife mit Radius 6 mm nimmt 38 mm Ader auf, zwei Windungen also etwa 75 mm. Das reicht für die etwa {de(reserve, 0)} mm Reserve beim Anlöten mit 35 mm Abstand.</p></div>
    <div class="card"><span class="yes">gelöst</span><h3>Alles rund, keine Kanten im Kanal</h3>
      <p>Das Profil der Kammer in der Biegeebene ist mit Radius {de(D.ROUND_R, 0)} mm gerundet, die Ecken des Kabelfensters mit 1,5 mm. Die Adern biegen sich nur in dieser Ebene. Die Seitenwände sind eben und berühren die Adern nicht.</p></div>
    <div class="card"><span class="yes">gelöst</span><h3>Schräge bis zur Oberkante</h3>
      <p>Der Rückdeckel läuft von der Oberkante über der Kassette ({de(d['z_rear'])} mm über der Platte, {de(D.AIR)} mm Luft) schräg hoch bis zur Oberkante des Gehäuses ({de(d['z_top'])} mm). Die Luft über der Kassette beträgt am hinteren Ende der Kammer mindestens {de(air_rear)} mm und nimmt nach vorn zu.</p></div>
    <div class="card"><span class="yes">umgesetzt</span><h3>Display höher</h3>
      <p>Das Sichtfenster beginnt <span class="num">{de(d['wb'])} mm</span> über der Platte, die Unterkante der Platine {de(d['mb'])} mm. Weil unter dem Fenster noch {de(L.BELOW_WINDOW)} mm Platine liegen, ist das die tiefste Lage, bei der der Kopf ganz über der Platte bleibt. Fenster ab 5 mm hieße, dass der Kopf 4,7 mm in die Platte tauchen müsste, also wieder die große Mulde.</p></div>
    <div class="card"><span class="yes">umgesetzt</span><h3>Breite nur am Display</h3>
      <p>Der Kopf ist {de(d['W'])} mm breit. Dahinter verjüngt sich der Körper kantig in der Draufsicht bis auf die Breite der Kassette, {de(d['NW'])} mm. Der Keil hinter dem Kopf braucht deshalb keine {de(d['W'])} mm.</p></div>
    <div class="card"><span class="yes">umgesetzt</span><h3>Pins am Modul bleiben</h3>
      <p>Die Adern werden an die Pinenden gelötet. Die Stiftspitzen liegen laut Zeichnung des Schwestermoduls {de(D.PIN_TIP)} mm hinter der Glasfront, also {de(-d['x_tip'])} mm hinter der Frontblende. Die Kassette steht {de(D.PIN_CLEAR)} mm dahinter. <b>Die Pinlänge deines Moduls bitte prüfen</b>, sie ändert diese Lage.</p></div>
    <div class="card"><span class="mid">gefunden</span><h3>Fase unten am Hals</h3>
      <p>In <code>main</code> (<code>plug/buildings.py</code>, aus dem Zweig <code>claude/jolly-pascal-853ju9</code> über PR 23 eingegangen und in diesen Zweig gemergt): Fuß mit Fase <code>EF_CH_T</code> 0,5 an der Bettkante, Einführfase <code>ENTRY_CH_T</code> 0,5 am Schacht. Im Zweig <code>claude/gebaeude-fit-test-plan-39bfbt</code> steht eine Fuß-Fase von 2,0 mm für den Passform-Stummel (Patch <code>plug/footfit/buildings_fuss_fase.patch</code>), noch nicht in <code>main</code> und ungetestet. Für den Hals schlage ich {de(D.FOOT_CH)} mm vor.</p></div>
  </div>
</section>

<section aria-labelledby="h-sec">
  <h2 id="h-sec">Schnitt und Draufsicht</h2>
  <div class="twofig">
    <div class="card"><h3>Längsschnitt durch die Mitte</h3><div class="scroll">{sec}</div>
      <p class="small muted">Osten rechts. Der Kopf (Frontblende violett, Modul grün) hängt über der Platte, der Hals mit der Kassette (dunkelblau) steckt in der Mulde. Gelb der schräge Rückdeckel, rot eine mögliche Lage der Adern mit Schleife in der Kammer.</p></div>
    <div class="card"><h3>Draufsicht</h3><div class="scroll">{plan}</div>
      <p class="small muted">Umrisse in 5 mm (ausgefüllt), 20 mm (gestrichelt) und im Fuß (blass). Der Kopf ist am breitesten, der Hals hinten so breit wie die Kassette.</p></div>
  </div>
</section>

<section aria-labelledby="h-kab">
  <h2 id="h-kab">Kabelreserve</h2>
  <ul>
    <li><b>Länge:</b> Du lötest mit etwa 35 mm Abstand vor der Ostfläche. Dann braucht jede Ader vom Schacht aus etwa {de(solder_len, 0)} mm, weil der Hals {de(d['pe'], 0)} mm hinter der Front sitzt. Zusammengebaut liegen Kassettenoberkante und Stiftspitzen nur etwa {de(straight, 0)} mm auseinander. Es bleiben etwa {de(reserve, 0)} mm Reserve in der Kammer, mehr als deine geschätzten 3 bis 4 cm. Lötest du mit 20 mm Abstand, sind es etwa {de(reserve - 15, 0)} mm.</li>
    <li><b>Platz:</b> Die Kammer fasst sie als Schleife. Ein Radius von 6 mm liegt weit über dem Biegeradius von 28-AWG-Silikonlitze (etwa 3 mm).</li>
    <li><b>Einschieben:</b> Beim Schieben des Moduls von vorn in die Tasche klappt die Reserve von selbst nach hinten durch das Kabelfenster in die Kammer. Du hilfst mit einem Stäbchen durch die offene Rückseite (Rückdeckel ab).</li>
    <li><b>Rückdeckel:</b> Er liegt bündig in der Schräge, ist {de(D.LID_W)} mm breit und {de(D.WALL)} mm dick und wird liegend gedruckt. Zwei Haken am hinteren Ende und zwei Zapfen oben halten ihn, wie bei der Deckplatte der Fachprobe, die nur aufgelegt wackelte.</li>
  </ul>
</section>

<section aria-labelledby="h-map">
  <h2 id="h-map">Lage auf der Platte</h2>
  <div class="mapcol">
    <div class="card">{mini}<p class="small muted">Körper E4 am Ostrand bei y = {de(y_mid, 0)} mm.</p></div>
    <div class="card"><h3>Was am Ostrand geht</h3>
      <p>Der Körper (Kopf {de(d['W'])} mm breit, {de(d['depth'])} mm tief) braucht {de(L4.AIR_MARGIN)} mm Abstand zu Gebäuden, Hof und Schrift, weil der Kopf in der Luft darüber liegt. Am Ostrand passt er bei <b class="num">{ivs}</b> (Mitte des Kopfs von der Südkante). Das ist mehr als beim versenkten Körper E2 (y 37 bis 46), weil nur der schmale Hals bis in die Nähe des Hochhaus-Bogens reicht.</p>
      <p class="small muted">Die Mulde des Halses misst {de(d['NW'] + 0.2)} × {de(d['KD'] + 0.2)} mm, ihre Mitte liegt {de(d['pe'])} mm hinter der Ostfläche des Kopfs. Die Dockzone (14,9 × 11,1 mm) bleibt frei von Stützen. Die Südgrenze y = 37 kommt aus der Schrift (Kopf an der Unterkante 0,3 mm, Schrift 0,6 mm hoch) und der Fadenkerbe in der Ecke.</p></div>
  </div>
</section>

<section aria-labelledby="h-teile">
  <h2 id="h-teile">Teile, Druck und Zusammenbau</h2>
  <div class="scroll"><table>
    <thead><tr><th>Teil</th><th>Maße</th><th>Drucklage</th><th>Anmerkung</th></tr></thead>
    <tbody>
      <tr><td><b>1 Körper</b></td><td class="num">{de(d['W'])} × {de(d['depth'])} × {de(d['z_top'] - d['foot'])}</td><td>stehend, Hals unten auf dem Bett, <b>mit Support</b> unter dem Kopf</td><td>Hals mit Fase {de(D.FOOT_CH)} unten (Schacht mit Einführfase), Tasche von vorn offen, Rückenkeil mit offener Kammer unter der Schräge (Wand lehnt höchstens 31° über Luft, kein Support nötig). Support nur unter dem Kopf: Tree-Support bis auf das Bett, Kontakt nur an der Kopfunterseite.</td></tr>
      <tr><td><b>2 Rückdeckel</b></td><td class="num">{de(D.LID_W)} × 31,9 × {de(D.WALL)}</td><td>liegend</td><td>Schräge Wand, bündig im Körper, Haken und Zapfen noch zu zeichnen.</td></tr>
      <tr><td><b>3 Frontblende</b></td><td class="num">{de(d['W'])} × {de(d['z_top'] - d['z_hb'])} × {de(D.BLENDE_T)}</td><td>liegend, Außenseite unten</td><td>Sichtfenster {de(P['aa_w'] + 2 * D.WINDOW_MARGIN)} × {de(P['aa_h'] + 2 * D.WINDOW_MARGIN)} als glattes Loch. Klickt von vorn in die Tasche.</td></tr>
      <tr><td><b>4 Kassette</b></td><td class="num">{de(D.KASS_W)} × {de(D.KASS_D)} × 17,1</td><td>stehend</td><td>Unterbau der V2 ohne Blatt und Streifen, neu zu zeichnen.</td></tr>
      <tr><td>Kaufteile</td><td colspan="3">Modul mit Header, vier Silikon-Adern 28 AWG (etwa 60 mm), Dupont-Buchse 4-polig mit Kontakten, Winkelleiste für das Dock.</td></tr>
    </tbody></table></div>
  <ol class="todo">
    <li><b>Kassette bestücken:</b> Buchse mit vier Adern (60 mm) crimpen und in die Kassette drücken.</li>
    <li><b>Kassette von unten in den Hals schieben:</b> Die Adern kommen oben in die Kammer. Rückdeckel ist ab. Du ziehst die Adern durch das Kabelfenster in die Tasche und vorn heraus.</li>
    <li><b>Adern an die Pinenden löten:</b> Das Modul liegt etwa 35 mm vor dem Körper. Header bleibt, die Adern kommen an die Pinenden hinten.</li>
    <li><b>Modul von vorn in die Tasche schieben:</b> Die Reserve legt sich in der Kammer ab (Stäbchen von hinten).</li>
    <li><b>Rückdeckel einsetzen und Frontblende von vorn einklicken.</b></li>
    <li><b>Körper in die Mulde stecken</b> (Kassette auf die Pins der Winkelleiste), danach I²C-Scan.</li>
  </ol>
</section>

<section aria-labelledby="h-chain">
  <h2 id="h-chain">Maßkette im Worst-Case</h2>
  <div class="scroll"><table>
    <thead><tr><th>Maß</th><th>Soll</th><th>Worst-Case</th><th>Ergebnis</th><th>Quelle</th></tr></thead>
    <tbody>
      <tr><td>Fenster über der Platte</td><td class="num">{de(d['wb'])} bis {de(d['wt'])}</td><td class="num">Platine ± 0,5: ± 0,5</td><td><span class="pill mid">Maße nachliefern</span></td><td class="src">Nutzer, Foto</td></tr>
      <tr><td>Kopfunterkante</td><td class="num">{de(d['z_hb'])} über der Platte</td><td class="num">Schrift 0,6, Hof 1,9 hoch</td><td><span class="pill ok">nur außerhalb der Schriftzone</span></td><td class="src">A</td></tr>
      <tr><td>Stiftspitzen bis Kassettensäule</td><td class="num">{de(D.PIN_CLEAR)}</td><td class="num">Pins 0,5 länger: 3,0</td><td><span class="pill mid">Pinlänge prüfen</span></td><td class="src">Zeichnung -79</td></tr>
      <tr><td>Luft über der Kassette</td><td class="num">{de(D.AIR)} (hinten ≥ {de(air_rear)})</td><td class="num">Kassettenoberkante ± 0,2</td><td><span class="pill ok">≥ 4</span></td><td class="src">Nutzer</td></tr>
      <tr><td>Kammer, größter Kreis</td><td class="num">Radius {de(r_max)}</td><td class="num">Biegeradius der Ader etwa 3</td><td><span class="pill ok">frei</span></td><td class="src">A</td></tr>
      <tr><td>Mulde des Halses</td><td class="num">{de(d['NW'] + 0.2)} × {de(d['KD'] + 0.2)} × 14,2</td><td class="num">Spiel 0,1 je Seite</td><td><span class="pill mid">Kippen ungetestet</span></td><td class="src">Plan Campus</td></tr>
      <tr><td>Überhang Kopf</td><td class="num">{de(d['pe'] - d['KD'] / 2 + 0.0)} mm nach Osten über den Hals</td><td class="num">Support nötig</td><td><span class="pill mid">Support</span></td><td class="src">A</td></tr>
    </tbody></table></div>
</section>

<section aria-labelledby="h-dec">
  <h2 id="h-dec">Entscheidungen</h2>
  <div class="dec">
    <div class="card rec"><h3><span class="tag">A</span> Kopf über der Platte</h3><div class="opts">
      <div class="opt pick"><b>Ja (E4)</b><span class="num2">Hals {de(d['NW'] + 0.2)} × {de(d['KD'] + 0.2)}, Support unter dem Kopf. Empfohlen.</span></div>
      <div class="opt"><b>Nein, versenkt (E2b aus Plan 2)</b><span class="num2">Mulde {de(d['W'])} × 19,9 mm, kein Support.</span></div></div></div>
    <div class="card rec"><h3><span class="tag">B</span> Fenster über der Platte</h3><div class="opts">
      <div class="opt pick"><b>10 mm</b><span class="num2">Kopf ganz über der Platte. Empfohlen.</span></div>
      <div class="opt"><b>12 bis 15 mm</b><span class="num2">höher, Körper wächst um das gleiche Maß.</span></div>
      <div class="opt"><b>5 mm</b><span class="num2">Kopf taucht 4,7 mm ein, große Mulde.</span></div></div></div>
    <div class="card rec"><h3><span class="tag">C</span> Rückenkeil mit schrägem Rückdeckel</h3><div class="opts">
      <div class="opt pick"><b>Schräg bis zur Oberkante</b><span class="num2">Große runde Kammer, Rückdeckel zum Öffnen. Empfohlen.</span></div>
      <div class="opt"><b>Flacher Deckel über der Kassette</b><span class="num2">Weniger Platz für die Reserve ({de(D.AIR)} mm Luft).</span></div></div></div>
    <div class="card"><h3><span class="tag">D</span> Fase unten am Hals</h3><div class="opts">
      <div class="opt"><b>0,5 mm</b><span class="num2">wie die Gebäude in main, bewährt (Steckprobe 2).</span></div>
      <div class="opt pick"><b>1,0 mm</b><span class="num2">etwas leichteres Einführen. Vorschlag.</span></div>
      <div class="opt"><b>2,0 mm</b><span class="num2">wie im Passform-Branch, ungetestet.</span></div></div></div>
    <div class="card"><h3><span class="tag">E</span> Druck</h3><div class="opts">
      <div class="opt pick"><b>Stehend, Support nur unter dem Kopf</b><span class="num2">Hals mit senkrechten Wänden passt in die Mulde. Empfohlen.</span></div>
      <div class="opt"><b>Liegend auf der Seite</b><span class="num2">kein Support, aber der Hals bekommt Schichtlinien quer und Elefantenfuß an der Passfläche.</span></div></div></div>
    <div class="card"><h3><span class="tag">F</span> Kopfunterkante</h3><div class="opts">
      <div class="opt pick"><b>0,3 mm über der Platte</b><span class="num2">frei in der Luft.</span></div>
      <div class="opt"><b>Zwei Füße auf der Platte</b><span class="num2">der Kopf stützt sich ab und kippt nicht, braucht Auflagen am Kopf.</span></div></div></div>
  </div>
</section>

<section aria-labelledby="h-open">
  <h2 id="h-open">Offen</h2>
  <ul>
    <li><b>Du:</b> Modulmaße nachliefern (Pinlänge und Lage der Stiftspitzen, Dicke mit Header, Lochlage). Mit einem Lineal und einem seitlichen Foto reicht es auch.</li>
    <li><b>Kassette ohne Streifen</b> (Unterbau der V2) ist noch zu zeichnen. Der Anschlag im Schacht ist hier vereinfacht.</li>
    <li><b>Rückdeckel:</b> Haken und Zapfen sind noch nicht gezeichnet, die Auflage um die Öffnung ist {de(D.SPILL)} mm Spiel.</li>
    <li>Die Adern der 3D-Ansicht sind nur ein Beispiel einer Schleife.</li>
  </ul>
  <p class="small muted">Alle Maße sind Planwerte, nichts ist gedruckt. Die Werte stehen in <code>plug/display/params.py</code>, die Körpergeometrie in <code>plug/display/body4.py</code>, die Lage in <code>plug/display/layout4.py</code>. Plan 1 (Lage am Ostrand) und Plan 2 (versenkter Körper E2b) bleiben stehen.</p>
</section>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>{JS.replace('__DATA__', json.dumps(data, separators=(',', ':')))}
document.getElementById('expl').addEventListener('input', (e) => {{ document.getElementById('explv').textContent = e.target.value + ' %'; }});
document.getElementById('pull').addEventListener('input', (e) => {{ document.getElementById('pullv').textContent = Math.round(e.target.value * 0.34) + ' mm'; }});
</script>
"""
    return head + html


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache")
    a = ap.parse_args()
    html = page(load(a.cache))
    open(OUT, "w", encoding="utf-8").write(html)
    print("geschrieben:", OUT, "%.0f KB" % (len(html) / 1024))


if __name__ == "__main__":
    main()
