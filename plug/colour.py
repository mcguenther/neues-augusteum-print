#!/usr/bin/env python3
"""Farbige Fassung der steckbaren Gebäude (1:1300) mit den Filamenten des Nutzers.

Liest die fertigen Hohlgebäude aus `stl/steckmodul_campus/gebaeude/` (erst `python3 -m plug.buildings`) und den Hof-Einsatz
(`python3 -m plug.campus`), färbt sie nach den Fassaden-Zonen (`fassaden.colour_mesh`, Bezug ist der massive Körper aus
`plug.campus.models_plan`, also derselbe Stand mit Trennfugen und Durchgang) und bildet die Farben auf die Filamente in
`farben.FILAMENTE` ab (vier Hauptfarben, drei Reserven, höchstens `farben.GLEICHZEITIG` je Druck):

  * je Gebäude der beste Satz aus 4 Filamenten (`farben.waehle_filamente`, Reserven nur, wenn sie deutlich besser treffen):
    `<slug>_1zu1300_farbig.3mf`
  * alle sechs Gebäude und der Hof-Einsatz zusammen mit den vier Hauptfarben (ein Druck, Lage wie auf der Platte):
    `alle_1zu1300_hauptfarben.3mf`
  * Farbe: der massive Körper wird gefärbt und dann mit `plug.buildings.gebaeude` (gleiche Lage, Kassette und Rohrstütze wie die STL)
    ausgehöhlt; die Farbe läuft als face_id durch alle Schritte, die Geometrie ist dieselbe wie in der STL (Volumen wird verglichen).
  * einfarbig (wenig Filamentwechsel): jedes Gebäude in der Farbe, die mit den Hauptfarben die größte Außenfläche hat, der Hof Beige
    mit grünen Baumkronen: `<slug>_1zu1300_einfarbig.3mf`
  * Innenflächen (Gewölbe, Schacht) bekommen die Farbe der nächsten Außenfläche, damit die 0,8-mm-Wand durchgefärbt ist; der Fuß
    (unter der Plattenoberseite, steckt in der Mulde) eine einzige Farbe, die der untersten Fassadenzone: dort kein Farbwechsel.

Ausgabe nach `stl/steckmodul_campus/gebaeude_farbig/` (3MF, `filamente.json`, README.md), Bilder nach
`vorschau/steckmodul_campus/farbig/`, Daten der 3D-Seite nach `plug/views/farbig/` (`python3 -m plug.views.farbig.build_view`).

Aufruf (aus dem Repo-Wurzelverzeichnis, ca. 1 min):
    python3 -m plug.colour [slug …]
"""
import argparse
import json
import os
import sys

import manifold3d as m3d
import numpy as np
import trimesh

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

import farben as F            # noqa: E402
import fassaden               # noqa: E402
import generate as G          # noqa: E402
import innenhof               # noqa: E402
from plug import buildings as B  # noqa: E402
from plug import campus as C  # noqa: E402
from plug.testcase import params as P  # noqa: E402

GEB = os.path.join(HERE, "stl", "steckmodul_campus", "gebaeude")
OUT = os.path.join(HERE, "stl", "steckmodul_campus", "gebaeude_farbig")
PREV = os.path.join(HERE, "vorschau", "steckmodul_campus", "farbig")
VIEW = os.path.join(HERE, "plug", "views", "farbig")
HOF_STL = os.path.join(HERE, "stl", "steckmodul_campus", "hof_einsatz_1zu%d.stl")
FUSS_Z = 0.05          # Dreiecke mit Mitte unter dieser Höhe gehören zum Fuß (z = 0 ist die Plattenoberseite)
# Einfarbige Variante (wenig Filamentwechsel): jedes Gebäude in der Farbe, die mit den Hauptfarben die größte Außenfläche hat;
# der Hof-Einsatz Beige mit grünen Baumkronen (Stämme Beige, Nutzer 19.10.)
EINFARBIG_HOF = ("Beige", {"krone": "Grasgrün"})
PFLICHT = {"08_innenhof": ["Grasgrün"]}   # Bäume im Hof grün, auch wenn ihre Fläche klein ist
SOCKEL_H = 1.5         # mm über der Plattenoberseite: Zone, deren häufigste Farbe der Fuß bekommt


