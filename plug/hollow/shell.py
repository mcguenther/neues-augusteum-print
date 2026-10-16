"""Hohlkörper-Studie: Gebäude-Volumenkörper (mm, Boden bei z=0) zur dünnen Schale mit offener Unterseite aushöhlen.

Nur Untersuchung für den Plan `plug/hollow/plan.html`; noch nicht im Generator (`generate.py`) eingebaut.
Verfahren: Die Gebäude sind aus dem Boden extrudiert, der Querschnitt C(z) nimmt mit der Höhe nur ab. Der Hohlraum ist die Vereinigung
der um die Wand geschrumpften Querschnitte E(z) = C(z) - WAND, je Schicht, bis zur Höhe z - DACH (Decke folgt dem Dach).
"""
import numpy as np
import manifold3d as m3d
import trimesh
import shapely
from shapely.geometry import Polygon, MultiPolygon

LAYER = 0.4   # Höhenraster der Schalen-Schnitte (mm)


def load(path):
    tm = trimesh.load(path)
    mesh = m3d.Mesh(vert_properties=np.asarray(tm.vertices, dtype=np.float32), tri_verts=np.asarray(tm.faces, dtype=np.uint32))
    return m3d.Manifold(mesh)


def section_poly(man, z):
    """Querschnitt als shapely-Geometrie."""
    cs = man.slice(z)
    polys = []
    for c in cs.to_polygons():
        if len(c) >= 3:
            polys.append(Polygon(c))
    if not polys:
        return Polygon()
    # Even-Odd über symmetrische Differenz
    g = polys[0]
    for p in polys[1:]:
        g = g.symmetric_difference(p)
    return g.buffer(0)


def levels(zmax, step=LAYER):
    n = int(zmax // step)
    return [round((i + 1) * step, 3) for i in range(n)]


def sections(man, step=LAYER):
    """Liste (z_oben_des_bandes, Querschnitt in der Bandmitte) für das ganze Gebäude."""
    zmax = man.bounding_box()[5]
    out = []
    z = 0.0
    while z < zmax - 1e-6:
        z1 = min(z + step, zmax)
        out.append((z1, section_poly(man, (z + z1) / 2)))
        z = z1
    return out


def shell(man, wall=0.8, roof=0.8, step=LAYER):
    """Hohlraum (Manifold). Der Querschnitt nimmt nach oben ab, also ist der Hohlraum die Vereinigung ineinander liegender Prismen:
    je Höhe z der um `wall` geschrumpfte Querschnitt, `roof` weiter oben gelesen, von unter dem Boden (offen) bis z. Keine Überlappungs-Splitter."""
    secs = sections(man, step)
    prisms = []
    for z1, _ in secs:
        j = int(round((z1 + roof) / step)) - 1
        pj = secs[j][1] if j < len(secs) else Polygon()
        if pj.is_empty:
            continue
        e = pj.buffer(-wall, join_style=1)
        if e.is_empty or e.area < 0.5:
            continue
        prisms.append(prism(e, -0.5, z1))
    return m3d.Manifold.batch_boolean(prisms, m3d.OpType.Add) if prisms else None


def prism(geom, z0, z1):
    cs = []
    geoms = list(geom.geoms) if isinstance(geom, MultiPolygon) else [geom]
    for p in geoms:
        if p.is_empty:
            continue
        cs.append(np.asarray(p.exterior.coords)[:-1])
        for r in p.interiors:
            cs.append(np.asarray(r.coords)[:-1])
    return m3d.Manifold.extrude(m3d.CrossSection(cs, m3d.FillRule.EvenOdd), z1 - z0).translate([0, 0, z0])


# --------------------------------------------------------------------------
# Auswertung für den Plan: Schnitte, Brücken der Decke
# --------------------------------------------------------------------------
TOL = 0.45        # Überhang je 0,4-mm-Band, der ohne Stütze geht (etwa 45°)
SPAN_CLASSES = (0.5, 1.0, 2.5, 5.0, 10.0)   # innere Radien r: Spannweite 2r = 1, 2, 5, 10, 20 mm


def layer_sets(man, wall, roof, step=LAYER):
    """Je Band: (z1, Querschnitt C, Hohlraum E); E liegt `roof` unter dem Dach und `wall` innerhalb der Wand."""
    secs = sections(man, step)
    out = []
    for i, (z1, c) in enumerate(secs):
        j = int(round((z1 + roof) / step)) - 1
        pj = secs[j][1] if j < len(secs) else Polygon()
        e = pj.buffer(-wall, join_style=1) if not pj.is_empty else Polygon()
        if (not e.is_empty) and e.area < 0.5:
            e = Polygon()
        out.append((z1, c, e))
    return out


def inscribed_radius(poly, hi=40.0):
    """Größter Innenkreis-Radius einer Fläche (Binärsuche über negative Puffer)."""
    if poly.is_empty:
        return 0.0
    lo = 0.0
    for _ in range(9):
        mid = (lo + hi) / 2
        if poly.buffer(-mid).is_empty:
            hi = mid
        else:
            lo = mid
    return lo


def bridge_analysis(layers, step=LAYER):
    """Überhänge der Schale: Fläche, die in einer Lage über Luft liegt (nicht von der Lage darunter plus TOL getragen wird).
    Rückgabe: Kennzahlen und je Spannweitenklasse die Flächen (shapely) für die Draufsicht."""
    classes = {r: [] for r in SPAN_CLASSES}
    maxr, area_tot, area_cls = 0.0, 0.0, {r: 0.0 for r in SPAN_CLASSES}
    prev = None
    for z1, c, e in layers:
        mat = c.difference(e) if not e.is_empty else c
        if prev is not None:
            sup = prev.buffer(TOL, join_style=1)
            u = mat.difference(sup)
            u = u.buffer(-0.05).buffer(0.05) if not u.is_empty else u
            if not u.is_empty and u.area > 0.3:
                area_tot += u.area
                parts = list(u.geoms) if hasattr(u, "geoms") else [u]
                for g in parts:
                    if g.area < 0.3:
                        continue
                    r = inscribed_radius(g)
                    maxr = max(maxr, r)
                for rc in SPAN_CLASSES:
                    g = u.buffer(-rc)
                    if not g.is_empty:
                        area_cls[rc] += g.buffer(rc).area
                        classes[rc].append(g.buffer(rc))
        prev = mat
    return dict(maxr=maxr, area=area_tot, area_cls=area_cls), classes
