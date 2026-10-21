#!/usr/bin/env python3
"""Hof-Einsatz in zwei Teile zerlegt (Einsatz, Grünes = Bäume und Beete), damit Bambu Studio jedem Teil ein eigenes Filament geben kann.

Bambu Studio 2.8 lädt die Farben unserer 3MF nicht (Meldung „ungültige Konfiguration, nur Geometriedaten“, Nutzer 21.10.2026). Beide STL
ziehen und mit „Als ein Objekt mit mehreren Teilen laden“ bestätigen, dann je Teil ein Filament wählen. Die Teile ergänzen sich genau
(Einsatz = Körper − Bäume): Volumen zusammen gleich dem des Einsatzes, sie berühren sich nur an den Flächen.

  python3 -m plug.hof_teile                    Bäume (Krone und Stamm) und Beete grün
  python3 -m plug.hof_teile --staemme-beige    nur die Kronen und die Beete grün, die Stämme bleiben im Einsatz

Schreibt nach stl/steckmodul_campus/gebaeude_farbig/: 08_innenhof_1zu1300_[staemme_beige_]teil1_einsatz.stl und ..._teil2_gruen.stl.
"""
import argparse
import os
import sys

import manifold3d as m3d
import numpy as np

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

import generate as G       # noqa: E402
import innenhof            # noqa: E402
from plug import buildings as BU  # noqa: E402
from plug import campus as C  # noqa: E402
from plug.testcase import params as P  # noqa: E402

OUT = os.path.join(HERE, "stl", "steckmodul_campus", "gebaeude_farbig")


def teile(scale=P.SCALE_PLAN, nur_kronen=False):
    """(Einsatz ohne das Grüne, das Grüne = Bäume und Beete) als Manifold in Plattenlage. Erst zerlegen, dann bereinigen: Bereinigt man den Einsatz vorher (float32) und zieht die
    Bäume danach ab, bleiben Splitter der Kronen zurück (290 Berührkanten)."""
    s = 1000.0 / scale
    r = C.build(scale)
    hof, fp = r[5], r[2][G.HOF["slug"]][1]
    data = innenhof.load()
    H = innenhof.hub(data, s)
    zmax = max(o.get("hoehe", 1) for o in data["objekte"]) * s + 2
    teile_ = []
    for o in data["objekte"]:
        if o["typ"] == "baum":
            krone, stamm = innenhof.baum_teile(o, s)
            teile_.append(krone if nur_kronen else krone + stamm)
        elif o["typ"] == "beet":                 # Beete grün wie die Bäume (Nutzer 21.10.)
            teile_.append(innenhof.prism(innenhof.widen(innenhof.rechteck(o, data), s), o["hoehe"] * s))
    baeume = G.union(teile_).translate([0, 0, H - 0.01])
    baeume = baeume ^ G.extrude(fp.buffer(-0.05, join_style=2), -0.5, zmax)     # wie im Einsatz (nichts über den Rand)
    baeume = baeume ^ hof                                                       # nur was im Einsatz steckt
    baeume = baeume ^ G.extrude(fp.buffer(1.0), H, zmax + H + 5)                # erst ab Hofboden: der Fuß im Pflaster bleibt Einsatz (keine 0,01-mm-Tasche)
    return hof - baeume, baeume


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--staemme-beige", action="store_true")
    ap.add_argument("--scale", type=int, default=P.SCALE_PLAN)
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    koerper, baeume = teile(a.scale, a.staemme_beige)
    pre = "08_innenhof_1zu%d_%s" % (a.scale, "staemme_beige_" if a.staemme_beige else "")
    v0 = koerper.volume() + baeume.volume()
    ok = True
    for name, teil in (("teil1_einsatz", koerper), ("teil2_gruen", baeume)):
        sauber, netz = BU.sauber(teil)
        tm = C.to_tm(sauber)
        path = os.path.join(a.out, pre + name + ".stl")
        tm.export(path)
        dicht = tm.is_watertight and sauber.status() == m3d.Error.NoError
        ok &= dicht
        print("  %-62s %5.1f × %5.1f × %5.1f mm  %6.2f cm³  dicht=%s  Berührkanten %d" % (
            os.path.relpath(path, HERE), *tm.extents, tm.volume / 1000, dicht, netz["nachher"]["beruehrkanten"]))
    hof_stl = C.to_tm(C.build(a.scale)[5])
    print("Volumen der Teile zusammen %.3f cm³ gegen Einsatz vor dem Zerlegen %.3f cm³" % (v0 / 1000, hof_stl.volume / 1000))
    print("alle dicht" if ok else "ACHTUNG: nicht dicht")


if __name__ == "__main__":
    main()
