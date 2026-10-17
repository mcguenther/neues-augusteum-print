#!/usr/bin/env python3
"""Hilfen für den Vergleich des Hof-Einsatzes vorher/nachher (plug/hof/build_page.py): der alte Umriss, der Ausschnitt der Platte um den Hof,
Umwandlung STL ↔ Volumenkörper und Schnitte. Der alte Stand (Commit c46d9d3, vor dem blockigen Umriss) liegt eingefroren in plug/hof/alt/."""
import numpy as np
import manifold3d as m3d
import trimesh
from shapely.geometry import Polygon
from shapely.ops import unary_union

import generate as G
import innenhof

REV_ALT = "c46d9d3"   # letzter Commit mit dem alten Umriss (Spalt, Steg, Zungen)


def alt_umriss(building_fps_mm, s):
    """Umriss des Hofs wie bis REV_ALT: OSM ∩ (Hofgrenze ∪ Terrasse) minus Gebäude, nur Splitter unter 1 mm entfernt."""
    data = innenhof.load()
    hof = innenhof.hof_polygon_local().intersection(Polygon(data["grenze"]).union(Polygon(data["terrasse"])))
    hof = G.scale_geom(hof, s)
    blds = unary_union(list(building_fps_mm)).buffer(2 * G.POCKET_CLEARANCE, join_style=2)
    rest = hof.difference(blds).buffer(-0.5, join_style=2).buffer(0.5, join_style=2)
    polys = G.polys_of(rest)
    big = max(p.area for p in polys)
    return G.clean(unary_union([p for p in polys if p.area > 0.05 * big]))


def ausschnitt(alt_fp, rand=6.0):
    """Bereich (mm), in dem die Platte für die 3D-Ansicht ausgeschnitten wird: alter Hofumriss plus Rand (der neue liegt darin)."""
    return G.clean(alt_fp.buffer(rand, join_style=2))


def to_man(tm):
    return m3d.Manifold(m3d.Mesh(vert_properties=np.asarray(tm.vertices, np.float32), tri_verts=np.asarray(tm.faces, np.uint32)))


def lade_stl(pfad_oder_bytes):
    import io
    src = io.BytesIO(pfad_oder_bytes) if isinstance(pfad_oder_bytes, bytes) else pfad_oder_bytes
    return trimesh.load(src, file_type="stl")


def schnitt_x(man, x0):
    """Schnitt der Ebene x = x0: Liste von Konturen (Nx2) in (y, z) mm."""
    mat = [[0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, 0]]   # (x, y, z) → (y, z, x)
    cs = man.transform(mat).slice(x0)
    return [np.asarray(c) for c in cs.to_polygons()]


def schnitt_y(man, y0):
    """Schnitt der Ebene y = y0: Liste von Konturen (Nx2) in (x, z) mm."""
    mat = [[-1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0]]   # (x, y, z) → (-x, z, y), Drehung ohne Spiegelung
    return [np.column_stack([-c[:, 0], c[:, 1]]) for c in (np.asarray(c) for c in man.transform(mat).slice(y0).to_polygons())]


def schnitt_u(man, u0, achse_grad):
    """Schnitt der Ebene u = u0 im Hofsystem (Achse nach Norden, u quer): Liste von Konturen (Nx2) in (t, z) mm."""
    mat = [[0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, 0]]
    return [np.asarray(c) for c in man.rotate([0.0, 0.0, achse_grad]).transform(mat).slice(u0).to_polygons()]


def schnitt_t(man, t0, achse_grad):
    """Schnitt der Ebene t = t0 im Hofsystem (Achse nach Norden, t längs): Liste von Konturen (Nx2) in (u, z) mm, u nach Osten."""
    return schnitt_y(man.rotate([0.0, 0.0, achse_grad]), t0)
