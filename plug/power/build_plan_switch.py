"""Plan Hauptschalter (Wippenschalter 10 x 15 mm) in der Rückwand des Unterkastens: `plug/power/plan_switch.html`.

Konzept, keine STL (Regel 2 im Logbuch: erst nach dem Abnicken). Die Maße des Fachs kommen aus `plug/power/params.py` und
`plug/power/build_concept.py`; die Schaltermaße stehen in `SW` (Nutzer grob gemessen, Rest geschätzt, Status je Wert).
Aufruf: `python3 -m plug.power.build_plan_switch` (Sekunden).
"""
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
ROOM_D = round(DEPTH_OUT - WALL_AT_HOLE + 0.5, 1)                       # Schalterraum ab Innenseite der Rückwand
V_SW = round(BC.KV0 - 4.0 - SW["flange_l"] / 2, 1)                      # Mitte des Schalters quer, 4 mm Abstand zum Kabelkanal
ROOM_W = round(SW["flange_l"] + 2 * 3.0, 1)                             # Breite des Schalterraums


def f(x):
    return f"{x:.1f}"


# ---------------------------------------------------------------- Bild 1: Draufsicht
def fig_top():
    s = 5.0
    ox, oy = 14 + PP.UK_WALL * s + 63 * s, 40 + 35 * s + PP.UK_WALL * s
    X = lambda u: ox + u * s                  # noqa: E731
    Y = lambda v: oy + v * s                  # noqa: E731
    W = ox + 63 * s + (ROOM_D + PP.UK_WALL) * s + 60
    Hh = oy + 35 * s + PP.UK_WALL * s + 44
    u0, u1, v0, v1 = BC.U0, BC.U1, BC.V0, BC.V1
    bu0 = BC.BU0
    t = []
    t.append(f'<svg viewBox="0 0 {f(W)} {f(Hh)}" role="img" aria-label="Draufsicht Unterkasten mit Schalterraum an der Rückwand">')
    # Außenwand + Schalterraum
    sw_v0, sw_v1 = V_SW - ROOM_W / 2, V_SW + ROOM_W / 2
    t.append(f'<rect class="wall" x="{f(X(u0 - PP.UK_WALL))}" y="{f(Y(v0 - PP.UK_WALL))}" '
             f'width="{f((u1 - u0 + 2 * PP.UK_WALL) * s)}" height="{f((v1 - v0 + 2 * PP.UK_WALL) * s)}"/>')
    t.append(f'<rect class="wall" x="{f(X(u1))}" y="{f(Y(sw_v0 - PP.UK_WALL))}" width="{f((ROOM_D + PP.UK_WALL) * s)}" '
             f'height="{f((ROOM_W + 2 * PP.UK_WALL) * s)}"/>')
    t.append(f'<rect class="fach" x="{f(X(u0))}" y="{f(Y(v0))}" width="{f((u1 - u0) * s)}" height="{f((v1 - v0) * s)}"/>')
    t.append(f'<rect class="fach" x="{f(X(u1) - 1)}" y="{f(Y(sw_v0))}" width="{f(ROOM_D * s + 1)}" height="{f(ROOM_W * s)}"/>')
    # Fenster vorn, Steckerraum, Kabelkanal
    t.append(f'<rect class="win" x="{f(X(u0 - PP.UK_WALL))}" y="{f(Y(BC.WIN[0]))}" width="{f((PP.UK_WALL + 0.5) * s)}" '
             f'height="{f((BC.WIN[1] - BC.WIN[0]) * s)}"/>')
    t.append(f'<rect class="chan" x="{f(X(bu0 - PP.PB_CLR))}" y="{f(Y(BC.KV0))}" width="{f((u1 - bu0 + PP.PB_CLR) * s)}" '
             f'height="{f(PP.PB_CABLE * s)}"/>')
    t.append(f'<rect class="pb" x="{f(X(bu0))}" y="{f(Y(BC.BV0))}" width="{f(PP.PB_L * s)}" height="{f(PP.PB_W * s)}" rx="3"/>')
    t.append(f'<text class="lbl" x="{f(X(bu0 + PP.PB_L / 2))}" y="{f(Y(BC.BVC) + 4)}" text-anchor="middle">Powerbank 90 × 63 × 12,6</text>')
    t.append(f'<text class="lbl" x="{f(X(u0 + 14))}" y="{f(Y(BC.BVC) + 4)}" text-anchor="middle">Steckerraum 35</text>')
    # Kabel
    pts = " ".join(f"{f(X(p[0]))},{f(Y(p[1]))}" for p in BC.fach_parts(BC.Frame(0, 0, 0, 1))["cable"][:5])
    t.append(f'<polyline class="cab" points="{pts} {f(X(u1))},{f(Y(BC.KV0 + PP.PB_CABLE / 2))}"/>')
    # Schalter
    sx = X(u1) + 2
    t.append(f'<rect class="sw" x="{f(sx)}" y="{f(Y(V_SW - SW["flange_l"] / 2))}" width="{f(SW["body_depth"] * s)}" '
             f'height="{f(SW["body_l"] * s)}" transform="translate(0 {f(SW["flange_t"] * s)})"/>')
    t.append(f'<rect class="swf" x="{f(X(u1) - SW["flange_t"] * s)}" y="{f(Y(V_SW - SW["flange_l"] / 2))}" '
             f'width="{f(SW["flange_t"] * s)}" height="{f(SW["flange_l"] * s)}"/>')
    for k in (-0.5, 0.5):
        yy = Y(V_SW + k * SW["pin_pitch"])
        t.append(f'<line class="pin" x1="{f(sx + SW["body_depth"] * s)}" x2="{f(sx + (SW["body_depth"] + SW["pin_len"]) * s)}" '
                 f'y1="{f(yy)}" y2="{f(yy)}"/>')
    t.append(f'<line class="wire" x1="{f(sx + (SW["body_depth"] + SW["pin_len"]) * s)}" y1="{f(Y(V_SW - SW["pin_pitch"] / 2))}" '
             f'x2="{f(sx + (SW["body_depth"] + SW["pin_len"] + 2) * s)}" y2="{f(Y(V_SW - SW["pin_pitch"] / 2) - 10)}"/>')
    # Beschriftung
    t.append(f'<text class="hl" x="{f(X(u1) + 2)}" y="{f(Y(sw_v0 - PP.UK_WALL) - 20)}">Schalterraum</text>')
    t.append(f'<text class="hl" x="{f(X(u1) + 2)}" y="{f(Y(sw_v0 - PP.UK_WALL) - 7)}">{f(ROOM_W)} × {f(ROOM_D)}</text>')
    t.append(f'<text class="lbl" x="{f(X(bu0 + 40))}" y="{f(Y(BC.KV0 + PP.PB_CABLE / 2) - 9)}">Kabelkanal 6</text>')
    t.append(f'<text class="lbl" x="{f(X(u0 - PP.UK_WALL))}" y="{f(Y(v0 - PP.UK_WALL) - 7)}">Plattenkante (links), Fenster für LEDs und Buchsen</text>')
    t.append(f'<text class="lbl" x="{f(X(u1) + 2)}" y="{f(Y(sw_v1 + PP.UK_WALL) + 14)}">Rückwand</text>')
    # Maßlinie Fachlänge
    ym = Y(v1 + PP.UK_WALL) + 14
    t.append(f'<line class="dim" x1="{f(X(u0))}" x2="{f(X(u1))}" y1="{f(ym)}" y2="{f(ym)}"/>'
             f'<text class="lbl" x="{f(X(0))}" y="{f(ym - 4)}" text-anchor="middle" dy="26">Fach {f(u1 - u0)}</text>')
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
    X = lambda v: ox + (v - (V_SW - Wp / 2)) * s    # noqa: E731
    Z = lambda z: oy + (H_WALL - z) * s            # noqa: E731
    W = ox + Wp * s + 36
    Hh = Z(0) + 36
    zc = Z_MID
    cx = X(V_SW)
    t = [f'<svg viewBox="0 0 {f(W)} {f(Hh)}" role="img" aria-label="Rückwand von außen mit Schalterausschnitt">']
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
        ("Loch in der Wand (Spiel 0,15 je Seite)", f"{f(HOLE[0])} × {f(HOLE[1])}", "E Vorschlag, Testprobe T1 klärt 13,1 / 13,3 / 13,5"),
        ("Wand am Loch", f"{f(WALL_AT_HOLE)}", "S Schnapphaken greifen je nach Typ bei 0,8 bis 2,0; Abstand Frontplatte bis Hakenkante messen"),
        ("Außenwand sonst, Innentasche", f"{f(PP.UK_WALL)} / {f(POCKET[0])} × {f(POCKET[1])} × {f(POCKET_T)}", "E Tasche von innen, damit die Haken ausfedern können"),
        ("Höhe der Wand außen / Schaltermitte", f"{f(H_WALL)} / {f(Z_MID)}", "A aus der Maßkette (Boden bis Oberplatte, Plan 1:1300), Frontplatte 10 hoch lässt je {f((H_WALL - 10) / 2)} Rand"),
        ("Einbautiefe ab Außenfläche", f"≈ {f(DEPTH_OUT)}", f"A Kasten {f(SW['body_depth'])} + Pins {f(SW['pin_len'])} (aus Foto) + {f(SW['wire'])} Lötstelle und Biegung"),
        ("Schalterraum hinter der Rückwand, B × T", f"{f(ROOM_W)} × {f(ROOM_D)}", "E Ausbuchtung neben dem Fach, nach oben von der Oberplatte geschlossen"),
        ("Mitte des Schalters quer zum Fach (v)", f"{f(V_SW)}", f"E 4 mm neben dem Kabelkanal (Kanal ab v = {f(BC.KV0)}), kurze Wege zum Kabelausgang"),
    ]
    html = f"""<title>Hauptschalter Rückwand</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>
/* Layout: Zeichenblatt, Hauptzeichnung oben, Schnitt und Ansicht nebeneinander, darunter Maßtabelle und Entscheidungskarten */
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
.row {{ display:grid; grid-template-columns:minmax(0,1.5fr) minmax(0,1fr); gap:16px; }}
@media (max-width:820px) {{ .row {{ grid-template-columns:minmax(0,1fr); }} }}
svg {{ display:block; width:100%; height:auto; min-width:520px; }}
.row svg {{ min-width:0; }}
svg .wall {{ fill:var(--wall); stroke:var(--wallline); stroke-width:1.2; }}
svg .fach {{ fill:var(--paper); stroke:var(--wallline); stroke-width:.8; }}
svg .win {{ fill:var(--paper); stroke:var(--accent); stroke-width:1; stroke-dasharray:3 2; }}
svg .chan {{ fill:var(--chan); stroke:var(--line); }}
svg .pb {{ fill:var(--pb); stroke:var(--wallline); stroke-width:1; }}
svg .plate {{ fill:var(--pb); stroke:var(--wallline); }}
svg .cab {{ fill:none; stroke:var(--mute); stroke-width:2; stroke-linecap:round; }}
svg .sw, svg .swf {{ fill:var(--accent); stroke:var(--ink); stroke-width:1; }}
svg .swf {{ fill-opacity:.85; }}
svg .hook {{ fill:var(--ink); }}
svg .pin {{ stroke:var(--ink); stroke-width:2.2; }}
svg .wire {{ fill:none; stroke:var(--accent); stroke-width:2; }}
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
  <div class="kicker">Plan · Konzept, noch keine STL · Stand 17.10.2026</div>
  <h1>Hauptschalter in der Rückwand des Unterkastens</h1>
  <p>Wippenschalter 10 × 15 mm (KCD11, 2 Pins) schaltet das Plus der Powerbank. Das Kabel kommt aus dem Kabelkanal, geht über den Schalter und weiter zum INA226. Der Schalter schnappt von außen in ein Loch von {f(HOLE[0])} × {f(HOLE[1])} mm in der Rückwand, die Frontplatte liegt außen auf.</p>
</header>

<section class="sheet">
  <h2>Draufsicht Unterkasten, Maßstab 5 : 1</h2>
  <p>Fach wie im Konzept (Stand 6): Steckerraum 35 mm an der Plattenkante, Powerbank, Kabelkanal an der langen Seite. Die Rückwand liegt 0,5 mm hinter der Powerbank, der Schalter ist 16 mm tief und braucht deshalb eine eigene Ausbuchtung neben dem Fach.</p>
  <div class="scroll">{fig_top()}</div>
</section>

<div class="row">
  <section class="sheet">
    <h2>Schnitt durch die Schalterachse, 13 : 1</h2>
    <p>Wand außen links. Die Haken (schwarz) fassen hinter der {f(WALL_AT_HOLE)} mm dünnen Wand am Loch; die Innentasche gibt ihnen Platz zum Ausfedern.</p>
    <div class="scroll">{fig_section()}</div>
  </section>
  <section class="sheet">
    <h2>Rückwand von außen, 11 : 1</h2>
    <p>Wand {f(H_WALL)} hoch, Frontplatte 10 hoch. Langseite waagerecht: Stehend (13,3 hoch) blieben nur 2 mm Wand oben und unten.</p>
    <div class="scroll">{fig_front()}</div>
  </section>
</div>

<section class="sheet">
  <h2>Warum die Rückwand</h2>
  <p>Ich habe vier Stellen geprüft. Nur die Rückwand geht ohne Umbau des Fachs.</p>
  <table>
    <tr><th>Stelle</th><th>Urteil</th></tr>
    <tr><td>Rückwand, neben dem Kabelkanal</td><td><b>Empfehlung.</b> Kabel tritt dort aus, die Wege zum INA226 sind kurz. Braucht eine Ausbuchtung von {f(ROOM_W)} × {f(ROOM_D)} mm.</td></tr>
    <tr><td>Stirnwand an der Plattenkante</td><td>Voll belegt: Fenster für LEDs und Buchsen reicht von v = {f(BC.WIN[0])} bis {f(BC.WIN[1])}, dann kommt der USB-A-Stecker, dann der Kabelkanal. Kein Platz für 15 mm Frontplatte.</td></tr>
    <tr><td>Längswand mit Kabelkanal</td><td>Kanal ist nur 6 mm breit; die Frontplatte (10 × 15) hätte dort keinen Platz neben dem Kabel.</td></tr>
    <tr><td>Längswand gegenüber</td><td>Möglich, aber die Ausbuchtung läge seitlich und das Kabel müsste quer durch das Fach.</td></tr>
  </table>
  <p class="note"><b>Offen:</b> Die Rückwand liegt auf der Platte nach innen. Ob dort von außen etwas zugänglich ist, hängt davon ab, wo das Fach am Plattenrand sitzt. Dort muss noch geprüft werden, ob die Ausbuchtung zur Elektronik (Doktorhut) passt und ob der Schalter von einer Seite erreichbar bleibt.</p>
</section>

<section class="sheet">
  <h2>Maße und Maßkette</h2>
  <div class="scroll"><table>
    <tr><th>Größe</th><th>Wert in mm</th><th>Status und Herkunft</th></tr>
    {rows([(a, b, c) for a, b, c in dims])}
  </table></div>
  <p>Status: M gemessen, A abgeleitet, S geschätzt, E Entscheidung, wie im Logbuch. Der Händler-Ausschnitt 13,5 × 8,5 bis 9 stammt aus Angeboten für den KCD11 (<a href="https://makerselectronics.com/product/kcd11-101-on-off-switch-250v-3a/">Makers Electronics</a>, <a href="https://www.ebay.com/p/13026640396">eBay</a>). Eine Plattenstärke für den Einschnapp-Sitz steht dort nicht.</p>
</section>

<section class="sheet">
  <h2>Verdrahtung</h2>
  <div class="circ">Powerbank USB  ──rot (+5 V)──▶ [ Schalter ] ──▶ INA226 VIN+ ──(Shunt)── VIN− ──▶ ESP32 und LEDs
Powerbank USB  ──schwarz (GND)────────────────────────▶ INA226 GND / gemeinsame Masse</div>
  <p>Der Schalter liegt vor dem Shunt, damit der INA226 beim Ausschalten stromlos ist und nichts am Messkreis vorbeifließt. Auf dem Schalter steht 3 A bei 250 V AC; bei 5 V und höchstens 2,1 A (Powerbank) ist das reichlich. Lötstellen mit Schrumpfschlauch isolieren, das Kabel mit einer Zugentlastung im Kabelkanal führen.</p>
</section>

<section>
  <h2 style="margin-bottom:12px">Entscheidungen</h2>
  <div class="cards">
    <div class="card"><h3>1. Lage in der Rückwand</h3>
      <ul><li><b>A</b> neben dem Kabelkanal, v = {f(V_SW)}</li><li>B am anderen Ende der Rückwand, längere Kabel</li></ul>
      <div class="pick">Vorschlag: A</div></div>
    <div class="card"><h3>2. Wand am Loch</h3>
      <ul><li><b>1,6</b> mit Innentasche 0,8</li><li>2,4 ohne Tasche (nur wenn die Haken so weit reichen)</li></ul>
      <div class="pick">Vorschlag: 1,6, Probe T1 klärt das</div></div>
    <div class="card"><h3>3. Oberkante des Lochs</h3>
      <ul><li><b>Brücke</b> über 13,3 mm drucken (Bambu A1 schafft das meist)</li><li>Dachform mit 45°, dann bleibt oben ein Dreieck offen</li></ul>
      <div class="pick">Vorschlag: Brücke, in T1 prüfen</div></div>
    <div class="card"><h3>4. Schalterraum</h3>
      <ul><li><b>Ausbuchtung</b> {f(ROOM_W)} × {f(ROOM_D)}</li><li>Fach um {f(ROOM_D)} verlängern, Powerbank dann nicht bündig</li></ul>
      <div class="pick">Vorschlag: Ausbuchtung</div></div>
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
