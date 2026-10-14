#!/usr/bin/env python3
"""Farbmodell (alt/neu) in kompakter Form für den 3D-Betrachter im HTML-Bericht.

    python3 werkzeuge/farbmessung/modell_export.py <alte farben.json> <ausgabe.json>

Je Zustand (alt, neu) wird das Laserscan-Modell wie in generate.py an den Zonengrenzen zerschnitten und mit den
gemessenen Farben (farben.json, nicht auf Filamente gerundet) gefärbt (vergleich.farbmodell). Damit die Seite klein
bleibt, werden Eckpunkte auf ein 0,2-m-Raster zusammengelegt (Dreiecke darunter fallen weg), Unterseiten entfallen.
Pro Zustand liegt ein Block aus Eckpunkten (uint16), Dreiecken (uint32), Palettenindex und Änderungsklasse je Dreieck
vor (zlib, base64). Die Änderungsklasse vergleicht die Farbe mit der des anderen Zustands an derselben Stelle
(ΔE76 in Lab: 0 unter 4, 1 bis 10, 2 bis 20, 3 darüber).
"""
import base64
import json
import os
import sys
import zlib

import numpy as np
from scipy.spatial import cKDTree

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import farbmessung as FM
import generate as G
import vergleich as V

RASTER = 0.2           # m, Zusammenlegen der Eckpunkte
KLASSEN = (4.0, 10.0, 20.0)


def _hexe(cols):
    v = np.clip(np.round(np.asarray(cols) * 255), 0, 255).astype(int)
    return ["#%02x%02x%02x" % tuple(c) for c in v]


def modell(farben, quelle="laserscan"):
    """Farbmodell eines Zustands: dict(tris [n,3,3], rgb [n,3] sRGB 0..1)."""
    tris, nrm, cols = V.farbmodell(farben, quelle)
    keep = nrm[:, 2] > -0.95          # Unterseiten sieht der Betrachter nicht
    return dict(tris=tris[keep], rgb=cols[keep])


def _lab(rgb_srgb):
    return FM._lab(FM.lin(rgb_srgb))


def delta_klassen(a, b, dichte=0.6):
    """Änderungsklasse (0..3) je Dreieck von a gegenüber b: ΔE76 zwischen der Farbe von a und der von b an der
    nächsten Stichprobe auf der Oberfläche von b (Punktdichte etwa 1 je dichte² m²)."""
    t = b["tris"]
    area = 0.5 * np.linalg.norm(np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0]), axis=1)
    n = np.maximum(1, np.round(area / dichte ** 2).astype(int))
    rng = np.random.default_rng(1)
    idx = np.repeat(np.arange(len(t)), n)
    r = rng.random((len(idx), 2))
    flip = r.sum(1) > 1
    r[flip] = 1 - r[flip]
    pts = t[idx, 0] + r[:, :1] * (t[idx, 1] - t[idx, 0]) + r[:, 1:] * (t[idx, 2] - t[idx, 0])
    tree = cKDTree(pts)
    c = a["tris"].mean(1)
    _, j = tree.query(c)
    de = np.linalg.norm(_lab(a["rgb"]) - _lab(b["rgb"][idx[j]]), axis=1)
    return np.digitize(de, KLASSEN).astype(np.uint8), de


def netz(m, klassen, lo, raster=RASTER):
    """Eckpunkte auf Raster legen; liefert dict(v [k,3] uint16, f [p,3] uint32, c [p] uint8, d [p] uint8, pal)."""
    tris = m["tris"]
    q = np.round((tris.reshape(-1, 3) - lo) / raster).astype(np.int64)
    key = (q[:, 0] * 100003 + q[:, 1]) * 100003 + q[:, 2]
    u, first, inv = np.unique(key, return_index=True, return_inverse=True)
    v = q[first]
    f = inv.reshape(-1, 3)
    ok = (f[:, 0] != f[:, 1]) & (f[:, 1] != f[:, 2]) & (f[:, 0] != f[:, 2])
    hexes = np.array(_hexe(m["rgb"]))
    pal, ci = np.unique(hexes, return_inverse=True)
    f, ci, kl = f[ok], ci[ok], klassen[ok]
    srt = np.sort(f, axis=1)
    k2 = (srt[:, 0] * 10000019 + srt[:, 1]) * 10000019 + srt[:, 2]
    _, ix = np.unique(k2, return_index=True)
    ix = np.sort(ix)
    f, ci, kl = f[ix], ci[ix], kl[ix]
    used = np.unique(f)                        # nur benutzte Eckpunkte
    remap = np.zeros(len(v), np.int64)
    remap[used] = np.arange(len(used))
    return dict(v=v[used].astype(np.uint16), f=remap[f].astype(np.uint32), c=ci.astype(np.uint8), d=kl.astype(np.uint8),
                pal=list(pal))


def block(n):
    raw = n["v"].tobytes() + n["f"].tobytes() + n["c"].tobytes() + n["d"].tobytes()
    return dict(nv=int(len(n["v"])), nf=int(len(n["f"])), pal=n["pal"],
                bin=base64.b64encode(zlib.compress(raw, 9)).decode())


def export(alt_pfad, out_pfad, neu_pfad=None):
    alt = json.load(open(alt_pfad))
    neu = json.load(open(neu_pfad or os.path.join(G.HERE, "data", "farben.json")))
    a, b = modell(alt), modell(neu)
    lo = np.minimum(a["tris"].reshape(-1, 3).min(0), b["tris"].reshape(-1, 3).min(0)) - 1.0
    ka, dea = delta_klassen(a, b)
    kb, deb = delta_klassen(b, a)
    na, nb = netz(a, ka, lo), netz(b, kb, lo)
    out = dict(raster=RASTER, lo=[round(float(x), 3) for x in lo], klassen=list(KLASSEN),
               vorher=block(na), nachher=block(nb))
    with open(out_pfad, "w") as f:
        json.dump(out, f)
    print("Dreiecke: vorher %d, nachher %d; Datei %.2f MB" % (len(na["f"]), len(nb["f"]), os.path.getsize(out_pfad) / 1e6))
    print("Änderungsklassen (nachher, flächenunabhängig):", np.bincount(nb["d"], minlength=4).tolist())
    return out


if __name__ == "__main__":
    export(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
