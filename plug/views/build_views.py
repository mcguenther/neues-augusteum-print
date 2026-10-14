#!/usr/bin/env python3
"""Baut die 3D-Ansichten (HTML-Seiten) aus Vorlage und Daten.

Die Generatoren schreiben die Daten (Geometrie als Zahlen, Maße, Tabellen) als data.json; hier wird sie in die Vorlage
(Platzhalter /*DATA*/) eingesetzt.

    dupont     plug/views/dupont/view.template.html + plug/views/dupont/data.json  ->  plug/views/dupont/view.html
    institute  plug/views/institute/view.template.html + plug/build/institute/data.json  ->  plug/build/institute/view.html
               (groß, gitignoriert; data.json erzeugt `python3 -m plug.institute`)

Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m plug.views.build_views [dupont|institute|all]     # Standard: all
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))                 # plug/views
PLUG = os.path.dirname(HERE)
REPO = os.path.dirname(PLUG)

VIEWS = {
    "dupont": dict(
        template=os.path.join(HERE, "dupont", "view.template.html"),
        data=os.path.join(HERE, "dupont", "data.json"),
        out=os.path.join(HERE, "dupont", "view.html"),
        hint="python3 -m plug.dupont"),
    "institute": dict(
        template=os.path.join(HERE, "institute", "view.template.html"),
        data=os.path.join(PLUG, "build", "institute", "data.json"),
        out=os.path.join(PLUG, "build", "institute", "view.html"),
        hint="python3 -m plug.institute"),
}


def build(name):
    """Setzt data.json in die Vorlage ein und schreibt view.html. Gibt den Pfad der Seite zurück."""
    v = VIEWS[name]
    for key in ("template", "data"):
        if not os.path.exists(v[key]):
            raise SystemExit("%s fehlt (%s)%s" % (os.path.relpath(v[key], REPO), name,
                                                 ": zuerst `%s` ausführen" % v["hint"] if key == "data" else ""))
    with open(v["template"], encoding="utf-8") as f:
        tpl = f.read()
    with open(v["data"], encoding="utf-8") as f:
        data = f.read()
    if "/*DATA*/" not in tpl:
        raise SystemExit("%s enthält keinen Platzhalter /*DATA*/" % os.path.relpath(v["template"], REPO))
    out = tpl.replace("/*DATA*/", data)
    os.makedirs(os.path.dirname(v["out"]), exist_ok=True)
    with open(v["out"], "w", encoding="utf-8") as f:
        f.write(out)
    print("%s  %.0f kB" % (os.path.relpath(v["out"], REPO), len(out.encode()) / 1024))
    return v["out"]


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    what = argv[0] if argv else "all"
    if what not in ("all", *VIEWS):
        raise SystemExit("Aufruf: python3 -m plug.views.build_views [dupont|institute|all]")
    for name in (VIEWS if what == "all" else [what]):
        build(name)


if __name__ == "__main__":
    main()
