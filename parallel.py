"""Kleine Parallel-Hilfe: Aufgaben auf alle Kerne verteilen (fork), Ausgaben in Reihenfolge.

    results = parallel.starmap(func, [(arg1, arg2), ...])

Jeder Aufruf läuft in einem Kindprozess; seine print-Ausgaben werden eingesammelt und
in Aufgabenreihenfolge ausgegeben, damit das Protokoll lesbar bleibt. Argumente und
Ergebnisse müssen sich pickeln lassen (also keine Manifold-Objekte zurückgeben).
Anzahl Prozesse: parallel.JOBS (Standard: Kerne; `generate.py --jobs 1` = seriell).
"""
import contextlib
import io
import multiprocessing as mp
import os
import sys
import time

JOBS = os.cpu_count() or 1


def _run(job):
    func, args = job
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        res = func(*args)
    return res, buf.getvalue()


def starmap(func, arglist):
    arglist = list(arglist)
    if JOBS <= 1 or len(arglist) <= 1:
        return [func(*a) for a in arglist]
    # Aufgaben einzeln verteilen: die Laufzeiten sind sehr verschieden. ProcessPoolExecutor statt Pool: Stirbt ein Prozess
    # (z. B. Speichermangel, OOM), bricht der Lauf mit BrokenProcessPool ab, statt ewig auf das verlorene Ergebnis zu warten.
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(min(JOBS, len(arglist)), mp_context=mp.get_context("fork")) as ex:
        out = list(ex.map(_run, [(func, a) for a in arglist], chunksize=1))
    for _, text in out:
        sys.stdout.write(text)
    return [r for r, _ in out]


TIMES = {}


@contextlib.contextmanager
def phase(name):
    """Wanduhrzeit einer Phase mitschreiben (Summe bei Wiederholung), siehe report()."""
    t = time.perf_counter()
    try:
        yield
    finally:
        TIMES[name] = TIMES.get(name, 0.0) + time.perf_counter() - t


def report():
    total = sum(TIMES.values())
    print("\nLaufzeit je Phase (%d Prozesse):" % JOBS)
    for k, v in TIMES.items():
        print("  %-34s %7.1f s  %4.1f %%" % (k, v, 100 * v / max(total, 1e-9)))
    print("  %-34s %7.1f s" % ("gesamt", total))
