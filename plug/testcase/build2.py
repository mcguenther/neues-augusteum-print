#!/usr/bin/env python3
"""Steckprobe 2: Zwei-Lagen-Aufbau im Kleinen nach stl/steckmodul_testcase2/.

Teile (Plan plug/testcase/plan2.html, Empfehlungen A, dazu der Aufbau aus plug/power/concept.html):
  S2_cassette.stl      1 × Kassette (Tasche 14,60, Fase 0,5)
  S2_building.stl      Mini-Gebäude mit L-Fuß, Schacht 0,06 durchgehend, 17,40 tief, Anschlagrand 1,2, Fußfase 0,8
  S2_top_plate.stl     Mini-Oberplatte 12,6 mm: Mulde, Dock (Platte B) mit Kabelnische und Rippen, vier Faden-V (links 53°, rechts 40°), Zapfenlöcher
  S2_under_box.stl     Mini-Unterkasten 14,4 mm: hohl, Steg-Anschlag unter der Winkelleiste, Zapfen, Eckaussparungen, Kabelfenster

Maße kommen aus plug/testcase/params.py (Steckprobe-Werte) und plug/power/params.py (Aufbau); die Geometrie der Docks, V-Kanäle und
Fasen ist die des Konzepts (plug/power/build_concept.py). Seit der Auswertung von r4 gilt die halbe Nische (`PP.NICHE`, 12 × 9,5 mm, eine Öffnung): ein neuer Lauf baut sie; der gedruckte Stand
r4 (24 × 19 mm, drei Fenster) liegt eingefroren in `plug/logbook/rounds/r4_steckprobe2/steckprobe2.zip`.
Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m plug.testcase.build2       # STL, README.txt, ZIP, Prüfbericht, Vorschau nach vorschau/steckmodul_testcase2/
"""
import os
import sys
import zipfile

import manifold3d as m3d
import shapely
from shapely.geometry import Point
from shapely.geometry import box as sbox
from shapely.ops import unary_union

from plug import dupont as sd
from plug import institute as I
from plug import series as SR
from plug import series2 as N2
from plug.fit_test.generator import overhangs
from plug.geom import box, cbox, cyl, ext, to_bed, to_tm, union, vol_int, xcut
from plug.power import build_concept as BC
from plug.power import params as PP
from plug.testcase import build as TB
from plug.testcase import kassette as KA
from plug.testcase import params as P

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(HERE, "stl", "steckmodul_testcase2")
PREV = os.path.join(HERE, "vorschau", "steckmodul_testcase2")
de = SR.de
L = sd.LAYER
CH = P.EF_CH_T                      # Bettkanten 0,5
D = P.dims()
H = BC.H0                           # Höhen des Aufbaus (Oberplatte 12,6, Unterkasten 14,4)
DK = BC.DK                          # Maße des Docks (Nische, Schlitz, Körpertasche)
ZF = H["uk_bot"] + PP.UK_FLOOR      # Oberkante Boden des Unterkastens
DECK = H["deck"]                    # Unterseite der Oberplatte = Oberkante Unterkasten
SLOPES = (P.V_SLOPE_A, P.V_SLOPE_B)  # links 53°, rechts 40°

# Platte: Rand 8 mm um den Fuß (hinten und seitlich), vorn so weit, dass die Nische samt Wand hineinpasst
PX = P.BOX_W / 2 + P.S2_MARGIN
PY0 = DK["niche_end"] - PP.ZONE_PAD - PP.UK_WALL
PY1 = D["yc"] + P.BOX_L / 2 + P.S2_MARGIN
OUTLINE = sbox(-PX, PY0, PX, PY1).buffer(-3).buffer(3)
INNER = OUTLINE.buffer(-PP.UK_WALL, join_style=2)
LIP_X = TB.LIP_X
gx = BC.G.extrude                  # Fläche (shapely) → Körper


def foot_poly():
    return TB.foot_poly()


# --------------------------------------------------------------------------
# Teile
# --------------------------------------------------------------------------
def cassette(notches):
    return KA.kassette4(P.HSG_TOL_SAFE, notches=notches)


