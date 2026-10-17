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
.fig .mulde4 { fill: none; stroke: var(--c-niche); stroke-width: 1.6; stroke-dasharray: 5 3; }
.fig .void2 { fill: var(--panel); stroke: var(--edge); stroke-width: .5; }
.done { display: flex; flex-direction: column; gap: 6px; }
.done .it { display: grid; grid-template-columns: auto 1fr; gap: 2px 10px; font-size: .93rem; padding: 6px 0; border-bottom: 1px solid var(--line); }
.done .it:last-child { border-bottom: 0; }
.done .ok { font-family: var(--mono); font-size: .74rem; color: var(--ok); letter-spacing: .06em; text-transform: uppercase; padding-top: 3px; }
.chg { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; }
.chg .card { gap: 6px; } .chg .card p { font-size: .93rem; }
.chg .tag2 { font-family: var(--mono); font-size: .74rem; letter-spacing: .06em; color: var(--accent); text-transform: uppercase; }
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
  b.onclick = () => {
    [...views.children].forEach((c, j) => c.setAttribute('aria-pressed', j === i));
    ['plate', 'leiste'].forEach((id) => { document.getElementById('v_' + id).checked = !(v.hide || []).includes(id); });
    if (v.pull !== undefined) { ui.pull.value = v.pull; ui.pull.dispatchEvent(new Event('input')); } else apply();
    goTo(v);
  };
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
    ch = aux["chamber"]
    pt = polylabel(ch, tolerance=0.05)
    r_max = ch.exterior.distance(pt)
    from shapely.geometry import LineString
    xs = d["x_s0"] + 1.5
    seg = ch.intersection(LineString([(xs, d["z_cass"] - 1), (xs, d["z_top"] + 1)]))
    air_rear = seg.bounds[3] - d["z_cass"] if not seg.is_empty else 0.0
    solder_len = d["pe"] + 35.0 + 5.0
    straight = math.hypot(-d["x_tip"] + d["x_s0"] / 2 + d["x_s1"] / 2 + 0.6, d["z_pins"] - d["z_cass"])
    reserve = solder_len - straight
    foot_len = d["x_fe"] - d["x_bw"]
    mu_w, mu_l = d["NW"] + 2 * D.CLR_MULDE, foot_len + 2 * D.CLR_MULDE
    win_h = d["win_top"] - d["mb"]
    pillar = d["W"] / 2 - D.WIN_W / 2 - D.WALL
    wide_w = D.KASS_W + 2 * (D.WALL + D.FOOT_CH_FRONT)
    kd2 = body4.V.dims("V2")
    lp = aux["lid_pts"]
    lid_len = math.hypot(lp[0][0] - lp[1][0], lp[0][1] - lp[1][1])
    head = open(CONCEPT_TEMPLATE, encoding="utf-8").read().split('<div class="wrap">')[0]
    head = head.replace("<title>Powerbank in der Grundplatte</title>", "<title>Plan 3 Display-Gebäude</title>\n<meta name=\"description\" content=\"Display-Körper mit Kopf über der Platte, Rückenkeil und 3D-Ansicht\">")
    head = head.replace("</style>", CSS_EXTRA + CSS3 + "</style>")
    nx, nz = aux["normal"]
    pal = dict(
        body=("#e6dfcb", "#cfc7b0"), lid=("#f0a21a", "#f2b441"), blende=("#5b4a7a", "#8d73b8"), cassette=("#5f7086", "#7d8ea6"),
        pcb=("#2f7d4f", "#4c9a69"), glass=("#3a3f44", "#59616a"), aa=("#f4c36a", "#f2b441"), header=("#1f2326", "#8a9299"), pins=("#d4a017", "#e3b54a"),
        plate=("#8fa3b8", "#5d7087"), leiste=("#2d3236", "#8a9299"))
    labels = dict(body="Körper", lid="Rückdeckel", blende="Frontblende mit Zapfen", cassette="Kassette", pcb="Modul, Platine", glass="Modul, Glas", aa="aktive Fläche",
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
               dict(name="Von oben", t=[-12, 0, 0], d=190, az=0, el=88), dict(name="Von unten (Fuß)", t=[-10, 0, 28], d=130, az=-70, el=-48, pull=100, hide=["plate", "leiste"])])
    sec = F3.section(parts, aux, d)
    plan = F3.plan(parts, aux, d)
    foot = F3.foot_plan(parts, aux, d)
    peg = F3.peg_section(parts, aux, d)
    bump = F3.bump_cross()
    mini = mini_map(v, pl, L.EAST_XE, y_mid)
    html = f"""<div class="wrap">
<header>
  <div class="kicker">Steckmechanismus · Display-Gebäude · Plan 3, zweite Fassung, STL für den ersten Probedruck mit Standardwerten gebaut</div>
  <h1>Display-Gebäude: Kopf über der Platte</h1>
  <p class="lead">Zweite Fassung nach deiner Rückmeldung: Das Kabelfenster geht hoch, der Fuß ist verdrehsicher, die Fase folgt <code>main</code>, und die dünnen Teile halten mit Zapfen und Rastnasen. Kopf über der Platte, Fenster ab 10 mm und der Rückenkeil mit schrägem Rückdeckel sind abgenickt. Auf deine Bitte, erst mit meinen Standardwerten zu testen, sind die STL für den ersten Probedruck gebaut (<code>stl/steckmodul_display/</code>, <code>python3 -m plug.display.build</code>).</p>
  <p class="small muted">Korrektur beim Bau: Die Kassette ist der V2-Unterbau mit {de(kd2['w'], 2)} × {de(kd2['depth'], 2)} × {de(kd2['z_b'], 1)} mm im Schacht {de(D.KASS_W, 2)} × {de(D.KASS_D, 2)}. Plan 3 hatte die Maße der v4 (13,2 × 5,58 × 17,1) angenommen; die Kassette endet deshalb nur {de(D.KASS_TOP, 1)} mm über der Platte, und der Rückenkeil ist {de(d['z_rear'], 1)} mm statt 8,6 mm hoch. Alle Zahlen und Bilder auf dieser Seite sind neu gerechnet. Nach Probedruck 1: Das Modul passte nicht in die Tasche (etwa 0,75 mm zu hoch, jetzt {de(D.DISP['pcb_h'], 2)} angenommen), die Breite hat {de(D.CLR_W, 1)} statt 0,3 Luft je Seite, die Zapfen sitzen {de(D.PEG_HOLE_T - D.PEG_TIP_GAP, 1)} mm tief in Sacklöchern Ø {de(D.PEG_HOLE_D, 1)} (Modulprobe <code>stl/steckmodul_display_modul/</code>, <code>python3 -m plug.display.build_test</code>). Die Kassette soll nach Wunsch des Nutzers in den Körper integriert werden; das ist hier noch die Kassette K0.</p>
</header>

<section aria-labelledby="h-neu">
  <h2 id="h-neu">Das hat sich geändert</h2>
  <div class="chg">
    <div class="card"><span class="tag2">Kabelfenster</span><h3>Bis weit nach oben, {de(D.WIN_W, 0)} mm breit</h3>
      <p>Die Rückwand hinter dem Modul hat ein Langloch mit Rundbogen: {de(D.WIN_W)} mm breit, von {de(d['mb'])} bis {de(d['win_top'])} mm über der Platte ({de(win_h, 0)} mm hoch), vorher nur {de(D.SLIT_W)} × 8 mm. Die Kammer weitet sich zum Fenster von {de(D.KASS_W)} auf {de(D.CHAMBER_FRONT_W)} mm. Das Modul liegt hinten fast frei, die Reserve der Adern kann überall hinter dem Display liegen. Rechts und links bleiben Pfeiler von je {de(pillar, 0)} mm, die das Modul und die Zapfen halten.</p></div>
    <div class="card"><span class="tag2">Verdrehsicher</span><h3>Fuß {de(D.FOOT_EXT, 0)} mm nach vorn, Ecke abgeschrägt</h3>
      <p>Der Fuß ist zur Bildschirmfront hin um {de(D.FOOT_EXT)} mm verlängert und misst jetzt {de(d['NW'])} × {de(foot_len)} mm. Vorn auf der Südseite fehlt eine Ecke von {de(D.KEY)} mm, die Kodierecke aus <code>parts.py</code> (Steckprobe 1). Der Körper passt nur in einer Lage in die Mulde. Die Verlängerung liegt unter dem Kopf und stört weder Kammer noch Pins. Die Mulde in der Platte ist der Fußumriss plus {de(D.CLR_MULDE, 2)} mm: {de(mu_w)} × {de(mu_l)} mm.</p></div>
    <div class="card"><span class="tag2">Fase</span><h3>Wie in main: 2,0 mm, Spiel 0,15</h3>
      <p>Nach dem Merge von <code>main</code>: <code>FUSS_FASE_T</code> 2,0 mm ist in r8 bewährt (fängt das Gebäude, kein Wulst), das Spiel von 0,15 mm ist deine Vorgabe für den nächsten Probedruck. Der Hals bekommt vorn und an der Kodierecke die 2,0 mm. An den Längsseiten und hinten sind es {de(D.FOOT_CH_SIDE)} mm, weil die Wand um den Schacht nur {de(D.WALL)} mm dick ist; 2,0 mm würden dort in den Schacht schneiden. Wie das aussieht, zeigt der Abschnitt zum Fuß.</p></div>
    <div class="card"><span class="tag2">Befestigung</span><h3>Zapfen und Rastnasen, Kleben als Rückfall</h3>
      <p>Die Frontblende hat vier Zapfen (Ø {de(D.PEG_D)} mm). Sie gehen durch die vier Befestigungslöcher des Moduls in Sacklöcher der Rückwand und halten Blende und Modul zugleich. Der Rückdeckel hat je Längskante zwei Rastnasen ({de(D.BUMP['h'])} mm) in Nuten der Öffnung. Beide Teile sind mechanisch kaum belastet und dürfen dünn gedruckt werden. Im schlechtesten Fall klebst du sie an.</p></div>
  </div>
</section>

<section aria-labelledby="h-3d">
  <h2 id="h-3d">3D-Ansicht zum Auseinandernehmen</h2>
  <p>Ziehen dreht die Ansicht, Umschalt oder rechte Maustaste verschiebt sie, das Mausrad zoomt. Mit dem ersten Regler fasst du die Teile einzeln heraus (Kassette nach unten, Rückdeckel schräg, Frontblende mit Zapfen und Modul nach vorn), mit dem zweiten ziehst du den ganzen Körper aus der Platte. „Von unten“ zeigt den Fuß mit der Kodierecke. Die Adern zeigen eine Schleife von etwa 32 mm als Beispiel; die Kammer hat Platz für mehr, die echte Lage entsteht beim Einschieben.</p>
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

<section aria-labelledby="h-sec">
  <h2 id="h-sec">Schnitt und Draufsicht</h2>
  <div class="twofig">
    <div class="card"><h3>Längsschnitt durch die Mitte</h3><div class="scroll">{sec}</div>
      <p class="small muted">Osten rechts. Der Kopf (Frontblende violett, Modul grün) hängt über der Platte, der Hals mit der Kassette (dunkelblau) steckt in der Mulde. Gelb der schräge Rückdeckel, rot eine mögliche Lage der Adern. Im Schnitt durch die Mitte ist die Rückwand offen: Dort liegt das hohe Kabelfenster.</p></div>
    <div class="card"><h3>Draufsicht</h3><div class="scroll">{plan}</div>
      <p class="small muted">Umrisse in 5 mm (ausgefüllt), 20 mm (gestrichelt) und im Fuß (blass). Der Kopf ist am breitesten, der Hals hinten so breit wie die Kassette.</p></div>
  </div>
</section>

<section aria-labelledby="h-fuss">
  <h2 id="h-fuss">Fuß, Mulde und Kodierecke</h2>
  <div class="twofig">
    <div class="card"><h3>Fuß von oben, mit Mulde</h3><div class="scroll">{foot}</div>
      <p class="small muted">Dunkel der Fuß auf halber Höhe, blass sein Umriss ganz unten (Fase), gestrichelt orange die Mulde in der Platte (Fuß plus {de(D.CLR_MULDE, 2)} mm). Vorn ist rechts, die abgeschrägte Ecke liegt vorn auf der Südseite.</p></div>
    <div class="card"><h3>Fase je Kante an der Unterseite</h3>
      <div class="scroll"><table>
        <thead><tr><th>Kante</th><th>Fase</th><th>Grund</th></tr></thead>
        <tbody>
          <tr><td>vorn (Ost)</td><td class="num">{de(D.FOOT_CH_FRONT)}</td><td class="src">main, r8 bewährt; hier steht Material vor dem Schacht</td></tr>
          <tr><td>Kodierecke</td><td class="num">{de(D.FOOT_CH_FRONT)}</td><td class="src">wie vorn</td></tr>
          <tr><td>Süd- und Nordseite</td><td class="num">{de(D.FOOT_CH_SIDE)}</td><td class="src">Wand um den Schacht {de(D.WALL)}, bleibt unten {de(D.WALL - D.FOOT_CH_SIDE)}</td></tr>
          <tr><td>hinten (West)</td><td class="num">{de(D.FOOT_CH_SIDE)}</td><td class="src">wie die Seiten</td></tr>
          <tr><td>Schachteingang</td><td class="num">0,5</td><td class="src">ENTRY_CH_T, wie bei den Gebäuden</td></tr>
        </tbody></table></div>
      <p class="small">Die senkrechten Fußkanten bekommen im STL den Radius 0,5 mm (<code>FOOT_R</code> in <code>parts.py</code>), damit die Mulde sauber druckt. Wer rundum 2,0 mm will, braucht einen breiteren Hals: {de(wide_w)} statt {de(d['NW'])} mm, weil Wand und Fase zusammen {de(D.WALL + D.FOOT_CH_FRONT)} mm je Seite kosten. Das steht als Karte H unten.</p></div>
  </div>
</section>

<section aria-labelledby="h-snap">
  <h2 id="h-snap">Befestigung: Zapfen und Rastnasen</h2>
  <div class="twofig">
    <div class="card"><h3>Zapfen der Frontblende (Schnitt durch ein Loch des Moduls)</h3><div class="scroll">{peg}</div>
      <p class="small muted">Violett die Blende mit dem Zapfen, grün die Platine mit dem Loch, rechts die Rückwand mit dem Sackloch ({de(D.PEG_HOLE_T)} mm tief). Der Zapfen ist Ø {de(D.PEG_D)} mm, das Loch im Modul etwa Ø {de(D.DISP['hole_d'])} mm und das Sackloch Ø {de(D.PEG_HOLE_D)} mm.</p></div>
    <div class="card"><h3>Rastnasen am Rückdeckel (Querschnitt, Prinzip)</h3><div class="scroll">{bump}</div>
      <p class="small muted">Zwei Nasen je Längskante ({de(D.BUMP['len'])} mm lang, {de(D.BUMP['h'])} mm hoch) rasten in Nuten ({de(D.BUMP['groove'])} mm tief) der Öffnung. Das Spiel des Deckels in der Öffnung ist {de(D.SPILL, 2)} mm.</p></div>
  </div>
  <ul>
    <li><b>Vorteil der Zapfen durch die Modullöcher:</b> Sie zentrieren das Modul und halten es, ohne dass ein Teil über die Platine greift. Die Lochlage ({de(D.DISP['hole_dx'])} × {de(D.DISP['hole_dy'])} mm) kommt aus dem Foto und gilt ± 0,5 mm. Zwischen Zapfen (Ø {de(D.PEG_D)}) und Loch (Ø {de(D.DISP['hole_d'])}) bleiben je Seite etwa 0,3 mm. <b>Deshalb bitte die Lochlage nachmessen</b>, bevor die STL entstehen.</li>
    <li><b>Dünn drucken:</b> Frontblende und Rückdeckel sind {de(D.BLENDE_T)} mm dick (drei Linien). Mit 0,8 mm (zwei Linien) gehen sie auch, wenn du sie biegsamer willst.</li>
    <li><b>Rückfall:</b> Die Nasen und Zapfen weglassen und die Teile mit Sekundenkleber oder einem Klebepunkt befestigen. Dann lässt sich das Modul nur noch durch Abbrechen der Blende wechseln.</li>
  </ul>
</section>

<section aria-labelledby="h-kab">
  <h2 id="h-kab">Kabelreserve</h2>
  <ul>
    <li><b>Länge:</b> Du lötest mit etwa 35 mm Abstand vor der Ostfläche. Dann braucht jede Ader vom Schacht aus etwa {de(solder_len, 0)} mm, weil der Hals {de(d['pe'], 0)} mm hinter der Front sitzt. Zusammengebaut liegen Kassettenoberkante und Stiftspitzen nur etwa {de(straight, 0)} mm auseinander. Es bleiben etwa {de(reserve, 0)} mm Reserve, mehr als deine geschätzten 3 bis 4 cm. Lötest du mit 20 mm Abstand, sind es etwa {de(reserve - 15, 0)} mm.</li>
    <li><b>Platz:</b> Der größte Kreis in der Kammer hat {de(r_max)} mm Radius. Dazu kommt das große Kabelfenster: Die Reserve kann als Schleife hinter dem Modul bis fast unter das Kopfdach liegen. Ein Radius von 6 mm liegt weit über dem Biegeradius von 28-AWG-Silikonlitze (etwa 3 mm).</li>
    <li><b>Einschieben:</b> Beim Schieben des Moduls von vorn in die Tasche klappt die Reserve durch das Fenster nach hinten in die Kammer. Du hilfst mit einem Stäbchen durch die offene Rückseite (Rückdeckel ab).</li>
    <li><b>Rückdeckel:</b> Er liegt bündig in der Schräge, ist {de(D.LID_W)} mm breit und {de(D.BLENDE_T)} mm dick und wird liegend gedruckt.</li>
  </ul>
</section>

<section aria-labelledby="h-map">
  <h2 id="h-map">Lage auf der Platte</h2>
  <div class="mapcol">
    <div class="card">{mini}<p class="small muted">Körper E4 am Ostrand bei y = {de(y_mid, 0)} mm.</p></div>
    <div class="card"><h3>Was am Ostrand geht</h3>
      <p>Der Körper (Kopf {de(d['W'])} mm breit, {de(d['depth'])} mm tief) braucht {de(L4.AIR_MARGIN)} mm Abstand zu Gebäuden, Hof und Schrift, weil der Kopf in der Luft darüber liegt. Am Ostrand passt er bei <b class="num">{ivs}</b> (Mitte des Kopfs von der Südkante). Die Verlängerung des Fußes ändert daran nichts, sie liegt unter dem Kopf.</p>
      <p class="small muted">Die Mulde misst {de(mu_w)} × {de(mu_l)} mm, die Mitte der Kassette liegt {de(d['pe'])} mm hinter der Ostfläche des Kopfs. Die Dockzone (14,9 × 11,1 mm) bleibt frei von Stützen. Die Südgrenze y = 37 kommt aus der Schrift (Kopf an der Unterkante 0,3 mm, Schrift 0,6 mm hoch) und der Fadenkerbe in der Ecke.</p></div>
  </div>
</section>

<section aria-labelledby="h-teile">
  <h2 id="h-teile">Teile, Druck und Zusammenbau</h2>
  <div class="scroll"><table>
    <thead><tr><th>Teil</th><th>Maße</th><th>Drucklage</th><th>Anmerkung</th></tr></thead>
    <tbody>
      <tr><td><b>1 Körper</b></td><td class="num">{de(d['W'])} × {de(d['depth'])} × {de(d['z_top'] - d['foot'])}</td><td>stehend, Fuß unten auf dem Bett, <b>mit Support</b> unter dem Kopf</td><td>Fuß {de(d['NW'])} × {de(foot_len)} mit Kodierecke und Fasen (2,0 vorn, {de(D.FOOT_CH_SIDE)} seitlich), Schacht mit Einführfase, Tasche von vorn offen, Kabelfenster mit Rundbogen, Rückenkeil mit offener Kammer unter der Schräge (Wand lehnt höchstens 31° über Luft). Support nur unter dem Kopf: Tree-Support bis auf das Bett, Kontakt nur an der Kopfunterseite.</td></tr>
      <tr><td><b>2 Rückdeckel</b></td><td class="num">{de(D.LID_W)} × {de(lid_len)} × {de(D.BLENDE_T)}</td><td>liegend</td><td>Schräge Wand mit vier Rastnasen, bündig im Körper.</td></tr>
      <tr><td><b>3 Frontblende</b></td><td class="num">{de(d['W'])} × {de(d['z_top'] - d['z_hb'])} × {de(D.BLENDE_T)}</td><td>liegend, Außenseite unten, Zapfen nach oben</td><td>Sichtfenster {de(P['aa_w'] + 2 * D.WINDOW_MARGIN)} × {de(P['aa_h'] + 2 * D.WINDOW_MARGIN)} als glattes Loch, vier Zapfen Ø {de(D.PEG_D)}.</td></tr>
      <tr><td><b>4 Kassette</b></td><td class="num">{de(kd2['w'], 2)} × {de(kd2['depth'], 2)} × {de(kd2['z_b'], 1)}</td><td>stehend, Tasche unten</td><td>Kassette K0: Unterbau der V2 (Unterbau im Schacht bewährt, r8) ohne Blatt und Streifen; Schacht {de(D.KASS_W, 2)} × {de(D.KASS_D, 2)}, Anschlag {de(d['ledge'])} mm in 45° auf die Öffnung.</td></tr>
      <tr><td>Kaufteile</td><td colspan="3">Modul mit Header, vier Silikon-Adern 28 AWG (etwa 60 mm), Dupont-Buchse 4-polig mit Kontakten, Winkelleiste für das Dock.</td></tr>
    </tbody></table></div>
  <ol class="todo">
    <li><b>Kassette bestücken:</b> Buchse mit vier Adern (60 mm) crimpen und in die Kassette drücken.</li>
    <li><b>Kassette von unten in den Hals schieben:</b> Die Adern kommen oben in die Kammer. Rückdeckel ist ab. Du ziehst die Adern durch das Kabelfenster in die Tasche und vorn heraus.</li>
    <li><b>Adern an die Pinenden löten:</b> Das Modul liegt etwa 35 mm vor dem Körper. Header bleibt, die Adern kommen an die Pinenden hinten.</li>
    <li><b>Modul von vorn in die Tasche schieben:</b> Die Reserve legt sich in der Kammer ab (Stäbchen von hinten).</li>
    <li><b>Frontblende von vorn aufdrücken:</b> Die vier Zapfen gehen durch die Löcher des Moduls in die Sacklöcher. <b>Rückdeckel einsetzen:</b> Die Nasen rasten ein.</li>
    <li><b>Körper in die Mulde stecken</b> (Kodierecke nach vorn Süd, Kassette auf die Pins der Winkelleiste), danach I²C-Scan.</li>
  </ol>
</section>

<section aria-labelledby="h-chain">
  <h2 id="h-chain">Maßkette im Worst-Case</h2>
  <div class="scroll"><table>
    <thead><tr><th>Maß</th><th>Soll</th><th>Worst-Case</th><th>Ergebnis</th><th>Quelle</th></tr></thead>
    <tbody>
      <tr><td>Fenster über der Platte</td><td class="num">{de(d['wb'])} bis {de(d['wt'])}</td><td class="num">Platine ± 0,5: ± 0,5</td><td><span class="pill mid">Maße nachliefern</span></td><td class="src">Nutzer, Foto</td></tr>
      <tr><td>Kabelfenster</td><td class="num">{de(D.WIN_W)} × {de(win_h, 0)}, Pfeiler {de(pillar, 0)}</td><td class="num">Brücke entfällt (Rundbogen)</td><td><span class="pill ok">frei</span></td><td class="src">E</td></tr>
      <tr><td>Zapfen im Modulloch</td><td class="num">Ø {de(D.PEG_D)} in Ø {de(D.DISP['hole_d'])}</td><td class="num">Lochlage ± 0,5: Spiel 0,3 bleibt</td><td><span class="pill mid">Lochlage prüfen</span></td><td class="src">Foto</td></tr>
      <tr><td>Fuß</td><td class="num">{de(d['NW'])} × {de(foot_len)}, Ecke {de(D.KEY)}</td><td class="num">Druckmaß ± 0,1</td><td><span class="pill mid">ungetestet</span></td><td class="src">parts.py KEY</td></tr>
      <tr><td>Mulde</td><td class="num">{de(mu_w)} × {de(mu_l)} × 14,2 (Spiel {de(D.CLR_MULDE, 2)})</td><td class="num">0,10 war an kleiner Lehre bewährt</td><td><span class="pill mid">Spiel 0,15 testen</span></td><td class="src">r8, Nutzer</td></tr>
      <tr><td>Fase vorn</td><td class="num">{de(D.FOOT_CH_FRONT)}</td><td class="num">45°</td><td><span class="pill ok">bewährt</span></td><td class="src">r8</td></tr>
      <tr><td>Stiftspitzen bis Kassettensäule</td><td class="num">{de(D.PIN_CLEAR)}</td><td class="num">Pins 0,5 länger: 3,0</td><td><span class="pill mid">Pinlänge prüfen</span></td><td class="src">Zeichnung -79</td></tr>
      <tr><td>Luft über der Kassette</td><td class="num">{de(D.AIR)} (hinten ≥ {de(air_rear)})</td><td class="num">Kassettenoberkante ± 0,2</td><td><span class="pill ok">≥ 4</span></td><td class="src">Nutzer</td></tr>
      <tr><td>Kopfunterkante</td><td class="num">{de(d['z_hb'])} über der Platte</td><td class="num">Schrift 0,6, Hof 1,9 hoch</td><td><span class="pill ok">nur außerhalb der Schriftzone</span></td><td class="src">A</td></tr>
    </tbody></table></div>
</section>

<section aria-labelledby="h-dec">
  <h2 id="h-dec">Entscheidungen</h2>
  <div class="card"><h3>Schon entschieden</h3><div class="done">
    <div class="it"><span class="ok">ja</span><span><b>Kopf über der Platte</b> (E4), Hals als Halter der Kassette</span></div>
    <div class="it"><span class="ok">ja</span><span><b>Fenster 10 mm über der Platte</b></span></div>
    <div class="it"><span class="ok">ja</span><span><b>Rückenkeil mit schrägem Rückdeckel</b> bis zur Oberkante</span></div>
    <div class="it"><span class="ok">ja</span><span><b>Druck stehend, Support nur unter dem Kopf</b>; Kopfunterkante 0,3 mm über der Platte</span></div>
    <div class="it"><span class="ok">ja</span><span><b>Pins bleiben am Modul</b>, Adern an die Pinenden</span></div>
    <div class="it"><span class="ok">ja</span><span><b>Fase nach main</b> (2,0 mm), Spiel 0,15 mm; Zapfen und Rastnasen, Kleben als Rückfall</span></div>
  </div></div>
  <div class="dec">
    <div class="card rec"><h3><span class="tag">G</span> Verlängerung des Fußes nach vorn</h3><div class="opts">
      <div class="opt pick"><b>{de(D.FOOT_EXT, 0)} mm</b><span class="num2">Ecke {de(D.KEY)} plus 3 mm gerade Fläche; Fuß {de(d['NW'])} × {de(foot_len)}. Empfohlen.</span></div>
      <div class="opt"><b>4 mm</b><span class="num2">kürzer, nur eben die Ecke und die Fase.</span></div>
      <div class="opt"><b>8 mm</b><span class="num2">stabiler gegen Kippen nach vorn, größere Mulde.</span></div></div></div>
    <div class="card rec"><h3><span class="tag">H</span> Fase am Hals</h3><div class="opts">
      <div class="opt pick"><b>Vorn 2,0, Seiten und hinten {de(D.FOOT_CH_SIDE)}</b><span class="num2">Hals bleibt {de(d['NW'])} breit. Empfohlen.</span></div>
      <div class="opt"><b>Rundum 2,0</b><span class="num2">Hals {de(wide_w)} breit, Mulde entsprechend größer.</span></div>
      <div class="opt"><b>Rundum 0,5</b><span class="num2">wie Steckprobe 2, fängt weniger.</span></div></div></div>
    <div class="card"><h3><span class="tag">I</span> Spiel Fuß zur Mulde</h3><div class="opts">
      <div class="opt pick"><b>{de(D.CLR_MULDE, 2)} mm</b><span class="num2">deine Vorgabe für den nächsten Probedruck (L43).</span></div>
      <div class="opt"><b>0,10 mm</b><span class="num2">an der kleinen Lehre bewährt, bei großen Umrissen zu eng.</span></div></div></div>
    <div class="card"><h3><span class="tag">J</span> Frontblende</h3><div class="opts">
      <div class="opt pick"><b>Vier Zapfen durch die Modullöcher</b><span class="num2">Reibsitz in Sacklöchern. Empfohlen, braucht gemessene Lochlage.</span></div>
      <div class="opt"><b>Zapfen plus Klebepunkt</b><span class="num2">falls der Reibsitz zu lose ist.</span></div>
      <div class="opt"><b>Nur kleben</b><span class="num2">Rückfall, Modul nicht mehr wechselbar.</span></div></div></div>
    <div class="card"><h3><span class="tag">K</span> Rückdeckel</h3><div class="opts">
      <div class="opt pick"><b>Zwei Rastnasen je Längskante</b><span class="num2">0,4 mm hoch in 0,5 tiefen Nuten. Empfohlen.</span></div>
      <div class="opt"><b>Kleben</b><span class="num2">einfach, Kammer danach nicht mehr offen.</span></div></div></div>
    <div class="card"><h3><span class="tag">L</span> Kabelfenster</h3><div class="opts">
      <div class="opt pick"><b>{de(D.WIN_W, 0)} breit, bis {de(d['win_top'])} mm hoch, Rundbogen</b><span class="num2">Pfeiler {de(pillar, 0)} mm. Empfohlen.</span></div>
      <div class="opt"><b>Ganz offen bis zu den Zapfen</b><span class="num2">etwa 26 mm breit, Pfeiler nur noch um die Zapfenlöcher.</span></div>
      <div class="opt"><b>Wie vorher</b><span class="num2">{de(D.SLIT_W)} × 8 mm.</span></div></div></div>
  </div>
</section>

<section aria-labelledby="h-open">
  <h2 id="h-open">Offen</h2>
  <ul>
    <li><b>Du:</b> Modulmaße nachliefern (Pinlänge, Dicke mit Header, vor allem die <b>Lochlage</b> für die Zapfen). Ein Lineal und ein seitliches Foto reichen.</li>
    <li><b>Kassette in zwei Lagen:</b> Die Buchsentasche ist symmetrisch, die Kassette passt gedreht in den Schacht. Dann liegen GND und 3,3 V vertauscht an den Pins. Bis zu einer Kodierecke an Kassette und Schacht (Vorschlag für den nächsten Satz): Pin 1 beim Bestücken markieren und vor dem ersten Stecken durchmessen.</li>
    <li><b>Rastnasen und Zapfen</b> sind klein (0,4 bis 2,4 mm): Passung erst im Probedruck sicher.</li>
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
