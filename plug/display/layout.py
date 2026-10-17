"""Lage des Display-Gebäudes auf der Grundplatte (1:1300): Grundrisse der Entwürfe, freie Fläche, Kandidaten, Sichtlinie.

Koordinaten wie `plug.power.build_concept.variant`: x nach Osten, y nach Norden, Ursprung Südwestecke der Platte. Das Display zeigt immer nach
Osten (+x), die Lötenden des Docks nach Westen (−x), die Stele hat die Breite in y.
"""
import math

import numpy as np
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

from plug.display import params as D
from plug.power import build_concept as BC

BELOW_WINDOW = D.DISP["pcb_h"] - D.DISP["aa_top"] - D.DISP["aa_h"] - D.WINDOW_MARGIN     # Platine unter dem Sichtfenster (ungenutzt)
WIN_H = D.DISP["aa_h"] + 2 * D.WINDOW_MARGIN

# Entwürfe: Mulde (Fuß) als Rechteck Breite × Tiefe, Lage der Pin-Reihe von der Ostkante der Mulde nach Westen
W_FOOT = D.DISP["pcb_w"] + 2 * (D.CLR + D.WALL)                      # 30,3
SLAB = D.WALL + D.CLR + D.DISP["mod_t"] + D.CLR + D.BACK              # Wand vorn + Spiel + Modul + Spiel + Rückwand
KD = D.KASS_D + 2 * D.WALL                                            # Kassettenfuß mit Wand in x-Richtung (Tiefe)
DESIGNS = {
    "E1": dict(name="Stele kompakt", depth=max(SLAB, KD), pin_from_east=max(SLAB, KD) / 2),
    "E2": dict(name="Display vorn, Block dahinter", depth=SLAB + D.CAVITY + KD, pin_from_east=SLAB + D.CAVITY + KD / 2),
    "E3": dict(name="Pult, 15° geneigt", depth=SLAB + D.CAVITY + KD, pin_from_east=SLAB + D.CAVITY + KD / 2),
    # Rückfall E2 mit aufgestecktem Dupont-Gehäuse auf der Pinleiste statt direkt angelöteter Adern (Kabelraum etwa 17 mm); nur für den Vergleich
    "E2D": dict(name="E2 mit Dupont-Buchse am Display", depth=SLAB + D.CAVITY_DUPONT + KD, pin_from_east=SLAB + D.CAVITY_DUPONT + KD / 2),
}
for d in DESIGNS.values():
    d["w"] = W_FOOT
DESIGNS["E3"]["depth"] += (D.DISP["pcb_h"] - BELOW_WINDOW) * math.tan(math.radians(D.TILT_DEG))
DESIGNS["E3"]["pin_from_east"] = DESIGNS["E3"]["depth"] - KD / 2


def module_bottom_z(design):
    """Unterkante der Platine über (+) bzw. unter (−) der Plattenoberfläche. E1: Modul steht auf der Kassette; E2/E3: das untere,
    ungenutzte Drittel der Platine steckt im Fuß, das Sichtfenster beginnt GAP_FRONT über der Platte."""
    if design == "E1":
        return D.KASS_TOP + 1.2
    if design == "E3":
        return D.GAP_FRONT - BELOW_WINDOW * math.cos(math.radians(D.TILT_DEG))
    return D.GAP_FRONT - BELOW_WINDOW


def window_z(design):
    """Höhe der Mitte des Sichtfensters über der Plattenoberfläche."""
    k = math.cos(math.radians(D.TILT_DEG)) if design == "E3" else 1.0
    return module_bottom_z(design) + (BELOW_WINDOW + WIN_H / 2) * k


def module_top_z(design):
    return module_bottom_z(design) + D.DISP["pcb_h"]


def rect_for(design, xe, yc):
    """Mulde der Stele mit Ostkante xe, Mitte yc."""
    d = DESIGNS[design]
    return box(xe - d["depth"], yc - d["w"] / 2, xe, yc + d["w"] / 2)


def zone_for(design, xe, yc, tail="W"):
    """Dockzone (Platz unter der Platte, in dem keine Stütze steht): Lötenden und Draht nach Westen (W) oder Osten (E).
    Die Pin-Reihe läuft immer quer zur Blickrichtung, also zeigen die Lötenden nur nach W oder E."""
    d = DESIGNS[design]
    xp = xe - d["pin_from_east"]
    zb = BC.dock_zone().bounds          # lokal: x ± hw+2, y von y_tail − 4 bis y_front + 2; Lötenden zeigen nach −y
    hw = (zb[2] - zb[0]) / 2
    if tail == "W":
        return box(xp + zb[1], yc - hw, xp + zb[3], yc + hw), xp
    return box(xp - zb[3], yc - hw, xp - zb[1], yc + hw), xp


