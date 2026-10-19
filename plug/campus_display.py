#!/usr/bin/env python3
"""Display-Gebäude in der Steckplatte: Mulde und Dock (vier Pin-Löcher) am Ostrand der Platte 1:1300.

Das Display-Gebäude (OLED mit INA226, `plug/display/`, Entwurf E4) steht nicht in `params.CASSETTE` und nicht in `placements_1300.json`: sein Kopf
schwebt mit 0,3 mm Luft über der Platte, nur der Fuß (Hals mit Verlängerung nach vorn und Kodierecke) taucht in die Platte. Die Mulde dafür und die vier
Pin-Löcher kommen hierher; `plug.campus.build` ruft `cuts` auf und schneidet sie mit den Gebäude-Mulden.

**Maße: zweiter Satz** (seit 20.10.2026, `SATZ = 2`: der Nutzer hat den Körper mit der Dupont-Buchse direkt im Hals gedruckt). Bis dahin erster Satz (Commit 59000df,
Probedruck 1; Fuß, Mulde mit Kodierecke und Einführfase 0,5 waren dort „in Ordnung“, Vorgabe des Nutzers 2026-10-18).
Der zweite Satz (`plug/display/body4.py` heute: Hals 12,96 × 5,34, Buchsentasche im Hals) ist ungedruckt; sein Fuß ist 2,52 mm schmaler und flacher, die
Pin-Reihe liegt 1,26 mm näher an der Vorderkante des Fußes. `SATZ = 2` baut die Mulde stattdessen nach dem zweiten Satz (danach die Lage prüfen).
Die Prüfung `report` meldet, wie der jeweils andere Fuß in die gebaute Mulde passt.

Koordinaten: Plattenkoordinaten (x nach Osten, y nach Norden, Ursprung Südwestecke der Platte, wie `plug/display/layout.py`); `plug.campus` rechnet mit den
Rohkoordinaten des Umrisses, `cuts` bekommt dazu die Südwestecke. Lokaler Rahmen des Körpers: x = 0 an der Ostfläche des Kopfes, nach Westen negativ,
y quer, Mitte 0, z = 0 Plattenoberfläche.

Aufruf (Passprobe im Rechner: Display-Körper in der Mulde, Kopf gegen die Gebäude, Dockzone gegen den gedruckten Unterkasten, Bilder; ca. 1 min):
    python3 -m plug.campus_display
"""
import math
import os

import numpy as np
from shapely import affinity
from shapely.geometry import Polygon, box as sbox
from shapely.ops import unary_union

from plug import dupont as sd
from plug.geom import ext
from plug.testcase import params as P

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---- Lage (Plattenkoordinaten, SW-Ecke = 0)
# xe: Ostfläche des Kopfes (Display-Front), 4,1 mm von der Plattenkante (115,58): `plug/display/layout.py` EAST_XE, Vorgabe des Nutzers. Der Fuß mit der Mulde
#     liegt dahinter (Vorderkante des Fußes 10,3 mm westlich davon).
# yc: Mitte des Kopfes und der Pin-Reihe. Südlichste Lage, die die Prüfung freigibt (Suche in 0,1-mm-Schritten, y 20 bis 110, `lage_suche`): Der Kopf (38,34 breit)
#     bleibt 1,5 mm (`AIR_MARGIN`) über dem Buchstaben N des Nordpfeils (Oberkante y = 13,69) und der Schrift; weiter südlich stößt er an die Beschriftung.
#     Das City-Hochhaus (y ab 58,7) liegt rechts (nördlich) davon, hinter dem Kopf steht das Hörsaalgebäude (y 18 bis 123). Obere Grenze 56,0 (Dockzone
#     stößt an das Dock des Hochhauses); `plug/display/layout4.py` meldet mit den Faden-V des Konzepts 39 bis 58 (die Fadenkerben dort entfallen, die Fadentaschen
#     liegen weit weg), die Prüfung hier rechnet mit den echten Fadentaschen, Zapfenlöchern, Mulden und der Schrift der Platte.
DISPLAY_LAGE = dict(xe=111.5, yc=34.4)
SATZ = 2                # 2 (seit 20.10.2026, Nutzer: gedruckter Körper hat die Dupont-Buchse direkt im Hals): Mulde nach dem aktuellen Stand von plug/display/body4.py; 1: nach dem ersten Satz (Commit 59000df, mit Kassette K0)
AIR_MARGIN = 1.5        # E  Luft zwischen Kopf und Gebäuden, Hof, Schrift (wie plug/display/layout4.py)
WALL_MIN = 0.8          # E  Mindestwand der neuen Mulde zu anderen Aussparungen (Auftrag), Fadentaschen 1,4 (plug/thread/params.py WALL_MIN)
WALL_FADEN = 1.4
KOPF_LUFT = 0.3         # A  Kopf über der Platte (aus plug/display/params.py: WIN_BOTTOM − Platine unter dem Fenster − FLOOR_T)

# Erster Satz, eingefroren (so gebaut in 59000df, `git show 59000df:plug/display/params.py body4.py layout.py`): Schacht 13,08 × 5,46 (V2-Unterbau 12,96 × 5,34 plus
# Einpressspiel 0,06 je Seite) plus Wand 1,2 ergibt Hals 15,48 × 7,86. Alles andere (Abstand Stiftspitze, Fußverlängerung, Kodierecke) stimmt mit dem aktuellen Stand überein.
SATZ1 = dict(NW=15.48, KD=7.86, x_be=-16.3, ext=6.0, key=3.0, clr=0.15, W=38.3, x_back=-7.9, z_top=36.0, foot=-14.2, ch_front=2.0, ch_side=0.6)


