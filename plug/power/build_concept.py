"""Konzept Grundplatte mit Powerbank (Stand 3, 1:1000): Oberplatte, hohler Unterkasten, Powerbank Intenso XS5000, Faden zum Doktorhut.

Stand 3 übernimmt die Maßkette und Passungen der Steckprobe (`plug/testcase/params.py`, Plan Steckprobe 2), siehe
`plug/power/params.py`:

- Oberplatte: Mulde F (10,2) + Muldenboden (0,4) + Körper der Winkelleiste (2,0) = 12,6 mm. Dock wie Platte B, die Tasche der
  Leiste ist nach unten offen; der Kabelraum ist der Unterkasten (Lehre L20). Mulde mit 0,10 Spiel je Seite.
- Unterkasten (ersetzt den Deckel): Boden, Außenwand, Stützen, einige davon mit Zentrierzapfen für die Oberplatte, Zaun um die
  Powerbank, Fenster in der Kante, Stößel zur Taste, Eckaussparungen für den Faden. Offen nach oben gedruckt, keine Brücken.
- Faden: V-Kanal mit Trichtern in jeder Ecke der Oberplatte (Zwischenstand Steckprobe 2). Der Faden kommt vom Hut durch die
  Eckaussparung des Unterkastens, läuft schräg durch die Lasche und wieder hinunter; festgezogen drückt er die Oberplatte auf den
  Unterkasten und beides auf den Hut.

Aufruf aus dem Repo-Wurzelverzeichnis: `python3 -m plug.power.build_concept` (rund 15 s), schreibt `plug/power/concept.html`.
"""
import json
import math
import os
import sys

import manifold3d as m3d
import numpy as np
import shapely
from shapely import affinity
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import generate as G  # noqa: E402
import innenhof  # noqa: E402
from plug import dupont as sd  # noqa: E402
from plug.geom import encode  # noqa: E402
from plug.power import params as PP  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "concept.template.html")
OUT = os.path.join(HERE, "concept.html")
SCALE = 1000

FACH_L = PP.PB_PLUG + PP.PB_L + 2 * PP.PB_CLR       # Fach entlang der Powerbank: Steckerraum + Powerbank
FACH_W = PP.PB_W + 2 * PP.PB_CLR + PP.PB_CABLE      # quer: Powerbank + Kabelkanal
FACH_H = sd.layer_up(PP.PB_T + PP.PB_CLR_Z)
OLD = dict(stand1=31.2, ober1=16.2, uk1=15.0)        # Stand 1 des Konzepts (für den Vergleich)


def heights():
    """z-Lagen (Plattenoberseite = 0), Maßkette der Steckprobe."""
    d = PP.stack()
    deck = d["z_bb"]                                    # Unterseite Oberplatte = Unterkante Leistenkörper
    uk_bot = deck - FACH_H - PP.UK_FLOOR
    return dict(F=d["F"], E=d["E"], ceil=PP.CEIL, body=sd.HDR_BODY, z_hb=d["z_hb"], z_bb=d["z_bb"], z_tip=d["z_tip"],
                z_bm=d["z_bm"], deck=deck, fach_h=FACH_H, floor=PP.UK_FLOOR, uk_bot=uk_bot, total=-uk_bot, uk_t=deck - uk_bot,
                stamp_top=d["z_bb"] - PP.STAMP_AIR, pocket=G.POCKET_DEPTH, old=OLD["stand1"], old_ober=OLD["ober1"],
                tc_plate=d["plate_t"])


class Frame:
    """Fach-Koordinaten: u von der Anschlussseite ins Fach, v quer (Kabelkanal bei +v). Mitte des Fachs = (0, 0)."""

    def __init__(self, cx, cy, ang, sgn=1):
        a = math.radians(ang)
        self.c = np.array([cx, cy])
        self.u = np.array([math.cos(a), math.sin(a)])
        self.v = sgn * np.array([-math.sin(a), math.cos(a)])
        self.ang, self.sgn = ang, sgn

    def pt(self, u, v):
        return self.c + u * self.u + v * self.v

    def rect(self, u0, u1, v0, v1):
        return Polygon([self.pt(u0, v0), self.pt(u1, v0), self.pt(u1, v1), self.pt(u0, v1)]).buffer(0)


