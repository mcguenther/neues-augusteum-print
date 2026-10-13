#!/usr/bin/env python3
"""Fassadenfarben aus vielen Fotos: Projektion des Modells ins Foto, Zellstatistik, Konsens.

Statt Messfelder von Hand zu setzen, wird das 3D-Modell in jedes registrierte Foto
projiziert (kamera.py). Jedes Bildpixel gehört dann zu einer bekannten Wandfläche
(Gebäude, Himmelsrichtung, Position entlang der Fassade, Höhe) – dieselben Koordinaten,
in denen data/fassaden/<slug>.json die Zonen beschreibt. Je Foto und Zelle (1 m × 1 m)
entsteht eine Statistik (Pixelzahl, Mittel und Median im linearen RGB, besonnt ja/nein),
über alle Fotos ein Konsens, aus dem Zonen und Farben abgeleitet werden.

Schritte
  messe_foto      Tiefenpuffer des Modells im Foto, Pixel -> Zellen, Schattenwurf der Sonne
  bodenabgleich   Belichtung/Weißabgleich je Foto am Platzbelag, dessen Farbe das Luftbild
                  2024 von oben zeigt (ersetzt die frühere Annahme „Pflaster = Grau 150“)
  konsens         je Zelle gewichteter Median über Fotos, besonnte Aufnahmen bevorzugt
"""
import json
import os

import cv2
import numpy as np

import fassaden
import generate as G
import kamera as K
import szene

CACHE = os.path.join(G.HERE, "data", "cache", "messung")
ROOF_NZ = fassaden.ROOF_NZ
SEITEN = ("N", "O", "S", "W")          # 90°-Keile um die Himmelsrichtungen, wie fassaden.side_mask
ZELLE = 1.0                            # m Kantenlänge der Messzellen (entlang, Höhe)
MIN_COS = 0.30                         # Wände unter flacherem Winkel (cos) zur Blickrichtung zählen nicht
RAND = 3                               # Pixel Randabstand zu Kanten der Modellflächen


# --------------------------------------------------------------------------
# Farbräume
# --------------------------------------------------------------------------
def lin(c):
    """sRGB 0..1 -> linear."""
    c = np.asarray(c, float)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def srgb(c):
    """linear -> sRGB 0..1."""
    c = np.clip(np.asarray(c, float), 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)


def hexrgb(lin_rgb):
    v = np.round(srgb(lin_rgb) * 255).astype(int)
    return "#%02x%02x%02x" % tuple(np.clip(v, 0, 255))


def lum(l):
    """Helligkeit (linear) aus linearem RGB (..., 3)."""
    return np.asarray(l) @ np.array([0.2126, 0.7152, 0.0722])


