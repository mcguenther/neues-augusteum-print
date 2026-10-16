"""Gebäude als Hohlkörper: dünne Wand, unten offen, Decke als 45°-Gewölbe ohne Überhänge, Kanten und Brücken.

Eingabe ist der massive Volumenkörper eines Gebäudes (Manifold, mm, Boden bei z=0, aus dem Boden extrudiert, der Querschnitt
nimmt nach oben nur ab; so sind alle drei Quellen gebaut). Ausgabe ist die Schale ohne Boden: Wand `WAND`, Dach mindestens `DACH`.
Plan und Zahlen: plug/hollow/plan.html, Studie plug/hollow/study.py.

Verfahren (je 0,4 mm Höhe eine Lage):
  1. Querschnitt C(z) der Lage schneiden. Ziel-Hohlraum E(z) = Querschnitt `DACH` weiter oben, um `WAND` nach innen versetzt.
     Da E nach oben nur kleiner wird, ist der Ziel-Hohlraum eine Säule je Grundrisspunkt bis zur Höhe H(p) (Höhenfeld).
  2. Gewölbe: Tragend sind nur die Wände, die vom Boden an durchgehen (Wandring der untersten Lage, dazu Teile, die zu schmal für einen
     Hohlraum sind). Die Decke wird als Höhenfeld h(p) = min über alle tragenden Punkte w von (phi(w) + |p - w|) gebaut: Kegel mit 45°,
     die von den Wänden aufsteigen. Jede Stelle der Decke steigt damit genau mit 45° zur nächsten Wand ab; es gibt keine Senke, keine
     Kante nach unten und keine flache Brücke, die Decke schließt oben in einem First. phi(w) ist so hoch wie möglich gewählt, dass h
     nirgends über H liegt: der kleinste Wert von H(p) - |p - w| über die frei hängenden Deckenstellen p, deren nächste Wand w ist
     (frei hängend: weiter als `TOL` von Wand oder tieferer Decke; steile Dächer und Stellen an der Wand tragen sich selbst).
  3. Hohlraum = Ziel-Hohlraum (Platten je Lage, exakte Wände) geschnitten mit dem Körper unter der Kegelfläche (Höhenfeld-Netz, glatte
     45°-Flächen statt Lagenstufen). Weil jede Grundrissstelle eine Säule bis zur Decke ist, gibt es keine Taschen über dem Gewölbe.
  4. Den Hohlraum (nach unten offen) vom Volumenkörper abziehen und das Netz leicht vereinfachen (`VEREINFACHEN`).
Die Kegelfläche wird auf einem Raster von `PX` mm gerechnet (OpenCV-Distanztransformation); die Wände bleiben exakt.
"""
import cv2
import numpy as np

cv2.setNumThreads(0)   # keine OpenCV-Threads: generate.py rechnet in per fork gestarteten Prozessen (Threads darin blockieren)
import manifold3d as m3d
from shapely.geometry import MultiPolygon, Polygon
from shapely.ops import unary_union

WAND = 0.8        # mm Wandstärke (Plan: Entscheidung 1, hängt an der Lichtprobe)
DACH = 0.8        # mm Dachstärke (mindestens; unter dem Gewölbe ist das Dach dicker)
STEP = 0.4        # mm Höhenraster der Lagen
PX = 0.1          # mm Rasterweite für das Gewölbe
TOL = 0.45        # mm Überhang je Lage, der als getragen gilt (etwa 45° bei 0,4 mm Lagenhöhe)
WINKEL = 45.0     # Grad, Neigung des Gewölbes gegen die Senkrechte (45 = Standard für Drucke ohne Stützen)
FIRST = 0.0       # mm, Breite des flachen Streifens oben im Gewölbe (0 = Gewölbe schließt in einem First, keine Brücke)
RAND = 0.4        # mm, Gewölbe einer Decke greift in bis zu so viel höhere Decken daneben (mehr kostet viel Hohlraum, z. B. Hörsaalgebäude)
BRUECKE = 10.0    # mm, so weit darf eine Decke ohne Gewölbe frei spannen (Abstand zur nächsten Stütze höchstens die Hälfte)
VEREINFACHEN = 0.03  # mm, Netz nach dem Abziehen so weit vereinfachen (Manifold.simplify; hält die STL klein, bleibt dicht)
SAME_AREA = 0.05  # mm², Lagen, die sich weniger unterscheiden, werden zu einer Platte zusammengefasst (hält die STL klein)


