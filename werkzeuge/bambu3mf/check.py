"""Prüft eine 3MF gegen die Lade-Logik von Bambu Studio v02.08.02.61 (ohne Bambu Studio).

    python3 werkzeuge/bambu3mf/check.py DATEI.3mf

Nachgebildet (Quellen: src/libslic3r/Model.cpp read_from_archive, src/libslic3r/Format/3mf.cpp
PrusaFileParser, src/libslic3r/Format/bbs_3mf.cpp _BBS_3MF_Importer, src/slic3r/GUI/Plater.cpp load_files,
src/libslic3r/PresetBundle.cpp validate_presets, src/libslic3r/TriangleSelector.cpp deserialize):

 1. PrusaFileParser: <metadata name="...Application...">…PrusaSlicer…</metadata> → From_Prusa, nur Geometrie.
 2. Application beginnt mit "BambuStudio-" → m_is_bbl_3mf, file_version; sonst dont_load_config = true.
 3. project_settings.config wird gelesen (JSON) → config_loaded nicht leer.
 4. Plater: !is_bbl_vendor_config && !check_project_config → Dialog „ungültige Konfiguration“.
    check_project_config (2.8.2.61): nozzle_diameter muss da sein; bei >1 Extruder gleich viele extruder_type.
 5. Versionsvergleich file_version / app_version (Newer3mfVersionDialog, „lower version“-Dialog).
 6. validate_presets: printer_settings_id, filament_settings_id müssen Systemprofile sein (sonst
    „customized presets“-Dialog), different_settings_to_system ohne G-Code-Schlüssel.
 7. Netz: Teile laut model_settings.config vorhanden, Dreiecke/Ecken gültig, paint_color dekodierbar und
    Filament <= Anzahl filament_colour; Längen der Filament-Listen stimmen.
"""
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

NS = {"m": "http://schemas.microsoft.com/3dmanufacturing/core/2015/02",
      "p": "http://schemas.microsoft.com/3dmanufacturing/production/2015/06"}
APP = (2, 8, 2, 61)
# printer_model der BBL-Druckerprofile (resources/profiles/BBL.json, Auszug)
BBL_MODELS = {"Bambu Lab A1", "Bambu Lab A1 mini", "Bambu Lab P1P", "Bambu Lab P1S", "Bambu Lab X1",
              "Bambu Lab X1 Carbon", "Bambu Lab X1E", "Bambu Lab H2D", "Bambu Lab P2S", "Bambu Lab H2S"}
GCODE_KEYS = {"machine_start_gcode", "machine_end_gcode", "before_layer_change_gcode", "layer_change_gcode",
              "change_filament_gcode", "filament_start_gcode", "filament_end_gcode", "time_lapse_gcode",
              "machine_pause_gcode", "template_custom_gcode", "printing_by_object_gcode", "wrapping_detection_gcode"}


def decode(code):
    code = code.upper()
    return {"4": 1, "8": 2}.get(code) or (int(code[0], 16) + 3 if len(code) == 2 and code[1] == "C" else None)


