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
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from plug.divider import check as DC  # noqa: E402
from plug.testcase import params as P  # noqa: E402

OUT = os.path.join(HERE, "stl", "steckmodul_campus")
SCALE = P.SCALE_PLAN
NAMEN = {"01_paulinum": "Paulinum", "02_neues_augusteum": "Neues Augusteum", "03_hoersaalgebaeude": "Hörsaalgebäude",
         "04_seminargebaeude": "Seminargebäude", "05_institutsgebaeude": "Institutsgebäude", "06_city_hochhaus": "City-Hochhaus"}


def aufgeschnitten(path):
    """Übersichtsbild: alle sechs Gebäude an einer senkrechten Ebene durch die Mitte aufgeschnitten (Blick von Osten), zeigt Wand, Gewölbe und Schacht."""
    import preview
    kacheln = []
    for slug in DC.SLUGS:
        tm = trimesh.load(os.path.join(OUT, "gebaeude", "%s_1zu%d.stl" % (slug, SCALE)))
        man = m3d.Manifold(m3d.Mesh(vert_properties=np.asarray(tm.vertices, dtype=np.float32), tri_verts=np.asarray(tm.faces, dtype=np.uint32)))
        lo, hi = tm.bounds
        cx = (lo[0] + hi[0]) / 2
        keep = m3d.Manifold.cube((cx - (lo[0] - 5), hi[1] - lo[1] + 10, hi[2] - lo[2] + 10)).translate((lo[0] - 5, lo[1] - 5, lo[2] - 5))
        mesh = (man ^ keep).to_mesh()
        ct = trimesh.Trimesh(np.asarray(mesh.vert_properties)[:, :3], np.asarray(mesh.tri_verts), process=False)
        img = preview.render([(ct, "#b9c3cf")], size=(520, 520), azim=0, elev=18).convert("RGB")
        ImageDraw.Draw(img).text((10, 8), NAMEN[slug] + " (aufgeschnitten)", fill="black")
        kacheln.append(img)
    bild = Image.new("RGB", (520 * 3, 520 * 2), "white")
    for i, k in enumerate(kacheln):
        bild.paste(k, ((i % 3) * 520, (i // 3) * 520))
    bild.save(path)


def schachtbilder(path_schnitt, path_unten):
    """Zwei Übersichtsbilder zur Kassettenaufnahme: (1) Unterseiten aller sechs Gebäude, (2) Schnitte quer und längs durch die Schachtmitte der v4-Gebäude
    (Anschlagring der v4 bei 4 bis 4,5 mm über der Platte, darüber Platz für LED und Streifen)."""
    import preview
    placements = json.load(open(os.path.join(HERE, "plug", "scale1176", "placements_%d.json" % SCALE)))
    kacheln = []
    for slug in DC.SLUGS:
        tm = trimesh.load(os.path.join(OUT, "gebaeude", "%s_1zu%d.stl" % (slug, SCALE)))
        img = preview.render([(tm, "#b9c3cf")], size=(520, 520), azim=-90, elev=-80).convert("RGB")
        ImageDraw.Draw(img).text((10, 8), NAMEN[slug] + " von unten", fill="black")
        kacheln.append(img)
    bild = Image.new("RGB", (520 * 3, 520 * 2), "white")
    for i, k in enumerate(kacheln):
        bild.paste(k, ((i % 3) * 520, (i // 3) * 520))
    bild.save(path_unten)
    kacheln = []
    for slug in [s for s in DC.SLUGS if placements[s]["var"] == "v4"]:
        p = placements[slug]
        a = np.radians(-p["angle"])
        tm = trimesh.load(os.path.join(OUT, "gebaeude", "%s_1zu%d.stl" % (slug, SCALE)))
        v = np.asarray(tm.vertices).copy()
        v[:, 0] -= p["cx"]
        v[:, 1] -= p["cy"]
        v[:, :2] = v[:, :2] @ np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]]).T
        man = m3d.Manifold(m3d.Mesh(vert_properties=v.astype(np.float32), tri_verts=np.asarray(tm.faces, dtype=np.uint32)))
        big = 200.0
        for art, azim in (("quer", 0), ("längs", 90)):
            keep = (m3d.Manifold.cube((big, 2 * big, 2 * big)).translate((-big, -big, -big)) if art == "quer"
                    else m3d.Manifold.cube((2 * big, big, 2 * big)).translate((-big, -big, -big)))
            mesh = (man ^ keep).to_mesh()
            ct = trimesh.Trimesh(np.asarray(mesh.vert_properties)[:, :3], np.asarray(mesh.tri_verts), process=False)
            img = preview.render([(ct, "#b9c3cf")], size=(520, 560), azim=azim, elev=12).convert("RGB")
            ImageDraw.Draw(img).text((10, 8), "%s, Schnitt %s durch die Schachtmitte" % (NAMEN[slug], art), fill="black")
            kacheln.append(img)
    bild = Image.new("RGB", (520 * 2, 560 * 3), "white")
    for i, k in enumerate(kacheln):
        bild.paste(k, ((i % 2) * 520, (i // 2) * 560))
    bild.save(path_schnitt)


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
    bild = os.path.join(OUT, "gebaeude", "uebersicht_aufgeschnitten.png")
    aufgeschnitten(bild)
    bild_unten = os.path.join(OUT, "gebaeude", "uebersicht_unterseiten.png")
    bild_schacht = os.path.join(OUT, "gebaeude", "uebersicht_schacht_schnitt.png")
    schachtbilder(bild_schacht, bild_unten)
    zpath = os.path.join(OUT, "druckdaten_campus_1zu%d.zip" % SCALE)
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        z.write(os.path.join(OUT, "README.txt"), "README.txt")
        z.write(os.path.join(OUT, "pruefbericht.txt"), "pruefbericht.txt")
        z.write(bild, "uebersicht_aufgeschnitten.png")
        z.write(bild_unten, "uebersicht_unterseiten.png")
        z.write(bild_schacht, "uebersicht_schacht_schnitt.png")
        for name, _, ordner in teile:
            z.write(os.path.join(ordner, name), name)
    print("\n".join(bericht))
    print("%s (%.1f MB)" % (os.path.relpath(zpath, HERE), os.path.getsize(zpath) / 1e6))
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
