#!/usr/bin/env python3
"""HTML-Bericht „Farbvergleich Runde 2“: Stand vor und nach neuen Fotos, mit 3D-Modell, Fotovergleichen und Tabellen.

    python3 werkzeuge/farbmessung/bericht_runde2.py <vorherige farben.json> [--ausgabe ordner] [--fragment datei]
                                                  [--stand TT.MM.JJJJ]

Voraussetzungen
  - <vorherige farben.json> und data/messung.json aus dem vorherigen Stand liegen im selben Ordner (so sichert man sie:
    git show <commit>:data/farben.json), dazu vorschau_laserscan/ mit dem Gesamtmodell des vorherigen Standes
    (1zu1500/komplett_campus_mit_extras_farbig_ost.png und einzelgebaeude_farbig_1zu1000.png).
  - Der neue Stand ist data/farben.json, data/messung.json, data/messfotos.json und vorschau/laserscan/ (generate.py).
  - Bilder der neuen Fotos: vergleich_bilder.py <vorherige farben.json> <ausgabe> --fotos id,id,…
Standard-Ausgabe: vorschau/farbvergleich_runde2/index.html (eigenständige Seite). Mit --fragment entsteht zusätzlich
eine Fassung ohne Kopf für die Veröffentlichung als Artifact.
"""
import argparse
import html
import json
import os
import shutil
import sys
from string import Template

from PIL import Image

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HIER, "..", ".."))
import bericht as B
import farbmessung as FM
import generate as G
import modell_export as ME
import registrierung as R

OUT = os.path.join(G.HERE, "vorschau", "farbvergleich_runde2")
SEITE = {"N": "Nord", "O": "Ost", "S": "Süd", "W": "West"}

ZUSATZ_CSS = """
.zahlen { display: grid; grid-template-columns: repeat(auto-fit, minmax(11rem, 1fr)); gap: 0.75rem; }
.zahl { background: var(--surface); border: 1px solid var(--line); border-radius: 0.5rem; padding: 0.8rem 1rem; display: grid; gap: 0.15rem; align-content: start; }
.zahl .was { font-family: var(--font-mono); font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--muted); }
.zahl .wert { font-family: var(--font-display); font-weight: 700; font-size: 1.7rem; line-height: 1.15; font-variant-numeric: tabular-nums; }
.zahl .wert .alt { color: var(--alt); font-weight: 500; }
.zahl .wert .pfeil { color: var(--muted); font-weight: 400; padding-inline: 0.25rem; }
.zahl .wert .neu { color: var(--neu); }
.zahl .note { font-size: 0.85rem; color: var(--muted); }
.seite { padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); }
.cmp .tag { top: auto; bottom: 0.6rem; }
.neumarke { font-family: var(--font-mono); font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.06em; background: var(--neu-soft); color: var(--neu); padding: 0.05rem 0.35rem; border-radius: 0.25rem; margin-left: 0.4rem; }
.befund ul { margin: 0; padding-left: 1.1rem; font-size: 0.93rem; color: var(--muted); display: grid; gap: 0.2rem; }
"""


def stil():
    """CSS der ersten Berichtsvorlage plus Betrachter und Kennzahlen."""
    t = open(os.path.join(HIER, "bericht_vorlage.html")).read()
    css = t[t.index("<style>") + 7:t.index("</style>")]
    viewer = open(os.path.join(HIER, "viewer.css")).read()
    return css + viewer + ZUSATZ_CSS


def lade(pfad):
    return json.load(open(pfad))


def groesse(pfad):
    return Image.open(pfad).size


def kopieren(quellen, ziel):
    for src, name in quellen:
        shutil.copy(src, os.path.join(ziel, name))


def nur_geprueft(kat):
    return [i for i, e in kat.items() if e.get("geprueft")]


