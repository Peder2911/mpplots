
from matplotlib import pyplot as plt
import contextily as ctx 
import geopandas as gpd
import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib.colors import ListedColormap

BUF = 200000

DESCR = {
    "p36_c":"Agree with crop substitution",
    "p37_c":"Rating of crop substitution implementation"
}

pdets = gpd.read_file("cache/pdet.geojson")
pdets = pdets.to_crs(epsg=3857)

depts = gpd.read_file("shp/dtos_geo.shp")
depts = depts.to_crs(epsg=3857)

dat = pd.read_csv("raw/merged_data_PDET.csv",encoding="latin1")
dat = dat[dat["PDET"].notna()]
dat["PDET"] = dat["PDET"].apply(int)

def fixNa(v):
    if v < 0 or v == 5:
        return np.nan
    else:
        return v

for v in ["p36_c","p37_c"]:
    dat[v] = dat[v].apply(fixNa)

    sub = dat.copy()
    sub = sub[["PDET",v]]
    sub = sub.dropna()
    sub = sub.groupby("PDET").agg("mean")
    sub = gpd.GeoDataFrame(pdets.merge(sub,on="PDET"))
    plt.clf()

    mp = depts.plot(figsize=(9,9),color="#989898",edgecolor="#101010",alpha=0.4)
    minx,miny,maxx,maxy = depts.total_bounds
    mp.set_xlim(minx-BUF,maxx+BUF)

    mp = sub.plot(column = v,ax = mp,
        legend=True,edgecolor="#606060",cmap = ListedColormap(sns.color_palette("RdBu_r")),
        legend_kwds={"label":"Scale mean"}
        )

    mp.set_axis_off()

    ctx.add_basemap(mp,source=ctx.providers.Esri.WorldPhysical,zoom=8)

    plt.title(DESCR[v])
    plt.xlabel("Scale mean")

    plt.savefig(f"plots/{v.upper()}_map.png")

    sub = dat.copy()

    ispos = lambda x: int(x in [3,4])
    sub["pos"] = sub[v].apply(ispos)
    sub = sub[["PDET","pos"]]
    sub = sub.dropna()
    sub = sub.groupby("PDET")["pos"].value_counts(normalize=True).reindex()
    posPst = sub[:,1].reindex()
    sub = pdets.merge(posPst,left_on="PDET",right_index=True)

    mp = depts.plot(figsize=(9,9),color="#989898",edgecolor="#101010",alpha=0.4)
    minx,miny,maxx,maxy = depts.total_bounds
    mp.set_xlim(minx-BUF,maxx+BUF)

    sub["pos"] = sub["pos"].apply(lambda x: x*100)

    mp = sub.plot(column = "pos",ax = mp,
        legend=True,edgecolor="#606060",cmap = ListedColormap(sns.color_palette("RdBu_r")),
        legend_kwds={"label":"% positive"}
        )

    mp.set_axis_off()

    ctx.add_basemap(mp,source=ctx.providers.Esri.WorldPhysical,zoom=8)

    plt.title(DESCR[v])
    plt.xlabel("% positive")

    plt.savefig(f"plots/{v.upper()}_pst_map.png")

