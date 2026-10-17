#!/usr/bin/env python3
"""Modulprobe Display-Gebäude nach stl/steckmodul_display_modul/: nur die Aufnahme des Moduls (Kopf des Körpers) und die Frontblende mit Zapfen.

Anlass: Probedruck 1 (stl/steckmodul_display/): das Modul passte nicht in die Tasche (etwa 0,75 mm zu hoch), die Breite passte (Nutzer: 0,1 mm mehr Luft),
die Zapfen griffen kaum und waren kurz. Die Kassette entfällt in dieser Probe (sie wird später in den Körper integriert).
Teile (Maße aus plug/display/params.py, alles Planwerte):
  M1_aufnahme.stl             Kopf des Körpers: Tasche für das Modul von vorn, Rückwand 3,6 mm dick mit Kabelfenster und vier Sacklöchern (Ø 2,5, 2,6 tief)
  M2_blende_A_zapfen_2_4.stl  Frontblende mit Sichtfenster und vier Zapfen Ø 2,4 (0,05 Luft je Seite im Sackloch)
  M3_blende_B_zapfen_2_5.stl  dieselbe Blende mit Zapfen Ø 2,5 (ohne Luft)
Die Dateien liegen in Druckausrichtung wie im Körper (Aufnahme stehend auf der Kopfunterseite, Blende flach, Außenfläche unten).

Aufruf (aus dem Wurzelverzeichnis):  python3 -m plug.display.build_test    (ca. 15 s)
"""
import math
import os
import sys
import zipfile

from shapely.geometry import LineString, Polygon

import preview as PV
from plug import buildings as BU
from plug.display import body4 as B
from plug.display import params as D
from plug.fit_test.generator import overhangs
from plug.geom import box, prism_x, to_tm, union, vol_int
from plug.display.build import Report, minutes, place_bed
from plug.testcase import params as TP

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(HERE, "stl", "steckmodul_display_modul")
PREV = os.path.join(HERE, "vorschau", "steckmodul_display_modul")
ZIP = "display_modulprobe.zip"
SKIN = 1.0             # E  Material hinter dem Grund der Sacklöcher (Rückseite der Aufnahme)
P = D.DISP


def aufnahme(d):
    """Kopf des Körpers (Weltlage): Block von der Rückseite bis zur Rückseite der Blende, Tasche, Kabelfenster, Sacklöcher; Bettkante 0,5 gefast."""
    xb = d["x_slot0"] - D.PEG_HOLE_T - SKIN
    w = d["W"] / 2
    pts = [(xb, -w), (d["x_blende"], -w), (d["x_blende"], w), (xb, w)]
    z_pocket = d["mb"] + P["pcb_h"] + D.CLR                       # Aufnahme endet oben mit der Tasche (offen), das Dach ist die Lippe der Blende
    blk = B.chamfered_prism(pts, d["z_hb"], z_pocket, [TP.EF_CH_T] * 4)
    hw = P["pcb_w"] / 2 + D.CLR_W
    pocket = box(d["x_slot0"], 0.05, -hw, hw, d["mb"], z_pocket + 1.0)
    window = prism_x(list(B.window_poly(d).exterior.coords)[:-1], xb - 0.05, d["x_slot0"] + 0.05)
    holes = union([B.peg_hole(d, y, z) for y, z in B.peg_centres(d)])
    return blk - pocket - window - holes, xb


def hinten_material(d):
    """Kleinster Abstand des Sacklochgrunds zur Außenfläche im echten Körper (Grundriss und Seitenprofil), je Zapfen."""
    side, plan = Polygon(B.profile_side(d)), Polygon(B.profile_plan(d))
    xb, out = d["x_slot0"] - D.PEG_HOLE_T, []
    for y, z in B.peg_centres(d):
        xs = side.intersection(LineString([(-60, z), (5, z)])).bounds[0]
        xp = plan.intersection(LineString([(-60, abs(y) + D.PEG_HOLE_D / 2), (5, abs(y) + D.PEG_HOLE_D / 2)])).bounds[0]
        out.append(xb - max(xs, xp))
    return min(out)


