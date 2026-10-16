# r1: Nachtdruck 1 (2026-10-14/15)

Der wörtliche Ergebnistext dieser Runde ist nicht erhalten; die Zusammenfassung stammt aus dem Entscheidungsdokument (`plug/decision/page.html`) und dem
Kopf von `plug/series2.py`.

## Ziel

Serien mit Spielgravur: je Fuge eine Serie, nach Gefühl beurteilt. K Kontakt-Plättchen (t 1,2 / 1,8 / 2,4), N Schieber in der Nut (Spiel 0,05 bis 0,20),
S Boden-Platten (Schachtspiel 0,05 bis 0,20), C Kassette, R Buchsenhülsen (0,08 bis 0,20), FM Mulden-Ringe (0,10 / 0,15 / 0,20), D Passprobe v6.

## Teile und Quellen

`plug/series.py` → `stl/steckmodul_night1/` (`night1_fit_series.zip`, README). Commits `8965f40`, `08b6f70`; Testbogen `plug/feedback` (Commit `604660b`).
Plan und Fahrplan: `plug/roadmap`.

## Ergebnis

| Serie | Ergebnis |
|---|---|
| K | kein stabiler Durchgang; **Test lief mit leerem Gehäuse ohne Kontakte** (wertlos), später mit gecrimpten Kontakten wiederholt |
| N | alle vier Schieber klemmen; Decke über der Nut (34 mm Brücke) stark durchgehängt, Fäden in der Nut |
| S | **0,15 ideal**, 0,20 minimales Spiel, 0,10 nur mit Kraft, 0,05 passt nicht |
| C | Buchse nur mit Kraft (0,22 + Rippen), geht nicht ganz hinein; Adern knicken stark; Ablage 1 mm weiter weg von der Tasche |
| R | **0,20 ohne Rippen ideal** |
| D | überall schief (Körper liegt auf der Stufe) |
| FM | nicht getestet (Fuß-Lehre fehlte) |
| Druck | schwarzes PLA, Gravur schlecht lesbar, Elefantenfuß etwa 0,2 mm |

## Entscheidungen (Antworten auf das Entscheidungsdokument)

K nur bis 1,0 mm testen (Kontakte waren gecrimpt); N: Schieber noch einmal und dazu Einpressen testen; S 0,15; C: LED-Fläche ohne Tasche, sonst wie
vorgeschlagen; D: Tasche +1,5 und Körperhöhe variieren; FM Fuß-Lehre; Beschriftung erhaben, Fasen an Steckstellen.

## Folgen

Lehren L01 bis L04, L09, L10, L14, L15; Konstanten `KASS_CLR2` 0,15, `SNUG2` 0,20, `HSG_TOL2` 0,45, Einführfase 0,4 (jetzt in `plug/series2.py`).
