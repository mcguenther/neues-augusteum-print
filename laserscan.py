#!/usr/bin/env python3
"""Gebäude aus der Laserscan-Punktwolke von GeoSN (Befliegung 9. 1. 2023).

Quelle: Landesamt für Geobasisinformation Sachsen (GeoSN), Laserscandaten
(Kachel lsc_33316_5690_2_sn, ca. 18 Punkte/m²), Lizenz dl-de/by-2-0.
https://www.geodaten.sachsen.de/downloadbereich-digitale-hoehenmodelle-4851.html

Die 2×2-km-Kachel (ca. 240 MB) wird nur mit `--fetch` geladen; ins Repo kommt
nur der Ausschnitt um die Campus-Gebäude (`data/laserscan_campus.laz`).

Verfahren: Je Gebäude wird aus den Nicht-Boden-Punkten ein Höhenraster
(höchster Punkt je Zelle, RASTER m Kantenlänge) gebildet, Lücken werden aus den
Nachbarzellen gefüllt und Einzelausreißer per Medianfilter entfernt. Das Raster
wird als geschlossene Höhenfeld-Oberfläche vernetzt und mit dem Grundriss des
Gebäudes aus dem LoD2-Modell (Kataster-Grundriss) ausgeschnitten. So bekommt
man die tatsächliche Dachlandschaft (Aufbauten, Giebel, Technik, Turmkrone) mit
sauberen, senkrechten Außenwänden.
"""
import io
import os
import urllib.request
import zipfile

import laspy
import manifold3d as m3d
import numpy as np
import shapely
from scipy import ndimage
from shapely.ops import unary_union

import generate as G
import lod2

LAZ_URL = ("https://geocloud.landesvermessung.sachsen.de/public.php/dav/files/EpkzyJHScGb5ndd/"
           "lsc_33316_5690_2_sn_laz.zip")
LAZ_MEMBER = "lsc_33316_5690_2_sn.laz"
LAZ_FILE = os.path.join(G.HERE, "data", "laserscan_campus.laz")
ATTRIBUTION = "Laserscan © GeoSN (dl-de/by-2-0)"

RASTER = 0.3        # m Rasterweite des Höhenfelds
MARGIN = 4.0        # m Puffer um die Grundrisse beim Ausschneiden der Punkte
GROUND_CLASS = 2
SIMPLIFY = 0.08     # mm Toleranz beim Vereinfachen des Netzes (unter Schichthöhe)
LOD2_CAP = 4.0      # m, so weit darf der Scan über das LoD2-Dach ragen (Aufbauten)
LOD2_SNAP = 0.5     # m, innerhalb dieser Abweichung gilt die (glatte) LoD2-Dachfläche
EDGE = 1.0          # m Randstreifen, in dem Löcher im Scan aus dem LoD2-Dach gefüllt werden
NOTCH = 3.0         # m: schmalere Vertiefungen unter dem LoD2-Dach gelten als Messlücke


def footprints_utm():
    """Alle Grundrisse (OSM + LoD2) in UTM, als Auswahlbereich für die Punkte."""
    to_utm = lambda a: np.column_stack(lod2.local_to_utm(a[:, 0], a[:, 1]))
    geoms = [shapely.transform(g, to_utm) for g in lod2.osm_outlines_local().values()]
    for b in lod2.load_lod2():
        for r, _ in b["roofs"]:
            geoms.append(shapely.Polygon(np.column_stack(lod2.local_to_utm(r[:, 0], r[:, 1]))).buffer(0))
    return unary_union(geoms).buffer(MARGIN)


def fetch():
    """Lädt die Laserscan-Kachel und speichert den Campus-Ausschnitt."""
    print("Lade", LAZ_URL)
    req = urllib.request.Request(LAZ_URL)
    with urllib.request.urlopen(req, timeout=1200) as r:
        data = r.read()
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        extract(io.BytesIO(z.read(LAZ_MEMBER)), LAZ_FILE)


