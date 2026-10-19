"""Unterkasten Stand 8 (Plan, noch keine STL): Kasten höher, Knopfraum mit Erhebung und Kordelgänge für den Doktorhut, ohne Eckaussparungen.

Der Hut trägt in der Mitte seines Deckbretts einen Knopf (`HUT_KNOPF`, Ø 22 × 12,0; die Höhe ist eine Annahme, vom Nutzer zu bestätigen) mit
der Kordel der Quaste. Die Grundplatte liegt mittig auf dem Hut, also hat der Unterkasten in der Plattenmitte unten einen Knopfraum (mindestens
Ø 25 × 12,2), und die Kordel läuft in acht Gängen (`KORDEL_GANG`, freies Rechteck 8 × 5, darüber 45°-Dachschrägen 1,5, Höcker 11,4 breit)
unter dem Kasten zur Außenwand. Am Rand haben die Gänge Gang-Höhe; `KNOPF_RAMPE["vor"]` mm vor dem Knopfkörper beginnt ein 45°-Kegel, der
auf die Knopfhöhe steigt und mit einer flachen Decke Ø 20 schließt. Darüber sitzt die Erhebung (Plateau `KNOPF_PLATEAU_D`), von oben sichtbar.

Nutzer 19.10.: Steckerraum über der Powerbank 6 mm (viele Leitungen). Die Powerbank bleibt, wo sie im Stand 7 liegt (quer passt sie wegen des
Steckers nicht), also über dem Knopf. Sie liegt auf dem Plateau der Erhebung und auf Auflagen gleicher Höhe in den Ecken ihrer Fläche
(`PB_AUFLAGE`), sonst kippt sie: ihr Schwerpunkt liegt etwa 31 mm neben der Knopfmitte. Befestigung mit Heißkleber (Kasten auf den Hut,
im Zweifel Platte auf den Kasten): die Eckaussparungen für die Fäden entfallen.

Geometrie in Plattenkoordinaten (x Osten, y Norden, Ursprung Südwestecke), z = 0 an der Unterkante des Kastens. Werte in `params.py`.
Aufruf zum Prüfen: `python3 -m plug.power.kasten8` (ca. 20 s) druckt die Prüfzeilen.
"""
import math
import os
import sys

import numpy as np
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import generate as G  # noqa: E402
from plug.geom import box as mbox  # noqa: E402
from plug.geom import prism_y  # noqa: E402
import manifold3d as m3d  # noqa: E402
from plug.power import build_concept as BC  # noqa: E402
from plug.power import params as PP  # noqa: E402

H7 = round(BC.H0["uk_t"], 2)                         # 17,6
PB_T = PP.PB_T + PP.PB_T_ZUSCHLAG                    # 12,8
DACH = PP.KORDEL_DACH
KN = PP.HUT_KNOPF
R_KN = KN["d"] / 2                                   # Knopfkörper Radius 11
GANG_W, GANG_H, FASE = PP.KORDEL_GANG["w"], PP.KORDEL_GANG["h"], PP.KORDEL_GANG["fase"]
MODI = ("innen", "aussen")
MODUS = WAND = GANG_Z = None


def modus(m):
    """Gangfase umschalten: "innen" (Fase in den oberen Ecken des Rechtecks, Höcker 10,4 × 6,2) oder "aussen" (Rechteck 8 × 5 frei,
    Dachschrägen darüber, Höcker 11,4 × 7,7). Setzt MODUS, WAND, GANG_Z dieses Moduls."""
    global MODUS, WAND, GANG_Z
    assert m in MODI, m
    MODUS = m
    WAND = PP.KORDEL_WAND if m == "aussen" else DACH                 # seitlich am Gang 1,7 bzw. 1,2
    GANG_Z = GANG_H + (FASE if m == "aussen" else 0.0) + DACH        # Oberkante der Höcker 7,7 bzw. 6,2
    return m


modus(PP.GANG_FASE_MODUS)
if PP.KORDEL_ANSATZ_OBEN:                            # Kordel oben auf dem Knopf: darüber und am Rand hinunter Platz für sie
    R_RAUM = max(KN["r"], round(math.hypot(R_KN + PP.KORDEL["h"], PP.KORDEL["b"] / 2) + KN["luft"], 1))   # 14,4
    H_RAUM = KN["h"] + PP.KORDEL["h"] + KN["luft"]
else:                                                # Kordel verlässt den Knopf am Fuß (Hut-Höhe 0 bis 3)
    R_RAUM, H_RAUM = KN["r"], KN["h"] + KN["luft"]   # 12,5 und 12,2
