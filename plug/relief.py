#!/usr/bin/env python3
"""Fassadenrelief am Ostgiebel des Paulinums (1:1300): die Farbzonen aus `data/fassaden/01_paulinum.json` (Seite O) zusätzlich als flache
Geometrie, damit man sie auch beim einfarbigen Druck sieht.

Betroffen sind die Zonen Spitzbogen-Blende (weißer Kalkstein), Maßwerkfenster, Rosette (weißer Ring) und Rosette (Maßwerk/Glas); Grundfläche
ist der Ostgiebel (Naturstein) = Ebene des Giebels. Jede Zone bekommt einen Pegel in mm gegen diese Ebene (+ nach außen, − nach innen), die
Zonenformen sind dieselben wie die der Farbzonen (`fassaden.expand_zones`: Spitzbogen gleichseitig, Kreis), nur glatt statt in Streifen.

Verfahren (wirkt auf das fertige Hohlgebäude, nicht auf den massiven Körper, damit `plug/buildings.py` `gebaeude()` unberührt bleibt):
  1. Giebelebene aus den größten Ost-Wandflächen des massiven Körpers (Normale, Abstand, Fläche des Giebels).
  2. Je 0,2-mm-Lage (Schnitt in der Lagenmitte, wie der Slicer) den Zielpegel entlang der Wand abtasten (Raster 0,01 mm) und mit der
     45°-Regel begrenzen: die Oberfläche darf von Lage zu Lage höchstens um `DW` (0,2 mm) nach außen wandern, sonst entsteht ein Überhang
     (Unterkante eines Vorsprungs, Decke eines Einzugs werden so zu 45°-Rampen). Nach innen wandern darf sie beliebig.
  3. Vorsprünge (Pegel > 0) werden als Quader je Lage und Lauf an die Außenwand gesetzt, Einzüge (Pegel < 0) ausgeschnitten.
  4. Hinter jedem Einzug bekommt der Hohlraum eine Delle (Rückwand), damit die Wand zwischen Einzug und Hohlraum mindestens `WAND` (0,8 mm)
     bleibt, auch an den Kanten (Filter über ± WAND entlang und ± WAND/`LAYER` Lagen); die Delle wird nach unten mit 45° ausgezogen
     (keine Brücke im Hohlraum).
Vorsprünge nach außen verdicken die Wand nur, brauchen also keine Delle.

Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m plug.relief [A04 B04 …] [--out stl/steckmodul_relief]     # baut das Paulinum einmal, setzt jede Variante, prüft, schreibt STL + Bilder
    python3 -m plug.buildings --relief A04 01_paulinum --out <ordner>    # derselbe Schalter in der Hauptkette (Standard aus)
Varianten: `VARIANTEN` unten (Pegel je Zone in mm).
"""
import json
import os
import sys

import manifold3d as m3d
import numpy as np
import shapely
from shapely import affinity
from shapely.geometry import Point, Polygon, box as sbox
from shapely.ops import unary_union
from scipy import ndimage

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import fassaden  # noqa: E402
import generate as G  # noqa: E402
import hohl  # noqa: E402

SLUG = "01_paulinum"
LAYER = 0.2          # mm Schichthöhe (die Lagen des Druckers liegen auf Vielfachen von 0,2 ab Plattenoberseite z = 0, Bett bei -14,2)
DW = 0.2             # mm Überhang je Lage, den die Oberfläche nach außen wandern darf (die Prüfung in plug/buildings.py erlaubt 0,25)
WAND = hohl.WAND     # 0,8 mm Mindestwand zwischen Außenfläche und Hohlraum
GRID = 0.01          # mm Raster entlang der Wand
RAND_GIEBEL = 0.15   # mm Abstand des Reliefs vom Rand der Giebelfläche (Dachkante): dort sitzt der Vorsprung nicht mehr auf der Wand
EINBETT = 0.2        # mm, so tief reichen Vorsprünge und Rückwände in die Wand hinein (die Wand ist 0,8 dick)
Z_START = 0.2        # mm über der Plattenoberseite: darunter kein Relief (die erste Lage bleibt glatt, 0,2 mm Luft über dem Rand der Mulde samt Einführfase)

# Zonen, die ein Relief tragen können: Schlüssel -> Anfang des Zonennamens in data/fassaden/01_paulinum.json (Reihenfolge der Datei = Überschreiben)
ZONEN = {"blende": "Spitzbogen-Blende", "fenster": "Maßwerkfenster", "ring": "Rosette (weißer Ring)", "rosette": "Rosette (Maßwerk/Glas)"}

# Pegel in mm gegen die Giebelebene (Naturstein = 0). Name: A vor, B zurück, C Treppe, D Staffel um die Ebene.
VARIANTEN = {
    "A02": dict(blende=0.2, fenster=0.0, ring=0.2, rosette=0.0),
    "A04": dict(blende=0.4, fenster=0.0, ring=0.4, rosette=0.0),
    "A06": dict(blende=0.6, fenster=0.0, ring=0.6, rosette=0.0),
    "B02": dict(blende=0.0, fenster=-0.2, ring=0.0, rosette=-0.2),
    "B04": dict(blende=0.0, fenster=-0.4, ring=0.0, rosette=-0.4),
    "B06": dict(blende=0.0, fenster=-0.6, ring=0.0, rosette=-0.6),
    "C04": dict(blende=0.4, fenster=0.2, ring=0.4, rosette=0.2),       # Treppe 0,2 + 0,2 nach außen: Stein 0, Glas +0,2, Blende/Ring +0,4
    "D04": dict(blende=0.2, fenster=-0.2, ring=0.2, rosette=-0.2),     # Staffel um die Ebene: Blende/Ring +0,2, Glas -0,2 (0,4 Höhenunterschied)
}


