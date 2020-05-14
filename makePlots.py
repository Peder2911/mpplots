
import pandas as pd
from typing import Dict
import json
import os
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap
from collections import defaultdict
import textwrap
import numpy as np
import re
import geopandas as gpd
import contextily as ctx

from util import getDescriptionsFromExcel, getCodebookFromExcel, lookup, genDeptName, daneCode, stripPrefix
from mytypes import Codebook,Descriptions
from style import mapsCmap, barColor

import multiprocessing as mp

# ========================================================
#
sns.set(font_scale = 1.5)

# ========================================================
#

"""
Removes a prefix that is added to some variables, but doesn't have
any significance here.
"""
# ========================================================
print("loading data")

codebook = getCodebookFromExcel("docs/codebook_merged.xlsx")
#codebook["PDETCAT"] = {"1":"PDET"}
description = getDescriptionsFromExcel("docs/codebook_merged.xlsx")
#description["PDETCAT"] = "PDETs" 

for fname in os.listdir("mask"):
    if os.path.splitext(fname)[-1] != ".json":
        continue
    var = os.path.split(os.path.splitext(fname)[0])[-1]

    with open(os.path.join("mask",fname)) as f:
        d = json.load(f)
        try:
            codebook[var] = {k:v for k,v in d.items() if k != "desc"} 
            description[var] = d["desc"] 
        except:
            print(f"Parsing mask for {var} failed")
        else:
            print(f"Masked {var}")

dat = pd.read_csv("raw/merged_data_PDET.csv",encoding="latin1",low_memory=False)
dat.columns = [c.upper() for c in dat.columns] 
dat.columns = [stripPrefix(c) for c in dat.columns]
dat["pdet"] = dat["PDET"].apply(daneCode)
dat["PDETCAT"] = 1 

shp = gpd.read_file("cache/pdet.geojson")
shp["pdet"] = shp["PDET"].apply(daneCode)
shp = shp.to_crs(epsg=3857)

depts = gpd.read_file("shp/dtos_geo.shp")
depts = depts.to_crs(epsg=3857)

pvm = pd.read_csv("raw/Plot_variable_mapping - Sheet1.csv")

# ========================================================
def makePlot(r):
    """
    Makes a plot using an instruction-row from a dataset. 
    """

    variable = str(r["Variable"]).upper()
    plotname = f"plots/{r['Slide']}_{variable}.png"
    if os.path.exists(plotname):
        print(f"Skipping {plotname} (exists)")
        return

    slide = r["Slide"]

    # Catching irregularities ============================
    # 

    if str(variable).lower() == "nan":
        print(f"Missing variable for {slide}")
        return

    try:
        values = dat[variable]
        values = values[np.invert(np.isnan(values))]
        values = values.apply(lambda x: int(x))
        values = values[values != -7]
    except KeyError:
        print(f"{variable} not in data")
        return

    if variable+".json" in os.listdir("mask"):
        print(f"Masking {variable}")
        with open(os.path.join("mask",variable+".json")) as f:
            mask = json.load(f)
            cb = {variable:mask}
            desc = mask["desc"]
    else:
        try:
            desc = description[variable]
        except KeyError:
            print(f"{variable} not found in descriptions")
            return
        try:
            cb = codebook
        except KeyError:
            print(f"{variable} not in codebook")
            return
    try:
        variableLookup = lookup(cb = cb, idx = variable)
        values = variableLookup(values)
    except KeyError:
        print(f"{variable} not in codebook")
        return

    values = values[values != "No answer"]

    # Catching irregularities ============================
    #   
    
    counts = values.value_counts(sort=False,ascending=False)
    counts = counts.iloc[::-1]

    percentages = counts.apply(lambda x: (x / counts.sum())*100) 
    labels = counts.index 

    labels = ["\n".join(textwrap.wrap(l,25)) for l in labels]
    title = "\n".join(textwrap.wrap(desc,60))

    plt.clf()
    fig,ax = plt.subplots()

    chart = sns.barplot(y=labels,x=percentages,ax = ax,color = barColor)

    plt.title(title)
    plt.xlabel("Percent of respondents %")
    plt.ylabel("")
    plt.subplots_adjust(left = 0.3,top=0.85)
    fig.set_size_inches(14,9)

    print(f"Saving plot for {slide}_{variable}")
    plt.savefig(plotname)

def makeMap(row):
    var = row["Variable"].upper()

    plotname = f"plots/{var}_map.png"
    if os.path.exists(plotname):
        print(f"Skipping {plotname} (exists)")
        return

    print(f"Making map for {row['Variable']} with type {row['Maptype']}")

    var = row["Variable"].upper()
    maptype = row["Maptype"]
    try:
        desc = "\n".join(textwrap.wrap(description[var],50))
    except KeyError:
        print(f"{var} not in description")

    try:
        sub = dat[[var,"pdet"]]
    except KeyError:
        print(f"{var} not found in data")
        return

    leg = ""
    cat = False
    if maptype == "satisfaction":
        #fn = lambda x: np.mean([v for v in x if v in [1,2,3,4]])
        fn = lambda x: sum([v in [3,4] for v in x])
        leg = "\n\n% satisfied"
    elif maptype == "yesno":
        fn = lambda x: sum(x == 1)
        leg = "\n\n% yes"
    elif maptype == "cat":
        variableLookup = lookup(cb = codebook, idx = var)
        sub[var] = sub[var].fillna(-99)
        sub[var] = sub[var].astype("int32")
        sub[var] = variableLookup(sub[var])
        fn = lambda x: x.mode()[0]
        cat = True
    else:
        print(f"Unknown type: {maptype}")
        return
    
    summary = sub.groupby("pdet")
    c = sub["pdet"].value_counts()

    a = summary[var].agg([fn])
    a = a.merge(c,left_index=True,right_index=True)

    if not cat:
        a["pst"] = (a[a.columns[0]] / a[a.columns[1]])*100

    a = shp.merge(a,left_on="pdet",right_index=True)

    plt.clf()

    b = depts.plot(figsize=(14,14),color="#989898",edgecolor="#101010",alpha=0.4)

    if not cat:
        mapPlot = a.plot(column="pst", ax = b,
            legend=True,edgecolor="#606060",cmap="viridis",#alpha = 0.9,#cmap="rainbow",
            legend_kwds={"label":leg}
        )
    else:
        mapPlot = a.plot(column="<lambda>", ax = b,
            cmap=mapsCmap,
            legend=True,edgecolor="#606060",categorical = True 
        )

    minx, miny, maxx, maxy = depts.total_bounds
    mapPlot.set_xlim(minx-200000, maxx+200000)

    mapPlot.set_axis_off()
    ctx.add_basemap(mapPlot,source = ctx.providers.Esri.WorldPhysical,zoom=8)

    plt.subplots_adjust(top = 0.78)
    plt.title(desc,pad=35)
    plt.savefig(plotname)

histograms = pvm[pvm["Type"] == "Hist"]
rows = [r for idx,r in histograms.iterrows()]
print("Making histogram plots")
with mp.Pool(mp.cpu_count()) as p:
    p.map(makePlot,rows)

maps = pvm[pvm["Type"] == "Map"]
rows = [r for idx,r in maps.iterrows()]
print("Making maps")
with mp.Pool(mp.cpu_count()) as p:
    p.map(makeMap,rows)
