#!/usr/bin/env python3
"""Testbogen für die Fadenführung (Eckmuster P3 und P45): baut plug/thread/feedback.html aus feedback.template.html.

Führt durch die Teile aus plug/thread/build.py (plug/thread/stl/): Druckqualität, Aufbauen, Faden einfädeln, kräftig ziehen, Luft vergleichen. Zeichnungen aus
plug/thread/build_plan.py, Vorschaubilder aus plug/thread/vorschau/. Formularfelder nur fühlbar oder ja/nein (L24); die ZIP-Version wird abgefragt (L25, L33).

Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m plug.thread.build_feedback      # schreibt plug/thread/feedback.html
"""
import base64
import io
import json
import os

from PIL import Image

from plug.feedback.build import fld, opts, render_field
from plug.thread import build as B
from plug.thread import build_plan as BP
from plug.thread import params as P
from plug.thread.build_plan1 import de

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TEMPLATE = os.path.join(HERE, "feedback.template.html")
OUT = os.path.join(HERE, "feedback.html")
PREV = os.path.join(HERE, "vorschau")
STEPS = []


def img_uri(path, width):
    im = Image.open(path).convert("RGB")
    im = im.resize((width, int(im.size[1] * width / im.size[0])), Image.LANCZOS)
    b = io.BytesIO()
    im.save(b, "JPEG", quality=86, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()


def ch(*texts, first="– bitte wählen –"):
    return opts([("", first)] + [(str(i + 1), t) for i, t in enumerate(texts)])


def add(sid, title, tag, lead, instr, diagrams, fields, optional=False):
    STEPS.append(dict(id=sid, title=title, tag=tag, lead=lead, instr=instr, diagrams=diagrams, fields=fields, optional=optional, calc=None))


def both(prefix, label, options):
    """Dasselbe Feld für P3 und P45."""
    return [fld("%s-p3" % prefix, "P3 (3,0 mm Luft): %s" % label, "select", options), fld("%s-p45" % prefix, "P45 (4,5 mm Luft): %s" % label, "select", options)]


def steps():
    d3, d45 = P.pill(3.0), P.pill(4.5)
    c, cs = P.PILL["chamfer"], P.PILL["steg_chamfer"]
    add("z0", "Welche Teile", "0", "Kurz festhalten, was gedruckt wurde, damit ich die Ergebnisse dem richtigen Stand zuordnen kann.",
        ["ZIP: <code>faden_eckmuster_v%s.zip</code> mit vier STL (je Muster Plattenecke und Unterkasten-Ecke). Gedruckt ohne Stützen, mit „Thick bridges“." % B.VERSION,
         "Notiere Datum oder Namen der ZIP, die du gedruckt hast, und welche der beiden Varianten dabei waren."],
        [("img", os.path.join(PREV, "aufbau.png"), "Die beiden Eckmuster, Plattenecke über der Unterkasten-Ecke (auseinandergezogen): links P3, rechts P45.")],
        [fld("z0-zip", "Welche ZIP (Version oder Datum der Datei)?", "text", ph="z. B. faden_eckmuster_v1.zip"),
         fld("z0-var", "Welche Muster gedruckt?", "select", ch("P3 und P45", "nur P3", "nur P45")),
         fld("z0-sup", "Mit Stützen gedruckt?", "select", ch("nein, ohne Stützen", "ja, Stützen")),
         fld("z0-pr", "Drucker und Filament", "text", ph="z. B. Bambu A1, PLA schwarz"),
         fld("z0-time", "Druckzeit insgesamt in Stunden", "text", ph="z. B. 1,5")])
    add("q", "Druck ansehen", "1", "Bevor etwas gefädelt wird: die Tasche von unten ansehen. Hier zeigt sich, ob etwas zugeschmoddert ist, wie beim alten V.",
        ["Plattenecke mit der <b>Unterseite zu dir</b> halten. Die Tasche ist nach unten offen: runde Decke, in der Mitte der Steg, an beiden Seiten je ein Spalt mit Fase (%s mm am Rand, %s mm am Steg-Fuß)." % (de(c, 1), de(cs, 1)),
         "Mit dem Fingernagel über die <b>Fasen</b> und die Kante am Bett fahren. Mit einem Stück Faden oder Draht über den <b>Steg</b> streichen: Ist die Luft darüber frei, hängt die Decke durch, sind Fäden oder Reste da?",
         "Unterkasten-Ecke: Eckaussparung und Wände ansehen; nichts abgebrochen?"],
        [("img", os.path.join(PREV, "unterseite.png"), "Plattenecken von unten (P3 links, P45 rechts): Tasche mit Fase, Steg in der Mitte."),
         ("img", os.path.join(PREV, "schnitt.png"), "Schnitt längs durch die Tasche: runde Decke, Steg, Luft darüber, Fase an den Rändern (Stufen sind die Schichten).")],
        both("q-decke", "Decke der Tasche (von unten)", ch("glatt", "leicht durchgehängt", "stark durchgehängt oder Fäden")) +
        both("q-offen", "Luft über dem Steg frei, nichts zugeschmoddert", ch("ja, ganz frei", "kleine Reste, lassen sich entfernen", "nein, zu")) +
        both("q-steg", "Steg", ch("sauber und gerade", "Stufen, aber glatt genug", "schief, rau oder gerissen")) +
        [fld("q-fase", "Fasen an Rand und Steg-Fuß", "select", ch("glatt, Elefantenfuß ausgeglichen", "leichter Wulst", "starker Wulst")),
         fld("q-ub", "Unterkasten-Ecken", "select", ch("heil", "verbogen", "etwas abgebrochen"))])
    add("a", "Aufbauen", "2", "Plattenecke auf die Unterkasten-Ecke setzen und auf den „Hut“ stellen.",
        ["Plattenecke mit der Unterseite nach unten auf die zugehörige Unterkasten-Ecke setzen: Die Eckaussparung liegt dann unter der Tasche.",
         "Beides auf ein Stück Filz oder Pappe (etwa 60 × 60 mm) stellen, das den Hut spielt."],
        [("svg", BP.svg_pill_section(3.0, thread=False, label="Tasche über der Eckaussparung"), "P3 im Schnitt: Tasche, Steg und die offene Eckaussparung darunter, unten der „Hut“.")],
        both("a-flat", "Plattenecke liegt auf dem Unterkasten", ch("rundum flach", "kleiner Spalt", "klafft oder wackelt")) +
        both("a-notch", "Eckaussparung lässt unter der Tasche genug Platz", ch("ja, Hand und Faden kommen gut hin", "knapp", "zu klein")))
    add("f", "Faden einfädeln", "3", "Der Hauptversuch: Faden von unten durch den linken Spalt (A), über den Steg, durch den rechten Spalt (B) wieder nach unten. Nur mit Faden, so wie du ihn für den Hut nimmst.",
        ["Das Fadenende von unten in den linken Spalt (<b>Eingang A</b>) stecken, über den Steg legen und im rechten Spalt (<b>Ausgang B</b>) nach unten herausfallen lassen. Die Fasen sollen dir helfen, die Öffnung zu treffen.",
         "Wenn es mit dem Faden allein nicht geht: Nadel, Pinzette oder gebogenen Draht nehmen und aufschreiben, womit.",
         "Das an <b>P3</b> und an <b>P45</b>."],
        [("svg", BP.svg_pill_section(3.0, thread=True, loop=True, label="Faden von A über den Steg nach B"), "P3: Faden (rot) von A über den Steg nach B."),
         ("svg", BP.svg_pill_section(4.5, thread=True, loop=True, label="Faden von A über den Steg nach B bei 4,5 mm Luft"), "P45: dasselbe mit 4,5 mm Luft.")],
        both("f-treff", "Eingang A mit dem Faden treffen", ch("trifft von selbst, die Fase führt", "mit etwas Zielen", "schwer zu treffen")) +
        both("f-ein", "Faden über den Steg bringen (nur Faden)", ch("leicht", "mit Mühe oder mehreren Versuchen", "nicht möglich ohne Hilfsmittel")) +
        both("f-aus", "Faden im Ausgang B nach unten bekommen", ch("fällt von selbst durch", "braucht etwas Nachhelfen", "nicht möglich")) +
        [fld("f-tool", "Hilfsmittel, wenn nötig", "select", opts([("", "– keins nötig –"), ("1", "Nadel"), ("2", "Pinzette"), ("3", "gebogener Draht oder Büroklammer"), ("4", "mehrere zusammen")])),
         fld("f-fase", "Hilft die Fase beim Treffen von Ein- und Ausgang", "select", ch("ja, deutlich", "ein bisschen", "nein, nicht spürbar")),
         fld("f-fase-n", "Fase", "select", ch("passt so", "größer wäre besser", "kleiner reicht"))])
    add("z", "Anziehen und Ziehen", "4", "Der Faden muss die Platte auf den Unterkasten drücken können. Das Ganze wird jetzt belastet.",
        ["Beide Fadenenden durch den Filz stechen, <b>straff ziehen und verknoten</b>. Die Plattenecke soll dabei fest auf der Unterkasten-Ecke liegen.",
         "Dann <b>kräftig am Faden ziehen</b> (so, wie es am Hut bei einem Ruck passieren könnte). Bleibt die Plattenecke liegen? Verformt sich der Steg, bricht etwas?",
         "Faden ein paarmal hin- und herziehen: läuft er glatt, oder hakt er an Steg, Decke oder Fase?"],
        [],
        both("z-hold", "Anziehen: Plattenecke auf dem Unterkasten", ch("zieht fest auf, hält", "bleibt ein Spalt", "gibt nach")) +
        both("z-steg", "Steg nach kräftigem Ziehen", ch("unverändert", "sichtbar verformt", "gerissen oder gebrochen")) +
        both("z-glatt", "Faden beim Hin- und Herziehen", ch("läuft glatt", "hakt leicht an einer Kante", "klemmt oder scheuert stark")) +
        [fld("z-wo", "Wo hakt der Faden (falls)", "text", ph="z. B. Steg-Kante, Fase, Decke"),
         fld("z-fest", "Wie fest kam sie dir vor", "select", ch("fester als nötig", "fest genug", "zu locker"))])
    add("l", "Luft vergleichen", "5", "Welche Luft über dem Steg ist besser: 3,0 oder 4,5 mm?",
        ["Beide Muster nebeneinander legen und die Ergebnisse vergleichen. 4,5 mm Luft heißt: Decke 9,0, Material darüber nur %s mm." % de(d45["roof"], 1)],
        [],
        [fld("l-luft", "Welche Luft", "select", ch("3,0 reicht, so lassen", "4,5 ist deutlich besser", "kein Unterschied", "weder noch, anders (Freitext)")),
         fld("l-dicke", "Material über der Decke bei P45 (%s mm)" % de(d45["roof"], 1), "select", ch("wirkt stabil genug", "wirkt zu dünn", "nicht beurteilt"))])
    add("s", "Abschluss", "Σ", "Zum Schluss ein Gesamteindruck. Danach unten den Text kopieren und mir schicken.",
        ["Überlege, ob die halbe Pille mit Steg so in die vier Ecken der großen Platte übernommen werden kann."],
        [],
        [fld("s-ok", "Fadenführung insgesamt", "select", ch("taugt, so in die große Platte übernehmen", "taugt mit Änderungen (Freitext)", "taugt nicht, anderes Konzept")),
         fld("s-next", "Was als Nächstes", "select", ch("in Oberplatte und Unterkasten der großen Platte übernehmen", "Maße anpassen und noch einmal testen", "Fadenführung anders lösen"))])


def render_diagram(step):
    out = []
    for kind, a, cap in step["diagrams"]:
        if kind == "img":
            out.append('<figure class="dg"><img src="%s" alt="%s"><figcaption>%s</figcaption></figure>' % (img_uri(a, 900), cap, cap))
        else:
            out.append('<figure class="dg"><div class="dgbox">%s</div><figcaption>%s</figcaption></figure>' % (a, cap))
    return "".join(out)


def build_steps_html():
    out, nav, spec = [], [], []
    for st in STEPS:
        instr = "".join("<li>%s</li>" % x for x in st["instr"])
        form = "".join(render_field(f) for f in st["fields"])
        opt = ' <span class="opt">optional</span>' if st["optional"] else ""
        out.append(
            '<section class="step" id="s-%s" data-step="%s"><header><span class="tg">%s</span><h2>%s%s</h2><span class="done" aria-hidden="true"></span></header>'
            '<p class="lead">%s</p><div class="cols"><ol class="how">%s</ol><div style="display:flex;flex-direction:column;gap:12px;min-width:0">%s</div></div>'
            '<form class="fb" onsubmit="return false"><h3>Feedback</h3><div class="grid">%s'
            '<label class="fld wide" for="f-%s-free"><span>Notizen, Auffälligkeiten (Freitext)</span><textarea id="f-%s-free" data-fid="%s-free" rows="2" placeholder="alles, was nicht in die Auswahl passt"></textarea></label>'
            '</div></form></section>' % (st["id"], st["id"], st["tag"], st["title"], opt, st["lead"], instr, render_diagram(st), form, st["id"], st["id"], st["id"]))
        nav.append('<a href="#s-%s" data-nav="%s" title="%s">%s</a>' % (st["id"], st["id"], st["title"], st["tag"]))
        spec.append(dict(id=st["id"], tag=st["tag"], title=st["title"], optional=st["optional"],
                         items=[dict(id=f["id"], label=f["label"], kind=f["kind"], map={x["v"]: x["t"] for x in f["opts"] if x["v"]}) for f in st["fields"]]
                         + [dict(id=st["id"] + "-free", label="Notizen", kind="text", map={})], calc=None))
    return "\n".join(out), "".join(nav), spec


def main():
    steps()
    html, nav, spec = build_steps_html()
    with open(TEMPLATE, encoding="utf-8") as f:
        page = f.read()
    for k, v in {"{{STEPS}}": html, "{{NAV}}": nav, "{{SPEC}}": json.dumps(spec, ensure_ascii=False)}.items():
        page = page.replace(k, v)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(page)
    print("geschrieben: %s (%d kB), %d Schritte, %d Felder" % (os.path.relpath(OUT, ROOT), os.path.getsize(OUT) / 1024, len(STEPS), sum(len(s["fields"]) for s in STEPS)))


if __name__ == "__main__":
    main()
