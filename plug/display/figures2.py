"""Zeichnungen der Planseite 2 (Aufbau und Zusammenbau des Display-Körpers E2b): Modul, Schnitt, Explosion, Grundriss."""
from plug.display import body
from plug.display import layout as L
from plug.display import params as D
from plug.display.figures import Svg, de

B = body.dims()
P = D.DISP


def _pins(g, x0, z, cls="pin"):
    for i in range(4):
        x = x0 + (i - 1.5) * P["hdr_pitch"]
        g.rect(x - 0.45, z - 0.45, x + 0.45, z + 0.45, cls)


def module_front():
    """Vorderansicht des Moduls in Einbaulage (Pinleiste unten), Maße aus den Fotos."""
    w, h = P["pcb_w"], P["pcb_h"]
    g = Svg(-w / 2 - 6, w / 2 + 12, -8.0, h + 5.0, 9.0)
    g.rect(-w / 2, 0, w / 2, h, "pcb")
    # Ausschnitt oben (FPC)
    g.rect(-P["notch_w"] / 2, h - P["notch_d"], P["notch_w"] / 2, h + 0.05, "notch")
    # Glas
    gt = 3.3
    g.rect(-P["panel_w"] / 2, h - gt - P["panel_h"], P["panel_w"] / 2, h - gt, "glass")
    # aktive Fläche und Sichtfenster
    aa0 = P["aa_bottom"]
    g.rect(-P["aa_w"] / 2, aa0, P["aa_w"] / 2, aa0 + P["aa_h"], "aa2")
    wm = D.WINDOW_MARGIN
    g.rect(-P["aa_w"] / 2 - wm, aa0 - wm, P["aa_w"] / 2 + wm, aa0 + P["aa_h"] + wm, "win2")
    # Löcher
    for sx in (-1, 1):
        for sz in (0, 1):
            x = sx * P["hole_dx"] / 2
            z = (h / 2 - P["hole_dy"] / 2) + sz * P["hole_dy"]
            g.rect(x - 1.5, z - 1.5, x + 1.5, z + 1.5, "hole")
    _pins(g, 0, P["hdr_edge"])
    g.text(w / 2 + 0.8, P["hdr_edge"], "4 Pins", "mut")
    g.dim_h(-w / 2, w / 2, -2.4, de(w))
    g.dim_v(-w / 2 - 2.6, 0, h, "", -1)
    g.text(-w / 2 - 3.4, h / 2, de(h), "num", "end")
    g.dim_v(w / 2 + 2.6, aa0, aa0 + P["aa_h"], "", 1)
    g.text(w / 2 + 3.4, aa0 + P["aa_h"] / 2, "aktiv %s" % de(P["aa_h"]), "ok", "start")
    g.text(0, h + 1.8, "oben: Ausschnitt für das FPC, Controllerstreifen", "mut", "middle")
    g.text(0, -6.2, "unten: Pins, im Fuß", "mut", "middle")
    return g.svg("modfront", "Vorderansicht des Moduls in Einbaulage")


# ----------------------------------------------------------------------------------------------- Schnitt
def wire_path(dx=0.0):
    """Weg der Adern; mit dx > 0 hängt das Modul um dx vor dem Körper an den Adern (Schritt 3)."""
    w = list(B["wire"][:-1])
    xc = -(L.SLAB + D.CHAN / 2)
    zp = B["z_pins"]
    if dx > 0:
        w = w[:4] + [(xc, zp), (B["xh"] + dx, zp)]
    else:
        w = w + [(B["xh"], zp)]
    return w