def satz(n=None):
    """Maße des Fußes und des Kopfes nach Satz 1 (eingefroren) oder Satz 2 (aktueller Stand `plug/display/body4.dims()`); lokaler Rahmen."""
    n = n or SATZ
    if n == 1:
        s = dict(SATZ1)
    else:
        from plug.display import body4 as B
        from plug.display import params as D
        d = B.dims()
        s = dict(NW=d["NW"], KD=d["KD"], x_be=d["x_be"], ext=D.FOOT_EXT, key=D.KEY, clr=D.CLR_MULDE, W=d["W"], x_back=d["x_back"],
                 z_top=d["z_top"] + D.LIP_T, foot=d["foot"], ch_front=D.FOOT_CH_FRONT, ch_side=D.FOOT_CH_SIDE)
    s["x_bw"] = s["x_be"] - s["KD"]                     # Westkante des Halses
    s["x_fe"] = s["x_be"] + s["ext"]                    # Vorderkante des Fußes (nach Osten verlängert)
    s["pe"] = -(s["x_be"] + s["x_bw"]) / 2              # Pin-Reihe: Abstand von der Ostfläche des Kopfes nach Westen (Mitte des Halses)
    s["satz"] = n
    return s


def foot_poly(s):
    """Grundriss des Fußes: Schachtsäule plus Verlängerung nach vorn (Osten), Kodierecke vorn Süd (wie body4.foot_poly)."""
    n, xb, xf, k = s["NW"] / 2, s["x_bw"], s["x_fe"], s["key"]
    return [(xb, -n), (xf - k, -n), (xf, -n + k), (xf, n), (xb, n)]


def head_poly(s):
    """Grundriss des Körpers in der Luft über der Platte: Kopf in voller Breite, dahinter schmaler bis zum Hals (wie body4.profile_plan)."""
    w, n = s["W"] / 2, s["NW"] / 2
    return [(0.0, -w), (0.0, w), (s["x_back"], w), (s["x_be"], n), (s["x_bw"], n), (s["x_bw"], -n), (s["x_be"], -n), (s["x_back"], -w)]


def pin_x(lage=None, s=None):
    """x der Pin-Reihe (Plattenkoordinaten): immer an der Mulde des gebauten Satzes (SATZ), auch wenn ein anderer Körper geprüft wird."""
    lage = lage or DISPLAY_LAGE
    return lage["xe"] - (s or satz())["pe"]


def body_xe(s_body, lage=None):
    """x der Ostfläche des Kopfes für einen Körper des Satzes s_body, wenn seine Stifte in die Löcher der gebauten Mulde treffen sollen."""
    return pin_x(lage) + s_body["pe"]


def at(poly, xe, yc):
    return affinity.translate(poly, xe, yc)


def mulde_poly(lage=None, s=None):
    """Mulde in der Platte (Plattenkoordinaten): Fuß plus Spiel `clr` je Seite, Ecken spitz (wie plug/campus.py mulde_body)."""
    lage = lage or DISPLAY_LAGE
    s = s or satz()
    return at(Polygon(foot_poly(s)).buffer(s["clr"], join_style=2), lage["xe"], lage["yc"])


def pin_xy(lage=None, s=None):
    """Mitten der vier Pin-Löcher (Plattenkoordinaten), Reihe in y, Teilung 2,54 (wie die Gebäude-Docks, `sd.pin_x`)."""
    lage = lage or DISPLAY_LAGE
    return [(pin_x(lage, s), lage["yc"] + x) for x in sd.pin_x()]


def dock_zone(lage=None, s=None):
    """Dockzone unter der Platte (Leistenkörper, Lötenden nach Westen, Draht, Rand 2,0; `BC.dock_zone`): Raum, den im Unterkasten keine Stütze belegt (Plattenkoordinaten)."""
    from plug.power import build_concept as BC
    lage = lage or DISPLAY_LAGE
    zb = BC.dock_zone().bounds             # lokal: Pin-Reihe bei y = 0, Lötenden nach −y; hier nach −x gedreht
    xp = pin_x(lage, s)
    return sbox(xp + zb[1], lage["yc"] + zb[0], xp + zb[3], lage["yc"] + zb[2])


def dock_env(lage=None, s=None):
    """Hüllkurve des Docks wie `plug.campus.dock_local` (Leiste, Lötenden, Draht aus `TB.dock_cuts_b`), Lötenden nach Westen gedreht (Plattenkoordinaten)."""
    from plug import campus as C       # lazy: campus importiert dieses Modul in build()
    lage = lage or DISPLAY_LAGE
    _, env = C.dock_local("v4", 0.0, P.dims_plan())
    return affinity.translate(affinity.rotate(env, -90.0, origin=(0, 0)), pin_x(lage, s), lage["yc"])


def foot_prism(s, z0=None):
    """Außenform des Fußes als Körper (lokal, z = 0 Plattenoberfläche), mit den Fasen des Körpers (vorn und Kodierecke 2,0, Seiten und hinten 0,6)."""
    from plug.display import body4 as B
    z0 = s["foot"] if z0 is None else z0
    ch = [s["ch_side"], s["ch_front"], s["ch_front"], s["ch_side"], s["ch_side"]]     # Süd, Kodierecke, Ost, Nord, West
    return B.chamfered_prism(foot_poly(s), z0, KOPF_LUFT + 1.0, ch)


def head_prism(s):
    """Kopf und Rücken als Hüllkörper (lokal): Grundriss `head_poly` von der Unterkante (0,3 über der Platte) bis zur Oberkante der Blende. Etwas größer als der Körper
    (die Schräge hinten ist nicht abgezogen), also für Abstandsprüfungen auf der sicheren Seite."""
    return ext_poly(Polygon(head_poly(s)), KOPF_LUFT, s["z_top"])


def ext_poly(poly, z0, z1):
    from plug.display import body4 as B
    return ext(B._poly_cs(poly), z0, z1)


