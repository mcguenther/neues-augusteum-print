#!/usr/bin/env python3
"""Setzt stecker/daten.json (aus steckmodul.py) in die HTML-Vorlage ein -> stecker/ansicht.html."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
tpl = open(os.path.join(HERE, "ansicht.template.html"), encoding="utf-8").read()
data = open(os.path.join(HERE, "daten.json"), encoding="utf-8").read()
out = tpl.replace("/*DATA*/", data)
path = os.path.join(HERE, "ansicht.html")
open(path, "w", encoding="utf-8").write(out)
print("%s  %.0f kB" % (os.path.relpath(path), len(out.encode()) / 1024))