def render_images(P3, auf, bl, d, parts):
    os.makedirs(PREV, exist_ok=True)
    col = dict(auf="#c9a227", blende="#3a3f4a", pcb="#3f8f5a", glass="#1d2330", header="#222222", pins="#c0c0c0")
    def mk(m, k):
        return (to_tm(m), col[k])
    mod = [mk(P3[k], k) for k in ("pcb", "glass", "header", "pins")]
    full = [mk(auf, "auf"), mk(bl, "blende")] + mod
    out = []
    im = PV.render(full, size=(1000, 760), azim=-32, elev=22)
    p = os.path.join(PREV, "zusammengebaut.png")
    PV.caption(im, "Modulprobe: Aufnahme, Modul (Attrappe) und Blende", "Modulmaße ungemessen: Platine 35,3 × 34,05 × 4,5 (Dicke angenommen)").save(p, optimize=True)
    out.append(p)
    # Schnitt durch die Achse der Zapfen (y = +15,15), Blick von Süden auf die Schnittfläche
    y0 = B.peg_centres(d)[-1][0]
    cut = box(-500, 500, -500, y0, -500, 500)
    sect = [mk(m - cut, k) for m, k in ((auf, "auf"), (bl, "blende"), (P3["pcb"], "pcb"), (P3["glass"], "glass"))]
    im = PV.render(sect, size=(1000, 760), azim=-90, elev=0)
    p = os.path.join(PREV, "schnitt_zapfen.png")
    PV.caption(im, "Schnitt durch die Zapfen (y = %.2f, Blick von Süden)" % y0, "Blende mit Zapfen, Platine mit Loch, Sackloch 2,6 tief in der Rückwand").save(p, optimize=True)
    out.append(p)
    x, row = 0.0, []
    for (name, man), c in zip(parts.items(), ["#c9a227", "#3a3f4a", "#5b4a7a"]):
        b = man.bounding_box()
        row.append((to_tm(man.translate([x - b[0], -(b[1] + b[4]) / 2, 0])), c))
        x += (b[3] - b[0]) + 8.0
    im = PV.render(row, size=(1000, 520), azim=-35, elev=32)
    p = os.path.join(PREV, "teile.png")
    PV.caption(im, "Modulprobe: Teile in Druckausrichtung", "links nach rechts: M1 Aufnahme, M2 Blende A (Zapfen 2,4), M3 Blende B (Zapfen 2,5)").save(p, optimize=True)
    out.append(p)
    return out