def body_hull(s):
    """Fuß plus Kopf als ein Körper (lokal)."""
    return foot_prism(s) + head_prism(s)


def place(man, xe, yc, minx, miny, T):
    """Körper (lokal) in die Rohkoordinaten der Platte setzen: Ostfläche des Kopfes bei Plattenkoordinate xe, Mitte yc, Oberfläche z = T."""
    return man.translate([minx + xe, miny + yc, T])


def cuts(T, minx, miny, mulde_body, pin_holes, d, lage=None):
    """Schnittkörper der Platte (Rohkoordinaten, Oberfläche bei z = T): Mulde (Fußumriss plus Spiel, bis zur Fußunterkante, oben Einführfase, Muldenboden 0,4 bleibt)
    und vier Pin-Löcher mit Fase unten und oben. `mulde_body(polygon, d, clr)` und `pin_holes(d)` kommen aus plug/campus.py (dieselbe Geometrie wie bei den Gebäuden)."""
    lage = lage or DISPLAY_LAGE
    s = satz()
    fp = at(Polygon(foot_poly(s)), lage["xe"] + minx, lage["yc"] + miny)
    out = [mulde_body(fp, d, s["clr"]).translate([0, 0, T])]
    for h in pin_holes(d):                               # Pin-Reihe in x: quer legen (y) und an die Mitte des Halses setzen (wie D4 in plug/display/build.py)
        out.append(h.rotate([0, 0, 90]).translate([minx + pin_x(lage, s), miny + lage["yc"], T]))
    return out


# --------------------------------------------------------------------------
# Prüfungen (in plug.campus.main und als Passprobe `python3 -m plug.campus_display`)
# --------------------------------------------------------------------------
def pose(man, s_body, minx, miny, T, ang=0.0, dx=0.0, dy=0.0, lage=None):
    """Körper des Satzes s_body (lokal) so setzen, dass seine Stifte in die Pin-Löcher der gebauten Mulde treffen (Pin-Reihe senkrecht an `pin_x`),
    optional um die Pin-Achse gedreht (ang, Grad) und um (dx, dy) verschoben; Rohkoordinaten, Plattenoberfläche bei z = T."""
    lage = lage or DISPLAY_LAGE
    m = man.translate([s_body["pe"], 0.0, 0.0]).rotate([0.0, 0.0, ang])
    return m.translate([minx + pin_x(lage) + dx, miny + lage["yc"] + dy, T])


def vol(a, b):
    return float((a ^ b).volume())


def fit_rows(plate, minx, miny, T):
    """Passprobe des Körpers (Fuß plus Kopf als Hüllkörper) des gebauten Satzes (`SATZ`) in der Mulde: [(Text, Überschneidung mm³, soll_null)]; Kontrollen müssen
    stoßen. Dazu der andere Satz: Satz 2 säße in der Mulde von Satz 1 lose, Satz 1 passt nicht in die Mulde von Satz 2 (Fuß 2,5 mm breiter)."""
    sb, so = satz(SATZ), satz(3 - SATZ)
    nb, no = ("erster", "zweiter") if SATZ == 1 else ("zweiter", "erster")
    rows = []
    hb, ho = body_hull(sb), body_hull(so)
    rows.append(("Körper %s Satz (Fuß in der Mulde, Kopf %.1f mm in der Luft), Spiel %.2f je Seite" % (nb, KOPF_LUFT, sb["clr"]), vol(pose(hb, sb, minx, miny, T), plate), True))
    for dx, dy, txt in ((0.10, 0.0, "0,10 nach Osten verschoben (Spiel 0,15 reicht noch)"), (0.0, 0.10, "0,10 nach Norden verschoben (Spiel 0,15 reicht noch)")):
        rows.append(("Kontrolle: Körper %s Satz %s" % (nb, txt), vol(pose(hb, sb, minx, miny, T, dx=dx, dy=dy), plate), True))
    for dx, dy, txt in ((0.0, 0.20, "0,20 nach Norden verschoben stößt an die Mulde"), (0.20, 0.0, "0,20 nach Osten verschoben stößt an die Mulde"),
                        (0.0, -0.20, "0,20 nach Süden verschoben stößt an die Mulde")):
        rows.append(("Kontrolle: Körper %s Satz %s" % (nb, txt), vol(pose(hb, sb, minx, miny, T, dx=dx, dy=dy), plate), False))
    for ang in (90, 180, 270):
        rows.append(("Kontrolle: Körper %s Satz um %d° gedreht (Verdrehsicherung) stößt an die Mulde" % (nb, ang), vol(pose(hb, sb, minx, miny, T, ang=ang), plate), False))
    mir = hb.mirror([0.0, 1.0, 0.0])                               # Kodierecke vorn Nord statt vorn Süd
    rows.append(("Kontrolle: Körper %s Satz gespiegelt (Kodierecke vorn Nord statt Süd) stößt an die Mulde" % nb, vol(pose(mir, sb, minx, miny, T), plate), False))
    if SATZ == 1:
        rows.append(("Fuß zweiter Satz (Hals %.2f × %.2f) mit den Stiften an den Löchern, lose in der Mulde" % (so["NW"], so["KD"]), vol(pose(ho, so, minx, miny, T), plate), True))
    else:
        rows.append(("Kontrolle: Körper erster Satz (Fuß %.2f × %.2f, mit Kassette K0) passt nicht in diese Mulde" % (so["x_fe"] - so["x_bw"], so["NW"]), vol(pose(ho, so, minx, miny, T), plate), False))
    return rows


def slop(s_body):
    """Luft zwischen dem Fuß des Satzes s_body (Stifte an den Löchern) und der gebauten Mulde: (West, Ost, Süd, Nord) in mm (aus den Umrissen)."""
    mu = mulde_poly()
    fp = at(Polygon(foot_poly(s_body)), pin_x() + s_body["pe"], DISPLAY_LAGE["yc"])
    a, b = mu.bounds, fp.bounds
    return round(b[0] - a[0], 2), round(a[2] - b[2], 2), round(b[1] - a[1], 2), round(a[3] - b[3], 2)