class Plate:
    def __init__(self, v):
        self.v = v
        P = lambda r: Polygon(r[0] if isinstance(r[0][0], list) else r)
        self.outline = P(v["outline"])
        self.buildings = {b["slug"]: dict(poly=P(b["poly"]), h=b["h"], title=b["title"]) for b in v["buildings"]}
        self.hof = P(v["hof"])
        self.fach = P(v["fach_poly"])
        self.elec = P(v["elec"])
        self.notches = [P([v_ for v_ in n]) if isinstance(n[0][0], (int, float)) else P(n[0]) for n in [x["notch"] for x in v["vs"]]]
        self.zones = [P(d["zone"]) for d in v["docks"] if d["ok"]]
        minx, miny, maxx, maxy = self.outline.bounds
        self.bounds = (minx, miny, maxx, maxy)
        self.inner = self.outline.buffer(-D.EDGE, join_style=2)
        self.dock_inner = self.outline.buffer(-2.4 - 0.5, join_style=2)       # Unterkastenwand 2,4
        mulden = unary_union([b["poly"].buffer(0.1) for b in self.buildings.values()] + [self.hof])
        self.mulden = mulden
        self.blocked = unary_union([mulden.buffer(D.WALL_MULDE), box(minx, miny, maxx, miny + D.LABEL_Y)] +
                                   [n.buffer(D.V_PAD) for n in self.notches])
        self.zones_all = unary_union([z.buffer(1.0) for z in self.zones])

    def check(self, design, xe, yc):
        """Prüft Mulde und Dockzone (Lötenden nach Westen, sonst nach Osten); liefert (ok, Meldungen, Richtung der Lötenden)."""
        r = rect_for(design, xe, yc)
        base = []
        if not self.inner.contains(r):
            base.append("Mulde zu nah an der Plattenkante")
        if r.intersects(self.blocked):
            base.append("Mulde stößt an Gebäude, Hof, Schrift oder Fadenkerbe")
        notch = unary_union([n.buffer(1.0) for n in self.notches])
        first = None
        for tail in ("W", "E"):
            z, _ = zone_for(design, xe, yc, tail)
            why = list(base)
            if not self.dock_inner.contains(z):
                why.append("Dockzone ragt aus der Platte")
            if z.intersects(self.zones_all):
                why.append("Dockzone überlappt ein anderes Dock")
            if z.intersects(notch):
                why.append("Dockzone an der Fadenkerbe")
            if not why:
                return True, [], tail
            first = first or why
        return False, first, None

    def under_other_mulde(self, design, xe, yc, tail="W"):
        z, _ = zone_for(design, xe, yc, tail)
        return z.intersection(self.mulden.buffer(-0.01)).area

    def feasible_map(self, design, step=1.0):
        """Alle möglichen (xe, yc) auf einem Raster."""
        minx, miny, maxx, maxy = self.bounds
        pts = []
        for xe in np.arange(minx + D.EDGE, maxx - D.EDGE + 0.01, step):
            for yc in np.arange(miny + D.EDGE, maxy - D.EDGE + 0.01, step):
                if self.check(design, float(xe), float(yc))[0]:
                    pts.append((round(float(xe), 2), round(float(yc), 2)))
        return pts

    def sight(self, design, xe, yc):
        """Kleinster Blickwinkel (Grad über der Waagerechten, aus Osten), unter dem die Mitte des Sichtfensters ganz frei zu sehen ist,
        und die Gebäude, die davor stehen. Strahlen vom Fenster nach Osten über die ganze Breite des Fensters (y ± aa_w/2).
        Gebäudehöhe = höchster Punkt des Gebäudes (konservativ)."""
        zw = window_z(design)
        worst, blockers = 0.0, set()
        for dy in np.linspace(-D.DISP["aa_w"] / 2, D.DISP["aa_w"] / 2, 5):
            ray = box(xe, yc + dy - 0.05, self.bounds[2] + 1, yc + dy + 0.05)
            for slug, b in self.buildings.items():
                inter = b["poly"].intersection(ray)
                if inter.is_empty:
                    continue
                dist = max(inter.bounds[0] - xe, 0.5)
                ang = math.degrees(math.atan2(b["h"] - zw, dist))
                if ang > 0:
                    worst = max(worst, ang)
                    blockers.add(slug)
        return round(worst, 1), sorted(blockers)

    def behind(self, design, xe, yc):
        """Gebäude, die hinter dem Display (nach Westen) in dessen Breite liegen, von Ost nach West sortiert."""
        d = DESIGNS[design]
        ray = box(self.bounds[0], yc - d["w"] / 2, xe - d["depth"], yc + d["w"] / 2)
        out = []
        for slug, b in self.buildings.items():
            if b["poly"].intersects(ray):
                out.append((b["poly"].intersection(ray).bounds[2], slug))
        return [s for _, s in sorted(out, reverse=True)]

    def in_front_of(self, design, xe, yc):
        """Gebäude, deren Ostseite das Display verdeckt (östlich in der Breite des Displays)."""
        d = DESIGNS[design]
        ray = box(xe, yc - d["w"] / 2, self.bounds[2] + 1, yc + d["w"] / 2)
        return [s for s, b in self.buildings.items() if b["poly"].intersects(ray)]

    def nearest(self, design, anchor, pts):
        if not pts:
            return None
        return min(pts, key=lambda p: math.hypot(p[0] - anchor[0], p[1] - anchor[1]))


