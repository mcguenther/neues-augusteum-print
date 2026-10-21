"""3MF als Bambu-Studio-Projekt schreiben (Farben bleiben als Filamente erhalten).

Hintergrund (Quellen von Bambu Studio v02.08.02.61, src/slic3r/GUI/Plater.cpp, load_files):
Eine 3MF ohne Metadata/project_settings.config hat eine leere Konfiguration. In 2.8.2.61 liefert
check_project_config() dafür false (fehlendes nozzle_diameter), und weil auch kein printer_model
eines BBL-Druckers drinsteht, zeigt Bambu Studio den modalen Dialog „Die 3MF-Datei weist eine
ungültige Konfiguration auf, es werden nur Geometriedaten geladen“ und setzt load_config=false.
(Im master-Stand steht dort zusätzlich `if (config_loaded.empty()) return true;`.)
Deshalb schreibt dieses Skript ein vollständiges Bambu-Projekt:

- 3D/3dmodel.model mit `Application = BambuStudio-02.08.02.61` und `BambuStudio:3mfVersion = 1`
  (sonst liest bbs_3mf.cpp project_settings.config gar nicht erst: dont_load_config = true),
  je Objekt eine Komponente auf 3D/Objects/object_N.model (Aufbau wie Bambu Studio selbst).
- Netz in 3D/Objects/object_N.model; Dreiecke mit anderem Filament als dem Objekt-Filament tragen
  `paint_color` (Filament 1 = "4", 2 = "8", ab 3 = "%XC" % (n-3), TriangleSelector::deserialize).
- Metadata/project_settings.config aus template_a1.json (Bambu Lab A1 0.4, Systemprofile, also
  keine Warnung „customized presets“ / „modified G-codes“), auf die Zahl der Filamente erweitert,
  mit filament_colour = gewünschte Farben.
- Metadata/model_settings.config mit object/part/plate/assemble, Metadata/slice_info.config,
  Vorschaubilder Metadata/plate_1.png und plate_1_small.png (eigener Renderer, falls verfügbar).

Aufruf:
    python3 werkzeuge/bambu3mf/convert.py EIN.3mf AUS.3mf [--farbe "#E6D6BC" --farbe "#4F9A3C"]
            [--name "Bambu-Filamentname"] [--no-thumbnail]

Ohne --farbe gelten die Farben aus basematerials/displaycolor der Eingabe (bei generate.export_3mf
genau die Filamente), sonst Beige #E6D6BC und Grasgrün #4F9A3C.
EIN.3mf: eine 3MF aus generate.export_3mf (oder eine andere Kern-3MF mit Netzen in 3D/3dmodel.model):
Filament je Dreieck aus paint_color, sonst aus p1 (basematerials), sonst aus dem Objekt-Extruder.
"""
import argparse
import io
import json
import os
import re
import sys
import uuid
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter
from xml.sax.saxutils import escape as _esc

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
APP_VERSION = "02.08.02.61"
BED_CENTER = (128.0, 128.0)          # Bambu Lab A1: 256 x 256 mm
NS_CORE = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
NS_PROD = "http://schemas.microsoft.com/3dmanufacturing/production/2015/06"
NS_BAMBU = "http://schemas.bambulab.com/package/2021"
DEFAULT_COLOURS = ("#E6D6BC", "#4F9A3C")   # Beige, Grasgrün (farben.FILAMENTE)


def esc(t):
    return _esc(str(t), {'"': "&quot;"})


def paint_code(n):
    """Kodierung „ganzes Dreieck = Filament n“ (wie generate.paint_code)."""
    return {1: "4", 2: "8"}[n] if n < 3 else "%XC" % (n - 3)


def decode_paint(code):
    """Filament-Nummer eines ungeteilten Dreiecks aus paint_color, sonst None (geteilte Dreiecke)."""
    code = code.strip().upper()
    if code == "4":
        return 1
    if code == "8":
        return 2
    if len(code) == 2 and code[1] == "C":
        return int(code[0], 16) + 3
    return None


# ---------------------------------------------------------------- Einlesen

