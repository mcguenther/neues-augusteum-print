#!/usr/bin/env python3
"""Unterseite der Steckplatte des Campus: Zapfenaufnahmen (Sacklöcher) und Fadenösen an den vier Ecken.

Die Platte (`plug/campus.py`) wird mit der flachen Unterseite aufs Bett gedruckt; unten hat sie die 24 Pin-Löcher der Docks. Dieses Modul ergänzt
die zwei Dinge, die die Platte mit dem Unterkasten des Konzepts (`plug/power/build_concept.py`, `variant(1300)`) verbinden:

1. **Zapfenaufnahmen**: Sacklöcher Ø 4,3 × 2,8 für die Zentrierzapfen Ø 4,0 × 2,5 auf den Stützen des Unterkastens. Lage, Größe und Spiel sind die des
   Konzepts (`PP.PIN_PLAN`, `PP.POST`, Auswahl der Zapfenstützen in `variant()`); die Lagen werden einmal aus dem Konzept gelesen und in
   `plug/scale1176/underside_<Maßstab>.json` zwischengespeichert (wie `placements_<Maßstab>.json`; veraltet der Stand, wird er neu gerechnet).
2. **Fadenösen** für den Faden zum Doktorhut (keine Schrauben), zwei Formen, umschaltbar mit `FADEN` (Standard `"pille"`):
   - `"pille"`: die „halbe Pille mit Steg“ aus `plug/thread/` (Plan Stand 2, abgenickt 16.10.; Luft über dem Steg 4,0, Fase 2,0 am Rand und 1,0 am Steg-Fuß).
     Eckmuster P3 und P45 (Luft 3,0 und 4,5) wurden gedruckt, die Decke war glatt, der Faden ging durch (r6, `plug/thread/round/r6_eckmuster/`). Das ist der
     Stand für die große Platte (`plug/thread/round/r6_eckmuster/summary.md`, „Folgen“). Die Tasche liegt so nah an der Ecke wie möglich, mit 1,4 mm Wand zu Rand,
     Mulden, Hof und Zapfenlöchern; die Eckaussparung des Unterkastens muss Mündung plus 2,0 überdecken (`notch_boxes`), das Konzept hat sie noch nicht.
   - `"v"`: der V-Kanal des Konzepts (`build_concept.v_solid`, `place_vs`; Ø 2,2, Scheitel 3,4, 40°, Trichter R 2,0), an den Lagen des Konzepts: passt zum Unterkasten
     des Konzepts, **wurde aber in Steckprobe 2 (r4) verworfen** (der Faden kam durch keinen Kanal, Kanäle unter etwa 3 mm schließen sich im Druck).

Die Aufnahmen sind nach unten offen (Bett), die Platte braucht keinen Support.

Aufruf (Passprobe im Rechner: Zapfen und Faden des Unterkastens in die Platte setzen, ca. 1 min):
    python3 -m plug.campus_underside [--scale 1300] [--faden pille|v]
    python3 -m plug.campus --unten-neu                      # Lagen der Zapfen aus dem Konzept neu lesen (nach Änderungen an Docks oder Konzept)
"""
import argparse
import hashlib
import json
import os

import manifold3d as m3d
import numpy as np
import shapely
from shapely.geometry import Point, Polygon, box as sbox
from shapely.ops import unary_union

import generate as G
from plug.geom import capsule, ccw, union, vol_int
from plug.power import build_concept as BC
from plug.power import params as PP
from plug.testcase import params as P
from plug.thread import build as TH
from plug.thread import params as TP

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(HERE, "plug", "scale1176", "underside_%d.json")

FADEN = "pille"                                        # "pille" (plug/thread, Standard) oder "v" (V-Kanal des Konzepts, in r4 verworfen)
PILLE_ACHSEN = None                                    # Ausrichtung der Taschen: None = automatisch (so nah an der Ecke wie möglich; an den zwei Ecken der Kante, an der das Powerbank-Fach des
#   Konzepts liegt, nur mit der schmalen Seite zur Kante, damit die Eckaussparungen dem Fach Platz lassen: bei 30 mm Breite an beiden Ecken hat `build_concept.fach_candidates`
#   keinen Kandidaten mehr, bei 18 mm bleiben 6); oder ein Tupel ("x", "y") bzw. ("y",) für alle Ecken
FACH_ECKEN = dict(N=("NW", "NO"), S=("SW", "SO"), W=("NW", "SW"), O=("NO", "SO"))

