# r9: Schalterprobe Hauptschalter (gedruckt und ausgewertet, 2026-10-17)

**Status: gedruckt und ausgewertet.** Wörtlicher Ergebnistext: [`result.txt`](result.txt). Eingefrorener Satz: [`schalterprobe_T1_T2.zip`](schalterprobe_T1_T2.zip) (T1, T2, README und Prüfbericht von T2).

## Ziel und Teile

Ob der Wippenschalter KCD11 (10 × 15, Kasten 13 × 8) in der 1,2 mm dünnen Wand am Loch einrastet und wie groß das Loch sein soll. Eine Wand der Westwand des Unterkastens im Kleinen: Wandstück 24 × 17,4 × 2,4 mm, Loch mit der Langseite waagerecht, Innentasche mit 45°-Dach, Bodenstreifen, ≈ 1 g, 5 bis 10 Minuten.

- **T1** `T1_wand_schalter.stl`: Loch 13,6 × 8,6 (0,3 mm Spiel je Seite), Wand am Loch 1,2, Tasche 17,6 × 11,6 × 1,2 tief.
- **T2** `T2_wand_schalter.stl`: Loch 13,7 × 9,0 (horizontal +0,1, vertikal +0,4), Wand am Loch 1,2, Tasche 17,7 × 12,0 × 1,2 tief.
- Generator `python3 -m plug.power.build_switch_probe`, Plan `plug/power/plan_switch.html` (https://claude.ai/artifact/1B2dQEZPG32R1xqXzWnG16), Doku `docs/wippenschalter-kcd11.md`. Prüfbericht: dicht, Kasten im Loch ohne Kollision (Kontrollen stoßen an).

## Ergebnis

| Punkt | Ergebnis | Status |
|---|---|---|
| T1, Loch 13,6 × 8,6, Wand 1,2 | passt, aber **sehr stramm** | Loch zu eng |
| T2, Loch 13,7 × 9,0, Wand 1,2 | **lässt sich sehr gut einsetzen und hält trotzdem sehr fest** | **bewährt** |
| Wand am Loch 1,2 mm (drei Linien) | hält mit T1 und T2 | **bewährt** |
| Innentasche mit 45°-Dach | gedruckt, keine Beanstandung | bewährt (nicht gesondert bewertet) |
| Brücke über dem Loch (13,7 mm, ohne Stützen gedruckt) | **sauber** (Nutzer, nachgemeldet) | **bewährt** |
| Hakenspanne, Zug an der Wippe | Hakenspanne ungemessen; Halt „sehr fest“ | Spanne offen |

## Entscheidungen und Folgen

- Werte stehen in `plug/power/params.py` (`SW_HOLE`, `SW_WALL`, `SW_POCKET_PAD`, `SW_Y`) und werden vom Plan `build_plan_switch.py` gelesen.
- Lage: Westwand, y = 36 (Platte 1:1300, südlich der Elektronikbox); der Schieber der Planseite zeigt sie frei von Konflikten. Sie ist noch nicht in der echten Platte gedruckt.
- Offen: Einbau in den echten Unterkasten (Generator `hohl`/`build_concept` kennt die Wand und das Loch noch nicht), Hakenspanne mit der Schieblehre nachmessen, Brücke im echten Teil nur noch gegenzuprüfen (im Probeteil sauber).
