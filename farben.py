#!/usr/bin/env python3
"""Bestimmt Dach- und Fassadenfarben der Gebäude aus offenen Bilddaten.

- Dachfarbe: Median der Luftbild-Pixel (Stadt Leipzig, Luftbild 2024, 20 cm,
  WMTS, dl-de/by-2-0) innerhalb des Gebäudegrundrisses, je Gebäude und zusätzlich
  als Raster für die farbige Vorschau (jede Dachfläche bekommt ihre Farbe).
  Das GeoSN-DOP 2025 (März) wäre auch frei verfügbar, hat aber lange
  Schlagschatten des Uniriesen über dem Campus; das Leipziger Luftbild ist
  sommerlicher und deutlich schattenärmer.
- Fassadenfarbe: Median über Bildausschnitte aus Panoramax-Straßenfotos
  (CC-BY-SA-4.0), definiert in data/fassaden_proben.json. Für Fassaden ohne
  offenes Foto: OSM-Tags building:colour / building:material, sonst eine
  ausdrücklich als Annahme markierte Farbe.

Ergebnis: data/farben.json (wird von preview.py für die farbigen Vorschauen und
von generate.py für die farbigen 3MF-Dateien benutzt). Bilder werden nur in
data/cache/ zwischengespeichert (nicht im Repo).

Aufruf:  python3 farben.py
"""
import io
import json
import os
import urllib.request

import numpy as np
import shapely
from PIL import Image, ImageDraw

import generate as G
import lod2

CACHE = os.path.join(G.HERE, "data", "cache")
PROBEN = os.path.join(G.HERE, "data", "fassaden_proben.json")
FARBEN = os.path.join(G.HERE, "data", "farben.json")
DOP_FILE = os.path.join(G.HERE, "data", "luftbild2024_campus.jpg")  # Ausschnitt, © Stadt Leipzig
WMTS = ("https://geodienste.leipzig.de/l1/Rasterdaten/luftbild_2024/MapServer/WMTS/tile/1.0.0/"
        "Rasterdaten_luftbild_2024/default/default028mm/{z}/{row}/{col}")
WMTS_LEVEL = 9                                   # 944,94 · 0,28 mm = 0,265 m/Pixel
WMTS_RES = 944.9423660750896 * 0.00028
WMTS_ORIGIN = (-5120900.0, 9998100.0)            # TopLeftCorner der TileMatrixSet
PANORAMAX = "https://api.panoramax.xyz/api/pictures/{}"
REF_GRAU = 150.0  # angenommener Grauwert (0..255) des Granitpflasters für Weißabgleich/Belichtung

# Für Fassaden ohne Foto: OSM-Material -> typische Farbe
MATERIAL = {"brick": "#9c5a3c", "stone": "#c9c5bc", "plaster": "#dcd8cf", "glass": "#6f8796",
            "concrete": "#b5b2ab", "metal": "#9da3a6"}
OSM_NAMED = {"lightgrey": "#d3d3d3", "gray": "#808080", "grey": "#808080", "white": "#f2f2f2"}
# Gebäude ohne offenes Foto und ohne brauchbare OSM-Angabe (Annahme, s. README)
ANNAHME = {
    "03_hoersaalgebaeude": ("#d8d6d0", "Annahme: helle Natursteinfassade wie die übrigen Campus-Neubauten"),
    "04_seminargebaeude": ("#d8d6d0", "Annahme: helle Natursteinfassade wie die übrigen Campus-Neubauten"),
}


def hexcol(rgb):
    return "#%02x%02x%02x" % tuple(int(round(v)) for v in rgb)


def fetch(url, path):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        req = urllib.request.Request(url, headers={"User-Agent": "neues-augusteum-print/1.0"})
        with urllib.request.urlopen(req, timeout=180) as r, open(path, "wb") as f:
            f.write(r.read())
    return path


# --------------------------------------------------------------------------
# Orthofoto
# --------------------------------------------------------------------------
def dop_bounds():
    blds = lod2.load_lod2()
    xs, ys = [], []
    for b in blds:
        for r, _ in b["roofs"]:
            ux, uy = lod2.local_to_utm(r[:, 0], r[:, 1])
            xs += list(ux)
            ys += list(uy)
    m = 15.0
    return (np.floor(min(xs) - m), np.floor(min(ys) - m), np.ceil(max(xs) + m), np.ceil(max(ys) + m))


