# Maßstab, Mulden und Kassettenwahl (festgelegt am 2026-10-16, Maßstab am Ende auf 1:1300 geändert)

Entscheidungen des Nutzers im Chat; Rechnung und Grafiken: `plug/scale1176/page.html` (Artifact https://claude.ai/artifact/S3qGmVQRr9tAPNqm2NyLQx, Ordnername von der ersten Fassung bei 1:1176).
**Alles Planung, nichts gedruckt, keine STL.** Werte in `plug/parts.py` und `plug/testcase/params.py` sind noch nicht umgestellt.

## Festgelegt

| Punkt | Entscheidung | Beleg |
|---|---|---|
| Größe der Platte | höchstens 230 × 230 mm (Druckbett mit Reserve) | Nutzer |
| Maßstab | **1:1250** (Grenze für 230 mm ist 1:1242); Platte 119,7 × 228,7 mm, einteilig | `plug/scale1176/page.html`, Abschnitt Maßstab |
| Muldentiefe | **überall 4 mm tiefer**: F 14,2 statt 10,2 mm, Platte 20,2 statt 16,2 mm; die LED liegt dadurch 4 mm tiefer gegenüber dem Dach | Nutzer, Vorschlag aus dem senkrechten Schnitt |
| Standard-Kassette | **v4** (LED strahlt nach oben), überall wo sie passt (bei 1:1300: Neues Augusteum, Hörsaalgebäude, Paulinum; Paulinum nur 0,9 mm Wand, knapp, Wechsel auf V1RS möglich) | Nutzer |
| City-Hochhaus | **V2R** (zwei LEDs, hochkant, Konzept aus `cassettes.md`), weil v4 dort nicht passt | Nutzer |
| Innenhof | eigenes Einsteckteil, Bäume angedruckt (bestätigt: „Bäume andrucken ist super“) | Nutzer, Seite Abschnitt Innenhof |
| **Maßstab (aktuell)** | **1:1300**, Platte 115,6 × 220,8 mm einteilig; dafür V1RS in Institutsgebäude und Seminargebäude | Nutzer, nach Rechnung V1RS bei 1:1300 |
| Maßstab (überholt) | 1:1250 war zwischenzeitlich bestätigt (Platte 119,7 × 228,7 mm); (1:1200 ergäbe eine Platte von etwa 237 × 124 mm, über der 230-mm-Grenze); 1,3 mm Reserve auf 230 mm sind in Ordnung; Drehen der Platte (auch diagonal) bringt nichts | Nutzer |
| LED-Streifen | nur der 10-mm-Streifen, wie immer geplant; Kassettenwahl je Gebäude bleibt (v4 überall, V2R Hochhaus) | Nutzer |
| Hof-Einsatz | **ohne die 4 mm Zusatztiefe** (1 mm unter, 1,9 mm über der Oberfläche wie bisher), aber **einsetzen wie die Gebäude: mit Einführfase** (0,4 bis 0,5 mm wie `ENTRY_CH_T`/`EF_CH_T`); Stämme erst mit 0,8 mm im Probedruck testen, 1 mm als Rückfall | Nutzer |
| Institutsgebäude | **V1RS** (Wand ≥ 3,0 mm, Luft 10,2 mm bei 1:1300); Rückfall v4 nur bei 1:1250 (Luft 4,4 mm) | Nutzer, ersetzt „v4 testen“ |
| Seminargebäude | **V1RS** (Wand ≥ 3,0 mm, Luft 10,2 mm bei 1:1300); v4 hätte bei 1:1300 nur 0,6 mm Wand und passt nicht | Nutzer, ersetzt „v4 ausprobieren“ |

## Rechnung bei 1:1250 (Stand vor der Änderung auf 1:1300; Mulde +4 mm, Wand 0,8 mm Mindestmaß)

Größte Wand um den Schacht bei Grundriss und Höhe zusammen und Luft von der LED-Mitte bis zum Dach an der höchsten Stelle, an der der Schacht passt. LED v4: 2,9 mm über der Platte (6,9 − 4).

| Gebäude | Kassette | Wand mm | Dachhöhe mm | Luft LED bis Dach mm |
|---|---|---|---|---|
| Paulinum | v4 | 1,2 | 23,9 | 21,0 |
| Neues Augusteum | v4 | ≥ 3,0 | 12,5 | 9,6 |
| Hörsaalgebäude | v4 | ≥ 3,0 | 14,6 | 11,7 |
| Seminargebäude | v4 | 0,9 (knapp) | 19,2 | 16,3 |
| Institutsgebäude | v4 | 1,9 | 7,3 | **4,4** |
| City-Hochhaus | V2R | ≥ 3,0 | 95,7 | 84,1 |

## Rechnung bei 1:1300 (aktuell, Mulde +4 mm, Wand 0,8 mm Mindestmaß)

| Gebäude | Kassette | Wand mm | Luft LED bis Dach mm |
|---|---|---|---|
| Paulinum | v4 (Alternative V1RS: ≥ 3,0 / 22,4) | 0,9 (knapp) | 18,3 |
| Neues Augusteum | v4 | ≥ 3,0 | 9,1 |
| Hörsaalgebäude | v4 | ≥ 3,0 | 11,2 |
| Seminargebäude | **V1RS** (v4: 0,6, passt nicht) | ≥ 3,0 | 10,2 |
| Institutsgebäude | **V1RS** (v4: 1,6 / Luft 4,1) | ≥ 3,0 | 10,2 |
| City-Hochhaus | V2R | ≥ 3,0 | 80,4 |

Bis 1:1350 trägt der Plan, wenn auch das Paulinum V1RS bekommt (Hochhaus bei 1:1350 nicht geprüft). **V1RS**: Streifen quer, zwei LEDs (vorn und hinten), Unterbau 19,2 × 6,4 mm, 27,7 mm hoch, Verkettung am Blattrand vorbei; die LED strahlt seitlich; Konzept, Adernweg und Streifendicke 2,2 mm ungetestet. Der Hof (Maße, Stämme 0,8 mm) ist bei 1:1300 neu zu rechnen; die Zahlen der Seite für Hof, Platte und Tabellen gelten bei 1:1250.

## Offen aus dieser Festlegung

- **Institutsgebäude (jetzt V1RS; Hinweis galt für v4):** nur 4,4 mm Luft über der LED, der Schacht darf nur unter dem niedrigen Dachteil (7,3 mm hoch) liegen. Richtwert 8 mm ist eine Annahme, ungetestet. Möglichkeiten: Kassette dort anders legen, V1 (Luft 12,3 mm bei +4 mm, LED dort 6,9 mm über der Platte, strahlt aber seitlich), oder nur dort tiefer.
- **Seminargebäude (jetzt V1RS; Hinweis galt für v4):** Wand nur 0,9 mm (knapp).
- **Hochhaus V2R:** Konzept, Streifendicke 2,2 mm nicht gemessen, Adern und Verkettung ungetestet; das Hochhaus braucht eine Kassette V2R mit Schacht 12,96 × 6,4 mm und Gebäude mindestens 23,9 mm hoch (es ist 116 mm hoch). Die LED blickt dort seitlich, nicht nach oben.
- **Fuß 14,2 mm** statt 10,2 mm ist nicht getestet (Führung in der Mulde, Kippen). Dock, Kabelraum, Muldenboden und Platte rücken 4 mm tiefer; Platte 20,2 mm dick.
- Schächte sind noch Vollkörper im Generator (kein Hohlraum, kein Lichtfenster im Gebäude).
- Licht durch die Wand und Druckbarkeit der 0,8-mm-Stämme des Hofs bei 1:1250: nur ein Probedruck zeigt es.
- **Hof-Einsatz:** Fuge, Halt (Reibrippen oder Kleber) und Oberkante 1,9 mm über der Straße sind nicht festgelegt; bei 20,2 mm Plattendicke Aussparungstiefe und Einsatzdicke (heute 1 mm unter, 1,9 mm über der Oberfläche) prüfen.
- **Kabelraum und Löträume der Nachbarn** bei tieferen Docks nicht gerechnet; Fadenführung (Plan Steckprobe 2) hängt von der Plattendicke ab.
- **Platte 20,2 mm dick und 230 mm lang:** Druckzeit und Material, Auflage auf dem A1-Bett mit Reserve 1,3 mm; Verzug bei der langen Seite.
- **Steckprobe für 1:1250:** Kassette v4 mit Podest in Mulde 14,2 mm; Mini-Gebäude im neuen Maßstab; Probedruck V2R fürs Hochhaus.
- **Werte umstellen:** nach bewährtem Test `params.py` und `parts.py` auf F 14,2 setzen, Generator für den Fuß mit Mulde 14,2 und für die Platte mit allen Docks.
- **To-do (anderer Chat): Gebäude als Hohlkörper.** Jedes Gebäude braucht einen Hohlraum, in dem die Aufnahme für die Kassette (Schacht im Fuß, Lichtfenster, Dachanschlag) sitzt; heute erzeugt `generate.py` Vollkörper.

## Werte, die für die Festlegung umzustellen sind (noch nicht umgesetzt)

| Wert | Wo | alt | neu | Warum |
|---|---|---|---|---|
| Zusatztiefe der Mulde | neue Konstante `MULDE_EXTRA_T` in `plug/testcase/params.py`, geht in `F = layer_up(g1 + GUIDE + CH_F + CH_P + MULDE_EXTRA_T)` ein (gleichwertig: `GUIDE` 3,0 → 7,0, erst nach bewährtem Test in `parts.py`) | 0 | 4,0 | LED sitzt 4 mm tiefer unter dem Dach |
| Fußhöhe / Muldentiefe F | abgeleitet, `dims()["F"]` | 10,2 | 14,2 | folgt aus der Zusatztiefe |
| Plattendicke | abgeleitet, `dims()["plate_t"]` | 16,2 | 20,2 | Dock und Kabelraum rücken mit nach unten |
| Lage von Winkelleiste, Pin-Spitze, Kabelraum | abgeleitet (`z_hb`, `z_bb`, `z_tip`, `z_lt`) | −10,6 / −12,6 / −4,92 / −16,2 | −14,6 / −16,6 / −8,92 / −20,2 | alles unter dem Muldenboden hängt an F |
| Kassettenoberkante über der Platte | abgeleitet, `kass_top` | 6,75 | 2,75 | gleiche Kassette, Fuß 4 mm länger |
| Dach über der Kassette (Gebäudehöhe mindestens) | abgeleitet, `box_top` | 7,95 | 3,95 | wie oben; die Gebäude brauchen weniger Höhe |
| Einstecktiefe E, Muldenboden, Kassettenmaße, Schachtspiel, Fasen | `E` 5,28, `CEIL_T` 0,4, `KASS_CLR_T` 0,06, `ENTRY_CH_T` 0,4 | | **unverändert** | bewährte Werte gelten weiter; `box_h` (Fußunterkante bis Dach) bleibt 18,15 |
| Maßstab | `python3 generate.py --scale 1250`, README-Block Maßstäbe | 1000 und 1500 | 1250 zusätzlich | neue Vorgabe 230 × 230 mm |
| Plattendicke im Generator | `generate.py`: `PLATE_THICKNESS` | 3,0 | 20,2 (aus `params.dims()`), neue Platte mit Docks | die heutige Grundplatte hat weder Muldentiefe noch Docks |
| Hof-Einsatz | `generate.py`/`innenhof.py`: `POCKET_DEPTH` | 1,0 | 1,0 (unverändert), neu: Einführfase 0,4 bis 0,5 | ohne Zusatztiefe, aber einsetzen wie die Gebäude |
| Kassettenwahl je Gebäude | neue Tabelle in `params.py` | – | v4 überall, V2R für City-Hochhaus | Festlegung oben |
| `plug/parts.py` | Kaufteil-Maße und alte Werte | | **bleibt**, bis die Steckprobe 3 die 14,2 mm bestätigt | Regel aus CLAUDE.md |

## Umstellen: jetzt oder erst nach Test

Der Nutzer (2026-10-16): Steckprobe 3 ist nicht wichtig (Reserve-Druck), weil schon viel geklappt hat. Deshalb alles, was nur Planung und Parameter ist, **jetzt** in `plug/testcase/params.py` und im Generator; `plug/parts.py` und alles, was gedruckte Teile festlegt, erst nach Test.

| Jetzt (Parameter, Planung, Generator) | Erst nach Test |
|---|---|
| `MULDE_EXTRA_T = 4.0` in `params.py` (F 14,2, Platte 20,2 und alle abgeleiteten Lagen) | `GUIDE` 3,0 → 7,0 in `plug/parts.py` (gleiche Wirkung, aber Quelle der bewährten Werte) |
| Maßstab 1300 im Generator (`--scale 1300`), README-Block Maßstäbe | Hof-Stämme 0,8 mm als bewährt (Probedruck) |
| Kassettenwahl je Gebäude als Tabelle in `params.py` | V1RS und V2R als druckfertige Teile (Streifendicke 2,2 mm messen, Adernweg, Verkettung) |
| Hof-Einführfase 0,4 bis 0,5 mm | Fuß 14,2 mm als bewährt (Führung, Kippen) |
| Neue Platte mit Docks im Generator (statt 3 mm Grundplatte) | Paulinum v4 mit 0,9 mm Wand |
