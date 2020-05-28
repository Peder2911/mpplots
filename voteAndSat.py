
import pandas as pd import seaborn as sns
from matplotlib import pyplot as plt
from util import *

sns.set()

cb = getCodebookFromExcel("docs/codebook_merged.xlsx")

DESCR = {
    "p34": "Satisfied with agreement",
    "p35": "Satisfied with implementation",
}


d = pd.read_csv("raw/merged_data_PDET.csv",encoding="latin1")

d = d[d["p22_x"].apply(lambda x: x in [1,2])]

d = d[d["p34"].apply(lambda x: x in [1,2,3,4])]
d = d[d["p35"].apply(lambda x: x in [1,2,3,4])]

def orderedCats(cbdict):
    items = [(k,v) for k,v in cbdict.items()]
    items.sort(key = lambda x: int(x[0]))
    return [v for k,v in items]

def fixCatVar(v,vname):
    return pd.Categorical(
        v.apply(lambda x: cb[vname.upper()][str(int(x))]),
        categories=orderedCats(cb[vname.upper()])[2:],
        ordered=True)

for v in ["p34","p35"]:
    summarized = (d.groupby("p22_x")[v].value_counts(normalize=True,sort=False).rename("pst").reset_index())
    summarized["pst"] = summarized["pst"] * 100
    summarized[v] = fixCatVar(summarized[v],v) 
    print(summarized)

    p = sns.catplot(x="p22_x",y="pst",hue=v,kind="bar",data=summarized,aspect=1.4,height=5)

    fig = plt.gcf()
    fig.subplots_adjust(right=.7)

    p._legend.set_title(DESCR[v])

    plt.xlabel("Vote for agreement")
    plt.xticks([0,1],["Yes","No"])
    plt.ylabel("%")

    plt.savefig(f"plots/vote/{v}.png")
    plt.close()

