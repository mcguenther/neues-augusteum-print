#!/usr/bin/env python3
"""Fotokatalog für die Farbmessung (data/messfotos.json) und Registrierung der Fotos am Modell.

Katalogeintrag je Foto:
    {"quelle": "panoramax|commons|...", "url": "<Bild, ≥1500 px>", "seite": "<Quellseite>",
     "lizenz": "CC BY-SA 4.0", "urheber": "...", "zeit": "2022-03-27T15:34:48+02:00",
     "gebaeude": ["01", "02"], "prior": {...}, "pose": {...}, "pose_kosten": 0.03, "geprueft": true}

prior (Suchbereich der Pose, Meter im lokalen System x Ost / y Nord):
    pos [x, y] + "unsicher" (m)  oder  "bereich" [xmin, xmax, ymin, ymax]
    yaw (Kompasskurs der Blickrichtung) + "yaw_unsicher" (°)   (oder "yaw_bereich" [lo, hi])
    hfov [lo, hi]  pitch [lo, hi]  z [lo, hi]  roll [lo, hi]

Aufruf:
    python3 registrierung.py suche [id ...]     Pose per Himmelslinie suchen (alle ohne Pose, oder die genannten)
    python3 registrierung.py pruefen [id ...]   Überlagerungen (Modellkanten im Foto) nach vorschau/messung/ schreiben
"""
import json
import os
import sys
import urllib.request

import numpy as np
from PIL import Image

import generate as G
import kamera as K
import parallel
import skyline
import szene

KATALOG = os.path.join(G.HERE, "data", "messfotos.json")
CACHE = os.path.join(G.HERE, "data", "cache", "fotos")
UA = "neues-augusteum-print/1.0 (3D-Druckmodelle Campus Augustusplatz)"


def lade_katalog():
    return json.load(open(KATALOG)) if os.path.exists(KATALOG) else {"_hinweis": "", "fotos": {}}


def speichere_katalog(k):
    with open(KATALOG, "w") as f:
        json.dump(k, f, indent=1, ensure_ascii=False)


def foto_bild(fid, e):
    """Foto (PIL, RGB) aus dem Cache; fehlt es, wird es von e["url"] geladen."""
    import time
    path = os.path.join(CACHE, fid + ".jpg")
    if not os.path.exists(path):
        os.makedirs(CACHE, exist_ok=True)
        req = urllib.request.Request(e["url"], headers={"User-Agent": UA})
        for k in range(5):
            try:
                data = urllib.request.urlopen(req, timeout=120).read()
                break
            except OSError as ex:
                if k == 4 or getattr(ex, "code", 0) == 404:
                    raise
                time.sleep(5 * (k + 1))
        with open(path, "wb") as f:
            f.write(data)
    return Image.open(path).convert("RGB")


def grenzen(prior):
    if "bereich" in prior:
        x0, x1, y0, y1 = prior["bereich"]
    else:
        (px, py), u = prior["pos"], prior.get("unsicher", 12.0)
        x0, x1, y0, y1 = px - u, px + u, py - u, py + u
    if "yaw_bereich" in prior:
        ya = tuple(prior["yaw_bereich"])
    else:
        ya = (prior["yaw"] - prior.get("yaw_unsicher", 15.0), prior["yaw"] + prior.get("yaw_unsicher", 15.0))
    return [(x0, x1), (y0, y1), tuple(prior.get("z", (1.3, 2.2))), ya, tuple(prior.get("pitch", (-8, 20))),
            tuple(prior.get("roll", (-3, 3))), tuple(prior.get("hfov", (55, 80)))]


def suche_pose(fid, e, popsize=12, maxiter=90, seed=1):
    img = foto_bild(fid, e)
    mesh, _, _ = szene.gesamt(None, "lod2")
    s = skyline.Suche(img, mesh.triangles, min_abdeckung=e["prior"].get("min_abdeckung", 0.4))
    kam, c = s.lauf(grenzen(e["prior"]), popsize=popsize, maxiter=maxiter, seed=seed, workers=1)
    print("  %-24s Kosten %.4f  %s" % (fid, c, kam.to_dict()))
    return fid, kam.to_dict(), float(c)


def registriere(ids=None, jobs=None, neu=False):
    kat = lade_katalog()
    todo = [i for i, e in kat["fotos"].items() if (ids is None or i in ids) and "prior" in e
            and (neu or "pose" not in e or (ids and i in ids))]
    if jobs:
        parallel.JOBS = jobs
    res = parallel.starmap(suche_pose, [(i, kat["fotos"][i]) for i in todo])
    for fid, pose, c in res:
        kat["fotos"][fid]["pose"], kat["fotos"][fid]["pose_kosten"] = pose, round(c, 4)
        kat["fotos"][fid].pop("geprueft", None)
    speichere_katalog(kat)
    return res


def pruefbild(fid, e, out_dir, laser=None):
    """Foto mit Modellkanten (je Gebäude eine Farbe) -> out_dir/<fid>_pose.jpg."""
    img = foto_bild(fid, e)
    kam = K.Kamera.aus_dict(e["pose"], *img.size)
    sc = laser or szene.laden("laserscan")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, fid + "_pose.jpg")
    im = K.ueberlagerung(img, kam, sc)
    im.thumbnail((1400, 1000))
    im.save(path, quality=85)
    return path


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "suche":
        registriere(sys.argv[2:] or None)
    elif len(sys.argv) >= 2 and sys.argv[1] == "pruefen":
        kat = lade_katalog()
        sc = szene.laden("laserscan")
        out = os.path.join(G.HERE, "vorschau", "messung")
        for i, e in kat["fotos"].items():
            if "pose" in e and (len(sys.argv) == 2 or i in sys.argv[2:]):
                print(pruefbild(i, e, out, sc))
    else:
        print(__doc__)
