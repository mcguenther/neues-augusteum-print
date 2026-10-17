"""Plan Hauptschalter (Wippenschalter 10 x 15 mm) in der Westwand des Unterkastens: `plug/power/plan_switch.html`.

Konzept, keine STL (Regel 2 im Logbuch: erst nach dem Abnicken). Die Maße des Fachs kommen aus `plug/power/params.py` und
`plug/power/build_concept.py`; die Schaltermaße stehen in `SW` (Nutzer grob gemessen, Rest geschätzt, Status je Wert).
Aufruf: `python3 -m plug.power.build_plan_switch` (Sekunden).
"""
import json
import os

from plug.power import build_concept as BC
from plug.power import params as PP

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "plan_switch.html")

# ---- Schalter KCD11 (Wippe 10 x 15, 2 Pins). M gemessen vom Nutzer, A aus Foto abgeleitet, S geschätzt, Q Händlerangaben
SW = dict(
    body_w=8.0, body_l=13.0,             # M  Kasten, der in der Wand verschwindet (Nutzer grob)
    flange_w=10.0, flange_l=15.0,        # M  Frontplatte, etwa 1 mm Rand je Seite (Nutzer)
    flange_t=1.2,                        # S  Dicke der Frontplatte
    rocker=3.0,                          # S  Wippe über der Frontplatte
    body_depth=9.0,                      # A  Kasten ab Außenfläche der Wand (Foto 1: ca. 8,5 bis 9,5)
    pin_len=7.0,                         # A  Pins hinter dem Kasten (Foto 1: ca. 6,9)
    pin_pitch=4.8,                       # A  Pinabstand (Foto 4)
    wire=4.0,                            # E  Platz für Lötstelle, Schrumpfschlauch und Biegung
)
HOLE_CLR = 0.15                          # E  Spiel je Seite, wie der Nutzer-Vorgabe 0,15 bei Passungen (r8)
HOLE = (SW["body_l"] + 2 * HOLE_CLR, SW["body_w"] + 2 * HOLE_CLR)   # 13,3 x 8,3 (Händler nennen 13,5 x 8,5 bis 9)
WALL_AT_HOLE = 1.6                       # S  Wand am Loch (Schnapphaken brauchen etwa 0,8 bis 2,0; Messung offen)
POCKET = (HOLE[0] + 4.0, HOLE[1] + 3.0)  # E  Innentasche: lässt die Haken beim Einschnappen ausfedern
POCKET_T = PP.UK_WALL - WALL_AT_HOLE     # 0,8 tief
H_WALL = BC.H0["uk_t"]                   # 14,6 Außenhöhe des Unterkastens
Z_MID = H_WALL / 2
DEPTH_OUT = SW["body_depth"] + SW["pin_len"] + SW["wire"]               # ab Außenfläche
LAYOUT = json.load(open(os.path.join(HERE, "switch_layout.json")))   # Lage aus build_concept.variant(1300), Platte 115,6 × 220,8
FACH_X0 = min(p[0] for p in LAYOUT["fach"][0])                          # Westkante des Fachs (22,4); Plattenaußenwand liegt bei x = 0
Y_SW = 116.0                                                            # E  Mitte des Schalters auf der Platte (Nord = größeres y), unter dem Südende des Seminargebäudes
MARGIN = round(FACH_X0 - DEPTH_OUT, 1)                                  # Luft zwischen den Pins mit Draht und dem Fach


def f(x):
    return f"{x:.1f}"


# ---------------------------------------------------------------- Bild 1: Platte von oben (Norden oben), Unterkasten darunter
def _path(rings, X, Y):
    return " ".join("M" + " L".join(f"{f(X(x))},{f(Y(y))}" for x, y in r) + " Z" for r in rings)


