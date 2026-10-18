"""Maße des Display-Körpers E2b (Display vorn, Block mit Kassette dahinter, einstufig) im lokalen Rahmen.

x = 0 an der Ostkante der Mulde, nach Westen negativ; z = 0 an der Plattenoberfläche, nach unten negativ; y quer (Breite), Mitte 0.
Alles Planwerte aus `plug/display/params.py`; nichts davon ist gedruckt.
"""
import math

from plug.display import layout as L
from plug.display import params as D


def dims():
    P = D.DISP
    d = {}
    d["W"] = L.W_FOOT                                   # Breite der Mulde (y)
    d["slab"] = L.SLAB                                  # Wand vorn + Spiel + Modulschlitz + Rückwand
    slot_t = P["mod_t"] + 2 * D.CLR
    d["x_front"] = -D.WALL                              # Rückseite der Vorderwand
    d["x_slot0"], d["x_slot1"] = -(D.WALL + slot_t), -D.WALL
    d["x_back"] = -(D.WALL + slot_t + D.BACK)           # Rückseite der Rückwand = −SLAB
    d["x_mod_front"] = -(D.WALL + D.CLR)                # Glasfront des Moduls
    d["x_mod_back"] = d["x_mod_front"] - P["mod_t"]
    d["x_chan0"], d["x_chan1"] = d["x_back"] - D.CHAN, d["x_back"]
    d["pe"] = L.DESIGNS["E2"]["pin_from_east"]          # Pin-Reihe von der Ostkante
    d["depth"] = L.DESIGNS["E2"]["depth"]
    d["x_shaft0"], d["x_shaft1"] = -(d["pe"] + D.KASS_D / 2), -(d["pe"] - D.KASS_D / 2)
    d["foot"] = -14.2
    d["z_cass"] = D.KASS_TOP
    d["z_lid0"] = D.KASS_TOP + D.AIR
    d["z_block"] = d["z_lid0"] + D.LID_T                # Dach des Blocks
    d["mb"] = L.module_bottom_z("E2")                   # Unterkante der Platine
    d["z_floor"] = d["mb"] - 0.6
    d["mt"] = d["mb"] + P["pcb_h"]
    d["z_cap0"] = d["mt"] + 0.3                         # Unterkante des Kopfdachs (im Körper, nach dem Modul von vorn eingeschoben)
    d["z_top"] = d["z_cap0"] + D.TOP_CAP
    d["blende_bottom"] = d["z_floor"]                   # Frontblende: von der Auflage im Fuß bis zum Kopfdach
    d["win_back"] = (d["mb"] - 0.6, d["mb"] + 8.0)      # Kabelfenster in der Rückwand (14 mm breit)
    d["wb"] = D.GAP_FRONT
    d["wt"] = D.GAP_FRONT + L.WIN_H
    d["z_pins"] = d["mb"] + P["hdr_edge"]               # Lage der Lötlöcher
    # Weg der Adern: aus der Kassette nach oben, in der Kammer zum Kanal, im Kanal nach unten, von hinten in die Löcher
    zc = D.KASS_TOP + D.AIR * 0.5
    xc = -(L.SLAB + D.CHAN / 2)
    xh = d["x_mod_front"] - 1.7 - P["pcb_t"] / 2        # Lochmitte in der Platine
    d["xh"] = xh + 1.0
    d["wire"] = [(-d["pe"], D.KASS_TOP), (-d["pe"], zc), (xc, zc), (xc, d["z_pins"] + 1.5), (d["xh"], d["z_pins"])]
    d["wire_len"] = round(sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(d["wire"], d["wire"][1:])), 1)
    d["lid"] = (d["x_shaft0"], d["x_chan1"])            # Deckel überdeckt Luftkammer und Kanal
    d["height_total"] = d["z_top"] - d["foot"]          # Körper von der Fußunterkante bis zur Kopfleiste
    return d
