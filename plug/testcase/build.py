#!/usr/bin/env python3
"""Kompletter Testfall: 2 × Kassette v4, Mini-Gebäude A und B, Mini-Grundplatte, Mini-Deckel nach stl/steckmodul_testcase/.

Die Wahl folgt den Empfehlungen der Planungsseite (plug/testcase/plan.html): L-Fuß, Schacht A (0,06 durchgehend) und B (Passzone 8 mm),
Podest über die ganze Oberseite, Kabelraum offen mit Deckelfenster, Mini-Deckel mit 4 Schrauben, keine Federzunge, eine Platte mit Muldenboden 0,4.
Sollwerte: plug/testcase/params.py. Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m plug.testcase.build       # STL, README.txt, ZIP, Prüfbericht, Vorschau nach vorschau/steckmodul_testcase/
"""
import os
import zipfile

import manifold3d as m3d
import shapely
from shapely.geometry import Point
from shapely.geometry import box as sbox
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

from plug import dupont as sd
from plug import institute as I
from plug import series as SR
from plug import series2 as N2
from plug.fit_test.generator import overhangs
from plug.geom import box, cbox, cyl, diff, ext, prism_x, prism_y, to_bed, to_tm, union, vol_int, xcut, ycut
from plug.testcase import kassette as KA
from plug.testcase import params as P
from plug.testcase.build_plan import KABEL_HX, KABEL_Y1, LID_WIN, LOETRAUM_Y0

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(HERE, "stl", "steckmodul_testcase")
PREV = os.path.join(HERE, "vorschau", "steckmodul_testcase")
de = SR.de
LIP_X = 1.2            # Anschlagrand: Überstand über die Kassette in x
SCREW_X = 16.2         # Schrauben in der Platte
HOLE_CH = 0.15         # Fase an den Stiftlöchern im Muldenboden (bei 0,4 mm Dicke höchstens die halbe Dicke)
SLOPE = 0.75           # Platte B: Böschung der Schächte unter dem Muldenboden, Versatz je mm Höhe (36,9° zur Senkrechten, 0,15 Überhang je Schicht)
CONE_MAX = 1.6         # Platte B: größter Radius der Trichter um die Pins
SLOT_END = -7.0        # Platte B: Ende des Lötendenschlitzes (0,7 mm hinter den Spitzen), darunter offen
LID_WIN_Y = (-10.0, -3.9)   # Deckelfenster über den Lötenden (y)


def foot_poly():
    d = P.dims()
    return orient(shapely.Polygon([(x, y + d["yc"]) for x, y in P.footprint()]), 1.0)


def plate_y():
    d = P.dims()
    return d["yc"] - P.BOX_L / 2 - P.PLATE_MARGIN, d["yc"] + P.BOX_L / 2 + P.PLATE_MARGIN


# --------------------------------------------------------------------------
# Mini-Gebäude (Fuß unten, Schacht öffnet nach unten, oben Fenster mit Anschlagrand)
# --------------------------------------------------------------------------
def building(variant, c=None):
    d, k = P.dims(), P.kass_dims()
    F = d["F"]
    c = P.KASS_CLR_T if c is None else c
    cs = I.hcs(foot_poly())
    body = union([I.foot_solid(cs, F), ext(I.rounded(cs), 0.0, d["box_top"])])
    sy0, sy1 = d["y_kass0"] - c, d["y_kass1"] + c
    hx = k["cw"] / 2 + c
    zk = -F + d["kass_h"]
    cuts = []
    if variant == "A":
        cuts.append(box(-hx, hx, sy0, sy1, -F - 0.01, zk))
    else:
        r = P.KASS_RELIEF - c
        cuts.append(box(-hx, hx, sy0, sy1, -F - 0.01, -F + P.KASS_FIT_LEN))
        cuts.append(box(-hx - r, hx + r, sy0 - r, sy1 + r, -F + P.KASS_FIT_LEN - 0.01, zk))
    cuts.append(N2.chamfer_hole(2 * hx, sy1 - sy0, -F, P.ENTRY_CH_T, True, cx=0.0, cy=(sy0 + sy1) / 2))     # Einführfase am Bett
    cuts.append(box(-hx + LIP_X, hx - LIP_X, sy0 + N2.E_LIP, sy1 - N2.E_LIP, zk - 0.01, d["box_top"] + 0.01))   # Fenster
    m = diff(body, *cuts)
    fp = foot_poly()
    xl = fp.bounds[0] + 10.0
    lab = N2.emboss_side(N2.big_label("GEB " + variant, 1 if variant == "A" else 2, 3.6), xl, 6.0, fp.bounds[1])
    return union([m, lab])


