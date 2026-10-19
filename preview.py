#!/usr/bin/env python3
"""Rendert Vorschaubilder (PNG) der erzeugten STL/3MF-Dateien.

Software-Rasterizer mit Tiefenpuffer (kein Display/GPU nötig): schattierte
Isometrie mit Kantenlinien, Beschriftung mit Name und Maßen.

Aufruf:
    python3 preview.py                    # Standard-Vorschauen nach vorschau/
    python3 preview.py datei.stl ...      # beliebige Dateien -> vorschau/einzeln_gerendert/
"""
import argparse
import glob
import os
import re
import zipfile

import matplotlib
import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "vorschau")
FONT_DIR = os.path.join(matplotlib.get_data_path(), "fonts", "ttf")

PALETTE = ["#3B5991", "#7d9bd1", "#c9a227", "#8fb573", "#d7845b", "#9a9a9a", "#a0522d"]
PLATE_COLOR = "#e4e0d8"
SINGLE_COLOR = "#6f8fc7"
BG = (250, 250, 248)
OUTLINE = (44, 50, 66)  # Linienfarbe bei transparenten README-Bildern

NAMES = {
    "01": "Paulinum", "02": "Neues Augusteum", "03": "Hörsaalgebäude",
    "04": "Seminargebäude", "05": "Institutsgebäude", "06": "City-Hochhaus (Uniriese)",
    "08": "Innenhof (Leibnizforum)",
}


