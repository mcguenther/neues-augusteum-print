"""Zeichnungen der Planseite Display-Gebäude: Schnitte der Entwürfe E1 bis E3 und Schaltbild (SVG als Text)."""
import math

from plug.display import layout as L
from plug.display import params as D
from plug.power import params as PP
from plug.testcase import params as TP

de = lambda x, n=1: ("%.*f" % (n, x)).replace(".", ",")
PLATE_BOTTOM = -(TP.dims_plan()["F"] + TP.CEIL_T)          # −14,6 flache Unterseite
FOOT_BOTTOM = -TP.dims_plan()["F"]                          # −14,2 Muldenboden oben
HDR = dict(body=2.0, tip=TP.dims_plan()["z_tip"], tail=6.3)


class Svg:
    """Kleine SVG-Hilfe: x nach rechts (Osten), z nach oben."""

    def __init__(self, x0, x1, z0, z1, s, pad=14):
        self.x0, self.z1, self.s, self.pad = x0, z1, s, pad
        self.w, self.h = (x1 - x0) * s + 2 * pad, (z1 - z0) * s + 2 * pad
        self.o = []

    def X(self, x):
        return self.pad + (x - self.x0) * self.s

    def Y(self, z):
        return self.pad + (self.z1 - z) * self.s

    def poly(self, pts, cls, close=True):
        tag = "polygon" if close else "polyline"
        self.o.append('<%s points="%s" class="%s"/>' % (tag, " ".join("%.1f,%.1f" % (self.X(x), self.Y(z)) for x, z in pts), cls))

    def rect(self, x0, z0, x1, z1, cls):
        self.poly([(x0, z0), (x1, z0), (x1, z1), (x0, z1)], cls)

    def line(self, x0, z0, x1, z1, cls):
        self.poly([(x0, z0), (x1, z1)], cls, close=False)

    def text(self, x, z, s, cls="", anchor="start", dx=0, dy=4):
        self.o.append('<text x="%.1f" y="%.1f" class="%s" text-anchor="%s">%s</text>' % (self.X(x) + dx, self.Y(z) + dy, cls, anchor, s))

    def dim_h(self, x0, x1, z, label):
        self.line(x0, z, x1, z, "dim")
        for x in (x0, x1):
            self.line(x, z - 0.8, x, z + 0.8, "dim")
        self.text((x0 + x1) / 2, z - 1.6, label, "num", "middle", dy=-2)

    def dim_v(self, x, z0, z1, label, side=1):
        self.line(x, z0, x, z1, "dim")
        for z in (z0, z1):
            self.line(x - 0.8, z, x + 0.8, z, "dim")
        self.text(x + 1.2 * side, (z0 + z1) / 2, label, "num", "start" if side > 0 else "end", dy=4)

    def svg(self, ident, label):
        return '<svg id="%s" viewBox="0 0 %.0f %.0f" role="img" aria-label="%s" class="fig sec" style="max-width:%.0fpx">%s</svg>' % (ident, self.w, self.h, label, self.w, "".join(self.o))


def _rot(pts, piv, deg):
    a = math.radians(deg)
    out = []
    for x, z in pts:
        dx, dz = x - piv[0], z - piv[1]
        out.append((piv[0] + dx * math.cos(a) + dz * math.sin(a), piv[1] - dx * math.sin(a) + dz * math.cos(a)))   # Kopf nach Westen (−x) geneigt
    return out


