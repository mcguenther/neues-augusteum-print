"""Lage des Körpers E4 (Kopf über der Platte, Hals in der Mulde) auf der Platte 1:1300.

Der Kopf liegt in der Luft über der Platte (ab 0,3 mm), also gilt für ihn derselbe Abstand zu Gebäuden, Hof und Schrift wie für ein Gebäude;
in die Platte taucht nur der Hals (Mulde 15,8 × 8,2 mm). Koordinaten wie `layout` (x nach Osten, y nach Norden, Ursprung Südwestecke).
"""
import math

from shapely.geometry import Polygon, box
from shapely.ops import unary_union

from plug.display import body4
from plug.display import layout as L
from plug.display import params as D

AIR_MARGIN = 1.5            # Abstand des Körpers zu Gebäuden und Hof (Luft), Kopf und Keil
D4 = body4.dims()


def env_at(xe, yc):
    return Polygon([(xe + x, yc + y) for x, y in body4.profile_plan(D4)])


def mulde_at(xe, yc):
    return box(xe + D4["x_bw"] - 0.1, yc - D4["NW"] / 2 - 0.1, xe + D4["x_be"] + 0.1, yc + D4["NW"] / 2 + 0.1)


def zone_at(xe, yc, tail="W"):
    xp = xe - D4["pe"]
    zb = L.BC.dock_zone().bounds
    hw = (zb[2] - zb[0]) / 2
    if tail == "W":
        return box(xp + zb[1], yc - hw, xp + zb[3], yc + hw), xp
    return box(xp - zb[3], yc - hw, xp - zb[1], yc + hw), xp


class Plate4(L.Plate):
    def __init__(self, v):
        super().__init__(v)
        minx, miny, maxx, maxy = self.bounds
        self.air_blocked = unary_union([b["poly"].buffer(AIR_MARGIN) for b in self.buildings.values()] + [self.hof.buffer(AIR_MARGIN),
                                        box(minx, miny, maxx, miny + D.LABEL_Y)] + [n.buffer(D.V_PAD) for n in self.notches])
        self.notch1 = unary_union([n.buffer(1.0) for n in self.notches])

    def check4(self, xe, yc):
        env, mu = env_at(xe, yc), mulde_at(xe, yc)
        base = []
        if not self.inner.contains(env):
            base.append("Körper zu nah an der Plattenkante")
        if env.intersects(self.air_blocked):
            base.append("Körper stößt an Gebäude, Hof, Schrift oder Fadenkerbe")
        if mu.intersects(self.mulden.buffer(D.WALL_MULDE)):
            base.append("Mulde des Halses stößt an eine andere Mulde")
        first = None
        for tail in ("W", "E"):
            z, _ = zone_at(xe, yc, tail)
            why = list(base)
            if not self.dock_inner.contains(z):
                why.append("Dockzone ragt aus der Platte")
            if z.intersects(self.zones_all):
                why.append("Dockzone überlappt ein anderes Dock")
            if z.intersects(self.notch1):
                why.append("Dockzone an der Fadenkerbe")
            if not why:
                return True, [], tail
            first = first or why
        return False, first, None

    def behind4(self, xe, yc):
        env = env_at(xe, yc)
        ray = box(self.bounds[0], yc - D4["W"] / 2, xe + D4["x_bw"], yc + D4["W"] / 2)
        out = [(b["poly"].intersection(ray).bounds[2], s) for s, b in self.buildings.items() if b["poly"].intersects(ray)]
        return [s for _, s in sorted(out, reverse=True)]


def scan4(plate, xe=L.EAST_XE):
    ost = []
    ex = plate.elec.centroid
    for y in range(20, 111):
        ok, why, tail = plate.check4(xe, float(y))
        ost.append(dict(yc=float(y), ok=ok, why=why, tail=tail))
    iv = []
    for r in ost:
        if r["ok"]:
            if iv and r["yc"] - iv[-1][1] <= 1.01:
                iv[-1][1] = r["yc"]
            else:
                iv.append([r["yc"], r["yc"]])
    return dict(ost=ost, intervals=iv)
