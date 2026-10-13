#!/usr/bin/env python3
"""Fassaden-Zonen: färbt Gebäudenetze abschnittsweise ein.

Je Gebäude beschreibt data/fassaden/<slug>.json die Farben (gemessen in Fotos,
siehe farben.py) und die Zonen der Fassaden:

    {
      "farben": {"platten": {"notiz": "...", "proben": [{"bild": "...", "box": [x0, y0, x1, y1]}]},
                 "glas":    {"notiz": "...", "hex": "#334455"}},      # hex = feste Farbe statt Messung
      "basis": "platten",                 # Farbe aller Wände ohne passende Zone
      "zonen": [                          # spätere Zonen überschreiben frühere
        {"name": "Sockel", "farbe": "sockel", "z": [0, 4.2]},
        {"name": "Fensterband 1. OG", "farbe": "glas", "seite": "W", "z": [5.0, 6.4],
         "entlang": [0.1, 0.9]},
        {"name": "Glasdach", "farbe": "glas", "flaechen": "dach", "entlang": [0.6, 1.0], "seite": "O"}
      ]
    }

Zonen-Felder (alle optional außer farbe):
  z        [z0, z1] Höhe in m über Gelände (Wände: Höhe der Dreiecksmitte)
  seite    Himmelsrichtung der Wand-Außenseite: N, NO, O, SO, S, SW, W, NW (±45°)
           oder [von, bis] in Grad (Kompass, 0 = Nord, 90 = Ost)
  entlang  [t0, t1] Anteil entlang der Fassade dieser Seite, von links nach rechts
           gesehen von außen (0 = linkes Ende, 1 = rechtes Ende der Seite); nur mit seite
  flaechen "wand" (Standard), "dach" oder "alle"
  kreis    {"entlang": Mitte (Anteil), "z": Mitte (m), "d": Durchmesser (m)} statt z/entlang:
           runde Fläche (z. B. Rosette), angenähert durch "stufen" (Standard 7) Streifen; nur mit seite
  bogen    {"entlang": Mitte, "breite": Spannweite (m), "z0": Unterkante (m), "kaempfer": Kämpferhöhe (m)}:
           Spitzbogen (gleichseitig, Scheitel = Kämpfer + 0,866 · Breite), z. B. gotisches
           Fenster; senkrechter Teil als ein Rechteck, Bogen in "stufen" (Standard 6) Streifen
Das Netz wird an allen Zonengrenzen (Höhen, entlang-Positionen) zerschnitten,
damit die Farbgrenzen exakt liegen. Dächer ohne Dach-Zone bekommen die Klasse
der Dachpalette, die das Luftbild dort zeigt.

Prüfen:  python3 fassaden.py 03_hoersaalgebaeude [--quelle lod2] [--out ordner]
  rendert das Gebäude von allen Seiten mit Raster (Höhe in m, entlang-Anteil) und
  daneben die Fotos mit den Messfeldern dieses Gebäudes.
"""
import argparse
import json
import os

import numpy as np
import trimesh

import generate as G

DIR = os.path.join(G.HERE, "data", "fassaden")
ROOF_NZ = 0.35       # wie generate.ROOF_NZ: steilere Normale = Dach
SEITEN = {"N": 0, "NO": 45, "O": 90, "SO": 135, "S": 180, "SW": 225, "W": 270, "NW": 315}


def load_spec(slug):
    path = os.path.join(DIR, slug + ".json")
    return json.load(open(path)) if os.path.exists(path) else None


# --------------------------------------------------------------------------
# Geometrie
# --------------------------------------------------------------------------
def face_kind(normals):
    """0 = Wand, 1 = Dach, 2 = Unterseite."""
    nz = normals[:, 2]
    return np.where(nz > ROOF_NZ, 1, np.where(nz < -ROOF_NZ, 2, 0))


def azimuth(normals):
    """Kompassrichtung (Grad) der horizontalen Normalenkomponente."""
    return np.degrees(np.arctan2(normals[:, 0], normals[:, 1])) % 360


def side_mask(normals, seite):
    az = azimuth(normals)
    if isinstance(seite, str):
        a0, a1 = SEITEN[seite.upper().replace("Ö", "O")] - 45, SEITEN[seite.upper().replace("Ö", "O")] + 45
    else:
        a0, a1 = seite
    a0, a1 = a0 % 360, a1 % 360
    return (az >= a0) & (az < a1) if a0 < a1 else (az >= a0) | (az < a1)


