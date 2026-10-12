#!/usr/bin/env python3
"""Erzeugt 3D-Druckdateien (STL/3MF) der Gebäude am Campus Augustusplatz
der Universität Leipzig – aus drei Datenquellen zum Vergleich:

    osm        OpenStreetMap-Grundrisse + Höhen/Dachformen (© OSM-Mitwirkende, ODbL)
    lod2       3D-Stadtmodell LoD2 der Stadt Leipzig (dl-de/by-2-0), siehe lod2.py
    laserscan  Laserscan-Punktwolke GeoSN 2023 (dl-de/by-2-0), siehe laserscan.py

Aufruf:
    python3 generate.py                 # alle Quellen, Maßstäbe 1:1000 und 1:1500
    python3 generate.py --quelle lod2   # nur eine Quelle (mehrfach angebbar)
    python3 generate.py --scale 750     # beliebiger Maßstab
    python3 generate.py --fetch         # Quelldaten vorher neu herunterladen

Danach werden automatisch Vorschaubilder nach vorschau/ gerendert (preview.py).
"""
import argparse
import math
import os
import sys
import urllib.request
import xml.etree.ElementTree as ET

import manifold3d as m3d
import numpy as np
import shapely
import trimesh
from shapely.geometry import LineString, MultiPolygon, Polygon, box
from shapely.ops import polygonize, unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
OSM_FILE = os.path.join(HERE, "data", "augustusplatz.osm")
OSM_BBOX = (12.3770, 51.3370, 12.3830, 51.3400)  # lon_min, lat_min, lon_max, lat_max
ORIGIN = (12.3800, 51.3385)  # Bezugspunkt der lokalen Projektion (lon, lat)

# Ausgewählte Gebäude (OSM-ID: w = way, r = relation)
BUILDINGS = [
    dict(slug="01_paulinum", osm="w226096975", group="campus",
         name="Paulinum (Aula und Universitätskirche St. Pauli)"),
    dict(slug="02_neues_augusteum", osm="w35479085", group="campus",
         name="Neues Augusteum"),
    dict(slug="03_hoersaalgebaeude", osm="w186275377", group="campus",
         name="Hörsaalgebäude (mit Mensa am Park)"),
    dict(slug="04_seminargebaeude", osm="w35460251", group="campus",
         name="Seminargebäude"),
    dict(slug="05_institutsgebaeude", osm="w35460253", group="campus",
         name="Institutsgebäude / Wirtschaftswiss. Fakultät (Grimmaische Str. 12)"),
    dict(slug="06_city_hochhaus", osm="w35462506", group="extra",
         name="City-Hochhaus (\"Uniriese\")"),
    dict(slug="07_moritzbastei", osm="r1769862", group="extra",
         name="Moritzbastei"),
]

LEVEL_HEIGHT = 3.5        # m pro Geschoss, falls keine Höhe in OSM
ROOF_LEVEL_HEIGHT = 3.0   # m pro Dachgeschoss, falls keine Dachhöhe in OSM
DEFAULT_HEIGHT = 10.0     # m, falls weder Höhe noch Geschosse bekannt

# Druckparameter (mm)
MIN_FEATURE = 0.8         # minimale Wandstärke/Strukturbreite
PLATE_THICKNESS = 3.0     # Grundplatte mit Aussparungen
POCKET_DEPTH = 1.0        # Tiefe der Aussparungen
POCKET_CLEARANCE = 0.25   # Spiel pro Seite
BASE_THICKNESS = 2.0      # Sockelplatte beim Komplettmodell
MARGIN = 6.0              # Rand um die Gebäude
LABEL_BAND = 12.0         # zusätzlicher Rand unten für die Beschriftung
ENGRAVE_DEPTH = 0.6
BED_SIZE = 250.0          # größere Platten werden in Kacheln geteilt


# --------------------------------------------------------------------------
# OSM einlesen
# --------------------------------------------------------------------------
def fetch_osm():
    url = "https://api.openstreetmap.org/api/0.6/map?bbox=%f,%f,%f,%f" % OSM_BBOX
    print("Lade", url)
    os.makedirs(os.path.dirname(OSM_FILE), exist_ok=True)
    with urllib.request.urlopen(url, timeout=120) as r, open(OSM_FILE, "wb") as f:
        f.write(r.read())