# ---- Zapfenaufnahmen (Sacklöcher), Werte aus dem Konzept (plug/power/params.py, build_concept.variant)
# Lage der Zapfenlöcher in Plattenkoordinaten (Ecke unten links, Süden y = 0, mm). Nutzer 18.10.: Position des zweiten Zapfens ändern, weil der Unterkasten
# (Batteriefach, PR #32 Branch ccr-395903c6-2y3sex, Stand 7, `U_unterkasten.stl`) schon gedruckt wird: seine Zapfen stehen bei (20 | 20) und (100 | 180). Das Konzept
# dieses Branches (ohne `FACH_FIX`) lieferte (100 | 20). None = Lagen aus dem Konzept.
ZAPFEN_LOKAL = [(20.0, 20.0), (100.0, 180.0)]
ZAPFEN = PP.PIN_PLAN                                   # Zapfen Ø 4,0 × 2,5, Gleitspiel 0,15 je Seite (Konzept; Test-Dock: 1 mm länger als r4); Zapfen 2,5 ungetestet
LOCH_D = ZAPFEN["d"] + 2 * ZAPFEN["clr"]               # 4,3 (L10: 0,15 gleitet)
LOCH_T = ZAPFEN["h"] + 0.3                             # 2,8 tief ab Plattenunterseite (0,3 Luft über der Zapfenspitze, wie build_concept.variant)
LOCH_FASE = PP.CH_BED                                  # 0,5 Einführfase am Bett (Konzept, L03)
WAND_MIN = 0.8                                         # Mindestwand um eine Aufnahme (Auftrag; wie Trennwand der Platte)
# ---- Fadentasche "pille", Werte aus plug/thread/params.py (Plan Stand 2, abgenickt 16.10., Eckmuster P3/P45 gedruckt)
FADEN_LUFT = TP.CHOSEN_AIR                             # 4,0 über dem Steg (Kompromiss aus 3,0 und 4,5; 4,0 selbst nicht gedruckt)
FADEN_WAND = TP.WALL_MIN                               # 1,4 Wand zu Rand, Mulden, Hof, Zapfenlöchern
NOTCH_PAD = TP.NOTCH_PAD                               # Eckaussparung im Unterkasten reicht 2,0 über die gefaste Mündung hinaus
FADEN_D = TP.THREAD_D                                  # 0,8 Faden doppelt genommen (ungemessen)
# ---- V-Kanal "v": Werte des Konzepts (plug/power/params.py V), Ø aus Steckprobe 2 (r4: zu eng)
V_D = PP.V["leg_d"]                                    # 2,2; r4: "mindestens 1 mm weiter" (Ø 3,2 oder mehr); hier ändern, wenn "v" gebaut werden soll


# --------------------------------------------------------------------------
# Lagen aus dem Konzept (Zapfen, Stützen, Fach, Elektronik, V)
# --------------------------------------------------------------------------
def _signature(scale, outline):
    from plug import campus as CA
    md5 = hashlib.md5(open(CA.CACHE % scale, "rb").read()).hexdigest()[:12]
    return dict(outline=[round(float(x), 1) for x in outline.bounds], placements=md5, post=list(PP.POST), pin=dict(PP.PIN_PLAN),
                uk_wall=PP.UK_WALL, v=dict(PP.V))


def _compute(scale):
    """Lagen von Stützen, Zapfen, Fach, Elektronik und V aus `build_concept.variant` (ohne Unterseite der Platte, sonst rekursiv), Rohkoordinaten der Platte."""
    from plug import campus as CA
    with BC.patched(CA, UNTEN=False):
        v = BC.variant(scale)
    sh = BC.LAST["sh"]                                  # (−minx, −miny): Konzeptkoordinaten = Rohkoordinaten + sh
    minx, miny = -sh[0], -sh[1]
    n = PP.POST[1]

    def snap(p):                                        # Stützen liegen auf dem Raster minx + n/2 + k·n (Ausgabe des Konzepts ist auf 0,01 gerundet)
        cx, cy = np.mean(p["r"], axis=0)
        kx, ky = round((cx - sh[0] - minx - n / 2) / n), round((cy - sh[1] - miny - n / 2) / n)
        return [round(minx + n / 2 + kx * n, 3), round(miny + n / 2 + ky * n, 3)]

    raw = lambda rings: [[[round(x - sh[0], 3), round(y - sh[1], 3)] for x, y in r] for r in rings]   # noqa: E731
    vs = [dict(c=[v_["c"][0] - sh[0], v_["c"][1] - sh[1]], axis=v_["axis"], notch=raw([v_["notch"]])[0]) for v_ in v["vs"]]
    return dict(posts=[snap(p) for p in v["posts"]], pins=[snap(p) for p in v["posts"] if p["pin"]],
                fach=raw(v["fach_poly"]), elec=raw(v["elec"]), vs=vs, side=v["side"], uk_t=BC.H0["uk_t"])


