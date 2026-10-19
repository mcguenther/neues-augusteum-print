"""Unterkasten Stand 8 (Plan, noch keine STL): Kasten 5 mm höher, Knopfraum und Kordelgänge für den Doktorhut.

Der Hut trägt in der Mitte seines Deckbretts den Knopf mit der Kordel (Quaste). Die Grundplatte liegt mittig auf dem Hut, also muss der
Unterkasten in der Plattenmitte unten einen freien Raum haben (`HUT_KNOPF`, Ø 40 × 12) und die Kordel muss in einem Gang unter dem Kasten
zur Außenwand laufen können (`KORDEL_GANG`, 8 × 5, acht Richtungen in 45°-Schritten). Innen werden Knopfraum und Gänge zu Höckern mit der
Decke `KORDEL_DACH`.

Konflikt: Die Mitte (57,8 | 110,4) liegt im Stand 7 mitten unter der Powerbank. Zwei Varianten:

- `quer`: Kasten nur 5 mm höher (22,6). Die Powerbank liegt quer im Nordteil auf den Dächern der Gänge N, NO und NW (Oberkante 19,0,
  Steckerraum 3,6). Vor der Anschlussseite bleiben nur 19,8 mm (Winkelstecker), das Fenster wandert in die Westwand.
- `podest`: Powerbank bleibt, wo sie ist, liegt aber auf einem Podest über dem Knopfraum (Oberkante Podest 13,2). Der Kasten wird 12,0 mm
  höher (29,6) statt 5.

Geometrie in Plattenkoordinaten (x Osten, y Norden, Ursprung Südwestecke), z = 0 an der Unterkante des Kastens. Werte in `params.py`.
Aufruf zum Prüfen: `python3 -m plug.power.kasten8` (ca. 30 s) druckt die Prüfzeilen beider Varianten.
"""
import math
import os
import sys

import manifold3d as m3d
import numpy as np
from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import generate as G  # noqa: E402
from plug import dupont as sd  # noqa: E402
from plug.geom import box as mbox  # noqa: E402
from plug.power import build_concept as BC  # noqa: E402
from plug.power import params as PP  # noqa: E402

H7 = round(BC.H0["uk_t"], 2)                         # 17,6
PB_T = PP.PB_T + PP.PB_T_ZUSCHLAG                    # 12,8
DACH = PP.KORDEL_DACH
R_FREI = PP.HUT_KNOPF["d"] / 2
KNOPF_Z = PP.HUT_KNOPF["h"] + DACH                   # Oberkante Knopfraum 13,2
GANG_Z = PP.KORDEL_GANG["h"] + DACH                  # Oberkante Gangdach 6,2
RICHTUNG = ("O", "NO", "N", "NW", "W", "SW", "S", "SO")   # k · 45°, 0° = Osten


def hoehe(var):
    """Kastenhöhe (Boden bis Oberkante, ohne Zapfen)."""
    if var == "podest":
        return round(KNOPF_Z + sd.layer_up(PP.STECKERRAUM + PB_T), 2)
    return round(H7 + PP.UK_PLUS, 2)


def kordel(W, L):
    """Mitte, Knopfraum, Gänge (frei) und Höcker (Wand plus Decke) als Polygone, dazu die Austrittspunkte an der Außenwand."""
    c = (W / 2, L / 2)
    outline = box(0, 0, W, L)
    inner = outline.buffer(-PP.UK_WALL, join_style=2)
    frei = Point(c).buffer(R_FREI, 96)
    kuppel = Point(c).buffer(R_FREI + DACH, 96)
    gaenge, hoecker, aus = [], [], []
    hw = PP.KORDEL_GANG["w"] / 2
    for k in range(PP.KORDEL_GANG["n"]):
        a = math.radians(k * 360.0 / PP.KORDEL_GANG["n"])
        d = (math.cos(a), math.sin(a))
        ln = LineString([c, (c[0] + 400 * d[0], c[1] + 400 * d[1])])
        g = ln.buffer(hw, cap_style=2).intersection(outline.buffer(3, join_style=2))
        gaenge.append(g)
        hoecker.append(ln.buffer(hw + DACH, cap_style=2).intersection(inner))
        p = ln.intersection(outline.exterior)
        p = p if p.geom_type == "Point" else list(p.geoms)[0]
        aus.append(dict(r=RICHTUNG[k], ang=k * 45, x=round(p.x, 1), y=round(p.y, 1),
                        len=round(math.hypot(p.x - c[0], p.y - c[1]) - R_FREI, 1),
                        wand=round(PP.KORDEL_GANG["w"] / (abs(d[0]) if min(p.x, W - p.x) < 1e-6 else abs(d[1])), 1)))
    return dict(c=c, frei=frei, kuppel=kuppel.intersection(inner), gaenge=gaenge, hoecker=hoecker, aus=aus)


