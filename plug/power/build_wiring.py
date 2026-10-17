"""Schaltplan- und Lötplan-Seite für die Elektronik im Unterkasten: `python3 -m plug.power.build_wiring`.

Schreibt `plug/power/wiring.html` (Artifact). Pin-Nummern der Docks kommen aus `build_pinout.py` (DIN, DETECT, LEFT, RIGHT),
Maße des Unterkastens aus `params.py`. Die Zeichnungen stehen in `wiring.template.html`, nur Tabellen und das Höhenbild werden hier erzeugt.
"""
from math import ceil
from pathlib import Path

from plug.power import params as PP
from plug.power.build_pinout import DETECT, DIN, LEFT, RIGHT

OUT = Path(__file__).with_name("wiring.html")
TEMPLATE = Path(__file__).with_name("wiring.template.html").read_text(encoding="utf-8")

# ---- Docks (Reihenfolge wie 01_ bis 06_ im Konzept; die Zuordnung zu den Gebäuden ist noch nicht festgelegt)
BUILDINGS = [("Paulinum", "Paulinum"), ("Neues Augusteum", "N. Augusteum"), ("Hörsaalgebäude", "Hörsaal"),
             ("Seminargebäude", "Seminar"), ("Institutsgebäude", "Institut"), ("City-Hochhaus", "Hochhaus")]
# Luftlinie Dock bis Elektronikbox in mm, Konzept PR #28 (Branch ccr-e337172c-xtl689, concept.html, Stand nach Innenhof-Merge)
TO_ELEC = [83.8, 33.7, 10.9, 61.3, 111.1, 0.0]


def wire_len(d):
    """Ader = 1,3 × Luftlinie + 40 mm (Abgang am Dock, Verlegen in der Box), auf 5 mm aufgerundet, mindestens 60 mm."""
    return max(60, int(ceil((1.3 * d + 40) / 5.0) * 5))


# ---- Höhen (mm); ESP32-Maße typisch, Schieblehre nötig
LAYER = 0.2
UK_FLOOR = PP.UK_FLOOR
UK_INNEN = ceil((PP.STECKERRAUM + PP.PB_T) / LAYER - 1e-9) * LAYER          # Innenhöhe wie im Konzept (auf Lagen gerundet)
UK_TOTAL = UK_INNEN + UK_FLOOR
PCB, MODULE, USBC = 1.6, 3.1, 3.3
SOLDER = 1.0                                                                 # gekürzte Lötstellen unter der Platine (Aufbau A)
PIN_LONG, PLASTIC = 6.0, 2.5                                                 # Stiftleiste 2,54 mm
ZONE = 2.9                                                                   # Leiste 2,0 + Lötstelle/Draht bis 2,9 unter der Platte (Konzept)
H_A = round(SOLDER + PCB + USBC, 1)
H_B = round(PIN_LONG + PLASTIC + PCB + USBC, 1)


def fmt(v, n=1):
    return f"{v:.{n}f}".replace(".", ",")


def dock_rows():
    out = []
    for i, (_, short) in enumerate(BUILDINGS):
        y0 = 80 + 44 * i
        out.append(f'<rect class="led" x="778" y="{y0 + 8}" width="44" height="16" rx="2"/>'
                   f'<rect class="chip5050" x="792" y="{y0 + 10}" width="14" height="12" rx="1"/>'
                   f'<text x="832" y="{y0 + 20}">{i + 1} {short}</text>')
    return "".join(out)


