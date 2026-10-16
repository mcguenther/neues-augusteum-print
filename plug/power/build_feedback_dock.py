#!/usr/bin/env python3
"""Testbogen zum Test-Dock (flache Unterseite): plug/power/feedback_dock.html.

Gleiche Seitenform und Formularlogik wie die Testbögen Steckprobe 2 und Fachprobe (plug/testcase/feedback2.template.html, Schritte über
plug/testcase/build_feedback2.py). Nur fühlbare oder ja/nein-Felder (Logbuch Regel 7); Kleber, Füße-Satz und ZIP-Version stehen im Ergebnistext.
    python3 -m plug.power.build_feedback_dock
"""
import json
import os

from plug.feedback.build import R_FIT, R_YN, fld, opts
from plug.feedback.build_night2 import GOOD3
from plug.testcase import build_feedback2 as BF

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(HERE, "feedback_dock.html")
PREV = os.path.join(ROOT, "vorschau", "steckmodul_testdock")


def steps():
    BF.STEPS.clear()
    add = BF.add
    add("a", "Aufbau ansehen (vor dem Druck)", "0", "Was gedruckt wird: eine Mini-Oberplatte mit flacher Unterseite und zwei Sätze Füße.",
        ["Oben die Teile in Druckausrichtung, darunter der Schnitt: Gebäude in der Mulde, die Leiste (dunkel) unter der Platte, der Draht (rot) und der Tisch.",
         "Der Körper der Leiste liegt flach an der Unterseite und wird aufgeklebt. Es gibt keine Tasche, keine Stufe, keine Nische und keinen Support.",
         "Die Platte steht auf Füßen mit 3,5 mm (eine Kerbe) oder 2,5 mm (zwei Kerben) Höhe; der Tisch steht für die Oberkante der Powerbank."],
        [("img", PREV + "/teile.png", "Platte (hellblau) und die zwei Sätze Füße."),
         ("img", PREV + "/schnitt.png", "Schnitt durch die Pin-Reihe: Gebäude und Kassette in der Mulde, Leiste unter der Platte, Draht rot, Tisch hellgrau.")],
        [fld("a-ok", "So drucken?", "select", opts([("", "– bitte wählen –"), ("a", "ja, so drucken"), ("b", "ja, aber mit Anmerkung (Freitext)"), ("c", "nein, vorher ändern (Freitext)")]))],
        optional=True)
    add("p", "Vorbereiten", "1", "Alles hinlegen. Messen musst du nichts.",
        ["Bereitlegen: <b>Platte</b> (<code>D_platte</code>), die <b>Füße</b> (3,5 und 2,5), das <b>Mini-Gebäude</b> mit eingepresster Kassette und Buchse aus Steckprobe 2, die <b>Winkelleiste</b>.",
         "Dazu <b>Sekundenkleber</b>, <b>Heißkleber</b>, etwas <b>Draht</b> samt Lötkolben und ein Multimeter."],
        [("img", PREV + "/teile.png", "Die gedruckten Teile.")],
        [fld("p-zip", "Welche ZIP wurde gedruckt (Datum oder Dateiname)?", "text", ph="z. B. testdock.zip von heute"),
         fld("p-glue", "Kleber vorhanden: Sekundenkleber und Heißkleber?", "select", opts([("", "– bitte wählen –"), ("a", "beides"), ("b", "nur Sekundenkleber"), ("c", "nur Heißkleber")])),
         fld("p-sold", "Draht und Lötkolben vorhanden?", "select", R_YN("ja", "nein")),
         fld("p-mm", "Multimeter mit Durchgangsprüfung vorhanden?", "select", R_YN("ja", "nein"))])
    add("q", "Druckqualität ansehen", "2", "Bevor etwas geklebt oder gesteckt wird: die Platte kurz prüfen.",
        ["Platte von unten ansehen: Die Unterseite soll flach und glatt sein, ohne Wulst am Rand (Fase 0,5).",
         "Die <b>vier Pin-Löcher</b> in der Mulde und in der Unterseite: offen? Mit einer Nadel durchstechen. Der Muldenboden ist nur 0,4 mm dick.",
         "Die vier <b>Zapfenlöcher</b> (außerhalb der Mulde) und die Füße ansehen."],
        [],
        [fld("q-all", "Welche Dateien wurden gedruckt?", "text", ph="z. B. Platte und beide Füße-Sätze"),
         fld("q-flat", "Unterseite der Platte", "select", GOOD3("flach, glatt", "leichter Wulst am Rand", "wellig oder verzogen")),
         fld("q-holes", "Vier Pin-Löcher durchstechen", "select", GOOD3("alle offen", "eines oder zwei zu, mit Nadel frei", "mehrere zu")),
         fld("q-floor", "Muldenboden (oben, 0,4 mm)", "select", GOOD3("glatt, ohne Löcher", "kleine Mängel", "durchgehängt oder gerissen")),
         fld("q-feet", "Füße und Zapfenlöcher", "select", GOOD3("sauber", "leichte Mängel, stört nicht", "Zapfen abgebrochen")),
         fld("q-time", "Druckzeit insgesamt in Stunden", "text", ph="z. B. 0,5"),
         fld("q-fil", "Drucker und Filament", "text", ph="z. B. Bambu A1, PLA schwarz")])
    add("K", "Leiste ankleben", "K", "Winkelleiste von unten durch die Pin-Löcher stecken und mit Sekundenkleber an die flache Unterseite kleben.",
        ["Die Winkelleiste mit den vier senkrechten Pins von unten in die Löcher stecken. Gehen sie leicht durch?",
         "Den Körper flach an die Plattenunterseite drücken und mit einem Tropfen <b>Sekundenkleber</b> festkleben. Nur den Körper, nicht die Pins. Mit dem Finger kurz andrücken.",
         "Die Leiste von der Seite ansehen: liegt der Körper flach an? Stehen die Pins gerade nach oben?"],
        [("img", PREV + "/unterseite.png", "Platte von unten: links schräg, rechts senkrecht, mit Leiste (dunkel), Draht (rot) und einem Fuß.")],
        [fld("K-pins", "Pins durch die Löcher", "select", GOOD3("gehen leicht durch", "mit Mühe", "gehen nicht durch")),
         fld("K-flat", "Körper liegt an der Unterseite", "select", GOOD3("flach, kein Spalt", "kleiner Spalt", "steht schief ab")),
         fld("K-str", "Pins stehen", "select", GOOD3("gerade und mittig in den Löchern", "leicht schief", "deutlich schief")),
         fld("K-align", "Lage der Leiste (Ausrichtung ohne Tasche)", "select", GOOD3("war leicht zu treffen", "schwer, eine kleine Markierung wäre gut", "nicht zu treffen"))])
    add("S", "Stecken", "S", "Gebäude aufstecken: Treffen die Pins die Buchse, und hält die geklebte Leiste?",
        ["Gebäude (mit eingepresster Kassette) in die Mulde setzen, bis es unten anliegt.",
         "Beim Aufstecken beobachten: gehen alle vier Pins gleichzeitig hinein?",
         "Das Gebäude wieder abziehen und die Leiste ansehen: sitzt sie noch fest an der Platte?"],
        [],
        [fld("S-hit", "Pins treffen die Buchse", "select", GOOD3("ohne Kraft, alle vier gleichzeitig", "mit leichtem Suchen oder Rütteln", "verkantet, einzelne Pins bleiben hängen", "geht nicht")),
         fld("S-force", "Kraft zum Aufstecken", "select", GOOD3("leicht", "mittel", "viel")),
         fld("S-seat", "Gebäude nach dem Aufstecken", "select", GOOD3("sitzt fest, kein Wackeln", "leichtes Wackeln", "wackelt deutlich")),
         fld("S-glue1", "Leiste nach dem ersten Abziehen (Sekundenkleber)", "select", GOOD3("sitzt fest", "hat sich leicht gelöst", "ist abgefallen"))])
    add("H", "Halt des Klebers, zehn Mal", "H", "Zehn Mal aufstecken und abziehen: hält der Kleber?",
        ["Gebäude zehn Mal aufstecken und wieder abziehen. Nach jedem fünften Mal die Leiste kurz ansehen.",
         "Falls sich der Sekundenkleber löst: Leiste neu ankleben, diesmal mit <b>Heißkleber</b> rund um den herausragenden Körper (eine kleine Kehle zur Platte), und noch einmal zehn Mal.",
         "Wenn schon der Sekundenkleber hält, ist der Heißkleber nicht nötig."],
        [],
        [fld("H-sek", "Sekundenkleber nach zehn Mal", "select", GOOD3("hält", "löst sich nach einigen Malen", "löst sich sofort", "nicht getestet")),
         fld("H-heiss", "Heißkleber nach zehn Mal", "select", GOOD3("hält", "löst sich nach einigen Malen", "löst sich sofort", "nicht getestet")),
         fld("H-more", "Was hält besser?", "select", opts([("", "– bitte wählen –"), ("a", "Sekundenkleber"), ("b", "Heißkleber"), ("c", "kein Unterschied"), ("d", "beides hält nicht")]))])
    add("D", "Durchgang", "D", "Hält der Kontakt stabil?",
        ["Multimeter auf Durchgang: eine Spitze an das <b>Lötende</b>, die andere an die Ader des passenden Kontakts in der Buchse. Für alle vier Pins.",
         "Dabei das Gebäude seitlich um etwa 0,5 mm schieben und leicht kippen."],
        [],
        [fld("D-1", "Durchgang", "select", opts([("", "– noch nicht getestet –"), ("alle", "alle 4 Kontakte stabil, auch beim Wackeln"), ("aus", "mit Aussetzern beim Wackeln"), ("teil", "nur 1 bis 3 Kontakte"), ("kein", "kein Durchgang")]))])
    add("L", "Luft für Draht und Lötstelle", "L", "Passt die Luft unter der Platte, ohne dass etwas am Tisch hängt?",
        ["An die Lötenden je einen Draht anlöten (etwa 5 cm), wie später im Einsatz.",
         "Platte mit den Zapfen in die <b>Füße 3,5</b> (eine Kerbe) setzen und auf den Tisch stellen. Hängt Draht, Lötstelle oder der Körper der Leiste am Tisch?",
         "Dann dasselbe mit den <b>Füßen 2,5</b> (zwei Kerben)."],
        [("img", PREV + "/schnitt.png", "Schnitt: Der Tisch steht für die Oberkante der Powerbank.")],
        [fld("L-35", "Füße 3,5: Draht und Lötstelle", "select", GOOD3("frei, Luft übrig", "knapp, berührt fast", "liegt auf dem Tisch", "nicht geprüft")),
         fld("L-body35", "Füße 3,5: Körper der Leiste", "select", GOOD3("frei", "knapp", "liegt auf")),
         fld("L-25", "Füße 2,5: Draht und Lötstelle", "select", GOOD3("frei", "knapp, berührt fast", "liegt auf dem Tisch", "nicht geprüft")),
         fld("L-body25", "Füße 2,5: Körper der Leiste", "select", GOOD3("frei", "knapp", "liegt auf")),
         fld("L-best", "Welche Luft reicht?", "select", opts([("", "– bitte wählen –"), ("a", "3,5"), ("b", "2,5"), ("c", "dazwischen (Freitext)"), ("d", "mehr als 3,5 nötig")]))])
    add("Z", "Zapfen", "Z", "Sitzen die Zapfen mit 2,5 mm Länge ohne Wackeln?",
        ["Füße mit den Zapfen in die Löcher der Platte drücken (alle vier). Platte auf den Tisch stellen und leicht seitlich anstoßen."],
        [],
        [fld("Z-fit", "Zapfen in den Löchern", "select", R_FIT),
         fld("Z-stand", "Platte steht auf den Füßen", "select", GOOD3("fest und gerade", "wackelt leicht", "wackelt deutlich")),
         fld("Z-pull", "Füße wieder abziehen", "select", GOOD3("leicht", "mit Kraft", "gehen nicht ab"))])
    add("z", "Abschluss", "Σ", "Zum Schluss ein Gesamteindruck. Danach unten den Text kopieren und mir schicken.",
        ["Überlege, ob die flache Unterseite so für die große Platte taugt."],
        [],
        [fld("z-glue", "Verwendeter Kleber im Test", "select", opts([("", "– bitte wählen –"), ("a", "Sekundenkleber"), ("b", "Heißkleber"), ("c", "beide nacheinander")])),
         fld("z-ok", "Flache Unterseite so übernehmen?", "select", opts([("", "– bitte wählen –"), ("a", "ja, so lassen"), ("b", "ja, mit Änderungen (Freitext)"), ("c", "nein")])),
         fld("z-pocket", "Flache Tasche (0,4 mm) als Ausrichtung nötig?", "select", opts([("", "– bitte wählen –"), ("a", "nein, ohne geht"), ("b", "ja, mit Tasche"), ("c", "nur eine Markierung")])),
         fld("z-next", "Was als Nächstes", "select", opts([("", "– bitte wählen –"), ("a", "in die große Platte einbauen"), ("b", "Test-Dock nochmal mit Änderungen"), ("c", "anderes Konzept")]))])