def walls(plate_base, outline, info, lay):
    """Mindestwand (XY, mm) der neuen Mulde zu allen vorhandenen Aussparungen der Platte ohne Display (Mulden, Pin-Löcher, Hof, Zapfenlöcher, Fadentaschen):
    aus Schnitten in mehreren Höhen, dazu zum Plattenrand, zu den Zapfenlöchern und den Fadentaschen einzeln."""
    from plug import campus_underside as U
    minx, miny = info["minx"], info["miny"]
    mu = affinity.translate(mulde_poly(), minx, miny)
    inner = outline.buffer(-0.6)
    voids = unary_union([inner.difference(U.section_poly(plate_base, z)) for z in (0.1, 0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 9.0, 12.0)])
    res = {"allen Aussparungen": mu.distance(voids), "Plattenrand": mu.distance(outline.exterior)}
    if lay:
        res["Zapfenlöchern"] = min(mu.distance(U.zapfen_circle(p, U.LOCH_FASE)) for p in lay["pins"])
        if lay["faden"]:
            res["Fadentaschen"] = min(mu.distance(g) for g in U.faden_polys(lay))
    return res


def pin_circles():
    from shapely.geometry import Point
    return [Point(xy).buffer(sd.HOLE / 2 + 0.3, 16) for xy in pin_xy()]


def report(plate, outline, info, lay):
    """Prüfzeilen für `plug.campus.main` (Platte `plate` mit Display-Dock, `info["base"]` ohne); True, wenn alle harten Prüfungen bestehen."""
    from plug import campus_underside as U
    ok = True
    s, s2, lage = satz(), satz(2), DISPLAY_LAGE
    minx, miny, T, base = info["minx"], info["miny"], info["T"], info["base"]
    mu = mulde_poly()
    mu_raw = affinity.translate(mu, minx, miny)
    plate_w = outline.bounds[2] - minx
    print("Display-Dock (plug/campus_display.py; Mulde und Pin-Löcher nach dem %s Satz%s):" % (
        "ersten" if s["satz"] == 1 else "zweiten", " (Commit 59000df, gedruckt, Fuß und Mulde in Ordnung)" if s["satz"] == 1 else " (ungedruckt)"))
    print("  Lage (Plattenkoordinaten, SW-Ecke = 0): Ostfläche des Kopfes x = %.1f (%.1f mm von der Plattenkante), Mitte y = %.1f; Fußmulde x %.2f bis %.2f, y %.2f bis %.2f" % (
        lage["xe"], plate_w - lage["xe"], lage["yc"], mu.bounds[0], mu.bounds[2], mu.bounds[1], mu.bounds[3]))
    print("  Mulde %.2f × %.2f (Fuß %.2f × %.2f plus Spiel %.2f je Seite) mit Kodierecke %.1f, Tiefe %.1f, Einführfase %.1f, Boden %.1f; vier Pin-Löcher Ø %.1f bei x = %.2f, y = %s" % (
        s["x_fe"] - s["x_bw"] + 2 * s["clr"], s["NW"] + 2 * s["clr"], s["x_fe"] - s["x_bw"], s["NW"], s["clr"], s["key"], P.dims_plan()["F"], P.MULDE_CH_T, P.CEIL_T,
        sd.HOLE, pin_x(), ", ".join("%.2f" % y for _, y in pin_xy())))
    lim = {"Fadentaschen": WALL_FADEN}
    for k, v in walls(base, outline, info, lay).items():
        print("  Mindestwand der Mulde zu %-24s %.2f mm" % (k, v))
        ok &= v >= lim.get(k, WALL_MIN)
    zones, envs = info["zones"], info["envs"]
    env = affinity.translate(dock_env(), minx, miny)
    z_raw = affinity.translate(dock_zone(), minx, miny)
    bad = env.difference(outline.buffer(-1.0)).area + sum(env.intersection(o).area for o in envs)
    zmin = min(z_raw.distance(z) for z in zones)
    print("  Dock außerhalb/überlappt (Hüllkurve wie bei den Gebäuden) %.2f mm²; Dockzone %.1f × %.1f mm, Abstand zur nächsten Dockzone eines Gebäudes %.1f mm, zum Plattenrand %.1f mm" % (
        bad, z_raw.bounds[2] - z_raw.bounds[0], z_raw.bounds[3] - z_raw.bounds[1], zmin, z_raw.distance(outline.exterior)))
    ok &= bad < 0.05 and zmin > 1.0 and outline.buffer(-2.9).contains(z_raw)
    circs = [affinity.translate(c, minx, miny) for c in pin_circles()]
    o_m = U.layer_overhang(plate, [mu_raw] + circs, T + 0.6)
    print("  Überhang je 0,2-mm-Lage (Mulde samt Pin-Löchern, Fasen in Stufen): größter Sprung %.2f mm bei z = %.1f; Boden 0,4 auf dem Bett, Mulde oben offen: keine Brücke, kein Support" % (o_m[0], o_m[1]))
    ok &= o_m[0] <= 0.3
    rows = []
    for z in (0.1, 0.5, 2.0, 9.0, 10.0, 12.0, 14.0, 14.5):
        a, b = U.section_poly(base, z), U.section_poly(plate, z)
        rows.append((z, a.symmetric_difference(b).difference(mu_raw.buffer(s["clr"] + P.MULDE_CH_T + 0.2)).area))
    removed = base - plate
    added = float((plate - base).volume())
    rb, mb = removed.bounding_box(), mu_raw.bounds
    inside = rb[0] >= mb[0] - 0.8 and rb[3] <= mb[2] + 0.8 and rb[1] >= mb[1] - 0.8 and rb[4] <= mb[3] + 0.8
    print("  unverändert: Schnittdifferenz alt/neu außerhalb der Mulde bei z = %s: %s mm²; hinzugekommen %.3f mm³; abgetragen %.1f mm³ (%.2f cm³), nur innerhalb der Mulde: %s" % (
        " / ".join("%.1f" % z for z, _ in rows), " / ".join("%.4f" % a for _, a in rows), added, float(removed.volume()), float(removed.volume()) / 1000, inside))
    ok &= all(a < 0.01 for _, a in rows) and added < 0.01 and inside
    print("  Passprobe im Rechner (Überschneidung mit der Platte in mm³; Hüllkörper aus Fuß und Kopf, der Kopf schwebt %.1f mm über der Platte):" % KOPF_LUFT)
    for txt, v_, soll_null in fit_rows(plate, minx, miny, T):
        good = (v_ < 0.05) if soll_null else (v_ > 0.05)
        ok &= good
        print("    %-112s %8.3f  %s" % (txt, v_, "ok" if good else "FEHLER"))
    sl = slop(s2)
    print("  Fuß zweiter Satz (Hals %.2f × %.2f, Fuß %.2f × %.2f) in dieser Mulde: Luft West %.2f, Ost %.2f, Süd %.2f, Nord %.2f mm (gebauter Satz %d: %.2f je Seite); die Stifte liegen %.2f mm näher an der Vorderkante des Fußes" % (
        s2["NW"], s2["KD"], s2["x_fe"] - s2["x_bw"], s2["NW"], *sl, SATZ, s["clr"], s["x_fe"] - (s["x_be"] + s["x_bw"]) / 2 - (s2["x_fe"] - (s2["x_be"] + s2["x_bw"]) / 2)))
    return ok