# --------------------------------------------------------------------------
# Giebelebene und Zonenformen
# --------------------------------------------------------------------------
class Ebene:
    """Giebelebene des Paulinums: Normale n (nach außen, waagerecht), Achse t (nach rechts, von außen gesehen), Ursprung P0 (Punkt der Ebene
    in der Mitte der Spitzbogen-Blende, z = 0), Giebelfläche `flaeche` und die Zonen in Wandkoordinaten (u entlang, z Höhe, mm)."""

    def __init__(self, solid, s, spec):
        import trimesh
        tm = G.to_trimesh(solid)
        m = trimesh.Trimesh(tm.vertices / s, tm.faces, process=False)
        self.s = s
        ext = fassaden.side_extent(m, "O")
        ax, t0, t1 = ext
        wand = (fassaden.face_kind(m.face_normals) == 0) & fassaden.side_mask(m.face_normals, "O") & (np.abs(m.face_normals[:, 2]) < 0.02)
        idx = np.nonzero(wand)[0]
        nh = m.face_normals[idx, :2] / np.linalg.norm(m.face_normals[idx, :2], axis=1, keepdims=True)
        cen = m.triangles_center[idx]
        off = (cen[:, :2] * nh).sum(1)
        ang = np.degrees(np.arctan2(nh[:, 1], nh[:, 0]))
        big = idx[np.argmax(m.area_faces[idx])]
        i0 = int(np.argmax(m.area_faces[idx]))
        sel = (np.abs(ang - ang[i0]) < 0.3) & (np.abs(off - off[i0]) < 0.06)
        a = m.area_faces[idx][sel]
        n2 = (nh[sel] * a[:, None]).sum(0)
        n2 /= np.linalg.norm(n2)
        offm = float((off[sel] * a).sum() / a.sum())
        self.n = np.array([n2[0], n2[1], 0.0])
        self.t = np.array([-n2[1], n2[0], 0.0])
        if self.t[1] < 0:
            self.t = -self.t
        self.az = float(np.degrees(np.arctan2(n2[0], n2[1])) % 360)
        # Zonen der Seite O in m (wie fassaden.expand_zones, ohne Streifen)
        zo = {k: next(z for z in spec["zonen"] if z["name"].startswith(v)) for k, v in ZONEN.items()}
        fc = zo["blende"]["bogen"]["entlang"]
        yc = t0 + fc * (t1 - t0)                                   # m, Mitte der Blende (entlang der Achse y)
        x0 = (offm - self.n[1] * yc) / self.n[0]
        self.P0 = np.array([x0 * s, yc * s, 0.0])                  # mm
        self.zonen_roh = zo
        self.ext = (t0, t1)
        self.off_mm = offm * s
        ty = self.t[1]

        def uz(poly_dy_z):
            """Polygon in (Δy m, z m) relativ zur Blendenmitte -> Wandkoordinaten (u mm, z mm)."""
            return shapely.transform(poly_dy_z, lambda p: np.column_stack([p[:, 0] * s / ty, p[:, 1] * s]))

        self.regionen = {}
        for k, z in zo.items():
            dy0 = t0 + (z["bogen"]["entlang"] if "bogen" in z else z["kreis"]["entlang"]) * (t1 - t0) - yc
            if "bogen" in z:
                S, z0, zk = z["bogen"]["breite"], z["bogen"]["z0"], z["bogen"]["kaempfer"]
                spitz = Point(-S / 2, zk).buffer(S, 128).intersection(Point(S / 2, zk).buffer(S, 128)).intersection(sbox(-S, zk, S, zk + S))
                g = unary_union([sbox(-S / 2, z0, S / 2, zk), spitz])
            else:
                g = Point(0, z["kreis"]["z"]).buffer(z["kreis"]["d"] / 2, 128)
            self.regionen[k] = uz(affinity.translate(g, dy0, 0))
        # Giebelfläche (Wandkoordinaten): alle Dreiecke der Ebene
        tris = []
        for i in idx[sel]:
            p = m.triangles[i] * s - self.P0
            q = np.column_stack([p @ self.t, p[:, 2]])
            pg = Polygon(q)
            if pg.area > 1e-6:
                tris.append(pg)
        self.flaeche = unary_union(tris).buffer(1e-4).buffer(-1e-4)

    def lokal_zu_welt(self):
        """3x4-Matrix: (x = w nach außen, y = u entlang, z) -> Welt (mm)."""
        n, t, P = self.n, self.t, self.P0
        return [[n[0], t[0], 0, P[0]], [n[1], t[1], 0, P[1]], [0, 0, 1, 0]]

    def welt_zu_lokal(self, pts):
        """Weltpunkte (…,3) -> (w, u, z) mm."""
        p = np.asarray(pts, float) - self.P0
        return np.stack([p @ self.n, p @ self.t, p[..., 2]], axis=-1)


