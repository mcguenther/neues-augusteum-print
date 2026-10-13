"""Phasenzeiten des Ist-Stands: wraps wichtige Funktionen mit Zeitmessung."""
import sys, time, json, os, collections
sys.path.insert(0, "/home/user/neues-augusteum-print")
import generate as G
T = collections.OrderedDict()
def wrap(mod, name, label=None):
    f = getattr(mod, name); label = label or f"{mod.__name__}.{name}"
    def w(*a, **k):
        t = time.perf_counter()
        try: return f(*a, **k)
        finally: T[label] = T.get(label, 0) + time.perf_counter() - t
    setattr(mod, name, w)
import laserscan, lod2, preview, fassaden, farben
for m, n in [(G,"osm_models"),(G,"refresh_colours"),(G,"colourise"),(G,"export_3mf"),(G,"render_coloured"),(G,"export"),
             (G,"split_tiles"),(G,"engrave_labels"),(G,"union"),(G,"to_trimesh"),
             (laserscan,"load_points"),(laserscan,"building_grid"),(laserscan,"heightfield_solid"),(laserscan,"models"),
             (lod2,"models"),(lod2,"load_lod2"),(preview,"default_previews"),(preview,"readme_assets"),(fassaden,"check")]:
    wrap(m, n)
t0 = time.perf_counter()
sys.argv = ["generate.py"] + sys.argv[1:]
G.main()
T["GESAMT"] = time.perf_counter() - t0
json.dump(T, open(os.environ["OUT"], "w"), indent=1)
for k, v in T.items(): print("%-32s %8.1f s" % (k, v))