def main(path):
    ok, warn = [], []

    def need(cond, text):
        (ok if cond else warn).append(("OK    " if cond else "FEHLER ") + text)
        return cond

    z = zipfile.ZipFile(path)
    names = z.namelist()
    for n in names:
        if n.endswith((".model", ".rels", ".config", ".xml")) and n != "Metadata/project_settings.config":
            try:
                ET.fromstring(z.read(n))
            except ET.ParseError as e:
                need(False, "XML %s: %s" % (n, e))
    need(True, "alle XML-Teile wohlgeformt (sonst oben FEHLER)")
    for req in ("[Content_Types].xml", "_rels/.rels", "3D/3dmodel.model", "Metadata/model_settings.config",
                "Metadata/project_settings.config"):
        need(req in names, "Datei vorhanden: " + req)

    root = ET.fromstring(z.read("3D/3dmodel.model"))
    meta = {m.get("name"): (m.text or "") for m in root.findall("m:metadata", NS)}
    app = meta.get("Application", "")
    need("PrusaSlicer" not in app, "nicht als Prusa-3MF erkannt (PrusaFileParser)")
    need(app.startswith("BambuStudio-"), "Application = %r → m_is_bbl_3mf, Konfiguration wird gelesen" % app)
    fv = tuple(int(x) for x in app[12:].split(".")) if app.startswith("BambuStudio-") else (0, 0, 0, 0)
    need(meta.get("BambuStudio:3mfVersion") == "1", "BambuStudio:3mfVersion = 1")
    need(fv[0] <= APP[0], "Hauptversion %d <= %d (sonst „lower version“-Dialog)" % (fv[0], APP[0]))
    newer = fv > APP and (fv[1] != APP[1] or fv[2] // 100 != APP[2] // 100)
    need(not newer, "kein Newer3mfVersionDialog (Datei %s, App %s)" % (".".join(map(str, fv)), ".".join(map(str, APP))))

    # bbs_3mf.cpp: ohne Application "BambuStudio-…" ist dont_load_config = true → config_loaded leer
    cfg = json.loads(z.read("Metadata/project_settings.config")) if (
        "Metadata/project_settings.config" in names and app.startswith("BambuStudio-")) else {}
    need(bool(cfg), "project_settings.config gelesen und nicht leer")
    if not cfg:
        need(False, "2.8.2.61: check_project_config({}) = false und kein printer_model → modaler Dialog "
                    "„ungültige Konfiguration, nur Geometrie“, load_config = false")
        for line in ok + warn:
            print(line)
        return 1
    is_bbl_vendor = cfg.get("printer_model") in BBL_MODELS
    nd = cfg.get("nozzle_diameter")
    check_pc = isinstance(nd, list) and (len(nd) <= 1 or len(cfg.get("extruder_type", [])) == len(nd))
    need(is_bbl_vendor or check_pc, "kein Dialog „ungültige Konfiguration“ (printer_model=%r, nozzle_diameter=%r)"
         % (cfg.get("printer_model"), nd))
    need(check_pc, "check_project_config allein wäre auch true")

    n = len(cfg["filament_colour"])
    need(all(re.fullmatch(r"#[0-9A-F]{6}", c) for c in cfg["filament_colour"]), "filament_colour %s" % cfg["filament_colour"])
    for k in ("filament_settings_id", "filament_diameter", "filament_type", "filament_ids", "filament_self_index",
              "filament_map", "filament_extruder_variant", "nozzle_temperature", "filament_multi_colour"):
        need(len(cfg.get(k, [])) == n, "%s hat %d Einträge (= Filamente)" % (k, len(cfg.get(k, []))))
    need(len(cfg["flush_volumes_matrix"]) == n * n * len(nd), "flush_volumes_matrix n*n")
    need(len(cfg["different_settings_to_system"]) == n + 2, "different_settings_to_system n+2")
    diffs = {k for s in cfg["different_settings_to_system"] for k in s.split(";") if k}
    need(not diffs & GCODE_KEYS, "keine geänderten G-Codes gegenüber System (kein „modified G-codes“-Dialog)")
    need(cfg.get("printer_settings_id", "").endswith("nozzle") and "@" not in cfg.get("printer_settings_id"),
         "Druckerprofil sieht nach Systemprofil aus: %r" % cfg.get("printer_settings_id"))
    need(all("@BBL" in f for f in cfg["filament_settings_id"]) and "@BBL" in cfg.get("print_settings_id", ""),
         "Filament-/Prozessprofile mit @BBL (Systemprofile): %s / %r" % (sorted(set(cfg["filament_settings_id"])),
                                                                         cfg.get("print_settings_id")))
    # filamentbezogene Listen: Länge 1 bei n > 1 wäre verdächtig (normalize füllt mit Standardwerten auf)
    short = [k for k, v in cfg.items() if k.startswith("filament_") and isinstance(v, list) and len(v) not in (n, 0)
             and not k.startswith("filament_dev")]
    need(not short, "alle filament_*-Listen haben n Einträge %s" % (short[:8] or ""))

    # Netz und Bemalung
    rels = ET.fromstring(z.read("3D/_rels/3dmodel.model.rels")) if "3D/_rels/3dmodel.model.rels" in names else None
    subs = [r.get("Target").lstrip("/") for r in rels] if rels is not None else []
    meshes = {}
    for part in ["3D/3dmodel.model"] + subs:
        need(part in names, "Teilmodell vorhanden: " + part)
        r = ET.fromstring(z.read(part))
        for o in r.findall("m:resources/m:object", NS):
            m = o.find("m:mesh", NS)
            if m is None:
                continue
            nv = len(m.find("m:vertices", NS))
            tris = list(m.find("m:triangles", NS))
            idx_ok = all(0 <= int(t.get(a)) < nv for t in tris for a in ("v1", "v2", "v3"))
            codes = [t.get("paint_color") for t in tris if t.get("paint_color")]
            fil = [decode(c) for c in codes]
            need(o.get("id") not in meshes, "Netz-ID %s eindeutig (m_shared_meshes)" % o.get("id"))
            meshes[o.get("id")] = len(tris)
            need(idx_ok, "%s Objekt %s: %d Dreiecke, Eckindizes gültig" % (part, o.get("id"), len(tris)))
            need(all(f is not None and 1 <= f <= n for f in fil),
                 "%s Objekt %s: %d bemalte Dreiecke, Filamente %s <= %d" % (part, o.get("id"), len(codes), sorted(set(fil)), n))
    comp_ok = True
    for o in root.findall("m:resources/m:object", NS):
        for c in o.findall("m:components/m:component", NS):
            comp_ok &= c.get("{%s}path" % NS["p"], "").lstrip("/") in subs and c.get("objectid") in meshes
    need(comp_ok, "alle Komponenten zeigen auf vorhandene Netze")
    ms = ET.fromstring(z.read("Metadata/model_settings.config"))
    build_ids = {i.get("objectid") for i in root.findall("m:build/m:item", NS)}
    for o in ms.findall("object"):
        need(o.get("id") in build_ids, "model_settings object %s steht im build" % o.get("id"))
        ext = [int(md.get("value")) for md in o.iter("metadata") if md.get("key") == "extruder"]
        need(all(1 <= e <= n for e in ext), "Extruder %s <= %d" % (ext, n))
        for p in o.findall("part"):
            fc = int(p.find("mesh_stat").get("face_count"))
            need(meshes.get(p.get("id")) == fc, "part %s: face_count %d passt" % (p.get("id"), fc))
    plate = ms.find("plate")
    need(plate is not None and len(plate.findall("model_instance")) == len(build_ids), "Platte 1 enthält alle Objekte")
    for md in plate.findall("metadata"):
        if md.get("key", "").endswith("_file"):
            need(md.get("value") in names, "Bild der Platte vorhanden: %s" % md.get("value"))

    for line in ok + warn:
        print(line)
    print("\n%d Prüfungen, %d Fehler" % (len(ok) + len(warn), len(warn)))
    return 1 if warn else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