# --------------------------------------------------------------------------
# Profile je Lage
# --------------------------------------------------------------------------
class Plan:
    """Zielpegel T, begrenzte Oberfläche S und Rückwandtiefe C je Lage j (z = [j·LAYER, (j+1)·LAYER]) und Rasterpunkt u."""

    def __init__(self, E, pegel, rand=RAND_GIEBEL):
        self.E, self.pegel = E, pegel
        zr = [E.regionen[k].bounds for k in pegel if pegel[k] != 0 or True]
        umin = min(b[0] for b in zr) - 1.0
        umax = max(b[2] for b in zr) + 1.0
        zmax = max(b[3] for b in zr)
        self.u = np.arange(np.floor(umin / GRID) * GRID, umax, GRID)
        self.nl = int(np.ceil(zmax / LAYER)) + 1
        self.zmid = (np.arange(self.nl) + 0.5) * LAYER
        fb = E.flaeche.bounds
        gebiet = unary_union([E.flaeche, sbox(fb[0], -5.0, fb[2], 0.0)]).buffer(-rand).intersection(sbox(-1e3, Z_START, 1e3, 1e3))
        T = np.zeros((self.nl, len(self.u)))
        Z = np.zeros((self.nl, len(self.u)), int)             # Nummer der Zone (1 = erste in ZONEN), die den Pegel bestimmt; 0 = keine
        for j, z in enumerate(self.zmid):
            ok = shapely.contains_xy(gebiet, self.u, np.full(len(self.u), z))
            row = np.zeros(len(self.u))
            zid = np.zeros(len(self.u), int)
            for i, k in enumerate(ZONEN, 1):                  # Reihenfolge = Überschreiben
                if k in pegel:
                    inn = shapely.contains_xy(E.regionen[k], self.u, np.full(len(self.u), z))
                    row[inn] = pegel[k]
                    zid[inn] = i
            T[j] = np.where(ok, row, 0.0)
            Z[j] = np.where(ok, zid, 0)
        self.T, self.Z = T, Z
        S = np.zeros_like(T)
        prev = np.zeros(len(self.u))
        for j in range(self.nl):                              # von unten: höchstens DW nach außen je Lage
            S[j] = np.minimum(T[j], prev + DW)
            prev = S[j]
        self.S = S
        # Rückwand hinter Einzügen: Mindestwand auch an den Kanten (Filter), dann von oben nach unten mit 45° auslaufen
        kern = (2 * int(round(WAND / LAYER)) + 1, 2 * int(round(WAND / GRID)) + 1)
        smin = ndimage.minimum_filter(np.minimum(S, 0.0), size=kern, mode="nearest")
        req = np.where(smin < -1e-6, smin - WAND, np.inf)
        C = np.full_like(req, np.inf)
        nxt = np.full(len(self.u), np.inf)
        for j in range(self.nl - 1, -1, -1):
            C[j] = np.minimum(req[j], nxt + DW)
            nxt = C[j]
        self.C = C

    # ---- Körper ----
    def _laeufe(self, j, feld):
        """Zerlegt Lage j in Läufe gleichen Werts und gleicher Zone: [(u0, u1, Wert, Zone)]."""
        v, z = feld[j], self.Z[j]
        cut = np.nonzero((np.abs(np.diff(v)) > 1e-9) | (np.diff(z) != 0))[0] + 1
        st = np.r_[0, cut]
        en = np.r_[cut, len(v)]
        return [(self.u[a] - GRID / 2, self.u[b - 1] + GRID / 2, v[a], int(z[a])) for a, b in zip(st, en)]

    def _schichten(self, feld, bedingung, w0, w1):
        """Eine Lage nach der anderen: Rechtecke (w0(Wert) … w1(Wert)) über die Läufe, für die `bedingung(Wert)` gilt; je Zone getrennt:
        {Zone: [Körper je Lage]} (Zone 0: keine Zone, z. B. die Rückwand)."""
        out = {}
        for j in range(self.nl):
            polys = {}
            for u0, u1, val, zn in self._laeufe(j, feld):
                if bedingung(val):
                    a, b = sorted((w0(val), w1(val)))
                    polys.setdefault(zn, []).append(sbox(a, u0, b, u1))
            z0, z1 = round(j * LAYER, 6), round((j + 1) * LAYER, 6)
            for zn, pl in polys.items():
                out.setdefault(zn, []).append(G.extrude(unary_union(pl).buffer(0), z0, z1))
        return out

    def koerper(self, farb=None):
        """(Vorsprünge, Einzüge, Rückwände) als Manifold in Weltlage (leer = None). farb: {Zonenschlüssel: face_id}: Vorsprünge und Einzüge
        tragen die face_id ihrer Zone (Farbe, siehe plug/colour.py), die Rückwände face_id 0."""
        M = self.E.lokal_zu_welt()
        keys = list(ZONEN)
        res = []
        for gruppen, mit_zone in (
            (self._schichten(self.S, lambda v: v > 0.02, lambda v: -EINBETT, lambda v: v), True),
            (self._schichten(self.S, lambda v: v < -0.02, lambda v: v, lambda v: 0.05), True),
            (self._schichten(self.C, lambda v: np.isfinite(v) and v < -WAND - 0.02, lambda v: v, lambda v: -WAND + EINBETT), False),
        ):
            teile = []
            for zn, lst in gruppen.items():
                man = G.union(lst)
                if farb is not None:
                    man = _mit_id(man, farb.get(keys[zn - 1], 0) if (mit_zone and zn) else 0)
                teile.append(man)
            res.append(G.union(teile).transform(M) if teile else None)
        return res


def _mit_id(man, fid):
    """Manifold mit fester face_id für alle Dreiecke (float32 wie das Netz in plug/buildings.py sauber())."""
    m = man.to_mesh()
    vp = np.array(np.asarray(m.vert_properties)[:, :3], np.float32, order="C")
    tv = np.array(m.tri_verts, np.uint32, order="C")
    return m3d.Manifold(m3d.Mesh(vert_properties=vp, tri_verts=tv, face_id=np.full(len(tv), fid, np.uint32)))


