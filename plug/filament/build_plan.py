#!/usr/bin/env python3
"""Planseite „Passungsplan Filamente“: plug/filament/plan.html (Vorlage plan.template.html).

Zeigt, was in Schwarz bewährt ist, warum beige Teile klemmen (Spiel minus Aufmaß, Regler), Kassette im Schacht, Fase und Reibung, Treffen der Stifte,
die vier Testteile (Mulden-Block T1 mit dem echten Umriss des Institutsgebäudes, Kassettenserie T2, Stumpf T3, Messplättchen T4) und die
Entscheidungskarten. Keine STL: der Plan wird erst abgenickt (plug/logbook/README.md).

Aufruf (aus dem Wurzelverzeichnis, ca. 10 s):
    python3 -m plug.filament.build_plan
"""
import os

from shapely.geometry import box

from plug.filament import geom as FG

HERE = os.path.dirname(os.path.abspath(__file__))
SPIELE = (0.10, 0.15, 0.20)          # T1: Spiel je Seite
LEIT = "05_institutsgebaeude"


def de(v, nd=1):
    return ("%.*f" % (nd, v)).replace(".", ",")


def umrisse_svg(u):
    zellen = [("03_hoersaalgebaeude", 0, 0), ("05_institutsgebaeude", 1, 0), ("04_seminargebaeude", 2, 0),
              ("02_neues_augusteum", 0, 1), ("01_paulinum", 1, 1), ("06_city_hochhaus", 2, 1)]
    cw, ch = 118.0, 82.0
    out = []
    for slug, cx, cy in zellen:
        d = u[slug]
        w, h = d["laenge"], d["breite"]
        ox, oy = cx * cw + (cw - w) / 2, cy * ch + 6 + (58 - h) / 2 + h
        leit = slug == LEIT
        out.append('<path d="%s" transform="translate(%.1f %.1f)" class="s-beige" fill-rule="evenodd" stroke-width="%s" vector-effect="non-scaling-stroke" %s/>' %
                   (FG.pfad(d["poly"]), ox, oy, "2" if leit else "1", 'style="stroke:var(--accent)"' if leit else ""))
        out.append('<text x="%.1f" y="%.1f" text-anchor="middle" font-size="6.2" font-weight="600">%s%s</text>' %
                   (cx * cw + cw / 2, cy * ch + 70, FG.NAMEN[slug], " (Leitumriss)" if leit else ""))
        out.append('<text x="%.1f" y="%.1f" text-anchor="middle" font-size="5" class="mut">%s × %s mm · Umfang %d mm · Kassette %s</text>' %
                   (cx * cw + cw / 2, cy * ch + 77, de(w, 0), de(h, 0), round(d["umfang"]), FG.KASSETTE[slug]))
    return "".join(out)


def t1_svg(b):
    plat = b["platte"]
    for _, g in b["mulden"]:
        plat = plat.difference(g)
    out = ['<path d="%s" class="s-grau" fill-rule="evenodd" stroke-width="1.2" vector-effect="non-scaling-stroke"/>' % FG.pfad(plat)]
    for s, g in b["mulden"]:
        c = g.centroid
        out.append('<text x="%.1f" y="%.1f" text-anchor="middle" font-size="6" font-weight="600" class="mono">%s</text>' % (c.x, -c.y + 2, de(s, 2)))
    return "".join(out)


def t2_svg():
    k = 7.0
    out = []
    zeilen = [("V1RS 1", 0.12, "–0,06"), ("V1RS 2", 0.16, "–0,10"), ("V1RS 3", 0.20, "–0,14")]
    for i, (n, spiel, d) in enumerate(zeilen):
        w = (19.2 - 2 * (spiel - 0.06)) * k
        h = 6.4 * k
        x = 12 + (19.2 * k - w) / 2
        y = 10 + i * 52
        out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" class="s-beige" stroke-width="1.2"/>' % (x, y, w, h))
        pw, ph = 10.56 * k, 2.94 * k
        out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="var(--stage)" stroke="var(--beige-line)" stroke-width="0.8"/>' % (12 + (19.2 * k - pw) / 2, y + 1.2 * k, pw, ph))
        out.append('<text x="%d" y="%.1f" font-size="11" font-weight="600">%s</text>' % (160, y + 14, n))
        out.append('<text x="%d" y="%.1f" font-size="10" class="mut">Spiel %s, Außenmaß %s</text>' % (160, y + 29, de(spiel, 2), d))
    out.append('<text x="12" y="184" font-size="10" class="mut">dazu v4 × 2 (Spiel 0,12 und 0,16)</text>')
    return "".join(out)