def extract(src, dst):
    area = footprints_utm()
    shapely.prepare(area)
    minx, miny, maxx, maxy = area.bounds
    with laspy.open(src) as f:
        header = f.header
        keep = []
        for c in f.chunk_iterator(5_000_000):
            x, y = np.asarray(c.x), np.asarray(c.y)
            m = (x >= minx) & (x <= maxx) & (y >= miny) & (y <= maxy)
            if m.any():
                sub = c[m]
                inside = shapely.contains_xy(area, np.asarray(sub.x), np.asarray(sub.y))
                keep.append(sub[inside])
    out = laspy.LasData(laspy.LasHeader(point_format=header.point_format, version=header.version))
    out.header.scales, out.header.offsets = header.scales, header.offsets
    out.points = laspy.ScaleAwarePointRecord(
        np.concatenate([k.array for k in keep]), header.point_format, header.scales, header.offsets)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    out.write(dst)
    print("  %d Punkte -> %s" % (len(out.points), os.path.relpath(dst, G.HERE)))


def load_points():
    """Nicht-Boden-Punkte (lokal, m). Nur letzte Echos: Vegetation (Bäume auf der
    Moritzbastei, Kronen über Dachkanten) liefert mehrere Echos, das letzte trifft
    meist darunterliegende Flächen; Dächer liefern nur ein Echo."""
    las = laspy.read(LAZ_FILE)
    keep = ((np.asarray(las.classification) != GROUND_CLASS)
            & (np.asarray(las.return_number) == np.asarray(las.number_of_returns)))
    x, y = lod2.utm_to_local(np.asarray(las.x)[keep], np.asarray(las.y)[keep])
    return np.column_stack([x, y, np.asarray(las.z)[keep]])


def height_grid(pts, bounds, res=RASTER):
    """Höchster Punkt je Rasterzelle, Lücken gefüllt, Ausreißer entfernt."""
    minx, miny, maxx, maxy = bounds
    nx, ny = int(np.ceil((maxx - minx) / res)) + 1, int(np.ceil((maxy - miny) / res)) + 1
    ix = np.floor((pts[:, 0] - minx) / res).astype(int)
    iy = np.floor((pts[:, 1] - miny) / res).astype(int)
    ok = (ix >= 0) & (ix < nx) & (iy >= 0) & (iy < ny)
    grid = np.full((ny, nx), -np.inf)
    np.maximum.at(grid, (iy[ok], ix[ok]), pts[ok, 2])
    empty = ~np.isfinite(grid)
    if empty.all():
        return None
    # Lücken mit dem nächstgelegenen Messwert füllen
    _, (iyy, ixx) = ndimage.distance_transform_edt(empty, return_indices=True)
    grid = grid[iyy, ixx]
    return ndimage.median_filter(grid, size=3)


def lod2_grid(roofs, shape, x0, y0, res):
    """Dachhöhe des LoD2-Modells je Rasterzelle (NaN außerhalb).

    Zellen, deren Mittelpunkt knapp neben allen Dachflächen liegt (Ränder), werden
    aus der nächstgelegenen Fläche fortgesetzt – aber nur dort, sonst würden
    steile Dachflächen über den First hinaus verlängert.
    """
    ny, nx = shape
    X, Y = np.meshgrid(x0 + (np.arange(nx) + 0.5) * res, y0 + (np.arange(ny) + 0.5) * res)
    z = np.full(shape, -np.inf)
    for grow in (0.0, res):
        z2 = np.full(shape, -np.inf)
        for poly, n, d in roofs:
            inside = shapely.contains_xy(poly.buffer(grow) if grow else poly, X, Y)
            z2[inside] = np.maximum(z2[inside], (d - n[0] * X[inside] - n[1] * Y[inside]) / n[2])
        z = np.where(np.isfinite(z), z, z2)
    return np.where(np.isfinite(z), z, np.nan)


