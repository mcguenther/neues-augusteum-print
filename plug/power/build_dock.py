#!/usr/bin/env python3
"""Test-Dock "flache Unterseite": STL, README, ZIP, Prüfbericht und Vorschaubilder nach stl/steckmodul_testdock/.

Plan: plug/power/plan_dock.html (vom Nutzer abgenickt: alles auf gleicher Höhe, ohne Tasche, Stufe, Nische und Support, Leiste aufgeklebt).
Teile:
  D_platte.stl         Mini-Oberplatte 40 × 50,4 × 10,6 mm: Mulde, vier Pin-Löcher, vier Zapfenlöcher, flache Unterseite
  D_fuesse_3_5.stl     4 Füße 8 × 8 mm, 3,5 mm hoch, Zapfen 2,5 (eine Kerbe)
  D_fuesse_2_5.stl     4 Füße, 2,5 mm hoch (zwei Kerben)
Gebäude und Kassette aus Steckprobe 2 (stl/steckmodul_testcase2/) werden wiederverwendet.
Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m plug.power.build_dock
"""
import os
import zipfile

from shapely.geometry import Point
from shapely.geometry import box as sbox

from plug import dupont as sd
from plug import institute as I
from plug import series as SR
from plug import series2 as N2
from plug.fit_test.generator import overhangs
from plug.geom import box, to_bed, to_tm, union, vol_int, xcut
from plug.power import build_concept as BC
from plug.power import build_plan_dock as PD
from plug.power import params as PP
from plug.testcase import build as TB
from plug.testcase import build2 as B2
from plug.testcase import params as P

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(HERE, "stl", "steckmodul_testdock")
PREV = os.path.join(HERE, "vorschau", "steckmodul_testdock")
de = SR.de
gx = BC.G.extrude
D = B2.D
F = D["F"]
CH = P.EF_CH_T                                   # Bettkanten 0,5
DECK = -(F + P.CEIL_T)                           # Unterseite der Platte, -10,6
PIN = dict(PP.PIN, h=PD.PROP["PIN_H"])           # Zapfen 2,5
HOLE_DEPTH = PD.PROP["HOLE_D"]                   # Zapfenloch 2,8 tief
HOLE_CH = TB.HOLE_CH                             # Fase der Pin-Löcher 0,15
PX, PY0, PY1 = PD.PX, PD.PY0, PD.PY1
OUTLINE = sbox(-PX, PY0, PX, PY1).buffer(-3).buffer(3)
FEET = [(-16.0, 8.0), (16.0, 8.0), (-16.0, 30.0), (16.0, 30.0)]    # außerhalb der Mulde (x ±12)
FOOT = 8.0                                       # Fuß 8 × 8
GAPS = (3.5, 2.5)


def plate():
    cs = I.hcs(B2.foot_poly())
    with BC.patched(sd, CLR=P.MULDE_CLR_T):
        cuts = list(I.pocket_cuts(cs, F))
    for x in sd.pin_x():
        cuts += N2.hole_ch(x, 0.0, DECK, -F, sd.HOLE, HOLE_CH, HOLE_CH)
    for x, y in FEET:
        circ = Point(x, y).buffer(PIN["d"] / 2 + PIN["clr"], 24)
        cuts += [gx(circ, DECK - 1, DECK + HOLE_DEPTH), BC.mouth_ch(circ, DECK, CH)]
    m = BC.slab_ch(OUTLINE, DECK, 0.0, CH) - union(cuts)
    lab = N2.emboss_side(N2.big_label("DOCK", 0, 3.4), 0.0, DECK + 5.0, PY0)
    return union([m, lab])


def feet(gap, notches):
    out = []
    zt = DECK - gap
    for x, y in FEET:
        base = gx(sbox(x - FOOT / 2, y - FOOT / 2, x + FOOT / 2, y + FOOT / 2), zt, DECK + 0.01)
        base = BC.slab_ch(sbox(x - FOOT / 2, y - FOOT / 2, x + FOOT / 2, y + FOOT / 2), zt, DECK + 0.01, 0.4) if False else base
        zapfen = BC.pin_solid_at(Point(x, y), DECK, PIN, PP.CH_PIN)
        grooves = [box(x - FOOT / 2 - 0.1, x + FOOT / 2 + 0.1, y - FOOT / 2 - 0.1, y - FOOT / 2 + 0.6, zt + 0.9 + 0.9 * k - 0.3, zt + 0.9 + 0.9 * k + 0.3) for k in range(notches)]
        out.append(union([base, zapfen]) - union(grooves) if grooves else union([base, zapfen]))
    return union(out)