def building():
    """Mini-Gebäude: Fuß unten (Fußfase 0,8), Schacht 0,06 durchgehend und SHAFT_EXTRA tiefer als die Kassette, Fase 0,5 am Eingang, Anschlagrand 1,2."""
    k, F = P.kass_dims(), D["F"]
    cs = I.hcs(foot_poly())
    zk = -F + D["kass_h"] + P.SHAFT_EXTRA_T
    top = zk + P.STOP_T
    body = union([I.foot_solid(cs, F), ext(I.rounded(cs), 0.0, top)])
    c = P.KASS_CLR_T
    sy0, sy1 = D["y_kass0"] - c, D["y_kass1"] + c
    hx = k["cw"] / 2 + c
    cuts = [box(-hx, hx, sy0, sy1, -F - 0.01, zk),
            N2.chamfer_hole(2 * hx, sy1 - sy0, -F, P.ENTRY_CH_T, True, cx=0.0, cy=(sy0 + sy1) / 2),
            box(-hx + LIP_X, hx - LIP_X, sy0 + N2.E_LIP, sy1 - N2.E_LIP, zk - 0.01, top + 0.01)]
    m = body - union(cuts)
    lab = N2.emboss_side(N2.big_label("GEB S2", 0, 3.6), foot_poly().bounds[0] + 10.0, 6.0, foot_poly().bounds[1])
    return union([m, lab])


def post_positions():
    """Stützen im Unterkasten (außerhalb der Dockzone und der V-Aussparungen); die ersten zwei tragen die Zapfen."""
    return [(-8.5, 8.0), (8.5, 30.0), (8.5, 8.0), (-8.5, 30.0)]


def vs_placed():
    blocked = unary_union([foot_poly().buffer(P.MULDE_CLR_T + sd.RELIEF), sbox(-DK["niche_w"] / 2, DK["niche_end"], DK["niche_w"] / 2, DK["y_slot"])])
    global_slopes = [SLOPES[0], SLOPES[1], SLOPES[0], SLOPES[1]]      # SW, SO, NW, NO: links 53°, rechts 40°
    assert (BC.V["apex"], BC.V["leg_d"], BC.V["entry_r"], BC.V["wall"]) == (P.V_APEX, P.V_LEG_D, P.V_ENTRY_R, P.V_WALL)   # gleiche Kanalmaße wie im Konzept
    return BC.place_vs(OUTLINE, blocked, global_slopes)


def top_plate(vs):
    cs = I.hcs(foot_poly())
    with BC.patched(sd, CLR=P.MULDE_CLR_T):
        cuts = list(I.pocket_cuts(cs, D["F"]))
    cuts += [BC.v_solid(v, DECK) for v in vs]
    pin = PP.PIN
    pins = post_positions()[:2]
    for x, y in pins:
        circ = Point(x, y).buffer(pin["d"] / 2 + pin["clr"], 24)
        cuts += [gx(circ, DECK - 1, DECK + pin["h"] + 0.3), BC.mouth_ch(circ, DECK, CH)]
    with BC.patched(TB, SLOT_END=P.SLOT_END_T):
        cuts += BC.dock_cuts(H, DK)
    m = BC.slab_ch(OUTLINE, DECK, 0.0, CH) - union(cuts)
    yb, zb, zt = DK["yb"], H["z_bb"], H["z_hb"]
    ribs = [cbox(2 * sd.RIB + 0.2, 0.6, zb, zt, cx=sx * (sd.HDR_W / 2 + sd.SNUG_HDR - sd.RIB + 0.1), cy=yb) for sx in (-1, 1)]      # an den Stirnseiten wie bisher
    ribs += [box(x - 0.5, x + 0.5, DK["y_slot"] - 0.01, yb - sd.HDR_T / 2 + 0.25, zb, zt) for x in (-2.54, 0.0, 2.54)]            # an der hinteren Wand, 0,25 Übermaß, zwischen den Lötenden
    lab = [N2.emboss_side(N2.big_label("S2 OBEN", 0, 3.4), 0.0, DECK + 5.0, PY0),
           N2.emboss_side(N2.big_label("53", 0, 3.4), -13.0, DECK + 5.0, PY0),
           N2.emboss_side(N2.big_label("40", 0, 3.4), 13.0, DECK + 5.0, PY0)]
    return union([m] + ribs + lab)


