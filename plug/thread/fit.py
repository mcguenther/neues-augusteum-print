#!/usr/bin/env python3
"""Passt die Fadentasche in die echte Oberplatte? Prüft an den vier Ecken der Grundplatte (Umriss und gesperrte Flächen wie in plug/power/build_concept.py).

Gesperrt sind die Mulden der Gebäude (mit Spiel) und die Vertiefung des Innenhofs, jeweils mit `params.WALL_MIN` Wand. Die Tasche liegt mit der langen Seite
parallel zur nächsten Kante, so nah an der Ecke wie möglich; Maßgeblich ist die gefaste Mündung an der Unterseite (`pill()['mouth_l']` × `['mouth_w']`); die Eckaussparung im Unterkasten reicht `params.NOTCH_PAD` darüber hinaus und darf bis zum Rand offen sein.

Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m plug.thread.fit [--write]        # Tabelle je Maßstab 1:1000 und 1:1300, ca. 1 min; --write schreibt fit.json
"""
import json
import sys

import numpy as np
from shapely.geometry import box
from shapely.ops import unary_union

from plug.power import build_concept as BC
from plug.power import params as PP
from plug.thread import params as P

JSON = __file__.replace("fit.py", "fit.json")


def plate(scale):
    """Umriss der Oberplatte und gesperrte Fläche (Mulden, Hof) im Maßstab 1:scale, Koordinaten in mm wie im Konzept."""
    s = 1000.0 / scale
    m = BC.G.osm_models(s)
    fps = {k: v[1] for k, v in m.items()}
    _, hof_fp, _ = BC.innenhof.model(s, list(fps.values()))
    foot = unary_union([fps[b["slug"]] for b in BC.G.BUILDINGS])
    outline = BC.G.plate_outline(unary_union([foot, hof_fp]))
    blocked = unary_union([foot.buffer(PP.MULDE_CLR), hof_fp.buffer(BC.G.POCKET_CLEARANCE, join_style=2)])
    return outline, blocked


def place(outline, blocked, length, width, wall=P.WALL_MIN, step=0.5):
    """Je Ecke: kleinster Abstand (Summe der Verschiebungen in x und y) einer Tasche length × width mit Wand ringsum; beide Ausrichtungen."""
    x0, y0, x1, y1 = outline.bounds
    res = []
    for sx, sy, cx, cy in ((1, 1, x0, y0), (-1, 1, x1, y0), (1, -1, x0, y1), (-1, -1, x1, y1)):
        best = None
        for horiz in (True, False):
            lx, ly = (length, width) if horiz else (width, length)
            for da in np.arange(0, 80, step):
                for db in np.arange(0, 80, step):
                    if best is not None and da + db >= best[0]:
                        break
                    ax = cx + sx * (lx / 2 + wall + da)
                    ay = cy + sy * (ly / 2 + wall + db)
                    foot = box(ax - lx / 2 - wall, ay - ly / 2 - wall, ax + lx / 2 + wall, ay + ly / 2 + wall)
                    if outline.contains(foot) and not foot.intersects(blocked):
                        best = (da + db, round(float(ax), 1), round(float(ay), 1), "x" if horiz else "y")
        res.append(None if best is None else dict(shift=round(best[0], 1), c=best[1:3], axis=best[3]))
    return res


def table():
    out = {}
    for scale in (1000, 1300):
        outline, blocked = plate(scale)
        row = {"plate": [round(outline.bounds[2] - outline.bounds[0], 1), round(outline.bounds[3] - outline.bounds[1], 1)]}
        for name, (l, w) in (("alt", (2 * (BC.V["slope"] * BC.V["apex"] + BC.V["entry_r"]), 2 * BC.V["entry_r"])),
                             ("pille3", (P.pill(3.0)["mouth_l"], P.pill(3.0)["mouth_w"])), ("pille4", (P.pill(4.0)["mouth_l"], P.pill(4.0)["mouth_w"])), ("pille45", (P.pill(4.5)["mouth_l"], P.pill(4.5)["mouth_w"]))):
            row[name] = place(outline, blocked, l, w)
        out["1:%d" % scale] = row
    return out


if __name__ == "__main__":
    t = table()
    for k, row in t.items():
        print(k, "Platte", row["plate"])
        for name in ("alt", "pille3", "pille4", "pille45"):
            print("   %-8s %s" % (name, [("–" if r is None else "%s mm von der Ecke" % r["shift"]) for r in row[name]]))
    if "--write" in sys.argv:
        with open(JSON, "w") as f:
            json.dump(t, f, indent=1)
        print("geschrieben:", JSON)
