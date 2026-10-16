# Logbuch Steckmechanismus (`plug/logbook/`)

Hier stehen die Ergebnisse der Testdrucke, damit wir **keinen Fehler zweimal machen**. `plug/STATUS.md` bleibt die
große Chronologie des Zweigs (Passproben, Konstanten mit Herkunft, Repo-Ablage); das Logbuch ist die kurze, laufend
gepflegte Sicht darauf: Was hat geklappt, was nicht, was kommt als Nächstes.

| Datei | Inhalt | Wann lesen |
|---|---|---|
| [`current.md`](current.md) | Bewährter Stand: Werte und Geometrie, die funktioniert haben (mit Status, Beleg und Code-Stelle), Maßkette, Druckeinstellungen, Dateien des getesteten Satzes | vor jedem Plan |
| [`lessons.md`](lessons.md) | Fehlerkatalog „nicht noch einmal“ und die Vorab-Checkliste vor jeder STL | vor jedem Plan und vor jeder STL |
| [`next.md`](next.md) | Nächste Drucke mit Priorität, offene Fragen, Ideen | am Anfang einer Runde |
| [`scale.md`](scale.md) | Festlegung Maßstab 1:1250, Mulde 4 mm tiefer, v4 als Standard, V2R fürs Hochhaus (Planung, ungetestet) | vor jeder Arbeit an Maßstab, Mulde, Kassettenwahl |
| [`cassettes.md`](cassettes.md) | Register der Kassetten-Varianten V1, V2, V2R, V1R, V1RS (Maße, Status, offene Punkte, Befehle) | vor jeder Arbeit an der Kassette |
| [`rounds/`](rounds/) | je Runde ein Ordner: `summary.md` (Ziel, Teile, Ergebnis, Entscheidungen, Folgen, Commits) und `result.txt` (der Ergebnistext des Testbogens, wörtlich), bei Bedarf die eingefrorenen ZIP | zum Nachschlagen |

Runden: [r0 Passproben und Probestück](rounds/r0_fitprobes/summary.md) ·
[r1 Nachtdruck 1](rounds/r1_night1/summary.md) · [r2 Nachtdruck 2](rounds/r2_night2/summary.md) ·
[r3 Steckprobe 1](rounds/r3_steckprobe1/summary.md) ·
[r4 Steckprobe 2 (Planung, Zwischenstand)](rounds/r4_steckprobe2/summary.md)

## Begriffe

- **Steckprobe**: der Testaufbau aus Mini-Gebäude (L-Fuß), Kassette mit Buchse, Mini-Grundplatte mit Winkelleiste und Mini-Deckel.
  Er prüft den kompletten Steckmechanismus im Kleinen, ohne ein echtes Gebäude zu drucken. Im Code heißt das Paket
  `plug/testcase/` (englischer Ordnername), in Gesprächen und Dokumenten sagen wir *Steckprobe* (`r3` = Steckprobe 1; der Name ist vom Nutzer bestätigt).
- **Kassette**: gedruckte Hülse für Dupont-Buchse, Adern und LED-Streifen; wird von unten in den Schacht des Gebäudefußes gepresst.
- **Platte / Dock A**: Grundplatte mit Mulde für den Fuß und der Tasche für die abgewinkelte Winkelleiste; Pins ragen durch den Muldenboden.
- **E** (Einstecktiefe): wie tief die Pins in der Buchse stecken; Durchgang stabil ab etwa 5,1 mm.
- **Muldenboden / CEIL**: Dicke zwischen Winkelleistenkörper und Fußunterkante, zählt von E ab.

## Arbeitsmodus (so arbeiten wir)

```
 Claude                                  Nutzer
 ──────                                  ──────
 1  Plan als HTML mit Grafiken,          2  prüft, wählt in den Karten,
    Maßkette, Entscheidungskarten           nickt ab (oder ändert)
    (plug/<paket>/plan.html)
 3  STL + README + ZIP, Prüfbericht      4  druckt, steckt zusammen,
    (dicht, keine Kollisionen,              füllt das Testbogen-Formular aus
    Überhangprüfung), Vorschaubilder
 5  Testbogen als HTML-Formular          6  kopiert den Ergebnistext
    (Schritte, Zeichnungen, Regler,         und fügt ihn im Chat ein
    Ergebnistext zum Kopieren)
 7  Auswertung: erst Erkenntnisse zusammenfassen und bewerten, offene Fragen nennen,
    dann ins Logbuch (Runde, current, lessons, next) und in `STATUS.md`, committen, pushen
```

Regeln:

1. **Erst lesen, dann planen.** Vor jedem Plan `lessons.md` und `current.md` lesen; im Plan steht, welche Lehren berücksichtigt sind.
2. **Plan vor STL.** Ohne Abnicken des Nutzers gibt es keine STL. Der Plan zeigt Alternativen und eine Empfehlung, die Maßkette (Worst-Case) und die Risiken.
3. **Vor jeder STL die Checkliste** aus `lessons.md` durchgehen und den Prüfbericht zeigen.
4. **Ein Testbogen je Druck**, im Ergebnistext steht, welche Variante gedruckt wurde (A/B …) und welche Version die ZIP hat.
5. **Auswerten, bevor etwas gebaut wird.** Unklarheiten und widersprüchliche Angaben werden benannt, nicht erraten.
6. **Logbuch pflegen.** Nach jeder Auswertung: `rounds/rN_*/summary.md` und `result.txt` anlegen, `current.md` (Werte mit Status), `lessons.md` (neue Lehren), `next.md` (Backlog) und `STATUS.md` nachziehen.
   Der getestete Satz wird eingefroren (ZIP im Rundenordner, Commit-Hash in `summary.md`), weil der Generator die Dateien in `stl/` überschreibt.
7. **Messfelder nur, wenn der Nutzer messen kann** (Spalt unter 0,5 mm nicht). Besser: fühlbare Skala 1 bis 5 oder ja/nein.
8. `plug/parts.py` ändert sich erst, wenn ein Wert in einer Runde bewährt ist; bis dahin stehen neue Werte in `plug/<paket>/params.py`.

## Format eines Rundeneintrags

`rounds/rN_name/summary.md`: Ziel · gedruckte Teile (Dateien, Commits, Artifacts) · Ergebnis je Teil (bewährt / verworfen / offen) ·
Entscheidungen · Folgen für Werte und Geometrie · was die Runde nicht klärte. `result.txt`: der Ergebnistext des Testbogens, unverändert.
