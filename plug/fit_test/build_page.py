#!/usr/bin/env python3
"""Baut plug/fit_test/page.html aus page.template.html: Anleitung zur Passprobe mit Grafik im Maßstab.
Maße kommen aus plug/fit_test/generator.py (Passprobe) und plug/dupont.py bzw. plug/parts.py (Kaufteile).

Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m plug.fit_test.build_page
"""
import os

from plug import dupont as sd
from plug.fit_test import generator as pr

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))


def g(v):
    return ("%g" % v).replace(".", ",")


def f(v, n=2):
    return ("%.*f" % (n, v)).replace(".", ",").replace("-", "−")


# ---------------- SVG 1: Draufsicht auf die Schriftseite. Taschen öffnen sich nach unten und sind gestrichelt ----------------
def top_view():
    S, M = 14.0, 24
    W, H = pr.PP_W, pr.PP_L
    px = lambda x: M + (x + W / 2) * S
    py = lambda y: 14 + (H / 2 - y) * S          # y nach oben wie im Teil
    w_svg, h_svg = M * 2 + W * S, 14 + H * S + 40
    s = [f'<svg viewBox="0 0 {w_svg:.0f} {h_svg:.0f}" role="img" aria-label="Draufsicht der Passprobe: drei Felder mit Körpertasche, Lötendenschlitz und vier Pinlöchern, beschriftet mit der angenommenen Körperhöhe" width="{w_svg:.0f}" height="{h_svg:.0f}">']
    s.append(f'<rect x="{px(-W/2)}" y="{py(H/2)}" width="{W*S}" height="{H*S}" rx="3" class="blk"/>')
    yb, w, d = pr.PP_YB, sd.HDR_W + 2 * pr.PP_CLR, sd.HDR_T + 2 * pr.PP_CLR
    for h, x in zip(pr.PP_VAR, pr.PP_X):
        s.append(f'<rect x="{px(x-w/2)}" y="{py(yb+d/2)}" width="{w*S}" height="{d*S}" class="pocket b ghost"/>')
        s.append(f'<rect x="{px(x-pr.PP_SLOT_X)}" y="{py(yb+pr.PP_FWD)}" width="{2*pr.PP_SLOT_X*S}" height="{(pr.PP_FWD-d/2)*S}" class="trench"/>')
        s.append(f'<rect x="{px(x-pr.PP_SLOT_X)}" y="{py(yb-d/2)}" width="{2*pr.PP_SLOT_X*S}" height="{(pr.PP_BACK-d/2)*S}" class="trench"/>')
        for xp in sd.pin_x():
            cy = yb + pr.PP_YOFF
            s.append(f'<circle cx="{px(x+xp)}" cy="{py(cy)}" r="{(pr.PP_HOLE/2+pr.PP_HCH)*S:.1f}" class="csink"/>')
            s.append(f'<circle cx="{px(x+xp)}" cy="{py(cy)}" r="{pr.PP_HOLE*S/2:.1f}" class="hole b"/>')
        s.append(f'<text x="{px(x)}" y="{py(pr.PP_LAB)+6}" text-anchor="middle" class="eng big">{pr.pp_label(h)}</text>')
    # Beschriftung der Bereiche am ersten Feld
    x0 = pr.PP_X[0]
    s.append(f'<text x="{px(x0)}" y="{py(yb)+4}" text-anchor="middle" class="mut">Körpertasche</text>')
    s.append(f'<text x="{px(x0)}" y="{py(yb-pr.PP_BACK/2-0.3)+4}" text-anchor="middle" class="mut">Lötendenschlitz</text>')
    s.append(f'<text x="{px(x0 - sd.PITCH * 1.5 - 0.1)}" y="{py(yb+pr.PP_FWD)-6}" class="mut">Löcher</text>')
    s.append(f'<path class="dim" d="M{px(-W/2)} {py(-H/2)+14}v8M{px(W/2)} {py(-H/2)+14}v8M{px(-W/2)} {py(-H/2)+18}H{px(W/2)}"/>')
    s.append(f'<text x="{px(0)}" y="{py(-H/2)+36}" text-anchor="middle">{f(W,1)} × {f(H,1)} mm · Dicke {f(pr.PP_H,1)} mm</text>')
    s.append('</svg>')
    return "".join(s)