def load(path):
    return trimesh.load(path, process=False)


def _naechste(ref, pts, k=12, schritt=0.25):
    """(Abstand, Dreieck) des nächsten Dreiecks von ref je Punkt (ohne rtree): Oberfläche dicht abtasten, die k nächsten
    Abtastpunkte (KD-Baum) nennen die Kandidaten, dazu der genaue Punkt-Dreieck-Abstand."""
    from scipy.spatial import cKDTree
    n = int(ref.area / schritt ** 2) + len(ref.faces)
    smp, fid = trimesh.sample.sample_surface(ref, n, seed=1)
    smp = np.vstack([smp, ref.triangles_center])
    fid = np.concatenate([fid, np.arange(len(ref.faces))])
    _, idx = cKDTree(smp).query(pts, k=k)
    cand = fid[idx]                                              # (n, k)
    tri = ref.triangles[cand.ravel()]
    q = np.repeat(pts, k, axis=0)
    cp = trimesh.triangles.closest_point(tri, q)
    d = np.linalg.norm(cp - q, axis=1).reshape(-1, k)
    j = d.argmin(axis=1)
    return d[np.arange(len(pts)), j], cand[np.arange(len(pts)), j]


def innen_nachfuehren(tm, hexes, outer):
    """Innenflächen über dem Fuß: Farbe der nächsten Außenfläche; Fuß: häufigste Farbe der untersten Zone."""
    hexes = hexes.copy()
    cen = tm.triangles_center
    fuss = cen[:, 2] < FUSS_Z
    rest = ~outer & ~fuss
    if rest.any() and outer.any():
        sub = tm.submesh([np.flatnonzero(outer)], append=True)
        _, tri = _naechste(sub, cen[rest])
        hexes[rest] = hexes[np.flatnonzero(outer)[tri]]
    unten = outer & (cen[:, 2] < SOCKEL_H)
    if not unten.any():
        unten = outer
    vals, inv = np.unique(hexes[unten].astype(str), return_inverse=True)
    area = np.bincount(inv, weights=tm.area_faces[unten])
    hexes[fuss] = vals[area.argmax()]
    return hexes


def dicht(tm):
    """Manifold-Prüfung wie plug.export_campus (der Hof-Einsatz hat Berührkanten, trimesh nennt ihn darum nicht dicht)."""
    man = m3d.Manifold(m3d.Mesh(vert_properties=np.asarray(tm.vertices, dtype=np.float32), tri_verts=np.asarray(tm.faces, dtype=np.uint32)))
    return bool(man.status() == m3d.Error.NoError and man.volume() > 0 and abs(man.volume() - tm.volume) < 1e-3 * abs(tm.volume))


