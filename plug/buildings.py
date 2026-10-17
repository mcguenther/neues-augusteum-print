#!/usr/bin/env python3
"""Gebäude für die Steckplatte (Laserscan, 1:1300): Hohlkörper mit Fuß und Aufnahme für die Kassette, druckbar ohne Stützen im Gebäude.

Aufbau je Gebäude (z = 0 ist die Plattenoberseite, das Gebäude reicht bis zur Fußunterkante z = -F = -14,2 mm hinunter):
  * Fuß: der volle Grundriss (derselbe wie die Mulde der Steckplatte, `plug/campus.py`) von -F bis 0, Bettkante mit Fase EF_CH_T.
  * Hohlkörper: Gebäude und Fuß zusammen mit `hohl.py` ausgehöhlt (Wand 0,8, glattes 45°-Gewölbe, keine Taschen).
  * Boden BODEN_T über die ganze Grundfläche (liegt beim Druck auf dem Bett); er trägt das Schachtrohr und schließt den Hohlraum nach unten.
  * Schachtrohr: Schacht plus Wand (Wand aus `placements_1300.json`) vom Boden bis über den Unterbau der Kassette.
  * Schacht: Kassette mit Einpressspiel KASS_CLR_T, so tief wie der Unterbau plus SHAFT_EXTRA_T, Einführfase ENTRY_CH_T am Bett.
    Oben ein Anschlagrand, dessen Unterseite in 45° nach innen läuft (kein waagerechter Überhang); darüber die Öffnung für alles, was über
    dem Unterbau liegt (LED-Streifen, Blatt, Rücken-Streifen), mit Spiel FREI_T.
  * Platz für die Kassette: Was über dem Anschlag liegt, bekommt im Hohlraum einen freien Raum (Öffnung bis zur Kassettenoberkante + FREI_T,
    darüber ein 45°-Walm), begrenzt auf den Ziel-Hohlraum ohne Gewölbe (Wand und Dach bleiben).
  * 45°-Dach (`dach45`): alle Schnitte über dem Anschlag werden von oben nach unten so beschnitten, dass keine flache Decke entsteht (wo das
    niedrige Gebäudedach den Walm kappt); nur der Raum, den die Kassette wirklich braucht, bleibt unangetastet.
  * Gewölbe streng (BRUECKE_T 2 statt 10 wie in `generate.py`): fast jede Decke im Hohlraum wird 45°-Gewölbe, damit im Gebäude keine
    Brücken unter dem Dach bleiben.
  * Das Schachtrohr trägt das Gewölbe mit (STUETZE_ROHR, `hohl.ceiling(stuetzen=…)`): Von der Rohroberkante steigen ebenfalls 45°-Kegel
    auf, jeder Raum wird von Wand und Rohr aus überwölbt und das Gewölbe setzt höher an (Neues Augusteum 23,7 statt 36,1 cm³,
    Hörsaalgebäude 43,2 statt 56,3 cm³).
  * Spalten im Hohlraum unter FUELLEN_T (2 mm) werden Material (`hohl.spalten`): ein voller Streifen druckt mit Füllung statt mit zwei
    Wänden und Spalt.
  * `--umkreis 2`: Kegel nur im eigenen Bereich (weniger Material, aber senkrechte Stufen in der Decke); Standard ist die glatte Decke.

Prüfungen (je Gebäude): dicht; Kollision der Kassette (mit Streifen) mit dem Gebäude; Überhang: das fertige Gebäude in Lagen von 0,2 mm
geschnitten, Material jeder Lage, das weiter als UEBERHANG_T vom Material der Lage darunter liegt (über Luft, flacher als 45°), getrennt nach
Brücken (ringsum Material derselben Lage, Spannweite etwa 2 × Reichweite) und Kragstücken (freie Kante; Reichweite = Auskragung). Lagen und Kassetten: `plug/scale1176/placements_1300.json`, `plug/testcase/params.py` (CASSETTE).

Aufruf (aus dem Repo-Wurzelverzeichnis, 1 bis 2 min je Gebäude):
    python3 -m plug.buildings                       # alle; STL und JSON nach stl/steckmodul_campus/gebaeude/, Schnittbilder nach vorschau/…/gebaeude/
    python3 -m plug.buildings 02_neues_augusteum --bruecke 10   # ein Gebäude, Gewölbe wie im Generator
"""
import argparse
import json
import os
import sys

