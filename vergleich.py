#!/usr/bin/env python3
"""Farbmodelle (alt/neu) aus der Kameraposition eines Fotos rendern – für den Vergleich Foto | alt | neu.

Das Gebäudemodell wird wie in generate.py an den Zonengrenzen zerschnitten und je Dreieck gefärbt
(fassaden.colour_mesh), dann mit der registrierten Foto-Kamera (kamera.py) gerendert.
"""
import json
import os

import numpy as np
from PIL import Image

import farben as F
import fassaden
import generate as G
import kamera as K
import szene

_ROOF = None


def farbmodell(farben, quelle="laserscan"):
    """farben: Inhalt einer farben.json (alt oder neu). Liefert (Dreiecke[n,3,3], Normalen[n,3], RGB[n,3]) in
    Szenenkoordinaten für alle Gebäude der Szene."""
    global _ROOF
    sc = szene.laden(quelle)
    if _ROOF is None:
        _ROOF = F.roof_classifier(farben)
    import preview as P
    tris, nrm, cols = [], [], []
    for slug, (m, dz) in sc.items():
        loc = m.copy()
        loc.vertices = loc.vertices - [0, 0, dz]
        e = farben.get(slug)
        mesh, hexes = fassaden.colour_mesh(loc, slug, ((0, 0, 0), 1.0), e, _ROOF)
        t = mesh.triangles + [0, 0, dz]
        tris.append(t)
        nrm.append(mesh.face_normals)
        cols.append(np.array([P.rgb(h) for h in hexes]))
    return np.vstack(tris), np.vstack(nrm), np.vstack(cols)


def ansicht(kam, modell, hintergrund=(236, 238, 240), licht=(-0.35, -0.55, 0.76), scale=0.5):
    """Flach schattiertes Bild des Farbmodells aus der Kamera (PIL, Größe = scale · Foto)."""
    import preview as P
    tris, nrm, cols = modell
    fid, tiefe = kam.exakt(tris, nrm, scale)
    H, W = fid.shape
    img = np.empty((H, W, 3))
    img[:] = np.array(hintergrund) / 255.0
    hit = fid >= 0
    f = fid[hit]
    l = np.array(licht) / np.linalg.norm(licht)
    shade = 0.9 + 0.1 * np.clip(nrm[f] @ l, 0, 1)
    img[hit] = np.clip(cols[f] * shade[:, None], 0, 1)
    return Image.fromarray((img * 255).astype(np.uint8)), hit
