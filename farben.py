#!/usr/bin/env python3
"""Bestimmt Dach- und Fassadenfarben der Gebäude aus offenen Bilddaten.

- Dachfarbe: Median der Luftbild-Pixel (Stadt Leipzig, Luftbild 2024, 20 cm,
  WMTS, dl-de/by-2-0) innerhalb des Gebäudegrundrisses, je Gebäude und zusätzlich
  als Raster für die farbige Vorschau (jede Dachfläche bekommt ihre Farbe).
  Das GeoSN-DOP 2025 (März) wäre auch frei verfügbar, hat aber lange
  Schlagschatten des Uniriesen über dem Campus; das Leipziger Luftbild ist
  sommerlicher und deutlich schattenärmer.
- Dachpalette: wenige typische Dachfarben (k-means über alle Dachpixel); jede
  Dachfläche bekommt die Klasse, die das Luftbild an ihr zeigt (fassaden.py).
- Fassadenfarben: je Gebäude mehrere benannte Farben (Platten, Sockel, Glas,
  Bänder ...) in data/fassaden/<slug>.json, jede gemessen als Median über
  Bildausschnitte aus offen lizenzierten Straßenfotos (Fotokatalog
  data/fotos.json: Panoramax, Wikimedia Commons inkl. 360°-Panoramen), mit
  Weißabgleich am Pflaster. Wo die Farben auf der Fassade liegen, beschreiben
  die Zonen in derselben Datei (siehe fassaden.py).

Ergebnis: data/farben.json (wird von generate.py für die farbigen 3MF-Dateien und
Vorschauen benutzt). Bilder werden nur in data/cache/ zwischengespeichert.

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
FOTOS = os.path.join(G.HERE, "data", "fotos.json")
FARBEN = os.path.join(G.HERE, "data", "farben.json")
DOP_FILE = os.path.join(G.HERE, "data", "luftbild2024_campus.jpg")  # Ausschnitt, © Stadt Leipzig
WMTS = ("https://geodienste.leipzig.de/l1/Rasterdaten/luftbild_2024/MapServer/WMTS/tile/1.0.0/"
        "Rasterdaten_luftbild_2024/default/default028mm/{z}/{row}/{col}")
WMTS_LEVEL = 9                                   # 944,94 · 0,28 mm = 0,265 m/Pixel
WMTS_RES = 944.9423660750896 * 0.00028
WMTS_ORIGIN = (-5120900.0, 9998100.0)            # TopLeftCorner der TileMatrixSet
PANORAMAX = "https://api.panoramax.xyz/api/pictures/{}"
REF_GRAU = 150.0  # angenommener Grauwert (0..255) des Granitpflasters für Weißabgleich/Belichtung


PLATTE = "#e4e0d8"  # Sockelplatte / Grundplatte


FILAMENT_TOLERANZ = 16  # RGB-Abstand, unter dem zwei Farben ein Filament teilen
MAX_FILAMENTE = 15      # Grenze PrusaSlicer (Bambu/Orca: 32)


def used_colours(farben):
    """Alle verwendeten Farben mit Verwendungszweck: [(hex, text)]."""
    out = [(PLATTE, "Platte")]
    for b in G.OBJEKTE:
        e = farben.get(b["slug"])
        if not e:
            continue
        keys = [e["basis"]] + [z["farbe"] for z in e.get("zonen", [])]
        for k in dict.fromkeys(keys):
            out.append((e["farben"][k]["rgb"], "%s %s" % (b["slug"][:2], k)))
    for c in farben.get("_dachpalette", []):
        out.append((c["rgb"], "Dach %s" % c["name"]))
    return out


def filamente(farben):
    """Globale Filament-Palette [(hex, [Verwendungen])], Filament-Nr. = Index + 1.

    Ähnliche Farben werden zusammengelegt (das ähnlichste Paar zuerst), bis alle
    Paare mindestens FILAMENT_TOLERANZ auseinander liegen und höchstens
    MAX_FILAMENTE übrig sind. Die Platte bleibt Filament 1.
    """
    groups = []
    for c, use in used_colours(farben):
        for g in groups:
            if g[0].lower() == c.lower():
                g[1].append(use)
                break
        else:
            groups.append([c.lower(), [use], [rgb255(c)]])
    while len(groups) > 1:
        best = None
        for i in range(len(groups)):
            for j in range(i + 1, len(groups)):
                d = np.linalg.norm(np.mean(groups[i][2], 0) - np.mean(groups[j][2], 0))
                if best is None or d < best[0]:
                    best = (d, i, j)
        d, i, j = best
        if d >= FILAMENT_TOLERANZ and len(groups) <= MAX_FILAMENTE:
            break
        gi, gj = groups[i], groups.pop(j)
        gi[1] += gj[1]
        gi[2] += gj[2]
        if i != 0:  # Platte behält ihre Farbe
            gi[0] = hexcol(np.mean(gi[2], 0))
    return [(g[0], g[1]) for g in groups]


def filament_nr(farben, colour):
    """Filament-Nummer (1-basiert): nächstgelegene Farbe der Palette in data/farben.json."""
    pal = np.array([rgb255(f["rgb"]) for f in farben["_filamente"]])
    return int(np.argmin(np.linalg.norm(pal - rgb255(colour), axis=1))) + 1


def rgb255(c):
    return np.array([int(c[i:i + 2], 16) for i in (1, 3, 5)], float)


def hexcol(rgb):
    return "#%02x%02x%02x" % tuple(int(round(v)) for v in rgb)


# --------------------------------------------------------------------------
# Filamente des Nutzers und Profile für wenige Filamente (generate.py --filamente 3|4, plug.colour)
# --------------------------------------------------------------------------
# Vorhandenes PLA (Stand 2026-10-19): vier Hauptfarben und drei Reserven; der Drucker kann 4 Filamente in einem Druck.
# Die Hex-Werte sind Schätzungen nach den Farbnamen (die Spulen sind nicht gemessen); hier anpassen, wenn Farbmuster
# vorliegen. Die Rollen beschreiben, wofür die Farbe gedacht ist (Beige = Stein, Platten, Platte; Graublau = Glas, Fenster;
# Weinrot = Brüstungsbänder, rote Dächer, Ziegel; Space Grey = Sockel, dunkle Bänder, Lamellen).
FILAMENTE = [("#e6d6bc", "Beige"), ("#6b7d8c", "Graublau"), ("#7b2433", "Weinrot"), ("#4a4e54", "Space Grey"),
             ("#f3f3f0", "Weiß"), ("#1f2022", "Schwarz"), ("#4f9a3c", "Grasgrün")]
HAUPT = FILAMENTE[:4]          # die vier Hauptfarben
RESERVE = FILAMENTE[4:]        # Weiß, Schwarz, Grasgrün: nur, wenn sie ein Gebäude deutlich besser treffen
GLEICHZEITIG = 4               # Filamente je Druck
RESERVE_KOSTEN = 4.0           # Aufschlag je Reservefarbe in der Auswahl (ΔE, flächengewichtet): Hauptfarben bevorzugt
PROFILE = {
    3: [FILAMENTE[0], FILAMENTE[1], FILAMENTE[3]],
    4: HAUPT,
}
# Fenster und Glas (Gebäude-Nr. + Farbname in data/fassaden/*.json) bleiben Graublau, auch wenn eine helle Farbe näher
# läge – sonst verschwinden das Maßwerkfenster und die Rosette.
PROFIL_FENSTER = ("01 fensterglas", "01 rosette_innen", "06 fassade")
# Feste Rollen: diese Verwendungen bekommen die genannte Farbe, wenn sie im Satz ist (sonst die nächste).
PROFIL_ROLLEN = {"Dach rot": "Weinrot", "08 krone": "Grasgrün", "08 beet": "Grasgrün"}
# Nur hier darf ein Dach Graublau sein. Bei den übrigen Gebäuden sind blaugraue Dachflächen im
# Luftbild vor allem Schatten und werden hell.
PROFIL_DACH_BLAU = ("01_paulinum", "02_neues_augusteum", "06_city_hochhaus")
PROFIL_ROOF_NZ = 0.35   # wie fassaden.ROOF_NZ


def palette(profil):
    """Profil (3, 4 oder eine Liste [(hex, name)]) als Liste [(hex, name)]."""
    return PROFILE[profil] if isinstance(profil, int) else list(profil)


def profil_filamente(profil):
    """Filament-Liste des Profils im Format von data/farben.json (_filamente)."""
    return [{"nr": i + 1, "rgb": c, "fuer": [name]} for i, (c, name) in enumerate(palette(profil))]


def _lab(c):
    v = rgb255(c) / 255
    v = np.where(v <= 0.04045, v / 12.92, ((v + 0.055) / 1.055) ** 2.4)
    xyz = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]]) @ v
    xyz /= np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 216 / 24389, np.cbrt(xyz), (24389 / 27 * xyz + 16) / 116)
    return np.array([116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2])])


def _namen(eintrag, farben=None):
    """Hex -> Verwendung („01 glas“, „Dach rot“) für die Regeln."""
    out = {}
    for c in (farben or {}).get("_dachpalette", []):
        out[c["rgb"].lower()] = "Dach %s" % c["name"]
    if eintrag:
        out.update({v["rgb"].lower(): k for k, v in eintrag["farben"].items()})
    return out


def _ziel(slug, use, h, roof, pal, labs):
    """Index der Profilfarbe für eine Farbe h (Regeln wie in reduziere)."""
    names = [n for _, n in pal]
    key = "%s %s" % (slug[:2], use) if slug and not use.startswith("Dach") else use
    if key in PROFIL_FENSTER and "Graublau" in names:
        t = names.index("Graublau")
    elif PROFIL_ROLLEN.get(key) in names:
        t = names.index(PROFIL_ROLLEN[key])
    else:
        lab = _lab(h)
        t = int(np.argmin([np.linalg.norm(lab - l) for l in labs]))
    if roof and names[t] == "Graublau" and slug not in PROFIL_DACH_BLAU:
        t = int(np.argmax([l[0] for l in labs]))    # hellste Farbe des Satzes
    return t


def reduziere(slug, eintrag, mesh, hexes, profil, farben=None):
    """Bildet die Farben eines Gebäudes (Hex je Dreieck) auf ein Profil ab.

    slug     Gebäude (None = Platte), eintrag dessen Eintrag in data/farben.json
    mesh     Netz mit den Dreiecken zu hexes (für die Dachflächen)
    profil   3, 4 oder Liste [(hex, name)] (z. B. aus waehle_filamente)
    Regeln: nächste Profilfarbe (CIE-Lab), Fenster/Glas immer Graublau (PROFIL_FENSTER), feste Rollen
    (PROFIL_ROLLEN: rote Dächer Weinrot, Baumkronen Grasgrün), Dächer außer bei PROFIL_DACH_BLAU nie Graublau
    (dann die hellste Farbe).
    """
    pal = palette(profil)
    labs = [_lab(c) for c, _ in pal]
    name_of = _namen(eintrag, farben)
    roof = mesh.face_normals[:, 2] > PROFIL_ROOF_NZ
    cache = {}
    out = np.empty(len(hexes), dtype=object)
    for i, (h, r) in enumerate(zip(hexes, roof)):
        t = cache.get((h, r))
        if t is None:
            t = cache[(h, r)] = _ziel(slug, name_of.get(h.lower(), ""), h, r, pal, labs)
        out[i] = pal[t][0]
    return out


def waehle_filamente(teile, farben, n=GLEICHZEITIG, pflicht=()):
    """Die n Filamente aus FILAMENTE, die die Fassadenfarben am besten treffen.

    teile    [(slug, mesh, hexes, gewicht je Dreieck oder None)] – alles, was in einem Druck liegt
    pflicht  Namen, die immer im Satz sind
    Kosten: flächengewichteter ΔE (CIE-Lab) zwischen Fassadenfarbe und zugeordneter Filamentfarbe (nach den Regeln von
    reduziere) plus RESERVE_KOSTEN je Reservefarbe. Liefert (Satz [(hex, name)] in der Reihenfolge von FILAMENTE, Kosten).
    """
    import itertools
    # Flächen je (slug, hex, dach) einmal sammeln
    posten = {}
    for slug, mesh, hexes, w in teile:
        area = mesh.area_faces if w is None else mesh.area_faces * w
        roof = mesh.face_normals[:, 2] > PROFIL_ROOF_NZ
        name_of = _namen(farben.get(slug) if slug else None, farben)
        for h, r, a in zip(hexes, roof, area):
            k = (slug, h, bool(r))
            if k not in posten:
                posten[k] = [name_of.get(h.lower(), ""), 0.0]
            posten[k][1] += a
    total = sum(a for _, a in posten.values()) or 1.0
    best = None
    for satz in itertools.combinations(FILAMENTE, n):
        names = [nm for _, nm in satz]
        if any(p not in names for p in pflicht):
            continue
        labs = [_lab(c) for c, _ in satz]
        cost = sum(a * np.linalg.norm(_lab(h) - labs[_ziel(slug, use, h, r, satz, labs)])
                   for (slug, h, r), (use, a) in posten.items()) / total
        cost += RESERVE_KOSTEN * sum(1 for s in satz if s in RESERVE)
        if best is None or cost < best[1]:
            best = (list(satz), cost)
    return best


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


def dop_probe(p):
    """Farbe einer Fläche im Luftbild: Median der beleuchteten Pixel (ohne die dunkelsten 35 %,
    also weitgehend ohne Schlagschatten). p = {"polygon": [[x, y], ...]} lokal in m oder eine
    benannte Fläche des Innenhofs ({"objekt": "beet"}, {"flaeche": "rand"}, siehe innenhof.py)."""
    import innenhof
    poly = innenhof.probe_polygon(p)
    img, (x0, y0, x1, y1) = load_dop()
    to_utm = lambda a: np.column_stack(lod2.local_to_utm(a[:, 0], a[:, 1]))
    poly = shapely.transform(poly, to_utm)
    minx, miny, maxx, maxy = poly.bounds
    c0, c1 = int((minx - x0) / WMTS_RES), int((maxx - x0) / WMTS_RES) + 1
    r0, r1 = int((y1 - maxy) / WMTS_RES), int((y1 - miny) / WMTS_RES) + 1
    X, Y = np.meshgrid(x0 + (np.arange(c0, c1) + 0.5) * WMTS_RES, y1 - (np.arange(r0, r1) + 0.5) * WMTS_RES)
    px = img[r0:r1, c0:c1][shapely.contains_xy(poly, X, Y)].astype(float)
    lum = px @ [0.299, 0.587, 0.114]
    lit = px[lum >= np.percentile(lum, 35)]
    return dict(p, rgb=hexcol(np.median(lit, axis=0)), pixel=int(len(px)))


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


def fotos(extra=None):
    """Fotokatalog (data/fotos.json), ergänzt um Einträge einer Gebäudedatei."""
    f = json.load(open(FOTOS))
    if extra:
        f["bilder"].update(extra.get("bilder", {}))
        f["weissabgleich"].update(extra.get("weissabgleich", {}))
    return f


def photo(pid, katalog=None):
    """Foto (PIL) und Metadaten {datum, lizenz, urheber, url}."""
    b = (katalog or fotos())["bilder"].get(pid, {})
    if "url" in b:
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


_PHOTOS = {}


def photo_cached(pid, katalog):
    if pid not in _PHOTOS:
        _PHOTOS[pid] = photo(pid, katalog)
    return _PHOTOS[pid]


def box_median(im, b):
    W, H = im.size
    crop = np.asarray(im.crop((int(b[0] * W), int(b[1] * H), int(b[2] * W), int(b[3] * H))), float)
    return np.median(crop.reshape(-1, 3), axis=0)


def measure_probe(p, katalog):
    """Farbe eines Messfelds, weißabgeglichen am grauen Pflaster desselben Fotos."""
    im, meta = photo_cached(p["bild"], katalog)
    roh = box_median(im, p["box"])
    rgb = roh
    wb = katalog["weissabgleich"].get(p["bild"])
    if wb:
        # Weißabgleich + Belichtung: Pflaster -> neutrales Granitgrau (Annahme REF_GRAU)
        rgb = np.clip(roh * REF_GRAU / box_median(im, wb["box"]), 0, 255)
    return dict(p, rgb=hexcol(rgb), roh=hexcol(roh), **meta)


MESSUNG = os.path.join(G.HERE, "data", "messung.json")


def messung(slug):
    """Eintrag des Gebäudes aus data/messung.json (farbmessung.py) oder None."""
    if not os.path.exists(MESSUNG):
        return None
    return json.load(open(MESSUNG)).get("gebaeude", {}).get(slug)


def building_colours(slug):
    """Gemessene Farben, Basis und Zonen eines Gebäudes aus data/fassaden/<slug>.json."""
    import fassaden
    spec = fassaden.load_spec(slug)
    if spec is None:
        return None
    m = messung(slug)
    if m:       # Ergebnis der Fotoprojektion (farbmessung.py): Farben und Zonen ersetzen die Handwerte
        spec = dict(spec, farben=m["farben"], zonen=m["zonen"])
    katalog = fotos(spec)
    out = dict(basis=spec["basis"], zonen=spec.get("zonen", []), farben={})
    for k, f in spec["farben"].items():
        if "hex" in f:
            out["farben"][k] = dict(rgb=f["hex"].lower(), notiz=f.get("notiz", ""), quelle=f.get("quelle", "fest"))
            continue
        proben = [measure_probe(p, katalog) for p in f.get("proben", [])]
        luft = [dop_probe(p) for p in f.get("luftbild", [])]
        rgb = hexcol(np.median([rgb255(p["rgb"]) for p in proben + luft], axis=0))
        quelle = []
        if proben:
            quelle.append("Foto (%d Messfeld%s)" % (len(proben), "er" if len(proben) > 1 else ""))
        if luft:
            quelle.append("Luftbild 2024 (%d Fläche%s)" % (len(luft), "n" if len(luft) > 1 else ""))
        out["farben"][k] = dict(rgb=rgb, notiz=f.get("notiz", ""), quelle=" + ".join(quelle), proben=proben,
                                luftbild=luft)
    return out


def building_probes(slug):
    e = building_colours(slug)
    return [dict(p, gebaeude=slug, farbe=k) for k, f in e["farben"].items() for p in f.get("proben", [])]


# --------------------------------------------------------------------------
# Dächer
# --------------------------------------------------------------------------
DACH_KLASSEN = 6


def roof_pixels(img, bounds, cells):
    x0, y0, x1, y1 = bounds
    H, W, _ = img.shape
    X, Y = np.meshgrid((np.arange(W) + 0.5) * WMTS_RES + x0, y1 - (np.arange(H) + 0.5) * WMTS_RES)
    to_utm = lambda a: np.column_stack(lod2.local_to_utm(a[:, 0], a[:, 1]))
    out = []
    for cell in cells.values():
        poly = shapely.transform(cell, to_utm).buffer(-0.5)
        out.append(img[shapely.contains_xy(poly, X, Y)])
    return np.vstack(out).astype(float)


def kmeans(px, k, it=30, seed=1):
    rng = np.random.default_rng(seed)
    c = px[rng.choice(len(px), k, replace=False)]
    for _ in range(it):
        lab = np.argmin(((px[:, None, :] - c[None]) ** 2).sum(-1), axis=1)
        c = np.array([px[lab == i].mean(0) if (lab == i).any() else c[i] for i in range(k)])
    return c, np.bincount(lab, minlength=k) / len(px)


def colour_name(rgb):
    r, g, b = rgb
    if r > g + 25 and r > b + 25:
        return "rot"
    if g > r + 8 and g > b + 5:
        return "grün"
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    return "hell" if lum > 165 else ("dunkel" if lum < 95 else "grau")


def roof_palette(img, bounds, cells):
    px = roof_pixels(img, bounds, cells)
    px = px[::max(1, len(px) // 60000)]
    c, share = kmeans(px, DACH_KLASSEN)
    order = np.argsort(-share)
    return [dict(rgb=hexcol(c[i]), anteil=round(float(share[i]), 3), name=colour_name(c[i])) for i in order]


def roof_classifier(farben=None):
    """Funktion (Dreiecke[n,3,2] lokal in m) -> Hex-Farbe der Dachpalette je Dreieck.

    Je Dreieck werden 7 Punkte im Luftbild abgefragt (Schwerpunkt + 6 innere
    Punkte); es gewinnt die häufigste Klasse.
    """
    farben = farben or load_farben()
    pal = np.array([rgb255(c["rgb"]) / 255 for c in farben["_dachpalette"]])
    hexes = np.array([c["rgb"] for c in farben["_dachpalette"]], dtype=object)
    sample = dop_sampler()
    w = np.array([[1, 1, 1], [4, 1, 1], [1, 4, 1], [1, 1, 4], [2, 2, 1], [2, 1, 2], [1, 2, 2]], float)
    w /= w.sum(1, keepdims=True)

    def classify(tris):
        tris = np.asarray(tris, float)
        if len(tris) == 0:
            return np.array([], dtype=object)
        pts = np.einsum("kj,njd->nkd", w, tris).reshape(-1, 2)
        col = sample(pts[:, 0], pts[:, 1])
        lab = np.argmin(((col[:, None, :] - pal[None]) ** 2).sum(-1), axis=1).reshape(len(tris), -1)
        best = np.array([np.bincount(r, minlength=len(pal)).argmax() for r in lab])
        return hexes[best]
    return classify


# --------------------------------------------------------------------------
# Gesamtlauf
# --------------------------------------------------------------------------
def main():
    img, bounds = load_dop()
    cells = {k: v[1] for k, v in lod2.models(1.0).items()}  # Grundrisse (bei s = 1 in m)
    dach = roof_colours(img, bounds, cells)
    farben = {"_quellen": {
        "dach": "Stadt Leipzig, Luftbild 2024 (20 cm, WMTS), dl-de/by-2-0",
        "fassade": "Straßenfotos (Panoramax, Wikimedia Commons; Lizenzen je Messfeld), Messfelder und Zonen in "
                   "data/fassaden/<slug>.json, Fotokatalog data/fotos.json"}}
    farben["_dachpalette"] = roof_palette(img, bounds, cells)
    for b in G.OBJEKTE:
        e = building_colours(b["slug"])
        if e is None:
            continue
        e = dict(name=b["name"], dach=dach[b["slug"]]["rgb"] if b["slug"] in dach else None, **e)
        e["fassade"] = e["farben"][e["basis"]]["rgb"]
        farben[b["slug"]] = e
    farben["_filamente"] = [dict(nr=i + 1, rgb=c, fuer=u) for i, (c, u) in enumerate(filamente(farben))]
    if len(farben["_filamente"]) > MAX_FILAMENTE:
        print("  Warnung: %d Filamente > %d" % (len(farben["_filamente"]), MAX_FILAMENTE))
    with open(FARBEN, "w") as f:
        json.dump(farben, f, indent=1, ensure_ascii=False)
    print("Farben ->", os.path.relpath(FARBEN, G.HERE))
    for b in G.OBJEKTE:
        e = farben.get(b["slug"])
        if e:
            print("  %-22s %s" % (b["slug"], ", ".join("%s %s" % (k, v["rgb"]) for k, v in e["farben"].items())))
    print("  Dachpalette:", ", ".join("%s %s (%.0f %%)" % (c["name"], c["rgb"], 100 * c["anteil"])
                                     for c in farben["_dachpalette"]))
    print("  Filamente: %d" % len(farben["_filamente"]))
    swatches(farben)
    proben = [p for b in G.OBJEKTE if b["slug"] in farben
              for k, f in farben[b["slug"]]["farben"].items()
              for p in [dict(q, gebaeude=b["slug"], farbe=k) for q in f.get("proben", [])]]
    if proben:
        probe_sheet(proben, os.path.join(G.HERE, "vorschau", "farben_fotoproben.jpg"))
    write_sources()


QUELLEN_MD = os.path.join(G.HERE, "FOTOQUELLEN.md")


def write_sources(_proben=None):
    """FOTOQUELLEN.md: alle verwendeten Fotos mit Urheber, Lizenz und Verwendung.

    1. Fotoprojektion (farbmessung.py, data/messung.json): die Fotos, aus denen die Fassadenfarben
       neu bestimmt wurden (Katalog data/messfotos.json).
    2. Handmessung (Altbestand): Fotos, aus denen die übrigen, unverändert übernommenen Farben stammen
       (data/fassaden/*.json, Feld proben_alt)."""
    import fassaden
    lines = ["# Fotoquellen der Fassadenfarben", "",
             "Automatisch erzeugt von `farben.py`. Die Vorschaubilder mit Fotoausschnitten stehen unter der Lizenz",
             "des jeweiligen Fotos (CC BY / CC BY-SA: Namensnennung, bei BY-SA Weitergabe unter gleichen Bedingungen).", ""]
    mess = json.load(open(MESSUNG)) if os.path.exists(MESSUNG) else None
    n1 = 0
    if mess:
        kat = json.load(open(os.path.join(G.HERE, "data", "messfotos.json")))["fotos"]
        lines += ["## Fotoprojektion (Farbmessung am 3D-Modell)", "",
                  "Das Modell wurde in jedes dieser Fotos projiziert (`kamera.py`, `registrierung.py`), die Pixel sind so",
                  "den Wandflächen zugeordnet (`farbmessung.py`). Pose, Aufnahmezeit und Belichtung je Foto: `data/messfotos.json`,",
                  "`data/messung.json`.", "",
                  "| Foto | Urheber | Lizenz | Datum | Quelle |", "|---|---|---|---|---|"]
        for fid, info in mess["fotos"].items():
            e = kat[fid]
            lines.append("| [%s](%s) | %s | %s | %s | %s |" % (fid, e["seite"], e["urheber"], e["lizenz"], (e.get("zeit") or e.get("datum", ""))[:10],
                                                                e["quelle"]))
            n1 += 1
        lines.append("")
    alt = {}
    for b in G.OBJEKTE:
        spec = fassaden.load_spec(b["slug"])
        if not spec:
            continue
        katalog = {**json.load(open(FOTOS))["bilder"], **spec.get("bilder_alt", spec.get("bilder", {}))}
        for k, fa in spec["farben"].items():
            for p in fa.get("proben_alt", fa.get("proben", [])):
                e = katalog.get(p["bild"])
                if e and "seite" in e:
                    alt.setdefault(p["bild"], dict(e, verwendung=set()))["verwendung"].add("%s %s" % (b["slug"][:2], k))
    if alt:
        lines += ["## Handmessung (Altbestand, für nicht neu gemessene Farben übernommen)", "",
                  "| Foto | Urheber | Lizenz | Datum | verwendet für |", "|---|---|---|---|---|"]
        for pid, e in sorted(alt.items(), key=lambda kv: (kv[1]["urheber"], kv[0])):
            lines.append("| [%s](%s) | %s | %s | %s | %s |" % (pid, e["seite"], e["urheber"], e["lizenz"], e.get("datum", ""),
                                                           ", ".join(sorted(e["verwendung"]))))
    with open(QUELLEN_MD, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("  Quellen:", os.path.relpath(QUELLEN_MD, G.HERE), "(%d Fotos Projektion, %d Altbestand)" % (n1, len(alt)))


def swatches(farben):
    """Übersicht: Farben je Gebäude mit Filament-Nummer, Dachpalette (vorschau/farben.png)."""
    from preview import font, NAMES, OUT, BG
    rows = [b["slug"] for b in G.OBJEKTE if b["slug"] in farben]
    cw = 118
    ncol = max(len(farben[s]["farben"]) for s in rows)
    W, rh = max(1100, 300 + cw * max(ncol, len(farben["_dachpalette"]))), 96
    im = Image.new("RGB", (W, 70 + rh * (len(rows) + 1) + 40), BG)
    d = ImageDraw.Draw(im)
    d.text((16, 14), "Fassaden- und Dachfarben", fill=(30, 30, 30), font=font(28, True))

    def field(x, y, c, label):
        d.rectangle((x, y + 6, x + 100, y + 58), fill=c, outline=(60, 60, 60))
        nr = filament_nr(farben, c)
        hell = sum(rgb255(c)) > 380
        d.text((x + 6, y + 10), "F%d" % nr, fill=(20, 20, 20) if hell else (240, 240, 240), font=font(16, True))
        for i, line in enumerate(label.split("\n")[:2]):
            d.text((x, y + 62 + 13 * i), line[:18], fill=(60, 60, 60), font=font(11))

    for i, slug in enumerate(rows):
        e = farben[slug]
        y = 70 + i * rh
        d.text((16, y + 8), "%s %s" % (slug[:2], NAMES.get(slug[:2], slug)), fill=(30, 30, 30), font=font(18, True))
        d.text((16, y + 34), "%d Farben, %d Zonen" % (len(e["farben"]), len(e["zonen"])), fill=(90, 90, 90),
               font=font(13))
        for j, (k, v) in enumerate(e["farben"].items()):
            field(300 + j * cw, y, v["rgb"], "%s\n%s" % (k, v["rgb"]))
    y = 70 + len(rows) * rh
    d.text((16, y + 8), "Dachpalette", fill=(30, 30, 30), font=font(18, True))
    d.text((16, y + 34), "aus dem Luftbild 2024", fill=(90, 90, 90), font=font(13))
    for j, c in enumerate(farben["_dachpalette"]):
        field(300 + j * cw, y, c["rgb"], "%s %.0f %%\n%s" % (c["name"], 100 * c["anteil"], c["rgb"]))
    d.text((16, im.height - 30), "Dach: Luftbild 2024 © Stadt Leipzig (dl-de/by-2-0) · Fassaden: Straßenfotos "
           "(Panoramax, Commons) · F1–F%d = Filament-Nr. in den 3MF-Dateien (F1 = Platte)"
           % len(farben["_filamente"]), fill=(90, 90, 90), font=font(13))
    path = os.path.join(OUT, "farben.png")
    os.makedirs(OUT, exist_ok=True)
    im.save(path, optimize=True)
    print("  Vorschau:", os.path.relpath(path, G.HERE))


def probe_sheet(proben, path):
    """Fotos mit Messfeldern (magenta) und Weißabgleich-Referenz (cyan), Urheber/Lizenz je Foto."""
    from preview import font, BG
    import fassaden
    tiles = []
    for pid in dict.fromkeys(p["bild"] for p in proben):
        mine = [p for p in proben if p["bild"] == pid]
        katalog = fotos(fassaden.load_spec(mine[0]["gebaeude"]))
        ph, meta = photo_cached(pid, katalog)
        ph = ph.copy()
        k = ph.width / 1600
        dr = ImageDraw.Draw(ph)
        for p in mine:
            b = p["box"]
            box = (b[0] * ph.width, b[1] * ph.height, b[2] * ph.width, b[3] * ph.height)
            dr.rectangle(box, outline=(255, 0, 255), width=max(2, int(4 * k)))
            s_ = int(30 * k)
            dr.rectangle((box[0], box[3] + 3, box[0] + s_, box[3] + 3 + s_), fill=p["rgb"], outline=(255, 0, 255))
            dr.text((box[0] + 3, box[1] + 3), "%s %s" % (p["gebaeude"][:2], p["farbe"]), fill=(255, 0, 255),
                    font=font(int(26 * k), True))
        wb = katalog["weissabgleich"].get(pid)
        if wb:
            b = wb["box"]
            dr.rectangle((b[0] * ph.width, b[1] * ph.height, b[2] * ph.width, b[3] * ph.height),
                         outline=(0, 230, 255), width=max(2, int(4 * k)))
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
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sheet.save(path, quality=85)
    print("  Vorschau:", os.path.relpath(path, G.HERE))


if __name__ == "__main__":
    main()
