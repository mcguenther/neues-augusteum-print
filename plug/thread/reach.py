#!/usr/bin/env python3
"""Einfädelprobe im Schnitt: kommt eine gerade, starre Nadel durch einen gebogenen V-Kanal?

Der Kanal wird im Schnitt (x entlang der V-Achse, z Höhe über der Plattenunterseite) als freie Fläche gerastert; darunter liegt die Eckaussparung des
Unterkastens als freier Raum (Breite `FREE_X`, Tiefe `params.UK_H`). Die Nadel ist eine Strecke der Länge L mit Durchmesser w. Sie darf überall liegen, wo
die Strecke mindestens w/2 Abstand zur Wand hat; die **Spitze** muss im Kanal bleiben (z ≥ 0). Gesucht ist, ob sich die Spitze von der Mündung des einen
Schenkels zur Mündung des anderen führen lässt (Zusammenhang im Konfigurationsraum Spitze × Winkel). Das ist die Näherung für die ungünstigste Ebene: der Kanal
ist quer dazu nur so breit wie in der Ebene, die Nadel kann dort nicht ausweichen.

Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m plug.thread.reach          # Tabelle: längste durchführbare Nadel je Kanal
"""
import math

import numpy as np
from scipy import ndimage
from shapely import contains_xy
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

from plug.thread import params as P

RES = 0.2           # mm je Rasterpunkt
FREE_X = 12.0       # Eckaussparung unter dem Kanal: |x| ≤ FREE_X frei
X0, X1, Z0, Z1 = -15.0, 15.0, -P.UK_H - 1.0, 12.0


def tunnel(leg_d, apex, slope, entry_r, margin=0.0):
    """Freie Fläche des V-Kanals im Schnitt (Λ aus zwei Schenkeln mit rundem Scheitel, Trichter an der Unterseite)."""
    hs = apex * slope
    r = leg_d / 2.0 - margin
    parts = []
    for s in (-1, 1):
        a, b = (s * hs * (1 + 0.5 / apex), -0.5), (0.0, apex)
        dx, dz = b[0] - a[0], b[1] - a[1]
        n = math.hypot(dx, dz)
        nx, nz = -dz / n * r, dx / n * r
        parts.append(Polygon([(a[0] + nx, a[1] + nz), (b[0] + nx, b[1] + nz), (b[0] - nx, b[1] - nz), (a[0] - nx, a[1] - nz)]))
    parts.append(Point(0.0, apex).buffer(r, 32))
    for s in (-1, 1):                      # Trichter: Kegel von entry_r am Bett auf Schenkelbreite nach 1,5 mm
        parts.append(Polygon([(s * hs - entry_r, 0.0), (s * hs + entry_r, 0.0), (s * hs + r, 1.5), (s * hs - r, 1.5)]))
    return unary_union(parts)


def free_mask(poly):
    xs = np.arange(X0, X1 + RES / 2, RES)
    zs = np.arange(Z0, Z1 + RES / 2, RES)
    gx, gz = np.meshgrid(xs, zs, indexing="ij")
    free = contains_xy(poly, gx, gz)
    below = (gz < 0.0) & (np.abs(gx) <= FREE_X) & (gz > -P.UK_H)
    return xs, zs, free | below


def _reach_labels(poly, length, needle_d, step_mm=0.35):
    """Konfigurationsraum (Winkel × x × z der Spitze) als Raster; Etiketten der zusammenhängenden freien Lagen."""
    xs, zs, free = free_mask(poly)
    clear = ndimage.distance_transform_edt(free) * RES          # Abstand zur Wand in mm
    nx, nz = free.shape
    na = max(36, int(math.ceil(2 * math.pi * length / step_mm)))
    ang = np.linspace(0.0, 2 * math.pi, na, endpoint=False)
    need = needle_d / 2.0 + 0.5 * RES
    ts = np.arange(0.0, length + 1e-9, RES * 1.5)
    ix, iz = np.meshgrid(np.arange(nx), np.arange(nz), indexing="ij")
    tip_in = np.broadcast_to(zs[None, :] >= 0.0, (nx, nz))      # die Spitze bleibt im Kanal (z ≥ 0)
    ok = np.zeros((na, nx, nz), bool)
    for k, a in enumerate(ang):
        fit = tip_in.copy()
        for t in ts:                                             # Nadel liegt von der Spitze aus in Richtung (cos a, sin a)
            jx = np.clip(np.rint(ix + t * math.cos(a) / RES).astype(int), 0, nx - 1)
            jz = np.clip(np.rint(iz + t * math.sin(a) / RES).astype(int), 0, nz - 1)
            fit &= clear[jx, jz] >= need
        ok[k] = fit
    lab, _ = ndimage.label(ok)
    return lab, xs, zs