def font(size, bold=False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    try:
        return ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    except OSError:
        return ImageFont.load_default()


def rgb(c):
    return np.array(matplotlib.colors.to_rgb(c))


def _raster_loop(px, py, sz, ids, zbuf, fid):
    """Dreiecke einzeln rastern (für große Dreiecke); Gleichstand gewinnt der kleinere Index."""
    H, W = zbuf.shape
    for i in ids:
        x0, y0, z0 = px[i], py[i], sz[i]
        x_lo, x_hi = int(max(np.floor(x0.min()), 0)), int(min(np.ceil(x0.max()), W - 1))
        y_lo, y_hi = int(max(np.floor(y0.min()), 0)), int(min(np.ceil(y0.max()), H - 1))
        if x_lo > x_hi or y_lo > y_hi:
            continue
        gx, gy = np.meshgrid(np.arange(x_lo, x_hi + 1) + 0.5, np.arange(y_lo, y_hi + 1) + 0.5)
        (ax_, bx, cx), (ay, by, cy) = x0, y0
        den = (by - cy) * (ax_ - cx) + (cx - bx) * (ay - cy)
        if abs(den) < 1e-12:
            continue
        w0 = ((by - cy) * (gx - cx) + (cx - bx) * (gy - cy)) / den
        w1 = ((cy - ay) * (gx - cx) + (ax_ - cx) * (gy - cy)) / den
        w2 = 1 - w0 - w1
        inside = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
        if not inside.any():
            continue
        depth = w0 * z0[0] + w1 * z0[1] + w2 * z0[2]
        zb = zbuf[y_lo:y_hi + 1, x_lo:x_hi + 1]
        fb = fid[y_lo:y_hi + 1, x_lo:x_hi + 1]
        upd = inside & ((depth > zb) | ((depth == zb) & (i < fb)))
        zb[upd] = depth[upd]
        fb[upd] = i


try:  # optional: Numba kompiliert die Rasterschleife (pixelgleich zu rasterize, ~10-50x schneller)
    import numba
except ImportError:
    numba = None


def _raster_nb_py(px, py, sz, ids, zbuf, fid):
    """Alle Dreiecke `ids` in einem Durchgang rastern; dieselben Formeln und dieselbe Rangfolge
    (Gleichstand gewinnt der kleinere Index) wie _raster_loop und die gestapelte Variante."""
    H, W = zbuf.shape
    for k in range(len(ids)):
        i = ids[k]
        ax_, bx, cx = px[i, 0], px[i, 1], px[i, 2]
        ay, by, cy = py[i, 0], py[i, 1], py[i, 2]
        x_lo = int(max(np.floor(min(ax_, bx, cx)), 0))
        x_hi = int(min(np.ceil(max(ax_, bx, cx)), W - 1))
        y_lo = int(max(np.floor(min(ay, by, cy)), 0))
        y_hi = int(min(np.ceil(max(ay, by, cy)), H - 1))
        if x_lo > x_hi or y_lo > y_hi:
            continue
        den = (by - cy) * (ax_ - cx) + (cx - bx) * (ay - cy)
        if abs(den) < 1e-12:
            continue
        z0, z1, z2 = sz[i, 0], sz[i, 1], sz[i, 2]
        for y in range(y_lo, y_hi + 1):
            gy = y + 0.5
            for x in range(x_lo, x_hi + 1):
                gx = x + 0.5
                w0 = ((by - cy) * (gx - cx) + (cx - bx) * (gy - cy)) / den
                w1 = ((cy - ay) * (gx - cx) + (ax_ - cx) * (gy - cy)) / den
                w2 = 1 - w0 - w1
                if w0 >= -1e-6 and w1 >= -1e-6 and w2 >= -1e-6:
                    depth = w0 * z0 + w1 * z1 + w2 * z2
                    zb = zbuf[y, x]
                    if depth > zb or (depth == zb and i < fid[y, x]):
                        zbuf[y, x] = depth
                        fid[y, x] = i


_raster_nb = numba.njit(cache=True, nogil=True)(_raster_nb_py) if numba else None


def _finish_nb_py(fid, zbuf, shade, cols, norms, bg, thr, zmin, out, edge):
    """Schattierung und Kantenlinien in einem Durchgang (gleiche Formeln wie der NumPy-Pfad in render):
    out = Bild (uint8), edge = Kantenmaske."""
    H, W = fid.shape
    for y in range(H):
        for x in range(W):
            f = fid[y, x]
            e = False
            if f >= 0:
                if x + 1 < W:
                    g = fid[y, x + 1]
                    if g < 0:
                        e = True
                    else:
                        d = norms[f, 0] * norms[g, 0] + norms[f, 1] * norms[g, 1] + norms[f, 2] * norms[g, 2]
                        if d < 0.9 or abs(zbuf[y, x] - zbuf[y, x + 1]) > thr:
                            e = True
                if y + 1 < H and not e:
                    g = fid[y + 1, x]
                    if g < 0:
                        e = True
                    else:
                        d = norms[f, 0] * norms[g, 0] + norms[f, 1] * norms[g, 1] + norms[f, 2] * norms[g, 2]
                        if d < 0.9 or abs(zbuf[y, x] - zbuf[y + 1, x]) > thr:
                            e = True
            else:
                if x + 1 < W and fid[y, x + 1] >= 0:
                    e = True
                if y + 1 < H and fid[y + 1, x] >= 0:
                    e = True
            edge[y, x] = e
            for c in range(3):
                v = bg[c] if f < 0 else min(max(cols[f, c] * shade[f], 0.0), 1.0)
                if e:
                    v = v * 0.35
                out[y, x, c] = np.uint8(v * 255)


_finish_nb = numba.njit(cache=True, nogil=True)(_finish_nb_py) if numba else None


def rasterize(px, py, sz, ids, W, H, max_box=48, budget=1 << 21):
    """Z-Buffer-Rasterisierung der Dreiecke `ids` (Pixelkoordinaten px, py; Tiefe sz je Eckpunkt).

    Liefert (zbuf, fid) – Tiefe und Dreiecksindex je Pixel (-1 = leer). Kleine Dreiecke
    (Bounding-Box bis max_box Pixel) werden in Stapeln gleicher Boxgröße vektorisiert
    gerastert, große einzeln. Dieselben Formeln und dieselbe Rangfolge wie die
    Einzelschleife (bei Gleichstand gewinnt der kleinere Index): Ergebnis identisch.
    """
    zbuf = np.full((H, W), -np.inf)
    fid = np.full((H, W), -1, dtype=np.int64)
    ids = np.asarray(ids)
    if _raster_nb is not None and not os.environ.get("NO_NUMBA"):
        _raster_nb(np.ascontiguousarray(px), np.ascontiguousarray(py), np.ascontiguousarray(sz),
                   ids.astype(np.int64), zbuf, fid)
        return zbuf, fid
    x_lo = np.maximum(np.floor(px[ids].min(1)), 0).astype(np.int64)
    x_hi = np.minimum(np.ceil(px[ids].max(1)), W - 1).astype(np.int64)
    y_lo = np.maximum(np.floor(py[ids].min(1)), 0).astype(np.int64)
    y_hi = np.minimum(np.ceil(py[ids].max(1)), H - 1).astype(np.int64)
    ok = (x_lo <= x_hi) & (y_lo <= y_hi)
    box = np.maximum(x_hi - x_lo, y_hi - y_lo) + 1
    big = ok & (box > max_box)
    _raster_loop(px, py, sz, ids[big], zbuf, fid)
    small = ok & ~big
    cls = np.where(small, np.ceil(np.log2(np.maximum(box, 1))).astype(int), -1)  # Boxkante 2^cls
    for c in range(0, int(np.log2(max_box)) + 2):
        sel = np.nonzero(cls == c)[0]
        if not len(sel):
            continue
        K = 1 << c
        step = max(1, budget // (K * K))
        off = np.arange(K)
        for lo in range(0, len(sel), step):
            s_ = sel[lo:lo + step]
            t = ids[s_]
            X, Y, Z = px[t], py[t], sz[t]
            gx = x_lo[s_][:, None, None] + off[None, None, :] + 0.5
            gy = y_lo[s_][:, None, None] + off[None, :, None] + 0.5
            ax_, bx, cx = X[:, 0, None, None], X[:, 1, None, None], X[:, 2, None, None]
            ay, by, cy = Y[:, 0, None, None], Y[:, 1, None, None], Y[:, 2, None, None]
            den = (by - cy) * (ax_ - cx) + (cx - bx) * (ay - cy)
            good = np.abs(den) >= 1e-12
            den = np.where(good, den, 1.0)
            w0 = ((by - cy) * (gx - cx) + (cx - bx) * (gy - cy)) / den
            w1 = ((cy - ay) * (gx - cx) + (ax_ - cx) * (gy - cy)) / den
            w2 = 1 - w0 - w1
            inside = ((w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6) & good
                      & (gx < (x_hi[s_][:, None, None] + 1)) & (gy < (y_hi[s_][:, None, None] + 1)))
            depth = w0 * Z[:, 0, None, None] + w1 * Z[:, 1, None, None] + w2 * Z[:, 2, None, None]
            n, yy, xx = np.nonzero(inside)
            if not len(n):
                continue
            pix = (y_lo[s_][n] + yy) * W + (x_lo[s_][n] + xx)
            d, tri = depth[n, yy, xx], t[n]
            # je Pixel den besten Treffer: größte Tiefe, bei Gleichstand kleinster Index
            order = np.lexsort((tri, -d, pix))
            pix, d, tri = pix[order], d[order], tri[order]
            first = np.r_[True, pix[1:] != pix[:-1]]
            pix, d, tri = pix[first], d[first], tri[first]
            zf, ff = zbuf.reshape(-1), fid.reshape(-1)
            upd = (d > zf[pix]) | ((d == zf[pix]) & (tri < ff[pix]))
            zf[pix[upd]], ff[pix[upd]] = d[upd], tri[upd]
    return zbuf, fid


SS = 2  # Überabtastung (Kantenglättung); 1 = schneller, gröber (generate.py --fast)


def render(meshes, size=(900, 700), azim=-35, elev=30, ss=None, margin=0.06, return_proj=False, flat=False,
           light_from_view=False, transparent=False, px_per_mm=None, pad=10):
    """meshes: Liste von (trimesh.Trimesh, Farbe oder Farben je Dreieck). Liefert PIL-Bild,
    mit return_proj zusätzlich eine Funktion Weltpunkt -> Pixel (x, y) im Bild.

    transparent: RGBA mit freigestelltem Hintergrund (für die README).
    px_per_mm:   feste Pixel-Skala statt Einpassen in `size`; die Bildgröße folgt
                 dann aus der Ausdehnung (+ `pad` Pixel Rand). So lassen sich
                 mehrere Modelle im gleichen Verhältnis darstellen.
    """
    ss = ss or SS
    a, e = np.radians(azim), np.radians(elev)
    cam = np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])
    right = np.array([-np.sin(a), np.cos(a), 0.0])
    up = np.cross(cam, right)
    light = np.array([-0.35, -0.55, 0.76])
    if light_from_view:  # Licht von links oben hinter der Kamera: sichtbare Seiten hell
        light = 0.7 * cam - 0.45 * right + np.array([0, 0, 0.8])
    light /= np.linalg.norm(light)

    tris, cols, norms = [], [], []
    for m, c in meshes:
        tris.append(m.triangles)
        norms.append(m.face_normals)
        c = np.asarray(c, float) if not isinstance(c, str) else rgb(c)
        cols.append(c if c.ndim == 2 else np.repeat(c[None], len(m.faces), axis=0))
    tris, cols, norms = np.vstack(tris), np.vstack(cols), np.vstack(norms)

    sx, sy, sz = tris @ right, tris @ up, tris @ cam
    xmin, xmax, ymin, ymax = sx.min(), sx.max(), sy.min(), sy.max()
    if px_per_mm:
        k = px_per_mm * ss
        size = (int(np.ceil((xmax - xmin) * px_per_mm)) + 2 * pad,
                int(np.ceil((ymax - ymin) * px_per_mm)) + 2 * pad)
        W, H = size[0] * ss, size[1] * ss
    else:
        W, H = size[0] * ss, size[1] * ss
        k = (1 - 2 * margin) * min(W / max(xmax - xmin, 1e-9), H / max(ymax - ymin, 1e-9))
    px = (sx - (xmin + xmax) / 2) * k + W / 2
    py = H / 2 - (sy - (ymin + ymax) / 2) * k

    zbuf, fid = rasterize(px, py, sz, np.nonzero(norms @ cam > -1e-9)[0], W, H)  # ohne Rückseiten

    if _finish_nb is not None and not os.environ.get("NO_NUMBA"):
        if flat:  # fast unschattiert: Farben beurteilen
            shade_f = 0.82 + 0.18 * np.clip(norms @ cam, 0, 1)
        else:
            shade_f = 0.42 + 0.48 * np.clip(norms @ light, 0, 1) + 0.10 * np.clip(norms @ cam, 0, 1)
        hit = fid >= 0
        zmin = zbuf[hit].min() - 1 if hit.any() else 0
        zz = np.where(hit, zbuf, zmin)
        out = np.empty((H, W, 3), np.uint8)
        edge = np.empty((H, W), np.bool_)
        _finish_nb(fid, zz, shade_f, np.ascontiguousarray(cols, dtype=np.float64), np.ascontiguousarray(norms),
                   np.array(OUTLINE if transparent else BG) / 255, 2.4 / k * ss, zmin, out, edge)
        return _render_tail(out, hit, edge, size, transparent, return_proj, (xmin, xmax, ymin, ymax), k, W, H, ss, right, up)
    img = np.empty((H, W, 3))
    img[:] = np.array(OUTLINE if transparent else BG) / 255
    hit = fid >= 0
    f = fid[hit]
    if flat:  # fast unschattiert: Farben beurteilen
        shade = 0.82 + 0.18 * np.clip(norms[f] @ cam, 0, 1)
    else:
        shade = 0.42 + 0.48 * np.clip(norms[f] @ light, 0, 1) + 0.10 * np.clip(norms[f] @ cam, 0, 1)
    img[hit] = np.clip(cols[f] * shade[:, None], 0, 1)

    # Kantenlinien: Sprünge in Flächennormale oder Tiefe
    nb = np.zeros((H, W, 3))
    nb[hit] = norms[f]
    zz = np.where(hit, zbuf, zbuf[hit].min() - 1 if hit.any() else 0)
    edge = np.zeros((H, W), bool)
    for dy, dx in ((0, 1), (1, 0)):
        n1, n2 = nb[: H - dy, : W - dx], nb[dy:, dx:]
        both = hit[: H - dy, : W - dx] & hit[dy:, dx:]
        crease = both & ((n1 * n2).sum(-1) < 0.9)
        jump = both & (np.abs(zz[: H - dy, : W - dx] - zz[dy:, dx:]) > 2.4 / k * ss)
        sil = hit[: H - dy, : W - dx] != hit[dy:, dx:]
        e_ = crease | jump | sil
        edge[: H - dy, : W - dx] |= e_
    img[edge] *= 0.35
    return _render_tail((img * 255).astype(np.uint8), hit, edge, size, transparent, return_proj,
                        (xmin, xmax, ymin, ymax), k, W, H, ss, right, up)


