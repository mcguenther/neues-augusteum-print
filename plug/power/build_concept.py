"""Konzept Stromversorgung: Powerbank Intenso XS5000 in der Grundplatte des Campusmodells, Ösen für den Doktorhut.

Aufbau (Stand 2): Oberplatte + hohler Unterkasten.

- Oberplatte: nur so dick wie nötig, also Mulde (Fußhöhe F) + Muldenboden (CEIL) + Körper der Winkelleiste (HDR_BODY).
  Die Leiste sitzt in einer nach unten offenen Tasche, die Lötenden zeigen in den Unterkasten. Glatte Unterseite, keine Brücken.
- Unterkasten (ersetzt den Deckel): Boden, Außenwand, Stützen unter der Oberplatte, Zaun um die Powerbank, Elektronik.
  Innen hohl: Kabel liegen frei. Wird offen nach oben gedruckt.
- Powerbank: Anschlussseite zur Plattenkante, davor Platz für einen geraden USB-A-Stecker, das Kabel läuft in einem Kanal
  an der Längsseite zurück. Taste und Ladebuchsen durch ein Fenster in der Kante (Taste über einen Stößel).
- Ösen: vier Blöcke im Unterkasten mit je zwei Fadenlöchern; ihr Zapfen greift in die Oberplatte, darüber ein Tunnel
  (Öse). Die Fadenschlaufe läuft von unten durch den Unterkasten über die Öse und wieder hinunter zum Doktorhut; so
  zieht der Faden die Oberplatte auf den Unterkasten.

Varianten: Unterkasten bei 1:1000 und 1:1500, Hof-Fach (Powerbank ganz unter dem Innenhof, Hof als Deckel) beim
kleinsten Maßstab, bei dem das Fach in den Hof passt. Dazu der bisherige Stand (Oberplatte 16,2 + Unterkasten 15,0)
zum Vergleich des Materials.

Aufruf aus dem Repo-Wurzelverzeichnis: `python3 -m plug.power.build_concept` (rund 15 s).
"""
import json
import math
import os
import sys

import numpy as np
import shapely
from shapely import affinity
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import generate as G  # noqa: E402
import innenhof  # noqa: E402
from plug import dupont as sd  # noqa: E402
from plug.geom import encode  # noqa: E402
from plug.parts import (CEIL, CLR, ESP_BOX, HDR_BODY, HOF_LEDGE, HUT, OESE, PB_CABLE, PB_CLR, PB_CLR_Z,  # noqa: E402
                        PB_EFF, PB_G, PB_IMAX, PB_KEEP_MA, PB_L, PB_PLUG, PB_PORT_V, PB_PORTS, PB_SLEEP_S, PB_T,
                        PB_W, PB_WH, UK_CABLE_H, UK_FLOOR, UK_WALL)

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "concept.template.html")
OUT = os.path.join(HERE, "concept.html")

FACH_L = PB_PLUG + PB_L + 2 * PB_CLR       # Fach entlang der Powerbank: Steckerraum + Powerbank
FACH_W = PB_W + 2 * PB_CLR + PB_CABLE      # quer: Powerbank + Kabelkanal
FACH_H = sd.layer_up(PB_T + PB_CLR_Z)
FENCE = (1.6, 5.0)       # Zaun um die Powerbank: Breite, Höhe über dem Boden
POST = (6.0, 40.0)       # Stützen unter der Oberplatte: Kante, Raster
PLA = 1.24               # g/cm³
SHELL, INFILL = 1.0, 0.15   # Schätzung Material: 1 mm Hülle (3 Wände, 4 Decken-/Bodenschichten), 15 % Füllung

# bisheriger Stand (erste Fassung des Konzepts), nur für den Materialvergleich
OLD = dict(ober=16.2, fach_h=13.4, floor=1.6)