def side_axis(seite):
    """Einheitsvektor „nach rechts“, von außen auf die Fassade gesehen."""
    a = SEITEN[seite.upper()] if isinstance(seite, str) else (seite[0] + (seite[1] - seite[0]) % 360 / 2)
    n = np.array([np.sin(np.radians(a)), np.cos(np.radians(a))])
    return np.array([-n[1], n[0]])


def side_extent(mesh, seite):
    """(axis, tmin, tmax) der Wände einer Seite (Koordinaten des Netzes)."""
    walls = (face_kind(mesh.face_normals) == 0) & side_mask(mesh.face_normals, seite)
    if not walls.any():
        return None
    ax = side_axis(seite)
    t = mesh.triangles[walls][:, :, :2].reshape(-1, 2) @ ax
    return ax, t.min(), t.max()


def split_plane(mesh, normal, origin):
    """Zerschneidet alle Dreiecke an einer Ebene; das Netz bleibt geschlossen."""
    from trimesh.intersections import slice_mesh_plane
    normal = np.asarray(normal, float)
    a = slice_mesh_plane(mesh, normal, origin, cap=False)
    b = slice_mesh_plane(mesh, -normal, origin, cap=False)
    if len(a.faces) == 0 or len(b.faces) == 0:
        return mesh
    m = trimesh.util.concatenate([a, b])
    # Nur Punkte auf der Schnittebene zusammenführen: Das Ausgangsnetz kann an
    # Engstellen getrennte Eckpunkte an derselben Position haben (Manifold), die
    # getrennt bleiben müssen.
    v = m.vertices
    on = np.abs(v @ normal - np.dot(normal, origin)) < 1e-7 * max(1.0, np.abs(v).max())
    idx = np.arange(len(v))
    if on.any():
        key = np.round(v[on], 6)
        _, first, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
        idx[on] = np.nonzero(on)[0][first][inv.ravel()]
    f = idx[m.faces]
    keep = (f[:, 0] != f[:, 1]) & (f[:, 1] != f[:, 2]) & (f[:, 0] != f[:, 2])
    m = trimesh.Trimesh(v, f[keep], process=False)
    m.remove_unreferenced_vertices()
    return m


def expand_zones(mesh, zones):
    """Löst runde (kreis) und spitzbogige (bogen) Zonen in Rechteck-Streifen auf."""
    out = []
    for zo in zones:
        form = "kreis" if "kreis" in zo else "bogen" if "bogen" in zo else None
        if form is None:
            out.append(zo)
            continue
        ext = side_extent(mesh, zo["seite"])
        if ext is None:
            continue
        L = ext[2] - ext[1]
        base = {key: v for key, v in zo.items() if key not in ("kreis", "bogen", "stufen")}
        k = zo[form]
        fc = k["entlang"]
        if form == "kreis":
            n, r, zc = int(zo.get("stufen", 7)), k["d"] / 2, k["z"]
            bands = [(zc - r + 2 * r * i / n, zc - r + 2 * r * (i + 1) / n) for i in range(n)]
            half = lambda zm: np.sqrt(max(r * r - (zm - zc) ** 2, 0))
        else:
            n, S, zk = int(zo.get("stufen", 6)), k["breite"], k["kaempfer"]
            rise = S * np.sqrt(3) / 2
            bands = [(k["z0"], zk)] + [(zk + rise * i / n, zk + rise * (i + 1) / n) for i in range(n)]
            half = lambda zm: S / 2 if zm <= zk else max(np.sqrt(max(S * S - (zm - zk) ** 2, 0)) - S / 2, 0)
        for z0, z1 in bands:
            w = half((z0 + z1) / 2) / L
            if w > 0:
                out.append(dict(base, z=[z0, z1], entlang=[fc - w, fc + w]))
    return out


