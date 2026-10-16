#!/usr/bin/env python3
"""Testbogen zur Fachprobe Powerbank (Variante B): plug/power/feedback_fach.html.

Gleiche Seitenform und Formularlogik wie der Testbogen Steckprobe 2 (plug/testcase/feedback2.template.html, Schritte über
plug/testcase/build_feedback2.py). Nur fühlbare oder ja/nein-Felder (Logbuch Regel 7), die Variante steht im Ergebnistext.
    python3 -m plug.power.build_feedback_fach
"""
import json
import os

from plug.feedback.build import R_FIT, R_YN, fld, opts
from plug.feedback.build_night2 import GOOD3
from plug.testcase import build_feedback2 as BF

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(HERE, "feedback_fach.html")
PREV = os.path.join(ROOT, "vorschau", "steckmodul_fachprobe")
NOTE = fld  # Kurzschreibweise


def steps():
    BF.STEPS.clear()
    add = BF.add
    add("a", "Aufbau ansehen (vor dem Druck)", "0", "Was gedruckt wird: ein Ausschnitt vom Anschlussende des Fachs und eine Deckplatte. Die Powerbank ragt hinten heraus.",
        ["Oben die zwei Teile in Druckausrichtung, darunter der Zusammenbau mit Powerbank, USB-A-Stecker (dunkel) und Kabel (rot).",
         "Die Taste und ein Stößel fehlen mit Absicht. Der Ladeanschluss (micro-USB, USB-C) liegt hinter dem Fenster in der Vorderwand.",
         "Das Kabel läuft vom Stecker seitlich in einen Kanal neben dem Zaun und hinten heraus. Der Kanal ist 4,4 mm frei."],
        [("img", PREV + "/teile.png", "Die zwei Teile: Fach (blaugrau) und Deckplatte (hellblau)."),
         ("img", PREV + "/zusammenbau.png", "Links schräg mit abgehobener Deckplatte, rechts von oben; die Powerbank (hell) ragt nach rechts heraus.")],
        [fld("a-ok", "So drucken?", "select", opts([("", "– bitte wählen –"), ("a", "ja, so drucken"), ("b", "ja, aber mit Anmerkung (Freitext)"), ("c", "nein, vorher ändern (Freitext)")]))],
        optional=True)
    add("p", "Vorbereiten", "1", "Alles hinlegen. Messen musst du nichts.",
        ["Bereitlegen: <b>Fach</b> (<code>F_fach</code>), <b>Deckplatte</b> (<code>F_deckplatte</code>), die <b>Powerbank</b> und das <b>USB-A-Kabel</b> mit geradem Stecker, das später dranhängt.",
         "Das Ladekabel, mit dem du die Powerbank sonst auflädst (micro-USB oder USB-C), für den Test durch das Fenster."],
        [("img", PREV + "/teile.png", "Die zwei gedruckten Teile.")],
        [fld("p-cab", "Wie dick ist das USB-A-Kabel ungefähr?", "select", opts([("", "– bitte wählen –"), ("a", "dünn (bis etwa 3 mm)"), ("b", "normal (etwa 4 mm)"), ("c", "dick (5 mm oder mehr)")])),
         fld("p-plug", "Ist der USB-A-Stecker gerade (Kabel geht hinten heraus)?", "select", R_YN("ja, gerade", "nein, abgewinkelt")),
         fld("p-chg", "Welches Ladekabel für den Test?", "select", opts([("", "– bitte wählen –"), ("a", "micro-USB"), ("b", "USB-C"), ("c", "beide"), ("d", "keines")]))])
    add("q", "Druckqualität ansehen", "2", "Bevor etwas gesteckt wird: die gedruckten Teile kurz prüfen.",
        ["Beide Teile von oben, unten und von der Seite ansehen. Mit dem Fingernagel die <b>Kanten am Bett</b> fühlen (Fase 0,5).",
         "Das <b>Fenster</b> in der Vorderwand und der <b>Zaun</b> um die Powerbank: sauber und gerade?"],
        [],
        [fld("q-all", "Welche Dateien wurden gedruckt?", "text", ph="z. B. beide"),
         fld("q-edge", "Elefantenfuß an den Bettkanten (Fase 0,5)", "select", GOOD3("sauber, Fase hat gewirkt", "leichter Wulst", "starker Wulst, musste entgratet werden")),
         fld("q-fence", "Fenster und Zaun", "select", GOOD3("sauber und gerade", "leichte Mängel, stört nicht", "Zaun verbogen oder abgebrochen", "Fehldruck")),
         fld("q-lid", "Deckplatte", "select", GOOD3("flach und eben", "leicht verzogen", "stark verzogen")),
         fld("q-time", "Druckzeit insgesamt in Stunden", "text", ph="z. B. 1,5"),
         fld("q-fil", "Drucker und Filament", "text", ph="z. B. Bambu A1, PLA schwarz")])
    add("P", "Powerbank einlegen", "P", "Passt die Powerbank in das Fach, und wie sitzt sie?",
        ["Powerbank mit der <b>Anschlussseite zur Vorderwand</b> (die Wand mit dem Fenster) in das Fach legen. Der Rest ragt hinten heraus.",
         "Geht sie ohne Zwang hinein? Schleift sie am Zaun? Fach leicht schütteln: wackelt sie?",
         "Einmal herausnehmen und wieder einlegen, drei Mal."],
        [],
        [fld("P-fit", "Sitz der Powerbank im Zaun", "select", R_FIT),
         fld("P-dir", "Anschlussseite liegt an der Fensterwand", "select", R_YN("ja", "nein, sie muss andersherum")),
         fld("P-wob", "Schütteln des Fachs", "select", GOOD3("sitzt fest", "wackelt leicht", "wackelt deutlich")),
         fld("P-len", "Passt die Länge zum Datenblatt (90 mm, mit dem Lineal)?", "select", opts([("", "– nicht geprüft –"), ("a", "ja, etwa 90"), ("b", "nein, deutlich anders (Freitext)")]))])
    add("D", "Deckplatte", "D", "Wie viel Luft bleibt über der Powerbank?",
        ["Deckplatte auf das Fach legen.",
         "Liegt sie flach auf den Wänden und dem Zaun, oder liegt sie auf der Powerbank auf? Mit dem Finger leicht auf die Platte drücken: klappert etwas?"],
        [],
        [fld("D-flat", "Deckplatte liegt flach auf den Wänden", "select", GOOD3("rundum flach, kein Spalt", "kleiner Spalt an einer Stelle", "liegt auf der Powerbank auf, klafft")),
         fld("D-air", "Luft zwischen Powerbank und Deckplatte", "select", GOOD3("deutlich Luft", "knapp, aber frei", "berührt die Powerbank")),
         fld("D-clap", "Klappern oder Wackeln", "select", GOOD3("nichts", "leichtes Spiel", "klappert deutlich"))])
    add("F", "Fenster und Ladeanschluss", "F", "Kommt man durch das Fenster an das, was man braucht?",
        ["Mit aufgelegter Deckplatte von vorn durch das Fenster schauen: sind die LEDs der Powerbank sichtbar?",
         "Das Ladekabel (micro-USB oder USB-C) durch das Fenster an die Powerbank stecken und wieder abziehen. Reicht der Platz um den Stecker?",
         "Das ist nur ein Test des Ladeanschlusses; die Taste wird nicht gebraucht."],
        [],
        [fld("F-led", "LEDs sichtbar", "select", GOOD3("gut sichtbar", "teilweise verdeckt", "nicht sichtbar")),
         fld("F-chg", "Ladekabel durch das Fenster einstecken", "select", GOOD3("geht leicht", "geht mit Mühe, Stecker streift den Rand", "geht nicht", "nicht geprüft")),
         fld("F-edge", "Sitz der Anschlüsse im Fenster", "select", GOOD3("mittig, Rand frei", "knapp am Rand", "Anschluss liegt hinter der Wand")),
         fld("F-gap", "Fenster", "select", GOOD3("Größe passt", "etwas größer wäre besser", "kleiner reicht"))])
    add("S", "USB-A-Stecker und Kabel", "S", "Passt der gerade Stecker samt Kabel in den Steckerraum, und läuft das Kabel in den Kanal?",
        ["Den USB-A-Stecker des Kabels in die USB-A-Buchse der Powerbank stecken. Er liegt im Steckerraum vor der Powerbank.",
         "Das Kabel seitlich in den Kanal neben dem Zaun legen und hinten herausführen. Deckplatte auflegen.",
         "Stecker und Kabel einmal abziehen und wieder einstecken."],
        [],
        [fld("S-plug", "Stecker im Steckerraum (35 mm)", "select", GOOD3("passt gut, Platz übrig", "knapp, streift die Wand", "passt nicht")),
         fld("S-bend", "Kabel vom Stecker in den Kanal", "select", GOOD3("liegt ohne Knick", "leichter Knick", "knickt stark oder klemmt")),
         fld("S-chan", "Kabel im Kanal neben dem Zaun", "select", GOOD3("liegt frei", "klemmt leicht am Zaun", "passt nicht hinein")),
         fld("S-lid", "Deckplatte mit Stecker und Kabel", "select", GOOD3("liegt flach auf", "hebt sich an", "geht nicht zu")),
         fld("S-pull", "Stecker abziehen und einstecken", "select", GOOD3("leicht, nichts verschiebt sich", "schiebt die Powerbank mit", "kaum möglich"))])
    add("z", "Abschluss", "Σ", "Zum Schluss ein Gesamteindruck. Danach unten den Text kopieren und mir schicken.",
        ["Überlege, ob das Fach so für die große Platte taugt."],
        [],
        [fld("z-var", "Gedruckte Variante", "select", opts([("", "– bitte wählen –"), ("B", "B, Anschlussende (wie im Plan)")])),
         fld("z-ok", "Fach so übernehmen?", "select", opts([("", "– bitte wählen –"), ("a", "ja, so lassen"), ("b", "ja, mit Änderungen (Freitext)"), ("c", "nein")])),
         fld("z-next", "Was als Nächstes", "select", opts([("", "– bitte wählen –"), ("a", "Fach in die große Platte einbauen"), ("b", "Fachprobe nochmal mit Änderungen"), ("c", "ganzes Fach (Variante A) drucken")]))])