def farb_aenderungen(alt, neu):
    """{slug: [(schluessel, alt, neu, de)]} für alle Farben, deren Wert sich geändert hat (ΔE > 1)."""
    out = {}
    for slug, e in neu.items():
        if slug.startswith("_") or slug not in alt:
            continue
        for k, f in e["farben"].items():
            a = alt[slug]["farben"].get(k, {}).get("rgb")
            if a and a.lower() != f["rgb"].lower():
                d = FM.de(FM.lin_hex(a), FM.lin_hex(f["rgb"]))
                if d > 1.0:
                    out.setdefault(slug, []).append((k, a, f["rgb"], d))
    return out


def zonen_neu(messung, slug):
    m = messung["gebaeude"].get(slug)
    return sum(1 for z in m["bericht"]["zonen"] if z["neu"]) if m else 0


def mit_ergebnis(m):
    """Zahl der Gebäude, bei denen die Fotos eine Farbe oder eine Zone neu bestimmt haben."""
    return sum(1 for s, g in m["gebaeude"].items()
               if zonen_neu(m, s) or any(v["gemessen"] for v in g["bericht"]["farben"].values()))


def kennzahlen(alt_ids, neu_ids, kons_alt, kons_neu, m_alt, m_neu):
    def licht(k):
        return int((k["n_licht"] > 0).sum())
    z_alt = sum(zonen_neu(m_alt, s) for s in m_alt["gebaeude"])
    z_neu = sum(zonen_neu(m_neu, s) for s in m_neu["gebaeude"])
    return [
        ("Fotos", len(alt_ids), len(neu_ids), "am Modell ausgerichtet und geprüft"),
        ("Zellen mit Messung", len(kons_alt["b"]), len(kons_neu["b"]), "Wandzellen à 1 m × 1 m"),
        ("davon besonnt", licht(kons_alt), licht(kons_neu), "mindestens eine Messung mit Sonne"),
        ("Gebäude mit Messergebnis", mit_ergebnis(m_alt), mit_ergebnis(m_neu), "neue Farbe oder Zone aus Fotos, von sieben"),
        ("Zonen aus Fotos", z_alt, z_neu, "Farbflächen über den Handzonen"),
    ]


def zahlen_html(rows):
    out = []
    for was, a, n, note in rows:
        out.append('<div class="zahl"><span class="was">%s</span><span class="wert"><span class="alt">%s</span>'
                   '<span class="pfeil">→</span><span class="neu">%s</span></span><span class="note">%s</span></div>'
                   % (html.escape(was), "{:,}".format(a).replace(",", "."), "{:,}".format(n).replace(",", "."), html.escape(note)))
    return "\n".join(out)


def befunde_html(alt, neu, m_alt, m_neu, texte):
    """Karten: je Gebäude mit Änderungen eine Karte aus den Daten, davor Karten mit von Hand geschriebenem Text."""
    karten = ['<div><span class="marke %s">%s</span><h3>%s</h3><p>%s</p></div>' % (c, html.escape(m), html.escape(t), html.escape(p))
              for c, m, t, p in texte]
    aend = farb_aenderungen(alt, neu)
    for b in G.OBJEKTE:
        slug = b["slug"]
        if slug not in neu:
            continue
        nr = slug[:2]
        name = B.NAMEN.get(nr, slug)
        za, zn = zonen_neu(m_alt, slug), zonen_neu(m_neu, slug)
        l = aend.get(slug, [])
        gemessen_alt = slug in m_alt["gebaeude"]
        gemessen_neu = slug in m_neu["gebaeude"]
        behalten = [B.FARBNAMEN.get(k, "Fläche " + k) for k, f in neu[slug]["farben"].items() if "beibehalten" in f.get("quelle", "")]
        if not l and za == zn and not behalten and gemessen_alt == gemessen_neu:
            karten.append('<div><span class="marke alt">gleich</span><h3>%s</h3><p>Keine Änderung an Farben und Zonen.</p></div>'
                          % html.escape(name))
            continue
        pkt = []
        for k, a, n_, d in sorted(l, key=lambda x: -x[3])[:4]:
            pkt.append('<li>%s <span style="white-space:nowrap">%s <code>%s</code> → %s <code>%s</code></span> (ΔE %.0f)</li>' % (
                html.escape(B.FARBNAMEN.get(k, "Fläche " + k)), B.swatch(a, "alt"), a, B.swatch(n_, "neu"), n_, d))
        kopf = []
        if not gemessen_alt and gemessen_neu and not behalten:
            kopf.append("Neu gemessen (vorher keine Fotos mit Sonne).")
        if behalten:
            kopf.append("Von Hand beibehalten (Messung war grauer): %s." % ", ".join(behalten))
        if zn != za:
            kopf.append("Zonen aus Fotos: %d → %d." % (za, zn))
        if l:
            kopf.append("%d Farbe%s geändert." % (len(l), "n" if len(l) > 1 else ""))
        karten.append('<div><span class="marke %s">%s</span><h3>%s</h3><p>%s</p><ul>%s</ul></div>' % (
            "neu" if (l or zn != za) else "alt", "geändert" if (l or zn != za) else "beibehalten", html.escape(name),
            html.escape(" ".join(kopf)), "".join(pkt)))
    return "\n".join(karten)


