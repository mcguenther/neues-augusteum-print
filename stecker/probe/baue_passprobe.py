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


# ---------------- SVG 1: Draufsicht auf die Schriftseite. Taschen öffnen sich nach unten und sind gestrichelt ----------------
def top_view():
    S, M = 11.0, 46
    W, H = pr.PP_W, pr.PP_L
    px = lambda x: M + (x + W / 2) * S
    py = lambda y: 20 + (H / 2 - y) * S          # y nach oben wie im Teil
    w_svg, h_svg = M + W * S + 20, 20 + H * S + 40
    s = [f'<svg viewBox="0 0 {w_svg:.0f} {h_svg:.0f}" role="img" aria-label="Draufsicht der Passprobe mit Körpertaschen und Pinlöchern in zwei Zeilen und drei Spalten" width="{w_svg:.0f}" height="{h_svg:.0f}">']
    s.append(f'<rect x="{px(-W/2)}" y="{py(H/2)}" width="{W*S}" height="{H*S}" rx="3" class="blk"/>')
    for r, (c, yb, ly) in enumerate(zip(pr.PP_ROWS, pr.PP_YB, pr.PP_LAB)):
        w, d = sd.HDR_W + 2 * c, sd.HDR_BODY + 2 * c
        for off, x in zip(pr.PP_OFF, pr.PP_X):
            s.append(f'<rect x="{px(x-w/2)}" y="{py(yb+d/2)}" width="{w*S}" height="{d*S}" class="pocket b ghost"/>')
            s.append(f'<rect x="{px(x-pr.PP_SLOT_X)}" y="{py(yb+pr.PP_FWD)}" width="{2*pr.PP_SLOT_X*S}" height="{(pr.PP_FWD-d/2)*S}" class="trench"/>')
            s.append(f'<rect x="{px(x-pr.PP_SLOT_X)}" y="{py(yb-d/2)}" width="{2*pr.PP_SLOT_X*S}" height="{(pr.PP_BACK-d/2)*S}" class="trench"/>')
            for xp in sd.pin_x():
                cy = yb + pr.PP_YOFF + off
                s.append(f'<circle cx="{px(x+xp)}" cy="{py(cy)}" r="{(pr.PP_HOLE/2+pr.PP_HCH)*S:.1f}" class="csink"/>')
                s.append(f'<circle cx="{px(x+xp)}" cy="{py(cy)}" r="{pr.PP_HOLE*S/2:.1f}" class="hole b"/>')
            # Soll-Lage der Pins als kleine Markierung (Kreuz) neben dem ersten Pin
        for x in pr.PP_X:
            s.append(f'<text x="{px(x)}" y="{py(ly)+4}" text-anchor="middle" class="eng">{g(c)}</text>')
        s.append(f'<g class="badge b"><circle cx="{px(-W/2)-24}" cy="{py(yb)}" r="11"/><text x="{px(-W/2)-24}" y="{py(yb)+4}" text-anchor="middle">{r+1}</text></g>')
        s.append(f'<path d="M{px(-W/2)-12} {py(yb)}H{px(-W/2)+6}" class="lead"/>')
    for off, x in zip(pr.PP_OFF, pr.PP_X):
        lab = ("%+g" % off if off else "0").replace(".", ",").replace("-", "−")
        s.append(f'<text x="{px(x)}" y="{py(pr.PP_LAB_OFF)+4}" text-anchor="middle" class="eng">{lab}</text>')
    s.append(f'<path class="dim" d="M{px(-W/2)} {py(-H/2)+14}v8M{px(W/2)} {py(-H/2)+14}v8M{px(-W/2)} {py(-H/2)+18}H{px(W/2)}"/>')
    s.append(f'<text x="{px(0)}" y="{py(-H/2)+34}" text-anchor="middle">{f(W,1)} × {f(H,1)} mm · Dicke {f(pr.PP_H,1)} mm</text>')
    s.append('</svg>')
    return "".join(s)