def heights():
    """z-Lagen (Plattenoberseite = 0)."""
    d = sd.dims()
    deck = -(d["F"] + CEIL + HDR_BODY)                 # Unterseite Oberplatte = Unterkante Leistenkörper
    uk_bot = deck - FACH_H - UK_FLOOR
    hof_bot = min(deck - UK_CABLE_H, -G.POCKET_DEPTH - FACH_H) - UK_FLOOR
    return dict(F=d["F"], ceil=CEIL, body=HDR_BODY, z_hb=d["z_hb"], z_bb=d["z_bb"], z_tip=d["z_tip"],
                deck=deck, fach_h=FACH_H, floor=UK_FLOOR, uk_bot=uk_bot, total_uk=-uk_bot, uk_t=deck - uk_bot,
                hof_bot=hof_bot, total_hof=-hof_bot, pocket=G.POCKET_DEPTH,
                old_ober=OLD["ober"], old_total=OLD["ober"] + OLD["fach_h"] + OLD["floor"])


# --------------------------------------------------------------------------
# Einpassen
# --------------------------------------------------------------------------
def fit_rect(poly, L, W, res=0.5, step=2):
    """Rechteck L × W in poly (beliebig gedreht): (Winkel der L-Achse in Grad, Mitte) der mittigsten Lage oder None."""
    c = poly.centroid
    best = None
    for th in range(0, 180, step):
        p = affinity.rotate(poly, -th, origin=c)
        x0, y0, x1, y1 = p.bounds
        xs = np.arange(x0, x1, res) + res / 2
        ys = np.arange(y0, y1, res) + res / 2
        X, Y = np.meshgrid(xs, ys)
        M = shapely.contains_xy(p, X, Y).astype(np.int32)
        S = np.zeros((M.shape[0] + 1, M.shape[1] + 1), np.int64)
        S[1:, 1:] = M.cumsum(0).cumsum(1)
        for a, b, rot in ((L, W, 0), (W, L, 90)):
            nx, ny = int(math.ceil(a / res)), int(math.ceil(b / res))
            if nx >= M.shape[1] or ny >= M.shape[0]:
                continue
            win = S[ny:, nx:] - S[:-ny, nx:] - S[ny:, :-nx] + S[:-ny, :-nx]
            ok = np.argwhere(win == nx * ny)
            if not len(ok):
                continue
            k = ((ok - ok.mean(0)) ** 2).sum(1).argmin()
            j, i = ok[k]
            ctr = affinity.rotate(shapely.Point(xs[i] + (nx - 1) * res / 2, ys[j] + (ny - 1) * res / 2), th, origin=c)
            if best is None or len(ok) > best[2]:
                best = ((th + rot) % 180, (ctr.x, ctr.y), len(ok))
    return best


