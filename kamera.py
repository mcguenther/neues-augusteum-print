#!/usr/bin/env python3
"""Kameramodell und Projektion des Gebäudemodells in Fotos (für die Farbmessung).

Pose: Position (lokale Meter, x Ost, y Nord, z hoch), Blickrichtung als Kompasskurs
`yaw` (0 = Nord, 90 = Ost), Neigung `pitch` (+ = nach oben), `roll`, Bildwinkel
`hfov` (horizontal, Grad). Pixel (0, 0) = links oben.

- `Kamera.ids`      schneller Flächen-ID-Puffer (Painter-Algorithmus, cv2) – für
                    Registrierung und Überlagerungen
- `Kamera.exakt`    exakter Tiefenpuffer (preview.rasterize) mit 3D-Punkt je Pixel – für die Messung
- `register`        Pose-Feinabgleich: Kanten des Modells gegen Bildkanten (Chamfer-Abstand)
- `pnp`             Pose aus Punktkorrespondenzen (3D-Eckpunkt <-> Pixel)

Aufruf (Überlagerung prüfen):
    python3 kamera.py ueberlagerung foto.jpg pose.json out.jpg
"""
import json
import sys

import cv2
import numpy as np

import szene


def _basis(yaw, pitch, roll):
    y, p, r = np.radians([yaw, pitch, roll])
    fwd = np.array([np.sin(y) * np.cos(p), np.cos(y) * np.cos(p), np.sin(p)])
    right = np.array([np.cos(y), -np.sin(y), 0.0])
    up = np.cross(right, fwd)
    right, up = right * np.cos(r) + up * np.sin(r), up * np.cos(r) - right * np.sin(r)
    return np.array([right, up, fwd])


