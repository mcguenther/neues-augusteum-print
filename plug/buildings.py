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
  * `--spalt-min 0.4` (Standard aus): nachträglicher Schritt `plug/spalt.py`, Teile des fertigen Hohlraums schmaler als das Mindestmaß werden Material
    (Haarspalte an der Wand, Splitter am Gewölbe); Schacht und Platz für die Kassette bleiben frei.
  * `--umkreis 2`: Kegel nur im eigenen Bereich (weniger Material, aber senkrechte Stufen in der Decke); Standard ist die glatte Decke.
  * Optionen für möglichst viel offenen Raum (alle aus, der Standardbau bleibt Byte für Byte derselbe; `--offen` fasst sie zusammen):
    - `--aufsatz boden|oeffnung|rohr|alles` (`hohl.aufsatz`): zweites Gewölbe über der Rohrsäule. Das Rohr trägt Kegel nur von seiner
      niedrigen Oberkante, darüber blieb bis zum Dach Material stehen (Neues Augusteum: 12 bis 24 mm über der Kassette massiv). Der Aufsatz
      überwölbt diesen Raum von den Wänden und vom Dach des niedrigeren Nachbarn aus (Ansatz am Absatz, 45° bis zum First); `oeffnung`
      lässt den Walm über der Kassette weg, `rohr` auch die Säule über dem Rohr, `alles` auch die Keile daneben (bis unten offen).
    - `--saeulen D` (`hohl.ceiling saeulen`): dünne Pfeiler Ø 1,6 als zusätzliche Stützpunkte im Raum mit niedrigem Dach, bis kein Punkt
      weiter als D mm von Wand oder Stütze entfernt ist; die Kegel von dort verkürzen die Spannweiten, das Dach wird dünner.
    - `--fuellen 1.2` statt 2: der First wird nicht auf 2 mm Breite flach gekappt (Kragstücke am First, Material).
    - `--winkel W`: Neigung der Gewölbe (Standard 45, nur zur Untersuchung; Walm und `dach45` bleiben 45).
    - `--nur-rohr`: nur die Fassung mit Rohrstütze bauen (halbe Rechenzeit, für Probeläufe).

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
from plug import spalt as SP  # noqa: E402
from plug import campus as C  # noqa: E402
from plug.geom import to_tm  # noqa: E402
from plug.power import build_concept as BC  # noqa: E402
from plug.testcase import kassette as KA  # noqa: E402
from plug.testcase import params as P  # noqa: E402
from plug.testcase import variants as V  # noqa: E402

OUT = os.path.join(HERE, "stl", "steckmodul_campus", "gebaeude")
PREV = os.path.join(HERE, "vorschau", "steckmodul_campus", "gebaeude")
FUSS_FASE_T = 4.0      # Fase am Fuß an der Bettkante (Einführung in die Mulde; die Campus-Platte hat oben keine Muldenfase). r8: 2,0 mm fängt das Gebäude, kein Wulst; Passungsserie (19.10.2026, Probefuß B1): 4,0 beschlossen, die gedruckten Gebäude (Hörsaal, Seminar, Institut) haben 2,0. Wird nach dem Aushöhlen angebracht
BODEN_T = 1.2          # Boden des Gebäudes (3 Wände, liegt auf dem Bett)
FREI_T = 0.3           # Spiel um alles, was über dem Unterbau der Kassette liegt
ANSCHLAG_T = 1.2       # Mindestbreite des Anschlagrands (wie LIP_X/E_LIP der Steckprobe 1)
ROHR_T = 1.2           # Wand des Schachtrohrs (höchstens; im Paulinum lässt die Lage nur weniger zu, dann die Wand aus der Platzierung)
BRUECKE_T = 2.0        # größte freie Spannweite einer Decke ohne Gewölbe (hohl.BRUECKE ist 10); 2 = fast überall Gewölbe, keine Decken über Luft
STUETZE_ROHR = True    # Schachtrohr trägt das Gewölbe mit
UMKREIS_T = None       # Kegel nur im eigenen Bereich (hohl.ceiling umkreis); None = überall
FUELLEN_T = 2.0        # Spalten im Hohlraum, die schmaler sind, werden gefüllt (hohl.spalten)
FUELLEN_T_STANDARD = FUELLEN_T
NUR_ROHR = False       # nur mit Rohrstütze bauen (Probeläufe)
# --- Optionen für möglichst viel offenen Raum (alle Standard aus, der bisherige Bau bleibt unverändert) ---
SAEULEN_T = None       # Abstand (mm): dünne Pfeiler Ø 1,6 als zusätzliche Stützpunkte im Raum mit niedrigem Dach (hohl.ceiling saeulen); None = aus
SAEULEN_HMAX_T = 12.0  # nur dort, wo das Dach (Ziel-Hohlraum) höchstens so hoch über der Plattenoberseite liegt (mm)
OFFEN_AUFSATZ, OFFEN_SAEULEN, OFFEN_FUELLEN = "alles", 6.0, 1.2    # Werte von `--offen` (Neues Augusteum 28,16 -> 16,5 cm³)
AUFSATZ_T = None       # zweites Gewölbe über dem Schachtrohr (`hohl.aufsatz`), None = aus (Standard, der bisherige Bau). "boden": Boden über der Säule;
                       # "oeffnung": dazu geht die Kassettenöffnung ohne Walm in den Aufsatz über; "rohr": dazu entfällt die Säule über dem Rohr;
                       # "alles": dazu entfallen auch die Keile neben dem Rohr