# --------------------------------------------------------------------------
# Anwenden
# --------------------------------------------------------------------------
def anwenden(body, solid, slug, s, variante, farb=None):
    """Relief `variante` (Name aus VARIANTEN oder Pegel-Dict) auf das fertige Hohlgebäude `body` (Manifold, Weltlage). solid: massiver Körper
    (für die Giebelebene). farb: optional {Zonenschlüssel: face_id} – dann tragen die Flächen des Reliefs diese face_id (siehe plug/colour.py).
    Liefert (Manifold, info, Plan); andere Gebäude als das Paulinum bleiben unverändert (info leer)."""
    if slug != SLUG:
        return body, {}, None
    pegel = dict(VARIANTEN[variante]) if isinstance(variante, str) else dict(variante)
    spec = fassaden.load_spec(slug)
    E = Ebene(solid, s, spec)
    P = Plan(E, pegel)
    vor, ein, rueck = P.koerper(farb)
    v0 = body.volume()
    out = body
    if ein is not None:
        out = out - ein
    if vor is not None:
        out = out + vor
    if rueck is not None:
        out = out + rueck
    info = dict(variante=variante if isinstance(variante, str) else "frei", pegel=pegel, giebel_az=round(E.az, 2),
                vorsprung_mm3=round(vor.volume(), 3) if vor is not None else 0.0, einzug_mm3=round(ein.volume(), 3) if ein is not None else 0.0,
                rueckwand_mm3=round(rueck.volume(), 3) if rueck is not None else 0.0, volumen_zuwachs_mm3=round(out.volume() - v0, 3))
    return out, info, P


# --------------------------------------------------------------------------
# Prüfungen am fertigen Körper
# --------------------------------------------------------------------------
def _lokal_netz(body, E):
    """(Dreiecke lokal [n,3,3] mit (w, u, z), Normalen lokal [n,3]) des Körpers in Wandkoordinaten."""
    m = body.to_mesh()
    v = np.asarray(m.vert_properties)[:, :3].astype(float)
    f = np.asarray(m.tri_verts)
    L = E.welt_zu_lokal(v)
    tri = L[f]
    nrm = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    ln = np.linalg.norm(nrm, axis=1)
    nrm = nrm / np.maximum(ln, 1e-12)[:, None]
    if np.linalg.det(np.array([E.n, E.t, [0, 0, 1.0]])) < 0:      # (w, u, z) ist rechtshändig (n × t = +z); nur zur Sicherheit
        nrm = -nrm
    return tri, nrm, ln / 2


def wand_min(body, E, plan, abstand=1.0, schritt=0.04):
    """Kleinster Abstand von der Außenfläche im Bereich des Reliefs zu den Hohlraumflächen dahinter (mm) und seine Stelle (w, u, z).
    Außenfläche: Dreiecke mit Mitte w > -0.7 im Bereich (Zonen + `abstand`); Hohlraum: Dreiecke mit Mitte w < -0.75 in demselben Bereich
    (die Einzüge sind höchstens 0,6 tief, die Wand ist 0,8, so trennt die Schwelle beide sicher). Beide Flächen werden dicht abgetastet
    (Raster `schritt`), der Abstand kommt aus einem KD-Baum, Fehler höchstens etwa `schritt`/2."""
    from scipy.spatial import cKDTree
    tri, nrm, area = _lokal_netz(body, E)
    cen = tri.mean(1)
    gebiet = unary_union([E.regionen[k] for k in plan.pegel]).buffer(abstand)
    ok = shapely.contains_xy(gebiet, cen[:, 1], cen[:, 2])
    out = ok & (cen[:, 0] > -0.7) & (cen[:, 0] < 1.5)
    cav = ok & (cen[:, 0] < -0.75) & (cen[:, 0] > -4.0)

    def probe(sel):
        t = tri[sel]
        a = area[sel]
        n = np.maximum(1, np.ceil(a / schritt ** 2 * 1.5).astype(int))
        idx = np.repeat(np.arange(len(t)), n)
        r1, r2 = np.random.default_rng(1).random((2, len(idx)))
        flip = r1 + r2 > 1
        r1, r2 = np.where(flip, 1 - r1, r1), np.where(flip, 1 - r2, r2)
        P = t[idx, 0] + r1[:, None] * (t[idx, 1] - t[idx, 0]) + r2[:, None] * (t[idx, 2] - t[idx, 0])
        return np.vstack([P, t.reshape(-1, 3)])

    A, Bc = probe(out), probe(cav)
    keep = shapely.contains_xy(unary_union([E.regionen[k] for k in plan.pegel]).buffer(0.3), A[:, 1], A[:, 2])   # nur unter dem Relief selbst
    A = A[keep]
    d, i = cKDTree(Bc).query(A)
    j = int(np.argmin(d))
    return float(d[j]), [round(float(x), 2) for x in A[j]]