def project(lon, lat):
    lon0, lat0 = ORIGIN
    x = (lon - lon0) * 111320.0 * math.cos(math.radians(lat0))
    y = (lat - lat0) * 110540.0
    return x, y


def load_features():
    root = ET.parse(OSM_FILE).getroot()
    nodes = {n.get("id"): project(float(n.get("lon")), float(n.get("lat")))
             for n in root.findall("node")}
    ways = {}
    for w in root.findall("way"):
        ways[w.get("id")] = ([nd.get("ref") for nd in w.findall("nd")],
                             {t.get("k"): t.get("v") for t in w.findall("tag")})
    feats = {}
    for wid, (refs, tags) in ways.items():
        if not ("building" in tags or "building:part" in tags):
            continue
        if refs[0] != refs[-1] or not all(r in nodes for r in refs) or len(refs) < 4:
            continue
        feats["w" + wid] = (Polygon([nodes[r] for r in refs]).buffer(0), tags)
    for rel in root.findall("relation"):
        tags = {t.get("k"): t.get("v") for t in rel.findall("tag")}
        if not ("building" in tags or "building:part" in tags):
            continue
        outer, inner, ok = [], [], True
        for m in rel.findall("member"):
            if m.get("type") != "way":
                continue
            if m.get("ref") not in ways:
                ok = False
                break
            refs = ways[m.get("ref")][0]
            if not all(r in nodes for r in refs):
                ok = False
                break
            line = LineString([nodes[r] for r in refs])
            (inner if m.get("role") == "inner" else outer).append(line)
        if not ok:
            continue
        geom = unary_union(list(polygonize(unary_union(outer))))
        if inner:
            geom = geom.difference(unary_union(list(polygonize(unary_union(inner)))))
        feats["r" + rel.get("id")] = (geom.buffer(0), tags)
    return feats


def num(tags, key):
    try:
        v = tags.get(key)
        return float(v.replace("m", "").strip()) if v else None
    except ValueError:
        return None


def heights(tags):
    """Liefert (Gesamthöhe, Dachhöhe, Dachform) in Metern."""
    shape = tags.get("roof:shape", "flat")
    roof_h = num(tags, "roof:height")
    if roof_h is None:
        rl = num(tags, "roof:levels")
        roof_h = rl * ROOF_LEVEL_HEIGHT if rl and shape != "flat" else 0.0
    if shape in ("flat", "many"):
        shape, roof_h = "flat", 0.0
    h = num(tags, "height")
    if not h or h <= 0:
        lv = num(tags, "building:levels")
        h = lv * LEVEL_HEIGHT + roof_h if lv else DEFAULT_HEIGHT + roof_h
    roof_h = min(roof_h, 0.9 * h)
    if roof_h <= 0:
        shape = "flat"
    return h, roof_h, shape


def building_parts(feats, osm_id):
    """Teilt ein Gebäude in (Polygon, Tags)-Bauteile (Simple 3D Buildings)."""
    outline, btags = feats[osm_id]
    parts = []
    for fid, (g, t) in feats.items():
        if "building:part" not in t or g.is_empty:
            continue
        inter = g.intersection(outline)
        if g.area < 1e-6:  # z.B. Antenne als Punkt-Polygon
            if outline.contains(g.centroid):
                parts.append((g.centroid.buffer(0.3), t, fid))
            continue
        if inter.area > 0.5 * g.area:
            parts.append((inter, t, fid))
    if parts:
        rest = outline.difference(unary_union([p[0] for p in parts]))
        if rest.area > 0.05 * outline.area:
            parts.append((rest, btags, osm_id))
    else:
        parts = [(outline, btags, osm_id)]
    return outline, parts


# --------------------------------------------------------------------------
# Geometrie
# --------------------------------------------------------------------------
def polys_of(geom):
    if geom.is_empty:
        return []
    if isinstance(geom, Polygon):
        return [geom]
    if isinstance(geom, MultiPolygon):
        return list(geom.geoms)
    return [g for g in getattr(geom, "geoms", []) if isinstance(g, Polygon)]


def cross_section(geom):
    contours = []
    for p in polys_of(geom):
        contours.append(np.asarray(p.exterior.coords)[:-1])
        for i in p.interiors:
            contours.append(np.asarray(i.coords)[:-1])
    return m3d.CrossSection(contours, m3d.FillRule.EvenOdd)


def extrude(geom, z0, z1):
    return m3d.Manifold.extrude(cross_section(geom), z1 - z0).translate([0, 0, z0])


