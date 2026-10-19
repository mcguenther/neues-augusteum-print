"""Unterkasten Stand 8 (Plan, noch keine STL): Kasten höher, Knopfraum und Kordelgänge für den Doktorhut, ohne Eckaussparungen.

Der Hut trägt in der Mitte seines Deckbretts einen flachen Knopf (Ø 22, 1,2 hoch) mit der Kordel der Quaste. Die Grundplatte liegt mittig
auf dem Hut, also hat der Unterkasten in der Plattenmitte unten einen Knopfraum (`HUT_KNOPF`, Ø 24 × 1,4 mit Spiel und 0,2 Luft), und die Kordel
läuft in einem Gang unter dem Kasten zur Außenwand (`KORDEL_GANG`, 8 × 5, acht Richtungen in 45°-Schritten). Innen werden Knopfraum und
Gänge zu Höckern mit der Decke `KORDEL_DACH`.

Nutzer 19.10.: Steckerraum über der Powerbank 6 mm (viele Leitungen), daher Kasten 25,0 statt 17,6. Die Powerbank bleibt, wo sie im Stand 7 liegt (quer passt sie wegen des Steckers nicht), also über dem Knopf. Sie liegt
auf den Dächern der Gänge (6,2 über dem Boden). Befestigung mit Heißkleber
(Kasten auf den Hut, im Zweifel Platte auf den Kasten): die Eckaussparungen für die Fäden entfallen.

Geometrie in Plattenkoordinaten (x Osten, y Norden, Ursprung Südwestecke), z = 0 an der Unterkante des Kastens. Werte in `params.py`.
Aufruf zum Prüfen: `python3 -m plug.power.kasten8` (ca. 15 s) druckt die Prüfzeilen.
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
from plug.power import build_concept as BC  # noqa: E402
from plug.power import params as PP  # noqa: E402

H7 = round(BC.H0["uk_t"], 2)                         # 17,6
PB_T = PP.PB_T + PP.PB_T_ZUSCHLAG                    # 12,8
DACH = PP.KORDEL_DACH
R_KNOPF = (PP.HUT_KNOPF["d"] + 2 * PP.HUT_KNOPF["spiel"]) / 2     # Knopfraum Ø 24
KNOPF_H = round(PP.HUT_KNOPF["h"] + PP.HUT_KNOPF["luft"], 2)   # Knopfraum 1,4
KNOPF_Z = round(KNOPF_H + DACH, 2)                   # Oberkante Knopfdach 2,6
GANG_Z = PP.KORDEL_GANG["h"] + DACH                  # Oberkante Gangdach 6,2
H8 = round(GANG_Z + PB_T + PP.STECKERRAUM_8, 2)      # Kasten so hoch, dass über der Powerbank 6,0 bleiben: 25,0
RICHTUNG = ("O", "NO", "N", "NW", "W", "SW", "S", "SO")   # k · 45°, 0° = Osten
TP_CLR = 0.10                                        # Spiel der Mulden um die Gebäude (Sperrfläche für Zapfen)


def kordel(W, L):
    """Mitte, Knopfraum, Gänge (frei) und Höcker (Wand plus Decke) als Polygone, dazu die Austrittspunkte an der Außenwand."""
    c = (W / 2, L / 2)
    outline = box(0, 0, W, L)
    inner = outline.buffer(-PP.UK_WALL, join_style=2)
    frei = Point(c).buffer(R_KNOPF, 96)
    kuppel = Point(c).buffer(R_KNOPF + DACH, 96)
    gaenge, hoecker, aus = [], [], []
    hw = PP.KORDEL_GANG["w"] / 2
    for k in range(PP.KORDEL_GANG["n"]):
        a = math.radians(k * 360.0 / PP.KORDEL_GANG["n"])
        d = (math.cos(a), math.sin(a))
        ln = LineString([c, (c[0] + 400 * d[0], c[1] + 400 * d[1])])
        gaenge.append(ln.buffer(hw, cap_style=2).intersection(outline.buffer(3, join_style=2)))
        hoecker.append(ln.buffer(hw + DACH, cap_style=2).intersection(inner))
        p = ln.intersection(outline.exterior)
        p = p if p.geom_type == "Point" else list(p.geoms)[0]
        aus.append(dict(r=RICHTUNG[k], ang=k * 45, x=round(p.x, 1), y=round(p.y, 1),
                        len=round(math.hypot(p.x - c[0], p.y - c[1]) - R_KNOPF, 1),
                        wand=round(PP.KORDEL_GANG["w"] / (abs(d[0]) if min(p.x, W - p.x) < 1e-6 else abs(d[1])), 1)))
    return dict(c=c, frei=frei, kuppel=kuppel.intersection(inner), gaenge=gaenge, hoecker=hoecker, aus=aus)


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
    z_pb = GANG_Z if unter_pb else (KNOPF_Z if body.intersects(K["kuppel"]) else PP.UK_FLOOR)

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
    solids.append(G.extrude(K["kuppel"], PP.UK_FLOOR - 0.01, KNOPF_Z))
    solids.append(G.extrude(hoeck_all, PP.UK_FLOOR - 0.01, GANG_Z))
    solids += [G.extrude(r, PP.UK_FLOOR - 0.01, H) for r in posts]
    solids += [BC.pin_solid_at(posts[i].centroid, H, PP.PIN_PLAN, PP.CH_PIN) for i in pins]
    unten = unary_union([K["frei"], gang_all])
    holes = [G.extrude(K["frei"], -1, KNOPF_H), G.extrude(gang_all, -1, PP.KORDEL_GANG["h"]), BC.mouth_ch(unten, 0, PP.CH_BED)]
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
    esp_z0 = GANG_Z if esp_fp.intersects(hoeck_all) else (KNOPF_Z if esp_fp.intersects(K["kuppel"]) else PP.UK_FLOOR)
    espm = mbox(*esp_fp.bounds[0::2], *esp_fp.bounds[1::2], esp_z0 + 0.01, esp_z0 + PP.ESP_H + 2 * PP.ESP_TAPE)
    pc = plug.bounds
    zm = z_pb + PB_T / 2
    plugm = mbox(pc[0] + 0.3, pc[2] - 0.3, pc[1] + 0.3, pc[3] - 0.3, zm - 4.0, zm + 4.0)
    frei_m = G.extrude(K["frei"], 0.0, KNOPF_H - 0.01)
    gang_m = G.extrude(gang_all.intersection(outline).difference(K["frei"]), 0.0, PP.KORDEL_GANG["h"] - 0.01)
    pb_luft = z_pb - KNOPF_Z                         # Luft zwischen Knopfdach und Powerbank

    def iv(a):
        return round(float((a ^ uk).volume()), 2)

    tm = G.to_trimesh(uk)
    pb_top = z_pb + PB_T
    esp_top = esp_z0 + PP.ESP_H + 2 * PP.ESP_TAPE
    lie = len(unter_pb)
    checks = [
        ("dicht", bool(tm.is_watertight), "Netz geschlossen (Manifold)"),
        ("Knopfraum frei", iv(frei_m) == 0, "Ø %.0f × %.1f (Knopf Ø %.0f × %.1f, Spiel %.1f je Seite, Luft %.1f oben) gegen Kasten: %.2f mm³" % (2 * R_KNOPF, KNOPF_H, PP.HUT_KNOPF["d"], PP.HUT_KNOPF["h"], PP.HUT_KNOPF["spiel"], PP.HUT_KNOPF["luft"], iv(frei_m))),
        ("Gänge frei", iv(gang_m) == 0, "%d Gänge %.0f × %.0f bis zur Außenwand gegen Kasten: %.2f mm³" % (PP.KORDEL_GANG["n"], PP.KORDEL_GANG["w"], PP.KORDEL_GANG["h"], iv(gang_m))),
        ("Powerbank frei", iv(pbm) == 0, "liegt auf z = %.1f auf %d Gangdächern (%s), Überschneidung %.2f mm³" % (z_pb, lie, ", ".join(unter_pb), iv(pbm))),
        ("Steckerraum über der Powerbank", H - pb_top >= PP.STECKERRAUM_8 - 0.01, "%.1f mm (gefordert %.1f)" % (H - pb_top, PP.STECKERRAUM_8)),
        ("Kordel im Gang", PP.KORDEL["h"] < PP.KORDEL_GANG["h"] and PP.KORDEL["b"] < PP.KORDEL_GANG["w"], "Kordel %.0f × %.0f in Gang %.0f × %.0f (breit × hoch): Spiel %.1f hoch, %.1f seitlich" % (PP.KORDEL["b"], PP.KORDEL["h"], PP.KORDEL_GANG["w"], PP.KORDEL_GANG["h"], PP.KORDEL_GANG["h"] - PP.KORDEL["h"], PP.KORDEL_GANG["w"] - PP.KORDEL["b"])),
        ("Stecker USB-A frei", iv(plugm) == 0, "Steckerraum %.1f mm lang wie Stand 7, Überschneidung %.2f mm³" % (pc[3] - pc[1], iv(plugm))),
        ("ESP32 frei", iv(espm) == 0, "liegt auf z = %.1f (%s), Überschneidung %.2f mm³" % (esp_z0, "auf Gangdach" if esp_z0 == GANG_Z else "auf dem Boden", iv(espm))),
        ("Adern über dem ESP32", H - esp_top >= PP.ADERN_ZONE - 0.01, "%.1f mm unter der Platte (gefordert %.1f)" % (H - esp_top, PP.ADERN_ZONE)),
        ("Schalterraum frei", iv(sw["room"]) < 0.05, "Mitte %.1f über dem Boden, Überschneidung %.2f mm³" % (sw["z"], iv(sw["room"]))),
        ("Fenster der Powerbank", True, "Nordwand wie Stand 7, offen ab z = %.1f bis oben" % z_pb),
    ]
    return dict(H=H, plus=round(H - H7, 1), total=round(H + BC.H0["plate_t"], 1), uk=uk, grams=BC.grams(uk), checks=checks,
                body=body, plug=plug, win=win, z_pb=z_pb, unter_pb=unter_pb, pb_luft=round(pb_luft, 1), pb_m=pbm, esp_m=espm, esp_z0=esp_z0,
                plug_m=plugm, posts=posts, pins=pins, pin_rows=pin_rows, K=K, sw=sw, pb_top=round(pb_top, 1), esp_top=round(esp_top, 1), elec=elec)


def stand7():
    """Stand 7 aus build_batteriefach (gleiche Lagen wie der gedruckte Unterkasten)."""
    from plug.power import build_batteriefach as BB
    v = BB.final_variant()
    v.pop("meshes", None)
    return v


def main():
    v = stand7()
    r = build(v)
    print("Stand 8: Kasten %.1f mm (+%.1f), mit Platte %.1f, %s g / %s cm³, Stützen %d, Zapfen %s" % (
        r["H"], r["plus"], r["total"], r["grams"][0], r["grams"][1], len(r["posts"]), r["pin_rows"]))
    for name, ok, txt in r["checks"]:
        print("  %-32s %-5s %s" % (name, "ok" if ok else "FEHLT", txt))
    print("Austritte:", r["K"]["aus"])


if __name__ == "__main__":
    main()