def write_readme(info, d, skin):
    de = lambda v, n=2: ("%.*f" % (n, v)).replace(".", ",")
    t = {k: v["min"] for k, v in info.items()}
    txt = f"""MODULPROBE DISPLAY-GEBÄUDE: AUFNAHME UND FRONTBLENDE MIT ZAPFEN
==============================================================

Anlass: Modulprobe 1 (stl/steckmodul_display_modul/): Das Modul passt, die Decke über der Tasche löste sich vom Support, die Zapfen kamen nur etwa 0,5 mm ins Loch.
Entscheidung des Nutzers nach Plan 4: Decke A (Kappe) und Zapfen P1, Loch Ø {de(D.PEG_HOLE_D, 2)}. Alle Werte sind Planwerte (plug/display/params.py), nichts davon ist gedruckt.

Was sich gegenüber Modulprobe 1 geändert hat
  Aufnahme         Oben offen, keine Decke mehr, kein Support. Die Seitenwände und die Rückwand enden an der Oberkante der Tasche ({de(P['pcb_h'] + D.CLR)} über dem Boden).
  Blende (Kappe)   Hat oben eine Lippe {de(D.LIP_T, 1)} mm dick, die über die Tasche und {de(1.0, 1)} mm über die Rückwand reicht und als Dach auf den Wänden liegt. Die Blende liegt flach, die Lippe steht als Rippe nach oben.
  Tasche           Breite {de(P['pcb_w'] + 2 * D.CLR_W)} ({de(D.CLR_W, 2)} Luft je Seite), Höhe {de(P['pcb_h'] + D.CLR)} (Modul als {de(P['pcb_h'])} angenommen, oben {de(D.CLR)} Luft), Dicke {de(d['slot_t'])}.
  Sackloch         Ø {de(D.PEG_HOLE_D, 2)} (Modulprobe 1: 2,5), {de(D.PEG_HOLE_T, 1)} tief, Einführfase {de(D.PEG_HOLE_CH, 1)}.
  Zapfen P1        Spitze Ø {de(D.PEG_TIP_D, 1)}, Kegel über {de(D.PEG_TAPER_L, 1)} mm (11 Lagen) auf den vollen Durchmesser, dann zylindrisch. Blende M2: Enddurchmesser {de(D.PEG_D, 1)}, Blende M3: {de(D.PEG_D_B, 1)}
                   (etwas fester). Im Sackloch {de(D.PEG_HOLE_T - D.PEG_TIP_GAP, 1)} tief. Im echten Körper bleibt hinter dem Sackloch mindestens {de(skin, 1)} mm Material.

Teile
  M1_aufnahme.stl             {info['M1_aufnahme']['ext']} mm  Kopf mit Tasche (oben und vorn offen), Kabelfenster in der Rückwand, vier Sacklöcher
  M2_blende_A_zapfen_2_4.stl  {info['M2_blende_A_zapfen_2_4']['ext']} mm  Blende mit Lippe, Fenster und vier Zapfen, Ende Ø {de(D.PEG_D, 1)}
  M3_blende_B_zapfen_2_5.stl  {info['M3_blende_B_zapfen_2_5']['ext']} mm  dieselbe Blende, Zapfen Ende Ø {de(D.PEG_D_B, 1)}

Druckausrichtung (so liegen die Dateien schon)
  M1  stehend auf der Kopfunterseite (Tasche und Sacklöcher liegen waagerecht wie im echten Körper), kein Support nötig.
  M2, M3  flach, Außenfläche unten, Zapfen und Lippe zeigen nach oben, kein Support. Eine Blende reicht, die zweite für den Vergleich.
Einstellungen wie bisher (plug/slicer.md): Bambu A1, PLA, Düse 0,4, Schichthöhe 0,2, Wände 3, kein Brim. Druckzeit geschätzt (nicht kalibriert):
M1 {t['M1_aufnahme']:.0f} min, M2 {t['M2_blende_A_zapfen_2_4']:.0f}, M3 {t['M3_blende_B_zapfen_2_5']:.0f} min.

Ablauf und was zu melden ist
  1. Modul in die Tasche schieben (Pins zuerst durch das Kabelfenster). Passt es jetzt in der Höhe? Wie viel Luft oben ungefähr (mm), und seitlich (leicht, saugend, klemmt)?
     Liegt es unten auf dem Taschenboden? Passt der Header durch das Kabelfenster?
  2. Durch die Befestigungslöcher des Moduls auf die Sacklöcher schauen: stimmen sie überein (mittig, nach oben, unten, links, rechts versetzt, ungefähr wie viel)?
     Das ist die Lochlage, die ich aus dem Foto geschätzt habe (Lochabstand {de(P['hole_dx'], 1)} × {de(P['hole_dy'], 1)}, untere Löcher {de(P['hole_edge'], 1)} über der Pinkante). Die Zapfen haben
     0,3 Luft je Seite im Modulloch: bei mehr Versatz gehen sie nicht durch die Platine. Das Modul ist höher als gedacht; wo die zusätzlichen 0,75 mm liegen (oben oder an der Pinkante), weiß ich nicht.
     Stoßen die beiden oberen Zapfen am Glas des Moduls an (das Glas darf die Löcher nicht verdecken)?
  3. Blende A aufstecken: gehen die vier Zapfen durch die Modullöcher? Greifen sie im Sackloch (1 lose bis 5 fest), wie viel Kraft zum Abziehen? Dasselbe mit Blende B.
     Ist eine Variante zu fest (bricht, reißt die Rückwand), eine zu lose?
  4. Sichtfenster: Ist die aktive Fläche des Displays vollständig sichtbar? Wie viel Rand bleibt oben, unten, links und rechts (mm, grob)? Ist das Display zu hoch oder zu tief im Fenster?
  5. Sitzt das Modul zwischen Blende und Rückwand mit Spiel (wackelt es in der Dicke)?

Prüfbericht: pruefbericht.txt.
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
    P3, aux = B.parts(d)
    auf, xb = aufnahme(d)
    bA, bB = B.make_blende(d, D.PEG_D, True), B.make_blende(d, D.PEG_D_B, True)
    parts = {"M1_aufnahme": place_bed(auf.translate([0, 0, -d["z_hb"]])),
             "M2_blende_A_zapfen_2_4": place_bed(bA.rotate([0, 90, 0])),
             "M3_blende_B_zapfen_2_5": place_bed(bB.rotate([0, 90, 0]))}
    rep("Modulprobe Display-Gebäude: Aufnahme und Frontblende mit Zapfen (plug/display/params.py, body4.py)")
    rep("Modul angenommen %.2f × %.2f × %.1f (Platine); Tasche %.2f × %.2f × %.2f, Luft je Seite %.2f, oben %.2f, Dicke je Seite %.2f" % (
        P["pcb_w"], P["pcb_h"], P["mod_t"], P["pcb_w"] + 2 * D.CLR_W, P["pcb_h"] + D.CLR, d["slot_t"], D.CLR_W, D.CLR, D.CLR))
    rep("Kopf %.2f breit × %.2f hoch × %.2f tief (Aufnahme), Rückwand %.2f dick, Sacklöcher Ø%.2f × %.2f tief, Zapfen Ø%.1f / Ø%.1f" % (
        d["W"], d["z_top"] - d["z_hb"], d["x_blende"] - xb, d["x_slot0"] - xb, D.PEG_HOLE_D, D.PEG_HOLE_T, D.PEG_D, D.PEG_D_B))
    rep("\nTeile (Druckausrichtung, Bett z = 0):")
    info = {}
    for name, man in parts.items():
        tm = to_tm(man)
        tm.export(os.path.join(OUT, name + ".stl"))
        ov = overhangs(man, name)
        ue = BU.ueberhang(man)
        info[name] = dict(ext=("%.1f × %.1f × %.1f" % tuple(tm.extents)).replace(".", ","), min=minutes(man))
        rep("  %-26s %6.1f × %6.1f × %5.1f mm  %5.2f cm³  dicht=%s (Manifold: %s)" % (name + ".stl", *tm.extents, tm.volume / 1000.0, tm.is_watertight, man.status().name))
        rep("      waagerechte Decken: %s" % ("; ".join("z=%.1f: %.0f mm² (%.1f × %.1f)" % f for f in sorted(ov["flat"], key=lambda t: -t[1])[:5]) or "keine"))
        rep("      Lagenprüfung: Brücken %.1f mm² (bis %.1f mm), Kragstücke %.1f mm² (bis %.1f mm)" % (ue["bruecke_mm2"], ue["bruecke_mm"], ue["krag_mm2"], ue["krag_mm"]))
        for s in sorted(ue["stellen"], key=lambda s: -s[2])[:6]:
            rep("         %s bei z=%.1f: %.0f mm², Reichweite %.1f mm, Mitte (%.1f, %.1f)" % s)
        if not tm.is_watertight or man.status().name != "NoError":
            raise SystemExit("nicht dicht: " + name)

    rep("\nPrüfung im Zusammenbau (Überschneidungsvolumen, mm³; muss 0 sein):")
    bad = 0

    def chk(txt, v, limit=0.05, must=False):
        nonlocal bad
        ok = (v > limit) if must else (v <= limit)
        bad += (not ok)
        rep("  %-78s %9.3f  %s" % (txt, v, "ok" if ok else "FEHLER"))
    mod = P3["pcb"]
    chk("Aufnahme und Modulplatine (%.2f × %.2f in Tasche %.2f × %.2f)" % (P["pcb_w"], P["pcb_h"], P["pcb_w"] + 2 * D.CLR_W, P["pcb_h"] + D.CLR), vol_int(auf, mod))
    chk("Aufnahme und Modulglas, Header, Pins (Kabelfenster)", vol_int(auf, P3["glass"]) + vol_int(auf, P3["header"]) + vol_int(auf, P3["pins"]))
    for nm, bl in (("A (Ø%.1f)" % D.PEG_D, bA), ("B (Ø%.1f)" % D.PEG_D_B, bB)):
        chk("Blende %s und Aufnahme (Zapfen im Sackloch, Blende vor der Aufnahme)" % nm, vol_int(auf, bl))
        chk("Blende %s und Modulplatine, Header (Zapfen durch die Löcher Ø%.1f)" % (nm, P["hole_d"]), vol_int(bl, mod) + vol_int(bl, P3["header"]))
        gl = vol_int(bl, P3["glass"])
        rep("  Hinweis Blende %s und Modulglas (Lage des Glases nur aus dem Foto, ± 0,5): Überschneidung %.3f mm³ (obere Zapfen laufen an der Glaskante entlang)" % (nm, gl))
    rep("  Kontrollen (müssen stoßen):")
    big = B.make_blende(d, D.PEG_HOLE_D + 0.1, True)
    chk("Zapfen Ø%.1f (0,05 größer als das Sackloch) stößt an die Aufnahme" % (D.PEG_HOLE_D + 0.1), vol_int(auf, big), must=True)
    chk("Blende A um 0,2 mm nach oben versetzt: Zapfen stoßen am Sackloch (Spiel 0,05)", vol_int(auf, bA.translate([0, 0, 0.2])), must=True)
    chk("Blende A um 0,04 mm nach oben versetzt: noch kein Anstoß (Spiel 0,05 je Seite)", vol_int(auf, bA.translate([0, 0, 0.04])))
    # Zapfen im Modulloch: Spiel und Lagetoleranz
    rep("\nAbstände (mm):")
    rep("  Zapfen Ø%.1f im Modulloch Ø%.1f: %.2f je Seite (Lochlage aus dem Foto ± 0,5; ab 0,3 Versatz stößt der Zapfen an der Platine)" % (D.PEG_D, P["hole_d"], (P["hole_d"] - D.PEG_D) / 2))
    rep("  Zapfen A Ende Ø%.1f im Sackloch Ø%.1f: %.2f je Seite, B Ø%.1f: %.2f je Seite; Tiefe im Sackloch %.1f (Probedruck 1: 1,0)" % (
        D.PEG_D, D.PEG_HOLE_D, (D.PEG_HOLE_D - D.PEG_D) / 2, D.PEG_D_B, (D.PEG_HOLE_D - D.PEG_D_B) / 2, D.PEG_HOLE_T - D.PEG_TIP_GAP))
    skin = hinten_material(d)
    rep("  Im echten Körper (Grundriss und Rückenkeil) bleibt hinter dem Grund des Sacklochs mindestens %.2f mm Material (Aufnahme: %.2f)" % (skin, SKIN))
    rep("  Taschenhöhe %.2f für Modul %.2f: oben %.2f Luft (liegt das Modul auf dem Boden)" % (P["pcb_h"] + D.CLR, P["pcb_h"], D.CLR))
    tot = sum(v["min"] for v in info.values())
    rep("\nDruckzeit geschätzt (nicht kalibriert): " + ", ".join("%s %.0f min" % (k.split("_")[0], v["min"]) for k, v in info.items()) + ", zusammen %.0f min" % tot)
    rep("  -> %s" % ("alle Prüfungen bestanden" if not bad else "%d Fehler!" % bad))
    imgs = render_images(P3, auf, bA, d, parts)
    write_readme(info, d, skin)
    zpath = os.path.join(OUT, ZIP)
    with open(os.path.join(OUT, "pruefbericht.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(rep.lines) + "\n")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(os.listdir(OUT)):
            if f.endswith(".stl") or f in ("README.txt", "pruefbericht.txt"):
                z.write(os.path.join(OUT, f), f)
        for p in imgs:
            z.write(p, os.path.join("bilder", os.path.basename(p)))
    print("%s: %.0f kB" % (os.path.relpath(zpath, HERE), os.path.getsize(zpath) / 1024))
    return bad


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