def profile_prism(profile, axis, center, length):
    """Extrudiert ein 2D-Profil (s, z) quer zur Richtung `axis` (Einheitsvektor in XY)."""
    ax, ay = axis
    bx, by = ay, -ax  # rechtshändiges Koordinatensystem
    solid = m3d.Manifold.extrude(m3d.CrossSection([np.asarray(profile)]), length)
    solid = solid.translate([0, 0, -length / 2])
    mat = [[ax, 0, bx, center[0]], [ay, 0, by, center[1]], [0, 1, 0, 0]]
    return solid.transform(mat)


def ridge_frame(poly, tags):
    """Firstrichtung, Mittelpunkt, halbe Breite/Länge aus dem minimalen Rechteck."""
    rect = np.asarray(poly.minimum_rotated_rectangle.exterior.coords)[:4]
    e1, e2 = rect[1] - rect[0], rect[2] - rect[1]
    long_, short = (e1, e2) if np.linalg.norm(e1) >= np.linalg.norm(e2) else (e2, e1)
    if tags.get("roof:orientation") == "across":
        long_, short = short, long_
    d = long_ / np.linalg.norm(long_)
    c = rect.mean(axis=0)
    return d, c, np.linalg.norm(short) / 2, np.linalg.norm(long_) / 2


def clean(geom, eps=0.01):
    """Entfernt Punktberührungen und Splitter aus 2D-Geometrie (mm)."""
    geom = geom.buffer(eps, join_style=2).buffer(-eps, join_style=2)
    return shapely.set_precision(geom, 0.001).buffer(0)


def part_footprint(poly, tags, s, min_feature):
    """Grundriss eines Bauteils in mm, dünne Strukturen auf druckbare Breite gebracht."""
    poly = poly.buffer(0)
    if poly.is_empty:
        return None
    width_mm = 2 * poly.area / max(poly.length, 1e-9) * s
    if width_mm < min_feature:  # Antennen, Lamellen
        poly = poly.buffer((min_feature - width_mm) / s, join_style=2)
    return clean(scale_geom(poly, s))


def building_solid(parts, s, min_feature):
    """Volumenkörper eines Gebäudes in mm (s = mm pro m).

    Flachdach-Bauteile werden als Höhenschichten aus 2D-Vereinigungen gestapelt
    (robust gegen Bauteile, die sich nur an Kanten berühren). Unterseiten
    (min_height) werden für die Druckbarkeit nach unten aufgefüllt.
    """
    flat, sloped = [], []
    for poly, tags in parts:
        geom = part_footprint(poly, tags, s, min_feature)
        if geom is None or geom.is_empty:
            continue
        h, roof_h, shape = heights(tags)
        if shape == "flat":
            flat.append((geom, round(h * s, 3)))
        else:
            # leicht aufgeweitet, damit es mit den Nachbarn überlappt statt nur zu berühren
            sloped.append(roof_solid(geom.buffer(0.05, join_style=2), tags, h * s, roof_h * s, shape, poly))
    solids, z0 = [], 0.0
    for z1 in sorted({H for _, H in flat}):
        layer = clean(unary_union([g for g, H in flat if H >= z1]))
        if not layer.is_empty:
            solids.append(extrude(layer, z0, z1))
        z0 = z1
    return union(solids + sloped)


