#!/usr/bin/env python3
"""Probeteil T2 für den Hauptschalter (Wippe KCD11 10 × 15): STL, README, ZIP, Prüfbericht und Vorschau nach stl/steckmodul_schalterprobe/.

Plan: plug/power/plan_switch.html (Nutzer nach T1: Loch 13,7 × 9,0 (T1 mit 13,6 × 8,6 war sehr stramm), Wand am Loch weiter 1,2 mm). Möglichst sparsam: ein Wandstück der Westwand
des Unterkastens mit einem Loch und der Innentasche, dazu ein Bodenstreifen, damit es steht wie in der Wand. Maße kommen aus
`plug/power/build_plan_switch.py` (HOLE, WALL_AT_HOLE, POCKET, H_WALL, Z_MID).
Koordinaten: x entlang der Wand, y Wanddicke (Außenfläche y = 0, Innenseite y = 2,4), z über dem Bett (Boden des Unterkastens z = 0).
Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m plug.power.build_switch_probe
"""
import os
import zipfile

from plug import series as SR
from plug.fit_test.generator import overhangs
from plug.geom import box, prism_x, to_tm, union, vol_int
from plug.power import build_plan_switch as BS
from plug.power import params as PP

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "stl", "steckmodul_schalterprobe")
PREV = os.path.join(ROOT, "vorschau", "steckmodul_schalterprobe")
de = SR.de
SW, HOLE, POCKET = BS.SW, BS.HOLE, BS.POCKET
W, H, T = BS.T1_W, BS.H_WALL, PP.UK_WALL
ZC = BS.Z_MID
CX = W / 2
Y_POCKET = T - BS.POCKET_T            # Grund der Innentasche (Wand am Loch)
FLOOR_T, FLOOR_D = PP.UK_FLOOR, BS.T1_FLOOR_D


def part():
    wall = box(0, W, 0, T, 0, H)
    floor = box(0, W, T - 0.01, T + FLOOR_D, 0, FLOOR_T)
    hole = box(CX - HOLE[0] / 2, CX + HOLE[0] / 2, -0.1, T + 0.1, ZC - HOLE[1] / 2, ZC + HOLE[1] / 2)
    # Innentasche für die Haken (an den kurzen Enden der 13-mm-Seite); oben mit 45°-Dach, damit keine Brücke von 17,7 mm entsteht
    z0, z1 = ZC - POCKET[1] / 2, ZC + POCKET[1] / 2
    roof = (T + 0.1) - Y_POCKET
    pocket = prism_x([(Y_POCKET, z0), (T + 0.1, z0), (T + 0.1, z1 + roof), (Y_POCKET, z1)], CX - POCKET[0] / 2, CX + POCKET[0] / 2)
    return union([wall, floor]) - hole - pocket


