"""Mapa de avistamientos de ballena jorobada en el Pacífico colombiano.

Lee data/avistamientos_pacifico_co.csv (sale de notebooks/01_fase0_datos.ipynb)
y escribe docs/img/mapa_avistamientos.png.

Uso, desde la raíz del repo:  python scripts/mapa_avistamientos.py
"""
import os, urllib.request
import json, numpy as np, pandas as pd, matplotlib.pyplot as plt, shapely
from shapely.geometry import shape, box
from matplotlib.patches import Circle
df = pd.read_csv("data/avistamientos_pacifico_co.csv")
df["tipo"] = np.where(df.base.str.upper().str.replace("_","")=="MACHINEOBSERVATION","telemetría","avistamiento")
NE = "data/ne_10m_land.geojson"
if not os.path.exists(NE):
    urllib.request.urlretrieve("https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_land.geojson", NE)
O,E,S,N = -82.5,-75.7,1.4,7.4
land = [shape(f["geometry"]).intersection(box(O-1,S-1,E+1,N+1)) for f in json.load(open(NE))["features"]]
land = shapely.unary_union([g for g in land if not g.is_empty])
TINTA,GRIS,MAR,TIERRA,AV,TEL = "#1C211D","#8A928B","#E4EEEF","#EFEDE6","#0F6E7A","#E07A2E"
plt.rcParams["font.family"]="DejaVu Sans"
fig,ax = plt.subplots(figsize=(10.8,10.2),dpi=200)
fig.patch.set_facecolor("white"); ax.set_facecolor(MAR)
for g in getattr(land,"geoms",[land]):
    x,y = g.exterior.xy; ax.fill(x,y,color=TIERRA,ec=GRIS,lw=0.6,zorder=2)
sitios = {"Bahía Solano":(-77.40,6.22),"Nuquí / Tribugá":(-77.35,5.70),"Bahía Málaga":(-77.35,4.05),"Gorgona":(-78.18,2.97)}
for n,(x,y) in sitios.items():
    ax.add_patch(Circle((x,y),0.25,fill=False,ls=(0,(3,2)),ec=TINTA,lw=0.9,zorder=4))
t = df[df.tipo=="telemetría"]; a = df[df.tipo=="avistamiento"]
ax.scatter(t.lon,t.lat,s=7,c=TEL,alpha=0.55,lw=0,zorder=5)
ax.scatter(a.lon,a.lat,s=12,c=AV,alpha=0.6,lw=0,zorder=6)
d = {n:int((np.hypot(df.lon-x,df.lat-y)<0.25).sum()) for n,(x,y) in sitios.items()}
off = {"Bahía Solano":(0.32,0.12),"Nuquí / Tribugá":(0.32,-0.05),"Bahía Málaga":(0.32,0.0),"Gorgona":(-0.36,0.30)}
for n,(x,y) in sitios.items():
    dx,dy = off[n]; ha = "left" if dx>0 else "right"
    ax.annotate(f"{n}\n", (x+dx,y+dy), fontsize=10, color=TINTA, ha=ha, va="center", fontweight="bold", zorder=8)
    ax.annotate(f"\n{d[n]} registros", (x+dx,y+dy), fontsize=9.5, color=GRIS, ha=ha, va="center", zorder=8)
ax.annotate("Malpelo", (-81.60,4.0), xytext=(8,-10), textcoords="offset points", fontsize=10, color=TINTA, zorder=8)
ax.set_xlim(O,E); ax.set_ylim(S,N); ax.set_aspect("equal")
ax.set_xticks(range(-82,-75)); ax.set_yticks(range(2,8))
ax.set_xticklabels([f"{-v}°O" for v in range(-82,-75)]); ax.set_yticklabels([f"{v}°N" for v in range(2,8)])
ax.tick_params(colors=GRIS,labelsize=9,length=0); ax.grid(color="white",lw=0.8,zorder=1)
for s in ax.spines.values(): s.set_visible(False)
cerca = int((np.min([np.hypot(df.lon-x,df.lat-y) for x,y in sitios.values()],axis=0)<0.25).sum())
fig.text(0.075,0.965,"Ballena jorobada en el Pacífico colombiano",fontsize=19,color=TINTA,fontweight="bold")
fig.text(0.075,0.94,f"{len(df):,}".replace(",",".")+f" registros de GBIF y OBIS, 1986-2026. El {cerca/len(df):.0%} cae dentro de los círculos: 25 km alrededor de sitios turísticos.",fontsize=11,color=GRIS)
# legend
lx,ly = -82.25,1.95
ax.scatter([lx],[ly+0.22],s=40,c=AV,zorder=9); ax.text(lx+0.15,ly+0.22,f"Avistamientos ({len(a)})",va="center",fontsize=10,color=TINTA,zorder=9)
ax.scatter([lx],[ly],s=30,c=TEL,zorder=9); ax.text(lx+0.15,ly,f"Telemetría satelital, 2013 ({len(t)})",va="center",fontsize=10,color=TINTA,zorder=9)
ax.add_patch(Circle((lx,ly-0.22),0.09,fill=False,ls=(0,(3,2)),ec=TINTA,lw=0.9,zorder=9)); ax.text(lx+0.15,ly-0.22,"25 km alrededor de un sitio turístico",va="center",fontsize=10,color=TINTA,zorder=9)
fig.text(0.075,0.025,"Fuentes: GBIF.org, OBIS, Natural Earth. Elaboración: Tatiana Zamudio.",fontsize=8.5,color=GRIS)
plt.subplots_adjust(left=0.075,right=0.97,top=0.925,bottom=0.06)
plt.savefig("docs/img/mapa_avistamientos.png",facecolor="white")
print(len(a),len(t),d,cerca)