def fig_plate():
    s = 2.4
    PW, PL = LAYOUT["plate"]
    ox, oy = 76, 24
    X = lambda x: ox + x * s                  # noqa: E731
    Y = lambda y: oy + (PL - y) * s           # noqa: E731
    W, Hh = ox + PW * s + 96, oy + PL * s + 24
    t = [f'<svg viewBox="0 0 {f(W)} {f(Hh)}" role="img" aria-label="Unterkasten der Campus-Platte von oben mit Schalter an der Westwand">']
    t.append(f'<path class="wall" d="{_path(LAYOUT["outline"], X, Y)}"/>')
    for b in LAYOUT["buildings"]:
        hot = b["slug"] in ("01_paulinum", "04_seminargebaeude")
        t.append(f'<path class="bld{" hot" if hot else ""}" d="{_path(b["poly"], X, Y)}"/>')
    t.append(f'<path class="bld" d="{_path(LAYOUT["hof"], X, Y)}" stroke-dasharray="3 2"/>')
    t.append(f'<path class="fach" d="{_path(LAYOUT["fach"], X, Y)}"/>')
    t.append(f'<path class="chan" d="{_path(LAYOUT["channel"], X, Y)}"/>')
    t.append(f'<path class="pb" d="{_path(LAYOUT["body"], X, Y)}"/>')
    t.append(f'<path class="elec" d="{_path(LAYOUT["elec"], X, Y)}"/>')
    t.append(f'<path class="win" d="{_path(LAYOUT["window"], X, Y)}"/>')
    t.append('<polyline class="cab" points="' + " ".join(f"{f(X(x))},{f(Y(y))}" for x, y in LAYOUT["cable"]) + '"/>')
    # Schalter an der Westwand
    t.append(f'<rect class="swf" x="{f(X(-1.5))}" y="{f(Y(Y_SW + SW["flange_l"] / 2))}" width="{f(1.5 * s + 2)}" height="{f(SW["flange_l"] * s)}"/>')
    t.append(f'<rect class="sw" x="{f(X(0))}" y="{f(Y(Y_SW + SW["body_l"] / 2))}" width="{f(SW["body_depth"] * s)}" height="{f(SW["body_l"] * s)}"/>')
    t.append(f'<line class="swlead" x1="{f(X(-2))}" y1="{f(Y(Y_SW))}" x2="{f(X(-2) - 8)}" y2="{f(Y(Y_SW))}"/>')
    t.append(f'<text class="hl" x="{f(X(-2) - 12)}" y="{f(Y(Y_SW) + 4)}" text-anchor="end">Schalter</text>')
    # Beschriftung (Name in der Mitte des Grundrisses)
    for b in LAYOUT["buildings"]:
        if b["slug"] in ("01_paulinum", "04_seminargebaeude"):
            ring = max(b["poly"], key=len)
            cx = sum(p[0] for p in ring) / len(ring)
            cy = sum(p[1] for p in ring) / len(ring)
            name = "Paulinum" if b["slug"] == "01_paulinum" else "Seminar"
            t.append(f'<text class="lbl" x="{f(X(cx))}" y="{f(Y(cy) + 4)}" text-anchor="middle">{name}</text>')
    fx = sum(p[0] for p in LAYOUT["body"][0]) / 4
    t.append(f'<text class="lbl" x="{f(X(fx))}" y="{f(Y(150))}" text-anchor="middle">Powerbank</text>')
    ex = sum(p[0] for p in LAYOUT["elec"][0]) / 4
    t.append(f'<text class="lbl" x="{f(X(ex))}" y="{f(Y(70) + 4)}" text-anchor="middle">Elektronik</text>')
    t.append(f'<text class="lbl" x="{f(X(PW / 2))}" y="{f(oy - 8)}" text-anchor="middle">Nord, Anschlussseite der Powerbank (Plattenkante)</text>')
    t.append(f'<text class="lbl" x="{f(X(0))}" y="{f(Hh - 6)}">West</text>')
    t.append(f'<text class="lbl" x="{f(X(PW))}" y="{f(Hh - 6)}" text-anchor="end">Ost</text>')
    t.append("</svg>")
    return "".join(t)


