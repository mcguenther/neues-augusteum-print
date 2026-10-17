"""Konzept Grundplatte mit Powerbank (Stand 4): Oberplatte, hohler Unterkasten, Powerbank Intenso XS5000, Faden zum Doktorhut.

Stand 4 gegenüber Stand 3 (Rückmeldung des Nutzers):

- Fasen: Gebäudefuß unten 0,8 (`institute.foot_solid`) und Mulde oben 1,0 (`institute.pocket_cuts`) wie im Probestück, dazu Bettkanten 0,5
  an Oberplatte, Unterkasten, Eckaussparungen, Mündungen und Zapfenlöchern; Zapfen oben 0,5; Innenhof-Teil unten 0,4.
- Maßstab: zwei Varianten (1:1000 Referenz, 1:1300 gewählt); der Doktorhut (24 cm, ungemessen) soll die Platte tragen, nicht umgekehrt.
- Dock: hinter den Lötenden eine Kabelnische in der Oberplatte (24 mm breit, 8 + 16 mm lang, mit Stegen), darunter freier Unterkasten
  ohne Zaun und Stützen; die Docks liegen nicht über der Powerbank. Der Anschlag ist ein Steg unter dem Körper der Leiste.
- Faden: V-Kanal 40° statt 53° zur Waagerechten (Böschung 1,2 statt 0,75).

Aufruf aus dem Repo-Wurzelverzeichnis: `python3 -m plug.power.build_concept` (rund 1 min), schreibt `plug/power/concept.html`.
"""
import json
import math
import os
import sys
from contextlib import contextmanager

import manifold3d as m3d
import numpy as np
import shapely
import shapely.prepared
from shapely import affinity
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import generate as G  # noqa: E402
import innenhof  # noqa: E402
from plug import dupont as sd  # noqa: E402
from plug import institute as I  # noqa: E402
from plug.geom import box as mbox  # noqa: E402
from plug.geom import encode, prism_x, prism_y, vol_int  # noqa: E402
from plug.power import params as PP  # noqa: E402
from plug.testcase import build as TB  # noqa: E402
from plug.testcase import params as TP  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "concept.template.html")
OUT = os.path.join(HERE, "concept.html")
L = sd.LAYER

FACH_L = PP.PB_PLUG + PP.PB_L + 2 * PP.PB_CLR       # Fach entlang der Powerbank: Steckerraum + Powerbank
FACH_W = PP.PB_W + 2 * PP.PB_CLR + PP.PB_CABLE      # quer: Powerbank + Kabelkanal
FACH_H = sd.layer_up(PP.PB_T + PP.PB_CLR_Z)
OLD = dict(stand1=31.2, ober1=16.2, uk1=15.0)        # Stand 1 des Konzepts (für den Vergleich)


@contextmanager
def patched(mod, **kw):
    old = {k: getattr(mod, k) for k in kw}
    for k, v in kw.items():
        setattr(mod, k, v)
    try:
        yield
    finally:
        for k, v in old.items():
            setattr(mod, k, v)


def heights():
    """z-Lagen (Plattenoberseite = 0), Maßkette der Steckprobe."""
    d = PP.stack_plan()
    deck = d["z_hb"]                                    # flache Unterseite der Oberplatte = F + Muldenboden (Leiste hängt darunter)
    uk_bot = deck - sd.layer_up(PP.STECKERRAUM + PP.PB_T) - PP.UK_FLOOR      # Steckerraum 3,5 über der Powerbank (die 0,8 Luft des Fachs sind darin enthalten)
    return dict(F=d["F"], E=d["E"], ceil=PP.CEIL, body=sd.HDR_BODY, z_hb=d["z_hb"], z_bb=d["z_bb"], z_tip=d["z_tip"],
                z_bm=d["z_bm"], deck=deck, fach_h=FACH_H, floor=PP.UK_FLOOR, uk_bot=uk_bot, total=-uk_bot, uk_t=deck - uk_bot,
                stamp_top=d["z_bb"] - PP.STAMP_AIR, pocket=TP.HOF_DEPTH_T, old=OLD["stand1"], old_ober=OLD["ober1"],
                tc_plate=d["plate_t"], z_slot=d["z_bb"] + 8 * L, step=d["step"], gap=PP.STECKERRAUM, plate_t=-deck)


H0 = heights()


# --------------------------------------------------------------------------
# Fasen (Bettkanten gegen den Elefantenfuß, Einführfasen)
# --------------------------------------------------------------------------
def n_layers(ch):
    return max(1, int(round(ch / L)))


def slab_ch(poly, z0, z1, ch):
    """Platte poly von z0 bis z1, untere Kante (am Bett) mit Fase ch in Schichtstufen (wie institute.foot_solid)."""
    n = n_layers(ch)
    parts = [G.extrude(poly.buffer(-(ch - L * (k + 0.5))), z0 + L * k, z0 + L * (k + 1) + 0.01) for k in range(n)]
    parts.append(G.extrude(poly, z0 + L * n, z1))
    return G.union(parts)


def mouth_ch(poly, z_bed, ch):
    """Einführfase einer Öffnung poly am Bett z_bed: Schnittkörper, der dort um ch je Seite größer ist (wächst nach oben)."""
    n = n_layers(ch)
    return G.union([G.extrude(poly.buffer(ch - L * (k + 0.5)), z_bed + L * k - 0.01, z_bed + L * (k + 1) + 0.01) for k in range(n)])


def pin_solid_at(c, deck, pin, ch):
    """Zentrierzapfen: Zylinder, oben mit Fase ch, auf der Unterkante deck der Oberplatte."""
    r, h = pin["d"] / 2, pin["h"]
    body = m3d.Manifold.cylinder(h - ch, r, r, 24)
    tip = m3d.Manifold.cylinder(ch, r, r - ch, 24).translate([0, 0, h - ch - 0.01])
    return G.union([body, tip]).translate([c.x, c.y, deck - 0.01])