AUFSATZ_BRUECKE_T = 0.9  # `bruecke` des Aufsatzes (hohl.ceiling): unter dem schrägen Dach (Stufen des Ziel-Hohlraums je 0,4 mm) sollen die Stufen schmal bleiben
AUFSATZ_ABZUG_T = 0.2  # Kegel des Aufsatzes setzen so viel tiefer an (hohl.ceiling abzug): der First bleibt unter dem schrägen Dach, keine flachen Stücke am First
AUFSATZ_FUELLEN_T = 0.6  # Spalten im Aufsatz, die schmaler sind, werden gefüllt (FUELLEN_T = 2 kappt jeden First flach auf 2 mm Breite: Kragstück am First)
AUFSATZ_BODEN_T = 0.4  # Boden des Aufsatzes liegt so viel (mindestens, aufs Lagenraster aufgerundet) über der Säule bzw. Walmspitze
WINKEL_T = hohl.WINKEL  # Neigung der Gewölbe gegen die Senkrechte (45 = Standard; Walm und `dach45` bleiben 45)
LAYER = 0.2            # Schichthöhe für die Überhangprüfung
UEBERHANG_T = 0.25     # Überhang je 0,2-mm-Schicht, der als getragen gilt (gut 45°)
SPALT_MIN_T = 0.0      # schmale Spalten und Splitter im fertigen Hohlraum schließen (plug/spalt.py): Teile des Hohlraums schmaler als dies werden Material; 0 = aus (Nutzer entscheidet), --spalt-min 0.4 = Düsenbreite
MAX_KANTEN_PRO_LAUF = 14   # beruehrkanten_trennen probiert je Gruppe zusammenhängender Berührkanten 2^n Kombinationen; über dieser Zahl bleibt das Netz, wie es ist
SPLITTER_MM3 = 1.0     # eigene Schalen mit kleinerem Betrag des Volumens sind Mikrohohlräume aus den Booleschen Schritten und entfallen (sauber)


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


def aufsatz_raum(cav, lay0, platz, kas, rohr_fp, zt, z_rohr, F):
    """Hohlraum des Aufsatzes (Weltlage): zweites Gewölbe (`hohl.aufsatz`) über dem Schachtrohr, Boden bei zt + AUFSATZ_BODEN_T auf dem
    Lagenraster. Wo die Decke des Raums darunter weniger als DACH unter dem Boden liegt, wird die Lücke zum Hohlraum (sonst bliebe dort
    eine messerscharfe Haut zwischen zwei Räumen). AUFSATZ_T:
      "boden"   : nur der Aufsatz;
      "oeffnung": über der Öffnung der Kassette entfällt der Walm, die Öffnung geht senkrecht in den Aufsatz über (der Walm war nur nötig,
                  weil dort sonst eine flache Decke läge);
      "rohr"    : auch die Säule über dem Schachtrohr entfällt: der Hohlraum beginnt auf der Rohroberkante z_rohr und reicht über den
                  ganzen Grundriss des Rohrs (das Rohr bleibt als Pfeiler im Raum, nur sein Kopf liegt frei);
      "alles"   : dazu auch neben dem Rohr (Keile zwischen der Decke des unteren Raums und dem Boden des Aufsatzes) bis unten offen."""
    z0 = np.ceil((zt + F + AUFSATZ_BODEN_T) / hohl.STEP - 1e-6) * hohl.STEP          # Boden im Rahmen von hohl.py (z = Welt + F)
    up = hohl.aufsatz(lay0, z0, winkel=WINKEL_T, bruecke=AUFSATZ_BRUECKE_T, fuellen=AUFSATZ_FUELLEN_T, abzug=AUFSATZ_ABZUG_T)
    if up is None or up.is_empty():
        return m3d.Manifold()
    up = up.translate([0, 0, -F])
    zb = z0 - F
    b = hohl._cs_poly(up.slice(zb + 0.1))                                              # Grundriss des Aufsatzes über dem Boden
    extra = []                                                                          # senkrechte Prismen, die den Aufsatz nach unten verlängern
    luecke = hohl._cs_poly(cav.slice(zb - hohl.DACH)).intersection(b)                  # Raum darunter reicht fast bis zum Boden
    if not luecke.is_empty and luecke.area > 0.05:
        extra.append(ext(luecke.buffer(0.02, join_style=2), zb - hohl.DACH - 0.01, zb + 0.01))
    if AUFSATZ_T == "oeffnung":
        zk = float(kas.bounding_box()[5]) + FREI_T                                      # Oberkante des senkrechten Teils der Öffnung
        fp = hohl._cs_poly(platz.project()).intersection(b)
        if not fp.is_empty and fp.area > 0.05:
            extra.append(ext(fp.buffer(0.02, join_style=2), zk - 0.01, zb + 0.01))
    elif AUFSATZ_T == "rohr":
        fp = rohr_fp.intersection(b)
        if not fp.is_empty and fp.area > 0.05:
            extra.append(ext(fp.buffer(0.02, join_style=2), z_rohr - 0.05, zb + 0.01))
    elif AUFSATZ_T == "alles":
        # Im ganzen Grundriss des Aufsatzes ist der Raum bis unten offen (Rohr, Boden und Fuß kommen danach wieder dazu): kein Material
        # zwischen der Decke des Raums darunter und dem Boden des Aufsatzes, keine Keile neben dem Rohr
        extra.append(ext(b.buffer(0.02, join_style=2), -F, zb + 0.01))
    if not extra:
        return up
    # Die Prismen überlappen den Aufsatz um 0,02 mm (sauberes Vereinigen), dürfen aber nicht über den Ziel-Hohlraum (Wand 0,8) hinaus
    ziel = hohl.cavity(lay0).translate([0, 0, -F])
    return up + (G.union(extra) ^ ziel)


