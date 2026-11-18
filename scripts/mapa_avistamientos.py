"""Mapa de avistamientos de ballena jorobada sobre la batimetría del Pacífico colombiano.

Lee data/avistamientos_pacifico_co.csv (sale de notebooks/01_fase0_datos.ipynb),
descarga tierra y batimetría de Natural Earth si no están en data/,
y escribe docs/img/mapa_avistamientos.png.

Uso, desde la raíz del repo:  python scripts/mapa_avistamientos.py
"""
import os, urllib.request
import json, numpy as np, pandas as pd, matplotlib.pyplot as plt, shapely
from shapely.geometry import shape, box
from matplotlib.patches import Circle, Rectangle
from matplotlib.collections import PatchCollection
import matplotlib.patheffects as pe
import cartopy.io.shapereader as shp

NE_URL = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master"
def bajar(url, ruta):
    if not os.path.exists(ruta):
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        urllib.request.urlretrieve(url, ruta)
bajar(f"{NE_URL}/geojson/ne_10m_land.geojson", "data/ne_10m_land.geojson")
for cod in ["L_0", "K_200", "J_1000", "I_2000", "H_3000", "G_4000", "F_5000"]:
    for ext in ["shp", "shx", "dbf", "prj"]:
        bajar(f"{NE_URL}/10m_physical/ne_10m_bathymetry_all/ne_10m_bathymetry_{cod}.{ext}",
              f"data/bati/ne_10m_bathymetry_{cod}.{ext}")

df = pd.read_csv("data/avistamientos_pacifico_co.csv")
df["tipo"] = np.where(df.base.str.upper().str.replace("_","")=="MACHINEOBSERVATION","telemetría","avistamiento")
O,E,S,N = -82.5,-75.7,1.4,7.4
B = box(O-0.5,S-0.5,E+0.5,N+0.5)

FONDO="#071A2C"; TEXTO="#EAF2F4"; SUAVE="#8FB3BF"
NIVELES = [("L_0",0,"#7FD1D3"),("K_200",200,"#3FA6B5"),("J_1000",1000,"#2B7F99"),
           ("I_2000",2000,"#1F6080"),("H_3000",3000,"#164867"),("G_4000",4000,"#0F3452"),("F_5000",5000,"#0A2540")]
TIERRA="#D8CFBD"; AV="#FFF6E0"; TEL="#FF8A5B"

plt.rcParams["font.family"]="DejaVu Sans"
fig = plt.figure(figsize=(10.8,10.6),dpi=200); fig.patch.set_facecolor(FONDO)
ax = fig.add_axes([0.075,0.08,0.9,0.81]); ax.set_facecolor(NIVELES[0][2])

def poligonos(geoms):
    for g in geoms:
        g = g.intersection(B)
        if g.is_empty: continue
        for p in getattr(g,"geoms",[g]):
            if p.geom_type!="Polygon": continue
            yield p
def pintar(p, **kw):
    path_x, path_y = p.exterior.xy
    ax.fill(path_x, path_y, **kw)
    for h in p.interiors:
        ax.fill(*h.xy, color=kw.get("hole"), lw=0, zorder=kw["zorder"]) if kw.get("hole") else None

# bandas de profundidad: cada capa es "más profundo que X", con huecos reales donde es más somero
from matplotlib.path import Path
from matplotlib.patches import PathPatch
def a_path(p):
    anillos = [p.exterior] + list(p.interiors)
    return Path.make_compound_path(*[Path(np.asarray(r.coords)[:, :2], closed=True) for r in anillos])
for i,(cod,prof,col) in enumerate(NIVELES):
    for p in poligonos(shp.Reader(f"data/bati/ne_10m_bathymetry_{cod}.shp").geometries()):
        ax.add_patch(PathPatch(a_path(p), fc=col, ec="none", lw=0, zorder=1+i))

land = shapely.unary_union([g for g in (shape(f["geometry"]).intersection(B) for f in json.load(open("data/ne_10m_land.geojson"))["features"]) if not g.is_empty])
for p in getattr(land,"geoms",[land]):
    ax.fill(*p.exterior.xy, color=TIERRA, ec="#B9AE98", lw=0.5, zorder=20)

sitios = {"Bahía Solano":(-77.40,6.22),"Nuquí / Tribugá":(-77.35,5.70),"Bahía Málaga":(-77.35,4.05),"Gorgona":(-78.18,2.97)}
for n,(x,y) in sitios.items():
    ax.add_patch(Circle((x,y),0.25,fill=False,ls=(0,(3,2)),ec=TEXTO,lw=1,alpha=0.85,zorder=24))