# ---------------- SVG 2: Schnitt durch ein Feld (Körperhöhe 2,0), Bestückung von unten. Schriftseite oben ----------------
def section_view():
    S = 30.0
    c = pr.PP_CLR
    H = pr.PP_H
    h = sd.HDR_BODY
    yb = 0.0                                              # Körpermitte als Nullpunkt der Zeichnung
    ymin, ymax = -pr.PP_BACK - 4.4, pr.PP_FWD + 2.2
    above, below = 6.6, 4.4
    M = 20
    px = lambda yv: M + (yv - ymin) * S
    pz = lambda z: 40 + (H + above - z) * S
    wv, hv = M + (ymax - ymin) * S + 300, 40 + (H + above + below) * S + 34
    s = [f'<svg viewBox="0 0 {wv:.0f} {hv:.0f}" role="img" aria-label="Schnitt durch das Feld 2,0: Körper an der Decke der Tasche, Pin in Körpermitte, Lötende liegt flach unter der Stufe, senkrechte Pins gehen durch die Löcher" width="{wv:.0f}" height="{hv:.0f}">']
    s.append(f'<rect x="{px(ymin)}" y="{pz(H)}" width="{(ymax-ymin)*S}" height="{H*S}" class="blk"/>')
    zb = H - pr.PP_FLOOR
    zm = zb - h / 2
    zs = pr.pp_step(h)
    T = sd.HDR_T
    hd = T / 2 + c
    y_leg = pr.PP_YOFF
    s.append(f'<rect x="{px(yb-hd)}" y="{pz(zb)}" width="{2*hd*S}" height="{zb*S}" class="cut"/>')
    s.append(f'<rect x="{px(yb)}" y="{pz(zb)}" width="{pr.PP_FWD*S}" height="{zb*S}" class="cut"/>')
    s.append(f'<rect x="{px(yb-pr.PP_BACK)}" y="{pz(zs)}" width="{pr.PP_BACK*S}" height="{zs*S}" class="cut"/>')
    hh = pr.PP_HOLE
    s.append(f'<rect x="{px(y_leg-hh/2)}" y="{pz(H)}" width="{hh*S}" height="{pr.PP_FLOOR*S}" class="cut"/>')
    cs, ch = pr.PP_HCH, pr.PP_CH
    s.append(f'<path d="M{px(y_leg-hh/2-cs)} {pz(H)}L{px(y_leg+hh/2+cs)} {pz(H)}L{px(y_leg+hh/2)} {pz(H-cs)}L{px(y_leg-hh/2)} {pz(H-cs)}Z" class="cut"/>')
    for sgn in (-1, 1):
        xe = yb + sgn * hd
        s.append(f'<path d="M{px(xe)} {pz(ch)}L{px(xe + sgn * ch)} {pz(0)}L{px(xe)} {pz(0)}Z" class="cut"/>')
    pin = sd.PIN_SQ
    zt = zm - pin / 2 + sd.HDR_LEG
    s.append(f'<rect x="{px(yb-T/2)}" y="{pz(zb)}" width="{T*S}" height="{h*S}" class="part b"/>')
    s.append(f'<path class="pinfill" d="M{px(yb-T/2-sd.RA_TAIL)} {pz(zm+pin/2)}H{px(y_leg+pin/2)}V{pz(zt)}H{px(y_leg-pin/2)}V{pz(zm-pin/2)}H{px(yb-T/2-sd.RA_TAIL)}Z"/>')

    def arrow(x, z0, z1):
        return (f'<path d="M{x} {pz(z0)}V{pz(z1)+4}" class="arrow"/><path d="M{x-5} {pz(z1)+10}L{x} {pz(z1)}L{x+5} {pz(z1)+10}" class="arrow"/>')

    def t(x, y, txt, anchor="start", cls=""):
        return f'<text x="{x}" y="{y}" text-anchor="{anchor}" class="{cls}">{txt}</text>'
    s.append(arrow(px(yb - 3.4), -2.4, -0.3))
    s.append(t(px(yb - 3.4) - 12, pz(-1.7), "von unten einsetzen", "end", "mut"))
    xs = yb - T / 2 - sd.RA_TAIL                         # Ende des Lötendes
    s.append(t(px(xs + sd.RA_TAIL / 2), pz(0.9), "Lötende 3 mm", "middle", "mut"))
    s.append(t(px(y_leg), pz(zt) - 10, "senkrechte Pins", "middle", "lab b"))
    # Stufe: Pfeil von oben auf die Stufenfläche zwischen Lötende und Schlitzende
    ys = (xs - pr.PP_BACK + yb) / 2 - T / 4 - 0.1        # Mitte zwischen Lötendenspitze und Schlitzende
    ys = (xs + (yb - pr.PP_BACK)) / 2
    s.append(f'<circle cx="{px(ys)}" cy="{pz(zs)}" r="3.5" class="dot"/>')
    s.append(f'<path class="lead" d="M{px(ys)} {pz(zs)}V{pz(H)-10}"/>')
    s.append(t(px(ys), pz(H) - 16, "Stufe", "middle", "lab a"))
    # Abstand Decke-Unterseite bis Stufe, links neben dem Schlitzende
    xd = px(yb - pr.PP_BACK) - 14
    s.append(f'<path class="dim" d="M{xd-5} {pz(zb)}h10M{xd-5} {pz(zs)}h10M{xd} {pz(zb)}V{pz(zs)}"/>')
    s.append(t(xd - 8, (pz(zb) + pz(zs)) / 2 + 4, f"{f(zb-zs)}", "end", "lab a"))
    # Pinvierkant
    xp = px(xs) - 12
    s.append(f'<path class="dim" d="M{xp-5} {pz(zm+pin/2)}h10M{xp-5} {pz(zm-pin/2)}h10M{xp} {pz(zm+pin/2)}V{pz(zm-pin/2)}"/>')
    s.append(t(xp - 8, pz(zm) + 4, f"{f(pin)}", "end"))
    yd = pz(0) + 30
    s.append(f'<path class="dim" d="M{px(yb+T/2)} {yd-5}v10M{px(y_leg-pin/2)} {yd-5}v10M{px(yb+T/2)} {yd}H{px(y_leg-pin/2)}"/>')
    s.append(t((px(yb + T / 2) + px(y_leg - pin / 2)) / 2, yd + 15, f"{f(sd.RA_BACK,1)}", "middle"))
    s.append(t(px(y_leg - pin / 2) + 6, yd + 4, f"Pin-Mitte {f(pr.PP_YOFF)} hinter der Körpermitte", "start", "mut"))
    xr = px(ymax) + 24
    def dimz(z0, z1, x, label):
        return f'<path class="dim" d="M{x-5} {pz(z0)}h10M{x-5} {pz(z1)}h10M{x} {pz(z0)}V{pz(z1)}"/>' + t(x + 9, (pz(z0)+pz(z1))/2 + 4, label)
    s.append(dimz(0, H, xr, f"Dicke {f(H,1)}"))
    s.append(dimz(zb - h, zb, xr + 100, f"Körper {f(h,1)}"))
    s.append(dimz(zb, H, xr + 100, f"Decke {f(pr.PP_FLOOR,1)}"))
    s.append(dimz(zm - pin / 2, zt, xr + 200, f"Pin {f(sd.HDR_LEG,0)}"))
    s.append('</svg>')
    return "".join(s)


