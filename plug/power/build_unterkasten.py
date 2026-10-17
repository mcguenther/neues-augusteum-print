#!/usr/bin/env python3
"""Unterkasten (Batteriefach) Stand 7 und Distanzplatten: STL, README, ZIP, Prüfbericht und Bilder nach stl/steckmodul_unterkasten/.

Teile (Druckausrichtung, Boden auf dem Bett):
  U_unterkasten.stl        Kasten 115,6 × 220,8 × 17,6 mm (mit Zapfen 20,1), hohl, ohne Zaun, mit Stützen, Zapfen, Eckaussparungen, Fenster, Schalterloch
  U_oberplatte.stl         Oberplatte (Steckplatte aus plug.campus) mit Faden-V an den vier Ecken und Zapfenlöchern, Unterseite flach auf das Bett
  U_distanz_3_4/3_6/3_8    Distanzplatte 20 × 20 mm, 3,4 / 3,6 / 3,8 mm dick (Luft über der Powerbank 3,6 bei 12,8 mm Dicke)
Die Distanzplatte liegt auf der Powerbank an einer Stelle ohne Dockzone, Adern und Zapfenloch und klemmt sie gegen die Oberplatte.
Geometrie: plug/power/build_concept.py (variant), Stand und Werte wie plug/power/batteriefach.html.
Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m plug.power.build_unterkasten
"""
import math
import os
import zipfile

import numpy as np
from shapely.geometry import Point, Polygon, box as sbox
from shapely.ops import unary_union

from plug.fit_test.generator import overhangs
from plug.geom import box, to_bed, to_tm, vol_int
from plug.power import build_batteriefach as BB
from plug.power import build_concept as BC
from plug.power import params as PP

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(HERE, "stl", "steckmodul_unterkasten")
PREV = os.path.join(HERE, "vorschau", "steckmodul_unterkasten")
SIDE = 20.0                      # Distanzplatte 20 × 20
THICK = (3.4, 3.6, 3.8)          # Dicken; 3,6 füllt die Luft über der Powerbank genau
CH = PP.CH_BED                   # Bettkante 0,5


class Report:
    def __init__(self):
        self.lines = []

    def __call__(self, s=""):
        print(s)
        self.lines.append(s)


def _rings(rs):
    return unary_union([Polygon(r) for r in rs])


def wires(v):
    """Adern der Docks als Linienzug in der Draufsicht (wie in plug/power/batteriefach.html), je Dock vier nebeneinander."""
    eb = _rings(v["elec"]).bounds
    out = []
    for d in v["docks"]:
        if not d["ok"]:
            continue
        a = math.radians(d["phi"])
        ux, uy, vx, vy = math.cos(a), math.sin(a), -math.sin(a), math.cos(a)
        loc = lambda x, y: (d["p"][0] + ux * x + vx * y, d["p"][1] + uy * x + vy * y)  # noqa: E731
        tx = min(eb[2] - 3, max(eb[0] + 3, d["p"][0]))
        ty = min(eb[3] - 3, max(eb[1] + 3, d["p"][1]))
        for k, lx in enumerate((-3.81, -1.27, 1.27, 3.81)):
            a0, a1 = loc(lx, BC.DK["y_tail"]), loc(lx * 1.2, BC.DK["y_tail"] - 3)
            dx, dy = tx - a1[0], ty - a1[1]
            n = math.hypot(dx, dy) or 1.0
            off = (k - 1.5) * 1.1
            px, py = -dy / n * off, dx / n * off
            out.append([a0, a1, (a1[0] + dx * 0.5 + px, a1[1] + dy * 0.5 + py), (tx + px, ty + py)])
    return out


def place_spacer(v):
    """Mitte der Distanzplatte: auf der Powerbank, frei von Dockzonen, Adern, Zapfenlöchern, Aussparungen; möglichst nah an der Mitte."""
    body = _rings(v["body"])
    keep = [Polygon(d["zone"]).buffer(1.0) for d in v["docks"] if d["ok"]]
    keep += [LS.buffer(2.5) for LS in (__import__("shapely").LineString(w) for w in wires(v))]
    keep += [Polygon(x["notch"]).buffer(1.0) for x in v["vs"]]
    keep += [Polygon(p["r"]).centroid.buffer(PP.PIN_PLAN["d"] / 2 + 2.0) for p in v["posts"] if p["pin"]]
    keep = unary_union(keep)
    area = body.buffer(-2.0)
    c = body.centroid
    x0, y0, x1, y1 = body.bounds
    best = None
    for x in np.arange(x0, x1, 1.0):
        for y in np.arange(y0, y1, 1.0):
            r = sbox(x - SIDE / 2, y - SIDE / 2, x + SIDE / 2, y + SIDE / 2)
            if area.contains(r) and not r.intersects(keep):
                d = math.hypot(x - c.x, y - c.y)
                if best is None or d < best[0]:
                    best = (d, x, y, r)
    if best is None:
        raise SystemExit("keine freie Stelle für die Distanzplatte")
    return best[1], best[2], best[3], keep, body