def _render_tail(img, hit, edge, size, transparent, return_proj, ext, k, W, H, ss, right, up):
    """Verkleinern (Kantenglättung), Transparenz und Projektionsfunktion; `img` ist das fertige uint8-Bild."""
    xmin, xmax, ymin, ymax = ext
    im = Image.fromarray(img).resize(size, Image.LANCZOS)
    if transparent:
        # Silhouette samt Kantenlinie bleibt deckend, alles andere ist transparent; der
        # Hintergrund trägt die Linienfarbe, damit am Rand kein heller Saum entsteht.
        alpha = Image.fromarray(((hit | edge) * 255).astype(np.uint8))
        im.putalpha(alpha.resize(size, Image.LANCZOS))
    if return_proj:
        cx, cy = (xmin + xmax) / 2, (ymin + ymax) / 2

        def proj(P):
            P = np.asarray(P, float)
            return ((P @ right - cx) * k + W / 2) / ss, (H / 2 - (P @ up - cy) * k) / ss
        return im, proj
    return im


def warmup():
    """Numba-Kerne vor dem Forken kompilieren bzw. aus dem Cache laden (sonst tut es jeder Kindprozess)."""
    if _raster_nb is not None:
        t = trimesh.creation.box()
        render([(t, "#888888")], size=(16, 16), ss=1)