R_KNOPF = R_RAUM                                     # Name wie bisher: Radius des Knopfraums
R_RAMPE = R_KN + PP.KNOPF_RAMPE["vor"]               # Beginn des Anstiegs (Gang-Höhe) 19,7
R_DECKE = PP.KNOPF_RAMPE["decke_d"] / 2              # flache Decke über dem Knopf Radius 10
R_PLATEAU = PP.KNOPF_PLATEAU_D / 2                   # Oberseite der Erhebung Radius 14


def knopf_profil(z0=-1.0):
    """Querschnitt (r, z) des Hohlraums unter der Erhebung: bis R_RAMPE Gang-Höhe, dann 45° nach innen; erreicht der Kegel den Raum Ø 2·R_RAUM
    unter H_RAUM, geht es dort senkrecht weiter; oben wieder 45° bis zur flachen Decke Radius R_DECKE."""
    z1 = GANG_H + (R_RAMPE - R_RAUM)                 # Höhe des Kegels am Raumrand
    pts = [(0.0, z0), (R_RAMPE, z0), (R_RAMPE, GANG_H)]
    if z1 >= H_RAUM:
        top = GANG_H + R_RAMPE - R_DECKE
    else:
        pts += [(R_RAUM, z1), (R_RAUM, H_RAUM)]
        top = H_RAUM + R_RAUM - R_DECKE
    return pts + [(R_DECKE, top), (0.0, top)], top


KNOPF_TOP = knopf_profil()[1]                        # Decke über dem Knopf 14,7
KNOPF_Z = KNOPF_TOP + DACH                           # Plateau der Erhebung 15,9
KNOPF_H = H_RAUM                                     # Höhe des Raums Ø 25 (12,2)
KNOPF_H0 = H_RAUM                                    # (alter Name) senkrechter Teil des Raums
H8 = round(KNOPF_Z + PB_T + PP.STECKERRAUM_8, 2)     # Powerbank auf dem Plateau, darüber 6,0: 34,7
RICHTUNG = ("O", "NO", "N", "NW", "W", "SW", "S", "SO")   # k · 45°, 0° = Osten
TP_CLR = 0.10                                        # Spiel der Mulden um die Gebäude (Sperrfläche für Zapfen)


def kordel(W, L):
    """Mitte, Knopfraum, Gänge (frei) und Höcker (Wand plus Decke) als Polygone, dazu die Austrittspunkte an der Außenwand."""
    c = (W / 2, L / 2)
    outline = box(0, 0, W, L)
    inner = outline.buffer(-PP.UK_WALL, join_style=2)
    frei = Point(c).buffer(R_RAMPE, 96)                       # Hohlraum am Bett (Gang-Höhe bis zum Beginn des Anstiegs)
    kuppel = Point(c).buffer(R_RAMPE + WAND, 96)              # Fuß der Erhebung
    gaenge, hoecker, aus = [], [], []
    hw = PP.KORDEL_GANG["w"] / 2
    for k in range(PP.KORDEL_GANG["n"]):
        a = math.radians(k * 360.0 / PP.KORDEL_GANG["n"])
        d = (math.cos(a), math.sin(a))
        ln = LineString([c, (c[0] + 400 * d[0], c[1] + 400 * d[1])])
        gaenge.append(ln.buffer(hw, cap_style=2).intersection(outline.buffer(3, join_style=2)))
        hoecker.append(ln.buffer(hw + WAND, cap_style=2).intersection(inner))
        p = ln.intersection(outline.exterior)
        p = p if p.geom_type == "Point" else list(p.geoms)[0]
        aus.append(dict(r=RICHTUNG[k], ang=k * 45, x=round(p.x, 1), y=round(p.y, 1),
                        len=round(math.hypot(p.x - c[0], p.y - c[1]) - R_KN, 1),
                        wand=round(PP.KORDEL_GANG["w"] / (abs(d[0]) if min(p.x, W - p.x) < 1e-6 else abs(d[1])), 1)))
    return dict(c=c, frei=frei, kuppel=kuppel.intersection(inner), gaenge=gaenge, hoecker=hoecker, aus=aus)


def gang_profil(w, h, fase, z0=-1.0, m=None):
    """Querschnitt eines Gangs in (y, z). Modus "aussen": freies Rechteck w × h, darüber 45°-Dachschrägen fase (Decke w − 2·fase breit bei
    h + fase), die Fase verkleinert den Gang nicht. Modus "innen": Rechteck w × h mit gefasten oberen Ecken (Decke w − 2·fase breit bei h).
    fase = 0: nur das Rechteck."""
    hw = w / 2
    m = MODUS if m is None else m
    if fase <= 0:
        return [(-hw, z0), (hw, z0), (hw, h), (-hw, h)]
    if m == "innen":
        return [(-hw, z0), (hw, z0), (hw, h - fase), (hw - fase, h), (-hw + fase, h), (-hw, h - fase)]
    return [(-hw, z0), (hw, z0), (hw, h), (hw - fase, h + fase), (-hw + fase, h + fase), (-hw, h)]