# Anker der Lagen (Mitte der Ostkante der Mulde ungefähr dort); die Suche nimmt den nächsten freien Punkt
ANCHORS = {
    "A": dict(name="Südost, am Südrand bei der Beschriftung", anchor=(112.0, 20.0)),
    "B": dict(name="Südost, Ostrand Mitte", anchor=(112.0, 42.0)),
    "C": dict(name="Südwest, links neben der Beschriftung", anchor=(10.0, 20.0)),
    "D": dict(name="Nordost-Ecke", anchor=(112.0, 195.0)),
    "E": dict(name="Ostrand zwischen Hochhaus und Neuem Augusteum", anchor=(112.0, 100.0)),
}


def candidates(plate):
    """Je Lage und Entwurf: nächster freier Punkt, Sichtlinie, Gebäude davor/dahinter, Kabelweg zum ESP-Feld."""
    ex = plate.elec.centroid
    out = {}
    maps = {e: plate.feasible_map(e) for e in DESIGNS}
    for k, a in ANCHORS.items():
        row = {}
        for e in DESIGNS:
            p = plate.nearest(e, a["anchor"], maps[e])
            if p is None or math.hypot(p[0] - a["anchor"][0], p[1] - a["anchor"][1]) > 14:
                near = plate.nearest(e, a["anchor"], maps[e])
                row[e] = dict(ok=False, near=near, why=_why(plate, e, a["anchor"]))
                continue
            xe, yc = p
            tail = plate.check(e, xe, yc)[2]
            z, xp = zone_for(e, xe, yc, tail)
            ang, blockers = plate.sight(e, xe, yc)
            row[e] = dict(ok=True, xe=xe, yc=yc, xp=round(xp, 1), tail=tail, sight=ang, blockers=blockers,
                          behind=plate.behind(e, xe, yc), front=plate.in_front_of(e, xe, yc),
                          to_esp=round(math.hypot(xp - ex.x, yc - ex.y), 0), under=round(plate.under_other_mulde(e, xe, yc, tail), 1),
                          edge=round(plate.bounds[2] - xe, 1), wz=window_z(e), mb=module_bottom_z(e))
        out[k] = dict(a, **{"row": row})
    return out, maps


def _why(plate, design, anchor):
    xe, yc = anchor
    xe = min(max(xe, plate.bounds[0] + D.EDGE + DESIGNS[design]["depth"]), plate.bounds[2] - D.EDGE)
    return plate.check(design, xe, yc)[1]


EAST_XE = 111.5            # Ostkante der Mulde: 4,1 mm von der Plattenkante (Rasterpunkt der Suche)
SW_YC, NE_YC = 37.5, 195.0


def entry(plate, design, xe, yc):
    ok, why, tail = plate.check(design, xe, yc)
    out = dict(xe=xe, yc=yc, ok=ok, why=why, tail=tail)
    ex = plate.elec.centroid
    t = tail or "W"
    z, xp = zone_for(design, xe, yc, t)
    out.update(xp=round(xp, 1), zone=[round(c, 1) for c in z.bounds], to_esp=round(math.hypot(xp - ex.x, yc - ex.y)),
               behind=plate.behind(design, xe, yc))
    out["sight"], out["blockers"] = plate.sight(design, xe, yc)
    out["under"] = round(plate.under_other_mulde(design, xe, yc, t), 1)
    return out


def scan(plate, designs=("E1", "E2", "E3", "E2D")):
    """Am Ostrand von Süd nach Nord (Schieber) plus die beiden Lagen, nach denen gefragt wurde (Südwest-Ecke, Nordost-Ecke)."""
    out = {}
    for e in designs:
        d = DESIGNS[e]
        ost = [entry(plate, e, EAST_XE, float(y)) for y in range(20, 111)]
        sw = entry(plate, e, plate.bounds[0] + D.EDGE + d["depth"], SW_YC)
        ne = entry(plate, e, EAST_XE, NE_YC)
        iv = []
        for r in ost:
            if r["ok"]:
                if iv and r["yc"] - iv[-1][1] <= 1.01:
                    iv[-1][1] = r["yc"]
                else:
                    iv.append([r["yc"], r["yc"]])
        out[e] = dict(ost=ost, sw=sw, ne=ne, intervals=iv, depth=round(d["depth"], 1), w=round(d["w"], 1),
                      win_z=round(window_z(e), 1), mod_b=round(module_bottom_z(e), 1),
                      win_bottom=round(module_bottom_z(e) + BELOW_WINDOW * (math.cos(math.radians(D.TILT_DEG)) if e == "E3" else 1), 1),
                      top=round(module_bottom_z(e) + D.DISP["pcb_h"] * (math.cos(math.radians(D.TILT_DEG)) if e == "E3" else 1) + D.WALL, 1))
    return out
