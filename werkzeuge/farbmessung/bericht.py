#!/usr/bin/env python3
"""Schreibt den HTML-Bericht „Farbvergleich alt/neu“ nach vorschau/farbvergleich/index.html.

    python3 werkzeuge/farbmessung/bericht.py <alte farben.json>

Voraussetzungen: data/messung.json (python3 farbmessung.py messen), vergleich_bilder.py (Bilder), generate.py
(Gesamtansichten in vorschau/laserscan/…); die Gesamtansichten „alt“ liegen im selben Ordner wie die alte farben.json
unter vorschau_laserscan/ (Sicherung vor der Änderung).
"""
import html
import json
import os
import shutil
import sys
from string import Template

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import farbmessung as FM
import generate as G
import registrierung as R

OUT = os.path.join(G.HERE, "vorschau", "farbvergleich")
NAMEN = {"01": "Paulinum", "02": "Neues Augusteum (mit Audimax)", "03": "Hörsaalgebäude / Mensa am Park",
         "04": "Seminargebäude", "05": "Institutsgebäude", "06": "City-Hochhaus „Uniriese“", "07": "Moritzbastei",
         "08": "Innenhof (Leibnizforum)"}
FARBNAMEN = {  # lesbare Namen der Farbschlüssel
    "stein_hell": "Giebelstein", "weiss": "weißer Kalkstein", "stein_glas": "Stein-Glas-Bänder", "glas": "Glasstreifen",
    "zink": "Dachreiter (Zink)", "fensterglas": "Maßwerkfenster", "rosette_innen": "Rosette innen",
    "glas_stein": "Glas mit Steinlamellen", "lamellen": "Lamellenband oben", "sandstein": "Sandsteinportal",
    "pavillon_weiss": "Audimax (weiße Hülle)", "platten": "helle Fassadenplatten", "sockel": "Sockel", "rot": "rote Verkleidung",
    "wabenplatten": "weiße Wabenplatten", "band_rotbraun": "rotbraunes Band", "glasfassade": "Glasfassade Eingang",
    "naturstein": "Naturstein (Lochfassade)", "rotbraun": "rotbraune Verkleidung", "dunkel": "dunkles Erdgeschoss",
    "glasfront": "Glasfront", "kopfbau_dunkel": "Kopfbau dunkel", "fassade": "Granitplatten mit Fenstern",
    "ziegel": "Ziegel", "stein": "Naturstein", "putz": "weißer Putz"}


def hexlum(h):
    return FM.lum(FM.lin(FM.np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)]) / 255.0))


def swatch(h, cls=""):
    return '<span class="sw %s" style="background:%s" title="%s"></span>' % (cls, h, h)


def foto_zeilen(kat, messung, ids):
    out = []
    for fid in ids:
        e = kat[fid]
        info = messung["fotos"][fid]
        zeit = (e.get("zeit") or "")[:16].replace("T", " ")
        sonne = "bedeckt (Zeitstempel unzuverlässig)" if e.get("bedeckt") else ("Sonne %.0f° über dem Horizont" % info["sonne"] if info.get("sonne") is not None else "")
        out.append('''<article class="vergleich">
  <header><h3>%s</h3><p>%s · %s%s</p></header>
  <div class="drei">
    <figure><img src="%s_foto.jpg" alt="Foto"><figcaption>Foto</figcaption></figure>
    <figure><img src="%s_alt.jpg" alt="Modell, alte Farben"><figcaption>Modell alt</figcaption></figure>
    <figure><img src="%s_neu.jpg" alt="Modell, neue Farben"><figcaption>Modell neu</figcaption></figure>
  </div>
  <p class="quelle">%s · <a href="%s">%s</a> · %s · %s</p>
</article>''' % (html.escape(e.get("titel") or fid), html.escape(zeit), html.escape(sonne), "", fid, fid, fid,
                 html.escape(e["urheber"]), html.escape(e["seite"]), "Quelle", html.escape(e["lizenz"]), html.escape(e["quelle"])))
    return "\n".join(out)