def concept_layout(scale, outline, refresh=False):
    """Lagen des Konzepts (Zwischenspeicher `underside_<Maßstab>.json`, neu bei geänderten Lagen, Umriss oder Maßen)."""
    sig = _signature(scale, outline)
    path = CACHE % scale
    if not refresh and os.path.exists(path):
        data = json.load(open(path))
        if data.get("signature") == sig:
            return data
        print("  Unterseite: Zwischenspeicher veraltet, Lagen der Zapfen werden aus dem Konzept neu gelesen ...", flush=True)
    data = _compute(scale)
    data["signature"] = sig
    json.dump(data, open(path, "w"), indent=1)
    return data


# --------------------------------------------------------------------------
# Fadentasche "pille": Geometrie (aus plug.thread.build), Lage
# --------------------------------------------------------------------------
def pille():
    """Maße der Tasche in der Mitte (0, 0); lange Seite (Mündung) in x, Steg quer dazu in y."""
    g = TH.Geo(FADEN_LUFT)
    g.cx = g.cy = 0.0
    g.name = "Campus"
    return g


def pille_world(man, c):
    """Körper der Tasche an die Lage c (Mitte, Achse 'x' oder 'y') setzen."""
    return man.rotate([0, 0, 0 if c["axis"] == "x" else 90]).translate([c["c"][0], c["c"][1], 0])


def pille_cut(g=None):
    """Schnittkörper: Tasche (Halbstadion mit gerundeter Decke) und Fase 45° am Rand der Mündung."""
    g = g or pille()
    return union([TH.cavity(g), TH.chamfer_cutter(g)])


def pille_steg(g=None):
    """Steg von Wand zu Wand (wird nach dem Schnitt wieder zugefügt)."""
    return TH.steg(g or pille())


def mouth_poly(c):
    """Mündung der Tasche samt Fase an der Plattenunterseite."""
    d = pille().d
    lx, ly = (d["mouth_l"], d["mouth_w"]) if c["axis"] == "x" else (d["mouth_w"], d["mouth_l"])
    return sbox(c["c"][0] - lx / 2, c["c"][1] - ly / 2, c["c"][0] + lx / 2, c["c"][1] + ly / 2)


def notch_box(ax, ay, lx, ly, bounds, pad=NOTCH_PAD, near=6.0):
    """Eckaussparung im Unterkasten für eine Tasche in (ax, ay): Mündung lx × ly plus `pad` ringsum; liegt eine Seite näher als `near` am Plattenrand, reicht
    sie bis zum Rand (offen, wie die Eckaussparungen des Konzepts in `build_concept.place_vs`)."""
    x0, y0, x1, y1 = bounds
    nx0, nx1, ny0, ny1 = ax - lx / 2 - pad, ax + lx / 2 + pad, ay - ly / 2 - pad, ay + ly / 2 + pad
    if nx0 - x0 < near:
        nx0 = x0 - 1.0
    if x1 - nx1 < near:
        nx1 = x1 + 1.0
    if ny0 - y0 < near:
        ny0 = y0 - 1.0
    if y1 - ny1 < near:
        ny1 = y1 + 1.0
    return (nx0, ny0, nx1, ny1)


def place_pillen(outline, blocked, extra_block=None, wall=FADEN_WAND, step=0.5, reach=60.0, axes=("x", "y")):
    """Je Ecke die Lage der Tasche (Mündung samt Fase, mit `wall` ringsum) so nah an der Ecke wie möglich (kleinste Summe der Verschiebungen längs und quer);
    beide Ausrichtungen (`axes`: Tupel für alle Ecken oder {Ecke: Tupel}), gleich nah: lange Seite in x. Frei von `blocked` (Mulden, Hof) und `extra_block` (Zapfenlöcher), mit `wall` Abstand zum Plattenrand.
    Die Eckaussparung im Unterkasten (Mündung + NOTCH_PAD, zum Rand offen, siehe `notch_box`) steht in `notch`."""
    d = pille().d
    x0, y0, x1, y1 = outline.bounds
    shapely.prepare(outline)
    obstacles = unary_union([blocked] + ([extra_block] if extra_block is not None else []))
    shapely.prepare(obstacles)
    out = []
    da = np.arange(0, reach, step)
    DA, DB = np.meshgrid(da, da, indexing="ij")
    DA, DB = DA.ravel(), DB.ravel()
    order = np.argsort(DA + DB, kind="stable")
    DA, DB = DA[order], DB[order]
    for name, sx, sy, cx, cy in (("SW", 1, 1, x0, y0), ("SO", -1, 1, x1, y0), ("NW", 1, -1, x0, y1), ("NO", -1, -1, x1, y1)):
        best = None
        for axis in (axes.get(name, ("x", "y")) if isinstance(axes, dict) else axes):
            lx, ly = (d["mouth_l"], d["mouth_w"]) if axis == "x" else (d["mouth_w"], d["mouth_l"])
            ax, ay = cx + sx * (lx / 2 + wall + DA), cy + sy * (ly / 2 + wall + DB)
            foot = shapely.box(ax - lx / 2 - wall, ay - ly / 2 - wall, ax + lx / 2 + wall, ay + ly / 2 + wall)
            ok = shapely.contains(outline, foot) & ~shapely.intersects(obstacles, foot)
            idx = np.where(ok)[0]
            if len(idx) and (best is None or DA[idx[0]] + DB[idx[0]] < best[0]):
                i = idx[0]
                best = (float(DA[i] + DB[i]), axis, float(ax[i]), float(ay[i]), notch_box(float(ax[i]), float(ay[i]), lx, ly, outline.bounds))
        if best is None:
            raise SystemExit("Fadentasche: kein Platz an der Ecke %s (Wand %.1f)" % (name, wall))
        out.append(dict(corner=name, shift=round(best[0], 1), axis=best[1], c=(round(best[2], 2), round(best[3], 2)), notch=best[4], kind="pille"))
    return out


