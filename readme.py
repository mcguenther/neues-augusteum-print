#!/usr/bin/env python3
"""Hält die automatisch erzeugten Teile der README.md aktuell.

In README.md stehen Platzhalter der Form

    <!-- AUTO:name -->
    ...
    <!-- /AUTO:name -->

Alles dazwischen wird aus den erzeugten Dateien (Maße aus den STL, Bilder aus
vorschau/readme/, siehe preview.readme_assets) neu geschrieben. Der Rest der README
ist normaler Text und darf von Hand bearbeitet werden. Läuft automatisch am Ende von
generate.py / preview.py; einzeln: python3 readme.py
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

# Quellen in der Reihenfolge der Spalten: (Ordner, Name, Kurzbeschreibung)
SOURCES = [
    ("osm", "OpenStreetMap", "Klötzchen aus Grundriss und Höhe"),
    ("lod2", "LoD2 Stadt Leipzig", "amtliche Höhen und Dachformen"),
    ("laserscan", "Laserscan GeoSN", "gemessene Dachlandschaft"),
]


def sources():
    return [s for s in SOURCES if os.path.isdir(os.path.join(STL_DIR, s[0]))]


def img(name, alt):
    """<img> mit Anzeigebreite aus der Pixelbreite; leer, wenn das Bild fehlt."""
    path = os.path.join(IMG_DIR, name)
    if not os.path.exists(path):
        return ""
    w = Image.open(path).width // DENSITY
    return '<img src="vorschau/readme/%s" alt="%s" width="%d">' % (name, alt, w)


def dims(path):
    if not os.path.exists(path):
        return ""
    return "%.0f × %.0f × %.0f mm" % tuple(trimesh.load(path, process=False).extents)


def head(name, sub):
    return '<th align="center"><b>%s</b><br><sub>%s</sub></th>' % (name, sub)


# --------------------------------------------------------------------------
# Blöcke
# --------------------------------------------------------------------------
def block_hero():
    return '<p align="center">\n  %s\n</p>' % img("hero.png", "Campus Augustusplatz als farbiges 3D-Modell")


def block_quellen():
    """Gesamtcampus je Datenquelle nebeneinander (1:1500, farbig)."""
    src = sources()
    return "<table>\n<tr>%s</tr>\n<tr>%s</tr>\n</table>" % (
        "".join(head(n, sub) for _, n, sub in src),
        "".join('<td align="center" valign="bottom">%s</td>' % img("campus_%s.png" % q, n) for q, n, _ in src))


def block_massstaebe():
    """Beste Quelle in beiden Maßstäben nebeneinander."""
    q = sources()[-1][0]
    heads, pics, facts = "", "", ""
    for sc, label, sub in (("1zu1500", "1:1500", "kompakt"), ("1zu1000", "1:1000", "groß, mehr Detail")):
        parts = len(glob.glob(os.path.join(STL_DIR, q, sc, "komplett_campus_mit_extras_teil*.stl")))
        note = "in %d Teile geteilt" % parts if parts > 1 else "passt auf ein Druckbett"
        d = dims(os.path.join(STL_DIR, q, sc, "komplett_campus_mit_extras_objekte.3mf"))
        heads += head(label, sub)
        pics += '<td align="center" valign="bottom">%s</td>' % img("campus_%s_%s.png" % (q, sc), label)
        facts += '<td align="center"><sub>%s<br>%s</sub></td>' % (d, note)
    return "<table>\n<tr>%s</tr>\n<tr>%s</tr>\n<tr>%s</tr>\n</table>" % (heads, pics, facts)


def block_gebaeude():
    import generate  # Gebäudeliste (Titel, Beschreibung) – eine Quelle für alles

    src = sources()
    rows = ['<tr><th align="left">Gebäude</th>%s</tr>' % "".join(head(n, sub) for _, n, sub in src)]
    for i, b in enumerate(generate.OBJEKTE, start=1):
        text = "<b>%s %s</b>" % (b["slug"][:2], b["title"])
        if b["group"] == "extra":
            text += " <sup>Extra</sup>"
        if b["note"]:
            text += "<br><sub>%s</sub>" % b["note"]
        cells = ""
        for q, n, _ in src:
            d = dims(os.path.join(STL_DIR, q, "1zu1000", "einzeln", b["slug"] + ".stl"))
            cells += '<td align="center" valign="middle">%s<br><sub>%s</sub></td>' % (
                img("%02d_%s.png" % (i, q), "%s, %s" % (b["title"], n)), d)
        rows.append('<tr><td valign="middle">%s</td>%s</tr>' % (text, cells))
    return "<table>\n%s\n</table>" % "\n".join(rows)


def block_grundplatte():
    return '<p align="center">\n  %s\n</p>' % img("grundplatte.png", "Grundplatte mit darüber schwebenden Gebäuden")


BLOCKS = {
    "hero": block_hero,
    "quellen": block_quellen,
    "massstaebe": block_massstaebe,
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
