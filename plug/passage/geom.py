#!/usr/bin/env python3
"""Durchgang zwischen Paulinum und Institutsgebäude: Geometrie des Vorschlags (Laserscan, noch nicht im Generator).

Befund: Zwischen Paulinum und Institutsgebäude führt ein überdeckter Durchgang vom Augustusplatz (Osten) zum Campus. Darüber liegt eine
Brücke, die die oberen Geschosse verbindet. Das Laserscan-Höhenfeld sieht nur die Brückenoberseite und macht daraus einen Vollblock
(Grundriss `TUNNEL_M`, bisher beim Paulinum); die senkrechten Streifen an seiner Ostwand sind Rasterfacetten zwischen Dach- und
Bodenzellen. Das 3D-Stadtmodell LoD2 hat die Brücke ab 131,1 m ü. NHN (Unterkante) bis 145,0 m (Dach), darunter nichts.

Vorschlag (Stand nach Nutzerwunsch 17.10.): Das ganze Teil entfällt, Brücke und Block. Das Paulinum bekommt eine gerade Nordwand (alles nördlich der
Wandlinie `WAND_T` im Hofsystem wird abgeschnitten, auch der Splitter an der Institutswand und der Absatz im Grundriss), das Institutsgebäude bleibt
unverändert. Die Gasse ist damit auf ganzer Länge frei, vom Hof bis zum Augustusplatz. Die Treppe der Platte im Nordosten reicht bis an das
Ostende der früheren Brücke (Hofsystem u = `ENDE_U`).

Alle Maße in mm im Kartensystem (Meter mal Maßstab), z = 0 ist der Boden des jeweiligen Gebäudes (`ground_z`).
"""
import math

import numpy as np
from shapely import affinity
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

import generate as G
import innenhof as I

SCALE = 1300
S = 1000.0 / SCALE

# Grundriss des Durchgangs (lokal, m): im Süden die Nordwand des Paulinums (Linie von (-55,2 | 74,0) nach (-41,9 | 71,2)), im Norden die
# Südwand des Institutsgebäudes, im Westen und Osten die Stirnflächen der Brücke (LoD2: x -49,7 bis -42,9)
TUNNEL_M = Polygon([(-49.4, 72.78), (-41.9, 71.2), (-42.7, 77.6), (-43.2, 77.7), (-44.6, 78.2), (-49.7, 79.3)])
Z_DECKE_M = 131.1     # m ü. NHN: Unterkante der Brücke (LoD2, Grundfläche der oberen Gebäudeteile)
Z_DACH_M = 145.0      # m ü. NHN: Oberkante der Brücke (LoD2 144,2 bis 145,2)
Z_BODEN_M = 115.4     # m ü. NHN: Boden im Durchgang (Laserscan, Bodenpunkte an der Westmündung 115,0 bis 115,6)
GROUND = {"01_paulinum": 114.461, "05_institutsgebaeude": 113.901}   # ground_z der Volumenkörper (lod2.models)
FENSTER_M = (-76.0, -21.0, 56.0, 106.0)      # Ausschnitt der 3D-Ansicht (lokal, m): x0, x1, y0, y1


def decke_mm(z_abs=Z_DECKE_M, slug="05_institutsgebaeude", s=S):
    """Höhe der Decke über dem Boden des Gebäudes in mm."""
    return (z_abs - GROUND[slug]) * s


def tunnel_mm(s=S):
    return G.scale_geom(TUNNEL_M, s)


def maße(s=S):
    """Länge (Ost-West entlang der Gasse), Breite und Fläche des Durchgangs, in m und mm."""
    p = TUNNEL_M
    c = np.asarray(p.exterior.coords)
    # Gassenrichtung: Südwand des Institutsgebäudes (parallel zur Nordwand des Paulinums)
    d = np.array([5.1, -1.1]); d = d / np.linalg.norm(d)
    n = np.array([d[1], -d[0]])
    laenge = np.ptp(c @ d)
    breite = np.ptp(c @ n)
    return dict(laenge_m=laenge, breite_m=breite, flaeche_m2=p.area, laenge=laenge * s, breite=breite * s, richtung=math.degrees(math.atan2(d[1], d[0])))


def laser_pair(s=S):
    """Volumenkörper, Grundrisse (mm) und Bodenhöhe von Paulinum und Institutsgebäude wie in laserscan.models, nur für diese beiden."""
    import laserscan as L
    import lod2
    pts = L.load_points()
    out = {}
    for slug, (_, fp_mm, info) in lod2.models(s).items():
        if slug not in GROUND:
            continue
        fp = G.scale_geom(fp_mm, 1.0 / s)
        theta = L.main_axis(fp)
        grid, _, minx, miny, npts, c = L.building_grid(pts, fp, info, theta)
        hf = L.heightfield_solid(grid - info["ground_z"], minx, miny, L.RASTER, s).simplify(L.SIMPLIFY)
        hf = hf.translate([-c[0] * s, -c[1] * s, 0]).rotate([0, 0, theta]).translate([c[0] * s, c[1] * s, 0])
        solid = hf ^ G.extrude(fp_mm, -1, (grid.max() - info["ground_z"]) * s + 1)
        comps = solid.decompose()
        vmax = max(x.volume() for x in comps)
        out[slug] = (G.union([x for x in comps if x.volume() > 0.005 * vmax]), fp_mm, info["ground_z"])
    return out


