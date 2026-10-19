#!/usr/bin/env python3
"""3D-Seite der farbigen Steckgebäude: `plug/views/farbig/view.html` aus `view.template.html`.

Die Daten (Außenflächen je Gebäude, Farbindex je Dreieck für den besten Satz und für die vier Hauptfarben) schreibt
`python3 -m plug.colour` nach `plug/views/farbig/data.json`; dieses Skript setzt nur die Seite zusammen (Sekunden):
    python3 -m plug.views.farbig.build_view
"""
import base64
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
DATA = os.path.join(HERE, "data.json")
Q = 0.01   # mm je Schritt der Quantisierung (Uint16)


def _b64(a):
    return base64.b64encode(np.ascontiguousarray(a).tobytes()).decode()


def _netz(tri, idx):
    """Dreiecke (n, 3, 3) in mm als Uint16 relativ zu ihrem Minimum, dazu Farbindizes je Dreieck."""
    lo = tri.reshape(-1, 3).min(axis=0)
    q = np.round((tri.reshape(-1, 3) - lo) / Q).astype("<u2")
    return {"lo": [round(float(v), 3) for v in lo], "pos": _b64(q), "n": int(len(tri))}


def daten(einzeln, info, scale):
    """einzeln: {slug: (name, Netz, Hex je Dreieck (Satz), Satz [(hex, name)], Außenmaske, Hex je Dreieck (Hauptfarben), Hex je Dreieck (einfarbig))}."""
    import trimesh
    import farben as F
    from plug import campus as C
    from plug.testcase import params as P
    T = C.plate_thickness(P.dims_plan())
    pal = {c: i for i, (c, _) in enumerate(F.FILAMENTE)}
    objs = []
    for slug, (name, mesh, red, satz, outer, red_h, red_1) in einzeln.items():
        fuss = ~outer & (mesh.triangles_center[:, 2] < 0.05) & (np.abs(mesh.face_normals[:, 2]) < 0.9)   # Wände des Fußes, hinten angehängt
        keep = np.r_[np.flatnonzero(outer), np.flatnonzero(fuss)]
        tri = mesh.triangles[keep] + [0, 0, T]
        g = info["gebaeude"][slug]
        o = dict(slug=slug, name=name, **_netz(tri, None),
                 satz=_b64(np.array([pal[h] for h in red[keep]], "u1")),
                 haupt=_b64(np.array([pal[h] for h in red_h[keep]], "u1")),
                 einfarbig=_b64(np.array([pal[h] for h in red_1[keep]], "u1")), einfarbig_namen=g["einfarbig"], datei_einfarbig=g["datei_einfarbig"],
                 n_aussen=int(outer.sum()), filamente=g["satz"], anteile=g["anteile_prozent"], datei=g["datei"],
                 dE=g["abweichung_dE"], dE_haupt=g["abweichung_hauptfarben_dE"],
                 mass=[round(float(v), 1) for v in mesh.extents])
        objs.append(o)
    plate = trimesh.load(os.path.join(ROOT, "stl", "steckmodul_campus", "steckplatte_1zu%d.stl" % scale), process=False)
    d = dict(scale=scale, filamente=info["filamente"], objekte=objs, platte=_netz(plate.triangles, None), q=Q,
             alle=info.get("alle"))
    json.dump(d, open(DATA, "w"))
    main()


def main():
    tpl = open(os.path.join(HERE, "view.template.html"), encoding="utf-8").read()
    data = open(DATA, encoding="utf-8").read()
    out = os.path.join(HERE, "view.html")
    open(out, "w", encoding="utf-8").write(tpl.replace("@DATA@", data))
    print("  Seite:", os.path.relpath(out, ROOT), "%.1f MB" % (os.path.getsize(out) / 1e6))


if __name__ == "__main__":
    main()
