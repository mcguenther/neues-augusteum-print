#!/usr/bin/env python3
"""Misst die Objekte im Innenhof im Laserscan und schreibt data/innenhof.json.

Verfahren: Höhenraster (höchster Punkt je 0,25-m-Zelle, Median 3×3) relativ zum
Hofboden. Zusammenhängende Flächen 0,25–1,5 m über dem Boden sind Beete,
Sitzpodeste oder Bänke (nach Grundfläche), gemessen als Rechteck entlang der
Hofachse. Denkmal und Bäume werden an ihren OSM-Positionen aus den Punkten in
der Umgebung bestimmt. Laternen (dünn, kaum Fläche) fallen heraus.

Die Hofgrenze ist die zusammenhängende Fläche auf Hofniveau (±0,2 m) innerhalb der
OSM-Fußgängerfläche; die höher liegenden Passagen (z. B. zur Universitätsstraße,
+0,75 m) gehören nicht dazu. Die Terrasse vor Hörsaal- und Seminargebäude (Treppe
hinab in den Hof) kommt als eigene Stufe dazu, bis TERRASSE_YMIN.

Nicht gemessen, sondern hier festgelegt (mit Begründung im JSON):
  - Hofachse: Richtung der Beetreihen
  - Pflasterflächen: im Luftbild 2024 abgegrenzt (heller Rand, dunklerer Platz,
    helle Fläche ums Denkmal)
  - Gliederung des Denkmals (Sockel/Postament/Figur), Höhen aus dem Scan

Aufruf: python3 werkzeuge/innenhof_messen.py
"""
import json
import math
import os
import sys

import laspy
import numpy as np
import shapely
from scipy import ndimage

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import generate as G  # noqa: E402
import innenhof  # noqa: E402
import laserscan  # noqa: E402
import lod2  # noqa: E402

RES = 0.25
MIN_H, MAX_H = 0.25, 1.5   # m über Boden: Stadtmöbel
ACHSE_GRAD = 11.8          # Richtung der Beetreihen (Kompass, Grad)
SOCKEL_Z = 114.46          # m ü. NHN: Gelände der umgebenden Gebäude im LoD2 (Paulinum, Augusteum,
                           # Hörsaalgebäude) = Straßenniveau, auf dem die Gebäudemodelle stehen
TERRASSE_H = 0.75          # m, Terrasse vor Hörsaal-/Seminargebäude (Startwert, wird gemessen)
TERRASSE_YMIN = -4.0       # m (lokal): südlich davon beginnt die Passage zur Universitätsstraße


def osm_punkte():
    import xml.etree.ElementTree as ET
    root = ET.parse(G.OSM_FILE).getroot()
    out = []
    for n in root.findall("node"):
        t = {x.get("k"): x.get("v") for x in n.findall("tag")}
        if t.get("natural") == "tree" or t.get("historic") == "memorial":
            out.append((G.project(float(n.get("lon")), float(n.get("lat"))), t))
    return out


def raster_polygon(mask, minx, miny):
    rows = []
    for r in range(mask.shape[0]):
        cols = np.flatnonzero(np.diff(np.r_[0, mask[r].astype(int), 0]))
        for c0, c1 in zip(cols[::2], cols[1::2]):
            rows.append(shapely.box(minx + c0 * RES, miny + r * RES, minx + c1 * RES, miny + (r + 1) * RES))
    return shapely.unary_union(rows).buffer(0.3).buffer(-0.3).simplify(0.4)


def in_achse(p, o, d, n):
    q = np.asarray(p) - o
    return q @ d, q @ n