# --------------------------------------------------------------------------
# Mini-Grundplatte und Mini-Deckel
# --------------------------------------------------------------------------
def layered(fn, z0, z1):
    """Hohlraum aus dünnen Scheiben (eine je Schicht): fn(z_mitte) liefert die Fläche in shapely. Böschungen entstehen als Treppe aus 0,2-mm-Schichten."""
    parts = []
    n = int(round((z1 - z0) / sd.LAYER))
    for i in range(n):
        za = z0 + i * sd.LAYER
        g = fn(za + sd.LAYER / 2)
        if g is None or g.is_empty:
            continue
        parts.append(ext(I.hcs(g), za - (0.01 if i == 0 else 0.0), za + sd.LAYER + 0.01))
    return union(parts)


def dock_cuts_b(d):
    """Winkelleisten-Dock ohne Stützen: alle Decken über der Leiste sind 45°-nahe Böschungen oder kurze Brücken (höchstens 3,7 mm), Löcher konisch."""
    F, zhb, zbb, zlt, step = d["F"], d["z_hb"], d["z_bb"], d["z_lt"], d["step"]
    yb, hd = d["yb"], sd.HDR_T / 2 + sd.SNUG_HDR
    hw = sd.HDR_W / 2 + sd.SNUG_HDR
    px = abs(sd.pin_x()[0]) + sd.PIN_SQ / 2 + 0.8
    y_slot = yb - hd - P.BODY_EXT_T
    pocket = sbox(-hw, y_slot, hw, yb + hd)
    slot_top = sbox(-px, SLOT_END, px, y_slot + 0.02)
    z_slot = zbb + 8 * sd.LAYER                                   # Schlitzdecke auf dem Schichtraster, knapp über der Stufe
    cones = lambda z: unary_union([Point(x, 0.0).buffer(min(0.7 + SLOPE * (zhb - z), CONE_MAX), 24) for x in sd.pin_x()])
    slot = lambda z: slot_top.buffer(SLOPE * (z_slot - z), join_style=2)
    top_bb = unary_union([pocket, cones(zbb), slot(zbb)])         # Öffnung des Trichters unter der Leiste auf Höhe der Körperunterkante
    cuts = [layered(lambda z: top_bb.buffer(SLOPE * (zbb - z), join_style=2), zlt, zbb),           # Kabelraum als Trichter, unten offen
            box(-hw, hw, y_slot, yb + hd, zbb - 0.01, zhb),                                        # Körper
            layered(cones, zbb, zhb),                                                              # Trichter um die senkrechten Pins
            layered(slot, zbb, z_slot)]                                                            # Lötenden-Schlitz, seitlich geböscht
    for x in sd.pin_x():
        cuts.append(box(x - 0.9, x + 0.9, -1.6, 0.6, d["z_bm"] - 0.45, d["z_bm"] + 0.45))         # Durchlass für den Knick des Pins
        cuts += N2.hole_ch(x, 0.0, zhb, -F, sd.HOLE, 0.0, HOLE_CH)
    return cuts