# --------------------------------------------------------------------------
# V-Kanal "v" (Konzept)
# --------------------------------------------------------------------------
def v_items(data, outline):
    """Die vier V des Konzepts (Rohkoordinaten) im Format der Fadenösen: Mitte, Achse, Eintritte, Eckaussparung."""
    x0, y0, x1, y1 = outline.bounds
    out = []
    for v in data["vs"]:
        cx, cy = v["c"]
        ent, _, _ = BC.v_geom(cx, cy, v["axis"])
        corner = ("S" if cy < (y0 + y1) / 2 else "N") + ("W" if cx < (x0 + x1) / 2 else "O")
        out.append(dict(corner=corner, shift=None, axis=v["axis"], c=(round(cx, 2), round(cy, 2)), ent=[list(p) for p in ent],
                        notch=Polygon(v["notch"]).bounds, kind="v", slope=PP.V["slope"]))
    return out


def v_cut(c):
    """Hohlraum eines V (Plattenunterseite bei z = 0): zwei Schenkel, runder Scheitel, Trichter am Bett; Maße des Konzepts (`PP.V`, Ø `V_D`).
    Wie `build_concept.v_solid`, aber beide Schenkel mit `ccw` (dort liegt der Schenkel s = −1 im Uhrzeigersinn und fällt weg: nur ein Schenkel bleibt)."""
    ld, r, apex = V_D, PP.V["entry_r"], PP.V["apex"]
    hs = apex * c["slope"]
    parts = []
    for s in (-1, 1):
        t0, z0, t1, z1 = s * hs * (1 + 0.5 / apex), -0.5, 0.0, apex
        n = np.array([-(z1 - z0), (t1 - t0)])
        n = n / np.linalg.norm(n) * ld / 2
        poly = ccw([(t0 + n[0], z0 + n[1]), (t1 + n[0], z1 + n[1]), (t1 - n[0], z1 - n[1]), (t0 - n[0], z0 - n[1])])
        parts.append(m3d.Manifold.extrude(m3d.CrossSection([poly]), ld).rotate([90, 0, 0]).translate([0, ld / 2, 0]))
    parts.append(m3d.Manifold.cylinder(ld, ld / 2, ld / 2, 16).rotate([90, 0, 0]).translate([0, ld / 2, apex]))
    core = union(parts)
    if c["axis"] == "y":
        core = core.rotate([0, 0, 90])
    core = core.translate([c["c"][0], c["c"][1], 0])
    cones = [m3d.Manifold.cylinder(1.5, r, ld / 2, 24).translate([p[0], p[1], -0.01]) for p in c["ent"]]
    return union([core] + cones)


def v_poly(c):
    """Fußabdruck des V an der Plattenunterseite: Trichter und Kanal."""
    funnels = unary_union([Point(p).buffer(PP.V["entry_r"], 24) for p in c["ent"]])
    line = shapely.LineString([tuple(c["ent"][0]), tuple(c["ent"][1])]).buffer(V_D / 2, cap_style=2)
    return unary_union([funnels, line])


# --------------------------------------------------------------------------
# Gesamtlage und Schnittkörper
# --------------------------------------------------------------------------
def zapfen_circle(c, extra=0.0):
    return Point(c[0], c[1]).buffer(LOCH_D / 2 + extra, 24)