def load_dop():
    """Luftbild-Ausschnitt (RGB-Array) und UTM-Bounds der Pixelkanten."""
    import time
    x0, y0, x1, y1 = dop_bounds()
    T = 256 * WMTS_RES
    X0, Y0 = WMTS_ORIGIN
    c0, c1 = int((x0 - X0) // T), int((x1 - X0) // T)
    r0, r1 = int((Y0 - y1) // T), int((Y0 - y0) // T)
    bounds = (X0 + c0 * T, Y0 - (r1 + 1) * T, X0 + (c1 + 1) * T, Y0 - r0 * T)
    if not os.path.exists(DOP_FILE):
        mos = Image.new("RGB", ((c1 - c0 + 1) * 256, (r1 - r0 + 1) * 256))
        for r in range(r0, r1 + 1):
            for c in range(c0, c1 + 1):
                url = WMTS.format(z=WMTS_LEVEL, row=r, col=c)
                for k in range(6):  # der Server bricht gelegentlich Verbindungen ab
                    try:
                        req = urllib.request.Request(url, headers={"User-Agent": "neues-augusteum-print/1.0"})
                        tile = Image.open(io.BytesIO(urllib.request.urlopen(req, timeout=60).read()))
                        break
                    except OSError:
                        time.sleep(2 * (k + 1))
                else:
                    raise RuntimeError("Kachel nicht ladbar: " + url)
                mos.paste(tile.convert("RGB"), ((c - c0) * 256, (r - r0) * 256))
        mos.save(DOP_FILE, quality=88)
    return np.asarray(Image.open(DOP_FILE).convert("RGB")), bounds


def load_farben():
    if not os.path.exists(FARBEN):
        return None
    return json.load(open(FARBEN))


def dop_sampler():
    """Funktion (x_lokal, y_lokal) in m -> RGB 0..1 aus dem Luftbild (leicht weichgezeichnet)."""
    from scipy import ndimage
    img, (x0, y0, x1, y1) = load_dop()
    img = ndimage.uniform_filter(img.astype(float), size=(5, 5, 1)) / 255.0  # ~1 m Mittel
    H, W, _ = img.shape

    def sample(x, y):
        ux, uy = lod2.local_to_utm(np.asarray(x), np.asarray(y))
        c = np.clip(((ux - x0) / WMTS_RES).astype(int), 0, W - 1)
        r = np.clip(((y1 - uy) / WMTS_RES).astype(int), 0, H - 1)
        return img[r, c]
    return sample


def roof_colours(img, bounds, cells):
    x0, y0, x1, y1 = bounds
    H, W, _ = img.shape
    cols = (np.arange(W) + 0.5) * WMTS_RES + x0
    rows = y1 - (np.arange(H) + 0.5) * WMTS_RES
    X, Y = np.meshgrid(cols, rows)
    out = {}
    for slug, cell in cells.items():
        to_utm = lambda a: np.column_stack(lod2.local_to_utm(a[:, 0], a[:, 1]))
        poly = shapely.transform(cell, to_utm).buffer(-1.0)
        minx, miny, maxx, maxy = poly.bounds
        c0, c1 = int((minx - x0) / WMTS_RES), int((maxx - x0) / WMTS_RES) + 1
        r0, r1 = int((y1 - maxy) / WMTS_RES), int((y1 - miny) / WMTS_RES) + 1
        sub = (slice(max(r0, 0), r1), slice(max(c0, 0), c1))
        inside = shapely.contains_xy(poly, X[sub], Y[sub])
        px = img[sub][inside].astype(float)
        lum = px @ [0.299, 0.587, 0.114]
        lit = px[lum >= np.percentile(lum, 35)]  # Schlagschatten weitgehend ausblenden
        out[slug] = dict(rgb=hexcol(np.median(lit, axis=0)), pixel=int(len(px)))
    return out


# --------------------------------------------------------------------------
# Fassaden
# --------------------------------------------------------------------------
def photo(pid):
    meta_path = os.path.join(CACHE, "panoramax", pid + ".json")
    fetch(PANORAMAX.format(pid), meta_path)
    meta = json.load(open(meta_path))
    path = fetch(meta["assets"]["sd"]["href"], os.path.join(CACHE, "panoramax", pid + ".jpg"))
    return Image.open(path).convert("RGB"), meta


def box_median(im, b):
    W, H = im.size
    crop = np.asarray(im.crop((int(b[0] * W), int(b[1] * H), int(b[2] * W), int(b[3] * H))), float)
    return np.median(crop.reshape(-1, 3), axis=0)


def facade_samples():
    """Fassadenfarben aus den Foto-Ausschnitten, weißabgeglichen am grauen Pflaster."""
    data = json.load(open(PROBEN))
    res = []
    for p in data["proben"]:
        im, meta = photo(p["bild"])
        rgb = box_median(im, p["box"])
        wb = data.get("weissabgleich", {}).get(p["bild"])
        if wb:
            # Weißabgleich + Belichtung: Pflaster -> neutrales Granitgrau (Annahme REF_GRAU)
            ref = box_median(im, wb["box"])
            rgb = np.clip(rgb * REF_GRAU / ref, 0, 255)
        res.append(dict(p, rgb=hexcol(rgb), roh=hexcol(box_median(im, p["box"])),
                        datum=meta["properties"]["datetime"][:10],
                        lizenz=meta["properties"].get("license"),
                        fotograf=meta["properties"].get("geovisio:producer"),
                        url="https://api.panoramax.xyz/#focus=pic&pic=%s" % p["bild"]))
    return res


def osm_facades():
    feats = G.load_features()
    out = {}
    for b in G.BUILDINGS:
        outline, parts = G.building_parts(feats, b["osm"])
        for _, t, fid in sorted(parts, key=lambda p: -p[0].area):  # größter Bauteil zuerst
            c = t.get("building:colour")
            m = t.get("building:material")
            if c:
                out.setdefault(b["slug"], ("OSM building:colour=%s (%s)" % (c, fid),
                                           OSM_NAMED.get(c, c if c.startswith("#") else None)))
            elif m in MATERIAL:
                out.setdefault(b["slug"], ("OSM building:material=%s (%s)" % (m, fid), MATERIAL[m]))
    return out


def main():
    img, bounds = load_dop()
    cells = {k: v[1] for k, v in lod2.models(1.0).items()}  # Grundrisse (bei s = 1 in m)
    dach = roof_colours(img, bounds, cells)
    proben = facade_samples()
    osm = osm_facades()
    farben = {"_quellen": {
        "dach": "Stadt Leipzig, Luftbild 2024 (20 cm, WMTS), dl-de/by-2-0, Median im Grundriss",
        "fassade_foto": "Panoramax-Straßenfotos, CC-BY-SA-4.0, Ausschnitte in data/fassaden_proben.json",
        "fassade_osm": "OpenStreetMap building:colour / building:material (ODbL)"}}
    for b in G.BUILDINGS:
        slug = b["slug"]
        e = dict(name=b["name"], dach=dach[slug]["rgb"] if slug in dach else None)
        mine = [p for p in proben if p["gebaeude"] == slug]
        haupt = [p for p in mine if p["rolle"] == "haupt"]
        if haupt:
            e["fassade"] = hexcol(np.median([[int(p["rgb"][i:i + 2], 16) for i in (1, 3, 5)] for p in haupt], axis=0))
            e["fassade_quelle"] = "Foto (Panoramax): " + "; ".join(p["notiz"] for p in haupt)
        elif slug in osm and osm[slug][1]:
            e["fassade"], e["fassade_quelle"] = osm[slug][1], osm[slug][0]
        else:
            e["fassade"], e["fassade_quelle"] = ANNAHME.get(slug, ("#d0cec8", "Annahme"))
        groups = {}  # gleiche Stelle aus mehreren Fotos zusammenfassen
        for p in mine:
            if p["rolle"] == "akzent":
                groups.setdefault(p["notiz"].split(" (")[0], []).append(p["rgb"])
        e["akzente"] = [dict(rgb=hexcol(np.median([[int(c[i:i + 2], 16) for i in (1, 3, 5)] for c in cs], axis=0)),
                             notiz=k) for k, cs in groups.items()]
        if slug in osm:
            e["osm"] = osm[slug][0]
        farben[slug] = e
    farben["_proben"] = proben
    with open(FARBEN, "w") as f:
        json.dump(farben, f, indent=1, ensure_ascii=False)
    print("Farben ->", os.path.relpath(FARBEN, G.HERE))
    for b in G.BUILDINGS:
        e = farben[b["slug"]]
        print("  %-22s Dach %s  Fassade %s  (%s)" % (b["slug"], e["dach"], e["fassade"], e["fassade_quelle"]))
    swatches(farben, proben)


def swatches(farben, proben):
    """Übersichtsbild: Farbfelder je Gebäude + Foto-Ausschnitte (vorschau/farben.png)."""
    from preview import font, NAMES, OUT, BG
    rows = [b["slug"] for b in G.BUILDINGS]
    W, rh = 1100, 92
    im = Image.new("RGB", (W, 70 + rh * len(rows) + 40), BG)
    d = ImageDraw.Draw(im)
    d.text((16, 14), "Dach- und Fassadenfarben", fill=(30, 30, 30), font=font(28, True))
    for i, slug in enumerate(rows):
        e = farben[slug]
        y = 70 + i * rh
        d.text((16, y + 8), "%s %s" % (slug[:2], NAMES.get(slug[:2], slug)), fill=(30, 30, 30), font=font(18, True))
        q = e["fassade_quelle"]
        d.text((16, y + 34), q if len(q) <= 78 else q[:76] + " …", fill=(90, 90, 90), font=font(13))
        x = 640
        for lab, c in [("Fassade", e["fassade"]), ("Dach", e["dach"])] + [("Akzent", a["rgb"]) for a in e["akzente"]]:
            d.rectangle((x, y + 6, x + 90, y + 60), fill=c, outline=(60, 60, 60))
            d.text((x, y + 64), "%s %s" % (lab, c), fill=(60, 60, 60), font=font(11))
            x += 112
    d.text((16, im.height - 30), "Dach: Luftbild 2024 © Stadt Leipzig (dl-de/by-2-0) · Fassade: Panoramax-Fotos "
           "(CC-BY-SA-4.0, Robot8A) bzw. OSM (ODbL)", fill=(90, 90, 90), font=font(13))
    path = os.path.join(OUT, "farben.png")
    os.makedirs(OUT, exist_ok=True)
    im.save(path, optimize=True)
    print("  Vorschau:", os.path.relpath(path, G.HERE))
    # Foto-Ausschnitte zum Nachprüfen
    tiles = []
    for pid in dict.fromkeys(p["bild"] for p in proben):
        ph, _ = photo(pid)
        ph = ph.copy()
        dr = ImageDraw.Draw(ph)
        for p in [p for p in proben if p["bild"] == pid]:
            b = p["box"]
            box = (b[0] * ph.width, b[1] * ph.height, b[2] * ph.width, b[3] * ph.height)
            dr.rectangle(box, outline=(255, 0, 255), width=6)
            dr.rectangle((box[0], box[3] + 4, box[0] + 46, box[3] + 50), fill=p["rgb"], outline=(255, 0, 255))
            dr.text((box[0] + 4, box[1] + 6), p["gebaeude"][:2], fill=(255, 0, 255), font=font(40, True))
        wb = json.load(open(PROBEN)).get("weissabgleich", {}).get(pid)
        if wb:
            b = wb["box"]
            dr.rectangle((b[0] * ph.width, b[1] * ph.height, b[2] * ph.width, b[3] * ph.height),
                         outline=(0, 230, 255), width=6)
            dr.text((b[0] * ph.width + 6, b[1] * ph.height + 6), "Weißabgleich", fill=(0, 230, 255), font=font(34, True))
        ph.thumbnail((900, 700))
        tiles.append(ph)
    sheet = Image.new("RGB", (sum(t.width for t in tiles), max(t.height for t in tiles) + 34), BG)
    x = 0
    for t in tiles:
        sheet.paste(t, (x, 0))
        x += t.width
    ImageDraw.Draw(sheet).text((10, sheet.height - 26), "Foto: Robot8A via Panoramax, CC-BY-SA-4.0 – "
                               "Messfelder (magenta, Feld darunter = gemessene Farbe) und Weißabgleich-Referenz (cyan)", fill=(60, 60, 60), font=font(15))
    path = os.path.join(OUT, "farben_fotoproben.jpg")
    sheet.save(path, quality=85)
    print("  Vorschau:", os.path.relpath(path, G.HERE))


if __name__ == "__main__":
    main()
