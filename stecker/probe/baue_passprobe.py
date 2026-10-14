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


# ---------------- SVG 1: Draufsicht ----------------
def top_view():
    S, M = 11.0, 46
    W, H = pr.PP_W, pr.PP_L
    px = lambda x: M + (x + W / 2) * S
    py = lambda y: 20 + (H / 2 - y) * S
    w_svg, h_svg = M + W * S + 20, 20 + H * S + 40
    s = [f'<svg viewBox="0 0 {w_svg:.0f} {h_svg:.0f}" role="img" aria-label="Draufsicht der Passprobe mit Taschen für Buchse und Stiftleiste und Stiftlöchern" width="{w_svg:.0f}" height="{h_svg:.0f}">']
    s.append(f'<rect x="{px(-W/2)}" y="{py(H/2)}" width="{W*S}" height="{H*S}" rx="3" class="blk"/>')
    for c, x in zip(pr.PP_CL, pr.PP_X):
        # Buchsentasche
        w, d = sd.HSG_W + 2 * c, sd.HSG_T + 2 * c
        s.append(f'<rect x="{px(x-w/2)}" y="{py(pr.PP_Y_B+d/2)}" width="{w*S}" height="{d*S}" class="pocket a"/>')
        s.append(f'<text x="{px(x)}" y="{py(pr.PP_Y_B)+4}" text-anchor="middle" class="mut">Spiel {f(c,1)}</text>')
        # Leistentasche + Schlitz
        w, d = sd.HDR_W + 2 * c, sd.HDR_BODY + 2 * c
        x0, x1, y0, y1, zb = pr.PP_TRENCH
        s.append(f'<rect x="{px(x+x0)}" y="{py(pr.PP_Y_L+y1)}" width="{(x1-x0)*S}" height="{(y1-y0)*S}" class="trench"/>')
        s.append(f'<rect x="{px(x-w/2)}" y="{py(pr.PP_Y_L+d/2)}" width="{w*S}" height="{d*S}" class="pocket b"/>')
        s.append(f'<text x="{px(x)}" y="{py(pr.PP_Y_L)+4}" text-anchor="middle" class="mut">Spiel {f(c,1)}</text>')
        # Beschriftung im Teil (graviert)
        s.append(f'<text x="{px(x)}" y="{py(pr.PP_Y_B-5.6)+4}" text-anchor="middle" class="eng">B {f(c,1)}</text>')
        s.append(f'<text x="{px(x)}" y="{py(pr.PP_Y_L-5.0)+4}" text-anchor="middle" class="eng">L {f(c,1)}</text>')
    for hd, x in zip(pr.PP_HOLES, pr.PP_HOLE_X):
        s.append(f'<circle cx="{px(x)}" cy="{py(pr.PP_Y_H)}" r="{max(hd*S/2, 2.2)}" class="hole"/>')
        s.append(f'<text x="{px(x)}" y="{py(pr.PP_Y_H-4.4)+4}" text-anchor="middle" class="eng">{f(hd,1)}</text>')
    # Markierungen A, B, C
    for letter, y, cls in (("A", pr.PP_Y_B, "a"), ("B", pr.PP_Y_L + 1.5, "b"), ("C", pr.PP_Y_H, "c")):
        s.append(f'<g class="badge {cls}"><circle cx="{px(-W/2)-24}" cy="{py(y)}" r="11"/><text x="{px(-W/2)-24}" y="{py(y)+4}" text-anchor="middle">{letter}</text></g>')
        s.append(f'<path d="M{px(-W/2)-12} {py(y)}H{px(-W/2)+6}" class="lead"/>')
    # Maße
    s.append(f'<path class="dim" d="M{px(-W/2)} {py(-H/2)+14}v8M{px(W/2)} {py(-H/2)+14}v8M{px(-W/2)} {py(-H/2)+18}H{px(W/2)}"/>')
    s.append(f'<text x="{px(0)}" y="{py(-H/2)+34}" text-anchor="middle">{f(W,0)} mm · Höhe {f(pr.PP_H,0)} mm</text>')
    s.append('</svg>')
    return "".join(s)