def t3_svg():
    return ('<path d="M20 30 H250 V122 H56 L20 86 Z" class="s-beige" stroke-width="1.2"/>'
            '<path d="M70 30 V118 H206 V30" fill="var(--stage)" stroke="var(--beige-line)" stroke-width="1"/>'
            '<rect x="95" y="64" width="86" height="54" fill="var(--schwarz)" opacity="0.85"/>'
            '<text x="138" y="95" text-anchor="middle" font-size="10" style="fill:#fff">Kassette</text>'
            '<text x="138" y="52" text-anchor="middle" font-size="10" class="mut">Schacht</text>'
            '<line x1="262" x2="262" y1="30" y2="122" class="dim"/><text x="268" y="80" font-size="10" class="mut">≈ 20</text>'
            '<text x="20" y="144" font-size="10" class="mut">Fuß 14,2, Fase 2,0, Boden unten (Bett), Institutsumriss</text>')


def t4_svg():
    k = 3.6
    x0, y0 = 52, 14
    return ('<path d="M%d %d h%.1f v%.1f h%.1f z M%.1f %.1f h%.1f v%.1f h%.1f z" class="s-grau" fill-rule="evenodd" stroke-width="1.2"/>' %
            (x0, y0, 60 * k, 40 * k, -60 * k, x0 + 30 * k, y0 + 10 * k, 20 * k, 20 * k, -20 * k) +
            '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" class="s-grau" stroke-width="1.2"/>' % (x0 - 10 * k, y0 + 15 * k, 10 * k, 10 * k) +
            '<text x="%.1f" y="%.1f" font-size="10" text-anchor="middle" class="mut">60</text>' % (x0 + 30 * k, y0 + 40 * k + 14) +
            '<text x="%.1f" y="%.1f" font-size="10" text-anchor="middle" class="mut">Loch 20 × 20</text>' % (x0 + 40 * k, y0 + 20 * k + 3) +
            '<text x="%.1f" y="%.1f" font-size="10" class="mut">40</text>' % (x0 + 60 * k + 6, y0 + 20 * k) +
            '<text x="%.1f" y="%.1f" font-size="9" text-anchor="middle" class="mut">Nase 10</text>' % (x0 - 5 * k, y0 + 15 * k - 4))


def zeiten_ersetzen(b):
    """Zeiten aus dem Prüfbericht von plug.filament.build (Zeilen „Variante A/B“); fehlt der Bericht, bleiben Platzhalter leer."""
    import re
    f = os.path.join(FG.ROOT, "stl", "steckmodul_passung", "pruefbericht.txt")
    t = open(f, encoding="utf-8").read() if os.path.exists(f) else ""
    ma = re.search(r"Variante A .*?: (\d+) min Block \+ (\d+) min Kassetten = (\d+) min", t)
    mb = re.search(r"Variante B .*?: (\d+) min Fuß \+ (\d+) min Block \+ (\d+) min Kassetten = (\d+) min", t)
    if not (ma and mb):
        return {k: "?" for k in ("@@ZA@@", "@@ZB@@", "@@ZB1@@", "@@ZBB@@", "@@ZAB@@", "@@ZBF@@", "@@AB@@", "@@AH@@")}
    return {"@@ZA@@": ma.group(3), "@@ZB@@": mb.group(4), "@@ZB1@@": mb.group(4), "@@ZBB@@": mb.group(2),
            "@@ZAB@@": ma.group(1), "@@ZBF@@": mb.group(1), "@@AB@@": de(b["breite"], 0), "@@AH@@": de(b["hoehe"], 0)}


def main():
    u = FG.umrisse()
    b = FG.block(u[LEIT]["poly"], SPIELE, rand_l=9.6)
    s = open(os.path.join(HERE, "plan.template.html"), encoding="utf-8").read()
    rep = {"@@UMRISSE@@": umrisse_svg(u), "@@T1@@": t1_svg(b),
           "@@T1VIEW@@": "-3 %.1f %.1f %.1f" % (-b["hoehe"] - 3, b["breite"] + 6, b["hoehe"] + 6),
           "@@T1B@@": de(b["breite"]), "@@T1H@@": de(b["hoehe"]), "@@T1V@@": de(b["cm3"]), "@@T1A@@": de(b["anteil"] * 100, 0)}
    rep.update(zeiten_ersetzen(b))
    for k, v in rep.items():
        s = s.replace(k, v)
    s = s.replace('<g id="t2"></g>', '<g id="t2">%s</g>' % t2_svg()).replace('<g id="t3"></g>', '<g id="t3">%s</g>' % t3_svg()).replace('<g id="t4"></g>', '<g id="t4">%s</g>' % t4_svg())
    with open(os.path.join(HERE, "plan.html"), "w", encoding="utf-8") as f:
        f.write(s)
    print("plan.html geschrieben: %d KB; T1 %s × %s mm, %s cm³ (%s %% der Platte)" % (len(s) // 1024, de(b["breite"]), de(b["hoehe"]), de(b["cm3"]), de(b["anteil"] * 100, 0)))
    for slug, d in u.items():
        print("  %-22s %5.1f × %5.1f  Fläche %5.0f  Umfang %4.0f" % (slug, d["laenge"], d["breite"], d["flaeche"], d["umfang"]))


if __name__ == "__main__":
    main()
