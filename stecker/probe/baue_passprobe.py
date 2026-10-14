#!/usr/bin/env python3
"""Baut stecker/probe/passprobe.html: Anleitung zur Passprobe mit Grafik im Maßstab.
Maße kommen aus steckmodul_probe.py (Passprobe) und steckmodul_dupont.py (Kaufteile)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import steckmodul_dupont as sd          # noqa: E402
import steckmodul_probe as pr           # noqa: E402


def f(v, n=2):
    return ("%.*f" % (n, v)).replace(".", ",").replace("-", "−")


# ---------------- SVG 1: Ansicht auf die Einsetzseite (Druckbettseite), Block um die lange Kante umgedreht ----------------
# In der Ansicht ist y' = −y: Löcher oben, Leiste in der Mitte, Buchse unten, Schrift lesbar.
def top_view():
    S, M = 11.0, 46
    W, H = pr.PP_W, pr.PP_L
    px = lambda x: M + (x + W / 2) * S
    py = lambda y: 20 + (H / 2 + y) * S          # y' = -y  ->  nach unten wachsend in y
    w_svg, h_svg = M + W * S + 20, 20 + H * S + 40
    s = [f'<svg viewBox="0 0 {w_svg:.0f} {h_svg:.0f}" role="img" aria-label="Die Einsetzseite der Passprobe mit Taschen für Buchse und Stiftleiste und Stiftlöchern" width="{w_svg:.0f}" height="{h_svg:.0f}">']
    s.append(f'<rect x="{px(-W/2)}" y="{py(-H/2)}" width="{W*S}" height="{H*S}" rx="3" class="blk"/>')
    for c, x in zip(pr.PP_CL, pr.PP_X):
        # Buchsentasche + Aderschlitz
        w, d = sd.HSG_W + 2 * c, sd.HSG_T + 2 * c
        s.append(f'<rect x="{px(x-w/2)}" y="{py(pr.PP_Y_B-d/2)}" width="{w*S}" height="{d*S}" class="pocket a"/>')
        s.append(f'<rect x="{px(x-pr.PP_SLOT[0]/2)}" y="{py(pr.PP_Y_B-pr.PP_SLOT[1]/2)}" width="{pr.PP_SLOT[0]*S}" height="{pr.PP_SLOT[1]*S}" class="slot"/>')
        # Raum, Leistentasche, Löcher
        rx, ry = pr.PP_ROOM
        s.append(f'<rect x="{px(x-rx)}" y="{py(pr.PP_Y_L-ry)}" width="{2*rx*S}" height="{2*ry*S}" class="trench"/>')
        w, d = sd.HDR_W + 2 * c, sd.HDR_BODY + 2 * c
        s.append(f'<rect x="{px(x-w/2)}" y="{py(pr.PP_Y_L-d/2)}" width="{w*S}" height="{d*S}" class="pocket b"/>')
        for xp in sd.pin_x():
            s.append(f'<circle cx="{px(x+xp)}" cy="{py(pr.PP_Y_L)}" r="{sd.HOLE*S/2:.1f}" class="hole b"/>')
        # Beschriftung (steht auf dem Teil)
        s.append(f'<text x="{px(x)}" y="{py(pr.PP_LABEL_Y["B"])+4}" text-anchor="middle" class="eng">B {f(c,1)}</text>')
        s.append(f'<text x="{px(x)}" y="{py(pr.PP_LABEL_Y["L"])+4}" text-anchor="middle" class="eng">L {f(c,1)}</text>')
    for hd, x in zip(pr.PP_HOLES, pr.PP_HOLE_X):
        s.append(f'<circle cx="{px(x)}" cy="{py(pr.PP_Y_H)}" r="{max(hd*S/2, 2.2)}" class="hole"/>')
        s.append(f'<text x="{px(x)}" y="{py(pr.PP_LABEL_Y["H"])+4}" text-anchor="middle" class="eng">{f(hd,1)}</text>')
    # Markierungen A, B, C
    for letter, y, cls in (("A", pr.PP_Y_B, "a"), ("B", pr.PP_Y_L, "b"), ("C", pr.PP_Y_H, "c")):
        yy = py(y)
        s.append(f'<g class="badge {cls}"><circle cx="{px(-W/2)-24}" cy="{yy}" r="11"/><text x="{px(-W/2)-24}" y="{yy+4}" text-anchor="middle">{letter}</text></g>')
        s.append(f'<path d="M{px(-W/2)-12} {yy}H{px(-W/2)+6}" class="lead"/>')
    s.append(f'<path class="dim" d="M{px(-W/2)} {py(H/2)+14}v8M{px(W/2)} {py(H/2)+14}v8M{px(-W/2)} {py(H/2)+18}H{px(W/2)}"/>')
    s.append(f'<text x="{px(0)}" y="{py(H/2)+34}" text-anchor="middle">{f(W,0)} × {f(H,0)} mm · Höhe {f(pr.PP_H,0)} mm</text>')
    s.append('</svg>')
    return "".join(s)


# ---------------- SVG 2: Schnitt durch die mittlere Spalte (Spiel 0,1) an Pin 2, Bestückung von unten ----------------
def section_view():
    S = 12.0
    c = pr.PP_CL[1]
    H = pr.PP_H
    below, above = 9.0, 7.0                              # Platz unter dem Block (Gehäuse ragt 7 mm heraus) und darüber (Pins)
    ymin, ymax = -20.0, 20.0                              # y' = -y
    M = 30
    px = lambda yv: M + (yv - ymin) * S
    pz = lambda z: 20 + (H + above - z) * S
    wv, hv = M + (ymax - ymin) * S + 310, 20 + (H + above + below) * S + 30
    s = [f'<svg viewBox="0 0 {wv:.0f} {hv:.0f}" role="img" aria-label="Schnitt durch die Passprobe: Buchse und Stiftleiste werden von unten eingesetzt" width="{wv:.0f}" height="{hv:.0f}">']
    s.append(f'<rect x="{px(ymin)}" y="{pz(H)}" width="{(ymax-ymin)*S}" height="{H*S}" class="blk"/>')
    yb, yl, yh = -pr.PP_Y_B, -pr.PP_Y_L, -pr.PP_Y_H    # Lage in y'
    # Aussparungen (hell)
    d = sd.HSG_T + 2 * c
    s.append(f'<rect x="{px(yb-d/2)}" y="{pz(pr.PP_B_DEPTH)}" width="{d*S}" height="{pr.PP_B_DEPTH*S}" class="cut"/>')
    s.append(f'<rect x="{px(yb-pr.PP_SLOT[1]/2)}" y="{pz(H)}" width="{pr.PP_SLOT[1]*S}" height="{(H-pr.PP_B_DEPTH)*S}" class="cut"/>')
    rx, ry = pr.PP_ROOM
    s.append(f'<rect x="{px(yl-ry)}" y="{pz(pr.PP_ROOM_H)}" width="{2*ry*S}" height="{pr.PP_ROOM_H*S}" class="cut"/>')
    d2 = sd.HDR_BODY + 2 * c
    s.append(f'<rect x="{px(yl-d2/2)}" y="{pz(H-pr.PP_FLOOR)}" width="{d2*S}" height="{sd.HDR_BODY*S}" class="cut"/>')
    s.append(f'<rect x="{px(yl-sd.HOLE/2)}" y="{pz(H)}" width="{sd.HOLE*S}" height="{pr.PP_FLOOR*S}" class="cut"/>')
    hd = pr.PP_HOLES[2]
    s.append(f'<rect x="{px(yh-hd/2)}" y="{pz(H)}" width="{hd*S}" height="{H*S}" class="cut"/>')
    # eingesetzte Teile
    zb_top = pr.PP_B_DEPTH
    s.append(f'<rect x="{px(yb-sd.HSG_T/2)}" y="{pz(zb_top)}" width="{sd.HSG_T*S}" height="{sd.HSG_H*S}" class="part a"/>')
    zbody1 = H - pr.PP_FLOOR
    zbody0 = zbody1 - sd.HDR_BODY
    s.append(f'<rect x="{px(yl-sd.HDR_BODY/2)}" y="{pz(zbody1)}" width="{sd.HDR_BODY*S}" height="{sd.HDR_BODY*S}" class="part b"/>')
    pin = sd.PIN_SQ
    zbend = zbody0 - sd.RA_BACK
    s.append(f'<rect x="{px(yl-pin/2)}" y="{pz(zbody1+sd.HDR_UP)}" width="{pin*S}" height="{(sd.HDR_UP+sd.RA_BACK+sd.HDR_BODY)*S}" class="pinfill"/>')
    s.append(f'<rect x="{px(yl-pin/2)}" y="{pz(zbend+pin/2)}" width="{(sd.RA_TAIL+sd.HDR_BODY/2+pin/2)*S}" height="{pin*S}" class="pinfill"/>')
    # Pfeile: von unten einsetzen
    def arrow(x, z0, z1):
        return (f'<path d="M{x} {pz(z0)}V{pz(z1)+4}" class="arrow"/><path d="M{x-5} {pz(z1)+10}L{x} {pz(z1)}L{x+5} {pz(z1)+10}" class="arrow"/>')
    s.append(arrow(px(yb-2.6), -8.0, -1.5))
    s.append(arrow(px(yl-3.0), -4.5, 0.8))
    def t(x, y, txt, anchor="start", cls=""):
        return f'<text x="{x}" y="{y}" text-anchor="{anchor}" class="{cls}">{txt}</text>'
    s.append(t(px(yb), pz(zb_top+sd.HSG_H*0)-0, "", "middle"))
    s.append(t(px(yb), pz(-7.2)+16, "A Buchse, Kabelseite zuerst", "middle", "lab a"))
    s.append(t(px(yb) + 18, pz(-2.5), "Steckseite unten", "start", "mut"))
    s.append(t(px(yl), pz(H + sd.HDR_UP) - 8, "B Stiftleiste, Pins nach oben", "middle", "lab b"))
    s.append(t(px(yl) + 8, pz(zbend) + 30, "Lötende im Raum", "start", "mut"))
    s.append(t(px(yh), pz(H) - 8, "C Loch", "middle", "lab c"))
    s.append(t(px(yl) + 10, pz(-5.5), "von unten einsetzen", "start", "mut"))
    xr = px(ymax) + 24
    def dimz(z0, z1, x, label):
        return f'<path class="dim" d="M{x-5} {pz(z0)}h10M{x-5} {pz(z1)}h10M{x} {pz(z0)}V{pz(z1)}"/>' + t(x + 9, (pz(z0)+pz(z1))/2 + 4, label)
    s.append(dimz(0, pr.PP_B_DEPTH, xr, f"Buchsentasche {f(pr.PP_B_DEPTH,0)}"))
    s.append(dimz(pr.PP_B_DEPTH, H, xr, f"Decke {f(H-pr.PP_B_DEPTH,0)}"))
    s.append(dimz(zbody0, zbody1, xr + 150, f"Körper {f(sd.HDR_BODY,2)}"))
    s.append(dimz(zbody1, H, xr + 150, f"Decke {f(pr.PP_FLOOR,1)}"))
    s.append(dimz(0, zbody0, xr + 150, ""))
    s.append(t(xr + 159, (pz(0)+pz(zbody0))/2 + 4, f"Raum {f(zbody0,1)}"))
    s.append('</svg>')
    return "".join(s)


TEMPLATE = open(os.path.join(HERE, "passprobe.template.html"), encoding="utf-8").read()


def main():
    nominal = [
        ("Buchse (Dupont-Gehäuse 1×4)", "Breite", sd.HSG_W, "HSG_W", "Dupont-Gehäuse"),
        ("Buchse (Dupont-Gehäuse 1×4)", "Dicke", sd.HSG_T, "HSG_T", ""),
        ("Buchse (Dupont-Gehäuse 1×4)", "Höhe", sd.HSG_H, "HSG_H", "±0,25"),
        ("Stiftleiste, 4 Pins", "Körper, Länge", sd.HDR_W, "HDR_W", "4 × 2,54"),
        ("Stiftleiste, 4 Pins", "Körper, Höhe", sd.HDR_BODY, "HDR_BODY", ""),
        ("Stiftleiste, 4 Pins", "Stiftvierkant", sd.PIN_SQ, "PIN_SQ", ""),
        ("Stiftleiste, 4 Pins", "Pin über dem Körper", sd.HDR_UP, "HDR_UP", "Steckseite"),
        ("Gerade Leiste", "Lötende unter dem Körper", sd.HDR_TAIL, "HDR_TAIL", "nur gerade Leiste"),
        ("Winkelleiste", "Biegung hinter dem Körper", sd.RA_BACK, "RA_BACK", "nur Winkelleiste"),
        ("Winkelleiste", "Lötende über die Körperseite", sd.RA_TAIL, "RA_TAIL", "nur Winkelleiste"),
    ]
    rows = "".join(
        f'<tr><td>{a}</td><td>{b}</td><td class="num">{f(v)}</td><td><input class="meas" type="text" inputmode="decimal" autocomplete="off" '
        f'id="m-{k}" data-nom="{v}" data-k="{k}" aria-label="{a}, {b}, gemessen in mm"></td><td class="num dev" id="d-{k}">–</td><td><code>{k}</code></td></tr>'
        for a, b, v, k, _ in nominal)
    html = (TEMPLATE.replace("/*TOP*/", top_view()).replace("/*SECTION*/", section_view())
            .replace("/*ROWS*/", rows)
            .replace("/*SNUG*/", f(sd.SNUG)).replace("/*HOLE*/", f(sd.HOLE, 1)).replace("/*RIB*/", f(sd.RIB)))
    out = os.path.join(HERE, "passprobe.html")
    open(out, "w", encoding="utf-8").write(html)
    print("%s  %.0f kB" % (os.path.relpath(out, os.path.join(HERE, "..", "..")), len(html.encode()) / 1024))


if __name__ == "__main__":
    main()
