"""Daten der Produktseite (`product/index.html`): reduzierte 3D-Netze aller Teile in Weltlage und Bilder als WebP.

Liest die fertigen STL (erst `python3 -m plug.campus`, `plug.buildings`, `plug.power.build_unterkasten8`), setzt Steckplatte, sechs
Gebäude, Hof-Einsatz, Display-Gebäude, Kassetten mit LED-Streifen, Unterkasten (Stand 8), Powerbank, ESP32 und Hauptschalter in eine
gemeinsame Lage (z = 0 Plattenoberseite, mm) und schreibt

- `product/assets/model.json` Inhaltsverzeichnis (Teil, Gruppe, Versatz, Anzahl, Box) und die Netze als base64 im Feld `bin`
  (Ecken als uint16 über die Gesamtbox, Dreiecke als uint16/uint32; Artifacts liefern keine Binärdateien aus)
- `product/assets/*.webp`     Bilder aus `vorschau/` für die Seite

Aufruf: `python3 -m product.build_assets` (ca. 30 s).
"""
import base64
import contextlib
import io
import json
import os

import fast_simplification
import numpy as np
import trimesh
from PIL import Image

from plug import buildings as BU
from plug import campus as C
from plug import campus_display as CD
from plug.display import body4 as B
from plug.geom import to_tm
from plug.power import kasten8 as K8
from plug.power import params as PP
from plug.testcase import params as P

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, "assets")
GEB = os.path.join(ROOT, "stl", "steckmodul_campus", "gebaeude")

# Anteil der Dreiecke, der nach dem Reduzieren bleibt (Laserscan-Dächer sind sehr fein; für den Bildschirm reicht weniger)
KEEP = {"building": 0.22, "plate": 0.6, "hof": 0.8}

TITLES = {
    "01_paulinum": "Paulinum",
    "02_neues_augusteum": "Neues Augusteum",
    "03_hoersaalgebaeude": "Hörsaalgebäude",
    "04_seminargebaeude": "Seminargebäude",
    "05_institutsgebaeude": "Institutsgebäude",
    "06_city_hochhaus": "City-Hochhaus",
}

IMAGES = {  # Ziel: (Quelle, größte Breite)
    "hero.webp": ("vorschau/readme/hero.png", 1600),
    "farbig.webp": ("vorschau/steckmodul_campus/farbig/uebersicht_haupt.png", 1000),
    "quelle_osm.webp": ("vorschau/readme/campus_osm.png", 900),
    "quelle_lod2.webp": ("vorschau/readme/campus_lod2.png", 900),
    "quelle_laserscan.webp": ("vorschau/readme/campus_laserscan.png", 900),
}


def simplify(m, keep):
    if keep >= 1.0 or len(m.faces) < 2000:
        return m
    v, f = fast_simplification.simplify(np.asarray(m.vertices, "f4"), np.asarray(m.faces, "i4"), target_reduction=1.0 - keep)
    return trimesh.Trimesh(v, f, process=False)


def box(x0, y0, z0, x1, y1, z1):
    return trimesh.creation.box(bounds=[[x0, y0, z0], [x1, y1, z1]])