def read_3mf(path):
    """[(Name, Ecken (n,3), Dreiecke (m,3), Filament je Dreieck (m,), roher paint_color je Dreieck)]."""
    z = zipfile.ZipFile(path)
    root = ET.fromstring(z.read("3D/3dmodel.model"))
    ns = {"m": NS_CORE}
    extruder_of = {}
    if "Metadata/model_settings.config" in z.namelist():
        cfg = ET.fromstring(z.read("Metadata/model_settings.config"))
        for o in cfg.findall("object"):
            for md in o.findall("metadata"):
                if md.get("key") == "extruder":
                    extruder_of[o.get("id")] = int(md.get("value"))
    out = []
    for obj in root.findall("m:resources/m:object", ns):
        mesh = obj.find("m:mesh", ns)
        if mesh is None:
            raise SystemExit("Objekt %s ohne Netz (Komponenten werden nicht unterstützt)" % obj.get("id"))
        v = np.array([[float(e.get(a)) for a in "xyz"] for e in mesh.find("m:vertices", ns)], float)
        tris = mesh.find("m:triangles", ns)
        f = np.array([[int(e.get(a)) for a in ("v1", "v2", "v3")] for e in tris], np.int64)
        default = extruder_of.get(obj.get("id"))
        if default is None:
            default = int(obj.get("pindex", 0)) + 1 if obj.get("pid") else 1
        fil, raw = [], []
        for e in tris:
            pc = e.get("paint_color") or ""
            n = decode_paint(pc) if pc else None
            if n is None and e.get("p1") is not None and not pc:
                n = int(e.get("p1")) + 1
            fil.append(n if n is not None else default)
            raw.append(pc if pc and decode_paint(pc) is None else "")
        out.append((obj.get("name") or "Objekt %s" % obj.get("id"), v, f, np.array(fil, np.int64), raw))
    return out


def read_palette(path):
    """Filamentfarben aus basematerials/displaycolor (#RRGGBB, groß), leer, wenn keine da sind."""
    root = ET.fromstring(zipfile.ZipFile(path).read("3D/3dmodel.model"))
    return ["#" + b.get("displaycolor").lstrip("#")[:6].upper()
            for b in root.iter("{%s}base" % NS_CORE) if b.get("displaycolor")]


# ---------------------------------------------------------------- Projektkonfiguration

def project_settings(colours, filament_name=None):
    """project_settings.config (dict) für len(colours) Filamente aus template_a1.json."""
    t = json.load(open(os.path.join(HERE, "template_a1.json"), encoding="utf-8"))
    c = json.loads(json.dumps(t["config"]))
    n = len(colours)
    for k in t["pro_filament"]:
        v = c[k]
        assert isinstance(v, list) and len(v) == 1, k
        c[k] = v * n
    cols = [col.upper() for col in colours]
    c["filament_colour"] = cols
    c["filament_multi_colour"] = list(cols)
    c["filament_colour_type"] = ["1"] * n
    c["filament_self_index"] = [str(i + 1) for i in range(n)]
    c["default_filament_colour"] = [""] * n
    c["flush_volumes_matrix"] = ["0" if i == j else "280" for i in range(n) for j in range(n)]
    c["flush_volumes_vector"] = ["140"] * (2 * n)
    c["different_settings_to_system"] = [""] * (n + 2)
    c["inherits_group"] = [""] * (n + 2)
    if filament_name:
        c["filament_settings_id"] = [filament_name] * n
    return c


# ---------------------------------------------------------------- Schreiben

def _fmt(x):
    s = "%.6f" % x
    s = s.rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def thumbnail(objs, colours, size):
    """PNG (bytes) der Objekte in den Filamentfarben, oder None, wenn der Renderer fehlt."""
    try:
        sys.path.insert(0, ROOT)
        import trimesh
        import preview
    except Exception:
        return None
    pal = np.array([[int(c[i:i + 2], 16) / 255 for i in (1, 3, 5)] for c in colours])
    meshes = [(trimesh.Trimesh(v, f, process=False), pal[np.clip(fil, 1, len(pal)) - 1]) for _, v, f, fil, _ in objs]
    im = preview.render(meshes, size=(size, size), azim=-60, elev=35)
    buf = io.BytesIO()
    im.convert("RGB").save(buf, "PNG", optimize=True)
    return buf.getvalue()


