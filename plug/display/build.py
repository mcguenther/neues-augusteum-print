#!/usr/bin/env python3
"""STL für den ersten Probedruck des Display-Gebäudes (Körper E4, Standardwerte) nach stl/steckmodul_display/.

Teile (Maße aus plug/display/params.py und body4.py, alles Planwerte, nichts davon ist gedruckt):
  D1_koerper.stl       Körper: Kopf mit Modultasche (von vorn), Rückenkeil mit Kabelkammer und Kabelfenster, Hals mit Buchsentasche (von unten offen, Schultern oben) und Aderschlitz, Fuß mit Kodierecke
  D2_rueckdeckel.stl   Rückdeckel der Kabelkammer (schräg), mit vier Rastnasen
  D3_frontblende.stl   Frontblende mit Sichtfenster und vier Zapfen (durch die Befestigungslöcher des Moduls)
  D4_mini_platte.stl   Mini-Platte: Mulde (Fußumriss plus Spiel) mit Einführfase, vier Pin-Löcher, flache Unterseite 14,6 mm
Die Dateien liegen in Druckausrichtung (Bett z = 0). Prüfungen: dicht, keine Kollisionen im Zusammenbau, Verdrehsicherung, Überhang je Lage.

Aufruf (aus dem Wurzelverzeichnis):  python3 -m plug.display.build    (ca. 2 min)
"""
import math
import os
import subprocess
import sys
import zipfile

import manifold3d as m3d
import numpy as np
import trimesh
from shapely.geometry import Polygon, box as sbox

import generate as G
import preview as PV
from plug import buildings as BU
from plug import campus as C
from plug.display import body4 as B
from plug.display import params as D
from plug.fit_test.generator import overhangs
from plug.geom import box, to_tm, union, vol_int
from plug.power import build_concept as BC
from plug.testcase import params as TP

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(HERE, "stl", "steckmodul_display")
PREV = os.path.join(HERE, "vorschau", "steckmodul_display")
ZIP = "display_probedruck.zip"
MARGIN = 6.0           # E  Rand der Mini-Platte um die Mulde (Wand 6,0; die Platte liegt unter dem Kopf, 0,3 Luft)
LAYER = BU.LAYER


# --------------------------------------------------------------------------
# Teile
# --------------------------------------------------------------------------
def mulde_cut(poly, F, clr, ch):
    """Mulde wie plug/campus.py mulde_body, aber mit eigenem Spiel clr: voller Umriss bis zur Fußunterkante (-F), oben Einführfase ch in Schichtstufen."""
    n = BC.n_layers(ch)
    dz = ch / n
    parts = [G.extrude(poly.buffer(clr, join_style=2), -F, -ch + 0.01)]
    for k in range(n):
        top = 1.0 if k == n - 1 else -ch + dz * (k + 1) + 0.01
        parts.append(G.extrude(poly.buffer(clr + dz * (k + 0.5), join_style=2), -ch + dz * k, top))
    return union(parts)


def mini_plate(d):
    """Mini-Platte in der Lage des Zusammenbaus (z = 0 Oberseite, Unterseite bei -T): Mulde = Fußumriss + CLR_MULDE, Einführfase 0,5, vier Pin-Löcher mit Fase."""
    dd = TP.dims_plan()
    F, T = dd["F"], C.plate_thickness(dd)
    fp = Polygon(B.foot_poly(d))
    x0, x1 = d["x_bw"] - D.CLR_MULDE - MARGIN, d["x_fe"] + D.CLR_MULDE + MARGIN
    yh = d["NW"] / 2 + D.CLR_MULDE + MARGIN
    outline = sbox(x0, -yh, x1, yh)
    plate = BC.slab_ch(outline, 0.0, T, TP.EF_CH_T)                     # Bettkante gefast (Elefantenfuß), Bett z = 0
    plate = plate ^ C.top_edge(outline, T, TP.PLATE_TOP_CH_T)           # obere Außenkante gefast
    cut = [mulde_cut(fp, F, D.CLR_MULDE, TP.MULDE_CH_T).translate([0, 0, T])]
    sx = (d["x_s0"] + d["x_s1"]) / 2
    for h in C.pin_holes(dd):                                           # Pin-Reihe in x: quer legen (y) und an die Schachtmitte setzen
        cut.append(h.rotate([0, 0, 90]).translate([sx, 0.0, T]))
    plate = plate - union(cut)
    return plate.translate([0, 0, -T]), T