def spacer(t):
    sq = sbox(-SIDE / 2, -SIDE / 2, SIDE / 2, SIDE / 2)
    return BC.slab_ch(sq, 0.0, t, CH)


def main():
    rep = Report()
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(PREV, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith((".stl", ".zip", ".txt")):
            os.remove(os.path.join(OUT, f))
    v = BB.final_variant()
    v.pop("meshes")
    h = BC.H0
    sh = BC.LAST["sh"]
    uk = BC.LAST["uk"].translate([sh[0], sh[1], 0])           # Plattenmitte an (0, 0)-Ecke, z: Oberplatte-Unterseite = h["deck"]
    zf = h["uk_bot"] + PP.UK_FLOOR
    pb_t = PP.PB_T + PP.PB_T_ZUSCHLAG
    z_top_pb = zf + pb_t
    gap = h["deck"] - z_top_pb
    x, y, r, keep, body = place_spacer(v)
    rep("Unterkasten Stand 7: Platte %.1f × %.1f, Kasten %.1f hoch (Boden %.1f, innen %.1f), Powerbank %.1f dick (12,6 + Zuschlag %.1f), Luft darüber %.2f" % (
        v["plate"][0], v["plate"][1], h["uk_t"], PP.UK_FLOOR, h["uk_t"] - PP.UK_FLOOR, pb_t, PP.PB_T_ZUSCHLAG, gap))
    rep("Distanzplatte %.0f × %.0f auf der Powerbank bei x = %.0f, y = %.0f (Rohkoordinaten der Platte, Süden y = 0)" % (SIDE, SIDE, x, y))
    ober = BC.LAST["ober"].translate([sh[0], sh[1], 0])
    parts = {"U_unterkasten": to_bed(uk), "U_oberplatte": to_bed(ober)}
    for t in THICK:
        parts["U_distanz_%s" % str(t).replace(".", "_")] = spacer(t)
    rep("\nTeile (Druckausrichtung, Bett z = 0):")
    info = {}
    for name, man in parts.items():
        tm = to_tm(man)
        tm.export(os.path.join(OUT, name + ".stl"))
        g, nl = BC.grams(man)[0], int(round(tm.extents[2] / 0.2))      # Schätzung wie im Konzept (1 mm Hülle, 15 %% Füllung); Voxelmodell wäre für den Kasten zu groß
        ov = overhangs(man, name)
        info[name] = dict(g=g, layers=nl)
        rep("  %-18s %6.1f × %6.1f × %5.1f mm  %6.1f cm³  ≈ %5.1f g  dicht=%s" % (name + ".stl", *tm.extents, tm.volume / 1000.0, g, tm.is_watertight))
        rep("      waagerechte Decken: %s   Überhang flacher als 45° zur Senkrechten: %.0f mm²" % (
            "; ".join("z=%.1f: %.0f mm² (%.1f × %.1f)" % f for f in sorted(ov["flat"], key=lambda t: -t[1])[:5]) or "keine", ov["steep_area"]))

    rep("\nPrüfung (Überschneidungsvolumen, mm³; muss 0 sein):")
    bad = 0

    def chk(txt, val, limit=0.05):
        nonlocal bad
        ok = val <= limit
        bad += (not ok)
        rep("  %-78s %8.3f  %s" % (txt, val, "ok" if ok else "KOLLISION"))

    import shapely
    b = body.bounds
    pb = box(b[0], b[2], b[1], b[3], zf, zf + pb_t)
    chk("Powerbank (%.1f dick) im Kasten" % pb_t, vol_int(pb, uk))
    chk("Kasten und Oberplatte (Zapfen in den Zapfenlöchern, Kasten liegt auf)", vol_int(uk, ober))
    for t in THICK:
        sp = parts["U_distanz_%s" % str(t).replace(".", "_")].translate([x, y, z_top_pb])
        chk("Distanzplatte %.1f auf der Powerbank, Kasten" % t, vol_int(sp, uk))
        chk("Distanzplatte %.1f und Powerbank (liegt nur auf)" % t, vol_int(sp, pb))
        rep("      Luft über der Platte bis zur Oberplatte: %+.2f mm (%s)" % (gap - t, "Spiel" if gap - t > 1e-6 else ("bündig" if abs(gap - t) < 1e-6 else "Pressung")))
    dist_dock = r.distance(unary_union([Polygon(d["zone"]) for d in v["docks"] if d["ok"]]))
    dist_wire = min(r.distance(shapely.LineString(w)) for w in wires(v))
    pins = [Polygon(p["r"]).centroid for p in v["posts"] if p["pin"]]
    rep("  Abstand der Distanzplatte: Dockzone %.1f mm, nächste Ader %.1f mm, Zapfenloch %.1f mm, Rand der Powerbank %.1f mm" % (
        dist_dock, dist_wire, min(r.distance(p) for p in pins) - (PP.PIN_PLAN["d"] / 2 + PP.PIN_PLAN["clr"]), body.exterior.distance(r)))
    if dist_dock < 0.5 or dist_wire < 0.5:
        bad += 1
    rep("  -> %s" % ("keine Kollisionen" if not bad else "%d Fehler!" % bad))

    from plug.roadmap import build as rb
    for prof, pr in rb.PROFILE.items():
        mins = (info["U_unterkasten"]["g"] / pr["rate"] * 60.0 + info["U_unterkasten"]["layers"] * pr["layer"] / 60.0) + pr["start"]
        rep("Kasten allein: Material ≈ %.0f g, Zeit %s ≈ %.1f h" % (info["U_unterkasten"]["g"], prof, mins / 60.0))
    rep("Bei deinem Drucker (Nacht 1: 47 g in 2,5 h) ≈ %.1f h" % (info["U_unterkasten"]["g"] / 47.0 * 2.5))
    with open(os.path.join(OUT, "pruefbericht.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(rep.lines) + "\n")
    plan_png(v, r, keep, body)
    write_readme(info, x, y, gap)
    zpath = os.path.join(OUT, "unterkasten.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(os.listdir(OUT)):
            if f.endswith(".stl") or f == "README.txt":
                z.write(os.path.join(OUT, f), f)
    rep("%s: %.0f kB" % (os.path.relpath(zpath, HERE), os.path.getsize(zpath) / 1024))
    return bad


def plan_png(v, r, keep, body):
    """Draufsicht: Kasten, Powerbank, Dockzonen, Adern, Distanzplatte."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import shapely
    fig, ax = plt.subplots(figsize=(5.2, 9.2), dpi=130)
    poly = lambda g, **kw: [ax.fill(*p.exterior.xy, **kw) for p in getattr(g, "geoms", [g])]  # noqa: E731
    poly(_rings(v["outline"]), fc="#dfe4ea", ec="#1b2220", lw=1.2)
    poly(body, fc="#fbfbf8", ec="#1b2220", lw=1.0)
    for d in v["docks"]:
        if d["ok"]:
            poly(Polygon(d["zone"]), fc="#d97a1f", alpha=0.3, ec="#d97a1f")
    for w in wires(v):
        ax.plot(*zip(*w), color="#c8423b", lw=0.7)
    for p in v["posts"]:
        poly(Polygon(p["r"]), fc="#5f7086", ec="#1b2220", lw=0.6)
    for xx in v["vs"]:
        poly(Polygon(xx["notch"]), fc="#c8423b", alpha=0.5)
    poly(_rings(v["elec"]), fc="#2f7d4f", alpha=0.25, ec="#2f7d4f")
    poly(r, fc="#2f7d4f", ec="#1b2220", lw=1.4)
    ax.annotate("20 × 20", (r.centroid.x, r.centroid.y), ha="center", va="center", color="white", fontsize=7, weight="bold")
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("Unterkasten von oben (Norden oben): Distanzplatte auf der Powerbank", fontsize=8)
    fig.savefig(os.path.join(PREV, "distanzplatte_lage.png"), bbox_inches="tight")
    plt.close(fig)


def write_readme(info, x, y, gap):
    txt = """UNTERKASTEN (BATTERIEFACH) UND DISTANZPLATTEN, Stand 7
=======================================================
Plattenmaß 115,6 x 220,8 mm (1:1300), Kasten 17,6 mm hoch. Ohne Zaun um die Powerbank, mit Stützen, Zapfen, Eckaussparungen,
Fenster in der Nordkante (oben offen, keine Brücke) und Schalterloch in der Westwand. Übersicht: plug/power/batteriefach.html

Teile:
  U_unterkasten.stl     Kasten, Boden auf das Bett, kein Support nötig (siehe pruefbericht.txt)   ca. %(k).0f g
  U_oberplatte.stl      Oberplatte mit Faden-V und Zapfenlöchern, 14,6 mm hoch, Unterseite auf das Bett                          ca. %(o).0f g
  U_distanz_3_4.stl     Distanzplatte 20 x 20 x 3,4 mm (Spiel %(g34).1f mm)
  U_distanz_3_6.stl     Distanzplatte 20 x 20 x 3,6 mm (füllt die Luft über einer 12,8-mm-Powerbank genau)
  U_distanz_3_8.stl     Distanzplatte 20 x 20 x 3,8 mm (Pressung 0,2 mm)

Distanzplatte: auf die Powerbank legen, an eine Stelle ohne Leiste, Ader und Zapfenloch; Vorschlag bei x = %(x).0f, y = %(y).0f mm
(Rohkoordinaten der Platte, Süden y = 0; Bild distanzplatte_lage.png). Dann Oberplatte aufsetzen und vernähen. Zuerst 3,6 versuchen;
sitzt die Powerbank locker, 3,8, ist es zu stramm, 3,4. Bei Bedarf einen Punkt Heißkleber auf die Powerbank.

Druck: PLA, 0,2 mm Schicht, Gyroid 10 %% wie plug/slicer.md; Kasten Boden unten. Der Kasten ist noch nicht gedruckt, alle Werte sind Planwerte.
"""
    open(os.path.join(OUT, "README.txt"), "w", encoding="utf-8").write(txt % dict(k=info["U_unterkasten"]["g"], o=info["U_oberplatte"]["g"], g34=gap - 3.4, x=x, y=y))


if __name__ == "__main__":
    raise SystemExit(main())
