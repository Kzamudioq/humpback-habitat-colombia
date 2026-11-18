"""Gráficas de registros por año y por mes, con la paleta del mapa.

Lee data/avistamientos_pacifico_co.csv y escribe docs/img/tiempo_avistamientos.png.
Uso, desde la raíz del repo:  python scripts/tiempo_avistamientos.py
"""
import sys, numpy as np, pandas as pd, matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
from matplotlib.colors import LinearSegmentedColormap

CSV = sys.argv[1] if len(sys.argv) > 1 else "data/avistamientos_pacifico_co.csv"
SALIDA = sys.argv[2] if len(sys.argv) > 2 else "docs/img/tiempo_avistamientos.png"
FONDO, PANEL, TEXTO, SUAVE, REJILLA = "#071A2C", "#0B2238", "#EAF2F4", "#8FB3BF", "#15314A"
# degradados de abajo (profundo) hacia arriba (superficie)
AV = LinearSegmentedColormap.from_list("av", ["#1B5E7E", "#2FA3B4", "#8FF0E6"])
TEL = LinearSegmentedColormap.from_list("tel", ["#D9543A", "#FF8A5B", "#FFC8A2"])

df = pd.read_csv(CSV, parse_dates=["fecha"])
df["tipo"] = np.where(df.base.str.upper().str.replace("_", "") == "MACHINEOBSERVATION", "telemetría", "avistamiento")
df["año"], df["mes"] = df.fecha.dt.year, df.fecha.dt.month

def tabla(col, idx):
    t = df.pivot_table(index=col, columns="tipo", values="id", aggfunc="count").reindex(idx).fillna(0)
    for c in ["avistamiento", "telemetría"]:
        if c not in t: t[c] = 0
    return t

def barra(ax, x, y0, h, w, cmap, ymax, borde):
    """Barra recta con degradado vertical y contorno."""
    if h <= 0: return
    caja = Rectangle((x - w / 2, y0), w, h, fc="none", ec="none", zorder=3)
    ax.add_patch(caja)
    grad = np.linspace(0, 1, 64).reshape(-1, 1)   # cada barra con su degradado completo
    im = ax.imshow(grad, cmap=cmap, vmin=0, vmax=1, extent=(x - w / 2, x + w / 2, y0, y0 + h),
                   origin="lower", aspect="auto", zorder=3, interpolation="bicubic")
    im.set_clip_path(caja)
    ax.add_patch(Rectangle((x - w / 2, y0), w, h, fc="none", ec=borde, lw=1.1, zorder=4))

def estilo(ax, ymax):
    ax.set_facecolor(PANEL)
    for s in ax.spines.values(): s.set_visible(False)
    ax.tick_params(colors=SUAVE, length=0, labelsize=11)
    ax.grid(axis="y", color=REJILLA, lw=1); ax.set_axisbelow(True)
    ax.set_ylim(0, ymax)

def leyenda(ax, x, y):
    """Convenciones dentro del gráfico, en coordenadas del eje (0-1)."""
    ax.add_patch(FancyBboxPatch((x, y - 0.17), 0.30, 0.23, boxstyle="round,pad=0.012,rounding_size=0.02",
                                transform=ax.transAxes, fc=FONDO, ec=REJILLA, lw=1, alpha=0.92, zorder=8))
    ax.text(x + 0.018, y + 0.015, "Convenciones", transform=ax.transAxes, fontsize=12, fontweight="bold",
            color=TEXTO, va="center", zorder=9)
    for i, (n, c) in enumerate([(f"Avistamientos ({int(df.tipo.eq('avistamiento').sum())})", "#4FC4CC"),
                                (f"Telemetría satelital ({int(df.tipo.eq('telemetría').sum())})", "#FF8A5B")]):
        yy = y - 0.055 - i * 0.075
        ax.add_patch(Rectangle((x + 0.018, yy - 0.018), 0.018, 0.036, transform=ax.transAxes, fc=c,
                              ec=("#C9FBF4" if i == 0 else "#FFE1CC"), lw=1.1, zorder=9))
        ax.text(x + 0.048, yy, n, transform=ax.transAxes, fontsize=11, color=TEXTO, va="center", zorder=9)

plt.rcParams.update({"font.family": "DejaVu Sans", "text.color": TEXTO})
fig = plt.figure(figsize=(16, 6.2), dpi=200); fig.patch.set_facecolor(FONDO)
a1 = fig.add_axes([0.045, 0.1, 0.6, 0.72]); a2 = fig.add_axes([0.685, 0.1, 0.295, 0.72])

# por año
años = np.arange(df.año.min(), df.año.max() + 1)
t = tabla("año", años)
ymax = t.sum(axis=1).max() * 1.12
estilo(a1, ymax)
for a in años:
    av, te = t.loc[a, "avistamiento"], t.loc[a, "telemetría"]
    barra(a1, a, 0, av, 0.74, AV, ymax, "#C9FBF4")
    barra(a1, a, av, te, 0.74, TEL, ymax, "#FFE1CC")
    if av + te >= 150:
        a1.text(a, av + te + ymax * 0.015, f"{int(av + te)}", ha="center", fontsize=10.5, color=TEXTO, fontweight="bold")
a1.set_xlim(años[0] - 1, años[-1] + 1)
leyenda(a1, 0.025, 0.86)
a1.text(0, 1.13, "Registros por año", transform=a1.transAxes, fontsize=17, fontweight="bold")
a1.text(0, 1.045, "El pico de 2013 es telemetría de pocas ballenas; los avistamientos despegan desde 2016.",
        transform=a1.transAxes, fontsize=11, color=SUAVE)

# por mes
m = tabla("mes", range(1, 13))
ymax2 = m.sum(axis=1).max() * 1.12
estilo(a2, ymax2)
a2.axvspan(4.5, 12.5, color="#0F3452", lw=0, zorder=1)
a2.text(8.5, ymax2 * 0.95, "Temporada de cría", ha="center", fontsize=10.5, color=SUAVE, zorder=4)
for mes in range(1, 13):
    av, te = m.loc[mes, "avistamiento"], m.loc[mes, "telemetría"]
    barra(a2, mes, 0, av, 0.7, AV, ymax2, "#C9FBF4")
    barra(a2, mes, av, te, 0.7, TEL, ymax2, "#FFE1CC")
a2.set_xticks(range(1, 13), ["E", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"])
a2.set_xlim(0.4, 12.6)
a2.text(0, 1.13, "Registros por mes", transform=a2.transAxes, fontsize=17, fontweight="bold")
a2.text(0, 1.045, "Los avistamientos van de julio a octubre.", transform=a2.transAxes, fontsize=11, color=SUAVE)

fig.text(0.045, 0.025, "Fuentes: GBIF.org y OBIS. Elaboración: Tatiana Zamudio.", fontsize=9, color=SUAVE)
plt.savefig(SALIDA, facecolor=FONDO)