TEMPLATE = open(os.path.join(HERE, "page.template.html"), encoding="utf-8").read()


def main():
    nominal = [
        ("Körper, Höhe (Richtung der Taschentiefe)", sd.HDR_BODY, "HDR_BODY", "bisher gemessen 2,0"),
        ("Körper, Dicke in Pin-Richtung", sd.HDR_T, "HDR_T", "gemessen 2"),
        ("Körper, Länge (4 Pins, abgebrochen)", sd.HDR_W, "HDR_W", "gemessen etwa 10,66"),
        ("Abstand Körperkante bis Innenkante des senkrechten Pins", sd.RA_BACK, "RA_BACK", "gemessen etwa 1"),
        ("Stiftvierkant", sd.PIN_SQ, "PIN_SQ", ""),
        ("Lötende vor dem Körper", sd.RA_TAIL, "RA_TAIL", "gemessen etwa 3"),
    ]
    rows = "".join(
        f'<tr><td>{b}</td><td class="num">{f(v)}</td><td><input class="meas" type="text" inputmode="decimal" autocomplete="off" '
        f'id="m-{i}" data-nom="{v}" data-k="{k}" data-name="{b}" aria-label="{b}, gemessen in mm"></td><td class="num dev" id="d-{i}">–</td><td><code>{k}</code></td></tr>'
        for i, (b, v, k, _) in enumerate(nominal))
    var_rows = "".join(
        f'<tr><td class="num"><b>{pr.pp_label(h)}</b></td><td class="num">{f(h/2)}</td><td class="num"><b>{f(h/2 - sd.PIN_SQ/2)}</b></td></tr>' for h in pr.PP_VAR)
    opts = "".join(f"<option>{pr.pp_label(h)}</option>" for h in pr.PP_VAR)
    html = (TEMPLATE.replace("/*TOP*/", top_view()).replace("/*SECTION*/", section_view())
            .replace("/*ROWS*/", rows).replace("/*VARROWS*/", var_rows).replace("/*VAROPTS*/", opts)
            .replace("/*V1*/", pr.pp_label(pr.PP_VAR[0])).replace("/*V2*/", pr.pp_label(pr.PP_VAR[1])).replace("/*V3*/", pr.pp_label(pr.PP_VAR[2]))
            .replace("/*D1*/", f(pr.PP_VAR[0]/2 - sd.PIN_SQ/2)).replace("/*D2*/", f(pr.PP_VAR[1]/2 - sd.PIN_SQ/2)).replace("/*D3*/", f(pr.PP_VAR[2]/2 - sd.PIN_SQ/2))
            .replace("/*CLR*/", f(pr.PP_CLR, 1)).replace("/*POCKW*/", f(sd.HDR_W + 2 * pr.PP_CLR)).replace("/*POCKT*/", f(sd.HDR_T + 2 * pr.PP_CLR))
            .replace("/*HOLE*/", f(pr.PP_HOLE, 1)).replace("/*YOFF*/", f(pr.PP_YOFF)).replace("/*HCH*/", f(pr.PP_HCH, 1))
            .replace("/*CEIL*/", f(sd.CEIL, 1)).replace("/*CH*/", f(pr.PP_CH, 1)).replace("/*UNDER*/", f(pr.PP_UNDER, 1))
            .replace("/*HDRT*/", f(sd.HDR_T, 1)).replace("/*HDRW*/", f(sd.HDR_W)).replace("/*HDRB*/", f(sd.HDR_BODY, 1)).replace("/*PIN*/", f(sd.PIN_SQ))
            .replace("/*PW*/", f(pr.PP_W, 1)).replace("/*PL*/", f(pr.PP_L, 1)).replace("/*PH*/", f(pr.PP_H, 1)).replace("/*RABACK*/", f(sd.RA_BACK, 1))
            .replace("/*STEPCLR*/", f(sd.STEP_CLR, 1)))
    out = os.path.join(HERE, "page.html")
    open(out, "w", encoding="utf-8").write(html)
    print("%s  %.0f kB" % (os.path.relpath(out, REPO), len(html.encode()) / 1024))


if __name__ == "__main__":
    main()