# ---------------- SVG 2: Schnitt durch die untere Zeile, Spalte Mitte (Verschiebung 0). Bestückung von unten ----------------
def section_view():
    S = 26.0
    c = pr.PP_ROWS[0]
    H = pr.PP_H
    yb = 0.0                                              # Körpermitte als Nullpunkt der Zeichnung
    ymin, ymax = -pr.PP_BACK - 5.0, pr.PP_FWD + 3.0
    above, below = 6.0, 4.4
    M = 20
    px = lambda yv: M + (yv - ymin) * S
    pz = lambda z: 40 + (H + above - z) * S
    wv, hv = M + (ymax - ymin) * S + 330, 40 + (H + above + below) * S + 30
    s = [f'<svg viewBox="0 0 {wv:.0f} {hv:.0f}" role="img" aria-label="Schnitt durch ein Feld der Passprobe: Körper in der Tasche, Pins durch den Muldenboden, Lötenden im Schlitz" width="{wv:.0f}" height="{hv:.0f}">']
    s.append(f'<rect x="{px(ymin)}" y="{pz(H)}" width="{(ymax-ymin)*S}" height="{H*S}" class="blk"/>')
    zb = H - pr.PP_FLOOR
    zm = zb - sd.HDR_BODY / 2
    hd = sd.HDR_BODY / 2 + c
    y_leg = pr.PP_YOFF
    # Aussparungen
    s.append(f'<rect x="{px(yb-hd)}" y="{pz(zb)}" width="{2*hd*S}" height="{zb*S}" class="cut"/>')
    s.append(f'<rect x="{px(yb)}" y="{pz(zb)}" width="{pr.PP_FWD*S}" height="{zb*S}" class="cut"/>')
    s.append(f'<rect x="{px(yb-pr.PP_BACK)}" y="{pz(zm+0.7)}" width="{pr.PP_BACK*S}" height="{(zm+0.7)*S}" class="cut"/>')
    hh = pr.PP_HOLE
    s.append(f'<rect x="{px(y_leg-hh/2)}" y="{pz(H)}" width="{hh*S}" height="{pr.PP_FLOOR*S}" class="cut"/>')
    cs, ch = pr.PP_HCH, pr.PP_CH
    s.append(f'<path d="M{px(y_leg-hh/2-cs)} {pz(H)}L{px(y_leg+hh/2+cs)} {pz(H)}L{px(y_leg+hh/2)} {pz(H-cs)}L{px(y_leg-hh/2)} {pz(H-cs)}Z" class="cut"/>')
    for sgn in (-1, 1):
        xe = yb + sgn * hd
        s.append(f'<path d="M{px(xe)} {pz(ch)}L{px(xe + sgn * ch)} {pz(0)}L{px(xe)} {pz(0)}Z" class="cut"/>')
    # eingesetzte Winkelleiste
    pin = sd.PIN_SQ
    zt = zm - pin / 2 + sd.HDR_LEG
    s.append(f'<rect x="{px(yb-sd.HDR_BODY/2)}" y="{pz(zb)}" width="{sd.HDR_BODY*S}" height="{sd.HDR_BODY*S}" class="part b"/>')
    s.append(f'<path class="pinfill" d="M{px(yb-sd.HDR_BODY/2-sd.RA_TAIL)} {pz(zm+pin/2)}H{px(y_leg+pin/2)}V{pz(zt)}H{px(y_leg-pin/2)}V{pz(zm-pin/2)}H{px(yb-sd.HDR_BODY/2-sd.RA_TAIL)}Z"/>')
    def arrow(x, z0, z1):
        return (f'<path d="M{x} {pz(z0)}V{pz(z1)+4}" class="arrow"/><path d="M{x-5} {pz(z1)+10}L{x} {pz(z1)}L{x+5} {pz(z1)+10}" class="arrow"/>')
    s.append(arrow(px(yb - 3.0), -2.2, -0.2))
    def t(x, y, txt, anchor="start", cls=""):
        return f'<text x="{x}" y="{y}" text-anchor="{anchor}" class="{cls}">{txt}</text>'
    s.append(t(px(yb - 3.0) - 12, pz(-1.6), "von unten einsetzen", "end", "mut"))
    s.append(t(px(yb - sd.HDR_BODY / 2 - sd.RA_TAIL / 2), pz(zm + 0.7) - 24, "Lötende 3", "middle", "mut"))
    s.append(t(px(y_leg), pz(zt) - 10, "senkrechte Pins", "middle", "lab b"))
    # Maße (y)
    yd = pz(0) + 34
    def dimy(ya, yb_, label, yy=yd):
        return (f'<path class="dim" d="M{px(ya)} {yy-5}v10M{px(yb_)} {yy-5}v10M{px(ya)} {yy}H{px(yb_)}"/>'
                + t((px(ya) + px(yb_)) / 2, yy + 15, label, "middle"))
    s.append(dimy(yb + sd.HDR_BODY / 2, y_leg - pin / 2, f"{f(sd.RA_BACK,1)}"))
    s.append(dimy(y_leg - pin / 2, y_leg + pin / 2, "", yd))
    s.append(t(px(y_leg - pin / 2), yd + 34, f"Pin-Mitte {f(pr.PP_YOFF)} hinter der Körpermitte", "start", "mut"))
    xr = px(ymax) + 24
    def dimz(z0, z1, x, label):
        return f'<path class="dim" d="M{x-5} {pz(z0)}h10M{x-5} {pz(z1)}h10M{x} {pz(z0)}V{pz(z1)}"/>' + t(x + 9, (pz(z0)+pz(z1))/2 + 4, label)
    s.append(dimz(0, H, xr, f"Dicke {f(H,1)}"))
    s.append(dimz(zb - sd.HDR_BODY, zb, xr + 110, f"Körper {f(sd.HDR_BODY,2)}"))
    s.append(dimz(zb, H, xr + 110, f"Decke {f(pr.PP_FLOOR,1)}"))
    s.append(dimz(zm - pin / 2, zt, xr + 220, f"Pin {f(sd.HDR_LEG,0)}"))
    s.append('</svg>')
    return "".join(s)


