#!/usr/bin/env python3
"""Fadenführung, Eckmuster nach dem abgenickten Plan Stand 2 (plug/thread/plan.html): Variante A als „halbe Pille mit Steg“, mit Fase an Ein- und Ausgängen.

Zwei Eckmuster in einem Druck, je mit Plattenecke (Unterseite am Bett, Tasche nach unten offen) und Unterkasten-Ecke (hohl, Eckaussparung):
  F2_P3_*    Luft über dem Steg 3,0 (Decke 7,5)
  F2_P45_*   Luft über dem Steg 4,5 (Decke 9,0)
Maße aus plug/thread/params.py (`pill()`), Passprüfung im Modell: plug/thread/fit.py. Keine Stützen, Thick bridges an.

Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m plug.thread.build        # STL, README.txt, pruefbericht.txt, ZIP nach plug/thread/stl/, Bilder nach plug/thread/vorschau/
"""
import math
import os
import zipfile

import numpy as np
import trimesh
from shapely.geometry import box as sbox

from plug import series as SR
from plug import series2 as N2
from plug.fit_test.generator import overhangs
from plug.geom import box, capsule, prism_x, prism_y, to_bed, to_tm, union, vol_int, ycut
from plug.power import build_concept as BC
from plug.power import params as PP
from plug.thread import params as P

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "stl")
PREV = os.path.join(HERE, "vorschau")
L = 0.2                                           # Schichthöhe
CH = PP.CH_BED                                    # Fase an Bettkanten der Außenkanten (0,5)
SAMPLES = (("P3", 3.0), ("P45", 4.5))
VERSION = "1"                                     # ZIP-Version (L33: im Ergebnistext nennen)
de = SR.de


def arc(cx, cz, r, a0, a1, n=48):
    return [(cx + r * math.cos(math.radians(a)), cz + r * math.sin(math.radians(a))) for a in np.linspace(a0, a1, n)]


class Geo:
    """Maße und Lage eines Eckmusters (Ecke der Platte im Ursprung, Außenwände bei x = 0 und y = 0, z = 0 Plattenunterseite)."""

    def __init__(self, air):
        self.air = air
        self.d = P.pill(air)
        d = self.d
        self.wall = P.WALL_MIN
        self.cx = self.wall + d["mouth_l"] / 2
        self.cy = self.wall + d["mouth_w"] / 2
        self.pw = math.ceil(d["mouth_l"] + 2 * self.wall + 6)
        self.pl = math.ceil(d["mouth_w"] + 2 * self.wall + 6)
        self.outline = sbox(0, 0, self.pw, self.pl).buffer(-3).buffer(3)

    def xend(self, z):
        d = self.d
        return d["steg_w"] / 2 + math.sqrt(max(0.0, d["r"] ** 2 - z * z))


def cavity(g):
    """Tasche: Halbstadion (Viertelkreis-Enden) im Längsschnitt, an den Wänden zur Decke mit R gerundet."""
    d = g.d
    hf, r = d["steg_w"] / 2, d["r"]
    xz = [(-hf - r, -0.5), (hf + r, -0.5)] + arc(hf, 0.0, r, 0, 90) + arc(-hf, 0.0, r, 90, 180)
    w2, fr, ceil = d["width"] / 2, d["fillet"], d["ceil"]
    yz = [(g.cy - w2, -0.5), (g.cy + w2, -0.5)] + arc(g.cy + w2 - fr, ceil - fr, fr, 0, 90, 24) + arc(g.cy - w2 + fr, ceil - fr, fr, 90, 180, 24)
    a = prism_y([(g.cx + x, z) for x, z in xz], g.cy - w2, g.cy + w2)
    b = prism_x(yz, g.cx - hf - r - 1, g.cx + hf + r + 1)
    return a ^ b


def chamfer_cutter(g):
    """45°-Fase am Rand der Mündung: Schichtstufen von z = 0 bis z = Fase, je Höhe um (Fase − z) größer als die Tasche."""
    d = g.d
    c = d["chamfer"]
    parts = []
    for k in range(int(round(c / L))):
        zk = L * (k + 0.5)
        off = max(0.0, c - zk)
        hx, hy = g.xend(zk) + off, d["width"] / 2 + off
        parts.append(BC.G.extrude(sbox(g.cx - hx, g.cy - hy, g.cx + hx, g.cy + hy), L * k - 0.01, L * (k + 1) + 0.01))
    return union(parts)