def place_bed(m, rot=None):
    """Teil mit der tiefsten Stelle auf z = 0 und der Mitte der Grundfläche auf x = y = 0 ablegen."""
    b = m.bounding_box()
    return m.translate([-(b[0] + b[3]) / 2, -(b[1] + b[4]) / 2, -b[2]])


def print_pose(P, aux, d, plate):
    """Alle Teile in Druckausrichtung."""
    body = P["body"].translate([0, 0, -d["foot"]])                      # Fuß unten auf dem Bett
    nx, nz = aux["normal"]                                              # Außennormale der Schräge (oben/Westen) nach unten drehen
    c, s = -nz, nx
    lid = P["lid"].transform([[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0]])
    blende = P["blende"].rotate([0, 90, 0])                             # (x, y, z) -> (z, y, -x): Außenfläche (x = 0) liegt unten, Zapfen zeigen nach oben
    return {"D1_koerper": place_bed(body), "D2_rueckdeckel": place_bed(lid), "D3_frontblende": place_bed(blende),
            "D4_mini_platte": place_bed(plate)}


# --------------------------------------------------------------------------
# Prüfung
# --------------------------------------------------------------------------
def minutes(man):
    """Druckzeit grob geschätzt (Pfadlänge = Fläche / 0,42, 60 mm/s, Zuschlag 1,5 s je Lage, Mindestzeit 6 s, Start 6 min); nicht kalibriert."""
    b = man.bounding_box()
    sec, z = 0.0, 0.1
    while z < b[5]:
        a = man.slice(z).area()
        sec += max((a / 0.42) / 60.0 + 1.5, 6.0) if a > 0 else 0.0
        z += LAYER
    return sec / 60.0 + 6.0


class Report:
    def __init__(self):
        self.lines = []

    def __call__(self, txt=""):
        print(txt)
        self.lines.append(txt)


def render_images(P, plate, d, parts, rep):
    """Vorschaubilder: Zusammenbau, Schnitt, Rückseite, Teile in Druckausrichtung."""
    os.makedirs(PREV, exist_ok=True)
    col = dict(body="#c9a227", lid="#d7845b", blende="#3a3f4a", cassette="#8fb573", pcb="#3f8f5a", glass="#1d2330", header="#222222", plate="#e4e0d8")
    def mk(man, key):
        return (to_tm(man), col[key])
    names = ["body", "lid", "blende", "cassette", "pcb", "glass", "header", "pins", "plate"]
    src = {k: P[k] for k in names if k != "plate"}
    src["plate"] = plate
    src["pins"] = P["pins"]
    col["pins"] = "#c0c0c0"
    full = [mk(m, k) for k, m in src.items()]
    title = "Display-Gebäude E4, Probedruck (Standardwerte)"
    sub = "Körper (Buchsentasche integriert), Rückdeckel, Frontblende mit Kappe, Mini-Platte; mit Display-Modul (Attrappe: Platine, Glas, Header)"
    out = []
    im = PV.render(full, size=(1000, 760), azim=-32, elev=24)
    p = os.path.join(PREV, "zusammengebaut.png")
    PV.caption(im, title, sub).save(p, optimize=True)
    out.append(p)
    im = PV.render(full, size=(1000, 760), azim=-148, elev=26)
    p = os.path.join(PREV, "rueckseite.png")
    PV.caption(im, "Display-Gebäude E4: Rückseite mit Rückdeckel", sub).save(p, optimize=True)
    out.append(p)
    cutbox = box(-500, 500, -500, 0.0, -500, 500)
    sect = [mk(m - cutbox, k) for k, m in src.items()]
    im = PV.render(sect, size=(1000, 760), azim=-90, elev=6)
    p = os.path.join(PREV, "schnitt.png")
    PV.caption(im, "Display-Gebäude E4: Längsschnitt in der Mitte", "Blick von Süden; Fuß in der Mulde, Buchse in der Tasche, Schultern, Kabelkammer, Modul in der Tasche").save(p, optimize=True)
    out.append(p)
    # Teile nebeneinander in Druckausrichtung
    x, row = 0.0, []
    cols = ["#c9a227", "#d7845b", "#3a3f4a", "#e4e0d8"]
    for (name, man), c in zip(parts.items(), cols):
        b = man.bounding_box()
        row.append((to_tm(man.translate([x - b[0], -(b[1] + b[4]) / 2, 0])), c))
        x += (b[3] - b[0]) + 8.0
    im = PV.render(row, size=(1100, 560), azim=-35, elev=32)
    p = os.path.join(PREV, "teile.png")
    PV.caption(im, "Probedruck: Teile in Druckausrichtung", "links nach rechts: D1 Körper, D2 Rückdeckel, D3 Frontblende, D4 Mini-Platte; so liegen die Dateien im ZIP").save(p, optimize=True)
    out.append(p)
    return out


