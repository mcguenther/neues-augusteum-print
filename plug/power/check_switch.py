#!/usr/bin/env python3
"""Prüfung: Loch und Innentasche des Hauptschalters im echten Unterkasten (Westwand, `plug/power/build_concept.switch_cut`).

Baut den Unterkasten 1:1300 (ca. 15 s), prüft dicht, Volumen mit und ohne Schnitt, Schalterraum frei, Kasten und Frontplatte des Schalters
im Loch, und rendert einen Ausschnitt um den Schalter nach vorschau/steckmodul_schalterprobe/unterkasten_schalter.png.
Aufruf (aus dem Repo-Wurzelverzeichnis): python3 -m plug.power.check_switch
"""
import os

from plug.geom import box, to_tm, vol_int
from plug.power import build_concept as BC
from plug.power import params as PP

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PREV = os.path.join(ROOT, "vorschau", "steckmodul_schalterprobe")


def main():
    BC.variant(1300)
    uk, sh = BC.LAST["uk"], BC.LAST["sh"]
    minx, miny = -sh[0], -sh[1]
    h = BC.H0
    bot = h["uk_bot"]
    sw = BC.switch_cut(minx, miny, bot, h)
    tm = to_tm(uk)
    bad = 0

    def chk(txt, ok):
        nonlocal bad
        bad += (not ok)
        print("  %-78s %s" % (txt, "ok" if ok else "FEHLER"))

    print("Unterkasten 1:1300 mit Schalterloch: %.1f × %.1f × %.1f mm, %.1f cm³" % (*tm.extents, tm.volume / 1000.0))
    chk("Unterkasten dicht", bool(tm.is_watertight))
    chk("Schalterraum (Kasten, Pins, Draht, 20 mm tief) frei von Material", float(vol_int(sw["room"], uk)) < 0.05)
    yc, zc = miny + PP.SW_Y, bot + h["uk_t"] / 2
    body = box(minx, minx + 9.0, yc - 6.5, yc + 6.5, zc - 4.0, zc + 4.0)
    flange = box(minx - 1.2, minx, yc - 7.5, yc + 7.5, zc - 5.0, zc + 5.0)
    chk("Kasten 13 × 8 im Loch ohne Kollision", float(vol_int(body, uk)) < 0.05)
    chk("Frontplatte 15 × 10 liegt außen auf (nur Berührung)", float(vol_int(flange, uk)) < 0.05)
    chk("Kontrolle: Kasten 13,9 breit stößt an", float(vol_int(box(minx, minx + 9.0, yc - 6.95, yc + 6.95, zc - 4.0, zc + 4.0), uk)) > 0.05)
    wall = float(vol_int(box(minx, minx + PP.SW_WALL, yc - 6.0, yc + 6.0, zc - 7.0, zc + 7.0), uk))
    chk("Wand am Loch bleibt %.1f mm dick (Material 13 × 14 mm Fenster neben dem Loch)" % PP.SW_WALL, wall > 0.5)
    os.makedirs(PREV, exist_ok=True)
    import preview
    from PIL import Image
    crop = uk - box(minx - 5, minx + 400, miny - 5, miny + PP.SW_Y - 32, bot - 5, bot + 100) \
        - box(minx - 5, minx + 400, miny + PP.SW_Y + 32, miny + 600, bot - 5, bot + 100) \
        - box(minx + 40, minx + 400, miny - 5, miny + 600, bot - 5, bot + 100)
    dummy = [(to_tm(box(minx, minx + 9.0, yc - 6.5, yc + 6.5, zc - 4.0, zc + 4.0)), "#d9480f"),
             (to_tm(flange), "#e9733a")]
    base = [(to_tm(crop), "#8fa3b8")]
    a = preview.render(base, size=(900, 800), azim=180, elev=15)                      # von außen (von Westen)
    b = preview.render(base, size=(900, 800), azim=-35, elev=35)                      # schräg von innen
    c = preview.render(base + dummy, size=(900, 800), azim=165, elev=15)              # mit Schalter
    sheet = Image.new("RGB", (2700, 800), "white")
    for i, im in enumerate((a, b, c)):
        sheet.paste(im, (900 * i, 0))
    sheet.save(os.path.join(PREV, "unterkasten_schalter.png"))
    print("  -> %s" % ("alles in Ordnung" if not bad else "%d Fehler!" % bad))
    return bad


if __name__ == "__main__":
    raise SystemExit(1 if main() else 0)
