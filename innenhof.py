#!/usr/bin/env python3
"""Innenhof des Campus (Leibnizforum): Pflaster, Beete, Sitzpodeste, Bänke,
Leibnizdenkmal und Bäume als eigenes Druckteil.

Geometrie: data/innenhof.json. Die Objekte (Lage, Größe, Höhe) sind im Laserscan
GeoSN 2023 gemessen (werkzeuge/innenhof_messen.py), die Hoffläche ist die
Fußgängerfläche aus OSM abzüglich der Gebäudegrundrisse, die Pflasterflächen
(Platz, Fläche ums Denkmal) sind im Luftbild 2024 abgegrenzt.

Höhenlage: Der Hof liegt 2,3 m über dem Straßenniveau, auf dem die Gebäude
stehen (19 Stufen hinab zur Grimmaischen Straße). Das Druckteil ist deshalb ein
Podest: Platte von POCKET_DEPTH unter der Oberkante der Sockel-/Grundplatte bis
zum Hofboden, darauf die Objekte. In der Grundplatte steckt es in der
Aussparung, im Komplettmodell ist es in die Sockelplatte eingelassen.
Kleine Objekte werden auf druckbare Breite (MIN_FEATURE) und Mindesthöhe
(MIN_HOEHE) gebracht; Baumkronen haben unten höchstens 45° Überhang.

Farben: data/fassaden/08_innenhof.json. Statt Fassaden-Zonen ordnen die
"zonen" dort jedem Teil (Feld "teil", siehe TEILE) eine Farbe zu.
"""
import json
import math
import os

import manifold3d as m3d
import numpy as np
import shapely
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

import generate as G

SLUG = "08_innenhof"
DATA = os.path.join(G.HERE, "data", "innenhof.json")
HOF_WAY = "118176611"   # OSM highway=pedestrian, area=yes: Innenhof mit Passagen
MIN_HOEHE = 0.4         # mm, flachere Objekte werden darauf angehoben (2 Schichten)
ROOF_NZ = G.ROOF_NZ

# Teile, denen data/fassaden/08_innenhof.json Farben zuordnet
TEILE = ["pflaster", "platz", "denkmalplatz", "beet", "beet_rand", "podest", "bank",
         "sockel", "bronze", "stamm", "krone"]


def load():
    return json.load(open(DATA))


def hof_polygon_local():
    """Fußgängerfläche des Innenhofs aus OSM (lokal, m)."""
    import xml.etree.ElementTree as ET
    root = ET.parse(G.OSM_FILE).getroot()
    nodes = {n.get("id"): G.project(float(n.get("lon")), float(n.get("lat"))) for n in root.findall("node")}
    w = root.find("way[@id='%s']" % HOF_WAY)
    return Polygon([nodes[nd.get("ref")] for nd in w.findall("nd")]).buffer(0)


def achse(data):
    """Einheitsvektoren entlang (t, nach Norden) und quer (u, nach Osten) zur Hofachse."""
    a = math.radians(data["achse_grad"])
    d = np.array([math.sin(a), math.cos(a)])
    return d, np.array([d[1], -d[0]])


def rechteck(o, data):
    """Grundriss eines Objekts (lokal, m): Rechteck entlang der Hofachse."""
    d, n = achse(data)
    c = np.asarray(o["mitte"], float)
    hl, hb = o["laenge"] / 2, o["breite"] / 2
    return Polygon([c - hl * d - hb * n, c + hl * d - hb * n, c + hl * d + hb * n, c - hl * d + hb * n])


def flaeche_mm(building_fps_mm, s):
    """Hoffläche (mm): OSM-Fläche ∩ Hofgrenze (Scan) minus Gebäude, mit Fuge für die Grundplatte."""
    data = load()
    hof = hof_polygon_local().intersection(Polygon(data["grenze"]).union(Polygon(data["terrasse"])))
    hof = G.scale_geom(hof, s)
    blds = unary_union(list(building_fps_mm)).buffer(2 * G.POCKET_CLEARANCE, join_style=2)
    rest = hof.difference(blds)
    rest = rest.buffer(-0.5, join_style=2).buffer(0.5, join_style=2)  # Splitter und Stege entfernen
    polys = G.polys_of(rest)
    big = max(p.area for p in polys)
    return G.clean(unary_union([p for p in polys if p.area > 0.05 * big]))


def widen(poly_m, s):
    """Grundriss in mm, mindestens MIN_FEATURE breit."""
    p = G.scale_geom(poly_m, s)
    w = 2 * p.area / max(p.length, 1e-9)
    if w < G.MIN_FEATURE:
        p = p.buffer((G.MIN_FEATURE - w) / 2, join_style=2)
    return p


def prism(poly_mm, h_mm):
    return G.extrude(poly_mm, 0, max(h_mm, MIN_HOEHE))


