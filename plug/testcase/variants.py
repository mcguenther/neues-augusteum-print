#!/usr/bin/env python3
"""Kassetten-Varianten V1 (Streifen quer auf einer Wand) und V2 (Streifen hochkant auf einer Wand): Konzeptgeometrie.

Beide haben denselben Unterbau wie Kassette v4 (Buchsentasche, Schultern, Aderschlitz, Einpress-Schacht 0,06) und tragen den LED-Streifen
auf einer dünnen Wand (Blatt), die oberhalb der Buchse die hintere Taschenwand nach oben fortsetzt. Der Streifen steht, die LED blickt nach −y.
  V1  Streifen quer (lange Kante waagerecht, 10 mm hoch): Unterbau 17,2 breit; niedrig, aber breit
  V2  Streifen hochkant (lange Kante senkrecht, 16,7 hoch): Unterbau 12,96 breit; schlank, aber hoch
Konstruktionslage wie Kassette v4: x mittig, y = 0 an der Vorderseite, z = 0 Unterkante (Taschenseite).
Nur Konzept (Bilder für die Planungsseite plan3.html), keine STL. Bild: python3 -m plug.testcase.variants
"""
import math
import os

from plug import dupont as sd
from plug import series2 as N2
from plug.geom import box, cbox, capsule, diff, prism_x, to_tm, union, xcut
from plug.testcase import params as P

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PREV = os.path.join(HERE, "vorschau", "steckmodul_testcase")

# ---- Vorschläge (Plan Kassetten-Varianten, noch abzunicken)
HSG_TOL_V = 0.60        # Taschenhöhe 14,60 wie im Plan Steckprobe 2
BLATT_T = 1.2           # Dicke des Blatts (drei Wände)
STRIP_W, STRIP_L, STRIP_T = sd.LED_W, sd.LED_L, sd.LED_T     # 10 × 16,7 × 2,2
STRIP_TOL = 0.25        # Spiel je Seite um den Streifen
FPC = sd.LED_FPC        # Folie ohne Chip
CHIP = 5.0              # Chip 5 × 5
ROOM = dict(V1=1.0, V2=1.5)     # Luft zwischen Schulterfläche und Streifenunterkante für die Adern
EF = 0.5                # Fase am Bett


def base():
    """Unterbau: Maße der Tasche und der Schulterfläche."""
    pk_w, pk_d = sd.HSG_W + 2 * N2.SNUG2, sd.HSG_T + 2 * N2.SNUG2
    zp = sd.HSG_H + HSG_TOL_V
    z_b = zp + N2.SEAT_RISE                 # Schulterfläche (Oberkante des Unterbaus)
    y_p0 = sd.WALL
    y1 = y_p0 + pk_d                        # Rückseite der Tasche
    return dict(pk_w=pk_w, pk_d=pk_d, zp=zp, z_b=z_b, y_p0=y_p0, y1=y1, depth=y1 + sd.WALL, ypin=y_p0 + pk_d / 2, slot=N2.WIRE_W)


def dims(var):
    b = base()
    room = ROOM[var]
    if var == "V1":
        w, sh = STRIP_L + 2 * STRIP_TOL, STRIP_W            # Streifen quer: Länge waagerecht, Breite senkrecht
    else:
        w, sh = max(b["pk_w"] + 2 * sd.WALL, STRIP_W + 2 * STRIP_TOL), STRIP_L    # hochkant
    z0 = b["z_b"] + room                    # Unterkante des Streifens
    z_top = z0 + sh + STRIP_TOL             # Oberkante des Blatts
    y_face = b["y1"] - STRIP_T              # Vorderseite des Streifens (Chip)
    return dict(b, var=var, w=w, sh=sh, z0=z0, top=z_top, y_face=y_face, y_fpc=b["y1"] - FPC, room=room,
                strip_w=(STRIP_L if var == "V1" else STRIP_W), strip_h=sh)


def outlines():
    """Außenmaße im Grundriss (ohne Spiel und Wand): v4 zum Vergleich, V1, V2."""
    k4 = P.kass_dims()
    return dict(v4=dict(w=k4["cw"], d=k4["L"], h=k4["top"]),
                V1=dict(w=dims("V1")["w"], d=base()["depth"], h=dims("V1")["top"]),
                V2=dict(w=dims("V2")["w"], d=base()["depth"], h=dims("V2")["top"]))


