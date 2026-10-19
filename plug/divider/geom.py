#!/usr/bin/env python3
"""Trennwand zwischen aneinanderstoßenden Gebäuden der Steckplatte (Geometrie; seit 17.10.2026 umgesetzt: `plug.campus.models_plan` ruft `getrennt` auf,
`plug.campus.build` und `plug.buildings` benutzen es; Planseite plug/divider/page.html).

Spiel und Fuge sind seit 19.10.2026 entkoppelt (Passung bei wechselnden Filamenten): Das Mulden-Spiel der Platte ist `P.OUTLINE_CLR_T` (0,15), der Zuschnitt der
Gebäude rechnet mit `P.ZUSCHNITT_CLR_T` (0,10, Fuge 1,0 wie bei den gebauten Gebäuden). Die Differenz je Naht, 2 × (0,15 − 0,10) = 0,1 mm, holt die Platte durch
Verschieben der Gebäude: `verschiebungen` (Minimum-Norm-Ausgleich, Neues Augusteum bleibt), `schiebe`, `schiebe_places`; die Fuge in der Platte ist `fuge_platte()` = 1,1 mm,
die Wand zwischen den Mulden bleibt `WAND_T`. Gebäude (STL) und Zuschnitt ändern sich dadurch nicht, nur ihre Lage auf der Platte (`plug.campus.models_platte`).

Befund: Die Grundrisse stoßen in allen Quellen ohne Abstand aneinander (Paulinum und Neues Augusteum überlappen im Laserscan sogar um einen Keil), die
Mulden der Steckplatte verschmelzen dort zu einer Aussparung, es bleibt keine Wand zwischen ihnen stehen. Der Vorschlag: an jeder Naht bleibt eine
Wand WAND_T (wie die Hof-Wand `P.HOF_WALL_T`) zwischen den beiden Mulden stehen. Die Fuge zwischen den Grundrissen ist dann
    FUGE = 2 × Spiel (P.ZUSCHNITT_CLR_T) + WAND_T
und wird aus den Gebäuden geschnitten, nicht aus der Platte: der Plattenumriss hängt nur an den äußeren Grundrissen und bleibt gleich.

Wer weicht: Je Naht teilen sich beide Gebäude die Fuge je zur Hälfte, sofern jedes Schachtrohr danach RESTWAND_T vom neuen Rand behält; sonst gibt
der Nachbar die ganze Fuge (Paulinum: das Rohr sitzt 0,18 mm von der Naht zum Neuen Augusteum; Hochhaus und Neues Augusteum: 3,2 und 3,4 mm von der
Naht zum Hörsaalgebäude, das darum die Fuge dort allein abgibt).

    fps2, info = trenn(fps, rohren())   # fps: {slug: Polygon in mm}, rohren: {slug: Polygon des Schachtrohrs}
"""
import itertools
import json
import math
import os

from shapely import affinity
from shapely.geometry import Polygon
from shapely.geometry import box as sbox
from shapely.ops import unary_union

import generate as G
from plug import campus as C
from plug.testcase import params as P

WAND_T = P.HOF_WALL_T          # mm, Wand zwischen zwei Mulden (wie zum Hof)
RESTWAND_T = 2.9               # mm, Abstand Schachtrohr zum neuen Gebäuderand mindestens: Wand 0,8 + Luft FUELLEN_T 2,0 + 0,1; bleibt weniger Luft, füllt hohl.py den
                               # Spalt und das Gewölbe wird zu Vollmaterial (Hochhaus bei Fuge 1,0: 27,9 statt 13,5 cm³; bei 0,5 mm Fuge ohne Folgen)
MIN_STUECK = 0.3               # mm², kleinere Reste nach dem Beschnitt werden verworfen
# Naht Paulinum / Neues Augusteum: beide Grundrisse liegen an einer geraden Kante (Südkante des Paulinums = Nordkante des Augusteums). Das Paulinum hat dort
# einen rechteckigen und einen dünnen Zahn nach Süden (zusammen 38 mm²), die in den Augusteum-Grundriss ragen; die Wand müsste sich um beide winden.
# Nutzerwunsch 18.10.: Wand gerade von West nach Ost. Das Paulinum wird deshalb an der Geraden durch die beiden Endpunkte abgeschnitten (Zähne weg),
# und der Schlitz im Augusteum, den der Zahn dort hinterlässt (1 mm breit, 4 mm tief), wird im Fenster gefüllt (Schließen mit Radius SCHLITZ_R).
# Seit 18.10. wieder aus (Nutzer: vorher besser): Die Zähne tragen den höchsten Firstpunkt des Paulinums, der gerade Schnitt machte es 2,3 mm niedriger.
GERADE_NAHT = {}   # {"01_paulinum": ((-62.48, 44.28), (-22.08, 35.95))}: mm, behalten wird die Seite mit der größeren Fläche
SCHLITZ_FENSTER = {}   # {"02_neues_augusteum": (-40.5, 31.0, -23.0, 40.0)}: mm (x0, y0, x1, y1)
SCHLITZ_R = 1.2                # mm