def layout(scale, outline, blocked, refresh=False):
    """Lage aller Aufnahmen: Zapfenlöcher (aus dem Konzept) und vier Fadenösen (Tasche: neu gesucht auf dem echten Umriss; V: aus dem Konzept)."""
    data = concept_layout(scale, outline, refresh)
    if ZAPFEN_LOKAL:                                    # Zapfenlöcher an den Zapfen des gedruckten Unterkastens statt an den Konzept-Lagen
        minx, miny = outline.bounds[:2]
        pins = [[round(minx + x, 3), round(miny + y, 3)] for x, y in ZAPFEN_LOKAL]
        data = dict(data, pins=pins, posts=data["posts"] + [p for p in pins if p not in data["posts"]])
    zap = unary_union([zapfen_circle(p, LOCH_FASE) for p in data["pins"]])
    axes = PILLE_ACHSEN
    if axes is None:                                    # an der Fach-Kante nur die schmale Ausrichtung (Kante N/S: lange Seite in y, Kante W/O: in x)
        axes = {c: ("y",) if data["side"] in "NS" else ("x",) for c in FACH_ECKEN[data["side"]]}
    faden = place_pillen(outline, blocked, extra_block=zap, axes=axes) if FADEN == "pille" else v_items(data, outline)
    return dict(pins=[tuple(p) for p in data["pins"]], posts=[tuple(p) for p in data["posts"]], faden=faden, kind=FADEN, uk_t=data["uk_t"], data=data)


def cuts(lay):
    """Schnittkörper der Unterseite (Rohkoordinaten, Plattenunterseite bei z = 0): Zapfenlöcher mit Fase, Fadenösen."""
    out = []
    for p in lay["pins"]:
        circ = zapfen_circle(p)
        out += [G.extrude(circ, -1.0, LOCH_T), BC.mouth_ch(circ, 0.0, LOCH_FASE)]
    if lay["kind"] == "pille":
        body = pille_cut()
        out += [pille_world(body, c) for c in lay["faden"]]
    else:
        out += [v_cut(c) for c in lay["faden"]]
    return out


def adds(lay):
    """Körper, die nach dem Schnitt wieder zugefügt werden: der Steg in jeder Tasche (beim V keine)."""
    if lay["kind"] != "pille":
        return []
    st = pille_steg()
    return [pille_world(st, c) for c in lay["faden"]]


def faden_polys(lay):
    return [mouth_poly(c) if lay["kind"] == "pille" else v_poly(c) for c in lay["faden"]]


def notch_boxes(lay):
    """Eckaussparungen, die der Unterkasten für die Fadenösen braucht (Rohkoordinaten, offen bis zum Plattenrand): [(x0, y0, x1, y1)]."""
    return [tuple(c["notch"]) for c in lay["faden"]]


def uk_conflicts(lay, outline):
    """Wo die Eckaussparung (Mündung + 2,0 bzw. beim V die des Konzepts) Teile des Konzept-Unterkastens trifft: Stützen, Zapfen, Fach, Elektronik, Schalterraum.
    Rückgabe je Ecke (Name, {Teil: Fläche mm²})."""
    d = lay["data"]
    minx, miny = outline.bounds[0], outline.bounds[1]
    posts = [sbox(x - PP.POST[0] / 2, y - PP.POST[0] / 2, x + PP.POST[0] / 2, y + PP.POST[0] / 2) for x, y in lay["posts"]]
    items = dict(Stützen=unary_union(posts), Fach=unary_union([Polygon(r) for r in d["fach"]]), Elektronik=unary_union([Polygon(r) for r in d["elec"]]),
                 Schalterraum=sbox(minx + PP.UK_WALL, miny + PP.SW_Y - 7.0, minx + BC.SW_DEPTH, miny + PP.SW_Y + 7.0))
    res = []
    for c in lay["faden"]:
        nb = sbox(*c["notch"])
        res.append((c["corner"], {k: round(nb.intersection(g).area, 1) for k, g in items.items() if nb.intersection(g).area > 0.05}))
    return res


# --------------------------------------------------------------------------
# Prüfungen
# --------------------------------------------------------------------------
def section_poly(man, z):
    g = None
    for ring in man.slice(z).to_polygons():
        r = Polygon(ring)
        g = r if g is None else g.symmetric_difference(r)
    return Polygon() if g is None else g.buffer(0)


