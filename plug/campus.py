#!/usr/bin/env python3
"""Steckplatte des Campus: Grundplatte mit Mulde (voller Gebäudeumriss), vier Pin-Löchern je Gebäude und Aussparung für den Innenhof-Einsatz
(Trennwand HOF_WALL_T zu den Gebäude-Mulden; Gang im Süden auf Terrassenhöhe, Treppen im Nordosten und am Westende des Gangs sind Teil der Platte).

Festlegung (plug/logbook/scale.md): Maßstab 1:1300, Mulde überall 4 mm tiefer (F 14,2), Kassette je Gebäude aus
params.CASSETTE (v4, V1RS, V2R). Die Lage der Mulde im Grundriss wird gesucht (Rechteck um den Schacht, beliebige Drehung, höchste Dachhöhe
bei mindestens 0,8 mm Wand, bevorzugt 1,2 mm) und in plug/scale1176/placements_<N>.json zwischengespeichert.

Flache Unterseite (Konzept des Test-Docks, plug/power/build_dock.py): Die Platte ist F + CEIL_T = 14,6 mm dick, der Muldenboden (0,4 mm) ist die
unterste Schicht auf dem Bett, die Unterseite ist eben. Pin-Löcher mit Fase beidseitig, keine Tasche, keine Stufe, keine Hohlräume, kein Support.
Die Winkelleiste wird von unten aufgeklebt (Körper hängt 2,0 mm unter der Platte, Lötenden und Draht darunter); der Steckerraum entsteht erst
durch den Unterkasten (noch nicht Teil dieser Datei).
Unten außerdem (plug/campus_underside.py, Lagen aus dem Konzept `plug/power/build_concept.py`): Zapfenaufnahmen (Sacklöcher Ø 4,3 × 2,8 für die Zapfen
der Stützen des Unterkastens) und an den vier Ecken je eine Fadentasche („halbe Pille mit Steg“ aus plug/thread/, für den Faden zum Doktorhut); beide
sind nach unten offen (Bett), kein Support. `UNTEN = False` baut die Platte ohne (Stand davor).

Display-Gebäude (plug/campus_display.py, Korrektur 7 in scale.md): Mulde und vier Pin-Löcher am Ostrand (Maße des ersten Satzes, Lage DISPLAY_LAGE); `--ohne-display` gibt den Stand davor.

Lage der Gebäude auf der Platte (19.10.2026, Passung bei wechselnden Filamenten): Mulden-Spiel `OUTLINE_CLR_T` 0,15, aber die Gebäude sind mit `ZUSCHNITT_CLR_T` 0,10 zugeschnitten
(Fuge 1,0). Damit die Wand zwischen den Mulden 0,8 bleibt, rückt `models_platte` die Gebäude je Naht um 2 × (0,15 − 0,10) auseinander (`plug/divider/geom.py` `verschiebungen`,
höchstens etwa 0,14 mm je Gebäude); Grundriss, Körper, Schächte und Docks (Lagen aus `placements_<N>.json`, die Datei bleibt unverändert, Weltlage der Gebäude-STL) wandern
gemeinsam, der Umriss der Platte folgt den verschobenen Grundrissen. `VERSCHIEBEN = False` gibt den Stand davor (Gebäude in Weltlage).

Aufruf (aus dem Wurzelverzeichnis):
    python3 -m plug.campus [--scale 1300] [--replace] [--unten-neu]   # STL nach stl/steckmodul_campus/, Bilder nach vorschau/steckmodul_campus/
                                                                       # (--unten-neu: Lagen der Zapfenaufnahmen aus dem Konzept neu lesen)
Die Gebäude selbst (Fuß mit Schacht, Hohlkörper) sind noch nicht Teil davon (To-do, siehe plug/logbook/next.md).
"""
import argparse
import json
import math
import os

import manifold3d as m3d
import numpy as np
import shapely
from shapely import affinity
from shapely.geometry import Polygon, box as sbox
from shapely.ops import unary_union