def square(c, a):
    return box(c[0] - a / 2, c[1] - a / 2, c[0] + a / 2, c[1] + a / 2)


def rotated_square(c, a, data):
    return rechteck(dict(mitte=c, laenge=a, breite=a), data)


def denkmal(o, s, data):
    """Leibnizdenkmal: Granitsockel, Bronze-Postament, stehende Figur (verjüngter Pfeiler)."""
    c = o["mitte"]
    sockel = G.scale_geom(rotated_square(c, o["sockel_breite"], data), s)
    post = widen(rotated_square(c, o["postament_breite"], data), s)
    fig_b = max(o["figur_breite"] * s, G.MIN_FEATURE)
    z1, z2, z3 = o["sockel_hoehe"] * s, o["postament_hoehe"] * s, o["hoehe"] * s
    fig = m3d.Manifold.extrude(m3d.CrossSection.square([fig_b, fig_b], True), z3 - z2 + 0.01,
                               scale_top=[0.7, 0.7])
    cx, cy = c[0] * s, c[1] * s
    fig = fig.rotate([0, 0, -data["achse_grad"]]).translate([cx, cy, z2 - 0.01])
    return G.union([G.extrude(sockel, 0, z1), G.extrude(post, z1 - 0.01, z2), fig])


def baum(o, s):
    """Baum: Stamm + Krone als Drehkörper; unten Kegel mit 45° (stützenfrei druckbar)."""
    R = o["krone_radius"] * s
    top = o["hoehe"] * s
    zb = o["krone_unten"] * s
    r0 = max(o.get("stamm_radius", 0.2) * s, G.MIN_FEATURE / 2)
    zm = min(zb + R - r0, top - 0.3 * R)  # breiteste Stelle
    zb = zm - (R - r0)
    prof = [(0, zb - 0.01), (r0, zb - 0.01), (R, zm), (R * 0.92, zm + 0.35 * (top - zm)),
            (R * 0.6, zm + 0.75 * (top - zm)), (0, top)]
    crown = m3d.Manifold.revolve(m3d.CrossSection([np.asarray(prof)]), 32)
    stem = m3d.Manifold.cylinder(zb + 0.02, r0, r0, 16)
    cx, cy = o["mitte"][0] * s, o["mitte"][1] * s
    return (crown + stem).translate([cx, cy, 0])


def probe_polygon(p):
    """Messfläche im Luftbild (lokal, m) für farben.dop_probe:
    {"polygon": [[x, y], ...]}, {"objekt": "beet"|"podest"|"bank"|"baum"|"denkmal"} (alle
    Objekte dieses Typs, verkleinert) oder {"flaeche": "platz"|"denkmalplatz"|"rand"|"terrasse"}
    (ohne Objekte, Baumkronen und 1 m Abstand zu Gebäuden)."""
    if "polygon" in p:
        return Polygon(p["polygon"])
    data = load()
    objs = data["objekte"]
    if "objekt" in p:
        polys = []
        for o in objs:
            if o["typ"] != p["objekt"]:
                continue
            if o["typ"] == "baum":
                polys.append(shapely.Point(o["mitte"]).buffer(0.7 * o["krone_radius"]))
            elif o["typ"] == "denkmal":
                polys.append(rotated_square(o["mitte"], o["postament_breite"], data))
            else:
                polys.append(rechteck(o, data).buffer(-0.4 if o["typ"] != "bank" else -0.2, join_style=2))
        return unary_union(polys)
    belegt = unary_union([shapely.Point(o["mitte"]).buffer(o["krone_radius"] + 0.5) if o["typ"] == "baum"
                          else rechteck(o, data).buffer(1.0) if o["typ"] != "denkmal"
                          else rotated_square(o["mitte"], o["sockel_breite"] + 0.6, data) for o in objs])
    hof = Polygon(data["grenze"]).buffer(-1.0)
    terr = Polygon(data["terrasse"])
    platz, dplatz = Polygon(data["flaechen"]["platz"]), Polygon(data["flaechen"]["denkmalplatz"])
    f = {"platz": platz.buffer(-0.5).difference(dplatz.buffer(0.5)).intersection(hof),
         "denkmalplatz": dplatz.buffer(-0.3),
         "terrasse": terr.buffer(-1.0),
         "rand": hof.difference(platz.buffer(0.5)).difference(terr.buffer(0.5))}[p["flaeche"]]
    return f.difference(belegt) if p["flaeche"] != "denkmalplatz" else f.difference(belegt.intersection(
        rotated_square(next(o for o in objs if o["typ"] == "denkmal")["mitte"], 3.0, data)))


