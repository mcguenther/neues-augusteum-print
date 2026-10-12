#!/usr/bin/env python3
"""Gebäude aus dem 3D-Stadtmodell LoD2 der Stadt Leipzig (CityGML).

Quelle: Stadt Leipzig, Amt für Geoinformation und Bodenordnung,
„3D-Stadtmodell LoD2“ (https://opendata.leipzig.de/dataset/3d-stadtmodell-lod2-stadt-leipzig),
Lizenz: Datenlizenz Deutschland – Namensnennung – 2.0 (dl-de/by-2-0).

Die Gesamtdatei der Stadt (ca. 130 MB) wird nur mit `--fetch` geladen; ins Repo
kommt nur der Ausschnitt mit den Campus-Gebäuden (`data/lod2_campus.gml`).

Die LoD2-Gebäude sind anders zugeschnitten als in OSM (z. B. ist der ganze
Komplex Paulinum + Neues Augusteum + Hörsaalgebäude ein einziges Gebäude mit
47 Bauteilen). Deshalb wird jedes Modell entlang der OSM-Grundrisse auf die
Gebäude in `generate.BUILDINGS` aufgeteilt.

Volumenkörper: Jede Dachfläche wird als Prisma vom Boden bis zur Dachebene
extrudiert, alle Prismen werden vereinigt (LoD2 ist 2,5D, das ergibt genau das
Gebäudevolumen und ist robust gegen kleine Lücken zwischen den Flächen).
"""
import io
import math
import os
import urllib.request
import zipfile

import numpy as np
import pyproj
import shapely
from lxml import etree
from shapely.geometry import Polygon
from shapely.ops import unary_union

import generate as G

LOD2_URL = ("https://geodaten.leipzig.de/open_data/organisationseinheit/"
            "Amt_fuer_Geoinformation_und_Bodenordnung/3d/LoD2/GEB3D_Leipzig_LoD2_CityGML.zip")
LOD2_MEMBER = "GEB3D_Leipzig_LoD2_00_Zentrum.gml"
LOD2_FILE = os.path.join(G.HERE, "data", "lod2_campus.gml")
ATTRIBUTION = "3D-Stadtmodell LoD2 © Stadt Leipzig (dl-de/by-2-0)"

NS = {"gml": "http://www.opengis.net/gml",
      "bldg": "http://www.opengis.net/citygml/building/1.0",
      "gen": "http://www.opengis.net/citygml/generics/1.0",
      "core": "http://www.opengis.net/citygml/1.0"}
BLDG = "{%s}" % NS["bldg"]
GML = "{%s}" % NS["gml"]

_to_ll = pyproj.Transformer.from_crs(25833, 4326, always_xy=True)
_to_utm = pyproj.Transformer.from_crs(4326, 25833, always_xy=True)


def utm_to_local(x, y):
    lon, lat = _to_ll.transform(np.asarray(x), np.asarray(y))
    return G.project(lon, lat)


def local_to_utm(x, y):
    lon0, lat0 = G.ORIGIN
    lon = lon0 + np.asarray(x) / (111320.0 * math.cos(math.radians(lat0)))
    lat = lat0 + np.asarray(y) / 110540.0
    return _to_utm.transform(lon, lat)


def osm_outlines_local():
    feats = G.load_features()
    out = {}
    for b in G.BUILDINGS:
        outline, parts = G.building_parts(feats, b["osm"])
        out[b["slug"]] = unary_union([outline] + [p for p, _, _ in parts]).buffer(0)
    return out


# --------------------------------------------------------------------------
# Laden / Ausschnitt
# --------------------------------------------------------------------------
def rings(el):
    """Alle Polygone (Außenring, [Innenringe]) unterhalb von el als (n,3)-Arrays."""
    for poly in el.iter(GML + "Polygon"):
        def ring(r):
            v = np.array(r.findtext(".//gml:posList", namespaces=NS).split(), float)
            return v.reshape(-1, 3)
        ext = poly.find("gml:exterior/gml:LinearRing", NS)
        if ext is None:
            continue
        yield ring(ext), [ring(i) for i in poly.findall("gml:interior/gml:LinearRing", NS)]


def ground_footprint_utm(bel):
    polys = []
    for gs in bel.iter(BLDG + "GroundSurface"):
        for ext, ints in rings(gs):
            p = Polygon(ext[:, :2], [i[:, :2] for i in ints]).buffer(0)
            if not p.is_empty:
                polys.append(p)
    return unary_union(polys) if polys else None


