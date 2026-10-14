#!/usr/bin/env python3
"""Gemeinsame Geometriewerkzeuge für alle Steckmechanismus-Generatoren (manifold3d, trimesh).

Nur Werkzeuge, keine Maße und nichts Steckerspezifisches: Quader, Zylinder, Boolesche Hilfen, Prismen,
Schnitte, Umwandlung nach trimesh und Kodierung für die HTML-Ansichten. Importiert von `plug/dupont.py`,
`plug/institute.py`, `plug/sample.py`, `plug/fit_test/generator.py` und `plug/archive/jst/jst.py`.
Alle Maße in mm.
"""
import base64

import manifold3d as m3d
import numpy as np
import trimesh


def box(x0, x1, y0, y1, z0, z1):
    return m3d.Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])


def cbox(w, d, z0, z1, cx=0.0, cy=0.0):
    return box(cx - w / 2, cx + w / 2, cy - d / 2, cy + d / 2, z0, z1)


def cyl(r, z0, z1, cx=0.0, cy=0.0, n=20):
    return m3d.Manifold.cylinder(z1 - z0, r, r, n).translate([cx, cy, z0])


def union(parts):
    parts = [p for p in parts if p is not None]
    return m3d.Manifold.batch_boolean(parts, m3d.OpType.Add)


def diff(a, *bs):
    for b in bs:
        a = a - b
    return a


def frustum(w, d, z0, z1, grow, cx=0.0, cy=0.0):
    """Pyramidenstumpf: unten (z0) w×d, oben (z1) je Seite um `grow` größer (Einführfase)."""
    cs = m3d.CrossSection([[(-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2)]])
    sc = ((w + 2 * grow) / w, (d + 2 * grow) / d)
    return m3d.Manifold.extrude(cs, z1 - z0, 0, 0.0, sc).translate([cx, cy, z0])


def keyed_cs(w, d, key):
    """Rechteck mit abgeschrägter Ecke (−x, −y) als Kodierung (Querschnitt)."""
    pts = [(-w / 2 + key, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2), (-w / 2, -d / 2 + key)]
    return m3d.CrossSection([pts])


def ext(cs, z0, z1):
    return m3d.Manifold.extrude(cs, z1 - z0).translate([0, 0, z0])


def keyed(w, d, z0, z1, key, cx=0.0, cy=0.0):
    """Quader mit abgeschrägter Ecke (−x, −y) als Kodierung."""
    return ext(keyed_cs(w, d, key), z0, z1).translate([cx, cy, 0])


def ccw(pts):
    a = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]))
    return pts if a > 0 else pts[::-1]


def prism_x(pts, x0, x1):
    """Profil in (y, z), entlang x extrudiert."""
    return m3d.Manifold.extrude(m3d.CrossSection([ccw(pts)]), x1 - x0).rotate([90, 0, 90]).translate([x0, 0, 0])


def prism_y(pts, y0, y1):
    """Profil in (x, z), entlang y extrudiert."""
    return m3d.Manifold.extrude(m3d.CrossSection([ccw(pts)]), y1 - y0).rotate([90, 0, 0]).translate([0, y1, 0])


def capsule(a, b, r, n=10):
    s = m3d.Manifold.sphere(r, n)
    return m3d.Manifold.batch_hull([s.translate(list(a)), s.translate(list(b))])


def vol_int(a, b):
    """Überschneidungsvolumen zweier Körper."""
    return (a ^ b).volume()


def to_bed(man):
    """Körper so verschieben, dass seine Unterseite auf z = 0 (Druckbett) liegt."""
    b = man.bounding_box()
    return man.translate([0, 0, -b[2]])


def xcut(man, xc):
    """Querschnitt: alles mit x > xc weg (Blick von +x)."""
    return man - box(xc, 500, -500, 500, -500, 500)


def ycut(man, yc):
    """Längsschnitt durch die Pin-Reihe: alles mit y < yc weg (Blick von −y)."""
    return man - box(-500, 500, -500, yc, -500, 500)


def to_tm(man):
    mesh = man.to_mesh()
    return trimesh.Trimesh(vertices=np.asarray(mesh.vert_properties)[:, :3],
                           faces=np.asarray(mesh.tri_verts), process=False)


def encode(tm):
    v = np.asarray(tm.vertices, np.float32)
    f = np.asarray(tm.faces, np.uint32)
    return dict(v=base64.b64encode(v.tobytes()).decode(), i=base64.b64encode(f.tobytes()).decode(),
                n=int(len(f)))
