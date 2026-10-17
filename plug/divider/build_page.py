#!/usr/bin/env python3
"""Planseite Trennwände zwischen Gebäuden: plug/divider/page.html (Vorlage page.template.html).

Die Gebäude des Campus stoßen an vier Nähten ohne Abstand aneinander; die Mulden der Steckplatte verschmelzen dort, es bleibt keine Wand
stehen. Die Seite zeigt den Befund (Nähte, Quellen, Keil zwischen Paulinum und Neuem Augusteum), den Vorschlag (Wand wie zum Hof, Fuge aus den
Gebäuden geschnitten, Geometrie in plug/divider/geom.py) und rechnet ihn mit der echten Steckplatte durch (C.build mit beschnittenen Grundrissen,
nur im Speicher; stl/ bleibt unverändert).

Aufruf (aus dem Wurzelverzeichnis, ca. 1 min):
    python3 -m plug.divider.build_page
"""
import glob
import html
import itertools
import json
import os
import re

import numpy as np
import trimesh
from shapely.geometry import Polygon
from shapely.ops import unary_union

import generate as G
import innenhof
from plug import campus as C
from plug.divider import geom as D
from plug.hof.build_page import NAMEN, Plan, de, gebaeude
from plug.geom import to_tm
from plug.testcase import params as P

HERE = os.path.dirname(os.path.abspath(__file__))
S = 1000.0 / P.SCALE_PLAN
PAARE = [("01_paulinum", "02_neues_augusteum"), ("02_neues_augusteum", "03_hoersaalgebaeude"),
         ("03_hoersaalgebaeude", "06_city_hochhaus"), ("04_seminargebaeude", "05_institutsgebaeude")]
G_RASTER = [round(0.6 + 0.05 * i, 2) for i in range(21)]     # Fugenbreiten für den Regler (2 × Spiel + Wand)


def teile(g):
    if g.is_empty:
        return []
    return [q for gg in getattr(g, "geoms", [g]) for q in teile(gg)] if hasattr(g, "geoms") else [g]


def linien(plan, geom, cls):
    d = []
    for g in teile(geom):
        if g.geom_type == "LineString" and g.length > 0:
            d.append("M" + " L".join("%.1f %.1f" % plan.pt(x, y) for x, y in g.coords))
    if d:
        plan.items.append('<path class="%s" d="%s"/>' % (cls, " ".join(d)))


def modelle(quelle):
    G.FAST = True
    m = G.source_models(quelle, S)
    return {k: v[1] for k, v in m.items() if k in P.CASSETTE}


def platte(fps_neu=None):
    """Steckplatte (Manifold) wie plug.campus.build, optional mit anderen Grundrissen (nur im Speicher)."""
    orig = G.source_models

    def patched(q, s):
        m = orig(q, s)
        if fps_neu:
            m = {k: ((v[0], fps_neu[k]) + tuple(v[2:]) if k in fps_neu else v) for k, v in m.items()}
        return m
    G.source_models = patched
    try:
        return C.build(P.SCALE_PLAN, False)
    finally:
        G.source_models = orig


def schnitt_poly(man, z):
    g = None
    for ring in man.slice(z).to_polygons():
        r = Polygon(ring)
        g = r if g is None else g.symmetric_difference(r)
    return g.buffer(0)


def stl_ueberlapp(z=-7.0):
    """Überlapp der Wandringe von Paulinum und Neuem Augusteum in den fertigen Gebäude-STL (mm² je Lage)."""
    def ring(path):
        sec = trimesh.load(path).section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
        polys = sorted([Polygon(np.asarray(e)[:, :2]).buffer(0) for e in sec.discrete if len(e) > 3], key=lambda q: -q.area)
        g = None
        for p in polys:
            g = p if g is None else g.symmetric_difference(p)
        return g
    base = os.path.join(G.HERE, "stl", "steckmodul_campus", "gebaeude")
    a = glob.glob(os.path.join(base, "01_paulinum_1zu1300.stl"))[0]
    b = glob.glob(os.path.join(base, "02_neues_augusteum_1zu1300.stl"))[0]
    return ring(a).intersection(ring(b)).area