U0, U1 = -FACH_L / 2, FACH_L / 2
V0, V1 = -FACH_W / 2, FACH_W / 2
BU0 = U0 + PP.PB_PLUG + PP.PB_CLR            # Anschlussseite der Powerbank
BV0 = V0 + PP.PB_CLR
BVC = BV0 + PP.PB_W / 2                      # Mitte der Powerbank quer
KV0 = V1 - PP.PB_CABLE                       # Kabelkanal
PORT_HALF = dict(usb_a=6.25, usb_c=4.5, micro=3.75, taste=2.0, leds=5.0)   # S  halbe Breite je Anschluss
WIN = [BVC + PP.PB_PORT_V["leds"] - PORT_HALF["leds"] - PP.WINDOW_PAD,
       BVC + PP.PB_PORT_V["usb_c"] + PORT_HALF["usb_c"] + PP.WINDOW_PAD]


def fach_parts(f):
    ua = BVC + PP.PB_PORT_V["usb_a"]
    plug_end = BU0 - 25.0
    kc = KV0 + PP.PB_CABLE / 2
    cable = [f.pt(BU0, ua), f.pt(plug_end, ua), f.pt(plug_end - 5, (ua + kc) / 2), f.pt(plug_end, kc),
             f.pt(U1, kc), f.pt(U1 + 12, kc)]
    inner = f.rect(BU0 - PP.PB_CLR, U1, V0, KV0)
    fence = inner.buffer(PP.FENCE[0], join_style=2).difference(inner) \
        .difference(f.rect(U0 - 5, BU0 + 2, V0 - 5, V1 + 5)).difference(f.rect(BU0, U1 + 5, KV0 - 0.1, V1 + 5))
    tv = BVC + PP.PB_PORT_V["taste"]
    return dict(
        fach=f.rect(U0, U1, V0, V1), body=f.rect(BU0, BU0 + PP.PB_L, BV0, BV0 + PP.PB_W),
        niche=f.rect(U0, BU0 - PP.PB_CLR, V0, V1), channel=f.rect(BU0 - PP.PB_CLR, U1, KV0, V1),
        plug=f.rect(plug_end, BU0, ua - 7.5, ua + 7.5),
        rod=f.rect(U0 - PP.UK_WALL, BU0, tv - PP.ROD / 2, tv + PP.ROD / 2),
        window=f.rect(U0 - PP.UK_WALL - 1, U0 + 0.5, WIN[0], WIN[1]), fence=fence,
        cable=[np.round(p, 2).tolist() for p in cable], far=f.pt(U1, kc))


def place_edge(outline, hof_fp):
    """Anschlussseite an einer Plattenkante, Powerbank möglichst weit unter dem Innenhof."""
    inner = outline.buffer(-PP.UK_WALL, join_style=2)
    x0, y0, x1, y1 = inner.bounds
    hc = hof_fp.centroid
    best = None
    for side, ang in (("W", 0), ("O", 180), ("S", 90), ("N", 270)):
        for sgn in (1, -1):
            if side in "WO":
                cy = min(max(hc.y, y0 + FACH_W / 2), y1 - FACH_W / 2)
                cx = x0 + FACH_L / 2 if side == "W" else x1 - FACH_L / 2
            else:
                cx = min(max(hc.x, x0 + FACH_W / 2), x1 - FACH_W / 2)
                cy = y0 + FACH_L / 2 if side == "S" else y1 - FACH_L / 2
            f = Frame(cx, cy, ang, sgn)
            fp = fach_parts(f)
            if not inner.buffer(1e-6).contains(fp["fach"]):
                continue
            score = fp["body"].intersection(hof_fp).area
            if best is None or score > best[0] + 1:
                best = (score, side, f)
    return best[1], best[2]