import manifold3d as m3d
import numpy as np
import shapely
from shapely.geometry import Polygon, box as sbox
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import generate as G  # noqa: E402
import hohl  # noqa: E402
from plug import campus as C  # noqa: E402
from plug.geom import to_tm  # noqa: E402
from plug.power import build_concept as BC  # noqa: E402
from plug.testcase import kassette as KA  # noqa: E402
from plug.testcase import params as P  # noqa: E402
from plug.testcase import variants as V  # noqa: E402

OUT = os.path.join(HERE, "stl", "steckmodul_campus", "gebaeude")
PREV = os.path.join(HERE, "vorschau", "steckmodul_campus", "gebaeude")
BODEN_T = 1.2          # Boden des Gebäudes (3 Wände, liegt auf dem Bett)
FREI_T = 0.3           # Spiel um alles, was über dem Unterbau der Kassette liegt
ANSCHLAG_T = 1.2       # Mindestbreite des Anschlagrands (wie LIP_X/E_LIP der Steckprobe 1)
ROHR_T = 1.2           # Wand des Schachtrohrs (höchstens; im Paulinum lässt die Lage nur weniger zu, dann die Wand aus der Platzierung)
BRUECKE_T = 2.0        # größte freie Spannweite einer Decke ohne Gewölbe (hohl.BRUECKE ist 10); 2 = fast überall Gewölbe, keine Decken über Luft
STUETZE_ROHR = True    # Schachtrohr trägt das Gewölbe mit
UMKREIS_T = None       # Kegel nur im eigenen Bereich (hohl.ceiling umkreis); None = überall
FUELLEN_T = 2.0        # Spalten im Hohlraum, die schmaler sind, werden gefüllt (hohl.spalten)
LAYER = 0.2            # Schichthöhe für die Überhangprüfung
UEBERHANG_T = 0.25     # Überhang je 0,2-mm-Schicht, der als getragen gilt (gut 45°)


def ext(poly, z0, z1):
    return G.extrude(poly, z0, z1)


# --------------------------------------------------------------------------
# Kassette im Kassettensystem (x Mitte, y = 0 an der Taschenseite, z = 0 Unterkante)
# --------------------------------------------------------------------------
def unterbau_top(var):
    """Oberkante des Unterbaus (bis dorthin geht der Schacht mit Einpressspiel)."""
    return P.kass_dims()["top"] if var == "v4" else V.dims(var)["z_b"]


def kassette_mit_streifen(var):
    """Kassette samt LED-Streifen (und Blatt) als Manifold im Kassettensystem."""
    if var == "v4":
        k = P.kass_dims()
        yc = (k["seat0"] + k["seat1"]) / 2
        led = m3d.Manifold.cube([V.STRIP_W, V.STRIP_L, V.STRIP_T]).translate([-V.STRIP_W / 2, yc - V.STRIP_L / 2, k["top"]])
        return KA.kassette4() + led
    return V.kassette(var) + V.strip(var)


def oeffnung(var, kas):
    """Grundriss (shapely, Kassettensystem) von allem, was über dem Unterbau liegt, mit Spiel FREI_T."""
    zt = unterbau_top(var)
    top = kas.trim_by_plane([0, 0, 1], zt + 0.05)
    if top.is_empty():
        return Polygon()
    cs = top.project()
    g = unary_union([Polygon(r).buffer(0) for r in cs.to_polygons() if len(r) >= 3])
    return g.buffer(FREI_T, join_style=2)


def schacht_rechteck(var):
    """Schacht (Kassette plus Einpressspiel) im Kassettensystem."""
    w, dep = C.shaft_size(var)
    return sbox(-w / 2, -P.KASS_CLR_T, w / 2, dep - P.KASS_CLR_T)


# --------------------------------------------------------------------------
# Gebäude
# --------------------------------------------------------------------------
def place(m, p, yc):
    """Kassettensystem -> Gebäudesystem (Pin-Reihe y = 0) -> Weltlage der Platzierung."""
    return m.translate([0.0, P.dims_plan()["y_kass0"] - yc, 0.0]).rotate([0.0, 0.0, p["angle"]]).translate([p["cx"], p["cy"], 0.0])