def gaenge_cut(c, w, h, fase, n, z0=-1.0, laenge=200.0, r0=0.0):
    """Schnittkörper aller Gänge: je ein Prisma von r0 nach außen, in 45°-Schritten gedreht."""
    one = prism_y_x(gang_profil(w, h, fase, z0), r0, laenge)
    return G.union([one.rotate([0, 0, k * 360.0 / n]).translate([c[0], c[1], 0]) for k in range(n)])


def prism_y_x(pts, x0, x1):
    """Profil in (y, z), entlang x extrudiert (wie plug.geom.prism_x, aber mit Rückgabe im Ursprung)."""
    from plug.geom import prism_x
    return prism_x(pts, x0, x1)


def revolve(pts, c, n=128):
    from shapely.geometry.polygon import orient
    ring = list(orient(Polygon(pts), 1.0).exterior.coords)[:-1]
    return m3d.Manifold.revolve(m3d.CrossSection([ring]), n).translate([c[0], c[1], 0])


def knopf_cut(c, z0=-1.0):
    """Hohlraum unter der Erhebung (Knopfraum, 45°-Anstieg, flache Decke) als Drehkörper um c."""
    return revolve(knopf_profil(z0)[0], c)


def erhebung_solid(c, z0):
    """Volle Erhebung von z0 bis KNOPF_Z: Hohlraumprofil um DACH (45°-Teile senkrecht gemessen) aufgedickt, unten die Gangwand WAND,
    oben das Plateau Radius R_PLATEAU mit senkrechtem Rand. Außen nirgends überhängend (Radius nimmt nach oben nur ab)."""
    prof = Polygon(knopf_profil(z0)[0])
    outer = unary_union([prof.buffer(DACH, join_style=2, mitre_limit=3.0), box(0, z0, R_RAMPE + WAND, GANG_H), box(0, z0, R_PLATEAU, KNOPF_Z)])
    outer = outer.intersection(box(0, z0, 200, KNOPF_Z))
    return revolve(list(outer.exterior.coords)[:-1], c)


def ueberhang(uk, zmax=8.0, dz=0.2, detail=None):
    """Überhang je 0,2-mm-Lage bis zmax: Fläche, die nicht von der Lage darunter (um dz nach außen = 45°) getragen wird.
    Rückgabe: größte freie Breite (mm, Brücke) und größte Fläche (mm²) mit der Höhe z. detail (Liste): bekommt je freie Fläche
    (z, Breite, Fläche, x, y) für die Zuordnung zu Bereichen."""
    from shapely.geometry import Polygon as SP

    def cs(z):
        rings = [SP(r) for r in uk.slice(z).to_polygons() if len(r) > 2]
        out = None
        for r in rings:
            out = r.buffer(0) if out is None else out.symmetric_difference(r.buffer(0))
        return out

    worst_w, worst_a, worst_z = 0.0, 0.0, 0.0
    prev = cs(dz / 2)
    z = dz / 2 + dz
    while z < zmax:
        cur = cs(z)
        if cur is not None and prev is not None:
            un = cur.difference(prev.buffer(dz + 0.02))
            parts = [un] if un.geom_type == "Polygon" else list(getattr(un, "geoms", []))
            for q in parts:
                if q.area < 0.3:
                    continue
                w, d = 0.0, 0.1
                while not q.buffer(-d).is_empty and d < 40:
                    w = 2 * d
                    d += 0.1
                if w > worst_w:
                    worst_w = w
                if detail is not None:
                    detail.append((round(z, 2), round(w, 1), round(q.area, 1), round(q.centroid.x, 2), round(q.centroid.y, 2)))
                if q.area > worst_a:
                    worst_a, worst_z = q.area, z
        prev = cur
        z += dz
    return round(worst_w, 1), round(worst_a, 1), round(worst_z, 1)


def auflagen(body, hoeck_all, K):
    """Auflagen der Powerbank auf Plateauhöhe: je Ecke ihrer Fläche ein Stück bis a × a, frei von Höckern (Abstand) und Erhebung."""
    A = PP.PB_AUFLAGE
    if not A["on"]:
        return []
    fl = body.buffer(-(PP.PB_CLR + 1.0), join_style=2)
    free = fl.difference(hoeck_all.buffer(A["abstand"])).difference(K["kuppel"].buffer(A["abstand"]))
    b = fl.bounds
    out = []
    for x0, x1 in ((b[0], b[0] + A["a"]), (b[2] - A["a"], b[2])):
        for y0, y1 in ((b[1], b[1] + A["a"]), (b[3] - A["a"], b[3])):
            q = free.intersection(box(x0, y0, x1, y1))
            parts = [g for g in getattr(q, "geoms", [q]) if g.geom_type == "Polygon" and g.area > 30.0]
            if parts:
                out.append(max(parts, key=lambda g: g.area).buffer(0))
    return out


