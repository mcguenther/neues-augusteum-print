ERSTER NACHTDRUCK: PASSUNGSSERIEN FÜR DIE KASSETTE
==================================================

Warum Serien?
  Abstände unter 0,5 mm lassen sich am Probestück nicht messen. Jedes Teil trägt deshalb sein Spiel als Gravur
  (Millimeter je Seite). Beurteilt wird mit der Hand. Je Serie zwei Zahlen aufschreiben:
    ENG  = engste Variante, die ohne Gewalt passt (mit leichtem Fingerdruck, ohne Hebeln)
    WEIT = weiteste Variante, die noch nicht merklich wackelt
  Liegt der Wert dazwischen, wird er der neue Sollwert. Die Probestück-Werte stehen in jeder Zeile als Vergleich.

Alle Serien sind voneinander unabhängig (jede Fuge hat genau eine Serie), also alle in einem Druck.
Nach Gefühl geprüft wird alles außer K; K misst Durchgang.

Dateien (alle in Druckausrichtung, einfarbig, keine Stützen, keine Brims an Schieber und Plättchen)
  K_contact_spacers.stl   3 Plättchen 1,2 / 1,8 / 2,4 mm   ≈ 1,0 g
  N_sliders.stl           4 Schieber, Spiel 0,05 / 0,10 / 0,15 / 0,20   ≈ 4,0 g   (Probestück: 0,15)
  S_floor_slabs.stl       4 Boden-Platten, Schachtspiel 0,05 / 0,10 / 0,15 / 0,20   ≈ 11,9 g   (Probestück: 0,20)
  C_cassette.stl          Kassette wie im Probestück (Lehre für S, zum Bestücken)   ≈ 3,6 g
  R_sleeves.stl           4 Buchsenhülsen, Spiel 0,08 / 0,12 / 0,16 / 0,20, ohne Rippen   ≈ 4,0 g   (Kassette: 0,22 mit Rippen)
  FM_mulde_rings.stl      3 Mulden-Ringe, Spiel 0,10 / 0,15 / 0,20   ≈ 19,7 g   (Probestück: 0,25)   OPTIONAL, schwerstes Teil
  D_fitprobe_v6.stl       Passprobe Winkelleiste, unverändert aus stl/steckmodul_probe/   ≈ 2,1 g   OPTIONAL

Ausbaustufen (Material und Druckzeit sind Schätzungen; die Zeit im Slicer hat Vorrang)
  Kern     K + N + S + C + R           ≈ 24 g    ≈ 3,1 h normaler Drucker, ≈ 1,1 h schneller Drucker
  + D      Passprobe dazu              ≈ 26 g    ≈ 3,4 h / 1,2 h
  alles    zusätzlich FM (Mulden-Ringe) ≈ 46 g    ≈ 5,6 h / 2,1 h
  Zeigt der Slicer für alles mehr als etwa 7 Stunden, FM weglassen (größtes Teil, 20 g) und in einer zweiten Nacht drucken.
  Platzbedarf aller Teile etwa 211 × 105 mm (Anordnungsvorschlag: vorschau/steckmodul_night1/anordnung.png).

Zuordnung der Ergebnisse zu den Konstanten in plug/parts.py
  Serie N → KEY_CLR      Serie S → KASS_CLR      Serie R → SNUG (Rippen RIB danach getrennt)
  Serie FM → CLR         Serie K → CEIL und FUNNEL_T (nur wenn 1,8 nicht hält)
  Das Gehäuse der Dupont-Buchse streut um ±0,3 mm. Vor dem Anprobieren die Breite der benutzten Buchsen mit der Schieblehre
  messen (Soll 10,16 mm) und beim Ergebnis dazuschreiben; Bauteilmaße von mehreren Zehnteln lassen sich messen, Spalte nicht.

Slicer-Einstellungen: dieselben wie für die späteren echten Teile, sonst gelten die Spielwerte nicht
  Düse 0,4 mm, Schichthöhe 0,2 mm, PLA, Wände 3 Linien, Füllung 15 %, Brückenerkennung an, keine Stützen.
  Elefantenfuß-Kompensation genau so, wie sie später gilt. Teile nicht umdrehen, nicht skalieren.
  Schieber und Plättchen ohne Rand, erste Schicht langsam (Schieber sind nur 1 mm dick und können sich verziehen).
  Die Boden-Platten haben über der Nut eine Brücke (siehe unten): Brückenerkennung nicht abschalten.
  Anordnung: die sieben STL einzeln importieren und vom Slicer anordnen lassen (Schicht für Schicht, nicht Objekt für Objekt).
  Der Vorschlag in anordnung.png braucht 211 × 105 mm.
  Lösen sich die Boden-Platten (S) vom Bett (kleine Auflagefläche, nur die Ränder um die Nut), einen Brim von 3 mm nur außen ergänzen.