def gebaeude(slug, solid, fp, p, s, rohrstuetze=None, farb_id=None):
    """Steckbares Hohlgebäude (Manifold, Weltlage, z = 0 Plattenoberseite) und Prüfwerte. rohrstuetze: Rohr trägt das Gewölbe mit
    (Standard STUETZE_ROHR). farb_id: originalID eines gefärbten solid (face_id = Farbnummer + 1, `plug/colour.py`); dann trägt das
    Ergebnis face_id = Farbnummer + 1 für Dreiecke aus dem solid und 0 für alle übrigen (Fuß, Hohlraum, Schacht)."""
    rohrstuetze = STUETZE_ROHR if rohrstuetze is None else rohrstuetze
    d = P.dims_plan()
    F = d["F"]
    var = p["var"]
    yc = C.foot_local(var, 0.0).centroid.y
    fuss = ext(fp, -F, 0.02)                                        # Fuß ohne Fase (die Fase FUSS_FASE_T kommt nach dem Aushöhlen, siehe unten)
    voll = solid + fuss
    rohr, cut, platz, bedarf, kas, zs, z_rohr = schacht_teile(var, min(ROHR_T, p["wall"]), F)
    T = lambda m: place(m.translate([0, 0, -F]), p, yc)
    rohr, cut, platz, bedarf, kas = T(rohr), T(cut), T(platz), T(bedarf), T(kas)
    zs -= F
    # Hohlraum: hohl.py rechnet mit Boden bei z = 0, also um F nach oben schieben und zurück. Das Schachtrohr wird vom Bett an gedruckt
    # und trägt das Gewölbe mit (Stütze bis zur Rohroberkante): die Räume werden von Wand und Rohr aus überwölbt.
    rohr_fp = hohl._cs_poly(rohr.slice(-F + 0.5))
    stuetzen = [(rohr_fp, z_rohr)] if rohrstuetze else None
    saeulen = []
    cav, lay0 = hohl.hohlraum(voll.translate([0, 0, F]), bruecke=BRUECKE_T, stuetzen=stuetzen, fuellen=FUELLEN_T,
                              umkreis=UMKREIS_T, winkel=WINKEL_T, saeulen=SAEULEN_T, saeulen_hmax=SAEULEN_HMAX_T + F, saeulen_out=saeulen)
    cav = cav.translate([0, 0, -F])
    if saeulen:
        # Pfeiler: über die ganze Höhe aus dem Hohlraum aussparen (über dem Kegelansatz ist ohnehin Material)
        cav = cav - ext(unary_union([shapely.Point(x, y).buffer(hohl.SAEULE_D / 2, quad_segs=8) for x, y in saeulen]), -F - 1.0, 400.0)
    if rohrstuetze:
        # Über dem Rohr kein Gewölbe-Hohlraum: das Rohr setzt sich nach oben als Säule fort, frei bleibt dort nur der Raum über der
        # Kassette (Platz mit 45°-Walm, unten). Sonst griffe das Gewölbe eines Nachbarraums über den Rohrkopf, wo das Rohr nicht trägt,
        # und zwischen ihm und dem Walm bliebe eine nach unten hängende Kante.
        # Die Säule reicht bis 0,4 mm über die Walmspitze; darüber darf das Gewölbe wieder über das Rohr greifen (hohe Gebäude).
        zt = float(platz.bounding_box()[5]) + 0.4
        cav = cav - ext(rohr_fp, -F - 1.0, zt)
        if AUFSATZ_T:
            cav = cav + aufsatz_raum(cav, lay0, platz, kas, rohr_fp, zt, z_rohr - F, F)
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
    # Fuß-Fase FUSS_FASE_T: außen abschrägen, innen die Wand nachführen (0,8 horizontal), damit keine Schneide entsteht. Nach dem Aushöhlen,
    # weil hohl.py einen nach oben nur abnehmenden Querschnitt erwartet (eine Fase im Volumenkörper macht die Wände darüber zu Gewölbe).
    zc = -F + BC.n_layers(FUSS_FASE_T) * BC.L + 0.02
    ch_out = BC.slab_ch(fp, -F, zc, FUSS_FASE_T)
    ch_in = BC.slab_ch(fp.buffer(-hohl.WAND), -F, zc, FUSS_FASE_T)
    # Liegt das Schachtrohr näher am Rand als die Fase (Paulinum, Wand 1,2: die Kassette sitzt dicht an der Nordwand; Hochhaus: Rohr 3,5 mm vom
    # Rand, Fase 3,9 in der untersten Lage), würde die Fase die Rohrwand abschneiden. Nur das Rohr (Umriss `rohr_fp` im Grundriss) bleibt dann in
    # voller Ausdehnung stehen; der Rest des Umrisses behält die Fase, so steht kein breites Randstück als Wulst über der Fase. Der Innenring der
    # Fase endet am Schacht (er darf nicht in Schacht und Einführfase ragen).
    rohr_aussen = G.clean(rohr_fp.intersection(fp))
    nah = rohr_aussen.difference(fp.buffer(-FUSS_FASE_T, join_style=2)) if not rohr_aussen.is_empty else Polygon()
    ausnahme = ext(rohr_aussen, -F - 0.01, zc) if not nah.is_empty and nah.area >= 0.05 else None
    huelle = ch_out + ausnahme if ausnahme is not None else ch_out
    ring = (ch_out - ch_in) - cut.trim_by_plane([0, 0, -1], -zc - 1.0)
    behalte = huelle + ext(fp.buffer(5.0), zc - 0.01, 300.0)
    body = (body ^ behalte) + ring
    fuell, spalt = None, None
    if SPALT_MIN_T > 0:
        # Nachträglicher Schritt (plug/spalt.py): schmale Spalten und Splitter im Hohlraum; Hülle = massiver Körper mit Fuß und Fase.
        # Die Füllung wird erst nach dem Vereinfachen zum Körper gefügt (siehe unten).
        mund = hohl._cs_poly(cut.slice(-F + 0.05))                               # Grundriss des unten offenen Schachts
        fuell, spalt = SP.fuellung(body, voll ^ behalte, schutz=cut + bedarf, nach_unten=mund, z_unten=-F, mind=SPALT_MIN_T)
    if farb_id:
        body = farb_ids(body)
    body0 = body.simplify(hohl.VEREINFACHEN)
    verworfen = 0
    while True:
        body, netz = sauber(SP.einsetzen(body0, fuell, bool(farb_id)), ids=bool(farb_id))
        # Füllstücke, an denen im fertigen Netz Berührkanten (Haarkanten, Slicer meldet sie) entstehen, weglassen und neu zusammensetzen
        if not fuell or netz.get("nachher", {}).get("beruehrkanten", 0) == 0:
            break
        mt = body.to_mesh()
        rest = SP.ohne_stuecke_bei(fuell, _beruehr_orte(np.asarray(mt.vert_properties)[:, :3], np.asarray(mt.tri_verts)))
        if len(rest) == len(fuell):
            break
        verworfen += len(fuell) - len(rest)
        fuell = rest
    if spalt is not None and verworfen:
        spalt["verworfen_wegen_beruehrkanten"] = verworfen
    info = dict(slug=slug, var=var, wall=p["wall"], F=F, rohrstuetze=rohrstuetze, netz=netz)
    if ausnahme is not None:
        info["fase_rohr_voll_mm2"] = round(nah.area, 1)
    if saeulen:
        info["saeulen"] = len(saeulen)
    if AUFSATZ_T:
        info["aufsatz"] = AUFSATZ_T
    if spalt:
        info["spalt"] = spalt
    kol = (body ^ kas).volume()
    info["kollision_mm3"] = round(kol, 3)
    info["platz_fehlt_mm3"] = round((bedarf - ziel).volume(), 2)    # Platz für die Kassette, den der Ziel-Hohlraum nicht hergibt
    info["volumen_cm3"] = round(body.volume() / 1000, 2)
    return body, kas, info