def fuge(spiel=None, wand=None):
    """Abstand der Grundrisse an der Naht beim Zuschnitt der Gebäude: Spiel (`P.ZUSCHNITT_CLR_T`, unabhängig vom Mulden-Spiel der Platte) auf beiden Seiten plus Wand."""
    return 2 * (P.ZUSCHNITT_CLR_T if spiel is None else spiel) + (WAND_T if wand is None else wand)


def fuge_platte(spiel=None, wand=None):
    """Abstand der Grundrisse an der Naht auf der Platte: Mulden-Spiel (`P.OUTLINE_CLR_T`) auf beiden Seiten plus Wand (1,1 mm bei 0,15 und 0,8)."""
    return 2 * (P.OUTLINE_CLR_T if spiel is None else spiel) + (WAND_T if wand is None else wand)


def rohren(scale=P.SCALE_PLAN, places=None):
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


def _gerade(fp, p1, p2):
    """Grundriss entlang der Geraden p1-p2 abschneiden; behalten wird die Seite mit der größeren Fläche (Zähne auf der anderen Seite entfallen)."""
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    n = math.hypot(dx, dy)
    ux, uy, big = dx / n, dy / n, 400.0
    best = None
    for sgn in (1, -1):
        nx, ny = -uy * sgn, ux * sgn
        half = Polygon([(p1[0] - big * ux, p1[1] - big * uy), (p2[0] + big * ux, p2[1] + big * uy),
                        (p2[0] + big * ux + big * nx, p2[1] + big * uy + big * ny), (p1[0] - big * ux + big * nx, p1[1] - big * uy + big * ny)])
        g = unary_union([q for q in G.polys_of(fp.intersection(half)) if q.area > MIN_STUECK])
        if best is None or g.area > best.area:
            best = g
    return best


def _schliessen(fp, fenster, r):
    """Schlitze und Einkerbungen im Fenster schließen (Schließen mit Mitre-Ecken, nur innerhalb des Fensters)."""
    zu = fp.buffer(r, join_style=2).buffer(-r, join_style=2)
    return unary_union([fp, zu.intersection(sbox(*fenster))])


