#!/usr/bin/env python3
"""Prüft die Steckmechanismus-Generatoren: alle STL dicht, keine Kollisionen, kein Fehler.

Führt `python3 -m plug.dupont`, `python3 -m plug.institute` und `python3 -m plug.sample` aus (aus der Repo-Wurzel) und
wertet die Ausgabe aus:
  - jede STL-Zeile mit `dicht=` muss `dicht=True` haben,
  - je Generator mindestens einmal „keine Kollisionen“, nie „KOLLISION“ oder „Kollisionen!“,
  - Exit-Code 0 und kein Traceback.
Die Generatoren schreiben dabei ihre Dateien wie sonst auch (stl/, vorschau/, plug/build/, plug/views/dupont/data.json).
Exit-Code ≠ 0 bei einem Fehler. `run_module()` nutzen auch plug/build_all.py.

Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m plug.check [--skip-institute] [--log DATEI]
"""
import argparse
import os
import re
import subprocess
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENERATORS = ("plug.dupont", "plug.institute", "plug.sample")


def run_module(mod, args=(), echo=True):
    """Führt `python3 -m mod [args]` aus der Repo-Wurzel aus und liest die Ausgabe (stdout + stderr) zeilenweise.
    Gibt ein dict zurück: mod, rc, secs, lines (Liste der Ausgabezeilen); mit echo=True wird die Ausgabe live gezeigt."""
    t0 = time.time()
    env = dict(os.environ, PYTHONUNBUFFERED="1")
    p = subprocess.Popen([sys.executable, "-m", mod, *args], cwd=REPO, env=env, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
    lines = []
    for line in p.stdout:
        line = line.rstrip("\n")
        lines.append(line)
        if echo:
            print(line, flush=True)
    rc = p.wait()
    return dict(mod=mod, rc=rc, secs=time.time() - t0, lines=lines)


def evaluate(res):
    """Wertet die Ausgabe eines Generators aus. Ergänzt res um stl, dicht_ok, koll_ok, errors (Liste von Meldungen)."""
    lines = res["lines"]
    stl = [l for l in lines if "dicht=" in l]
    open_ = [l.strip() for l in stl if not re.search(r"dicht=True\b", l)]
    clear = sum("keine Kollisionen" in l for l in lines)
    hits = [l.strip() for l in lines if "KOLLISION" in l or "Kollisionen!" in l]
    trace = any(l.startswith("Traceback (most recent call last)") for l in lines)
    errors = []
    if res["rc"] != 0:
        errors.append("Exit-Code %d" % res["rc"])
    if trace:
        errors.append("Traceback in der Ausgabe")
    if not stl:
        errors.append("keine STL-Zeilen mit dicht= gefunden")
    errors += ["nicht dicht: %s" % l for l in open_]
    if not clear:
        errors.append("„keine Kollisionen“ fehlt")
    errors += ["Kollision: %s" % l for l in hits]
    res.update(stl=len(stl), dicht_ok=bool(stl) and not open_, koll_ok=bool(clear) and not hits, errors=errors)
    return res


def table(results):
    rows = [("Generator", "Dauer", "STL-Zeilen", "dicht ok", "Kollisionen ok", "Ergebnis")]
    for r in results:
        rows.append((r["mod"], "%.0f s" % r["secs"], str(r["stl"]), "ja" if r["dicht_ok"] else "NEIN",
                     "ja" if r["koll_ok"] else "NEIN", "ok" if not r["errors"] else "FEHLER"))
    w = [max(len(row[i]) for row in rows) for i in range(len(rows[0]))]
    out = []
    for i, row in enumerate(rows):
        out.append("  ".join(c.ljust(w[j]) for j, c in enumerate(row)))
        if i == 0:
            out.append("  ".join("-" * x for x in w))
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--skip-institute", action="store_true", help="Institutsgebäude (ca. 45 s) überspringen")
    ap.add_argument("--log", metavar="DATEI", help="gesamte Ausgabe zusätzlich in diese Datei schreiben")
    a = ap.parse_args(argv)
    mods = [m for m in GENERATORS if not (a.skip_institute and m == "plug.institute")]
    results = []
    for m in mods:
        print("\n=== python3 -m %s ===" % m, flush=True)
        results.append(evaluate(run_module(m)))
    summary = "\n=== Ergebnis ===\n" + table(results)
    bad = [(r["mod"], e) for r in results for e in r["errors"]]
    for mod, e in bad:
        summary += "\n  %s: %s" % (mod, e)
    summary += "\n%s" % ("Alles in Ordnung." if not bad else "FEHLER: %d Meldung(en)." % len(bad))
    print(summary)
    if a.log:
        with open(a.log, "w", encoding="utf-8") as f:
            for r in results:
                f.write("=== python3 -m %s ===\n" % r["mod"])
                f.write("\n".join(r["lines"]) + "\n\n")
            f.write(summary + "\n")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
