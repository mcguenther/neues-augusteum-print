# r5: Fachprobe Powerbank (gedruckt und ausgewertet, 2026-10-16)

**Status: gedruckt und ausgewertet (2026-10-16), Rückmeldung dünn.** Wörtliche Antworten des Nutzers: [`result.txt`](result.txt) (kein Ergebnistext des Testbogens, sondern Chat-Sätze). Eingefrorener Satz: [`fachprobe.zip`](fachprobe.zip) (Stand Commit `3ccceeb`: Bau und Testbogen; Plan `fed8228`). Welche ZIP-Version gedruckt wurde, steht nicht in der Rückmeldung (L33); es gab nur diesen Stand, die Variante war B.

## Ziel und Teile

Ob die Powerbank (Intenso XS5000, laut Datenblatt 90 × 63 × 12,6 mm, ungemessen) in das Fach der großen Grundplatte passt, wie sie sitzt, ob der Ladeanschluss durchs Fenster erreichbar ist, ob der gerade USB-A-Stecker samt Kabel Platz hat. Keine Taste, kein Stößel, keine Schablone (Nutzer: der Mikrocontroller fragt später alle 5 s kurz Strom ab).

- `F_fach.stl`: Ausschnitt vom Anschlussende (Variante B) 67,9 × 74,8 × 14,4 mm: Boden 1,2, Wand 2,4, Fenster in der Vorderwand (oben offen), Zaun 1,6 × 5, Kabelkanal 6 (frei 4,4 neben dem Zaun), hinten offen, ≈ 15,2 g.
- `F_deckplatte.stl`: 2 mm, steht für die Oberplatte, nur aufgelegt, ≈ 10,9 g.
- Generator `python3 -m plug.power.build_fach`, Geometrie `plug/power/fachprobe.py`. Plan `plug/power/plan_fach.html` (https://claude.ai/artifact/JgTgE5ckNHmt56F3igkXhK), Testbogen `plug/power/feedback_fach.html` (https://claude.ai/artifact/FKLje3Pq8eSphqzvaohz7W). Prüfbericht: dicht, keine Kollisionen; Kontrolle „Powerbank 13,0 dick“ unter der Deckplatte Überschneidung 0.

## Ergebnis

| Punkt | Ergebnis | Status |
|---|---|---|
| Höhe über der Powerbank (Luft 0,6 bei 12,6) | Powerbank „tatsächlich minimal dicker“, Nutzer: „wir müssen ca. 0.2 mm mehr höhe für die powerbank einplanen“; keine Zahl | **verworfen (zu knapp)**, Luft +0,2 |
| Deckplatte | **hat gewackelt**; Ursache nicht abgefragt (vermutlich liegt sie auf der etwas zu dicken Powerbank auf und kippelt; ohne Zapfen oder Faden hält sie ohnehin nicht) | offen (Ursache ungeklärt) |
| Zaun | **nicht mitgedruckt**, nur der Ausschnitt am Anschlussende (Aussage des Nutzers, im Widerspruch zu README und Prüfbericht, die einen Zaun um die Powerbank nennen) | Sitz im Zaun und Seitenspiel 0,5 nicht belegt |
| Powerbank-Länge 90 mm (30 mm im Fach) | keine Rückmeldung | offen |
| Kabelkanal 4,4 mm frei (Kabel 4 mm) | keine Rückmeldung (nicht beanstandet) | offen |
| Fenster, LEDs, micro-USB, USB-C | keine Rückmeldung (nicht beanstandet) | offen |
| Steckerraum 35 mm, gerader USB-A-Stecker | keine Rückmeldung (nicht beanstandet) | offen |

„Nicht beanstandet“ heißt hier nicht „bewährt“: Der Nutzer schrieb, das Einzige, was ihn gestört habe, sei die Höhe. Ob die übrigen Punkte geprüft oder nur nicht erwähnt wurden, ist offen.

## Entscheidungen und Folgen

- `plug/power/params.py`: **`PB_CLR_Z` 0,6 → 0,8** (Luft über der Powerbank, +0,2 nach Nutzer). `PB_T` bleibt 12,6 (ungemessen); kein Zahlenwert für die tatsächliche Dicke. Fachhöhe 13,2 → 13,4, Unterkasten 14,4 → 14,6, Gesamthöhe der Grundplatte 27,0 → 27,2 mm (`python3 -m plug.power.build_concept`, Seite `plug/power/concept.html` neu erzeugt, Artifact noch nicht neu veröffentlicht).
- `plug/parts.py` unverändert. Der gedruckte Satz (`stl/steckmodul_fachprobe/`) bleibt auf Luft 0,6 stehen und wurde nicht neu gebaut.
- Neue Lehre L35 (Powerbank ungemessen, Luft im Worst-Case rechnen: Prüfbericht hatte 13,0 → 0,2 mm Luft noch als „ok“ gemeldet) in `lessons.md`.

## Was die Runde nicht klärte

- Tatsächliche Dicke der Powerbank (keine Zahl); ob +0,2 mm Luft genügt, hängt davon ab.
- Ursache des Wackelns der Deckplatte.
- Ob der Zaun fehlte oder nur am Anschlussende steht; Sitz im Zaun, Seitenspiel, Länge.
- Kabelkanal, Fenster mit Anschlüssen, Steckerraum 35 mm.
- Die Konzeptseite zeigt noch Stößel und Taste (entfallen laut Nutzer); nicht entfernt, weil die Aufgabe dieses Chats auf Logbuch und Werte begrenzt wurde.