def height_svg():
    s, yf = 14.0, 330.0
    yt = yf - UK_INNEN * s
    zb = yt + ZONE * s
    o = [f'<rect class="plate" x="100" y="60" width="830" height="{yt - 60:.1f}"/>',
         '<text class="tm" x="515" y="86" text-anchor="middle">Oberplatte 14,6 mm (abgeschnitten), Docks hängen mit Leiste und Adern darunter</text>',
         f'<rect class="zone" x="100" y="{yt:.1f}" width="830" height="{ZONE * s:.1f}"/>',
         f'<text class="tm t5" x="936" y="{yt + 15:.0f}" text-anchor="end">Adernzone {fmt(ZONE)} mm</text>',
         f'<rect class="plate" x="100" y="{yf}" width="830" height="{UK_FLOOR * s:.1f}"/>',
         f'<text class="tm" x="110" y="{yf + 13}">Boden {fmt(UK_FLOOR)} mm</text>',
         f'<path class="dim" d="M84 {yt:.1f} V{yf} M78 {yt:.1f} H90 M78 {yf} H90"/>',
         f'<text class="tm" x="20" y="{(yt + yf) / 2 - 4:.0f}">{fmt(UK_INNEN)} mm</text>',
         f'<text class="tm" x="20" y="{(yt + yf) / 2 + 12:.0f}">innen</text>']
    # Powerbank
    h = PP.PB_T * s
    o += [f'<rect class="pbk" x="180" y="{yf - h:.1f}" width="130" height="{h:.1f}"/>',
          f'<text class="tb" x="245" y="{yf - h / 2:.0f}" text-anchor="middle">Powerbank</text>',
          f'<text class="tm" x="245" y="{yf - h / 2 + 16:.0f}" text-anchor="middle">{fmt(PP.PB_T)} mm</text>']

    def stack(x, layers, w=130):
        y = yf
        res = []
        for h_mm, cls, label in layers:
            hp = h_mm * s
            y -= hp
            res.append((y, hp, cls, label))
        return res

    # A: Winkelleisten oben
    a = stack(380, [(SOLDER, "pad", ""), (PCB, "pcbg", "Platine 1,6"), (USBC, "mod", "Modul 3,3")])
    for y, hp, cls, label in a:
        o.append(f'<rect class="{cls}" x="380" y="{y:.1f}" width="130" height="{hp:.1f}"/>')
        if label:
            o.append(f'<text class="tm{" tl" if cls == "pcbg" else ""}" x="445" y="{y + hp / 2 + 4:.0f}" text-anchor="middle">{label}</text>')
    o.append(f'<text class="tb" x="445" y="{a[-1][0] - 8:.0f}" text-anchor="middle">{fmt(H_A)} mm</text>')
    # B: Stiftleisten nach unten
    b = stack(580, [(PIN_LONG, "pins", "Pins 6,0"), (PLASTIC, "pcb", "Kunststoff 2,5"), (PCB, "pcbg", "Platine 1,6"), (USBC, "mod", "Modul / USB-C 3,3")])
    for y, hp, cls, label in b:
        if cls == "pins":
            o.append("".join(f'<path class="syl" d="M{x} {y:.1f} V{y + hp:.1f}"/>' for x in range(595, 700, 18)))
        else:
            o.append(f'<rect class="{cls}" x="580" y="{y:.1f}" width="130" height="{hp:.1f}"/>')
        o.append(f'<text class="tm" x="722" y="{y + hp / 2 + 4:.0f}">{label}</text>')
    o.append(f'<text class="tb" x="645" y="{b[-1][0] - 8:.0f}" text-anchor="middle">{fmt(H_B)} mm</text>')
    over = (yf - b[-1][0]) / s - (UK_INNEN - ZONE)
    o.append(f'<text class="tm t5" x="722" y="{b[-1][0] - 8:.0f}">ragt {fmt(over)} mm in die Adernzone</text>')
    # Namen
    for x, t1, t2 in [(245, "Powerbank", f"{fmt(PP.PB_T)} mm"),
                      (445, "A: Winkelleisten oben", f"{fmt(H_A)} mm · Luft {fmt(UK_INNEN - H_A)} mm"),
                      (645, "B: Stiftleisten unten", f"{fmt(H_B)} mm · Luft {fmt(UK_INNEN - H_B)} mm")]:
        o.append(f'<text class="tb" x="{x}" y="372" text-anchor="middle">{t1}</text><text class="tm" x="{x}" y="388" text-anchor="middle">{t2}</text>')
    return "".join(o)


# ---- Drahtliste
CELLS = []


def grp(title):
    CELLS.append(f'<tr class="grp"><td colspan="4">{title}</td></tr>')


def row(nr, a, b, wire):
    CELLS.append(f'<tr><td class="mono"><b>{nr}</b></td><td>{a}</td><td>{b}</td><td>{wire}</td></tr>')