def plate(ribs=True, variant="A"):
    """variant A: Kasten-Hohlräume (mit Support drucken). variant B: Trichter-Hohlräume, ohne Support."""
    d = P.dims()
    F, zhb, zbb, zlt = d["F"], d["z_hb"], d["z_bb"], d["z_lt"]
    ph0, ph1 = plate_y()
    pw, _ = P.plate_size()
    blk = box(-pw / 2, pw / 2, ph0, ph1, zlt, 0.0)
    cs = I.hcs(foot_poly())
    old = sd.CLR
    sd.CLR = P.MULDE_CLR_T
    try:
        cuts = list(I.pocket_cuts(cs, F))
    finally:
        sd.CLR = old
    yb, hd = d["yb"], sd.HDR_T / 2 + sd.SNUG_HDR
    hw = sd.HDR_W / 2 + sd.SNUG_HDR
    px = abs(sd.pin_x()[0]) + sd.PIN_SQ / 2 + 0.8
    y_slot = yb - hd - P.BODY_EXT_T
    if variant == "A":
        cuts += [box(-hw, hw, y_slot, yb + hd, zbb - 0.01, zhb),                                  # Körper, +1,5 zum Lötende
                 box(-px, px, yb, sd.PIN_SQ / 2 + 0.8, zbb - 0.01, zhb),                          # Knick und Pins
                 box(-px, px, LOETRAUM_Y0, y_slot + 0.01, zbb - 0.01, d["step"]),                 # Lötenden, nach hinten offen
                 box(-KABEL_HX, KABEL_HX, LOETRAUM_Y0, KABEL_Y1, zlt - 0.01, zbb)]               # Kabelraum
        for x in sd.pin_x():
            cuts += N2.hole_ch(x, 0.0, zhb, -F, sd.HOLE, HOLE_CH, HOLE_CH)
    else:
        cuts += dock_cuts_b(d)
    for sx in (-1, 1):
        for y in (ph0 + 3.0, ph1 - 3.0):
            cuts.append(cyl(sd.SCREW_PILOT / 2, zlt - 0.01, zlt + 9.0, cx=sx * SCREW_X, cy=y))
    p = diff(blk, *cuts)
    rib = [cbox(2 * sd.RIB + 0.2, 0.6, zbb, zhb, cx=sx * (sd.HDR_W / 2 + sd.SNUG_HDR - sd.RIB + 0.1), cy=yb) for sx in (-1, 1)] if ribs else []
    lab = N2.emboss_side(N2.big_label("PLATTE " + variant, 0, 4.4), 0.0, zlt + 6.0, ph0)
    return union([p] + rib + [lab])


def lid():
    """Deckel: Platte mit Fenster, zwei kräftige Stempel unter dem Körper der Winkelleiste, mit Böschungsstreben (45°) an Seiten und Rückseite
    und einem Quersteg zwischen den Stempeln. Die Stempel stehen innerhalb x ≤ 5,3, damit sie auch in den Trichter der Platte B passen."""
    d = P.dims()
    zlt, zbb, yb = d["z_lt"], d["z_bb"], d["yb"]
    ph0, ph1 = plate_y()
    pw, _ = P.plate_size()
    zl = zlt - P.LID_T_T
    l = box(-pw / 2, pw / 2, ph0, ph1, zl, zlt)
    parts = [l]
    y0, y1 = yb - 0.88, yb + 0.88                                   # unter dem Körper (2,0 dick), 1,76 breit
    for sx in (-1, 1):
        xa, xb = 2.4, 5.3
        parts.append(box(*sorted((sx * xa, sx * xb)), y0, y1, zlt - 0.01, zbb))                              # Stempel 2,9 × 1,76
        t = 2.2
        parts.append(prism_y([(sx * xa, zlt - 0.01), (sx * xa, zlt + t), (sx * (xa - t), zlt - 0.01)], y0, y1))          # Strebe nach innen
        t = 1.6
        parts.append(prism_y([(sx * xb, zlt - 0.01), (sx * xb, zlt + t), (sx * (xb + t), zlt - 0.01)], y0, y1))          # Strebe nach außen
        t = 2.4
        parts.append(prism_x([(y1, zlt - 0.01), (y1, zlt + t), (y1 + t, zlt - 0.01)], *sorted((sx * xa, sx * xb))))        # Strebe zur Pin-Seite
    parts.append(box(-2.4, 2.4, yb - 0.5, yb + 0.5, zlt - 0.01, zlt + 1.6))                                  # Quersteg zwischen den Stempeln
    cuts = [box(-(KABEL_HX - 0.5), KABEL_HX - 0.5, LID_WIN_Y[0], LID_WIN_Y[1], zl - 0.01, zlt + 0.01)]
    for sx in (-1, 1):
        for y in (ph0 + 3.0, ph1 - 3.0):
            cuts.append(cyl(sd.SCREW_CLR / 2, zl - 0.01, zlt + 0.01, cx=sx * SCREW_X, cy=y))
    lab = N2.emboss_side(N2.big_label("DECKEL", 0, 1.2), 0.0, zlt - 1.0, ph0, h=0.4)
    return union([diff(union(parts), *cuts), lab])