def write_readme(info, tot, d, gap):
    de = lambda v, n=1: ("%.*f" % (n, v)).replace(".", ",")
    t = {k: info[k]["min"] for k in info}
    txt = f"""DISPLAY-GEBÄUDE E4, ZWEITER SATZ (alles in einem, Maßstab 1:1300)
================================================================

Gebaut nach Probedruck 1 und der Modulprobe 1 und 2. Alle Werte sind Planwerte (plug/display/params.py), der Körper als Ganzes ist nicht gedruckt.
Aus den Proben übernommen: Modul als {de(D.DISP['pcb_w'])} × {de(D.DISP['pcb_h'])} × {de(D.DISP['mod_t'])} angenommen (Tasche {de(D.DISP['pcb_w'] + 2 * D.CLR_W, 2)} × {de(D.DISP['pcb_h'] + D.CLR, 2)} × {de(d['slot_t'], 2)}, Luft {de(D.CLR_W, 2)} je Seite),
Zapfen mit Kegelspitze P1 (Ø {de(D.PEG_TIP_D, 1)} auf {de(D.PEG_D, 1)} über {de(D.PEG_TAPER_L, 1)} mm) im Sackloch Ø {de(D.PEG_HOLE_D, 2)} (Ø 2,5 passte gut), Kappe mit Lippe {de(D.LIP_T, 1)}, Fuß-Fase 2,0 und Spiel zur Mulde 0,15
(Probedruck 1: der Rest war in Ordnung). Neu und ungeprüft: die Buchsentasche im Hals (statt der Kassette K0), der kleinere Hals, die Schultern, der Rückdeckel zur niedrigeren Oberkante.

Teile (je 1 Stück)
  D1_koerper.stl       Körper {info['D1_koerper']['ext']} mm, {de(info['D1_koerper']['vol'])} cm³: Kopf mit Tasche (oben und vorn offen), Kabelfenster, Rückenkeil mit Kammer, Hals mit Buchsentasche, Fuß mit Kodierecke
  D2_rueckdeckel.stl   Rückdeckel {info['D2_rueckdeckel']['ext']} mm
  D3_frontblende.stl   Frontblende mit Lippe (Kappe), Fenster und vier Zapfen {info['D3_frontblende']['ext']} mm
  D4_mini_platte.stl   Mini-Platte {info['D4_mini_platte']['ext']} mm: Mulde mit Kodierecke, Einführfase 0,5, vier Pin-Löcher mit Fase, Unterseite flach

Buchsentasche im Hals: {de(D.KASS_W, 2)} × {de(D.KASS_D, 2)} mm, {de(D.ZP, 1)} mm hoch von der Fußunterkante, unten offen mit Einführfase {de(D.ENTRY_CH, 1)}. Oben liegen Schultern ({de(d['z_cass'] - d['foot'] - D.ZP, 1)} mm dick) mit dem
Aderschlitz ({de(9.2, 1)} breit, ganze Tiefe der Tasche). Die Buchse wird von unten eingeschoben; die Schultern halten sie gegen die Steckkraft.

Druckausrichtung (so liegen die Dateien schon)
  D1 Körper    Fuß unten (Tasche öffnet am Bett), Kopf oben. Kein Support für die Decke mehr (Tasche oben offen). Support braucht nur noch die Unterseite des Kopfs über dem Fuß ({de(info['D1_koerper']['krag'], 0)} mm² Kragstück laut Lagenprüfung,
               alles von der Bauplatte aus erreichbar: Support „nur vom Bett“ genügt).
  D2 Rückdeckel   flach, die schräge Außenfläche liegt auf dem Bett.
  D3 Frontblende  flach, Außenfläche (mit dem Fenster) auf dem Bett, Zapfen und Lippe zeigen nach oben.
  D4 Mini-Platte  flach, Unterseite auf dem Bett; Muldenboden 0,4 mm ist die unterste Schicht, kein Support.
Einstellungen wie bisher (plug/slicer.md): Bambu A1, PLA, Düse 0,4, Schichthöhe 0,2, Wände 3 oder mehr, kein Brim, Kante ohne Elefantenfuß-Kompensation. Druckzeit geschätzt (nicht kalibriert):
D1 {t['D1_koerper']:.0f} min, D2 {t['D2_rueckdeckel']:.0f}, D3 {t['D3_frontblende']:.0f}, D4 {t['D4_mini_platte']:.0f} min. Bitte die echten Zeiten melden.

Prüfbericht: pruefbericht.txt (dicht, keine Kollisionen im Zusammenbau, Verdrehsicherung, Überhang je Lage).

Zusammenbau
  1. Dupont-Buchse mit vier Adern (etwa 60 mm) crimpen. Adern von unten durch die Buchsentasche und den Aderschlitz in die Kammer fädeln (Rückdeckel ist ab), Buchse von unten in die Tasche schieben, bis sie an den Schultern anliegt.
  2. Adern an die Pinenden des Moduls löten (Header bleibt am Modul), Reserve (3 bis 4 cm) als Schleife in die Kammer legen.
  3. Modul von oben oder vorn in die Tasche setzen (Pins zuerst durch das Kabelfenster).
  4. Frontblende mit den Zapfen durch die Löcher stecken, die Lippe deckt die Tasche oben ab; Zapfen enden im Sackloch.
  5. Rückdeckel von hinten in die schräge Öffnung drücken (Rastnasen in die Nuten).
  6. Körper in die Mini-Platte stecken (die Kodierecke vorn Süd lässt nur eine Lage zu), Luft zwischen Kopf und Platte {de(d['z_hb'])} mm.

Verpolung: Die Buchsentasche ist symmetrisch, die Buchse passt in zwei Lagen. Gedreht liegen GND und 3,3 V (und SDA, SCL) vertauscht an den Pins, das Modul verträgt höchstens 3,5 V. Pin 1 der Buchse beim Einsetzen
markieren (Strich am Körper unten) und vor dem ersten Stecken am Modul durchmessen. Eine Kodierung in der Tasche ist ein Vorschlag für den nächsten Satz.

Zu fühlen und zu melden: Buchse in der Tasche (Sitz, Schultern, geht der Draht durch den Schlitz?), Körper in die Mulde (ohne Kraft, Fase fängt, wackelfrei, verdreht nicht aufsetzbar), Modul in der Tasche, Zapfen (wie in Modulprobe 2),
Frontblende bündig mit Lippe, Rückdeckel (Rast, Spiel), Kabelreserve in der Kammer, trifft die Buchse die Pins der Mini-Platte (Winkelleiste geklebt)?
"""
    open(os.path.join(OUT, "README.txt"), "w", encoding="utf-8").write(txt)