t = df[df.tipo=="telemetría"]; a = df[df.tipo=="avistamiento"]
ax.scatter(t.lon,t.lat,s=8,c=TEL,alpha=0.7,lw=0,zorder=25)
ax.scatter(a.lon,a.lat,s=14,c=AV,alpha=0.75,lw=0.3,edgecolors="#0A2540",zorder=26)

d = {n:int((np.hypot(df.lon-x,df.lat-y)<0.25).sum()) for n,(x,y) in sitios.items()}
halo=[pe.withStroke(linewidth=3,foreground=TIERRA)]
off = {"Bahía Solano":(0.30,0.12),"Nuquí / Tribugá":(0.30,-0.05),"Bahía Málaga":(0.30,0.0),"Gorgona":(-0.36,0.30)}
for n,(x,y) in sitios.items():
    dx,dy = off[n]; ha = "left" if dx>0 else "right"
    col = "#1C2A33" if dx>0 else TEXTO
    ax.text(x+dx,y+dy+0.06,n,fontsize=11,color=col,ha=ha,va="center",fontweight="bold",zorder=30)
    ax.text(x+dx,y+dy-0.08,f"{d[n]} registros",fontsize=10,color=("#5A6A70" if dx>0 else SUAVE),ha=ha,va="center",zorder=30)
ax.text(-81.53,3.88,"Malpelo",fontsize=10.5,color=TEXTO,zorder=30)
ax.text(-80.2,6.2,"Océano Pacífico",fontsize=15,color=SUAVE,style="italic",alpha=0.8,zorder=30)
ax.text(-76.35,5.0,"COLOMBIA",fontsize=13,color="#8C8270",fontweight="bold",rotation=90,ha="center",va="center",zorder=30)

ax.set_xlim(O,E); ax.set_ylim(S,N); ax.set_aspect("equal")
ax.set_xticks(range(-82,-75)); ax.set_yticks(range(2,8))
ax.set_xticklabels([f"{-v}°O" for v in range(-82,-75)]); ax.set_yticklabels([f"{v}°N" for v in range(2,8)])
ax.tick_params(colors=SUAVE,labelsize=9,length=0)
for s in ax.spines.values(): s.set_visible(False)

# leyenda
lx,ly = -82.3,2.55
ax.add_patch(Rectangle((lx-0.12,1.5),2.62,1.35,color=FONDO,alpha=0.72,lw=0,zorder=31))
ax.scatter([lx],[ly+0.15],s=45,c=AV,edgecolors="#0A2540",lw=0.3,zorder=32); ax.text(lx+0.13,ly+0.15,f"Avistamientos ({len(a)})",va="center",fontsize=10,color=TEXTO,zorder=32)
ax.scatter([lx],[ly-0.08],s=35,c=TEL,zorder=32); ax.text(lx+0.13,ly-0.08,f"Telemetría satelital, 2013 ({len(t)})",va="center",fontsize=10,color=TEXTO,zorder=32)
ax.add_patch(Circle((lx,ly-0.32),0.08,fill=False,ls=(0,(3,2)),ec=TEXTO,lw=1,zorder=32)); ax.text(lx+0.13,ly-0.32,"25 km alrededor de un sitio turístico",va="center",fontsize=10,color=TEXTO,zorder=32)
# escala de profundidad
ax.text(lx-0.04,ly-0.62,"Profundidad (m)",fontsize=9,color=SUAVE,zorder=32)
w=0.33
for i,(cod,prof,col) in enumerate(NIVELES):
    ax.add_patch(Rectangle((lx-0.04+i*w,ly-0.88),w,0.12,color=col,lw=0,zorder=32))
    ax.text(lx-0.04+i*w,ly-0.98,f"{prof:,}".replace(",","."),fontsize=7.5,color=SUAVE,ha="left",va="top",zorder=32)

cerca = int((np.min([np.hypot(df.lon-x,df.lat-y) for x,y in sitios.values()],axis=0)<0.25).sum())
fig.text(0.075,0.955,"Ballena jorobada en el Pacífico colombiano",fontsize=20,color=TEXTO,fontweight="bold")
fig.text(0.075,0.925,f"{len(df):,}".replace(",",".")+f" registros de GBIF y OBIS, 1986-2026. El {cerca/len(df):.0%} cae a menos de 25 km de un sitio turístico.",fontsize=11.5,color=SUAVE)
fig.text(0.075,0.03,"Fuentes: GBIF.org, OBIS, Natural Earth (tierra y batimetría). Elaboración: Tatiana Zamudio.",fontsize=8.5,color=SUAVE)
plt.savefig("docs/img/mapa_avistamientos.png",facecolor=FONDO)
