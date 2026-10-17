"""Pinout-Seite für den ESP32 (WROOM-32, 30 Pin) in der Steckplatte: `python3 -m plug.power.build_pinout`.

Schreibt `plug/power/pinout.html` (Artifact). Die Pin-Tabelle `PINS` ist die einzige Quelle für Zeichnung,
Tabelle und Zähler. Die Zuordnung der Docks steht in `DIN` und `DETECT`.
"""
from pathlib import Path

OUT = Path(__file__).with_name("pinout.html")

# Dock 1 bis 6: Datenausgang (DIN) und Eingang (DETECT) je Dock
DIN = [23, 19, 18, 17, 16, 4]
DETECT = [32, 33, 25, 26, 27, 13]
# I²C-Bus (INA226 0x40 und Display 0x3C) auf den Standard-Pins von Wire, ALERT des INA226 auf einen Eingang
SPECIAL = {
    21: ("i2c", "SDA", "I²C SDA: INA226 und Display"),
    22: ("i2c", "SCL", "I²C SCL: INA226 und Display"),
    34: ("inonly", "ALERT", "INA226 ALERT, braucht externen Pull-up 10 kΩ an 3V3"),
}
RESERVE = {}

# (gpio oder None, Beschriftung am Board, Seite, Klasse, Ausgang, Eingang, Pull-up, Hinweis)
# Reihenfolge je Seite von oben (Antenne) nach unten (USB), wie auf dem üblichen 30-Pin-DOIT-Board.
LEFT = [
    (None, "EN", "pwr", False, False, False, "Reset-Pin, nicht belegen."),
    (36, "VP", "inonly", False, True, False, "Nur Eingang, kein interner Pull-up (extern 10 kΩ), ADC1."),
    (39, "VN", "inonly", False, True, False, "Nur Eingang, kein interner Pull-up (extern 10 kΩ), ADC1."),
    (34, "D34", "inonly", False, True, False, "Nur Eingang, kein interner Pull-up (extern 10 kΩ), ADC1."),
    (35, "D35", "inonly", False, True, False, "Nur Eingang, kein interner Pull-up (extern 10 kΩ), ADC1."),
    (32, "D32", "ok", True, True, True, "Unauffällig beim Booten, RTC-Pin, ADC1."),
    (33, "D33", "ok", True, True, True, "Unauffällig beim Booten, RTC-Pin, ADC1."),
    (25, "D25", "ok", True, True, True, "Unauffällig beim Booten, DAC1, ADC2."),
    (26, "D26", "ok", True, True, True, "Unauffällig beim Booten, DAC2, ADC2."),
    (27, "D27", "ok", True, True, True, "Unauffällig beim Booten, ADC2."),
    (14, "D14", "cond", True, True, True, "Gibt beim Booten kurz ein PWM-Signal aus."),
    (12, "D12", "avoid", True, True, True, "Strapping (MTDI): HIGH beim Start stellt den Flash auf 1,8 V, das WROOM-32 startet dann nicht."),
    (13, "D13", "ok", True, True, True, "Unauffällig beim Booten, ADC2."),
    (None, "GND", "gnd", False, False, False, "Masse."),
    (None, "VIN", "pwr", False, False, False, "5 V Eingang, hier hängt die USB-A-Buchse der Powerbank."),
]
RIGHT = [
    (23, "D23", "ok", True, True, True, "Unauffällig beim Booten (VSPI MOSI)."),
    (22, "D22", "ok", True, True, True, "Unauffällig beim Booten (I²C SCL)."),
    (1, "TX0", "avoid", True, True, True, "UART0 zum USB-Chip, gibt das Boot-Log aus, wird beim Flashen benutzt."),
    (3, "RX0", "avoid", True, True, True, "UART0 vom USB-Chip, wird beim Flashen benutzt."),
    (21, "D21", "ok", True, True, True, "Unauffällig beim Booten (I²C SDA)."),
    (19, "D19", "ok", True, True, True, "Unauffällig beim Booten (VSPI MISO)."),
    (18, "D18", "ok", True, True, True, "Unauffällig beim Booten (VSPI SCK)."),
    (5, "D5", "cond", True, True, True, "Strapping, gibt beim Booten kurz ein PWM-Signal aus."),
    (17, "TX2", "ok", True, True, True, "Unauffällig beim Booten (beim WROVER mit PSRAM belegt)."),
    (16, "RX2", "ok", True, True, True, "Unauffällig beim Booten (beim WROVER mit PSRAM belegt)."),
    (4, "D4", "ok", True, True, True, "Unauffällig beim Booten, ADC2."),
    (2, "D2", "avoid", True, True, True, "Strapping: muss beim Flashen LOW oder offen sein, hängt oft an der Board-LED."),
    (15, "D15", "cond", True, True, True, "Strapping, gibt beim Booten kurz ein PWM-Signal aus (Boot-Log)."),
    (None, "GND", "gnd", False, False, False, "Masse."),
    (None, "3V3", "pwr", False, False, False, "3,3 V Ausgang des Boardreglers, versorgt INA226 und Display (zusammen unter 25 mA), sonst nicht belasten."),
]