def kassette(var):
    d = dims(var)
    w, depth, zb = d["w"], d["depth"], d["z_b"]
    body = N2.chamfered_block(w, depth, zb, EF, 0.0).translate([0, depth / 2, 0])
    cuts = [cbox(d["pk_w"], d["pk_d"], -0.01, d["zp"], cy=d["ypin"]),
            N2.chamfer_hole(d["pk_w"], d["pk_d"], 0.0, P.ENTRY_CH_T, True, cy=d["ypin"]),
            box(-d["slot"] / 2, d["slot"] / 2, d["y_p0"], d["y1"], d["zp"] - 0.01, zb + 0.01)]
    m = diff(body, *cuts)
    blatt = box(-w / 2, w / 2, d["y1"], d["y1"] + BLATT_T, zb - 0.01, d["top"])
    return union([m, blatt])


def housing(var):
    d = dims(var)
    return sd.housing_part(0.0).translate([0, -sd.dims()["HY"] + d["ypin"], 0])


def strip(var):
    d = dims(var)
    sw, sh, z0, y1 = d["strip_w"], d["strip_h"], d["z0"], d["y1"]
    parts = [box(-sw / 2, sw / 2, y1 - FPC, y1, z0, z0 + sh),
             box(-CHIP / 2, CHIP / 2, y1 - STRIP_T, y1 - FPC, z0 + sh / 2 - CHIP / 2, z0 + sh / 2 + CHIP / 2)]
    return union(parts)


def wire_path(var, i):
    """Mittellinie der Ader i (x, y, z) von der Buchsenoberkante zum Pad: V2 gerade nach oben, V1 seitlich unter dem Streifen zum Pad-Ende."""
    d = dims(var)
    x = sd.pin_x()[i]
    wr = sd.WIRE_D / 2
    ya, yp = d["ypin"], d["y_fpc"] - wr - 0.1       # Ader in der Tasche, Ader auf dem Pad
    if var == "V2":
        z_pad = d["z0"] + 1.5 + 0.9 * i
        return [(x, ya, d["zp"]), (x, ya, d["z0"] - 0.3), (x * 0.55, (ya + yp) / 2, d["z0"] + 0.6), (x * 0.55, yp, z_pad)]
    xe = -STRIP_L / 2 + 1.4
    z_pad = d["z0"] + 2.0 + 1.6 * i
    return [(x, ya, d["zp"]), (x, ya, d["z0"] - 0.5), (xe + 1.5 - 0.3 * i, ya, d["z0"] - 0.5), (xe + 0.3 * i, yp, d["z0"] + 0.6), (xe, yp, z_pad)]


def wires(var):
    out = []
    for i in range(4):
        pts = wire_path(var, i)
        out += [capsule(a, b, sd.WIRE_D / 2) for a, b in zip(pts, pts[1:])]
    return union(out)


def render_set(var, size=(560, 520), px=None):
    import preview
    k, h, s, wi = kassette(var), housing(var), strip(var), wires(var)
    kw = dict(size=size) if px is None else dict(px_per_mm=px, pad=40)
    iso = preview.render([(to_tm(k), "#e3862a"), (to_tm(h), "#f4f1e8"), (to_tm(s), "#f3dc7a"), (to_tm(wi), "#c8423b")], azim=-50, elev=28, **kw)
    cut = preview.render([(to_tm(xcut(k, 0.0)), "#e3862a"), (to_tm(xcut(h, 0.0)), "#f4f1e8"), (to_tm(xcut(s, 0.0)), "#f3dc7a"), (to_tm(wi), "#c8423b")],
                         azim=0, elev=0, **kw)
    return iso, cut


def main():
    os.makedirs(PREV, exist_ok=True)
    from PIL import Image
    ok = True
    for var in ("V1", "V2"):
        k = kassette(var)
        tm = to_tm(k)
        d = dims(var)
        print("%s: %.2f × %.2f × %.2f mm, dicht=%s, Streifen z %.1f bis %.1f, Blatt bis %.1f" % (
            var, d["w"], d["depth"], d["top"], tm.is_watertight, d["z0"], d["z0"] + d["sh"], d["top"]))
        ok &= tm.is_watertight
    px = 12
    a1, b1 = render_set("V1", px=px)
    a2, b2 = render_set("V2", px=px)
    ims = [a1, a2, b1, b2]
    W = max(i.size[0] for i in ims)
    H = max(i.size[1] for i in ims)
    bg = ims[0].getpixel((2, 2))
    sheet = Image.new("RGB", (2 * W, 2 * H), bg)
    for n, im in enumerate(ims):                    # jedes Bild mittig in seiner Zelle, gleicher Hintergrund
        cell = Image.new("RGB", (W, H), bg)
        cell.paste(im, ((W - im.size[0]) // 2, (H - im.size[1]) // 2))
        sheet.paste(cell, ((n % 2) * W, (n // 2) * H))
    sheet.save(os.path.join(PREV, "varianten_v1_v2.png"))
    print("Bild: vorschau/steckmodul_testcase/varianten_v1_v2.png")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
