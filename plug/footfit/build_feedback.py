#!/usr/bin/env python3
"""Testbogen zur ersten Passform-Runde (Hochhaus): kurze Auswahlfragen, Ergebnistext zum Kopieren. Aufruf: python3 -m plug.footfit.build_feedback -> plug/footfit/feedback.html"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
tpl = open(os.path.join(HERE, "feedback.template.html"), encoding="utf-8").read()
open(os.path.join(HERE, "feedback.html"), "w", encoding="utf-8").write(tpl)
print("feedback.html geschrieben")
