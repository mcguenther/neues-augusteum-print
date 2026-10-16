#!/usr/bin/env python3
"""Grafik zu nudge.py: Lagen aus der App (gestrichelt) gegen die angepassten (gefüllt), mit Ausschnitt auf die Änderungen."""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MP
from shapely import affinity
from shapely.geometry import box as sbox
from shapely.ops import unary_union

import generate as G
from plug import campus as C
from plug.testcase import params as P

HERE = os.path.dirname(__file__)
OUT = os.path.join(os.path.dirname(os.path.dirname(HERE)), "vorschau", "steckmodul_campus", "positionen_diff.png")
NAMES = {"01_paulinum": "Paulinum", "02_neues_augusteum": "Neues Augusteum", "03_hoersaalgebaeude": "Hörsaalgebäude",
         "04_seminargebaeude": "Seminargebäude", "05_institutsgebaeude": "Institutsgebäude", "06_city_hochhaus": "City-Hochhaus"}


def rect(p, w, d):
    return affinity.translate(affinity.rotate(sbox(-w / 2, -d / 2, w / 2, d / 2), p["angle"], origin=(0, 0)), p["cx"], p["cy"])


def draw_poly(ax, g, **kw):
    for p in (g.geoms if hasattr(g, "geoms") else [g]):
        ax.add_patch(MP(list(p.exterior.coords), closed=True, **kw))


def main():
    G.FAST = True
    s = 1000.0 / P.SCALE_PLAN
    models = G.source_models("laserscan", s)
    diff = json.load(open(os.path.join(HERE, "nudge_diff.json")))
    fig = plt.figure(figsize=(13, 8.5))
    ax = fig.add_axes([0.02, 0.05, 0.40, 0.90])
    changed = [k for k, v in diff.items() if v["old"] != {**v["new"], "wall": v["old"]["wall"]} and (v["old"]["cx"], v["old"]["cy"], v["old"]["angle"]) != (v["new"]["cx"], v["new"]["cy"], v["new"]["angle"])]
    for k, (solid, fp, _) in models.items():
        if k.startswith("08"):
            continue
        draw_poly(ax, fp, fc="#e6ebf0", ec="#8a97a5", lw=0.8)
    for k, v in diff.items():
        w, d = C.shaft_size(P.CASSETTE[k])
        col = "#d1495b" if k in changed else "#1f5f8b"
        draw_poly(ax, rect(v["new"], w, d), fc=col, ec=col, alpha=0.8)
        c = rect(v["new"], w, d).centroid
        ax.annotate("%s\nWand %.1f" % (NAMES[k], v["new"]["wall"]), (c.x, c.y), xytext=(c.x + 8, c.y + 3), fontsize=8, ha="left")
    ax.set_aspect("equal"); ax.autoscale_view(); ax.axis("off"); ax.set_title("Gesamtplan 1:1300: geänderte Lage rot", fontsize=11)
    # Ausschnitt je geänderte Lage
    for i, k in enumerate(changed[:2]):
        v = diff[k]; solid, fp, _ = models[k]
        w, d = C.shaft_size(P.CASSETTE[k])
        a = fig.add_axes([0.46, 0.52 - i * 0.47, 0.50, 0.42])
        draw_poly(a, fp, fc="#e6ebf0", ec="#8a97a5", lw=1)
        old, new = rect(v["old"], w, d), rect(v["new"], w, d)
        draw_poly(a, new, fc="#d1495b", ec="#d1495b", alpha=0.55)
        draw_poly(a, old, fc="none", ec="#222", lw=1.6, ls="--")
        draw_poly(a, new.buffer(1.2, join_style=2), fc="none", ec="#d1495b", lw=0.8, ls=":")
        b = new.bounds
        a.set_xlim(b[0] - 5, b[2] + 5); a.set_ylim(b[1] - 5, b[3] + 5); a.set_aspect("equal")
        a.set_title("%s: gestrichelt = Lage aus der App, rot = angepasst (Wand %.2f → %.2f mm)\nVerschiebung dx %+.2f, dy %+.2f mm, Drehung %+.1f°"
                    % (NAMES[k], v["old"]["wall"], v["new"]["wall"], v["new"]["cx"] - v["old"]["cx"], v["new"]["cy"] - v["old"]["cy"], v["new"]["angle"] - v["old"]["angle"]), fontsize=9)
    fig.text(0.46, 0.015, "Alle anderen Lagen unverändert. Gepunkteter Rahmen = bevorzugte Wand 1,2 mm um den Schacht.", fontsize=9)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    fig.savefig(OUT, dpi=110)
    print(OUT)


if __name__ == "__main__":
    main()