def under_box(vs):
    pin = PP.PIN
    shell = BC.slab_ch(OUTLINE, H["uk_bot"], DECK, CH) - gx(INNER, ZF, DECK + 1)
    posts = [gx(sbox(x - PP.POST[0] / 2, y - PP.POST[0] / 2, x + PP.POST[0] / 2, y + PP.POST[0] / 2), ZF - 0.01, DECK) for x, y in post_positions()]
    zapfen = [BC.pin_solid_at(Point(x, y), DECK, pin, PP.CH_PIN) for x, y in post_positions()[:2]]
    anschlag = BC.dock_anschlag(H, DK, ZF)
    notches = [v["notch"] for v in vs]
    holes = [gx(n, H["uk_bot"] - 1, DECK + 2) for n in notches] + [BC.mouth_ch(n, H["uk_bot"], CH) for n in notches]
    holes.append(gx(sbox(-8.0, PY0 - 1, 8.0, PY0 + PP.UK_WALL + 0.5), ZF, DECK + 1))                      # Kabelfenster in der Vorderwand, oben offen
    lab = N2.emboss_side(N2.big_label("UK S2", 0, 3.0), -13.0, H["uk_bot"] + 6.0, PY0)
    return union([shell] + posts + zapfen + [anschlag, lab]) - union(holes)


# --------------------------------------------------------------------------
# Kaufteile für die Prüfung
# --------------------------------------------------------------------------
def kass_world(notches=1):
    return KA.kassette4(P.HSG_TOL_SAFE, notches=notches).translate([0.0, D["y_kass0"], -D["F"]])


def buchse_world(flush=True):
    k = P.kass_dims()
    h = KA.housing(k)
    if flush:
        h = h.translate([0.0, 0.0, -(k["zp"] - sd.HSG_H)])
    return h.translate([0.0, D["y_kass0"], -D["F"]])