def gebaeude_tabellen(alt, neu, messung):
    out = []
    for b in G.OBJEKTE:
        slug = b["slug"]
        if slug not in neu:
            continue
        nr = slug[:2]
        m = messung["gebaeude"].get(slug)
        zeilen = []
        keys = list(neu[slug]["farben"])
        for k in keys:
            a = alt[slug]["farben"].get(k, {}).get("rgb")
            n = neu[slug]["farben"][k]["rgb"]
            if a is None:
                st, cls = "neu gemessene Fläche", "neu"
            elif a.lower() == n.lower():
                st, cls = "unverändert", "gleich"
            else:
                st, cls = "geändert", "geaendert"
            bem = ""
            if m and k in m["bericht"]["farben"]:
                v = m["bericht"]["farben"][k]
                bem = "%d besonnte Zellen" % v["zellen"] if v["gemessen"] else ""
            if k == "pavillon_weiss":
                bem = "Material: weiße Triflex-Beschichtung (Herstellerangabe)"
            name = FARBNAMEN.get(k, "Messfläche %s" % k)
            if a is None:
                z = next((z for z in neu[slug].get("zonen", []) if z.get("farbe") == k), None)
                if z:
                    bem = "%s-Seite, %g–%g m Höhe, %d–%d %% der Fassade" % (
                        {"N": "Nord", "O": "Ost", "S": "Süd", "W": "West"}.get(z.get("seite"), z.get("seite", "")),
                        z["z"][0], z["z"][1], round(100 * z["entlang"][0]), round(100 * z["entlang"][1]))
            zeilen.append('<tr class="%s"><th scope="row">%s<span class="key">%s</span></th><td>%s<code>%s</code></td><td>%s<code>%s</code></td><td>%s</td><td class="bem">%s</td></tr>' % (
                cls, html.escape(name), html.escape(k),
                swatch(a, "alt") if a else "–", a or "", swatch(n, "neu"), n, st, html.escape(bem)))
        nzon = sum(1 for z in (m["bericht"]["zonen"] if m else []) if z["neu"])
        out.append('''<details class="geb"%s><summary><span class="gn">%s</span><span class="gz">%s</span></summary>
<div class="tabelle"><table><thead><tr><th>Fläche</th><th>alt</th><th>neu</th><th>Status</th><th>Hinweis</th></tr></thead><tbody>
%s
</tbody></table></div>%s</details>''' % (
            " open" if nr in ("01", "02", "06") else "", html.escape(NAMEN.get(nr, slug)),
            ("%d neue Flächen aus Fotos" % nzon) if nzon else ("Fassade unverändert (keine neu messbaren Fotos)" if not m else "Farben geprüft"),
            "\n".join(zeilen), ""))
    return "\n".join(out)


def main(alt_pfad, fragment=None):
    os.makedirs(OUT, exist_ok=True)
    alt = json.load(open(alt_pfad))
    neu = json.load(open(os.path.join(G.HERE, "data", "farben.json")))
    messung = json.load(open(FM.MESSUNG))
    kat = R.lade_katalog()["fotos"]
    base = os.path.dirname(os.path.abspath(alt_pfad))
    for src, dst in ((os.path.join(base, "vorschau_laserscan", "1zu1500", "komplett_campus_mit_extras_farbig_ost.png"), "gesamt_alt.png"),
                     (os.path.join(G.HERE, "vorschau", "laserscan", "1zu1500", "komplett_campus_mit_extras_farbig_ost.png"), "gesamt_neu.png"),
                     (os.path.join(base, "vorschau_laserscan", "einzelgebaeude_farbig_1zu1000.png"), "einzel_alt.png"),
                     (os.path.join(G.HERE, "vorschau", "laserscan", "einzelgebaeude_farbig_1zu1000.png"), "einzel_neu.png")):
        shutil.copy(src, os.path.join(OUT, dst))
    kons, res = FM.messen_konsens()
    sc = FM.Szene()
    n_zellen = len(kons["b"])
    n_licht = int((kons["n_licht"] > 0).sum())
    ids = ["fl_25383321126", "fl_16905251612", "fl_24782688903", "fl_25292032932", "fl_25409407395", "fl_16719063090",
           "fl_13957964694", "fl_25291096262", "fl_9656690560"]
    verw = [i for i, e in kat.items() if e.get("geprueft")]
    foto_tab = []
    for i in verw:
        e, info = kat[i], messung["fotos"][i]
        kp = info.get("kreuzpruefung") or {}
        foto_tab.append('<tr><td><a href="%s">%s</a></td><td>%s</td><td>%s</td><td class="nowrap">%s</td><td class="num">%s</td><td class="num">%s</td><td class="num">%s</td><td class="num">%s</td></tr>' % (
            html.escape(e["seite"]), html.escape(e.get("titel") or i), html.escape(e["urheber"]), html.escape(e["lizenz"]),
            html.escape((e.get("zeit") or "")[:10]), "bedeckt" if e.get("bedeckt") else ("%.0f°" % info["sonne"] if info.get("sonne") is not None else "–"),
            "%d" % info["zellen"], ("%d %% · ΔE %.0f" % (round(100 * kp["rel_hell"]), kp["de"])) if kp else "–",
            "%.2f" % info.get("gewicht", 1.0)))
    n_aug = sum(1 for z in messung["gebaeude"]["02_neues_augusteum"]["bericht"]["zonen"] if z["neu"])
    st = dict(
        n_fotos=len(verw), n_zellen=n_zellen, n_licht=n_licht, n_aug_zonen=n_aug,
        gebaeude_html=gebaeude_tabellen(alt, neu, messung), fotos_html=foto_zeilen(kat, messung, ids), foto_tab="\n".join(foto_tab))
    tpl = Template(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "bericht_vorlage.html")).read())
    text = tpl.safe_substitute(st)
    head, body = text.split("<!--BODY-->")
    with open(os.path.join(OUT, "index.html"), "w") as f:      # eigenständige Seite
        f.write('<!doctype html>\n<html lang="de"><head><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width, initial-scale=1">\n' + head +
                '<style>:root{color-scheme:light}body{margin:0}img{max-width:100%}</style></head>\n<body>' + body + '</body></html>\n')
    if fragment:                                                # Fassung für die Artifact-Veröffentlichung
        with open(fragment, "w") as f:
            f.write(head + body)
    print("->", os.path.relpath(os.path.join(OUT, "index.html"), G.HERE))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