def schacht_teile(var, wall, F):
    """(Rohr, Schnittkörper, Platzkörper, Höhe der Rohroberkante) im Kassettensystem, z = 0 ist die Fußunterkante -F."""
    kas = kassette_mit_streifen(var)
    rect = schacht_rechteck(var)
    win = need = oeffnung(var, kas)
    zs = unterbau_top(var) + P.SHAFT_EXTRA_T                      # Schachtdecke (Anschlag) über der Fußunterkante
    # Anschlag: oberhalb zs wird der Schacht in 45° (Schichten von 0,1 mm) eingezogen, bis nur die Öffnung bleibt
    win = win.union(rect.buffer(-ANSCHLAG_T, join_style=2)) if not rect.buffer(-ANSCHLAG_T, join_style=2).is_empty else win
    depth = 0.0
    while not rect.buffer(-depth, join_style=2).difference(win).buffer(-1e-3).is_empty and depth < 6.0:
        depth += 0.1
    parts = [ext(rect, -0.01, zs)]
    t = 0.0
    while t < depth - 1e-9:
        g = rect.buffer(-(t + 0.05), join_style=2).union(win)
        parts.append(ext(g, zs + t - 0.005, zs + t + 0.1 + 0.005))
        t += 0.1
    z_rohr = zs + depth + 0.4                                       # Rohr endet 0,4 mm über dem Anschlag (zwei Schichten Deckel des Rands)
    parts.append(ext(win, zs - 0.01, z_rohr + 0.5))
    parts.append(BC.mouth_ch(rect, 0.0, P.ENTRY_CH_T))              # Einführfase am Bett
    cut = G.union(parts)
    rohr = ext(rect.buffer(wall, join_style=2), 0.0, z_rohr)
    zk = float(kas.bounding_box()[5]) + FREI_T
    # Freier Raum für Blatt und Streifen über dem Anschlag; oben als 45°-Walm (schrumpft je 0,1 mm Höhe um 0,1 mm), damit dort, wo er in
    # Gewölbematerial schneidet, keine flache Decke entsteht
    bedarf = ext(need, zs - 0.01, zk)                               # was die Kassette über dem Anschlag mindestens braucht
    platz = [ext(win, zs - 0.01, zk)]
    t = 0.0
    while True:
        g = win.buffer(-(t + 0.05), join_style=2)
        if g.is_empty or g.area < 0.05:
            break
        platz.append(ext(g, zk + t - 0.005, zk + t + 0.1 + 0.005))
        t += 0.1
    platz = G.union(platz)
    return rohr, cut, platz, bedarf, kas, zs, z_rohr


def dach45(X, frei, schutz, z0, dz=0.1):
    """Schnittkörper X oberhalb z0 so beschneiden, dass er keine flache Decke bekommt: von oben nach unten darf der Hohlraum je Lage dz
    nur um dz über den Hohlraum der Lage darüber (X selbst und der übrige Hohlraum `frei`) hinausgehen (45°); schmale Grate (unter 2·dz)
    bleiben als Spitze. Was die Kassette braucht (`schutz`), bleibt immer frei. Liefert den beschnittenen Körper (ab z0)."""
    z1 = float(X.bounding_box()[5])
    above, slabs = Polygon(), []
    z = z1 - dz / 2
    while z > z0:
        x = hohl._cs_poly(X.slice(z))
        if x.is_empty:
            above = hohl._cs_poly(frei.slice(z))
            z -= dz
            continue
        allow = above.buffer(dz, quad_segs=4)
        thin = x.difference(x.buffer(-0.75 * dz, join_style=2).buffer(0.75 * dz, join_style=2))
        xn = x.intersection(allow.union(thin)).union(x.intersection(hohl._cs_poly(schutz.slice(z))))
        xn = xn.buffer(0)
        if not xn.is_empty:
            slabs.append(ext(xn, max(z - dz / 2, z0) - 0.005, z + dz / 2 + 0.005))
        above = xn.union(hohl._cs_poly(frei.slice(z)))
        z -= dz
    return G.union(slabs) if slabs else m3d.Manifold()


