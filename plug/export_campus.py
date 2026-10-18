#!/usr/bin/env python3
"""Druckpaket der Steckplatte 1:1300: Platte, Hof-Einsatz und die sechs steckbaren Gebäude als ZIP (STL, README, Prüfbericht).

Liest die eingecheckten STL aus `stl/steckmodul_campus/` (erzeugt mit `python3 -m plug.campus` und `python3 -m plug.buildings`), prüft sie
(dicht, Maße, Volumen, Gebäude untereinander via `plug.divider.check`) und schreibt `stl/steckmodul_campus/druckdaten_campus_1zu1300.zip`
sowie `README.txt` und `pruefbericht.txt` daneben. Die `*_fase2.stl` des Hochhauses (alter Stand der Passform-Runde) kommen nicht ins Paket.

Aufruf (aus dem Repo-Wurzelverzeichnis, ca. 15 s):
    python3 -m plug.export_campus
"""
import io
import json
import os
import sys
import zipfile
from contextlib import redirect_stdout

import manifold3d as m3d
import numpy as np
import trimesh

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from plug.divider import check as DC  # noqa: E402
from plug.testcase import params as P  # noqa: E402

OUT = os.path.join(HERE, "stl", "steckmodul_campus")
SCALE = P.SCALE_PLAN
NAMEN = {"01_paulinum": "Paulinum", "02_neues_augusteum": "Neues Augusteum", "03_hoersaalgebaeude": "Hörsaalgebäude",
         "04_seminargebaeude": "Seminargebäude", "05_institutsgebaeude": "Institutsgebäude", "06_city_hochhaus": "City-Hochhaus"}


def main():
    teile = [("steckplatte_1zu%d.stl" % SCALE, "Steckplatte (Sockelplatte oben, flache Unterseite)", OUT),
             ("hof_einsatz_1zu%d.stl" % SCALE, "Innenhof-Einsatz (kommt in die Aussparung der Platte)", OUT)]
    for slug in DC.SLUGS:
        teile.append(("%s_1zu%d.stl" % (slug, SCALE), "Gebäude: " + NAMEN[slug], os.path.join(OUT, "gebaeude")))
    zeilen, ok = [], True
    for name, titel, ordner in teile:
        tm = trimesh.load(os.path.join(ordner, name))
        man = m3d.Manifold(m3d.Mesh(vert_properties=np.asarray(tm.vertices, dtype=np.float32), tri_verts=np.asarray(tm.faces, dtype=np.uint32)))
        dicht = man.status() == m3d.Error.NoError and abs(man.volume() - tm.volume) < 1e-3 * abs(tm.volume) and man.volume() > 0
        _, cnt = np.unique(tm.edges_sorted, axis=0, return_counts=True)
        beruehr = int((cnt != 2).sum())
        ok &= dicht
        zeilen.append("%-34s %6.1f × %6.1f × %6.1f mm  %8.2f cm³  dicht=%s  Berührkanten %4d   %s" % (name, *tm.extents, tm.volume / 1000, dicht, beruehr, titel))
    buf = io.StringIO()
    with redirect_stdout(buf):
        try:
            DC.main(SCALE)
            koll = True
        except SystemExit:
            koll = False
    ok &= koll
    bericht = ["Prüfbericht Druckpaket Steckplatte 1:1300", "", "Dateien (dicht = Manifold-Prüfung der geladenen STL; Berührkanten = Kanten, an denen sich Flächen nur berühren, Slicer",
               "melden das als nicht-mannigfaltige Kanten und reparieren es beim Laden; dieselben Stellen hatten die STL schon vor der Trennwand):"] + zeilen + ["", "Gebäude untereinander (python3 -m plug.divider.check):", buf.getvalue().rstrip(), ""]
    for slug in DC.SLUGS:
        j = json.load(open(os.path.join(OUT, "gebaeude", "%s_1zu%d.json" % (slug, SCALE))))
        u = j["ueberhang"]
        bericht.append("%-22s Kassette %-5s Kollision %.3f mm³  Platz fehlt %.2f mm³  Brücken %.1f mm²  Kragstücke %.1f mm² (bis %.1f mm)" % (
            slug, j["var"], j["kollision_mm3"], j["platz_fehlt_mm3"], u["bruecke_mm2"], u["krag_mm2"], u["krag_mm"]))
    bericht += ["", "Ergebnis: " + ("alle dicht, keine Kollisionen" if ok else "FEHLER, nicht drucken")]
    open(os.path.join(OUT, "pruefbericht.txt"), "w", encoding="utf-8").write("\n".join(bericht) + "\n")
    readme = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "export_campus_readme.txt"), encoding="utf-8").read()
    open(os.path.join(OUT, "README.txt"), "w", encoding="utf-8").write(readme)
    zpath = os.path.join(OUT, "druckdaten_campus_1zu%d.zip" % SCALE)
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        z.write(os.path.join(OUT, "README.txt"), "README.txt")
        z.write(os.path.join(OUT, "pruefbericht.txt"), "pruefbericht.txt")
        for name, _, ordner in teile:
            z.write(os.path.join(ordner, name), name)
    print("\n".join(bericht))
    print("%s (%.1f MB)" % (os.path.relpath(zpath, HERE), os.path.getsize(zpath) / 1e6))
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
