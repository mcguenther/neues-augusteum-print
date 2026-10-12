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

NAMES = {
    "01": "Paulinum", "02": "Neues Augusteum", "03": "Hörsaalgebäude",
    "04": "Seminargebäude", "05": "Institutsgebäude", "06": "City-Hochhaus (Uniriese)",
    "07": "Moritzbastei",
}


def font(size, bold=False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    try:
        return ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    except OSError:
        return ImageFont.load_default()


def rgb(c):
    return np.array(matplotlib.colors.to_rgb(c))


def render(meshes, size=(900, 700), azim=-35, elev=30, ss=2, margin=0.06):
    """meshes: Liste von (trimesh.Trimesh, Farbe). Liefert PIL-Bild."""
    a, e = np.radians(azim), np.radians(elev)
    cam = np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])
    right = np.array([-np.sin(a), np.cos(a), 0.0])
    up = np.cross(cam, right)
    light = np.array([-0.35, -0.55, 0.76])
    light /= np.linalg.norm(light)

    tris, cols, norms = [], [], []
    for m, c in meshes:
        tris.append(m.triangles)
        norms.append(m.face_normals)
        cols.append(np.repeat(rgb(c)[None], len(m.faces), axis=0))
    tris, cols, norms = np.vstack(tris), np.vstack(cols), np.vstack(norms)

    sx, sy, sz = tris @ right, tris @ up, tris @ cam
    W, H = size[0] * ss, size[1] * ss
    xmin, xmax, ymin, ymax = sx.min(), sx.max(), sy.min(), sy.max()
    k = (1 - 2 * margin) * min(W / max(xmax - xmin, 1e-9), H / max(ymax - ymin, 1e-9))
    px = (sx - (xmin + xmax) / 2) * k + W / 2
    py = H / 2 - (sy - (ymin + ymax) / 2) * k

    zbuf = np.full((H, W), -np.inf)
    fid = np.full((H, W), -1, dtype=np.int64)
    visible = norms @ cam > -1e-9  # Rückseiten weglassen
    for i in np.nonzero(visible)[0]:
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
        upd = inside & (depth > zb)
        zb[upd] = depth[upd]
        fid[y_lo:y_hi + 1, x_lo:x_hi + 1][upd] = i

    img = np.empty((H, W, 3))
    img[:] = np.array(BG) / 255
    hit = fid >= 0
    f = fid[hit]
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
    im = Image.fromarray((img * 255).astype(np.uint8))
    return im.resize(size, Image.LANCZOS)


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
    m = trimesh.load(path)
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


def default_previews(stl_dir=os.path.join(HERE, "stl")):
    """Standard-Vorschauen für alle erzeugten Maßstäbe."""
    print("\nVorschaubilder")
    os.makedirs(OUT, exist_ok=True)
    for sdir in sorted(glob.glob(os.path.join(stl_dir, "1zu*"))):
        scale = os.path.basename(sdir)
        odir = os.path.join(OUT, scale)
        label = scale.replace("1zu", "1:")
        singles = []
        for f in sorted(glob.glob(os.path.join(sdir, "einzeln", "*.stl"))):
            slug = os.path.basename(f)[:-4]
            name = NAMES.get(slug[:2], slug)
            singles.append(render_file(f, os.path.join(odir, slug + ".png"),
                                       "%s %s  (%s)" % (slug[:2], name, label)))
        for f in sorted(glob.glob(os.path.join(sdir, "*_objekte.3mf"))):
            base = os.path.basename(f)[:-4]
            render_file(f, os.path.join(odir, base + ".png"),
                        "Gesamtmodell %s  (%s)" % ("mit Extras" if "extras" in base else "Campus", label),
                        azim=-30, elev=32, size=(1100, 800))
        for f in sorted(glob.glob(os.path.join(sdir, "grundplatte_*.stl"))):
            base = os.path.basename(f)[:-4]
            render_file(f, os.path.join(odir, base + ".png"), "Grundplatte %s" % label,
                        azim=-90, elev=55)
        for f in sorted(glob.glob(os.path.join(sdir, "komplett_*.stl"))):
            base = os.path.basename(f)[:-4]
            render_file(f, os.path.join(odir, base + ".png"), "Komplettmodell (1 Druckteil) %s" % label,
                        azim=-30, elev=32)
        if singles:
            contact_sheet(singles, os.path.join(OUT, "einzelgebaeude_%s.png" % scale),
                          "Einzelgebäude %s" % label)
    hero = os.path.join(OUT, "1zu1500", "komplett_campus_mit_extras_objekte.png")
    if os.path.exists(hero):
        Image.open(hero).save(os.path.join(HERE, "vorschau.png"), optimize=True)
        print("  Vorschau: vorschau.png")


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
