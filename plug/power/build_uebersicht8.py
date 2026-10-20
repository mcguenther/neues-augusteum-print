"""Übersichtsseite Batteriefach Stand 8 mit Steckplatte: beide Platten zusammen, 3D, Maße alt/neu, Prüfung, Druckhinweise.

Kurzfassung zu `plug/power/plan_kasten8.html` für den Druck: Kasten aus `build_unterkasten8.build()` (dieselbe Geometrie wie
`stl/steckmodul_unterkasten8/U8_unterkasten.stl`), Steckplatte `stl/steckmodul_campus/steckplatte_1zu1300.stl` aufgesetzt, dazu Gebäude,
Hof-Einsatz (an ihrer Lage auf der Platte, `plug.campus.SHIFTS`), Powerbank, Auflage-Klötze an den vorgeschlagenen Stellen, Doktorhut mit Knopf und Kordel.
Dazu die Passprobe der Gebäude in den Mulden (`plug.check_platte`). Netze für die Ansicht ausgedünnt (fast_simplification).

Aufruf: python3 -m plug.power.build_uebersicht8   (ca. 40 s)  ->  plug/power/uebersicht8.html   (Vorlage uebersicht8.template.html; Artifact)
"""
import json
import os

import trimesh

from plug import check_platte as CP
from plug.geom import encode, to_tm
from plug.power import build_concept as BC
from plug.power import build_unterkasten8 as U8
from plug.power import kasten8 as K8
from plug.power import params as PP
from plug.testcase import params as TP

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TEMPLATE = os.path.join(HERE, "uebersicht8.template.html")
OUT = os.path.join(HERE, "uebersicht8.html")
CAMPUS = os.path.join(ROOT, "stl", "steckmodul_campus")
PLATTE_VORHER = (115.58, 220.84)        # Steckplatte vor dem Auseinanderrücken (Commit 0009967), Mulden-Spiel 0,10


def thin(tm, faces):
    if len(tm.faces) <= faces:
        return tm
    try:
        return tm.simplify_quadric_decimation(face_count=faces)
    except Exception as e:                  # noqa: BLE001
        print("  (nicht ausgedünnt: %s)" % e)
        return tm


def enc(tm, dx=0.0, dy=0.0, dz=0.0, faces=None):
    tm = tm.copy()
    tm.apply_translation([dx, dy, dz])
    return encode(thin(tm, faces) if faces else tm)


def bounds(m):
    return [round(float(x), 2) for x in to_tm(m).bounds.flatten()]


def main():
    r, plate, bad, _ = U8.build()
    ok_geb, rows_geb, _, shifts = CP.pruefung()
    bad += not ok_geb
    H, pt = r["H"], BC.H0["plate_t"]
    raw = trimesh.load(U8.PLATE)
    sh = (-raw.bounds[0][0], -raw.bounds[0][1])
    meshes = dict(uk=enc(to_tm(r["uk"]), faces=90000), plate=enc(raw, *sh, H - raw.bounds[0][2], faces=60000),
                  hof=enc(trimesh.load(os.path.join(CAMPUS, "hof_einsatz_1zu1300.stl")), *sh, H + pt), buildings={})
    geb = os.path.join(CAMPUS, "gebaeude")
    for f in sorted(os.listdir(geb)):
        if f.endswith("_1zu1300.stl"):
            dx, dy = shifts.get(f[:-12], (0.0, 0.0))
            meshes["buildings"][f[:-12]] = enc(trimesh.load(os.path.join(geb, f)), sh[0] + dx, sh[1] + dy, H + pt, faces=9000)
    pd = r["plate_dims"]
    kb = r["uk"].bounding_box()
    data = dict(
        H=H, plate_t=pt, total=r["total"], h7=K8.H7, grams=r["grams"][0], zeit=r["zeit"], modus=r["modus"],
        W=round(kb[3] - kb[0], 2), L=round(kb[4] - kb[1], 2), Hz=round(kb[5] - kb[2], 2),
        pw=round(pd[3] - pd[0], 2), pl=round(pd[4] - pd[1], 2), ph=round(pd[5] - pd[2], 2), vorher=PLATTE_VORHER,
        spiel=dict(mulde=TP.OUTLINE_CLR_T, zuschnitt=TP.ZUSCHNITT_CLR_T, hof=TP.HOF_CLR_T),
        knopf=PP.HUT_KNOPF, kordel=PP.KORDEL, gang=PP.KORDEL_GANG, dach=PP.KORDEL_DACH, wand=PP.KORDEL_WAND, hut=PP.HUT,
        knopf_z=K8.KNOPF_Z, knopf_top=K8.KNOPF_TOP, raum_d=2 * K8.R_RAUM, raum_h=K8.H_RAUM, steckerraum=PP.STECKERRAUM_8,
        c=[round(r["K"]["c"][0], 2), round(r["K"]["c"][1], 2)], aus=r["K"]["aus"], z_pb=r["z_pb"], sw_z=r["sw"]["z"],
        pins=[row["neu"] for row in r["pin_rows"]], bruecken=[dict(n=n, w=w, z=z) for n, w, z in r["bruecken"]],
        pb_box=bounds(r["pb_m"]), plug_box=bounds(r["plug_m"]), esp_box=bounds(r["esp_m"]),
        checks=[dict(n=n, ok=bool(ok), t=t) for n, ok, t in r["checks"]], fit=[dict(t=t, ok=ok, v=v) for t, ok, v in r["fit"]],
        geb=[dict(n=n, ok=bool(ok), t=t) for n, ok, t in rows_geb], spalt_max=CP.SPALT_MAX,
        klotz=dict(a=U8.KLOTZ, h=round(r["z_pb"] - PP.UK_FLOOR, 2), floor=PP.UK_FLOOR,
                   lagen=[[round(a.centroid.x, 2), round(a.centroid.y, 2)] for a in r["auflagen"]]),
        bad=bad, meshes=meshes,
    )
    tpl = open(TEMPLATE, encoding="utf-8").read()
    html = tpl.replace("/*DATA*/", json.dumps(data, ensure_ascii=False, separators=(",", ":"), default=float))
    open(OUT, "w", encoding="utf-8").write(html)
    print("Übersicht Stand 8: Kasten %.2f × %.2f × %.1f, Platte %.2f × %.2f, Fehler %d" % (data["W"], data["L"], H, data["pw"], data["pl"], bad))
    print("geschrieben:", os.path.relpath(OUT, ROOT), "(%.1f MB)" % (len(html) / 1e6))


if __name__ == "__main__":
    main()
