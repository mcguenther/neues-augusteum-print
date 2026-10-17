#!/usr/bin/env python3
"""Trennwand zwischen aneinanderstoßenden Gebäuden der Steckplatte (Geometrie, Planstand, noch nicht in `plug.campus`/`plug.buildings` verdrahtet).

Befund: Die Grundrisse stoßen in allen Quellen ohne Abstand aneinander (Paulinum und Neues Augusteum überlappen im Laserscan sogar um einen Keil), die
Mulden der Steckplatte verschmelzen dort zu einer Aussparung, es bleibt keine Wand zwischen ihnen stehen. Der Vorschlag: an jeder Naht bleibt eine
Wand WAND_T (wie die Hof-Wand `P.HOF_WALL_T`) zwischen den beiden Mulden stehen. Die Fuge zwischen den Grundrissen ist dann
    FUGE = 2 × Spiel (P.OUTLINE_CLR_T) + WAND_T
und wird aus den Gebäuden geschnitten, nicht aus der Platte: der Plattenumriss hängt nur an den äußeren Grundrissen und bleibt gleich.

Wer weicht: Jedes Gebäude gibt je Naht höchstens so viel ab, dass sein Schachtrohr noch RESTWAND_T Material zum neuen Rand behält; sonst gibt der
Nachbar die ganze Fuge (Paulinum: das Rohr sitzt 0,18 mm von der Naht zum Neuen Augusteum). Sonst teilen sich beide die Fuge je zur Hälfte.

    fps2, info = trenn(fps, rohre)      # fps: {slug: Polygon in mm}, rohre: {slug: Polygon des Schachtrohrs}
"""
import itertools
import json
import os

from shapely import affinity
from shapely.geometry import box as sbox
from shapely.ops import unary_union

import generate as G
from plug import campus as C
from plug.testcase import params as P

WAND_T = P.HOF_WALL_T          # mm, Wand zwischen zwei Mulden (wie zum Hof)
RESTWAND_T = 0.8               # mm, Material, das zwischen Schachtrohr und neuem Gebäuderand mindestens bleibt (G.MIN_FEATURE)
MIN_STUECK = 0.3               # mm², kleinere Reste nach dem Beschnitt werden verworfen


def fuge(spiel=None, wand=None):
    """Abstand der Grundrisse an der Naht: Spiel auf beiden Seiten plus Wand."""
    return 2 * (P.OUTLINE_CLR_T if spiel is None else spiel) + (WAND_T if wand is None else wand)


def rohre(places=None, scale=P.SCALE_PLAN):
    """Schachtrohr je Gebäude (Rechteck um die Kassette mit Rohrwand min(1,2; Wand der Platzierung), Weltlage in mm)."""
    if places is None:
        places = json.load(open(os.path.join(G.HERE, "plug", "scale1176", "placements_%d.json" % scale)))
    out = {}
    for slug, p in places.items():
        w, dep = C.shaft_size(p["var"])
        wl = min(1.2, p["wall"])
        r = sbox(-w / 2 - wl, -dep / 2 - wl, w / 2 + wl, dep / 2 + wl)
        out[slug] = affinity.translate(affinity.rotate(r, p["angle"], origin=(0, 0)), p["cx"], p["cy"])
    return out


def _sauber(g):
    """Winzige Reste (Spitzen an den Nahtenden) entfernen, größtes Stück behalten."""
    teile = [q for q in G.polys_of(g) if q.area >= MIN_STUECK]
    return unary_union(teile) if teile else g


def trenn(fps, rohr, spiel=None, wand=None, naht_max=None):
    """Grundrisse mit Fuge an allen Nähten. Rückgabe: (neue Grundrisse, Info je Naht).
    Info: Paar, Naht, Anteil des ersten (a) am Abtrag, Fläche, die jedes Gebäude verliert, kleinster Abstand danach, Rohrabstand zum neuen Rand."""
    g = fuge(spiel, wand)
    neu = dict(fps)
    info = []
    # Nähte: Paare mit Abstand unter der Fuge (aus den ursprünglichen Grundrissen)
    paare = [(a, b) for a, b in itertools.combinations(fps, 2) if fps[a].distance(fps[b]) < g - 1e-6]
    for a, b in paare:
        A0, B0 = fps[a], fps[b]
        naht = A0.boundary.intersection(B0.buffer(0.02)).length if A0.distance(B0) < 0.01 else 0.0
        # Anteil: wer sein Rohr zu nah an der Naht hat, gibt nichts ab (Rohr bleibt RESTWAND_T vom neuen Rand)
        zone = A0.buffer(g, join_style=2).intersection(B0.buffer(g, join_style=2)).buffer(0.01)
        da = rohr[a].distance(zone) if a in rohr else 99.0
        db = rohr[b].distance(zone) if b in rohr else 99.0
        ok_a, ok_b = da >= g / 2 + RESTWAND_T, db >= g / 2 + RESTWAND_T
        if ok_a and ok_b:
            anteil = 0.5
        elif ok_a:
            anteil = 1.0
        elif ok_b:
            anteil = 0.0
        else:
            raise SystemExit("%s/%s: beide Rohre zu nah an der Naht (%.2f, %.2f)" % (a, b, da, db))
        # Reihenfolge: das Gebäude mit Anteil 1 oder 0,5 schneidet zuerst, das andere folgt auf dem Rest; so ist der Abstand genau g
        if anteil >= 0.5:
            A1 = _sauber(neu[a].difference(neu[b].buffer(anteil * g, join_style=2)))
            B1 = _sauber(neu[b].difference(A1.buffer(g, join_style=2)))
        else:
            B1 = _sauber(neu[b].difference(neu[a].buffer((1 - anteil) * g, join_style=2)))
            A1 = _sauber(neu[a].difference(B1.buffer(g, join_style=2)))
        info.append(dict(a=a, b=b, naht=naht, anteil=anteil, rohr_a=da, rohr_b=db,
                         verlust_a=neu[a].difference(A1).area, verlust_b=neu[b].difference(B1).area, ueberlapp=A0.intersection(B0).area))
        neu[a], neu[b] = A1, B1
    for i in info:
        i["abstand"] = neu[i["a"]].distance(neu[i["b"]])
    return neu, info


def kleinste_wand(fps, spiel=None):
    """Kleinste Wand zwischen zwei Mulden (Abstand der Grundrisse minus 2 × Spiel) über alle Paare mit Abstand unter 4 mm; 0 und weniger = verschmolzen."""
    c = P.OUTLINE_CLR_T if spiel is None else spiel
    return {(a, b): fps[a].distance(fps[b]) - 2 * c for a, b in itertools.combinations(fps, 2) if fps[a].distance(fps[b]) < 4.0}
