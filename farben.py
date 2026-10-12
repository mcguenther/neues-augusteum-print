#!/usr/bin/env python3
"""Bestimmt Dach- und Fassadenfarben der Gebäude aus offenen Bilddaten.

- Dachfarbe: Median der Luftbild-Pixel (Stadt Leipzig, Luftbild 2024, 20 cm,
  WMTS, dl-de/by-2-0) innerhalb des Gebäudegrundrisses, je Gebäude und zusätzlich
  als Raster für die farbige Vorschau (jede Dachfläche bekommt ihre Farbe).
  Das GeoSN-DOP 2025 (März) wäre auch frei verfügbar, hat aber lange
  Schlagschatten des Uniriesen über dem Campus; das Leipziger Luftbild ist
  sommerlicher und deutlich schattenärmer.
- Fassadenfarbe: Median über Bildausschnitte aus offen lizenzierten Straßenfotos
  (Panoramax, Wikimedia Commons inkl. 360°-Panoramen), definiert in
  data/fassaden_proben.json, mit Weißabgleich am Pflaster. Ohne Foto: OSM-Tags
  building:colour / building:material, sonst eine als Annahme markierte Farbe.

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


PLATTE = "#e4e0d8"  # Sockelplatte / Grundplatte


FILAMENT_TOLERANZ = 16  # RGB-Abstand, unter dem zwei Farben ein Filament teilen


def filamente(farben):
    """Globale Filament-Palette: Liste [(hex, [Verwendungen])], Filament-Nr. = Index + 1.

    Reihenfolge: Platte, dann je Gebäude Fassade und Dach. Sehr ähnliche Farben
    (RGB-Abstand < FILAMENT_TOLERANZ) teilen sich ein Filament – im Druck ist der
    Unterschied ohnehin nicht sichtbar. PrusaSlicer erlaubt höchstens 15 Filamente.
    """
    pal = [(PLATTE.lower(), ["Platte"])]
    for b in G.BUILDINGS:
        e = farben.get(b["slug"])
        if not e:
            continue
        for rolle, c in (("Fassade", e["fassade"]), ("Dach", e.get("dach") or e["fassade"])):
            use = "%s %s" % (b["slug"][:2], rolle)
            for pc, uses in pal:
                if np.linalg.norm(rgb255(pc) - rgb255(c)) < FILAMENT_TOLERANZ:
                    uses.append(use)
                    break
            else:
                pal.append((c.lower(), [use]))
    if len(pal) > 15:
        print("  Warnung: %d Filamentfarben > 15 (Grenze PrusaSlicer)" % len(pal))
    return pal


def filament_nr(farben, colour):
    """Filament-Nummer (1-basiert) einer Gebäudefarbe in der Palette."""
    for i, (pc, _) in enumerate(filamente(farben)):
        if np.linalg.norm(rgb255(pc) - rgb255(colour)) < FILAMENT_TOLERANZ:
            return i + 1
    raise KeyError(colour)


def rgb255(c):
    return np.array([int(c[i:i + 2], 16) for i in (1, 3, 5)], float)


def hexcol(rgb):
    return "#%02x%02x%02x" % tuple(int(round(v)) for v in rgb)


def fetch(url, path):
    """Lädt url nach path (Cache). Wikimedia drosselt geteilte IPs: mit Wartezeit wiederholen."""
    import time
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        req = urllib.request.Request(url, headers={
            "User-Agent": "neues-augusteum-print/1.0 (3D-Druckmodelle Campus Augustusplatz)"})
        for k in range(6):
            try:
                with urllib.request.urlopen(req, timeout=180) as r:
                    data = r.read()
                break
            except OSError as e:
                if k == 5:
                    raise
                wait = int(getattr(e, "headers", None) and e.headers.get("Retry-After") or 0) or 5 * (k + 1)
                time.sleep(min(wait, 60))
        with open(path, "wb") as f:
            f.write(data)
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
def persp(img, yaw, pitch=0.0, hfov=65.0, W=1600, H=1000):
    """Perspektivische Ansicht aus einem 360°-Panorama (equirektangular)."""
    from scipy.ndimage import map_coordinates
    A = np.asarray(img)
    h, w = A.shape[:2]
    f = (W / 2) / np.tan(np.radians(hfov / 2))
    X, Y = np.meshgrid(np.arange(W) - W / 2 + 0.5, np.arange(H) - H / 2 + 0.5)
    Z = np.full_like(X, f)
    p = np.radians(pitch)
    Yr, Zr = Y * np.cos(p) - Z * np.sin(p), Y * np.sin(p) + Z * np.cos(p)
    lon = np.arctan2(X, Zr) + np.radians(yaw)
    lat = np.arctan2(-Yr, np.hypot(X, Zr))
    u = ((lon / (2 * np.pi)) + 0.5) % 1 * w
    v = (0.5 - lat / np.pi) * h
    out = np.stack([map_coordinates(A[..., c], [v - 0.5, u - 0.5], order=1, mode="wrap") for c in range(3)], -1)
    return Image.fromarray(out.astype(np.uint8))


def photo(pid):
    """Foto (PIL) und Metadaten {datum, lizenz, urheber, url} – Panoramax-ID oder Eintrag in „bilder“."""
    bilder = json.load(open(PROBEN)).get("bilder", {})
    if pid in bilder:
        b = bilder[pid]
        path = fetch(b["url"], os.path.join(CACHE, "commons", pid + ".jpg"))
        im = Image.open(path).convert("RGB")
        if b.get("ansicht"):
            im = persp(im, **b["ansicht"])
        return im, dict(datum=b["datum"], lizenz=b["lizenz"], urheber=b["urheber"], url=b["seite"])
    meta_path = os.path.join(CACHE, "panoramax", pid + ".json")
    fetch(PANORAMAX.format(pid), meta_path)
    meta = json.load(open(meta_path))
    path = fetch(meta["assets"]["sd"]["href"], os.path.join(CACHE, "panoramax", pid + ".jpg"))
    pr = meta["properties"]
    return Image.open(path).convert("RGB"), dict(
        datum=pr["datetime"][:10], lizenz=pr.get("license"), urheber=pr.get("geovisio:producer"),
        url="https://api.panoramax.xyz/#focus=pic&pic=%s" % pid)


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
        res.append(dict(p, rgb=hexcol(rgb), roh=hexcol(box_median(im, p["box"])), **meta))
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
        "fassade_foto": "Straßenfotos (Panoramax, Wikimedia Commons; Lizenzen je Probe), Ausschnitte in "
                        "data/fassaden_proben.json",
        "fassade_osm": "OpenStreetMap building:colour / building:material (ODbL)"}}
    for b in G.BUILDINGS:
        slug = b["slug"]
        e = dict(name=b["name"], dach=dach[slug]["rgb"] if slug in dach else None)
        mine = [p for p in proben if p["gebaeude"] == slug]
        haupt = [p for p in mine if p["rolle"] == "haupt"]
        if haupt:
            e["fassade"] = hexcol(np.median([[int(p["rgb"][i:i + 2], 16) for i in (1, 3, 5)] for p in haupt], axis=0))
            notizen = list(dict.fromkeys(p["notiz"].split(" (")[0] for p in haupt))
            e["fassade_quelle"] = "Foto (%d Messfeld%s): %s" % (len(haupt), "er" if len(haupt) > 1 else "",
                                                               "; ".join(notizen))
        elif slug in osm and osm[slug][1]:
            e["fassade"], e["fassade_quelle"] = osm[slug][1], osm[slug][0]
        else:
            e["fassade"], e["fassade_quelle"] = "#d0cec8", "Annahme (kein Foto, keine OSM-Angabe)"
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
    farben["_filamente"] = [dict(nr=i + 1, rgb=c, fuer=u) for i, (c, u) in enumerate(filamente(farben))]
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
    pal = filamente(farben)
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
            nr = filament_nr(farben, c) if lab != "Akzent" else None
            if nr:
                hell = sum(int(c[i:i + 2], 16) for i in (1, 3, 5)) > 380
                d.text((x + 6, y + 10), "F%d" % nr, fill=(20, 20, 20) if hell else (240, 240, 240), font=font(16, True))
            d.text((x, y + 64), "%s %s" % (lab, c), fill=(60, 60, 60), font=font(11))
            x += 112
    d.text((16, im.height - 30), "Dach: Luftbild 2024 © Stadt Leipzig (dl-de/by-2-0) · Fassade: Fotos (Panoramax, "
           "Commons) bzw. OSM · F1–F%d = Filament-Nr. in den 3MF-Dateien (F1 = Platte)"
           % len(pal), fill=(90, 90, 90), font=font(13))
    path = os.path.join(OUT, "farben.png")
    os.makedirs(OUT, exist_ok=True)
    im.save(path, optimize=True)
    print("  Vorschau:", os.path.relpath(path, G.HERE))
    # Foto-Ausschnitte zum Nachprüfen, mit Urheber und Lizenz je Foto
    wbs = json.load(open(PROBEN)).get("weissabgleich", {})
    tiles = []
    for pid in dict.fromkeys(p["bild"] for p in proben):
        ph, meta = photo(pid)
        ph = ph.copy()
        k = ph.width / 1600
        dr = ImageDraw.Draw(ph)
        for p in [p for p in proben if p["bild"] == pid]:
            b = p["box"]
            box = (b[0] * ph.width, b[1] * ph.height, b[2] * ph.width, b[3] * ph.height)
            dr.rectangle(box, outline=(255, 0, 255), width=max(2, int(5 * k)))
            s_ = int(40 * k)
            dr.rectangle((box[0], box[3] + 4, box[0] + s_, box[3] + 4 + s_), fill=p["rgb"], outline=(255, 0, 255))
            dr.text((box[0] + 4, box[1] + 4), p["gebaeude"][:2], fill=(255, 0, 255), font=font(int(34 * k), True))
        if pid in wbs:
            b = wbs[pid]["box"]
            dr.rectangle((b[0] * ph.width, b[1] * ph.height, b[2] * ph.width, b[3] * ph.height),
                         outline=(0, 230, 255), width=max(2, int(5 * k)))
        ph.thumbnail((620, 470))
        t = Image.new("RGB", (640, 520), BG)
        t.paste(ph, ((640 - ph.width) // 2, 0))
        ImageDraw.Draw(t).text((10, 478), "%s · %s · %s" % (meta["urheber"], meta["lizenz"], meta["datum"]),
                               fill=(60, 60, 60), font=font(14))
        tiles.append(t)
    cols = 3
    rows_ = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 640, rows_ * 520 + 40), BG)
    for i, t in enumerate(tiles):
        sheet.paste(t, ((i % cols) * 640, (i // cols) * 520))
    ImageDraw.Draw(sheet).text((10, sheet.height - 30), "Messfelder (magenta, Feld darunter = gemessene Farbe nach "
                               "Weißabgleich), Weißabgleich-Referenz (cyan). Fotos: Panoramax / Wikimedia Commons, "
                               "Lizenzen siehe Bildunterschrift.", fill=(60, 60, 60), font=font(15))
    path = os.path.join(OUT, "farben_fotoproben.jpg")
    sheet.save(path, quality=85)
    print("  Vorschau:", os.path.relpath(path, G.HERE))


if __name__ == "__main__":
    main()