def standfest(body, tragen, z_top, h_hoecker):
    """Standfestigkeit der Powerbank: Abstand des Schwerpunkts (Mitte ihrer Fläche) zum Rand der Stützfläche (konvexe Hülle aller Auflagen;
    negativ = außerhalb, sie kippt), dazu der Kippwinkel um den nächsten Rand, bis ein Ende auf einem Höcker liegt oder die Platte berührt."""
    from shapely.geometry import MultiPolygon
    hull = unary_union(tragen).convex_hull
    s = body.centroid
    d = hull.exterior.distance(s) * (1 if hull.contains(s) else -1)
    if d >= 0:
        return dict(rand=round(d, 1), kipp=0.0)
    # Kippachse: Tangente am Rand der Hülle quer zur Richtung zum Schwerpunkt
    p = hull.exterior.interpolate(hull.exterior.project(s))
    ux, uy = (s.x - p.x), (s.y - p.y)
    n = math.hypot(ux, uy)
    ux, uy = ux / n, uy / n
    proj = [(x - p.x) * ux + (y - p.y) * uy for x, y in body.exterior.coords]
    vor, hinter = max(proj), -min(proj)                  # Hebel zum fallenden und zum steigenden Ende
    a_fall = math.degrees(math.asin(min(1.0, (z_top - h_hoecker) / vor)))
    a_stieg = math.degrees(math.asin(min(1.0, PP.STECKERRAUM_8 / hinter))) if hinter > 0 else 90.0
    return dict(rand=round(d, 1), kipp=round(min(a_fall, a_stieg), 1), vor=round(vor, 1), hinter=round(hinter, 1))