def main():
    las = laspy.read(laserscan.LAZ_FILE)
    x, y = lod2.utm_to_local(np.asarray(las.x), np.asarray(las.y))
    z = np.asarray(las.z)
    hof = innenhof.hof_polygon_local()
    sel = shapely.contains_xy(hof.buffer(6), x, y)
    x, y, z = x[sel], y[sel], z[sel]
    ground = np.asarray(las.classification)[sel] == laserscan.GROUND_CLASS
    inner = shapely.contains_xy(hof.buffer(-3), x, y)
    z0 = float(np.median(z[ground & inner]))
    print("Hofboden: %.2f m ü. NHN (%d Bodenpunkte)" % (z0, (ground & inner).sum()))

    # Höhenraster
    minx, miny, maxx, maxy = hof.bounds
    nx, ny = int((maxx - minx) / RES) + 1, int((maxy - miny) / RES) + 1
    ix, iy = ((x - minx) / RES).astype(int), ((y - miny) / RES).astype(int)
    ok = (ix >= 0) & (ix < nx) & (iy >= 0) & (iy < ny)
    grid = np.full((ny, nx), -np.inf)
    np.maximum.at(grid, (iy[ok], ix[ok]), z[ok])
    empty = ~np.isfinite(grid)
    _, (a, b) = ndimage.distance_transform_edt(empty, return_indices=True)
    h = ndimage.median_filter(grid[a, b], 3) - z0
    X, Y = np.meshgrid(minx + (np.arange(nx) + 0.5) * RES, miny + (np.arange(ny) + 0.5) * RES)
    flach = shapely.contains_xy(hof.buffer(-1.0), X, Y)

    a = math.radians(ACHSE_GRAD)
    d, n = np.array([math.sin(a), math.cos(a)]), np.array([math.cos(a), -math.sin(a)])
    objekte = []
    special = osm_punkte()
    near_special = np.zeros_like(flach)
    for (px, py), t in special:
        near_special |= np.hypot(X - px, Y - py) < (2.0 if t.get("historic") else 4.5)
    lab, cnt = ndimage.label(flach & ~near_special & (h > MIN_H) & (h < MAX_H))
    moebel = np.zeros_like(flach)
    for i in range(1, cnt + 1):
        m = lab == i
        area = m.sum() * RES * RES
        hm = float(np.median(h[m]))
        if area < 1.2 or area > 40 or (area < 7 and hm > 0.55):
            continue  # Laternenfüße/Poller, Geländestufen (Passagen), Mauern/Geländer
        P = np.column_stack([X[m], Y[m]])
        c = P.mean(axis=0)
        t, u = in_achse(P, c, d, n)
        moebel |= m
        (t0, t1), (u0, u1) = np.percentile(t, [1, 99]), np.percentile(u, [1, 99])
        L, B = t1 - t0 + RES, u1 - u0 + RES
        mitte = c + d * (t0 + t1) / 2 + n * (u0 + u1) / 2
        typ = "beet" if area > 15 else ("podest" if area > 7 else "bank")
        objekte.append(dict(typ=typ, mitte=[round(float(v), 2) for v in mitte], laenge=round(float(L), 2),
                            breite=round(float(B), 2), hoehe=round(hm, 2), flaeche_m2=round(float(area), 1)))
    # Bäume und Denkmal an den OSM-Positionen
    above = z - z0
    for (px, py), t in special:
        if not hof.contains(shapely.Point(px, py)):
            continue
        r = np.hypot(x - px, y - py)
        if t.get("natural") == "tree":
            k = (r < 6) & (above > 2.0) & ~ground
            if k.sum() < 20:
                continue
            cx, cy = x[k].mean(), y[k].mean()
            rr = np.hypot(x[k] - cx, y[k] - cy)
            objekte.append(dict(typ="baum", art=t.get("species", ""), mitte=[round(float(cx), 2), round(float(cy), 2)],
                                hoehe=round(float(np.percentile(above[k], 99)), 1),
                                krone_radius=round(float(np.percentile(rr, 85)), 1),
                                krone_unten=round(float(np.percentile(above[k], 5)), 1), stamm_radius=0.2,
                                punkte=int(k.sum())))
        elif t.get("historic") == "memorial":
            k = (r < 2.0) & (above > 0.3)
            hk = above[k]
            post = k & (above > 1.5)
            cx, cy = np.median(x[post]), np.median(y[post])
            objekte.append(dict(typ="denkmal", name=t.get("name", ""), mitte=[round(float(cx), 2), round(float(cy), 2)],
                                hoehe=round(float(hk.max()), 2),
                                postament_hoehe=round(float(np.median(hk[(hk > 2.0) & (hk < 3.5)])), 2),
                                sockel_hoehe=0.6, sockel_breite=2.4, postament_breite=1.4, figur_breite=0.9,
                                punkte=int(k.sum())))
    # Hofgrenze: zusammenhängende Fläche auf Hofniveau (ohne die höher liegenden Passagen)
    level = np.abs(h) < 0.2
    for o in objekte:
        if o["typ"] == "baum":  # unter den Kronen misst der Scan die Krone, nicht den Boden
            level |= np.hypot(X - o["mitte"][0], Y - o["mitte"][1]) < 2.0
    level |= moebel
    level = ndimage.binary_closing(level, iterations=4) & shapely.contains_xy(hof, X, Y)
    reg, _ = ndimage.label(level)
    level = ndimage.binary_fill_holes(reg == np.bincount(reg[reg > 0]).argmax())
    level = ndimage.binary_opening(level, iterations=4)  # schmale Ausläufer weg
    grenze = max(innenhof.G.polys_of(raster_polygon(level, minx, miny)), key=lambda p: p.area)
    print("Hofgrenze: %.0f m² (OSM-Fläche %.0f m²)" % (grenze.area, hof.area))
    # Terrasse vor Hörsaal- und Seminargebäude (Treppe hinab in den Hof), ohne die Passage nach Südwesten
    nahe = ndimage.binary_dilation(level, iterations=3)
    cand = ~level & shapely.contains_xy(hof, X, Y) & (Y > TERRASSE_YMIN)
    th = float(np.median(h[nahe & cand & (np.abs(h - TERRASSE_H) < 0.2)]))
    tl, _ = ndimage.label(ndimage.binary_closing(cand & (np.abs(h - th) < 0.2), iterations=2))
    terr = np.isin(tl, np.unique(tl[nahe & (tl > 0)]))
    terr = ndimage.binary_opening(ndimage.binary_closing(terr, iterations=2), iterations=2)
    terrasse = raster_polygon(terr, minx, miny).buffer(RES)  # überlappt den Hof um eine Zelle
    terrasse = max(innenhof.G.polys_of(terrasse), key=lambda p: p.area)
    print("Terrasse: %.0f m², %.2f m über dem Hof" % (terrasse.area, th))

    objekte.sort(key=lambda o: ("beet podest bank denkmal baum".split().index(o["typ"]), -o["mitte"][1]))

    data = json.load(open(innenhof.DATA)) if os.path.exists(innenhof.DATA) else {}
    data.update({
        "_hinweis": "Erzeugt von werkzeuge/innenhof_messen.py (Objekte); 'flaechen' und die "
                    "Gliederung des Denkmals sind von Hand festgelegt. Koordinaten lokal in m "
                    "(generate.project), Höhen in m über dem Hofboden. laenge = entlang der Hofachse.",
        "quelle": "Laserscan GeoSN, Befliegung 9. 1. 2023 (dl-de/by-2-0); Luftbild 2024 © Stadt Leipzig "
                  "(dl-de/by-2-0); Semantik (Bäume, Denkmal, Hoffläche) © OpenStreetMap-Mitwirkende (ODbL)",
        "boden_z": round(z0, 2),
        "sockel_z": SOCKEL_Z,
        "achse_grad": ACHSE_GRAD,
        "grenze": [[round(float(a), 2), round(float(b), 2)] for a, b in grenze.exterior.coords[:-1]],
        "terrasse": [[round(float(a), 2), round(float(b), 2)] for a, b in terrasse.exterior.coords[:-1]],
        "terrasse_hoehe": round(float(th), 2),
        "objekte": objekte,
    })
    with open(innenhof.DATA, "w") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
    for o in objekte:
        print("  %-7s %s" % (o["typ"], {k: v for k, v in o.items() if k != "typ"}))
    print("->", os.path.relpath(innenhof.DATA, G.HERE))


if __name__ == "__main__":
    main()