def caption(im, title, subtitle=None):
    pad = 70 if subtitle else 46
    out = Image.new("RGB", (im.width, im.height + pad), BG)
    out.paste(im, (0, pad))
    d = ImageDraw.Draw(out)
    d.text((16, 10), title, fill=(30, 30, 30), font=font(24, True))
    if subtitle:
        d.text((16, 42), subtitle, fill=(90, 90, 90), font=font(16))
    return out


def dims(m):
    x, y, z = m.extents
    return "%.0f × %.0f × %.0f mm" % (x, y, z)


def load_mesh(path):
    m = trimesh.load(path, process=False)
    if isinstance(m, trimesh.Scene):
        return [(g, None, name) for name, g in m.geometry.items()]
    return [(m, None, os.path.basename(path))]


def render_file(path, out_png, title=None, azim=-35, elev=30, size=(900, 700)):
    parts = load_mesh(path)
    meshes, ci = [], 0
    for g, _, name in parts:
        if len(parts) == 1:
            col = PLATE_COLOR if "grundplatte" in os.path.basename(path) else SINGLE_COLOR
        elif name.lower().startswith("sockel"):
            col = PLATE_COLOR
        else:
            col = PALETTE[ci % len(PALETTE)]
            ci += 1
        meshes.append((g, col))
    im = render(meshes, size=size, azim=azim, elev=elev)
    allm = trimesh.util.concatenate([m for m, _ in meshes])
    rel = os.path.relpath(path, HERE)
    out = caption(im, title or os.path.basename(path), "%s  ·  %s" % (dims(allm), rel))
    os.makedirs(os.path.dirname(out_png), exist_ok=True)
    out.save(out_png, optimize=True)
    print("  Vorschau:", os.path.relpath(out_png, HERE))
    return out