def build(v):
    """Unterkasten Stand 8 als Manifold (z = 0 unten) und alles, was die Seite und die Prüfung brauchen."""
    W, L = v["plate"]
    H = H8
    outline = box(0, 0, W, L)
    inner = outline.buffer(-PP.UK_WALL, join_style=2)
    K = kordel(W, L)
    body, plug, win = Polygon(v["body"][0]), Polygon(v["plug"][0]), Polygon(v["window"][0])
    elec = Polygon(v["elec"][0])
    zones = [Polygon(d["zone"]) for d in v["docks"] if d["ok"]]
    gang_all, hoeck_all = unary_union(K["gaenge"]), unary_union(K["hoecker"])
    unter_pb = [K["aus"][i]["r"] for i, h in enumerate(K["hoecker"]) if h.intersects(body)]
    plateau = Point(K["c"]).buffer(R_PLATEAU, 96)
    auf = auflagen(body, hoeck_all, K) if body.intersects(plateau) else []
    z_pb = KNOPF_Z if body.intersects(plateau) else (GANG_Z if unter_pb else PP.UK_FLOOR)

    # Stützen im 40-mm-Raster wie Stand 7, frei von Knopfraum, Gängen, Powerbank, Elektronik und Docks (keine Eckaussparungen mehr)
    block = [body.buffer(3), plug.buffer(3), elec.buffer(3), K["kuppel"].buffer(3), hoeck_all.buffer(1.5)] + [z.buffer(3) for z in zones]
    free = inner.buffer(-PP.POST[0]).difference(unary_union(block))
    posts = []
    for x in np.arange(PP.POST[1] / 2, W, PP.POST[1]):
        for y in np.arange(PP.POST[1] / 2, L, PP.POST[1]):
            r = box(x - PP.POST[0] / 2, y - PP.POST[0] / 2, x + PP.POST[0] / 2, y + PP.POST[0] / 2)
            if free.contains(r):
                posts.append(r)
    old_pins = [Polygon(p["r"]).centroid for p in v["posts"] if p["pin"]]
    no_pin = unary_union([Polygon(r) for b in v["buildings"] for r in b["poly"]] + [Polygon(r) for r in v["hof"]]).buffer(TP_CLR + PP.PIN_PLAN["d"] / 2 + 1.5)
    pins, pin_rows = [], []
    for t in old_pins:
        cand = sorted((r.centroid.distance(t), i) for i, r in enumerate(posts) if i not in pins and not r.centroid.within(no_pin))
        if cand:
            i = cand[0][1]
            pins.append(i)
            pin_rows.append(dict(alt=[round(t.x, 1), round(t.y, 1)], neu=[round(posts[i].centroid.x, 1), round(posts[i].centroid.y, 1)], weg=round(cand[0][0], 1)))

    # Körper
    solids = [BC.slab_ch(outline, 0, H, PP.CH_BED) - G.extrude(inner, PP.UK_FLOOR, H + 1)]
    solids.append(erhebung_solid(K["c"], PP.UK_FLOOR - 0.01))
    solids.append(G.extrude(hoeck_all, PP.UK_FLOOR - 0.01, GANG_Z))
    solids += [G.extrude(r, PP.UK_FLOOR - 0.01, z_pb) for r in auf]
    solids += [G.extrude(r, PP.UK_FLOOR - 0.01, H) for r in posts]
    solids += [BC.pin_solid_at(posts[i].centroid, H, PP.PIN_PLAN, PP.CH_PIN) for i in pins]
    unten = unary_union([K["frei"], gang_all])
    gc = gaenge_cut(K["c"], GANG_W, GANG_H, FASE, PP.KORDEL_GANG["n"])
    kc = knopf_cut(K["c"])
    holes = [kc, gc, BC.mouth_ch(unten, 0, PP.CH_BED)]
    holes.append(G.extrude(win, z_pb, H + 2))
    sw = BC.switch_cut(0, 0, 0, dict(uk_t=H))
    holes.append(sw["cut"])
    uk = G.union(solids) - G.union(holes)

    # Teile, die im Kasten liegen (für Prüfung und Ansicht)
    b = body.bounds
    pbm = mbox(b[0] + PP.PB_CLR, b[2] - PP.PB_CLR, b[1] + PP.PB_CLR, b[3] - PP.PB_CLR, z_pb + 0.01, z_pb + PB_T)
    eb = elec.bounds
    ecx, ecy = (eb[0] + eb[2]) / 2, (eb[1] + eb[3]) / 2
    bw, bh = PP.ESP_BOARD if eb[2] - eb[0] >= eb[3] - eb[1] else PP.ESP_BOARD[::-1]
    esp_fp = box(ecx - bw / 2 - PP.ESP_TAPE, ecy - bh / 2 - PP.ESP_TAPE, ecx + bw / 2 + PP.ESP_TAPE, ecy + bh / 2 + PP.ESP_TAPE)
    esp_z0 = KNOPF_Z if esp_fp.intersects(plateau) else (GANG_Z if esp_fp.intersects(hoeck_all) else PP.UK_FLOOR)
    espm = mbox(*esp_fp.bounds[0::2], *esp_fp.bounds[1::2], esp_z0 + 0.01, esp_z0 + PP.ESP_H + 2 * PP.ESP_TAPE)
    pc = plug.bounds
    zm = z_pb + PB_T / 2
    plugm = mbox(pc[0] + 0.3, pc[2] - 0.3, pc[1] + 0.3, pc[3] - 0.3, zm - 4.0, zm + 4.0)
    c3 = [K["c"][0], K["c"][1], 0.0]
    raum_m = m3d.Manifold.cylinder(H_RAUM - 0.03, R_RAUM - 0.02, R_RAUM - 0.02, 96).translate([c3[0], c3[1], 0.01])
    knopf_m = m3d.Manifold.cylinder(KN["h"], R_KN, R_KN, 64).translate(c3)
    reach = min(W, L) / 2 - PP.UK_WALL - 0.02
    gang_m = gaenge_cut(K["c"], GANG_W - 0.04, GANG_H - 0.02, 0.0, PP.KORDEL_GANG["n"], z0=0.01, laenge=reach)      # volles Rechteck
    gangf_m = gaenge_cut(K["c"], GANG_W - 0.04, GANG_H - 0.02, FASE - 0.02, PP.KORDEL_GANG["n"], z0=0.01, laenge=reach)  # Profil mit Fase
    kb, kh = PP.KORDEL["b"], PP.KORDEL["h"]

    def kord(z0, z1, r0, r1):
        return G.union([prism_y_x([(-kb / 2, z0), (kb / 2, z0), (kb / 2, z1), (-kb / 2, z1)], r0, r1).rotate([0, 0, k * 45.0]).translate(c3) for k in range(8)])
    kord_m = kord(0.05, kh, R_KN, reach)                 # auf dem Hut vom Knopfrand bis zur Außenwand
    if PP.KORDEL_ANSATZ_OBEN:                            # oben auf dem Knopf, am Rand hinunter (Ring R_KN bis R_KN + kh), dann auf dem Hut
        kord_kn = G.union([kord(KN["h"], KN["h"] + kh, 0.0, R_KN), kord(0.05, KN["h"] + kh, R_KN, R_KN + kh)])
        ansatz = "oben auf dem Knopf (z %.1f bis %.1f) und am Rand hinunter" % (KN["h"], KN["h"] + kh)
    else:
        kord_kn = kord(0.05, kh, R_KN, R_RAMPE + 2.0)
        ansatz = "am Fuß des Knopfs (Hut-Höhe 0 bis %.1f) durch Raum und Anstieg" % kh
    pb_luft = z_pb - KNOPF_Z                         # Luft zwischen Plateau und Powerbank

    def iv(a):
        return round(float((a ^ uk).volume()), 2)

    tm = G.to_trimesh(uk)
    pb_top = z_pb + PB_T
    esp_top = esp_z0 + PP.ESP_H + 2 * PP.ESP_TAPE
    lie = len(unter_pb)
    det = []
    ow, oa, oz = ueberhang(uk, zmax=KNOPF_Z + 0.5, detail=det)
    br = brueckenbereiche(det, K["c"])
    tragen = [body.intersection(plateau)] + auf
    sf = standfest(Polygon(body.buffer(-PP.PB_CLR, join_style=2)), tragen, z_pb, GANG_Z)
    sf0 = standfest(Polygon(body.buffer(-PP.PB_CLR, join_style=2)), [body.intersection(plateau)], z_pb, GANG_Z)
    checks = [
        ("dicht", bool(tm.is_watertight), "Netz geschlossen (Manifold), %d Körper" % len(uk.decompose())),
        ("Überhang ohne Support", ow <= 20.0, "je 0,2-mm-Lage bis %.1f mm Höhe, Wände bis 45° getragen: breiteste freie Decke %.1f mm (gefordert höchstens 20); %s" % (
            KNOPF_Z + 0.5, ow, "; ".join("%s %.1f mm bei z %.1f" % (n, w, z) for n, w, z in br))),
        ("Knopfraum frei", iv(raum_m) < 0.05, "Ø %.0f × %.1f (Knopf Ø %.0f × %.1f plus %.1f seitlich, %.1f oben), gegen Kasten: %.2f mm³" % (
            2 * R_RAUM, H_RAUM, KN["d"], KN["h"], R_RAUM - R_KN, H_RAUM - KN["h"], iv(raum_m))),
        ("Knopf im Raum", iv(knopf_m) < 0.05, "Knopf Ø %.0f × %.1f (Höhe Annahme): Überschneidung %.2f mm³" % (KN["d"], KN["h"], iv(knopf_m))),
        ("Anstieg und Decke", KNOPF_TOP >= H_RAUM, "45°-Kegel ab Radius %.1f (%.1f mm vor dem Knopfkörper) auf Gang-Höhe %.1f, flache Decke Ø %.0f bei z %.1f, Plateau Ø %.0f bei z %.1f, Wand %.1f" % (
            R_RAMPE, R_RAMPE - R_KN, GANG_H, 2 * R_DECKE, KNOPF_TOP, 2 * R_PLATEAU, KNOPF_Z, DACH)),
        (("Gänge frei (Rechteck)" if MODUS == "aussen" else "Gänge frei (Profil mit Fase)"),
         iv(gang_m if MODUS == "aussen" else gangf_m) < 0.05,
         ("%d Gänge, freies Rechteck %.0f × %.0f (ohne Fase) bis zur Außenwand, gegen Kasten: %.2f mm³; Dachschrägen %.1f × 45° darüber, Decke %.0f breit bei z %.1f" % (
             PP.KORDEL_GANG["n"], GANG_W, GANG_H, iv(gang_m), FASE, GANG_W - 2 * FASE, GANG_H + FASE)) if MODUS == "aussen" else
         ("%d Gänge %.0f × %.0f mit Fase %.1f in den oberen Ecken, gegen Kasten: %.2f mm³; das volle Rechteck ist nicht frei (Ecken %.2f mm³), die Kordel passt" % (
             PP.KORDEL_GANG["n"], GANG_W, GANG_H, FASE, iv(gangf_m), iv(gang_m)))),
        ("Wände an den Gängen", DACH >= 1.2 - 1e-6 and (WAND - PP.CH_BED >= 1.2 - 1e-6 or PP.UK_FLOOR >= 1.2), "seitlich %.1f (an der Bettkante %.1f%s), Decke %.1f, Höcker %.1f breit und %.1f hoch (Modus %s)" % (
            WAND, WAND - PP.CH_BED, "" if WAND - PP.CH_BED >= 1.2 - 1e-6 else "; im Kasten liegt dort der Boden %.1f an, im Probeteil ohne Boden bleiben %.1f" % (PP.UK_FLOOR, WAND - PP.CH_BED),
            DACH, GANG_W + 2 * WAND, GANG_Z, MODUS)),
        ("Kordel vom Knopf", iv(kord_kn) < 0.05, "Kordel %.0f × %.0f %s in alle acht Richtungen: Überschneidung %.2f mm³ (%s)" % (
            kb, kh, ansatz, iv(kord_kn), "Nutzer: Kordel kommt unten seitlich am Knopffuß heraus" if not PP.KORDEL_ANSATZ_OBEN else "KORDEL_ANSATZ_OBEN = True")),
        ("Kordel in allen Gängen", iv(kord_m) < 0.05, "Kordel %.0f × %.0f in jeder der 8 Richtungen vom Knopfrand bis zur Außenwand: Überschneidung %.2f mm³" % (kb, kh, iv(kord_m))),
        ("Powerbank frei", iv(pbm) == 0, "liegt auf z = %.1f (Plateau Ø %.0f und %d Auflagen), Überschneidung %.2f mm³" % (z_pb, 2 * R_PLATEAU, len(auf), iv(pbm))),
        ("Powerbank steht", sf["rand"] > 3.0, "Schwerpunkt %.1f mm innerhalb der Stützfläche (Plateau und Auflagen); nur auf dem Plateau: %.1f mm außerhalb, kippt um %.0f°" % (
            sf["rand"], -sf0["rand"], sf0["kipp"])),
        ("Steckerraum über der Powerbank", H - pb_top >= PP.STECKERRAUM_8 - 0.01, "%.1f mm (gefordert %.1f)" % (H - pb_top, PP.STECKERRAUM_8)),
        ("Kordel im Gang", PP.KORDEL["h"] < GANG_H and PP.KORDEL["b"] < GANG_W, "Kordel %.0f × %.0f in Gang %.0f × %.0f (breit × hoch): Spiel %.1f hoch, %.1f seitlich" % (PP.KORDEL["b"], PP.KORDEL["h"], GANG_W, GANG_H, GANG_H - PP.KORDEL["h"], GANG_W - PP.KORDEL["b"])),
        ("Stecker USB-A frei", iv(plugm) == 0, "Steckerraum %.1f mm lang wie Stand 7, Überschneidung %.2f mm³" % (pc[3] - pc[1], iv(plugm))),
        ("ESP32 frei", iv(espm) == 0, "liegt auf z = %.1f (%s), Überschneidung %.2f mm³" % (esp_z0, "auf Gangdach" if esp_z0 == GANG_Z else ("auf dem Plateau" if esp_z0 == KNOPF_Z else "auf dem Boden"), iv(espm))),
        ("Adern über dem ESP32", H - esp_top >= PP.ADERN_ZONE - 0.01, "%.1f mm unter der Platte (gefordert %.1f)" % (H - esp_top, PP.ADERN_ZONE)),
        ("Schalterraum frei", iv(sw["room"]) < 0.05, "Mitte %.1f über dem Boden, Überschneidung %.2f mm³" % (sw["z"], iv(sw["room"]))),
        ("Fenster der Powerbank", True, "Nordwand wie Stand 7, offen ab z = %.1f bis oben" % z_pb),
    ]
    return dict(H=H, plus=round(H - H7, 1), total=round(H + BC.H0["plate_t"], 1), uk=uk, grams=BC.grams(uk), checks=checks,
                body=body, plug=plug, win=win, z_pb=z_pb, unter_pb=unter_pb, pb_luft=round(pb_luft, 1), pb_m=pbm, esp_m=espm, esp_z0=esp_z0,
                plug_m=plugm, posts=posts, pins=pins, pin_rows=pin_rows, K=K, sw=sw, pb_top=round(pb_top, 1), esp_top=round(esp_top, 1), elec=elec,
                auflagen=auf, standfest=sf, standfest0=sf0, bruecken=br, ueberhang=(ow, oa, oz), zeit=zeiten(BC.grams(uk)[0], H), modus=MODUS, gang_z=GANG_Z, wand=WAND)


