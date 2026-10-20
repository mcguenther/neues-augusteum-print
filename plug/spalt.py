"""Schmale Spalten und Splitter im fertigen Hohlkörper schließen (nachträglicher Schritt, Standard aus: `plug/buildings.py --spalt-min 0.4`).

Befund (Neues Augusteum, 20.10.2026, Schnittbild `vorschau/steckmodul_campus/gebaeude/02_neues_augusteum_schnitt.png`): Im Hohlraum bleiben
Teile übrig, die schmaler sind als eine Düsenbreite und die kein Slicer druckt oder zeigt:
  * senkrechte Schlitze von 0,1 mm Breite an der Innenseite einer Wand (Rand des Gewölbe-Höhenfelds: `hohl.vault_solid` setzt außerhalb des
    Hohlraums eine steile Rampe, die auf dem 0,2-mm-Netz in den Rand des Ziel-Hohlraums schneidet),
  * Splitter und Dreiecke von 0,2 mm Kantenlänge entlang der 45°-Flächen (Gewölbe gegen Lagen von 0,4 mm, `hohl.cavity`),
  * kleine Taschen an den Graten und Spitzen des Gewölbes und Keile zwischen Wand und Gewölbe.
`hohl.spalten` füllt je 0,4-mm-Lage nur Streifen unter `FUELLEN_T`, schneidet aber nur waagerecht und in der Lagenmitte; was zwischen den
Lagen liegt oder nur in der Höhe schmal ist, bleibt.

Verfahren (`schliessen`): Luft im Gebäude = Hülle (massiver Körper mit Fuß und Fuß-Fase) minus fertiger Körper. Je Achse (z, x, y) in dünnen
Schnitten das morphologische Öffnen der Luft mit dem Mindestmaß `mind` (Abtragen um `mind`/2 und wieder Aufweiten, Gehrung wie in
`hohl.spalten`: Ecken von 90° bleiben scharf); was dabei verschwindet, ist schmaler als `mind` und wird als Prisma Material. Das Öffnen
entfernt nie, was breiter als `mind` ist; das Gebäude behält Außenform, Wand und alle Räume. Was die Kassette braucht (`schutz`: Schacht
und Platz über dem Anschlag) bleibt frei. Der Schacht, der unten offen ist, wird nach unten verlängert, damit sein Rand nicht als Wand zählt.
"""
import manifold3d as m3d
import numpy as np
from shapely.geometry import MultiPolygon, Polygon

import hohl

MIND_T = 0.4           # Mindestbreite eines Hohlraumteils (Düsenbreite); schmalere werden gefüllt
STEP_Z = 0.1           # Abstand der waagerechten Schnitte (mm)
STEP_XY = 0.2          # Abstand der senkrechten Schnitte (mm); Teile, die nur in der Höhe schmal sind, sind in x und y lang
VEREINFACHEN = 0.002   # mm, Toleranz beim Vereinfachen von Körper plus Füllung (kleiner als hohl.VEREINFACHEN, damit die Füllung ihre Form behält)
MIN_FLAECHE = 0.004    # mm², kleinere Reste je Schnitt entfallen (Rundungsreste)
SCHWELLE_T = 0.01      # mm, Reste, die um weniger als dies abgetragen verschwinden (Breite unter 2 × SCHWELLE_T), sind Rundungsstufen und bleiben
MIN_TEIL_MM3 = 0.01    # mm³, kleinere Füllstücke entfallen (nicht druckbar, aber die meisten Berührkanten an den Rändern)
HAUT_T = 0.1           # mm, so nah an der Außenhaut des Körpers wird nichts gefüllt (die Hülle reicht dort teils über die Haut hinaus, z. B. Paulinum an der Nordwand: Füllung der Lücke wäre Außenform und gäbe Berührkanten)
RAND_T = 0.03          # mm, die Füllung greift so weit in das Material hinein, damit zwischen Füllung und Wand kein Haarspalt bleibt
NACH_UNTEN = 3.0       # mm, so weit wird der offene Schacht nach unten verlängert (nur für Schnitte in x und y)
ACHSEN = "z"           # Richtungen der Schnitte: "z" = nur waagerechte Schnitte (Standard), "zxy" zusätzlich senkrechte (findet auch Taschen, die nur in der Höhe schmal sind; deren Füllung kann aber große Flächen über Luft anlegen, Überhang)

# Achse -> (Drehung, die die Achse nach z bringt als Zeilen von 3×4) ; zyklische Vertauschung ist eine Drehung
_PERM = {"z": np.eye(3), "x": np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0]], float), "y": np.array([[0, 0, 1], [1, 0, 0], [0, 1, 0]], float)}


def _mat(R):
    return [[float(R[i, 0]), float(R[i, 1]), float(R[i, 2]), 0.0] for i in range(3)]


def _duenn(k, r, schwelle=SCHWELLE_T, inner=None):
    """Teile der Fläche k, die schmaler als 2r sind (Rest von k minus Öffnen), als Liste von Polygonen; Gehrung wie `hohl.spalten`."""
    if k.is_empty:
        return []
    o = k.buffer(-r, join_style=2).buffer(r, join_style=2)
    t = k.difference(o)
    if t.is_empty:
        return []
    t = t.buffer(-schwelle, join_style=2).buffer(schwelle + RAND_T, join_style=2).difference(o)    # Rundungsreste weg, in das Material hinein erweitert
    if inner is not None:
        t = t.intersection(inner)
    if t.is_empty:
        return []
    return [q for q in hohl._parts(t) if q.area > MIN_FLAECHE]


