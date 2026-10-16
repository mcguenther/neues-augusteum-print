#!/usr/bin/env python3
"""Passungsserien für den ersten Nachtdruck (Kassette), `stl/steckmodul_night1/`.

Abstände unter 0,5 mm lassen sich am Probestück nicht messen. Darum trägt jedes Teil seinen Spielwert als Gravur, und die Hand
ist das Messgerät: je Serie die engste Variante, die ohne Gewalt passt, und die weiteste, die nicht merklich wackelt.
Alle Serien sind unabhängig voneinander (Fahrplan: plug/roadmap/page.html), jede Fuge hat genau eine Serie:

  K  Kontakt-Distanzplättchen   t = 1,2 / 1,8 / 2,4 mm → Einstecktiefe E = HDR_UP − t (Durchgang prüfen, nicht Gefühl)
  N  Schieber                   KEY_CLR 0,05 / 0,10 / 0,15 / 0,20, in echter Breite, Funnellöcher und Griffkerbe wie im Probestück
  S  Boden-Platten              KASS_CLR 0,05 / 0,10 / 0,15 / 0,20: Unterseite des Probestücks mit Schacht und Nut, 9 mm hoch
  C  Kassette                   unverändert wie im Probestück (Lehre für S, zum Bestücken)
  R  Buchsenhülsen              SNUG 0,08 / 0,12 / 0,16 / 0,20 ohne Rippen (die Kassette hat 0,22 mit Rippen)
  FM Mulden-Ringe               CLR 0,10 / 0,15 / 0,20 (das Probestück hat 0,25); Lehre ist 1_probestueck.stl
  D  Passprobe v6               unverändert (stl/steckmodul_probe/0_passprobe.stl)

Die Geometrie kommt aus denselben Funktionen wie das Probestück (plug/institute.py, plug/dupont.py); nur das Spiel wird je Teil
verändert. Alle Teile liegen in Druckausrichtung auf z = 0, keine Stützen.

Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m plug.series      # STL, README.txt und ZIP nach stl/steckmodul_night1/, Prüfbericht, Vorschau nach vorschau/steckmodul_night1/
"""
import os
import zipfile

import manifold3d as m3d
import numpy as np

from plug import dupont as sd
from plug import institute as I
from plug import sample as S
from plug.fit_test import generator as pp
from plug.fit_test.generator import overhangs
from plug.geom import box, cbox, cyl, union, diff, ext, prism_x, to_bed, to_tm, vol_int

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))     # Repo-Wurzel
OUT = os.path.join(HERE, "stl", "steckmodul_night1")
PREV = os.path.join(HERE, "vorschau", "steckmodul_night1")

# Serien: Spiel je Seite in mm (Wert im Probestück jeweils in der Beschreibung oben)
K_T = (1.2, 1.8, 2.4)
N_CLR = (0.05, 0.10, 0.15, 0.20)
S_CLR = (0.05, 0.10, 0.15, 0.20)
R_SNUG = (0.08, 0.12, 0.16, 0.20)
FM_CLR = (0.10, 0.15, 0.20)

SLAB_H = 9.0          # Höhe der Boden-Platten (Schacht ist darin 9 mm tief geführt, im Gebäude 14,6)
RING_MARGIN = 4.0     # Wandstärke der Mulden-Ringe außerhalb des Relief-Spiels
RING_FLOOR = 1.2      # Boden der Ringe (Anschlag für den Fuß)
GAP = 5.0             # Abstand zwischen Teilen auf dem Bett
BED = (220.0, 220.0)  # angenommenes Druckbett für die Anordnungsvorschau (Slicer ordnet selbst an)


def de(x, n=2):
    return ("%.*f" % (n, x)).replace(".", ",")


MARK_BOLD = 0.28      # Verbreiterung der Schrift je Seite (fett)
CHAMF = 0.3           # Fase (45°) an jedem Pin-Loch, auf beiden Seiten


def mark_cs(text, rank, size):
    """2D-Marke: Text (fett, DejaVu Bold + MARK_BOLD) mittig bei x = 0, darunter `rank` Punkte (1 Punkt = engste bzw. dünnste Variante)."""
    import generate
    cs = generate.text_cross_section(text, size, 0.0, -size / 2, anchor="center")
    cs = cs.offset(MARK_BOLD, m3d.JoinType.Round)
    r = size * 0.17
    y = -size * 0.72 - 1.1 - r
    dots = [m3d.CrossSection.circle(r, 24).translate(((i - (rank - 1) / 2.0) * 3.0 * r, y)) for i in range(rank)]
    return m3d.CrossSection.batch_boolean([cs] + dots, m3d.OpType.Add)


