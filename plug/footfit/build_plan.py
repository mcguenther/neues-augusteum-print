#!/usr/bin/env python3
"""Planseite der Passform-Stummel (City-Hochhaus, Platte 14,6 mm): Schnitt mit Höhenregler, Druckzeit, Einstellungen zum Kopieren.

Aufruf: python3 -m plug.footfit.build_plan   (Sekunden; liest data.json aus `python3 -m plug.footfit.data`), schreibt plug/footfit/plan.html
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    data = open(os.path.join(HERE, "data.json")).read()
    tpl = open(os.path.join(HERE, "plan.template.html"), encoding="utf-8").read()
    open(os.path.join(HERE, "plan.html"), "w", encoding="utf-8").write(tpl.replace("/*DATA*/null", data))
    print("plan.html geschrieben,", len(tpl) + len(data), "Zeichen")


if __name__ == "__main__":
    main()