def fetch_lod2():
    """Lädt das Stadtmodell und speichert die Campus-Gebäude nach data/lod2_campus.gml."""
    print("Lade", LOD2_URL)
    with urllib.request.urlopen(LOD2_URL, timeout=600) as r:
        data = r.read()
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        gml = z.read(LOD2_MEMBER)
    extract(io.BytesIO(gml), LOD2_FILE)


def extract(src, dst):
    """Schreibt alle LoD2-Gebäude, die einen OSM-Grundriss aus BUILDINGS berühren."""
    osm = {k: shapely.transform(g, lambda a: np.column_stack(local_to_utm(a[:, 0], a[:, 1])))
           for k, g in osm_outlines_local().items()}
    keep = []
    for _, el in etree.iterparse(src, tag=BLDG + "Building"):
        fp = ground_footprint_utm(el)
        if fp is not None and any(fp.intersection(g).area > 20 for g in osm.values()):
            keep.append(etree.tostring(el))
        el.clear()
    root = etree.Element("{%s}CityModel" % NS["core"], nsmap={
        "core": NS["core"], "bldg": NS["bldg"], "gml": NS["gml"], "gen": NS["gen"],
        "xlink": "http://www.w3.org/1999/xlink"})
    etree.SubElement(root, GML + "description").text = (
        "Ausschnitt aus dem 3D-Stadtmodell LoD2 der Stadt Leipzig (%s), "
        "Lizenz dl-de/by-2-0, Namensnennung: Stadt Leipzig. CRS EPSG:25833 + DHHN2016." % LOD2_MEMBER)
    for k in keep:
        m = etree.SubElement(root, "{%s}cityObjectMember" % NS["core"])
        m.append(etree.fromstring(k))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    etree.ElementTree(root).write(dst, xml_declaration=True, encoding="UTF-8", pretty_print=True)
    print("  %d LoD2-Gebäude -> %s" % (len(keep), os.path.relpath(dst, G.HERE)))


# --------------------------------------------------------------------------
# Geometrie
# --------------------------------------------------------------------------
def load_lod2():
    """Liefert Liste von Gebäuden: dict(id, attrs, roofs=[(ring_local(n,3), [inner...])], ground_z)."""
    out = []
    for _, el in etree.iterparse(LOD2_FILE, tag=BLDG + "Building"):
        attrs = {a.get("name"): a.findtext("gen:value", namespaces=NS)
                 for a in el.findall("gen:stringAttribute", NS)}
        roofs, gz = [], []
        for rs in el.iter(BLDG + "RoofSurface"):
            for ext, ints in rings(rs):
                roofs.append((to_local3(ext), [to_local3(i) for i in ints]))
        for gs in el.iter(BLDG + "GroundSurface"):
            for ext, _ in rings(gs):
                gz.append(ext[:, 2].min())
        out.append(dict(id=el.get(GML + "id"), attrs=attrs, roofs=roofs,
                        ground_z=min(gz) if gz else min(r[:, 2].min() for r, _ in roofs)))
    return out


def to_local3(a):
    x, y = utm_to_local(a[:, 0], a[:, 1])
    return np.column_stack([x, y, a[:, 2]])


def plane(ring):
    """Normale (Newell) und Abstand der Ebene durch einen 3D-Ring."""
    p = ring[:-1] if np.allclose(ring[0], ring[-1]) else ring
    q = np.roll(p, -1, axis=0)
    n = np.array([((p[:, 1] - q[:, 1]) * (p[:, 2] + q[:, 2])).sum(),
                  ((p[:, 2] - q[:, 2]) * (p[:, 0] + q[:, 0])).sum(),
                  ((p[:, 0] - q[:, 0]) * (p[:, 1] + q[:, 1])).sum()])
    ln = np.linalg.norm(n)
    if ln < 1e-9:
        return None, None
    n = n / ln
    if n[2] < 0:
        n = -n
    return n, n @ p.mean(axis=0)


def roof_prism(poly, n, d, ztop, z_ground, s):
    """Prisma vom Boden bis zur Dachebene n·p = d unter dem Grundriss `poly` (lokal, m) -> mm."""
    geom = G.clean(G.scale_geom(poly.buffer(0.02, join_style=2), s))
    if geom.is_empty:
        return None
    body = G.extrude(geom, 0, (max(ztop, z_ground) - z_ground) * s + 1)
    # Ebene in mm relativ zum Boden: n·p_mm = (d - n_z * z_ground) * s
    off = (d - n[2] * z_ground) * s
    return body.trim_by_plane([-n[0], -n[1], -n[2]], -off)