def brueckenbereiche(det, c):
    """Größte freie Breite je Bereich aus ueberhang(detail): Decke über dem Knopf (Mitte), Gangdecken (um z 6,5), sonst."""
    best = {}
    for z, w, a, x, y in det:
        r = math.hypot(x - c[0], y - c[1])
        if r < R_RAUM and z > H_RAUM:
            n = "Decke über dem Knopf"
        elif abs(z - (GANG_H + (FASE if MODUS == "aussen" else 0.0))) < 0.35:
            n = "Gangdecken"
        elif r < R_RAMPE + 2 and z > GANG_H:
            n = "Anstieg"
        else:
            n = "sonst"
        if w > best.get(n, (0, 0))[0]:
            best[n] = (w, z)
    return [(n, w, z) for n, (w, z) in sorted(best.items(), key=lambda t: -t[1][0])]


def zeiten(g, h):
    """Druckzeit in Stunden: Modell normal/schnell aus plug/roadmap und Erfahrung Nacht 1 (47 g in 2,5 h)."""
    from plug.roadmap import build as rb
    n = h / 0.2
    out = {k: round((g / p["rate"] * 60.0 + n * p["layer"] / 60.0 + p["start"]) / 60.0, 1) for k, p in rb.PROFILE.items()}
    out["nacht1"] = round(g / 47.0 * 2.5, 1)
    return out