def main():
    steps()
    html, nav, spec = BF.build_steps_html()
    with open(BF.TEMPLATE, encoding="utf-8") as f:
        page = f.read()
    i = page.index('<header class="top">')
    j = page.index("</header>") + len("</header>")
    head = '''<header class="top">
  <p class="kicker">Steckmechanismus · Fachprobe Powerbank · Variante B</p>
  <h1>Testbogen Fachprobe Powerbank</h1>
  <p class="lead">Der Bogen führt Schritt für Schritt durch die Probe: Powerbank einlegen, Deckplatte, Fenster und Ladeanschluss, USB-A-Stecker und Kabel. Je Schritt ein kurzes Formular; alles, was du ausfüllst, wird unten zu einem Text für mich zusammengesetzt. Was fehlt, bleibt weg.</p>
  <p class="lead">Es geht nur darum, ob alles zusammenpasst und wie es sitzt. Beurteilt wird mit der Hand: <b>1</b> geht nicht, <b>2</b> nur mit Gewalt, <b>3</b> mit Fingerdruck ohne spürbares Spiel (ideal), <b>4</b> leicht mit minimalem Spiel, <b>5</b> locker. Taste und Stößel gibt es nicht mehr.</p>
</header>'''
    page = page[:i] + head + page[j:]
    page = page.replace("<title>Testbogen Steckprobe 2</title>", "<title>Testbogen Fachprobe Powerbank</title>")
    page = page.replace("var KEY = 'steckprobe2-testbogen-v1';", "var KEY = 'fachprobe-testbogen-v1';")
    page = page.replace("'STECKPROBE 2 · ERGEBNIS (", "'FACHPROBE POWERBANK · ERGEBNIS (")
    for k, v in {"{{STEPS}}": html, "{{NAV}}": nav, "{{SPEC}}": json.dumps(spec, ensure_ascii=False)}.items():
        page = page.replace(k, v)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(page)
    print("geschrieben: %s (%d kB), %d Schritte, %d Felder" % (os.path.relpath(OUT, ROOT), os.path.getsize(OUT) / 1024, len(BF.STEPS),
                                                              sum(len(s["fields"]) for s in BF.STEPS)))


if __name__ == "__main__":
    main()