def sections(man, step=STEP):
    """[(z_oben, Querschnitt als shapely-Fläche)] je Lage, Schnitt in der Lagenmitte."""
    zmax = man.bounding_box()[5]
    out, z = [], 0.0
    while z < zmax - 1e-6:
        z1 = min(z + step, zmax)
        polys = [Polygon(c) for c in man.slice((z + z1) / 2).to_polygons() if len(c) >= 3]
        g = Polygon()
        for p in polys:  # Gerade-Ungerade-Regel: Löcher heben sich über die symmetrische Differenz auf
            g = p if g.is_empty else g.symmetric_difference(p)
        out.append((z1, g.buffer(0)))
        z = z1
    return out


def prism(geom, z0, z1):
    cs = []
    for p in (geom.geoms if isinstance(geom, MultiPolygon) else [geom]):
        if p.is_empty:
            continue
        cs.append(np.asarray(p.exterior.coords)[:-1])
        for r in p.interiors:
            cs.append(np.asarray(r.coords)[:-1])
    return m3d.Manifold.extrude(m3d.CrossSection(cs, m3d.FillRule.EvenOdd), z1 - z0).translate([0, 0, z0])


def _parts(g):
    return list(g.geoms) if hasattr(g, "geoms") else [g]


class Raster:
    """Raster über dem Grundriss: Weltkoordinaten (mm) <-> Pixel."""

    def __init__(self, bounds, px=PX, margin=2.0):
        self.px = px
        self.x0, self.y0 = bounds[0] - margin, bounds[1] - margin
        self.w = int(np.ceil((bounds[2] - bounds[0] + 2 * margin) / px)) + 1
        self.h = int(np.ceil((bounds[3] - bounds[1] + 2 * margin) / px)) + 1

    def mask(self, geom):
        m = np.zeros((self.h, self.w), np.uint8)
        if geom.is_empty:
            return m.astype(bool)
        rings = []
        for p in _parts(geom):
            for r in [p.exterior] + list(p.interiors):
                xy = (np.asarray(r.coords) - (self.x0, self.y0)) / self.px
                rings.append(np.round(xy * 16).astype(np.int32))      # 4 Bit Unterpixel
        cv2.fillPoly(m, rings, 1, lineType=cv2.LINE_8, shift=4)     # Gerade-Ungerade über alle Ringe
        return m.astype(bool)


