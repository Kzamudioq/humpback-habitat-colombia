"""Figuras de la fase 1 con la paleta del mapa.

Lee data/variables_fase1.csv y data/avistamientos_pacifico_co.csv
y escribe docs/img/fase1_fondo.png y docs/img/fase1_variables.png.
Uso, desde la raíz del repo:  python scripts/fase1_figuras.py
"""
import sys, json, numpy as np, pandas as pd, matplotlib.pyplot as plt, shapely
from shapely.geometry import shape, box
from scipy.stats import gaussian_kde
from matplotlib.patches import Rectangle, FancyBboxPatch

VARS = sys.argv[1] if len(sys.argv) > 1 else "data/variables_fase1.csv"
AVIS = sys.argv[2] if len(sys.argv) > 2 else "data/avistamientos_pacifico_co.csv"
LAND = sys.argv[3] if len(sys.argv) > 3 else "data/ne_10m_land.geojson"
OUT = sys.argv[4] if len(sys.argv) > 4 else "docs/img"
FONDO, PANEL, TEXTO, SUAVE, REJILLA = "#071A2C", "#0B2238", "#EAF2F4", "#8FB3BF", "#15314A"
C_FONDO, C_AV, C_TEL, TIERRA = "#5E7F96", "#5FE0D8", "#FF8A5B", "#D8CFBD"
plt.rcParams.update({"font.family": "DejaVu Sans", "text.color": TEXTO})

d = pd.read_csv(VARS)
av = pd.read_csv(AVIS)
O, E, S_, N = -82.5, -77.0, 1.4, 7.4

# ---------- 1. superficie de esfuerzo y puntos de fondo ----------
B = box(O - 0.5, S_ - 0.5, E + 0.5, N + 0.5)
land = shapely.unary_union([g for g in (shape(f["geometry"]).intersection(B)
                            for f in json.load(open(LAND))["features"]) if not g.is_empty])
gx, gy = np.meshgrid(np.linspace(O, E, 450), np.linspace(S_, N, 490))
z = gaussian_kde(np.vstack([av.lon, av.lat]), bw_method=0.15)(np.vstack([gx.ravel(), gy.ravel()])).reshape(gx.shape)
z = z / z.max()
z[shapely.contains_xy(land, gx, gy)] = np.nan

from matplotlib.colors import LinearSegmentedColormap
cm = LinearSegmentedColormap.from_list("esf", ["#0A2540", "#123E5E", "#1F6080", "#2FA3B4", "#8FF0E6"])
fig = plt.figure(figsize=(9.6, 10.4), dpi=200); fig.patch.set_facecolor(FONDO)
ax = fig.add_axes([0.08, 0.08, 0.88, 0.8]); ax.set_facecolor("#0A2540")
ax.imshow(np.sqrt(z), extent=(O, E, S_, N), origin="lower", cmap=cm, zorder=1, aspect="auto")
for p in getattr(land, "geoms", [land]):
    ax.fill(*p.exterior.xy, color=TIERRA, ec="#B9AE98", lw=0.5, zorder=2)
f = d[d.tipo == "fondo"]; t = d[d.tipo == "telemetría"]; a = d[d.tipo == "avistamiento"]
ax.scatter(f.lon, f.lat, s=2.2, c="#C9D6DF", alpha=0.45, lw=0, zorder=3)
ax.scatter(t.lon, t.lat, s=9, c=C_TEL, alpha=0.85, lw=0, zorder=4)
ax.scatter(a.lon, a.lat, s=16, c="#FFF6E0", lw=0.5, edgecolors="#06182B", zorder=5)
ax.set_xlim(O, E); ax.set_ylim(S_, N); ax.set_aspect("equal")
ax.set_xticks(range(-82, -76)); ax.set_yticks(range(2, 8))
ax.set_xticklabels([f"{-v}°O" for v in range(-82, -76)]); ax.set_yticklabels([f"{v}°N" for v in range(2, 8)])
ax.tick_params(colors=SUAVE, labelsize=9, length=0)
for s in ax.spines.values(): s.set_visible(False)
# convenciones
lx, ly = -82.3, 3.15
ax.add_patch(FancyBboxPatch((lx - 0.12, 1.55), 2.75, 1.85, boxstyle="round,pad=0,rounding_size=0.05",
                            fc=FONDO, ec=REJILLA, lw=1, alpha=0.9, zorder=8))
ax.text(lx - 0.02, ly + 0.08, "Convenciones", fontsize=11.5, fontweight="bold", va="center", zorder=9)
items = [("o", "#FFF6E0", 50, f"Avistamientos ({len(a)})"), ("o", C_TEL, 30, f"Telemetría satelital ({len(t)})"),
         ("o", "#C9D6DF", 14, f"Puntos de fondo ({len(f):,})".replace(",", "."))]
for i, (m, c, sz, n) in enumerate(items):
    yy = ly - 0.22 - i * 0.24
    ax.scatter([lx + 0.05], [yy], s=sz, c=c, edgecolors="#06182B" if i == 0 else "none", lw=0.5, zorder=9)
    ax.text(lx + 0.2, yy, n, fontsize=10, va="center", zorder=9)
ax.text(lx - 0.02, ly - 1.0, "Esfuerzo de observación", fontsize=9.5, color=SUAVE, zorder=9)
for i in range(5):
    ax.add_patch(Rectangle((lx - 0.02 + i * 0.4, ly - 1.33), 0.4, 0.13, color=cm(i / 4), lw=0, zorder=9))