def profil_koerper(body, E, u, zmids):
    """Außenfläche je Lage an den Stellen `u` aus den Schnitten des fertigen Körpers: Feld [Lagen, len(u)] mit dem größten w der Schnittfläche
    in Wandkoordinaten (nan = kein Material). Zeigt, was der Slicer pro Lage sieht."""
    out = np.full((len(zmids), len(u)), np.nan)
    for j, z in enumerate(zmids):
        poly = hohl._cs_poly(body.slice(z))
        if poly.is_empty:
            continue
        xy = shapely.transform(poly, lambda p: np.column_stack([(p - E.P0[:2]) @ E.n[:2], (p - E.P0[:2]) @ E.t[:2]]))   # (w, u)
        for k, uu in enumerate(u):
            seg = shapely.LineString([(-3.0, uu), (3.0, uu)]).intersection(xy)
            if not seg.is_empty:
                out[j, k] = seg.bounds[2]
    return out


def hoehenfeld(body, E, plan, px_mm=36, rand=1.0):
    """Höhenfeld der Giebelwand von außen (Parallelprojektion, Z-Puffer des Körpers mit preview.rasterize): (h [mm, w nach außen], px_mm)."""
    import preview
    tri, nrm, _ = _lokal_netz(body, E)
    b = unary_union([E.regionen[k] for k in ZONEN]).buffer(rand).bounds
    u0, u1, z0, z1 = b[0], b[2], max(b[1], 0.0), b[3]
    W, H = int((u1 - u0) * px_mm), int((z1 - z0) * px_mm)
    px = (tri[:, :, 1] - u0) * px_mm
    py = (z1 - tri[:, :, 2]) * px_mm
    ids = np.nonzero(nrm[:, 0] > -1e-9)[0]
    zb, fid = preview.rasterize(px, py, tri[:, :, 0], ids, W, H)
    h = np.where(fid >= 0, zb, np.nan)
    return np.where(np.isnan(h), np.nanmin(h), h), px_mm


def beleuchten(h, px_mm, az, el):
    """Graustufenbild eines Höhenfelds bei Licht (az: Richtung in der Wandebene gegen +u, 0 = von rechts, 90 = von oben, 180 = von links;
    el: Höhe über der Wandebene, 90 = senkrecht davor). Flächen nach Lambert (Rampen aus dem geglätteten Feld), Schatten durch Verfolgen des
    Lichtstrahls im Höhenfeld (bis 4 mm weit). Ambient 0,28."""
    H, W = h.shape
    hs = ndimage.gaussian_filter(h, 0.8)
    gy, gx = np.gradient(hs, 1 / px_mm)                           # gy = dh/d(Zeile) = -dh/dz, gx = dh/du (je mm)
    nu, nz, nw = -gx, gy, np.ones_like(hs)                        # Normale des Höhenfelds w = h(u, z): (1, -dh/du, -dh/dz)
    nl = np.sqrt(nu ** 2 + nz ** 2 + nw ** 2)
    nu, nz, nw = nu / nl, nz / nl, nw / nl
    a, e = np.radians(az), np.radians(el)
    lw, lu, lz = np.sin(e), np.cos(e) * np.cos(a), np.cos(e) * np.sin(a)
    lam = np.clip(nw * lw + nu * lu + nz * lz, 0, 1)
    shadow = np.zeros_like(h, bool)
    ln = np.hypot(lu, lz)
    if ln > 1e-6:
        step = np.array([lu, -lz]) / ln                           # Pixelrichtung zum Licht (Zeilen laufen nach unten)
        yy, xx = np.mgrid[0:H, 0:W]
        for k in range(1, int(4.0 * px_mm)):
            xs = np.clip(np.rint(xx + step[0] * k).astype(int), 0, W - 1)
            ys = np.clip(np.rint(yy + step[1] * k).astype(int), 0, H - 1)
            shadow |= h[ys, xs] > h + (k / px_mm) * np.tan(e) + 0.01      # der Strahl steigt je mm in der Wandebene um tan(Höhe)
    shade = 0.28 + 0.72 * lam * (~shadow)
    return (np.clip(shade, 0, 1) * 235 + 10).astype(np.uint8)


def _kachel(img, text):
    import preview
    from PIL import Image, ImageDraw
    im = Image.fromarray(img).convert("RGB")
    ImageDraw.Draw(im).text((6, 4), text, fill=(200, 40, 40), font=preview.font(15))
    return im


def _zeile(tiles, gap=8):
    from PIL import Image
    out = Image.new("RGB", (sum(t.width for t in tiles) + gap * (len(tiles) - 1), max(t.height for t in tiles)), (250, 250, 250))
    x = 0
    for t in tiles:
        out.paste(t, (x, 0))
        x += t.width + gap
    return out


def streiflicht(body, E, plan, licht, pfad, px_mm=36, titel=None):
    """Bild der Giebelwand von außen bei `licht` = [(Name, Azimut°, Höhe°)], nebeneinander (siehe beleuchten)."""
    import preview
    h, _ = hoehenfeld(body, E, plan, px_mm)
    out = _zeile([_kachel(beleuchten(h, px_mm, az, el), "%s (%d°/%d°)" % (n, az, el)) for n, az, el in licht])
    if titel:
        out = preview.caption(out, titel)
    out.save(pfad, optimize=True)


def vergleich_licht(koerper, E, plan, licht, pfad, px_mm=26, titel=None):
    """Alle Körper (Liste (Name, Manifold)) nebeneinander bei einem Licht `licht` = (Name, Azimut°, Höhe°) – dieselbe Wand, derselbe Ausschnitt."""
    import preview
    n, az, el = licht
    tiles = [_kachel(beleuchten(hoehenfeld(b, E, plan, px_mm)[0], px_mm, az, el), name) for name, b in koerper]
    out = _zeile(tiles)
    out = preview.caption(out, titel or "Ostgiebel, Licht: %s (%d°/%d°)" % (n, az, el))
    out.save(pfad, optimize=True)