def zone_planes(mesh, zones):
    """Schnittebenen (normal, origin) für alle Zonengrenzen."""
    planes = []
    zmax = mesh.bounds[1][2]
    for zo in zones:
        for z in zo.get("z", []):
            if 0.01 < z < zmax - 0.01:
                planes.append(((0, 0, 1), (0, 0, float(z))))
        if "entlang" in zo and "seite" in zo:
            ext = side_extent(mesh, zo["seite"])
            if ext is None:
                continue
            ax, t0, t1 = ext
            for f in zo["entlang"]:
                if 0.001 < f < 0.999:
                    t = t0 + f * (t1 - t0)
                    planes.append(((ax[0], ax[1], 0), (ax[0] * t, ax[1] * t, 0)))
    uniq = []
    for n, o in planes:
        if not any(np.allclose(n, n2) and abs(np.dot(n, np.subtract(o, o2))) < 0.02 for n2, o2 in uniq):
            uniq.append((n, o))
    return uniq


def zone_keys(mesh, spec, extents):
    """Farbschlüssel je Dreieck (None = Dach aus Luftbild)."""
    kind = face_kind(mesh.face_normals)
    c = mesh.triangles_center
    keys = np.array([spec["basis"]] * len(mesh.faces), dtype=object)
    keys[kind == 1] = None
    for zo in spec.get("zonen", []):
        fl = zo.get("flaechen", "wand")
        sel = {"wand": kind == 0, "dach": kind == 1, "alle": kind != 2}[fl]
        if "z" in zo:
            sel &= (c[:, 2] >= zo["z"][0]) & (c[:, 2] < zo["z"][1])
        if "seite" in zo:
            if fl == "wand":
                sel &= side_mask(mesh.face_normals, zo["seite"])
            if "entlang" in zo:
                ext = extents.get(json.dumps(zo["seite"]))
                if ext is None:
                    continue
                ax, t0, t1 = ext
                t = (c[:, :2] @ ax - t0) / max(t1 - t0, 1e-9)
                sel &= (t >= zo["entlang"][0]) & (t < zo["entlang"][1])
        keys[sel] = zo["farbe"]
    return keys


def colour_mesh(tm, slug, to_local, farben, roof_class):
    """Zerschneidet ein Gebäudenetz an seinen Zonengrenzen und färbt es.

    tm        Netz in Modellkoordinaten (mm)
    to_local  (offset[3], s): lokal_m = (v - offset) / s; z = Höhe über Gelände
    farben    Eintrag des Gebäudes aus data/farben.json ({"farben": {key: {"rgb"}}, "basis", "zonen"})
    roof_class Funktion (punkte_lokal_m[n,2]) -> Hex-Farbe der Dachpalette
    Liefert (Netz in Modellkoordinaten, Hex-Farbe je Dreieck).
    """
    off, s = np.asarray(to_local[0], float), float(to_local[1])
    m = trimesh.Trimesh((tm.vertices - off) / s, tm.faces.copy(), process=False)
    zones = expand_zones(m, farben.get("zonen", [])) if farben else []
    dicht = m.is_watertight
    planes = zone_planes(m, zones)
    # Schnellweg: alle Schnitte ohne Zwischenprüfung; die Dichtheitsprüfung kostet mehr als
    # der Schnitt. Ist das Ergebnis dicht, wäre es auch jeder Zwischenstand gewesen.
    m_fast = m
    for n, o in planes:
        m_fast = split_plane(m_fast, n, o)
    if not dicht or m_fast.is_watertight:
        m = m_fast
    else:
        for n, o in planes:
            # Ebenen, die genau durch Engstellen des Netzes laufen, minimal verschieben
            for d in (0.0, 0.003, -0.003, 0.01, -0.01):
                m2 = split_plane(m, n, np.asarray(o, float) + d * np.asarray(n, float))
                if m2.is_watertight:
                    m = m2
                    break
    extents = {}
    for zo in zones:
        if "seite" in zo and "entlang" in zo:
            extents[json.dumps(zo["seite"])] = side_extent(m, zo["seite"])
    if farben:
        keys = zone_keys(m, dict(farben, zonen=zones), extents)
        hexes = np.array([farben["farben"][k]["rgb"] if k else None for k in keys], dtype=object)
    else:
        hexes = np.array([None] * len(m.faces), dtype=object)
    roof = np.array([h is None for h in hexes])
    if roof.any():
        hexes[roof] = roof_class(m.triangles[roof][:, :, :2])
    out = trimesh.Trimesh(m.vertices * s + off, m.faces, process=False)
    return out, hexes