import generate as G
import innenhof
from plug import dupont as sd
from plug import institute as I
from plug import series2 as N2
from plug.geom import diff, ext, to_tm, union
from plug.power import build_concept as BC
from plug.scale1176 import variants1250 as W
from plug.testcase import build as TB
from plug.testcase import fit_study as FS
from plug.testcase import params as P
from plug.testcase import variants as V

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "stl", "steckmodul_campus")
PREV = os.path.join(HERE, "vorschau", "steckmodul_campus")
CACHE = os.path.join(HERE, "plug", "scale1176", "placements_%d.json")
WALL_PREF = (1.2, 0.8)          # Wand um den Schacht: bevorzugt, Mindestmaß


def shaft_size(var):
    """Schacht (Breite in x, Tiefe in y) der Kassette mit Spiel."""
    if var == "v4":
        k = P.kass_dims()
        w, d = k["cw"], k["L"]
    else:
        v = V.dims(var)
        w, d = v["w"], v["depth"]
    return w + 2 * P.KASS_CLR_T, d + 2 * P.KASS_CLR_T


def led_local(var):
    """LED (Mitte) im Gebäudesystem (Pin-Reihe y = 0): (x, y). Bei zwei LEDs (V2R, V1RS) die Mitte zwischen beiden."""
    d = P.dims()
    if var == "v4":
        k = P.kass_dims()
        return 0.0, (k["seat0"] + k["seat1"]) / 2 + d["y_kass0"]
    v = V.dims(var)
    yf = v["y_face"] + 0.95
    if var in V.RVARS:
        yf = (yf + v["yb_back"] + V.FPC + 0.95) / 2
    return v["x_off"], yf + d["y_kass0"]


def foot_local(var, wall):
    """Schacht plus Wand im Gebäudesystem (Pin-Reihe bei y = 0); Rechteck. Nur für die Wandprüfung und die Lage."""
    d = P.dims_plan()
    w, dep = shaft_size(var)
    y0 = d["y_kass0"] - P.KASS_CLR_T
    return sbox(-w / 2 - wall, y0 - wall, w / 2 + wall, y0 + dep + wall)


def slice_poly(solid, z, fp):
    g = None
    for ring in solid.slice(z).to_polygons():
        r = Polygon(ring)
        g = r if g is None else g.symmetric_difference(r)
    return None if g is None else g.buffer(0).intersection(fp.buffer(0.01))


def target_point(fp):
    """Mitte der Grundfläche: Schwerpunkt, sonst (liegt er außerhalb) die Stelle mit dem größten Abstand zum Rand."""
    c = fp.centroid
    if fp.contains(c):
        return c
    from shapely.ops import polylabel
    big = max(fp.geoms, key=lambda g: g.area) if hasattr(fp, "geoms") else fp
    return polylabel(big, 0.1)


def candidates(u, A, B, led_dxy, tgt, astep=5, gstep=0.5):
    """Alle Lagen des Rechtecks A × B (Drehung 0 bis 355°) im Polygon u, sortiert nach Abstand der LED zur Zielmitte.
    led_dxy: LED relativ zur Rechteckmitte (x quer, y längs). Liefert Liste (Abstand, Winkel, cx, cy)."""
    r = min(A, B) / 2
    er = u.buffer(-r)
    if er.is_empty:
        return []
    x0, y0, x1, y1 = er.bounds
    X, Y = np.meshgrid(np.arange(x0, x1 + 1e-9, gstep), np.arange(y0, y1 + 1e-9, gstep))
    X, Y = X.ravel(), Y.ravel()
    ins = shapely.contains_xy(er, X, Y)
    X, Y = X[ins], Y[ins]
    shapely.prepare(u)
    corners = np.array([[-A / 2, -B / 2], [A / 2, -B / 2], [A / 2, B / 2], [-A / 2, B / 2], [-A / 2, -B / 2]])
    out = []
    for ang in range(0, 360, astep):
        a = math.radians(ang)
        rot = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
        off = corners @ rot.T
        coords = np.stack([X[:, None] + off[None, :, 0], Y[:, None] + off[None, :, 1]], axis=2)
        ok = shapely.contains(u, shapely.polygons(coords))
        if ok.any():
            lx, ly = rot @ np.array(led_dxy)
            dist = np.hypot(X[ok] + lx - tgt.x, Y[ok] + ly - tgt.y)
            out += list(zip(dist.tolist(), [ang] * int(ok.sum()), X[ok].tolist(), Y[ok].tolist()))
    out.sort()
    return out