def partition(outlines, lod2_fps, grow_step=0.5, grow_max=6.0):
    """Teilt die LoD2-Grundflächen entlang der OSM-Grundrisse auf die Gebäude auf.

    Jedes LoD2-Gebäude wird nur den OSM-Gebäuden zugeschlagen, mit denen es sich
    deutlich überlappt. Innerhalb davon zählt zuerst der OSM-Grundriss, Reste
    (Abweichungen der Kartengrundlagen) wachsen schrittweise dem nächsten Gebäude zu.
    """
    cells = {k: [] for k in outlines}
    for fp in lod2_fps:
        match = [k for k, g in outlines.items()
                 if fp.intersection(g).area > 0.2 * min(fp.area, g.area)]
        if not match:
            continue
        own = {k: fp.intersection(outlines[k]) for k in match}
        taken = unary_union(list(own.values()))
        for _ in range(int(grow_max / grow_step)):
            if fp.difference(taken).area < 0.01:
                break
            for k in match:
                grow = fp.intersection(own[k].buffer(grow_step, join_style=2)).difference(taken)
                if grow.area > 0:
                    own[k] = own[k].union(grow)
                    taken = taken.union(grow)
        for k in match:
            cells[k].append(own[k])
    return {k: unary_union(c).buffer(0.05, join_style=2).buffer(-0.05, join_style=2)
            for k, c in cells.items() if c}


def thin(p, width=1.0):
    return 2 * p.area / max(p.length, 1e-9) < width


def models(s, min_share=0.25):
    """Volumenkörper (mm), Grundrisse (mm) und Infos je Gebäude-Slug.

    Dachflächen werden an den Zellgrenzen geschnitten; kleine oder schmale
    Abschnitte (< min_share der Fläche bzw. < 1 m breit) bleiben aber beim
    Gebäude, dem der größte Teil der Dachfläche gehört – sonst entstehen an den
    Grenzen dünne Grate (z. B. Giebel des Paulinums über dem Augusteum).
    """
    if not os.path.exists(LOD2_FILE):
        fetch_lod2()
    blds = load_lod2()
    outlines = osm_outlines_local()
    for b in blds:
        b["fp"] = unary_union([Polygon(r[:, :2]).buffer(0) for r, _ in b["roofs"]]).buffer(0.01)
    cells = partition(outlines, [b["fp"] for b in blds])
    assigned = {k: [] for k in cells}
    for b in blds:
        for ext, ints in b["roofs"]:
            n, d = plane(ext)
            if n is None or n[2] < 0.05:  # senkrechte Flächen tragen nichts bei
                continue
            poly = Polygon(ext[:, :2], [i[:, :2] for i in ints]).buffer(0)
            pieces = {k: poly.intersection(c) for k, c in cells.items()}
            pieces = {k: p for k, p in pieces.items() if p.area > 0.05}
            if not pieces:
                continue
            major = max(pieces, key=lambda k: pieces[k].area)
            for k in list(pieces):
                if k != major and (pieces[k].area < min_share * poly.area or thin(pieces[k])):
                    pieces[major] = pieces[major].union(pieces.pop(k))
            for k, p in pieces.items():
                assigned[k].append((p, n, d, ext[:, 2].max(), b))
    out = {}
    for slug, roofs in assigned.items():
        if not roofs:
            continue
        mine = {id(b): b for *_, b in roofs}.values()
        zg = min(b["ground_z"] for b in mine)
        solid = G.union([roof_prism(p, n, d, zt, zg, s) for p, n, d, zt, _ in roofs])
        comps = solid.decompose()
        vmax = max(c.volume() for c in comps)
        solid = G.union([c for c in comps if c.volume() > 0.005 * vmax])  # Splitter weg
        fp = unary_union([p for p, *_ in roofs]).buffer(0.05, join_style=2).buffer(-0.05, join_style=2)
        out[slug] = (solid, G.scale_geom(fp, s),
                     dict(ground_z=zg, lod2_ids=sorted(b["id"] for b in mine),
                          attrs=[b["attrs"] for b in mine],
                          roofs=[(p, n, d) for p, n, d, *_ in roofs]))
    return out


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--extract", help="lokale Zentrum-GML statt Download verwenden")
    a = ap.parse_args()
    if a.extract:
        extract(a.extract, LOD2_FILE)
    else:
        fetch_lod2()