# --------------------------------------------------------------------------
# Prüfansicht
# --------------------------------------------------------------------------
def check(slug, quelle="lod2", out=None):
    """Ansichten des eingefärbten Gebäudes mit Raster + Fotos mit Messfeldern."""
    import farben as F
    import preview as P
    from PIL import Image, ImageDraw
    out = out or os.path.join(G.HERE, "vorschau", "fassaden")
    os.makedirs(out, exist_ok=True)
    spec = F.building_colours(slug)
    models = G.source_models(quelle, 1.0)  # s = 1: Modell in m
    solid = models[slug][0]
    tm = G.to_trimesh(solid)
    roof_class = F.roof_classifier()
    mesh, hexes = colour_mesh(tm, slug, ((0, 0, 0), 1.0), spec, roof_class)
    cols = np.array([P.rgb(h) for h in hexes])
    tiles = []
    H = mesh.bounds[1][2]
    for seite in ("N", "O", "S", "W"):
        ext = side_extent(mesh, seite)
        a = SEITEN[seite]
        im, proj = P.render([(mesh, cols)], size=(900, 520), azim=90 - a, elev=0, return_proj=True, flat=True)
        d = ImageDraw.Draw(im)
        if ext is not None:
            ax, t0, t1 = ext
            # Raster: entlang-Anteile (vertikale Linien) und Höhen (horizontale Linien)
            base = np.array([ax[0], ax[1], 0.0])
            nrm = np.array([np.sin(np.radians(a)), np.cos(np.radians(a)), 0.0])
            front = mesh.vertices[:, :2] @ nrm[:2]
            p0 = nrm * front.max()
            for f in np.linspace(0, 1, 11):
                pa, pb = p0 + base * (t0 + f * (t1 - t0)), p0 + base * (t0 + f * (t1 - t0)) + [0, 0, H]
                (xa, ya), (xb, yb) = proj(pa), proj(pb)
                d.line((xa, ya, xb, yb), fill=(0, 160, 0), width=1)
                d.text((xa + 2, ya + 2), "%.1f" % f, fill=(0, 120, 0), font=P.font(11))
            step = 2 if H < 40 else 10
            for z in np.arange(0, H + 0.01, step):
                pa, pb = p0 + base * t0 + [0, 0, z], p0 + base * t1 + [0, 0, z]
                (xa, ya), (xb, yb) = proj(pa), proj(pb)
                d.line((xa, ya, xb, yb), fill=(220, 0, 160), width=1)
                d.text((xa - 34, ya - 7), "%g m" % z, fill=(200, 0, 140), font=P.font(11))
        tiles.append(P.caption(im, "%s – Fassade %s" % (slug, seite),
                               "grün: entlang-Anteil (von außen links→rechts) · magenta: Höhe über Gelände"))
    sw = Image.new("RGB", (900, 60 + 36 * len(spec["farben"])), P.BG)
    d = ImageDraw.Draw(sw)
    d.text((10, 10), "Farben (%s)" % slug, fill=(30, 30, 30), font=P.font(20, True))
    for i, (k, v) in enumerate(spec["farben"].items()):
        y = 44 + 36 * i
        d.rectangle((10, y, 70, y + 28), fill=v["rgb"], outline=(60, 60, 60))
        d.text((80, y + 6), "%s  %s  %s" % (k, v["rgb"], v.get("notiz", "")), fill=(30, 30, 30), font=P.font(14))
    tiles.append(sw)
    W = max(t.width for t in tiles)
    sheet = Image.new("RGB", (W * 2, sum(t.height for t in tiles[::2]) + 10), P.BG)
    y = 0
    for i in range(0, len(tiles), 2):
        sheet.paste(tiles[i], (0, y))
        if i + 1 < len(tiles):
            sheet.paste(tiles[i + 1], (W, y))
        y += max(t.height for t in tiles[i:i + 2])
    p1 = os.path.join(out, "%s_zonen.png" % slug)
    sheet.save(p1, optimize=True)
    p2 = os.path.join(out, "%s_fotos.jpg" % slug)
    F.probe_sheet(F.building_probes(slug), p2)
    print("  Vorschau:", os.path.relpath(p1, G.HERE), "+", os.path.relpath(p2, G.HERE))
    return p1, p2


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slug")
    ap.add_argument("--quelle", default="lod2", choices=G.QUELLEN)
    ap.add_argument("--out")
    a = ap.parse_args()
    check(a.slug, a.quelle, a.out)