def switch_dummies():
    """Kaufteil für die Prüfung: Kasten im Loch, Frontplatte außen, Haken hinter der Innenwand der Tasche."""
    bw, bl, bd = SW["body_w"], SW["body_l"], SW["body_depth"]
    body = box(CX - bl / 2, CX + bl / 2, 0, bd, ZC - bw / 2, ZC + bw / 2)
    flange = box(CX - SW["flange_l"] / 2, CX + SW["flange_l"] / 2, -SW["flange_t"], 0, ZC - SW["flange_w"] / 2, ZC + SW["flange_w"] / 2)
    hooks = union([box(CX + s * (bl / 2 + 0.35) - 0.35, CX + s * (bl / 2 + 0.35) + 0.35, Y_POCKET, Y_POCKET + 0.9, ZC - 2, ZC + 2) for s in (-1, 1)])
    return body, flange, hooks


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(PREV, exist_ok=True)
    for f in os.listdir(OUT):
        if "T2" in f:
            os.remove(os.path.join(OUT, f))
    lines = []

    def rep(s=""):
        print(s)
        lines.append(s)

    man = part()
    tm = to_tm(man)
    tm.export(os.path.join(OUT, "T2_wand_schalter.stl"))
    g, nl = SR.estimate(man)
    ov = overhangs(man, "T2")
    rep("Probeteil T2 Hauptschalter: Wand %.1f × %.1f × %.1f mm, Loch %.1f × %.1f, Wand am Loch %.1f, Tasche %.1f × %.1f × %.1f tief, Bodenstreifen %.0f mm" % (
        W, H, T, *HOLE, BS.WALL_AT_HOLE, *POCKET, BS.POCKET_T, FLOOR_D))
    rep("  T2_wand_schalter.stl  %.1f × %.1f × %.1f mm  %.2f cm³  ≈ %.1f g  dicht=%s" % (*tm.extents, tm.volume / 1000.0, g, tm.is_watertight))
    rep("      waagerechte Decken: %s   Überhang flacher als 45° zur Senkrechten: %.0f mm²" % (
        "; ".join("z=%.1f: %.0f mm² (%.1f × %.1f)" % f for f in sorted(ov["flat"], key=lambda t: -t[1])[:4]) or "keine", ov["steep_area"]))
    rep("      (die einzige Brücke ist die Oberkante des Lochs, %.1f mm lang bei %.1f mm Wand)" % (HOLE[0], BS.WALL_AT_HOLE))

    rep("\nPrüfung (Überschneidungsvolumen, mm³; muss 0 sein):")
    bad = 0

    def chk(txt, v, limit=0.05):
        nonlocal bad
        ok = v <= limit
        bad += (not ok)
        rep("  %-72s %8.3f  %s" % (txt, v, "ok" if ok else "KOLLISION"))

    def ctl(txt, v):
        nonlocal bad
        ok = v > 0.05
        bad += (not ok)
        rep("  %-72s %8.3f  %s" % (txt, v, "stößt an (wie erwartet)" if ok else "PRÜFUNG WERTLOS"))

    body, flange, hooks = switch_dummies()
    chk("Kasten 13,0 × 8,0 im Loch", vol_int(body, man))
    chk("Frontplatte 15 × 10 liegt außen auf (nur Berührung)", vol_int(flange, man))
    chk("Haken (Spanne 13,7) hinter der Wand, in der Tasche", vol_int(hooks, man))
    chk("Kasten 13,4 × 8,4 (Druckabweichung 0,2 je Maß) im Loch", vol_int(box(CX - 6.7, CX + 6.7, 0, 9, ZC - 4.2, ZC + 4.2), man))
    ctl("Kontrolle: Kasten 13,8 breit stößt an", vol_int(box(CX - 6.9, CX + 6.9, 0, 9, ZC - 4.0, ZC + 4.0), man))
    ctl("Kontrolle: Haken auf Höhe der Restwand stoßen an", vol_int(box(CX - 7.05, CX + 7.05, 0.3, 1.1, ZC - 2, ZC + 2), man))
    rep("  -> %s" % ("keine Kollisionen" if not bad else "%d Fehler!" % bad))
    rep("Schalter eingesetzt: Frontplatte außen, Kasten %.1f tief (ab Außenfläche), Wand am Loch %.1f." % (SW["body_depth"], BS.WALL_AT_HOLE))
    rep("Druckzeit grob: %.0f Schichten, ≈ %.0f g, etwa 5 bis 10 Minuten." % (nl, g))
    with open(os.path.join(OUT, "pruefbericht_T2.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    write_readme(g)
    previews(man)
    zpath = os.path.join(OUT, "schalterprobe_T2.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(os.listdir(OUT)):
            if "T2" in f and (f.endswith(".stl") or f == "README_T2.txt"):
                z.write(os.path.join(OUT, f), f)
    rep("%s: %.1f kB" % (os.path.relpath(zpath, ROOT), os.path.getsize(zpath) / 1024))
    return bad


def previews(man):
    import preview
    from PIL import Image
    body, flange, hooks = switch_dummies()
    base = [(to_tm(man), "#8fa3b8")]
    sw = [(to_tm(body), "#d9480f"), (to_tm(flange), "#e9733a")]
    a = preview.render(base, size=(900, 800), azim=-35, elev=25)                  # Blick auf die Innenseite (Tasche)
    b = preview.render(base, size=(900, 800), azim=145, elev=20)                  # Blick von außen
    c = preview.render(base + sw, size=(900, 800), azim=145, elev=20)             # mit Schalter
    sheet = Image.new("RGB", (2700, 800), "white")
    for i, im in enumerate((a, b, c)):
        sheet.paste(im, (900 * i, 0))
    sheet.save(os.path.join(PREV, "T2.png"))
    print("Vorschau: %s" % os.path.relpath(PREV, ROOT))


def write_readme(g):
    txt = f"""PROBETEIL T2 HAUPTSCHALTER (Plan: plug/power/plan_switch.html)
==============================================================

Ein Stück der Westwand des Unterkastens mit dem Loch für den Wippenschalter (KCD11, 10 × 15 mm, 2 Pins). Geprüft wird, ob der Schalter mit der
dünnen Wand von {de(BS.WALL_AT_HOLE, 1)} mm einrastet und hält, ob das Loch {de(HOLE[0], 1)} × {de(HOLE[1], 1)} mm (T1 hatte 13,6 × 8,6 und war sehr stramm: horizontal +0,1, vertikal +0,4) sitzt oder klappert und ob die Brücke
über dem Loch sauber wird. Nur ein Teil, ≈ {de(g, 1)} g, etwa 5 bis 10 Minuten.

Datei (Druckausrichtung, keine Stützen)
  T2_wand_schalter.stl  Wand {de(W, 0)} × {de(H, 1)} × {de(T, 1)} mm, steht senkrecht auf dem Bodenstreifen ({de(FLOOR_D, 0)} mm tief, {de(FLOOR_T, 1)} dick).
                        Loch {de(HOLE[0], 1)} × {de(HOLE[1], 1)} mit der Langseite waagerecht, Mitte {de(ZC, 1)} mm über dem Bett (wie in der echten Wand).
                        Innentasche {de(POCKET[0], 1)} × {de(POCKET[1], 1)} mm, {de(BS.POCKET_T, 1)} tief, oben mit 45°-Dach: In der Tasche bleibt die Wand {de(BS.WALL_AT_HOLE, 1)} mm dick.

Slicer wie bisher (Bambu, PLA, 0,2 mm, 3 Wände, 15 % Füllung), ohne Stützen. Die {de(BS.WALL_AT_HOLE, 1)} mm Wand am Loch sind genau drei Linien.
  Ausrichtung: wie die STL liegt, Bodenstreifen auf dem Bett. Die Außenfläche zeigt nach vorn, die Tasche nach hinten (zum Streifen).
  Ein Rand (Brim) 3 mm darf dazu, wenn das Teil wackelt.

Prüfen
  1. Loch und Brücke ansehen: Oberkante des Lochs durchgehängt? Kanten sauber? Maß mit Schieblehre (soll {de(HOLE[0], 1)} × {de(HOLE[1], 1)}).
  2. Schalter von außen eindrücken (Frontplatte nach außen). Fühlbar: leicht, saugend oder nur mit Kraft?
  3. Rastet er hörbar ein? Hält er, wenn man an der Wippe zieht und sie bewegt? Wackelt er im Loch?
  4. Reißt die Wand an einer Ecke der Tasche, oder biegt sie sich beim Einschnappen sichtbar?
  5. Ohne Schalter: wie steif ist die {de(BS.WALL_AT_HOLE, 1)} mm Wand, wenn man an der Kante der Tasche drückt?

Vorher mit der Schieblehre messen (Plan, Abschnitt „Bitte nachmessen“): Abstand von der Unterseite der Frontplatte bis zur Hakenkante,
Spanne über die Haken an der 13-mm-Seite (muss größer als {de(HOLE[0], 1)} sein, sonst hält er nicht), Kasten und Frontplatte genau.

Prüfbericht: pruefbericht.txt. Ergebnistext bitte im Chat einfügen (Wand ok oder zu dünn, Sitz leicht oder fest, Haken fassen ja oder nein, Brücke ok).
"""
    with open(os.path.join(OUT, "README_T2.txt"), "w", encoding="utf-8") as fh:
        fh.write(txt)


if __name__ == "__main__":
    raise SystemExit(1 if main() else 0)