def stufen_tabelle(prof, zmids, tol=0.01):
    """Zusammenfassung eines Profils (w je Lage) zu [(z_von, z_bis, w)] mit gleichem w (Stufenfolge, wie sie der Slicer druckt)."""
    out = []
    for j, w in enumerate(prof):
        z0, z1 = round(zmids[j] - LAYER / 2, 2), round(zmids[j] + LAYER / 2, 2)
        if out and (abs(out[-1][2] - w) < tol or (np.isnan(w) and np.isnan(out[-1][2]))):
            out[-1] = (out[-1][0], z1, out[-1][2])
        else:
            out.append((z0, z1, float(w)))
    return out


def schicht_statistik(plan):
    """Was das Relief je Lage zu einer druckbaren Kontur macht (aus dem Plan, Läufe entlang der Wand): Anzahl der Läufe (zusammenhängende
    Streifen mit Vorsprung oder Einzug in einer Lage), ihre Breiten (0,4 = Düse, 0,8 = zwei Linien) und die Stufen: Sprünge des
    Pegels entlang der Wand (senkrechte Kanten) und von Lage zu Lage (45°-Rampen sind 0,2)."""
    S = plan.S
    lauf = dict(vor=[], ein=[])
    for j in range(plan.nl):
        sg = (S[j] > 0.02).astype(int) - (S[j] < -0.02).astype(int)           # zusammenhängende Streifen gleichen Vorzeichens, unabhängig von der Höhe
        cut = np.nonzero(np.diff(sg) != 0)[0] + 1
        for a, b in zip(np.r_[0, cut], np.r_[cut, len(sg)]):
            if sg[a] != 0:
                lauf["vor" if sg[a] > 0 else "ein"].append((b - a) * GRID)
    out = dict(lagen=int(((np.abs(S) > 0.02).any(axis=1)).sum()), lagen_gesamt=plan.nl)
    for k, b in lauf.items():
        b = np.array(b) if b else np.zeros(0)
        out[k] = dict(laeufe=int(len(b)), schmaler_04=int((b < 0.4).sum()), von_04_bis_08=int(((b >= 0.4) & (b < 0.8)).sum()),
                      ab_08=int((b >= 0.8).sum()), min_breite=round(float(b.min()), 2) if len(b) else None)
    dq = np.abs(np.diff(S, axis=1))
    st = dq[dq > 1e-6]
    out["sprung_entlang_mm"] = {str(v): int((np.abs(st - v) < 0.02).sum()) for v in (0.2, 0.4, 0.6, 0.8)}
    dl = np.abs(np.diff(S, axis=0))
    stl = dl[dl > 1e-6]
    out["sprung_lage_zu_lage_mm"] = {str(v): int((np.abs(stl - v) < 0.02).sum()) for v in (0.2, 0.4, 0.6, 0.8)}
    return out


def druck_verlust(body, basis, E, plan, r=0.2):
    """Was die 0,4-mm-Düse vom Relief nicht zeichnet (Näherung): je Lage der Unterschied zwischen Körper und Basis im Bereich des Reliefs
    (mm², Summe über die Lagen), davon der Teil, der beim Öffnen (Erosion und Dilatation mit r = halbe Düse) verschwindet (Vorsprünge
    schmaler als 0,4) bzw. beim Schließen zuwächst (Einzüge schmaler als 0,4); je abzüglich desselben Verlusts der Basis an denselben Stellen
    (scharfe Ecken). Ergebnis: Relief-Fläche, davon verloren, in Prozent."""
    gebiet = unary_union([E.regionen[k] for k in plan.pegel]).buffer(1.0)
    ub = gebiet.bounds
    ecken = [(-3.0, ub[0]), (3.0, ub[0]), (3.0, ub[2]), (-3.0, ub[2])]
    welt = Polygon([E.P0[:2] + w * E.n[:2] + u * E.t[:2] for w, u in ecken])
    flaeche = verl_o = verl_c = 0.0
    for j in range(plan.nl):
        z = plan.zmid[j]
        a = hohl._cs_poly(body.slice(z)).intersection(welt)
        b = hohl._cs_poly(basis.slice(z)).intersection(welt)
        d = a.symmetric_difference(b)
        if d.is_empty:
            continue
        flaeche += d.area
        oa, ob = a.buffer(-r).buffer(r), b.buffer(-r).buffer(r)
        ca, cb = a.buffer(r).buffer(-r), b.buffer(r).buffer(-r)
        verl_o += max(0.0, a.difference(oa).area - b.difference(ob).area)
        verl_c += max(0.0, ca.difference(a).area - cb.difference(b).area)
    return dict(relief_mm2_summe_ueber_lagen=round(flaeche, 1), geht_verloren_oeffnen_mm2=round(verl_o, 2), geht_verloren_schliessen_mm2=round(verl_c, 2),
                prozent=round(100 * (verl_o + verl_c) / max(flaeche, 1e-9), 1))


# --------------------------------------------------------------------------
# Schalter für plug/buildings.py und plug/colour.py
# --------------------------------------------------------------------------
def farb_ids(slug, solid_farben, keys):
    """face_id je Zonenschlüssel für plug/colour.py: Nummer der Zonenfarbe in `keys` (Hex-Farben des gefärbten Körpers) + 1."""
    spec = fassaden.load_spec(slug)
    out = {}
    for k, v in ZONEN.items():
        z = next(z for z in spec["zonen"] if z["name"].startswith(v))
        rgb = solid_farben["farben"][z["farbe"]]["rgb"]
        hit = np.nonzero(np.asarray(keys).astype(str) == rgb)[0]
        out[k] = int(hit[0]) + 1 if len(hit) else 0
    return out