# ---------------------------------------------------------------- Bild 1b: Ausschnitt um den Schalter
def fig_detail():
    s = 9.0
    x0, x1, y0, y1 = -3.0, 46.0, 84.0, 134.0
    X = lambda x: 80 + (x - x0) * s           # noqa: E731
    Y = lambda y: 30 + (y1 - y) * s           # noqa: E731
    W, Hh = X(x1) + 20, Y(y0) + 30
    t = [f'<svg viewBox="0 0 {f(W)} {f(Hh)}" role="img" aria-label="Ausschnitt Draufsicht um den Schalter">']
    t.append(f'<rect class="wall" x="{f(X(0))}" y="{f(Y(y1))}" width="{f(PP.UK_WALL * s)}" height="{f((y1 - y0) * s)}"/>')
    # Fach (ab y 92,4), Kabelkanal, Elektronikbox
    fx0, fy0 = FACH_X0, min(p[1] for p in LAYOUT["fach"][0])
    t.append(f'<rect class="fach" x="{f(X(fx0))}" y="{f(Y(y1))}" width="{f((x1 - fx0) * s)}" height="{f((y1 - fy0) * s)}"/>')
    t.append(f'<rect class="chan" x="{f(X(fx0))}" y="{f(Y(y1))}" width="{f(PP.PB_CABLE * s)}" height="{f((y1 - fy0) * s)}"/>')
    ex1 = max(p[1] for p in LAYOUT["elec"][0])
    t.append(f'<rect class="elec" x="{f(X(3.4))}" y="{f(Y(ex1))}" width="{f((x1 - 3.4) * s)}" height="{f((ex1 - y0) * s)}"/>')
    cx = LAYOUT["cable"][-1][0]
    t.append(f'<polyline class="cab" points="{f(X(cx))},{f(Y(y1))} {f(X(cx))},{f(Y(y0))}"/>')
    t.append(f'<text class="lbl" x="{f(X(fx0 + 7))}" y="{f(Y(y1) + 14)}">Fach, Powerbank ab x {f(fx0)}</text>')
    t.append(f'<text class="lbl" x="{f(X(fx0 + 7))}" y="{f(Y(fy0) - 6)}">hinten, y {f(fy0)}</text>')
    t.append(f'<text class="lbl" x="{f(X(6))}" y="{f(Y(ex1 - 4))}">Elektronik (ESP, INA226)</text>')
    t.append(f'<text class="lbl" x="{f(X(cx) + 6)}" y="{f(Y(104))}">Kabel</text>')
    # Seminargebäude (Mulde darüber) gestrichelt
    sem = next(b for b in LAYOUT["buildings"] if b["slug"] == "04_seminargebaeude")
    t.append(f'<path class="bld hot" d="{_path(sem["poly"], X, Y)}" clip-path="url(#cl)"/>')
    t.append(f'<clipPath id="cl"><rect x="{f(X(x0))}" y="{f(Y(y1))}" width="{f((x1 - x0) * s)}" height="{f((y1 - y0) * s)}"/></clipPath>')
    # Schalter
    ys = Y_SW
    t.append(f'<rect class="swf" x="{f(X(-SW["flange_t"]))}" y="{f(Y(ys + SW["flange_l"] / 2))}" width="{f(SW["flange_t"] * s)}" height="{f(SW["flange_l"] * s)}"/>')
    t.append(f'<rect class="sw" x="{f(X(0))}" y="{f(Y(ys + SW["body_l"] / 2))}" width="{f(SW["body_depth"] * s)}" height="{f(SW["body_l"] * s)}"/>')
    for k in (-0.5, 0.5):
        yy = Y(ys + k * SW["pin_pitch"])
        t.append(f'<line class="pin" x1="{f(X(SW["body_depth"]))}" x2="{f(X(SW["body_depth"] + SW["pin_len"]))}" y1="{f(yy)}" y2="{f(yy)}"/>')
    pin_n = Y(ys + SW["pin_pitch"] / 2)
    t.append(f'<polyline class="wire" points="{f(X(SW["body_depth"] + SW["pin_len"]))},{f(pin_n)} {f(X(18))},{f(pin_n)} {f(X(18))},{f(Y(fy0 + 4))} {f(X(cx))},{f(Y(fy0 + 4))}"/>')
    pin_s = Y(ys - SW["pin_pitch"] / 2)
    t.append(f'<polyline class="wire" points="{f(X(SW["body_depth"] + SW["pin_len"]))},{f(pin_s)} {f(X(12))},{f(pin_s)} {f(X(12))},{f(Y(ex1))}"/>')
    t.append(f'<text class="hl" x="{f(X(-SW["flange_t"]) - 4)}" y="{f(Y(ys) + 4)}" text-anchor="end">Schalter</text>')
    t.append(f'<text class="lbl" x="{f(X(-SW["flange_t"]) - 4)}" y="{f(Y(ys) + 18)}" text-anchor="end">y = {f(Y_SW)}</text>')
    # Maßlinie Einbautiefe
    ym = Y(ys + SW["flange_l"] / 2) - 22
    t.append(f'<line class="dim" x1="{f(X(0))}" x2="{f(X(DEPTH_OUT))}" y1="{f(ym)}" y2="{f(ym)}"/>'
             f'<text class="lbl" x="{f(X(0))}" y="{f(ym - 6)}">Einbautiefe {f(DEPTH_OUT)}, Luft zum Fach {f(MARGIN)}</text>')
    t.append("</svg>")
    return "".join(t)


