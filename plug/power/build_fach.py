#!/usr/bin/env python3
"""Fachprobe Powerbank, Variante B (Anschlussende): STL, README, ZIP, Prüfbericht und Vorschaubilder nach stl/steckmodul_fachprobe/.

Plan: plug/power/plan_fach.html (vom Nutzer abgenickt: Variante B, ohne Schablone, ohne Taste und Stößel, Deckplatte voll).
Teile:
  F_fach.stl       Unterkasten-Ausschnitt: Boden, Wände, Fenster in der Vorderwand, Zaun; hinten offen, die Powerbank ragt heraus
  F_deckplatte.stl Deckplatte 2 mm, steht für die Oberplatte
Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m plug.power.build_fach
"""
import os
import zipfile

from shapely.geometry import LineString
from shapely.geometry import box as sbox

from plug import series as SR
from plug.fit_test.generator import overhangs
from plug.geom import box, to_bed, to_tm, vol_int
from plug.power import build_concept as BC
from plug.power import fachprobe as FA
from plug.power import params as PP

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(HERE, "stl", "steckmodul_fachprobe")
PREV = os.path.join(HERE, "vorschau", "steckmodul_fachprobe")
de = SR.de
G = BC.G
ZF, TOP = FA.ZF, FA.TOP
UA = BC.BVC + PP.PB_PORT_V["usb_a"]
PLUG_END = BC.BU0 - 25.0
CABLE_D = 4.0                                 # Kabel, für die Prüfung
CHAN_FREE = (BC.V1 - (BC.KV0 + PP.FENCE[0]))  # freie Breite des Kabelkanals neben dem Zaun
CABLE_V = BC.KV0 + PP.FENCE[0] + CHAN_FREE / 2


def powerbank(t=None, w=None):
    t = PP.PB_T if t is None else t
    w = PP.PB_W if w is None else w
    return box(BC.BU0, BC.BU0 + PP.PB_L, BC.BVC - w / 2, BC.BVC + w / 2, ZF, ZF + t)


def plug_dummy():
    """Gerader USB-A-Stecker samt Knickschutz: 25 mm lang, 15 breit, 9 hoch, auf halber Dicke der Powerbank."""
    zc = ZF + PP.PB_T / 2
    return box(PLUG_END, BC.BU0, UA - 7.5, UA + 7.5, zc - 4.5, zc + 4.5)