def zoom(fps_a, fps_b, a, b, nahtgeom, ueber, wand_neu, weg):
    """Zwei Grundrisse (Ist, Neu) um eine Naht. Rückgabe (svg_ist, svg_neu)."""
    x0, y0, x1, y1 = nahtgeom.bounds
    m = 4.5
    x0, y0, x1, y1 = x0 - m, y0 - m, x1 + m, y1 + m
    k = min(430.0 / (x1 - x0), 400.0 / (y1 - y0))
    out = []
    for neu in (False, True):
        fps = fps_b if neu else fps_a
        plan = Plan(x0, x1, y0, y1, k)
        plan.poly(plan.box, "platte")
        mulden = unary_union([f.buffer(P.OUTLINE_CLR_T, join_style=2) for f in (fps[a], fps[b])])
        plan.poly(mulden, "mulde")
        if neu:
            plan.poly(weg, "weg")
        else:
            plan.poly(ueber, "keil")
        for sl in (a, b):
            plan.poly(fps[sl], "bld2")
        if neu:
            plan.poly(wand_neu, "wand")
        for sl in (a, b):
            c = fps[sl].intersection(plan.box.buffer(-1)).representative_point()
            plan.text(c.x, c.y, NAMEN[sl], "bname", "middle")
        plan.scale_and_north(5.0)
        out.append(plan.svg("Naht %s / %s, %s" % (NAMEN[a], NAMEN[b], "neu" if neu else "heute")))
    return out


def uebersicht(fps, nahte, outline):
    b = outline.bounds
    plan = Plan(b[0] - 1.5, b[2] + 1.5, b[1] - 1.5, b[3] + 1.5, 3.4)
    plan.poly(outline, "platte")
    gebaeude(plan, fps)
    for i, (naht, off) in enumerate(nahte):
        linien(plan, naht, "naht")
        c = unary_union([q for q in teile(naht)]).centroid
        plan.marker(c.x, c.y, c.x + off[0], c.y + off[1], str(i + 1))
    plan.scale_and_north(20.0)
    return plan.svg("Platte mit den vier Nähten", "tall")