def wire_dummy(gap_extra=0.0):
    """Draht und Lötstelle: 1,6 mm dick, unter den Lötenden, x ±4,4, ab dem Ende der Lötenden nach vorn."""
    zb = D["z_bm"] - 0.32 - 1.6
    return box(-4.4, 4.4, PY0 + 0.5, D["y_tail"] + 0.5, zb, D["z_bm"] - 0.32)


class Report:
    def __init__(self):
        self.lines = []

    def __call__(self, s=""):
        print(s)
        self.lines.append(s)


def main():
    rep = Report()
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(PREV, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith((".stl", ".zip", ".txt")):
            os.remove(os.path.join(OUT, f))
    pl = plate()
    f35, f25 = feet(GAPS[0], 1), feet(GAPS[1], 2)
    parts = {"D_platte": to_bed(pl), "D_fuesse_3_5": to_bed(f35), "D_fuesse_2_5": to_bed(f25)}
    rep("Test-Dock flache Unterseite: Platte %.1f × %.1f × %.1f mm (Unterseite z %.1f), Füße 8 × 8, Luft %.1f und %.1f, Zapfen %.1f, Loch %.1f tief" % (
        2 * PX, PY1 - PY0, -DECK, DECK, GAPS[0], GAPS[1], PIN["h"], HOLE_DEPTH))
    rep("\nTeile (Druckausrichtung, Bett z = 0):")
    info = {}
    for name, man in parts.items():
        tm = to_tm(man)
        tm.export(os.path.join(OUT, name + ".stl"))
        g, nl = SR.estimate(man)
        ov = overhangs(man, name)
        info[name] = dict(g=g, layers=nl)
        rep("  %-16s %6.1f × %6.1f × %5.1f mm  %5.1f cm³  ≈ %4.1f g  dicht=%s" % (name + ".stl", *tm.extents, tm.volume / 1000.0, g, tm.is_watertight))
        rep("      waagerechte Decken: %s   Überhang flacher als 45° zur Senkrechten: %.0f mm²" % (
            "; ".join("z=%.1f: %.0f mm² (%.1f × %.1f)" % f for f in sorted(ov["flat"], key=lambda t: -t[1])[:4]) or "keine", ov["steep_area"]))

    rep("\nPrüfung der Passungen (Überschneidungsvolumen, mm³; muss 0 sein):")
    bad = 0

    def chk(txt, v, limit=0.05):
        nonlocal bad
        ok = v <= limit
        bad += (not ok)
        rep("  %-74s %8.3f  %s" % (txt, v, "ok" if ok else "KOLLISION"))

    def ctl(txt, v):
        nonlocal bad
        ok = v > 0.05
        bad += (not ok)
        rep("  %-74s %8.3f  %s" % (txt, v, "stößt an (wie erwartet)" if ok else "PRÜFUNG WERTLOS"))

    hd = TB.header()
    bld, kw, bw = B2.building(), B2.kass_world(1), B2.buchse_world(True)
    chk("Winkelleiste an der Platte (Pins durch die Löcher, Körper liegt nur an)", vol_int(hd, pl))
    chk("Mini-Gebäude in der Mulde der Platte", vol_int(bld, pl))
    chk("Kassette im Mini-Gebäude", vol_int(kw, bld))
    chk("Buchse (Nennmaß, bündig) und Winkelleiste (Pins in den Kammern)", vol_int(bw, hd))
    chk("Kassette und Winkelleiste", vol_int(kw, hd))
    for i, (x, y) in enumerate(FEET):
        pass
    fz = BC.pin_solid_at(Point(*FEET[0]), DECK, PIN, PP.CH_PIN)
    chk("Zapfen im Zapfenloch der Platte (Gleitspiel 0,15)", vol_int(fz, pl))
    ctl("Kontrolle: Zapfen um 0,4 versetzt stößt an der Lochwand an", vol_int(BC.pin_solid_at(Point(FEET[0][0] + 0.4, FEET[0][1]), DECK, PIN, PP.CH_PIN), pl))
    chk("Füße 3,5 und 2,5 stecken im Loch: Zapfen 2,5 passt in 2,8 Lochtiefe", 0.0 if PIN["h"] + 0.3 <= HOLE_DEPTH + 1e-6 else 1.0)
    wd = wire_dummy()
    ztab = lambda g: box(-30, 30, -30, 60, DECK - g - 5.0, DECK - g)
    chk("Draht (Tail 1,0 unter der Platte, 1,6 dick) und Tisch bei Luft 3,5", vol_int(wd, ztab(GAPS[0])))
    chk("Körper der Leiste (hängt 2,0 tief) und Tisch bei Luft 2,5", vol_int(hd, ztab(GAPS[1])))
    ctl("Kontrolle: Draht bei Luft 2,5 stößt an den Tisch (Grenze des Tests)", vol_int(wd, ztab(GAPS[1])))
    rep("  Luft unter der Platte: Körper reicht %.1f, Draht etwa %.1f unter die Unterseite" % (-(D["z_bm"] - 1.0 - DECK), -(D["z_bm"] - 0.32 - 1.6 - DECK)))
    rep("  -> %s" % ("keine Kollisionen" if not bad else "%d Fehler!" % bad))

    tot = sum(i["g"] for i in info.values())
    from plug.roadmap import build as rb
    for prof, pr in rb.PROFILE.items():
        mins = sum(i["g"] / pr["rate"] * 60.0 + i["layers"] * pr["layer"] / 60.0 for i in info.values()) + pr["start"]
        rep("Material ≈ %.0f g, Zeit %s ≈ %.1f h" % (tot, prof, mins / 60.0))
    rep("Bei deinem Drucker (Nacht 1: 47 g in 2,5 h) ≈ %.1f h" % (tot / 47.0 * 2.5))
    with open(os.path.join(OUT, "pruefbericht.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(rep.lines) + "\n")
    previews(parts, pl, hd, bld, kw, bw, f35, wd)
    write_readme(info, tot)
    zpath = os.path.join(OUT, "testdock.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(os.listdir(OUT)):
            if f.endswith(".stl") or f == "README.txt":
                z.write(os.path.join(OUT, f), f)
    rep("%s: %.0f kB" % (os.path.relpath(zpath, HERE), os.path.getsize(zpath) / 1024))
    return bad


def previews(parts, pl, hd, bld, kw, bw, f35, wd):
    import preview
    from PIL import Image
    tms = {n: to_tm(m) for n, m in parts.items()}
    pos, need = SR.pack([(n, float(t.extents[0]), float(t.extents[1])) for n, t in tms.items()], bed=(130.0, 400.0))
    col = {"D_platte": "#b6cde0", "D_fuesse_3_5": "#8fa3b8", "D_fuesse_2_5": "#6b7d93"}
    items = []
    for n, tm in tms.items():
        x, y = pos[n]
        tm.apply_translation([x - tm.bounds[0][0], y - tm.bounds[0][1], 0])
        items.append((tm, col[n]))
    preview.render(items, size=(1200, 800), azim=-60, elev=50).save(os.path.join(PREV, "teile.png"))
    cutx = lambda m: to_tm(xcut(m, 0.0))
    table = box(-30, 30, -30, 60, DECK - GAPS[0] - 1.0, DECK - GAPS[0])
    its = [(cutx(pl), "#b6cde0"), (cutx(hd), "#2d3236"), (cutx(bld), "#e9e1c9"), (cutx(kw), "#e3862a"), (cutx(bw), "#f4f1e8"), (cutx(wd), "#c8423b"), (cutx(table), "#cfd6dc")]
    preview.render(its, size=(1400, 700), azim=0, elev=0).save(os.path.join(PREV, "schnitt.png"))
    full = [(to_tm(pl), "#b6cde0"), (to_tm(hd), "#2d3236"), (to_tm(wd), "#c8423b"), (to_tm(f35), "#8fa3b8")]
    a = preview.render(full, size=(1100, 900), azim=-35, elev=-45)
    b = preview.render([(to_tm(pl), "#b6cde0"), (to_tm(hd), "#2d3236"), (to_tm(wd), "#c8423b")], size=(1100, 900), azim=-90, elev=-85)
    sheet = Image.new("RGB", (2200, 900), "white")
    sheet.paste(a, (0, 0))
    sheet.paste(b, (1100, 0))
    sheet.save(os.path.join(PREV, "unterseite.png"))
    print("Vorschau: %s" % os.path.relpath(PREV, HERE))


def write_readme(info, tot):
    g = {n: info[n]["g"] for n in info}
    txt = f"""TEST-DOCK, flache Unterseite (Plan: plug/power/plan_dock.html)
================================================================

Ein Dock ohne Tasche, Stufe, Schlitz, Nische, Steg und Support: Die Unterseite der Platte ist flach, die Winkelleiste liegt mit ihrem Körper (2,0 mm)
daran und wird aufgeklebt. Darunter bleibt ein offener Raum; der Tisch steht für die Oberkante der Powerbank. Geprüft werden Leiste und Lötenden
flach an der Platte, Halt des Klebers beim Aufstecken, Luft für Draht und Lötstelle und die Zapfen mit 2,5 mm Länge.

Dateien (Druckausrichtung, kein Support)
  D_platte.stl       Mini-Oberplatte {de(2 * PX, 1)} × {de(PY1 - PY0, 1)} × {de(-DECK, 1)} mm, Unterseite flach (auf dem Bett), Mulde oben, vier Pin-Löcher Ø {de(sd.HOLE, 1)} (Fase {de(HOLE_CH, 2)}),
                     vier Zapfenlöcher Ø 4,3 (2,8 tief) außerhalb der Mulde.   ≈ {de(g['D_platte'], 1)} g
  D_fuesse_3_5.stl   4 Füße 8 × 8 mm, 3,5 mm hoch, Zapfen 2,5 (eine Kerbe).   ≈ {de(g['D_fuesse_3_5'], 1)} g
  D_fuesse_2_5.stl   4 Füße 8 × 8 mm, 2,5 mm hoch, Zapfen 2,5 (zwei Kerben).   ≈ {de(g['D_fuesse_2_5'], 1)} g
  Zusammen ≈ {de(tot, 0)} g; bei deinem Drucker (Nacht 1: 47 g in 2,5 h) etwa {de(tot / 47.0 * 2.5, 1)} h.

Wiederverwenden aus Steckprobe 2: Mini-Gebäude (GEB S2) und die Kassette mit Buchse, dazu Winkelleiste, Dupont-Buchse mit Adern, Kleber (Sekundenkleber
und Heißkleber), etwas Draht zum Anlöten, Multimeter.

Slicer wie bisher (Bambu, PLA, 0,2 mm, 3 Wände, 15 % Füllung), ohne Support. Platte: flache Unterseite auf dem Bett. Füße stehend, Zapfen oben.
Danach die vier Pin-Löcher mit einer Nadel prüfen, ob sie offen sind.

Zusammenbau
  1. Winkelleiste mit den Pins von unten durch die vier Löcher stecken, mit dem Körper flach an die Plattenunterseite drücken und mit einem Tropfen Sekundenkleber
     festkleben (nur den Körper, nicht die Pins).
  2. Gebäude (mit eingepresster Kassette) in die Mulde setzen: Pins treffen die Buchse. Zehn Mal aufstecken und abziehen: hält der Kleber?
  3. Danach dasselbe mit Heißkleber um den Körper.
  4. Drähte an die Lötenden löten.
  5. Die Platte mit Zapfen in die Füße setzen (zuerst Satz 3,5 mit einer Kerbe) und auf den Tisch stellen: hängt Draht oder Lötstelle am Tisch? Dann Satz 2,5.

Prüfung: siehe Testbogen (plug/power/feedback_dock.html). Im Ergebnistext stehen Kleber und Füße-Satz.
"""
    with open(os.path.join(OUT, "README.txt"), "w", encoding="utf-8") as f:
        f.write(txt)


if __name__ == "__main__":
    raise SystemExit(1 if main() else 0)