def section(flags=None, dx=None, dz=None, arrows=(), label="", ident="sec2", plate=True, notes=True, wire_dx=0.0, ztop=33.0, zbot=-24.0):
    """Längsschnitt durch die Mitte (y = 0, durch das Kabelfenster der Rückwand). flags: Teile, die gezeichnet werden; dx, dz: Versätze je Teil."""
    f = dict(body=True, cass=True, module=True, lid=True, blende=True, wires=True, dock=True)
    f.update(flags or {})
    ox = dict(body=0.0, cass=0.0, module=0.0, lid=0.0, blende=0.0)
    ox.update(dx or {})
    oz = dict(body=0.0, cass=0.0, module=0.0, lid=0.0, blende=0.0)
    oz.update(dz or {})
    xl, xr, z0, z1 = -34.0, 22.0, zbot, ztop
    g = Svg(xl, xr, z0, z1, 7.0)
    pb = -14.6
    if plate:
        g.rect(xl, pb, 4.1, 0, "plate")
        g.line(xl, 0, 4.1, 0, "tablel")
        g.text(xl + 0.6, -7, "Platte", "mut")
    if f["body"]:
        zb = B["z_top"]
        # Fuß in der Mulde und Block: Vollkörper, danach die Hohlräume
        g.rect(-B["depth"], B["foot"], -D.BLENDE_T, 0, "foot")
        g.rect(-D.BLENDE_T, B["foot"], 0, B["blende_bottom"], "foot")                # Fuß reicht unten bis zur Ostkante der Mulde, darauf steht die Blende
        g.rect(-B["depth"], 0, B["x_shaft0"], B["z_block"], "foot")                 # Westwand des Blocks, einstufig bis zum Dach
        g.rect(B["x_shaft1"], 0, B["x_chan1"], B["z_cass"], "foot")                 # Ostwand des Schachts nur bis zur Kassettenoberkante
        # Rückwand des Modultaschens (Taschenboden und Kopfdach) mit Kabelfenster
        g.rect(B["x_back"], 0, B["x_slot0"], B["win_back"][0], "foot") if B["win_back"][0] > 0 else None
        g.rect(B["x_back"], B["win_back"][1], B["x_slot0"], B["z_top"], "foot")
        g.rect(B["x_back"], B["z_cap0"], B["x_front"], B["z_top"], "foot")          # Kopfdach
        # Hohlräume im Fuß
        g.rect(B["x_shaft0"], B["foot"], B["x_shaft1"], B["z_cass"], "void")
        g.rect(B["x_chan0"], B["z_floor"], B["x_chan1"], 0, "void")
        g.rect(B["x_back"], B["win_back"][0], B["x_slot0"], B["win_back"][1], "void")
        g.rect(B["x_slot0"], B["z_floor"], B["x_slot1"], 0, "void")
        g.rect(B["x_chan1"] - 0.0, B["z_cass"], B["x_back"] + 0.0, B["z_block"], "void") if False else None
        # Rückwand ober- und unterhalb des Fensters hinter dem Schnitt: Pfeiler gestrichelt
        g.rect(B["x_back"], B["z_floor"], B["x_slot0"], B["win_back"][0], "ghost")
    if f["cass"]:
        g.rect(B["x_shaft0"] + 0.1, B["foot"] + oz["cass"], B["x_shaft1"] - 0.1, B["z_cass"] + oz["cass"], "kass")
    if f["lid"]:
        g.rect(B["lid"][0] - 0.6, B["z_lid0"] + oz["lid"], B["lid"][1] + 0.6, B["z_block"] + oz["lid"], "lid")
    if f["module"]:
        m0 = ox["module"]
        g.rect(B["x_mod_back"] + m0, B["mb"] + oz["module"], B["x_mod_front"] + m0, B["mt"] + oz["module"], "pcb")
        g.line(B["x_mod_front"] + m0, B["wb"] + D.WINDOW_MARGIN + oz["module"], B["x_mod_front"] + m0,
               B["wb"] + D.WINDOW_MARGIN + P["aa_h"] + oz["module"], "aa")
    if f["blende"]:
        b0 = ox["blende"]
        g.rect(-D.BLENDE_T + b0, B["blende_bottom"] + oz["blende"], 0 + b0, B["wb"] + oz["blende"], "blende")
        g.rect(-D.BLENDE_T + b0, B["wt"] + oz["blende"], 0 + b0, B["z_top"] + oz["blende"], "blende")
    if f["wires"]:
        g.poly(wire_path(wire_dx), "wire", close=False)
    if f["dock"] and plate:
        pe = B["pe"]
        g.rect(-(pe + 1.0), pb - 2.0, -(pe - 1.0), pb, "body")
        g.line(-pe, pb, -pe, -8.9, "pin")
        g.line(-pe, pb - 1.0, -pe - 6.3, pb - 1.0, "tail")
    for a in arrows:
        x0, zz0, x1, zz1 = a
        g.line(x0, zz0, x1, zz1, "arrow")
        g.o.append('<circle cx="%.1f" cy="%.1f" r="2.6" class="arrowhead"/>' % (g.X(x1), g.Y(zz1)))
    if notes:
        g.dim_v(-B["depth"] - 3.0, B["z_cass"], B["z_lid0"], "", -1)
        g.text(-B["depth"] - 4.0, (B["z_cass"] + B["z_lid0"]) / 2, "Luft %s" % de(D.AIR), "ok", "end")
        g.dim_v(5.0, 0, B["z_top"], "", 1)
        g.text(5.8, B["z_top"] / 2, de(B["z_top"]), "num", "start")
        g.dim_v(5.0, B["wb"], B["wt"], "", 1) if False else None
    if label:
        g.text(xl + 0.6, z1 - 2.0, label, "lab")
    return g.svg(ident, label or "Schnitt durch den Display-Körper")


