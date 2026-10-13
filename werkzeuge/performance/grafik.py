"""Balkengrafik: Laufzeit je Phase, Ist-Stand vs. Varianten. Liest scratchpad/results.json."""
import json, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

res = json.load(open(sys.argv[1]))      # [{name, phasen:{}, gesamt}]
out = sys.argv[2]
dark = len(sys.argv) > 3 and sys.argv[3] == "dark"
surf, ink, ink2, grid = ("#1a1a19", "#f0efec", "#c3c2b7", "#383835") if dark else ("#fcfcfb", "#0b0b0b", "#52514e", "#f0efec")
cols = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"] if not dark else ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181"]
phases = ["Modelle bauen, färben, exportieren", "Farbvorschauen (3D-Rendering)",
          "Vorschaubilder je Quelle + Quellenvergleich", "README-Bilder + README", "Fassaden-Prüfansichten"]
short = ["Modelle bauen/färben/exportieren", "Farbvorschauen (Rendering)", "Vorschaubilder + Quellenvergleich",
         "README-Bilder", "Fassaden-Prüfansichten"]
fig, ax = plt.subplots(figsize=(11, 0.9 * len(res) + 2.2), facecolor=surf)
ax.set_facecolor(surf)
y = list(range(len(res)))[::-1]
for r, yy in zip(res, y):
    left = 0
    for i, p in enumerate(phases):
        v = r["phasen"].get(p, 0)
        if v <= 0:
            continue
        ax.barh(yy, v, left=left, height=0.58, color=cols[i], edgecolor=surf, linewidth=2,
                label=short[i] if yy == y[0] else None)
        left += v
    ist = res[0]["gesamt"]
    lab = "%s  (%.0f s)" % (("%d min %02d s" % divmod(round(r["gesamt"]), 60)), r["gesamt"]) if r["gesamt"] >= 60 else "%.0f s" % r["gesamt"]
    if r is not res[0]:
        lab += "   ·  %.1f× schneller" % (ist / r["gesamt"])
    ax.text(left + ist * 0.01, yy, lab, va="center", color=ink, fontsize=10)
ax.set_yticks(y); ax.set_yticklabels([r["name"] for r in res], color=ink, fontsize=10)
ax.set_xlim(0, res[0]["gesamt"] * 1.32)
ax.set_xlabel("Laufzeit in Sekunden (Wanduhr, 4 Kerne)", color=ink2)
ax.tick_params(colors=ink2, length=0)
ax.xaxis.grid(True, color=grid); ax.set_axisbelow(True)
for s in ax.spines.values(): s.set_visible(False)
ax.set_title("generate.py: wo die Zeit hingeht – Ist-Stand und Varianten", color=ink, loc="left", fontsize=13, fontweight="bold")
leg = ax.legend(loc="lower right", frameon=False, fontsize=9, ncol=1)
for t in leg.get_texts(): t.set_color(ink2)
fig.tight_layout()
fig.savefig(out, dpi=140, facecolor=surf)