def teil_polygone(data, s):
    """Grundrisse (mm) der Teile für die Einfärbung: [(typ, Polygon, Objekt)]."""
    out = []
    for o in data["objekte"]:
        typ = o["typ"]
        if typ in ("beet", "podest", "bank"):
            poly = widen(rechteck(o, data), s).buffer(0.05)
        elif typ == "denkmal":
            poly = G.scale_geom(rotated_square(o["mitte"], o["sockel_breite"], data), s).buffer(0.6)
        elif typ == "baum":
            poly = G.scale_geom(shapely.Point(o["mitte"]).buffer(o["krone_radius"]), s).buffer(0.3)
        else:
            continue
        out.append((typ, poly, o))
    return out


def hub(data, s):
    """Höhe des Hofbodens über der Sockelplatte (mm): Hof über dem Gebäudesockel (Straßenniveau)."""
    return (data["boden_z"] - data["sockel_z"]) * s


def model(s, building_fps_mm):
    """(Volumenkörper mm, Grundriss mm, Info): Platte von -POCKET_DEPTH bis zum Hofboden (hub),
    Objekte darauf."""
    data = load()
    fp = flaeche_mm(building_fps_mm, s)
    T = G.POCKET_DEPTH
    H = hub(data, s)
    # Pflaster aus getrennten Feldern, damit die Dreiecke an den Farbgrenzen enden
    felder = [G.scale_geom(Polygon(data["flaechen"][k]), s) for k in ("denkmalplatz", "platz")]
    rest, slabs = fp, []
    for f in felder:
        part = G.clean(rest.intersection(f))
        rest = G.clean(rest.difference(f))
        if not part.is_empty:
            slabs.append(G.extrude(part, -T, H))
    slabs.append(G.extrude(rest, -T, H))
    solids = [prism(G.clean(fp.intersection(G.scale_geom(Polygon(data["terrasse"]), s))),
                    data["terrasse_hoehe"] * s)]
    for o in data["objekte"]:
        typ = o["typ"]
        if typ in ("beet", "podest", "bank"):
            solids.append(prism(widen(rechteck(o, data), s), o["hoehe"] * s))
        elif typ == "denkmal":
            solids.append(denkmal(o, s, data))
        elif typ == "baum":
            solids.append(baum(o, s))
    objs = G.union(solids)
    # nichts über den Hofrand hinaus (Kronen über Gebäuden), sonst passt die Grundplatte nicht
    zmax = max(o.get("hoehe", 1) for o in data["objekte"]) * s + 2
    objs = objs ^ G.extrude(fp.buffer(-0.05, join_style=2), -0.5, zmax)
    solid = G.union(slabs + [objs.translate([0, 0, H - 0.01])])
    counts = {}
    for o in data["objekte"]:
        counts[o["typ"]] = counts.get(o["typ"], 0) + 1
    return solid, fp, dict(objekte=" ".join("%s×%d" % kv for kv in counts.items()),
                           flaeche_m2=round(fp.area / s / s))


def colour_mesh(tm, to_local, eintrag):
    """Hex-Farbe je Dreieck. tm in Modellkoordinaten (mm), to_local = (offset[3], s)."""
    data = load()
    off, s = np.asarray(to_local[0], float), float(to_local[1])
    farbe = {z["teil"]: eintrag["farben"][z["farbe"]]["rgb"] for z in eintrag.get("zonen", [])}
    basis = eintrag["farben"][eintrag["basis"]]["rgb"]
    cen = (tm.triangles.mean(axis=1) - off) - [0, 0, hub(data, s)]  # mm, z über dem Hofboden
    nz = tm.face_normals[:, 2]
    keys = np.array(["pflaster"] * len(cen), dtype=object)
    for k in ("platz", "denkmalplatz"):
        keys[shapely.contains_xy(G.scale_geom(Polygon(data["flaechen"][k]), s), cen[:, 0], cen[:, 1])] = k
    oben = cen[:, 2] > 1e-3
    for typ, poly, o in teil_polygone(data, s):
        sel = oben & shapely.contains_xy(poly, cen[:, 0], cen[:, 1])
        if typ == "beet":
            keys[sel] = "beet_rand"
            keys[sel & (nz > 0.9)] = "beet"
        elif typ == "denkmal":
            keys[sel] = "bronze"
            keys[sel & (cen[:, 2] < o["sockel_hoehe"] * s + 1e-3)] = "sockel"
        elif typ == "baum":
            keys[sel] = "krone"
            r = np.hypot(cen[:, 0] - o["mitte"][0] * s, cen[:, 1] - o["mitte"][1] * s)
            r0 = max(o.get("stamm_radius", 0.2) * s, G.MIN_FEATURE / 2) + 0.05
            keys[sel & (r <= r0) & (np.abs(nz) < 0.5)] = "stamm"
        else:
            keys[sel] = typ
    return np.array([farbe.get(k, basis) for k in keys], dtype=object)