def exploded():
    return section(dx=dict(module=16.0, blende=16.0), dz=dict(cass=-20.0, lid=14.0), flags=dict(wires=False), ident="sec-expl",
                   label="Explosion", notes=False, ztop=50.0, zbot=-33.0)


STEPS = [
    dict(t="Kassette bestücken", d="Dupont-Buchse mit vier Adern (55 mm) crimpen und in die Kassette drücken. Die Adern kommen oben aus dem Aderschlitz.", fig=None),
    dict(t="Kassette von unten einschieben", d="Die Kassette geht von der Fußunterseite in den Schacht, bis die Schultern an der Anschlagleiste im Schacht anliegen. Die Adern ziehst du oben durch Kammer, Kanal und Kabelfenster in die Tasche und vorn heraus.",
         fig=dict(flags=dict(module=False, lid=False, blende=False, dock=False), dz=dict(cass=-12.0), wire_dx=16.0,
                  arrows=[(-B["pe"], -22.0, -B["pe"], -14.5)])),
    dict(t="Adern am Modul anlöten", d="Header am Modul auslöten. Die Adern von hinten durch die Löcher stecken und vorn verlöten. Das Modul hängt dabei vor dem Körper an den Adern.",
         fig=dict(flags=dict(lid=False, blende=False, dock=False), dx=dict(module=16.0), wire_dx=16.0)),
    dict(t="Modul von vorn in die Tasche schieben", d="Das Modul gleitet in die Tasche, die überzähligen Adern schiebst du nach hinten in die Kammer über der Kassette. Dort werden sie gebogen (mindestens 4 mm Luft).",
         fig=dict(flags=dict(lid=False, blende=False, dock=False), dx=dict(module=8.0), wire_dx=8.0, arrows=[(10.0, 8.0, 2.0, 8.0)])),
    dict(t="Deckel und Frontblende aufsetzen", d="Der Deckel schließt Kammer und Kanal bündig im Blockdach. Die Frontblende mit dem Fenster klickt von vorn auf die Tasche und hält das Modul.",
         fig=dict(flags=dict(dock=False), dx=dict(blende=8.0), dz=dict(lid=6.0), arrows=[(-13.0, 22.0, -13.0, 10.0), (14.0, 14.0, 4.0, 14.0)])),
    dict(t="Stecken und prüfen", d="Den Körper in die Mulde der Platte stecken (Kassette auf die Pins der Winkelleiste). Danach I²C-Scan: 0x3C oder 0x3D und 0x40 müssen erscheinen.",
         fig=dict(flags={})),
]