# ---------------------------------------------------------------- Bild 2: Schnitt durch die Schalterachse
def fig_section():
    s = 13.0
    ox, oy = 150, 36
    Z = lambda z: oy + (H_WALL - z) * s       # noqa: E731
    D = lambda d: ox + d * s                  # d = Tiefe ab Außenfläche der Wand nach innen   # noqa: E731
    W = D(DEPTH_OUT + 6) + 10
    Hh = Z(0) + 56
    zc = Z_MID
    t = [f'<svg viewBox="0 0 {f(W)} {f(Hh)}" role="img" aria-label="Schnitt durch Rückwand und Schalter">']
    # Wand mit Loch und Tasche (Schnitt in der Höhenrichtung, Wand außen links)
    hh = HOLE[1]
    wall_pts = [
        (0, 0), (PP.UK_WALL, 0), (PP.UK_WALL, zc - POCKET[1] / 2), (WALL_AT_HOLE, zc - POCKET[1] / 2), (WALL_AT_HOLE, zc - hh / 2),
        (0, zc - hh / 2)]
    top_pts = [
        (0, zc + hh / 2), (WALL_AT_HOLE, zc + hh / 2), (WALL_AT_HOLE, zc + POCKET[1] / 2), (PP.UK_WALL, zc + POCKET[1] / 2),
        (PP.UK_WALL, H_WALL), (0, H_WALL)]
    for pts in (wall_pts, top_pts):
        t.append('<polygon class="wall" points="' + " ".join(f"{f(D(d))},{f(Z(z))}" for d, z in pts) + '"/>')
    # Boden des Unterkastens, Oberplatte
    t.append(f'<rect class="wall" x="{f(D(PP.UK_WALL))}" y="{f(Z(PP.UK_FLOOR))}" width="{f(DEPTH_OUT * s)}" height="{f(PP.UK_FLOOR * s)}"/>')
    t.append(f'<rect class="plate" x="{f(D(0))}" y="{f(Z(H_WALL) - 12)}" width="{f((DEPTH_OUT + 4) * s)}" height="12"/>')
    t.append(f'<text class="lbl" x="{f(D(DEPTH_OUT + 4))}" y="{f(Z(H_WALL) - 16)}" text-anchor="end">Oberplatte</text>')
    # Schalter
    fl = SW["flange_w"]
    t.append(f'<rect class="swf" x="{f(D(-SW["flange_t"]))}" y="{f(Z(zc + fl / 2))}" width="{f(SW["flange_t"] * s)}" height="{f(fl * s)}"/>')
    t.append(f'<rect class="sw" x="{f(D(0))}" y="{f(Z(zc + SW["body_w"] / 2))}" width="{f(SW["body_depth"] * s)}" height="{f(SW["body_w"] * s)}"/>')
    t.append(f'<polygon class="sw" points="{f(D(-SW["flange_t"]))},{f(Z(zc + 2.2))} {f(D(-SW["flange_t"] - SW["rocker"]))},{f(Z(zc + 1.2))} '
             f'{f(D(-SW["flange_t"] - SW["rocker"]))},{f(Z(zc - 3.0))} {f(D(-SW["flange_t"]))},{f(Z(zc - 3.0))}"/>')
    # Haken
    for sgn in (1, -1):
        zz = zc + sgn * SW["body_w"] / 2
        t.append(f'<polygon class="hook" points="{f(D(WALL_AT_HOLE))},{f(Z(zz))} {f(D(WALL_AT_HOLE + 0.9))},{f(Z(zz))} '
                 f'{f(D(WALL_AT_HOLE))},{f(Z(zz + sgn * 0.7))}"/>')
    # Pins + Draht
    t.append(f'<line class="pin" x1="{f(D(SW["body_depth"]))}" x2="{f(D(SW["body_depth"] + SW["pin_len"]))}" y1="{f(Z(zc + 1))}" y2="{f(Z(zc + 1))}"/>')
    t.append(f'<path class="wire" d="M {f(D(SW["body_depth"] + SW["pin_len"] - 1))} {f(Z(zc + 1))} q 40 0 60 30"/>')
    # Powerbank
    # Maße
    t.append(f'<line class="dim" x1="{f(D(0))}" x2="{f(D(WALL_AT_HOLE))}" y1="{f(Z(0) + 14)}" y2="{f(Z(0) + 14)}"/>'
             f'<text class="lbl" x="{f(D(0))}" y="{f(Z(0) + 28)}">Wand am Loch {f(WALL_AT_HOLE)}</text>')
    t.append(f'<line class="dim" x1="{f(D(0))}" x2="{f(D(DEPTH_OUT))}" y1="{f(Z(0) + 42)}" y2="{f(Z(0) + 42)}"/>'
             f'<text class="lbl" x="{f(D(DEPTH_OUT / 2))}" y="{f(Z(0) + 53)}" text-anchor="middle">Einbautiefe ab Außenfläche ≈ {f(DEPTH_OUT)}</text>')
    t.append(f'<text class="lbl" x="{f(D(-SW["flange_t"] - SW["rocker"]) - 6)}" y="{f(Z(zc) + 4)}" text-anchor="end">außen</text>')
    t.append(f'<text class="lbl" x="{f(D(PP.UK_WALL + 1.2))}" y="{f(Z(zc + POCKET[1] / 2) - 6)}">Innentasche {f(POCKET[0])} × {f(POCKET[1])}, {f(POCKET_T)} tief</text>')
    t.append("</svg>")
    return "".join(t)