def contact_sheet(images, out_png, title, cols=4, cell=(420, 360)):
    rows = (len(images) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cell[0], rows * cell[1] + 60), BG)
    d = ImageDraw.Draw(sheet)
    d.text((16, 14), title, fill=(30, 30, 30), font=font(28, True))
    for i, im in enumerate(images):
        r, c = divmod(i, cols)
        t = im.copy()
        t.thumbnail(cell)
        sheet.paste(t, (c * cell[0] + (cell[0] - t.width) // 2, 60 + r * cell[1]))
    sheet.save(out_png, optimize=True)
    print("  Vorschau:", os.path.relpath(out_png, HERE))


QUELLEN_NAMEN = {"osm": "OpenStreetMap", "lod2": "LoD2 Stadt Leipzig", "laserscan": "Laserscan GeoSN"}
HERO = ("laserscan", "1zu1500", "komplett_campus_mit_extras_farbig_ost.png")


# --------------------------------------------------------------------------
# Bilder für die README: farbig (Filamentfarben aus den 3MF), transparent, ohne
# Beschriftung, zugeschnitten. Modelle, die verglichen werden, teilen sich eine
# Pixel/mm-Skala, damit Größenunterschiede sichtbar bleiben. Die Bilder sind mit
# DENSITY-facher Auflösung gerendert (scharf auf HiDPI); die README zeigt sie mit
# Breite = Pixelbreite / DENSITY (siehe readme.py).
# --------------------------------------------------------------------------
README_DIR = os.path.join(OUT, "readme")
DENSITY = 2
README_VIEW = dict(azim=25, elev=28, light_from_view=True)  # vom Augustusplatz (Osten)


def load_3mf_coloured(path):
    """[(Name, Netz, RGB je Dreieck)] aus einer *_objekte.3mf (Farbe = Filament-Grundmaterial)."""
    import html
    xml = zipfile.ZipFile(path).read("3D/3dmodel.model").decode()
    pal = np.array([[int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
                    for h in re.findall(r'displaycolor="#([0-9A-Fa-f]{6})', xml)])
    out = []
    for m in re.finditer(r'<object id="\d+" name="([^"]*)".*?<vertices>(.*?)</vertices>'
                         r'<triangles>(.*?)</triangles>', xml, re.S):
        v = np.array(re.findall(r'<vertex x="([^"]+)" y="([^"]+)" z="([^"]+)"', m.group(2)), float)
        t = np.array(re.findall(r'v1="(\d+)" v2="(\d+)" v3="(\d+)" pid="1" p1="(\d+)"', m.group(3)), int)
        out.append((html.unescape(m.group(1)), trimesh.Trimesh(v, t[:, :3], process=False), pal[t[:, 3]]))
    return out


def _fit(meshes, max_w, max_h, azim, elev):
    """Pixel/mm, mit der die Meshes in max_w x max_h (CSS-Pixel) passen."""
    a, e = np.radians(azim), np.radians(elev)
    cam = np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])
    right = np.array([-np.sin(a), np.cos(a), 0.0])
    up = np.cross(cam, right)
    pts = np.vstack([m.vertices for m, _ in meshes])
    return min(max_w / np.ptp(pts @ right), max_h / np.ptp(pts @ up))


def _save(im, name):
    os.makedirs(README_DIR, exist_ok=True)
    path = os.path.join(README_DIR, name)
    im.save(path, optimize=True)
    print("  README-Bild:", os.path.relpath(path, HERE))


def _render_one(meshes, kw):
    return render(meshes, **kw)


def _group_jobs(groups, max_w, max_h, view):
    """groups: {Dateiname: Meshes}; gemeinsame Skala, passend für das größte Modell."""
    k = min(_fit(m, max_w, max_h, view["azim"], view["elev"]) for m in groups.values()) * DENSITY
    return [(name, meshes, dict(transparent=True, px_per_mm=k, pad=6 * DENSITY, **view))
            for name, meshes in groups.items()]


def readme_assets(stl_dir=os.path.join(HERE, "stl")):
    print("\nREADME-Bilder")
    import parallel
    quellen = [q for q in QUELLEN_NAMEN if os.path.isdir(os.path.join(stl_dir, q))]
    objekte = lambda q, sc: os.path.join(stl_dir, q, sc, "komplett_campus_mit_extras_objekte.3mf")
    quellen = [q for q in quellen if os.path.exists(objekte(q, "1zu1500"))]
    if not quellen:
        return
    cache = {}

    def coloured(q, sc):
        if (q, sc) not in cache:
            cache[q, sc] = load_3mf_coloured(objekte(q, sc))
        return cache[q, sc]

    meshes = lambda q, sc: [(m, c) for _, m, c in coloured(q, sc)]
    best = quellen[-1]  # detailreichste Quelle (Laserscan)
    jobs = []  # (Dateiname, Meshes, render-Argumente); gerendert wird am Ende parallel

    # Titelbild und Campus je Quelle (gleiche Skala) sowie beide Maßstäbe der besten Quelle
    k = _fit(meshes(best, "1zu1500"), 900, 560, README_VIEW["azim"], README_VIEW["elev"]) * DENSITY
    jobs.append(("hero.png", meshes(best, "1zu1500"),
                 dict(transparent=True, px_per_mm=k, pad=8 * DENSITY, **README_VIEW)))
    jobs += _group_jobs({"campus_%s.png" % q: meshes(q, "1zu1500") for q in quellen}, 270, 400, README_VIEW)
    if os.path.exists(objekte(best, "1zu1000")):
        jobs += _group_jobs({"campus_%s_%s.png" % (best, sc): meshes(best, sc) for sc in ("1zu1500", "1zu1300", "1zu1000")
                             if os.path.exists(objekte(best, sc))}, 440, 600, README_VIEW)

    # Einzelgebäude je Quelle (1:1000), je Gebäude gemeinsame Skala
    have1000 = [q for q in quellen if os.path.exists(objekte(q, "1zu1000"))]
    names = [n for n, _, _ in coloured(best, "1zu1000")][1:] if best in have1000 else []
    for i in range(1, len(names) + 1):
        groups = {}
        for q in have1000:
            objs = coloured(q, "1zu1000")
            if i < len(objs):
                groups["%02d_%s.png" % (i, q)] = [(objs[i][1], objs[i][2])]
        jobs += _group_jobs(groups, 190, 230, dict(README_VIEW, azim=-35))

    # Grundplatte mit darüber schwebenden Gebäuden
    plate = os.path.join(stl_dir, best, "1zu1500", "grundplatte_campus_mit_extras.stl")
    if os.path.exists(plate):
        parts = [(trimesh.load(plate, process=False), PLATE_COLOR)]
        for _, m, c in coloured(best, "1zu1500")[1:]:
            m = m.copy()
            m.apply_translation([0, 0, 28])
            parts.append((m, c))
        k = _fit(parts, 560, 700, README_VIEW["azim"], README_VIEW["elev"]) * DENSITY
        jobs.append(("grundplatte.png", parts, dict(transparent=True, px_per_mm=k, pad=8 * DENSITY, **README_VIEW)))

    for (name, _, _), im in zip(jobs, parallel.starmap(_render_one, [(m, kw) for _, m, kw in jobs])):
        _save(im, name)


def default_previews(stl_dir=os.path.join(HERE, "stl"), fast=False):
    """Standard-Vorschauen für alle erzeugten Quellen und Maßstäbe, dazu Vergleichsbilder.

    fast: nur die Bilder je Quelle (kein Vergleich, kein vorschau.png, keine README-Bilder)."""
    import parallel
    print("\nVorschaubilder")
    with parallel.phase("Vorschaubilder je Quelle"):
        for qdir in sorted(glob.glob(os.path.join(stl_dir, "*"))):
            if os.path.isdir(qdir) and glob.glob(os.path.join(qdir, "1zu*")):
                source_previews(qdir, os.path.join(OUT, os.path.basename(qdir)))
    if fast:
        return
    with parallel.phase("Quellenvergleich"):
        comparisons(stl_dir)
    hero = os.path.join(OUT, *HERO)
    if os.path.exists(hero):
        Image.open(hero).save(os.path.join(HERE, "vorschau.png"), optimize=True)
        print("  Vorschau: vorschau.png")
    with parallel.phase("README-Bilder + README"):
        readme_assets(stl_dir)
        import readme
        readme.update()


def source_preview_jobs(qdir, out):
    """Aufgaben (render_file-Argumente) für alle Dateien einer Quelle; sheets: Kontaktblätter."""
    quelle = QUELLEN_NAMEN.get(os.path.basename(qdir), os.path.basename(qdir))
    jobs, sheets = [], []
    for sdir in sorted(glob.glob(os.path.join(qdir, "1zu*"))):
        scale = os.path.basename(sdir)
        odir = os.path.join(out, scale)
        label = "%s, %s" % (scale.replace("1zu", "1:"), quelle)
        singles = []
        for f in sorted(glob.glob(os.path.join(sdir, "einzeln", "*.stl"))):
            slug = os.path.basename(f)[:-4]
            name = NAMES.get(slug[:2], slug)
            singles.append(len(jobs))
            jobs.append((f, os.path.join(odir, slug + ".png"), "%s %s  (%s)" % (slug[:2], name, label)))
        for f in sorted(glob.glob(os.path.join(sdir, "*_objekte.3mf"))):
            base = os.path.basename(f)[:-4]
            jobs.append((f, os.path.join(odir, base + ".png"),
                         "Gesamtmodell %s  (%s)" % ("mit Extras" if "extras" in base else "Campus", label),
                         -30, 32, (1100, 800)))
        for f in sorted(glob.glob(os.path.join(sdir, "grundplatte_*.stl"))):
            base = os.path.basename(f)[:-4]
            jobs.append((f, os.path.join(odir, base + ".png"), "Grundplatte %s" % label, -90, 55))
        for f in sorted(glob.glob(os.path.join(sdir, "komplett_*.stl"))):
            base = os.path.basename(f)[:-4]
            jobs.append((f, os.path.join(odir, base + ".png"), "Komplettmodell (1 Druckteil) %s" % label, -30, 32))
        if singles:
            sheets.append((singles, os.path.join(out, "einzelgebaeude_%s.png" % scale),
                           "Einzelgebäude %s" % label))
    return jobs, sheets


def source_previews(qdir, out):
    """Alle Bilder einer Quelle rendern (parallel) und die Kontaktblätter der Einzelgebäude bauen."""
    import parallel
    jobs, sheets = source_preview_jobs(qdir, out)
    images = parallel.starmap(render_file, jobs)
    for idx, path, title in sheets:
        contact_sheet([images[i] for i in idx], path, title)


def _render_cell(f, q):
    m = trimesh.load(f, process=False)
    im = render([(m, SINGLE_COLOR)], size=(560, 460))
    return caption(im, QUELLEN_NAMEN[q], "%s  ·  %d Dreiecke" % (dims(m), len(m.faces)))


def comparisons(stl_dir, scale="1zu1000"):
    """Gleiche Ansicht je Gebäude aus allen Quellen nebeneinander (vorschau/vergleich/)."""
    quellen = [q for q in QUELLEN_NAMEN if os.path.isdir(os.path.join(stl_dir, q, scale, "einzeln"))]
    if len(quellen) < 2:
        return
    odir = os.path.join(OUT, "vergleich")
    os.makedirs(odir, exist_ok=True)
    slugs = sorted({os.path.basename(f)[:-4] for q in quellen
                    for f in glob.glob(os.path.join(stl_dir, q, scale, "einzeln", "*.stl"))})
    import parallel
    todo = [(slug, q) for slug in slugs for q in quellen
            if os.path.exists(os.path.join(stl_dir, q, scale, "einzeln", slug + ".stl"))]
    done = dict(zip(todo, parallel.starmap(_render_cell, [(os.path.join(stl_dir, q, scale, "einzeln", s + ".stl"), q)
                                                         for s, q in todo])))
    rows = []
    for slug in slugs:
        cells = [done.get((slug, q)) for q in quellen]
        rows.append((slug, cells))
        grid([(slug, cells)], os.path.join(odir, "%s_%s.png" % (slug, scale)),
             "%s %s – Vergleich der Quellen (%s)" % (slug[:2], NAMES.get(slug[:2], slug),
                                                      scale.replace("1zu", "1:")))
    grid(rows, os.path.join(OUT, "vergleich_%s.png" % scale),
         "Vergleich der Quellen, Einzelgebäude %s" % scale.replace("1zu", "1:"), thumb=(380, 330))
    # farbige Gesamtmodelle (von generate.py gerendert) untereinander
    for blick in ("_ost", ""):
        ims = [os.path.join(OUT, q, "1zu1500", "komplett_campus_mit_extras_farbig%s.png" % blick) for q in quellen]
        ims = [Image.open(f) for f in ims if os.path.exists(f)]
        if len(ims) > 1:
            grid([("", ims)], os.path.join(OUT, "vergleich_farbig%s.png" % blick),
                 "Vergleich der Quellen, farbig (1:1500)", thumb=(760, 600))


def grid(rows, out_png, title, thumb=None):
    cells = [c for _, r in rows for c in r if c is not None]
    cw, ch = thumb or (max(c.width for c in cells), max(c.height for c in cells))
    ncol = max(len(r) for _, r in rows)
    lab = 210 if len(rows) > 1 else 0
    sheet = Image.new("RGB", (lab + ncol * cw, 60 + len(rows) * ch), BG)
    d = ImageDraw.Draw(sheet)
    d.text((16, 14), title, fill=(30, 30, 30), font=font(28, True))
    for i, (slug, r) in enumerate(rows):
        if lab:
            name = NAMES.get(slug[:2], slug).replace(" (", "\n(").replace(" ", "\n", 1 if len(NAMES.get(slug[:2], slug)) > 16 else 0)
            d.multiline_text((12, 60 + i * ch + ch // 2 - 30), "%s\n%s" % (slug[:2], name),
                             fill=(30, 30, 30), font=font(19, True))
        for j, c in enumerate(r):
            if c is None:
                continue
            t = c.copy()
            t.thumbnail((cw, ch))
            sheet.paste(t, (lab + j * cw + (cw - t.width) // 2, 60 + i * ch))
    sheet.save(out_png, optimize=True)
    print("  Vorschau:", os.path.relpath(out_png, HERE))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*", help="STL/3MF-Dateien (leer: Standard-Vorschauen)")
    ap.add_argument("--azim", type=float, default=-35, help="Blickrichtung in Grad (-90 = von Süden)")
    ap.add_argument("--elev", type=float, default=30, help="Blickhöhe in Grad")
    ap.add_argument("--out", default=os.path.join(OUT, "einzeln_gerendert"))
    args = ap.parse_args()
    if not args.files:
        default_previews()
        return
    for f in args.files:
        out = os.path.join(args.out, os.path.splitext(os.path.basename(f))[0] + ".png")
        render_file(f, out, azim=args.azim, elev=args.elev)


if __name__ == "__main__":
    main()