def parts():
    """Liste (name, gruppe, titel, trimesh) in Weltlage."""
    out = []
    d = P.dims_plan()
    T = C.plate_thickness(d)
    plate = trimesh.load(os.path.join(ROOT, "stl", "steckmodul_campus", "steckplatte_1zu1300.stl"))
    minx, miny = plate.bounds[0][:2]                     # Rohkoordinaten der Platte: Unterseite z = 0, Ecke Südwest (minx, miny)
    out.append(("steckplatte", "plate", "Steckplatte", simplify(plate.apply_translation([0, 0, -T]), KEEP["plate"])))
    hof = trimesh.load(os.path.join(ROOT, "stl", "steckmodul_campus", "hof_einsatz_1zu1300.stl"))
    out.append(("hof", "hof", "Innenhof", simplify(hof, KEEP["hof"])))

    for slug, title in TITLES.items():
        m = trimesh.load(os.path.join(GEB, "%s_1zu%d.stl" % (slug, P.SCALE_PLAN)))
        out.append((slug, "building", title, simplify(m, KEEP["building"])))

    # Kassetten mit LED-Streifen an ihrem Platz im Schacht (wie plug.buildings.gebaeude)
    places = json.load(open(C.CACHE % P.SCALE_PLAN))
    F = d["F"]
    for slug, p in places.items():
        var = p["var"]
        yc = C.foot_local(var, 0.0).centroid.y
        if var == "v4":
            k = P.kass_dims()
            ys = (k["seat0"] + k["seat1"]) / 2
            kas = BU.KA.kassette4()
            led = BU.m3d.Manifold.cube([BU.V.STRIP_W, BU.V.STRIP_L, BU.V.STRIP_T]).translate([-BU.V.STRIP_W / 2, ys - BU.V.STRIP_L / 2, k["top"]])
        else:
            kas, led = BU.V.kassette(var), BU.V.strip(var)
        out.append(("kassette_" + slug, "cassette", "Kassette " + var, to_tm(BU.place(kas.translate([0, 0, -F]), p, yc))))
        out.append(("led_" + slug, "led", "LED-Streifen", to_tm(BU.place(led.translate([0, 0, -F]), p, yc))))

    # Display-Gebäude, zweiter Satz, auf seinem Dock am Ostrand
    with contextlib.redirect_stdout(io.StringIO()):
        dp, _ = B.parts()
    s2 = CD.satz(2)
    for key, grp in (("body", "display"), ("lid", "display"), ("blende", "display_front"), ("pcb", "pcb"), ("glass", "glass")):
        out.append(("display_" + key, grp, "Display-Gebäude", to_tm(CD.pose(dp[key], s2, minx, miny, 0.0))))

    # Unterkasten Stand 8 (Plattenkoordinaten, Oberkante = Plattenunterseite) mit Powerbank, ESP32 und Hauptschalter an den Lagen aus kasten8
    with contextlib.redirect_stdout(io.StringIO()):
        K8.modus(PP.GANG_FASE_MODUS)
        k = K8.build(K8.stand7())
    z0 = -T - k["H"]
    uk = trimesh.load(os.path.join(ROOT, "stl", "steckmodul_unterkasten8", "U8_unterkasten.stl"))
    out.append(("unterkasten", "case", "Unterkasten", uk.apply_translation([minx, miny, z0])))
    # Powerbank liegt auf dem Plateau über dem Knopf des Huts, der ESP32 auf einem Gangdach; Boxen aus den Prüfkörpern von kasten8
    pb = k["pb_m"].to_mesh()
    pb_b = np.asarray(pb.vert_properties)[:, :3]
    (px0, py0, pz0), (px1, py1, pz1) = pb_b.min(0), pb_b.max(0)
    out.append(("powerbank", "powerbank", "Powerbank", box(minx + px0, miny + py0, z0 + pz0, minx + px1, miny + py1, z0 + pz1)))
    ex, ey = (np.asarray(k["elec"].bounds).reshape(2, 2).mean(0))
    bw, bl = PP.ESP_BOARD
    ew = np.asarray(k["elec"].bounds)
    if (ew[2] - ew[0]) < (ew[3] - ew[1]):
        bw, bl = bl, bw
    zf = z0 + k["esp_z0"]
    out.append(("esp32", "pcb", "ESP32", box(minx + ex - bw / 2, miny + ey - bl / 2, zf + 1.0, minx + ex + bw / 2, miny + ey + bl / 2, zf + 2.6)))
    out.append(("esp32_chip", "chip", "ESP32", box(minx + ex - 9, miny + ey - 8, zf + 2.6, minx + ex + 9, miny + ey + 9, zf + 5.6)))
    sy, sz = PP.SW_Y, z0 + k["sw"]["z"]
    out.append(("schalter", "switch", "Hauptschalter", box(minx - 1.6, miny + sy - 7.5, sz - 5.0, minx + PP.UK_WALL + 8.0, miny + sy + 7.5, sz + 5.0)))
    return out


def write_model(items):
    allv = np.vstack([m.vertices for *_, m in items])
    lo, hi = allv.min(0), allv.max(0)
    span = hi - lo
    blob, index = bytearray(), []
    for name, grp, title, m in items:
        q = np.round((np.asarray(m.vertices) - lo) / span * 65535).astype("<u2")
        f = np.asarray(m.faces)
        ft = "<u2" if len(m.vertices) < 65536 else "<u4"
        while len(blob) % 4:
            blob += b"\0"
        vo = len(blob)
        blob += q.tobytes()
        while len(blob) % 4:
            blob += b"\0"
        fo = len(blob)
        blob += f.astype(ft).tobytes()
        b = m.bounds
        index.append(dict(name=name, group=grp, title=title, v=[vo, len(m.vertices)], f=[fo, len(f), 2 if ft == "<u2" else 4],
                          box=[round(float(x), 2) for x in list(b[0]) + list(b[1])]))
    json.dump(dict(lo=lo.round(4).tolist(), span=span.round(4).tolist(), parts=index, bin=base64.b64encode(bytes(blob)).decode()),
              open(os.path.join(OUT, "model.json"), "w"), ensure_ascii=False)
    tris = sum(p["f"][1] for p in index)
    print("model.json: %.2f MB Netze, %d Teile, %d Dreiecke, Box %s mm" % (len(blob) / 1e6, len(index), tris, " × ".join("%.1f" % x for x in span)))


def write_images():
    for dst, (src, w) in IMAGES.items():
        im = Image.open(os.path.join(ROOT, src))
        if im.width > w:
            im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        im.save(os.path.join(OUT, dst), "WEBP", quality=86, method=6)
        print("%-24s %4d × %-4d %4.0f KB" % (dst, im.width, im.height, os.path.getsize(os.path.join(OUT, dst)) / 1024))


def main():
    os.makedirs(OUT, exist_ok=True)
    write_model(parts())
    write_images()


if __name__ == "__main__":
    main()
