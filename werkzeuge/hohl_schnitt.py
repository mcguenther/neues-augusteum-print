#!/usr/bin/env python3
"""Schnittansichten der Hohlkörper: je *_farbig.3mf in einzeln_hohl/ ein Bild mit aufgeschnittenem Gebäude (Blick auf die Schnittfläche).

    python3 werkzeuge/hohl_schnitt.py stl-fast/laserscan/1zu1500/einzeln_hohl --out $SCRATCHPAD/schnitt
Das Gebäude wird in der Mitte der kürzeren Grundrissachse geschnitten (Manifold, exakt); die Farben der Schnittfläche
kommen vom nächsten Dreieck des gefärbten Netzes.
"""
import argparse
import glob
import os
import sys

import manifold3d as m3d
import numpy as np
import trimesh
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import preview  # noqa: E402


def cut_view(path, out_png, elev=38):
    (name, mesh, cols), = preview.load_3mf_coloured(path)
    ext = mesh.extents
    axis = 0 if ext[0] <= ext[1] else 1                      # senkrecht zur kürzeren Seite schneiden
    c = mesh.bounds.mean(axis=0)
    man = m3d.Manifold(m3d.Mesh(vert_properties=np.asarray(mesh.vertices, np.float32), tri_verts=np.asarray(mesh.faces, np.uint32)))
    n = [0.0, 0.0, 0.0]
    n[axis] = 1.0                                             # behält x (bzw. y) <= Schnitt, Blick von +x (bzw. +y)
    half = man.trim_by_plane([-v for v in n], -c[axis])
    mm = half.to_mesh()
    tm = trimesh.Trimesh(mm.vert_properties[:, :3], mm.tri_verts, process=False)
    _, idx = cKDTree(mesh.triangles_center).query(tm.triangles_center)
    azim = 0 if axis == 0 else 90
    im = preview.render([(tm, cols[idx])], size=(900, 700), azim=azim, elev=elev, light_from_view=True)
    preview.caption(im, name + ", Schnitt", None).save(out_png)
    print(os.path.basename(out_png))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dir")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    for f in sorted(glob.glob(os.path.join(a.dir, "*_farbig.3mf"))):
        cut_view(f, os.path.join(a.out, os.path.basename(f).replace("_farbig.3mf", "_schnitt.png")))