def place_box(inner, blocked, near, size):
    a, b = size
    x0, y0, x1, y1 = inner.bounds
    best = None
    for w, h in ((a, b), (b, a)):
        for x in np.arange(x0 + w / 2, x1 - w / 2, 1.0):
            for y in np.arange(y0 + h / 2, y1 - h / 2, 1.0):
                r = box(x - w / 2, y - h / 2, x + w / 2, y + h / 2)
                if not inner.contains(r) or r.intersects(blocked):
                    continue
                d = math.hypot(x - near[0], y - near[1])
                if best is None or d < best[0]:
                    best = (d, r)
    return best[1]


# --------------------------------------------------------------------------
# Fadenführung: V-Kanal in der Oberplatte, Eckaussparung im Unterkasten
# --------------------------------------------------------------------------
V = PP.V
V_HS = V["apex"] * V["slope"]                 # Abstand Eintritt bis Scheitel entlang der Achse


def v_geom(cx, cy, axis):
    """Ein V: Mitte (Scheitel) bei (cx, cy), Achse 'y' oder 'x'. Eintritte, Fußabdruck mit Wänden, Trichterbereich."""
    if axis == "y":
        ent = [(cx, cy - V_HS), (cx, cy + V_HS)]
    else:
        ent = [(cx - V_HS, cy), (cx + V_HS, cy)]
    r = V["entry_r"]
    funnels = unary_union([shapely.Point(p).buffer(r, 24) for p in ent])
    foot = funnels.buffer(V["wall"], join_style=2).envelope
    return ent, funnels, foot


def place_vs(outline, blocked):
    """Je Ecke ein V so nah an der Ecke wie möglich (Achse senkrecht zur nächsten Kante), Wände ≥ 1,4, frei von Mulden und Hof."""
    x0, y0, x1, y1 = outline.bounds
    out = []
    for sx, sy, cxo, cyo in ((1, 1, x0, y0), (-1, 1, x1, y0), (1, -1, x0, y1), (-1, -1, x1, y1)):
        best = None
        for axis in ("y", "x"):
            for da in np.arange(0, 60, 0.5):         # entlang der Achse ab V["y"]
                for db in np.arange(0, 60, 0.5):     # quer
                    if best is not None and da + db >= best[0]:
                        break
                    if axis == "y":
                        cx = cxo + sx * (V["entry_r"] + V["wall"] + db)
                        cy = cyo + sy * (V["y"] + da)
                    else:
                        cx = cxo + sx * (V["y"] + da)
                        cy = cyo + sy * (V["entry_r"] + V["wall"] + db)
                    ent, fun, foot = v_geom(cx, cy, axis)
                    if outline.contains(foot) and not foot.intersects(blocked):
                        best = (da + db, cx, cy, axis, ent, fun, foot)
        _, cx, cy, axis, ent, fun, foot = best
        # Eckaussparung: Trichter + Rand, bis zur Kante entlang der Achse und, wenn nah, auch quer
        nb = fun.buffer(PP.NOTCH_PAD, join_style=2).bounds
        nx0, ny0, nx1, ny1 = nb
        if axis == "y":
            ny0, ny1 = (y0 - 1, ny1) if sy > 0 else (ny0, y1 + 1)
            if (nx0 - x0 if sx > 0 else x1 - nx1) < 6:
                nx0, nx1 = (x0 - 1, nx1) if sx > 0 else (nx0, x1 + 1)
        else:
            nx0, nx1 = (x0 - 1, nx1) if sx > 0 else (nx0, x1 + 1)
            if (ny0 - y0 if sy > 0 else y1 - ny1) < 6:
                ny0, ny1 = (y0 - 1, ny1) if sy > 0 else (ny0, y1 + 1)
        out.append(dict(c=(cx, cy), axis=axis, ent=ent, funnels=fun, foot=foot, notch=box(nx0, ny0, nx1, ny1)))
    return out