def steg(g):
    """Steg von Wand zu Wand: oben voll gerundet, am Fuß mit Fase; reicht in y bis zum Rand der gefasten Mündung."""
    d = g.d
    hf, cs, st = d["steg_w"] / 2, d["steg_chamfer"], d["steg_top"]
    pts = [(-hf + cs, 0.0), (hf - cs, 0.0), (hf, cs), (hf, st - hf)] + arc(0.0, st - hf, hf, 0, 180, 48)[1:-1] + [(-hf, st - hf), (-hf, cs)]
    ext = d["width"] / 2 + d["chamfer"] + 0.5
    return prism_y([(g.cx + x, z) for x, z in pts], g.cy - ext, g.cy + ext)


def plate_corner(g):
    m = BC.slab_ch(g.outline, 0.0, P.PLATE_T, CH) - cavity(g) - chamfer_cutter(g)
    m = m + steg(g)
    return m + N2.emboss_side(N2.big_label("F2 " + g.name, 0, 3.4), g.pw / 2, P.PLATE_T - 5.5, 0.0)


def under_corner(g):
    d = g.d
    shell = BC.slab_ch(g.outline, 0.0, P.UK_H, CH) - BC.G.extrude(g.outline.buffer(-P.UK_WALL, join_style=2), 1.2, P.UK_H + 1)
    nx1, ny1 = g.cx + d["mouth_l"] / 2 + P.NOTCH_PAD, g.cy + d["mouth_w"] / 2 + P.NOTCH_PAD
    notch = sbox(-1, -1, nx1, ny1)
    return shell - BC.G.extrude(notch, -1, P.UK_H + 1) - BC.mouth_ch(notch.intersection(sbox(0, 0, nx1, ny1)), 0.0, CH)


def thread_path(g, n_pts=15):
    """Mittellinie eines taut gespannten Fadens: aus dem Hut (A) hoch, über die Stegkante, nach unten (B)."""
    d = g.d
    hf, st = d["steg_w"] / 2, d["steg_top"]
    xa = -(hf + d["gap0"] / 2)
    rr = hf + 0.4 + 0.02
    top = arc(0.0, st - hf, rr, 165, 15, n_pts)
    return [(xa, -P.UK_H + 1.6)] + top + [(-xa, -P.UK_H + 1.6)]


def chain(points, r, g):
    return union([capsule((g.cx + a[0], g.cy, a[1]), (g.cx + b[0], g.cy, b[1]), r, 8) for a, b in zip(points[:-1], points[1:])])