# ---------------- SVG 2: Schnitt längs y durch die mittlere Spalte (Spiel 0,1) ----------------
def section_view():
    S = 13.0
    c = pr.PP_CL[1]
    x_mid = pr.PP_X[1]
    H = pr.PP_H
    top_extra = 15.0                                   # darüber ragende Teile (Buchse 14 mm, Pins 6 mm)
    ymin, ymax = -19.0, 19.0
    M = 30
    px = lambda y: M + (y - ymin) * S
    pz = lambda z: 20 + (H + top_extra - z) * S
    wv, hv = M + (ymax - ymin) * S + 330, 20 + (H + top_extra) * S + 40
    s = [f'<svg viewBox="0 0 {wv:.0f} {hv:.0f}" role="img" aria-label="Schnitt durch die Passprobe: Buchse und Stiftleiste in ihren Taschen" width="{wv:.0f}" height="{hv:.0f}">']
    # Block (Schnitt) mit Aussparungen als hellere Flächen darüber
    s.append(f'<rect x="{px(ymin)}" y="{pz(H)}" width="{(ymax-ymin)*S}" height="{H*S}" class="blk"/>')
    d = sd.HSG_T + 2 * c
    s.append(f'<rect x="{px(pr.PP_Y_B-d/2)}" y="{pz(H)}" width="{d*S}" height="{(H-pr.PP_BUCHSE_Z)*S}" class="cut"/>')
    d2 = sd.HDR_BODY + 2 * c
    x0, x1, y0, y1, zb = pr.PP_TRENCH
    s.append(f'<rect x="{px(pr.PP_Y_L-d2/2)}" y="{pz(H)}" width="{d2*S}" height="{sd.HDR_BODY*S}" class="cut"/>')
    s.append(f'<rect x="{px(pr.PP_Y_L+y0)}" y="{pz(H-sd.HDR_BODY)}" width="{(y1-y0)*S}" height="{(H-sd.HDR_BODY-zb)*S}" class="cut"/>')
    hd = pr.PP_HOLES[2]
    s.append(f'<rect x="{px(pr.PP_Y_H-hd/2)}" y="{pz(H)}" width="{hd*S}" height="{H*S}" class="cut"/>')
    # eingesetzte Teile (gestrichelt, Farbe)
    # A: Buchse, Steckseite unten auf dem Taschenboden
    zb0 = pr.PP_BUCHSE_Z
    s.append(f'<rect x="{px(pr.PP_Y_B-sd.HSG_T/2)}" y="{pz(zb0+sd.HSG_H)}" width="{sd.HSG_T*S}" height="{sd.HSG_H*S}" class="part a"/>')
    # B: Leistenkörper + Winkelstifte
    zbody0 = H - sd.HDR_BODY
    s.append(f'<rect x="{px(pr.PP_Y_L-sd.HDR_BODY/2)}" y="{pz(H)}" width="{sd.HDR_BODY*S}" height="{sd.HDR_BODY*S}" class="part b"/>')
    pin = sd.PIN_SQ
    zbend = zbody0 - sd.RA_BACK
    s.append(f'<rect x="{px(pr.PP_Y_L-pin/2)}" y="{pz(zbody0+sd.HDR_BODY+sd.HDR_UP)}" width="{pin*S}" height="{(sd.HDR_UP+sd.HDR_BODY+sd.RA_BACK)*S}" class="pinfill"/>')
    s.append(f'<rect x="{px(pr.PP_Y_L-pin/2)}" y="{pz(zbend+pin/2)}" width="{(sd.RA_TAIL+sd.HDR_BODY/2+pin/2)*S}" height="{pin*S}" class="pinfill"/>')
    # Beschriftungen
    def t(x, y, txt, anchor="start", cls=""):
        return f'<text x="{x}" y="{y}" text-anchor="{anchor}" class="{cls}">{txt}</text>'
    s.append(t(px(pr.PP_Y_B), pz(zb0+sd.HSG_H)-8, "A Buchse", "middle", "lab a"))
    s.append(t(px(pr.PP_Y_B) + 14, pz(zb0 + 1.2), "← Steckseite unten", "start", "mut"))
    s.append(t(px(pr.PP_Y_L), pz(H+sd.HDR_UP)-8, "B Stiftleiste", "middle", "lab b"))
    s.append(t(px(pr.PP_Y_L+0.9), pz(zb)+16, "Lötende (Winkelleiste)", "start", "mut"))
    s.append(t(px(pr.PP_Y_H), pz(H)-8, "C Loch", "middle", "lab c"))
    s.append(t(px(pr.PP_Y_B), pz(zb0)+16, "Taschenboden", "middle", "mut"))
    # z-Maße rechts
    xr = px(ymax) + 22
    def dimz(z0, z1, x, label):
        return f'<path class="dim" d="M{x-5} {pz(z0)}h10M{x-5} {pz(z1)}h10M{x} {pz(z0)}V{pz(z1)}"/>' + t(x + 9, (pz(z0)+pz(z1))/2 + 4, label)
    s.append(dimz(zb0, H, xr, f"Buchsentasche {f(H-zb0,0)} mm"))
    s.append(dimz(zbody0, H, xr + 190, f"Körper {f(sd.HDR_BODY,2)}"))
    s.append(dimz(zb, zbody0, xr + 190, ""))
    s.append(t(xr + 199, (pz(zb)+pz(zbody0))/2 + 4, f"Schlitz {f(zbody0-zb,1)}"))
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