# --------------------------------------------------------------------------
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
    k = P.kass_dims()
    vs = vs_placed()
    bld, tp, uk = building(), top_plate(vs), under_box(vs)
    kc = cassette(1)
    rep("Steckprobe 2: Kassette %.2f × %.2f × %.2f (Tasche %.2f), Gebäude %.0f × %.0f × %.2f (Schacht %.2f), Oberplatte %.1f × %.1f × %.1f, Unterkasten %.1f hoch (gesamt %.1f)" % (
        k["cw"], k["L"], k["top"], k["zp"], P.BOX_W, P.BOX_L, D["kass_h"] + P.SHAFT_EXTRA_T + P.STOP_T, D["kass_h"] + P.SHAFT_EXTRA_T, 2 * PX, PY1 - PY0, -DECK, H["uk_t"], H["total"]))
    rep("V-Kanäle: %s" % ["(%.1f, %.1f) %s %.0f°" % (v["c"][0], v["c"][1], v["axis"], BC.math.degrees(BC.math.atan2(1.0, v["slope"]))) for v in vs])
    parts = {"S2_cassette": to_bed(kc), "S2_building": to_bed(bld), "S2_top_plate": to_bed(tp), "S2_under_box": to_bed(uk)}
    rep("\nTeile (Druckausrichtung, Bett z = 0):")
    info = {}
    for name, man in parts.items():
        tm = to_tm(man)
        tm.export(os.path.join(OUT, name + ".stl"))
        g, nl = SR.estimate(man)
        ov = overhangs(man, name)
        info[name] = dict(tm=tm, g=g, layers=nl, ov=ov)
        rep("  %-16s %6.1f × %6.1f × %5.1f mm  %5.1f cm³  ≈ %4.1f g  dicht=%s" % (name + ".stl", *tm.extents, tm.volume / 1000.0, g, tm.is_watertight))
        rep("      waagerechte Decken: %s   Überhang flacher als 45° zur Senkrechten: %.0f mm²" % (
            "; ".join("z=%.1f: %.0f mm² (%.1f × %.1f)" % f for f in sorted(ov["flat"], key=lambda t: -t[1])[:4]) or "keine", ov["steep_area"]))

    rep("\nPrüfung der Passungen (Überschneidungsvolumen, mm³; muss 0 sein):")
    bad = 0

    def chk(txt, v, limit=0.05):
        nonlocal bad
        ok = v <= limit
        bad += (not ok)
        rep("  %-70s %8.3f  %s" % (txt, v, "ok" if ok else "KOLLISION"))
    kw, bw, hd = kass_world(1), buchse_world(True), TB.header()
    chk("Kassette im Mini-Gebäude", vol_int(kw, bld))
    chk("Buchse (Nennmaß) bündig in der Kassette", vol_int(bw, kw))
    chk("Buchse (Nennmaß) an den Schultern der Kassette", vol_int(buchse_world(False), kw))
    chk("Mini-Gebäude in der Mulde der Oberplatte", vol_int(bld, tp))
    chk("Winkelleiste in der Oberplatte (ohne die Crush-Rippen)", vol_int(hd, top_plate_norib(vs)))
    print("      Crush-Rippen am Körper drücken %.2f mm³ ein (gewollt, Stirnseiten 0,12 und hinten 0,25 Übermaß)" % vol_int(hd, tp))
    chk("Winkelleiste und Buchse (Pins in den Kammern)", vol_int(hd, bw))
    chk("Winkelleiste und Kassette", vol_int(hd, kw))
    chk("Winkelleiste und Unterkasten (Steg bleibt unter dem Körper)", vol_int(hd, uk))
    chk("Oberplatte auf dem Unterkasten (nur Auflage)", vol_int(tp, uk))
    chk("Kassette und Unterkasten", vol_int(kw, uk))
    zones = box(-DK["niche_w"] / 2 - PP.ZONE_PAD, DK["niche_end"] - PP.ZONE_PAD, DK["niche_w"] / 2 + PP.ZONE_PAD, DK["yb"] - PP.ANSCHLAG["t"] / 2 - 0.05, ZF, DECK)
    chk("Dockzone hinter dem Steg ist frei (Nische: nichts steht im Weg)", vol_int(zones, uk))
    chk("Kontrolle: Winkelleiste 1,25 mm tiefer stößt an den Steg an", 0.0 if vol_int(hd.translate([0, 0, -1.25]), uk) > 0.05 else 1.0)
    pz = post_positions()[0]
    chk("Zapfen im Zapfenloch der Oberplatte (Gleitspiel 0,15)", vol_int(BC.pin_solid_at(Point(*pz), DECK, PP.PIN, PP.CH_PIN), tp))
    chk("Kontrolle: Zapfen um 0,4 versetzt stößt an der Lochwand an", 0.0 if vol_int(BC.pin_solid_at(Point(pz[0] + 0.4, pz[1]), DECK, PP.PIN, PP.CH_PIN), tp) > 0.05 else 1.0)
    chk("Kontrolle: Schacht mit Spiel −0,05 stößt an der Kassette an", 0.0 if vol_int(kw, building_c(-0.05)) > 0.05 else 1.0)
    e_bund = D["z_tip"] - bw.bounding_box()[2]
    rep("  Buchse bündig: unten bei z=%.2f (Fußunterkante %.2f), Pin-Spitze bei z=%.2f, E = %.2f mm; an den Schultern (Luft %.2f) E = %.2f mm" % (
        bw.bounding_box()[2], -D["F"], D["z_tip"], e_bund, k["zp"] - 14.55, e_bund - (k["zp"] - 14.55)))
    rep("  -> %s" % ("keine Kollisionen" if not bad else "%d Kollisionen!" % bad))

    tot = sum(i["g"] for i in info.values())
    from plug.roadmap import build as rb
    for prof, pr in rb.PROFILE.items():
        mins = sum(i["g"] / pr["rate"] * 60.0 + i["layers"] * pr["layer"] / 60.0 for i in info.values()) + pr["start"]
        rep("Material ≈ %.0f g, Zeit %s ≈ %.1f h" % (tot, prof, mins / 60.0))
    rep("Bei deinem Drucker (Nacht 1: 47 g in 2,5 h) ≈ %.1f h" % (tot / 47.0 * 2.5))
    with open(os.path.join(OUT, "pruefbericht.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(rep.lines) + "\n")
    previews(parts, bld, tp, uk, kw, bw, hd, vs)
    write_readme(info, tot, vs)
    zpath = os.path.join(OUT, "steckprobe2.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(os.listdir(OUT)):
            if f.endswith(".stl") or f == "README.txt":
                z.write(os.path.join(OUT, f), f)
    rep("%s: %.0f kB" % (os.path.relpath(zpath, HERE), os.path.getsize(zpath) / 1024))
    return bad


def building_c(c):
    """Mini-Gebäude mit anderem Schachtspiel (nur für die Kontrolle)."""
    old = P.KASS_CLR_T
    P.KASS_CLR_T = c
    try:
        return building()
    finally:
        P.KASS_CLR_T = old


def top_plate_norib(vs):
    cs = I.hcs(foot_poly())
    with BC.patched(sd, CLR=P.MULDE_CLR_T):
        cuts = list(I.pocket_cuts(cs, D["F"]))
    cuts += [BC.v_solid(v, DECK) for v in vs]
    with BC.patched(TB, SLOT_END=P.SLOT_END_T):
        cuts += BC.dock_cuts(H, DK)
    return BC.slab_ch(OUTLINE, DECK, 0.0, CH) - union(cuts)


def previews(parts, bld, tp, uk, kw, bw, hd, vs):
    import preview
    from PIL import Image
    col = dict(S2_cassette="#e3862a", S2_building="#e9e1c9", S2_top_plate="#b6cde0", S2_under_box="#8fa3b8")
    tms = {n: to_tm(m) for n, m in parts.items()}
    pos, need = SR.pack([(n, float(t.extents[0]), float(t.extents[1])) for n, t in tms.items()], bed=(130.0, 400.0))
    items = []
    for n, tm in tms.items():
        x, y = pos[n]
        tm.apply_translation([x - tm.bounds[0][0], y - tm.bounds[0][1], 0])
        items.append((tm, col[n]))
    preview.render(items, size=(1400, 900), azim=-60, elev=50).save(os.path.join(PREV, "teile.png"))
    cutx = lambda m: to_tm(xcut(m, 0.0))
    scenes = []
    for lift_b, lift_t in ((0.0, 0.0), (16.0, 6.0)):
        its = [(cutx(uk), "#8fa3b8"), (cutx(tp.translate([0, 0, lift_t])), "#b6cde0"), (cutx(hd.translate([0, 0, lift_t])), "#2d3236"),
               (cutx(bld.translate([0, 0, lift_b + lift_t])), "#e9e1c9"), (cutx(kw.translate([0, 0, lift_b + lift_t])), "#e3862a"), (cutx(bw.translate([0, 0, lift_b + lift_t])), "#f4f1e8")]
        scenes.append(preview.render(its, size=(1000, 900), azim=0, elev=0))
    sheet = Image.new("RGB", (2000, 900), "white")
    sheet.paste(scenes[0], (0, 0))
    sheet.paste(scenes[1], (1000, 0))
    sheet.save(os.path.join(PREV, "zusammenbau_schnitt.png"))
    its = [(to_tm(uk), "#8fa3b8"), (to_tm(tp.translate([0, 0, 20.0])), "#b6cde0"), (to_tm(hd.translate([0, 0, 20.0])), "#2d3236"),
           (to_tm(bld.translate([0, 0, 42.0])), "#e9e1c9"), (to_tm(kw.translate([0, 0, 42.0])), "#e3862a")]
    preview.render(its, size=(1100, 900), azim=-35, elev=40).save(os.path.join(PREV, "zusammenbau_schraeg.png"))
    a = preview.render([(to_tm(tp), "#b6cde0"), (to_tm(hd), "#2d3236")], size=(800, 700), azim=-90, elev=-80)
    b = preview.render([(to_tm(uk), "#8fa3b8")], size=(800, 700), azim=-90, elev=75)
    c = preview.render([(to_tm(tp), "#b6cde0"), (to_tm(hd), "#2d3236")], size=(800, 700), azim=-25, elev=-50)
    e = preview.render([(to_tm(uk), "#8fa3b8"), (to_tm(tp.translate([0, 0, 12.0])), "#b6cde0")], size=(800, 700), azim=-30, elev=35)
    sheet = Image.new("RGB", (1600, 1400), "white")
    for i, im in enumerate((a, b, c, e)):
        sheet.paste(im, ((i % 2) * 800, (i // 2) * 700))
    sheet.save(os.path.join(PREV, "platte_unterkasten.png"))
    # Schnitt durch je ein V (links 53°, rechts 40°), Ansicht senkrecht zur Achse; Oberplatte, Unterkasten, Hut als Streifen
    tiles = []
    chosen = [min(vs, key=lambda q: (q["slope"], -q["c"][1])), min(vs, key=lambda q: (-q["slope"], -q["c"][1]))]
    for v in chosen:
        xc = v["c"][0]
        if v["axis"] == "y":
            keep = lambda m, xc=xc: m - box(xc, 500, -500, 500, -500, 500) if xc < 0 else m - box(-500, xc, -500, 500, -500, 500)
            az = 0 if xc < 0 else 180
            cut = [(to_tm(keep(tp)), "#b6cde0"), (to_tm(keep(uk)), "#8fa3b8")]
            tiles.append(preview.render(cut, size=(800, 700), azim=az, elev=0))
    if len(tiles) == 2:
        sheet = Image.new("RGB", (1600, 700), "white")
        sheet.paste(tiles[0], (0, 0))
        sheet.paste(tiles[1], (800, 0))
        sheet.save(os.path.join(PREV, "faden_v.png"))
    print("Vorschau: %s" % os.path.relpath(PREV, HERE))


def write_readme(info, tot, vs):
    k = P.kass_dims()
    g = {n: info[n]["g"] for n in info}
    pw, pl_ = 2 * PX, PY1 - PY0
    ang = lambda sl: BC.math.degrees(BC.math.atan2(1.0, sl))
    txt = f"""STECKPROBE 2 (Plan: plug/testcase/plan2.html, Aufbau: plug/power/concept.html)
=============================================================================

Der komplette Steckmechanismus im Kleinen, jetzt im Zwei-Lagen-Aufbau der großen Platte: Oberplatte (Mulde, Dock, Faden-V) auf einem hohlen
Unterkasten. Gedruckt wird alles in einem Lauf. Alle Dateien liegen in Druckausrichtung, keine Stützen.

Dateien
  S2_cassette.stl      1 × Kassette ({de(k['cw'], 1)} × {de(k['L'], 1)} × {de(k['top'], 2)} mm), Tasche {de(k['zp'], 2)} hoch (Luft über der Buchse etwa 0,05), Fase {de(P.EF_CH_T, 1)}.
                       Nur diese eine Kassette, keine Reserve.   ≈ {de(g['S2_cassette'], 1)} g
  S2_building.stl      Mini-Gebäude, L-Fuß {de(P.BOX_W, 0)} × {de(P.BOX_L, 0)}, Schacht {de(P.KASS_CLR_T)} durchgehend, {de(D['kass_h'] + P.SHAFT_EXTRA_T, 2)} tief (Kassette + {de(P.SHAFT_EXTRA_T, 1)}),
                       Anschlagrand {de(P.STOP_T, 1)}, Fußfase {de(sd.CH_F, 1)}, Fase {de(P.ENTRY_CH_T, 1)} am Schachteingang.   ≈ {de(g['S2_building'], 1)} g
  S2_top_plate.stl     Mini-Oberplatte {de(pw, 0)} × {de(pl_, 0)} × {de(-DECK, 1)} mm: Mulde {de(D['F'], 1)} tief (Spiel {de(P.MULDE_CLR_T)}, Muldenfase {de(sd.CH_P, 1)}), Muldenboden {de(P.CEIL_T, 1)},
                       Dock wie Platte B (Trichter um die Pins, nach unten offene Körpertasche, Schlitz bis {de(P.SLOT_END_T, 1)}) plus <b>Kabelnische</b> {de(DK['niche_w'], 0)} × {de(DK['y_slot'] - DK['niche_end'], 0)} mm
                       ohne Fenster und Stege (der gedruckte Stand r4 hatte drei Fenster mit zwei Stegen, siehe `plug/logbook/rounds/r4_steckprobe2/steckprobe2.zip`), Rippen an der Körpertasche, zwei Zapfenlöcher, vier Faden-V.   ≈ {de(g['S2_top_plate'], 1)} g
                       Faden-V: <b>linke Ecken 53°</b> (Beschriftung „53“), <b>rechte Ecken 40°</b> (Beschriftung „40“).
  S2_under_box.stl     Mini-Unterkasten {de(pw, 0)} × {de(pl_, 0)} × {de(H['uk_t'], 1)} mm, innen hohl: Steg-Anschlag unter dem Körper der Winkelleiste ({de(PP.STAMP_AIR, 1)} Luft),
                       vier Stützen, zwei Zapfen, vier Eckaussparungen für den Faden, Kabelfenster in der Vorderwand.   ≈ {de(g['S2_under_box'], 1)} g
  Zusammen ≈ {de(tot, 0)} g; bei deinem Drucker (Nacht 1: 47 g in 2,5 h) etwa {de(tot / 47.0 * 2.5, 1)} h.

Kaufteile: Winkelleiste (4 Pins), Dupont-Buchse mit gecrimpten Adern, LED-Streifen 10 mm, Faden und eine Nadel (für den Test der Faden-V),
  ein Tropfen Heißkleber. Keine Schrauben.

Slicer wie bisher (Bambu, PLA, 0,2 mm, 3 Wände, 15 % Füllung), ohne Stützen, „Thick bridges“ an.
  Oberplatte: Unterseite liegt auf dem Bett (Mulde oben). Alle Hohlräume sind Böschung, kurze Decke oder die eine Kabelnische (mit Support); die Decke der Kabelnische liegt
  1,6 mm über dem Bett. Die Faden-V haben 0,15 (links, 53°) bzw. 0,24 mm Überhang je Schicht (rechts, 40°): das ist der Test.
  Unterkasten: offen nach oben gedruckt, Boden auf dem Bett.
  Die Fasen ({de(P.EF_CH_T, 1)} an den Bettkanten) gleichen den Elefantenfuß aus.

Die Höhe der Buchsengehäuse muss nicht mehr gemessen werden (Tasche {de(k['zp'], 2)} hoch, bewährt aus Steckprobe 1).

Zusammenbau
  1. Winkelleiste von unten in die Oberplatte schieben (Oberplatte mit der Unterseite nach oben): Pins durch den Muldenboden, Körper in die Tasche, Lötenden nach hinten
     in den Schlitz und die Nische. Die Rippen halten den Körper; ein Tropfen Heißkleber ist erlaubt.
  2. Buchse bündig einsetzen: Buchse mit der Steckseite auf einen flachen Tisch stellen, Kassette von oben darüberstülpen. LED-Streifen auf das Podest legen.
  3. Kassette mit der offenen Seite voran von unten in das Mini-Gebäude drücken, bis sie am Rand anschlägt.
  4. Faden durch je ein V ziehen (Trichter hinein, über die Lasche, Trichter heraus), Enden hängen lassen.
  5. Unterkasten unter die Oberplatte setzen: Zapfen in die Löcher, der Steg liegt {de(PP.STAMP_AIR, 1)} unter dem Körper, die Fadenenden hängen durch die Eckaussparungen.
  6. Mini-Gebäude in die Mulde setzen, Kabel der Lötenden durch die Nische nach unten und aus dem Kabelfenster führen.

Prüfung: siehe Testbogen (plug/testcase/feedback2.html).
"""
    with open(os.path.join(OUT, "README.txt"), "w", encoding="utf-8") as f:
        f.write(txt.replace("<b>", "").replace("</b>", ""))


if __name__ == "__main__":
    raise SystemExit(1 if main() else 0)