def build(scale=P.SCALE_PLAN, slugs=None):
    """[(slug, name, Netz, Hex je Dreieck (volle Farben), Außenmaske)] der Gebäude und des Hof-Einsatzes."""
    s = 1000.0 / scale
    G.FAST = True
    farben = F.load_farben()
    roof = F.roof_classifier(farben)
    models = C.models_plan(s, scale)
    names = {b["slug"]: b["name"] for b in G.OBJEKTE}
    out = []
    places = json.load(open(C.CACHE % scale))
    for slug in P.CASSETTE:
        if slugs and slug not in slugs:
            continue
        solid, fp, _ = models[slug]
        vorher = json.load(open(os.path.join(GEB, "%s_1zu%d.json" % (slug, scale))))
        # massiven Körper färben (wie generate.colourise), Farbe als face_id durch alle Schritte von plug.buildings mitnehmen
        cm, hx = fassaden.colour_mesh(G.to_trimesh(solid), slug, ((0.0, 0.0, 0.0), s), farben[slug], roof)
        keys, inv = np.unique(hx.astype(str), return_inverse=True)
        man = m3d.Manifold(m3d.Mesh(vert_properties=np.array(cm.vertices, np.float32, order="C"),
                                    tri_verts=np.array(cm.faces, np.uint32, order="C"), face_id=np.array(inv.ravel() + B.FARB_ID0, np.uint32)))
        body, _, info = B.gebaeude(slug, man, fp, places[slug], s, vorher["rohrstuetze"], farb_id=True)
        m = body.to_mesh()
        mesh = trimesh.Trimesh(np.asarray(m.vert_properties)[:, :3], np.asarray(m.tri_verts), process=False)
        fid = np.asarray(m.face_id).astype(np.int64)
        outer = (fid > 0) & (mesh.triangles_center[:, 2] >= FUSS_Z)
        hexes = np.array([keys[i - 1] if i > 0 else farben[slug]["farben"][farben[slug]["basis"]]["rgb"] for i in fid], dtype=object)
        print("  %-22s %6d Dreiecke, davon %d außen, %.2f cm³ (STL %.2f cm³), dicht=%s" % (
            slug, len(mesh.faces), outer.sum(), info["volumen_cm3"], vorher["volumen_cm3"], mesh.is_watertight), flush=True)
        out.append((slug, names[slug], mesh, hexes, outer))
    if not slugs or G.HOF["slug"] in slugs:
        tm = trimesh.load(HOF_STL % scale)          # mit Zusammenführen der Eckpunkte (STL), sonst nicht dicht
        hexes = innenhof.colour_mesh(tm, ((0.0, 0.0, 0.0), s), farben[G.HOF["slug"]])
        outer = tm.face_normals[:, 2] > -0.5            # Unterseite liegt in der Aussparung
        print("  %-22s %6d Dreiecke, dicht=%s" % (G.HOF["slug"], len(tm.faces), dicht(tm)), flush=True)
        out.append((G.HOF["slug"], G.HOF["name"], tm, hexes, outer))
    return out, farben


def reduziert(teil, satz, farben):
    slug, name, mesh, hexes, outer = teil
    red = F.reduziere(slug, farben.get(slug), mesh, hexes, satz, farben)
    if slug != G.HOF["slug"]:
        red = innen_nachfuehren(mesh, red, outer)
    return red


def einfarbig(slug, mesh, hexes, outer, red_h, farben):
    """Hex je Dreieck der einfarbigen Variante (siehe EINFARBIG_HOF)."""
    hex_of = {n: c for c, n in F.FILAMENTE}
    if slug == G.HOF["slug"]:
        grund, teile = EINFARBIG_HOF
        out = np.array([hex_of[grund]] * len(hexes), dtype=object)
        for key, name in teile.items():
            out[hexes == farben[slug]["farben"][key]["rgb"]] = hex_of[name]
        return out
    vals, inv = np.unique(red_h[outer].astype(str), return_inverse=True)
    c = vals[np.bincount(inv, weights=mesh.area_faces[outer]).argmax()]
    return np.array([c] * len(hexes), dtype=object)