def pb_lage(var, v, W, L, K):
    """Powerbank (Körper mit Spiel), Steckerraum und Fenster in der Wand; Liegehöhe z0."""
    if var == "podest":
        body = Polygon(v["body"][0])
        plug = Polygon(v["plug"][0])
        win = Polygon(v["window"][0])
        return dict(body=body, plug=plug, win=win, z0=KNOPF_Z, ports="N", podest=Polygon(v["fach_poly"][0]))
    x0 = PP.UK_WALL + PP.PB_STECKER_QUER                 # Anschlussseite nach Westen
    lo = K["c"][1] + R_FREI + DACH + 1.0                 # nördlich des Knopfraums
    hi = min(Polygon(n["notch"]).bounds[1] for n in v["vs"] if Polygon(n["notch"]).bounds[1] > L / 2) - 1.0
    bl, bw = PP.PB_L + 2 * PP.PB_CLR, PP.PB_W + 2 * PP.PB_CLR
    y0 = (lo + hi) / 2 - bw / 2
    body = box(x0, y0, x0 + bl, y0 + bw)
    yc = y0 + bw / 2
    ua = yc + PP.PB_PORT_V["usb_a"]
    plug = box(PP.UK_WALL, ua - 7.5, x0, ua + 7.5)
    w0 = yc + PP.PB_PORT_V["leds"] - BC.PORT_HALF["leds"] - PP.WINDOW_PAD
    w1 = yc + PP.PB_PORT_V["usb_a"] + BC.PORT_HALF["usb_a"] + PP.WINDOW_PAD
    win = box(-1.0, w0, PP.UK_WALL + 0.5, w1)
    return dict(body=body, plug=plug, win=win, z0=GANG_Z, ports="W", podest=None, lo=lo, hi=hi)