def probe(man, origin, direction, maxlen=30.0):
    """Freie Strecke ab `origin` in Achsenrichtung `direction` (mm): Bisektion mit einem dünnen Quader (0,1 × 0,1), der das Netz nicht schneiden darf."""
    ax = int(np.argmax(np.abs(direction)))
    sg = 1 if direction[ax] > 0 else -1

    def free(h):
        lo = [origin[i] - 0.05 for i in range(3)]
        hi = [origin[i] + 0.05 for i in range(3)]
        lo[ax], hi[ax] = (origin[ax], origin[ax] + h) if sg > 0 else (origin[ax] - h, origin[ax])
        return vol_int(man, box(lo[0], hi[0], lo[1], hi[1], lo[2], hi[2])) < 1e-6
    if free(maxlen):
        return None
    a, b = 0.0, maxlen
    for _ in range(14):
        m = (a + b) / 2
        a, b = (m, b) if free(m) else (a, m)
    return a


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
    bad = 0
    parts, info, geos = {}, {}, {}
    rep("Fadenführung, Eckmuster (Plan Stand 2, plug/thread/plan.html): halbe Pille mit Steg, Fase %s am Rand, %s am Steg-Fuß" % (de(P.PILL["chamfer"], 1), de(P.PILL["steg_chamfer"], 1)))
    for name, air in SAMPLES:
        g = Geo(air)
        g.name = name
        geos[name] = g
        parts["F2_%s_plate" % name] = plate_corner(g)
        parts["F2_%s_under" % name] = under_corner(g)
    rep("\nTeile (Druckausrichtung, Bett z = 0, ohne Stützen):")
    for name, man in parts.items():
        m = to_bed(man)
        tm = to_tm(m)
        tm.export(os.path.join(OUT, name + ".stl"))
        gr, nl = SR.estimate(m)
        ov = overhangs(m, name)
        info[name] = dict(tm=tm, g=gr, layers=nl, ov=ov)
        rep("  %-18s %5.1f × %5.1f × %5.1f mm  %5.1f cm³  ≈ %4.1f g  dicht=%s" % (name + ".stl", *tm.extents, tm.volume / 1000.0, gr, tm.is_watertight))
        rep("      waagerechte Decken: %s   Überhang flacher als 45° zur Senkrechten: %.0f mm²" % (
            "; ".join("z=%.1f: %.0f mm² (%.1f × %.1f)" % f for f in sorted(ov["flat"], key=lambda t: -t[1])[:3]) or "keine", ov["steep_area"]))
        bad += (not tm.is_watertight)

    def chk(txt, v, limit=0.05):
        nonlocal bad
        ok = v <= limit
        bad += (not ok)
        rep("  %-92s %8.3f  %s" % (txt, v, "ok" if ok else "KOLLISION"))

    rep("\nMaße im gebauten Modell (gemessen mit einem dünnen Prüfquader):")
    for name, g in geos.items():
        d = g.d
        tm = parts["F2_%s_plate" % name]
        hf = d["steg_w"] / 2
        z_top = d["steg_top"]
        air = probe(tm, [g.cx, g.cy, z_top + 0.001], [0, 0, 1])
        top = (P.PLATE_T + 1.0) - probe(tm, [g.cx, g.cy, P.PLATE_T + 1.0], [0, 0, -1])      # Oberseite der Platte
        roof = top - (z_top + air)
        wl = probe(tm, [g.cx - hf - 0.05, g.cy, 3.0], [-1, 0, 0])
        wr = probe(tm, [g.cx + hf + 0.05, g.cy, 3.0], [1, 0, 0])
        a0 = probe(tm, [g.cx - (hf - d["steg_chamfer"] + 0.1), g.cy, 0.05], [-1, 0, 0])
        b0 = probe(tm, [g.cx + (hf - d["steg_chamfer"] + 0.1), g.cy, 0.05], [1, 0, 0])
        rep("  %-4s Luft über dem Steg %.2f (Soll %.1f) · Material über der Decke %.2f (Soll %.1f) · Spalt neben dem Steg bei z = 3: links %.2f, rechts %.2f (Soll ≥ %.1f)" % (
            name, air, d["air"], roof, d["roof"], wl, wr, d["gap_top"] - 0.1))
        rep("       Eingang A %.1f mm weit, Ausgang B %.1f mm weit an der Unterseite (bei z = 0,05; Soll %.1f mit Fase, %.1f ohne)" % (a0 + 0.1, b0 + 0.1, d["gap_mouth"], d["gap0"]))
        bad += (abs(air - d["air"]) > 0.05) + (min(wl, wr) < d["gap_top"] - 0.15) + (abs(a0 + 0.1 - d["gap_mouth"]) > 0.3) + (abs(b0 + 0.1 - d["gap_mouth"]) > 0.3)

    rep("\nPrüfung der Wege (Überschneidungsvolumen, mm³; muss 0 sein):")
    for name, g in geos.items():
        d = g.d
        pl = parts["F2_%s_plate" % name]
        un = parts["F2_%s_under" % name].translate([0, 0, -P.UK_H])
        chk("%s: Plattenecke auf der Unterkasten-Ecke (nur Auflage)" % name, vol_int(pl, un))
        chk("%s: Faden Ø %s von A über den Steg nach B" % (name, de(P.THREAD_D, 1)), vol_int(pl, chain(thread_path(g), P.THREAD_D / 2, g)), 0.2)
        hf, st = d["steg_w"] / 2, d["steg_top"]
        xa = -(hf + d["gap0"] / 2)
        tip = (-hf - 1.0, st + 1.6)
        needle = chain([(xa - 4.2, -P.UK_H + 1.6), tip], P.NEEDLE_D / 2, g)
        chk("%s: Nadel Ø %s von unten durch den linken Spalt, Spitze über dem Steg" % (name, de(P.NEEDLE_D, 1)), vol_int(pl, needle))
        needle_bad = chain([(xa - 4.2, -P.UK_H + 1.6), (-hf - 1.0, d["ceil"] + 0.6)], P.NEEDLE_D / 2, g)
        chk("%s: Kontrolle: Nadelspitze 0,6 über der Decke stößt an" % name, 0.0 if vol_int(pl, needle_bad) > 0.05 else 1.0)
        cut_notch = vol_int(under_corner(g).translate([0, 0, -P.UK_H]), chain(thread_path(g), P.THREAD_D / 2, g))
        chk("%s: Faden im Unterkasten (Eckaussparung lässt den Weg frei)" % name, cut_notch)
    rep("  -> %s" % ("keine Kollisionen" if not bad else "%d Fehler!" % bad))

    tot = sum(i["g"] for i in info.values())
    from plug.roadmap import build as rb
    for prof, pr in rb.PROFILE.items():
        mins = sum(i["g"] / pr["rate"] * 60.0 + i["layers"] * pr["layer"] / 60.0 for i in info.values()) + pr["start"]
        rep("Material ≈ %.0f g, Zeit %s ≈ %.1f h" % (tot, prof, mins / 60.0))
    rep("Bei deinem Drucker (Nacht 1: 47 g in 2,5 h) ≈ %.1f h" % (tot / 47.0 * 2.5))
    with open(os.path.join(OUT, "pruefbericht.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(rep.lines) + "\n")
    previews(geos, parts)
    write_readme(info, tot, geos)
    zpath = os.path.join(OUT, "faden_eckmuster_v%s.zip" % VERSION)
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(os.listdir(OUT)):
            if f.endswith((".stl", ".txt")):
                z.write(os.path.join(OUT, f), f)
    rep("%s: %.0f kB" % (os.path.relpath(zpath, HERE), os.path.getsize(zpath) / 1024))
    return bad


def previews(geos, parts):
    import preview
    from PIL import Image
    col = dict(plate="#b6cde0", under="#8fa3b8")
    tiles = []
    for name, g in geos.items():
        pl, un = parts["F2_%s_plate" % name], parts["F2_%s_under" % name]
        # Schnitt längs durch die Tasche (Blick von −y auf die Schnittfläche bei y = Taschenmitte)
        cut = [(to_tm(ycut(pl, g.cy)), col["plate"]), (to_tm(ycut(un.translate([0, 0, -P.UK_H]), g.cy)), col["under"])]
        tiles.append(preview.render(cut, size=(900, 800), azim=-90, elev=0))
    sheet = Image.new("RGB", (1800, 800), "white")
    for i, t in enumerate(tiles):
        sheet.paste(t, (i * 900, 0))
    sheet.save(os.path.join(PREV, "schnitt.png"))
    ims = []
    for name, g in geos.items():
        pl = parts["F2_%s_plate" % name]
        ims.append(preview.render([(to_tm(pl), col["plate"])], size=(900, 800), azim=-60, elev=-65))
    sheet = Image.new("RGB", (1800, 800), "white")
    for i, t in enumerate(ims):
        sheet.paste(t, (i * 900, 0))
    sheet.save(os.path.join(PREV, "unterseite.png"))
    ims = []
    for name, g in geos.items():
        pl, un = parts["F2_%s_plate" % name], parts["F2_%s_under" % name]
        ims.append(preview.render([(to_tm(un), col["under"]), (to_tm(pl.translate([0, 0, 6.0])), col["plate"])], size=(900, 800), azim=-35, elev=35))
    sheet = Image.new("RGB", (1800, 800), "white")
    for i, t in enumerate(ims):
        sheet.paste(t, (i * 900, 0))
    sheet.save(os.path.join(PREV, "aufbau.png"))
    print("Vorschau: %s" % os.path.relpath(PREV, os.path.dirname(os.path.dirname(HERE))))


def write_readme(info, tot, geos):
    d3, d45 = geos["P3"].d, geos["P45"].d
    g = {n: info[n]["g"] for n in info}
    txt = f"""FADENFÜHRUNG, ECKMUSTER v{VERSION}  (Plan: plug/thread/plan.html, Stand 2, abgenickt)
=========================================================================

Zwei Eckmuster für die Fadenführung an den Plattenecken: Variante A als „halbe Pille mit Steg“. Eine nach unten offene Tasche an der Plattenunterseite
mit runder Decke und einem Steg in der Mitte; der Faden läuft von unten durch den einen Spalt, über den Steg und durch den anderen Spalt wieder nach unten.
Kein Tunnel, kein Trichter. Ein- und Ausgang haben eine Fase von {de(P.PILL['chamfer'], 1)} × 45° am Taschenrand, der Steg {de(P.PILL['steg_chamfer'], 1)} × 45° am Fuß.
Kein Gebäude, kein Dock, keine Zapfen: nur die Ecke der Oberplatte und eine Ecke des Unterkastens zum Daraufstellen.

Dateien (alle in Druckausrichtung, keine Stützen)
  F2_P3_plate.stl    Plattenecke {geos['P3'].pw} × {geos['P3'].pl} × {de(P.PLATE_T, 1)} mm, Luft über dem Steg {de(d3['air'], 1)} (Decke {de(d3['ceil'], 1)}), Beschriftung „F2 P3“.   ≈ {de(g['F2_P3_plate'], 1)} g
  F2_P3_under.stl    Unterkasten-Ecke {geos['P3'].pw} × {geos['P3'].pl} × {de(P.UK_H, 1)} mm, hohl, Eckaussparung {de(d3['notch_l'], 0)} × {de(d3['notch_w'], 0)}.   ≈ {de(g['F2_P3_under'], 1)} g
  F2_P45_plate.stl   Plattenecke {geos['P45'].pw} × {geos['P45'].pl} × {de(P.PLATE_T, 1)} mm, Luft über dem Steg {de(d45['air'], 1)} (Decke {de(d45['ceil'], 1)}), Beschriftung „F2 P45“.   ≈ {de(g['F2_P45_plate'], 1)} g
  F2_P45_under.stl   Unterkasten-Ecke {geos['P45'].pw} × {geos['P45'].pl} × {de(P.UK_H, 1)} mm, hohl, Eckaussparung {de(d45['notch_l'], 0)} × {de(d45['notch_w'], 0)}.   ≈ {de(g['F2_P45_under'], 1)} g
  Zusammen ≈ {de(tot, 0)} g; bei deinem Drucker (Nacht 1: 47 g in 2,5 h) etwa {de(tot / 47.0 * 2.5, 1)} h.

Slicer wie bisher (Bambu, PLA, 0,2 mm, 3 Wände, 15 % Füllung), **ohne Stützen**, „Thick bridges“ an.
  Plattenecke: Unterseite (Tasche) liegt auf dem Bett. Die Decke der Tasche ist rund; über dem Steg liegt eine Brücke von {de(d3['steg_w'], 0)} mm, die Viertelkreise laufen
  in den letzten 2 bis 3 mm flach aus (Prüfbericht nennt die Überhänge). Fasen am Bett gleichen den Elefantenfuß aus.
  Unterkasten-Ecke: Boden auf dem Bett, offen nach oben.
  Die Fase am Taschenrand ist an den Rundungen der Enden etwas kleiner als {de(P.PILL['chamfer'], 1)} (45° zur Wand in jeder Höhe, die Wand ist dort gekrümmt).

Kaufteile: Faden (so wie du ihn für den Hut nimmst), ein Stück Filz oder Pappe als „Hut“ (etwa 60 × 60 mm). Keine Schrauben.

Aufbau
  1. Plattenecke mit der Unterseite nach unten auf die Unterkasten-Ecke setzen (gleiche Ecke zu gleicher Ecke, die Eckaussparung liegt unter der Tasche).
  2. Das Ganze auf den Filz oder die Pappe stellen.
  3. Faden von unten durch den linken Spalt (Eingang A), über den Steg, durch den rechten Spalt (Ausgang B) nach unten schieben.
     Fädeln nur mit dem Faden, ohne Nadel und Haken: er biegt sich von allein zurecht (Angabe des Nutzers). Klappt es nicht, gerne mit Nadel, Pinzette oder gebogenem Draht.
  4. Enden durch den Filz stechen, straff ziehen, verknoten. Kräftig am Faden ziehen: Plattenecke bleibt?

Prüfung: siehe Testbogen (plug/thread/, folgt) und pruefbericht.txt.
"""
    with open(os.path.join(OUT, "README.txt"), "w", encoding="utf-8") as f:
        f.write(txt)


if __name__ == "__main__":
    raise SystemExit(1 if main() else 0)
