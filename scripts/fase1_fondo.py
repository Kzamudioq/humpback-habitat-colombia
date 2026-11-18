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
# convenciones
lx, ly = -82.35, 2.15
ax.add_patch(FancyBboxPatch((lx - .08, 1.5), 1.95, 0.98, boxstyle="round,pad=0,rounding_size=0.04", fc=FONDO, ec=REJILLA, lw=1, alpha=0.92, zorder=8))
ax.text(lx, ly + .2, "Convenciones", fontsize=9.5, fontweight="bold", va="center", zorder=9)
ax.scatter([lx + .04], [ly - .01], s=22, c="#FFF6E0", edgecolors="#06182B", lw=.5, zorder=9)
ax.text(lx + .14, ly - .01, f"Registros de ballena ({len(pres):,})".replace(",", "."), fontsize=8.5, va="center", zorder=9)
ax.text(lx, ly - .22, "Densidad de puntos de comparación", fontsize=8.5, va="center", zorder=9)
for i in range(6): ax.add_patch(Rectangle((lx + i * .29, ly - .46), .29, .1, color=cm(i / 5), lw=0, zorder=9))
ax.text(lx, ly - .52, "pocos", fontsize=7.5, color=SUAVE, va="top", zorder=9)
ax.text(lx + 1.74, ly - .52, "muchos", fontsize=7.5, color=SUAVE, va="top", ha="right", zorder=9)
def justificado(fig, texto, x0, x1, y, size, color, interlinea=0.022):
    """Escribe un párrafo justificado entre x0 y x1 (coordenadas de la figura)."""
    r = fig.canvas.get_renderer(); W = fig.bbox.width
    def ancho(t):
        m = fig.text(0, 0, t, fontsize=size)
        w = m.get_window_extent(r).width / W
        m.remove()
        return w
    palabras = texto.split(); esp = ancho("a a") - 2 * ancho("a")
    medidas = {w: ancho(w) for w in palabras}
    lineas, actual = [], []
    for w in palabras:
        if actual and sum(medidas[p] for p in actual + [w]) + esp * len(actual) > x1 - x0:
            lineas.append(actual); actual = []
        actual.append(w)
    lineas.append(actual)
    for k, ln in enumerate(lineas):
        yy = y - k * interlinea
        if k == len(lineas) - 1 or len(ln) == 1:
            fig.text(x0, yy, " ".join(ln), fontsize=size, color=color); continue
        hueco = (x1 - x0 - sum(medidas[p] for p in ln)) / (len(ln) - 1)
        x = x0
        for w in ln:
            fig.text(x, yy, w, fontsize=size, color=color); x += medidas[w] + hueco
    return y - (len(lineas) - 1) * interlinea

justificado(fig, "Las yubartas llegan desde el sur de Chile y la Antártida a parir y criar en aguas cálidas, someras y protegidas. "
            "Para encontrar esas condiciones, el modelo compara sus registros con 10.000 puntos de comparación, ubicados donde hay "
            "más gente observando, para que la diferencia la explique el mar y no el turismo.",
            0.06, 0.94, 0.925, 11, SUAVE)
fig.text(0.06, 0.955, "Contra qué se compara cada ballena", fontsize=19, fontweight="bold")
fig.text(0.06, 0.025, "Fuentes: GBIF.org, OBIS, Natural Earth. Elaboración: Tatiana Zamudio.", fontsize=8.5, color=SUAVE)
plt.savefig(OUT, facecolor=FONDO)