WAND_T = 61.15        # m im Hofsystem: Nordwand des Paulinums; was weiter nördlich liegt (Block, Splitter, Absatz), entfällt
GASSE_U = (-102.0, -30.0)   # m im Hofsystem: so weit reicht der Schnitt entlang der Wand (vom Hof bis hinter die Ostecke des Paulinums)


def schnittbereich_mm(s=S):
    """Fläche (mm, Kartensystem), die vom Paulinum entfällt: nördlich der Wandlinie, zwischen Hof und Ostecke."""
    _, aus_hof = I.rahmen(I.load())
    return aus_hof(box(GASSE_U[0] * s, WAND_T * s, GASSE_U[1] * s, 100 * s))


def umbauen(pair, s=S):
    """Neue Körper: {slug: (Volumenkörper, Grundriss mm)} für Paulinum und Institutsgebäude.

    Paulinum: alles nördlich der Wandlinie WAND_T entfällt (Block des Durchgangs mit der Brücke, Splitter an der Institutswand, Absatz im Grundriss),
    senkrechter Schnitt. Institutsgebäude: unverändert. Keine Brücke, keine Decke."""
    (p_solid, p_fp, _), (i_solid, i_fp, _) = pair["01_paulinum"], pair["05_institutsgebaeude"]
    zmax = p_solid.bounding_box()[5] + 2
    weg = schnittbereich_mm(s)
    return {"01_paulinum": (p_solid - G.extrude(weg, -1, zmax), G.clean(p_fp.difference(weg))), "05_institutsgebaeude": (i_solid, i_fp)}


def freie_gasse(neu, s=S, u=(-94.0, -50.0), t=(61.3, 67.3), hoehen=None):
    """Prüft, dass in der Gasse nichts steht: Schnitte beider neuer Körper in vielen Höhen, Fläche im Rechteck u × t (Hofsystem, m)
    zwischen den Wänden. Liefert (größte Restfläche in mm², Liste von (Höhe, Fläche) mit Fläche > 0, engste freie Breite in m über alle Höhen
    und alle u)."""
    import hohl
    from shapely.geometry import LineString
    hoehen = hoehen or [0.2, 0.6, 1, 2, 3, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28]
    rest, eng = [], 99.0
    ber = box(u[0] * s, t[0] * s, u[1] * s, t[1] * s)
    for z in hoehen:
        flaeche = 0.0
        geoms = [nach_hof_mm(hohl._cs_poly(sol.slice(z))) for sol in (v[0] for v in neu.values())]
        for g in geoms:
            flaeche += g.intersection(ber).area
        rest.append((z, flaeche))
        for uu in np.arange(u[0], u[1] + 0.01, 1.0):
            ln = LineString([(uu * s, 55 * s), (uu * s, 75 * s)])
            frei_t0 = max([g.intersection(ln).bounds[3] for g in geoms[:1] if not g.intersection(ln).is_empty] or [55 * s])
            frei_t1 = min([g.intersection(ln.difference(geoms[0])).bounds[1] for g in geoms[1:] if not g.intersection(ln.difference(geoms[0])).is_empty] or [75 * s])
            eng = min(eng, (frei_t1 - frei_t0) / s)
    return max(f for _, f in rest), [(z, f) for z, f in rest if f > 1e-6], eng


# --------------------------------------------------------------------------
# Treppe der Platte im Nordosten (Gasse zwischen Paulinum und Institutsgebäude)
# --------------------------------------------------------------------------
def gasse_baender(fps_mm, u, t, n, lauf, s=S, data=None):
    """Stufen der Gasse: [(Polygon mm, Oberkante mm über der Plattenoberfläche)]. Rechteck u × t im Hofsystem, n Stufen (n - 1 Podeste von hub
    nach unten, das letzte Stück liegt auf Plattenhöhe), Länge der Teilung `lauf` m (wie innenhof.platte_aufbau_mm, nordost); die Gebäude
    (fps_mm) und ihre Fuge werden abgezogen."""
    data = data or I.load()
    hb = I.hub(data, s)
    tr = lauf / n
    frei = unary_union(list(fps_mm)).buffer(0.1, join_style=2)
    # nur südlich der verlängerten Südwand des Institutsgebäudes: östlich davon beginnt der Platz, nicht mehr die Gasse
    yl = lambda x: 78.2 - 0.2157 * (x + 44.6)
    sued = G.scale_geom(Polygon([(-130, yl(-130)), (-20, yl(-20)), (-20, 40), (-130, 40)]), s)
    frei = frei.union(box(-1000, -1000, 1000, 1000).difference(sued))
    out = []
    for k in range(n - 1):
        lo = u[0] + k * tr - (2.0 if k == 0 else 0.0)
        hi = u[0] + (k + 1) * tr
        poly = G.clean(G.scale_geom(I.block_m(data, (lo, min(hi, u[1])), t), s).difference(frei))
        if not poly.is_empty:
            out.append((poly, hb * (n - 1 - k) / n))
    return out