def roof_over(solid, fp, rect, hmax):
    """Dachhöhe über dem Schacht: größte Höhe, bei der das Rechteck noch ganz im Gebäudeschnitt liegt."""
    lo, hi = 0.3, hmax - 0.2
    for _ in range(8):
        mid = (lo + hi) / 2
        u = slice_poly(solid, mid, fp)
        if u is not None and not u.is_empty and u.buffer(1e-6).contains(rect):
            lo = mid
        else:
            hi = mid
    return lo


def mulde_body(slug_fp, d, clr=None):
    """Mulde: der volle Gebäudeumriss, durchgehend bis zur Fußunterkante (eine Ebene, keine Stufen), oben mit Einführfase MULDE_CH_T.
    Die Fase wächst in Stufen nach oben (wie die Bettfasen, BC.mouth_ch) und reicht bis über die Oberkante, damit sich die Öffnung nicht zuzieht
    und kein Rest-Überhang bleibt. clr: Spiel je Seite (Standard OUTLINE_CLR_T; das Display-Gebäude nimmt sein eigenes, plug/campus_display.py)."""
    clr = P.OUTLINE_CLR_T if clr is None else clr
    poly = slug_fp.buffer(clr, join_style=2)
    ch = P.MULDE_CH_T
    n = BC.n_layers(ch)
    dz = ch / n
    parts = [G.extrude(poly, -d["F"], -ch + 0.01)]
    for k in range(n):
        top = SCHNITT_OBEN if k == n - 1 else -ch + dz * (k + 1) + 0.01
        parts.append(G.extrude(slug_fp.buffer(clr + dz * (k + 0.5), join_style=2), -ch + dz * k, top))
    return G.union(parts)


def top_edge(outline, T, ch):
    """Körper, der die Platte an der oberen Außenkante mit einer 45°-Fase ch (in Stufen) begrenzt; mit der Platte schneiden."""
    n = BC.n_layers(ch)
    dz = ch / n
    z0 = T - ch
    parts = [G.extrude(outline, 0.0, z0 + 0.01)]
    for k in range(n):
        top = T + 1.0 if k == n - 1 else z0 + dz * (k + 1) + 0.01
        parts.append(G.extrude(outline.buffer(-dz * (k + 0.5)), z0 + dz * k, top))
    return G.union(parts)


def dock_local(var, wall, d):
    """Dock im Gebäudesystem (Pin-Reihe bei y = 0): Schnittkörper der Pin-Löcher und Hüllkurve (shapely) von Leiste, Lötenden und Draht unter der Platte.
    Die Hüllkurve stammt aus dem Dock der Platte B (dock_cuts_b); sie ist größer als die aufgeklebte Leiste und hält die Lagen aus der Platzierungs-App gültig."""
    cs = union(TB.dock_cuts_b(d)).project()
    env = unary_union([Polygon(r) for r in cs.to_polygons()])
    return pin_holes(d), env


def pin_holes(d):
    """Vier Pin-Löcher durch den Muldenboden, Fase unten (Bett) und oben (Mulde), wie im Test-Dock."""
    cuts = []
    for x in sd.pin_x():
        cuts += N2.hole_ch(x, 0.0, -plate_thickness(d), -d["F"], sd.HOLE, TB.HOLE_CH, TB.HOLE_CH)
    return cuts


def plate_thickness(d):
    """Mulde F plus Muldenboden CEIL_T; darunter nichts (flache Unterseite)."""
    return d["F"] + P.CEIL_T


