"""Mapa de los puntos de comparación (fondo) de la fase 1.

Lee data/variables_fase1.csv y escribe docs/img/fase1_fondo.png.
Uso, desde la raíz del repo:  python scripts/fase1_fondo.py
"""
import sys, json, numpy as np, pandas as pd, matplotlib.pyplot as plt, shapely
from shapely.geometry import shape, box
from scipy.stats import gaussian_kde
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyBboxPatch, Rectangle
VARS = sys.argv[1] if len(sys.argv) > 1 else "data/variables_fase1.csv"
LAND = sys.argv[2] if len(sys.argv) > 2 else "data/ne_10m_land.geojson"
OUT = sys.argv[3] if len(sys.argv) > 3 else "docs/img/fase1_fondo.png"
FONDO, TEXTO, SUAVE, REJILLA, TIERRA = "#071A2C", "#EAF2F4", "#8FB3BF", "#15314A", "#D8CFBD"
plt.rcParams.update({"font.family": "DejaVu Sans", "text.color": TEXTO})
d = pd.read_csv(VARS)
O, E, S_, N = -82.5, -77.0, 1.4, 7.4
B = box(O - .5, S_ - .5, E + .5, N + .5)
land = shapely.unary_union([g for g in (shape(f["geometry"]).intersection(B) for f in json.load(open(LAND))["features"]) if not g.is_empty])
bg = d[d.tipo == "fondo"]; pres = d[d.tipo != "fondo"]
gx, gy = np.meshgrid(np.linspace(O, E, 400), np.linspace(S_, N, 440))
z = gaussian_kde(np.vstack([bg.lon, bg.lat]), bw_method=0.08)(np.vstack([gx.ravel(), gy.ravel()])).reshape(gx.shape)
z = z / z.max()
cm = LinearSegmentedColormap.from_list("f", ["#0A2540", "#103A5A", "#1B5E7E", "#2FA3B4", "#6FD9D2", "#C9FBF4"])
niveles = [0, .03, .07, .15, .3, .55, 1.01]
fig = plt.figure(figsize=(10, 11), dpi=200); fig.patch.set_facecolor(FONDO)
ax = fig.add_axes([0.06, 0.07, 0.9, 0.78]); ax.set_facecolor("#0A2540")
ax.contourf(gx, gy, z, levels=niveles, colors=[cm(i / 5) for i in range(6)], zorder=1, antialiased=True)
for p in getattr(land, "geoms", [land]): ax.fill(*p.exterior.xy, color=TIERRA, ec="#B9AE98", lw=0.5, zorder=2)
ax.scatter(pres.lon, pres.lat, s=10, c="#FFF6E0", lw=0.4, edgecolors="#06182B", zorder=3)
ax.set_xlim(O, E); ax.set_ylim(S_, N); ax.set_aspect("equal")
ax.set_xticks(range(-82, -76)); ax.set_yticks(range(2, 8))
ax.set_xticklabels([f"{-v}°O" for v in range(-82, -76)]); ax.set_yticklabels([f"{v}°N" for v in range(2, 8)])
ax.tick_params(colors=SUAVE, labelsize=9, length=0)
for s in ax.spines.values(): s.set_visible(False)
# anotaciones directas
def nota(x, y, t, ha="left"):
    ax.text(x, y, t, fontsize=10.5, color=TEXTO, ha=ha, va="center", zorder=6, linespacing=1.4,
            bbox=dict(boxstyle="round,pad=0.5", fc=FONDO, ec=REJILLA, alpha=0.9))
nota(-80.9, 6.55, "Mar adentro casi nadie observa:\naquí el modelo toma\npocos puntos de comparación")
nota(-80.15, 3.55, "Cerca de la costa hay más\nobservadores: aquí toma\nmuchos puntos de comparación")
# convenciones
lx, ly = -82.3, 2.6
ax.add_patch(FancyBboxPatch((lx - .12, 1.55), 2.75, 1.4, boxstyle="round,pad=0,rounding_size=0.05", fc=FONDO, ec=REJILLA, lw=1, alpha=0.92, zorder=8))
ax.text(lx - .02, ly + .17, "Convenciones", fontsize=11.5, fontweight="bold", va="center", zorder=9)
ax.scatter([lx + .05], [ly - .13], s=40, c="#FFF6E0", edgecolors="#06182B", lw=.5, zorder=9)
ax.text(lx + .2, ly - .13, f"Registros de ballena ({len(pres):,})".replace(",", "."), fontsize=10, va="center", zorder=9)
ax.text(lx - .02, ly - .45, "Densidad de puntos de comparación", fontsize=10, va="center", zorder=9)
for i in range(6): ax.add_patch(Rectangle((lx - .02 + i * .4, ly - .78), .4, .14, color=cm(i / 5), lw=0, zorder=9))
ax.text(lx - .02, ly - .88, "pocos", fontsize=8.5, color=SUAVE, va="top", zorder=9)
ax.text(lx + 2.38, ly - .88, "muchos", fontsize=8.5, color=SUAVE, va="top", ha="right", zorder=9)
fig.text(0.06, 0.955, "Contra qué se compara cada ballena", fontsize=19, fontweight="bold")
fig.text(0.06, 0.925, "Para saber qué mar prefieren las ballenas, el modelo compara sus registros con 10.000 puntos de comparación.", fontsize=11, color=SUAVE)
fig.text(0.06, 0.903, "Esos puntos se ubican donde hay más gente observando, para que la diferencia la explique el mar y no el turismo.", fontsize=11, color=SUAVE)
fig.text(0.06, 0.025, "Fuentes: GBIF.org, OBIS, Natural Earth. Elaboración: Tatiana Zamudio.", fontsize=8.5, color=SUAVE)
plt.savefig(OUT, facecolor=FONDO)