def anteile(mesh, hexes, outer, satz):
    """Anteil der Außenfläche je Filament des Satzes (%)."""
    a = mesh.area_faces[outer]
    tot = a.sum() or 1.0
    h = hexes[outer]
    return {n: round(100 * float(a[h == c].sum()) / tot, 1) for c, n in satz}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--scale", type=int, default=P.SCALE_PLAN)
    a = ap.parse_args()
    for d in (OUT, PREV, VIEW):
        os.makedirs(d, exist_ok=True)
    teile, farben = build(a.scale, a.slugs)
    info = {"filamente": [{"rgb": c, "name": n, "rolle": "Hauptfarbe" if (c, n) in F.HAUPT else ("vorerst nicht verwendet" if n in F.GESPERRT else "Reserve")} for c, n in F.FILAMENTE],
            "gebaeude": {}}
    einzeln, haupt = {}, []
    for t in teile:
        slug, name, mesh, hexes, outer = t
        satz, kosten = F.waehle_filamente([(slug, mesh, hexes, outer.astype(float))], farben, pflicht=PFLICHT.get(slug, ()))
        red = reduziert(t, satz, farben)
        satz = [f for f in satz if (red == f[0]).any()]     # nicht gebrauchte Spulen weglassen (dann reichen weniger als 4)
        path = os.path.join(OUT, "%s_1zu%d_farbig.3mf" % (slug, a.scale))
        G.export_3mf([(name, mesh, red)], path, profil=satz)
        _, k_haupt = F.waehle_filamente([(slug, mesh, hexes, outer.astype(float))], farben, pflicht=[n for _, n in F.HAUPT])
        red_h = reduziert(t, F.HAUPT, farben)
        haupt.append((name, mesh, red_h))
        red_1 = einfarbig(slug, mesh, hexes, outer, red_h, farben)
        satz_1 = [f for f in F.FILAMENTE if (red_1 == f[0]).any()]
        path_1 = os.path.join(OUT, "%s_1zu%d_einfarbig.3mf" % (slug, a.scale))
        G.export_3mf([(name, mesh, red_1)], path_1, profil=satz_1)
        einzeln[slug] = (name, mesh, red, satz, outer, red_h, red_1)
        info["gebaeude"][slug] = {"name": name, "datei": os.path.basename(path), "satz": [n for _, n in satz],
                                  "abweichung_dE": round(kosten - F.RESERVE_KOSTEN * sum(1 for x in satz if x in F.RESERVE), 1),
                                  "abweichung_hauptfarben_dE": round(k_haupt, 1),
                                  "anteile_prozent": anteile(mesh, red, outer, satz), "dreiecke": int(len(mesh.faces)),
                                  "einfarbig": [n for _, n in satz_1], "datei_einfarbig": os.path.basename(path_1),
                                  "dicht": dicht(mesh)}
        print("  %-60s %s" % (os.path.relpath(path_1, HERE), ", ".join(n for _, n in satz_1)))
        print("  %-60s %s  ΔE %.1f (nur Hauptfarben %.1f)  dicht=%s" % (os.path.relpath(path, HERE), ", ".join(n for _, n in satz),
                                                                    info["gebaeude"][slug]["abweichung_dE"], k_haupt, info["gebaeude"][slug]["dicht"]))
    if not a.slugs:
        path = os.path.join(OUT, "alle_1zu%d_hauptfarben.3mf" % a.scale)
        G.export_3mf(haupt, path, profil=F.HAUPT)
        print("  %s (%d Objekte, Hauptfarben)" % (os.path.relpath(path, HERE), len(haupt)))
        info["alle"] = os.path.basename(path)
        json.dump(info, open(os.path.join(OUT, "filamente.json"), "w"), indent=1, ensure_ascii=False)
        readme(info, a.scale)
    bilder(einzeln, a.scale)
    from plug.views.farbig import build_view
    build_view.daten(einzeln, info, a.scale)
    print("alle dicht" if all(g["dicht"] for g in info["gebaeude"].values()) else "ACHTUNG: nicht alle dicht")