def _netz_werte(v, f):
    """Entartete Dreiecke (Fläche null in float32, wie in der STL) und Berührkanten (Kanten mit mehr als zwei Flächen, wenn man die Eckpunkte
    nach Lage zusammenfasst wie ein Slicer beim Laden)."""
    v = np.asarray(v, np.float32).astype(np.float64)
    f = np.asarray(f, np.int64)
    a = np.linalg.norm(np.cross(v[f[:, 1]] - v[f[:, 0]], v[f[:, 2]] - v[f[:, 0]]), axis=1) / 2
    _, inv = np.unique(np.asarray(v, np.float32), axis=0, return_inverse=True)
    g = inv.ravel()[f]
    e = np.sort(np.concatenate([g[:, [0, 1]], g[:, [1, 2]], g[:, [2, 0]]]), axis=1)
    _, cnt = np.unique(e, axis=0, return_counts=True)
    return int((a < 1e-9).sum()), int((cnt > 2).sum())


def _beruehr_orte(v, f):
    """Mittelpunkte der Berührkanten (Kanten mit mehr als zwei Flächen, Eckpunkte nach Lage zusammengefasst)."""
    v = np.asarray(v, np.float32)
    uv, inv = np.unique(v, axis=0, return_inverse=True)
    g = inv.ravel()[np.asarray(f, np.int64)]
    e = np.sort(np.concatenate([g[:, [0, 1]], g[:, [1, 2]], g[:, [2, 0]]]), axis=1)
    ue, cnt = np.unique(e, axis=0, return_counts=True)
    bad = ue[cnt > 2]
    return (uv[bad[:, 0]].astype(np.float64) + uv[bad[:, 1]]) / 2


FARB_ID0 = 10_000_000   # face_id der gefärbten Dreiecke (die übrigen Körper tragen ihre Dreiecksnummern, weit darunter)


def farb_ids(body):
    """face_id = Farbnummer + 1 für Dreiecke aus dem gefärbten Körper (face_id ab FARB_ID0), sonst 0 (siehe gebaeude, farb_id)."""
    m = body.to_mesh()
    fid = np.asarray(m.face_id).astype(np.int64)
    key = np.where(fid >= FARB_ID0, fid - FARB_ID0 + 1, 0).astype(np.uint32)
    return m3d.Manifold(m3d.Mesh(vert_properties=np.array(np.asarray(m.vert_properties)[:, :3], np.float32, order="C"),
                                 tri_verts=np.array(m.tri_verts, np.uint32, order="C"), face_id=key))