def walls(base, outline, lay, plate_t):
    """Mindestwand (XY-Abstand) der neuen Aufnahmen zu allen vorhandenen Aussparungen der Platte `base` (ohne Unterseite): Mulden und Pin-Löcher (Schnitte in
    mehreren Höhen unter der Decke der Tasche), Hof (Schnitt über seinem Boden), Plattenrand. Rückgabe {Name: (Zapfenlöcher, Fadenösen)}."""
    inner = outline.buffer(-0.6)                                    # ohne den Ring der Randfasen
    voids = unary_union([inner.difference(section_poly(base, z)) for z in (0.1, 0.5, 1.0, 2.0, 3.0, 5.0, 8.0)])
    hof = inner.difference(section_poly(base, plate_t - P.HOF_DEPTH_T + 0.2)).difference(voids.buffer(0.01))     # nur der Hof
    zap = [zapfen_circle(p, LOCH_FASE) for p in lay["pins"]]
    fd = faden_polys(lay)
    edge = outline.exterior
    res = {}
    res["Mulden und Pin-Löchern"] = (min(g.distance(voids) for g in zap), min(g.distance(voids) for g in fd))
    res["Hof (Aussparung)"] = (min(g.distance(hof) for g in zap) if not hof.is_empty else None,
                               min(g.distance(hof) for g in fd) if not hof.is_empty else None)
    res["Plattenrand"] = (min(g.distance(edge) for g in zap), min(g.distance(edge) for g in fd))
    res["Zapfenloch gegen Fadenöse"] = (min(a.distance(b) for a in zap for b in fd), None)
    return res


def layer_overhang(man, polys, z1, dz=0.2, margin=3.0):
    """Größter Überhang je Schicht (mm, Abstand der neuen Lage zur darunter) in den Fenstern um die neuen Aufnahmen, über alle Lagen bis z1.
    Rückgabe (größter Wert, z der Lage, [(z, Überhang)] der Lagen über 0,25)."""
    win = unary_union([p.buffer(margin) for p in polys])
    worst, zw, many = 0.0, 0.0, []
    prev = section_poly(man, dz / 2).intersection(win)
    k = 1
    while dz * k < z1:
        cur = section_poly(man, dz * k + dz / 2).intersection(win)
        rest = cur.difference(prev.buffer(0.001))
        o = 0.0
        if not rest.is_empty and rest.area > 0.01:                 # Punkte im neuen Bereich (Raster 0,2 mm): größter Abstand zur Lage darunter
            x0, y0, x1, y1 = rest.bounds
            X, Y = np.meshgrid(np.arange(x0, x1 + 1e-9, 0.2), np.arange(y0, y1 + 1e-9, 0.2))
            X, Y = X.ravel(), Y.ravel()
            ins = shapely.contains_xy(rest, X, Y)
            if ins.any():
                o = float(shapely.distance(shapely.points(np.stack([X[ins], Y[ins]], axis=1)), prev).max())
        if o > worst:
            worst, zw = o, dz * k
        if o > 0.25:
            many.append((round(dz * k, 1), round(o, 2)))
        prev = cur
        k += 1
    return worst, zw, many


def compare_rows(old, new, zs=(9.0, 10.0, 12.0, 14.0, 14.5)):
    """Fläche der symmetrischen Differenz der Schnitte alt/neu in Höhen über den neuen Aufnahmen (muss 0 sein): [(z, Differenz mm², Fläche mm²)]."""
    out = []
    for z in zs:
        a, b = section_poly(old, z), section_poly(new, z)
        out.append((z, round(a.symmetric_difference(b).area, 4), round(a.area, 1)))
    return out