# ---------------------------------------------------------------- Bild 3: Ansicht von außen
def fig_front():
    s = 11.0
    ox, oy = 48, 40
    Wp = 40.0
    X = lambda v: ox + (Wp / 2 - (v - Y_SW)) * s    # noqa: E731   von außen gesehen liegt Norden links
    Z = lambda z: oy + (H_WALL - z) * s            # noqa: E731
    W = ox + Wp * s + 36
    Hh = Z(0) + 36
    zc = Z_MID
    cx = X(Y_SW)
    t = [f'<svg viewBox="0 0 {f(W)} {f(Hh)}" role="img" aria-label="Westwand von außen mit Schalterausschnitt">']
    t.append(f'<rect class="wall" x="{f(ox)}" y="{f(Z(H_WALL))}" width="{f(Wp * s)}" height="{f(H_WALL * s)}"/>')
    t.append(f'<rect class="pocket" x="{f(cx - POCKET[0] / 2 * s)}" y="{f(Z(zc + POCKET[1] / 2))}" width="{f(POCKET[0] * s)}" height="{f(POCKET[1] * s)}"/>')
    t.append(f'<rect class="swf" x="{f(cx - SW["flange_l"] / 2 * s)}" y="{f(Z(zc + SW["flange_w"] / 2))}" width="{f(SW["flange_l"] * s)}" height="{f(SW["flange_w"] * s)}" fill-opacity=".55"/>')
    t.append(f'<rect class="hole" x="{f(cx - HOLE[0] / 2 * s)}" y="{f(Z(zc + HOLE[1] / 2))}" width="{f(HOLE[0] * s)}" height="{f(HOLE[1] * s)}"/>')
    # Maße
    def hdim(x0, x1, y, txt):
        return (f'<line class="dim" x1="{f(x0)}" x2="{f(x1)}" y1="{f(y)}" y2="{f(y)}"/>'
                f'<text class="lbl" x="{f((x0 + x1) / 2)}" y="{f(y + 13)}" text-anchor="middle">{txt}</text>')
    t.append(hdim(cx - HOLE[0] / 2 * s, cx + HOLE[0] / 2 * s, Z(0) + 10, f"Loch {f(HOLE[0])}"))
    t.append(f'<line class="dim" x1="{f(ox + Wp * s + 10)}" x2="{f(ox + Wp * s + 10)}" y1="{f(Z(zc + HOLE[1] / 2))}" y2="{f(Z(zc - HOLE[1] / 2))}"/>'
             f'<text class="lbl" x="{f(ox + Wp * s + 14)}" y="{f(Z(zc) + 4)}">{f(HOLE[1])}</text>')
    t.append(f'<line class="dim" x1="{f(ox - 10)}" x2="{f(ox - 10)}" y1="{f(Z(H_WALL))}" y2="{f(Z(0))}"/>'
             f'<text class="lbl" x="{f(ox - 14)}" y="{f(Z(zc) + 4)}" text-anchor="end">{f(H_WALL)}</text>')
    t.append(f'<text class="lbl" x="{f(cx)}" y="{f(Z(zc + POCKET[1] / 2) - 8)}" text-anchor="middle">Frontplatte 15 × 10 liegt außen auf</text>')
    t.append("</svg>")
    return "".join(t)


def rows(data):
    return "".join(f"<tr><td>{a}</td><td class='n'>{b}</td><td><span class='st st-{c[0]}'>{c[0]}</span> {c[1:]}</td></tr>" for a, b, c in data)