def gebaeude(slug, solid, fp, p, s, rohrstuetze=None):
    """Steckbares Hohlgebäude (Manifold, Weltlage, z = 0 Plattenoberseite) und Prüfwerte. rohrstuetze: Rohr trägt das Gewölbe mit
    (Standard STUETZE_ROHR)."""
    rohrstuetze = STUETZE_ROHR if rohrstuetze is None else rohrstuetze
    d = P.dims_plan()
    F = d["F"]
    var = p["var"]
    yc = C.foot_local(var, 0.0).centroid.y
    fuss = BC.slab_ch(fp, -F, 0.02, P.EF_CH_T)                      # Fuß mit Fase an der Bettkante
    voll = solid + fuss
    rohr, cut, platz, bedarf, kas, zs, z_rohr = schacht_teile(var, min(ROHR_T, p["wall"]), F)
    T = lambda m: place(m.translate([0, 0, -F]), p, yc)
    rohr, cut, platz, bedarf, kas = T(rohr), T(cut), T(platz), T(bedarf), T(kas)
    zs -= F
    # Hohlraum: hohl.py rechnet mit Boden bei z = 0, also um F nach oben schieben und zurück. Das Schachtrohr wird vom Bett an gedruckt
    # und trägt das Gewölbe mit (Stütze bis zur Rohroberkante): die Räume werden von Wand und Rohr aus überwölbt.
    rohr_fp = hohl._cs_poly(rohr.slice(-F + 0.5))
    stuetzen = [(rohr_fp, z_rohr)] if rohrstuetze else None
    cav, lay0 = hohl.hohlraum(voll.translate([0, 0, F]), bruecke=BRUECKE_T, stuetzen=stuetzen, fuellen=FUELLEN_T,
                              umkreis=UMKREIS_T)
    cav = cav.translate([0, 0, -F])
    if rohrstuetze:
        # Über dem Rohr kein Gewölbe-Hohlraum: das Rohr setzt sich nach oben als Säule fort, frei bleibt dort nur der Raum über der
        # Kassette (Platz mit 45°-Walm, unten). Sonst griffe das Gewölbe eines Nachbarraums über den Rohrkopf, wo das Rohr nicht trägt,
        # und zwischen ihm und dem Walm bliebe eine nach unten hängende Kante.
        # Die Säule reicht bis 0,4 mm über die Walmspitze; darüber darf das Gewölbe wieder über das Rohr greifen (hohe Gebäude).
        zt = float(platz.bounding_box()[5]) + 0.4
        cav = cav - ext(rohr_fp, -F - 1.0, zt)
        # Wo über der Säule bis zum Gewölbe weniger als FUELLEN_T Luft bliebe, wird auch das Material (keine flachen Taschen)
        flach = rohr_fp.intersection(hohl._cs_poly(cav.slice(zt + 0.1))).difference(hohl._cs_poly(cav.slice(zt + max(FUELLEN_T, 0.4))))
        if flach.area > 0.05:
            cav = cav - ext(flach.buffer(0.02, join_style=2), zt - 0.01, zt + max(FUELLEN_T, 0.4) + 0.01)
    ziel = hohl.cavity(lay0).translate([0, 0, -F])                  # Ziel-Hohlraum ohne Gewölbe (Wand und Dach 0,8)
    boden = ext(fp, -F - 0.01, -F + BODEN_T)
    body = (voll - cav) + (boden ^ voll) + (rohr ^ voll)
    # unterhalb des Anschlags der Schacht wie er ist; darüber Platz und Fenster mit 45°-Dach (keine flache Decke unter dem Gebäudedach)
    body = body - cut.trim_by_plane([0, 0, -1], -zs)
    oben = ((platz ^ ziel) + cut).trim_by_plane([0, 0, 1], zs - 0.02)
    body = body - dach45(oben, cav - rohr, bedarf, zs - 0.02)
    body = body.simplify(hohl.VEREINFACHEN)
    info = dict(slug=slug, var=var, wall=p["wall"], F=F, rohrstuetze=rohrstuetze)
    kol = (body ^ kas).volume()
    info["kollision_mm3"] = round(kol, 3)
    info["platz_fehlt_mm3"] = round((bedarf - ziel).volume(), 2)    # Platz für die Kassette, den der Ziel-Hohlraum nicht hergibt
    info["volumen_cm3"] = round(body.volume() / 1000, 2)
    return body, kas, info