# --------------------------------------------------------------------------
# Passprobe im Rechner: Lagesuche, Kopf gegen die Gebäude, Dockzone gegen den gedruckten Unterkasten, Bilder
# --------------------------------------------------------------------------
UK_STL = os.path.join(HERE, "stl", "steckmodul_unterkasten", "U_unterkasten.stl")
GEB = os.path.join(HERE, "stl", "steckmodul_campus", "gebaeude")
PREV = os.path.join(HERE, "vorschau", "steckmodul_campus")
UK_H = 17.6             # B  Höhe des gedruckten Unterkastens (Stand 7), Oberkante = Auflage der Steckplatte (Plattenunterseite)
STECKERRAUM = 3.5       # E  Raum zwischen Plattenunterseite und Powerbank unter dem Dock (Leiste, Lötenden, Draht)
SLUGS = ("01_paulinum", "02_neues_augusteum", "03_hoersaalgebaeude", "04_seminargebaeude", "05_institutsgebaeude", "06_city_hochhaus")


def load_stl(path):
    import manifold3d as m3d
    import trimesh
    tm = trimesh.load(path)
    tm.merge_vertices()
    return m3d.Manifold(m3d.Mesh(vert_properties=np.asarray(tm.vertices, np.float32), tri_verts=np.asarray(tm.faces, np.uint32)))


def lage_suche(outline, fps, raised, blocked, zones_geb, notches, mouths, zapfen, kasten=None, step=0.1, y0=20.0, y1=110.0):
    """Freie Lagen des Docks entlang des Ostrandes (xe fest): Liste (yc, [Gründe]) in `step`-Schritten. Alles in Plattenkoordinaten.
    Gründe: Rand (Kopf zu nah an der Plattenkante), Luft (Kopf näher als AIR_MARGIN an Gebäude, Hof, erhabener Schrift, Nordpfeil, Aufbauten), Mulde (Wand zu anderen Mulden oder Hof
    unter WALL_MIN), Tasche (zu nah an einer Fadentasche), Zapfen, Dockzone (überlappt die Dockzone eines Gebäudes), Notch (Eckaussparung des Unterkastens), Kasten (Dockzone
    stößt an Wand, Stütze oder Zapfen des gedruckten Unterkastens)."""
    lage = dict(DISPLAY_LAGE)
    s1, s2 = satz(1), satz(2)
    heads = [Polygon(head_poly(s1)), Polygon(head_poly(s2))]
    off2 = body_xe(s2, lage) - lage["xe"]
    air = unary_union([g.buffer(AIR_MARGIN) for g in fps.values()] + [raised.buffer(AIR_MARGIN)])
    inner = outline.buffer(-3.5, join_style=2)
    others = [z.buffer(1.0) for z in zones_geb]
    notch = [sbox(*n).buffer(1.0) for n in notches]
    zap = unary_union([zapfen_c.buffer(0.0) for zapfen_c in zapfen])
    rows = []
    for yc in np.arange(y0, y1 + 1e-9, step):
        yc = round(float(yc), 3)
        lg = dict(lage, yc=yc)
        h = unary_union([at(heads[0], lg["xe"], yc), at(heads[1], lg["xe"] + off2, yc), at(heads[1], lg["xe"], yc)])
        mu = mulde_poly(lg)
        z = dock_zone(lg)
        why = []
        if not inner.contains(h):
            why.append("Rand")
        if h.intersects(air):
            why.append("Luft")
        if mu.distance(blocked) < WALL_MIN:
            why.append("Mulde")
        if mu.distance(mouths) < WALL_FADEN:
            why.append("Tasche")
        if mu.distance(zap) < WALL_MIN:
            why.append("Zapfen")
        if any(z.intersects(o) for o in others):
            why.append("Dockzone")
        if any(z.intersects(n) for n in notch):
            why.append("Notch")
        if kasten is not None and z.intersects(kasten):
            why.append("Kasten")
        rows.append((yc, why))
    return rows