def netlist():
    CELLS.clear()
    grp("Strom: Powerbank bis Docks (+5 V)")
    row("P1", "USB-A-Stecker rot", "Schalter, Lötfahne 1", "24 AWG rot")
    row("P2", "Schalter, Lötfahne 2", "INA226 VIN+", "24 AWG rot")
    row("P3", "INA226 VIN−", "Knoten K5", "24 AWG rot; Zusatzwiderstand 0,1 Ω parallel zum Shunt")
    row("P4", "INA226 VBUS", "VIN−", "meist schon auf dem Modul verbunden, Durchgang prüfen")
    row("P5", "Knoten K5", "ESP32 VIN", "Dupont-Ader rot")
    row("P6", "Knoten K5", "+5-V-LED-Schiene", "24 AWG rot, 3 cm: Drahtbrücke, Platzhalter für die geparkte Diode D1")
    row("P7", "+5-V-LED-Schiene", "C1 Plus und Pin 3 aller 6 Docks", "28 AWG orange; Elko liegend, Plus ohne Streifen")
    grp("Masse")
    row("G1", "USB-A-Stecker schwarz", "GND-Schiene", "24 AWG schwarz")
    row("G2", "ESP32 GND (linke Reihe)", "GND-Schiene", "Dupont-Ader schwarz")
    row("G3", "C1 Minus (Streifen)", "GND-Schiene", "Bein des Elkos")
    row("G4", "Pin 1 aller 6 Docks", "GND-Schiene", "28 AWG braun")
    row("G5", "ESP32 GND (rechte Reihe)", "Y-Knoten zu INA226 GND und OLED GND", "Dupont-Ader schwarz")
    grp("3,3 V und I²C")
    row("V1", "ESP32 3V3", "Y-Knoten zu INA226 VCC und OLED VDD", "Dupont-Ader orange")
    row("V2", f"ESP32 GPIO21 (SDA)", "Y-Knoten zu INA226 SDA und OLED SDA", "Dupont-Ader weiß")
    row("V3", f"ESP32 GPIO22 (SCL)", "Y-Knoten zu INA226 SCL und OLED SCK", "Dupont-Ader violett")
    grp("Docks: Daten und Erkennung")
    for n in range(6):
        row(f"D{n + 1}", f"ESP32 GPIO{DIN[n]}", f"Pin 2 (DIN) Dock {n + 1}", "Dupont-Ader blau, 330 Ω mitten in der Ader")
    for n in range(6):
        row(f"E{n + 1}", f"ESP32 GPIO{DETECT[n]}", f"Pin 4 (DETECT) Dock {n + 1}", "Dupont-Ader grün")
    grp("Optional: Strompuls-Last")
    row("L1", "Knoten K5", "47 Ω, 1 W, dann MOSFET Drain (Bein 2, Mitte)", "rote Ader")
    row("L2", "MOSFET Source (Bein 3, rechts)", "GND-Schiene", "schwarze Ader")
    row("L3", "ESP32 GPIO14", "100 Ω, dann MOSFET Gate (Bein 1, links)", "Dupont-Ader grau")
    row("L4", "graue Ader (GPIO14)", "10 kΩ, dann GND-Schiene", "Widerstand zwischen Ader und Schiene, nicht am MOSFET")
    return "".join(CELLS)


def dupont():
    dest = {}
    for n in range(6):
        dest[DIN[n]] = (f"DIN Dock {n + 1} über 330 Ω", "blau")
        dest[DETECT[n]] = (f"DETECT Dock {n + 1}", "grün")
    dest[21] = ("SDA zu INA226 und OLED", "weiß")
    dest[22] = ("SCL zu INA226 und OLED", "violett")
    dest[14] = ("Gate der Last über 100 Ω (optional)", "grau")
    out = []
    for side, rows in (("links", LEFT), ("rechts", RIGHT)):
        for i, (gpio, label, *_rest) in enumerate(rows):
            if gpio is not None and gpio in dest:
                d, color = dest[gpio]
            elif label == "VIN":
                d, color = "Knoten K5 (+5 V)", "rot"
            elif label == "3V3":
                d, color = "3,3 V zu INA226 und OLED", "orange"
            elif label == "GND":
                d, color = ("GND-Schiene", "schwarz") if side == "links" else ("GND zu INA226 und OLED", "schwarz")
            else:
                continue
            g = f"GPIO{gpio}" if gpio is not None else "–"
            out.append(f'<tr><td>{side}</td><td class="num">{i + 1}</td><td class="mono">{label}</td><td class="mono">{g}</td><td>{d}</td><td>{color}</td></tr>')
    return "".join(out)


def docks():
    out = []
    for n, ((name, _), d) in enumerate(zip(BUILDINGS, TO_ELEC)):
        lux = "in der Box" if d == 0 else f"{d:.0f} mm"
        out.append(f'<tr><td><b>Dock {n + 1}</b></td><td>{name}</td><td class="mono">GPIO{DIN[n]}</td><td class="mono">GPIO{DETECT[n]}</td>'
                   f'<td class="num">{lux}</td><td class="num"><b>{wire_len(d)} mm</b></td></tr>')
    return "".join(out)


def main():
    assert len(dupont().split("<tr>")) - 1 == 19, "19 Dupont-Adern erwartet"
    html = (TEMPLATE
            .replace("{{DOCK_ROWS}}", dock_rows())
            .replace("{{HEIGHT_SVG}}", height_svg())
            .replace("{{NETLIST}}", netlist())
            .replace("{{DUPONT}}", dupont())
            .replace("{{DOCKS}}", docks()))
    for k, v in dict(UK_INNEN=fmt(UK_INNEN), UK_TOTAL=fmt(UK_TOTAL), UK_FLOOR=fmt(UK_FLOOR), ZONE=fmt(ZONE),
                     H_A=fmt(H_A), H_B=fmt(H_B), LUFT_A=fmt(UK_INNEN - H_A), LUFT_B=fmt(UK_INNEN - H_B)).items():
        html = html.replace("{{" + k + "}}", v)
    assert "{{" not in html, "unersetzte Platzhalter"
    OUT.write_text(html, encoding="utf-8")
    print(f"{OUT}: Innenhöhe {fmt(UK_INNEN)} mm, A {fmt(H_A)} mm, B {fmt(H_B)} mm, Adern {[wire_len(d) for d in TO_ELEC]}")


if __name__ == "__main__":
    main()
