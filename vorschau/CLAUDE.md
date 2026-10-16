# Bildkatalog `vorschau/` (was man im Chat zeigt)

Wird geladen, sobald Dateien unter `vorschau/` gelesen werden. Die Regel „Vorschaubilder im Chat – immer“ (Bild zuerst mit `Read` prüfen,
dann mit `SendUserFile`, display `render`, zeigen) steht in der `CLAUDE.md` im Repo-Wurzelverzeichnis. Alles hier ist erzeugt
(`generate.py`, `preview.py`) und wird mit eingecheckt; nie von Hand ändern. Zum Iterieren entstehen die Bilder in `vorschau-fast/` (gitignored).

- Überblick: `vorschau.png` (Gesamtmodell 1:1500, Laserscan-Variante, farbig)
- README-Bilder (farbig, transparent, ohne Beschriftung): `vorschau/readme/`
- Vergleich der Datenquellen: `vorschau/vergleich_1zu1000.png` (alle Einzelgebäude,
  OSM | LoD2 | Laserscan nebeneinander), `vorschau/vergleich/<name>_1zu1000.png`,
  `vorschau/vergleich_farbig_ost.png`
- Alle Einzelgebäude einer Quelle: `vorschau/<quelle>/einzelgebaeude_1zu1000.png`
- Geändertes Gebäude bzw. geänderte Datei: `vorschau/<quelle>/<maßstab>/<name>.png`
- Farben: `vorschau/farben.png`, Gegenüberstellung Foto | alt | neu `vorschau/farbvergleich/index.html`
  (und die Bilder darin)
- Profile mit 3/4 Filamenten: `vorschau/filamente_vergleich.png` (alle Farben | 4 | 3, je
  Gesamtmodell, Seminargebäude-Bänder, Paulinum-Fenster), `vorschau/laserscan/1zu1500/komplett_campus_mit_extras_farbig_ost_<N>filamente.png`

Weitere Ordner: `steckmodul_*/` (Bilder des Steckmechanismus, siehe `plug/CLAUDE.md`), `fassaden/` (Zonenprüfung, `python3 fassaden.py <slug>`),
`farbvergleich/` und `farbvergleich_runde2/` (HTML-Berichte der Fotomessung, siehe `werkzeuge/farbmessung/CLAUDE.md`; die 3,3-MB-Seite nicht lesen).