def report(plate, lay, outline, plate_t, base):
    """Prüfzeilen für `plug.campus.main` (Platte `plate` und Platte `base` ohne Unterseite als Manifold); Rückgabe True, wenn alle harten Prüfungen bestehen."""
    ok = True
    pille_ = lay["kind"] == "pille"
    print("Unterseite (plug/campus_underside.py; Zapfen aus dem Konzept, Fadenösen: %s):" % ("Tasche mit Steg (plug/thread)" if pille_ else "V-Kanal (Konzept)"))
    print("  %d Zapfenaufnahmen Ø %.1f × %.1f mit Fase %.1f bei %s" % (len(lay["pins"]), LOCH_D, LOCH_T, LOCH_FASE, ", ".join("(%.1f, %.1f)" % p for p in lay["pins"])))
    for c in lay["faden"]:
        if pille_:
            print("  Fadentasche %s: Mitte (%.1f, %.1f), lange Seite in %s, %.1f mm von der Ecke (Summe der Verschiebungen)" % (c["corner"], *c["c"], c["axis"], c["shift"]))
        else:
            print("  V-Kanal %s: Mitte (%.1f, %.1f), Achse %s" % (c["corner"], *c["c"], c["axis"]))
    w = walls(base, outline, lay, plate_t)
    f_lim = FADEN_WAND if pille_ else PP.V["wall"]
    for k, (a, b) in w.items():
        print("  Mindestwand zu %-26s Zapfenlöcher %s · Fadenösen %s" % (k, "%.2f mm" % a if a is not None else "–", "%.2f mm" % b if b is not None else "–"))
        if k == "Plattenrand":
            ok &= a >= WAND_MIN and b >= f_lim - 0.5          # Randfase unten 0,5 zieht den Rand am Bett um 0,5 zurück
        elif k.startswith("Zapfenloch"):
            ok &= a >= WAND_MIN
        else:
            ok &= (a is None or a >= WAND_MIN) and (b is None or b >= f_lim - 1e-6)
    zp = [zapfen_circle(p, LOCH_FASE) for p in lay["pins"]]
    o_z = layer_overhang(plate, zp, LOCH_T + 0.6)
    z_f = (pille().d["ceil"] + 0.6) if pille_ else (PP.V["apex"] + V_D / 2 + 0.6)
    o_f = layer_overhang(plate, faden_polys(lay), z_f)
    print("  Überhang je 0,2-mm-Lage: Zapfenloch größter Sprung %.2f mm bei z = %.1f (Decke Ø %.1f = Brücke %.1f mm, unter 10)" % (o_z[0], o_z[1], LOCH_D, LOCH_D))
    print("  Überhang je 0,2-mm-Lage: %s größter Sprung %.2f mm bei z = %.1f; über 0,25 mm in %d Lagen%s" % (
        "Tasche" if pille_ else "V-Kanal", o_f[0], o_f[1], len(o_f[2]),
        " (Kuppel der Tasche; gedruckt in P3/P45 ohne Support, Decke glatt)" if pille_ and o_f[2] else ""))
    ok &= o_z[0] <= LOCH_D / 2 + 0.3
    cmp_ = compare_rows(base, plate)
    print("  unverändert über den Aufnahmen: Schnittdifferenz alt/neu bei z = %s: %s mm²" % (
        " / ".join("%.1f" % z for z, _, _ in cmp_), " / ".join("%.4f" % a for _, a, _ in cmp_)))
    ok &= all(a < 0.01 for _, a, _ in cmp_)
    print("  Volumen: ohne Unterseite %.2f cm³, mit %.2f cm³ (%.2f cm³ weniger)" % (
        base.volume() / 1000, plate.volume() / 1000, (base.volume() - plate.volume()) / 1000))
    for name, d in uk_conflicts(lay, outline):
        print("  Eckaussparung %s im Unterkasten %s" % (name, ("trifft im Konzept: " + ", ".join("%s %.1f mm²" % kv for kv in d.items())) if d else "kollidiert mit nichts im Konzept"))
    return ok


# --------------------------------------------------------------------------
# Passprobe im Rechner
# --------------------------------------------------------------------------
def thread_chain(lay, c, r=None):
    """Faden Ø FADEN_D, taut vom Hut (unten im Unterkasten) durch die Fadenöse, an die Lage c gesetzt."""
    r = (FADEN_D if r is None else r) / 2
    uk_t = lay["uk_t"] + 2.0                                   # bis unter den Boden des Unterkastens (Faden läuft durch die Eckaussparung zum Hut)
    if lay["kind"] == "pille":
        g = pille()
        d = g.d
        hf, st = d["steg_w"] / 2, d["steg_top"]
        xa = -(hf + d["gap0"] / 2)
        top = TH.arc(0.0, st - hf, hf + 0.4 + 0.02, 165, 15, 15)
        path = [(xa, -uk_t)] + top + [(-xa, -uk_t)]
        return pille_world(TH.chain(path, r, g), c)
    ent = [np.array(p) for p in c["ent"]]
    mid = (ent[0] + ent[1]) / 2
    hs = float(np.linalg.norm(ent[1] - ent[0])) / 2
    ax = (ent[1] - ent[0]) / (2 * hs)
    apex = PP.V["apex"]
    t0 = hs * (1 + 0.5 / apex)
    pts = []
    for t, z in ((-t0, -uk_t), (-t0, -0.5), (0.0, apex), (t0, -0.5), (t0, -uk_t)):
        p = mid + ax * t
        pts.append((float(p[0]), float(p[1]), z))
    return union([capsule(a, b, r, 8) for a, b in zip(pts[:-1], pts[1:])])