def cable_dummy():
    pts = [(PLUG_END, UA), (PLUG_END - 4.0, (UA + CABLE_V) / 2), (PLUG_END - 1.0, CABLE_V), (BC.BU0 + FA.LB + 8, CABLE_V)]
    return G.extrude(LineString(pts).buffer(CABLE_D / 2, 16), ZF + 0.01, ZF + CABLE_D)


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
    fach, lid = FA.box_part("B"), FA.lid_part("B")
    lid_on = lid.translate([0, 0, TOP])
    parts = {"F_fach": to_bed(fach), "F_deckplatte": to_bed(lid)}
    rep("Fachprobe Powerbank, Variante B: Fach %.1f × %.1f × %.1f mm, Deckplatte 2 mm; Powerbank %.0f × %.0f × %.1f (30 mm im Fach), Steckerraum %.0f mm" % (
        *FA.sizes("B"), TOP, PP.PB_L, PP.PB_W, PP.PB_T, PP.PB_PLUG))
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
        rep("  %-72s %8.3f  %s" % (txt, v, "ok" if ok else "KOLLISION"))

    def ctl(txt, v):
        """Kontrolle: muss anstoßen (Überschneidung > 0,05); sonst ist die Prüfung wertlos."""
        nonlocal bad
        ok = v > 0.05
        bad += (not ok)
        rep("  %-72s %8.3f  %s" % (txt, v, "stößt an (wie erwartet)" if ok else "PRÜFUNG WERTLOS"))

    pb = powerbank()
    chk("Powerbank im Fach (Nennmaß 90 × 63 × 12,6)", vol_int(pb, fach))
    chk("Powerbank unter der Deckplatte", vol_int(pb, lid_on))
    chk("Powerbank 13,0 dick (Anleitung rundet auf 13) unter der Deckplatte", vol_int(powerbank(t=13.0), lid_on))
    chk("Powerbank 13,0 dick im Fach", vol_int(powerbank(t=13.0), fach))
    chk("Powerbank 63,4 breit im Fach (Druckabweichung 0,2)", vol_int(powerbank(w=63.4), fach))
    chk("Deckplatte auf dem Fach (nur Auflage)", vol_int(lid_on, fach))
    chk("USB-A-Stecker im Steckerraum (15 × 9 × 25)", vol_int(plug_dummy(), fach))
    chk("USB-A-Stecker unter der Deckplatte", vol_int(plug_dummy(), lid_on))
    chk("Kabel %.1f mm im Kanal (frei %.1f mm neben dem Zaun)" % (CABLE_D, CHAN_FREE), vol_int(cable_dummy(), fach))
    ctl("Kontrolle: Powerbank 13,7 dick stößt an die Deckplatte", vol_int(powerbank(t=13.7), lid_on))
    ctl("Kontrolle: Powerbank 64,6 breit stößt an den Zaun", vol_int(powerbank(w=64.6), fach))
    wl = box(BC.U0 - FA.WALL - 1, BC.U0 + 0.5, BC.WIN[0], BC.WIN[1], ZF, TOP)
    chk("Fenster in der Vorderwand ist offen (Fensterraum frei von Material)", vol_int(wl, fach))
    rep("\nLadeanschluss und LEDs durch das Fenster (Fenster v %.1f bis %.1f, Anschlüsse nach Schätzung):" % (BC.WIN[0], BC.WIN[1]))
    for key, lab in (("leds", "LEDs"), ("micro", "micro-USB"), ("usb_c", "USB-C")):
        v0, v1 = BC.BVC + PP.PB_PORT_V[key] - BC.PORT_HALF[key], BC.BVC + PP.PB_PORT_V[key] + BC.PORT_HALF[key]
        ok = BC.WIN[0] <= v0 and v1 <= BC.WIN[1]
        bad += (not ok)
        rep("  %-10s v %6.1f bis %6.1f   %s (Rand links %.1f, rechts %.1f)" % (lab, v0, v1, "im Fenster" if ok else "AUSSERHALB", v0 - BC.WIN[0], BC.WIN[1] - v1))
    rep("Kabelkanal: frei %.1f mm neben dem Zaun, Kabel bis etwa %.1f mm Durchmesser (S, ungemessen)." % (CHAN_FREE, CHAN_FREE))
    rep("  -> %s" % ("keine Kollisionen" if not bad else "%d Fehler!" % bad))

    tot = sum(i["g"] for i in info.values())
    from plug.roadmap import build as rb
    for prof, pr in rb.PROFILE.items():
        mins = sum(i["g"] / pr["rate"] * 60.0 + i["layers"] * pr["layer"] / 60.0 for i in info.values()) + pr["start"]
        rep("Material ≈ %.0f g, Zeit %s ≈ %.1f h" % (tot, prof, mins / 60.0))
    rep("Bei deinem Drucker (Nacht 1: 47 g in 2,5 h) ≈ %.1f h" % (tot / 47.0 * 2.5))
    with open(os.path.join(OUT, "pruefbericht.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(rep.lines) + "\n")
    previews(parts, fach, lid_on, pb)
    write_readme(info, tot)
    zpath = os.path.join(OUT, "fachprobe.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(os.listdir(OUT)):
            if f.endswith(".stl") or f == "README.txt":
                z.write(os.path.join(OUT, f), f)
    rep("%s: %.0f kB" % (os.path.relpath(zpath, HERE), os.path.getsize(zpath) / 1024))
    return bad


def previews(parts, fach, lid_on, pb):
    import preview
    from PIL import Image
    tms = {n: to_tm(m) for n, m in parts.items()}
    pos, need = SR.pack([(n, float(t.extents[0]), float(t.extents[1])) for n, t in tms.items()], bed=(200.0, 400.0))
    items = []
    for n, tm in tms.items():
        x, y = pos[n]
        tm.apply_translation([x - tm.bounds[0][0], y - tm.bounds[0][1], 0])
        items.append((tm, "#8fa3b8" if n == "F_fach" else "#b6cde0"))
    preview.render(items, size=(1200, 800), azim=-60, elev=50).save(os.path.join(PREV, "teile.png"))
    base = [(to_tm(fach), "#8fa3b8"), (to_tm(pb), "#f4f1e8"), (to_tm(plug_dummy()), "#2d3236"), (to_tm(cable_dummy()), "#c8423b")]
    a = preview.render(base + [(to_tm(lid_on.translate([0, 0, 22.0])), "#b6cde0")], size=(1100, 900), azim=-40, elev=38)
    b = preview.render(base, size=(1100, 900), azim=-90, elev=80)
    sheet = Image.new("RGB", (2200, 900), "white")
    sheet.paste(a, (0, 0))
    sheet.paste(b, (1100, 0))
    sheet.save(os.path.join(PREV, "zusammenbau.png"))
    print("Vorschau: %s" % os.path.relpath(PREV, HERE))


def write_readme(info, tot):
    g = {n: info[n]["g"] for n in info}
    sx, sy = FA.sizes("B")
    txt = f"""FACHPROBE POWERBANK, Variante B (Plan: plug/power/plan_fach.html)
==================================================================

Ein Ausschnitt des Unterkastens der großen Grundplatte, nur das Anschlussende des Fachs. Die Powerbank (Intenso XS5000) steckt {de(FA.LB, 0)} mm tief im Fach,
der Rest ragt hinten heraus. Geprüft wird, ob sie hineinpasst, wie sie sitzt, ob der gerade USB-A-Stecker samt Kabel in den Steckerraum passt,
ob der Ladeanschluss (micro-USB, USB-C) durch das Fenster erreichbar ist und ob die Luft über der Powerbank reicht.
Keine Taste, kein Stößel, keine Schablone.

Dateien (Druckausrichtung, keine Stützen)
  F_fach.stl         Fach {de(sx, 1)} × {de(sy, 1)} × {de(FA.TOP, 1)} mm: Boden {de(FA.ZF, 1)}, Wand {de(FA.WALL, 1)}, Fenster in der Vorderwand (oben offen), Zaun {de(PP.FENCE[0])} × {de(PP.FENCE[1], 0)}
                     um die Powerbank, Kabelkanal {de(PP.PB_CABLE, 0)} mm (frei {de(CHAN_FREE, 1)} mm neben dem Zaun), hinten offen.   ≈ {de(g['F_fach'], 1)} g
  F_deckplatte.stl   Deckplatte {de(FA.PLATE_T, 0)} mm, steht für die Oberplatte.   ≈ {de(g['F_deckplatte'], 1)} g
  Zusammen ≈ {de(tot, 0)} g; bei deinem Drucker (Nacht 1: 47 g in 2,5 h) etwa {de(tot / 47.0 * 2.5, 1)} h.

Kaufteile: die Powerbank und das USB-A-Kabel mit geradem Stecker, das später dranhängt.

Slicer wie bisher (Bambu, PLA, 0,2 mm, 3 Wände, 15 % Füllung), ohne Stützen.
  Fach: Boden auf dem Bett, offen nach oben. Das Fenster ist oben offen, keine Brücke. Bettkanten mit Fase {de(PP.CH_BED, 1)}.
  Deckplatte: flach.

Zusammenbau
  1. Powerbank mit den Anschlüssen zur Vorderwand (Wand mit dem Fenster) in das Fach legen.
  2. Den USB-A-Stecker des Kabels in die USB-A-Buchse der Powerbank stecken; er liegt im Steckerraum, das Kabel läuft in den Kanal neben dem Zaun nach hinten.
  3. Deckplatte auflegen.
  4. Durch das Fenster das Ladekabel an micro-USB oder USB-C stecken (nur ausprobieren).

Prüfung: siehe Testbogen (plug/power/feedback_fach.html). Im Ergebnistext steht die Variante (B).
"""
    with open(os.path.join(OUT, "README.txt"), "w", encoding="utf-8") as f:
        f.write(txt)


if __name__ == "__main__":
    raise SystemExit(1 if main() else 0)