def engrave_top(cs, x, y, z_top, depth):
    """Gravur in eine waagerechte Fläche (Oberkante bei z_top), lesbar von oben."""
    return m3d.Manifold.extrude(cs.translate((x, y)), depth + 0.01).translate([0, 0, z_top - depth])


def engrave_side(cs, x, z, y_face, depth):
    """Gravur in eine senkrechte Fläche bei y = y_face (Außenseite zeigt nach −y), lesbar von −y: Text läuft in +x, oben ist +z."""
    m = m3d.Manifold.extrude(cs, depth + 0.01).rotate([90, 0, 0])          # (x, v, e) -> (x, -e, v)
    return m.translate([x, y_face + depth, z])


def pin_hole(x, y, z0, z1, d=None):
    """Durchgangsloch für einen Pin mit 45°-Fase CHAMF an beiden Enden (z0 = unten, z1 = oben)."""
    d = sd.HOLE if d is None else d
    return [cyl(d / 2, z0 - 0.01, z1 + 0.01, cx=x, cy=y, n=32),
            m3d.Manifold.cylinder(CHAMF + 0.01, d / 2 + CHAMF + 0.01, d / 2, 32).translate([x, y, z0 - 0.01]),
            m3d.Manifold.cylinder(CHAMF + 0.01, d / 2, d / 2 + CHAMF + 0.01, 32).translate([x, y, z1 - CHAMF])]


def rect_cs(w, d, r=sd.FOOT_R):
    cs = m3d.CrossSection.square((w, d), center=True)
    return cs.offset(-r, m3d.JoinType.Round).offset(r, m3d.JoinType.Round)


# --------------------------------------------------------------------------
# Teile (Konstruktionslage = Probestück-Koordinaten, Kassette mittig bei y = 0; to_bed legt sie aufs Bett)
# --------------------------------------------------------------------------
def contact_spacers():
    """K: drei Plättchen 14,5 × 14 mm mit vier Löchern im 2,54-Raster, beidseitig mit Fase 0,3 mm; Gravur K + Dicke, Rangpunkte."""
    W, D, gap = 14.5, 14.0, 3.0
    parts = []
    for i, t in enumerate(K_T):
        cx = (i - 1) * (W + gap)
        m = box(cx - W / 2, cx + W / 2, -D / 2, D / 2, 0, t)
        cuts = []
        for px in sd.pin_x():
            cuts += pin_hole(cx + px, 4.6, 0.0, t)
        cuts.append(engrave_top(mark_cs("K " + de(t, 1), i + 1, 4.0), cx, -0.4, t, depth=min(0.7, t - 0.6)))
        parts.append(diff(m, *cuts))
    return union(parts)


def slider(c, P):
    """Ein Schieber wie im Probestück (Schwalbenschwanz, Trichterlöcher, Griffkerbe) mit KEY_CLR = c, Konstruktionslage."""
    d, L = P["d"], P["L"]
    F, T = d["F"], sd.FUNNEL_T
    yc = (d["cass_y0"] + d["cass_y1"]) / 2
    xout = L["xwall"]
    k = prism_x(I.slider_prof(d, c), d["x_in"], xout).translate([0, -yc, 0])
    k = diff(k, *[h.translate([0, -yc, 0]) for h in sd.funnel_holes(-F, d["HY"])])      # unten Trichter 2,4 → 1,4
    ypin = d["HY"] - yc
    k = diff(k, *[m3d.Manifold.cylinder(CHAMF + 0.01, sd.HOLE / 2, sd.HOLE / 2 + CHAMF + 0.01, 32).translate([px, ypin, -F + T - CHAMF])
                  for px in sd.pin_x()])                                                  # oben Fase 0,3
    k = diff(k, cbox(1.0, 6.0, -F - 0.01, -F + 0.5, cx=xout - 0.2, cy=0.0))
    rank = N_CLR.index(c) + 1
    return diff(k, engrave_top(mark_cs("N " + de(c), rank, 4.6), (d["x_in"] + xout) / 2, 9.5, -F + T, depth=0.4))


def sliders(P):
    """N: vier Schieber nebeneinander (Reihe entlang x, Druckausrichtung)."""
    w = P["L"]["xwall"] - P["d"]["x_in"] + GAP
    return union([to_bed(slider(c, P)).translate([i * w, 0, 0]) for i, c in enumerate(N_CLR)])


