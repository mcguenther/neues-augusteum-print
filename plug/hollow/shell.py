"""Hohlkörper-Studie: Auswertung der Schale (Brücken der Decke) für den Plan `plug/hollow/plan.html`.

Das Verfahren selbst steht im Wurzelverzeichnis in `hohl.py` (vom Generator benutzt); hier liegen nur das Laden eines STL und die Messung
der Decken-Brücken (`bridge_analysis`) auf den Lagen von `hohl.layers()`.
"""
import numpy as np
import manifold3d as m3d
import trimesh
from shapely.geometry import Polygon

LAYER = 0.4   # Höhenraster, wie hohl.STEP


def load(path):
    tm = trimesh.load(path)
    mesh = m3d.Mesh(vert_properties=np.asarray(tm.vertices, dtype=np.float32), tri_verts=np.asarray(tm.faces, dtype=np.uint32))
    return m3d.Manifold(mesh)


# --------------------------------------------------------------------------
# Auswertung für den Plan: Schnitte, Brücken der Decke
# --------------------------------------------------------------------------
TOL = 0.45        # Überhang je 0,4-mm-Band, der ohne Stütze geht (etwa 45°)
SPAN_CLASSES = (0.5, 1.0, 2.5, 5.0, 10.0)   # Reichweiten r: Spannweite 2r = 1, 2, 5, 10, 20 mm


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
    """Überhänge der Schale. Je Lage ist U das Material, das nicht von der Lage darunter (plus TOL) getragen wird. Maß ist der Abstand eines
    Punktes von U zum Material der Lage darunter („Reichweite“); die freie Spannweite einer Brücke ist etwa das Doppelte, ein einseitiger
    Überhang hat genau diese Länge. Rückgabe: Kennzahlen (maxr = größte Reichweite, maxpt = Punkt dazu, area_cls = Fläche je Klasse) und je
    Klasse die Flächen (shapely) für die Draufsicht."""
    classes = {r: [] for r in SPAN_CLASSES}
    maxr, area_tot, area_cls = 0.0, 0.0, {r: 0.0 for r in SPAN_CLASSES}
    maxpt = None   # (x, y, Lagenindex) der größten freien Decke
    prev = None
    for li, (z1, c, e) in enumerate(layers):
        mat = c.difference(e) if not e.is_empty else c
        if prev is not None:
            u = mat.difference(prev.buffer(TOL, join_style=1, quad_segs=4))
            u = u.buffer(-0.05).buffer(0.05) if not u.is_empty else u
            if not u.is_empty and u.area > 0.3:
                area_tot += u.area
                for rc in SPAN_CLASSES:
                    g = u.difference(prev.buffer(rc, quad_segs=4))
                    g = g.buffer(-0.05).buffer(0.05) if not g.is_empty else g
                    if not g.is_empty and g.area > 0.1:
                        area_cls[rc] += g.area
                        classes[rc].append(g)
                # größte Reichweite dieser Lage (Binärsuche über den Abstand zur Lage darunter)
                def frei(r):
                    g = u.difference(prev.buffer(r, quad_segs=4))
                    return None if g.is_empty else (g.buffer(-0.05).buffer(0.05) if g.area > 1.0 else None)
                if frei(maxr + 0.05) is not None and not frei(maxr + 0.05).is_empty and frei(maxr + 0.05).area > 1.0:
                    lo, hi = maxr, maxr + 60.0
                    for _ in range(9):
                        mid = (lo + hi) / 2
                        g = frei(mid)
                        if g is None or g.is_empty or g.area <= 1.0:
                            hi = mid
                        else:
                            lo = mid
                    pt = frei(lo).representative_point() if frei(lo) is not None and not frei(lo).is_empty else u.representative_point()
                    maxr, maxpt = lo, (pt.x, pt.y, li)
        prev = mat
    return dict(maxr=maxr, area=area_tot, area_cls=area_cls, maxpt=maxpt), classes