def plateau_z(vor=None, decke_d=None, oben=None):
    """Plateauhöhe der Erhebung für andere Werte (Rampenstart, Decke, Kordelansatz); gleiche Regeln wie knopf_profil."""
    vor = PP.KNOPF_RAMPE["vor"] if vor is None else vor
    rd = (PP.KNOPF_RAMPE["decke_d"] if decke_d is None else decke_d) / 2
    oben = PP.KORDEL_ANSATZ_OBEN if oben is None else oben
    if oben:
        rr, hr = max(KN["r"], round(math.hypot(R_KN + PP.KORDEL["h"], PP.KORDEL["b"] / 2) + KN["luft"], 1)), KN["h"] + PP.KORDEL["h"] + KN["luft"]
    else:
        rr, hr = KN["r"], KN["h"] + KN["luft"]
    rs = R_KN + vor
    z1 = GANG_H + rs - rr
    top = GANG_H + rs - rd if z1 >= hr else hr + rr - rd
    return round(max(top, hr) + DACH, 2)


def varianten():
    """Kastenhöhe je Möglichkeit (Powerbank + Steckerraum 6,0 darüber), für Bericht und Planseite."""
    def H(z):
        return round(z + PB_T + PP.STECKERRAUM_8, 1)
    v = [
        ("gewählt", ("Anstieg %.1f mm vor dem Knopf, Decke Ø %.0f, Powerbank auf Plateau und Auflagen" % (PP.KNOPF_RAMPE["vor"], 2 * R_DECKE)).replace(".", ","), plateau_z(), True),
        ("rampe10", "Anstieg genau 10 mm vor dem Knopf (Decke Ø 20)", plateau_z(vor=10.0), True),
        ("decke18", "Decke Ø 18 statt 20 (mehr Reserve zur Brückenregel)", plateau_z(decke_d=18.0), True),
        ("flach25", "flache Decke Ø 25 direkt auf 12,2 (Brücke 25, über der Regel 20)", KN["h"] + KN["luft"] + DACH, False),
        ("weg", "Powerbank nicht über dem Knopf, auf den Gangdächern (neue Lage nötig)", GANG_Z, True),
        ("alt", "Stand 8 vorher (Knopf als 1,2 mm gelesen, Gangdach 6,2)", 6.2, True),
    ]
    return [dict(k=k, t=t, z=round(z, 1), H=H(z), ok=ok) for k, t, z, ok in v]


