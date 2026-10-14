#!/usr/bin/env python3
"""Pose-Suche über die Himmelslinie: Foto (Himmel/Gebäude) gegen Silhouette des 3D-Modells.

Für die meisten Straßenfotos ist der Himmel sichtbar. Die Linie, an der der Himmel
endet, ist im Foto leicht zu finden und im Modell exakt berechenbar (Vereinigung aller
projizierten Dreiecke). Aus dem Abstand beider Linien je Bildspalte entsteht eine
Kostenfunktion für Position, Blickrichtung, Neigung und Brennweite; ein globaler
Optimierer (differential evolution) findet die Pose, danach verfeinert kamera.register
mit den Kanten.
"""
import cv2
import numpy as np
from scipy import optimize

import kamera as K


def himmel_maske(img, breite=480):
    """Himmel als Binärmaske (True = Himmel) in verkleinerter Auflösung; PIL-Bild -> (mask, scale)."""
    a = np.asarray(img.convert("RGB"))
    s = breite / a.shape[1]
    sm = cv2.resize(a, None, fx=s, fy=s, interpolation=cv2.INTER_AREA).astype(np.float32)
    r, g, b = sm[..., 0], sm[..., 1], sm[..., 2]
    mx, mn = sm.max(-1), sm.min(-1)
    sat = (mx - mn) / np.maximum(mx, 1)
    blau = (b > r + 12) & (b >= g - 6) & (mx > 90)
    hell = (mn > 150) & (sat < 0.22)
    grau = (mx > 120) & (sat < 0.12)          # bedeckter Himmel
    cand = (blau | hell | grau).astype(np.uint8)
    # Textur: Himmel ist glatt (Gradient klein), Fassaden/Bäume nicht
    gray = cv2.cvtColor(sm.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
    gx, gy = cv2.Sobel(gray, cv2.CV_32F, 1, 0), cv2.Sobel(gray, cv2.CV_32F, 0, 1)
    grad = cv2.GaussianBlur(np.hypot(gx, gy), (0, 0), 1.0)
    cand &= (grad < 70).astype(np.uint8)
    cand = cv2.morphologyEx(cand, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab = cv2.connectedComponents(cand, connectivity=4)
    top = np.unique(lab[: max(2, sm.shape[0] // 40)])
    mask = np.isin(lab, top[top > 0])
    mask = cv2.morphologyEx(mask.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)).astype(bool)
    return mask, s


def himmelslinie(mask):
    """Je Spalte die Zeile, ab der der Himmel von oben her endet (0 = Gebäude bis zum Rand)."""
    nicht = ~mask
    first = np.where(nicht.any(0), nicht.argmax(0), mask.shape[0])
    return first.astype(np.float32)


def modelllinie(kam, tris, scale, W, H, near=1.0):
    """Himmelslinie des Modells (Zeile je Spalte) bei Bildgröße (W, H) aus der Kamera."""
    uv, z = kam.project(tris.reshape(-1, 3))
    z = z.reshape(-1, 3)
    ok = z.min(1) > near
    if not ok.any():
        return np.full(W, H, np.float32)
    p = (uv.reshape(-1, 3, 2)[ok] * scale)
    p = np.clip(p, -3e4, 3e4)
    mask = np.zeros((H, W), np.uint8)
    cv2.fillPoly(mask, list(np.round(p * 16).astype(np.int32)), 1, shift=4)
    has = mask.any(0)
    return np.where(has, mask.argmax(0), H).astype(np.float32)


class Suche:
    def __init__(self, img, tris, breite=480, min_abdeckung=0.4):
        self.min_abd = min_abdeckung
        self.W0, self.H0 = img.size
        self.mask, self.scale = himmel_maske(img, breite)
        self.H, self.W = self.mask.shape
        self.line = himmelslinie(self.mask)
        self.tris = tris
        self.k = self.W / self.W0     # Pixel Originalbild -> Suchbild

    def kosten(self, p):
        x, y, z, yaw, pitch, roll, hfov = p
        kam = K.Kamera.aus_pose([x, y, z], yaw, pitch, roll, hfov, self.W0, self.H0)
        ml = modelllinie(kam, self.tris, self.k, self.W, self.H)
        d = np.abs(ml - self.line) / self.H
        # Spalten, in denen das Modell nichts zeigt, zählen nicht (nicht modellierte Nachbargebäude)
        m = ml < self.H
        if m.sum() < 0.04 * self.W:
            return 1.0
        # Das Modell soll einen erwarteten Anteil der Bildbreite bedecken (sonst „versteckt“ es sich am Rand)
        fehl = max(0.0, self.min_abd - m.mean()) / self.min_abd
        return float(np.minimum(d[m], 0.15).mean() + 0.08 * fehl)

    def lauf(self, grenzen, popsize=14, maxiter=120, seed=1, workers=1, x0=None):
        res = optimize.differential_evolution(self.kosten, grenzen, popsize=popsize, maxiter=maxiter, seed=seed,
                                              tol=1e-4, mutation=(0.4, 0.9), recombination=0.8, polish=False,
                                              workers=workers, updating="deferred" if workers != 1 else "immediate",
                                              x0=x0)
        x, y, z, yaw, pitch, roll, hfov = res.x
        return K.Kamera.aus_pose([x, y, z], yaw, pitch, roll, hfov, self.W0, self.H0), res.fun


def darstellung(img, suche, kam=None):
    """Foto mit Himmelsmaske (blau getönt) und Himmelslinien: Foto grün, Modell rot."""
    a = np.array(img.convert("RGB"))
    m = cv2.resize(suche.mask.astype(np.uint8), (a.shape[1], a.shape[0]), interpolation=cv2.INTER_NEAREST) > 0
    a[m] = (0.65 * a[m] + 0.35 * np.array([0, 0, 255])).astype(np.uint8)
    xs = np.arange(suche.W)
    sx = xs / suche.k
    for x, y in zip(sx, suche.line / suche.k):
        cv2.circle(a, (int(x), int(y)), 2, (0, 255, 0), -1)
    if kam is not None:
        ml = modelllinie(kam, suche.tris, suche.k, suche.W, suche.H)
        for x, y in zip(sx, ml / suche.k):
            if y < suche.H / suche.k - 1:
                cv2.circle(a, (int(x), int(y)), 2, (255, 0, 0), -1)
    from PIL import Image
    return Image.fromarray(a)
