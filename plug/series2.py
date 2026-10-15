#!/usr/bin/env python3
"""Zweiter Nachtdruck: Änderungen aus dem Ergebnis von Nacht 1 (Entscheidungen: plug/decision/page.html).

Ergebnis Nacht 1 (Kurzfassung, Wortlaut im Chat):
  K  kein stabiler Durchgang, Buchse ohne Halt; getestet mit leerem Gehäuse (keine Kontakte) → Test wiederholen, dünnere Plättchen
  N  alle vier Schieber klemmen; Decke über der Nut stark durchgehängt (34 mm Brücke), Fäden in der Nut, Elefantenfuß ≈ 0,2 mm
  S  0,15 ideal, 0,20 minimales Spiel
  C  Buchse nur mit Kraft (0,22 + Rippen), geht nicht ganz hinein; Adern knicken; Ablage 1 mm weiter weg von der Tasche
  R  0,20 ohne Rippen ideal
  D  überall schief; Körper liegt vermutlich auf der Stufe auf
  FM nicht getestet (Fuß-Lehre fehlte)
  Druck: schwarzes PLA, Gravur schlecht lesbar, Elefantenfuß ≈ 0,2 mm, Bambu, 2,5 h für alles

Hier stehen zuerst nur die Parameter (gemeinsame Quelle für Entscheidungsdokument und STL); die Geometrie folgt darunter.

Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m plug.series2      # STL, README.txt und ZIP nach stl/steckmodul_night2/, Vorschau nach vorschau/steckmodul_night2/
"""
from plug import dupont as sd

# ---- Entscheidungen aus Nacht 1 (neue Sollwerte, gelten ab jetzt für die Kassette)
KASS_CLR2 = 0.15       # S: 0,15 „mit Fingerdruck, kein Spiel“, 0,20 „minimales Spiel“ (alt 0,20)
SNUG2 = 0.20           # R: Hülse 0,20 ohne Rippen „ziemlich perfekt“ (alt 0,22 mit Rippen 0,12: „nur mit Kraft“)
RIB2 = 0.0             # keine Crush-Rippen mehr in der Buchsentasche
HSG_TOL2 = 0.45        # C: Tasche 0,2 mm höher, die Buchse ging nicht ganz hinein (alt 0,25)
ENTRY_CH = 0.4         # neue Regel: 45°-Einführfase an jeder Öffnung, in die etwas gesteckt wird
EF_CH = 0.3            # neue Regel: Fase an Bettkanten von Steckteilen (Elefantenfuß ≈ 0,2 mm)

# ---- Kassette v2 (Ablage höher, Übergang rund, Ablage 1 mm weiter weg)
SEAT_RISE = 0.5        # Unterkante der LED-Ablage liegt so weit über der Taschenoberkante (alt: 1,05 darunter)
GAP_L2 = sd.GAP_L + 1.0   # Abstand Tasche → Ablage 1 mm größer (C: „1 mm mehr Abstand Richtung Tasche“)
FILLET = 1.5           # Rundung der Kante zwischen Tasche und Aderkanal
WIRE_W = 9.2           # Breite des Aderkanals über der Tasche (vier Adern im 2,54-Raster, Ader 1,0)
SEAT_TOL = 0.25        # Ablage je Seite größer (C/LED: „Toleranz einplanen“), alt 0,15

# ---- N wird ersetzt: Bodenplatte zum Eindrücken statt Schieber in Schwalbenschwanz-Nut
B_MARGIN = 1.5         # Rand der Vertiefung um den Schacht (Auflage der Platte, nur kurzer Überhang statt 34-mm-Brücke)
B_CLR = (0.05, 0.10, 0.15, 0.20)   # Spiel der Platte in der Vertiefung je Seite (Presspassung bis lose)
B_T = sd.FUNNEL_T      # Plattendicke = Trichterplatte (1,0)
B_H = 8.0              # Höhe der Prüfkörper

# ---- K wiederholen, dünnere Plättchen (Einstecktiefe bis 5,1 mm)
K2_T = (0.6, 0.9, 1.2, 1.5, 1.8)

# ---- D: Körpertasche zum Lötende hin verlängern, Stufe entsprechend kürzer
D2_EXT = (0.5, 1.0, 1.5)

# ---- FM: Fuß-Lehre (Unterseite des Probestücks) für die schon gedruckten Mulden-Ringe
LEHRE_CAP = 2.0        # Deckel über dem Fuß


def e_of(t):
    """Einstecktiefe der Pins in der Buchse bei Plättchendicke t."""
    return sd.HDR_UP - t
