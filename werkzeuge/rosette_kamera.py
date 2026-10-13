#!/usr/bin/env python3
"""Kameramodell für die Rosette und den Spitzbogen am Paulinum-Ostgiebel.

Passt eine Lochkamera (Brennweite, Neigung nach oben, Abstand) an das Foto
„Leipzig - Paulinum.jpg“ (Fred Romero, CC BY 2.0, Schlüssel pl_giebel_romero2 in
data/fassaden/01_paulinum.json) an. Bekannt sind die Firsthöhe der Giebelkante
aus dem LoD2-Modell (48,3 m) und dass die Giebelkanten Geraden sind; im Foto
gemessen (Pixel, Bild 1920 × 1280) sind First, je zwei Punkte der beiden
Giebelkanten und die Umrisspunkte der Rosette. Ergebnis: Höhe/Durchmesser der
Rosette und Höhen/Breiten von Spitzbogen-Blende und Maßwerkfenster, wie sie in
data/fassaden/01_paulinum.json stehen.

Aufruf:  python3 werkzeuge/rosette_kamera.py
"""
import numpy as np
from scipy.optimize import least_squares
W, Hh = 1920, 1280
cx, cy = W / 2, Hh / 2
ZA, HC = 48.3, 1.6   # LoD2-First (außen, Glaskante), Kamerahöhe
def proj(p, u, z):
    f, th, D = p[:3]
    xc = u
    yc = (z - HC) * np.cos(th) - D * np.sin(th)
    dep = D * np.cos(th) + (z - HC) * np.sin(th)
    return cx + f * xc / dep, cy - f * yc / dep
def res(q):
    f, th, D, ta, zr, d = q
    p = (f, th, D)
    r = []
    x, y = proj(p, 0, ZA); r += [x - 954, y - 25.6]
    # Kantenpunkte: für gemessene Bild-y die Bild-x
    for side, pts in ((-1, [(512, 330), (314, 586)]), (1, [(512, 1594), (314, 1332)])):
        for yi, xi in pts:
            # Punkt auf der Kante mit Bild-y = yi suchen (z über Bisektion)
            lo, hi = -30.0, ZA
            for _ in range(60):
                zm = (lo + hi) / 2
                u = side * (ZA - zm) / ta
                _, ym = proj(p, u, zm)
                if ym > yi: lo = zm
                else: hi = zm
            u = side * (ZA - zm) / ta
            xm, _ = proj(p, u, zm)
            r.append(xm - xi)
    xt, yt = proj(p, 0, zr + d / 2); xb, yb = proj(p, 0, zr - d / 2)
    xl, yl = proj(p, -d / 2, zr); xr_, yr = proj(p, d / 2, zr)
    r += [yt - 246, yb - 380, xl - 839, xr_ - 1089]
    return r
best = None
for f0 in (1200, 1600, 2200, 3000):
    for th0 in (0.4, 0.6, 0.8):
        for D0 in (20, 35, 50):
            s = least_squares(res, [f0, th0, D0, 2.0, 38, 5], bounds=([300, 0, 5, 0.8, 10, 1], [8000, 1.4, 200, 4, 48, 15]))
            if best is None or s.cost < best.cost:
                best = s
f, th, D, ta, zr, d = best.x
print('f=%.0f px  Neigung=%.1f°  Abstand=%.1f m  tanα=%.2f (%.0f°)  Rosette z=%.1f m  d=%.1f m  Rest=%.1f px' % (
    f, np.degrees(th), D, ta, np.degrees(np.arctan(ta)), zr, d, np.sqrt(2 * best.cost / len(best.fun))))
p = (f, th, D)
def z_of_y(yi):
    lo, hi = -40.0, ZA + 10
    for _ in range(80):
        zm = (lo + hi) / 2
        _, ym = proj(p, 0, zm)
        if ym > yi: lo = zm
        else: hi = zm
    return zm
for name, yfrac in (('Steinfirst', 0.07), ('Spitzbogen außen, Spitze', 0.355), ('Fenster, Spitze', 0.535), ('Bildunterkante', 1.0)):
    print('%-26s z = %.1f m' % (name, z_of_y(yfrac * Hh)))
# Breite des Spitzbogens und Fensters auf Höhe y (Bildbruchteile x links/rechts)
def u_of_x(xi, z):
    dep = D * np.cos(th) + (z - HC) * np.sin(th)
    return (xi - cx) * dep / f
for name, yfrac, xl, xr in (('Bogen außen @0.75', 0.75, 0.365, 0.80), ('Fenster @0.75', 0.75, 0.455, 0.70)):
    z = z_of_y(yfrac * Hh)
    print('%-20s z=%.1f  Breite %.1f m' % (name, z, u_of_x(xr * W, z) - u_of_x(xl * W, z)))