def heightfield_solid(grid, x0, y0, res, s, z_floor=0.0):
    """Geschlossenes Höhenfeld (Zellmittelpunkte als Stützpunkte) in mm."""
    ny, nx = grid.shape
    xs = (x0 + (np.arange(nx) + 0.5) * res) * s
    ys = (y0 + (np.arange(ny) + 0.5) * res) * s
    X, Y = np.meshgrid(xs, ys)
    Z = np.maximum(grid * s, z_floor + 0.05)
    top = np.column_stack([X.ravel(), Y.ravel(), Z.ravel()])
    bot = top.copy()
    bot[:, 2] = z_floor
    verts = np.vstack([top, bot])
    n = nx * ny
    idx = np.arange(n).reshape(ny, nx)
    a, b, c, d = idx[:-1, :-1].ravel(), idx[:-1, 1:].ravel(), idx[1:, 1:].ravel(), idx[1:, :-1].ravel()
    tris = [np.column_stack([a, b, c]), np.column_stack([a, c, d]),            # oben
            np.column_stack([a + n, c + n, b + n]), np.column_stack([a + n, d + n, c + n])]  # unten
    # Rand gegen den Uhrzeigersinn (von oben gesehen), Wände nach außen
    ring = np.concatenate([idx[0, :], idx[1:, -1], idx[-1, -2::-1], idx[-2:0:-1, 0]])
    p, q = ring, np.roll(ring, -1)
    tris += [np.column_stack([p, p + n, q]), np.column_stack([q, p + n, q + n])]
    mesh = m3d.Mesh(vert_properties=verts.astype(np.float32), tri_verts=np.vstack(tris).astype(np.uint32))
    return m3d.Manifold(mesh)


def main_axis(fp):
    """Hauptrichtung des Grundrisses (Grad, 0..90): längengewichtetes Mittel der Kanten mod 90°."""
    ang, w = [], []
    for p in G.polys_of(fp):
        c = np.asarray(p.exterior.coords)
        d = np.diff(c, axis=0)
        ang.append(np.arctan2(d[:, 1], d[:, 0]))
        w.append(np.hypot(d[:, 0], d[:, 1]))
    ang, w = np.concatenate(ang), np.concatenate(w)
    z = (w * np.exp(4j * ang)).sum()  # Richtungen mod 90° als Vektormittel
    return np.degrees(np.angle(z) / 4)


def rot2(xy, deg, c):
    t = np.radians(deg)
    R = np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]])
    return (np.asarray(xy) - c) @ R.T + c


