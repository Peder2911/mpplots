
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
import numpy as np
from util import *

sns.set()

DESCR = {
    "p36_c":"Agree with crop substitution",
    "p37_c":"Rating of crop substitution implementation"
}


cb = getCodebookFromExcel("docs/codebook_merged.xlsx")
d = pd.read_csv("raw/merged_data_PDET.csv",encoding="latin1")

def clfMuni(x):
    x = x.lower()
    if x in ["bojaya","novita"]:
        return "No PNIS"
    elif x in ["belen_de_los_andaquies", "montelibano", "orito", "santa_rosa_del_sur"]:
        return "PNIS"
    else:
        return "c"

d["grp"] = d.p2_muni.apply(clfMuni)
d = d[d["grp"] != "c"]

def sbsNa(x):
    if x == 5 or x < 0:
        return np.nan
    else:
        return x

for v in ["p36_c","p37_c"]:
    d[v] = d[v].apply(sbsNa)

    sm = (d[["grp",v]].groupby("grp")[v]
        .value_counts(normalize=True)
        .rename("pst")
        .reset_index()
    )
    print(sm)

    plt.clf()
    p = sns.catplot(x=v,y="pst",hue="grp",kind="bar",data=sm,height = 7)
    plt.xlabel(DESCR[v])
    plt.ylabel("%")
    p._legend.set_title("Group")
    plt.xticks(np.arange(4),cb[v.upper()].values())
    plt.savefig(f"plots/munigroups/{v}.png")


print(d.groupby("grp").size())