def trenn(fps, rohr, spiel=None, wand=None, naht_max=None):
    """Grundrisse mit Fuge an allen Nähten. Rückgabe: (neue Grundrisse, Info je Naht).
    Je Naht werden der Reihe nach drei Aufteilungen versucht: beide je zur Hälfte, nur das erste, nur das zweite Gebäude gibt die Fuge ab; genommen
    wird die erste, bei der jedes Schachtrohr RESTWAND_T vom neuen Rand bleibt (oder nicht näher kommt, als es schon war)."""
    g = fuge(spiel, wand)
    orig = fps
    fps = dict(fps)
    vor = {}
    for slug, (p1, p2) in GERADE_NAHT.items():
        if slug in fps:
            neu_fp = _gerade(fps[slug], p1, p2)
            if rohr.get(slug) is not None and rohr[slug].difference(neu_fp).area > 1e-6:
                raise SystemExit("%s: das Schachtrohr ragt über die gerade Naht" % slug)
            vor[slug] = fps[slug].difference(neu_fp).area
            fps[slug] = neu_fp
    for slug, (fenster, r) in ((k, (v, SCHLITZ_R)) for k, v in SCHLITZ_FENSTER.items()):
        if slug in fps:
            neu_fp = _schliessen(fps[slug], fenster, r)
            vor[slug] = -(neu_fp.difference(fps[slug]).area)
            fps[slug] = neu_fp
    neu = dict(fps)
    info = []
    alt = {k: rohr[k].distance(orig[k].boundary) for k in rohr if k in orig}
    paare = [(a, b) for a, b in itertools.combinations(fps, 2) if fps[a].distance(fps[b]) < g - 1e-6]

    def schnitt(A, B, anteil):
        # Reihenfolge: das Gebäude mit Anteil 1 oder 0,5 schneidet zuerst, das andere folgt auf dem Rest; so ist der Abstand genau g
        if anteil >= 0.5:
            A1 = _sauber(A.difference(B.buffer(anteil * g, join_style=2)))
            return A1, _sauber(B.difference(A1.buffer(g, join_style=2)))
        B1 = _sauber(B.difference(A.buffer((1 - anteil) * g, join_style=2)))
        return _sauber(A.difference(B1.buffer(g, join_style=2))), B1

    def passt(k, fp):
        if k not in rohr:
            return True
        d = rohr[k].distance(fp.boundary)
        return rohr[k].difference(fp).area < 1e-6 and (d >= RESTWAND_T or d >= alt[k] - 1e-6)

    for a, b in paare:
        A0, B0 = fps[a], fps[b]
        naht = A0.boundary.intersection(B0.buffer(0.02)).length if A0.distance(B0) < 0.01 else 0.0
        for anteil in (0.5, 1.0, 0.0):
            A1, B1 = schnitt(neu[a], neu[b], anteil)
            if passt(a, A1) and passt(b, B1):
                break
        else:
            raise SystemExit("%s/%s: keine Aufteilung der Fuge lässt beiden Rohren genug Wand" % (a, b))
        info.append(dict(a=a, b=b, naht=naht, anteil=anteil, rohr_a=rohr[a].distance(neu[a].boundary) if a in rohr else 99.0,
                         rohr_b=rohr[b].distance(neu[b].boundary) if b in rohr else 99.0,
                         verlust_a=neu[a].difference(A1).area, verlust_b=neu[b].difference(B1).area, ueberlapp=orig[a].intersection(orig[b]).area))
        neu[a], neu[b] = A1, B1
    for i in info:
        i["abstand"] = neu[i["a"]].distance(neu[i["b"]])
        i["rohr_a_neu"] = rohr[i["a"]].distance(neu[i["a"]].boundary) if i["a"] in rohr else 99.0
        i["rohr_b_neu"] = rohr[i["b"]].distance(neu[i["b"]].boundary) if i["b"] in rohr else 99.0
    for i in info:
        i["vorher"] = vor
    return neu, info


def kleinste_wand(fps, spiel=None):
    """Kleinste Wand zwischen zwei Mulden (Abstand der Grundrisse mit Mitre-Puffer `spiel`, `P.OUTLINE_CLR_T`) über alle Paare mit Abstand unter 4 mm; 0 und weniger = verschmolzen.
    Für Grundrisse in der Lage auf der Platte (nach `schiebe`), nicht für die zugeschnittenen Gebäude in Weltlage (dort ist die Wand bei Spiel 0,15 nur 0,7)."""
    c = P.OUTLINE_CLR_T if spiel is None else spiel
    m = {k: v.buffer(c, join_style=2) for k, v in fps.items()}
    return {(a, b): m[a].distance(m[b]) for a, b in itertools.combinations(fps, 2) if fps[a].distance(fps[b]) < 4.0}


def _fuell_hoehe(solid, add):
    """Höhe, bis zu der eine gefüllte Fläche aufgefüllt wird: die größte Höhe, in der der Körper noch mindestens den halben Ring um die Fläche füllt
    (der Querschnitt nimmt nach oben ab, Halbierung durch Bisektion)."""
    ring = add.buffer(0.8).difference(add.buffer(0.1))
    zmax = float(G.to_trimesh(solid).bounds[1][2])
    lo, hi = 0.0, zmax
    for _ in range(14):
        mid = (lo + hi) / 2
        cut = unary_union([Polygon(r).buffer(0) for r in solid.slice(mid).to_polygons()]) if solid.slice(mid).num_contour() else Polygon()
        if ring.intersection(cut).area >= 0.5 * ring.area:
            lo = mid
        else:
            hi = mid
    return lo


def getrennt(models, scale=P.SCALE_PLAN, spiel=None, wand=None):
    """Modelle (wie `G.source_models`, {slug: (Körper, Grundriss, …)}) mit Fuge an den Nähten: Grundriss und Körper der weichenden Gebäude
    werden beschnitten (Körper ∩ neuer Grundriss über die ganze Höhe), gefüllte Schlitze (SCHLITZ_FENSTER) bis zur Dachhöhe in ihrer Umgebung
    aufgefüllt; alle anderen Einträge bleiben dieselben Objekte."""
    fps = {k: v[1] for k, v in models.items() if k in P.CASSETTE}
    neu, _ = trenn(fps, rohren(scale), spiel, wand)
    out = dict(models)
    for k, fp in neu.items():
        if fp.symmetric_difference(fps[k]).area > 1e-6:
            solid = models[k][0]
            add = fp.difference(fps[k])
            if add.area > 1e-3:
                solid = solid + G.extrude(add.buffer(0.02, join_style=2), -1.0, _fuell_hoehe(solid, add))
            solid = solid ^ G.extrude(fp, -1.0, float(G.to_trimesh(solid).bounds[1][2]) + 1.0)
            out[k] = (solid, fp) + tuple(models[k][2:])
    return out


