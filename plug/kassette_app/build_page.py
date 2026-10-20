#!/usr/bin/env python3
"""Baut plug/kassette_app/app.html aus app.template.html und data.json (python3 -m plug.kassette_app.build_data).

Aufruf: python3 -m plug.kassette_app.build_page
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
data = open(os.path.join(HERE, "data.json"), encoding="utf-8").read()
html = open(os.path.join(HERE, "app.template.html"), encoding="utf-8").read().replace("@DATA@", data)
open(os.path.join(HERE, "app.html"), "w", encoding="utf-8").write(html)
print("app.html: %.0f kB" % (len(html.encode()) / 1000))