def roof_solid(geom, tags, H, R, shape, poly):
    """Bauteil mit geneigtem Dach (mm)."""
    body = extrude(geom, 0, H + 1)  # höher als der First: die Dachform kommt allein vom Schnittkörper
    gb = geom.bounds
    big = 2 * max(abs(v) for v in gb) + 20
    wall = H - R
    if shape == "skillion":
        dirn = num(tags, "roof:direction")
        if dirn is None:
            d, _, _, _ = ridge_frame(poly, tags)
            a = np.array([-d[1], d[0]])
        else:  # Kompassrichtung, in die die Dachfläche abfällt
            a = np.array([math.sin(math.radians(dirn)), math.cos(math.radians(dirn))])
        pts = shapely.get_coordinates(geom)
        p = pts @ a
        pmin, pmax = p.min(), p.max()
        span = max(pmax - pmin, 1e-6)
        zf = lambda q: H - R * (q - pmin) / span
        prof = [(pmin - 1, -1), (pmax + 1, -1), (pmax + 1, zf(pmax + 1)), (pmin - 1, zf(pmin - 1))]
        return body ^ profile_prism(prof, a, (0, 0), big)
    d, c, hw, hl = ridge_frame(geom, tags)
    n = np.array([-d[1], d[0]])
    off = c @ n
    prof = [(off - hw - 0.01, -1), (off + hw + 0.01, -1), (off + hw + 0.01, wall),
            (off, H), (off - hw - 0.01, wall)]
    if shape in ("gabled", "saltbox", "round", "gambrel", "half-hipped"):
        cutter = profile_prism(prof, n, (0, 0), big)
        return body ^ cutter
    # hipped, pyramidal, mansard, dome, onion, double_saltbox ... -> Walmdach
    slope = R / max(hw, 1e-6)
    offl = c @ d
    prof2 = [(offl - hl - 0.01, -1), (offl + hl + 0.01, -1), (offl + hl + 0.01, wall),
             (offl, wall + slope * (hl + 0.01)), (offl - hl - 0.01, wall)]
    cut1 = profile_prism(prof, n, (0, 0), big)
    cut2 = profile_prism(prof2, d, (0, 0), big)
    return body ^ cut1 ^ cut2


def scale_geom(geom, s, dx=0.0, dy=0.0):
    from shapely import affinity
    return affinity.affine_transform(geom, [s, 0, 0, s, dx * s, dy * s])


def union(solids):
    solids = [x for x in solids if x is not None and not x.is_empty()]
    return m3d.Manifold.batch_boolean(solids, m3d.OpType.Add)


def to_trimesh(man):
    mesh = man.to_mesh()
    tm = trimesh.Trimesh(vertices=np.asarray(mesh.vert_properties)[:, :3],
                         faces=np.asarray(mesh.tri_verts), process=False)
    return tm


def text_cross_section(text, size, x, y, anchor="left", max_width=None):
    from matplotlib.font_manager import FontProperties
    from matplotlib.textpath import TextPath
    prop = FontProperties(family="DejaVu Sans", weight="bold")
    if max_width:
        w1 = TextPath((0, 0), text, size=1.0, prop=prop).get_extents().width
        size = min(size, max_width / max(w1, 1e-9))
    tp = TextPath((0, 0), text, size=size, prop=prop)
    polys = [np.asarray(p) for p in tp.to_polygons() if len(p) >= 3]
    if not polys:
        return None
    allp = np.vstack(polys)
    w = allp[:, 0].max()
    shift = {"left": 0, "center": -w / 2, "right": -w}[anchor]
    polys = [p + [x + shift, y] for p in polys]
    return m3d.CrossSection(polys, m3d.FillRule.EvenOdd)


def north_arrow(x, y, size):
    tri = [(x, y + size), (x - size * 0.35, y), (x, y + size * 0.25), (x + size * 0.35, y)]
    return m3d.CrossSection([np.asarray(tri)])


# --------------------------------------------------------------------------
# Ausgabe
# --------------------------------------------------------------------------
def plate_outline(fp_mm):
    minx, miny, maxx, maxy = fp_mm.bounds
    rect = box(minx - MARGIN, miny - MARGIN - LABEL_BAND, maxx + MARGIN, maxy + MARGIN)
    return rect.buffer(-3, join_style=2).buffer(3)


ATTRIBUTION = {
    "osm": "Daten © OpenStreetMap-Mitwirkende (ODbL)",
    "lod2": "3D-Stadtmodell LoD2 © Stadt Leipzig (dl-de/by-2-0)",
    "laserscan": "Laserscan © GeoSN, LoD2 © Stadt Leipzig (dl-de/by-2-0)",
}


def engrave_labels(plate, outline, scale, title, top_z, quelle="osm"):
    minx, miny, maxx, maxy = outline.bounds
    cuts = []
    avail = maxx - minx - 22  # Platz links vom Nordpfeil
    t1 = text_cross_section(title, 4.2, minx + 5, miny + LABEL_BAND / 2 - 0.3, max_width=avail)
    t2 = text_cross_section("1:%d  ·  %s" % (scale, ATTRIBUTION[quelle]), 2.4,
                            minx + 5, miny + 2.4, max_width=avail)
    for t in (t1, t2):
        if t is not None:
            cuts.append(m3d.Manifold.extrude(t, ENGRAVE_DEPTH + 1).translate([0, 0, top_z - ENGRAVE_DEPTH]))
    na = north_arrow(maxx - 9, miny + 2.5, 7)
    cuts.append(m3d.Manifold.extrude(na, ENGRAVE_DEPTH + 1).translate([0, 0, top_z - ENGRAVE_DEPTH]))
    nt = text_cross_section("N", 3.0, maxx - 9, miny + 10, anchor="center")
    if nt is not None:
        cuts.append(m3d.Manifold.extrude(nt, ENGRAVE_DEPTH + 1).translate([0, 0, top_z - ENGRAVE_DEPTH]))
    return plate - union(cuts)