def check(leg_d, apex, slope, entry_r, length, needle_d):
    """True, wenn sich eine gerade Nadel (Länge, Durchmesser in mm) mit der Spitze von einer Mündung des V zur anderen führen lässt."""
    lab, xs, zs = _reach_labels(tunnel(leg_d, apex, slope, entry_r), length, needle_d)
    hs = apex * slope
    j = np.where((zs >= 0.0) & (zs <= 1.0))[0]
    ends = []
    for xc in (-hs, hs):
        i = np.where(np.abs(xs - xc) <= 0.8)[0]
        sub = lab[:, i[0]:i[-1] + 1, j[0]:j[-1] + 1]
        ends.append(set(np.unique(sub[sub > 0]).tolist()))
    parent = {}

    def find(a):
        while parent.setdefault(a, a) != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for a, b in zip(lab[0].ravel(), lab[-1].ravel()):           # Winkel schließt sich: 0° und 360° sind dieselbe Lage
        if a and b:
            parent[find(a)] = find(b)
    return bool({find(i) for i in ends[0]} & {find(i) for i in ends[1]})


def max_length(leg_d, apex, slope, entry_r, needle_d, lengths=(2, 3, 4, 6, 8, 10, 12, 15, 20, 30, 45)):
    """Längste Nadel aus `lengths`, die sich durchführen lässt (0, wenn schon die kürzeste nicht geht)."""
    best = 0
    for L in lengths:
        if check(leg_d, apex, slope, entry_r, L, needle_d):
            best = L
        elif best:
            break
    return best


ROWS = (("alt", "alt (Steckprobe 2)", P.OLD), ("A", "A weit", P.A), ("A5", "A, Ø 5,0", dict(P.A, leg_d=5.0)), ("A70", "A, steil 70°", dict(P.A, slope=0.36)))
JSON = __file__.replace("reach.py", "reach.json")


def _one(t):
    key, nd, v = t
    return max_length(v["leg_d"], v["apex"], v["slope"], v["entry_r"], nd)


def table(jobs=None):
    """Längste durchführbare Nadel je Kanalform und Nadeldurchmesser (mm; 0 = schon 2 mm gehen nicht); rechnet je Zeile ca. 1 bis 2 min."""
    import parallel                      # liegt im Repo-Wurzelverzeichnis
    tasks = [(key, nd, v) for key, _, v in ROWS for _, nd in P.NEEDLES]

    if jobs:
        parallel.JOBS = jobs
    res = parallel.starmap(_one, [(t,) for t in tasks])
    return {"%s|%.1f" % (t[0], t[1]): r for t, r in zip(tasks, res)}


if __name__ == "__main__":
    import json
    import sys
    import time
    t0 = time.time()
    out = table()
    for key, name, v in ROWS:
        print("%-20s Ø %.1f  Scheitel %.1f  Schenkel %2d°  längste Nadel: %s" % (name, v["leg_d"], v["apex"], round(P.slope_deg(v["slope"])),
              "  ".join("%s %s mm" % (n, out["%s|%.1f" % (key, d)] or "keine") for n, d in P.NEEDLES)))
    if "--write" in sys.argv:
        with open(JSON, "w") as f:
            json.dump(out, f, indent=1)
        print("geschrieben:", JSON)
    print("%.0f s" % (time.time() - t0))