def write_bambu_3mf(objs, path, colours=DEFAULT_COLOURS, filament_name=None, with_thumbnail=True, title=""):
    """objs: [(Name, Ecken, Dreiecke, Filament je Dreieck[, roher paint_color je Dreieck])].

    Die Lage der Objekte zueinander bleibt erhalten; das Ganze steht mittig auf der A1-Platte, Unterkante z = 0.
    """
    n_fil = len(colours)
    objs = [o if len(o) == 5 else (*o, [""] * len(o[2])) for o in objs]
    for name, v, f, fil, raw in objs:
        if fil.min() < 1 or fil.max() > n_fil:
            raise SystemExit("%s: Filament %d..%d, aber nur %d Farben angegeben" % (name, fil.min(), fil.max(), n_fil))
    allv = np.vstack([o[1] for o in objs])
    lo, hi = allv.min(0), allv.max(0)
    shift = np.array([BED_CENTER[0] - (lo[0] + hi[0]) / 2, BED_CENTER[1] - (lo[1] + hi[1]) / 2, -lo[2]])
    files = {}
    root_objects, items, rels, ms_objects, instances, assemble = [], [], [], [], [], []
    for k, (name, v, f, fil, raw) in enumerate(objs, start=1):
        mesh_id, root_id = 2 * k - 1, 2 * k
        c = (v.min(0) + v.max(0)) / 2
        local = v - c
        t = c + shift
        ext = int(Counter(fil.tolist()).most_common(1)[0][0])
        vx = "".join('<vertex x="%s" y="%s" z="%s"/>\n' % (_fmt(a), _fmt(b), _fmt(d)) for a, b, d in local)
        tr = []
        for (a, b, d), n, r in zip(f.tolist(), fil.tolist(), raw):
            code = r or (paint_code(n) if n != ext else "")
            tr.append('<triangle v1="%d" v2="%d" v3="%d"%s/>\n' % (a, b, d, ' paint_color="%s"' % code if code else ""))
        part = "3D/Objects/object_%d.model" % k
        files[part] = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<model unit="millimeter" xml:lang="en-US" xmlns="%s" xmlns:BambuStudio="%s" xmlns:p="%s" requiredextensions="p">\n'
            ' <metadata name="BambuStudio:3mfVersion">1</metadata>\n'
            ' <resources>\n'
            '  <object id="%d" p:UUID="%04x%04x-81cb-4c03-9d28-80fed5dfa1dc" type="model">\n'
            '   <mesh>\n<vertices>\n%s</vertices>\n<triangles>\n%s</triangles>\n   </mesh>\n'
            '  </object>\n </resources>\n</model>\n'
            % (NS_CORE, NS_BAMBU, NS_PROD, mesh_id, k, 0, vx, "".join(tr)))
        rels.append('<Relationship Target="/%s" Id="rel-%d" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>'
                    % (part, k))
        tf = "1 0 0 0 1 0 0 0 1 %s %s %s" % (_fmt(t[0]), _fmt(t[1]), _fmt(t[2]))
        root_objects.append(
            '  <object id="%d" p:UUID="%08x-61cb-4c03-9d28-80fed5dfa1dc" type="model">\n'
            '   <components>\n'
            '    <component p:path="/%s" objectid="%d" p:UUID="%04x0000-b206-40ff-9872-83e8017abed1" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>\n'
            '   </components>\n  </object>\n' % (root_id, k, part, mesh_id, k))
        items.append('  <item objectid="%d" p:UUID="%08x-b1ec-4553-aec9-835e5b724bb4" transform="%s" printable="1"/>\n'
                     % (root_id, root_id, tf))
        ms_objects.append(
            '  <object id="%d">\n'
            '    <metadata key="name" value="%s"/>\n'
            '    <metadata key="extruder" value="%d"/>\n'
            '    <metadata face_count="%d"/>\n'
            '    <part id="%d" subtype="normal_part">\n'
            '      <metadata key="name" value="%s"/>\n'
            '      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>\n'
            '      <metadata key="extruder" value="%d"/>\n'
            '      <mesh_stat face_count="%d" edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/>\n'
            '    </part>\n'
            '  </object>\n' % (root_id, esc(name), ext, len(f), mesh_id, esc(name), ext, len(f)))
        instances.append(
            '    <model_instance>\n'
            '      <metadata key="object_id" value="%d"/>\n'
            '      <metadata key="instance_id" value="0"/>\n'
            '      <metadata key="identify_id" value="%d"/>\n'
            '    </model_instance>\n' % (root_id, 100 + k))
        assemble.append('   <assemble_item object_id="%d" instance_id="0" transform="%s" offset="0 0 0" />\n' % (root_id, tf))

    thumbs = None
    if with_thumbnail:
        big = thumbnail(objs, colours, 512)
        small = thumbnail(objs, colours, 128) if big else None
        if big and small:
            thumbs = {"Metadata/plate_1.png": big, "Metadata/plate_1_small.png": small}

    from datetime import date
    today = date.today().isoformat()
    meta = [("Application", "BambuStudio-" + APP_VERSION), ("BambuStudio:3mfVersion", "1"), ("Copyright", ""),
            ("CreationDate", today), ("Description", ""), ("Designer", ""), ("DesignerCover", ""), ("DesignerUserId", ""),
            ("License", ""), ("ModificationDate", today), ("Origin", ""), ("ProfileCover", ""), ("ProfileDescription", ""),
            ("ProfileTitle", "")]
    if thumbs:
        meta += [("Thumbnail_Middle", "/Metadata/plate_1.png"), ("Thumbnail_Small", "/Metadata/plate_1_small.png")]
    meta += [("Title", title)]
    model = ('<?xml version="1.0" encoding="UTF-8"?>\n'
             '<model unit="millimeter" xml:lang="en-US" xmlns="%s" xmlns:BambuStudio="%s" xmlns:p="%s" requiredextensions="p">\n'
             % (NS_CORE, NS_BAMBU, NS_PROD)
             + "".join(' <metadata name="%s">%s</metadata>\n' % (k, esc(v)) for k, v in meta)
             + ' <resources>\n' + "".join(root_objects) + ' </resources>\n'
             + ' <build p:UUID="%s">\n' % uuid.uuid5(uuid.NAMESPACE_URL, os.path.basename(path))
             + "".join(items) + ' </build>\n</model>\n')

    plate_thumbs = ('    <metadata key="thumbnail_file" value="Metadata/plate_1.png"/>\n' if thumbs else "")
    model_settings = ('<?xml version="1.0" encoding="UTF-8"?>\n<config>\n' + "".join(ms_objects)
                      + '  <plate>\n'
                        '    <metadata key="plater_id" value="1"/>\n'
                        '    <metadata key="plater_name" value=""/>\n'
                        '    <metadata key="locked" value="false"/>\n'
                        '    <metadata key="filament_map_mode" value="Auto For Flush"/>\n'
                        '    <metadata key="filament_maps" value="%s"/>\n'
                        '    <metadata key="filament_volume_maps" value="%s"/>\n'
                      % (" ".join(["1"] * n_fil), " ".join(["0"] * n_fil))
                      + plate_thumbs + "".join(instances) + '  </plate>\n'
                      + '  <assemble>\n' + "".join(assemble) + '  </assemble>\n</config>\n')
    slice_info = ('<?xml version="1.0" encoding="UTF-8"?>\n<config>\n  <header>\n'
                  '    <header_item key="X-BBL-Client-Type" value="slicer"/>\n'
                  '    <header_item key="X-BBL-Client-Version" value="%s"/>\n  </header>\n</config>\n' % APP_VERSION)
    content_types = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                     '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n'
                     ' <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>\n'
                     ' <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>\n'
                     ' <Default Extension="png" ContentType="image/png"/>\n'
                     ' <Default Extension="gcode" ContentType="text/x.gcode"/>\n</Types>\n')
    top_rels = ['<Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>']
    if thumbs:
        top_rels += ['<Relationship Target="/Metadata/plate_1.png" Id="rel-2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/thumbnail"/>',
                     '<Relationship Target="/Metadata/plate_1.png" Id="rel-4" Type="http://schemas.bambulab.com/package/2021/cover-thumbnail-middle"/>',
                     '<Relationship Target="/Metadata/plate_1_small.png" Id="rel-5" Type="http://schemas.bambulab.com/package/2021/cover-thumbnail-small"/>']

    def rels_xml(lst):
        return ('<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n '
                + "\n ".join(lst) + '\n</Relationships>\n')

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels_xml(top_rels))
        z.writestr("3D/3dmodel.model", model)
        z.writestr("3D/_rels/3dmodel.model.rels", rels_xml(rels))
        for p, s in files.items():
            z.writestr(p, s)
        if thumbs:
            for p, b in thumbs.items():
                z.writestr(p, b)
        z.writestr("Metadata/project_settings.config",
                   json.dumps(project_settings(colours, filament_name), indent=4, ensure_ascii=False) + "\n")
        z.writestr("Metadata/model_settings.config", model_settings)
        z.writestr("Metadata/slice_info.config", slice_info)
    return path


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("ein")
    ap.add_argument("aus")
    ap.add_argument("--farbe", action="append",
                    help="Filamentfarbe #RRGGBB in Reihenfolge der Filamente (mehrfach); Standard: basematerials der Eingabe")
    ap.add_argument("--name", default=None, help="Bambu-Filamentprofil für alle Slots (Standard: Bambu PLA Basic @BBL A1)")
    ap.add_argument("--no-thumbnail", action="store_true")
    ap.add_argument("--titel", default="")
    a = ap.parse_args()
    colours = a.farbe or read_palette(a.ein) or list(DEFAULT_COLOURS)
    for c in colours:
        if not re.fullmatch(r"#[0-9A-Fa-f]{6}", c):
            raise SystemExit("Farbe %r ist nicht #RRGGBB" % c)
    objs = read_3mf(a.ein)
    write_bambu_3mf(objs, a.aus, colours, a.name, not a.no_thumbnail, a.titel)
    for name, v, f, fil, raw in objs:
        print("%s: %d Dreiecke, Filamente %s" % (name, len(f), dict(sorted(Counter(fil.tolist()).items()))))
    print("Filamente:", " ".join(colours))
    print("geschrieben:", a.aus)


if __name__ == "__main__":
    main()