def passprobe(scale):
    """Zapfen und Faden des Unterkastens im Konzept (`variant`) in die Platte setzen: Kollision, Spiel, Lage."""
    from plug import campus as CA
    print("Passprobe im Rechner: Konzept-Unterkasten (build_concept.variant) gegen die Steckplatte mit Aufnahmen ...", flush=True)
    BC.variant(scale)                                      # setzt BC.LAST["uk"] (Unterkasten, Konzeptkoordinaten: Plattenoberseite z = 0)
    uk = BC.LAST["uk"]
    plate, _, _, _, outline, _ = CA.build(scale)
    lay = CA.UNTEN_INFO["lay"]
    uk0 = uk.translate([0, 0, -BC.H0["deck"]])             # Unterkasten in der Lage der Platte (Unterseite z = 0), gleiche Rohkoordinaten
    ok = True

    def line(txt, val, limit=0.05):
        nonlocal ok
        good = val <= limit
        ok &= good
        print("  %-100s %8.3f mm³  %s" % (txt, val, "ok" if good else "KOLLISION"))

    print("Zapfen:")
    line("Unterkasten des Konzepts (Schale, Stützen, Zapfen) in der Platte, Überschneidungsvolumen", vol_int(plate, uk0))
    c1, c2 = vol_int(plate, uk0.translate([0.10, 0, 0])), vol_int(plate, uk0.translate([0.20, 0, 0]))
    print("  Kontrolle: Unterkasten 0,10 seitlich verschoben %.3f mm³ (Spiel 0,15 reicht), 0,20 seitlich %.3f mm³ (%s)" % (
        c1, c2, "stößt an, die Prüfung greift" if c2 > 0.05 else "KEIN Anstoß: Prüfung wertlos"))
    ok &= c1 <= 0.05 and c2 > 0.05
    pins_only = union([BC.pin_solid_at(Point(*p), 0.0, ZAPFEN, PP.CH_PIN) for p in lay["pins"]])
    line("nur die Zapfen (Ø %.1f × %.1f, Fase %.1f) in den Aufnahmen, nominal (an den Lagen der Platte)" % (ZAPFEN["d"], ZAPFEN["h"], PP.CH_PIN), vol_int(plate, pins_only))
    u1, u2 = vol_int(plate, pins_only.translate([0, 0, 0.25])), vol_int(plate, pins_only.translate([0, 0, 0.35]))
    print("  Kontrolle: Zapfen 0,25 höher %.3f mm³ (Luft über der Spitze 0,3), 0,35 höher %.3f mm³ (%s)" % (
        u1, u2, "stößt oben an, die Prüfung greift" if u2 > 0.05 else "KEIN Anstoß: Prüfung wertlos"))
    ok &= u1 <= 0.05 and u2 > 0.05
    for spiel in (0.10, 0.05, 0.0):
        dd = LOCH_D - 2 * spiel
        pin = union([BC.pin_solid_at(Point(*p), 0.0, dict(ZAPFEN, d=dd), PP.CH_PIN) for p in lay["pins"]])
        print("  Kontrolle: Zapfen mit %.2f Spiel je Seite (Ø %.2f) in der Aufnahme: %.3f mm³" % (spiel, dd, vol_int(plate, pin)))
    print("  Lage: Zapfen bei %s, Stützen bei %s (Rohkoordinaten der Platte)" % (
        ", ".join("(%.1f, %.1f)" % p for p in lay["pins"]), ", ".join("(%.0f, %.0f)" % p for p in lay["posts"])))

    print("Faden Ø %s (doppelt genommen, ungemessen), je Ecke vom Hut durch die Fadenöse (%s):" % (TH.de(FADEN_D, 1), lay["kind"]))
    for c in lay["faden"]:
        fd = thread_chain(lay, c)
        a = vol_int(plate, fd)
        b = vol_int(uk0, fd)
        nb = sbox(*c["notch"])
        rest = vol_int(uk0 - G.extrude(nb, -lay["uk_t"] - 3.0, 1.0), fd)
        print("  %s: Faden gegen Platte %.3f mm³ · gegen den Unterkasten des Konzepts (Faden bis unter den Boden) %.3f mm³ · gegen den Unterkasten mit Eckaussparung %.0f × %.0f %.3f mm³" % (
            c["corner"], a, b, nb.bounds[2] - nb.bounds[0], nb.bounds[3] - nb.bounds[1], rest))
        ok &= a <= 0.2 and rest <= 0.05
    print("  Eckaussparungen, die der Unterkasten braucht (Rohkoordinaten x0, y0, x1, y1, offen zum Rand): %s" % "; ".join(
        "%s %s" % (c["corner"], tuple(round(x, 1) for x in c["notch"])) for c in lay["faden"]))
    print("-> Passprobe: %s" % ("keine Kollisionen" if ok else "KOLLISION"))
    return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scale", type=int, default=P.SCALE_PLAN)
    ap.add_argument("--faden", choices=("pille", "v"), default=FADEN)
    a = ap.parse_args()
    from plug import campus_underside as M        # unter `python -m` ist dieses Modul `__main__`; plug.campus benutzt die Paketfassung
    M.FADEN = a.faden
    raise SystemExit(0 if passprobe(a.scale) else 1)


if __name__ == "__main__":
    main()
