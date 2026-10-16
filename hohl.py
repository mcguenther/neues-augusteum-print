"""Gebäude als Hohlkörper: dünne Wand, Dach folgt dem Gebäude, unten offen, flache Decken als Gewölbe.

Eingabe ist der massive Volumenkörper eines Gebäudes (Manifold, mm, Boden bei z=0, aus dem Boden extrudiert, der Querschnitt
nimmt nach oben nur ab; so sind alle drei Quellen gebaut). Ausgabe ist die Schale ohne Boden: Wand `WAND`, Dach `DACH`.
Plan und Zahlen: plug/hollow/plan.html, Studie plug/hollow/study.py.

Verfahren (je 0,4 mm Höhe eine Lage):
  1. Querschnitt C(z) der Lage schneiden.
  2. Hohlraum E(z) = Querschnitt `DACH` weiter oben, um `WAND` nach innen versetzt (die Decke folgt dem Dach).
  3. Gewölbe: Material einer Lage, das weiter als `BRUECKE`/2 vom Material der Lage darunter entfernt ist (flache Dächer, Staffelungen,
     Seitenflügel an hohen Bauteilen), würde beim Drucken über Luft liegen. Darunter wird der Hohlraum mit 45° von der Wand her eingezogen,
     bis die freie Spannweite höchstens `BRUECKE` ist. Das prüft `plug/hollow/shell.bridge_analysis` nach.
  4. Die Lagen (gleiche zusammengefasst) zu Platten vereinigen, nach unten offen machen und vom Volumenkörper abziehen.
"""
import numpy as np
import manifold3d as m3d
from shapely.geometry import MultiPolygon, Polygon

WAND = 0.8        # mm Wandstärke (Plan: Entscheidung 1, hängt an der Lichtprobe)
DACH = 0.8        # mm Dachstärke
BRUECKE = 10.0    # mm größte freie Spannweite der Decke, darüber wird ein 45°-Gewölbe gebaut
STEP = 0.4        # mm Höhenraster der Lagen
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


TOL = 0.45        # mm Überhang je Lage, der ohne Stütze geht (45° bei 0,4 mm Lagenhöhe)


def _frei(u, prev, r):
    """Teil von u, der weiter als r vom Material der Lage darunter (prev) entfernt ist (Splitter entfernt)."""
    g = u.difference(prev.buffer(r, quad_segs=4))
    return g.buffer(-0.05).buffer(0.05) if not g.is_empty and g.area > 0.1 else Polygon()


def vault(C, E, reach, step=STEP):
    """Zieht die Hohlräume E (je Lage) unter freien Decken mit 45° ein, bis jede Stelle höchstens `reach` von einer Stütze entfernt ist.

    Von unten nach oben: Material einer Lage, das nicht von der Lage darunter getragen wird (U = Material minus Material darunter plus TOL),
    darf höchstens `reach` (halbe Spannweite) von dieser Lage entfernt sein. Liegt ein Teil O weiter weg, ist s = größter Abstand - reach
    der nötige Einzug. Darunter wird je Lage ein Ring von der Wand her zu Material: direkt unter der Decke s breit, nach unten je Lage
    um `step` schmaler (45°), und nur in der Nähe von O."""
    n = len(E)
    K = list(E)

    def mat(i):
        return C[i].difference(K[i]) if not K[i].is_empty else C[i]

    for _durchgang in range(4):                          # Einzüge ändern tiefere Lagen: wiederholen, bis nichts mehr nachkommt
        if not _vault_pass(C, K, reach, step, mat):
            break
    return [Polygon() if k.is_empty else k.simplify(0.03) for k in K]


def _vault_pass(C, K, reach, step, mat):
    n, changed = len(K), False
    for i in range(1, n):
        Mi, prev = mat(i), mat(i - 1)
        U = Mi.difference(prev.buffer(TOL, join_style=1, quad_segs=4))
        if U.is_empty:
            continue
        O = _frei(U, prev, reach)
        if O.is_empty:
            continue
        lo, hi = reach, reach + 80.0
        for _ in range(9):                               # größter Abstand zur Stütze
            mid = (lo + hi) / 2
            if _frei(U, prev, mid).is_empty:
                hi = mid
            else:
                lo = mid
        s = lo - reach
        m = int(np.ceil(s / step - 1e-9))
        for t in range(1, m + 1):
            k = i - t
            if k < 0:
                break
            b = max(s - (t - 1) * step, step)
            if K[k].is_empty:
                continue
            band = K[k].intersection(mat(k).buffer(b, quad_segs=4)).intersection(O.buffer(b + reach, quad_segs=4))
            if not band.is_empty:
                kk = K[k].difference(band).buffer(0)
                K[k] = Polygon() if kk.is_empty or kk.area < 0.5 else kk
                changed = True
    return changed


def layers(man, wand=WAND, dach=DACH, bruecke=BRUECKE, step=STEP):
    """[(z_oben, Querschnitt C, Hohlraum K)] je Lage; bruecke=None schaltet das Gewölbe ab."""
    secs = sections(man, step)
    n = len(secs)
    E = []
    for z1, _ in secs:
        j = int(round((z1 + dach) / step)) - 1
        pj = secs[j][1] if j < n else Polygon()
        e = pj.buffer(-wand, join_style=2, mitre_limit=3.0).simplify(0.05) if not pj.is_empty else Polygon()
        E.append(Polygon() if e.is_empty or e.area < 0.5 else e)
    K = vault([c for _, c in secs], E, bruecke / 2, step) if bruecke else E
    return [(z1, c, k) for (z1, c), k in zip(secs, K)]


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


def hohl(solid, wand=WAND, dach=DACH, bruecke=BRUECKE, step=STEP):
    """(Schale als Manifold, Lagen). Ist kein Hohlraum möglich (zu dünn), kommt der Volumenkörper unverändert zurück."""
    lay = layers(solid, wand, dach, bruecke, step)
    cav = cavity(lay, step)
    return (solid - cav if cav is not None else solid), lay


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