def build():
    dims = [
        ("Kasten (verschwindet in der Wand), B × L", f"{f(SW['body_w'])} × {f(SW['body_l'])}", "M vom Nutzer grob gemessen; Händler: Ausschnitt 13,5 × 8,5 bis 9"),
        ("Frontplatte B × L (Rand etwa 1 je Seite)", f"{f(SW['flange_w'])} × {f(SW['flange_l'])}", "M Nutzer; passt zur Bauform 10 × 15 (KCD11)"),
        ("Loch in der Wand (Spiel 0,15 je Seite)", f"{f(HOLE[0])} × {f(HOLE[1])}", "E vom Nutzer übernommen; Testprobe T1 prüft 13,1 / 13,3 / 13,5"),
        ("Wand am Loch", f"{f(WALL_AT_HOLE)}", "S Schnapphaken greifen je nach Typ bei 0,8 bis 2,0; Abstand Frontplatte bis Hakenkante messen"),
        ("Außenwand sonst, Innentasche", f"{f(PP.UK_WALL)} / {f(POCKET[0])} × {f(POCKET[1])} × {f(POCKET_T)}", "E Tasche von innen, damit die Haken ausfedern können"),
        ("Höhe der Wand außen / Schaltermitte", f"{f(H_WALL)} / {f(Z_MID)}", f"A Unterkasten im Plan 1:1300 (Platte 14,6 + Unterkasten {f(H_WALL)} = {f(LAYOUT['thick'])}), Frontplatte 10 hoch lässt je {f((H_WALL - 10) / 2)} Rand"),
        ("Lage auf der Platte", f"Westwand, y = {f(Y_SW)}", "E unter dem Südende des Seminargebäudes (y 108 bis 185), 20 mm vor der Elektronik (y bis 88,4)"),
        ("Einbautiefe ab Außenfläche", f"≈ {f(DEPTH_OUT)}", f"A Kasten {f(SW['body_depth'])} + Pins {f(SW['pin_len'])} (aus Foto) + {f(SW['wire'])} Lötstelle und Biegung"),
        ("Platz bis zum Fach (Westkante x = %s)" % f(FACH_X0), f"{f(FACH_X0)} frei, Luft {f(MARGIN)}", "A Streifen westlich des Fachs, an der Stelle ohne Stützen, Zapfen und Dockzone"),
    ]
    html = f"""<title>Hauptschalter Westwand</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>
/* Layout: Zeichenblatt, Platte und Ausschnitt oben, Schnitt und Ansicht nebeneinander, darunter Maßtabelle und Entscheidungskarten */
:root {{
  --bg:#f3f5f6; --paper:#ffffff; --ink:#1d2a33; --mute:#5d6c76; --line:#c9d2d8;
  --wall:#cdd7de; --wallline:#44525c; --accent:#d9480f; --accent-soft:#fde8dc; --ok:#2b7a4b; --warn:#a86a00; --pb:#dfe6ea; --chan:#e7f0f6;
  --font-sans:"IBM Plex Sans",system-ui,sans-serif; --font-mono:"IBM Plex Mono",ui-monospace,monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg:#12181c; --paper:#1a2227; --ink:#e4ebef; --mute:#97a6b0; --line:#34414a;
  --wall:#2b3840; --wallline:#8fa2ae; --accent:#ff8a4c; --accent-soft:#3a2417; --ok:#6cc790; --warn:#e0a53a; --pb:#26323a; --chan:#1f2d37; color-scheme:dark; }} }}
:root[data-theme="dark"] {{
  --bg:#12181c; --paper:#1a2227; --ink:#e4ebef; --mute:#97a6b0; --line:#34414a;
  --wall:#2b3840; --wallline:#8fa2ae; --accent:#ff8a4c; --accent-soft:#3a2417; --ok:#6cc790; --warn:#e0a53a; --pb:#26323a; --chan:#1f2d37; color-scheme:dark; }}
body {{ background:var(--bg); color:var(--ink); font-family:var(--font-sans); font-size:15px; line-height:1.5;
  padding-block:24px 48px; padding-left:max(16px, env(safe-area-inset-left, 0px)); padding-right:max(16px, env(safe-area-inset-right, 0px)); }}
main {{ max-width:1080px; margin:0 auto; display:flex; flex-direction:column; gap:28px; }}
h1 {{ font-size:28px; line-height:1.2; margin:0; text-wrap:balance; }}
h2 {{ font-size:18px; margin:0 0 4px; text-wrap:balance; }}
p {{ margin:0; max-width:70ch; }}
.kicker {{ font-family:var(--font-mono); font-size:12px; letter-spacing:.08em; text-transform:uppercase; color:var(--mute); }}
.sheet {{ background:var(--paper); border:1px solid var(--line); padding:16px; display:flex; flex-direction:column; gap:10px; min-width:0; }}
.scroll {{ overflow-x:auto; }}
.row {{ display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr); gap:16px; }}
@media (max-width:820px) {{ .row {{ grid-template-columns:minmax(0,1fr); }} }}
svg {{ display:block; width:100%; height:auto; max-width:560px; margin:0 auto; }}
svg .wall {{ fill:var(--wall); stroke:var(--wallline); stroke-width:1.2; }}
svg .fach {{ fill:var(--paper); stroke:var(--wallline); stroke-width:.8; }}
svg .win {{ fill:var(--paper); stroke:var(--accent); stroke-width:1; stroke-dasharray:3 2; }}
svg .chan {{ fill:var(--chan); stroke:var(--line); }}
svg .bld {{ fill:none; stroke:var(--mute); stroke-width:.8; }}
svg .bld.hot {{ stroke:var(--accent); stroke-width:1.2; stroke-dasharray:4 3; }}
svg .elec {{ fill:var(--chan); stroke:var(--wallline); stroke-dasharray:5 3; }}
svg .swlead {{ stroke:var(--accent); stroke-width:1.2; }}
svg .pb {{ fill:var(--pb); stroke:var(--wallline); stroke-width:1; }}
svg .plate {{ fill:var(--pb); stroke:var(--wallline); }}
svg .cab {{ fill:none; stroke:var(--mute); stroke-width:2; stroke-linecap:round; stroke-linejoin:round; }}
svg .sw, svg .swf {{ fill:var(--accent); stroke:var(--ink); stroke-width:1; }}
svg .swf {{ fill-opacity:.85; }}
svg .hook {{ fill:var(--ink); }}
svg .pin {{ stroke:var(--ink); stroke-width:2.2; }}
svg .wire {{ fill:none; stroke:var(--accent); stroke-width:2; stroke-linejoin:round; }}
svg .pocket {{ fill:var(--paper); stroke:var(--wallline); stroke-dasharray:4 3; }}
svg .hole {{ fill:var(--bg); stroke:var(--ink); stroke-width:1.4; }}
svg .dim {{ stroke:var(--mute); stroke-width:1; }}
svg text {{ font-family:var(--font-mono); font-size:11px; fill:var(--ink); }}
svg .lbl {{ fill:var(--mute); }}
svg .hl {{ fill:var(--accent); font-weight:500; }}
table {{ border-collapse:collapse; width:100%; font-size:14px; }}
th, td {{ text-align:left; padding:7px 10px; border-bottom:1px solid var(--line); vertical-align:top; }}
th {{ font-family:var(--font-mono); font-size:11px; letter-spacing:.06em; text-transform:uppercase; color:var(--mute); font-weight:500; }}
td.n {{ font-family:var(--font-mono); white-space:nowrap; font-variant-numeric:tabular-nums; }}
.st {{ display:inline-block; font-family:var(--font-mono); font-size:11px; font-weight:500; min-width:1.5em; text-align:center; padding:0 5px; border:1px solid var(--line); margin-right:6px; }}
.st-M, .st-B {{ color:var(--ok); border-color:var(--ok); }}
.st-S, .st-A {{ color:var(--warn); border-color:var(--warn); }}
.st-E {{ color:var(--accent); border-color:var(--accent); }}
.cards {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:14px; }}
.card {{ background:var(--paper); border:1px solid var(--line); padding:14px; display:flex; flex-direction:column; gap:8px; min-width:0; }}
.card h3 {{ font-size:15px; margin:0; }}
.card ul {{ margin:0; padding-left:18px; display:flex; flex-direction:column; gap:4px; }}
.card .pick {{ background:var(--accent-soft); border:1px solid var(--accent); padding:6px 8px; font-size:13px; }}
.note {{ border-left:3px solid var(--accent); padding:4px 0 4px 12px; }}
.circ {{ font-family:var(--font-mono); font-size:13px; white-space:pre; overflow-x:auto; background:var(--bg); border:1px solid var(--line); padding:10px 12px; }}
a {{ color:var(--accent); }}
</style>
<main>
<header style="display:flex;flex-direction:column;gap:8px">
  <div class="kicker">Plan · Konzept, noch keine STL · Stand 17.10.2026 · Platte 1:1300</div>
  <h1>Hauptschalter in der Westwand des Unterkastens</h1>
  <p>Wippenschalter 10 × 15 mm (KCD11, 2 Pins) schaltet das Plus der Powerbank. Er sitzt in der Außenwand des Unterkastens auf der Seite gegenüber dem Paulinum, unter dem Seminargebäude, und schnappt von außen in ein Loch von {f(HOLE[0])} × {f(HOLE[1])} mm. Das Kabel geht von dort zum INA226 in der Elektronik.</p>
</header>

<div class="row">
  <section class="sheet">
    <h2>Unterkasten von oben, Norden oben</h2>
    <p>Die Platte ist 115,6 × 220,8 mm; der Unterkasten ist gleich groß und hat die Plattenkante als Außenwand. Das Paulinum liegt im Osten, das Seminargebäude im Westen. Die Gebäude stecken oben in der Platte, der Unterkasten liegt darunter.</p>
    <div class="scroll">{fig_plate()}</div>
  </section>
  <section class="sheet">
    <h2>Ausschnitt um den Schalter, 10 : 1</h2>
    <p>Westlich vom Fach bleiben {f(FACH_X0)} mm frei, ohne Stützen, Zapfen und Dockzone. Der Schalter braucht {f(DEPTH_OUT)} mm. Die Drähte laufen zum Kabel im Kanal und zur Elektronik. Orange gestrichelt: das Seminargebäude in der Platte darüber.</p>
    <div class="scroll">{fig_detail()}</div>
  </section>
</div>

<div class="row">
  <section class="sheet">
    <h2>Schnitt durch die Schalterachse, 13 : 1</h2>
    <p>Außenwand links. Die Haken (schwarz) fassen hinter der {f(WALL_AT_HOLE)} mm dünnen Wand am Loch; die Innentasche gibt ihnen Platz zum Ausfedern.</p>
    <div class="scroll">{fig_section()}</div>
  </section>
  <section class="sheet">
    <h2>Westwand von außen, 11 : 1</h2>
    <p>Wand {f(H_WALL)} hoch, Frontplatte 10 hoch. Langseite waagerecht: Stehend (13,3 hoch) blieben nur 2 mm Wand oben und unten. Norden liegt links.</p>
    <div class="scroll">{fig_front()}</div>
  </section>
</div>

<section class="sheet">
  <h2>Warum dort</h2>
  <table>
    <tr><th>Stelle</th><th>Urteil</th></tr>
    <tr><td>Westwand, y = {f(Y_SW)}</td><td><b>Vorschlag.</b> Gegenüber dem Paulinum, von außen erreichbar, ohne Ausbuchtung: Der Streifen bis zum Fach ist {f(FACH_X0)} mm breit und der Schalter braucht {f(DEPTH_OUT)}. Das Kabel liegt im Kanal (x 25,4), die Elektronik beginnt bei y = 88,4.</td></tr>
    <tr><td>Ostwand (Paulinum-Seite)</td><td>Auch möglich, der Streifen ist 23 mm breit. Entfällt nach deiner Vorgabe, außerdem läge das Kabel dann auf der falschen Seite des Fachs.</td></tr>
    <tr><td>Südwand</td><td>Dahinter liegt die Elektronik direkt an der Wand (x 3 bis 63, y 53 bis 88), kein Platz.</td></tr>
    <tr><td>Nordwand (Plattenkante, Anschlussseite)</td><td>Fenster für LEDs und Buchsen, dann USB-A-Stecker und Kabelkanal belegen die Breite.</td></tr>
  </table>
  <p class="note"><b>Zu klären:</b> Der Unterkasten ist hohl und hat an dieser Stelle keine Stützen. Die Wand ist 2,4 mm dick, mit Tasche 1,6 mm. Ob sie dort steif genug ist, zeigt die Probe T1. Die Stützen-Raster (Kante 6, alle 40 mm) liegen ohnehin weiter innen.</p>
</section>

<section class="sheet">
  <h2>Maße und Maßkette</h2>
  <div class="scroll"><table>
    <tr><th>Größe</th><th>Wert in mm</th><th>Status und Herkunft</th></tr>
    {rows([(a, b, c) for a, b, c in dims])}
  </table></div>
  <p>Status: M gemessen, A abgeleitet, S geschätzt, E Entscheidung, wie im Logbuch. Der Händler-Ausschnitt 13,5 × 8,5 bis 9 stammt aus Angeboten für den KCD11 (<a href="https://makerselectronics.com/product/kcd11-101-on-off-switch-250v-3a/">Makers Electronics</a>, <a href="https://www.ebay.com/p/13026640396">eBay</a>). Eine Plattenstärke für den Einschnapp-Sitz steht dort nicht. Lage der Teile aus `plug/power/build_concept.py` (Stand 1:1300, Fach an der Nordkante, Spiegelung sgn −1).</p>
</section>

<section class="sheet">
  <h2>Verdrahtung</h2>
  <div class="circ">Powerbank USB  ──rot (+5 V)──▶ [ Schalter ] ──▶ INA226 VIN+ ──(Shunt)── VIN− ──▶ ESP32 und LEDs
Powerbank USB  ──schwarz (GND)────────────────────────▶ INA226 GND / gemeinsame Masse</div>
  <p>Der Schalter liegt vor dem Shunt, damit der INA226 beim Ausschalten stromlos ist. Auf dem Schalter steht 3 A bei 250 V AC; bei 5 V und höchstens 2,1 A (Powerbank) ist das reichlich. Das Kabel wird im Kanal bei y ≈ 95 aufgetrennt, der rote Draht läuft zum Schalter und von dort zur Elektronik. Lötstellen mit Schrumpfschlauch isolieren.</p>
</section>

<section>
  <h2 style="margin-bottom:12px">Entscheidungen</h2>
  <div class="cards">
    <div class="card"><h3>1. Lage entlang der Westwand</h3>
      <ul><li><b>A</b> y = {f(Y_SW)}, unter dem Südende des Seminargebäudes</li><li>B y = 100, näher an der Elektronik, kürzere Drähte</li><li>C y = 150, Mitte unter dem Seminargebäude, die Dockzone des Seminars (y 137 bis 154) liegt dann nebenan</li></ul>
      <div class="pick">Vorschlag: A</div></div>
    <div class="card"><h3>2. Loch</h3>
      <ul><li><b>{f(HOLE[0])} × {f(HOLE[1])}</b></li><li>Wand am Loch 1,6 mit Innentasche 0,8</li></ul>
      <div class="pick">Loch übernommen; Wand 1,6 klärt Probe T1</div></div>
    <div class="card"><h3>3. Oberkante des Lochs</h3>
      <ul><li><b>Brücke</b> über 13,3 mm drucken (Bambu A1 schafft das meist)</li><li>Dachform mit 45°, dann bleibt oben ein Dreieck offen</li></ul>
      <div class="pick">Vorschlag: Brücke, in T1 prüfen</div></div>
  </div>
</section>

<section class="sheet">
  <h2>Bitte nachmessen (Schieblehre)</h2>
  <ul style="margin:0;padding-left:20px;display:flex;flex-direction:column;gap:4px">
    <li>Abstand von der Unterseite der Frontplatte bis zur Hakenkante: das ist die maximale Wandstärke, in die der Schalter einrastet.</li>
    <li>Kasten genau (B × L) und Frontplatte genau (B × L), Dicke der Frontplatte.</li>
    <li>Tiefe des Kastens hinter der Frontplatte und Länge der Pins.</li>
    <li>Pinabstand und Pinbreite (Lötfahne oder 4,8-mm-Flachstecker?).</li>
  </ul>
</section>

<section class="sheet">
  <h2>Testprobe T1, wenn der Plan passt</h2>
  <p>Ein Wandstück 30 × {f(H_WALL)} × 2,4 mm mit drei Löchern nebeneinander (13,1 × 8,1, 13,3 × 8,3 und 13,5 × 8,5), je mit Innentasche und Wand am Loch 1,2, 1,6 und 2,0. So ist an einem kleinen Druck (etwa 10 Minuten) klar, welcher Sitz hält, und ob die Brücke über dem Loch sauber wird. Erst nach dem Abnicken entsteht die STL.</p>
</section>
</main>
"""
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(html)
    print("geschrieben:", OUT, f"({len(html) // 1024} KB)")


if __name__ == "__main__":
    build()