# --------------------------------------------------------------------------
# Lage auf der Platte: Gebäude je Naht auseinanderschieben (Mulden-Spiel größer als Zuschnitt-Spiel)
# --------------------------------------------------------------------------
ANKER = "02_neues_augusteum"   # bleibt an seinem Platz (mittleres Gebäude, Hof und Nordpfeil beziehen sich auf die Weltlage)
SCHIEB_TOL = 1e-4              # mm, so viel darf die Wand an einer Naht unter dem Soll bleiben (0,7999)
KONTAKT_SCHRITT = 0.05         # mm, Abstand der Messpunkte entlang der Naht
GEGEN_COS = -0.8               # Kontakte, deren Richtung mit der eines anderen Kontakts der Naht mehr als etwa 143° einschließt, gelten als gegenüberliegende Flanken


def _kontakte(A, B, ziel, schritt=KONTAKT_SCHRITT, extra=0.2):
    """Kontakte der Grundrisse A und B: Randpunkte des einen, die dem anderen näher als ziel + extra liegen. Rückgabe [(n, d)] mit der Richtung n (Einheitsvektor von A
    nach B, zusammengefasst auf 1°) und dem kleinsten Abstand d je Richtung; Verschieben von B gegen A um u ändert den Abstand an diesem Kontakt in erster Näherung um n · u."""
    import numpy as np
    import shapely
    from shapely.ops import nearest_points
    rows = {}
    for X, Y, vz in ((A, B, 1.0), (B, A, -1.0)):
        near = X.boundary.intersection(Y.buffer(ziel + extra))
        pts = []
        for part in shapely.get_parts(near):
            if part.geom_type == "LineString":
                n_ = max(int(part.length / schritt), 1)
                pts += [part.interpolate(k * part.length / n_) for k in range(n_ + 1)] + [shapely.Point(c) for c in part.coords]
            elif part.geom_type == "Point":
                pts.append(part)
        for p in pts:
            q = nearest_points(p, Y)[1]
            d = p.distance(q)
            if d < 1e-9:
                continue
            n = vz * np.array([q.x - p.x, q.y - p.y]) / d
            key = int(round(math.degrees(math.atan2(n[1], n[0]))))
            if key not in rows or d < rows[key][1]:
                rows[key] = (n, d)
    return list(rows.values())


def _ldp(G_, h):
    """Kleinste Lösung x (Summe der Quadrate) von G_ x ≥ h (Least Distance Programming nach Lawson/Hanson über `scipy.optimize.nnls`)."""
    import numpy as np
    from scipy.optimize import nnls
    E = np.vstack([G_.T, h[None, :]])
    f = np.zeros(E.shape[0])
    f[-1] = 1.0
    u, _ = nnls(E, f, maxiter=50 * E.shape[1])
    r = E @ u - f
    if abs(r[-1]) < 1e-12:
        raise SystemExit("Verschiebung der Gebäude: die Bedingungen widersprechen sich")
    return -r[:-1] / r[-1]


