#!/usr/bin/env python3
"""Erzeugt alles neu: Generatoren, Ansichten und Passprobe-Seite.

Reihenfolge:
  1. python3 -m plug.dupont                     (Platte, Deckel, Würfel usw. + plug/views/dupont/data.json)
  2. python3 -m plug.institute                  (Institutsgebäude mit Kassette, ca. 45 s; entfällt mit --skip-institute)
  3. python3 -m plug.sample                     (Probestück + Passprobe-STL, README.txt, ZIP)
  4. python3 -m plug.views.build_views dupont   (und institute, wenn nicht übersprungen)
  5. python3 -m plug.fit_test.build_page        (Anleitung der Passprobe)
Bei einem Fehler (Exit-Code ≠ 0) wird sofort abgebrochen. Die Prüfung der Ausgabe (dicht, Kollisionen) macht
`python3 -m plug.check`; hier werden nur Fehler der Skripte selbst gemeldet.

Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m plug.build_all [--skip-institute]
"""
import argparse
import sys

from plug.check import run_module


def steps(skip_institute=False):
    s = [("plug.dupont", ())]
    if not skip_institute:
        s.append(("plug.institute", ()))
    s.append(("plug.sample", ()))
    s.append(("plug.views.build_views", ("dupont",)))
    if not skip_institute:
        s.append(("plug.views.build_views", ("institute",)))
    s.append(("plug.fit_test.build_page", ()))
    return s


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--skip-institute", action="store_true", help="Institutsgebäude und seine Ansicht überspringen")
    a = ap.parse_args(argv)
    done = []
    for mod, args in steps(a.skip_institute):
        label = " ".join(["python3 -m", mod, *args])
        print("\n=== %s ===" % label, flush=True)
        res = run_module(mod, args)
        done.append((label, res["secs"], res["rc"]))
        if res["rc"] != 0:
            print("\nFEHLER: `%s` endete mit Exit-Code %d, Abbruch." % (label, res["rc"]), file=sys.stderr)
            return res["rc"]
    print("\n=== Zusammenfassung ===")
    for label, secs, rc in done:
        print("  ok  %5.0f s  %s" % (secs, label))
    print("Fertig: %d Schritte, %.0f s. Prüfen mit `python3 -m plug.check`." % (len(done), sum(d[1] for d in done)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
