#!/usr/bin/env python3
"""Baut plug/scale1176/placer.html aus placer.template.html und app_data.json (python3 -m plug.scale1176.app_data)."""
import os

HERE = os.path.dirname(__file__)
data = open(os.path.join(HERE, "app_data.json"), encoding="utf-8").read()
html = open(os.path.join(HERE, "placer.template.html"), encoding="utf-8").read().replace("@DATA@", data)
open(os.path.join(HERE, "placer.html"), "w", encoding="utf-8").write(html)
print("placer.html: %.0f kB" % (len(html.encode()) / 1000))