def foto_karten(kat, messung, ids):
    out = []
    for fid in ids:
        e, info = kat[fid], messung["fotos"][fid]
        zeit = (e.get("zeit") or "")[:16].replace("T", " ")
        sonne = "bedeckt" if e.get("bedeckt") else ("Sonne %.0f° über dem Horizont" % info["sonne"] if info.get("sonne") is not None else "")
        gebs = ", ".join(B.NAMEN.get(g, g).split(" (")[0].split(" /")[0] for g in e.get("gebaeude", []))
        out.append('''<article class="vergleich">
  <header><h3>%s</h3><p>%s · %s · %s</p></header>
  <div class="drei">
    <figure><img src="%s_foto.jpg" alt="Foto"><figcaption>Foto</figcaption></figure>
    <figure><img src="%s_alt.jpg" alt="Modell, Farben vorher"><figcaption>Modell vorher</figcaption></figure>
    <figure><img src="%s_neu.jpg" alt="Modell, Farben nachher"><figcaption>Modell nachher</figcaption></figure>
  </div>
  <p class="quelle">%s · %s · <a href="%s">Quelle</a> · Überlagerung der Ausrichtung: <a href="%s_pose.jpg">Bild</a></p>
</article>''' % (html.escape(e.get("titel") or fid), html.escape(zeit), html.escape(sonne), html.escape(gebs), fid, fid, fid,
                 html.escape(e["urheber"]), html.escape(e["lizenz"]), html.escape(e["seite"]), fid))
    return "\n".join(out)