class Kamera:
    def __init__(self, pos, R, f, W, H, cx=None, cy=None):
        self.pos, self.R, self.f, self.W, self.H = np.asarray(pos, float), np.asarray(R, float), float(f), int(W), int(H)
        self.cx = W / 2 if cx is None else cx
        self.cy = H / 2 if cy is None else cy

    @classmethod
    def aus_pose(cls, pos, yaw, pitch, roll, hfov, W, H):
        return cls(pos, _basis(yaw, pitch, roll), (W / 2) / np.tan(np.radians(hfov / 2)), W, H)

    @classmethod
    def aus_dict(cls, d, W, H):
        """d: pos, yaw, pitch, roll, hfov (oder f in Pixeln)."""
        k = cls.aus_pose(d["pos"], d["yaw"], d.get("pitch", 0), d.get("roll", 0), d.get("hfov", 60), W, H)
        if "f" in d:
            k.f = float(d["f"])
        return k

    def pose(self):
        """(yaw, pitch, roll) aus R."""
        right, up, fwd = self.R
        yaw = np.degrees(np.arctan2(fwd[0], fwd[1]))
        pitch = np.degrees(np.arcsin(np.clip(fwd[2], -1, 1)))
        r0 = np.array([np.cos(np.radians(yaw)), -np.sin(np.radians(yaw)), 0.0])
        u0 = np.cross(r0, fwd)
        roll = np.degrees(np.arctan2(right @ u0, right @ r0))
        return float(yaw), float(pitch), float(roll)

    def hfov(self):
        return float(np.degrees(2 * np.arctan((self.W / 2) / self.f)))

    def to_dict(self):
        y, p, r = self.pose()
        return dict(pos=[round(float(v), 3) for v in self.pos], yaw=round(y, 3), pitch=round(p, 3),
                    roll=round(r, 3), hfov=round(self.hfov(), 3))

    def cam(self, P):
        """Weltpunkte -> Kamerakoordinaten (x rechts, y oben, z vorwärts)."""
        return (np.asarray(P, float) - self.pos) @ self.R.T

    def project(self, P):
        c = self.cam(P)
        z = np.where(np.abs(c[:, 2]) < 1e-9, 1e-9, c[:, 2])
        return np.column_stack([self.cx + self.f * c[:, 0] / z, self.cy - self.f * c[:, 1] / z]), c[:, 2]

    def strahl(self, u, v):
        """Pixel -> Weltrichtung (Einheitsvektoren)."""
        d = np.stack([(u - self.cx) / self.f, -(v - self.cy) / self.f, np.ones_like(u, dtype=float)], -1)
        d = d @ self.R
        return d / np.linalg.norm(d, axis=-1, keepdims=True)

    # ------------------------------------------------------------------
    NEAR = 0.3

    def _projiziert(self, tris, normals):
        """Dem Betrachter zugewandte Dreiecke, an der Nahebene z = NEAR beschnitten, in Bildkoordinaten.
        Gibt (uv[n,3,2], z_cam[n,3], orig[n]) zurück; orig = Index des Ausgangsdreiecks (für Gebäude/Normalen)."""
        c = tris.mean(1)
        front = np.einsum("ij,ij->i", normals, self.pos - c) > 0
        idx = np.nonzero(front)[0]
        cam = self.cam(tris[idx].reshape(-1, 3)).reshape(-1, 3, 3)
        z = cam[..., 2]
        inside = z >= self.NEAR
        n_in = inside.sum(1)
        ok_all = n_in == 3
        out_cam, out_idx = [cam[ok_all]], [idx[ok_all]]
        for t in np.nonzero((n_in > 0) & (n_in < 3))[0]:         # teilweise hinter der Kamera: beschneiden
            poly = []
            for i in range(3):
                a_, b_ = cam[t, i], cam[t, (i + 1) % 3]
                ia, ib = inside[t, i], inside[t, (i + 1) % 3]
                if ia:
                    poly.append(a_)
                if ia != ib:
                    k = (self.NEAR - a_[2]) / (b_[2] - a_[2])
                    poly.append(a_ + k * (b_ - a_))
            for j in range(1, len(poly) - 1):
                out_cam.append(np.array([[poly[0], poly[j], poly[j + 1]]]))
                out_idx.append(np.array([idx[t]]))
        cam = np.concatenate(out_cam) if out_cam else np.zeros((0, 3, 3))
        orig = np.concatenate(out_idx) if out_idx else np.zeros(0, int)
        zc = np.maximum(cam[..., 2], 1e-6)
        uv = np.stack([self.cx + self.f * cam[..., 0] / zc, self.cy - self.f * cam[..., 1] / zc], -1)
        return uv, cam[..., 2], orig

    def ids(self, tris, normals, scale=1.0):
        """ID-Puffer (int32, -1 = leer) im Maßstab `scale` (Painter-Algorithmus, schnell, nicht exakt)."""
        W, H = int(self.W * scale), int(self.H * scale)
        buf = np.full((H, W), -1, np.int32)
        uv, z, orig = self._projiziert(tris, normals)
        if not len(orig):
            return buf
        uv = uv * scale
        for i in np.argsort(-z.mean(1)):
            p = np.round(np.clip(uv[i], -3e4, 3e4) * 16).astype(np.int32)
            cv2.fillConvexPoly(buf, p, int(orig[i]), shift=4)
        return buf

    def exakt(self, tris, normals, scale=1.0):
        """Exakter Tiefenpuffer: (fid[H,W], tiefe z_cam[H,W] in m, NaN = leer)."""
        import preview as P
        W, H = int(self.W * scale), int(self.H * scale)
        uv, z, orig = self._projiziert(tris, normals)
        if not len(orig):
            return np.full((H, W), -1), np.full((H, W), np.nan)
        uv = uv * scale
        inv = 1.0 / np.maximum(z, 1e-3)
        zbuf, tid = P.rasterize(uv[..., 0], uv[..., 1], inv, np.arange(len(orig)), W, H)
        fid = np.where(tid >= 0, orig[np.maximum(tid, 0)], -1)
        with np.errstate(divide="ignore"):
            tiefe = np.where(tid >= 0, 1.0 / zbuf, np.nan)
        return fid, tiefe

    def punkte(self, tiefe, scale=1.0):
        """3D-Weltpunkt je Pixel aus Tiefe z_cam (NaN bleibt NaN) -> [H,W,3]."""
        H, W = tiefe.shape
        u, v = np.meshgrid((np.arange(W) + 0.5) / scale, (np.arange(H) + 0.5) / scale)
        d = np.stack([(u - self.cx) / self.f, -(v - self.cy) / self.f, np.ones_like(u)], -1)  # z_cam = 1
        return self.pos + (d * tiefe[..., None]) @ self.R