def main():
    steps()
    html, nav, spec = BF.build_steps_html()
    with open(BF.TEMPLATE, encoding="utf-8") as f:
        page = f.read()
    i = page.index('<header class="top">')
    j = page.index("</header>") + len("</header>")
    head = '''<header class="top">
  <p class="kicker">Steckmechanismus · Test-Dock · flache Unterseite</p>
  <h1>Testbogen Test-Dock</h1>
  <p class="lead">Der Bogen führt Schritt für Schritt durch den Test: Druckqualität, Leiste ankleben, Stecken, Halt des Klebers, Durchgang, Luft für den Draht und die Zapfen. Je Schritt ein kurzes Formular; alles, was du ausfüllst, wird unten zu einem Text für mich zusammengesetzt. Was fehlt, bleibt weg.</p>
  <p class="lead">Beurteilt wird mit der Hand: <b>1</b> geht nicht, <b>2</b> nur mit Gewalt, <b>3</b> mit Fingerdruck ohne spürbares Spiel (ideal), <b>4</b> leicht mit minimalem Spiel, <b>5</b> locker. Die wichtigste Frage: Hält der Kleber beim zehnmaligen Aufstecken?</p>
</header>'''
    page = page[:i] + head + page[j:]
    page = page.replace("<title>Testbogen Steckprobe 2</title>", "<title>Testbogen Test-Dock</title>")
    page = page.replace("var KEY = 'steckprobe2-testbogen-v1';", "var KEY = 'testdock-testbogen-v1';")
    page = page.replace("'STECKPROBE 2 · ERGEBNIS (", "'TEST-DOCK · ERGEBNIS (")
    for k, v in {"{{STEPS}}": html, "{{NAV}}": nav, "{{SPEC}}": json.dumps(spec, ensure_ascii=False)}.items():
        page = page.replace(k, v)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(page)
    print("geschrieben: %s (%d kB), %d Schritte, %d Felder" % (os.path.relpath(OUT, ROOT), os.path.getsize(OUT) / 1024, len(BF.STEPS),
                                                              sum(len(s["fields"]) for s in BF.STEPS)))


if __name__ == "__main__":
    main()