def header():
    """Winkelleiste (Kaufteil) in der Mini-Grundplatte."""
    d = P.dims()
    body = cbox(sd.HDR_W, sd.HDR_T, d["z_bb"], d["z_hb"], cy=d["yb"])
    pins = []
    for x in sd.pin_x():
        pins.append(box(x - sd.PIN_SQ / 2, x + sd.PIN_SQ / 2, d["yb"] - sd.HDR_T / 2 - sd.RA_TAIL, sd.PIN_SQ / 2,
                        d["z_bm"] - sd.PIN_SQ / 2, d["z_bm"] + sd.PIN_SQ / 2))
        pins.append(cbox(sd.PIN_SQ, sd.PIN_SQ, d["z_bm"] - sd.PIN_SQ / 2, d["z_tip"], cx=x, cy=0.0))
    return union([body] + pins)


def kass_world(tol=None, notches=0, flush=False):
    """Kassette im Gebäude (Unterkante bündig mit der Fußunterkante)."""
    d = P.dims()
    return KA.kassette4(tol, notches=notches).translate([0.0, d["y_kass0"], -d["F"]])


def buchse_world(tol=None, flush=False):
    """Buchse in der Kassette. Standard: oben an den Schultern (ungünstigster Fall). flush=True: bündig mit der Kassettenunterkante (so wird sie eingesetzt)."""
    d = P.dims()
    k = P.kass_dims(tol)
    h = KA.housing(k)
    if flush:
        h = h.translate([0.0, 0.0, -(k["zp"] - sd.HSG_H)])
    return h.translate([0.0, d["y_kass0"], -d["F"]])