def v_solid(v, deck):
    """Hohlraum eines V (Schenkel als Prismen, Trichter als Kegel) für die Oberplatte."""
    ld, r = V["leg_d"], V["entry_r"]
    apex_z = deck + V["apex"]
    parts = []
    # Schenkel in (t, z): von Eintritt (t = ∓V_HS, z = deck − 0,5) zum Scheitel (t = 0, z = apex)
    for s in (-1, 1):
        t0, z0, t1, z1 = s * V_HS * (1 + 0.5 / V["apex"]), deck - 0.5, 0.0, apex_z
        n = np.array([-(z1 - z0), (t1 - t0)])
        n = n / np.linalg.norm(n) * ld / 2
        poly = [(t0 + n[0], z0 + n[1]), (t1 + n[0], z1 + n[1]), (t1 - n[0], z1 - n[1]), (t0 - n[0], z0 - n[1])]
        if s > 0:
            poly = poly[::-1]
        cs = m3d.CrossSection([poly])
        leg = m3d.Manifold.extrude(cs, ld).rotate([90, 0, 0]).translate([0, ld / 2, 0])
        parts.append(leg)
    cap = m3d.Manifold.cylinder(ld, ld / 2, ld / 2, 16).rotate([90, 0, 0]).translate([0, ld / 2, apex_z])
    parts.append(cap)
    core = G.union(parts)
    if v["axis"] == "y":
        core = core.rotate([0, 0, 90])
    core = core.translate([v["c"][0], v["c"][1], 0])
    cones = [m3d.Manifold.cylinder(1.5, r, ld / 2, 24).translate([p[0], p[1], deck - 0.01]) for p in v["ent"]]
    return G.union([core] + cones)


def unterkasten_cut(length, deck_cuts, avoid):
    """Schnitte des Unterkastens (y), versetzt zu denen der Oberplatte, nicht durch Fach, Elektronik, Aussparungen."""
    if length <= PP.BED:
        return []
    n = math.ceil(length / PP.BED)
    cuts = []
    for k in range(1, n):
        target = length * k / n
        best = None
        for y in np.arange(length - (n - k) * PP.BED + 3, k * PP.BED - 3, 0.5):
            if any(abs(y - c) < 25 for c in deck_cuts):
                continue
            line = shapely.LineString([(-1e4, y), (1e4, y)])
            if any(line.intersects(a) for a in avoid):
                continue
            if best is None or abs(y - target) < abs(best - target):
                best = y
        cuts.append(round(float(best), 1) if best is not None else None)
    return cuts


# --------------------------------------------------------------------------
# Ausgabe
# --------------------------------------------------------------------------
def coords(geom, sh):
    out = []
    for p in G.polys_of(geom):
        out.append([[round(x + sh[0], 2), round(y + sh[1], 2)] for x, y in list(p.exterior.coords)[:-1]])
    return out


def mesh(man, sh):
    return encode(G.to_trimesh(man.translate([sh[0], sh[1], 0])))


def grams(man):
    """[g bei SHELL mm Hülle und INFILL Füllung, Volumen cm³]; Schätzung."""
    tm = G.to_trimesh(man)
    vol = float(abs(tm.volume))
    shell = min(vol, float(tm.area) * PP.SHELL)
    return [round((shell + PP.INFILL * (vol - shell)) / 1000 * PP.PLA), round(vol / 1000, 1)]


def section(outline, fps, hof_fp, f):
    """Schnitt entlang der Powerbank-Mitte: Abschnitte (t0, t1) ab der Plattenkante auf der Anschlussseite."""
    p_mid = f.pt(0, BVC)
    line = shapely.LineString([p_mid - 2000 * f.u, p_mid + 2000 * f.u])
    seg = line.intersection(outline)
    p0 = np.array(seg.coords[0])
    if np.dot(p0 - p_mid, f.u) > 0:
        p0 = np.array(seg.coords[-1])
    t = lambda pt: float(np.dot(np.array(pt) - p0, f.u))  # noqa: E731
    items = []
    for kind, title, g in [("bld", b["title"], fps[b["slug"]]) for b in G.BUILDINGS] + [("hof", "Innenhof", hof_fp)]:
        cut = g.intersection(line)
        for part in getattr(cut, "geoms", [cut]):
            if part.is_empty or part.length < 0.5:
                continue
            ts = sorted(t(c) for c in part.coords)
            items.append(dict(kind=kind, title=title, t0=round(ts[0], 1), t1=round(ts[-1], 1)))
    return dict(len=round(seg.length, 1), items=sorted(items, key=lambda i: i["t0"]), u0=round(t(f.pt(U0, BVC)), 1))