def place_all(models, scale, replace=False):
    path = CACHE % scale
    if os.path.exists(path) and not replace:
        return json.load(open(path))
    F0, dl = P.dims()["F"], P.MULDE_EXTRA_T
    d = P.dims_plan()
    res, placed_env = {}, []
    order = ["06_city_hochhaus", "05_institutsgebaeude", "04_seminargebaeude", "01_paulinum", "02_neues_augusteum", "03_hoersaalgebaeude"]
    for slug in order:
        solid, fp, _ = models[slug]
        var = P.CASSETTE[slug]
        t, _led = W.top_led(var)
        need = t - F0 - dl + P.STOP_T                       # Mindesthöhe des Gebäudes über der Platte
        w, dep = shaft_size(var)
        hmax = float(G.to_trimesh(solid).bounds[1][2])
        lx, ly = led_local(var)
        yc = foot_local(var, 0.0).centroid.y
        led_dxy = (lx, ly - yc)
        tgt = target_point(fp)
        _, env_local = dock_local(var, 0.0, d)
        best = None
        for wall in WALL_PREF:
            z_use = max(need - 0.2, 0.3)
            if slug in PREFER_ROOF:                         # höchste Dachhöhe, bei der der Schacht noch passt, dann dort möglichst mittig
                lo, hi = z_use, hmax - 0.2
                for _ in range(7):
                    mid = (lo + hi) / 2
                    um = slice_poly(solid, mid, fp)
                    if um is not None and not um.is_empty and FS.fit(um, w + 2 * wall, dep + 2 * wall) is not None:
                        lo = mid
                    else:
                        hi = mid
                z_use = lo - 0.3
            u = slice_poly(solid, z_use, fp)
            if u is None or u.is_empty:
                continue
            cand = candidates(u, w + 2 * wall, dep + 2 * wall, led_dxy, tgt)
            for dist, ang, cx, cy in cand[:4000]:
                env = affinity.translate(affinity.rotate(affinity.translate(env_local, 0, -yc), ang, origin=(0, 0)), cx, cy)
                if not outline_ok(env) or any(env.intersection(o).area > 0.01 for o in placed_env):
                    continue
                best = dict(var=var, wall=wall, cx=cx, cy=cy, angle=ang, led_dist=round(dist, 1))
                rect = affinity.translate(affinity.rotate(sbox(-w / 2, -dep / 2, w / 2, dep / 2), ang, origin=(0, 0)), cx, cy)
                best["roof"] = round(roof_over(solid, fp, rect, hmax), 1)
                best["need"] = round(need, 2)
                placed_env.append(env)
                break
            if best:
                break
        if best is None:
            raise SystemExit("%s: kein Platz für %s (Wand %.1f)" % (slug, var, WALL_PREF[-1]))
        res[slug] = best
        print("  %-22s %-5s Wand %.1f, LED %.1f mm von der Mitte, Dach %.1f (nötig %.1f)" % (
            slug, var, best["wall"], best["led_dist"], best["roof"], best["need"]), flush=True)
    json.dump(res, open(path, "w"), indent=1)
    return res


OUTLINE = None
UNTEN = True             # False: Platte ohne Zapfenaufnahmen und Fadentaschen (Stand davor); wird nur bei der Standard-Trennwand und dem Standard-Hof gebaut
REFRESH_UNTEN = False    # True: Lagen der Zapfen aus dem Konzept neu lesen (plug/scale1176/underside_<Maßstab>.json)
UNTEN_INFO = {}          # Lage, Platte ohne Unterseite und Sperrfläche des letzten build() (für die Prüfung in main und plug.campus_underside)
DISPLAY = True           # False: Platte ohne Mulde und Pin-Löcher des Display-Gebäudes (Stand davor, `--ohne-display`); gebaut nur bei der Standard-Trennwand und dem Standard-Hof
DISPLAY_INFO = {}        # Lage, Platte ohne Display-Dock, Dockzonen und Hüllkurven der Gebäude-Docks des letzten build() (für die Prüfung in main und plug.campus_display)
TRENNWAND = True         # False: Grundrisse ohne Fuge (Stand vor 17.10., nur für Vorher/Nachher-Seiten und Vergleiche)
VERSCHIEBEN = True       # False: Gebäude auf der Platte in Weltlage, ohne das Auseinanderrücken um das größere Mulden-Spiel (Stand vor 19.10.2026; Wand zwischen den Mulden dann 0,7)
SHIFTS = {}              # Verschiebung je Gebäude (dx, dy) in mm, Weltlage -> Lage auf der Platte, vom letzten `models_platte` (die Gebäude-STL liegen in Weltlage)
ECKE = (0.0, 0.0)        # Versatz der Südwest-Ecke der Platte gegenüber dem Stand ohne Verschiebung (Mitte der Verschiebungen, siehe `umriss_platte`)
WELT_ECKE = None         # Südwest-Ecke des Plattenumrisses ohne Verschiebung (Weltlage); beide vom letzten `platte_lage`
SCHNITT_OBEN = 3.0       # mm über der Plattenoberfläche: so hoch schneiden die Mulden (die Aufbauten der Platte, Gang und Treppe, sind bis 2,35 mm hoch)
# Gebäude, bei denen die LED unter dem hohen Dach sitzen soll statt exakt mittig (Nutzer: Neues Augusteum)
PREFER_ROOF = {"02_neues_augusteum"}


