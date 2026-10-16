"""Konzept Stromversorgung: Powerbank Intenso XS5000 in der Grundplatte des Campusmodells.

Rechnet drei Varianten durch und baut daraus die Seite `plug/power/concept.html`:

- Unterkasten 1:1000 und 1:1500: Die Grundplatte (Dock A, wie beim Institutsgebäude) bekommt statt des Deckels einen
  Unterkasten. Darin liegt die Powerbank unter dem Innenhof (sie ragt unter die Nachbargebäude), die Anschlussseite
  zeigt zur Plattenkante. Der Unterkasten wird offen nach oben gedruckt, das Fach braucht keine Brücke.
- Hof-Fach: Die Powerbank liegt ganz unter dem Innenhof, das herausnehmbare Innenhof-Teil ist der Deckel. Dafür muss
  der Hof breit genug sein; die Suche liefert den kleinsten Maßstab, bei dem das Fach in den Hof passt.

Grundrisse aus OSM (`generate.osm_models`), Innenhof aus `innenhof.py`. Konstanten der Powerbank in `plug/parts.py`.
Aufruf aus dem Repo-Wurzelverzeichnis: `python3 -m plug.power.build_concept` (rund 1 min, fast alles die Maßstabssuche).
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
from plug.parts import (ESP_BOX, HOF_LEDGE, LID_T, PB_CLR, PB_CLR_Z, PB_EFF, PB_G, PB_IMAX, PB_KEEP_MA, PB_L,  # noqa: E402
                        PB_PLUG, PB_PORTS, PB_SLEEP_S, PB_T, PB_W, PB_WH, UK_FLOOR, UK_WALL, CLR)

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "concept.template.html")
OUT = os.path.join(HERE, "concept.html")

FACH_L = PB_L + 2 * PB_CLR            # Fach innen, ohne Steckerraum
FACH_W = PB_W + 2 * PB_CLR
FACH_H = sd.layer_up(PB_T + PB_CLR_Z)


def heights():
    """z-Lagen (Plattenoberseite = 0) für Dock A, Unterkasten und Hof-Fach."""
    d = sd.dims()
    z_lt = sd.layer_down(d["z_bend"] - 3.0)          # wie plug/institute.py: nur Dock A
    uk_top = z_lt
    uk_fach = uk_top - FACH_H
    uk_bot = uk_fach - UK_FLOOR
    hof_fach = -G.POCKET_DEPTH - FACH_H
    return dict(F=d["F"], z_hb=d["z_hb"], z_bb=d["z_bb"], z_tip=d["z_tip"], z_lt=z_lt, z_lb=z_lt - LID_T,
                plate_A=-(z_lt - LID_T), ober=-z_lt, uk_top=uk_top, uk_fach=uk_fach, uk_bot=uk_bot,
                uk_t=uk_top - uk_bot, total_uk=-uk_bot, hof_fach=hof_fach, hof_floor=hof_fach - UK_FLOOR,
                pocket=G.POCKET_DEPTH, fach_h=FACH_H)


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


def oriented(cx, cy, ang, L, W, off=0.0):
    """Rechteck L (entlang ang) × W um (cx, cy), entlang verschoben um off."""
    r = box(-L / 2 + off, -W / 2, L / 2 + off, W / 2)
    return affinity.translate(affinity.rotate(r, ang, origin=(0, 0)), cx, cy)


def models(scale):
    s = 1000.0 / scale
    m = G.osm_models(s)
    fps = {k: v[1] for k, v in m.items()}
    hof = innenhof.model(s, list(fps.values()))
    return s, m, fps, hof


def hof_limit(lo=300, hi=1000, tol=5):
    """Kleinster Maßstab (größte Zahl), bei dem Fach + Steckerraum mit Auflage ganz in den Innenhof passt."""
    L, W = FACH_L + PB_PLUG, FACH_W
    while hi - lo > tol:
        mid = (lo + hi) / 2
        s = 1000.0 / mid
        fps = {k: v[1] for k, v in G.osm_models(s).items()}
        ok = fit_rect(innenhof.flaeche_mm(fps.values(), s).buffer(-HOF_LEDGE, join_style=2), L, W, step=3) is not None
        print("  1:%d %s" % (mid, "passt" if ok else "zu klein"), flush=True)
        lo, hi = (mid, hi) if ok else (lo, mid)
    return int(lo), int(lo // 10 * 10)


def hof_width(hof_fp):
    """Breite des Innenhofs quer zur Hofachse (mm): Median und Minimum über die mittleren 80 % der Länge."""
    data = innenhof.load()
    d, n = innenhof.achse(data)
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


def place_edge(outline, hof_fp):
    """Unterkasten: Fach mit der Anschlussseite an einer Plattenkante, möglichst viel unter dem Innenhof."""
    inner = outline.buffer(-UK_WALL, join_style=2)
    x0, y0, x1, y1 = inner.bounds
    hc = hof_fp.centroid
    L, W = FACH_L + PB_PLUG, FACH_W
    best = None
    for side, ang in (("W", 0), ("O", 180), ("S", 90), ("N", 270)):
        if side in "WO":
            cy = min(max(hc.y, y0 + W / 2), y1 - W / 2)
            cx = x0 + L / 2 if side == "W" else x1 - L / 2
        else:
            cx = min(max(hc.x, x0 + W / 2), x1 - W / 2)
            cy = y0 + L / 2 if side == "S" else y1 - L / 2
        r = oriented(cx, cy, ang, L, W)
        if not inner.buffer(1e-6).contains(r):
            continue
        score = r.intersection(hof_fp).area
        if best is None or score > best[0]:
            best = (score, side, ang, cx, cy)
    _, side, ang, cx, cy = best
    # ang zeigt von der Anschlussseite (Kante) ins Platteninnere
    return dict(side=side, ang=ang, cx=cx, cy=cy, L=L, W=W)


def place_elec(inner, blocked, near):
    """Elektronik-Kasten: nächste freie Lage zur Nische."""
    a, b = ESP_BOX
    x0, y0, x1, y1 = inner.bounds
    best = None
    for rot in (False, True):
        w, h = (b, a) if rot else (a, b)
        for x in np.arange(x0 + w / 2, x1 - w / 2, 1.0):
            for y in np.arange(y0 + h / 2, y1 - h / 2, 1.0):
                r = box(x - w / 2, y - h / 2, x + w / 2, y + h / 2)
                if not inner.contains(r) or r.intersects(blocked):
                    continue
                d = math.hypot(x - near[0], y - near[1])
                if best is None or d < best[0]:
                    best = (d, r)
    return best[1]


# --------------------------------------------------------------------------
# Geometrie für Seite und 3D
# --------------------------------------------------------------------------
def coords(geom, sh):
    out = []
    for p in G.polys_of(geom):
        out.append([[round(x + sh[0], 2), round(y + sh[1], 2)] for x, y in list(p.exterior.coords)[:-1]])
    return out


def section(outline, fps, hof_fp, cx, cy, ang):
    """Schnitt entlang der Powerbank-Achse: Abschnitte (t0, t1) ab der Plattenkante auf der Anschlussseite."""
    a = math.radians(ang)
    u = np.array([math.cos(a), math.sin(a)])
    far = 2000.0
    line = shapely.LineString([np.array([cx, cy]) - far * u, np.array([cx, cy]) + far * u])
    seg = line.intersection(outline)
    p0 = np.array(seg.coords[0])
    if np.dot(p0 - np.array([cx, cy]), u) > 0:
        p0 = np.array(seg.coords[-1])
    t = lambda pt: float(np.dot(np.array(pt) - p0, u))
    items = []
    for kind, title, g in [("bld", b["title"], fps[b["slug"]]) for b in G.BUILDINGS] + [("hof", "Innenhof", hof_fp)]:
        for part in getattr(g.intersection(line), "geoms", [g.intersection(line)]):
            if part.is_empty or part.length < 0.5:
                continue
            ts = sorted(t(c) for c in part.coords)
            items.append(dict(kind=kind, title=title, t0=round(ts[0], 1), t1=round(ts[-1], 1)))
    return dict(len=round(seg.length, 1), items=sorted(items, key=lambda i: i["t0"]), c=round(t((cx, cy)), 1))


def mesh(man, sh, dz=0.0):
    return encode(G.to_trimesh(man.translate([sh[0], sh[1], dz])))


def variant(key, scale, mode, h, hof_scale=None):
    s, m, fps, hof = models(scale)
    hof_solid, hof_fp = hof[0], hof[1]
    sel = [b for b in G.BUILDINGS]
    fp_all = unary_union([fps[b["slug"]] for b in sel] + [hof_fp])
    outline = G.plate_outline(fp_all)
    minx, miny, maxx, maxy = outline.bounds
    sh = (-minx, -miny)
    cuts = [c - miny for c in G.tile_cuts(outline, fp_all)]
    F = h["F"]
    foot_fp = unary_union([fps[b["slug"]] for b in sel])

    if mode == "unterkasten":
        pl = place_edge(outline, hof_fp)
        a = math.radians(pl["ang"])
        ux, uy = math.cos(a), math.sin(a)
        # Fach = Nische (Kante) + Powerbank
        fach = oriented(pl["cx"], pl["cy"], pl["ang"], pl["L"], pl["W"])
        body_c = (pl["cx"] + ux * PB_PLUG / 2, pl["cy"] + uy * PB_PLUG / 2)
        body = oriented(*body_c, pl["ang"], PB_L, PB_W)
        niche = oriented(pl["cx"] - ux * FACH_L / 2, pl["cy"] - uy * FACH_L / 2, pl["ang"], PB_PLUG, FACH_W)
        port_face = (body_c[0] - ux * PB_L / 2, body_c[1] - uy * PB_L / 2)
        inner = outline.buffer(-UK_WALL, join_style=2)
        near = (pl["cx"] - ux * (FACH_L / 2), pl["cy"] - uy * (FACH_L / 2))
        elec = place_elec(inner, fach.buffer(4.0, join_style=2), near)
        window = oriented(pl["cx"] - ux * (pl["L"] / 2 + UK_WALL), pl["cy"] - uy * (pl["L"] / 2 + UK_WALL),
                          pl["ang"], 2 * UK_WALL + 2, 50.0)
        z_top, z_fach, z_bot = h["uk_top"], h["uk_fach"], h["uk_bot"]
        thick = h["total_uk"]
        side = pl["side"]
        ang = pl["ang"]
    else:
        L, W = FACH_L + PB_PLUG, FACH_W
        ang, ctr, _ = fit_rect(hof_fp.buffer(-HOF_LEDGE, join_style=2), L, W)
        a = math.radians(ang)
        ux, uy = math.cos(a), math.sin(a)
        fach = oriented(*ctr, ang, L, W)
        body_c = (ctr[0] + ux * PB_PLUG / 2, ctr[1] + uy * PB_PLUG / 2)
        body = oriented(*body_c, ang, PB_L, PB_W)
        niche = oriented(ctr[0] - ux * FACH_L / 2, ctr[1] - uy * FACH_L / 2, ang, PB_PLUG, FACH_W)
        port_face = (body_c[0] - ux * PB_L / 2, body_c[1] - uy * PB_L / 2)
        elec = None
        window = None
        z_fach = h["hof_fach"]
        z_top = -G.POCKET_DEPTH
        z_bot = None
        thick = h["plate_A"]
        side = None

    # Teile (Plattenoberseite z = 0)
    mulden = G.extrude(foot_fp.buffer(CLR, join_style=2), -F, 1.0)
    pocket = G.extrude(hof_fp.buffer(G.POCKET_CLEARANCE, join_style=2), -G.POCKET_DEPTH, 1.0)
    if mode == "unterkasten":
        ober = G.extrude(outline, h["z_lt"], 0.0) - mulden - pocket
        uk = G.extrude(outline, z_bot, z_top) - G.extrude(fach, z_fach, z_top + 1) \
            - G.extrude(elec, z_bot + UK_FLOOR, z_top + 1) - G.extrude(window, z_fach, z_top + 1)
        plate_parts = dict(ober=mesh(ober, sh), unten=mesh(uk, sh))
    else:
        ober = G.extrude(outline, h["z_lt"], 0.0) - mulden - pocket - G.extrude(fach, z_fach, 1.0)
        deckel = G.extrude(outline, h["z_lb"], h["z_lt"])
        plate_parts = dict(ober=mesh(ober, sh), unten=mesh(deckel, sh))
    bld = {}
    for b in sel:
        sol = m[b["slug"]][0] + G.extrude(fps[b["slug"]], -F, 0.01)
        bld[b["slug"]] = mesh(sol, sh)
    hof_mesh = mesh(hof_solid, sh)

    heights_bld = {b["slug"]: round(float(G.to_trimesh(m[b["slug"]][0]).bounds[1][2]), 1) for b in sel}
    return dict(
        key=key, scale=scale, mode=mode, s=s,
        plate=[round(maxx - minx, 1), round(maxy - miny, 1)], thick=round(thick, 1),
        outline=coords(outline, sh), cuts=[round(c, 1) for c in cuts],
        buildings=[dict(slug=b["slug"], title=b["title"], poly=coords(fps[b["slug"]], sh), h=heights_bld[b["slug"]])
                   for b in sel],
        hof=coords(hof_fp, sh), hof_area=round(hof_fp.area), hof_bounds=[round(v, 1) for v in hof_fp.bounds],
        fach=coords(fach, sh), body=coords(body, sh), niche=coords(niche, sh),
        elec=coords(elec, sh) if elec is not None else None,
        port=[round(port_face[0] + sh[0], 2), round(port_face[1] + sh[1], 2)], ang=round(ang, 1), side=side,
        under_hof=round(body.intersection(hof_fp).area / body.area * 100),
        cut_conflict=any(fach.bounds[1] - miny < c < fach.bounds[3] - miny for c in cuts),
        z=dict(top=z_top, fach=z_fach, bot=z_bot),
        meshes=dict(plate=plate_parts, buildings=bld, hof=hof_mesh),
        tiles=math.ceil((maxx - minx) / G.BED_SIZE) * (len(cuts) + 1), hof_scale=hof_scale,
        hof_w=[round(x, 1) for x in hof_width(hof_fp)], hub=round(innenhof.hub(innenhof.load(), s), 2),
        section=section(outline, fps, hof_fp, fach.centroid.x, fach.centroid.y, ang),
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
        print("  %s 1:%d Platte %.1f × %.1f × %.1f mm, Kacheln %d, Powerbank %d %% unter dem Hof, Kante %s%s"
              % (v["key"], v["scale"], *v["plate"], v["thick"], v["tiles"], v["under_hof"], v["side"],
                 ", Fach kreuzt Kachelschnitt!" if v["cut_conflict"] else ""))
    data = dict(
        heights=h, variants=variants,
        pb=dict(L=PB_L, W=PB_W, T=PB_T, g=PB_G, wh=PB_WH, eff=PB_EFF, imax=PB_IMAX, sleep=PB_SLEEP_S, keep=PB_KEEP_MA,
                ports=PB_PORTS, clr=PB_CLR, clr_z=PB_CLR_Z, plug=PB_PLUG),
        fach=dict(L=FACH_L, W=FACH_W, H=FACH_H, plug=PB_PLUG, ledge=HOF_LEDGE),
        uk=dict(floor=UK_FLOOR, wall=UK_WALL), esp=ESP_BOX, hof_limit=lim, hof_limit_exact=lim_exact,
        led_buildings=[b["title"] for b in G.BUILDINGS],
    )
    tpl = open(TEMPLATE, encoding="utf-8").read()
    html = tpl.replace("/*DATA*/", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    open(OUT, "w", encoding="utf-8").write(html)
    print("geschrieben:", os.path.relpath(OUT, ROOT), "(%.1f MB)" % (len(html) / 1e6))


if __name__ == "__main__":
    main()