def ueberhang(body, step=LAYER, tol=UEBERHANG_T):
    """Lagenweise Prüfung: Material, das weiter als tol vom Material der Lage darunter liegt (flacher als gut 45°). Jede solche Stelle ist
    entweder eine Brücke (ringsum von Material derselben Lage umgeben, deckt einen geschlossenen Raum ab; Spannweite etwa 2 × Reichweite)
    oder ein Kragstück (hat eine freie Kante, bräuchte Support; Reichweite = Auskragung). Liefert Flächen, größte Reichweiten und die Stellen."""
    zmin, zmax = body.bounding_box()[2], body.bounding_box()[5]
    prev, res = None, dict(bruecke_mm2=0.0, bruecke_mm=0.0, krag_mm2=0.0, krag_mm=0.0, stellen=[])
    z = zmin + step / 2
    while z < zmax:
        m = hohl._cs_poly(body.slice(z))
        if prev is not None and not m.is_empty:
            u = m.difference(prev.buffer(tol, quad_segs=4))
            u = u.buffer(-0.05).buffer(0.05) if not u.is_empty else u
            rand = m.boundary.buffer(0.03)
            for g in getattr(u, "geoms", [u]):
                if g.is_empty or g.area < 0.2:
                    continue
                lo, hi = tol, 40.0
                for _ in range(8):
                    mid = (lo + hi) / 2
                    if g.difference(prev.buffer(mid, quad_segs=4)).buffer(-0.05).is_empty:
                        hi = mid
                    else:
                        lo = mid
                krag = g.boundary.intersection(rand).length > 0.5
                art = "krag" if krag else "bruecke"
                res[art + "_mm2"] += g.area
                res[art + "_mm"] = max(res[art + "_mm"], lo)
                if lo > 1.0:
                    c = g.representative_point()
                    res["stellen"].append((art, round(z, 1), round(g.area, 1), round(lo, 1), round(c.x, 1), round(c.y, 1)))
        prev = m
        z += step
    for k in ("bruecke_mm2", "bruecke_mm", "krag_mm2", "krag_mm"):
        res[k] = round(res[k], 2)
    return res


def build(scale=P.SCALE_PLAN, slugs=None):
    s = 1000.0 / scale
    models = G.source_models("laserscan", s)
    places = json.load(open(C.CACHE % scale))
    out = []
    for slug, p in places.items():
        if slugs and slug not in slugs:
            continue
        solid, fp, _ = models[slug]
        # Mit und ohne Rohrstütze bauen, das leichtere nehmen: Unter niedrigen Dächern (Neues Augusteum, Hörsaalgebäude) setzt das Gewölbe
        # mit der Rohrstütze viel höher an; in hohen, schmalen Gebäuden trägt das Rohr kaum und die Säule über ihm kostet nur.
        varianten = [gebaeude(slug, solid, fp, p, s, r) for r in ((True, False) if STUETZE_ROHR else (False,))]
        body, kas, info = min(varianten, key=lambda v: v[2]["volumen_cm3"])
        info["volumen_varianten_cm3"] = {("mit" if v[2]["rohrstuetze"] else "ohne") + "_rohrstuetze": v[2]["volumen_cm3"] for v in varianten}
        info["ueberhang"] = ueberhang(body)
        out.append((slug, body, kas, info))
        u = info["ueberhang"]
        print("  %-22s %-5s %6.2f cm³ (%s)  Kollision %.3f mm³  Platz fehlt %.2f mm³  Brücken %.0f mm² (Spannweite bis %.1f mm)  "
              "Kragstücke %.1f mm² (bis %.1f mm)" % (slug, info["var"], info["volumen_cm3"],
                                                    " / ".join("%s %.2f" % kv for kv in info["volumen_varianten_cm3"].items()), info["kollision_mm3"], info["platz_fehlt_mm3"],
                                                    u["bruecke_mm2"], 2 * u["bruecke_mm"], u["krag_mm2"], u["krag_mm"]), flush=True)
        for st in sorted(u["stellen"], key=lambda t: (t[0] != "krag", -t[3]))[:6]:
            print("      %-7s z=%5.1f  %5.1f mm²  Reichweite %.1f mm  bei (%.1f, %.1f)" % st)
    return out