def farben_fein(farben_slug, n=16):
    """Kopie der Farbzonen eines Gebäudes (Eintrag aus data/farben.json) mit feinerer Annäherung der Bogen- und Kreiszonen (n Streifen statt 5 bis 7; 16 ist der Kompromiss: 48 braucht mehr als 8 GB und Minuten),
    damit die Farbgrenzen des gefärbten massiven Körpers näher an den glatten Reliefkanten liegen."""
    out = dict(farben_slug)
    out["zonen"] = [dict(z, stufen=n) if any(z["name"].startswith(v) for v in ZONEN.values()) else z for z in farben_slug["zonen"]]
    return out


def aus_schalter(slug, body, solid, s, variante):
    """Aufruf aus plug/buildings.py `build()`: Relief setzen, wenn `variante` gesetzt ist (Standard None = unverändert). Liefert (body, info)."""
    if not variante:
        return body, {}
    import plug.buildings as B
    body2, info, _ = anwenden(body, solid, slug, s, variante)
    if info:
        body2, _ = B.sauber(body2)
    return body2, info


# --------------------------------------------------------------------------
# Läufe: Varianten bauen, prüfen, Bilder
# --------------------------------------------------------------------------
OUT = os.path.join(HERE, "stl", "steckmodul_relief")
PREV = os.path.join(HERE, "vorschau", "steckmodul_relief")
LICHTER = [("Lampe oben vorn", 100, 45), ("Fensterlicht von links", 175, 35), ("streifend von links", 180, 20)]


def baseline(scale=1300):
    """(Hohlgebäude ohne Relief, Kassette, massiver Körper, Info) des Paulinums wie `plug.buildings.build` (Rohrstütze nach dem eingecheckten JSON)."""
    from plug import buildings as B, campus as C
    from plug.testcase import params as P
    s = 1000.0 / scale
    models = C.models_plan(s, scale)
    places = json.load(open(C.CACHE % scale))
    solid, fp, _ = models[SLUG]
    try:
        r = json.load(open(os.path.join(B.OUT, "%s_1zu%d.json" % (SLUG, scale))))["rohrstuetze"]
    except (OSError, KeyError):
        r = False
    body, kas, info = B.gebaeude(SLUG, solid, fp, places[SLUG], s, r)
    body, _ = B.sauber(body)
    return body, kas, solid, info, s


def kontrolle(name, body, basis, kas, E, plan, info_rel):
    """Alle Prüfwerte einer Variante (siehe Aufgabe: dicht, Kollision, Überhang, Wand, Lagen)."""
    from plug import buildings as B
    from plug.geom import to_tm
    tm = to_tm(body)
    ub = B.ueberhang(basis)
    ur = B.ueberhang(body)
    neu = [x for x in ur["stellen"] if x not in ub["stellen"]]
    wm, wo = wand_min(body, E, plan)
    wm0, _ = wand_min(basis, E, plan)
    res = dict(variante=name, pegel=plan.pegel, dicht=bool(tm.is_watertight), manifold=str(body.status()), volumen_cm3=round(body.volume() / 1000, 3),
               volumen_zuwachs_mm3=round(body.volume() - basis.volume(), 2), kollision_kassette_mm3=round((body ^ kas).volume(), 3),
               wand_min_mm=round(wm, 3), wand_min_stelle_w_u_z=wo, wand_min_ohne_relief_mm=round(wm0, 3),
               ueberhang=dict(bruecke_mm2=ur["bruecke_mm2"], krag_mm2=ur["krag_mm2"], bruecke_mm=ur["bruecke_mm"], krag_mm=ur["krag_mm"],
                              neue_stellen_ueber_1mm=neu, basis=dict(bruecke_mm2=ub["bruecke_mm2"], krag_mm2=ub["krag_mm2"])),
               statistik=schicht_statistik(plan), druck_verlust=druck_verlust(body, basis, E, plan), bauteil=info_rel)
    return res, tm


def profil_pruefung(body, plan, spalten_u=(0.0,), zmax=None):
    """Plan gegen fertigen Körper: (größte Abweichung des Außenprofils von der Planoberfläche in mm, Stufentabellen je Spalte)."""
    ui = [int(np.argmin(np.abs(plan.u - u))) for u in spalten_u]
    prof = profil_koerper(body, plan.E, plan.u[ui], plan.zmid)
    tab, dev = {}, 0.0
    for k, i in enumerate(ui):
        soll = plan.S[:, i]
        base = prof[:, k]
        # Außenfläche der Basis ist w = 0 (Giebelebene); Abweichungen nur dort, wo Material liegt
        ok = ~np.isnan(base) & (plan.zmid < (zmax or 1e9))
        dev = max(dev, float(np.nanmax(np.abs(np.where(ok, base - np.maximum(soll, 0 * soll + soll), 0)))))
        tab[float(spalten_u[k])] = [(z0, z1, round(w, 2)) for z0, z1, w in stufen_tabelle(np.where(ok, base, np.nan), plan.zmid)]
    return round(dev, 3), tab