CHIP = {"i2c": "I²C", "din": "DIN", "det": "DET", "res": "Reserve", "inonly": "nur Ein", "cond": "bedingt",
        "avoid": "meiden", "pwr": "Versorg.", "gnd": "GND", "ok": "frei"}


def role(gpio, cls, label):
    """Klasse und Chip-Text einer Zeile nach der Dock-Zuordnung."""
    if gpio in DIN:
        return "din", f"DIN {DIN.index(gpio) + 1}", f"Datenleitung Dock {DIN.index(gpio) + 1}"
    if gpio in DETECT:
        return "det", f"DET {DETECT.index(gpio) + 1}", f"DETECT Dock {DETECT.index(gpio) + 1}"
    if gpio in SPECIAL:
        return SPECIAL[gpio]
    if gpio in RESERVE:
        return "res", "Reserve", RESERVE[gpio]
    if cls == "ok":
        return "res", "frei", "frei"
    return cls, CHIP[cls], {"inonly": "frei mit externem Pull-up", "cond": "bedingt nutzbar",
                            "avoid": "meiden", "pwr": "Versorgung", "gnd": "Masse", "i2c": "I²C"}[cls]


def pin_name(gpio, label):
    return f"GPIO{gpio}" if gpio is not None else label


def side(rows, left):
    out = []
    for gpio, label, cls, o, i, p, note in rows:
        c, chip, _ = role(gpio, cls, label)
        name = f'<b>{pin_name(gpio, label)}</b>' + (f'<small>{label}</small>' if gpio is not None else "")
        chip_html = f'<span class="chip {c}">{chip}</span>'
        inner = chip_html + f'<span class="nm">{name}</span>' if left else f'<span class="nm">{name}</span>' + chip_html
        out.append(f'<div class="pr {"l" if left else "r"}" title="{note}">{inner}<i class="dot {c}"></i></div>')
    return "".join(out)


def board():
    return (
        '<div class="board"><div class="col">' + side(LEFT, True) + '</div>'
        '<div class="body"><span class="ant">Antenne</span><span class="mod">ESP32-WROOM-32</span>'
        '<span class="usb">USB-C</span></div>'
        '<div class="col">' + side(RIGHT, False) + '</div></div>'
    )


def table():
    rows = []
    for gpio, label, cls, o, i, p, note in LEFT + RIGHT:
        if gpio is None:
            continue
        c, chip, _ = role(gpio, cls, label)
        yn = lambda v: "ja" if v else "nein"
        rows.append(
            f'<tr><td class="mono"><b>{gpio}</b></td><td class="mono">{label}</td>'
            f'<td><span class="chip {c}">{chip}</span></td><td>{yn(o)}</td><td>{yn(i)}</td><td>{yn(p)}</td>'
            f'<td>{yn(o)}</td><td>{note}</td></tr>'
        )
    rows.sort(key=lambda r: int(r.split("<b>")[1].split("</b>")[0]))
    return "".join(rows)


def docks():
    label = {g: l for g, l, *_ in LEFT + RIGHT if g is not None}
    rows = []
    for n in range(6):
        rows.append(
            f'<tr><td><b>Dock {n + 1}</b></td><td class="mono">GPIO{DIN[n]} <small>{label[DIN[n]]}</small></td>'
            f'<td class="mono">GPIO{DETECT[n]} <small>{label[DETECT[n]]}</small></td></tr>'
        )
    return "".join(rows)


def counts():
    allp = [r for r in LEFT + RIGHT if r[0] is not None]
    clean = [r[0] for r in allp if r[2] == "ok"]
    inonly = [r[0] for r in allp if r[2] == "inonly"]
    cond = [r[0] for r in allp if r[2] == "cond"]
    avoid = [r[0] for r in allp if r[2] == "avoid"]
    return len(allp), clean, inonly, cond, avoid


TEMPLATE = (Path(__file__).with_name("pinout.template.html")).read_text(encoding="utf-8")


def main():
    n, clean, inonly, cond, avoid = counts()
    used = len(DIN) + len(DETECT) + 2  # plus SDA, SCL
    html = (TEMPLATE
            .replace("{{BOARD}}", board())
            .replace("{{TABLE}}", table())
            .replace("{{DOCKS}}", docks())
            .replace("{{N_GPIO}}", str(n))
            .replace("{{N_CLEAN}}", str(len(clean)))
            .replace("{{N_USED}}", str(used))
            .replace("{{N_FREE}}", str(len(clean) - used))
            .replace("{{N_INONLY}}", str(len(inonly) - 1))  # ohne ALERT
            .replace("{{N_COND}}", str(len(cond)))
            .replace("{{N_AVOID}}", str(len(avoid))))
    OUT.write_text(html, encoding="utf-8")
    print(f"{OUT}: {n} GPIO am Board, {len(clean)} saubere Pins, {used} belegt, {len(clean) - used} Reserve")


if __name__ == "__main__":
    main()
