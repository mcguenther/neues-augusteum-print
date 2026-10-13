#!/usr/bin/env python3
"""Einmalig: schreibt die bisher gemessenen Fassadenfarben (data/farben.json, Stand vor der
Fotoprojektion) als feste hex-Werte in die Fassaden-Spezifikationen data/fassaden/<slug>.json.

Die handgesetzten Messfelder ("proben") und der alte Fotokatalog ("bilder") bleiben als
"proben_alt"/"bilder_alt" zur Herkunft erhalten, werden aber nicht mehr ausgewertet – so braucht das
Projekt keine der alten Fotos (deren 3840-px-Thumbnails bei Wikimedia nicht mehr abrufbar sind) und
farbmessung.py hat für jede Farbe einen Rückfallwert.

    python3 werkzeuge/farbmessung/spec_einfrieren.py <alte farben.json>
"""
import json
import os
import sys

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
alt = json.load(open(sys.argv[1]))
d = os.path.join(HERE, "data", "fassaden")
for fn in sorted(os.listdir(d)):
    if not fn.endswith(".json"):
        continue
    slug = fn[:-5]
    spec = json.load(open(os.path.join(d, fn)))
    if slug not in alt:
        continue
    for k, f in spec["farben"].items():
        if "hex" not in f and k in alt[slug]["farben"]:
            if f.get("proben"):
                f["proben_alt"] = f.pop("proben")
            f.pop("luftbild", None) if "luftbild" in f and not f["luftbild"] else None
            f["hex"] = alt[slug]["farben"][k]["rgb"]
            f["quelle"] = alt[slug]["farben"][k].get("quelle", "")
    if "bilder" in spec:
        spec["bilder_alt"] = spec.pop("bilder")
    json.dump(spec, open(os.path.join(d, fn), "w"), indent=1, ensure_ascii=False)
    print(slug, "eingefroren:", ", ".join(spec["farben"]))