def readme(info, scale):
    z = ["# Steckbare Gebäude farbig (1:%d)" % scale, "",
         "Erzeugt mit `python3 -m plug.colour` aus den Gebäuden in `../gebaeude/` (gleiche Geometrie, gleiche Lage) und dem Hof-Einsatz.",
         "Filamente des Nutzers (Hex-Werte geschätzt, in `farben.FILAMENTE` anpassen): " +
         ", ".join("%s `%s`%s" % (f["name"], f["rgb"], "" if f["rolle"] == "Hauptfarbe" else " (%s)" % f["rolle"]) for f in info["filamente"]) + ".",
         "Höchstens %d Filamente je Druck. 3D-Ansicht: `plug/views/farbig/view.html`. Slicer-Einstellungen: `plug/slicer.md`." % F.GLEICHZEITIG, "",
         "| Datei | Filamente (Slot 1–4) | Anteile der Außenfläche | ΔE (nur Hauptfarben) | einfarbig (`*_einfarbig.3mf`) |", "|---|---|---|---|---|"]
    for g in info["gebaeude"].values():
        z.append("| `%s` | %s | %s | %.1f (%.1f) | %s |" % (g["datei"], ", ".join(g["satz"]), ", ".join("%s %.0f %%" % kv for kv in g["anteile_prozent"].items() if kv[1] > 0),
                                                          g["abweichung_dE"], g["abweichung_hauptfarben_dE"], ", ".join(g["einfarbig"])))
    z += ["", "`%s`: alle Gebäude und der Hof-Einsatz in einem Druck mit den vier Hauptfarben (Lage wie auf der Steckplatte)." % info.get("alle", ""),
          "", "Einfarbig (wenig Filamentwechsel): jedes Gebäude in einer Farbe, nur der Hof-Einsatz hat grüne Baumkronen (Wechsel nur in den Lagen der Kronen).",
          "Gebäude mit derselben Farbe lassen sich zusammen ohne Wechsel drucken.",
          "", "Im Slicer die Filamentfarben einmal den Slots zuordnen (die 3MF nennt die Namen als Material F1 … F4); bemalt sind die Außenflächen,",
          "Innenflächen haben die Farbe der nächsten Außenwand, der Fuß eine einzige Farbe. Ungedruckt.", ""]
    open(os.path.join(OUT, "README.md"), "w").write("\n".join(z))


def bilder(einzeln, scale):
    """Je Gebäude ein Bild von Südosten und Nordwesten mit dem gewählten Satz; dazu die Übersicht aller."""
    import preview
    for slug, (name, mesh, red, satz, outer, _, _) in einzeln.items():
        cols = np.array([preview.rgb(h) for h in red])
        ims = [preview.render([(mesh, cols)], size=(700, 700), azim=az, elev=25, light_from_view=True) for az in (-50, 130)]
        from PIL import Image
        im = Image.new("RGB", (1400, 700), preview.BG)
        im.paste(ims[0], (0, 0))
        im.paste(ims[1], (700, 0))
        im = preview.caption(im, "%s · farbig 1:%d" % (name, scale), "Filamente: " + ", ".join(n for _, n in satz))
        path = os.path.join(PREV, "%s.png" % slug)
        im.save(path, optimize=True)
        print("  Vorschau:", os.path.relpath(path, HERE))
    plate = load(os.path.join(HERE, "stl", "steckmodul_campus", "steckplatte_1zu%d.stl" % scale))
    T = C.plate_thickness(P.dims_plan())
    for key, titel in (("satz", "je Gebäude der beste Satz"), ("haupt", "nur die vier Hauptfarben"), ("einfarbig", "jedes Gebäude einfarbig")):
        sel = [(plate, np.array([preview.rgb(F.HAUPT[3][0])] * len(plate.faces)))]
        for slug, (name, mesh, red, satz, outer, red_h, red_1) in einzeln.items():
            m = mesh.copy()
            m.apply_translation([0, 0, T])
            sel.append((m, np.array([preview.rgb(h) for h in {"satz": red, "haupt": red_h, "einfarbig": red_1}[key]])))
        im = preview.render(sel, size=(1400, 1000), azim=-35, elev=35, light_from_view=True)
        im = preview.caption(im, "Steckplatte 1:%d farbig" % scale, titel)
        path = os.path.join(PREV, "uebersicht_%s.png" % key)
        im.save(path, optimize=True)
        print("  Vorschau:", os.path.relpath(path, HERE))


if __name__ == "__main__":
    main()
