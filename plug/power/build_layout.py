#!/usr/bin/env python3
"""Lösungsfindung 1:1300: interaktive Seite zur Lage der Powerbank und zu den freien Docks: plug/power/layout.html.

Zweistufig, weil die Rechnung lange dauert:
    python3 -m plug.power.build_layout --collect   # rechnet Daten (einige Minuten) nach plug/power/layout_data.json
    python3 -m plug.power.build_layout             # baut die Seite aus layout_data.json und layout.template.html
Annahmen (Nutzer, 2026-10-16): Maßstab 1:1300, Nische halb so groß in beide Richtungen (12 × 9,5 mm), keine Taste, Ladeanschluss durch das Fenster.
Die Seite rechnet Docks, Elektronik und Karten im Browser nach (Raster 3 mm, gleiche Regeln wie `build_concept.place_docks`); sie ist eine Näherung zum
Suchen, die endgültige Prüfung bleibt `build_concept.variant()`.
"""
import json
import math
import os
import sys
import time

import numpy as np
from shapely.ops import unary_union

from plug.power import build_concept as BC
from plug.power import params as PP

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "layout_data.json")
TEMPLATE = os.path.join(HERE, "layout.template.html")
OUT = os.path.join(HERE, "layout.html")
G = BC.G
SCALE = 1300
WIDTHS = [13.62, 13.0, 12.4, 11.8, 11.2, 10.6, 10.0]      # Breite der Kassette samt Spiel, Rasterschritt der Suche


def poly(p, sh):
    if p.geom_type == "MultiPolygon":          # Laserscan-Grundrisse sind teils mehrteilig: größten Teil zeichnen
        p = max(p.geoms, key=lambda g: g.area)
    return [[round(x + sh[0], 2), round(y + sh[1], 2)] for x, y in list(p.exterior.coords)[:-1]]


def dock_dk(niche_w, niche_l):
    """Dock-Maße mit anderer Nische (Länge ab Körpertasche)."""
    old = PP.NICHE
    base = BC.dock_numbers()
    PP.NICHE = dict(old, w=niche_w, l=niche_l - (base["y_slot"] - base["slot_end"]))
    try:
        return BC.dock_numbers()
    finally:
        PP.NICHE = old


def cand_list(cands, sh, cap=1400):
    out, seen = [], set()
    for score, phi, p in cands:
        key = (round(p[0] / 2.0), round(p[1] / 2.0), round(phi))
        if key in seen:
            continue
        seen.add(key)
        out.append([round(p[0] + sh[0], 1), round(p[1] + sh[1], 1), round(phi, 1), round(score, 1)])
        if len(out) >= cap:
            break
    return out