def tile_cuts(outline, fp_mm):
    """Schnittpositionen (y) für Kacheln, möglichst durch Lücken zwischen Gebäuden."""
    minx, miny, maxx, maxy = outline.bounds
    if maxx - minx > BED_SIZE:
        print("  Warnung: Breite %.0f mm > Druckbett, nur in y geteilt" % (maxx - minx))
    length = maxy - miny
    n = math.ceil(length / BED_SIZE)
    if n <= 1:
        return []
    cuts = []
    for k in range(1, n):
        target = miny + length * k / n
        best, best_cost = target, float("inf")
        for y in np.arange(target - 0.2 * length / n, target + 0.2 * length / n, 0.5):
            cost = LineString([(minx, y), (maxx, y)]).intersection(fp_mm).length
            cost += 0.02 * abs(y - target)
            if cost < best_cost:
                best, best_cost = y, cost
        cuts.append(best)
    return cuts


def split_tiles(solid, cuts):
    tiles, rest = [], solid
    for y in sorted(cuts):
        lower = rest.trim_by_plane([0, -1, 0], -y)
        rest = rest.trim_by_plane([0, 1, 0], y)
        tiles.append(lower)
    tiles.append(rest)
    return tiles


def export(tm, path):
    tm.export(path)
    print("  %-60s %6.1f × %6.1f × %6.1f mm  dicht=%s" % (
        os.path.relpath(path, HERE), *tm.extents, tm.is_watertight))


def osm_models(s):
    """Volumenkörper (mm), Grundriss (mm) und Infos je Gebäude aus OSM (s = mm pro m)."""
    feats = load_features()
    missing = [b["osm"] for b in BUILDINGS if b["osm"] not in feats]
    if missing:
        sys.exit("Gebäude nicht in den OSM-Daten gefunden: %s" % missing)
    out = {}
    for b in BUILDINGS:
        outline, parts = building_parts(feats, b["osm"])
        out[b["slug"]] = (building_solid([(p, t) for p, t, _ in parts], s, MIN_FEATURE),
                          scale_geom(unary_union([outline] + [p for p, _, _ in parts]), s),
                          dict(parts=["%s(h=%.1f m, Dach %s %.1f m)" % (fid, *heights(t)[:1], heights(t)[2],
                                                                        heights(t)[1])
                                      for _, t, fid in parts]))
    return out


def source_models(quelle, s):
    if quelle == "osm":
        return osm_models(s)
    if quelle == "lod2":
        import lod2
        return lod2.models(s)
    if quelle == "laserscan":
        import laserscan
        return laserscan.models(s)
    raise ValueError(quelle)