ax.text(lx - 0.02, ly - 1.43, "bajo", fontsize=8.5, color=SUAVE, va="top", zorder=9)
ax.text(lx + 1.98, ly - 1.43, "alto", fontsize=8.5, color=SUAVE, va="top", ha="right", zorder=9)
fig.text(0.08, 0.955, "Superficie de esfuerzo y puntos de fondo", fontsize=18, fontweight="bold")
fig.text(0.08, 0.925, "Los puntos de fondo siguen la misma concentración que los registros: así el modelo compara", fontsize=10.5, color=SUAVE)
fig.text(0.08, 0.905, "sitios con un esfuerzo de observación parecido y aprende del mar, no de dónde salen las lanchas.", fontsize=10.5, color=SUAVE)
fig.text(0.08, 0.025, "Fuentes: GBIF.org, OBIS, Natural Earth. Elaboración: Tatiana Zamudio.", fontsize=8.5, color=SUAVE)
plt.savefig(f"{OUT}/fase1_fondo.png", facecolor=FONDO); plt.close()

# ---------- 2. variables: fondo vs avistamientos vs telemetría ----------
var = [("sst", "Temperatura del mar", "°C", None), ("log_chl", "Clorofila", "log10 mg/m³", None),
       ("prof", "Profundidad", "m", (0, 4000)), ("pendiente", "Pendiente del fondo", "grados", (0, 10)),
       ("dist_costa_km", "Distancia a la costa", "km", (0, 200))]
grupos = [("fondo", "Fondo", C_FONDO), ("avistamiento", "Avistamientos", C_AV), ("telemetría", "Telemetría", C_TEL)]
fig = plt.figure(figsize=(20, 6.2), dpi=180); fig.patch.set_facecolor(FONDO)
w = 0.172; g = (1 - 0.04 - 5 * w) / 4
for k, (v, tit, un, lim) in enumerate(var):
    ax = fig.add_axes([0.02 + k * (w + g), 0.14, w, 0.56]); ax.set_facecolor(PANEL)
    datos = d[v].dropna()
    lo, hi = lim if lim else (datos.quantile(0.005), datos.quantile(0.995))
    xs = np.linspace(lo, hi, 300)
    ymax = 0
    for tipo, n, c in grupos:
        x = d.loc[d.tipo == tipo, v].dropna(); x = x[(x >= lo) & (x <= hi)]
        y = gaussian_kde(x, bw_method=0.18)(xs)
        ymax = max(ymax, y.max())
        if tipo == "fondo":
            ax.fill_between(xs, y, color=c, alpha=0.45, lw=0)
            ax.plot(xs, y, color="#9DB6C6", lw=1.2)
        else:
            ax.fill_between(xs, y, color=c, alpha=0.12, lw=0)
            ax.plot(xs, y, color=c, lw=2.4)
        med = d.loc[d.tipo == tipo, v].median()
        ax.axvline(med, color=c if tipo != "fondo" else "#9DB6C6", lw=1, ls=(0, (2, 2)), alpha=0.9)
    ax.set_xlim(lo, hi); ax.set_ylim(0, ymax * 1.08); ax.set_yticks([])
    ax.tick_params(colors=SUAVE, labelsize=10, length=0)
    for s in ax.spines.values(): s.set_visible(False)
    ax.grid(axis="x", color=REJILLA, lw=1); ax.set_axisbelow(True)
    fig.text(0.02 + k * (w + g), 0.79, tit, fontsize=14, fontweight="bold")
    fig.text(0.02 + k * (w + g), 0.745, un, fontsize=10.5, color=SUAVE)
    # medianas
    mt = [f"{d.loc[d.tipo == tp, v].median():.1f}".replace(".", ",") if v in ("sst", "log_chl", "pendiente")
          else f"{d.loc[d.tipo == tp, v].median():,.0f}".replace(",", ".") for tp, _, _ in grupos]
    ax.text(0.97, 0.95, "medianas", transform=ax.transAxes, ha="right", fontsize=8.5, color=SUAVE)
    for i, ((tp, n, c), m) in enumerate(zip(grupos, mt)):
        ax.text(0.97, 0.86 - i * 0.085, m, transform=ax.transAxes, ha="right", fontsize=10.5,
                color=c if tp != "fondo" else "#B9CCD8", fontweight="bold")
# leyenda dentro del primer panel
ax0 = fig.axes[0]
ax0.add_patch(FancyBboxPatch((0.03, 0.62), 0.5, 0.33, boxstyle="round,pad=0.01,rounding_size=0.02",
                             transform=ax0.transAxes, fc=FONDO, ec=REJILLA, lw=1, alpha=0.92, zorder=8))
ax0.text(0.06, 0.9, "Convenciones", transform=ax0.transAxes, fontsize=10.5, fontweight="bold", va="center", zorder=9)
for i, (tp, n, c) in enumerate(grupos):
    yy = 0.81 - i * 0.075
    ax0.add_patch(Rectangle((0.06, yy - 0.02), 0.06, 0.04, transform=ax0.transAxes, fc=c,
                            alpha=0.8 if tp == "fondo" else 1, ec="none", zorder=9))
    ax0.text(0.15, yy, n, transform=ax0.transAxes, fontsize=10, va="center", zorder=9)
fig.text(0.02, 0.93, "Perfil ambiental de la yubarta en el Pacífico colombiano", fontsize=19, fontweight="bold")
fig.text(0.02, 0.885, "Distribución de cada variable en los avistamientos, la telemetría y los puntos de fondo. Donde las curvas se separan, la variable ayuda a explicar dónde están.",
         fontsize=11, color=SUAVE)
fig.text(0.02, 0.035, "Fuentes: NOAA OISST, NASA MODIS-Aqua, NOAA ETOPO1 (vía Google Earth Engine), Natural Earth, GBIF.org, OBIS. Líneas punteadas: medianas. Elaboración: Tatiana Zamudio.",
         fontsize=9, color=SUAVE)
plt.savefig(f"{OUT}/fase1_variables.png", facecolor=FONDO); plt.close()