def luft_im_gebaeude(huelle, body, nach_unten=None, z_unten=None):
    """Luft zwischen Körper und Hülle. nach_unten: Grundriss des unten offenen Schachts (shapely), wird um NACH_UNTEN verlängert."""
    luft = huelle - body
    if nach_unten is not None and not nach_unten.is_empty:
        luft = luft + hohl.prism(nach_unten, z_unten - NACH_UNTEN, z_unten + 0.06)
    return luft


def _umriss(m, z):
    """Umriss des Körpers m in der Höhe z mit gefüllten Löchern (shapely)."""
    import shapely
    g = hohl._cs_poly(m.slice(z))
    return shapely.union_all([Polygon(p.exterior) for p in hohl._parts(g) if not p.is_empty]) if not g.is_empty else Polygon()


def duenne_teile(luft, mind=MIND_T, step_z=STEP_Z, step_xy=STEP_XY, schwelle=SCHWELLE_T, achsen=ACHSEN, haut=None):
    """Die Teile der Luft, die schmaler als `mind` sind, als Manifold (None, wenn es keine gibt)."""
    r = mind / 2
    parts = []
    for ax, step in (("z", step_z), ("x", step_xy), ("y", step_xy)):
        if ax not in achsen:
            continue
        R = _PERM[ax]
        L = luft if ax == "z" else luft.transform(_mat(R))
        H = None if haut is None else (haut if ax == "z" else haut.transform(_mat(R)))
        bb = L.bounding_box()
        z = bb[2] + step / 2
        mine = []
        while z < bb[5]:
            inner = None
            if H is not None:      # nur innerhalb der Umrisse des Körpers (Löcher gefüllt) mit HAUT_T Abstand, auch nach oben und unten (flache Dächer)
                inner = _umriss(H, z)
                for dz in (-HAUT_T, HAUT_T):
                    inner = inner.intersection(_umriss(H, z + dz))
                inner = inner.buffer(-HAUT_T, join_style=2)
            for q in _duenn(hohl._cs_poly(L.slice(z)), r, schwelle, inner):
                mine.append(hohl.prism(q, z - step / 2 - 0.001, z + step / 2 + 0.001))
            z += step
        if mine:
            u = m3d.Manifold.batch_boolean(mine, m3d.OpType.Add)
            parts.append(u if ax == "z" else u.transform(_mat(R.T)))
    return m3d.Manifold.batch_boolean(parts, m3d.OpType.Add) if parts else None


def fuellung(body, huelle, schutz=None, nach_unten=None, z_unten=None, mind=MIND_T, achsen=ACHSEN):
    """(Liste der Füllstücke als Manifolds oder None, Werte). body: fertiger Körper (unvereinfacht, damit die Haut nicht als Luft zählt), huelle: massiver
    Körper ohne Hohlraum und ohne Schacht (mit Fuß und Fase), schutz: Manifold, das frei bleiben muss (Schacht, Platz für die Kassette),
    nach_unten/z_unten: Grundriss des unten offenen Schachts (nur für achsen mit x oder y). Der Körper wird danach mit
    `(body.simplify(..) + fuell).simplify(VEREINFACHEN)` zusammengesetzt (`plug/buildings.py`): Würde man die Füllung vor dem Vereinfachen
    zufügen, fielen Haarspalte unter der Vereinfachungstoleranz zu Berührkanten zusammen (17 statt 1 bei `sauber`)."""
    luft = luft_im_gebaeude(huelle, body, nach_unten if achsen != "z" else None, z_unten)
    fuell = duenne_teile(luft, mind, achsen=achsen, haut=body)
    info = dict(mind=mind, gefuellt_mm3=0.0)
    if fuell is None:
        return None, info
    fuell = fuell ^ huelle                                    # nie über die Hülle hinaus (Außenform bleibt)
    if schutz is not None:
        fuell = fuell - schutz
    teile = [t for t in fuell.decompose() if t.volume() >= MIN_TEIL_MM3]
    info["teile"] = len(teile)
    if not teile:
        return None, info
    info["gefuellt_mm3"] = round((m3d.Manifold.batch_boolean(teile, m3d.OpType.Add) ^ luft).volume(), 2)   # Luft, die zu Material wird (ohne das Stück, das in die Wand greift)
    return teile, info


def einsetzen(body, teile, ids=False):
    """Körper (schon vereinfacht) plus Füllstücke, danach mit VEREINFACHEN vereinfacht. ids: die Füllung trägt face_id 0 (keine Farbe)."""
    if not teile:
        return body
    f = m3d.Manifold.batch_boolean(teile, m3d.OpType.Add)
    if ids:
        f = ohne_ids(f)
    return (body + f).simplify(VEREINFACHEN)


def ohne_stuecke_bei(teile, orte, rand=0.1):
    """Füllstücke ohne die, deren Umkasten (um `rand` erweitert) einen der Orte enthält (Berührkanten im fertigen Netz)."""
    orte = np.asarray(orte, float).reshape(-1, 3)
    keep = []
    for t in teile:
        b = t.bounding_box()
        im = np.all((orte >= np.array(b[:3]) - rand) & (orte <= np.array(b[3:]) + rand), axis=1)
        if not im.any():
            keep.append(t)
    return keep


def ohne_ids(m):
    """Manifold mit face_id 0 für alle Dreiecke (Füllung trägt keine Farbe, siehe `plug/buildings.py` farb_ids)."""
    mm = m.to_mesh()
    return m3d.Manifold(m3d.Mesh(vert_properties=np.array(np.asarray(mm.vert_properties)[:, :3], np.float32, order="C"),
                                 tri_verts=np.array(mm.tri_verts, np.uint32, order="C"),
                                 face_id=np.zeros(len(mm.tri_verts), np.uint32)))
