#!/usr/bin/env python3
"""Baut stecker/probe/passprobe.html: Anleitung zur Passprobe mit Grafik im Maßstab.
Maße kommen aus steckmodul_probe.py (Passprobe) und steckmodul_dupont.py (Kaufteile)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import steckmodul_dupont as sd          # noqa: E402
import steckmodul_probe as pr           # noqa: E402


def g(v):
    return ("%g" % v).replace(".", ",")


def f(v, n=2):
    return ("%.*f" % (n, v)).replace(".", ",").replace("-", "−")


# ---------------- SVG 1: Draufsicht (Oberseite, Schrift lesbar). Taschen öffnen sich nach unten und sind gestrichelt ----------------
def top_view():
    S, M = 11.0, 46
    W, H = pr.PP_W, pr.PP_L
    px = lambda x: M + (x + W / 2) * S
    py = lambda y: 20 + (H / 2 - y) * S          # y nach oben wie im Teil
    w_svg, h_svg = M + W * S + 20, 20 + H * S + 40
    s = [f'<svg viewBox="0 0 {w_svg:.0f} {h_svg:.0f}" role="img" aria-label="Draufsicht der Passprobe mit Buchsentaschen, Leistentaschen und Blindlöchern" width="{w_svg:.0f}" height="{h_svg:.0f}">']
    s.append(f'<rect x="{px(-W/2)}" y="{py(H/2)}" width="{W*S}" height="{H*S}" rx="3" class="blk"/>')
    for c, x in zip(pr.PP_CL, pr.PP_X):
        w, d = sd.HSG_W + 2 * c, sd.HSG_T + 2 * c       # Buchse: durchgehend
        s.append(f'<rect x="{px(x-w/2)}" y="{py(pr.PP_Y_B+d/2)}" width="{w*S}" height="{d*S}" class="pocket a"/>')
        w, d = sd.HDR_W + 2 * c, sd.HDR_BODY + 2 * c    # Leiste: von oben nicht sichtbar, nur die Löcher
        s.append(f'<rect x="{px(x-w/2)}" y="{py(pr.PP_Y_L+d/2)}" width="{w*S}" height="{d*S}" class="pocket b ghost"/>')
        s.append(f'<rect x="{px(x-pr.PP_SLOT_X)}" y="{py(pr.PP_Y_L+pr.PP_TAIL)}" width="{2*pr.PP_SLOT_X*S}" height="{(pr.PP_TAIL-d/2)*S}" class="trench"/>')
        hd = pr.PP_HOLES[pr.PP_X.index(x)]
        for xp in sd.pin_x():
            s.append(f'<circle cx="{px(x+xp)}" cy="{py(pr.PP_Y_L)}" r="{(hd/2+pr.PP_HCH)*S:.1f}" class="csink"/>')
            s.append(f'<circle cx="{px(x+xp)}" cy="{py(pr.PP_Y_L)}" r="{hd*S/2:.1f}" class="hole b"/>')
        s.append(f'<text x="{px(x)}" y="{py(pr.PP_Y_LAB_C)+4}" text-anchor="middle" class="eng">{g(c)}</text>')
    for hd, x in zip(pr.PP_HOLES, pr.PP_X):
        s.append(f'<circle cx="{px(x)}" cy="{py(pr.PP_Y_H)}" r="{(hd/2+pr.PP_HCH)*S:.1f}" class="csink"/>')
        s.append(f'<circle cx="{px(x)}" cy="{py(pr.PP_Y_H)}" r="{hd*S/2:.1f}" class="hole"/>')
        s.append(f'<text x="{px(x)}" y="{py(pr.PP_Y_LAB_H)+4}" text-anchor="middle" class="eng">{f(hd,1)}</text>')
    for letter, y, cls in (("A", pr.PP_Y_B, "a"), ("B", pr.PP_Y_L, "b"), ("C", pr.PP_Y_H, "c")):
        yy = py(y)
        s.append(f'<g class="badge {cls}"><circle cx="{px(-W/2)-24}" cy="{yy}" r="11"/><text x="{px(-W/2)-24}" y="{yy+4}" text-anchor="middle">{letter}</text></g>')
        s.append(f'<path d="M{px(-W/2)-12} {yy}H{px(-W/2)+6}" class="lead"/>')
    s.append(f'<path class="dim" d="M{px(-W/2)} {py(-H/2)+14}v8M{px(W/2)} {py(-H/2)+14}v8M{px(-W/2)} {py(-H/2)+18}H{px(W/2)}"/>')
    s.append(f'<text x="{px(0)}" y="{py(-H/2)+34}" text-anchor="middle">{f(W,1)} × {f(H,1)} mm · Dicke {f(pr.PP_H,1)} mm</text>')
    s.append('</svg>')
    return "".join(s)


# ---------------- SVG 2: Schnitt, die drei Reihen nebeneinander gezeichnet (Spiel 0,3). Bestückung von unten ----------------
def section_view():
    S = 16.0
    c = pr.PP_CL[1]
    H = pr.PP_H
    below, above = 10.0, 6.0
    ymin, ymax = -pr.PP_L / 2, pr.PP_L / 2
    M = 110
    px = lambda yv: M + (yv - ymin) * S
    pz = lambda z: 30 + (H + above - z) * S
    wv, hv = M + (ymax - ymin) * S + 250, 20 + (H + above + below) * S + 30
    s = [f'<svg viewBox="0 0 {wv:.0f} {hv:.0f}" role="img" aria-label="Schnitt durch die Passprobe: Buchse und Stiftleiste werden von unten eingesetzt" width="{wv:.0f}" height="{hv:.0f}">']
    s.append(f'<rect x="{px(ymin)}" y="{pz(H)}" width="{(ymax-ymin)*S}" height="{H*S}" class="blk"/>')
    yb, yl, yh = pr.PP_Y_B, pr.PP_Y_L, pr.PP_Y_H
    d = sd.HSG_T + 2 * c
    s.append(f'<rect x="{px(yb-d/2)}" y="{pz(H)}" width="{d*S}" height="{H*S}" class="cut"/>')
    zb = H - pr.PP_FLOOR
    d2 = sd.HDR_BODY + 2 * c
    s.append(f'<rect x="{px(yl-d2/2)}" y="{pz(zb)}" width="{d2*S}" height="{zb*S}" class="cut"/>')
    s.append(f'<rect x="{px(yl)}" y="{pz(pr.PP_SLOT_H)}" width="{pr.PP_TAIL*S}" height="{pr.PP_SLOT_H*S}" class="cut"/>')
    hd = pr.PP_HOLES[1]
    cs = pr.PP_HCH
    s.append(f'<rect x="{px(yl-hd/2)}" y="{pz(H)}" width="{hd*S}" height="{pr.PP_FLOOR*S}" class="cut"/>')
    s.append(f'<rect x="{px(yh-hd/2)}" y="{pz(H)}" width="{hd*S}" height="{pr.PP_HOLE_DEPTH*S}" class="cut"/>')
    for yc in (yl, yh):                                 # Senkungen an der Schriftseite (oben in der Zeichnung)
        s.append(f'<path d="M{px(yc-hd/2-cs)} {pz(H)}L{px(yc+hd/2+cs)} {pz(H)}L{px(yc+hd/2)} {pz(H-cs)}L{px(yc-hd/2)} {pz(H-cs)}Z" class="cut"/>')
    ch = pr.PP_CH
    for yc, dd in ((yb, d), (yl, d2)):                  # Einlauffasen unten an Buchsen- und Leistentasche
        for sgn in (-1, 1):
            xe = yc + sgn * dd / 2
            s.append(f'<path d="M{px(xe)} {pz(ch)}L{px(xe + sgn * ch)} {pz(0)}L{px(xe)} {pz(0)}Z" class="cut"/>')
    # eingesetzte Teile
    s.append(f'<rect x="{px(yb-sd.HSG_T/2)}" y="{pz(H)}" width="{sd.HSG_T*S}" height="{sd.HSG_H*S}" class="part a"/>')
    zbody1 = zb
    zbody0 = zbody1 - sd.HDR_BODY
    s.append(f'<rect x="{px(yl-sd.HDR_BODY/2)}" y="{pz(zbody1)}" width="{sd.HDR_BODY*S}" height="{sd.HDR_BODY*S}" class="part b"/>')
    pin = sd.PIN_SQ
    zbend = zbody0 - sd.RA_BACK
    s.append(f'<rect x="{px(yl-pin/2)}" y="{pz(zbody1+sd.HDR_UP)}" width="{pin*S}" height="{(sd.HDR_UP+sd.RA_BACK+sd.HDR_BODY)*S}" class="pinfill"/>')
    s.append(f'<rect x="{px(yl-pin/2)}" y="{pz(zbend+pin/2)}" width="{(sd.RA_TAIL+sd.HDR_BODY/2+pin/2)*S}" height="{pin*S}" class="pinfill"/>')
    s.append(f'<rect x="{px(yh-pin/2)}" y="{pz(H+3.0)}" width="{pin*S}" height="{(3.0+pr.PP_HOLE_DEPTH)*S}" class="pinfill"/>')
    def arrow(x, z0, z1):
        return (f'<path d="M{x} {pz(z0)}V{pz(z1)+4}" class="arrow"/><path d="M{x-5} {pz(z1)+10}L{x} {pz(z1)}L{x+5} {pz(z1)+10}" class="arrow"/>')
    s.append(arrow(px(yb-2.6), -9.0, -1.5))
    s.append(arrow(px(yl-3.0), -5.0, -0.5))
    def t(x, y, txt, anchor="start", cls=""):
        return f'<text x="{x}" y="{y}" text-anchor="{anchor}" class="{cls}">{txt}</text>'
    s.append(t(px(yb), pz(-9.0)+20, "A Buchse, Kabelseite zuerst", "middle", "lab a"))
    s.append(t(px(yb) + 26, pz(-6.0), "Steckseite unten", "start", "mut"))
    s.append(t(px(yl), pz(H + sd.HDR_UP) - 10, "B Stiftleiste", "middle", "lab b"))
    s.append(t(px(yl - 3.0) - 12, pz(-3.0), "von unten einsetzen", "end", "mut"))
    s.append(t(px(yh) - 8, pz(H + 3.0) + 4, "C Blindloch", "end", "lab c"))
    xr = px(ymax) + 24
    def dimz(z0, z1, x, label):
        return f'<path class="dim" d="M{x-5} {pz(z0)}h10M{x-5} {pz(z1)}h10M{x} {pz(z0)}V{pz(z1)}"/>' + t(x + 9, (pz(z0)+pz(z1))/2 + 4, label)
    s.append(dimz(0, H, xr, f"Dicke {f(H,1)}"))
    s.append(dimz(zbody0, zbody1, xr + 105, f"Körper {f(sd.HDR_BODY,2)}"))
    s.append(dimz(zbody1, H, xr + 105, f"Decke {f(pr.PP_FLOOR,1)}"))
    s.append(dimz(0, zbody0, xr + 105, f"Raum {f(zbody0,1)}"))
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
            .replace("/*CL*/", " / ".join(g(c) for c in pr.PP_CL)).replace("/*CLN*/", g(pr.PP_CL[0])).replace("/*CLX*/", g(pr.PP_CL[-1]))
            .replace("/*HOLES*/", " / ".join(g(h) for h in pr.PP_HOLES)).replace("/*HCH*/", g(pr.PP_HCH)).replace("/*CH*/", g(pr.PP_CH))
            .replace("/*OPTS*/", "".join(f"<option>{g(c)}</option>" for c in pr.PP_CL)).replace("/*HOPTS*/", "".join(f"<option>{g(h)}</option>" for h in pr.PP_HOLES))
            .replace("/*PW*/", f(pr.PP_W, 1)).replace("/*PL*/", f(pr.PP_L, 1)).replace("/*PH*/", f(pr.PP_H, 1))
            .replace("/*SNUG*/", f(sd.SNUG)).replace("/*HOLE*/", f(sd.HOLE, 1)).replace("/*RIB*/", f(sd.RIB)))
    out = os.path.join(HERE, "passprobe.html")
    open(out, "w", encoding="utf-8").write(html)
    print("%s  %.0f kB" % (os.path.relpath(out, os.path.join(HERE, "..", "..")), len(html.encode()) / 1024))


if __name__ == "__main__":
    main()