def step_fig(i):
    st = STEPS[i]
    if not st["fig"]:
        return ""
    fg = st["fig"]
    return section(flags=fg.get("flags"), dx=fg.get("dx"), dz=fg.get("dz"), arrows=fg.get("arrows", ()), wire_dx=fg.get("wire_dx", 0.0),
                   ident="step%d" % i, label="Schritt %d" % (i + 1), notes=False, zbot=-33.0 if i == 1 else -24.0,
                   ztop=50.0 if i in (2, 4) else 40.0)


# ----------------------------------------------------------------------------------------------- Grundriss
def plan_view():
    """Draufsicht auf den Körper (Norden oben, Osten rechts): Mulde, Frontblende mit Fenster, Modultasche, Rückwand mit Kabelfenster, Kanal, Schacht, Deckel."""
    W = B["W"]
    g = Svg(-B["depth"] - 16.0, 8.0, -W / 2 - 5.0, W / 2 + 5.0, 10.0)
    g.rect(-B["depth"], -W / 2, 0, W / 2, "foot")
    g.rect(B["x_slot0"], -(P["pcb_w"] / 2 + D.CLR), B["x_slot1"], P["pcb_w"] / 2 + D.CLR, "void")             # Tasche
    g.rect(B["x_mod_back"], -P["pcb_w"] / 2, B["x_mod_front"], P["pcb_w"] / 2, "pcb")
    g.rect(B["x_back"] - 0.1, -D.SLIT_W / 2, B["x_slot0"] + 0.1, D.SLIT_W / 2, "void")                       # Kabelfenster
    g.rect(B["x_chan0"], -D.SLIT_W / 2, B["x_chan1"], D.SLIT_W / 2, "void")                                  # Kanal
    g.rect(B["x_shaft0"], -D.KASS_W / 2, B["x_shaft1"], D.KASS_W / 2, "void")                                # Schacht
    g.rect(B["x_shaft0"] + 0.1, -(D.KASS_W / 2 - 0.1), B["x_shaft1"] - 0.1, D.KASS_W / 2 - 0.1, "kass")
    g.rect(B["lid"][0] - 0.6, -(D.KASS_W / 2 + 1.0), B["lid"][1] + 0.6, D.KASS_W / 2 + 1.0, "lidv")           # Deckel
    g.rect(-D.BLENDE_T, -W / 2, 0, W / 2, "blende")                                                           # Frontblende
    g.rect(-D.BLENDE_T - 0.1, -(P["aa_w"] / 2 + D.WINDOW_MARGIN), 0.1, P["aa_w"] / 2 + D.WINDOW_MARGIN, "void")
    g.poly([(-B["pe"], 0), (-(L.SLAB + D.CHAN / 2), 0), (B["x_mod_back"], 0)], "wire", close=False)
    g.dim_h(-B["depth"], 0, -W / 2 - 2.6, "Tiefe %s" % de(B["depth"]))
    g.dim_v(-B["depth"] - 2.4, -W / 2, W / 2, "", -1)
    g.text(-B["depth"] - 3.2, 0, "Breite %s" % de(W), "num", "end")
    g.text(0.8, W / 2 + 1.5, "Osten", "mut", "start")
    g.text((B["x_slot0"] + B["x_slot1"]) / 2, W / 2 + 1.2, "Tasche", "lab", "middle")
    g.text((B["x_chan0"] + B["x_chan1"]) / 2, -D.SLIT_W / 2 - 1.2, "Kanal", "lab", "middle")
    g.text((B["x_shaft0"] + B["x_shaft1"]) / 2, D.KASS_W / 2 + 2.6, "Kassette", "lab", "middle")
    return g.svg("topv", "Draufsicht auf den Display-Körper")
