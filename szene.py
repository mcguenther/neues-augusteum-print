#!/usr/bin/env python3
"""Szene für die Farbmessung: Gebäudenetze in lokalen Metern, Sonnenstand, Geo-Umrechnung.

Die Netze kommen aus dem LoD2-Modell (ebene Fassaden, genau die Grundrisse und
Höhen, mit denen auch die Fassaden-Zonen in data/fassaden/*.json arbeiten).
Koordinaten: x = Ost, y = Nord (lokales System von generate.py, Ursprung
generate.ORIGIN), z = Höhe über NHN minus Z0 (Z0 ≈ Platzniveau).
"""
import datetime as dt
import math
import os
import pickle

import numpy as np
import trimesh

import generate as G

Z0 = 114.0                      # m ü. NHN, Bezug für z der Szene
CACHE = os.path.join(G.HERE, "data", "cache", "szene_%s.pkl")


def lonlat_to_local(lon, lat):
    """Geografische Länge/Breite -> lokale Meter (x Ost, y Nord)."""
    lon0, lat0 = G.ORIGIN
    return ((lon - lon0) * 111320.0 * math.cos(math.radians(lat0)), (lat - lat0) * 110540.0)


def laden(quelle="lod2"):
    """{slug: (Netz in Szenenkoordinaten, dz)}; Netz-z ist absolut (z_lokal + dz), z_lokal = Höhe über
    Gebäudeboden wie in den Fassaden-Zonen. quelle: "lod2" (wenige Dreiecke, schnell) oder "laserscan"."""
    path = CACHE % quelle
    if os.path.exists(path):
        return pickle.load(open(path, "rb"))
    models = G.source_models(quelle, 1.0)
    out = {}
    for slug, (solid, fp, info) in models.items():
        tm = G.to_trimesh(solid)
        dz = info["ground_z"] - Z0
        m = trimesh.Trimesh(tm.vertices + [0, 0, dz], tm.faces.copy(), process=False)
        out[slug] = (m, dz)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    pickle.dump(out, open(path, "wb"))
    return out


def gesamt(szene=None, quelle="lod2"):
    """Alle Gebäude als ein Netz + Gebäudenummer je Dreieck (Reihenfolge der Slugs)."""
    szene = szene or laden(quelle)
    slugs = list(szene)
    ms = [szene[s][0] for s in slugs]
    mesh = trimesh.util.concatenate(ms)
    bid = np.concatenate([np.full(len(m.faces), i) for i, m in enumerate(ms)])
    return mesh, bid, slugs


# --------------------------------------------------------------------------
# Sonne (NOAA-Näherung, Genauigkeit ~0,1°)
# --------------------------------------------------------------------------
def sonne(zeit_utc, lon=None, lat=None):
    """Sonnenstand (Azimut Kompass °, Höhe °) und Richtung zur Sonne (ENU-Einheitsvektor)."""
    lon = G.ORIGIN[0] if lon is None else lon
    lat = G.ORIGIN[1] if lat is None else lat
    t = zeit_utc
    n = t.toordinal() - dt.date(2000, 1, 1).toordinal() - 0.5 + (t.hour + t.minute / 60 + t.second / 3600) / 24 + 1.0
    L = (280.460 + 0.9856474 * n) % 360
    g = math.radians((357.528 + 0.9856003 * n) % 360)
    lam = math.radians(L + 1.915 * math.sin(g) + 0.020 * math.sin(2 * g))
    eps = math.radians(23.439 - 0.0000004 * n)
    ra = math.atan2(math.cos(eps) * math.sin(lam), math.cos(lam))
    dec = math.asin(math.sin(eps) * math.sin(lam))
    gmst = (18.697374558 + 24.06570982441908 * n) % 24
    ha = math.radians((gmst * 15 + lon) % 360) - ra
    la = math.radians(lat)
    alt = math.asin(math.sin(la) * math.sin(dec) + math.cos(la) * math.cos(dec) * math.cos(ha))
    az = math.atan2(-math.sin(ha) * math.cos(dec),
                    math.sin(dec) * math.cos(la) - math.cos(dec) * math.sin(la) * math.cos(ha)) % (2 * math.pi)
    az_d, alt_d = math.degrees(az), math.degrees(alt)
    v = np.array([math.sin(az) * math.cos(alt), math.cos(az) * math.cos(alt), math.sin(alt)])
    return az_d, alt_d, v


def zeit_utc(text, tz="Europe/Berlin"):
    """ISO-Zeitstempel (mit oder ohne Zeitzone; ohne = Ortszeit tz) -> naive UTC-datetime."""
    from zoneinfo import ZoneInfo
    s = text.replace("Z", "+00:00").replace(" ", "T", 1) if "T" not in text else text.replace("Z", "+00:00")
    t = dt.datetime.fromisoformat(s)
    if t.tzinfo is None:
        t = t.replace(tzinfo=ZoneInfo(tz))
    return t.astimezone(dt.timezone.utc).replace(tzinfo=None)


if __name__ == "__main__":
    # Plausibilität: Leipzig, 21.6.2025 12:00 UTC -> Sonne etwa Süd-Südwest, Höhe ~ 61°
    print(sonne(dt.datetime(2025, 6, 21, 12, 0))[:2])
    print(sonne(dt.datetime(2025, 3, 22, 10, 30))[:2])
    for s, (m, dz) in laden().items():
        print(s, len(m.faces), round(dz, 2))