def hof_limit(lo=300, hi=1000, tol=5):
    """Kleinster Maßstab (größte Zahl), bei dem das Fach mit Auflage ganz in den Innenhof passt."""
    while hi - lo > tol:
        mid = (lo + hi) / 2
        s = 1000.0 / mid
        fps = {k: v[1] for k, v in G.osm_models(s).items()}
        ok = fit_rect(innenhof.flaeche_mm(fps.values(), s).buffer(-HOF_LEDGE, join_style=2), FACH_L, FACH_W,
                      step=3) is not None
        print("  1:%d %s" % (mid, "passt" if ok else "zu klein"), flush=True)
        lo, hi = (mid, hi) if ok else (lo, mid)
    return int(lo), int(lo // 10 * 10)


def hof_width(hof_fp):
    """Breite des Innenhofs quer zur Hofachse (mm): Median, Minimum über die mittleren 80 % der Länge, Länge."""
    d, n = innenhof.achse(innenhof.load())
    c = np.array(hof_fp.centroid.coords[0])
    proj = [float(np.dot(np.array(q) - c, d)) for q in hof_fp.exterior.coords]
    lo, hi = min(proj), max(proj)
    ws = []
    for t in np.linspace(lo + 0.1 * (hi - lo), hi - 0.1 * (hi - lo), 60):
        p = c + t * d
        cut = shapely.LineString([p - 500 * n, p + 500 * n]).intersection(hof_fp)
        if not cut.is_empty:
            ws.append(cut.length)
    return float(np.median(ws)), float(min(ws)), hi - lo


class Frame:
    """Fach-Koordinaten: u von der Anschlussseite ins Fach, v quer (Kabelkanal bei +v). Mitte des Fachs = (0, 0)."""

    def __init__(self, cx, cy, ang, sgn=1):
        a = math.radians(ang)
        self.c = np.array([cx, cy])
        self.u = np.array([math.cos(a), math.sin(a)])
        self.v = sgn * np.array([-math.sin(a), math.cos(a)])
        self.ang, self.sgn = ang, sgn

    def pt(self, u, v):
        return self.c + u * self.u + v * self.v

    def rect(self, u0, u1, v0, v1):
        return Polygon([self.pt(u0, v0), self.pt(u1, v0), self.pt(u1, v1), self.pt(u0, v1)]).buffer(0)


# Lage im Fach (u, v): Steckerraum, Powerbank, Kabelkanal
U0, U1 = -FACH_L / 2, FACH_L / 2
V0, V1 = -FACH_W / 2, FACH_W / 2
BU0 = U0 + PB_PLUG + PB_CLR                 # Anschlussseite der Powerbank
BV0 = V0 + PB_CLR
BVC = BV0 + PB_W / 2                         # Mitte der Powerbank quer
KV0 = V1 - PB_CABLE                          # Kabelkanal


def fach_parts(f):
    port = {k: f.pt(BU0, BVC + v).round(2).tolist() for k, v in PB_PORT_V.items()}
    ua = BVC + PB_PORT_V["usb_a"]
    plug_end = BU0 - 25.0
    kc = KV0 + PB_CABLE / 2
    cable = [f.pt(BU0, ua), f.pt(plug_end, ua), f.pt(plug_end - 5, (ua + kc) / 2), f.pt(plug_end, kc),
             f.pt(U1, kc), f.pt(U1 + 12, kc)]
    inner = f.rect(BU0 - PB_CLR, U1, V0, KV0)
    fence = inner.buffer(FENCE[0], join_style=2).difference(inner) \
        .difference(f.rect(U0 - 5, BU0 + 2, V0 - 5, V1 + 5)).difference(f.rect(BU0, U1 + 5, KV0 - 0.1, V1 + 5))
    return dict(
        fach=f.rect(U0, U1, V0, V1), body=f.rect(BU0, BU0 + PB_L, BV0, BV0 + PB_W),
        niche=f.rect(U0, BU0 - PB_CLR, V0, V1), channel=f.rect(BU0 - PB_CLR, U1, KV0, V1),
        plug=f.rect(plug_end, BU0, ua - 7.5, ua + 7.5),
        rod=f.rect(U0 - UK_WALL, BU0, BVC + PB_PORT_V["taste"] - 2, BVC + PB_PORT_V["taste"] + 2),
        window=f.rect(U0 - UK_WALL - 1, U0 + 0.5, V0 + 2, KV0 - 2), fence=fence,
        cable=[np.round(p, 2).tolist() for p in cable], port=port, far=f.pt(U1, kc))


def place_edge(outline, hof_fp):
    """Unterkasten: Anschlussseite an einer Plattenkante, Powerbank möglichst weit unter dem Innenhof."""
    inner = outline.buffer(-UK_WALL, join_style=2)
    x0, y0, x1, y1 = inner.bounds
    hc = hof_fp.centroid
    best = None
    for side, ang in (("W", 0), ("O", 180), ("S", 90), ("N", 270)):
        for sgn in (1, -1):
            if side in "WO":
                cy = min(max(hc.y, y0 + FACH_W / 2), y1 - FACH_W / 2)
                cx = x0 + FACH_L / 2 if side == "W" else x1 - FACH_L / 2
            else:
                cx = min(max(hc.x, x0 + FACH_W / 2), x1 - FACH_W / 2)
                cy = y0 + FACH_L / 2 if side == "S" else y1 - FACH_L / 2
            f = Frame(cx, cy, ang, sgn)
            fp = fach_parts(f)
            if not inner.buffer(1e-6).contains(fp["fach"]):
                continue
            score = fp["body"].intersection(hof_fp).area
            if best is None or score > best[0] + 1:
                best = (score, side, f)
    return best[1], best[2]


def place_box(inner, blocked, near, size):
    a, b = size
    x0, y0, x1, y1 = inner.bounds
    best = None
    for w, h in ((a, b), (b, a)):
        for x in np.arange(x0 + w / 2, x1 - w / 2, 1.0):
            for y in np.arange(y0 + h / 2, y1 - h / 2, 1.0):
                r = box(x - w / 2, y - h / 2, x + w / 2, y + h / 2)
                if not inner.contains(r) or r.intersects(blocked):
                    continue
                d = math.hypot(x - near[0], y - near[1])
                if best is None or d < best[0]:
                    best = (d, r)
    return best[1]


def eyelets(outline, blocked):
    """Vier Ösen, je so nah an der Ecke wie möglich (Block längs oder quer), frei von Mulden, Hof, Fach und Elektronik."""
    x0, y0, x1, y1 = outline.bounds
    inner = outline.buffer(-1.0, join_style=2)
    out = []
    for sx, sy, cx, cy in ((1, 1, x0, y0), (-1, 1, x1, y0), (1, -1, x0, y1), (-1, -1, x1, y1)):
        best = None
        for L, B, along_x in ((OESE["L"], OESE["B"], True), (OESE["B"], OESE["L"], False)):
            for dx in np.arange(1.5, 90, 0.5):
                for dy in np.arange(1.5, 90, 0.5):
                    if best is not None and math.hypot(dx, dy) >= best[0]:
                        break
                    px, py = cx + sx * (dx + L / 2), cy + sy * (dy + B / 2)
                    r = box(px - L / 2, py - B / 2, px + L / 2, py + B / 2)
                    if inner.contains(r) and not r.buffer(1.2).intersects(blocked):
                        best = (math.hypot(dx, dy), r, (px, py), along_x)
        out.append(dict(rect=best[1], c=best[2], x=best[3]))
    return out


def oese_holes(o):
    """Die zwei Fadenlöcher (Mitte) und der Tunnel einer Öse als Rechtecke."""
    (cx, cy), p, hh = o["c"], OESE["pitch"] / 2, OESE["hole"] / 2
    if o["x"]:
        hs = [box(cx + d - hh, cy - hh, cx + d + hh, cy + hh) for d in (-p, p)]
        tun = box(cx - p - hh, cy - hh, cx + p + hh, cy + hh)
    else:
        hs = [box(cx - hh, cy + d - hh, cx + hh, cy + d + hh) for d in (-p, p)]
        tun = box(cx - hh, cy - p - hh, cx + hh, cy + p + hh)
    return hs, tun


def unterkasten_cut(length, deck_cuts, avoid):
    """Schnitte des Unterkastens (y), versetzt zu denen der Oberplatte, nicht durch Fach, Elektronik, Ösen."""
    if length <= G.BED_SIZE:
        return []
    n = math.ceil(length / G.BED_SIZE)
    cuts = []
    for k in range(1, n):
        target = length * k / n
        best = None
        for y in np.arange(length - (n - k) * G.BED_SIZE + 3, k * G.BED_SIZE - 3, 0.5):
            if any(abs(y - c) < 25 for c in deck_cuts):
                continue
            line = shapely.LineString([(-1e4, y), (1e4, y)])
            if any(line.intersects(a) for a in avoid):
                continue
            if best is None or abs(y - target) < abs(best - target):
                best = y
        cuts.append(round(float(best), 1) if best is not None else None)
    return cuts


# --------------------------------------------------------------------------
# Geometrie für Seite und 3D
# --------------------------------------------------------------------------
def coords(geom, sh):
    out = []
    for p in G.polys_of(geom):
        out.append([[round(x + sh[0], 2), round(y + sh[1], 2)] for x, y in list(p.exterior.coords)[:-1]])
    return out


def mesh(man, sh):
    return encode(G.to_trimesh(man.translate([sh[0], sh[1], 0])))


def grams(man):
    """(Material in g bei SHELL mm Hülle und INFILL Füllung, Volumen in cm³); Schätzung."""
    tm = G.to_trimesh(man)
    V = float(abs(tm.volume))
    shell = min(V, float(tm.area) * SHELL)
    return [round((shell + INFILL * (V - shell)) / 1000 * PLA), round(V / 1000, 1)]


def section(outline, fps, hof_fp, f):
    """Schnitt entlang der Powerbank-Mitte: Abschnitte (t0, t1) ab der Plattenkante auf der Anschlussseite."""
    p_mid = f.pt(0, BVC)
    far = 2000.0
    line = shapely.LineString([p_mid - far * f.u, p_mid + far * f.u])
    seg = line.intersection(outline)
    p0 = np.array(seg.coords[0])
    if np.dot(p0 - p_mid, f.u) > 0:
        p0 = np.array(seg.coords[-1])
    t = lambda pt: float(np.dot(np.array(pt) - p0, f.u))  # noqa: E731
    items = []
    for kind, title, g in [("bld", b["title"], fps[b["slug"]]) for b in G.BUILDINGS] + [("hof", "Innenhof", hof_fp)]:
        cut = g.intersection(line)
        for part in getattr(cut, "geoms", [cut]):
            if part.is_empty or part.length < 0.5:
                continue
            ts = sorted(t(c) for c in part.coords)
            items.append(dict(kind=kind, title=title, t0=round(ts[0], 1), t1=round(ts[-1], 1)))
    return dict(len=round(seg.length, 1), items=sorted(items, key=lambda i: i["t0"]), u0=round(t(f.pt(U0, BVC)), 1))


def variant(key, scale, mode, h, hof_scale=None):
    s = 1000.0 / scale
    m = G.osm_models(s)
    fps = {k: v[1] for k, v in m.items()}
    hof_solid, hof_fp, _ = innenhof.model(s, list(fps.values()))
    sel = list(G.BUILDINGS)
    foot_fp = unary_union([fps[b["slug"]] for b in sel])
    fp_all = unary_union([foot_fp, hof_fp])
    outline = G.plate_outline(fp_all)
    minx, miny, maxx, maxy = outline.bounds
    sh = (-minx, -miny)
    W, L = maxx - minx, maxy - miny
    deck_cuts = [round(c - miny, 1) for c in G.tile_cuts(outline, fp_all)]
    inner = outline.buffer(-UK_WALL, join_style=2)
    mulden_fp = foot_fp.buffer(CLR, join_style=2)
    pocket_fp = hof_fp.buffer(G.POCKET_CLEARANCE, join_style=2)
    deck_z = h["deck"]

    if mode == "unterkasten":
        side, f = place_edge(outline, hof_fp)
        bot, thick = h["uk_bot"], h["total_uk"]
    else:
        ang, ctr, _ = fit_rect(hof_fp.buffer(-HOF_LEDGE, join_style=2), FACH_L, FACH_W)
        f = Frame(ctr[0], ctr[1], ang)
        side = None
        bot, thick = h["hof_bot"], h["total_hof"]
    fp = fach_parts(f)
    elec = place_box(inner.buffer(-1), fp["fach"].buffer(4.0, join_style=2), fp["far"], ESP_BOX)
    oes = eyelets(outline, unary_union([mulden_fp.buffer(1.0), pocket_fp, fp["fach"].buffer(2), elec.buffer(2)]))
    oe_rects = [o["rect"] for o in oes]

    # Stützen unter der Oberplatte
    free = inner.buffer(-POST[0]).difference(unary_union([fp["fach"].buffer(3), elec.buffer(3)] +
                                                          [r.buffer(3) for r in oe_rects]))
    posts = []
    for x in np.arange(minx + POST[1] / 2, maxx, POST[1]):
        for y in np.arange(miny + POST[1] / 2, maxy, POST[1]):
            r = box(x - POST[0] / 2, y - POST[0] / 2, x + POST[0] / 2, y + POST[0] / 2)
            if free.contains(r):
                posts.append(r)

    # --- Oberplatte ---
    pin, up, hole = OESE["pin"], OESE["up"], OESE["hole"]
    deck = G.extrude(outline, deck_z, 0.0) - G.extrude(mulden_fp, -h["F"], 1.0) \
        - G.extrude(pocket_fp, -G.POCKET_DEPTH, 1.0)
    cuts = []
    for o in oes:
        hs, tun = oese_holes(o)
        cuts.append(G.extrude(o["rect"].buffer(0.25, join_style=2), deck_z - 1, deck_z + pin + 0.2))
        cuts += [G.extrude(r, deck_z - 1, deck_z + pin + up) for r in hs]
        cuts.append(G.extrude(tun, deck_z + pin + up - hole, deck_z + pin + up))
    if mode == "hof":
        cuts.append(G.extrude(fp["fach"], bot + UK_FLOOR, 1.0))
    deck = deck - G.union(cuts)

    # --- Unterkasten ---
    solids = [G.extrude(outline, bot, bot + UK_FLOOR),
              G.extrude(outline.difference(outline.buffer(-UK_WALL, join_style=2)), bot, deck_z)]
    solids += [G.extrude(r, bot, deck_z) for r in posts]
    solids += [G.extrude(r, bot, deck_z + pin) for r in oe_rects]
    if mode == "unterkasten":
        solids.append(G.extrude(fp["fence"], bot, bot + UK_FLOOR + FENCE[1]))
    uk = G.union(solids)
    holes = []
    for o in oes:
        holes += [G.extrude(r, bot - 1, deck_z + pin + 1) for r in oese_holes(o)[0]]
    if mode == "unterkasten":
        holes.append(G.extrude(fp["window"], bot + UK_FLOOR, deck_z + 0.5))
    uk = uk - G.union(holes)

    uk_cuts = unterkasten_cut(L, deck_cuts, [affinity.translate(g, *sh) for g in [fp["fach"], elec] + oe_rects])
    bld = {b["slug"]: mesh(m[b["slug"]][0] + G.extrude(fps[b["slug"]], -h["F"], 0.01), sh) for b in sel}
    mat = dict(deck=grams(deck), uk=grams(uk))
    if key == "uk1000":
        old_deck = G.extrude(outline, -OLD["ober"], 0.0) - G.extrude(mulden_fp, -h["F"], 1.0) \
            - G.extrude(pocket_fp, -G.POCKET_DEPTH, 1.0)
        z_t = -OLD["ober"]
        z_b = z_t - OLD["fach_h"] - OLD["floor"]
        old_uk = G.extrude(outline, z_b, z_t) - G.extrude(fp["fach"], z_t - OLD["fach_h"], z_t + 1) \
            - G.extrude(elec, z_b + OLD["floor"], z_t + 1)
        mat.update(old_deck=grams(old_deck), old_uk=grams(old_uk))

    return dict(
        key=key, scale=scale, mode=mode, s=s, plate=[round(W, 1), round(L, 1)], thick=round(thick, 1), bot=bot,
        outline=coords(outline, sh), deck_cuts=deck_cuts, uk_cuts=uk_cuts, x_cuts=math.ceil(W / G.BED_SIZE),
        tiles=math.ceil(W / G.BED_SIZE) * (len(deck_cuts) + 1),
        buildings=[dict(slug=b["slug"], title=b["title"], poly=coords(fps[b["slug"]], sh),
                        h=round(float(G.to_trimesh(m[b["slug"]][0]).bounds[1][2]), 1)) for b in sel],
        hof=coords(hof_fp, sh), hof_w=[round(x, 1) for x in hof_width(hof_fp)],
        hub=round(innenhof.hub(innenhof.load(), s), 2),
        fach=coords(fp["fach"], sh), body=coords(fp["body"], sh), niche=coords(fp["niche"], sh),
        channel=coords(fp["channel"], sh), plug=coords(fp["plug"], sh), rod=coords(fp["rod"], sh),
        cable=[[p[0] + sh[0], p[1] + sh[1]] for p in fp["cable"]],
        ports={k: [p[0] + sh[0], p[1] + sh[1]] for k, p in fp["port"].items()},
        elec=coords(elec, sh), posts=[coords(r, sh)[0] for r in posts],
        oesen=[dict(rect=coords(o["rect"], sh)[0], c=[o["c"][0] + sh[0], o["c"][1] + sh[1]], x=o["x"]) for o in oes],
        frame=dict(ang=f.ang, sgn=f.sgn, c=[f.c[0] + sh[0], f.c[1] + sh[1]]), side=side,
        under_hof=round(fp["body"].intersection(hof_fp).area / fp["body"].area * 100),
        hut=dict(size=HUT, fits=bool(W <= HUT and L <= HUT)),
        section=section(outline, fps, hof_fp, f), material=mat, hof_scale=hof_scale,
        meshes=dict(deck=mesh(deck, sh), uk=mesh(uk, sh), buildings=bld, hof=mesh(hof_solid, sh)),
    )


def main():
    h = heights()
    print("Höhen:", {k: round(v, 2) for k, v in h.items()})
    print("Suche den Maßstab, bei dem das Fach ganz unter den Innenhof passt …")
    lim_exact, lim = hof_limit()
    print("  Grenze: 1:%d, gerundet 1:%d" % (lim_exact, lim))
    variants = [variant("uk1000", 1000, "unterkasten", h), variant("uk1500", 1500, "unterkasten", h),
                variant("hof", lim, "hof", h, hof_scale=lim)]
    for v in variants:
        print("  %s 1:%d Platte %.1f × %.1f × %.1f mm, Druckteile %d, Powerbank %d %% unter dem Hof, Kante %s, "
              "Schnitte Oberplatte %s / Unterkasten %s, Material %s"
              % (v["key"], v["scale"], *v["plate"], v["thick"], v["tiles"], v["under_hof"], v["side"],
                 v["deck_cuts"], v["uk_cuts"], v["material"]))
    data = dict(
        heights=h, variants=variants,
        pb=dict(L=PB_L, W=PB_W, T=PB_T, g=PB_G, wh=PB_WH, eff=PB_EFF, imax=PB_IMAX, sleep=PB_SLEEP_S, keep=PB_KEEP_MA,
                ports=PB_PORTS, port_v=PB_PORT_V, clr=PB_CLR, clr_z=PB_CLR_Z, plug=PB_PLUG, cable=PB_CABLE),
        fach=dict(L=FACH_L, W=FACH_W, H=FACH_H, ledge=HOF_LEDGE, u0=U0, bu0=BU0, bv0=BV0, kv0=KV0),
        uk=dict(floor=UK_FLOOR, wall=UK_WALL, cable_h=UK_CABLE_H, fence=FENCE, post=POST), oese=OESE, hut=HUT,
        esp=ESP_BOX, hof_limit=lim, hof_limit_exact=lim_exact, mat=dict(shell=SHELL, infill=INFILL, pla=PLA),
        led_buildings=[b["title"] for b in G.BUILDINGS],
    )
    tpl = open(TEMPLATE, encoding="utf-8").read()
    html = tpl.replace("/*DATA*/", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    open(OUT, "w", encoding="utf-8").write(html)
    print("geschrieben:", os.path.relpath(OUT, ROOT), "(%.1f MB)" % (len(html) / 1e6))


if __name__ == "__main__":
    main()
