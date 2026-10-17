#!/usr/bin/env python3
"""Friert den alten Stand des Hof-Einsatzes und der Mulde für den Vergleich ein (plug/hof/alt/).

Liest die STL aus Commit REV_ALT (stl/steckmodul_campus/), schneidet die Platte auf den Bereich um den Hof zu (compare.ausschnitt) und schreibt
mulde_1zu1300.stl (Platte, Ausschnitt) und hof_einsatz_1zu1300.stl (Einsatz) nach plug/hof/alt/. Nur nötig, wenn alt/ fehlt.

Aufruf: python3 -m plug.hof.freeze_alt
"""
import os
import subprocess

import generate as G
from plug import campus as C
from plug.hof import compare as H
from plug.testcase import params as P

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
ALT = os.path.join(HERE, "alt")


def blob(pfad):
    return subprocess.check_output(["git", "show", "%s:%s" % (H.REV_ALT, pfad)], cwd=ROOT)


def main():
    os.makedirs(ALT, exist_ok=True)
    s = 1000.0 / P.SCALE_PLAN
    G.FAST = True
    models = G.source_models("laserscan", s)
    fps = [v[1] for k, v in models.items() if k in P.CASSETTE]
    region = H.ausschnitt(H.alt_umriss(fps, s))
    platte = H.to_man(H.lade_stl(blob("stl/steckmodul_campus/steckplatte_1zu1300.stl")))
    crop = platte ^ G.extrude(region, -1.0, 30.0)
    C.to_tm(crop).export(os.path.join(ALT, "mulde_1zu1300.stl"))
    einsatz = H.lade_stl(blob("stl/steckmodul_campus/hof_einsatz_1zu1300.stl"))
    einsatz.export(os.path.join(ALT, "hof_einsatz_1zu1300.stl"))
    print("alt/: Mulde %.0f KB, Einsatz %.0f KB" % tuple(os.path.getsize(os.path.join(ALT, f)) / 1024 for f in ("mulde_1zu1300.stl", "hof_einsatz_1zu1300.stl")))


if __name__ == "__main__":
    main()