Was gibt es dazu zu prüfen?

  K  Kontakt-Tiefe (das Gate, entscheidet Höhen)
     Aufbau: Winkelleiste mit den Pins nach oben, Plättchen auf den Körper stecken, Buchse (mit gecrimpten Kontakten) von oben
     bis auf das Plättchen drücken. Die Einstecktiefe der Pins in der Buchse ist E = 5,68 − t.
       Plättchen 1,2  →  E = 4,48 mm     Plättchen 1,8  →  E = 3,88 mm (Sollwert)     Plättchen 2,4  →  E = 3,28 mm
     Messen: Durchgang jedes Kontakts mit dem Multimeter beim Wackeln (±0,5 mm, leicht kippen). Möglichst mit dem kürzesten Pin.
     Auswertung: hält 2,4 → Reserve. Hält ab 1,8 → so lassen. Hält nur 1,2 → CEIL und FUNNEL_T auf 0,6 (alle Höhen neu, N hinfällig).
     Hält nirgends → Dupont-Kontakt ungeeignet. Bild: vorschau/steckmodul_night1/kontakt_stapel.png

  N  Schieber in der Nut, S  Kassette im Schacht (mit der Kassette C als Lehre; beides zusammen an einer Platte prüfen)
     Eine Platte (egal welche, die Nut ist bei allen gleich) mit der Gravur nach oben auf den Tisch legen. Den Schieber mit der Gravur
     nach oben von der Seite einschieben, an der die Nut offen ist, bis er am geschlossenen Nutende anschlägt. Die Griffkerbe liegt am
     hinteren Ende und dient zum Herausziehen.
       N: Welcher Schieber gleitet mit leichtem Fingerdruck? Fällt er beim Hochhalten heraus? Ist er flach (Lineal)? Geht ein
          Dupont-Stift durch alle vier Trichterlöcher?
     Dann die Kassette von oben in den Schacht setzen, die Buchsenöffnung nach unten: sie liegt auf dem Schieber wie im Gebäude.
       S: Welche Platte lässt die Kassette ohne Kraft einsinken, und bei welcher wackelt sie spürbar? Das Spiel gilt in x und y.
     Zusammenhang: 0,20 (Platte) ist der Probestück-Wert, der als "wackelt" bekannt ist. Die engere Platte zeigt, wie weit es geht.
     Bild: vorschau/steckmodul_night1/schnitt_platte_schieber_kassette.png

  C  Kassette: Buchse mit der Steckseite zur offenen Unterseite eindrücken, Adern in den Aderschlitz, Streifen in die Ablage
     (13,0 × 21,0 mm), DETECT-Brücke in die Querrinne. Prüfen: Buchse fest ohne Werkzeug? Rastfenster-Seite frei?
     Beide Streifenbreiten (10 und 12 mm) passen? Wird mit mehreren Buchsen probiert (Gehäusebreite ±0,3 mm!), ist das Ergebnis belastbarer.

  R  Buchsenhülsen: dieselbe Buchse in jede Hülse drücken. ENG = engste, in die sie ohne Gewalt geht; WEIT = weiteste ohne Wackeln.
     Mit zwei bis drei Buchsen probieren, weil das Gehäuse von Stück zu Stück um bis zu ±0,3 mm streut.

  FM Mulden-Ringe (optional): das bereits gedruckte Gebäude-Probestück (1_probestueck.stl, falls noch vorhanden) als Fuß mit dem Fuß nach
     unten in jeden Ring stellen (Kodierecke beachten, abgeschrägte Ecke).
     Welcher Ring lässt den Fuß ohne Klemmen bis zum Boden sinken, bei welchem wackelt er? Es gibt hier noch keine Federzunge
     (Rast und Haltekraft folgen in einer späteren Serie).

  D  Passprobe v6 (optional): Stufenhöhe 2,0 / 1,8 / 1,6 (Anleitung: plug/fit_test/page.html).

Bekannte Risiken beim Druck (bitte vor dem Start im Slicer-Vorschaubild ansehen)
  * Boden-Platten (S): über der Nut liegt eine waagerechte Decke in 1,0 mm Höhe, im Probestück (und damit hier) 209 mm² groß
    (bis 34 mm Spannweite quer). Das ist eine Brücke und kann durchhängen. Das wird so mitgetestet; hängt sie spürbar durch, ist
    das ein Ergebnis für das Gebäude.
  * Der Schacht ist 0,05 mm Spiel vermutlich zu eng. Er ist als Grenzwert gedacht; klemmt er, ist das die untere Grenze der Serie.
  * Die Gravur ist 0,4 bis 0,6 mm tief. Die Plättchen K haben bettseitig eine Senkung 0,3 mm an den Löchern (Elefantenfuß).
  * Wenn K scheitert (nur bei 1,2 hält): Schieberdicke (FUNNEL_T) ändert sich, die Schieber N werden dann neu gebraucht.
    Das Risiko dafür sind etwa 4 g.