def verschiebungen(fps, wand=None, spiel=None, untergrenze=None, anker=ANKER, max_iter=30):
    """Verschiebung je Gebäude auf der Platte ({slug: (dx, dy)} in mm), damit die Wand zwischen den Mulden an jeder Naht mindestens `wand` (`WAND_T`, 0,8 mm) beträgt.
    fps: zugeschnittene Grundrisse in Weltlage (`getrennt`, Fuge `fuge()`), nur die Gebäude der Platte; die Mulden sind die Grundrisse mit Mitre-Puffer `spiel` (`P.OUTLINE_CLR_T`),
    gemessen wird zwischen den Mulden (nicht zwischen den Grundrissen: an Ecken mit Mitre-Spitzen ist die Wand sonst bis zu 0,05 mm schmaler).
    Verfahren: Je Naht werden die Kontakte der beiden Mulden gesammelt (`_kontakte`: Richtung n von A nach B und Abstand d; an einer stufigen oder abgewinkelten Naht mehrere Richtungen);
    für jeden soll d + n · (t_b − t_a) ≥ wand gelten. Gesucht ist die Lösung mit der kleinsten Summe der Quadrate aller Verschiebungen (Minimum-Norm, als kleinste Lösung von G x ≥ h
    nach Lawson/Hanson, `_ldp`), `anker` bleibt bei (0, 0). Weil Abstände nur in erster Näherung linear sind, wird mit den neuen Lagen wiederholt, bis alle Kontakte stimmen.
    Ausnahme: Gegenüberliegende Flanken (Zahn des einen Gebäudes im Schlitz des anderen, Normalen entgegengesetzt, Paulinum/Neues Augusteum) lassen sich durch Verschieben nicht beide
    vergrößern; sie müssen nur ihren Abstand halten (mindestens `untergrenze` = Wand des Zuschnitts `fuge()` − 2 × `spiel`, 0,7 mm), die übrige Naht bekommt das Soll."""
    import numpy as np
    wand = WAND_T if wand is None else wand
    spiel = P.OUTLINE_CLR_T if spiel is None else spiel
    untergrenze = (fuge() - 2 * spiel) if untergrenze is None else untergrenze
    slugs = [k for k in P.CASSETTE if k in fps]
    ix = {k: i for i, k in enumerate(slugs)}
    t = np.zeros((len(slugs), 2))
    bounds = [(0.0, 0.0) if (anker in ix and i // 2 == ix[anker]) else (None, None) for i in range(2 * len(slugs))]
    for _ in range(max_iter):
        cur = {k: affinity.translate(fps[k], *t[ix[k]]).buffer(spiel, join_style=2) for k in slugs}
        zeilen, rhs, offen = [], [], False
        for a, b in itertools.combinations(slugs, 2):
            if cur[a].distance(cur[b]) >= wand + 0.2:
                continue
            kon = _kontakte(cur[a], cur[b], wand)
            defizit = [(n, d) for n, d in kon if d < wand - SCHIEB_TOL]
            for n, d in kon:
                gegen = any(float(n @ m) < GEGEN_COS for m, _ in defizit) and d < wand - SCHIEB_TOL
                r = min(d, untergrenze) if gegen else wand
                z = np.zeros(2 * len(slugs))
                z[2 * ix[a]:2 * ix[a] + 2] = -n
                z[2 * ix[b]:2 * ix[b] + 2] = n
                zeilen.append(z)
                rhs.append(r - d + float(z @ t.ravel()))
                offen |= d < r - SCHIEB_TOL
        if not offen:
            break
        A, bvec = np.array(zeilen), np.array(rhs)
        frei = [i for i, bd in enumerate(bounds) if bd[0] is None]
        x = _ldp(A[:, frei], bvec)
        t = np.zeros(2 * len(slugs))
        t[frei] = x
        t = t.reshape(-1, 2)
    else:
        raise SystemExit("Verschiebung der Gebäude: keine Lösung, die alle Nähte auf Wand %.2f mm bringt" % wand)
    return {k: (float(t[ix[k], 0]), float(t[ix[k], 1])) for k in slugs}


def schiebe(models, shifts):
    """Modelle (wie `getrennt`) mit um `shifts` ({slug: (dx, dy)}) verschobenem Körper und Grundriss; die anderen Einträge bleiben dieselben Objekte."""
    out = dict(models)
    for k, (dx, dy) in shifts.items():
        if k in models and (abs(dx) > 0 or abs(dy) > 0):
            out[k] = (models[k][0].translate([dx, dy, 0.0]), affinity.translate(models[k][1], dx, dy)) + tuple(models[k][2:])
    return out


def schiebe_places(places, shifts):
    """Lagen der Kassettenschächte und Docks ({slug: {cx, cy, …}}, `placements_<Maßstab>.json`) um dieselbe Verschiebung; die Datei selbst bleibt unverändert (Lage der Gebäude)."""
    out = {}
    for k, p in places.items():
        dx, dy = shifts.get(k, (0.0, 0.0))
        out[k] = dict(p, cx=p["cx"] + dx, cy=p["cy"] + dy)
    return out


def naehte(fps, grenze=4.0):
    """Nähte (Paare mit Abstand unter `grenze`): [(a, b, Abstand der Grundrisse, Wand zwischen den Mulden bei Mulden-Spiel P.OUTLINE_CLR_T)]."""
    w = kleinste_wand(fps)
    return [(a, b, fps[a].distance(fps[b]), w[(a, b)]) for a, b in itertools.combinations(fps, 2) if fps[a].distance(fps[b]) < grenze]
