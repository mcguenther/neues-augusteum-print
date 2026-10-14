#!/usr/bin/env python3
"""Nimmt Panoramax-Fotos in den Messkatalog data/messfotos.json auf (Position, Blickrichtung und
Zeit aus den Panoramax-Metadaten; iPhone XR: Hauptkamera 26 mm -> horizontaler Bildwinkel ~67°).

    python3 werkzeuge/farbmessung/katalog_panoramax.py <meta.json> <bilderordner> id1 id2 ...
(Bilder werden nach data/cache/fotos/ kopiert, damit nichts erneut geladen werden muss.)
"""
import glob
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import registrierung as R
import szene

meta_path, bilder, nrs = sys.argv[1], sys.argv[2], [int(n) for n in sys.argv[3:]]
meta = {m["nr"]: m for m in json.load(open(meta_path))}
gross = {f["id"]: f for f in json.load(open(os.path.join(os.path.dirname(meta_path), "gross.json")))["features"]}
kat = R.lade_katalog()
kat["_hinweis"] = ("Fotos für die Farbmessung (farbmessung.py). Bilder werden nicht eingecheckt (data/cache/fotos/); "
                   "'url' lädt sie neu. Pose = Kamera im lokalen Modellsystem (registrierung.py).")
for nr in nrs:
    m = meta[nr]
    f = gross[m["id"]]["properties"]
    x, y = szene.lonlat_to_local(m["lon"], m["lat"])
    fid = "pmx_%s" % m["id"][:8]
    src = glob.glob(os.path.join(bilder, "%s_*.jpg" % m["id"]))[0]
    os.makedirs(R.CACHE, exist_ok=True)
    shutil.copy(src, os.path.join(R.CACHE, fid + ".jpg"))
    kat["fotos"].setdefault(fid, {}).update(
        quelle="panoramax", url=m["assets"]["sd"], seite="https://api.panoramax.xyz/#focus=pic&pic=%s" % m["id"],
        lizenz=m["lizenz"].replace("CC-BY-SA-4.0", "CC BY-SA 4.0"), urheber=m["urheber"],
        zeit=f["datetimetz"][:19] + f["datetimetz"][-6:], kamera=m["kamera"],
        prior=dict(pos=[round(x, 1), round(y, 1)], unsicher=12, yaw=m["azimut"], yaw_unsicher=15,
                   hfov=[60, 74], pitch=[-8, 15], z=[1.2, 2.0]))
R.speichere_katalog(kat)
print(len(kat["fotos"]), "Fotos im Katalog")