def collect():
    t0 = time.time()
    s = 1000.0 / SCALE
    G.FAST = True                              # wie build_concept.variant: Laserscan-Grundrisse, F 14,2, Hof 6 mm
    m = G.source_models("laserscan", s)
    fps = {k: v[1] for k, v in m.items() if k in BC.TP.CASSETTE}
    hof_solid, hof_fp, _ = BC.innenhof.model(s, list(fps.values()), BC.TP.HOF_DEPTH_T, BC.TP.HOF_CLR_T)
    sel = list(G.BUILDINGS)
    foot = unary_union([fps[b["slug"]] for b in sel])
    outline = G.plate_outline(unary_union([foot, hof_fp]))
    minx, miny, maxx, maxy = outline.bounds
    sh = (-minx, -miny)
    inner = outline.buffer(-PP.UK_WALL, join_style=2)
    pocket_fp = BC.innenhof.flaeche_mm(list(fps.values()), s)
    mulden = foot.buffer(BC.TP.OUTLINE_CLR_T)
    vs = BC.place_vs(outline, unary_union([mulden.buffer(BC.V["wall"]), pocket_fp.buffer(BC.V["wall"])]))
    vzones = [n["notch"].buffer(1.0) for n in vs] + [v["foot"].buffer(1.0) for v in vs]
    dk_half = dock_dk(12.0, 9.54)
    dk_big = dock_dk(24.0, 19.08)
    base = BC.DK

    def dock_local(dk):
        z = BC.dock_zone(dk).bounds
        return dict(zone=[round(x, 2) for x in z],
                    body=[-dk["hw"], dk["y_slot"], dk["hw"], dk["yb"] + dk["hd"]],
                    kass=[-dk["kass_w"] / 2, dk["kass0"], dk["kass_w"] / 2, dk["kass1"]],
                    niche=[-dk["niche_w"] / 2, dk["niche_end"], dk["niche_w"] / 2, dk["y_slot"]],
                    niche_w=dk["niche_w"], niche_l=round(dk["niche_l"], 2))

    print("Maße fertig %.0f s" % (time.time() - t0), flush=True)
    # Kassettenbreite: Anzahl der Lagen je Gebäude
    width_rows, cand_sets = [], {}
    for w in WIDTHS:
        dk = dict(dk_half, kass_w=w)
        c = BC.kass_candidates(fps, dk, uniform=True)
        width_rows.append(dict(w=w, n={k: len(v) for k, v in c.items()}))
        cand_sets[w] = c
        print("Kassette %.2f: %s %.0f s" % (w, {k[:2]: len(v) for k, v in c.items()}, time.time() - t0), flush=True)
    full = [r["w"] for r in width_rows if all(r["n"][b["slug"]] > 0 for b in sel)]
    narrow_w = max(full) if full else WIDTHS[-1]
    sets = dict(cur=cand_list_set(cand_sets[WIDTHS[0]], sh), narrow=cand_list_set(cand_sets[narrow_w], sh))
    # Voreinstellungen und Maßstabstabelle mit der halben Nische
    scales = []
    pre = {}
    for sc in (1300, 1250, 1200, 1100):
        v = BC.variant(sc, BC.H0, dk_half)
        scales.append(dict(scale=sc, plate=v["plate"], hut_over=v["hut"]["over"], side=v["side"], esp=v["esp"], sides=v["sides"],
                           docks=[dict(slug=d["slug"], ok=d["ok"]) for d in v["docks"]]))
        print("Maßstab %d fertig: %s %.0f s" % (sc, [(d["slug"][:2], d["ok"]) for d in v["docks"]], time.time() - t0), flush=True)
        if sc == SCALE:
            pre = dict(frame=v["frame"], side=v["side"], esp=v["esp"], docks=v["docks"] if False else None)
    data = dict(
        scale=SCALE, W=round(maxx - minx, 2), H=round(maxy - miny, 2), outline=poly(outline, sh), inner=poly(inner, sh),
        hof=poly(hof_fp, sh), vzones=[poly(z, sh) for z in vzones if not z.is_empty],
        vpos=[[round(v["c"][0] + sh[0], 1), round(v["c"][1] + sh[1], 1)] for v in vs],
        buildings=[dict(slug=b["slug"], title=b["title"], poly=poly(fps[b["slug"]], sh), inr=round(2 * BC.max_inradius(fps[b["slug"]]), 1)) for b in sel],
        dock=dict(half=dock_local(dk_half), big=dock_local(dk_big), zone_pad=PP.ZONE_PAD),
        fach=dict(L=PP.PB_L, W=PP.PB_W, T=PP.PB_T, clr=PP.PB_CLR, plug=PP.PB_PLUG, cable=PP.PB_CABLE, wall=PP.UK_WALL, pad=PP.WINDOW_PAD,
                  ports={k: PP.PB_PORT_V[k] for k in ("leds", "micro", "usb_c", "usb_a")}, half={k: BC.PORT_HALF[k] for k in ("leds", "micro", "usb_c", "usb_a")}),
        esp=[list(b) for b in PP.ESP_BOXES], hut=PP.HUT, heights=dict(total=BC.H0["total"], uk=BC.H0["uk_t"], fach_h=BC.H0["fach_h"]),
        cands=sets, kass_w=dict(cur=WIDTHS[0], narrow=narrow_w), width_rows=width_rows, scales=scales, frame=pre["frame"], side=pre["side"],
        shift=list(sh))
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    print("geschrieben: %s (%d kB), %.0f s" % (os.path.relpath(DATA), os.path.getsize(DATA) // 1024, time.time() - t0))


def cand_list_set(c, sh):
    return {k: cand_list(v, sh) for k, v in c.items()}


def page():
    with open(DATA, encoding="utf-8") as f:
        data = json.load(f)
    with open(os.path.join(HERE, "concept.template.html"), encoding="utf-8") as f:
        head = f.read().split('<div class="wrap">')[0].replace("<title>Powerbank in der Grundplatte</title>", "<title>Lösungsfindung 1:1300</title>")
    with open(TEMPLATE, encoding="utf-8") as f:
        html = head + f.read()
    html = html.replace("{{DATA}}", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print("geschrieben: %s (%d kB)" % (os.path.relpath(OUT), os.path.getsize(OUT) // 1024))


if __name__ == "__main__":
    if "--collect" in sys.argv:
        collect()
    else:
        page()
