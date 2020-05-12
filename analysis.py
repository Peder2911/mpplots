
import pandas as pd
from typing import Dict
import json
import os
import seaborn as sns
from matplotlib import pyplot as plt
from collections import defaultdict
import textwrap
import numpy as np
import re
import geopandas as gpd

from util import getDescriptionsFromExcel, getCodebookFromExcel, lookup, genDeptName
from mytypes import Codebook,Descriptions

import multiprocessing as mp

# ========================================================
sns.set(font_scale = 1.5)

# ========================================================
"""
Removes a prefix that is added to some variables, but doesn't have
any significance here.
"""
stripPrefix = lambda x: re.sub("(_FW|_AT)$","",x)

# ========================================================
codebook = getCodebookFromExcel("docs/codebook_merged.xlsx")
description = getDescriptionsFromExcel("docs/codebook_merged.xlsx")

dat = pd.read_csv("raw/mergedFinal.csv",encoding="latin1",low_memory=False)
dat.columns = [c.upper() for c in dat.columns] 
dat.columns = [stripPrefix(c) for c in dat.columns]
dat["dept"] = dat["P2_DEPAR"].apply(genDeptName)

pvm = pd.read_csv("raw/Plot_variable_mapping - Sheet1.csv")

shp = gpd.read_file("shp/simpleCol.gpkg")
shp["dept"] = shp["DEPARTAMEN"].apply(genDeptName)

# ========================================================
def makePlot(r):
    """
    Makes a plot using an instruction-row from a dataset. 
    """
    variable = str(r["Variable"]).upper()
    slide = r["Slide"]

    if str(variable).lower() == "nan":
        print(f"Missing variable for {slide}")
        return

    try:
        values = dat[variable]
        values = values[np.invert(np.isnan(values))]
        values = values.apply(lambda x: int(x))

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

    counts = values.value_counts(sort=False,ascending=False)
    counts = counts.iloc[::-1]
    percentages = counts.apply(lambda x: (x / counts.sum())*100) 
    labels = counts.index 

    labels = ["\n".join(textwrap.wrap(l,25)) for l in labels]
    title = "\n".join(textwrap.wrap(desc,60))

    plt.clf()
    fig,ax = plt.subplots()

    chart = sns.barplot(y=labels,x=percentages,ax = ax)

    plt.title(title)
    plt.xlabel("%")
    plt.ylabel("")
    plt.subplots_adjust(left = 0.3)
    fig.set_size_inches(12,8)

    plt.savefig(f"plots/{r['Slide']}_{variable}.png")

def makeMap(row):
    print(f"Making map for {row['Variable']} with type {row['Maptype']}")

    var = row["Variable"]
    maptype = row["Maptype"]
    try:
        desc = "\n".join(textwrap.wrap(description[var],50))
    except KeyError:
        print(f"{var} not in description")

    try:
        sub = dat[[var,"dept"]]
    except KeyError:
        print(f"{var} not found in data")
        return

    if maptype == "satisfaction":
        fn = lambda x: sum([v in [3,4] for v in x])
        desc += "\n\n(% satisfied)"
    elif maptype == "yesno":
        fn = lambda x: sum(x == 1)
        desc += "\n\n(% yes)"
    elif maptype == "cat":
        fn = lambda x: sum(x)
    else:
        print(f"Unknown type: {maptype}")
        return
    
    summary = sub.groupby("dept")
    c = sub["dept"].value_counts()

    a = summary[var].agg([fn])
    a = a.merge(c,left_index=True,right_index=True)

    a["pst"] = (a[a.columns[0]] / a[a.columns[1]])*100

    a = shp.merge(a,left_on="dept",right_index=True)

    plt.clf()
    b = shp.plot(figsize=(10,10),color="gray")
    a.plot(column="pst",
        ax = b, legend=True
    )

    plt.subplots_adjust(top = 0.78)
    plt.title(desc,pad=35)
    plt.savefig(f"plots/{var}_map.png")

"""
histograms = pvm[pvm["Type"] == "Hist"]
rows = [r for idx,r in histograms.iterrows()]
print("Making histogram plots")
with mp.Pool(mp.cpu_count()) as p:
    p.map(makePlot,rows)
    """

maps = pvm[pvm["Type"] == "Map"]
rows = [r for idx,r in maps.iterrows()]
print("Making maps")
with mp.Pool(mp.cpu_count()) as p:
    p.map(makeMap,rows)
