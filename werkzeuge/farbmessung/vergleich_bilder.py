#!/usr/bin/env python3
"""Bilder für den Farbvergleich alt/neu: Foto | Modell alt | Modell neu aus derselben Kameraposition,
Überlagerungen der Registrierung und abgewickelte Fassadenkarten.

    python3 werkzeuge/farbmessung/vergleich_bilder.py <alte farben.json> [ausgabeordner]

Standard-Ausgabe: vorschau/farbvergleich/. Die „neuen“ Farben sind data/farben.json.
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import farbmessung as FM
import generate as G
import kamera as K
import registrierung as R
import szene
import vergleich as V

# Fotos für die Gegenüberstellung (Reihenfolge = Reihenfolge im Bericht)
FOTOS = ["fl_25383321126", "fl_13957964694", "fl_16905251612", "fl_16719063090", "fl_24782688903",
         "fl_25291096262", "fl_25292032932", "fl_25409407395", "fl_9656690560"]
BREITE = 720


def main(alt_pfad, out):
    os.makedirs(out, exist_ok=True)
    alt = json.load(open(alt_pfad))
    neu = json.load(open(os.path.join(G.HERE, "data", "farben.json")))
    ma, mn = V.farbmodell(alt), V.farbmodell(neu)
    kat = R.lade_katalog()["fotos"]
    sc_laser = szene.laden("laserscan")
    for fid in FOTOS:
        e = kat[fid]
        img = R.foto_bild(fid, e)
        kam = K.Kamera.aus_dict(e["pose"], *img.size)
        s = BREITE / img.width
        for name, m in (("alt", ma), ("neu", mn)):
            im, _ = V.ansicht(kam, m, scale=s)
            im.save(os.path.join(out, "%s_%s.jpg" % (fid, name)), quality=88)
        img.resize((BREITE, int(img.height * s)), Image.LANCZOS).save(os.path.join(out, "%s_foto.jpg" % fid), quality=88)
        ov = K.ueberlagerung(img, kam, sc_laser)
        ov.resize((BREITE, int(img.height * s)), Image.LANCZOS).save(os.path.join(out, "%s_pose.jpg" % fid), quality=85)
        print("  ", fid)
    # Bild für die README: Foto | alt | neu des ersten Fotos
    ims = [Image.open(os.path.join(out, "%s_%s.jpg" % (FOTOS[0], n))).convert("RGB") for n in ("foto", "alt", "neu")]
    h = min(i.height for i in ims)
    ims = [i.resize((int(i.width * h / i.height), h)) for i in ims]
    sheet = Image.new("RGB", (sum(i.width for i in ims) + 20, h), (250, 250, 248))
    x = 0
    for i in ims:
        sheet.paste(i, (x, 0))
        x += i.width + 10
    sheet.save(os.path.join(out, "vergleich_romero.jpg"), quality=88)
    # abgewickelte Fassaden (Konsens besonnter Zellen)
    kons, _ = FM.messen_konsens()
    sc = FM.Szene()
    for slug, seite, name in (("02_neues_augusteum", 1, "augusteum_ost"), ("01_paulinum", 1, "paulinum_ost")):
        b = sc.slugs.index(slug)
        r = FM.fassadenkarte(kons, b, seite, px=12, maske=kons["n_licht"] > 0)
        if r:
            im, (T, Z) = r
            im.save(os.path.join(out, "fassade_%s.png" % name))
            print("  Fassade", name, T, "x", Z, "m")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else os.path.join(G.HERE, "vorschau", "farbvergleich"))