def building_grid(pts, fp, info, theta=0.0):
    """Höhenraster (absolute Höhen, m) eines Gebäudes; fp = Grundriss lokal in m.

    Das Raster ist um `theta` (Grad) gedreht – an der Hauptachse des Gebäudes
    ausgerichtet, damit Kanten und Dachstufen nicht als Treppen im Raster
    erscheinen. Liefert (grid, zl, minx, miny, punkte, c) im gedrehten System
    (Drehung um -theta um den Punkt c); zl = LoD2-Dach im selben Raster.
    """
    from shapely import affinity
    c = np.array(fp.centroid.coords[0])
    near = pts[np.hypot(pts[:, 0] - c[0], pts[:, 1] - c[1]) < fp.hausdorff_distance(fp.centroid) + 3]
    pts = np.column_stack([rot2(near[:, :2], -theta, c), near[:, 2]])
    fp = affinity.rotate(fp, -theta, origin=tuple(c))
    roofs = []
    for poly, n, d in info["roofs"]:
        n2 = np.r_[rot2(n[:2], -theta, 0), n[2]]
        roofs.append((affinity.rotate(poly, -theta, origin=tuple(c)), n2, d - n[:2] @ c + n2[:2] @ c))

    minx, miny, maxx, maxy = fp.buffer(1.0).bounds
    sel = pts[(pts[:, 0] >= minx) & (pts[:, 0] <= maxx) & (pts[:, 1] >= miny) & (pts[:, 1] <= maxy)]
    # nur Punkte im (leicht verkleinerten) Grundriss: keine Fassaden der Nachbarn
    sel = sel[shapely.contains_xy(fp.buffer(-0.3), sel[:, 0], sel[:, 1])]
    grid = height_grid(sel, (minx, miny, maxx, maxy))
    if grid is None:
        return None
    # Deckel aus dem LoD2-Dach: Punkte, die deutlich darüber liegen, gehören zu
    # Nachbargebäuden an der gemeinsamen Grenze (z. B. Giebel des Paulinums).
    # Wo Scan und LoD2-Dach übereinstimmen, die glatte Dachebene nehmen (kein Messrauschen);
    # Abweichungen (Aufbauten, Oberlichter, Höfe, Turmkrone) kommen aus dem Scan.
    zl = lod2_grid(roofs, grid.shape, minx, miny, RASTER)
    has = ~np.isnan(zl)
    zl0 = np.where(has, zl, 0)
    grid[has] = np.minimum(grid[has], zl[has] + LOD2_CAP)
    snap = has & (np.abs(grid - zl0) < LOD2_SNAP)
    grid[snap] = zl[snap]
    # Randzellen, die nur Fassaden- statt Dachpunkte sahen (Kataster-Grundriss etwas
    # größer als die Dachkante), würden als Schlitze in den Wänden erscheinen.
    X, Y = np.meshgrid(minx + (np.arange(grid.shape[1]) + 0.5) * RASTER,
                       miny + (np.arange(grid.shape[0]) + 0.5) * RASTER)
    low = has & (grid < zl0 - LOD2_SNAP)
    edge = low & ~shapely.contains_xy(fp.buffer(-EDGE), X, Y)
    grid[edge] = zl[edge]
    # Schmale Vertiefungen unter dem LoD2-Dach (Rillen hinter der Dachkante, Schlitze
    # zwischen Aufbauten) auffüllen; was eine Öffnung mit NOTCH Durchmesser übersteht
    # (Lichthöfe, Terrassen, Einschnitte), ist echt und bleibt.
    r = int(round(NOTCH / 2 / RASTER))
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    wide = ndimage.binary_opening(low & ~edge, structure=(xx ** 2 + yy ** 2) <= r * r)
    notch = low & ~edge & ~wide
    grid[notch] = zl[notch]
    # schmale Rinnen (1–2 Zellen) schließen: ohnehin nicht druckbar, meist Messlücken
    grid = ndimage.grey_closing(grid, size=3)
    # Zellen außerhalb des Grundrisses = nächste Zelle innen. Sonst interpoliert das Netz
    # an der Dachkante zum (beliebigen) Außenwert, und die Wandoberkante bekommt Kerben.
    inside = shapely.contains_xy(fp, X, Y)
    if inside.any():
        _, (iy, ix) = ndimage.distance_transform_edt(~inside, return_indices=True)
        grid = grid[iy, ix]
    return grid, zl, minx, miny, len(sel), c


def models(s):
    """Volumenkörper (mm), Grundrisse (mm) und Infos je Gebäude-Slug."""
    if not os.path.exists(LAZ_FILE):
        fetch()
    pts = load_points()
    out = {}
    for slug, (_, fp_mm, info) in lod2.models(s).items():
        fp = G.scale_geom(fp_mm, 1.0 / s)  # zurück in m (lokal)
        theta = main_axis(fp)
        res = building_grid(pts, fp, info, theta)
        if res is None:
            continue
        grid, _, minx, miny, npts, c = res
        hf = heightfield_solid(grid - info["ground_z"], minx, miny, RASTER, s).simplify(SIMPLIFY)
        # zurück ins Kartensystem drehen
        hf = hf.translate([-c[0] * s, -c[1] * s, 0]).rotate([0, 0, theta]).translate([c[0] * s, c[1] * s, 0])
        # erst danach ausschneiden, damit die Außenwände exakt eben bleiben
        solid = hf ^ G.extrude(fp_mm, -1, (grid.max() - info["ground_z"]) * s + 1)
        comps = solid.decompose()
        vmax = max(c.volume() for c in comps)
        solid = G.union([c for c in comps if c.volume() > 0.005 * vmax])
        out[slug] = (solid, fp_mm, dict(ground_z=info["ground_z"], punkte=npts, raster_drehung=round(theta, 1)))
    return out


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--extract", help="lokale LAZ-Kachel statt Download verwenden")
    a = ap.parse_args()
    if a.extract:
        extract(a.extract, LAZ_FILE)
    else:
        fetch()