def build(var, v):
    """Unterkasten Stand 8 als Manifold (z = 0 unten) und alles, was die Seite und die Prüfung brauchen."""
    W, L = v["plate"]
    H = hoehe(var)
    outline = box(0, 0, W, L)
    inner = outline.buffer(-PP.UK_WALL, join_style=2)
    K = kordel(W, L)
    pb = pb_lage(var, v, W, L, K)
    elec = Polygon(v["elec"][0])
    notches = [Polygon(n["notch"]) for n in v["vs"]]
    zones = [Polygon(d["zone"]) for d in v["docks"] if d["ok"]]
    gang_all, hoeck_all = unary_union(K["gaenge"]), unary_union(K["hoecker"])

    # Stützen im 40-mm-Raster wie Stand 7, frei von Knopfraum, Gängen, Powerbank, Elektronik, Fäden und Docks
    block = [pb["body"].buffer(3), pb["plug"].buffer(3), elec.buffer(3), K["kuppel"].buffer(3), hoeck_all.buffer(1.5)] + \
            [n.buffer(3) for n in notches] + [z.buffer(3) for z in zones]
    if pb["podest"] is not None:
        block.append(pb["podest"].buffer(1))
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
    solids.append(G.extrude(K["kuppel"], PP.UK_FLOOR - 0.01, KNOPF_Z))
    solids.append(G.extrude(hoeck_all, PP.UK_FLOOR - 0.01, GANG_Z))
    if pb["podest"] is not None:                       # Podest unter Powerbank und Steckerraum: voller Block, der Slicer füllt ihn
        solids.append(G.extrude(pb["podest"].intersection(inner), PP.UK_FLOOR - 0.01, KNOPF_Z))
    solids += [G.extrude(r, PP.UK_FLOOR - 0.01, H) for r in posts]
    solids += [BC.pin_solid_at(posts[i].centroid, H, PP.PIN_PLAN, PP.CH_PIN) for i in pins]
    unten = unary_union([K["frei"], gang_all])
    holes = [G.extrude(K["frei"], -1, PP.HUT_KNOPF["h"]), G.extrude(gang_all, -1, PP.KORDEL_GANG["h"]), BC.mouth_ch(unten, 0, PP.CH_BED)]
    holes += [G.extrude(n, -1, H + 2) for n in notches] + [BC.mouth_ch(n, 0, PP.CH_BED) for n in notches]
    holes.append(G.extrude(pb["win"], pb["z0"], H + 2))
    sw = BC.switch_cut(0, 0, 0, dict(uk_t=H))
    holes.append(sw["cut"])
    uk = G.union(solids) - G.union(holes)

    # Teile, die im Kasten liegen (für Prüfung und Ansicht)
    b = pb["body"].bounds
    pbm = mbox(b[0] + PP.PB_CLR, b[2] - PP.PB_CLR, b[1] + PP.PB_CLR, b[3] - PP.PB_CLR, pb["z0"] + 0.01, pb["z0"] + PB_T)
    eb = elec.bounds
    ecx, ecy = (eb[0] + eb[2]) / 2, (eb[1] + eb[3]) / 2
    bw, bh = PP.ESP_BOARD if eb[2] - eb[0] >= eb[3] - eb[1] else PP.ESP_BOARD[::-1]
    esp_fp = box(ecx - bw / 2 - PP.ESP_TAPE, ecy - bh / 2 - PP.ESP_TAPE, ecx + bw / 2 + PP.ESP_TAPE, ecy + bh / 2 + PP.ESP_TAPE)
    esp_z0 = GANG_Z if esp_fp.intersects(hoeck_all) else PP.UK_FLOOR
    if esp_fp.intersects(K["kuppel"]):
        esp_z0 = KNOPF_Z
    espm = mbox(*esp_fp.bounds[0::2], *esp_fp.bounds[1::2], esp_z0 + 0.01, esp_z0 + PP.ESP_H + 2 * PP.ESP_TAPE)
    pc = pb["plug"].bounds
    zm = pb["z0"] + PB_T / 2
    plugm = mbox(pc[0] + 0.3, pc[2] - 0.3, pc[1] + 0.3, pc[3] - 0.3, zm - 4.0, zm + 4.0)
    frei_m = G.extrude(K["frei"], 0.0, PP.HUT_KNOPF["h"] - 0.01)
    gang_m = G.extrude(gang_all.intersection(outline).difference(K["frei"]), 0.0, PP.KORDEL_GANG["h"] - 0.01)

    def iv(a):
        return round(float((a ^ uk).volume()), 2)

    tm = G.to_trimesh(uk)
    gr = BC.grams(uk)
    pb_top = pb["z0"] + PB_T
    esp_top = esp_z0 + PP.ESP_H + 2 * PP.ESP_TAPE
    checks = [
        ("dicht", bool(tm.is_watertight), "Netz geschlossen (Manifold)", True),
        ("Knopfraum frei", iv(frei_m) == 0, "Ø %.0f × %.0f gegen Kasten: %.2f mm³" % (2 * R_FREI, PP.HUT_KNOPF["h"], iv(frei_m)), True),
        ("Gänge frei", iv(gang_m) == 0, "%d Gänge %.0f × %.0f bis zur Außenwand gegen Kasten: %.2f mm³" % (PP.KORDEL_GANG["n"], PP.KORDEL_GANG["w"], PP.KORDEL_GANG["h"], iv(gang_m)), True),
        ("Powerbank frei", iv(pbm) == 0, "liegt auf z = %.1f, Überschneidung %.2f mm³" % (pb["z0"], iv(pbm)), True),
        ("Steckerraum über der Powerbank", H - pb_top >= PP.STECKERRAUM - 0.01, "%.1f mm (gefordert %.1f)" % (H - pb_top, PP.STECKERRAUM), True),
        ("Stecker USB-A frei", iv(plugm) == 0, "Steckerraum %.1f mm lang, Überschneidung %.2f mm³" % (pc[2] - pc[0] if pb["ports"] == "W" else pc[3] - pc[1], iv(plugm)), True),
        ("ESP32 frei", iv(espm) == 0, "liegt auf z = %.1f (%s), Überschneidung %.2f mm³" % (esp_z0, "auf Gangdach" if esp_z0 == GANG_Z else "auf dem Boden", iv(espm)), True),
        ("Adern über dem ESP32", H - esp_top >= PP.ADERN_ZONE - 0.01, "%.1f mm unter der Platte (gefordert %.1f)" % (H - esp_top, PP.ADERN_ZONE), True),
        ("Schalterraum frei", iv(sw["room"]) < 0.05, "Mitte %.1f über dem Boden, Überschneidung %.2f mm³" % (sw["z"], iv(sw["room"])), True),
        ("Elektronik zum Knopfraum", elec.distance(K["kuppel"]) >= 1.0, "%.1f mm Abstand" % elec.distance(K["kuppel"]), False),
    ]
    return dict(var=var, H=H, plus=round(H - H7, 1), total=round(H + BC.H0["plate_t"], 1), uk=uk, grams=gr, checks=checks,
                pb=pb, pb_m=pbm, esp_m=espm, esp_z0=esp_z0, plug_m=plugm, posts=posts, pins=pins, pin_rows=pin_rows, K=K, sw=sw,
                pb_top=round(pb_top, 1), esp_top=round(esp_top, 1), elec=elec)


TP_CLR = 0.10


def stand7():
    """Stand 7 aus build_batteriefach (gleiche Lagen wie der gedruckte Unterkasten)."""
    from plug.power import build_batteriefach as BB
    v = BB.final_variant()
    v.pop("meshes", None)
    return v


def main():
    v = stand7()
    for var in ("quer", "podest"):
        r = build(var, v)
        print("Variante %s: Kasten %.1f mm (+%.1f), mit Platte %.1f, %s g / %s cm³, Stützen %d, Zapfen %s" % (
            var, r["H"], r["plus"], r["total"], r["grams"][0], r["grams"][1], len(r["posts"]), r["pin_rows"]))
        for name, ok, txt, _ in r["checks"]:
            print("  %-32s %-5s %s" % (name, "ok" if ok else "FEHLT", txt))
    print("Austritte:", kordel(*v["plate"])["aus"])


if __name__ == "__main__":
    main()