def foto_tabelle(kat, messung, alt_ids):
    zeilen = []
    for i, info in sorted(messung["fotos"].items(), key=lambda kv: ((kat[kv[0]].get("zeit") or "")[:4], kv[0])):
        e = kat[i]
        kp = info.get("kreuzpruefung") or {}
        neu = "" if i in alt_ids else '<span class="neumarke">neu</span>'
        zeilen.append('<tr><td><a href="%s">%s</a>%s</td><td>%s</td><td>%s</td><td class="nowrap">%s</td><td class="num">%s</td>'
                      '<td class="num">%s</td><td class="num">%s</td><td class="num">%s</td></tr>' % (
                          html.escape(e["seite"]), html.escape(e.get("titel") or i), neu, html.escape(e["urheber"]),
                          html.escape(e["lizenz"]), html.escape((e.get("zeit") or "")[:10]),
                          "bedeckt" if e.get("bedeckt") else ("%.0f°" % info["sonne"] if info.get("sonne") is not None else "–"),
                          "%d" % info["zellen"],
                          ("%d %% · ΔE %.0f" % (round(100 * kp["rel_hell"]), kp["de"])) if kp else "–", "%.2f" % info.get("gewicht", 1.0)))
    return "\n".join(zeilen)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("alt_farben")
    ap.add_argument("--ausgabe", default=OUT)
    ap.add_argument("--fragment")
    ap.add_argument("--stand", default="")
    ap.add_argument("--texte", default=os.path.join(HIER, "bericht_runde2_texte.json"),
                    help="JSON mit den von Hand geschriebenen Textblöcken")
    a = ap.parse_args()
    out = a.ausgabe
    os.makedirs(out, exist_ok=True)
    base = os.path.dirname(os.path.abspath(a.alt_farben))
    alt = lade(a.alt_farben)
    neu = lade(os.path.join(G.HERE, "data", "farben.json"))
    m_alt = lade(os.path.join(base, "messung.json"))
    m_neu = lade(FM.MESSUNG)
    kat = R.lade_katalog()["fotos"]
    texte = lade(a.texte)
    alt_ids = list(m_alt["fotos"])
    neu_ids = nur_geprueft(kat)
    neue = [i for i in neu_ids if i not in alt_ids]

    # Bilder: Gesamtmodell vorher/nachher
    kopieren([(os.path.join(base, "vorschau_laserscan", "1zu1500", "komplett_campus_mit_extras_farbig_ost.png"), "gesamt_vorher.png"),
              (os.path.join(G.HERE, "vorschau", "laserscan", "1zu1500", "komplett_campus_mit_extras_farbig_ost.png"), "gesamt_nachher.png"),
              (os.path.join(base, "vorschau_laserscan", "einzelgebaeude_farbig_1zu1000.png"), "einzel_vorher.png"),
              (os.path.join(G.HERE, "vorschau", "laserscan", "einzelgebaeude_farbig_1zu1000.png"), "einzel_nachher.png")], out)
    gw, gh = groesse(os.path.join(out, "gesamt_nachher.png"))
    ew, eh = groesse(os.path.join(out, "einzel_nachher.png"))

    # Kennzahlen aus den Konsens-Zellen (alte Fotos: gleiche Posen, daher dasselbe Ergebnis wie damals)
    kons_neu, _ = FM.messen_konsens()
    kons_alt, _ = FM.messen_konsens(nur=alt_ids)
    zahlen = kennzahlen(alt_ids, neu_ids, kons_alt, kons_neu, m_alt, m_neu)

    # 3D-Modell
    modell_pfad = os.path.join(out, "modell.json")
    ME.export(a.alt_farben, modell_pfad)
    modell = open(modell_pfad).read()
    os.remove(modell_pfad)

    st = dict(
        css=stil(), stand=a.stand, n_neu=len(neue), n_fotos=len(neu_ids), n_alt=len(alt_ids),
        kopf_satz=texte["kopf_satz"], zahlen_html=zahlen_html(zahlen),
        befunde_html=befunde_html(alt, neu, m_alt, m_neu, texte["befunde"]),
        viewer_html=open(os.path.join(HIER, "viewer.html")).read(), viewer_js=open(os.path.join(HIER, "viewer.js")).read(),
        modell_json=modell, gesamt_w=gw, gesamt_h=gh, einzel_w=ew, einzel_h=eh,
        fotos_hinweis=texte["fotos_hinweis"], fotos_html=foto_karten(kat, m_neu, [i for i in neue if i in texte["zeigen"]]),
        gebaeude_html=B.gebaeude_tabellen(alt, neu, m_neu), pruefung_text=texte["pruefung"], foto_tab=foto_tabelle(kat, m_neu, alt_ids),
        quellen_html=texte["quellen"], grenzen_html=texte["grenzen"])
    tpl = Template(open(os.path.join(HIER, "bericht_runde2_vorlage.html")).read())
    text = tpl.safe_substitute(st)
    head, body = text.split("<!--BODY-->")
    with open(os.path.join(out, "index.html"), "w") as f:
        f.write('<!doctype html>\n<html lang="de"><head><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width, initial-scale=1">\n' + head +
                '<style>:root{color-scheme:light}body{margin:0}img{max-width:100%}</style></head>\n<body>' + body + '</body></html>\n')
    if a.fragment:
        with open(a.fragment, "w") as f:
            f.write(head + body)
    print("->", os.path.relpath(os.path.join(out, "index.html"), G.HERE), "(%d neue Fotos)" % len(neue))


if __name__ == "__main__":
    main()