def section(e):
    """Schnitt in Blickrichtung (Osten rechts) durch die Mitte der Stele. x = 0 ist die Ostkante der Mulde, z = 0 die Plattenoberfläche."""
    d = L.DESIGNS[e]
    depth, pe = d["depth"], d["pin_from_east"]
    mb = L.module_bottom_z(e)
    mt = D.DISP["mod_t"]
    top = mb + D.DISP["pcb_h"] * (math.cos(math.radians(D.TILT_DEG)) if e == "E3" else 1) + D.WALL
    wb = mb + L.BELOW_WINDOW * (math.cos(math.radians(D.TILT_DEG)) if e == "E3" else 1)
    wt = wb + L.WIN_H * (math.cos(math.radians(D.TILT_DEG)) if e == "E3" else 1)
    xr, xl = 10.0, -40.0
    g = Svg(xl, xr, -30.0, 45.0, 7.0)
    kd = L.KD
    # Platte, Mulde und Fuß
    g.rect(xl, PLATE_BOTTOM, 4.1, 0, "plate")
    g.rect(-depth, FOOT_BOTTOM, 0, 0.02, "foot")
    g.text(xl + 1.0, PLATE_BOTTOM / 2 + 1.5, "Platte", "mut", "start")
    # Kassettenschacht (Fuß ist bis zum Boden der Mulde massiv), Kassette
    kx0, kx1 = -(pe + D.KASS_D / 2), -(pe - D.KASS_D / 2)
    kz1 = D.KASS_TOP
    g.rect(kx0, FOOT_BOTTOM, kx1, kz1, "kass")
    g.rect(kx0 - D.WALL, 0, kx1 + D.WALL, kz1 + 1.2, "foot") if e != "E1" else None
    g.rect(kx0, FOOT_BOTTOM, kx1, kz1, "kass")
    # Winkelleiste unter der Platte, Pins in die Buchse
    g.rect(-(pe + 1.0), PLATE_BOTTOM - HDR["body"], -(pe - 1.0), PLATE_BOTTOM, "body")
    g.line(-pe, PLATE_BOTTOM, -pe, HDR["tip"], "pin")
    g.line(-pe, PLATE_BOTTOM - 1.0, -pe - HDR["tail"], PLATE_BOTTOM - 1.0, "tail")
    g.line(-pe - HDR["tail"], PLATE_BOTTOM - 1.0, -pe - HDR["tail"] - 1.0, PLATE_BOTTOM - 8.0, "wire")
    g.text(-pe - HDR["tail"] + 0.8, PLATE_BOTTOM - 7.2, "Adern zum ESP", "mut", "start")
    # Display: Platine, Rahmen, Fenster
    x_front = -(D.WALL + D.CLR)
    pcb = [(x_front - mt, mb), (x_front, mb), (x_front, mb + D.DISP["pcb_h"]), (x_front - mt, mb + D.DISP["pcb_h"])]
    front = [(-D.WALL, mb - 0.6), (0, mb - 0.6), (0, top), (-D.WALL, top)]
    back = [(x_front - mt - D.CLR - D.BACK, mb - 0.6), (x_front - mt - D.CLR, mb - 0.6), (x_front - mt - D.CLR, top), (x_front - mt - D.CLR - D.BACK, top)]
    cap = [(x_front - mt - D.CLR - D.BACK, top - D.WALL), (0, top - D.WALL), (0, top), (x_front - mt - D.CLR - D.BACK, top)]
    if e == "E3":
        piv = (0.0, mb)
        pcb, front, back, cap = [_rot(p, piv, D.TILT_DEG) for p in (pcb, front, back, cap)]
    if e == "E1":
        g.rect(kx0 - D.WALL, kz1, kx1 + D.WALL, mb, "foot")
    if e != "E1":
        g.rect(x_front - mt - D.CLR - D.BACK, FOOT_BOTTOM + 3.2, 0, 0.02, "foot")
        slot = [(x_front - mt - D.CLR, mb - 0.6), (-D.WALL, mb - 0.6), (-D.WALL, 0.03), (x_front - mt - D.CLR, 0.03)]
        g.poly(slot, "void")
    g.poly(back, "foot")
    # Front in zwei Teilen (Fenster dazwischen)
    if e == "E3":
        fb = [(front[0]), (front[1]), _rot([(0, wb)], (0.0, mb), D.TILT_DEG)[0], _rot([(-D.WALL, wb)], (0.0, mb), D.TILT_DEG)[0]]
        ft = [_rot([(-D.WALL, wt)], (0.0, mb), D.TILT_DEG)[0], _rot([(0, wt)], (0.0, mb), D.TILT_DEG)[0], front[2], front[3]]
        g.poly(fb, "foot")
        g.poly(ft, "foot")
    else:
        g.rect(-D.WALL, mb - 0.6, 0, wb, "foot")
        g.rect(-D.WALL, wt, 0, top, "foot")
    g.poly(cap, "foot")
    g.poly(pcb, "pcb")
    # aktive Fläche
    aa0 = wb + D.WINDOW_MARGIN * (math.cos(math.radians(D.TILT_DEG)) if e == "E3" else 1)
    aa1 = aa0 + D.DISP["aa_h"] * (math.cos(math.radians(D.TILT_DEG)) if e == "E3" else 1)
    if e == "E3":
        p0 = _rot([(x_front, aa0 - (aa0 - mb) + (aa0 - mb) / math.cos(math.radians(D.TILT_DEG)))], (0.0, mb), D.TILT_DEG)[0]
        a = _rot([(x_front, mb + (L.BELOW_WINDOW + D.WINDOW_MARGIN)), (x_front, mb + (L.BELOW_WINDOW + D.WINDOW_MARGIN + D.DISP["aa_h"]))], (0.0, mb), D.TILT_DEG)
        g.poly(a, "aa", close=False)
    else:
        g.line(x_front, aa0, x_front, aa1, "aa")
    # Bemaßung
    g.dim_h(-depth, 0, PLATE_BOTTOM - 12.5, "Tiefe %s" % de(depth))
    g.dim_v(7.0, 0, top, "")
    g.text(7.6, top / 2 + 3.0, "Höhe", "num", "start")
    g.text(7.6, top / 2 - 1.0, de(top), "num", "start")
    g.line(4.2, wb, 5.8, wb, "dim")
    g.line(4.2, wt, 5.8, wt, "dim")
    g.line(5.0, wb, 5.0, wt, "okl")
    g.text(xr - 0.5, top + 3.4, "Fenster %s bis %s" % (de(wb), de(wt)), "ok", "end")
    g.line(xl, 0, 4.5, 0, "tablel")
    g.text(xl + 1.0, 1.3, "Plattenoberfläche", "mut", "start")
    if e == "E1":
        g.text(-pe - 7.0, kz1 - 6.0, "Kassette", "lab", "end")
    else:
        g.text(-pe, kz1 + 3.6, "Kassette", "lab", "middle")
    return g.svg("sec-" + e, "Schnitt durch Entwurf %s" % e)