def stand7():
    """Stand 7 aus build_batteriefach (gleiche Lagen wie der gedruckte Unterkasten)."""
    from plug.power import build_batteriefach as BB
    v = BB.final_variant()
    v.pop("meshes", None)
    return v


def main():
    v = stand7()
    for m in MODI:
        modus(m)
        r = build(v)
        print("Stand 8, Gangfase %s%s: Kasten %.1f mm (+%.1f), mit Platte %.1f, %s g / %s cm³, Stützen %d, Zapfen %s" % (
            m, " (Vorgabe)" if m == PP.GANG_FASE_MODUS else "", r["H"], r["plus"], r["total"], r["grams"][0], r["grams"][1], len(r["posts"]), r["pin_rows"]))
        for name, ok, txt in r["checks"]:
            print("  %-32s %-5s %s" % (name, "ok" if ok else "FEHLT", txt))
        print("  Druckzeit (h):", r["zeit"])
    modus(PP.GANG_FASE_MODUS)
    print("Austritte:", r["K"]["aus"])
    for x in varianten():
        print("  Variante %-8s Plateau/Auflage %.1f -> Kasten %.1f, mit Platte %.1f  %s" % (x["k"], x["z"], x["H"], x["H"] + BC.H0["plate_t"], x["t"]))
    print("Auflagen der Powerbank:", [tuple(round(x, 1) for x in a.bounds) for a in r["auflagen"]], "Standfestigkeit:", r["standfest"], "nur Plateau:", r["standfest0"])


if __name__ == "__main__":
    main()