TEMPLATE = open(os.path.join(HERE, "passprobe.template.html"), encoding="utf-8").read()


def main():
    nominal = [
        ("Winkelleiste, 4 Pins", "Körper, Länge (abgebrochen)", sd.HDR_W, "HDR_W", "4 × 2,54 plus Abbruchrest"),
        ("Winkelleiste, 4 Pins", "Körper, Höhe", sd.HDR_BODY, "HDR_BODY", ""),
        ("Winkelleiste, 4 Pins", "Körper, Dicke in Pin-Richtung", sd.HDR_BODY, "HDR_BODY", "gemessen etwa 2, Datenblatt 2,54"),
        ("Winkelleiste, 4 Pins", "Stiftvierkant", sd.PIN_SQ, "PIN_SQ", ""),
        ("Winkelleiste, 4 Pins", "Körperkante bis Innenkante des senkrechten Pins", sd.RA_BACK, "RA_BACK", "gemessen etwa 1"),
        ("Winkelleiste, 4 Pins", "Pin hinter dem Körper (Lötende)", sd.RA_TAIL, "RA_TAIL", "gemessen etwa 3"),
        ("Winkelleiste, 4 Pins", "senkrechter Pin, Ende bis Außenkante Biegung", sd.HDR_LEG, "HDR_LEG", "gemessen etwa 7"),
    ]
    rows = "".join(
        f'<tr><td>{a}</td><td>{b}</td><td class="num">{f(v)}</td><td><input class="meas" type="text" inputmode="decimal" autocomplete="off" '
        f'id="m-{i}" data-nom="{v}" data-k="{k}" data-name="{b}" aria-label="{a}, {b}, gemessen in mm"></td><td class="num dev" id="d-{i}">–</td><td><code>{k}</code></td></tr>'
        for i, (a, b, v, k, _) in enumerate(nominal))
    html = (TEMPLATE.replace("/*TOP*/", top_view()).replace("/*SECTION*/", section_view())
            .replace("/*ROWS*/", rows)
            .replace("/*ROWSC*/", " / ".join(g(c) for c in pr.PP_ROWS)).replace("/*OFFS*/", " / ".join(("%+g" % o if o else "0").replace(".", ",").replace("-", "−") for o in pr.PP_OFF)).replace("/*YOFF*/", f(pr.PP_YOFF)).replace("/*HOLEX*/", g(pr.PP_HOLE))
            .replace("/*ROW1*/", g(pr.PP_ROWS[0])).replace("/*ROW2*/", g(pr.PP_ROWS[1])).replace("/*RABACK*/", f(sd.RA_BACK)).replace("/*RAPLUS*/", f(sd.RA_BACK + 0.4)).replace("/*RAMINUS*/", f(sd.RA_BACK - 0.4)).replace("/*HCH*/", g(pr.PP_HCH)).replace("/*HDRW*/", f(sd.HDR_W)).replace("/*CEIL*/", g(sd.CEIL)).replace("/*CH*/", g(pr.PP_CH))
            .replace("/*OPTS*/", "".join(f"<option>{g(c)}</option>" for c in pr.PP_ROWS))
            .replace("/*PW*/", f(pr.PP_W, 1)).replace("/*PL*/", f(pr.PP_L, 1)).replace("/*PH*/", f(pr.PP_H, 1))
            .replace("/*SNUG*/", f(sd.SNUG)).replace("/*HOLE*/", f(sd.HOLE, 1)).replace("/*RIB*/", f(sd.RIB)))
    out = os.path.join(HERE, "passprobe.html")
    open(out, "w", encoding="utf-8").write(html)
    print("%s  %.0f kB" % (os.path.relpath(out, os.path.join(HERE, "..", "..")), len(html.encode()) / 1024))


if __name__ == "__main__":
    main()