def build_scale(quelle, scale, outdir):
    s = 1000.0 / scale  # mm pro m
    os.makedirs(outdir, exist_ok=True)
    print("\nQuelle %s, Maßstab 1:%d -> %s" % (quelle, scale, os.path.relpath(outdir, HERE)))

    models = source_models(quelle, s)
    buildings = [b for b in BUILDINGS if b["slug"] in models]
    solids = {k: v[0] for k, v in models.items()}
    footprints = {k: v[1] for k, v in models.items()}

    # 1) Einzelgebäude: zentriert, flache Unterseite auf z=0
    os.makedirs(os.path.join(outdir, "einzeln"), exist_ok=True)
    for b in buildings:
        tm = to_trimesh(solids[b["slug"]])
        c = tm.bounds.mean(axis=0)
        tm.apply_translation([-c[0], -c[1], -tm.bounds[0][2]])
        export(tm, os.path.join(outdir, "einzeln", b["slug"] + ".stl"))

    for variant, groups in (("campus", {"campus"}), ("campus_mit_extras", {"campus", "extra"})):
        sel = [b for b in buildings if b["group"] in groups]
        fp = unary_union([footprints[b["slug"]] for b in sel])
        outline = plate_outline(fp)
        minx, miny = outline.bounds[0], outline.bounds[1]
        shift = [-minx, -miny, 0]
        cuts = tile_cuts(outline, fp)

        # 2) Komplettmodell: alle Gebäude auf einer Sockelplatte
        base = extrude(outline, 0, BASE_THICKNESS)
        base = engrave_labels(base, outline, scale, "Campus Augustusplatz · Universität Leipzig",
                              BASE_THICKNESS, quelle)
        bld = union([solids[b["slug"]].translate([0, 0, BASE_THICKNESS - 0.01]) for b in sel])
        full = (base + bld).translate(shift)
        parts = split_tiles(full, [c - miny for c in cuts])
        for i, part in enumerate(parts):
            suffix = "" if len(parts) == 1 else "_teil%d" % (i + 1)
            export(to_trimesh(part), os.path.join(outdir, "komplett_%s%s.stl" % (variant, suffix)))

        # 3) Grundplatte mit Aussparungen für die einzeln gedruckten Gebäude
        plate = extrude(outline, 0, PLATE_THICKNESS)
        pockets = extrude(fp.buffer(POCKET_CLEARANCE, join_style=2), PLATE_THICKNESS - POCKET_DEPTH,
                          PLATE_THICKNESS + 1)
        plate = engrave_labels(plate - pockets, outline, scale,
                               "Campus Augustusplatz · Universität Leipzig", PLATE_THICKNESS, quelle)
        parts = split_tiles(plate.translate(shift), [c - miny for c in cuts])
        for i, part in enumerate(parts):
            suffix = "" if len(parts) == 1 else "_teil%d" % (i + 1)
            export(to_trimesh(part), os.path.join(outdir, "grundplatte_%s%s.stl" % (variant, suffix)))

        # 4) 3MF: Platte + jedes Gebäude als eigenes Objekt an korrekter Position,
        #    mit Fassaden-/Dachfarbe als Material je Dreieck (data/farben.json)
        objs = [("Sockelplatte", to_trimesh(base.translate(shift)), None)]
        for b in sel:
            objs.append((b["name"], to_trimesh(solids[b["slug"]].translate([0, 0, BASE_THICKNESS]).translate(shift)),
                         b["slug"]))
        coloured = colourise(objs, (shift[0], shift[1], BASE_THICKNESS), s)
        path = os.path.join(outdir, "komplett_%s_objekte.3mf" % variant)
        export_3mf(coloured, path)
        print("  %s (%d Objekte, farbig)" % (os.path.relpath(path, HERE), len(objs)))
        if RENDER_COLOUR:
            render_coloured(coloured, quelle, scale, variant)

    return models


ROOF_NZ = 0.35  # Dreiecke mit steilerer Normale als ~70° zählen als Dach


def colour_table():
    import farben
    return farben.load_farben() or {}, farben.PLATTE


def paint_code(n):
    """Kodierung „ganzes Dreieck = Filament n“ für paint_color / slic3rpe:mmu_segmentation
    (TriangleSelector::serialize in PrusaSlicer/Bambu Studio/OrcaSlicer)."""
    return {1: "4", 2: "8"}[n] if n < 3 else "%XC" % (n - 3)


_ROOF_CLASS = None


def colourise(objs, offset, s):
    """Zerschneidet und färbt die Objekte nach den Fassaden-Zonen (fassaden.py).

    Liefert [(name, Netz, Hex-Farbe je Dreieck)]; ohne data/farben.json einfarbig.
    """
    global _ROOF_CLASS
    import fassaden
    farben, plate = colour_table()
    out = []
    for name, tm, slug in objs:
        e = farben.get(slug) if slug else None
        if not e:
            out.append((name, tm, np.array([plate] * len(tm.faces), dtype=object)))
            continue
        if _ROOF_CLASS is None:
            import farben as F
            _ROOF_CLASS = F.roof_classifier(farben)
        mesh, hexes = fassaden.colour_mesh(tm, slug, (offset, s), e, _ROOF_CLASS)
        if not mesh.is_watertight:
            print("  Warnung: %s nach dem Zerschneiden nicht dicht" % name)
        out.append((name, mesh, hexes))
    return out