def ceiling(secs, E, step=STEP, px=PX, winkel=WINKEL, first=FIRST, bruecke=BRUECKE):
    """Kegelfläche des Gewölbes als Höhenfeld (mm) auf dem Raster, +inf wo kein Gewölbe wirkt. Liefert (Raster, hc, Ziel-Höhenfeld H)."""
    R = Raster(secs[0][1].bounds, px)
    H = np.zeros((R.h, R.w), np.float32)                         # Oberkante des Ziel-Hohlraums je Pixel
    T = np.zeros((R.h, R.w), np.float32)                         # Oberkante des Materials je Pixel
    for (z1, c), e in zip(secs, E):
        T[R.mask(c)] = z1
        if not e.is_empty:
            H[R.mask(e)] = z1
    omega = H > 0                                                # Grundriss des Hohlraums
    anchor = (T > 0) & ~omega                                    # tragende Wände: Material vom Boden an
    if not omega.any() or not anchor.any():
        return R, np.full(H.shape, np.inf, np.float32), H
    src = np.where(anchor, 0, 1).astype(np.uint8)
    d, lab = cv2.distanceTransformWithLabels(src, cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
    d = d * px
    # Frei hängende Deckenstellen: weiter als BRUECKE/2 von allem, was mindestens eine Lage tiefer liegt (Wand oder tiefere Decke).
    # Nur sie brauchen das Gewölbe; die übrigen Decken spannen höchstens BRUECKE weit und bleiben, wie sie sind.
    frei = np.zeros(H.shape, bool)
    for z in np.unique(H[omega]):
        at = omega & (H == z)
        lower = anchor | (omega & (H <= z - step + 1e-4))
        dz = cv2.distanceTransform(np.where(lower, 0, 1).astype(np.uint8), cv2.DIST_L2, cv2.DIST_MASK_PRECISE) * px
        frei |= at & (dz > max(TOL, bruecke / 2))
    # Je tragendem Pixel w: phi(w) = kleinster Wert von H - d über die frei hängenden Stellen in seinem Einzugsgebiet (höchstens die
    # Höhe der Wand selbst) und tau(w) = höchste dieser Decken. Wände ohne frei hängende Decke im Einzugsgebiet tragen kein Gewölbe.
    n = int(lab.max()) + 1
    phi = np.full(n, np.inf, np.float64)
    tau = np.full(n, -np.inf, np.float64)
    slope = 1.0 / np.tan(np.radians(winkel))                     # Höhe je mm waagerecht
    np.minimum.at(phi, lab[frei], (H - slope * np.maximum(d - first / 2, 0.0))[frei])
    np.maximum.at(tau, lab[frei], H[frei])
    tw = np.zeros(n, np.float64)
    tw[lab[anchor]] = T[anchor]
    phi = np.minimum(phi, tw)
    use = anchor & np.isfinite(tau[lab])
    h = np.full(H.shape, np.inf, np.float32)
    if use.any():
        # h(p) = min über die Wände w mit tau(w) >= H(p) - RAND von (phi(w) + |p - w|): Das Gewölbe einer niedrigen Decke greift nicht in
        # einen deutlich höheren Raum daneben, geht aber in leicht höhere Decken glatt über. Von oben nach unten: je Stufe von tau die neuen Wände dazu (je Stufe von phi eine
        # Distanztransformation), dann die Pixel fertigstellen, deren Ziel-Decke eine Stufe darüber liegt.
        kphi = np.where(use, np.ceil(phi[lab] / step - 1e-6), 0).astype(np.int64)
        ktau = np.where(use, np.round(tau[lab] / step), 0).astype(np.int64)
        kH = np.round(H / step).astype(np.int64)
        m = max(1, int(round(RAND / step)))
        G = np.full(H.shape, np.inf, np.float32)
        done = np.zeros(H.shape, bool)
        for t in range(int(kH.max()) + m, -1, -1):
            new = use & (ktau == t)
            for kp in np.unique(kphi[new]):
                sel = new & (kphi == kp)
                dk = cv2.distanceTransform(np.where(sel, 0, 1).astype(np.uint8), cv2.DIST_L2, cv2.DIST_MASK_PRECISE) * px
                np.minimum(G, kp * step + slope * dk, out=G)
            fin = omega & (kH == t + m) & ~done
            h[fin] = G[fin]
            done |= fin
        rest = omega & ~done
        h[rest] = G[rest]
    h = np.where(omega, h, np.inf).astype(np.float32)
    return R, h, H


def vault_solid(R, hc, zmax, sub=2):
    """Gewölbe-Körper als Höhenfeld-Netz: alles unter der Kegelfläche hc (glatte 45°-Flächen, Raster PX*sub). Der Hohlraum ist der
    Ziel-Hohlraum geschnitten mit diesem Körper; wo kein Gewölbe wirkt, liegt die Fläche über dem Gebäude und schneidet nichts."""
    g = hc[::sub, ::sub]
    top = np.clip(np.where(np.isfinite(g), g, zmax + 2.0), -3.0, zmax + 2.0).astype(np.float64)
    ny, nx = top.shape
    xs = R.x0 + np.arange(nx) * R.px * sub
    ys = R.y0 + np.arange(ny) * R.px * sub
    X, Y = np.meshgrid(xs, ys)
    nb = ny * nx
    verts = np.concatenate([np.stack([X, Y, top], -1).reshape(-1, 3), np.stack([X, Y, np.full_like(top, -4.0)], -1).reshape(-1, 3)])
    idx = np.arange(nb).reshape(ny, nx)
    a, b, c, d = idx[:-1, :-1].ravel(), idx[:-1, 1:].ravel(), idx[1:, 1:].ravel(), idx[1:, :-1].ravel()
    faces = [np.stack([a, b, c], 1), np.stack([a, c, d], 1), np.stack([a + nb, c + nb, b + nb], 1), np.stack([a + nb, d + nb, c + nb], 1)]
    ring = np.concatenate([idx[0, :], idx[1:, -1], idx[-1, -2::-1], idx[-2:0:-1, 0]])   # Rand gegen den Uhrzeigersinn (von oben)
    p, q = ring, np.roll(ring, -1)
    faces += [np.stack([p, p + nb, q + nb], 1), np.stack([p, q + nb, q], 1)]
    mesh = m3d.Mesh(vert_properties=verts.astype(np.float32), tri_verts=np.concatenate(faces).astype(np.uint32))
    man = m3d.Manifold(mesh)
    if man.status() != m3d.Error.NoError:
        raise RuntimeError("Gewölbe-Körper ungültig: %s" % man.status())
    if man.volume() < 0:
        raise RuntimeError("Gewölbe-Körper falsch orientiert")
    return man.simplify(0.02)


def _cs_poly(cs):
    g = Polygon()
    for c in cs.to_polygons():
        if len(c) >= 3:
            p = Polygon(c)
            g = p if g.is_empty else g.symmetric_difference(p)
    return g.buffer(0)


def target(man, wand=WAND, dach=DACH, step=STEP):
    """Schnitte und Ziel-Hohlraum ohne Gewölbe: [(z_oben, Querschnitt C, Ziel-Hohlraum E)]."""
    secs = sections(man, step)
    n = len(secs)
    out = []
    for z1, c in secs:
        j = int(round((z1 + dach) / step)) - 1
        pj = secs[j][1] if j < n else Polygon()
        e = pj.buffer(-wand, join_style=2, mitre_limit=3.0).simplify(0.05) if not pj.is_empty else Polygon()
        out.append((z1, c, Polygon() if e.is_empty or e.area < 0.5 else e))
    return out


def cavity(lay, step=STEP):
    """Hohlraum aus den Lagen: übereinanderliegende Platten (gleiche Lagen zusammengefasst) von unter dem Boden (offen) bis zur Decke.
    Die Platten stoßen mit exakt gleichen z-Werten aneinander, so bleibt die Vereinigung ohne Splitter."""
    slabs, i0, n = [], 0, len(lay)
    while i0 < n:
        k = lay[i0][2]
        i1 = i0
        while i1 + 1 < n and not k.is_empty and k.symmetric_difference(lay[i1 + 1][2]).area < SAME_AREA:
            i1 += 1
        if not k.is_empty:
            z0 = -0.5 if i0 == 0 else lay[i0 - 1][0]
            slabs.append(prism(k, z0, lay[i1][0]))
        i0 = i1 + 1
    return m3d.Manifold.batch_boolean(slabs, m3d.OpType.Add) if slabs else None


def hohl(solid, wand=WAND, dach=DACH, step=STEP, gewoelbe=True, winkel=WINKEL, first=FIRST, bruecke=BRUECKE):
    """(Schale als Manifold, Lagen [(z_oben, C, Hohlraum dieser Lage)]). Ist kein Hohlraum möglich, kommt der Volumenkörper zurück."""
    lay0 = target(solid, wand, dach, step)
    cav = cavity(lay0, step)
    if cav is None:
        return solid, lay0
    if gewoelbe:
        R, hc, _ = ceiling([(z1, c) for z1, c, _ in lay0], [e for _, _, e in lay0], step, winkel=winkel, first=first, bruecke=bruecke)
        if np.isfinite(hc).any():
            cav = cav ^ vault_solid(R, hc, lay0[-1][0])
    shell = (solid - cav).simplify(VEREINFACHEN)
    lay = []
    z0 = 0.0
    for z1, c, _ in lay0:
        k = _cs_poly(cav.slice((z0 + z1) / 2))
        lay.append((z1, c, Polygon() if k.is_empty or k.area < 0.5 else k))
        z0 = z1
    return shell, lay


def layers(man, wand=WAND, dach=DACH, step=STEP, gewoelbe=True, winkel=WINKEL, first=FIRST, bruecke=BRUECKE):
    """[(z_oben, Querschnitt C, Hohlraum K)] je Lage (Schnitt in der Lagenmitte); gewoelbe=False liefert den Ziel-Hohlraum."""
    if not gewoelbe:
        return target(man, wand, dach, step)
    return hohl(man, wand, dach, step, True, winkel, first, bruecke)[1]


def inner_mask(tm, lay, step=STEP):
    """Welche Dreiecke des Schalennetzes (trimesh, Koordinaten wie der Volumenkörper) liegen am Hohlraum (innen)?
    Prüfung: 0,15 mm vor dem Dreieck in Normalenrichtung liegt im Hohlraum der Lage."""
    import shapely
    q = tm.triangles_center + 0.15 * tm.face_normals
    idx = np.floor(q[:, 2] / step).astype(int)
    inner = np.zeros(len(tm.faces), bool)
    for i in np.unique(idx):
        if 0 <= i < len(lay) and not lay[i][2].is_empty:
            sel = idx == i
            inner[sel] = shapely.contains_xy(lay[i][2], q[sel, 0], q[sel, 1])
    return inner