BERUEHR_MAX = 12       # mehr Berührkanten werden nicht getrennt (die Suche probiert 2^n Kombinationen; bei der Farbfassung des Seminargebäudes lief sie nie zu Ende)


def beruehrkanten_trennen(v, f, eps_max=0.02):
    """Berührkanten (Kanten mit vier Flächen; Slicer melden sie als nicht-mannigfaltige Kanten) auflösen. An einer solchen Kante berühren sich
    zwei Keile (Material oder Hohlraum) nur an der Kante. Je Kante gibt es zwei Möglichkeiten, die vier Flächen (nach Winkel um die Kante
    sortiert) zu zwei Keil-Paaren zu ordnen. Probiert werden alle Kombinationen; gilt eine, bei der danach keine Berührkante mehr bleibt und
    nichts Neues offen ist, bekommt an den Eckpunkten jeder Kante jedes weitere zusammenhängende Flächenstück (Zusammenhang über reguläre
    Kanten und über die Paare) einen eigenen Eckpunkt, vom größten Flächenstück weggerückt um höchstens `eps_max` (und ein Viertel der
    kürzesten anliegenden Kante). Dreiecke bleiben in Anzahl und Reihenfolge (face_id passt weiter).
    Liefert (Eckpunkte float32, Dreiecke, Zahl der getrennten Kanten); unverändert (0), wenn keine Kombination aufgeht."""
    import itertools
    v = np.asarray(v, np.float32)
    f = np.asarray(f, np.int64)
    uv, inv = np.unique(v, axis=0, return_inverse=True)           # Eckpunkte nach Lage zusammenfassen wie ein Slicer
    g = inv.ravel()[f]
    vd = uv.astype(np.float64)
    n = len(uv)
    fi = np.nonzero((g[:, 0] != g[:, 1]) & (g[:, 1] != g[:, 2]) & (g[:, 2] != g[:, 0]))[0]
    E = np.concatenate([g[fi][:, [0, 1]], g[fi][:, [1, 2]], g[fi][:, [2, 0]]])
    key = np.sort(E, axis=1) @ np.array([n, 1], np.int64)
    fo = np.tile(fi, 3)
    uk, ie, cnt = np.unique(key, return_inverse=True, return_counts=True)
    bad = [int(b) for b in np.nonzero(cnt > 2)[0]]
    if not bad:
        return uv, g, 0
    cross = np.cross(vd[g[:, 1]] - vd[g[:, 0]], vd[g[:, 2]] - vd[g[:, 0]])      # 2 × Fläche × Normale (nach außen)
    kantenflaechen = {}
    for q, kk in zip(fo, ie):
        kantenflaechen.setdefault(int(kk), []).append(int(q))
    mog = {}                                                                    # Kante -> {"mat": Paare, "hohl": Paare}
    for b in bad:
        fs = kantenflaechen[b]
        if len(fs) != 4 or len(set(fs)) != 4:
            return uv, g, 0
        a, c = int(uk[b] // n), int(uk[b] % n)
        t = vd[c] - vd[a]
        t /= np.linalg.norm(t)
        ds = []
        for q in fs:
            w = [x for x in g[q] if x not in (a, c)][0]
            d = vd[w] - vd[a]
            d -= d @ t * t
            ds.append(d / np.linalg.norm(d))
        t2 = np.cross(t, ds[0])
        order = [int(i) for i in np.argsort([np.arctan2(d @ t2, d @ ds[0]) for d in ds])]
        paar = [(fs[order[k]], fs[order[(k + 1) % 4]]) for k in range(4)]       # Nachbarn in der Winkelfolge: Keile (Material oder Hohlraum)
        mog[b] = {"a": [paar[0], paar[2]], "b": [paar[1], paar[3]]}
    ecken = sorted({int(x) for b in bad for x in (uk[b] // n, uk[b] % n)})
    elem = {w: [] for w in ecken}
    for q in fi:
        for x in g[q]:
            if int(x) in elem:
                elem[int(x)].append(int(q))

    def versuch(wahl, lokal=None, nk=0):
        neu_pos, neu_w, ersatz = [], [], {}
        for w in ecken:
            fl = elem[w]
            par = {q: q for q in fl}

            def find(x):
                while par[x] != x:
                    par[x] = par[par[x]]
                    x = par[x]
                return x
            for q in fl:
                for k in range(3):
                    x, y = int(g[q][k]), int(g[q][(k + 1) % 3])
                    if w not in (x, y):
                        continue
                    kk = int(np.searchsorted(uk, min(x, y) * n + max(x, y)))
                    if cnt[kk] == 2:
                        o = [r for r in kantenflaechen[kk] if r != q]
                        if o and o[0] in par:
                            par[find(q)] = find(o[0])
            for b, art in zip(bad, wahl):
                a, c = int(uk[b] // n), int(uk[b] % n)
                if w in (a, c):
                    for p0, p1 in mog[b][art]:
                        par[find(int(p0))] = find(int(p1))
            grp = {}
            for q in fl:
                grp.setdefault(find(q), []).append(q)
            gruppen = sorted(grp.values(), key=lambda qs: -np.linalg.norm(cross[qs], axis=1).sum())
            for qs in gruppen[1:]:
                mitte = np.array([vd[g[q]].mean(axis=0) for q in gruppen[0]]).mean(axis=0)
                d = vd[w] - mitte                                          # weg vom größten Flächenstück
                nl = np.linalg.norm(d)
                if nl < 1e-12:
                    return None
                kurz = min(np.linalg.norm(vd[int(x)] - vd[w]) for q in qs for x in g[q] if int(x) != w)
                neu_pos.append(vd[w] + d / nl * min(eps_max, 0.25 * kurz))
                neu_w.append(w)
                ersatz.update({(q, w): n + len(neu_pos) - 1 for q in qs})
        if not ersatz:
            return None
        g2 = g.copy()
        for (q, w), nn in ersatz.items():
            g2[q][g2[q] == w] = nn
        e2 = np.sort(np.concatenate([g2[fi][:, [0, 1]], g2[fi][:, [1, 2]], g2[fi][:, [2, 0]]]), axis=1) @ np.array([n + len(neu_pos), 1], np.int64)
        if lokal is None:
            if int((np.unique(e2, return_counts=True)[1] != 2).sum()) != int((cnt != 2).sum()) - len(bad):      # alle Berührkanten weg, nichts Neues offen
                return None
        else:                                                                      # nur an den Eckpunkten dieser Gruppe prüfen: nk Kanten weg, nichts Neues offen
            nn = n + len(neu_pos)
            nah_ = np.zeros(nn, bool)
            nah_[list(lokal)] = True
            nah_[[n + i for i, w in enumerate(neu_w) if w in lokal]] = True
            ue2, c2 = np.unique(e2, return_counts=True)
            vor = nah_[:n][uk // n] | nah_[:n][uk % n]
            if int((c2[nah_[ue2 // nn] | nah_[ue2 % nn]] != 2).sum()) != int((cnt[vor] != 2).sum()) - nk:
                return None
        return np.concatenate([uv, np.array(neu_pos, np.float32).reshape(-1, 3)]), g2

    # Berührkanten, die einen Eckpunkt teilen, hängen zusammen; weit auseinanderliegende nicht. Je Gruppe die Kombinationen (2^n) einzeln
    # probieren (alle anderen Gruppen vorläufig "a"), die Wahlen danach zusammen prüfen: sonst sind 17 Kanten 131 072 Versuche.
    grp = {b: b for b in bad}

    def wurzel(x):
        while grp[x] != x:
            grp[x] = grp[grp[x]]
            x = grp[x]
        return x
    for i, b1 in enumerate(bad):
        for b2 in bad[i + 1:]:
            if {int(uk[b1] // n), int(uk[b1] % n)} & {int(uk[b2] // n), int(uk[b2] % n)}:
                grp[wurzel(b1)] = wurzel(b2)
    gruppen = {}
    for b in bad:
        gruppen.setdefault(wurzel(b), []).append(b)
    wahl_alle = {b: "a" for b in bad}
    for kanten in gruppen.values():
        if len(kanten) > MAX_KANTEN_PRO_LAUF:                                       # 2^n Kombinationen: zu viele zusammenhängende Berührkanten
            return uv, g, 0
        verts = {int(x) for b in kanten for x in (uk[b] // n, uk[b] % n)}
        for wahl in itertools.product(("a", "b"), repeat=len(kanten)):
            w_ = dict(wahl_alle)
            w_.update(zip(kanten, wahl))
            if versuch([w_[b] for b in bad], lokal=verts, nk=len(kanten)) is not None:
                wahl_alle = w_
                break
        else:
            return uv, g, 0
    r = versuch([wahl_alle[b] for b in bad])
    if r is not None:
        return r[0], r[1], len(bad)
    return uv, g, 0


def sauber(body, splitter=SPLITTER_MM3, ids=False):
    """Netz so bereinigen, dass ein Slicer es beim Laden nicht umdreht (Befund 2026-10-18, Paulinum im Slicer massiv):
    1. Über float32 neu aufbauen: Manifold rechnet in double, die STL hat float32. Dabei fallen Splitterdreiecke auf Fläche null; PrusaSlicer,
       Bambu Studio und Orca (alle mit admesh) löschen solche Dreiecke beim Laden, verbinden die Nachbarn neu und richten die Normalen danach
       aus. Beim Paulinum drehte das die ganze Innenschale um (18 772 Flächen, Slicer-Volumen 46,0 statt 7,5 cm³): der Innenraum wurde Füllung.
       Der Neuaufbau aus dem float32-Netz lässt Manifold diese Dreiecke selbst sauber zusammenziehen.
    2. Winzige eigene Schalen (Mikrohohlräume aus den Booleschen Schritten, |Volumen| < splitter mm³) weglassen; sie berühren die Wände nur an
       Kanten und sind die meisten Berührkanten. Gezählt wird nach der Netztopologie (Eckpunkt-Indizes), nicht nach Lage, damit Wände aus
       sich berührenden Teilen ganz bleiben.
    ids: face_id (Farben, siehe farb_ids) durch den Neuaufbau mitnehmen.
    Liefert (Körper, Werte vorher/nachher). Fällt auf den alten Körper zurück, wenn das Ergebnis nicht gültig wäre oder das Volumen abweicht."""
    m = body.to_mesh()
    v0, f0 = np.asarray(m.vert_properties)[:, :3], np.asarray(m.tri_verts)
    werte = dict(vorher=dict(zip(("entartet", "beruehrkanten"), _netz_werte(v0, f0))))
    fid = dict(face_id=np.asarray(m.face_id, np.uint32)) if ids else {}
    neu = m3d.Manifold(m3d.Mesh(vert_properties=np.array(v0, np.float32, order="C"), tri_verts=np.array(f0, np.uint32, order="C"), **fid))
    m = neu.to_mesh()
    fid = np.asarray(m.face_id, np.uint32) if ids else None
    v, f = np.array(np.asarray(m.vert_properties)[:, :3], np.float32, order="C"), np.asarray(m.tri_verts).astype(np.int64)
    # Schalen nach Topologie: Zusammenhangskomponenten der Eckpunkte über die Dreieckskanten
    import scipy.sparse as sp
    from scipy.sparse.csgraph import connected_components
    n = len(v)
    adj = sp.coo_matrix((np.ones(2 * len(f)), (np.r_[f[:, 0], f[:, 1]], np.r_[f[:, 1], f[:, 2]])), shape=(n, n))
    k, lab = connected_components(adj, directed=False)
    vd = v.astype(np.float64)
    vol = np.einsum("ij,ij->i", vd[f[:, 0]], np.cross(vd[f[:, 1]], vd[f[:, 2]])) / 6.0
    sv = np.bincount(lab[f[:, 0]], vol, minlength=k)
    weg = np.abs(sv) < splitter
    bleibt = ~weg[lab[f[:, 0]]]
    f2 = f[bleibt]
    fid2 = dict(face_id=np.ascontiguousarray(fid[bleibt])) if ids else {}
    neu = m3d.Manifold(m3d.Mesh(vert_properties=v, tri_verts=np.array(f2, np.uint32, order="C"), **fid2))
    if neu.status() != m3d.Error.NoError or abs(neu.volume() - body.volume()) > 0.002 * abs(body.volume()):
        werte["zurueckgefallen"] = True
        return body, werte
    # 3. Berührkanten trennen (Keile, die sich nur an einer Kante berühren, bekommen eigene Eckpunkte)
    mt = neu.to_mesh()
    vt, ft, ntr = beruehrkanten_trennen(np.asarray(mt.vert_properties)[:, :3], np.asarray(mt.tri_verts))
    if ntr:
        fid3 = dict(face_id=np.asarray(mt.face_id, np.uint32)) if ids else {}
        cand = m3d.Manifold(m3d.Mesh(vert_properties=np.array(vt, np.float32, order="C"), tri_verts=np.array(ft, np.uint32, order="C"), **fid3))
        if cand.status() == m3d.Error.NoError and abs(cand.volume() - body.volume()) <= 0.002 * abs(body.volume()) \
                and _netz_werte(vt, ft)[1] < _netz_werte(np.asarray(mt.vert_properties)[:, :3], np.asarray(mt.tri_verts))[1]:
            neu = cand
            werte["kanten_getrennt"] = ntr
        else:
            werte["kanten_trennen_verworfen"] = True
    m = neu.to_mesh()
    werte["nachher"] = dict(zip(("entartet", "beruehrkanten"), _netz_werte(np.asarray(m.vert_properties)[:, :3], np.asarray(m.tri_verts))))
    werte["schalen_entfernt"] = int(weg.sum())
    werte["schalen"] = int(k - weg.sum())
    return neu, werte


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
    models = C.models_plan(s, scale)
    places = json.load(open(C.CACHE % scale))
    out = []
    for slug, p in places.items():
        if slugs and slug not in slugs:
            continue
        solid, fp, _ = models[slug]
        # Mit und ohne Rohrstütze bauen, das leichtere nehmen: Unter niedrigen Dächern (Neues Augusteum, Hörsaalgebäude) setzt das Gewölbe
        # mit der Rohrstütze viel höher an; in hohen, schmalen Gebäuden trägt das Rohr kaum und die Säule über ihm kostet nur.
        varianten = [gebaeude(slug, solid, fp, p, s, r) for r in ((True,) if NUR_ROHR else (True, False) if STUETZE_ROHR else (False,))]
        body, kas, info = min(varianten, key=lambda v: v[2]["volumen_cm3"])
        info["volumen_varianten_cm3"] = {("mit" if v[2]["rohrstuetze"] else "ohne") + "_rohrstuetze": v[2]["volumen_cm3"] for v in varianten}
        info["ueberhang"] = ueberhang(body)
        out.append((slug, body, kas, info))
        u = info["ueberhang"]
        print("  %-22s %-5s %6.2f cm³ (%s)  Kollision %.3f mm³  Platz fehlt %.2f mm³  Brücken %.0f mm² (Spannweite bis %.1f mm)  "
              "Kragstücke %.1f mm² (bis %.1f mm)" % (slug, info["var"], info["volumen_cm3"],
                                                    " / ".join("%s %.2f" % kv for kv in info["volumen_varianten_cm3"].items()), info["kollision_mm3"], info["platz_fehlt_mm3"],
                                                    u["bruecke_mm2"], 2 * u["bruecke_mm"], u["krag_mm2"], u["krag_mm"]), flush=True)
        nz = info["netz"]
        print("      Netz: entartete Dreiecke %d -> %s, Berührkanten %d -> %s, Mikroschalen entfernt %s%s" % (
            nz["vorher"]["entartet"], nz.get("nachher", {}).get("entartet", "-"), nz["vorher"]["beruehrkanten"],
            nz.get("nachher", {}).get("beruehrkanten", "-"), nz.get("schalen_entfernt", 0), "  ZURÜCKGEFALLEN" if nz.get("zurueckgefallen") else ""))
        for st in sorted(u["stellen"], key=lambda t: (t[0] != "krag", -t[3]))[:6]:
            print("      %-7s z=%5.1f  %5.1f mm²  Reichweite %.1f mm  bei (%.1f, %.1f)" % st)
    return out


def main():
    global BRUECKE_T, STUETZE_ROHR, FUELLEN_T, UMKREIS_T, AUFSATZ_T, AUFSATZ_BRUECKE_T, AUFSATZ_ABZUG_T, AUFSATZ_FUELLEN_T, WINKEL_T, SAEULEN_T, SAEULEN_HMAX_T, NUR_ROHR, SPALT_MIN_T, OUT, PREV
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scale", type=int, default=P.SCALE_PLAN)
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--bruecke", type=float, default=BRUECKE_T, help="größte freie Spannweite einer Decke ohne Gewölbe (mm)")
    ap.add_argument("--ohne-rohrstuetze", action="store_true", help="Gewölbe nur von den Außenwänden (Stand vor 2026-10-17)")
    ap.add_argument("--fuellen", type=float, default=FUELLEN_T, help="Spalten schmaler als dies füllen (mm, 0 = aus)")
    ap.add_argument("--umkreis", type=float, default=UMKREIS_T, help="Kegel einer Stütze nur bis so viel weiter als die nächste Stütze (mm)")
    ap.add_argument("--aufsatz", nargs="?", const="boden", choices=("boden", "oeffnung", "rohr", "alles"),
                    help="zweites Gewölbe über dem Schachtrohr (Raum über dem Rohr bis zum Dach, hohl.aufsatz); oeffnung: ohne Walm über der Kassette, "
                         "rohr: auch ohne Säule über dem Rohr, alles: im ganzen Grundriss des Aufsatzes bis unten offen (Standard ohne diesen Schalter: aus)")
    ap.add_argument("--aufsatz-bruecke", type=float, default=AUFSATZ_BRUECKE_T, help="bruecke des Aufsatzes (mm); kleiner = schmalere Stufen unter dem schrägen Dach")
    ap.add_argument("--aufsatz-abzug", type=float, default=AUFSATZ_ABZUG_T, help="Kegel des Aufsatzes um so viel mm tiefer ansetzen (First unter dem schrägen Dach)")
    ap.add_argument("--aufsatz-fuellen", type=float, default=AUFSATZ_FUELLEN_T, help="Spalten im Aufsatz schmaler als dies füllen (mm)")
    ap.add_argument("--saeulen", type=float, default=SAEULEN_T, help="dünne Pfeiler als zusätzliche Stützpunkte: Abstand (mm) bis zur nächsten Wand oder Stütze, "
                                                                     "den ein Raum mit niedrigem Dach höchstens haben darf (None = aus)")
    ap.add_argument("--saeulen-hmax", type=float, default=SAEULEN_HMAX_T, help="Pfeiler nur, wo das Dach höchstens so hoch liegt (mm über der Platte)")
    ap.add_argument("--winkel", type=float, default=WINKEL_T, help="Neigung der Gewölbe gegen die Senkrechte in Grad (Standard 45)")
    ap.add_argument("--nur-rohr", action="store_true", help="nur die Fassung mit Rohrstütze bauen (Probeläufe, halbe Rechenzeit)")
    ap.add_argument("--offen", action="store_true", help="Voreinstellung für möglichst viel offenen Raum (weniger Material): --aufsatz alles, --saeulen 6, "
                                                         "--fuellen 1.2 (Schalter, die man selbst setzt, behalten ihren Wert)")
    ap.add_argument("--spalt-min", type=float, default=SPALT_MIN_T, help="Teile des Hohlraums schmaler als dies (mm) werden gefüllt (plug/spalt.py; 0 = aus, 0.4 = Düsenbreite)")
    ap.add_argument("--out", help="Ausgabeordner für STL und Bilder (Standard: die eingecheckten Ordner)")
    a = ap.parse_args()
    BRUECKE_T = a.bruecke
    STUETZE_ROHR = not a.ohne_rohrstuetze
    FUELLEN_T = a.fuellen
    UMKREIS_T = a.umkreis
    AUFSATZ_T = a.aufsatz
    if a.offen:
        AUFSATZ_T = a.aufsatz or OFFEN_AUFSATZ
        if a.saeulen is None:
            a.saeulen = OFFEN_SAEULEN
        if a.fuellen == FUELLEN_T_STANDARD:
            a.fuellen = OFFEN_FUELLEN
            FUELLEN_T = a.fuellen
    AUFSATZ_BRUECKE_T = a.aufsatz_bruecke
    AUFSATZ_ABZUG_T = a.aufsatz_abzug
    AUFSATZ_FUELLEN_T = a.aufsatz_fuellen
    WINKEL_T = a.winkel
    SAEULEN_T = a.saeulen
    SAEULEN_HMAX_T = a.saeulen_hmax
    NUR_ROHR = a.nur_rohr
    SPALT_MIN_T = a.spalt_min
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