# ---------------------------------------------------------------- Schaltbild
def wiring():
    """Blockschaltbild: Powerbank, INA226, ESP32, Docks, Display. Farben: 5 V, 3,3 V, I²C, Daten der LED."""
    W, H = 920, 250
    o = []

    def box(x, y, w, h, t, sub="", cls="blk"):
        o.append('<rect x="%d" y="%d" width="%d" height="%d" rx="6" class="%s"/><text x="%d" y="%d" class="bt" text-anchor="middle">%s</text>' % (
            x, y, w, h, cls, x + w / 2, y + 22, t))
        if sub:
            o.append('<text x="%d" y="%d" class="mut" text-anchor="middle">%s</text>' % (x + w / 2, y + 40, sub))

    def line(pts, cls, lab="", lx=0, ly=0, anchor="start"):
        o.append('<polyline points="%s" class="ln %s"/>' % (" ".join("%d,%d" % p for p in pts), cls))
        if lab:
            o.append('<text x="%d" y="%d" class="mut" text-anchor="%s">%s</text>' % (lx, ly, anchor, lab))

    box(10, 50, 120, 62, "Powerbank", "USB-A, 5 V")
    box(180, 50, 130, 62, "INA226", "Shunt in der 5-V-Leitung", "blk hot")
    box(380, 36, 150, 190, "ESP32-DevKit", "3,3 V-Regler, GPIO, I²C")
    box(600, 36, 130, 62, "74AHCT125", "3,3 V → 5 V")
    box(770, 36, 140, 62, "6 LED-Docks", "GND, DIN, 5 V, DETECT")
    box(600, 160, 130, 62, "Display-Dock", "GND, SDA, SCL, 3,3 V", "blk disp")
    box(770, 160, 140, 62, "OLED 1,3″", "I²C 0x3C", "blk disp")
    line([(130, 81), (180, 81)], "v5")
    line([(310, 81), (380, 81)], "v5", "5 V", 330, 72)
    line([(345, 81), (345, 12), (840, 12), (840, 36)], "v5")
    line([(665, 12), (665, 36)], "v5")
    o.append('<text x="360" y="8" class="mut">5 V an ESP-VIN, Pegelwandler und LED-Docks</text>')
    line([(530, 62), (600, 62)], "sig", "3,3 V Daten", 536, 54)
    line([(730, 67), (770, 67)], "sig", "DIN", 750, 88, "middle")
    line([(380, 150), (240, 150), (240, 112)], "i2c", "I²C", 246, 140)
    line([(380, 176), (270, 176), (270, 112)], "v3", "3,3 V", 276, 168)
    line([(530, 176), (600, 176)], "i2c", "SDA, SCL", 536, 168)
    line([(530, 200), (600, 200)], "v3", "3,3 V", 536, 192)
    line([(730, 191), (770, 191)], "ln-ig", "4 Adern", 750, 212, "middle")
    leg = ('<g transform="translate(10,150)"><rect x="0" y="0" width="14" height="3" class="v5s"/><text x="20" y="5" class="mut">5 V</text>'
           '<rect x="0" y="18" width="14" height="3" class="v3s"/><text x="20" y="23" class="mut">3,3 V</text>'
           '<rect x="0" y="36" width="14" height="3" class="i2s"/><text x="20" y="41" class="mut">I²C</text>'
           '<rect x="0" y="54" width="14" height="3" class="sgs"/><text x="20" y="59" class="mut">Daten der LEDs</text></g>')
    return '<svg id="wiring" viewBox="0 0 %d %d" role="img" aria-label="Blockschaltbild Powerbank, INA226, ESP32, Docks und Display" class="fig">%s%s</svg>' % (W, H, "".join(o), leg)