def main():
    rep = Report()
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(PREV, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith((".stl", ".zip", ".txt")):
            os.remove(os.path.join(OUT, f))
    d = B.dims()
    P, aux = B.parts(d)
    plate, T = mini_plate(d)
    parts = print_pose(P, aux, d, plate)

    rep("Display-Gebäude E4: zweiter Satz D1 bis D4 (Buchsentasche integriert, Kappe, Zapfen P1) (plug/display/params.py, body4.py)")
    rep("Buchsentasche %.2f × %.2f, %.1f hoch, Schultern bis %.2f über der Platte (Boden der Kammer); Spiel Mulde %.2f je Seite; Hals %.2f × %.2f" % (
        D.KASS_W, D.KASS_D, D.ZP, D.KASS_TOP, D.CLR_MULDE, d["NW"], d["KD"]))
    rep("Kopf %.1f breit, %.1f tief, %.1f hoch (Oberkante), Unterkante %.2f über der Platte; Schräge hinten %.1f bis %.1f; Fuß %.2f × %.2f mit Kodierecke %.1f" % (
        d["W"], -d["x_back"], d["z_top"], d["z_hb"], d["z_rear"], d["z_top"], d["x_fe"] - d["x_bw"], d["NW"], D.KEY))

    rep("\nTeile (Druckausrichtung, Bett z = 0):")
    info = {}
    for name, man in parts.items():
        tm = to_tm(man)
        tm.export(os.path.join(OUT, name + ".stl"))
        ov = overhangs(man, name)
        ue = BU.ueberhang(man)
        info[name] = dict(ext=("%.1f × %.1f × %.1f" % tuple(tm.extents)).replace(".", ","), vol=tm.volume / 1000.0, krag=ue["krag_mm2"], min=minutes(man), watertight=tm.is_watertight, status=man.status().name)
        rep("  %-20s %6.1f × %6.1f × %5.1f mm  %6.2f cm³  dicht=%s (Manifold: %s)" % (name + ".stl", *tm.extents, tm.volume / 1000.0, tm.is_watertight, man.status().name))
        rep("      waagerechte Decken: %s" % ("; ".join("z=%.1f: %.0f mm² (%.1f × %.1f)" % f for f in sorted(ov["flat"], key=lambda t: -t[1])[:6]) or "keine"))
        rep("      Lagenprüfung (Überhang je 0,2 mm über %.2f): Brücken %.1f mm² (bis %.1f mm), Kragstücke %.1f mm² (bis %.1f mm)" % (
            BU.UEBERHANG_T, ue["bruecke_mm2"], ue["bruecke_mm"], ue["krag_mm2"], ue["krag_mm"]))
        for s in sorted(ue["stellen"], key=lambda s: -s[2])[:8]:
            rep("         %s bei z=%.1f: %.0f mm², Reichweite %.1f mm, Mitte (%.1f, %.1f)" % s)

    rep("\nPrüfung der Passungen im Zusammenbau (Überschneidungsvolumen, mm³; muss 0 sein):")
    bad = 0

    def chk(txt, v, limit=0.05, must_collide=False):
        nonlocal bad
        ok = (v > limit) if must_collide else (v <= limit)
        bad += (not ok)
        rep("  %-78s %9.3f  %s" % (txt, v, "ok" if ok else "FEHLER"))

    body, cas = P["body"], P["cassette"]                       # cas = Attrappe der Dupont-Buchse
    chk("Körper und Dupont-Buchse 10,16 × 2,54 × 14 in der Tasche", vol_int(body, cas))
    chk("Körper und Modulplatine", vol_int(body, P["pcb"]))
    chk("Körper und Modulglas", vol_int(body, P["glass"]))
    chk("Körper und Header samt Pins (Kabelfenster)", vol_int(body, P["header"]) + vol_int(body, P["pins"]))
    chk("Körper und Rückdeckel", vol_int(body, P["lid"]))
    chk("Körper und Frontblende (Zapfen im Sackloch, Blende im Rücksprung)", vol_int(body, P["blende"]))
    chk("Frontblende und Modulplatine, Header (Zapfen durch die Löcher)", vol_int(P["blende"], P["pcb"]) + vol_int(P["blende"], P["header"]))
    rep("  Hinweis Frontblende und Modulglas (Lage des Glases nur aus dem Foto, ± 0,5): Überschneidung %.3f mm³ (obere Zapfen laufen an der Glaskante entlang)" % vol_int(P["blende"], P["glass"]))
    chk("Mini-Platte und Körper (Fuß in der Mulde, Spiel %.2f je Seite)" % D.CLR_MULDE, vol_int(plate, body))
    chk("Mini-Platte und Buchse (Buchse steht auf dem Muldenboden)", vol_int(plate, cas))
    chk("Mini-Platte und Winkelleiste mit Pins (Pins in den Löchern)", vol_int(plate, P["leiste"]))
    chk("Körper und Pins der Winkelleiste (Pins in der Buchsentasche)", vol_int(body, P["leiste"]))
    sx = (d["x_s0"] + d["x_s1"]) / 2
    rep("  Kontrollen (müssen stoßen):")
    chk("Körper 0,17 mm nach +x verschoben stößt an die Mulde", vol_int(plate, body.translate([0.17, 0, 0])), must_collide=True)
    chk("Körper 0,17 mm nach +y verschoben stößt an die Mulde", vol_int(plate, body.translate([0, 0.17, 0])), must_collide=True)
    chk("Körper 0,13 mm nach +y verschoben stößt noch nicht (Spiel 0,15 je Seite)", vol_int(plate, body.translate([0, 0.13, 0])))
    for ang in (90, 180, 270):
        rot = body.translate([-sx, 0, 0]).rotate([0, 0, ang]).translate([sx, 0, 0])
        chk("Körper um %d° gedreht (Verdrehsicherung, Kodierecke und Fußverlängerung) stößt an die Mulde" % ang, vol_int(plate, rot), must_collide=True)
    rep("  -> %s" % ("alle Prüfungen bestanden" if not bad else "%d Fehler!" % bad))

    rep("\nAbstände (mm):")
    from shapely.geometry import Point
    ch, w = aux["chamber"], aux["wire"]
    rep("  Adernweg in der Kammer: Länge %.1f mm (Polylinie), kleinster Abstand zur Wand %.2f mm" % (
        sum(math.dist(a, b) for a, b in zip(w, w[1:])), min(ch.exterior.distance(Point(p)) for p in w[1:])))
    rep("  Zapfen Ø%.1f im Modulloch Ø%.1f: %.2f je Seite; im Sackloch Ø%.1f: %.2f je Seite; Tiefe des Sacklochs %.1f, Zapfen ragt %.1f hinein" % (
        D.PEG_D, D.DISP["hole_d"], (D.DISP["hole_d"] - D.PEG_D) / 2, D.PEG_HOLE_D, (D.PEG_HOLE_D - D.PEG_D) / 2, D.PEG_HOLE_T, D.PEG_HOLE_T - 0.2))
    rep("  Modultasche %.2f × %.2f × %.2f (Platine %.1f × %.1f × %.1f): Spiel %.2f je Seite, oben %.2f, Dicke %.2f" % (
        D.DISP["pcb_w"] + 2 * D.CLR_W, D.DISP["pcb_h"] + D.CLR, d["slot_t"], D.DISP["pcb_w"], D.DISP["pcb_h"], D.DISP["mod_t"], D.CLR_W, D.CLR, d["slot_t"] - D.DISP["mod_t"]))
    rep("  Kopf über der Platte: %.2f; Wand um die Modultasche %.2f; Rückwand %.2f; Wand um den Schacht %.2f" % (d["z_hb"], D.WALL, D.BACK, D.WALL))
    rep("  Sichtfenster %.1f × %.1f (aktive Fläche %.2f × %.2f plus %.1f Rand je Seite), Unterkante %.1f über der Platte" % (
        2 * (D.DISP["aa_w"] / 2 + D.WINDOW_MARGIN), d["wt"] - d["wb"], D.DISP["aa_w"], D.DISP["aa_h"], D.WINDOW_MARGIN, d["wb"]))

    tot = sum(v["min"] for v in info.values())
    rep("\nDruckzeit geschätzt (nicht kalibriert): " + ", ".join("%s %.0f min" % (k.split("_")[0], v["min"]) for k, v in info.items()) + ", zusammen %.0f min" % tot)
    with open(os.path.join(OUT, "pruefbericht.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(rep.lines) + "\n")
    imgs = render_images(P, plate, d, parts, rep)
    write_readme(info, tot, d, 0)
    zpath = os.path.join(OUT, ZIP)
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(os.listdir(OUT)):
            if f.endswith(".stl") or f in ("README.txt", "pruefbericht.txt"):
                z.write(os.path.join(OUT, f), f)
        for p in imgs:
            z.write(p, os.path.join("bilder", os.path.basename(p)))
    rep("%s: %.0f kB" % (os.path.relpath(zpath, HERE), os.path.getsize(zpath) / 1024))
    # der Bericht in der ZIP ist der vor dem Schreiben der ZIP-Zeile; die Datei auf der Platte bekommt die letzte Zeile noch
    with open(os.path.join(OUT, "pruefbericht.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(rep.lines) + "\n")
    return bad


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
