import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
import unidecode
import textwrap
nlwrap = lambda x,y: "\n".join(textwrap.wrap(x,y))
from util import *

sns.set()

d = pd.read_csv("/tmp/f.csv",encoding="latin1")
d = d[d["PDET_name"].notna()]

d["PDET_name"] = d["PDET_name"].apply(lambda x: str(x))
#d["PDET_name"] = d["PDET_name"].apply(lambda x: unidecode.unidecode(str(x)))
d["PDET_name"] = d["PDET_name"].apply(lambda x: nlwrap(x,20))
#d = d[d["PDET_name"].apply(lambda x: x in ["PUTUMAYO","MACARENA GUAVIARE"])]

DESCR = {
    "p36_c":"Agree with crop substitution",
    "p37_c":"Rating of crop substitution implementation"
}

cb = getCodebookFromExcel("docs/codebook_merged.xlsx")

def fixMiss(x):
    try:
        x = int(x)
    except:
        return np.nan

    if x == 5 or x < 0:
        return np.nan 
    else:
        return x

for v in ["p36_c","p37_c"]:
    sub = d.copy()
    sub = sub[["PDET_name",v]]
    sub[v] = sub[v].apply(fixMiss) 
    sm = (sub
        .groupby("PDET_name")[v]
        .value_counts(normalize=True)
        .rename("pst")
        .reset_index()
    )
    sm["pst"] = sm["pst"] * 100

    p = sns.catplot(x = v, y = "pst", hue = "PDET_name",kind="bar", data = sm,height=8,aspect=1.2)

    p._legend.set_title("PDET")

    plt.ylabel("%")
    plt.xlabel(DESCR[v])
    plt.xticks([0,1,2,3],cb[v.upper()].values())

    plt.savefig(f"./plots/{v.upper()}_PDET_dist.png")