def slab(c, P):
    """S: Unterseite des Probestücks (Fußumriss, Schacht mit Spiel c, Schwalbenschwanz-Nut), SLAB_H hoch, Lage wie im Gebäude."""
    d, L = P["d"], P["L"]
    F = d["F"]
    yc = (d["cass_y0"] + d["cass_y1"]) / 2
    hx, hy = L["bar"] / 2, S.PROBE_L / 2
    m = ext(rect_cs(2 * hx, 2 * hy), -F, -F + SLAB_H)
    x0, x1 = -d["cass_w"] / 2, d["cass_w"] / 2
    y0, y1 = d["cass_y0"] - yc, d["cass_y1"] - yc
    shaft = box(x0 - c, x1 + c, y0 - c, y1 + c, -F - 0.01, -F + SLAB_H + 0.01)
    groove = prism_x(I.slider_prof(d, 0.0, 0.01), d["x_in"], L["xwall"] + 6.0).translate([0, -yc, 0])
    rank = S_CLR.index(c) + 1 if c in S_CLR else 1
    lab = engrave_side(mark_cs("S " + de(c), rank, 4.8), 0.0, -F + 6.6, -hy, depth=0.6)
    return diff(m, shaft, groove, lab)


def slabs(P, cache):
    """S: vier Platten nebeneinander (Reihe entlang x). cache[c] = Platte in Konstruktionslage (für die Prüfungen)."""
    for c in S_CLR:
        cache[c] = slab(c, P)
    pitch = P["L"]["bar"] + GAP
    return [to_bed(cache[c]).translate([i * pitch, 0, 0]) for i, c in enumerate(S_CLR)]


def sleeves():
    """R: vier Buchsenhülsen (beidseitig offen, 14,25 mm hoch wie die Tasche der Kassette) auf einer 1-mm-Platte mit Gravur."""
    H = sd.HSG_H + sd.HSG_TOL
    pw = [sd.HSG_W + 2 * s for s in R_SNUG]
    pd = [sd.HSG_T + 2 * s for s in R_SNUG]
    ow = [w + 2 * sd.WALL for w in pw]
    od = [dd + 2 * sd.WALL for dd in pd]
    gap = 5.0
    total = sum(ow) + gap * (len(ow) - 1)
    x = -total / 2
    centers = []
    for w in ow:
        centers.append(x + w / 2)
        x += w + gap
    odm = max(od)
    plate = box(-total / 2 - 2.0, total / 2 + 2.0, -odm / 2 - 12.0, odm / 2 + 2.0, 0, 1.0)
    solid = [plate]
    cuts = []
    for cx, w, dd, o_w, o_d, s in zip(centers, pw, pd, ow, od, R_SNUG):
        solid.append(cbox(o_w, o_d, 0, H, cx=cx))
        cuts.append(cbox(w, dd, -0.01, H + 0.01, cx=cx))
        cuts.append(engrave_top(mark_cs("R " + de(s), R_SNUG.index(s) + 1, 4.2), cx, -odm / 2 - 5.0, 1.0, depth=0.5))
    return diff(union(solid), *cuts), centers


def mulde_rings(P):
    """FM: Mulde des Probestücks als Ring (gleiche Funktionen wie die Platte), Boden RING_FLOOR dick, Spiel CLR je Variante."""
    d = P["d"]
    F = d["F"]
    poly = S.probe_source()[1]
    cs = I.hcs(poly)
    old = sd.CLR
    rings = []
    try:
        for i, c in enumerate(FM_CLR):
            sd.CLR = c                                               # pocket_cuts liest sd.CLR beim Aufruf
            outer = I.rounded(cs).offset(c + sd.RELIEF + RING_MARGIN, m3d.JoinType.Round)
            blk = ext(outer, -F - RING_FLOOR, 0.0)
            cuts = I.pocket_cuts(cs, F)
            yface = outer.bounds()[1]                                  # äußere −y-Fläche des Rings
            lab = engrave_side(mark_cs("F " + de(c), FM_CLR.index(c) + 1, 4.6), 2.5, -F - RING_FLOOR + 7.0, yface, depth=0.7)
            rings.append(diff(blk, *(cuts + [lab])))
    finally:
        sd.CLR = old
    xs = [r.bounding_box() for r in rings]
    out, x = [], 0.0
    for r, b in zip(rings, xs):
        w = b[3] - b[0]
        out.append(to_bed(r).translate([x - b[0], 0, 0]))
        x += w + GAP
    return union(out)