# --------------------------------------------------------------------------
# Szene
# --------------------------------------------------------------------------
class Szene:
    """Laserscan-Gebäudenetze als ein Netz mit Gebäude- und Seitennummer je Dreieck, Fassadenachsen."""

    def __init__(self, quelle="laserscan"):
        self.mesh, self.bid, self.slugs = szene.gesamt(None, quelle)
        self.tris, self.nrm = self.mesh.triangles, self.mesh.face_normals
        self.wand = np.abs(self.nrm[:, 2]) < ROOF_NZ
        az = fassaden.azimuth(self.nrm)
        self.seite = (((az + 45) % 360) // 90).astype(int)          # 0 N, 1 O, 2 S, 3 W
        self.dz = np.array([szene.laden(quelle)[s][1] for s in self.slugs])
        self.ext = {}                                                # (b, seite) -> (ax[2], t0, t1)
        for b, slug in enumerate(self.slugs):
            m = szene.laden(quelle)[slug][0]
            for si, name in enumerate(SEITEN):
                e = fassaden.side_extent(m, name)
                if e is not None:
                    self.ext[(b, si)] = e

    def zelle(self, b, si, pts):
        """Weltpunkte -> (t Meter ab linkem Ende, z Meter über Gebäudeboden)."""
        ax, t0, t1 = self.ext[(b, si)]
        return pts[:, :2] @ ax - t0, pts[:, 2] - self.dz[b]


# --------------------------------------------------------------------------
# Sonne und Schatten
# --------------------------------------------------------------------------
class Schatten:
    """Schattenkarte (Tiefenpuffer von der Sonne aus) für beliebige Punkte der Szene."""

    def __init__(self, sc, sonne_vec, res=0.5):
        import preview as P
        s = np.asarray(sonne_vec, float)
        r = np.cross(s, [0, 0, 1.0])
        r /= np.linalg.norm(r)
        u = np.cross(r, s)
        self.s, self.r, self.u, self.res = s, r, u, res
        t = sc.tris.reshape(-1, 3)
        pr, pu, pd = t @ r, t @ u, t @ s
        self.r0, self.u0 = pr.min() - 1, pu.max() + 1
        W = int((pr.max() - self.r0) / res) + 3
        H = int((self.u0 - pu.min()) / res) + 3
        px = ((pr - self.r0) / res).reshape(-1, 3)
        py = ((self.u0 - pu) / res).reshape(-1, 3)
        ids = np.nonzero(sc.nrm @ s > -0.05)[0]       # nur der Sonne zugewandte Flächen werfen den Rand
        zbuf, _ = P.rasterize(px, py, pd.reshape(-1, 3), ids, W, H)
        self.zbuf, self.W, self.H = zbuf, W, H

    def besonnt(self, pts, normalen=None, bias=0.6):
        pts = np.asarray(pts, float)
        x = np.clip(((pts @ self.r - self.r0) / self.res).astype(int), 0, self.W - 1)
        y = np.clip(((self.u0 - pts @ self.u) / self.res).astype(int), 0, self.H - 1)
        d = pts @ self.s
        lit = d >= self.zbuf[y, x] - bias
        if normalen is not None:
            lit &= (normalen @ self.s) > 0.05
        return lit


# --------------------------------------------------------------------------
# Messung je Foto
# --------------------------------------------------------------------------
def gruen(srgb255):
    """Laub/Vegetation (auch dunkles, schattiges): grünlicher Farbton, oder grünlich und stark texturiert.
    Pixel (..., 3) in 0..255 (H, W, 3)."""
    a = srgb255.astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx, mn = a.max(-1), a.min(-1)
    sat = (mx - mn) / np.maximum(mx, 1)
    klar = (g > r * 1.06) & (g > b * 1.10) & (sat > 0.18)
    leicht = (g > r * 0.97) & (g > b * 1.06) & (sat > 0.10)
    y = a @ np.array([0.299, 0.587, 0.114], np.float32)
    m1 = cv2.blur(y, (5, 5))
    var = cv2.blur(y * y, (5, 5)) - m1 * m1                 # lokale Varianz der Helligkeit
    laub = klar | (leicht & (var > 90.0))
    return cv2.dilate(laub.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0


def rand_maske(lab, tiefe, r=RAND):
    """True = Pixel liegt weiter als r Pixel von Rändern (Flächenwechsel, Lücken, Tiefensprünge)."""
    H, W = lab.shape
    d = np.zeros((H, W), bool)
    d[:, 1:] |= lab[:, 1:] != lab[:, :-1]
    d[:, :-1] |= lab[:, 1:] != lab[:, :-1]
    d[1:, :] |= lab[1:, :] != lab[:-1, :]
    d[:-1, :] |= lab[1:, :] != lab[:-1, :]
    t = np.nan_to_num(tiefe, nan=0.0)
    jump = np.zeros((H, W), bool)
    for ax in (0, 1):
        dd = np.abs(np.diff(t, axis=ax))
        lim = 0.6 + 0.03 * np.maximum(np.take(t, range(1, t.shape[ax]), axis=ax), 1)
        j = dd > lim
        if ax == 0:
            jump[1:, :] |= j
            jump[:-1, :] |= j
        else:
            jump[:, 1:] |= j
            jump[:, :-1] |= j
    bad = (d | jump | (lab < 0)).astype(np.uint8)
    bad = cv2.dilate(bad, np.ones((2 * r + 1, 2 * r + 1), np.uint8))
    return bad == 0


def rendern(kam, sc, scale=0.5):
    """Tiefenpuffer des Modells im Foto: (fid, tiefe) im Maßstab `scale` des Originalbilds."""
    return kam.exakt(sc.tris, sc.nrm, scale)


def messe_foto(img, kam, sc, sun=None, render=None, scale=0.5, himmel=None):
    """Zellstatistik eines Fotos.

    img    PIL-Bild, kam Kamera (Originalgröße), sc Szene, sun Einheitsvektor zur Sonne (oder None)
    render Ergebnis von rendern() (sonst wird neu gerendert), himmel Himmelsmaske (True = Himmel)
    Gibt dict mit je einem Eintrag pro Zelle zurück: b, s, ti, zi, n (Pixel), mean/med (lineares RGB),
    pos (3D-Mittelpunkt), nrm (mittlere Normale), cos (Blickwinkel), lit (besonnt).
    """
    fid, tiefe = render if render is not None else rendern(kam, sc, scale)
    H, W = fid.shape
    a = cv2.resize(np.asarray(img.convert("RGB")), (W, H), interpolation=cv2.INTER_AREA)
    hit = fid >= 0
    f = np.where(hit, fid, 0)
    wall = hit & sc.wand[f]
    b = np.where(hit, sc.bid[f], -1)
    si = np.where(hit, sc.seite[f], -1)
    lab = np.where(wall, b * 4 + si, -1)
    pts = kam.punkte(tiefe, scale)
    zum = kam.pos - pts
    zum /= np.maximum(np.linalg.norm(zum, axis=-1, keepdims=True), 1e-6)
    cosv = np.einsum("hwc,hwc->hw", sc.nrm[f], zum)
    fremd = gruen(a)
    if himmel is not None:      # Himmel, der durch ungenaue Pose auf Modellflächen fällt, samt Rand
        hm = cv2.resize(himmel.astype(np.uint8), (W, H), interpolation=cv2.INTER_NEAREST)
        fremd |= cv2.dilate(hm, np.ones((9, 9), np.uint8)) > 0
    ok = wall & (cosv > MIN_COS) & rand_maske(lab, tiefe) & ~fremd
    ys, xs = np.nonzero(ok)
    if not len(ys):
        return None
    p = pts[ys, xs]
    fi = f[ys, xs]
    bb, ss = b[ys, xs], si[ys, xs]
    t = np.zeros(len(ys))
    z = np.zeros(len(ys))
    for key in np.unique(bb * 4 + ss):
        m = (bb * 4 + ss) == key
        if (int(key // 4), int(key % 4)) not in sc.ext:
            continue
        t[m], z[m] = sc.zelle(int(key // 4), int(key % 4), p[m])
    ti, zi = np.floor(t / ZELLE).astype(int), np.floor(z / ZELLE).astype(int)
    keep = (ti >= 0) & (zi >= 0) & (ti < 1024) & (zi < 1024)
    ys, xs, p, fi, bb, ss, ti, zi = ys[keep], xs[keep], p[keep], fi[keep], bb[keep], ss[keep], ti[keep], zi[keep]
    col = lin(a[ys, xs] / 255.0)
    cv_ = cosv[ys, xs]
    code = ((bb * 4 + ss).astype(np.int64) * 1024 + ti) * 1024 + zi
    order = np.argsort(code, kind="stable")
    code, col, p, cv_, fi = code[order], col[order], p[order], cv_[order], fi[order]
    cut = np.r_[0, np.nonzero(np.diff(code))[0] + 1, len(code)]
    n = np.diff(cut)
    c0 = code[cut[:-1]]
    out = dict(zi=(c0 % 1024).astype(int), ti=((c0 // 1024) % 1024).astype(int))
    bs = c0 // 1024 // 1024
    out["s"], out["b"], out["n"] = (bs % 4).astype(int), (bs // 4).astype(int), n
    out["mean"] = np.add.reduceat(col, cut[:-1]) / n[:, None]
    out["pos"] = np.add.reduceat(p, cut[:-1]) / n[:, None]
    out["cos"] = np.add.reduceat(cv_, cut[:-1]) / n
    nrm = np.add.reduceat(sc.nrm[fi], cut[:-1])
    out["nrm"] = nrm / np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-9)
    out["med"] = np.array([np.median(col[i0:i1], axis=0) for i0, i1 in zip(cut[:-1], cut[1:])])
    if sun is not None:
        out["lit"] = Schatten(sc, sun).besonnt(out["pos"] + 0.3 * out["nrm"], out["nrm"])
    else:
        out["lit"] = np.zeros(len(n), bool)
    return out


# --------------------------------------------------------------------------
# Belichtung am Platzbelag
# --------------------------------------------------------------------------
def bodenabgleich(img, kam, sc, render=None, sun=None, scale=0.5, zg=0.45, maxdist=110.0):
    """Belichtung des Fotos am Platzbelag.

    Jeder Strahl, der kein Gebäude trifft und nach unten geht, trifft den Boden (Ebene z = zg). Dort
    zeigt das Luftbild 2024 die Farbe des Belags von oben (dop_sampler). Verhältnis Luftbild/Foto,
    Median über die besonnten Bodenpixel = Verstärkung je Kanal (linear).
    Gibt dict: gain (3 oder None), n (Pixel), mad (relative Streuung), schatten (Verhältnis
    besonnter/beschatteter Belag je Kanal oder None), n_schatten.
    """
    import farben as F
    fid, tiefe = render if render is not None else rendern(kam, sc, scale)
    H, W = fid.shape
    a = cv2.resize(np.asarray(img.convert("RGB")), (W, H), interpolation=cv2.INTER_AREA)
    u, v = np.meshgrid((np.arange(W) + 0.5) / scale, (np.arange(H) + 0.5) / scale)
    d = kam.strahl(u, v)
    down = d[..., 2] < -0.03
    tt = np.where(down, (zg - kam.pos[2]) / np.minimum(d[..., 2], -1e-6), np.inf)
    gnd = (fid < 0) & down & (tt < maxdist) & ~gruen(a)
    res = dict(gain=None, n=0, mad=None, schatten=None, n_schatten=0)
    if not gnd.any():
        return res
    ys, xs = np.nonzero(gnd)
    p = kam.pos + d[ys, xs] * tt[ys, xs, None]
    col = lin(a[ys, xs] / 255.0)
    ref = lin(F.dop_sampler()(p[:, 0], p[:, 1]))
    keep = (lum(col) > 0.02) & (lum(ref) > 0.02)
    lit = Schatten(sc, sun).besonnt(p + [0, 0, 0.2]) if sun is not None else np.ones(len(p), bool)
    sel = keep & lit
    sel &= lum(ref) >= np.percentile(lum(ref[sel]), 35) if sel.any() else sel   # DOP-Schatten ausblenden
    res["n"] = int(sel.sum())
    if sel.sum() >= 2500:
        # Nur die Helligkeit wird angeglichen (skalare Verstärkung). Der Farbton bleibt der der Kamera: Das
        # Luftbild zeigt den Belag neutraler/kühler als jedes der Fotos, ein Kanalabgleich würde alle Fassaden
        # bläulich färben (Prüfung an Paulinum-Giebel und Uniriese).
        ratio = lum(ref[sel]) / np.maximum(lum(col[sel]), 1e-4)
        g = float(np.median(ratio))
        res["gain"] = np.full(3, g)
        res["gain_kanal"] = np.median(ref[sel] / np.maximum(col[sel], 1e-4), axis=0)
        res["mad"] = float(np.median(np.abs(ratio - g)) / g)
    sh = keep & ~lit
    res["n_schatten"] = int(sh.sum())
    if sh.sum() >= 1500 and (keep & lit).sum() >= 1500:
        res["schatten"] = np.median(col[keep & lit], axis=0) / np.maximum(np.median(col[sh], axis=0), 1e-4)
    return res


# --------------------------------------------------------------------------
# Messung aller Fotos
# --------------------------------------------------------------------------
A_AMB, A_VERT = 0.12, 0.09   # diffuses Himmelslicht relativ zur direkten Normalstrahlung: waagerecht / senkrecht
MIN_SONNE_COS = 0.30         # besonnte Zellen flacher als ~72° Einfallswinkel zählen nicht (Streiflicht)


def bearbeite(fid, e, sc=None, force=False):
    """Misst ein registriertes Foto und speichert die Zellstatistik in data/cache/messung/<fid>.pkl."""
    import pickle
    import registrierung as R
    import skyline
    path = os.path.join(CACHE, fid + ".pkl")
    if os.path.exists(path) and not force:
        return pickle.load(open(path, "rb"))
    img = R.foto_bild(fid, e)
    kam = K.Kamera.aus_dict(e["pose"], *img.size)
    sc = sc or Szene()
    sun, alt = None, None
    if e.get("sonne"):                                  # von Hand: [Azimut, Höhe]
        az, alt = e["sonne"]
        sun = np.array([np.sin(np.radians(az)) * np.cos(np.radians(alt)),
                        np.cos(np.radians(az)) * np.cos(np.radians(alt)), np.sin(np.radians(alt))])
    elif e.get("zeit"):
        az, alt, sun = szene.sonne(szene.zeit_utc(e["zeit"]))
    if alt is not None and alt < 8 or e.get("bedeckt"):
        sun = None
    render = rendern(kam, sc)
    himmel, _ = skyline.himmel_maske(img)
    cells = messe_foto(img, kam, sc, sun, render, himmel=himmel)
    boden = bodenabgleich(img, kam, sc, render, sun)
    res = dict(cells=cells, boden=boden, sun=sun, alt=alt, bedeckt=bool(e.get("bedeckt")))
    os.makedirs(CACHE, exist_ok=True)
    pickle.dump(res, open(path, "wb"))
    return res


E_REF = 0.79        # Einstrahlung bei Normeinfall: cos 45° ≈ 0,7 plus Himmelslicht (Bezug der Farbwerte)


def beobachtungen(ergebnisse, fotos, gain_tab=None):
    """Alle Zellbeobachtungen der Fotos als Arrays.

    Die Farben bleiben „wie fotografiert“ (Belichtung und Farbton der Kamera). Besonnte Wände werden auf
    einen Normeinfall (E_REF) umgerechnet, damit Aufnahmen zu verschiedenen Tageszeiten vergleichbar sind;
    Beobachtungen mit sehr anderer Einstrahlung zählen weniger. Beschattete Zellen bekommen ein kleines
    Gewicht und werden nur genutzt, wo nichts Besonntes vorliegt.

    ergebnisse {fid: Ergebnis von bearbeite}, fotos {fid: Katalogeintrag} (Feld "qualitaet", Standard 1)
    gain_tab   {fid: Verstärkung} relativ zu den anderen Fotos (aus harmonisiere)
    """
    gain_tab = gain_tab or {}
    rows = dict(foto=[], b=[], s=[], ti=[], zi=[], n=[], rgb=[], raw=[], lit=[], w=[], pos=[], nrm=[])
    for fid, r in ergebnisse.items():
        c = r["cells"] if r else None
        if c is None:
            continue
        g = float(np.mean(gain_tab.get(fid, 1.0)))
        sr = r["boden"]["schatten"] if r["boden"]["schatten"] is not None else np.array([5.0, 5.2, 5.6])
        sr = float(np.mean(sr))
        q = float(fotos[fid].get("qualitaet", 1.0))
        if r["sun"] is not None:
            cs = np.clip(c["nrm"] @ r["sun"], 0, None)
        for i in range(len(c["n"])):
            if c["n"][i] < 6:
                continue
            if r["sun"] is None:                                  # bedeckt: nur Himmelslicht, senkrecht ~0,55 von waagerecht
                if not r["bedeckt"]:
                    continue                                       # Aufnahmezeit unbekannt: nicht verwendbar
                lit, f_, w = False, 0.79 / 0.5, 0.6
            elif c["lit"][i] and cs[i] >= MIN_SONNE_COS:
                f_ = float(np.clip(E_REF / (cs[i] + A_VERT), 0.6, 2.0))
                lit, w = True, float(np.exp(-np.log(f_) ** 2 / (2 * 0.35 ** 2)))
            elif not c["lit"][i]:
                lit, f_, w = False, sr * E_REF / (A_VERT + 1e-9) / 6.5, 0.3
            else:
                continue
            raw = c["mean"][i] * f_                                # ohne Verstärkung
            for k, v in (("foto", fid), ("b", c["b"][i]), ("s", c["s"][i]), ("ti", c["ti"][i]), ("zi", c["zi"][i]),
                         ("n", c["n"][i]), ("rgb", raw * g), ("raw", raw), ("lit", lit),
                         ("w", w * q * np.sqrt(min(c["n"][i], 400)) * c["cos"][i] * (0.5 if c["zi"][i] < 8 else 1.0)),
                         ("pos", c["pos"][i]), ("nrm", c["nrm"][i])):
                rows[k].append(v)
    return {k: (np.array(v) if k != "foto" else np.array(v, dtype=object)) for k, v in rows.items()}


def harmonisiere(ergebnisse, fotos, min_zellen=25, runden=4, aktiv=False):
    """Relative Verstärkung je Foto: Aufnahmen sehen dieselben besonnten Zellen unterschiedlich hell
    (Belichtung, Nachbearbeitung). Aus den gemeinsam gesehenen Zellen wird je Foto der Median des
    Helligkeitsverhältnisses zum Konsens der übrigen Fotos bestimmt (iterativ); das geometrische Mittel
    aller Verstärkungen ist 1, die Kamerabelichtung bleibt im Mittel erhalten.
    Gibt ({fid: gain}, {fid: Beschreibung}) zurück."""
    ids = [f for f, r in ergebnisse.items() if r and r["cells"] is not None]
    gain = {f: 1.0 for f in ids}
    how = {f: "nicht verglichen (keine gemeinsamen besonnten Zellen)" for f in ids}
    if not aktiv:
        for f in ids:
            how[f] = "Kamerabelichtung unverändert"
        return {f: np.ones(3) for f in ids}, how
    obs = beobachtungen(ergebnisse, fotos)
    lit = obs["lit"]
    code = ((obs["b"] * 4 + obs["s"]).astype(np.int64) * 1024 + obs["ti"]) * 1024 + obs["zi"]
    for _ in range(runden):
        # Konsens je Zelle ohne das jeweilige Foto: Mittel der Helligkeit (gewichtet) der anderen
        y = lum(obs["raw"]) * np.array([gain[f] for f in obs["foto"]])
        new = {}
        order = np.argsort(code, kind="stable")
        cut = np.r_[0, np.nonzero(np.diff(code[order]))[0] + 1, len(code)]
        ratios = {f: ([], []) for f in ids}
        for i0, i1 in zip(cut[:-1], cut[1:]):
            ix = order[i0:i1]
            ix = ix[lit[ix]]
            fs = obs["foto"][ix]
            if len(set(fs)) < 2:
                continue
            for j in ix:
                other = ix[obs["foto"][ix] != obs["foto"][j]]
                yo = (y[other] * obs["w"][other]).sum() / obs["w"][other].sum()
                if y[j] > 0.01 and yo > 0.01:
                    ratios[obs["foto"][j]][0].append(yo / y[j])
                    ratios[obs["foto"][j]][1].append(obs["w"][j])
        for f in ids:
            r_, w_ = np.array(ratios[f][0]), np.array(ratios[f][1])
            if len(r_) >= min_zellen:
                gain[f] *= float(_wmedian(r_, w_)) ** 0.5        # gedämpft
                how[f] = "Vergleich mit anderen Fotos (%d gemeinsame Zellen)" % len(r_)
        gm = np.exp(np.mean([np.log(gain[f]) for f in ids]))
        gain = {f: min(max(g / gm, 0.55), 1.8) for f, g in gain.items()}   # Belichtungsunterschiede über etwa eine Blende sind verdächtig
    return {f: np.full(3, g) for f, g in gain.items()}, how


def konsens(obs):
    """Je Zelle ein Farbwert aus allen Fotos: besonnte Aufnahmen bevorzugt, gewichteter Mittelwert nach
    Ausreißerausschluss. Gibt dict mit b, s, ti, zi, rgb (linear), n_foto, n_licht, streuung, nur_schatten, pos."""
    if not len(obs["b"]):
        return None
    code = ((obs["b"] * 4 + obs["s"]).astype(np.int64) * 1024 + obs["ti"]) * 1024 + obs["zi"]
    order = np.argsort(code, kind="stable")
    code_s = code[order]
    cut = np.r_[0, np.nonzero(np.diff(code_s))[0] + 1, len(code_s)]
    out = {k: [] for k in ("b", "s", "ti", "zi", "rgb", "n_foto", "n_licht", "streuung", "nur_schatten", "pos", "nrm")}
    for i0, i1 in zip(cut[:-1], cut[1:]):
        ix = order[i0:i1]
        lit = obs["lit"][ix]
        use = ix[lit] if lit.any() else ix
        rgb, w = obs["rgb"][use], obs["w"][use]
        y = lum(rgb)
        m = np.median(y) if len(use) < 3 else _wmedian(y, w)
        ok = (y > 0.9 * m) & (y < 1.8 * m) if len(use) >= 3 else np.ones(len(use), bool)   # Verdeckungen dunkeln nur ab
        if not ok.any():
            ok = np.ones(len(use), bool)
        wv = w[ok] / w[ok].sum()
        mean = np.minimum((rgb[ok] * wv[:, None]).sum(0), 1.0)      # Albedo ≤ 1
        k0 = ix[0]
        out["b"].append(obs["b"][k0]); out["s"].append(obs["s"][k0])
        out["ti"].append(obs["ti"][k0]); out["zi"].append(obs["zi"][k0])
        out["rgb"].append(mean)
        out["n_foto"].append(len(set(obs["foto"][ix])))
        out["n_licht"].append(int(lit.sum()))
        out["streuung"].append(float(np.sqrt((wv * (lum(rgb[ok]) - lum(mean)) ** 2).sum()) / max(lum(mean), 1e-3)))
        out["nur_schatten"].append(not lit.any())
        out["pos"].append(obs["pos"][use][ok].mean(0))
        nv = obs["nrm"][use][ok].mean(0)
        out["nrm"].append(nv / max(np.linalg.norm(nv), 1e-9))
    return {k: np.array(v) for k, v in out.items()}


def _wmedian(x, w):
    o = np.argsort(x)
    cw = np.cumsum(w[o])
    return x[o][np.searchsorted(cw, cw[-1] / 2)]


# --------------------------------------------------------------------------
# Flächen: Guillotine-Segmentierung der abgewickelten Fassaden
# --------------------------------------------------------------------------
def _lab(rgb_lin):
    """Lineares RGB (..., 3) -> CIE-Lab (D65)."""
    m = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = np.asarray(rgb_lin) @ m.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 216 / 24389, np.cbrt(xyz), (24389 / 27 * xyz + 16) / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def raster(kons, b, s, block=2, nur_licht=False):
    """Konsens-Zellen einer Fassade als Gitter [T, Z] (Blöcke von block × block Zellen).

    Gibt (rgb[T,Z,3] linear, gewicht[T,Z]) zurück; Gewicht 0 = keine Messung. Das Gewicht wächst
    mit Anzahl besonnter Fotos (n_licht) und Fotos (n_foto), ist aber je Zelle auf 3 begrenzt."""
    m = (kons["b"] == b) & (kons["s"] == s)
    if nur_licht:
        m &= kons["n_licht"] > 0
    if not m.any():
        return None, None
    ti, zi = kons["ti"][m] // block, kons["zi"][m] // block
    T, Z = ti.max() + 1, zi.max() + 1
    rgb = np.zeros((T, Z, 3))
    w = np.zeros((T, Z))
    wt = np.minimum(kons["n_foto"][m], 3) + np.minimum(kons["n_licht"][m], 3)
    for k in range(len(ti)):
        rgb[ti[k], zi[k]] += kons["rgb"][m][k] * wt[k]
        w[ti[k], zi[k]] += wt[k]
    ok = w > 0
    rgb[ok] /= w[ok][:, None]
    return rgb, w


def guillotine(lab, w, max_blatt=10, min_kante=2, min_gewinn=3.5 ** 2):
    """Zerlegt das Gitter in Rechtecke gleichmäßiger Farbe (best-first, waagerechte/senkrechte Schnitte).

    lab [T,Z,3] Lab-Farben, w [T,Z] Gewichte. Ein Rechteck wird geteilt, solange der Gewinn an
    Streuung (Σ w·ΔE²) je Zelle über min_gewinn liegt; höchstens max_blatt Rechtecke, jede Kante
    mindestens min_kante Blöcke. Gibt Liste (t0, t1, z0, z1) zurück (Blockindizes, halboffen)."""
    T, Z = w.shape
    W1 = np.pad(np.cumsum(np.cumsum(w, 0), 1), ((1, 0), (1, 0)))
    S1 = [np.pad(np.cumsum(np.cumsum(w * lab[..., c], 0), 1), ((1, 0), (1, 0))) for c in range(3)]
    S2 = np.pad(np.cumsum(np.cumsum(w * (lab ** 2).sum(-1), 0), 1), ((1, 0), (1, 0)))

    def box(A, t0, t1, z0, z1):
        return A[t1, z1] - A[t0, z1] - A[t1, z0] + A[t0, z0]

    def sse(t0, t1, z0, z1):
        n = box(W1, t0, t1, z0, z1)
        if n <= 0:
            return 0.0, 0.0
        s2 = box(S2, t0, t1, z0, z1)
        sq = sum(box(S1[c], t0, t1, z0, z1) ** 2 for c in range(3))
        return max(s2 - sq / n, 0.0), n

    def beste(t0, t1, z0, z1):
        base, n = sse(t0, t1, z0, z1)
        best = (0.0, None)
        if n <= 0:
            return best
        for t in range(t0 + min_kante, t1 - min_kante + 1):
            g = base - sse(t0, t, z0, z1)[0] - sse(t, t1, z0, z1)[0]
            if g > best[0]:
                best = (g, ("t", t))
        for z in range(z0 + min_kante, z1 - min_kante + 1):
            g = base - sse(t0, t1, z0, z) [0] - sse(t0, t1, z, z1)[0]
            if g > best[0]:
                best = (g, ("z", z))
        return best

    leaves = [(0, T, 0, Z)]
    cand = {leaves[0]: beste(*leaves[0])}
    while len(leaves) < max_blatt:
        r = max(leaves, key=lambda r: cand[r][0])
        g, cut = cand[r]
        n = box(W1, *r)
        if cut is None or g / max(n, 1) < min_gewinn:
            break
        t0, t1, z0, z1 = r
        kids = [(t0, cut[1], z0, z1), (cut[1], t1, z0, z1)] if cut[0] == "t" else \
               [(t0, t1, z0, cut[1]), (t0, t1, cut[1], z1)]
        leaves.remove(r)
        del cand[r]
        for k in kids:
            leaves.append(k)
            cand[k] = beste(*k)
    return leaves


def segmentiere(kons, sc, b, s, block=2, **kw):
    """Rechtecke gleichmäßiger Farbe auf Fassade (Gebäude b, Seite s): Liste von dict mit
    seite, z (m), entlang (Anteil), rgb (linear), n (Zellen mit Messung), anteil_licht."""
    rgb, w = raster(kons, b, s, block)
    if rgb is None or (b, s) not in sc.ext:
        return []
    lab = _lab(rgb)
    leaves = guillotine(lab, w, **kw)
    ax, t0, t1 = sc.ext[(b, s)]
    L = t1 - t0
    m = (kons["b"] == b) & (kons["s"] == s)
    out = []
    for (a0, a1, c0, c1) in leaves:
        sel = w[a0:a1, c0:c1] > 0
        if not sel.any():
            continue
        ww = w[a0:a1, c0:c1][sel]
        col = (rgb[a0:a1, c0:c1][sel] * ww[:, None]).sum(0) / ww.sum()
        cells = m & (kons["ti"] // block >= a0) & (kons["ti"] // block < a1) & \
            (kons["zi"] // block >= c0) & (kons["zi"] // block < c1)
        out.append(dict(seite="NOSW"[s], z=[c0 * block * ZELLE, c1 * block * ZELLE],
                        entlang=[round(min(a0 * block * ZELLE / L, 1.0), 4), round(min(a1 * block * ZELLE / L, 1.0), 4)],
                        rgb=col, n=int(cells.sum()), anteil_licht=float((kons["n_licht"][cells] > 0).mean()),
                        fotos=float(kons["n_foto"][cells].mean()), streuung=float(np.median(kons["streuung"][cells]))))
    return out


def palette_bilden(zonen, schwelle=7.0):
    """Fasst ähnliche Zonenfarben zusammen (Lab-Abstand < schwelle, flächengewichtet).
    Gibt (Palette[{rgb, n}], Index je Zone) zurück."""
    cols = np.array([z["rgb"] for z in zonen])
    n = np.array([z["n"] for z in zonen], float)
    groups = [[i] for i in range(len(zonen))]
    lab = lambda g: _lab((cols[g] * n[g][:, None]).sum(0) / n[g].sum())
    while len(groups) > 1:
        best = None
        for i in range(len(groups)):
            for j in range(i + 1, len(groups)):
                d = np.linalg.norm(lab(groups[i]) - lab(groups[j]))
                if best is None or d < best[0]:
                    best = (d, i, j)
        if best[0] > schwelle:
            break
        _, i, j = best
        groups[i] += groups.pop(j)
    pal = [dict(rgb=(cols[g] * n[g][:, None]).sum(0) / n[g].sum(), n=int(n[g].sum())) for g in groups]
    idx = np.zeros(len(zonen), int)
    for k, g in enumerate(groups):
        idx[g] = k
    return pal, idx


# --------------------------------------------------------------------------
# Zonen: Zellen -> benannte Farben der Fassaden-Spezifikation
# --------------------------------------------------------------------------
def zonen_zuordnung(sc, slug, spec, kons):
    """Farbname (Schlüssel in spec["farben"]) je Konsens-Zelle des Gebäudes `slug`; None = Dach/außerhalb.

    Dieselbe Logik wie fassaden.zone_keys, aber für Zellmittelpunkte statt Dreiecke: spätere Zonen
    überschreiben frühere; z = Höhe über Gebäudeboden, seite = Himmelsrichtung der Wandnormale,
    entlang = Anteil entlang der Fassade dieser Seite.
    """
    b = sc.slugs.index(slug)
    m = (kons["b"] == b)
    n = int(m.sum())
    keys = np.array([spec["basis"]] * n, dtype=object)
    pos = kons["pos"][m]
    z = pos[:, 2] - sc.dz[b]
    nrm = kons["nrm"][m]
    mesh = szene.laden("laserscan")[slug][0]
    zones = fassaden.expand_zones(mesh, spec.get("zonen", []))
    ext = {}
    for zo in zones:
        if zo.get("flaechen", "wand") != "wand":
            continue
        sel = np.ones(n, bool)
        if "z" in zo:
            zc = (np.floor(z / ZELLE) + 0.5) * ZELLE
            sel &= (zc >= zo["z"][0]) & (zc < zo["z"][1])
        if "seite" in zo:
            sel &= fassaden.side_mask(nrm, zo["seite"])
            if "entlang" in zo:
                k = json.dumps(zo["seite"])
                if k not in ext:
                    ext[k] = fassaden.side_extent(mesh, zo["seite"])
                if ext[k] is None:
                    continue
                ax, t0, t1 = ext[k]
                t = (pos[:, :2] @ ax - t0) / max(t1 - t0, 1e-9)
                sel &= (t >= zo["entlang"][0]) & (t < zo["entlang"][1])
        keys[sel] = zo["farbe"]
    full = np.array([None] * len(kons["b"]), dtype=object)
    full[np.nonzero(m)[0]] = keys
    return full


# --------------------------------------------------------------------------
# Spezifikation aus der Messung
# --------------------------------------------------------------------------
def de(rgb_a, rgb_b):
    """Farbabstand (Lab, ΔE76) zweier linearer RGB-Werte."""
    return float(np.linalg.norm(_lab(rgb_a) - _lab(rgb_b)))


def lin_hex(h):
    return lin(np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)]) / 255.0)


def neue_spezifikation(slug, sc, kons, min_zellen=30, abw_min=9.0, min_leaf=20, min_fotos=1.0, palette_de=6.0,
                       nur_licht=True, **seg_kw):
    """Neue Spezifikation (Format data/fassaden/<slug>.json, alle Farben als hex) eines Gebäudes.

    1. Die Farben der alten Zonen („Schlüssel“) werden aus den besonnten Zellen neu bestimmt, wenn
       mindestens min_zellen vorliegen (flächengewichteter Mittelwert, lineares RGB).
    2. Jede Fassade wird per Guillotine in Rechtecke gleichmäßiger Farbe zerlegt. Ein Rechteck wird zur
       neuen Zone, wenn seine Farbe um mehr als abw_min (ΔE) von der Farbe der alten Zone abweicht, die
       dort lag, und es besonnt gemessen ist (anteil_licht ≥ 0,5) und mindestens min_leaf Zellen hat.
    3. Zonenreihenfolge (spätere gewinnen): alte Zonen, neue Zonen, alte „feste“ Zonen (Bögen, Kreise,
       Portal usw.: "fest": true oder kreis/bogen).
    Gibt (spec, bericht) zurück."""
    spec = fassaden.load_spec(slug)
    b = sc.slugs.index(slug)
    keys = zonen_zuordnung(sc, slug, spec, kons)
    fest = [z for z in spec["zonen"] if z.get("fest") or "kreis" in z or "bogen" in z]
    fest_keys = {z["farbe"] for z in fest}
    farben, bericht = {}, dict(farben={}, zonen=[], seiten={})
    cur = {}                                        # Farbe je Schlüssel (linear) nach Neubestimmung
    for k, f in spec["farben"].items():
        old_rgb = f["hex"]                           # eingefrorener Wert der Handmessung (spec_einfrieren.py)
        m = np.array([x == k for x in keys])
        ml = m & (kons["n_licht"] > 0)
        rgb, n = lin_hex(old_rgb), int(ml.sum())
        neu, grund = False, "zu wenige besonnte Messzellen: %d" % n
        if k not in fest_keys and n >= min_zellen:
            w = np.minimum(kons["n_foto"][ml], 3) + np.minimum(kons["n_licht"][ml], 3)
            mean = (kons["rgb"][ml] * w[:, None]).sum(0) / w.sum()
            # Nur umfärben, wenn die Zone einheitlich ist: Median-ΔE der Zellen zum Mittel ≤ 9 (sonst enthält die
            # Zone mehrere Materialien, z. B. Stein und Glas, und ein Mittel würde keines davon treffen)
            dev = np.array([de(c, mean) for c in kons["rgb"][ml][:: max(1, n // 400)]])
            if np.median(dev) <= 9.0 or k == spec["basis"]:       # die Grundfarbe gilt auch für alle nicht gemessenen Wände
                rgb, neu = mean, True
            else:
                grund = "Zone uneinheitlich (Median-ΔE %.0f): Farbe bleibt, Flächen kommen aus der Segmentierung" % np.median(dev)
        cur[k] = rgb
        farben[k] = dict(hex=hexrgb(rgb), notiz=f.get("notiz", ""), alt=old_rgb,
                         quelle=("Fotos: %d besonnte Zellen" % n) if neu else "unverändert (%s)" % grund)
        bericht["farben"][k] = dict(alt=old_rgb, neu=hexrgb(rgb), gemessen=neu, zellen=n, zellen_alle=int(m.sum()))
    # neue Zonen aus der Segmentierung
    cand = []
    for s_ in range(4):
        for z in segmentiere(kons, sc, b, s_, **seg_kw):
            cand.append((s_, z))
    leaf_info = []
    for s_, z in cand:
        ax, t0, t1 = sc.ext[(b, s_)]
        L = t1 - t0
        sel = (kons["b"] == b) & (kons["s"] == s_) & (kons["zi"] * ZELLE >= z["z"][0] - 1e-6) & (kons["zi"] * ZELLE < z["z"][1] - 1e-6) \
            & (kons["ti"] * ZELLE >= z["entlang"][0] * L - 1e-6) & (kons["ti"] * ZELLE < z["entlang"][1] * L - 1e-6)
        under = [keys[i] or spec["basis"] for i in np.nonzero(sel)[0]]
        uk = max(set(under), key=under.count) if under else spec["basis"]
        d = de(z["rgb"], cur[uk])
        ok = z["n"] >= min_leaf and z["anteil_licht"] >= 0.5 and d >= abw_min and z["fotos"] >= min_fotos
        # Erdgeschosszone (bis 8 m): Bäume, Personen, Fahrzeuge und Spiegelungen verdecken die Wand häufig. Große
        # Farbsprünge dort gelten als Verdeckung, nicht als Material.
        if ok and z["z"][1] <= EG_HOEHE and d > EG_MAX_DE:
            ok = False
        leaf_info.append(dict(seite=z["seite"], z=z["z"], entlang=z["entlang"], rgb=hexrgb(z["rgb"]), n=z["n"],
                              licht=round(z["anteil_licht"], 2), fotos=round(z["fotos"], 2), unter=uk, de=round(d, 1),
                              neu=bool(ok)))
        if ok:
            leaf_info[-1]["_rgb"] = z["rgb"]
    # Palette der neuen Zonen (ähnliche Farben zusammenlegen, vorhandene Schlüsselfarben wiederverwenden)
    acc = [(li) for li in leaf_info if li["neu"]]
    zonen_neu = []
    if acc:
        pal, idx = palette_bilden([dict(rgb=a["_rgb"], n=a["n"]) for a in acc], palette_de)
        name = {}
        for pi, p in enumerate(pal):
            nearest = min(cur, key=lambda k: de(p["rgb"], cur[k]))
            if de(p["rgb"], cur[nearest]) < palette_de and nearest not in fest_keys:
                name[pi] = nearest
            else:
                name[pi] = "m%d" % (len([k for k in farben if k.startswith("m") and k[1:].isdigit()]) + 1)
                farben[name[pi]] = dict(hex=hexrgb(p["rgb"]), notiz="aus Fotos gemessene Fläche (automatisch)",
                                        quelle="Fotos: %d Messzellen" % p["n"])
                cur[name[pi]] = p["rgb"]
        for a, pi in zip(acc, idx):
            zonen_neu.append(dict(name="Messung %s z %g–%g m" % (a["seite"], a["z"][0], a["z"][1]), farbe=name[pi],
                                  seite=a["seite"], z=a["z"], entlang=a["entlang"], quelle="farbmessung"))
    for li in leaf_info:
        li.pop("_rgb", None)
    bericht["zonen"] = leaf_info
    out = dict(basis=spec["basis"], farben=farben,
               zonen=[z for z in spec["zonen"] if z not in fest] + zonen_neu + fest)
    for k in out["farben"]:
        if k in spec["farben"] and "quelle" not in out["farben"][k]:
            out["farben"][k]["quelle"] = "alt"
    return out, bericht


# --------------------------------------------------------------------------
# Darstellung: abgewickelte Fassaden
# --------------------------------------------------------------------------
def fassadenkarte(kons, b, seite, farbe_fn=None, px=10, maske=None):
    """Abgewickelte Fassade (Zellen als Kacheln, links→rechts von außen gesehen, unten = Boden).

    farbe_fn(i) -> lineares RGB der Zelle i (Standard: Konsensfarbe); maske: bool je Zelle (False = leer).
    Gibt PIL-Bild und (Breite, Höhe) in Zellen zurück oder None."""
    from PIL import Image
    m = (kons["b"] == b) & (kons["s"] == seite)
    if maske is not None:
        m &= maske
    if not m.any():
        return None
    ti, zi = kons["ti"][m], kons["zi"][m]
    T, Z = ti.max() + 1, zi.max() + 1
    im = np.full((Z * px, T * px, 3), 240, np.uint8)
    for i in np.nonzero(m)[0]:
        col = kons["rgb"][i] if farbe_fn is None else farbe_fn(i)
        im[(Z - 1 - kons["zi"][i]) * px:(Z - kons["zi"][i]) * px, kons["ti"][i] * px:(kons["ti"][i] + 1) * px] = \
            (srgb(col) * 255).round().astype(np.uint8)
    return Image.fromarray(im), (T, Z)


def gewichte_nach_uebereinstimmung(kp, soll=0.5, minimum=0.25):
    """Fotos, deren besonnte Blöcke stark von den übrigen abweichen (Belichtung, Nachbearbeitung, Ausrichtung),
    gehen mit geringerem Gewicht ein: q = soll / Abweichung, begrenzt auf [minimum, 1]. Fotos ohne gemeinsame
    Blöcke behalten das Gewicht 1. Es wird nichts umgerechnet, nur gewichtet."""
    return {f: float(np.clip(soll / max(v["rel_hell"], 1e-3), minimum, 1.0)) for f, v in kp.items()}


EG_HOEHE, EG_MAX_DE = 8.5, 28.0   # Erdgeschosszone: Höhe (m) und größter zulässiger Farbsprung (ΔE)


def kreuzpruefung(obs, block=4):
    """Wie gut stimmt jedes Foto mit den übrigen überein? Die besonnten Beobachtungen werden je Foto auf
    Blöcke von block × block Zellen (4 × 4 m, die Größenordnung der späteren Flächen) gemittelt und dann mit
    dem gewichteten Mittel der anderen Fotos im selben Block verglichen: Zahl gemeinsamer Blöcke, Median der
    relativen Helligkeitsabweichung und des Farbabstands (ΔE). Das prüft Konsistenz (Ausrichtung, Belichtung,
    Beleuchtungsmodell), nicht die absolute Richtigkeit der Farben."""
    m = obs["lit"]
    code = ((obs["b"][m] * 4 + obs["s"][m]).astype(np.int64) * 256 + obs["ti"][m] // block) * 256 + obs["zi"][m] // block
    foto = obs["foto"][m]
    rgb, w = obs["rgb"][m], obs["w"][m]
    key = {}
    for i in range(len(code)):
        k = (int(code[i]), foto[i])
        a = key.setdefault(k, [np.zeros(3), 0.0])
        a[0] += rgb[i] * w[i]
        a[1] += w[i]
    blocks = {}
    for (c, f), (sw, ww) in key.items():
        blocks.setdefault(c, {})[f] = (sw / ww, ww)
    res = {}
    for c, d in blocks.items():
        if len(d) < 2:
            continue
        for f, (col, ww) in d.items():
            oth = [(v, x) for g, (v, x) in d.items() if g != f]
            other = sum(v * x for v, x in oth) / sum(x for _, x in oth)
            yj, yo = lum(col), lum(other)
            if yj < 0.02 or yo < 0.02:
                continue
            r = res.setdefault(f, ([], []))
            r[0].append(abs(yj - yo) / yo)
            r[1].append(de(col, other))
    return {f: dict(zellen=len(v[0]), rel_hell=round(float(np.median(v[0])), 3), de=round(float(np.median(v[1])), 1))
            for f, v in res.items()}


def foto_blatt(slug, pfad):
    """Kontaktbogen der Fotos, aus denen die Farben dieses Gebäudes gemessen wurden (Urheber, Lizenz, Datum,
    Sonnenhöhe). Gibt pfad zurück oder None (und löscht ein veraltetes Blatt), wenn es keine gibt."""
    import registrierung as R
    from PIL import Image, ImageDraw
    import preview as P
    kat = R.lade_katalog()["fotos"]
    mess = json.load(open(MESSUNG))["fotos"] if os.path.exists(MESSUNG) else {}
    ids = [i for i, e in kat.items() if e.get("geprueft") and i in mess and slug[:2] in e.get("gebaeude", [])]
    if not ids:
        if os.path.exists(pfad):
            os.remove(pfad)
        return None
    tiles = []
    for i in ids:
        e = kat[i]
        im = R.foto_bild(i, e)
        im.thumbnail((620, 440))
        t = Image.new("RGB", (640, 500), P.BG)
        t.paste(im, ((640 - im.width) // 2, 0))
        sonne = "bedeckt" if e.get("bedeckt") else ("Sonne %.0f°" % mess[i]["sonne"] if mess[i].get("sonne") is not None else "")
        d = ImageDraw.Draw(t)
        d.text((10, 450), "%s · %s · %s" % (e["urheber"], e["lizenz"], (e.get("zeit") or "")[:10]), fill=(60, 60, 60), font=P.font(14))
        d.text((10, 472), sonne + "  ·  " + i, fill=(110, 110, 110), font=P.font(12))
        tiles.append(t)
    cols = 3
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 640, rows * 500 + 40), P.BG)
    for k, t in enumerate(tiles):
        sheet.paste(t, ((k % cols) * 640, (k // cols) * 500))
    ImageDraw.Draw(sheet).text((10, sheet.height - 28), "Fotos der Fotoprojektion (farbmessung.py); Lizenzen siehe FOTOQUELLEN.md.",
                               fill=(60, 60, 60), font=P.font(14))
    os.makedirs(os.path.dirname(pfad), exist_ok=True)
    sheet.save(pfad, quality=85)
    return pfad


MESSUNG = os.path.join(G.HERE, "data", "messung.json")
# Flächen: Rechtecke aus 2-m-Blöcken (Kante ≥ 4 m), nur mit ≥ 30 besonnten Zellen und ΔE ≥ 8 zur bisherigen Zone
SEGMENT = dict(max_blatt=9, min_gewinn=4.5 ** 2, min_kante=2, min_leaf=30, abw_min=8.0)


def messen_konsens(nur=None):
    """Konsens der geprüften Fotos (aus dem Cache data/cache/messung) ohne data/messung.json zu schreiben.
    Gibt (kons, ergebnisse) zurück."""
    import registrierung as R
    kat = R.lade_katalog()["fotos"]
    ids = [i for i, e in kat.items() if e.get("geprueft") and (nur is None or i in nur)]
    sc = Szene()
    res = {i: bearbeite(i, kat[i], sc) for i in ids}
    gain, _ = harmonisiere(res, kat)
    obs = beobachtungen(res, kat, gain)
    q = gewichte_nach_uebereinstimmung(kreuzpruefung(obs))
    gew = {f: dict(e, qualitaet=float(e.get("qualitaet", 1.0)) * q.get(f, 1.0)) for f, e in kat.items()}
    return konsens(beobachtungen(res, gew, gain)), res


def messen(force=False, nur=None):
    """Misst alle geprüften Fotos, bildet den Konsens und schreibt data/messung.json."""
    import registrierung as R
    kat = R.lade_katalog()["fotos"]
    ids = [i for i, e in kat.items() if e.get("geprueft") and (nur is None or i in nur)]
    sc = Szene()
    res = {}
    for i in ids:
        res[i] = bearbeite(i, kat[i], sc, force=force)
        c = res[i]["cells"]
        print("  %-16s %5d Zellen  Sonne %s" % (i, 0 if c is None else len(c["n"]),
                                              "-" if res[i]["alt"] is None else "%.0f°" % res[i]["alt"]))
    gain, how = harmonisiere(res, kat)
    obs = beobachtungen(res, kat, gain)
    kp = kreuzpruefung(obs)
    q = gewichte_nach_uebereinstimmung(kp)
    gew = {f: dict(e, qualitaet=float(e.get("qualitaet", 1.0)) * q.get(f, 1.0)) for f, e in kat.items()}
    obs2 = beobachtungen(res, gew, gain)               # zweiter Durchgang mit Gewichten
    kons = konsens(obs2)
    kp2 = kreuzpruefung(obs2)
    out = dict(_hinweis="Ergebnis von farbmessung.py (python3 farbmessung.py messen). Farben als hex; "
                        "farben.building_colours nimmt sie anstelle der Handmessung.",
               fotos={i: dict(gain=round(float(gain[i][0]), 3), herkunft=how[i], kreuzpruefung=kp.get(i), gewicht=round(q.get(i, 1.0), 2),
                              kreuzpruefung_gewichtet=kp2.get(i),
                              sonne=None if res[i]["alt"] is None else round(float(res[i]["alt"]), 1),
                              zellen=0 if res[i]["cells"] is None else int(len(res[i]["cells"]["n"]))) for i in ids},
               gebaeude={})
    for slug in sc.slugs:
        if (kons["b"] == sc.slugs.index(slug)).sum() < 50:
            continue
        spec, ber = neue_spezifikation(slug, sc, kons, **SEGMENT)
        out["gebaeude"][slug] = dict(spec, bericht=ber)
        n_neu = sum(1 for z in ber["zonen"] if z["neu"])
        print("  %-22s %d Farben neu bestimmt, %d neue Zonen" % (slug, sum(v["gemessen"] for v in ber["farben"].values()), n_neu))
    with open(MESSUNG, "w") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    print("->", os.path.relpath(MESSUNG, G.HERE))
    return kons, out


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 2 and sys.argv[1] == "messen":
        messen(force="--neu" in sys.argv)
    else:
        print(__doc__)