def ansicht_vergleich(koerper, E, plan, pfad, azim=-12, elev=8, ppm=26, titel=None):
    """Vergleichsbild des normalen Renderers (preview.render, Licht von der Kamera): ein Ausschnitt je Körper (Liste (Name, Trimesh)), alle gleich geschnitten."""
    import preview
    from PIL import Image
    b = unary_union([E.regionen[k] for k in plan.pegel]).buffer(1.2).bounds
    M = np.array(E.lokal_zu_welt())
    tiles = []
    for name, tm in koerper:
        im, proj = preview.render([(tm, preview.rgb("#8f9aa8"))], azim=azim, elev=elev, px_per_mm=ppm, light_from_view=True, return_proj=True)
        pts = [M @ np.array([w, u, z, 1.0]) for w, u in ((0, b[0]), (0.4, b[2])) for z in (0.0, b[3])]
        xy = np.array([proj(p) for p in pts]).T
        box = (int(xy[0].min()) - 4, int(xy[1].min()) - 4, int(xy[0].max()) + 4, int(xy[1].max()) + 4)
        tile = im.crop(box)
        d = __import__("PIL.ImageDraw", fromlist=["ImageDraw"]).Draw(tile)
        d.text((6, 4), name, fill=(200, 40, 40), font=preview.font(16))
        tiles.append(tile)
    h = max(t.height for t in tiles)
    out = Image.new("RGB", (sum(t.width for t in tiles) + 8 * (len(tiles) - 1), h), (250, 250, 250))
    x = 0
    for t in tiles:
        out.paste(t, (x, 0))
        x += t.width + 8
    if titel:
        out = preview.caption(out, titel)
    out.save(pfad, optimize=True)


def main():
    import argparse
    global OUT, PREV
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("varianten", nargs="*", help="Namen aus VARIANTEN (Standard: alle)")
    ap.add_argument("--out", default=OUT, help="Ausgabeordner STL/JSON")
    ap.add_argument("--prev", default=PREV, help="Ausgabeordner Bilder")
    ap.add_argument("--keine-bilder", action="store_true")
    a = ap.parse_args()
    OUT, PREV = a.out, a.prev
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(PREV, exist_ok=True)
    namen = a.varianten or list(VARIANTEN)
    from plug.geom import to_tm
    print("Basis (ohne Relief) …", flush=True)
    basis, kas, solid, binfo, s = baseline()
    tm0 = to_tm(basis)
    tm0.export(os.path.join(OUT, "%s_1zu1300_ohne_relief.stl" % SLUG))
    print("  ohne Relief: %.3f cm³ dicht=%s" % (basis.volume() / 1000, tm0.is_watertight), flush=True)
    alle, koerper, bodies = {}, [("ohne Relief", tm0)], [("ohne Relief", basis)]
    for n in namen:
        body, info, plan = anwenden(basis, solid, SLUG, s, n)
        from plug import buildings as B
        body, _ = B.sauber(body)
        res, tm = kontrolle(n, body, basis, kas, plan.E, plan, info)
        res["abweichung_profil_mm"], tab = profil_pruefung(body, plan, (0.0,))
        res["stufen_mittelspalte"] = tab
        path = os.path.join(OUT, "%s_1zu1300_relief_%s.stl" % (SLUG, n))
        tm.export(path)
        json.dump(res, open(path[:-4] + ".json", "w"), indent=1, ensure_ascii=False, default=str)
        alle[n] = res
        st = res["statistik"]
        print("  %-4s %s dicht=%s Zuwachs %.1f mm³  Wand min %.2f (ohne Relief %.2f)  Kollision %.3f  Überhang Brücke %.2f/Krag %.2f mm² (Basis %.2f/%.2f)  neue Stellen %d  "
              "Läufe vor/ein %d/%d (<0,4: %d/%d)  Verlust %.1f %%" % (
                  n, plan.pegel, res["dicht"], res["volumen_zuwachs_mm3"], res["wand_min_mm"], res["wand_min_ohne_relief_mm"], res["kollision_kassette_mm3"],
                  res["ueberhang"]["bruecke_mm2"], res["ueberhang"]["krag_mm2"], res["ueberhang"]["basis"]["bruecke_mm2"], res["ueberhang"]["basis"]["krag_mm2"],
                  len(res["ueberhang"]["neue_stellen_ueber_1mm"]), st["vor"]["laeufe"], st["ein"]["laeufe"], st["vor"]["schmaler_04"], st["ein"]["schmaler_04"],
                  res["druck_verlust"]["prozent"]), flush=True)
        koerper.append((n, tm))
        bodies.append((n, body))
        if not a.keine_bilder:
            streiflicht(body, plan.E, plan, LICHTER, os.path.join(PREV, "%s_streiflicht.png" % n), titel="Paulinum Ostgiebel, Relief %s: %s" % (n, ", ".join("%s %+.1f" % kv for kv in plan.pegel.items())))
    json.dump(alle, open(os.path.join(OUT, "pruefung.json"), "w"), indent=1, ensure_ascii=False, default=str)
    if not a.keine_bilder:
        E = plan.E
        for L, f in zip(LICHTER, ("lampe", "fenster", "streifend")):
            vergleich_licht(bodies, E, plan, L, os.path.join(PREV, "vergleich_licht_%s.png" % f))
        ansicht_vergleich(koerper, E, plan, os.path.join(PREV, "vergleich_giebel_schraeg.png"), azim=25, elev=14, titel="Ostgiebel schräg von Nordosten (Renderer des Repos, Licht von der Kamera)")
    print("fertig:", os.path.relpath(OUT, HERE))


if __name__ == "__main__":
    main()