def fit_rows():
    """Passmaße: Fuge, Wert, Status, Herkunft."""
    d = PP.stack()
    pin = PP.PIN
    return [
        ["Fuß in der Mulde", "Spiel %.2f je Seite, Mulde %.1f tief" % (PP.MULDE_CLR, d["F"]), "bewährt", "Steckprobe 1 (r2 FM, r3 M)"],
        ["Muldenboden über der Winkelleiste", "%.1f mm, Pinlöcher %.1f mit Fase, E %.2f" % (PP.CEIL, sd.HOLE, d["E"]), "vorläufig",
         "r2 K, r3 S"],
        ["Winkelleiste in der Tasche", "Spiel %.1f, Tasche +1,5 zum Lötende, Stufe für 1,8" % sd.SNUG_HDR, "bewährt, Kippen offen",
         "r2 D, r3 W"],
        ["Halt der Winkelleiste von unten", "Anschlag aus dem Unterkasten mit %.1f mm Luft, dazu Heißkleber" % PP.STAMP_AIR,
         "Vorschlag", "Plan Steckprobe 2, Karten D und K; L06, L21"],
        ["Kabel hinter den Lötenden", "Tasche nach unten offen, Unterkasten %.1f mm hoch frei" % (heights()["uk_t"]), "Vorschlag", "L20"],
        ["Oberplatte auf Unterkasten", "Zapfen Ø %.1f × %.1f, Loch Ø %.1f (%.2f Gleitspiel), Fase %.1f" % (
            pin["d"], pin["h"], pin["d"] + 2 * pin["clr"], pin["clr"], PP.EF_CH), "Vorschlag", "L10 (0,15 gleitet)"],
        ["Faden", "V-Kanal Ø %.1f, Scheitel %.1f, Böschung 0,15 je Schicht, Trichter R %.1f, Wände ≥ %.1f; Eckaussparung im Unterkasten" % (
            V["leg_d"], V["apex"], V["entry_r"], V["wall"]), "Zwischenstand", "Plan Steckprobe 2, Karte F; L29"],
        ["Powerbank im Zaun", "%.1f je Seite, %.1f Luft oben" % (PP.PB_CLR, PP.PB_CLR_Z), "geschätzt, ungemessen", "Fachprobe"],
        ["Stecker vor der Powerbank", "%.0f mm Steckerraum, Kabelkanal %.0f mm" % (PP.PB_PLUG, PP.PB_CABLE), "geschätzt, ungemessen",
         "Fachprobe"],
        ["Stößel zur Taste", "%.0f × %.0f mm, Führung mit 0,15 Spiel" % (PP.ROD, PP.ROD), "Vorschlag", "L10"],
        ["Bettkanten, Löcher am Bett", "Fase %.1f" % PP.EF_CH, "Vorschlag", "L02, L03, Plan Steckprobe 2"],
        ["Decken und Brücken", "höchstens 10 mm, keine Löcher in dünnen Brücken, sonst Böschung", "Regel", "L04, L05"],
    ]