ALT = dict(u=(-94.0, -60.0), t=(58.0, 90.0), n=6, lauf=7.0)
def neu(n=9, ende_u=-56.0):
    """Neue Treppe: bis zum Ostende des Durchgangs (`ende_u` im Hofsystem), n Stufen gleich lang."""
    u0 = -94.0
    lauf = (ende_u - u0) * n / (n - 1)       # die letzte Teilung (Plattenhöhe) liegt hinter dem Ende
    return dict(u=(u0, ende_u + 1.0), t=(61.0, 70.0), n=n, lauf=lauf)


ENDE_U = -56.0       # m im Hofsystem: Ostende der früheren Brücke (Ende der Treppe)


def tunnel_u():
    """Ausdehnung des Durchgangs im Hofsystem (u von, u bis, t von, t bis) in m."""
    data = I.load()
    nach_hof, _ = I.rahmen(data)
    b = nach_hof(TUNNEL_M).bounds
    return b


# --------------------------------------------------------------------------
# Schnitte (Hofsystem: u quer zur Hofachse nach Osten, t längs nach Norden)
# --------------------------------------------------------------------------
def _in_hof(solid, perm):
    """Körper ins Hofsystem drehen (u, t, z) und die Achsen mit `perm` (3×3, Drehung) vertauschen, damit ein Schnitt bei z = const möglich ist."""
    a = math.radians(I.load()["achse_grad"])
    c, s_ = math.cos(a), math.sin(a)
    rot = np.array([[c, -s_, 0], [s_, c, 0], [0, 0, 1]])
    m = perm @ rot
    return solid.transform(np.hstack([m, np.zeros((3, 1))]))


def schnitt_quer(solid, u_m, s=S):
    """Querschnitt bei u = u_m (m) quer durch die Gasse: shapely-Fläche in (t mm, z mm), t nach Norden (rechts im Bild)."""
    import hohl
    m = _in_hof(solid, np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0]]))
    return hohl._cs_poly(m.slice(u_m * s))


def schnitt_laengs(solid, t_m, s=S):
    """Längsschnitt bei t = t_m (m) entlang der Gasse: shapely-Fläche in (u mm, z mm), u nach Osten (rechts im Bild)."""
    import hohl
    m = _in_hof(solid, np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]]))
    cs = hohl._cs_poly(m.slice(t_m * s))
    return affinity.scale(cs, 1, -1, origin=(0, 0))


def nach_hof_mm(geom, s=S):
    """Geometrie (mm, Kartensystem) ins Hofsystem (mm): Gasse waagerecht, Osten rechts."""
    return I.rahmen(I.load())[0](geom)


# --------------------------------------------------------------------------
# Platte als Ausschnitt für die 3D-Ansicht (Mulden nicht modelliert)
# --------------------------------------------------------------------------
def platte_ausschnitt(fps_mm, baender, s=S, dicke=2.5):
    """Plattenausschnitt im Fenster FENSTER_M: Platte mit Hof-Einsatz (auf Hofhöhe) und den Stufen der Gasse. Körper in mm, z = 0 Plattenoberfläche."""
    data = I.load()
    x0, x1, y0, y1 = FENSTER_M
    fenster = box(x0 * s, y0 * s, x1 * s, y1 * s)
    hb = I.hub(data, s)
    hof = G.scale_geom(I.hof_polygon_local().buffer(I.HOF_UEBERMASS).intersection(I.huelle_m(data)), s)
    hof = hof.difference(unary_union(list(fps_mm)).buffer(0.9, join_style=2))
    parts = [G.extrude(fenster, -dicke, 0.0), G.extrude(G.clean(hof.intersection(fenster)), -0.01, hb)]
    for poly, h in baender:
        poly = G.clean(poly.intersection(fenster))
        if not poly.is_empty:
            parts.append(G.extrude(poly, -0.01, max(h, 0.01)))
    return G.union(parts)


if __name__ == "__main__":
    print("Durchgang", maße(), "Hofsystem", tunnel_u())
    print("Decke Institut %.2f mm, Paulinum %.2f mm, Dach Institut %.2f mm" % (decke_mm(), decke_mm(slug="01_paulinum"), decke_mm(Z_DACH_M)))
    print("hub %.3f mm" % I.hub(I.load(), S))