def outline_ok(env):
    return OUTLINE is None or env.within(OUTLINE.buffer(-1.0))


def hof_abstand(wand):
    """Abstand des Hof-Umrisses vom Gebäudegrundriss: Spiel der Gebäude-Mulde plus Trennwand."""
    return P.OUTLINE_CLR_T + wand


def models_plan(s, scale=P.SCALE_PLAN):
    """Laserscan-Modelle mit Fuge an den Nähten zwischen Gebäuden (plug/divider/geom.py: Wand HOF_WALL_T zwischen den Mulden, Neues Augusteum weicht
    dem Paulinum, sonst teilen sich beide die Fuge)."""
    models = G.source_models("laserscan", s)
    if not TRENNWAND:
        return models
    from plug.divider import geom as DV
    return DV.getrennt(models, scale)


def platte_lage(models):
    """(Modelle in der Lage auf der Platte, Verschiebung je Gebäude): die zugeschnittenen Gebäude (`models_plan`, Weltlage) je Naht um das größere Mulden-Spiel auseinandergerückt,
    sodass die Wand zwischen den Mulden `HOF_WALL_T` bleibt (`plug/divider/geom.py` `verschiebungen`). Ohne Trennwand oder mit `VERSCHIEBEN = False` unverändert."""
    from plug.divider import geom as DV
    fps = {k: v[1] for k, v in models.items() if k in P.CASSETTE}
    shifts = DV.verschiebungen(fps) if (TRENNWAND and VERSCHIEBEN) else {k: (0.0, 0.0) for k in fps}
    global ECKE, WELT_ECKE
    SHIFTS.clear()
    SHIFTS.update(shifts)
    xs, ys = [v[0] for v in shifts.values()] or [0.0], [v[1] for v in shifts.values()] or [0.0]
    ECKE = ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2)
    WELT_ECKE = G.plate_outline(unary_union([v[1] for k, v in models.items() if k in P.CASSETTE])).bounds[:2]
    return DV.schiebe(models, shifts), shifts


def umriss_platte(fp):
    """Umriss der Platte für die Grundrisse `fp` (Vereinigung, Lage auf der Platte): wie `G.plate_outline` (Rand 6 mm, unten das Beschriftungsband, Ecken R 3), aber die Südwest-Ecke
    liegt nicht beim Gebäude, das sich am weitesten nach Südwesten schiebt (Hörsaalgebäude), sondern um `ECKE` (Mitte der Verschiebungen) neben der Ecke ohne Verschiebung. Der Grund:
    Zapfenlöcher (`ZAPFEN_LOKAL`) und das Display-Dock liegen relativ zu dieser Ecke, ebenso die Zapfen des gedruckten Unterkastens; die Docks der Gebäude weichen dann nur um ihre Verschiebung
    gegenüber der Mitte ab (höchstens etwa 0,12 mm statt 0,23). Nordost folgt den Gebäuden (Rand 6 mm)."""
    o = G.plate_outline(fp)
    if WELT_ECKE is None or not any(abs(v[0]) + abs(v[1]) > 0 for v in SHIFTS.values()):
        return o
    b = o.bounds
    return sbox(WELT_ECKE[0] + ECKE[0], WELT_ECKE[1] + ECKE[1], b[2], b[3]).buffer(-3, join_style=2).buffer(3)


