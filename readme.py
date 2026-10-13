#!/usr/bin/env python3
"""Hält die automatisch erzeugten Teile der README.md aktuell.

In README.md stehen Platzhalter der Form

    <!-- AUTO:name -->
    ...
    <!-- /AUTO:name -->

Alles dazwischen wird aus den erzeugten Dateien (Maße aus den STL/3MF, Bilder aus
vorschau/readme/) neu geschrieben. Der Rest der README ist normaler Text und darf
von Hand bearbeitet werden. Läuft automatisch am Ende von generate.py / preview.py;
einzeln: python3 readme.py
"""
import glob
import os
import re

import trimesh
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
README = os.path.join(HERE, "README.md")
IMG_DIR = os.path.join(HERE, "vorschau", "readme")
STL_DIR = os.path.join(HERE, "stl")
DENSITY = 2  # Bilder sind doppelt so groß gerendert wie angezeigt (siehe preview.py)

# Anzeigename je Maßstab: Beschriftung der Spalten
LEVELS = {
    "1zu1500": ("1:1500", "kompakt"),
    "1zu1000": ("1:1000", "groß, mehr Detail"),
}


def img(name, alt):
    """<img> mit Anzeigebreite aus der Pixelbreite; leer, wenn das Bild fehlt."""
    path = os.path.join(IMG_DIR, name)
    if not os.path.exists(path):
        return ""
    w = Image.open(path).width // DENSITY
    return '<img src="vorschau/readme/%s" alt="%s" width="%d">' % (name, alt, w)


def extents(path):
    m = trimesh.load(path)
    return m.extents


def dims(path):
    if not os.path.exists(path):
        return ""
    return "%.0f × %.0f × %.0f mm" % tuple(extents(path))


def levels():
    """Vorhandene Maßstäbe, größte Verhältniszahl (kleinstes Modell) zuerst."""
    found = [os.path.basename(d) for d in glob.glob(os.path.join(STL_DIR, "1zu*"))]
    return sorted(found, key=lambda s: -int(s[3:]))


def level_head(sc):
    label, sub = LEVELS.get(sc, (sc.replace("1zu", "1:"), ""))
    return "<b>%s</b>" % label + ("<br><sub>%s</sub>" % sub if sub else "")


# --------------------------------------------------------------------------
# Blöcke
# --------------------------------------------------------------------------
def block_hero():
    return '<p align="center">\n  %s\n</p>' % img("hero.png", "Campus Augustusplatz als 3D-Modell")


def block_campus():
    scs = levels()
    head = "".join('<th align="center">%s</th>' % level_head(sc) for sc in scs)
    pics, facts = "", ""
    for sc in scs:
        pics += '<td align="center" valign="bottom">%s</td>' % img("campus_%s.png" % sc, "Gesamtcampus " + sc.replace("1zu", "1:"))
        d = dims(os.path.join(STL_DIR, sc, "komplett_campus_mit_extras_objekte.3mf"))
        parts = len(glob.glob(os.path.join(STL_DIR, sc, "komplett_campus_mit_extras_teil*.stl")))
        note = "in %d Teile geteilt" % parts if parts > 1 else "passt auf ein Druckbett"
        facts += '<td align="center"><sub>%s<br>%s</sub></td>' % (d, note)
    return ("<table>\n<tr>%s</tr>\n<tr>%s</tr>\n<tr>%s</tr>\n</table>" % (head, pics, facts))


def block_gebaeude():
    import generate  # Gebäudeliste (Titel, Beschreibung) – eine Quelle für alles

    scs = levels()
    rows = ["<tr><th align=\"left\">Gebäude</th>%s</tr>" %
            "".join('<th align="center">%s</th>' % level_head(sc) for sc in scs)]
    for b in generate.BUILDINGS:
        slug = b["slug"]
        title = "<b>%s %s</b>" % (slug[:2], b["title"])
        if b["group"] == "extra":
            title += " <sup>Extra</sup>"
        text = title
        if b["note"]:
            text += "<br><sub>%s</sub>" % b["note"]
        # reale Höhe = Höhe des Modells × Maßstabszahl (Modell in mm → Meter)
        ref = next((sc for sc in reversed(scs) if os.path.exists(
            os.path.join(STL_DIR, sc, "einzeln", slug + ".stl"))), None)
        if ref:
            h = extents(os.path.join(STL_DIR, ref, "einzeln", slug + ".stl"))[2] * int(ref[3:]) / 1000
            text += "<br><sub>ca. %s m hoch</sub>" % ("%g" % (round(h * 2) / 2)).replace(".", ",")
        cells = ""
        for sc in scs:
            f = os.path.join(STL_DIR, sc, "einzeln", slug + ".stl")
            cells += '<td align="center" valign="middle">%s<br><sub>%s</sub></td>' % (
                img("%s_%s.png" % (slug, sc), b["title"] + " " + sc.replace("1zu", "1:")), dims(f))
        rows.append('<tr><td valign="middle">%s</td>%s</tr>' % (text, cells))
    return "<table>\n%s\n</table>" % "\n".join(rows)


def block_grundplatte():
    sc = levels()[0] if levels() else "1zu1500"
    return '<p align="center">\n  %s\n</p>' % img("grundplatte_%s.png" % sc,
                                                  "Grundplatte mit darüber schwebenden Gebäuden")


BLOCKS = {
    "hero": block_hero,
    "campus": block_campus,
    "gebaeude": block_gebaeude,
    "grundplatte": block_grundplatte,
}


def update(path=README):
    text = open(path, encoding="utf-8").read()
    for name, fn in BLOCKS.items():
        pat = re.compile(r"(<!-- AUTO:%s -->\n).*?(<!-- /AUTO:%s -->)" % (name, name), re.S)
        if not pat.search(text):
            print("  README: Platzhalter AUTO:%s fehlt" % name)
            continue
        text = pat.sub(lambda m: m.group(1) + fn() + "\n" + m.group(2), text)
    open(path, "w", encoding="utf-8").write(text)
    print("  README aktualisiert:", os.path.relpath(path, HERE))


if __name__ == "__main__":
    update()