def export_3mf(objs, path):
    """3MF mit Farben für Slicer und Betrachter. objs: [(name, Netz, Hex je Dreieck)].

    - Jedes Objekt bekommt sein häufigstes Wand-Filament als Objekt-Extruder
      (Metadata/model_settings.config für Bambu Studio/OrcaSlicer,
      Metadata/Slic3r_PE_model.config für PrusaSlicer).
    - Alle anderen Dreiecke (Fassaden-Zonen, Dachflächen) sind mit ihrem
      Filament vorbemalt (paint_color bzw. slic3rpe:mmu_segmentation).
    - Zusätzlich basematerials/displaycolor (3MF-Kernspezifikation) für Betrachter
      wie Windows 3D Viewer; Slicer ignorieren das.
    Die Filament-Nummern sind global (farben.filamente, Legende in vorschau/farben.png);
    die Filamentfarben selbst lassen sich ohne vollständiges Slicer-Profil nicht
    mitliefern und müssen im Slicer einmal eingestellt werden.
    """
    import zipfile
    from xml.sax.saxutils import escape as esc
    import farben as F
    escape = lambda t: esc(t, {'"': "&quot;"})
    farben, plate = colour_table()
    pal = [f["rgb"] for f in farben["_filamente"]] if farben else [plate]
    mats = ["F%d %s" % (i + 1, c) for i, c in enumerate(pal)]
    nr_of = {}
    objects, items, bambu, prusa = [], [], [], []
    for oid, (name, tm, hexes) in enumerate(objs, start=2):
        for h in set(hexes):
            if h not in nr_of:
                nr_of[h] = F.filament_nr(farben, h) if farben else 1
        nrs = np.array([nr_of[h] for h in hexes])
        walls = np.abs(tm.face_normals[:, 2]) <= ROOF_NZ
        wall = int(np.bincount(nrs[walls] if walls.any() else nrs).argmax())
        v = "".join('<vertex x="%.4f" y="%.4f" z="%.4f"/>' % tuple(p) for p in tm.vertices)
        tris = []
        for (a, b_, c), n in zip(tm.faces, nrs):
            if n != wall:
                code = paint_code(int(n))
                tris.append('<triangle v1="%d" v2="%d" v3="%d" pid="1" p1="%d" paint_color="%s" '
                            'slic3rpe:mmu_segmentation="%s"/>' % (a, b_, c, n - 1, code, code))
            else:
                tris.append('<triangle v1="%d" v2="%d" v3="%d" pid="1" p1="%d"/>' % (a, b_, c, n - 1))
        objects.append('<object id="%d" name="%s" type="model" pid="1" pindex="%d"><mesh><vertices>%s'
                       '</vertices><triangles>%s</triangles></mesh></object>'
                       % (oid, escape(name), wall - 1, v, "".join(tris)))
        items.append('<item objectid="%d"/>' % oid)
        bambu.append('<object id="%d"><metadata key="name" value="%s"/><metadata key="extruder" value="%d"/>'
                     '</object>' % (oid, escape(name), wall))
        prusa.append('<object id="%d" instances_count="1"><metadata type="object" key="name" value="%s"/>'
                     '<metadata type="object" key="extruder" value="%d"/><volume firstid="0" lastid="%d">'
                     '<metadata type="volume" key="name" value="%s"/></volume></object>'
                     % (oid, escape(name), wall, len(tm.faces) - 1, escape(name)))
    base = "".join('<base name="%s" displaycolor="%sFF"/>' % (escape(n), c.upper()) for n, c in zip(mats, pal))
    model = ('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="de-DE" '
             'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
             'xmlns:slic3rpe="http://schemas.slic3r.org/3mf/2017/06">'
             '<metadata name="Title">Campus Augustusplatz</metadata>'
             '<resources><basematerials id="1">%s</basematerials>%s</resources><build>%s</build></model>'
             % (base, "".join(objects), "".join(items)))
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<config>%s</config>\n'
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml",
                   '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/'
                   'package/2006/content-types"><Default Extension="rels" ContentType="application/'
                   'vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" '
                   'ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
                   '<Default Extension="config" ContentType="text/xml"/></Types>')
        z.writestr("_rels/.rels",
                   '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/'
                   'package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" '
                   'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
        z.writestr("3D/3dmodel.model", model)
        z.writestr("Metadata/model_settings.config", xml % "".join(bambu))
        z.writestr("Metadata/Slic3r_PE_model.config", xml % "".join(prusa))


def render_coloured(objs, quelle, scale, variant):
    """Farbige Vorschau in den Filamentfarben – so, wie es gedruckt wird."""
    import farben as F
    import preview
    farben, plate = colour_table()
    pal = [preview.rgb(f["rgb"]) for f in farben["_filamente"]] if farben else [preview.rgb(plate)]
    meshes = []
    for name, tm, hexes in objs:
        nrs = {h: (F.filament_nr(farben, h) if farben else 1) for h in set(hexes)}
        meshes.append((tm, np.array([pal[nrs[h] - 1] for h in hexes])))
    label = "1:%d, %s" % (scale, preview.QUELLEN_NAMEN.get(quelle, quelle))
    for suffix, azim, elev, blick in (("", -30, 32, "von Südosten"), ("_ost", 25, 28, "vom Augustusplatz (Osten)")):
        im = preview.render(meshes, size=(1100, 800), azim=azim, elev=elev, light_from_view=True)
        out = preview.caption(im, "Farbig %s%s  (%s)" % (
            blick, ", mit Extras" if "extras" in variant else "", label),
            "%d Filamente · Fassaden-Zonen aus Straßenfotos, Dachflächen aus dem Luftbild 2024 © Stadt Leipzig"
            % len(pal))
        path = os.path.join(preview.OUT, quelle, "1zu%d" % scale, "komplett_%s_farbig%s.png" % (variant, suffix))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        out.save(path, optimize=True)
        print("  Vorschau:", os.path.relpath(path, HERE))
    if "extras" in variant:  # Einzelgebäude farbig, je von zwei Seiten
        tiles = []
        for (name, tm, _), (m, cols) in zip(objs[1:], meshes[1:]):
            for azim in (-35, 145):
                im = preview.render([(m, cols)], size=(560, 460), azim=azim, elev=25, light_from_view=True)
                tiles.append(preview.caption(im, name[:40], "Blick von %s" % ("Südosten" if azim < 0 else "Nordwesten")))
        preview.contact_sheet(tiles, os.path.join(preview.OUT, quelle, "einzelgebaeude_farbig_1zu%d.png" % scale),
                              "Einzelgebäude farbig (%s)" % label, cols=4, cell=(560, 530))


def refresh_colours():
    """data/farben.json neu messen, wenn Fassaden- oder Fotodateien neuer sind."""
    import glob
    import farben
    src = glob.glob(os.path.join(HERE, "data", "fassaden", "*.json")) + [farben.FOTOS]
    if not os.path.exists(farben.FARBEN) or max(map(os.path.getmtime, src)) > os.path.getmtime(farben.FARBEN):
        print("Fassadendaten geändert – Farben neu messen (farben.py)")
        farben.main()


QUELLEN = ["osm", "lod2", "laserscan"]
RENDER_COLOUR = True


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scale", type=int, action="append",
                    help="Maßstab 1:N (mehrfach möglich, Standard: 1000 und 1500)")
    ap.add_argument("--quelle", action="append", choices=QUELLEN,
                    help="Datenquelle (mehrfach möglich, Standard: alle)")
    ap.add_argument("--fetch", action="store_true", help="Quelldaten neu herunterladen")
    ap.add_argument("--out", default=os.path.join(HERE, "stl"))
    ap.add_argument("--no-preview", action="store_true", help="keine Vorschaubilder rendern")
    args = ap.parse_args()
    global RENDER_COLOUR
    RENDER_COLOUR = not args.no_preview
    quellen = args.quelle or QUELLEN
    if args.fetch or not os.path.exists(OSM_FILE):
        fetch_osm()
    if args.fetch and "lod2" in quellen:
        import lod2
        lod2.fetch_lod2()
    if args.fetch and "laserscan" in quellen:
        import laserscan
        laserscan.fetch()
    refresh_colours()
    for q in quellen:
        for sc in args.scale or [1000, 1500]:
            models = build_scale(q, sc, os.path.join(args.out, q, "1zu%d" % sc))
        for slug, (_, _, info) in models.items():
            print("  %-22s %s" % (slug, ", ".join("%s=%s" % kv for kv in info.items()
                                                    if kv[0] != "attrs")))
    if not args.no_preview:
        import preview
        preview.default_previews(args.out)
        import fassaden
        print("\nFassaden-Prüfansichten")
        for b in BUILDINGS:
            if fassaden.load_spec(b["slug"]):
                fassaden.check(b["slug"])


if __name__ == "__main__":
    main()
