"""Umrisse der sechs Gebäudefüße (Schnitt 7 mm über dem Bett der Hohlgebäude) und die Maße des Mulden-Blocks T1 für plan.html.

Nur Lesen und Rechnen: die STL in `stl/steckmodul_campus/gebaeude/` werden nicht verändert.
"""
import glob
import os

import numpy as np
import trimesh
from shapely import affinity
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
GEB = os.path.join(ROOT, "stl", "steckmodul_campus", "gebaeude")

NAMEN = {"01_paulinum": "Paulinum", "02_neues_augusteum": "Neues Augusteum", "03_hoersaalgebaeude": "Hörsaalgebäude",
         "04_seminargebaeude": "Seminargebäude", "05_institutsgebaeude": "Institutsgebäude", "06_city_hochhaus": "City-Hochhaus"}
KASSETTE = {"01_paulinum": "v4", "02_neues_augusteum": "v4", "03_hoersaalgebaeude": "v4",
            "04_seminargebaeude": "V1RS", "05_institutsgebaeude": "V1RS", "06_city_hochhaus": "V2R"}
FUSS = 14.2          # Fußhöhe = Muldentiefe (plug/testcase/params.py, MULDE_EXTRA_T)
PLATTE_T = 14.6      # Plattendicke der Steckplatte
BODEN = 0.4          # Muldenboden
PLATTE_CM3 = 206.15  # Steckplatte 1:1300 (Druckpaket, plug/export_campus.py)


def umrisse():
    """{slug: Polygon} aufrecht gedreht (lange Seite waagerecht), Ursprung links unten, dazu Kennzahlen."""
    aus = {}
    for slug in NAMEN:
        f = os.path.join(GEB, slug + "_1zu1300.stl")
        m = trimesh.load(f)
        z = m.bounds[0][2] + 7.0
        sec = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
        ps = [Polygon(d[:, :2]) for d in sec.discrete if len(d) > 3]
        p = Polygon(max(ps, key=lambda q: q.area).exterior).buffer(0)
        mr = p.minimum_rotated_rectangle
        c = np.array(mr.exterior.coords)
        v = c[1] - c[0] if np.linalg.norm(c[1] - c[0]) >= np.linalg.norm(c[2] - c[1]) else c[2] - c[1]
        w = affinity.rotate(p, -np.degrees(np.arctan2(v[1], v[0])), origin="centroid")
        x0, y0, x1, y1 = w.bounds
        w = affinity.translate(w, -x0, -y0)
        x0, y0, x1, y1 = w.bounds
        aus[slug] = dict(poly=w, laenge=x1 - x0, breite=y1 - y0, flaeche=p.area, umfang=p.length, ecken=len(p.simplify(0.05).exterior.coords) - 1)
    return aus


def block(poly, spiele, wand=2.4, rand=3.0, rand_l=None):
    """Mulden-Block: je Spiel eine Mulde mit dem Umriss `poly` (Spiel je Seite, Gehrung), untereinander (erstes Spiel unten), Stege `wand`, Rand `rand`,
    links `rand_l` (Platz für die Kennung). Gibt Platte (Rechteck), Mulden (Spiel, Polygon mit Spiel), Umrisse (Spiel, Polygon ohne Spiel) und
    Maße samt Volumen in cm³ zurück."""
    rand_l = rand if rand_l is None else rand_l
    mulden, fps, y = [], [], rand
    for s in spiele:
        g = poly.buffer(s, join_style=2, mitre_limit=5)
        gx0, gy0, gx1, gy1 = g.bounds
        dx, dy = rand_l - gx0, y - gy0
        mulden.append((s, affinity.translate(g, dx, dy)))
        fps.append((s, affinity.translate(poly, dx, dy)))
        y += (gy1 - gy0) + wand
    breite = max(g.bounds[2] for _, g in mulden) + rand
    hoehe = y - wand + rand
    platte = box(0, 0, breite, hoehe)
    vol = platte.area * PLATTE_T - sum(g.area for _, g in mulden) * (PLATTE_T - BODEN)
    return dict(platte=platte, mulden=mulden, fps=fps, breite=breite, hoehe=hoehe, cm3=vol / 1000.0, anteil=vol / 1000.0 / PLATTE_CM3)


def pfad(g, nd=2):
    """SVG-Pfad (mm, y nach unten gespiegelt) einer Fläche mit Löchern."""
    teile = []
    for p in ([g] if g.geom_type == "Polygon" else list(g.geoms)):
        for r in [p.exterior] + list(p.interiors):
            teile.append("M" + " L".join("%.*f %.*f" % (nd, x, nd, -y) for x, y in r.coords[:-1]) + "Z")
    return " ".join(teile)