def main():
    G.FAST = True
    fps_l = modelle("laserscan")
    R = D.rohre()
    g1 = D.fuge()
    neu, info = D.trenn(fps_l, R)
    infos = {(i["a"], i["b"]): i for i in info}
    # Quellenvergleich
    quellen = {q: modelle(q) for q in ("osm", "lod2", "laserscan")}
    # Regler: Verlust je Gebäude über die Fugenbreite
    tabelle = {}
    for g in G_RASTER:
        n2, _ = D.trenn(fps_l, R, spiel=0.0, wand=g)
        tabelle["%.2f" % g] = {k: round(fps_l[k].area - n2[k].area, 2) for k in fps_l}
    # echte Platte, vorher und nachher
    pl0, rep0, mod0, pls0, outline0, hof0 = platte()
    pl1, rep1, mod1, pls1, outline1, hof1 = platte(neu)
    tm0, tm1 = to_tm(pl0), to_tm(pl1)
    T = C.plate_thickness(P.dims_plan())
    sl1, sl0 = schnitt_poly(pl1, T - 4.0), schnitt_poly(pl0, T - 4.0)
    mp = {k: neu[k].buffer(P.OUTLINE_CLR_T, join_style=2) for k in neu}
    mp0 = {k: fps_l[k].buffer(P.OUTLINE_CLR_T, join_style=2) for k in fps_l}
    wande, deckung, wandlaenge = {}, {}, {}
    for a, b in PAARE:
        w = (mp[a].buffer(D.WAND_T + 0.05, join_style=2).intersection(mp[b].buffer(D.WAND_T + 0.05, join_style=2))).difference(mp[a]).difference(mp[b])
        wande[(a, b)] = w
        deckung[(a, b)] = w.intersection(sl1).area / max(w.area, 1e-9)
        wandlaenge[(a, b)] = w.area / D.WAND_T
    ist_wand = sum(mp0[a].buffer(D.WAND_T + 0.05).intersection(mp0[b].buffer(D.WAND_T + 0.05)).difference(mp0[a]).difference(mp0[b]).area for a, b in PAARE)
    hof_diff = hof0.symmetric_difference(hof1).area if hasattr(hof0, "symmetric_difference") else 0.0
    ab = C.hof_abstand(P.HOF_WALL_T)
    hof_a = innenhof.flaeche_mm(list(fps_l.values()), S, ab)
    hof_b = innenhof.flaeche_mm(list(neu.values()), S, ab)
    hof_diff = hof_a.symmetric_difference(hof_b).area
    b0, b1 = outline0.bounds, outline1.bounds
    dim0 = (b0[2] - b0[0], b0[3] - b0[1])
    dim1 = (b1[2] - b1[0], b1[3] - b1[1])
    koll = max(r[4] for r in rep1)
    ueber_stl = stl_ueberlapp()
    nahtgeo = {p: fps_l[p[0]].boundary.intersection(fps_l[p[1]].buffer(0.02)) for p in PAARE}
    keil = [q for q in teile(fps_l[PAARE[0][0]].intersection(fps_l[PAARE[0][1]])) if q.geom_type == "Polygon" and q.area > 0.01]
    from shapely.ops import polylabel
    keil_breit = max(2 * q.exterior.distance(polylabel(q, 0.001)) for q in keil)
    # Grafiken
    offs = [(-17, 14), (-22, 6), (8, 26), (-20, 2)]
    fig_ueber = uebersicht(fps_l, [(nahtgeo[p], offs[i]) for i, p in enumerate(PAARE)], outline0)
    zooms = []
    for i, (a, b) in enumerate(PAARE):
        ueber = fps_l[a].intersection(fps_l[b])
        weg = unary_union([fps_l[k].difference(neu[k]) for k in (a, b)])
        sa, sb = zoom(fps_l, neu, a, b, nahtgeo[(a, b)], ueber if ueber.area > 0.01 else G.Polygon(), wande[(a, b)], weg)
        zooms.append((i + 1, a, b, sa, sb))
    zoom_html = ""
    for n, a, b, sa, sb in zooms:
        inf = infos[(a, b)]
        cap_a = (("Rot: Fläche, auf der beide Grundrisse liegen (%s mm², bis %s mm breit)." % (de(inf["ueberlapp"], 0), de(keil_breit, 1)))
                 if inf["ueberlapp"] > 0.01 else "Beide Mulden gehen ohne Wand ineinander über.")
        cap_b = ("Gold: die stehende Wand (%s mm breit, %s mm lang). Rot gestreift: Fläche, die dem Gebäude entfällt (%s mm² und %s mm²)."
                 % (de(D.WAND_T, 1), de(wandlaenge[(a, b)], 0), de(inf["verlust_a"], 1), de(inf["verlust_b"], 1)))
        zoom_html += ('<div class="zoomrow"><h3>%d  %s und %s</h3><div class="panels">'
                      '<figure class="panel bad"><figcaption>Heute</figcaption>%s<p class="cap">%s</p></figure>'
                      '<figure class="panel ok"><figcaption>Mit Trennwand</figcaption>%s<p class="cap">%s</p></figure></div></div>'
                      % (n, NAMEN[a], NAMEN[b], sa, cap_a, sb, cap_b))
    # Tabellen
    nahtzeilen, geberzeilen = "", ""
    for i, (a, b) in enumerate(PAARE):
        inf = infos[(a, b)]
        inf["rohr_a"], inf["rohr_b"] = R[a].distance(nahtgeo[(a, b)]), R[b].distance(nahtgeo[(a, b)])
        L = nahtgeo[(a, b)].length
        nahtzeilen += ("<tr><td class=\"n\">%d</td><th>%s und %s</th><td class=\"n\">%s mm</td><td class=\"n\">%s m</td><td class=\"n bad\">0 mm</td><td class=\"hint2\">%s</td></tr>"
                       % (i + 1, NAMEN[a], NAMEN[b], de(L, 1), de(L / S, 0), "Mulden verschmolzen; Überlappung %s mm² (bis %s mm breit)" % (de(inf["ueberlapp"], 0), de(keil_breit, 1)) if inf["ueberlapp"] > 0.01 else "Mulden verschmolzen, Gebäude berühren sich"))
        wer = ("%s gibt alles ab, %s bleibt" % (NAMEN[b], NAMEN[a])) if inf["anteil"] == 0.0 else (("%s gibt alles ab, %s bleibt" % (NAMEN[a], NAMEN[b])) if inf["anteil"] == 1.0 else "beide je zur Hälfte")
        grund = ("Schachtrohr des %s liegt nur %s mm von der Naht" % (NAMEN[a], de(inf["rohr_a"], 2))) if inf["anteil"] == 0.0 else (("Schachtrohr des %s liegt nur %s mm von der Naht" % (NAMEN[b], de(inf["rohr_b"], 2))) if inf["anteil"] == 1.0 else "Rohre liegen %s und %s mm von der Naht" % (de(inf["rohr_a"], 1), de(inf["rohr_b"], 1)))
        geberzeilen += ("<tr><td class=\"n\">%d</td><th>%s und %s</th><td>%s</td><td class=\"hint2\">%s</td><td class=\"n\">%s mm² / %s mm²</td></tr>"
                        % (i + 1, NAMEN[a], NAMEN[b], wer, grund, de(inf["verlust_a"], 1), de(inf["verlust_b"], 1)))
    quellzeilen = ""
    for a, b in PAARE:
        z = []
        for q in ("osm", "lod2", "laserscan"):
            d = quellen[q][a].distance(quellen[q][b])
            o = quellen[q][a].intersection(quellen[q][b]).area
            z.append("<td class=\"n\">%s</td>" % (("Überlapp %s mm²" % de(o, 0)) if o > 0.05 else ("%s m" % de(d / S, 2))))
        quellzeilen += "<tr><th>%s und %s</th>%s</tr>" % (NAMEN[a], NAMEN[b], "".join(z))
    ctx = {
        "FIG_UEBER": fig_ueber, "ZOOMS": zoom_html, "NAHTZEILEN": nahtzeilen, "GEBERZEILEN": geberzeilen, "QUELLZEILEN": quellzeilen,
        "NAHT_SUMME": de(sum(nahtgeo[p].length for p in PAARE), 0), "NAHT_SUMME_M": de(sum(nahtgeo[p].length for p in PAARE) / S, 0),
        "FUGE": de(g1, 1), "FUGE_M": de(g1 / S, 1), "WAND": de(D.WAND_T, 1), "SPIEL": de(P.OUTLINE_CLR_T, 2),
        "DIM_X": de(dim1[0], 1), "DIM_Y": de(dim1[1], 1), "DIM_Z": de(T, 1), "DIM0_X": de(dim0[0], 3), "DIM1_X": de(dim1[0], 3),
        "DIM0_Y": de(dim0[1], 3), "DIM1_Y": de(dim1[1], 3),
        "KEIL_A": de(infos[PAARE[0]]["ueberlapp"], 0), "KEIL_A_M": de(infos[PAARE[0]]["ueberlapp"] / S ** 2, 0), "KEIL_B": de(keil_breit, 1), "KEIL_B_M": de(keil_breit / S, 1),
        "STL_UEBER": de(ueber_stl, 1),
        "DICHT0": "ja" if tm0.is_watertight else "nein", "DICHT1": "ja" if tm1.is_watertight else "nein",
        "KOLL": de(koll, 2), "HOF_DIFF": de(hof_diff, 4),
        "WAND_MIN": de(min(w for w in (a.distance(b) - 2 * P.OUTLINE_CLR_T for a, b in [(neu[p[0]], neu[p[1]]) for p in PAARE])), 2),
        "DECKUNG": de(100 * min(deckung.values()), 0), "WANDLAENGE": de(sum(wandlaenge.values()), 0), 
        "VOL0": de(tm0.volume / 1000, 2), "VOL1": de(tm1.volume / 1000, 2),
        "ROHR_MIN": de(min(R[k].distance(neu[k].boundary) for k in neu if k != "01_paulinum"), 1),
        "AUG_VERLUST": de(fps_l["02_neues_augusteum"].area - neu["02_neues_augusteum"].area, 0),
        "AUG_PROZENT": de(100 * (1 - neu["02_neues_augusteum"].area / fps_l["02_neues_augusteum"].area), 1),
        "AUG_M2": de((fps_l["02_neues_augusteum"].area - neu["02_neues_augusteum"].area) / S ** 2, 0),
        "TEILE": str(max(len(G.polys_of(v)) for v in neu.values())),
        "DATA_JSON": json.dumps({"tabelle": tabelle, "flaeche": {k: round(v.area, 2) for k, v in fps_l.items()}, "namen": NAMEN, "S": S}),
    }
    tpl = open(os.path.join(HERE, "page.template.html"), encoding="utf-8").read()
    for k, v in ctx.items():
        tpl = tpl.replace("{{%s}}" % k, v)
    left = sorted(set(re.findall(r"\{\{([A-Z0-9_]+)\}\}", tpl)))
    if left:
        raise SystemExit("unbelegte Platzhalter: %s" % left)
    out = os.path.join(HERE, "page.html")
    open(out, "w", encoding="utf-8").write(tpl)
    print("Platte %.3f × %.3f → %.3f × %.3f; dicht %s/%s; Wand steht zu %.0f %%, Länge %.0f mm; Hof-Diff %.4f; Koll %.2f; STL-Überlapp %.2f mm²; Überlappung %.1f mm² bis %.1f mm; %s (%d KB)"
          % (dim0[0], dim0[1], dim1[0], dim1[1], tm0.is_watertight, tm1.is_watertight, 100 * min(deckung.values()), sum(wandlaenge.values()), hof_diff, koll, ueber_stl,
             infos[PAARE[0]]["ueberlapp"], keil_breit, os.path.relpath(out, G.HERE), os.path.getsize(out) // 1024))


if __name__ == "__main__":
    main()
