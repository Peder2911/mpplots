
import pandas as pd
from typing import Dict
import json
import os
import seaborn as sns
from matplotlib import pyplot as plt
from collections import defaultdict
import textwrap
import numpy as np

Codebook = Dict[str,Dict[str,str]]
Descriptions = Dict[str,str]

sns.set(font_scale = 1.5)

def cache(location):
    def cached(fn):
        def wrapper(*args,**kwargs):
            if os.path.exists(location):
                with open(location) as f:
                    d = json.load(f)
            else:
                d = fn(*args,**kwargs)
                with open(location,"w") as f:
                    json.dump(d,f)
            return d

        return wrapper
    return cached

def getCodebook(dat: pd.DataFrame)-> Codebook:
    d = dict()
    for v in set(dat["Variable"]):
        vd = dict()
        for idx,r in dat[dat["Variable"] == v].iterrows():
            vd.update({str(r["Valor"]):str(r["Valor_Etiqueta"])})
        d.update({v:vd})
    return d

@cache("cache/codebook.json")
def getCodebookFromExcel(*args,**kwargs):
    return getCodebook(pd.read_excel(*args,**kwargs))

def getDescriptions(dat: pd.DataFrame) -> Descriptions:
    d = dict()
    for idx,r in dat.iterrows():
        label = r["Etiqueta"].split(".")[-1]
        d.update({r["Variable"]:label})
    return d

@cache("cache/descr.json")
def getDescriptionsFromExcel(*args,**kwargs):
    return getDescriptions(pd.read_excel(*args,**kwargs))

if __name__ == "__main__":
    codebook = getCodebookFromExcel("docs/Codebook_AT_New Dictionary.xlsx",sheet_name="Label")
    desc = getDescriptionsFromExcel("docs/Codebook_AT_New Dictionary.xlsx",sheet_name="Dictionary")
    dat = pd.read_csv("raw/mergedFinal.csv",encoding="latin1",low_memory=False)
    dat.columns = [c.upper() for c in dat.columns] 

    pvm = pd.read_csv("raw/Plot_variable_mapping - Sheet1.csv")
    histograms = pvm[pvm["Type"] == "Hist"]

    for idx,r in histograms.iterrows():
        r["Variable"] = str(r["Variable"]).upper()

        if str(r["Variable"]).lower() == "nan":
            print(f"Missing variable for {r['Slide']}")
            continue

        try:
            values = dat[r["Variable"]]
        except KeyError:
            print(f"{r['Variable']} not in data")
            continue

        values = values[np.invert(np.isnan(values))]
        values = values.apply(lambda x: int(x))
        values = values.apply(lambda x: codebook[r['Variable']].get(str(x),"NA"))

        counts = values.value_counts()
        percentages = counts.apply(lambda x: (x / counts.sum())*100) 

        labels = counts.index
        labels = ["\n".join(textwrap.wrap(l,25)) for l in labels]

        title = "\n".join(textwrap.wrap(desc[r["Variable"]],60))

        plt.clf()

        fig,ax = plt.subplots()

        chart = sns.barplot(y=labels,x=percentages,ax = ax)
        chart.set_title(title)

        ax.figure.subplots_adjust(left=0.3)
        ax.set(xlabel = "%")

        fig.set_size_inches(11.7,8.27)

        plt.savefig(f"plots/{r['Slide']}_{r['Variable']}.png")

