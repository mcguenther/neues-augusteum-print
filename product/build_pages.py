"""Produktseite für GitHub Pages: schreibt `docs/index.html` und `docs/assets/` aus `product/`.

`product/index.html` ist ein Fragment (das Artifact-Tool ergänzt Doctype, Zeichensatz und viewport beim Veröffentlichen). Für Pages
setzt dieses Skript dieselbe Hülle davor, entfernt das Artifact-Meta und kopiert `assets/`. Die Quelle bleibt `product/index.html`;
die Kopie unter `docs/` ist erzeugt und eingecheckt. Pages: Quelle „Deploy from a branch“, Branch main, Ordner /docs.

Aufruf: `python3 -m product.build_pages` (Sekunden; vorher bei Änderungen an Gebäuden, Platte oder Sockel `python3 -m product.build_assets`).
"""
import os
import re
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "docs")

# wie die Hülle des Artifact-Tools: heller Standard, kein Seitenrand, Bilder nie breiter als die Spalte, [hidden] gilt
RESET = ("<style>:root{color-scheme:light}body{margin:0;font:14px system-ui,sans-serif}img{max-width:100%}"
         "[hidden]{display:none!important}</style>\n")


def main():
    src = open(os.path.join(HERE, "index.html"), encoding="utf-8").read()
    src = re.sub(r'<meta name="claude:[^>]*>\n', "", src)
    cut = src.index("</style>") + len("</style>")
    head, body = src[:cut], src[cut:]
    head = re.sub(r"(<title>)", RESET + r"\1", head, count=1)
    html = ('<!doctype html>\n<html lang="de">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            + head + "\n</head>\n<body>" + body.rstrip() + "\n</body>\n</html>\n")
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(html)
    dst = os.path.join(OUT, "assets")
    shutil.rmtree(dst, ignore_errors=True)
    shutil.copytree(os.path.join(HERE, "assets"), dst)
    open(os.path.join(OUT, ".nojekyll"), "w").close()
    size = os.path.getsize(os.path.join(OUT, "index.html")) + sum(os.path.getsize(os.path.join(dst, f)) for f in os.listdir(dst))
    print("docs/: index.html und assets/, %.2f MB; docs/.nojekyll" % (size / 1e6))


if __name__ == "__main__":
    main()