# --------------------------------------------------------------------------
def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(PREV, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith(".stl"):
            os.remove(os.path.join(OUT, f))
    d, k = P.dims(), P.kass_dims()
    print("Testfall: F %.1f, E %.2f, Kassette v4 %.2f × %.2f × %.2f, Mini-Gebäude %.1f × %.1f × %.2f, Platte %.1f × %.1f × %.1f" % (
        d["F"], d["E"], k["cw"], k["L"], k["top"], P.BOX_W, P.BOX_L, d["box_h"], *P.plate_size(), d["plate_t"]))
    kc1, kc2 = KA.kassette4(P.HSG_TOL_SAFE, notches=1), KA.kassette4(P.HSG_TOL_TIGHT, notches=2)
    bA, bB, pl, plB, ld = building("A"), building("B"), plate(variant="A"), plate(variant="B"), lid()
    parts = {"T_cassette_v4_x2": N2.row([kc1, kc2], 6.0), "T_building_A": to_bed(bA), "T_building_B": to_bed(bB),
             "T_plate_A_support": to_bed(pl), "T_plate_B_nosupport": to_bed(plB), "T_lid": to_bed(ld)}
    print("\nTeile (Druckausrichtung, Bett z = 0):")
    info = {}
    for name, man in parts.items():
        tm = to_tm(man)
        tm.export(os.path.join(OUT, name + ".stl"))
        g, nl = SR.estimate(man)
        ov = overhangs(man, name)
        info[name] = dict(tm=tm, g=g, layers=nl, ov=ov)
        print("  %-18s %6.1f × %6.1f × %5.1f mm  %5.1f cm³  ≈ %4.1f g  dicht=%s" % (name + ".stl", *tm.extents, tm.volume / 1000.0, g, tm.is_watertight))
        print("      waagerechte Decken: %s   Überhang flacher als 45°: %.0f mm²" % (
            "; ".join("z=%.1f: %.0f mm² (%.1f × %.1f)" % f for f in sorted(ov["flat"], key=lambda t: -t[1])[:4]) or "keine", ov["steep_area"]))

    print("\nPrüfung der Passungen (Überschneidungsvolumen, mm³; muss 0 sein):")
    bad = 0

    def chk(txt, v, limit=0.05):
        nonlocal bad
        ok = v <= limit
        bad += (not ok)
        print("  %-66s %8.3f  %s" % (txt, v, "ok" if ok else "KOLLISION"))
    kw, bw, hd_ = kass_world(P.HSG_TOL_SAFE, 1), buchse_world(P.HSG_TOL_SAFE, flush=True), header()
    kw2, bw2 = kass_world(P.HSG_TOL_TIGHT, 2), buchse_world(P.HSG_TOL_TIGHT, flush=True)
    for nm, kk in (("1 (Luft 0,45)", kw), ("2 (Luft 0,15)", kw2)):
        chk("Kassette %s in Mini-Gebäude A" % nm, vol_int(kk, bA))
        chk("Kassette %s in Mini-Gebäude B" % nm, vol_int(kk, bB))
    chk("Buchse (Nennmaß) bündig in Kassette 1", vol_int(bw, kw))
    chk("Buchse (Nennmaß) bündig in Kassette 2", vol_int(bw2, kw2))
    chk("Buchse (Nennmaß) an den Schultern in Kassette 2", vol_int(buchse_world(P.HSG_TOL_TIGHT), kw2))
    chk("Kontrolle: Buchse 0,1 höher als 14,15 stößt in Kassette 2 an", 0.0 if vol_int(buchse_world(P.HSG_TOL_TIGHT).translate([0, 0, 0.2]), kw2) > 0.05 else 1.0)
    for v, pp in (("A", pl), ("B", plB)):
        chk("Mini-Gebäude A in der Mulde der Platte %s" % v, vol_int(bA, pp))
        chk("Mini-Gebäude B in der Mulde der Platte %s" % v, vol_int(bB, pp))
        chk("Winkelleiste in der Platte %s (ohne die Crush-Rippen)" % v, vol_int(hd_, plate(ribs=False, variant=v)))
        print("      Crush-Rippen am Körper drücken %.2f mm³ ein (gewollt, 0,12 mm Übermaß)" % vol_int(hd_, pp))
    chk("Winkelleiste und Buchse (Pins in den Kammern)", vol_int(hd_, bw))
    chk("Winkelleiste und Kassette", vol_int(hd_, kw))
    chk("Winkelleiste und Kassette 2", vol_int(hd_, kw2))
    chk("Mini-Deckel an der Platte A", vol_int(ld, pl))
    chk("Mini-Deckel an der Platte B", vol_int(ld, plB))
    chk("Mini-Deckel und Winkelleiste (Stempel stehen am Körper an)", vol_int(ld, hd_))
    chk("Kontrolle: Schacht mit Spiel −0,05 stößt an der Kassette an", 0.0 if vol_int(kw, building("A", c=-0.05)) > 0.05 else 1.0)
    print("  Buchse bündig: unten bei z=%.2f (Fußunterkante %.2f), Pin-Spitze bei z=%.2f, E = %.2f mm" % (
        bw.bounding_box()[2], -d["F"], d["z_tip"], d["z_tip"] - bw.bounding_box()[2]))
    for nm, tol in (("Kassette 1", P.HSG_TOL_SAFE), ("Kassette 2", P.HSG_TOL_TIGHT)):
        print("  %s, Buchse nach oben bis an die Schultern gerutscht: E = %.2f mm" % (nm, d["E"] - tol))
    print("  -> %s" % ("keine Kollisionen" if not bad else "%d Kollisionen!" % bad))

    tot = sum(i["g"] for i in info.values())
    from plug.roadmap import build as rb
    for prof, pr in rb.PROFILE.items():
        mins = sum(i["g"] / pr["rate"] * 60.0 + i["layers"] * pr["layer"] / 60.0 for i in info.values()) + pr["start"]
        print("Material ≈ %.0f g, Zeit %s ≈ %.1f h" % (tot, prof, mins / 60.0))
    print("Bei deinem Drucker (Nacht 1: 47 g in 2,5 h) ≈ %.1f h" % (tot / 47.0 * 2.5))
    previews(parts, bA, plB, ld, kw2, bw2, hd_)
    write_readme(info, tot)
    zpath = os.path.join(OUT, "testcase_series.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(os.listdir(OUT)):
            if f.endswith(".stl") or f == "README.txt":
                z.write(os.path.join(OUT, f), f)
    print("%s: %.0f kB" % (os.path.relpath(zpath, HERE), os.path.getsize(zpath) / 1024))
    upd = os.path.join(OUT, "testcase_update_plate_lid.zip")
    with zipfile.ZipFile(upd, "w", zipfile.ZIP_DEFLATED) as z:
        for f in ("T_plate_B_nosupport.stl", "T_lid.stl", "README_update.txt"):
            z.write(os.path.join(OUT, f), f)
    print("%s: %.0f kB" % (os.path.relpath(upd, HERE), os.path.getsize(upd) / 1024))
    return bad


def previews(parts, bA, pl, ld, kw, bw, hd_):
    import preview
    from PIL import Image
    col = dict(T_cassette_v4_x2="#e3862a", T_building_A="#e9e1c9", T_building_B="#e0d5b0", T_plate_A_support="#c9d6e2", T_plate_B_nosupport="#b6cde0", T_lid="#8ccf9a")
    tms = {n: to_tm(m) for n, m in parts.items()}
    pos, need = SR.pack([(n, float(t.extents[0]), float(t.extents[1])) for n, t in tms.items()], bed=(130.0, 400.0))
    items = []
    for n, tm in tms.items():
        x, y = pos[n]
        tm.apply_translation([x - tm.bounds[0][0], y - tm.bounds[0][1], 0])
        items.append((tm, col[n]))
    preview.render(items, size=(1400, 900), azim=-60, elev=50).save(os.path.join(PREV, "teile.png"))
    d = P.dims()
    cutx = lambda m: to_tm(xcut(m, 0.0))
    scenes = []
    for lift in (0.0, 14.0):
        its = [(cutx(pl), "#c9d6e2"), (cutx(ld), "#8ccf9a"), (cutx(hd_), "#2d3236"),
               (cutx(bA.translate([0, 0, lift])), "#e9e1c9"), (cutx(kw.translate([0, 0, lift])), "#e3862a"), (cutx(bw.translate([0, 0, lift])), "#f4f1e8")]
        scenes.append(preview.render(its, size=(900, 900), azim=0, elev=0))
    sheet = Image.new("RGB", (1800, 900), "white")
    sheet.paste(scenes[0], (0, 0))
    sheet.paste(scenes[1], (900, 0))
    sheet.save(os.path.join(PREV, "zusammenbau_schnitt.png"))
    its = [(to_tm(pl), "#c9d6e2"), (to_tm(hd_), "#2d3236"), (to_tm(bA.translate([0, 0, 22.0])), "#e9e1c9"), (to_tm(kw.translate([0, 0, 22.0])), "#e3862a")]
    preview.render(its, size=(1100, 900), azim=-35, elev=40).save(os.path.join(PREV, "zusammenbau_schraeg.png"))
    # Platte B: Schnitte durch die Trichter (x = 0 längs, y = 0 quer durch die Pins) und Blick von unten
    cuty = lambda m: to_tm(ycut(m, 0.0))
    a = preview.render([(cutx(pl), "#b6cde0"), (cutx(hd_), "#2d3236")], size=(800, 640), azim=0, elev=0)
    b = preview.render([(cuty(pl), "#b6cde0"), (cuty(hd_), "#2d3236")], size=(800, 640), azim=-90, elev=0)
    c = preview.render([(to_tm(pl), "#b6cde0"), (to_tm(hd_), "#2d3236")], size=(800, 640), azim=-30, elev=-55)
    e = preview.render([(to_tm(ld), "#8ccf9a")], size=(800, 640), azim=-30, elev=45)
    sheet = Image.new("RGB", (1600, 1280), "white")
    for i, im in enumerate((a, b, c, e)):
        sheet.paste(im, ((i % 2) * 800, (i // 2) * 640))
    sheet.save(os.path.join(PREV, "platte_b_deckel.png"))
    print("Vorschau: %s" % os.path.relpath(PREV, HERE))


def write_readme(info, tot):
    d, k = P.dims(), P.kass_dims()
    g = {n: info[n]["g"] for n in info}
    pw, pl_ = P.plate_size()
    txt = f"""TESTFALL KASSETTE (Planung: plug/testcase/plan.html)
====================================================

Ein kompletter Aufbau aus Mini-Gebäude, Kassette und Mini-Grundplatte mit Winkelleiste. Gedruckt wird alles in einem Lauf.

Dateien (alle in Druckausrichtung)
  T_cassette_v4_x2.stl   2 × Kassette v4 ({de(k['cw'], 1)} × {de(k['L'], 1)} × {de(k['top'], 2)} mm), Tasche unten offen, Podest, R {de(P.FILLET_T, 1)}   ≈ {de(g['T_cassette_v4_x2'], 1)} g
                         Kassette 1 (1 Kerbe an der Seite): Taschenhöhe {de(sd.HSG_H + P.HSG_TOL_SAFE, 2)}, Luft über der Buchse {de(P.HSG_TOL_SAFE)}
                         Kassette 2 (2 Kerben): Taschenhöhe {de(sd.HSG_H + P.HSG_TOL_TIGHT, 2)}, Luft {de(P.HSG_TOL_TIGHT)} (passt nur, wenn die Buchse höchstens {de(sd.HSG_H + P.HSG_TOL_TIGHT, 2)} mm hoch ist)
  T_building_A.stl       Mini-Gebäude, L-Fuß {de(P.BOX_W, 0)} × {de(P.BOX_L, 0)}, {de(d['box_h'], 2)} hoch, Schacht {de(P.KASS_CLR_T)} durchgehend   ≈ {de(g['T_building_A'], 1)} g
  T_building_B.stl       wie A, Schacht nur die ersten {de(P.KASS_FIT_LEN, 0)} mm mit {de(P.KASS_CLR_T)}, dahinter {de(P.KASS_RELIEF)}   ≈ {de(g['T_building_B'], 1)} g
  T_plate_A_support.stl  Mini-Grundplatte {de(pw, 0)} × {de(pl_, 0)} × {de(d['plate_t'], 1)} mm, Mulde {de(d['F'], 1)} tief (Spiel {de(P.MULDE_CLR_T)}), Muldenboden {de(P.CEIL_T, 1)}, Dock A mit Kasten-Hohlräumen.
                         MIT SUPPORT drucken (Hohlräume unter dem Muldenboden und Kabelraum)   ≈ {de(g['T_plate_A_support'], 1)} g
  T_plate_B_nosupport.stl  dieselbe Platte, aber alle Hohlräume unter dem Muldenboden als Trichter (Böschung 37° zur Senkrechten, je Schicht
                         0,15 mm Überhang), Pin-Löcher konisch. OHNE SUPPORT drucken. Längste Brücke 3,7 mm   ≈ {de(g['T_plate_B_nosupport'], 1)} g
  T_lid.stl              Mini-Deckel {de(P.LID_T_T, 1)} mm mit Fenster; zwei kräftige Stempel (2,9 × 1,76 mm, 3,6 hoch) mit Böschungsstreben an
                         drei Seiten und einem Quersteg dazwischen; passt zu beiden Platten   ≈ {de(g['T_lid'], 1)} g
  Zusammen ≈ {de(tot, 0)} g (mit beiden Platten); bei deinem Drucker (Nacht 1: 47 g in 2,5 h) etwa {de(tot / 47.0 * 2.5, 1)} h.

Kaufteile: Winkelleiste (4 Pins), Dupont-Buchse mit gecrimpten Adern, LED-Streifen 10 mm, 4 Schrauben M3.
  Das Fenster im Mini-Gebäude ist {de(2 * (k['cw'] / 2 + P.KASS_CLR_T - LIP_X), 1)} mm breit: der 10-mm-Streifen passt, der 12-mm-Streifen nicht.

Slicer wie Nacht 1 (Bambu, PLA, 0,2 mm, 3 Wände, 15 % Füllung). Gebäude, Kassetten und Deckel ohne Stützen.
  Platte A: mit Support (nur auf dem Bett, „normal“), die Brücken sind Muldenboden ({de(P.CEIL_T, 1)} mm) und Kabelraum ({de(2 * KABEL_HX, 1)} × {de(KABEL_Y1 - LOETRAUM_Y0, 0)} mm).
  Platte B: ohne Support. Unten ist der Kabelraum ein offener Trichter, der Muldenboden hängt nur über der Körpertasche (3,7 mm). Die Treppenstufen
  der Böschung sind gewollt. „Thick bridges“ trotzdem einschalten.
  Mini-Gebäude: Der Schacht öffnet am Druckbett. Die Fase {de(P.ENTRY_CH_T, 1)} am Eingang gleicht den Elefantenfuß aus.
  Die Beschriftung ist erhaben: GEB A / GEB B (1 bzw. 2 Punkte) am Gebäude, PLATTE an der Platte.

Vorab: Höhe der Buchsengehäuse mit der Schieblehre messen (Soll {de(sd.HSG_H, 1)}, kleinster und größter Wert aufschreiben).
  Die Buchse soll unten bündig mit der Kassette sitzen. Jeder Millimeter, den sie zu hoch sitzt, kostet Einstecktiefe:
  E = {de(d['E'])} bündig, {de(d['E'] - P.HSG_TOL_TIGHT)} bei Kassette 2 an den Schultern, {de(d['E'] - P.HSG_TOL_SAFE)} bei Kassette 1 an den Schultern (Aussetzer-Bereich!).

Zusammenbau
  1. Winkelleiste von unten (durch den Kabelraum) in die Platte schieben: Pins nach oben durch den Muldenboden, Körper in die Tasche,
     die Lötenden nach hinten (zur offenen Seite). Deckel mit 4 Schrauben M3 schließen; die Stempel halten den Körper.
     Bei Platte B ist der Schacht unten ein Trichter und lässt die Leiste von selbst in die Tasche gleiten.
  2. Buchse mit gecrimpten Adern bündig einsetzen: Buchse mit der Steckseite auf einen flachen Tisch stellen, Adern durch den Schlitz der
     Kassette fädeln, Kassette von oben darüberstülpen, bis sie auf dem Tisch steht. Nicht von unten bis an die Schultern schieben.
     Adern über die runde Kante, flach zur LED. LED-Streifen auf das Podest legen.
  3. Kassette mit der offenen Seite voran von unten in das Mini-Gebäude drücken, bis sie am Rand anschlägt (Buchse bündig mit der Fußunterkante).
  4. Mini-Gebäude in die Mulde der Platte setzen.

Prüfung
  1  Kassette ins Gebäude: nur mit Daumendruck, schlägt am Rand an, sitzt fest. A und B vergleichen.
  2  Gebäude in die Mulde: mit Fingerdruck, kein spürbares Spiel, nur in einer Lage, sinkt bis zum Boden.
  3  Pins treffen die Buchse ohne Trichter: geht ohne Kraft ein. Danach prüfen, ob die Buchse beim Aufstecken nach oben gerutscht ist
     (Unterkante der Buchse gegen die Fußunterkante halten).
  4  Durchgang aller vier Kontakte mit dem Multimeter, dabei wackeln. Mit Kassette 1 und Kassette 2 vergleichen.
  5  Gebäude zehnmal abziehen und aufstecken: Kassette und Buchse bleiben, Durchgang bleibt.
  6  Adern über das Podest: kein Knick, LED liegt flach.
  7  Lötseite: Kabel anlöten und nach unten durch das Fenster führen.
  8  Optional: Controller anschließen, LED leuchten lassen.
"""
    with open(os.path.join(OUT, "README.txt"), "w", encoding="utf-8") as f:
        f.write(txt)
    upd = f"""UPDATE: Platte ohne Support und stärkerer Deckel
================================================

Aus dem ersten Druck: Der Überhang über der Winkelleiste (Muldenboden 0,4 mm) fiel ein, die Pin-Löcher waren zugeschmolzen, und die Stempel
des Deckels brachen ab. Neu:

  T_plate_B_nosupport.stl  Alle Hohlräume unter dem Muldenboden sind Trichter. Böschung 37° zur Senkrechten (0,75 mm Versatz je mm Höhe,
                           also 0,15 mm Überhang je 0,2-mm-Schicht). Die senkrechten Pins sitzen in Kegeln, die nach unten weiter werden,
                           die Lötenden in einem seitlich abgeschrägten Schlitz, der Kabelraum ist ein offener Trichter mit 2,7 mm Zugabe
                           je Seite am Bett. Brücken: nur noch die Körpertasche (10,9 × 3,7 mm) und die Schlitzdecke (10 × 2 mm).
                           OHNE SUPPORT drucken. Unten sieht man die Stufen der Böschung; das ist gewollt und stört nicht.
                           Der Lötende-Schlitz endet 0,7 mm hinter den Spitzen; darunter ist alles offen, die Kabel gehen nach unten weg.
  T_lid.stl                Stempel 2,9 × 1,76 mm statt 1,35 × 2 mm, 3,6 mm hoch, mit 45°-Streben nach innen (2,2), außen (1,6) und zur Pin-Seite (2,4)
                           und einem Quersteg zwischen den Stempeln. Das Fenster ist 14 × 6 mm, alles liegt innerhalb x ≤ 5,3 und passt zu A und B.

Platte A (T_plate_A_support.stl) bleibt unverändert und wird mit Support gedruckt, falls B nicht gelingt.
Prüfung wie bisher; zusätzlich: Liegt der Muldenboden über der Körpertasche glatt, sind alle vier Pin-Löcher offen, halten die Stempel?
"""
    with open(os.path.join(OUT, "README_update.txt"), "w", encoding="utf-8") as f:
        f.write(upd)


if __name__ == "__main__":
    raise SystemExit(1 if main() else 0)