# --------------------------------------------------------------------------
# Kanten des Modells
# --------------------------------------------------------------------------
def kantenbild(kam, tris, normals, scale=0.5, winkel=25.0):
    """Binärbild der sichtbaren Modellkanten: Silhouette und Knicke > winkel (Grad)."""
    ids = kam.ids(tris, normals, scale)
    out = np.zeros(ids.shape, np.uint8)
    # Sprünge der Flächen-ID (Gebäude-/Flächenränder) und der Normalenrichtung
    nid = np.where(ids >= 0, ids, -1)
    nrm = np.zeros(ids.shape + (3,), np.float32)
    hit = ids >= 0
    nrm[hit] = normals[ids[hit]]
    for dy, dx in ((0, 1), (1, 0)):
        a, b = nid[: ids.shape[0] - dy, : ids.shape[1] - dx], nid[dy:, dx:]
        na, nb = nrm[: ids.shape[0] - dy, : ids.shape[1] - dx], nrm[dy:, dx:]
        cosang = (na * nb).sum(-1)
        e = (a != b) & ((a < 0) | (b < 0) | (cosang < np.cos(np.radians(winkel))))
        out[: ids.shape[0] - dy, : ids.shape[1] - dx] |= e.astype(np.uint8)
    return out, ids


def bildkanten(gray, scale=0.5):
    g = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    g = cv2.GaussianBlur(g, (0, 0), 1.2)
    med = np.median(g)
    return cv2.Canny(g, 0.66 * med, 1.33 * med + 20)


def register(kam, tris, normals, gray, frei=("yaw", "pitch", "roll", "x", "y", "z", "hfov"),
             scale=0.4, schritte=(3.0, 1.0, 0.3), verbose=False):
    """Feinabgleich der Pose durch Minimieren des abgeschnittenen Chamfer-Abstands zwischen
    Modellkanten und Canny-Kanten des Fotos (Koordinatenabstieg, grob nach fein).

    Gibt (Kamera, Kosten_vorher, Kosten_nachher) zurück."""
    edges = bildkanten(gray, scale)
    dist = cv2.distanceTransform(255 - edges, cv2.DIST_L2, 3)
    trunc = 25.0

    def kosten(k):
        m, _ = kantenbild(k, tris, normals, scale)
        if m.sum() < 30:
            return trunc
        ys, xs = np.nonzero(m)
        d = np.minimum(dist[ys, xs], trunc)
        return float(d.mean())

    p = dict(yaw=kam.pose()[0], pitch=kam.pose()[1], roll=kam.pose()[2], x=kam.pos[0], y=kam.pos[1], z=kam.pos[2],
             hfov=kam.hfov())

    def bauen(p):
        k = Kamera.aus_pose([p["x"], p["y"], p["z"]], p["yaw"], p["pitch"], p["roll"], p["hfov"], kam.W, kam.H)
        return k

    c0 = kosten(kam)
    best = c0
    einheit = dict(yaw=1.0, pitch=1.0, roll=0.5, x=1.0, y=1.0, z=0.3, hfov=1.5)
    for sch in schritte:
        for _ in range(6):
            besser = False
            for name in frei:
                for sgn in (+1, -1):
                    q = dict(p)
                    q[name] += sgn * sch * einheit[name]
                    c = kosten(bauen(q))
                    if c < best - 1e-3:
                        best, p, besser = c, q, True
            if verbose:
                print("   Schritt %.1f: %.2f px" % (sch, best))
            if not besser:
                break
    return bauen(p), c0, best


