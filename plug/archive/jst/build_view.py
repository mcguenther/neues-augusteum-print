#!/usr/bin/env python3
"""Setzt plug/archive/jst/data.json (aus plug/archive/jst/jst.py) in die HTML-Vorlage ein -> plug/archive/jst/view.html."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
tpl = open(os.path.join(HERE, "view.template.html"), encoding="utf-8").read()
data = open(os.path.join(HERE, "data.json"), encoding="utf-8").read()
out = tpl.replace("/*DATA*/", data)
path = os.path.join(HERE, "view.html")
open(path, "w", encoding="utf-8").write(out)
print("%s  %.0f kB" % (os.path.relpath(path), len(out.encode()) / 1024))
