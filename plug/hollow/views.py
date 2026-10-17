#!/usr/bin/env python3
"""Ansichten der Hohlkörper für `plug/hollow/plan.html`: Netze für die 3D-Ansicht und aufgeschnittene Renderbilder.

Je Gebäude (Laserscan 1:1500, `stl/laserscan/1zu1500/einzeln/`) wird die Schale mit `hohl.py` gebaut und jede Fläche einer Klasse zugeordnet:
0 Außenhaut, 1 Innenwand oder Decke wie gezielt, 2 Gewölbe (Material, das ohne Gewölbe Hohlraum wäre), 3 Schnittfläche (nur Renderbilder).
Die Renderbilder landen in `vorschau/hohl/<slug>_schnitt.png`. Aufgerufen von `plug/hollow/build_plan.py`.
"""
import base64
import os
import sys

import manifold3d as m3d
import numpy as np
import shapely
import trimesh

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, HERE)
import hohl      # noqa: E402
import preview   # noqa: E402
from plug.hollow import shell as S  # noqa: E402

OUT_PNG = os.path.join(HERE, "vorschau", "hohl")
COLOURS = {0: "#c9c2b6", 1: "#f1e6cf", 2: "#e39a3b", 3: "#56606e"}   # Außenhaut, innen, Gewölbe, Schnitt (Renderbilder)


def to_tm(man):
    m = man.to_mesh()
    return trimesh.Trimesh(np.asarray(m.vert_properties)[:, :3], np.asarray(m.tri_verts), process=False)


def to_man(tm):
    return m3d.Manifold(m3d.Mesh(vert_properties=np.asarray(tm.vertices, np.float32), tri_verts=np.asarray(tm.faces, np.uint32)))


def classes(tm, lay, lay0, step=hohl.STEP):
    """Klasse je Dreieck: 0 außen, 1 innen, 2 Gewölbe (hinter der Fläche läge ohne Gewölbe Hohlraum)."""
    inner = hohl.inner_mask(tm, lay)
    q = tm.triangles_center - 0.15 * tm.face_normals
    idx = np.floor(q[:, 2] / step).astype(int)
    vault = np.zeros(len(tm.faces), bool)
    for i in np.unique(idx):
        if 0 <= i < len(lay0) and not lay0[i][2].is_empty:
            sel = idx == i
            vault[sel] = shapely.contains_xy(lay0[i][2], q[sel, 0], q[sel, 1])
    return np.where(inner & vault, 2, np.where(inner, 1, 0)).astype(np.uint8)


def encode(tm, cls):
    """Netz kompakt für die Seite: Ecken als uint16 im Hüllquader, Dreiecke uint32, Klasse uint8 (base64)."""
    lo, hi = tm.vertices.min(axis=0), tm.vertices.max(axis=0)
    sc = np.maximum(hi - lo, 1e-6)
    q = np.round((tm.vertices - lo) / sc * 65535).astype(np.uint16)
    b = lambda a: base64.b64encode(np.ascontiguousarray(a).tobytes()).decode()
    return dict(lo=[round(float(x), 3) for x in lo], sc=[round(float(x), 4) for x in sc], v=b(q), f=b(tm.faces.astype(np.uint32)),
                c=b(cls), n=int(len(tm.faces)))


def cut_render(tm, cls, axis, value, title, path, elev=26):
    """Aufgeschnittenes Gebäude: behält die Seite <= value (axis 0: Schnitt quer zu y, 1: quer zu x), Blick schräg auf die Schnittfläche."""
    normal = [0.0, 0.0, 0.0]
    normal[1 if axis == 0 else 0] = -1.0                     # behält y <= value bzw. x <= value
    half = to_man(tm).trim_by_plane(normal, -value)
    ht = to_tm(half)
    hc = classes_like(ht, tm, cls)
    on_plane = np.abs(ht.triangles_center[:, 1 if axis == 0 else 0] - value) < 1e-3
    hc[on_plane & (np.abs(ht.face_normals[:, 1 if axis == 0 else 0]) > 0.99)] = 3
    cols = np.array([preview.rgb(COLOURS[int(k)]) for k in hc])
    azim = (90 if axis == 0 else 0) - 28
    im = preview.render([(ht, cols)], size=(900, 620), azim=azim, elev=elev, light_from_view=True)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    preview.caption(im, title, "aufgeschnitten · Gewölbe orange · Schnittfläche dunkel").save(path, optimize=True)
    return path


def classes_like(ht, tm, cls):
    """Klassen für ein aufgeschnittenes Netz: vom nächsten Dreieck des ganzen Netzes übernehmen."""
    from scipy.spatial import cKDTree
    _, idx = cKDTree(tm.triangles_center).query(ht.triangles_center)
    return cls[idx].copy()


def build(names, study, title):
    """{slug: Netzdaten} für die 3D-Ansicht und {slug: Pfad} der Renderbilder."""
    meshes, pngs = {}, {}
    for n in names:
        man = S.load(os.path.join(HERE, "stl", "laserscan", "1zu1500", "einzeln", n + ".stl"))
        shell, lay = hohl.hohl(man)
        lay0 = hohl.layers(man, gewoelbe=False)
        tm = to_tm(shell)
        cls = classes(tm, lay, lay0)
        light = to_tm(shell.simplify(0.08))
        meshes[n] = encode(light, classes(light, lay, lay0))
        v = study["laserscan/" + n]
        meshes[n].update(cut_axis=int(v["cut_axis"]), cut=float(v["cut_y"]))
        pngs[n] = cut_render(tm, cls, int(v["cut_axis"]), float(v["cut_y"]), title[n], os.path.join(OUT_PNG, n + "_schnitt.png"))
        print("  Ansicht %-22s %6d Dreiecke (3D %d)" % (n, len(tm.faces), meshes[n]["n"]), flush=True)
    return meshes, pngs