def pnp(pts3d, pts2d, W, H, hfov=60.0, f=None):
    """Pose aus ≥ 4 Korrespondenzen (feste Brennweite aus hfov). Gibt Kamera und mittleren
    Rückprojektionsfehler (Pixel) zurück."""
    f = f or (W / 2) / np.tan(np.radians(hfov / 2))
    K = np.array([[f, 0, W / 2], [0, f, H / 2], [0, 0, 1]], float)
    P3, P2 = np.asarray(pts3d, np.float64), np.asarray(pts2d, np.float64)
    ok, rvec, tvec = cv2.solvePnP(P3, P2, K, None, flags=cv2.SOLVEPNP_EPNP if len(P3) > 5 else cv2.SOLVEPNP_ITERATIVE)
    ok, rvec, tvec = cv2.solvePnP(P3, P2, K, None, rvec, tvec, True, cv2.SOLVEPNP_ITERATIVE)
    Rw, _ = cv2.Rodrigues(rvec)           # x_cam(OpenCV: rechts, unten, vorwärts) = Rw x + t
    pos = (-Rw.T @ tvec).ravel()
    R = np.array([Rw[0], -Rw[1], Rw[2]])  # rechts, oben, vorwärts
    kam = Kamera(pos, R, f, W, H)
    uv, _ = kam.project(P3)
    return kam, float(np.linalg.norm(uv - P2, axis=1).mean())


# --------------------------------------------------------------------------
# Überlagerung zum Prüfen
# --------------------------------------------------------------------------
FARBEN = [(255, 60, 60), (60, 200, 60), (60, 120, 255), (255, 170, 0), (200, 60, 255), (0, 200, 200),
          (200, 200, 0), (255, 100, 180)]


def ueberlagerung(img, kam, szene_, pfad=None, punkte=None, fuellung=0.30):
    """Zeichnet das Modell über das Foto: Flächen je Gebäude halbtransparent gefärbt, Kanten kräftig."""
    from PIL import Image, ImageDraw
    mesh, bid, slugs = szene.gesamt(szene_)
    tris, nrm = mesh.triangles, mesh.face_normals
    kb, ids = kantenbild(kam, tris, nrm, scale=1.0)
    out = np.array(img.convert("RGB"), np.uint8).astype(np.float32)
    if kb.shape[:2] != out.shape[:2]:
        kb = cv2.resize(kb, (out.shape[1], out.shape[0]), interpolation=cv2.INTER_NEAREST)
        ids = cv2.resize(ids, (out.shape[1], out.shape[0]), interpolation=cv2.INTER_NEAREST)
    hit = ids >= 0
    col = np.array(FARBEN, np.float32)[bid[np.maximum(ids, 0)] % len(FARBEN)]
    out[hit] = (1 - fuellung) * out[hit] + fuellung * col[hit]
    edge = cv2.dilate(kb, np.ones((3, 3), np.uint8)) > 0
    out[edge & hit] = col[edge & hit]
    out[edge & ~hit] = (255, 255, 255)
    im = Image.fromarray(out.astype(np.uint8))
    if punkte:
        d = ImageDraw.Draw(im)
        for (u, v), name in punkte:
            d.ellipse((u - 6, v - 6, u + 6, v + 6), outline=(255, 255, 0), width=3)
            d.text((u + 8, v - 8), name, fill=(255, 255, 0))
    if pfad:
        im.save(pfad, quality=88)
    return im


if __name__ == "__main__":
    if len(sys.argv) >= 5 and sys.argv[1] == "ueberlagerung":
        from PIL import Image
        im = Image.open(sys.argv[2])
        d = json.load(open(sys.argv[3]))
        k = Kamera.aus_dict(d, *im.size)
        ueberlagerung(im, k, None, sys.argv[4])
        print("->", sys.argv[4])
    else:
        print(__doc__)