def models_platte(s, scale=P.SCALE_PLAN):
    """Laserscan-Modelle in der Lage auf der Platte (`models_plan` plus `platte_lage`); die Lagen der Schächte dazu: `places_platte`."""
    return platte_lage(models_plan(s, scale))[0]


def places_platte(places, shifts=None):
    """Lagen der Schächte und Docks (`placements_<N>.json`, Weltlage) in der Lage auf der Platte (um `SHIFTS` verschoben); die Datei selbst bleibt unverändert."""
    from plug.divider import geom as DV
    return DV.schiebe_places(places, SHIFTS if shifts is None else shifts)


def build(scale=P.SCALE_PLAN, replace=False, hof_wand=None):
    """hof_wand: Trennwand zwischen Hof-Aussparung und Gebäude-Mulden in mm (Standard P.HOF_WALL_T)."""
    global OUTLINE
    s = 1000.0 / scale
    G.FAST = True
    abstand = hof_abstand(P.HOF_WALL_T if hof_wand is None else hof_wand)
    models_welt = models_plan(s, scale)
    models, shifts = platte_lage(models_welt)
    models[G.HOF["slug"]] = innenhof.model(s, [v[1] for v in models.values()], P.HOF_DEPTH_T, P.HOF_CLR_T, abstand)
    fps = {k: v[1] for k, v in models.items()}
    outline = umriss_platte(unary_union(list(fps.values())))
    # Lagen der Schächte: Zwischenspeicher (placements_<N>.json) und eine neue Suche gelten für die Weltlage der Gebäude (wie die Gebäude-STL); die Platte bekommt sie verschoben
    OUTLINE = G.plate_outline(unary_union([v[1] for k, v in models_welt.items() if k in P.CASSETTE]))
    places = place_all({k: v for k, v in models_welt.items() if k in P.CASSETTE}, scale, replace)
    places = places_platte(places, shifts)
    OUTLINE = outline
    d = P.dims_plan()
    T = plate_thickness(d)
    hof_solid = models[G.HOF["slug"]][0]
    plate = BC.slab_ch(outline, 0.0, T, P.EF_CH_T)           # Bettkante mit Fase gegen den Elefantenfuß
    plate = plate ^ top_edge(outline, T, P.PLATE_TOP_CH_T)    # obere Außenkante gefast (Wulst im Druck)
    plate = G.engrave_labels(plate, outline, scale, "Campus Augustusplatz", T, "laserscan", raised=P.LABEL_RAISE_T,
                           inset=P.PLATE_TOP_CH_T, nur_titel=True)
    # Aufbauten der Platte neben dem Einsatz: Gang im Süden auf Terrassenhöhe mit Treppe am Westende, Treppe im Nordosten (innenhof.platte_aufbau_mm);
    # die Mulden und die Hof-Aussparung schneiden sie danach zu
    hof = innenhof.flaeche_mm([v[1] for k, v in models.items() if k in P.CASSETTE], s, abstand)
    inner = outline.buffer(-P.PLATE_TOP_CH_T)
    for _, bands in innenhof.platte_aufbau_mm(hof, s):
        for poly, top in bands:
            plate = plate + G.extrude(G.clean(poly.intersection(inner)), T - 0.01, T + top)
    cut_all, report, envs, zones_geb = [], [], [], []
    for slug, p in places.items():
        w, dep = shaft_size(p["var"])
        yc = foot_local(p["var"], 0.0).centroid.y
        a_ = math.radians(p["angle"])                          # Dockzone unter der Platte (Raum für Leiste, Lötenden, Draht) wie BC.fixed_docks
        zones_geb.append(BC.poly_world(BC.dock_zone(), p["angle"], (p["cx"] + yc * math.sin(a_), p["cy"] - yc * math.cos(a_))))
        cuts, env_local = dock_local(p["var"], p["wall"], d)
        for c in cuts:
            cut_all.append(c.translate([0.0, -yc, 0.0]).rotate([0.0, 0.0, p["angle"]]).translate([p["cx"], p["cy"], T]))
        env = affinity.translate(affinity.rotate(affinity.translate(env_local, 0, -yc), p["angle"], origin=(0, 0)), p["cx"], p["cy"])
        bad = env.difference(outline.buffer(-1.0)).area + sum(env.intersection(o).area for o in envs)
        envs.append(env)
        report.append((slug, p["var"], p["wall"], p.get("led_dist"), bad))
        # Mulde: voller Gebäudeumriss, durchgehend bis zur Fußunterkante, oben mit Einführfase
        cut_all.append(mulde_body(fps[slug], d).translate([0, 0, T]))
        # Muldenboden bleibt 0,4 mm und ist die unterste Schicht; die Pin-Löcher kommen aus pin_holes
    # Hof-Aussparung: HOF_DEPTH_T tief, Einsatz mit Fuge HOF_CLR_T und Einführfase unten (innenhof.model); ohne Fase oben, damit die Trennwand
    # zu den Gebäude-Mulden (hof_wand) ihre Breite behält
    cut_all.append(G.extrude(hof, T - P.HOF_DEPTH_T, T + SCHNITT_OBEN))
    plate = diff(plate, *cut_all)
    global UNTEN_INFO, DISPLAY_INFO
    blocked = unary_union([fps[s_].buffer(P.OUTLINE_CLR_T, join_style=2) for s_ in places] + [hof])   # Mulden und Hof
    DISPLAY_INFO = dict(T=T, zones=zones_geb, envs=list(envs))
    dcuts, base_u = [], plate
    if DISPLAY and TRENNWAND and hof_wand is None:
        # Display-Gebäude (plug/campus_display.py): Mulde und vier Pin-Löcher am Ostrand; die Mulde sperrt Zapfenlöcher und Fadentaschen weiter unten
        from plug import campus_display as DP
        minx_, miny_ = outline.bounds[:2]
        dcuts = DP.cuts(T, minx_, miny_, mulde_body, pin_holes, d)
        blocked = unary_union([blocked, affinity.translate(DP.mulde_poly(), minx_, miny_)])
        base_u = diff(plate, *dcuts)                          # Platte mit Display-Dock, ohne Unterseite (Vergleichsstand für plug.campus_underside.report)
        DISPLAY_INFO.update(on=True, minx=minx_, miny=miny_)
    UNTEN_INFO = dict(blocked=blocked, T=T, base=base_u)
    if UNTEN and TRENNWAND and hof_wand is None:
        # Unterseite: Zapfenaufnahmen und Fadentaschen (plug/campus_underside.py); frei von Mulden und Hof, Wand 0,8 bzw. 1,4
        from plug import campus_underside as U
        lay = U.layout(scale, outline, blocked, refresh=REFRESH_UNTEN)
        plate = diff(plate, *U.cuts(lay))
        for a_ in U.adds(lay):                                 # Steg in jeder Fadentasche
            plate = plate + a_
        UNTEN_INFO["lay"] = lay
    if dcuts:
        DISPLAY_INFO["base"] = plate                           # Platte mit Unterseite, ohne Display-Dock (Vergleichsstand für plug.campus_display.report)
        plate = diff(plate, *dcuts)
    return plate, report, models, places, outline, hof_solid


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scale", type=int, default=P.SCALE_PLAN)
    ap.add_argument("--replace", action="store_true", help="Lage der Mulden neu suchen")
    ap.add_argument("--unten-neu", action="store_true", help="Lagen der Zapfenaufnahmen aus dem Konzept (plug/power/build_concept.py) neu lesen")
    ap.add_argument("--faden", choices=("pille", "v"), help="Form der Fadenösen: pille (Standard, plug/thread) oder v (V-Kanal des Konzepts, in r4 verworfen)")
    ap.add_argument("--ohne-unten", action="store_true", help="ohne Zapfenaufnahmen und Fadenösen bauen (Stand davor, nur zum Vergleich; schreibt trotzdem die STL)")
    ap.add_argument("--ohne-display", action="store_true", help="ohne Mulde und Pin-Löcher des Display-Gebäudes bauen (Stand davor, nur zum Vergleich; schreibt trotzdem die STL)")
    a = ap.parse_args()
    global UNTEN, REFRESH_UNTEN, DISPLAY
    REFRESH_UNTEN = a.unten_neu
    UNTEN = not a.ohne_unten
    DISPLAY = not a.ohne_display
    if a.faden:
        from plug import campus_underside as U_
        U_.FADEN = a.faden
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(PREV, exist_ok=True)
    plate, report, models, places, outline, hof_solid = build(a.scale, a.replace)
    tm = to_tm(plate)
    path = os.path.join(OUT, "steckplatte_1zu%d.stl" % a.scale)
    tm.export(path)
    b = outline.bounds
    print("Platte %.1f × %.1f × %.1f mm, dicht=%s, Mulde %.1f, Plattendicke %.1f" % (
        b[2] - b[0], b[3] - b[1], plate_thickness(P.dims_plan()), tm.is_watertight, P.dims_plan()["F"], plate_thickness(P.dims_plan())))
    from plug import buildings as BU
    hof_solid, hof_netz = BU.sauber(hof_solid)                 # wie die Gebäude: float32-Neuaufbau, Mikroschalen weg, Berührkanten getrennt
    hof_tm = to_tm(hof_solid)
    hof_path = os.path.join(OUT, "hof_einsatz_1zu%d.stl" % a.scale)
    hof_tm.export(hof_path)
    print("Hof-Einsatz %.1f × %.1f × %.1f mm, dicht=%s, %.1f mm unter der Oberfläche" % (*hof_tm.extents, hof_tm.is_watertight, P.HOF_DEPTH_T))
    ok = tm.is_watertight and hof_tm.is_watertight
    from plug.fit_test.generator import overhangs
    ov = overhangs(plate, "steckplatte")
    print("  waagerechte Decken: %s   Überhang flacher als 45° zur Senkrechten: %.0f mm²" % (
        "; ".join("z=%.1f: %.0f mm² (%.1f × %.1f)" % f for f in sorted(ov["flat"], key=lambda t: -t[1])[:4]) or "keine", ov["steep_area"]))
    for slug, var, wall, flip, bad in report:
        print("  %-22s %-5s Wand %.1f, %s, Dock außerhalb/überlappt %.2f mm²" % (
            slug, var, wall, "LED %.1f mm von der Mitte" % flip if flip is not None else "Lage aus der Platzierungs-App", bad))
        ok &= bad < 0.05
    if UNTEN_INFO.get("lay"):
        from plug import campus_underside as U
        ok &= U.report(plate, UNTEN_INFO["lay"], outline, plate_thickness(P.dims_plan()), UNTEN_INFO["base"])
    if DISPLAY_INFO.get("on"):
        from plug import campus_display as DP
        ok &= DP.report(plate, outline, DISPLAY_INFO, UNTEN_INFO.get("lay"))
    print("keine Kollisionen" if ok else "ACHTUNG: Kollision oder Hohlraum außerhalb der Platte")
    import preview
    preview.render([(tm, "#9aa7b4")], size=(1000, 1300), azim=-90, elev=89).save(os.path.join(PREV, "steckplatte_1zu%d_oben.png" % a.scale))
    preview.render([(tm, "#9aa7b4")], size=(1100, 900), azim=-50, elev=35).save(os.path.join(PREV, "steckplatte_1zu%d_schraeg.png" % a.scale))
    if UNTEN_INFO.get("lay"):                              # Unteransicht: Norden oben, Blick von unten durch die Platte (Osten links)
        preview.render([(tm, "#9aa7b4")], size=(1000, 1300), azim=90, elev=-89, light_from_view=True).save(
            os.path.join(PREV, "steckplatte_1zu%d_unten.png" % a.scale))
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