def main():
    h = heights()
    print("Höhen:", {k: round(v, 2) for k, v in h.items()})
    s = 1000.0 / SCALE
    m = G.osm_models(s)
    fps = {k: v[1] for k, v in m.items()}
    hof_solid, hof_fp, _ = innenhof.model(s, list(fps.values()))
    sel = list(G.BUILDINGS)
    foot_fp = unary_union([fps[b["slug"]] for b in sel])
    fp_all = unary_union([foot_fp, hof_fp])
    outline = G.plate_outline(fp_all)
    minx, miny, maxx, maxy = outline.bounds
    sh = (-minx, -miny)
    W, L = maxx - minx, maxy - miny
    deck_cuts = [round(float(c - miny), 1) for c in G.tile_cuts(outline, fp_all)]
    inner = outline.buffer(-PP.UK_WALL, join_style=2)
    mulden_fp = foot_fp.buffer(PP.MULDE_CLR, join_style=2)
    pocket_fp = hof_fp.buffer(G.POCKET_CLEARANCE, join_style=2)
    deck, bot = h["deck"], h["uk_bot"]

    side, f = place_edge(outline, hof_fp)
    fp = fach_parts(f)
    elec = place_box(inner.buffer(-1), fp["fach"].buffer(4.0, join_style=2), fp["far"], PP.ESP_BOX)
    vs = place_vs(outline, unary_union([mulden_fp.buffer(V["wall"]), pocket_fp.buffer(V["wall"]),
                                        fp["fach"].buffer(3), elec.buffer(3)]))
    notches = [v["notch"] for v in vs]

    # Stützen und Zapfen
    free = inner.buffer(-PP.POST[0]).difference(unary_union([fp["fach"].buffer(3), elec.buffer(3)] +
                                                             [n.buffer(3) for n in notches]))
    posts = []
    for x in np.arange(minx + PP.POST[1] / 2, maxx, PP.POST[1]):
        for y in np.arange(miny + PP.POST[1] / 2, maxy, PP.POST[1]):
            r = box(x - PP.POST[0] / 2, y - PP.POST[0] / 2, x + PP.POST[0] / 2, y + PP.POST[0] / 2)
            if free.contains(r):
                posts.append(r)
    targets = [(minx + 0.3 * W, miny + 15), (maxx - 0.3 * W, maxy - 15)]
    for c in deck_cuts:
        for fx in (0.3, 0.7):
            for dy in (-12, 12):
                targets.append((minx + fx * W, miny + c + dy))
    pins = set()
    for tx, ty in targets:
        cand = [(math.hypot(r.centroid.x - tx, r.centroid.y - ty), i) for i, r in enumerate(posts) if i not in pins]
        if cand:
            pins.add(min(cand)[1])

    # --- Oberplatte ---
    pin = PP.PIN
    ober = G.extrude(outline, deck, 0.0) - G.extrude(mulden_fp, -h["F"], 1.0) - G.extrude(pocket_fp, -G.POCKET_DEPTH, 1.0)
    cuts = [v_solid(v, deck) for v in vs]
    for i in pins:
        c = posts[i].centroid
        cuts.append(G.extrude(shapely.Point(c.x, c.y).buffer(pin["d"] / 2 + pin["clr"], 24), deck - 1, deck + pin["h"] + 0.3))
    ober = ober - G.union(cuts)

    # --- Unterkasten ---
    solids = [G.extrude(outline, bot, bot + PP.UK_FLOOR),
              G.extrude(outline.difference(outline.buffer(-PP.UK_WALL, join_style=2)), bot, deck),
              G.extrude(fp["fence"], bot, bot + PP.UK_FLOOR + PP.FENCE[1])]
    solids += [G.extrude(r, bot, deck) for r in posts]
    solids += [G.extrude(shapely.Point(posts[i].centroid.x, posts[i].centroid.y).buffer(pin["d"] / 2, 24), deck - 0.01,
                         deck + pin["h"]) for i in pins]
    uk = G.union(solids) - G.union([G.extrude(n, bot - 1, deck + 2) for n in notches] +
                                   [G.extrude(fp["window"], bot + PP.UK_FLOOR, deck + 0.5)])

    uk_cuts = unterkasten_cut(L, deck_cuts, [affinity.translate(g, *sh) for g in [fp["fach"], elec] + notches])
    bld = {b["slug"]: mesh(m[b["slug"]][0] + G.extrude(fps[b["slug"]], -h["F"], 0.01), sh) for b in sel}
    mat = dict(ober=grams(ober), uk=grams(uk))
    print("Platte %.1f × %.1f × %.1f mm, Kante %s, Powerbank %d %% unter dem Hof, Schnitte %s / %s, Material %s, Zapfen %d"
          % (W, L, h["total"], side, fp["body"].intersection(hof_fp).area / fp["body"].area * 100, deck_cuts, uk_cuts, mat,
             len(pins)))

    data = dict(
        heights=h, scale=SCALE, plate=[round(W, 1), round(L, 1)], thick=round(h["total"], 1),
        outline=coords(outline, sh), deck_cuts=deck_cuts, uk_cuts=uk_cuts,
        buildings=[dict(slug=b["slug"], title=b["title"], poly=coords(fps[b["slug"]], sh),
                        h=round(float(G.to_trimesh(m[b["slug"]][0]).bounds[1][2]), 1)) for b in sel],
        hof=coords(hof_fp, sh), hub=round(innenhof.hub(innenhof.load(), s), 2),
        fach_poly=coords(fp["fach"], sh), body=coords(fp["body"], sh), niche=coords(fp["niche"], sh),
        channel=coords(fp["channel"], sh), plug=coords(fp["plug"], sh), rod=coords(fp["rod"], sh),
        window=coords(fp["window"], sh), cable=[[p[0] + sh[0], p[1] + sh[1]] for p in fp["cable"]],
        elec=coords(elec, sh), posts=[dict(r=coords(r, sh)[0], pin=i in pins) for i, r in enumerate(posts)],
        vs=[dict(c=[v["c"][0] + sh[0], v["c"][1] + sh[1]], axis=v["axis"],
                 ent=[[p[0] + sh[0], p[1] + sh[1]] for p in v["ent"]], notch=coords(v["notch"], sh)[0]) for v in vs],
        frame=dict(ang=f.ang, sgn=f.sgn, c=[f.c[0] + sh[0], f.c[1] + sh[1]]), side=side,
        under_hof=round(fp["body"].intersection(hof_fp).area / fp["body"].area * 100),
        hut=dict(size=PP.HUT, fits=bool(W <= PP.HUT and L <= PP.HUT)),
        section=section(outline, fps, hof_fp, f), material=mat, fits=fit_rows(),
        meshes=dict(ober=mesh(ober, sh), uk=mesh(uk, sh), buildings=bld, hof=mesh(hof_solid, sh)),
        pb=dict(L=PP.PB_L, W=PP.PB_W, T=PP.PB_T, g=PP.PB_G, wh=PP.PB_WH, imax=PP.PB_IMAX, sleep=PP.PB_SLEEP_S,
                keep=PP.PB_KEEP_MA, ports=PP.PB_PORTS, port_v=PP.PB_PORT_V, clr=PP.PB_CLR, clr_z=PP.PB_CLR_Z, plug=PP.PB_PLUG,
                cable=PP.PB_CABLE, rod=PP.ROD),
        fach=dict(L=FACH_L, W=FACH_W, H=FACH_H, u0=U0, bu0=BU0, bv0=BV0, kv0=KV0, win=WIN),
        uk=dict(floor=PP.UK_FLOOR, wall=PP.UK_WALL, fence=PP.FENCE, post=PP.POST, pin=PP.PIN), v=V, v_hs=V_HS,
        esp=PP.ESP_BOX, bed=PP.BED, mat=dict(shell=PP.SHELL, infill=PP.INFILL, pla=PP.PLA),
    )
    tpl = open(TEMPLATE, encoding="utf-8").read()
    html = tpl.replace("/*DATA*/", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    open(OUT, "w", encoding="utf-8").write(html)
    print("geschrieben:", os.path.relpath(OUT, ROOT), "(%.1f MB)" % (len(html) / 1e6))


if __name__ == "__main__":
    main()