def main():
    global BRUECKE_T, STUETZE_ROHR, FUELLEN_T, UMKREIS_T, OUT, PREV
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scale", type=int, default=P.SCALE_PLAN)
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--bruecke", type=float, default=BRUECKE_T, help="größte freie Spannweite einer Decke ohne Gewölbe (mm)")
    ap.add_argument("--ohne-rohrstuetze", action="store_true", help="Gewölbe nur von den Außenwänden (Stand vor 2026-10-17)")
    ap.add_argument("--fuellen", type=float, default=FUELLEN_T, help="Spalten schmaler als dies füllen (mm, 0 = aus)")
    ap.add_argument("--umkreis", type=float, default=UMKREIS_T, help="Kegel einer Stütze nur bis so viel weiter als die nächste Stütze (mm)")
    ap.add_argument("--out", help="Ausgabeordner für STL und Bilder (Standard: die eingecheckten Ordner)")
    a = ap.parse_args()
    BRUECKE_T = a.bruecke
    STUETZE_ROHR = not a.ohne_rohrstuetze
    FUELLEN_T = a.fuellen
    UMKREIS_T = a.umkreis
    if a.out:
        OUT = PREV = a.out
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(PREV, exist_ok=True)
    res = build(a.scale, a.slugs)
    ok = True
    for slug, body, kas, info in res:
        tm = to_tm(body)
        c = tm.bounds
        path = os.path.join(OUT, "%s_1zu%d.stl" % (slug, a.scale))
        tm.export(path)
        info["dicht"] = bool(tm.is_watertight)
        info["mass_mm"] = [round(float(x), 1) for x in tm.extents]
        print("  %-60s %5.1f × %5.1f × %5.1f mm  dicht=%s" % (os.path.relpath(path, HERE), *tm.extents, tm.is_watertight))
        ok &= info["dicht"] and info["kollision_mm3"] < 0.5 and info["platz_fehlt_mm3"] < 1.0
        json.dump(info, open(os.path.join(OUT, "%s_1zu%d.json" % (slug, a.scale)), "w"), indent=1)
        p = json.load(open(C.CACHE % a.scale))[slug]
        schnittbild(body, kas, p, "%s · Kassette %s · Fuß %.1f mm" % (slug, info["var"], info["F"]), os.path.join(PREV, "%s_schnitt.png" % slug))
    print("alle dicht, keine Kollisionen" if ok else "ACHTUNG: nicht dicht, Kollision oder zu wenig Platz für die Kassette")



def schnittbild(body, kas, p, title, path):
    """Zwei Schnitte durch die Kassettenmitte (quer und längs zur Kassette) als Bild: Material dunkel, Kassette rot, Plattenoberseite gestrichelt."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from shapely.geometry import Polygon
    a = np.radians(p["angle"])
    ex, ey = np.array([np.cos(a), np.sin(a), 0.0]), np.array([-np.sin(a), np.cos(a), 0.0])
    ez = np.array([0.0, 0.0, 1.0])
    kb = kas.bounding_box()
    c = np.array([(kb[0] + kb[3]) / 2, (kb[1] + kb[4]) / 2, 0.0])
    fig, axs = plt.subplots(1, 2, figsize=(13, 6.2))
    for ax, (n, u, lab) in zip(axs, ((ey, ex, "quer zur Kassette"), (ex, ey, "längs zur Kassette"))):
        # Schnittebene auf z = 0 drehen: x' = u, y' = z, z' = ±n (rechtshändig), dann Manifold.slice
        if np.linalg.det(np.array([u, ez, n])) < 0:
            n = -n
        R = np.array([u, ez, n])
        T = np.column_stack([R, -R @ c])
        for m, col, z in ((body, "#3b4452", 1), (kas, "#d6453d", 2)):
            g = hohl._cs_poly(m.transform(T).slice(0.0))
            for poly in getattr(g, "geoms", [g]):
                if poly.is_empty or not isinstance(poly, Polygon):
                    continue
                for ring, colr in [(poly.exterior, col)] + [(r, "white") for r in poly.interiors]:
                    q = np.asarray(ring.coords)
                    ax.fill(q[:, 0], q[:, 1], color=colr, alpha=1.0 if (z == 1 or colr == "white") else 0.55, lw=0, zorder=z)
        ax.axhline(0.0, color="#888", ls="--", lw=0.8)
        ax.set_aspect("equal")
        ax.set_title(lab, fontsize=11)
        ax.set_xlabel("mm")
    fig.suptitle(title, fontsize=13)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


if __name__ == "__main__":
    main()