def intervals(rows, step=0.1):
    iv = []
    for yc, why in rows:
        if not why:
            if iv and yc - iv[-1][1] < step * 1.5:
                iv[-1][1] = yc
            else:
                iv.append([yc, yc])
    return iv


def main():
    import argparse
    import contextlib
    import io

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon as MPoly
    import trimesh

    from plug import campus as C
    from plug import campus_underside as U
    from plug.geom import to_tm
    from plug.power import build_concept as BC
    from plug.power import params as PP

    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--keine-bilder", action="store_true")
    a = ap.parse_args()
    os.makedirs(PREV, exist_ok=True)
    plate, rep, models, places, outline, hof_solid = C.build(P.SCALE_PLAN)
    info, lay = C.DISPLAY_INFO, C.UNTEN_INFO["lay"]
    minx, miny, T = info["minx"], info["miny"], info["T"]
    sh = lambda g: affinity.translate(g, -minx, -miny)             # noqa: E731 (Rohkoordinaten -> Plattenkoordinaten)
    s1, s2, lage = satz(1), satz(2), DISPLAY_LAGE
    ok = True
    print("Passprobe Display-Dock (Lage x = %.1f, y = %.1f; Satz %d gebaut)" % (lage["xe"], lage["yc"], SATZ))

    # ---- 1. Lagesuche am Ostrand
    fps = {k: sh(v[1]) for k, v in models.items()}
    raised = sh(U.section_poly(plate, T + 0.31))                    # alles, was mehr als 0,31 über der Plattenoberfläche steht: Schrift, Nordpfeil, Aufbauten
    mu_plate = mulde_poly()
    blocked = sh(C.UNTEN_INFO["blocked"]).difference(mu_plate.buffer(0.01))
    mouths = unary_union([sh(U.mouth_poly(c)) for c in lay["faden"]])
    zap = [sh(U.zapfen_circle(p, U.LOCH_FASE)) for p in lay["pins"]]
    notches = [tuple(np.array(c["notch"]) - np.array([minx, miny, minx, miny])) for c in lay["faden"]]
    zones = [sh(z) for z in info["zones"]]
    uk = load_stl(UK_STL)
    kas = unary_union([U.section_poly(uk, z) for z in (14.2, 15.0, 16.0, 17.0, 17.5)])        # Wände, Stützen und Zapfen im Bereich des Steckerraums (Plattenkoordinaten)
    rows = lage_suche(sh(outline), fps, raised, blocked, zones, notches, mouths, zap, kas)
    iv = intervals(rows)
    print("  Lagesuche am Ostrand (Kopf bei x = %.1f, y 20 bis 110 in 0,1-mm-Schritten): freie Lagen y = %s" % (lage["xe"], "; ".join("%.1f bis %.1f" % tuple(i) for i in iv)))
    south = iv[0][0]
    why_south = [w for yc, w in rows if abs(yc - (south - 0.1)) < 1e-6]
    print("  südlichste freie Lage y = %.1f, eine Stufe weiter südlich gesperrt durch: %s; gewählt: y = %.1f -> %s" % (
        south, ", ".join(why_south[0]) if why_south else "–", lage["yc"], "ok" if abs(south - lage["yc"]) < 0.051 else "WEICHT AB"))
    ok &= abs(south - lage["yc"]) < 0.051
    head_y = (lage["yc"] - s1["W"] / 2, lage["yc"] + s1["W"] / 2)
    n_top = max(g.bounds[3] for g in getattr(raised.intersection(sbox(90, 0, 115, 20)), "geoms", [raised.intersection(sbox(90, 0, 115, 20))]))
    print("  Kopf y %.2f bis %.2f; Oberkante des erhabenen Nordpfeils und der Schrift im Ostteil y = %.2f (Luft %.2f mm, gefordert %.1f)" % (head_y[0], head_y[1], n_top, head_y[0] - n_top, AIR_MARGIN))
    ok &= head_y[0] - n_top >= AIR_MARGIN - 0.05
    hoch = fps["06_city_hochhaus"]
    print("  City-Hochhaus: y %.1f bis %.1f, x %.1f bis %.1f (liegt rechts, nördlich, des Kopfes: Abstand in y %.1f mm); Hörsaalgebäude dahinter: y %.1f bis %.1f, östlichster Punkt x = %.1f" % (
        hoch.bounds[1], hoch.bounds[3], hoch.bounds[0], hoch.bounds[2], hoch.bounds[1] - head_y[1], fps["03_hoersaalgebaeude"].bounds[1], fps["03_hoersaalgebaeude"].bounds[3], fps["03_hoersaalgebaeude"].bounds[2]))

    # ---- 2. Kopf gegen die Gebäude (Weltlage, z = 0 Plattenoberfläche)
    print("  Kopf in der Luft gegen die Gebäude (STL aus stl/steckmodul_campus/gebaeude/, um die Verschiebung auf der Platte versetzt; Überschneidung mm³ / kleinster Abstand mm, gefordert 0 und mindestens %.1f):" % AIR_MARGIN)
    from plug.display import body4 as B
    parts, _ = B.parts()
    real = parts["body"] + parts["lid"] + parts["blende"]
    h1 = pose(head_prism(s1), s1, minx, miny, 0.0)
    h2 = pose(head_prism(s2), s2, minx, miny, 0.0)
    h2r = pose(real, s2, minx, miny, 0.0)
    geb = {}
    for slug in SLUGS:
        m = load_stl(os.path.join(GEB, "%s_1zu%d.stl" % (slug, P.SCALE_PLAN)))
        dx_, dy_ = C.SHIFTS.get(slug, (0.0, 0.0))                  # die STL liegen in Weltlage, die Platte rückt die Gebäude je Naht auseinander (C.SHIFTS, aus C.build)
        m = m.translate([dx_, dy_, 0.0])
        geb[slug] = m
        v1, v2, v3 = vol(h1, m), vol(h2, m), vol(h2r, m)
        g1, g2, g3 = float(h1.min_gap(m, 50.0)), float(h2.min_gap(m, 50.0)), float(h2r.min_gap(m, 50.0))
        good = max(v1, v2, v3) < 0.05 and min(g1, g2, g3) >= AIR_MARGIN
        ok &= good
        gs = ["%5.1f" % g_ if g_ < 50.0 else "≥ 50 "for g_ in (g1, g2, g3)]
        print("    %-22s Hülle erster Satz %.3f / %s · Hülle zweiter Satz %.3f / %s · Körper mit Blende und Rückdeckel (zweiter Satz) %.3f / %s  %s" % (slug, v1, gs[0], v2, gs[1], v3, gs[2], "ok" if good else "FEHLER"))
    ctrl = pose(head_prism(s1), s1, minx, miny, 0.0, dy=30.0)
    vc = max(vol(ctrl, m) for m in geb.values())
    print("    Kontrolle: Kopf um 30 mm nach Norden verschoben stößt an ein Gebäude (Hochhaus): %.1f mm³ -> %s" % (vc, "ok" if vc > 0.05 else "FEHLER"))
    ok &= vc > 0.05
    # alle sechs Gebäude und der Körper gleichzeitig: Gebäude gegen Platte (Fuß in den Mulden), Körper gegen Platte
    plate0 = plate.translate([0, 0, -T])
    vb = max(vol(m, plate0) for m in geb.values())
    print("    Gebäude (alle sechs) gegen die Platte mit Display-Dock: größte Überschneidung %.3f mm³ (Fuß in den Mulden, Spiel %.2f)" % (vb, P.OUTLINE_CLR_T))

    # ---- 3. Dockzone gegen den gedruckten Unterkasten (Stand 7)
    print("  Dockzone gegen den gedruckten Unterkasten (stl/steckmodul_unterkasten/U_unterkasten.stl, Plattenkoordinaten, Höhe %.1f; Platte mit der Unterseite auf z = %.1f):" % (UK_H, UK_H))
    plate_k = plate.translate([-minx, -miny, UK_H])
    v_pk = vol(plate_k, uk)
    ctrl_k = plate_k.translate([0.3, 0.0, 0.0])
    v_ck = vol(ctrl_k, uk)
    print("    Platte (mit Display-Dock) auf dem Kasten: Überschneidung %.4f mm³; Kontrolle 0,3 mm seitlich verschoben: %.2f mm³ -> %s" % (v_pk, v_ck, "ok" if v_pk < 0.05 and v_ck > 0.05 else "FEHLER"))
    ok &= v_pk < 0.05 and v_ck > 0.05
    z_poly = dock_zone()
    zb = ext_poly(z_poly, UK_H - STECKERRAUM, UK_H)
    uk_k = uk
    v_z = vol(zb, uk_k)
    print("    Dockzone %.1f × %.1f mm von z = %.1f bis %.1f (Steckerraum %.1f) gegen den Kasten: Überschneidung %.4f mm³" % (
        z_poly.bounds[2] - z_poly.bounds[0], z_poly.bounds[3] - z_poly.bounds[1], UK_H - STECKERRAUM, UK_H, STECKERRAUM, v_z))
    ok &= v_z < 0.05
    # nächste Struktur des Kastens in der Draufsicht (Steckerraum-Höhen) und Kontrolle mit verschobener Dockzone
    from shapely.ops import nearest_points
    p0, p1 = nearest_points(z_poly, kas)
    dist = z_poly.distance(kas)
    shift = (p1.x - p0.x, p1.y - p0.y)
    n = math.hypot(*shift) or 1.0
    k = (dist + 0.3) / n
    zb_c = ext_poly(affinity.translate(z_poly, shift[0] * k, shift[1] * k), UK_H - STECKERRAUM, UK_H)
    v_zc = vol(zb_c, uk_k)
    print("    nächste Struktur des Kastens an der Dockzone: %.1f mm bei (%.1f | %.1f); Kontrolle: Dockzone um %.1f mm dorthin verschoben: %.2f mm³ -> %s" % (
        dist, p1.x, p1.y, dist + 0.3, v_zc, "ok" if v_zc > 0.05 else "FEHLER"))
    ok &= v_zc > 0.05
    with contextlib.redirect_stdout(io.StringIO()):
        v = BC.variant(P.SCALE_PLAN)
    fach, esp = Polygon(v["fach_poly"][0] if isinstance(v["fach_poly"][0][0], (list, tuple)) else v["fach_poly"]), Polygon(v["elec"][0] if isinstance(v["elec"][0][0], (list, tuple)) else v["elec"])
    posts = [Polygon(p["r"]) for p in v["posts"]]
    uk_posts = [g for g in getattr(U.section_poly(uk, 10.0), "geoms", []) if g.area < 60 and g.bounds[2] - g.bounds[0] < 8]
    notch_v = [Polygon(x["notch"]) for x in v["vs"]]
    sw = PP.SW_Y
    items = [("Stützen (Raster 40 mm, %d im gedruckten Kasten, 6 × 6)" % len(uk_posts), unary_union(uk_posts) if uk_posts else unary_union(posts)),
             ("Zapfen (20 | 20) und (100 | 180)", unary_union([Point_(p) for p in ((20.0, 20.0), (100.0, 180.0))])),
             ("Fach der Powerbank (%.0f × %.0f, Nordkante)" % (fach.bounds[2] - fach.bounds[0], fach.bounds[3] - fach.bounds[1]), fach),
             ("ESP-Fläche (%.0f × %.1f)" % (esp.bounds[2] - esp.bounds[0], esp.bounds[3] - esp.bounds[1]), esp),
             ("Eckaussparungen des Kastens (Faden-V, vier Ecken)", unary_union(notch_v)),
             ("Schalterloch (13,7 × 9,0 in der Westwand bei y = %.0f)" % sw, sbox(0.0, sw - 6.85, PP.UK_WALL, sw + 6.85)),
             ("Außenwand (2,4)", sh(outline).difference(sh(outline).buffer(-PP.UK_WALL))),
             ("Dockzonen der sechs Gebäude", unary_union(zones))]
    print("    Abstand der Dockzone des Displays zu den Teilen des Kastens (Draufsicht):")
    for name, g in items:
        print("      %-62s %6.1f mm" % (name, z_poly.distance(g)))
    ok &= all(z_poly.distance(g) > 0.0 for _, g in items)

    # ---- 4. Bilder
    colors = {"01_paulinum": "#d8c9ad", "02_neues_augusteum": "#c9b99a", "03_hoersaalgebaeude": "#b9c4d0", "04_seminargebaeude": "#a9b8a3", "05_institutsgebaeude": "#c8a9a0", "06_city_hochhaus": "#a8b4c8"}
    if not a.keine_bilder:
        import preview
        meshes = [(to_tm(plate0), "#8896a5")]
        for slug in SLUGS:
            meshes.append((to_tm(geb[slug]), colors[slug]))
        col = dict(body="#c9a227", lid="#d7845b", blende="#3a3f4a", pcb="#3f8f5a", glass="#1d2330")
        for key in ("body", "lid", "blende", "pcb", "glass"):
            meshes.append((to_tm(pose(parts[key], s2, minx, miny, 0.0)), col[key]))
        preview.render(meshes, size=(1500, 1000), azim=0, elev=25).save(os.path.join(PREV, "steckplatte_mit_display_von_osten.png"))
        preview.render(meshes, size=(1000, 1300), azim=-90, elev=89).save(os.path.join(PREV, "steckplatte_mit_display_oben.png"))
        print("  Bilder: vorschau/steckmodul_campus/steckplatte_mit_display_von_osten.png, steckplatte_mit_display_oben.png")
        fig, ax = plt.subplots(figsize=(7.2, 13.0), dpi=110)

        def fill(g, **kw):
            for q in getattr(g, "geoms", [g]):
                if q.is_empty or q.geom_type != "Polygon":
                    continue
                ax.add_patch(MPoly(list(q.exterior.coords), closed=True, **kw))
                for r in q.interiors:
                    ax.add_patch(MPoly(list(r.coords), closed=True, fc="white", ec="none"))
        fill(sh(outline), fc="#f3f1ec", ec="#555")
        fill(kas, fc="#8f9aa6", ec="#4a5560", lw=0.6, alpha=0.9)
        fill(fach, fc="#cfe3f5", ec="#2b6fb3", lw=1.2, alpha=0.7)
        fill(esp, fc="#d4efd0", ec="#2f8f3a", lw=1.2, alpha=0.7)
        fill(unary_union(notch_v), fc="#f7d0d0", ec="#c33", lw=1.0)
        fill(items[5][1], fc="#ffd9a8", ec="#d9730d", lw=1.2)
        for z in zones:
            fill(z, fc="none", ec="#777", lw=1.0, ls="--")
        fill(mu_plate, fc="#e7c64a", ec="#7a5d00", lw=1.2, alpha=0.9)
        ax.add_patch(MPoly(list(at(Polygon(head_poly(s1)), lage["xe"], lage["yc"]).exterior.coords), closed=True, fc="none", ec="#7a5d00", lw=1.2, ls=":"))
        fill(z_poly, fc="none", ec="#b0148f", lw=2.0)
        for x_, y_ in pin_xy():
            ax.plot([x_], [y_], "o", ms=3, color="#222")
        for p_ in ((20.0, 20.0), (100.0, 180.0)):
            ax.plot([p_[0]], [p_[1]], "o", ms=7, mfc="none", mec="k")
        for g in mouths.geoms if hasattr(mouths, "geoms") else [mouths]:
            fill(g, fc="none", ec="#999", lw=0.8)
        for slug in SLUGS:
            fill(fps[slug], fc="none", ec="#bbb", lw=0.6)
        ax.annotate("Dockzone Display\n(Steckerraum 3,5 über der Powerbank)", (z_poly.bounds[0], z_poly.bounds[3]), (20, 76), arrowprops=dict(arrowstyle="->", color="#b0148f"), color="#b0148f", fontsize=8)
        ax.annotate("Mulde (Fuß)", (mu_plate.bounds[2], mu_plate.centroid.y), (101, 62), arrowprops=dict(arrowstyle="->", color="#7a5d00"), color="#7a5d00", fontsize=8)
        ax.text(2, 218, "grau: Wände, Stützen, Zapfen des Kastens (Schnitt z = 14,2 bis 17,5)\nblau: Fach Powerbank · grün: ESP-Fläche · rot: Eckaussparungen · orange: Schalterloch\nstrichliert: Dockzonen der Gebäude · gelb: Display-Mulde, gepunktet Kopf (Luft)", fontsize=6.5, va="top")
        ax.set_xlim(-2, 118)
        ax.set_ylim(-2, 223)
        ax.set_aspect("equal")
        ax.set_title("Display-Dock am Ostrand und der gedruckte Unterkasten (Stand 7), Draufsicht, Norden oben", fontsize=9)
        fig.savefig(os.path.join(PREV, "display_dock_unterkasten.png"), bbox_inches="tight")
        print("  Bild: vorschau/steckmodul_campus/display_dock_unterkasten.png")
    print("keine Kollisionen" if ok else "ACHTUNG: Kollision oder Abstand zu klein")
    if not ok:
        raise SystemExit(1)


def Point_(xy):
    from shapely.geometry import Point
    return Point(xy).buffer(2.15, 24)


if __name__ == "__main__":
    main()