# --------------------------------------------------------------------------
# Fach der Powerbank
# --------------------------------------------------------------------------
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
PORT_HALF = dict(usb_a=6.25, usb_c=4.5, micro=3.75, leds=5.0)   # S  halbe Breite je Anschluss
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
    return dict(
        fach=f.rect(U0, U1, V0, V1), body=f.rect(BU0, BU0 + PP.PB_L, BV0, BV0 + PP.PB_W),
        niche=f.rect(U0, BU0 - PP.PB_CLR, V0, V1), channel=f.rect(BU0 - PP.PB_CLR, U1, KV0, V1),
        plug=f.rect(plug_end, BU0, ua - 7.5, ua + 7.5),
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


def place_box(inner, blocked, near, size, step=1.0):
    a, b = size
    x0, y0, x1, y1 = inner.bounds
    best = None
    for w, h in ((a, b), (b, a)):
        for x in np.arange(x0 + w / 2, x1 - w / 2, step):
            for y in np.arange(y0 + h / 2, y1 - h / 2, step):
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
V_HS = V["apex"] * V["slope"]                 # Abstand Eintritt bis Scheitel entlang der Achse (Standard)
V_ANGLE = math.degrees(math.atan2(1.0, V["slope"]))


def v_hs(slope=None):
    """Abstand Eintritt bis Scheitel entlang der Achse für die Böschung slope (Standard: V["slope"])."""
    return V["apex"] * (V["slope"] if slope is None else slope)


def v_geom(cx, cy, axis, slope=None):
    hs = v_hs(slope)
    ent = [(cx, cy - hs), (cx, cy + hs)] if axis == "y" else [(cx - hs, cy), (cx + hs, cy)]
    funnels = unary_union([Point(p).buffer(V["entry_r"], 24) for p in ent])
    return ent, funnels, funnels.buffer(V["wall"], join_style=2).envelope


def place_vs(outline, blocked, slopes=None):
    """Je Ecke ein V so nah an der Ecke wie möglich (Achse senkrecht zur nächsten Kante), Wände ≥ 1,4, frei von Mulden und Hof.
    slopes: Böschung je Ecke (Reihenfolge SW, SO, NW, NO); Standard V["slope"]."""
    x0, y0, x1, y1 = outline.bounds
    out = []
    for i, (sx, sy, cxo, cyo) in enumerate(((1, 1, x0, y0), (-1, 1, x1, y0), (1, -1, x0, y1), (-1, -1, x1, y1))):
        sl = V["slope"] if slopes is None else slopes[i]
        yv = v_hs(sl) + V["entry_r"] + V["wall"]       # Mitte des V von der Kante: Trichter mit Wand zur Kante
        best = None
        for axis in ("y", "x"):
            for da in np.arange(0, 60, 0.5):
                for db in np.arange(0, 60, 0.5):
                    if best is not None and da + db >= best[0]:
                        break
                    if axis == "y":
                        cx, cy = cxo + sx * (V["entry_r"] + V["wall"] + db), cyo + sy * (yv + da)
                    else:
                        cx, cy = cxo + sx * (yv + da), cyo + sy * (V["entry_r"] + V["wall"] + db)
                    ent, fun, foot = v_geom(cx, cy, axis, sl)
                    if outline.contains(foot) and not foot.intersects(blocked):
                        best = (da + db, cx, cy, axis, ent, fun, foot)
        _, cx, cy, axis, ent, fun, foot = best
        nx0, ny0, nx1, ny1 = fun.buffer(PP.NOTCH_PAD, join_style=2).bounds
        if axis == "y":
            ny0, ny1 = (y0 - 1, ny1) if sy > 0 else (ny0, y1 + 1)
            if (nx0 - x0 if sx > 0 else x1 - nx1) < 6:
                nx0, nx1 = (x0 - 1, nx1) if sx > 0 else (nx0, x1 + 1)
        else:
            nx0, nx1 = (x0 - 1, nx1) if sx > 0 else (nx0, x1 + 1)
            if (ny0 - y0 if sy > 0 else y1 - ny1) < 6:
                ny0, ny1 = (y0 - 1, ny1) if sy > 0 else (ny0, y1 + 1)
        out.append(dict(c=(cx, cy), axis=axis, ent=ent, funnels=fun, foot=foot, notch=box(nx0, ny0, nx1, ny1), slope=sl))
    return out


def v_solid(v, deck):
    """Hohlraum eines V: zwei Schenkel (Böschung v["slope"]), runder Scheitel, Trichter am Bett."""
    ld, r = V["leg_d"], V["entry_r"]
    apex_z = deck + V["apex"]
    hs = v_hs(v.get("slope"))
    parts = []
    for s in (-1, 1):
        t0, z0, t1, z1 = s * hs * (1 + 0.5 / V["apex"]), deck - 0.5, 0.0, apex_z
        n = np.array([-(z1 - z0), (t1 - t0)])
        n = n / np.linalg.norm(n) * ld / 2
        poly = [(t0 + n[0], z0 + n[1]), (t1 + n[0], z1 + n[1]), (t1 - n[0], z1 - n[1]), (t0 - n[0], z0 - n[1])]
        if s > 0:
            poly = poly[::-1]
        parts.append(m3d.Manifold.extrude(m3d.CrossSection([poly]), ld).rotate([90, 0, 0]).translate([0, ld / 2, 0]))
    parts.append(m3d.Manifold.cylinder(ld, ld / 2, ld / 2, 16).rotate([90, 0, 0]).translate([0, ld / 2, apex_z]))
    core = G.union(parts)
    if v["axis"] == "y":
        core = core.rotate([0, 0, 90])
    core = core.translate([v["c"][0], v["c"][1], 0])
    cones = [m3d.Manifold.cylinder(1.5, r, ld / 2, 24).translate([p[0], p[1], deck - 0.01]) for p in v["ent"]]
    return G.union([core] + cones)


# --------------------------------------------------------------------------
# Docks: Winkelleiste mit Kabelnische (Platte B der Steckprobe + Nische, Anschlag im Unterkasten)
# --------------------------------------------------------------------------
def dock_numbers():
    """Maße des Docks im lokalen Rahmen: Pin-Reihe bei y = 0, Lötenden zeigen nach −y (wie Steckprobe)."""
    d = PP.stack_plan()
    yb = d["yb"]
    hd = sd.HDR_T / 2 + sd.SNUG_HDR
    hw = sd.HDR_W / 2 + sd.SNUG_HDR
    y_slot = yb - hd - TP.BODY_EXT_T
    se = PP.SLOT_END
    nl = se - PP.NICHE["l"]
    return dict(yb=yb, hd=hd, hw=hw, y_slot=y_slot, y_tail=d["y_tail"], slot_end=se, niche_end=nl, niche_w=PP.NICHE["w"],
                niche_l=y_slot - nl, z_slot=H0["z_slot"], step=d["step"], y_front=yb + hd,
                kass0=d["y_kass0"] - TP.KASS_CLR_T, kass1=d["y_kass1"] + TP.KASS_CLR_T,
                kass_w=TP.kass_dims()["cw"] + 2 * TP.KASS_CLR_T)


DK = dock_numbers()


def dock_windows(dk=DK):
    """Die eine Kabelnische in lokalen Koordinaten (ohne Fenster und Stege, Support erlaubt)."""
    w2 = dk["niche_w"] / 2
    y0, y1 = dk["niche_end"], dk["slot_end"] + 1.0
    return [box(-w2, y0, w2, y1)]


def dock_zone(dk=DK):
    """Raum unter der Platte, den keine Stütze belegt: Leistenkörper, Lötenden und hängender Draht plus Rand (lokal). Die Powerbank liegt darunter."""
    return box(-dk["hw"] - PP.ZONE_PAD, dk["y_tail"] - 4.0, dk["hw"] + PP.ZONE_PAD, dk["y_front"] + 2.0)


def dock_cuts(h=H0, dk=DK):
    """Schnittkörper der Oberplatte, lokal: Platte B (Tasche, Trichter um die Pins, Schlitz) + Kabelnische + Fasen am Bett."""
    d = PP.stack_plan()
    with patched(TB, SLOT_END=PP.SLOT_END):
        cuts = list(TB.dock_cuts_b(d))
    zbb = h["z_bb"]
    for win in dock_windows(dk):
        cuts.append(G.extrude(win, zbb - 0.5, h["z_slot"]))
        cuts.append(mouth_ch(win, zbb, PP.CH_BED))
    pocket = box(-dk["hw"], dk["y_slot"], dk["hw"], dk["yb"] + dk["hd"])
    cuts.append(mouth_ch(pocket, zbb, PP.CH_BED))
    return cuts


def dock_anschlag(h, dk, zf):
    """Steg unter dem Körper der Leiste im Unterkasten (lokal), 1,2 mm Luft zum Körper, Streben nach vorn."""
    aw, at, gs = PP.ANSCHLAG["w"], PP.ANSCHLAG["t"], PP.ANSCHLAG["gusset"]
    yb, zt = dk["yb"], h["stamp_top"]
    parts = [mbox(-aw / 2, aw / 2, yb - at / 2, yb + at / 2, zf - 0.01, zt)]
    for sx in (-1, 1):
        x = sx * (aw / 2 - at / 2)
        parts.append(prism_x([(yb + at / 2 - 0.01, zf - 0.01), (yb + at / 2 + gs, zf - 0.01), (yb + at / 2 - 0.01, zt - 2.0)],
                             x - at / 2, x + at / 2))
    return G.union(parts)


def to_world(man, phi, p):
    return man.rotate([0, 0, phi]).translate([p[0], p[1], 0])


def poly_world(poly, phi, p):
    return affinity.translate(affinity.rotate(poly, phi, origin=(0, 0)), p[0], p[1])


def max_inradius(poly):
    """Größter Kreis in poly (Abstand der Mitte zum Rand), durch schrittweises Schrumpfen."""
    lo, hi = 0.0, 30.0
    for _ in range(14):
        mid = (lo + hi) / 2
        if poly.buffer(-mid).is_empty:
            hi = mid
        else:
            lo = mid
    return lo


def kass_rect(slug):
    """Schacht der Kassette je Gebäude (v4, V1RS, V2R aus TP.CASSETTE, Maße wie plug/campus.py) im Dock-Rahmen (Pin-Reihe bei y = 0)."""
    from plug import campus as CA
    var = TP.CASSETTE[slug]
    w, dep = CA.shaft_size(var)
    yc = CA.foot_local(var, 0.0).centroid.y
    return box(-w / 2, -dep / 2 - yc, w / 2, dep / 2 - yc)


def kass_candidates(fps, dk, uniform=False):
    """Je Gebäude alle Lagen (Winkel, Pin-Reihe, Wert), in denen die Kassette mit Wand in den Fuß passt (unabhängig von Fach und Platte)."""
    out = {}
    for b in G.BUILDINGS:
        kass = box(-dk["kass_w"] / 2, dk["kass0"], dk["kass_w"] / 2, dk["kass1"]) if uniform else kass_rect(b["slug"])
        fp = fps[b["slug"]]
        core = fp.buffer(-PP.KASS_WALL)
        cands = []
        if not core.is_empty:
            pc = shapely.prepared.prep(core)
            xs = list(fp.minimum_rotated_rectangle.exterior.coords)
            a = math.degrees(math.atan2(xs[1][1] - xs[0][1], xs[1][0] - xs[0][0]))
            dirs = sorted({round((a + q) % 360, 1) for q in (0, 90, 180, 270)} | {float(q) for q in range(0, 360, 45)})
            x0, y0, x1, y1 = core.bounds
            for td in dirs:
                phi = td + 90.0            # lokales −y zeigt auf td (Lötenden, Nische)
                for px in np.arange(x0 - 20, x1 + 20, 1.5):
                    for py in np.arange(y0 - 20, y1 + 20, 1.5):
                        kp = poly_world(kass, phi, (px, py))
                        if pc.contains(kp):
                            cands.append((kp.centroid.distance(fp.boundary), phi, (px, py)))
            cands.sort(key=lambda c: -c[0])
        out[b["slug"]] = cands
    return out


def place_docks(cands, forbidden, inner, dk, kept=()):
    """Je Gebäude ein Dock: Kassette passt mit Wand in den Fuß (kass_candidates), Dockzone liegt frei (nicht über Powerbank,
    Elektronik, V, anderen Docks) und in der Platte."""
    zone = dock_zone(dk)
    body = box(-dk["hw"], dk["y_slot"], dk["hw"], dk["yb"] + dk["hd"])
    pin = shapely.prepared.prep(inner)
    out, taken = list(kept), [d["zone"].buffer(1.0) for d in kept]
    for b in sorted([b for b in G.BUILDINGS if b["slug"] in cands], key=lambda b: len(cands[b["slug"]])):
        cs = cands[b["slug"]]
        if not cs:
            out.append(dict(slug=b["slug"], title=b["title"], ok=False, why="Kassette passt nicht in den Fuß"))
            continue
        pf = shapely.prepared.prep(unary_union([forbidden] + taken))
        found = None
        for _, phi, p in cs:
            z = poly_world(zone, phi, p)
            if pin.contains(z) and not pf.intersects(z):
                found = (phi, p, z)
                break
        if found is None:
            out.append(dict(slug=b["slug"], title=b["title"], ok=False, why="kein freier Platz für die Kabelnische"))
            continue
        phi, p, z = found
        taken.append(z.buffer(1.0))
        out.append(dict(slug=b["slug"], title=b["title"], ok=True, phi=phi, p=p, zone=z,
                        kass=poly_world(kass_rect(b["slug"]), phi, p), niche=[poly_world(w, phi, p) for w in dock_windows(dk)],
                        body=poly_world(body, phi, p)))
    order = {b["slug"]: i for i, b in enumerate(G.BUILDINGS)}
    return sorted(out, key=lambda d: order[d["slug"]])


def fixed_docks(fps, inner, dk, scale):
    """Docks an den vom Nutzer festgelegten Lagen (plug/scale1176/placements_<Maßstab>.json, von plug/campus.py gebaut).
    Die Lage (cx, cy, Winkel) bezieht sich auf die Mitte des Kassettenfußes; hier gilt der Ursprung der Pin-Reihe."""
    from plug import campus as CA
    places = json.load(open(CA.CACHE % scale))
    zone = dock_zone(dk)
    body = box(-dk["hw"], dk["y_slot"], dk["hw"], dk["yb"] + dk["hd"])
    out = []
    for b in G.BUILDINGS:
        pl = places[b["slug"]]
        yc = CA.foot_local(pl["var"], 0.0).centroid.y
        a = math.radians(pl["angle"])
        p = (pl["cx"] + yc * math.sin(a), pl["cy"] - yc * math.cos(a))
        w, dep = CA.shaft_size(pl["var"])
        z = poly_world(zone, pl["angle"], p)
        kass = poly_world(box(-w / 2, -dep / 2 - yc, w / 2, dep / 2 - yc), pl["angle"], p)
        out.append(dict(slug=b["slug"], title=b["title"], ok=bool(inner.contains(z)), why="Dockzone ragt aus der Platte", phi=pl["angle"],
                        p=p, zone=z, kass=kass, niche=[poly_world(body, pl["angle"], p)],
                        body=poly_world(body, pl["angle"], p), var=pl["var"]))
    return out


def fach_candidates(outline, hof_fp, avoid):
    """Fach an der Plattenkante (Anschlussseite an der Kante), entlang der Kante verschoben; nach Überdeckung mit dem Innenhof sortiert."""
    inner = outline.buffer(-PP.UK_WALL, join_style=2)
    x0, y0, x1, y1 = inner.bounds
    out = []
    for side, ang in (("W", 0), ("O", 180), ("S", 90), ("N", 270)):
        for sgn in (1, -1):
            lo, hi = (y0 + FACH_W / 2, y1 - FACH_W / 2) if side in "WO" else (x0 + FACH_W / 2, x1 - FACH_W / 2)
            if hi < lo:
                continue
            for c in np.arange(lo, hi + 0.01, 4.0):
                if side in "WO":
                    cx, cy = (x0 + FACH_L / 2 if side == "W" else x1 - FACH_L / 2), c
                else:
                    cx, cy = c, (y0 + FACH_L / 2 if side == "S" else y1 - FACH_L / 2)
                f = Frame(cx, cy, ang, sgn)
                fp = fach_parts(f)
                if not inner.buffer(1e-6).contains(fp["fach"]) or fp["fach"].intersects(avoid):
                    continue
                out.append((fp["body"].intersection(hof_fp).area, side, f))
    out.sort(key=lambda c: -c[0])
    return out


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


def unterkasten_cut(length, deck_cuts, avoid):
    """Schnitte des Unterkastens (y), versetzt zu denen der Oberplatte, nicht durch Fach, Elektronik, Aussparungen, Docks."""
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


def switch_cut(minx, miny, bot, h=H0):
    """Loch und Innentasche des Hauptschalters (Wippe KCD11) in der Westwand des Unterkastens, Rohkoordinaten der Platte.

    Maße vom Probeteil T2 (r9, bewährt): Loch `SW_HOLE` mit der Langseite waagerecht (entlang y), Wand am Loch `SW_WALL`, Innentasche
    Loch + `SW_POCKET_PAD`, oben mit 45°-Dach (keine Brücke). Mitte in der Höhe: halbe Wandhöhe; Lage entlang der Wand: `SW_Y` ab Südkante.
    Rückgabe: Schnittkörper und der Schalterraum (Kasten samt Pins und Draht) für die Kollisionsprüfung.
    """
    hy, hz = PP.SW_HOLE
    py, pz = hy + PP.SW_POCKET_PAD[0], hz + PP.SW_POCKET_PAD[1]
    yc, zc = miny + PP.SW_Y, bot + h["uk_t"] / 2
    x_out, x_in = minx, minx + PP.UK_WALL
    x_pocket = x_in - (PP.UK_WALL - PP.SW_WALL)            # Grund der Tasche: Wand am Loch SW_WALL
    z0, z1 = zc - pz / 2, zc + pz / 2
    roof = (x_in + 0.1) - x_pocket                          # 45°-Dach: oben um die Taschentiefe höher an der Innenseite
    hole = mbox(x_out - 0.1, x_in + 0.1, yc - hy / 2, yc + hy / 2, zc - hz / 2, zc + hz / 2)
    pocket = prism_y([(x_pocket, z0), (x_in + 0.1, z0), (x_in + 0.1, z1 + roof), (x_pocket, z1)], yc - py / 2, yc + py / 2)
    room = mbox(x_in, x_in + (SW_DEPTH - PP.UK_WALL), yc - 7.0, yc + 7.0, zc - 4.5, zc + 4.5)
    return dict(cut=G.union([hole, pocket]), room=room, y=PP.SW_Y, hole=PP.SW_HOLE, z=round(zc - bot, 2))


LAST = {}
SW_DEPTH = 20.0      # Schalter ab Außenfläche: Kasten 9 + Pins 7 + Lötstelle 4 (plug/power/build_plan_switch.py, DEPTH_OUT)


def variant(scale, h=H0, dk=DK):
    s = 1000.0 / scale
    G.FAST = True                              # Laser-Raster 0,6 m wie plug/campus.py (gleiche Grundrisse wie scale.md)
    m = G.source_models("laserscan", s)
    fps = {k: v[1] for k, v in m.items() if k in TP.CASSETTE}
    hof_solid, hof_fp, _ = innenhof.model(s, list(fps.values()), TP.HOF_DEPTH_T, TP.HOF_CLR_T)
    hof_cut = innenhof.flaeche_mm(list(fps.values()), s)      # Aussparung der Platte (ohne Fase oben), wie plug/campus.py
    sel = list(G.BUILDINGS)
    foot_fp = unary_union([fps[b["slug"]] for b in sel])
    outline = G.plate_outline(unary_union([foot_fp, hof_fp]))
    minx, miny, maxx, maxy = outline.bounds
    sh = (-minx, -miny)
    W, Ln = maxx - minx, maxy - miny
    deck_cuts = [round(float(c - miny), 1) for c in G.tile_cuts(outline, unary_union([foot_fp, hof_fp]))]
    inner = outline.buffer(-PP.UK_WALL, join_style=2)
    pocket_fp = hof_cut
    deck, bot, zf = h["deck"], h["uk_bot"], h["uk_bot"] + PP.UK_FLOOR

    mulden_poly = foot_fp.buffer(TP.OUTLINE_CLR_T)
    docks = fixed_docks(fps, inner.buffer(-0.5), dk, scale)     # alle Docks an den festgelegten Lagen; die Powerbank liegt unter dem Steckerraum
    dz = unary_union([d["zone"].buffer(1.0) for d in docks])
    vs = place_vs(outline, unary_union([mulden_poly.buffer(V["wall"]), pocket_fp.buffer(V["wall"]), dz]))
    notches = [v["notch"] for v in vs]
    v_zone = unary_union([n.buffer(1.0) for n in notches] + [v["foot"].buffer(1.0) for v in vs])
    n_possible = len(docks)
    best, sides = None, {}
    for ov, side_c, f_c in fach_candidates(outline, hof_fp, v_zone):      # Fach und Elektronik liegen unten, Docks stören nicht
        fp_c = fach_parts(f_c)
        elec_c = esp_c = None
        for sz in PP.ESP_BOXES:
            try:
                elec_c = place_box(inner.buffer(-1), unary_union([fp_c["fach"].buffer(4.0, join_style=2), v_zone]), fp_c["far"], sz, 2.0)
                esp_c = sz
                break
            except (TypeError, IndexError):
                continue
        if elec_c is None:
            continue
        if side_c not in sides:
            sides[side_c] = dict(ok=n_possible, fail=[], under_hof=round(ov / fp_c["body"].area * 100))
        if best is None or esp_c[0] > best[7][0]:
            best = (n_possible, side_c, f_c, fp_c, elec_c, docks, ov, esp_c)
    _, side, f, fp, elec, docks, _, esp = best

    # Stützen und Zapfen
    zones = [d["zone"].buffer(3) for d in docks if d["ok"]]
    free = inner.buffer(-PP.POST[0]).difference(unary_union([fp["fach"].buffer(3), elec.buffer(3)] +
                                                             [n.buffer(3) for n in notches] + zones))
    posts = []
    for x in np.arange(minx + PP.POST[1] / 2, maxx, PP.POST[1]):
        for y in np.arange(miny + PP.POST[1] / 2, maxy, PP.POST[1]):
            r = box(x - PP.POST[0] / 2, y - PP.POST[0] / 2, x + PP.POST[0] / 2, y + PP.POST[0] / 2)
            if free.contains(r):
                posts.append(r)
    no_pin = unary_union([mulden_poly, pocket_fp])       # Zapfenlöcher nur, wo über dem Loch Plattenmaterial steht (nicht unter Mulde und Hof)
    targets = [(minx + 0.3 * W, miny + 15), (maxx - 0.3 * W, maxy - 15)]
    for c in deck_cuts:
        for fx in (0.3, 0.7):
            for dy in (-12, 12):
                targets.append((minx + fx * W, miny + c + dy))
    pins = set()
    for tx, ty in targets:
        cand = [(math.hypot(r.centroid.x - tx, r.centroid.y - ty), i) for i, r in enumerate(posts)
                if i not in pins and not Point(r.centroid.x, r.centroid.y).buffer(PP.PIN_PLAN["d"] / 2 + 1.5).intersects(no_pin)]
        if cand:
            pins.add(min(cand)[1])

    # --- Gebäude mit Fußfase, Mulden mit Einführfase (wie Probestück) ---
    bld, mulden_cuts = {}, []
    for b in sel:                           # eine Ebene: voller Gebäudeumriss bis F, keine Stufen (scale.md, Korrektur 2)
        fp_b = fps[b["slug"]]
        bld[b["slug"]] = m[b["slug"]][0] + G.extrude(fp_b, -h["F"], 0.01)
        mulden_cuts.append(G.extrude(fp_b.buffer(TP.OUTLINE_CLR_T, join_style=2), -h["F"], 1.0))

    # --- Oberplatte = Steckplatte aus plug/campus.py (flache Unterseite 14,6, Pin-Löcher, Hof, Gravur), dazu V-Kanäle und Zapfenlöcher ---
    from plug import campus as CA
    plate_c = CA.build(scale)[0]
    t_plate = CA.plate_thickness(PP.stack_plan())
    pin_d = PP.PIN_PLAN["d"] + 2 * PP.PIN_PLAN["clr"]
    cuts = [v_solid(v, deck) for v in vs]
    for i in pins:
        c = posts[i].centroid
        circ = Point(c.x, c.y).buffer(pin_d / 2, 24)
        cuts += [G.extrude(circ, deck - 1, deck + PP.PIN_PLAN["h"] + 0.3), mouth_ch(circ, deck, PP.CH_BED)]
    ober = plate_c.translate([0, 0, -t_plate]) - G.union(cuts)

    # --- Unterkasten: Unterkante gefast, hohl, Stützen, Zapfen, Zaun, Eckaussparungen, Fenster (kein Anschlag: die Leiste ist aufgeklebt) ---
    shell = slab_ch(outline, bot, deck, PP.CH_BED) - G.extrude(outline.buffer(-PP.UK_WALL, join_style=2), zf, deck + 1)
    solids = [shell, G.extrude(fp["fence"], zf - 0.01, zf + PP.FENCE[1])]
    solids += [G.extrude(r, zf - 0.01, deck) for r in posts]
    solids += [pin_solid_at(posts[i].centroid, deck, PP.PIN_PLAN, PP.CH_PIN) for i in pins]
    holes = [G.extrude(n, bot - 1, deck + 2) for n in notches] + [mouth_ch(n, bot, PP.CH_BED) for n in notches] + \
            [G.extrude(fp["window"], zf, zf + PP.PB_T + 1.0)]
    uk = G.union(solids) - G.union(holes)
    sw = switch_cut(minx, miny, bot, h)
    uk = uk - sw["cut"]
    LAST["uk"], LAST["sh"] = uk, (-minx, -miny)           # für plug/power/check_switch.py
    sw_free = float(vol_int(sw["room"], uk)) < 0.05      # Schalterraum frei von Stützen, Zaun, Fach

    # --- Innenhof-Teil unten gefast ---
    env = slab_ch(hof_fp, -TP.HOF_DEPTH_T, 40.0, PP.CH_HOF)
    hof_c = m3d.Manifold.batch_boolean([hof_solid, env], m3d.OpType.Intersect)

    def dock_out(d):
        if not d["ok"]:
            return dict(slug=d["slug"], title=d["title"], ok=False, why=d["why"])
        return dict(slug=d["slug"], title=d["title"], ok=True, p=[d["p"][0] + sh[0], d["p"][1] + sh[1]], phi=round(d["phi"], 1),
                    kass=coords(d["kass"], sh)[0], zone=coords(d["zone"], sh)[0], body=coords(d["body"], sh)[0],
                    niche=[coords(n, sh)[0] for n in d["niche"]],
                    over_pb=round(d["zone"].intersection(fp["fach"]).area, 1), moved=bool(d.get("moved", True)), var=d.get("var", "v4"))

    uk_cuts = unterkasten_cut(Ln, deck_cuts, [affinity.translate(g, *sh) for g in [fp["fach"], elec] + notches] +
                              [affinity.translate(d["zone"], *sh) for d in docks if d["ok"]])
    mat = dict(ober=grams(ober), uk=grams(uk))
    print("Schalter: Loch %.1f × %.1f, Wand %.1f, Westwand y = %.1f, Mitte %.1f über dem Boden, Schalterraum frei: %s" % (*sw["hole"], PP.SW_WALL, sw["y"], sw["z"], sw_free), flush=True)
    print("1:%d Platte %.1f × %.1f × %.1f mm, Kante %s, Powerbank %d %% unter dem Hof, Stoß %s / %s, Material %s, Docks %s, V %s" % (
        scale, W, Ln, h["total"], side, fp["body"].intersection(hof_fp).area / fp["body"].area * 100, deck_cuts, uk_cuts, mat,
        ["%s%s" % (d["slug"][:2], "" if d["ok"] else "!") for d in docks],
        [(round(v["c"][0] - minx, 1), round(v["c"][1] - miny, 1), v["axis"]) for v in vs]), flush=True)
    widths = {b["slug"]: round(2 * max_inradius(fps[b["slug"]]), 1) for b in sel}
    return dict(
        key="s%d" % scale, widths=widths, sides=sides, n_possible=n_possible, cand={d["slug"]: 1 for d in docks}, scale=scale, plate=[round(W, 1), round(Ln, 1)], thick=round(h["total"], 1),
        outline=coords(outline, sh), deck_cuts=deck_cuts, uk_cuts=uk_cuts,
        buildings=[dict(slug=b["slug"], title=b["title"], poly=coords(fps[b["slug"]], sh),
                        h=round(float(G.to_trimesh(m[b["slug"]][0]).bounds[1][2]), 1)) for b in sel],
        hof=coords(hof_fp, sh), hof_w=round(hof_fp.area / (hof_fp.bounds[3] - hof_fp.bounds[1]), 1),
        hub=round(innenhof.hub(innenhof.load(), s), 2),
        fach_poly=coords(fp["fach"], sh), body=coords(fp["body"], sh), niche=coords(fp["niche"], sh),
        channel=coords(fp["channel"], sh), plug=coords(fp["plug"], sh),
        window=coords(fp["window"], sh), cable=[[p[0] + sh[0], p[1] + sh[1]] for p in fp["cable"]],
        elec=coords(elec, sh), esp=list(esp), posts=[dict(r=coords(r, sh)[0], pin=i in pins) for i, r in enumerate(posts)],
        vs=[dict(c=[v["c"][0] + sh[0], v["c"][1] + sh[1]], axis=v["axis"],
                 ent=[[p[0] + sh[0], p[1] + sh[1]] for p in v["ent"]], notch=coords(v["notch"], sh)[0]) for v in vs],
        docks=[dock_out(d) for d in docks], frame=dict(ang=f.ang, sgn=f.sgn, c=[f.c[0] + sh[0], f.c[1] + sh[1]]), side=side,
        under_hof=round(fp["body"].intersection(hof_fp).area / fp["body"].area * 100),
        hut=dict(size=PP.HUT, fits=bool(W <= PP.HUT and Ln <= PP.HUT), over=round((Ln - PP.HUT) / 2, 1)),
        section=section(outline, fps, hof_fp, f), material=mat, docks_ok=sum(1 for d in docks if d["ok"]),
        switch=dict(y=sw["y"], hole=list(sw["hole"]), wall=PP.SW_WALL, z=sw["z"], free=sw_free),
        meshes=dict(ober=mesh(ober, sh), uk=mesh(uk, sh), buildings={k: mesh(v, sh) for k, v in bld.items()},
                    hof=mesh(hof_c, sh)),
    )


def fit_rows(dk=DK):
    d = PP.stack_plan()
    pin = PP.PIN
    h = H0
    return [
        ["Gebäude in der Mulde", "eine Ebene: voller Gebäudeumriss mit Spiel %.2f je Seite, %.1f tief (4 mm tiefer als getestet), gerade Wand, "
         "keine Stufen, keine Fase oben" % (TP.OUTLINE_CLR_T, d["F"]), "ungetestet, Steckprobe 3",
         "plug/logbook/scale.md (Korrektur 2); Steckprobe 1 testete 10,2 mm mit Stufen"],
        ["Muldenboden über der Winkelleiste", "%.1f mm, Pinlöcher %.1f mit Fase %.2f, E %.2f" % (PP.CEIL, sd.HOLE, TB.HOLE_CH, d["E"]),
         "vorläufig", "r2 K, r3 S"],
        ["Winkelleiste in der Tasche", "Spiel %.1f, Tasche +%.1f zum Lötende, Stufe für 1,8" % (sd.SNUG_HDR, TP.BODY_EXT_T),
         "bewährt, Kippen offen", "r2 D, r3 W"],
        ["Halt der Winkelleiste von unten", "Steg unter dem Körper mit %.1f mm Luft, dazu Heißkleber" % PP.STAMP_AIR,
         "Vorschlag", "Plan Steckprobe 2, Karten D und K; L06, L21"],
        ["Kabel hinter den Lötenden", "Nische %.0f mm breit, %.0f mm lang ab Körpertasche (Schlitz bis %.1f), Decke %.1f über dem Bett, "
         "eine Nische ohne Stege (Support erlaubt); darunter Unterkasten %.1f mm frei" % (dk["niche_w"], dk["y_slot"] - dk["niche_end"], dk["slot_end"],
                                                          h["z_slot"] - h["z_bb"], h["uk_t"]),
         "Vorschlag", "L20, Nutzer Stand 4"],
        ["Oberplatte auf Unterkasten", "Zapfen Ø %.1f × %.1f mit Fase %.1f, Loch Ø %.1f (%.2f Gleitspiel), Fase %.1f am Bett" % (
            pin["d"], pin["h"], PP.CH_PIN, pin["d"] + 2 * pin["clr"], pin["clr"], PP.CH_BED), "Vorschlag", "L10 (0,15 gleitet)"],
        ["Faden", "V-Kanal Ø %.1f, Scheitel %.1f, %.0f° zur Waagerechten (Böschung %.1f, %.2f Überhang je Schicht), Trichter R %.1f, "
         "Wände ≥ %.1f" % (V["leg_d"], V["apex"], V_ANGLE, V["slope"], L * V["slope"], V["entry_r"], V["wall"]),
         "Vorschlag, flacher als Plan", "Plan Steckprobe 2 (53°), Nutzer Stand 4"],
        ["Powerbank im Zaun", "%.1f je Seite, %.1f Luft oben" % (PP.PB_CLR, PP.PB_CLR_Z), "geschätzt, ungemessen", "Fachprobe"],
        ["Stecker vor der Powerbank", "%.0f mm Steckerraum, Kabelkanal %.0f mm" % (PP.PB_PLUG, PP.PB_CABLE), "geschätzt, ungemessen", "Fachprobe"],
        ["Decken und Brücken", "Support ist erlaubt (Nutzer); trotzdem keine Löcher in dünnen Brücken ohne Support", "Regel", "L04, L05"],
    ]


def fasen_rows():
    """Fasen-Check: Kante, Fase, Stand im Modell, Herkunft."""
    c = PP.CH_BED
    return [
        ["Gebäudefuß unten (Bett)", "%.1f, 45°, Schichtstufen" % sd.CH_F, "Gebäude-Generator, noch nicht im Konzept", "scale.md (Gebäude um 4 mm verlängern: Hohlkörper-Chat)"],
        ["Mulde oben", "keine Fase und keine Stufen: gerade Wand, Spiel %.2f; so bleibt die Wand zum Hof 0,4 mm" % TP.OUTLINE_CLR_T, "im Modell",
         "scale.md (Korrektur 2), `plug/campus.py`"],
        ["Schachteingang im Fuß (Kassette, am Bett)", "%.1f Einführfase" % c, "Gebäude-Generator, noch nicht im Konzept", "Plan Steckprobe 2, L03"],
        ["Oberplatte, Außenkante unten (Bett)", "%.1f" % c, "im Modell", "L03"],
        ["Oberplatte, Mündungen am Bett: Körpertasche, Kabelnische, Zapfenlöcher", "%.1f" % c, "im Modell", "L02, L03"],
        ["Oberplatte, Pinlöcher im Muldenboden", "%.2f beidseitig, Böschung als Trichter" % TB.HOLE_CH, "im Modell (Platte B)", "L02, L05"],
        ["Oberplatte, V-Kanal am Bett", "Trichter R %.1f, selbst 45°" % V["entry_r"], "im Modell", "Plan Steckprobe 2"],
        ["Unterkasten, Außenkante unten (Bett)", "%.1f" % c, "im Modell", "L03"],
        ["Unterkasten, Eckaussparungen am Bett", "%.1f" % c, "im Modell", "L03"],
        ["Zentrierzapfen oben", "%.1f Einführfase" % PP.CH_PIN, "im Modell", "L10"],
        ["Innenhof-Teil unten (Bett)", "%.1f" % PP.CH_HOF, "im Konzept; `innenhof.py` hat sie noch nicht", "L03"],
        ["Stoßflächen beim Teilen (Bett)", "%.1f an den Schnittkanten" % PP.CH_HOF, "Generator-Aufgabe (`split_tiles`)", "L03"],
        ["Fenster in der Kante", "%.1f an den Mündungen" % c, "in der Fachprobe zu prüfen", "L02"],
    ]


def main():
    h, dk = H0, DK
    print("Höhen:", {k: round(v, 2) for k, v in h.items()})
    print("Dock:", {k: round(v, 2) for k, v in dk.items()})
    variants = [variant(sc, h, dk) for sc in PP.SCALES]
    data = dict(
        heights=h, dock=dk, variants=variants, scales=list(PP.SCALES), rec=1300,
        pb=dict(L=PP.PB_L, W=PP.PB_W, T=PP.PB_T, g=PP.PB_G, wh=PP.PB_WH, imax=PP.PB_IMAX, sleep=PP.PB_SLEEP_S,
                keep=PP.PB_KEEP_MA, ports=PP.PB_PORTS, port_v=PP.PB_PORT_V, clr=PP.PB_CLR, clr_z=PP.PB_CLR_Z, plug=PP.PB_PLUG,
                cable=PP.PB_CABLE),
        fach=dict(L=FACH_L, W=FACH_W, H=FACH_H, u0=U0, bu0=BU0, bv0=BV0, kv0=KV0, win=WIN),
        uk=dict(floor=PP.UK_FLOOR, wall=PP.UK_WALL, fence=PP.FENCE, post=PP.POST, pin=PP.PIN, anschlag=PP.ANSCHLAG),
        v=V, v_hs=V_HS, v_angle=round(V_ANGLE, 1),
        v_plan2=dict(PP.V_PLAN2, angle=round(math.degrees(math.atan2(1.0, PP.V_PLAN2["slope"])), 1)),
        niche=PP.NICHE, ch=dict(bed=PP.CH_BED, foot=sd.CH_F, pocket=sd.CH_P, hof=PP.CH_HOF, pin=PP.CH_PIN),
        hut=PP.HUT, esp=PP.ESP_BOX, esp_boxes=[list(b) for b in PP.ESP_BOXES], bed=PP.BED, mat=dict(shell=PP.SHELL, infill=PP.INFILL, pla=PP.PLA),
        fits=fit_rows(dk), fasen=fasen_rows(),
    )
    tpl = open(TEMPLATE, encoding="utf-8").read()
    html = tpl.replace("/*DATA*/", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    open(OUT, "w", encoding="utf-8").write(html)
    print("geschrieben:", os.path.relpath(OUT, ROOT), "(%.1f MB)" % (len(html) / 1e6))


if __name__ == "__main__":
    main()