# --------------------------------------------------------------------------
def estimate(man, infill=0.15):
    """Geschätztes extrudiertes Material in g (Voxelmodell, 3 Wände, 4 Deck-/Bodenschichten, PLA 1,24 g/cm³) und Schichtzahl."""
    from scipy import ndimage as ndi
    tm = to_tm(man)
    a = tm.voxelized(0.2).fill().matrix
    sx = np.zeros((3, 3, 3), bool); sx[1, 1, 1] = True; sx[0, 1, 1] = sx[2, 1, 1] = sx[1, 0, 1] = sx[1, 2, 1] = True
    sz = np.zeros((3, 3, 3), bool); sz[1, 1, 1] = True; sz[1, 1, 0] = sz[1, 1, 2] = True
    core = ndi.binary_erosion(ndi.binary_erosion(a, structure=sx, iterations=6), structure=sz, iterations=4)
    v = 0.2 ** 3 / 1000.0
    cm3 = (a.sum() - core.sum()) * v + infill * core.sum() * v
    return cm3 * 1.24, a.shape[2]


def pack(items, bed=BED):
    """Einfache Regalpackung (Reihen nach Höhe der y-Ausdehnung). Rückgabe: Positionen (x, y) der Ecken und Gesamtbedarf."""
    order = sorted(items, key=lambda it: -it[2])
    x = y = rowh = 0.0
    pos, maxx = {}, 0.0
    for name, w, h in order:
        if x + w > bed[0] and x > 0:
            x, y, rowh = 0.0, y + rowh + GAP, 0.0
        pos[name] = (x, y)
        x += w + GAP
        rowh = max(rowh, h)
        maxx = max(maxx, x - GAP)
    return pos, (maxx, y + rowh)


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(PREV, exist_ok=True)
    print("Baue das Probestück als Bezug (Kassette, Schieber, Leiste) …")
    P = I.build_all(S.probe_source(), win_rows=S.WIN_ROWS, win_h=S.WIN_H, screw_ring=(2.3, 4.8), center_cassette=True)
    d = P["d"]
    fl = I.files(P)

    parts = {}
    parts["K_contact_spacers"] = contact_spacers()
    parts["N_sliders"] = sliders(P)
    slab_cache = {}
    parts["S_floor_slabs"] = union(slabs(P, slab_cache))
    parts["C_cassette"] = fl["kassette"]
    sl, centers = sleeves()
    parts["R_sleeves"] = sl
    parts["FM_mulde_rings"] = mulde_rings(P)
    parts["D_fitprobe_v6"] = pp.passprobe()

    print("\nTeile (Druckausrichtung, Bett z = 0):")
    info = {}
    for name, man in parts.items():
        tm = to_tm(man)
        path = os.path.join(OUT, name + ".stl")
        tm.export(path)
        g, nl = estimate(man)
        ov = overhangs(man, name)
        info[name] = dict(tm=tm, g=g, layers=nl, flat=ov["flat"], steep=ov["steep_area"])
        print("  %-24s %6.1f × %6.1f × %5.1f mm  %5.1f cm³  ≈ %4.1f g  dicht=%s" % (
            name + ".stl", *tm.extents, tm.volume / 1000.0, g, tm.is_watertight))
        print("      waagerechte Decken: %s   Überhang flacher als 45°: %.0f mm²" % (
            "; ".join("z=%.1f: %.0f mm² (%.1f × %.1f)" % f for f in sorted(ov["flat"], key=lambda t: -t[1])[:3]) or "keine", ov["steep_area"]))

    # --- Passungsprüfung in der Konstruktionslage: nichts schneidet sich, das Spiel stimmt
    print("\nPrüfung der Passungen (Überschneidungsvolumen, mm³; muss 0 sein):")
    bad = 0

    def chk(txt, v, limit=0.05):
        nonlocal bad
        ok = v <= limit
        bad += (not ok)
        print("  %-62s %8.3f  %s" % (txt, v, "ok" if ok else "KOLLISION"))
    kass = P["kass"]
    chk("Kontrolle: Kassette passt bei Spiel 0,00 gerade (mittig, Maß stimmt)", vol_int(kass, slab(0.0, P)))
    v_neg = vol_int(kass, slab(-0.02, P))
    print("  Kontrolle: bei Spiel −0,02 stößt die Kassette an: %s (%.1f mm³)" % ("ja" if v_neg > 0.5 else "NEIN", v_neg))
    bad += (v_neg <= 0.5)
    for c in S_CLR:
        chk("Kassette in Boden-Platte c=%s" % de(c), vol_int(kass, slab_cache[c]))
    for c in N_CLR:
        k = slider(c, P)
        chk("Schieber %s in Nut der Platte %s" % (de(c), de(S_CLR[-1])), vol_int(k, slab_cache[S_CLR[-1]]))
        chk("Schieber %s unter der Kassette" % de(c), vol_int(k, kass))
        chk("Schieber %s und Winkelleiste (Pins durch die Trichter)" % de(c), vol_int(k, P["header"]))
    hz = sd.housing_part(0.0).translate([0, -d["HY"], 0])
    for cx, s_ in zip(centers, R_SNUG):
        chk("Buchse (Nennmaß) in Hülse %s" % de(s_), vol_int(hz.translate([cx, 0, 0]), parts["R_sleeves"]))
    print("  -> %s" % ("keine Kollisionen" if not bad else "%d Kollisionen!" % bad))

    # --- Anordnung (Vorschlag für ein 220 × 220-Bett)
    items = []
    for name, i_ in info.items():
        e = i_["tm"].extents
        items.append((name, float(e[0]), float(e[1])))
    pos, need = pack(items)
    print("\nAnordnung: alle Teile brauchen etwa %.0f × %.0f mm (Bett %.0f × %.0f angenommen)" % (need[0], need[1], *BED))
    boxes = [(n, pos[n][0], pos[n][1], pos[n][0] + w, pos[n][1] + h) for n, w, h in items]
    clash = [(a[0], b[0]) for i, a in enumerate(boxes) for b in boxes[i + 1:]
             if a[1] < b[3] and b[1] < a[3] and a[2] < b[4] and b[2] < a[4]]
    print("  Überlappungen der Anordnung: %s" % (clash or "keine"))
    bad += len(clash)

    # --- Zusammenfassung Material und Zeit (Modell wie in plug/roadmap/build.py)
    from plug.roadmap import build as rb
    tot_g = sum(i_["g"] for i_ in info.values())
    print("\nMaterial gesamt ≈ %.0f g PLA (Schätzung, 15 %% Füllung, 3 Wände)" % tot_g)
    for prof, pr in rb.PROFILE.items():
        mins = sum(i_["g"] / pr["rate"] * 60.0 + i_["layers"] * pr["layer"] / 60.0 for i_ in info.values()) + pr["start"]
        print("  Zeit %-8s ≈ %.1f h" % (prof, mins / 60.0))

    tiers = {}
    for tname, keys in (("core", ("K_contact_spacers", "N_sliders", "S_floor_slabs", "C_cassette")),
                        ("core_d", ("K_contact_spacers", "N_sliders", "S_floor_slabs", "C_cassette", "R_sleeves", "D_fitprobe_v6")),
                        ("all", tuple(info))):
        tiers[tname] = dict(g=sum(info[k]["g"] for k in keys), **{
            prof: (sum(info[k]["g"] / pr["rate"] * 60.0 + info[k]["layers"] * pr["layer"] / 60.0 for k in keys) + pr["start"]) / 60.0
            for prof, pr in rb.PROFILE.items()})
    previews(P, parts, info, pos)
    write_readme(P, info, pos, need, tiers)
    zpath = os.path.join(OUT, "night1_fit_series.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(os.listdir(OUT)):
            if f.endswith(".stl") or f == "README.txt":
                z.write(os.path.join(OUT, f), f)
    print("\n%s: %.0f kB" % (os.path.relpath(zpath, HERE), os.path.getsize(zpath) / 1024))
    return P, info


def previews(P, parts, info, pos):
    import preview
    col = dict(K="#d9b24a", N="#6bbf78", S="#c9b68a", C="#e3862a", R="#e8c58f", FM="#8fa3b8", D="#b9bfc4")
    items = []
    for name, man in parts.items():
        tm = to_tm(man)
        key = name.split("_")[0]
        x, y = pos[name]
        tm.apply_translation([x - tm.bounds[0][0], y - tm.bounds[0][1], 0])
        items.append((tm, col[key]))
    bed = to_tm(box(0, BED[0], 0, BED[1], -0.6, -0.1))
    items.append((bed, "#e6e8e6"))
    im = preview.render(items, size=(1500, 1000), azim=-30, elev=48)
    im.save(os.path.join(PREV, "anordnung.png"))
    # so wird geprüft: Platte, Schieber und Kassette zusammengesetzt, längs durch die Pin-Reihe geschnitten
    d = P["d"]
    ycl = (d["cass_y0"] + d["cass_y1"]) / 2
    ypin = d["HY"] - ycl
    cut = lambda m: sd.ycut(m, ypin)
    parts_ = [(to_tm(cut(slab(S_CLR[-1], P))), "#c9b68a"), (to_tm(cut(slider(N_CLR[2], P))), "#6bbf78"), (to_tm(cut(P["kass"])), "#e3862a"),
              (to_tm(cut(P["housing"])), "#f4f1e8")]
    im = preview.render(parts_, size=(1500, 900), azim=-62, elev=22)
    im.save(os.path.join(PREV, "schnitt_platte_schieber_kassette.png"))
    # Stapel für K: Leiste, Plättchen (t = 1,8), Buchse, längs durch einen Pin
    t = 1.8
    zhb = d["z_hb"]
    plate = box(-7.0, 7.0, ypin - 5.0, ypin + 5.0, zhb, zhb + t)
    for px in sd.pin_x():
        plate = plate - cyl(sd.HOLE / 2, zhb - 0.01, zhb + t + 0.01, cx=px, cy=ypin, n=32)
    xc = sd.pin_x()[2]
    cutx = lambda m: sd.xcut(m, xc)
    k_parts = [(to_tm(cutx(P["header"])), "#2d3236"), (to_tm(cutx(plate)), "#d9b24a"), (to_tm(cutx(P["housing"])), "#f4f1e8"),
               (to_tm(cutx(P["terms"])), "#caa13a")]
    im = preview.render(k_parts, size=(1500, 900), azim=0, elev=0)
    im.save(os.path.join(PREV, "kontakt_stapel.png"))
    # Beschriftung und Löcher aus der Nähe: Oberseite (K, N, R, D) bzw. Außenseite (S, FM), zu einem Bogen zusammengesetzt
    from PIL import Image
    views = [("K_contact_spacers", -90, 80), ("N_sliders", -90, 80), ("R_sleeves", -90, 80), ("D_fitprobe_v6", -90, 80),
             ("S_floor_slabs", -90, 6), ("FM_mulde_rings", -90, 6)]
    tiles = []
    for name, az, el in views:
        tmv = to_tm(parts[name])
        tiles.append(preview.render([(tmv, "#d9d2bf")], size=(1100, 420 if el > 40 else 330), azim=az, elev=el))
    sheet = Image.new("RGB", (1100, sum(t.size[1] for t in tiles)), "white")
    yy = 0
    for t_ in tiles:
        sheet.paste(t_, (0, yy)); yy += t_.size[1]
    sheet.save(os.path.join(PREV, "beschriftung.png"))
    print("Vorschau: %s" % os.path.relpath(PREV, HERE))


def write_readme(P, info, pos, need, tiers):
    d = P["d"]
    g = {k: info[k]["g"] for k in info}
    tot = sum(g.values())
    txt = f"""ERSTER NACHTDRUCK: PASSUNGSSERIEN FÜR DIE KASSETTE
==================================================

Warum Serien?
  Abstände unter 0,5 mm lassen sich am Probestück nicht messen. Jedes Teil trägt deshalb sein Spiel als Gravur
  (Millimeter je Seite). Beurteilt wird mit der Hand. Je Serie zwei Zahlen aufschreiben:
    ENG  = engste Variante, die ohne Gewalt passt (mit leichtem Fingerdruck, ohne Hebeln)
    WEIT = weiteste Variante, die noch nicht merklich wackelt
  Liegt der Wert dazwischen, wird er der neue Sollwert. Die Probestück-Werte stehen in jeder Zeile als Vergleich.

Beschriftung: Serienbuchstabe + Spiel in mm, dazu Punkte als Rang (1 Punkt = engste bzw. dünnste Variante, mehr Punkte = mehr Spiel).
  Die Schrift ist fett und 0,4 bis 0,8 mm tief graviert. Bei S und FM steht sie an der langen Außenseite (−y, zum Betrachter),
  bei N, K, R auf der Oberseite, bei D (Passprobe) unten auf dem Bett mit einem Zeichen je Feld (Dreieck 2,0 / Quadrat 1,8 / Kreis 1,6).

Alle Löcher für Pins (K-Plättchen, Schieber N, Passprobe D) haben auf beiden Seiten eine 45°-Fase von 0,3 mm
  (am Schieber unten der Trichter 2,4 → 1,4, oben 0,3), damit sie an der Oberfläche nicht durch Anschmelzen zuwachsen.

Alle Serien sind voneinander unabhängig (jede Fuge hat genau eine Serie), also alle in einem Druck.
Nach Gefühl geprüft wird alles außer K; K misst Durchgang.

Dateien (alle in Druckausrichtung, einfarbig, keine Stützen, keine Brims an Schieber und Plättchen)
  K_contact_spacers.stl   3 Plättchen 1,2 / 1,8 / 2,4 mm   ≈ {de(g['K_contact_spacers'],1)} g
  N_sliders.stl           4 Schieber, Spiel 0,05 / 0,10 / 0,15 / 0,20   ≈ {de(g['N_sliders'],1)} g   (Probestück: 0,15)
  S_floor_slabs.stl       4 Boden-Platten, Schachtspiel 0,05 / 0,10 / 0,15 / 0,20   ≈ {de(g['S_floor_slabs'],1)} g   (Probestück: 0,20)
  C_cassette.stl          Kassette wie im Probestück (Lehre für S, zum Bestücken)   ≈ {de(g['C_cassette'],1)} g
  R_sleeves.stl           4 Buchsenhülsen, Spiel 0,08 / 0,12 / 0,16 / 0,20, ohne Rippen   ≈ {de(g['R_sleeves'],1)} g   OPTIONAL: Passprobe Runde 2 testete 0,25 bis 0,33 (0,25 sitzt sehr gut), das hier ist nur der Bereich darunter
  FM_mulde_rings.stl      3 Mulden-Ringe, Spiel 0,10 / 0,15 / 0,20   ≈ {de(g['FM_mulde_rings'],1)} g   (Probestück: 0,25)   OPTIONAL, schwerstes Teil
  D_fitprobe_v6.stl       Passprobe Winkelleiste (wie stl/steckmodul_probe/0_passprobe.stl, jetzt mit Fase auf beiden Seiten und größerer Schrift)   ≈ {de(g['D_fitprobe_v6'],1)} g   OPTIONAL: nie gedruckt, aber Runden 1 bis 4 und das Probestück (passt mit 2,0) liegen vor, nur Bestätigung der Stufe

Ausbaustufen (Material und Druckzeit sind Schätzungen; die Zeit im Slicer hat Vorrang)
  Kern     K + N + S + C               ≈ {de(tiers['core']['g'],0)} g    ≈ {de(tiers['core']['normal'],1)} h normaler Drucker, ≈ {de(tiers['core']['schnell'],1)} h schneller Drucker
  + R + D  beide schon teilweise getestet ≈ {de(tiers['core_d']['g'],0)} g    ≈ {de(tiers['core_d']['normal'],1)} h / {de(tiers['core_d']['schnell'],1)} h
  alles    zusätzlich FM (Mulden-Ringe) ≈ {de(tiers['all']['g'],0)} g    ≈ {de(tiers['all']['normal'],1)} h / {de(tiers['all']['schnell'],1)} h
  Reicht die Zeit nicht: zuerst FM streichen (größtes Teil, 20 g), dann R und D. Der Kern K + N + S + C ist das Wichtige.
  Platzbedarf aller Teile etwa {need[0]:.0f} × {need[1]:.0f} mm (Anordnungsvorschlag: vorschau/steckmodul_night1/anordnung.png).

Zuordnung der Ergebnisse zu den Konstanten in plug/parts.py
  Serie N → KEY_CLR      Serie S → KASS_CLR      Serie R → SNUG (Rippen RIB danach getrennt)
  Serie FM → CLR         Serie K → CEIL und FUNNEL_T (nur wenn 1,8 nicht hält)
  Das Gehäuse der Dupont-Buchse streut um ±0,3 mm. Vor dem Anprobieren die Breite der benutzten Buchsen mit der Schieblehre
  messen (Soll 10,16 mm) und beim Ergebnis dazuschreiben; Bauteilmaße von mehreren Zehnteln lassen sich messen, Spalte nicht.

Slicer-Einstellungen: dieselben wie für die späteren echten Teile, sonst gelten die Spielwerte nicht
  Düse 0,4 mm, Schichthöhe 0,2 mm, PLA, Wände 3 Linien, Füllung 15 %, Brückenerkennung an, keine Stützen.
  Elefantenfuß-Kompensation genau so, wie sie später gilt. Teile nicht umdrehen, nicht skalieren.
  Schieber und Plättchen ohne Rand, erste Schicht langsam (Schieber sind nur 1 mm dick und können sich verziehen).
  Die Boden-Platten haben über der Nut eine Brücke (siehe unten): Brückenerkennung nicht abschalten.
  Anordnung: die sieben STL einzeln importieren und vom Slicer anordnen lassen (Schicht für Schicht, nicht Objekt für Objekt).
  Der Vorschlag in anordnung.png braucht {need[0]:.0f} × {need[1]:.0f} mm.
  Lösen sich die Boden-Platten (S) vom Bett (kleine Auflagefläche, nur die Ränder um die Nut), einen Brim von 3 mm nur außen ergänzen.

Was gibt es dazu zu prüfen?

  K  Kontakt-Tiefe (das Gate, entscheidet Höhen)
     Aufbau: Winkelleiste mit den Pins nach oben, Plättchen auf den Körper stecken, Buchse (mit gecrimpten Kontakten) von oben
     bis auf das Plättchen drücken. Die Einstecktiefe der Pins in der Buchse ist E = {de(sd.HDR_UP)} − t.
       Plättchen 1,2  →  E = {de(sd.HDR_UP-1.2)} mm     Plättchen 1,8  →  E = {de(sd.HDR_UP-1.8)} mm (Sollwert)     Plättchen 2,4  →  E = {de(sd.HDR_UP-2.4)} mm
     Messen: Durchgang jedes Kontakts mit dem Multimeter beim Wackeln (±0,5 mm, leicht kippen). Möglichst mit dem kürzesten Pin.
     Auswertung: hält 2,4 → Reserve. Hält ab 1,8 → so lassen. Hält nur 1,2 → CEIL und FUNNEL_T auf 0,6 (alle Höhen neu, N hinfällig).
     Hält nirgends → Dupont-Kontakt ungeeignet. Bild: vorschau/steckmodul_night1/kontakt_stapel.png

  N  Schieber in der Nut, S  Kassette im Schacht (mit der Kassette C als Lehre; beides zusammen an einer Platte prüfen)
     Eine Platte (egal welche, die Nut ist bei allen gleich) mit der Gravur nach oben auf den Tisch legen. Den Schieber mit der Gravur
     nach oben von der Seite einschieben, an der die Nut offen ist, bis er am geschlossenen Nutende anschlägt. Die Griffkerbe liegt am
     hinteren Ende und dient zum Herausziehen.
       N: Welcher Schieber gleitet mit leichtem Fingerdruck? Fällt er beim Hochhalten heraus? Ist er flach (Lineal)? Geht ein
          Dupont-Stift durch alle vier Trichterlöcher?
     Dann die Kassette von oben in den Schacht setzen, die Buchsenöffnung nach unten: sie liegt auf dem Schieber wie im Gebäude.
       S: Welche Platte lässt die Kassette ohne Kraft einsinken, und bei welcher wackelt sie spürbar? Das Spiel gilt in x und y.
     Zusammenhang: 0,20 (Platte) ist der Probestück-Wert, der als "wackelt" bekannt ist. Die engere Platte zeigt, wie weit es geht.
     Bild: vorschau/steckmodul_night1/schnitt_platte_schieber_kassette.png

  C  Kassette: Buchse mit der Steckseite zur offenen Unterseite eindrücken, Adern in den Aderschlitz, Streifen in die Ablage
     ({de(I.SEAT_W,1)} × {de(I.SEAT_L,1)} mm), DETECT-Brücke in die Querrinne. Prüfen: Buchse fest ohne Werkzeug? Rastfenster-Seite frei?
     Beide Streifenbreiten (10 und 12 mm) passen? Wird mit mehreren Buchsen probiert (Gehäusebreite ±0,3 mm!), ist das Ergebnis belastbarer.

  R  Buchsenhülsen: dieselbe Buchse in jede Hülse drücken. ENG = engste, in die sie ohne Gewalt geht; WEIT = weiteste ohne Wackeln.
     Mit zwei bis drei Buchsen probieren, weil das Gehäuse von Stück zu Stück um bis zu ±0,3 mm streut.

  FM Mulden-Ringe (optional): das bereits gedruckte Gebäude-Probestück (1_probestueck.stl, falls noch vorhanden) als Fuß mit dem Fuß nach
     unten in jeden Ring stellen (Kodierecke beachten, abgeschrägte Ecke).
     Welcher Ring lässt den Fuß ohne Klemmen bis zum Boden sinken, bei welchem wackelt er? Es gibt hier noch keine Federzunge
     (Rast und Haltekraft folgen in einer späteren Serie).

  D  Passprobe v6 (optional): Stufenhöhe 2,0 / 1,8 / 1,6 (Anleitung: plug/fit_test/page.html).

Bekannte Risiken beim Druck (bitte vor dem Start im Slicer-Vorschaubild ansehen)
  * Boden-Platten (S): über der Nut liegt eine waagerechte Decke in 1,0 mm Höhe, im Probestück (und damit hier) 209 mm² groß
    (bis 34 mm Spannweite quer). Das ist eine Brücke und kann durchhängen. Das wird so mitgetestet; hängt sie spürbar durch, ist
    das ein Ergebnis für das Gebäude.
  * Der Schacht ist 0,05 mm Spiel vermutlich zu eng. Er ist als Grenzwert gedacht; klemmt er, ist das die untere Grenze der Serie.
  * Die Gravur ist 0,4 bis 0,8 mm tief und fett, bei den 1 mm dicken Schiebern nur 0,4 mm. Löcher: Fase 0,3 mm auf beiden Seiten.
  * Wenn K scheitert (nur bei 1,2 hält): Schieberdicke (FUNNEL_T) ändert sich, die Schieber N werden dann neu gebraucht.
    Das Risiko dafür sind etwa {de(g['N_sliders'],0)} g.
"""
    with open(os.path.join(OUT, "README.txt"), "w", encoding="utf-8") as f:
        f.write(txt)


if __name__ == "__main__":
    main()
