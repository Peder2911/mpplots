

from util import getCodebookFromExcel,getDescriptionsFromExcel,fixMissing
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import textwrap

from style import mapsColors,cfloats

codebook = getCodebookFromExcel("docs/codebook_merged.xlsx")
desc = getDescriptionsFromExcel("docs/codebook_merged.xlsx")

sns.set()

voi = {
    "ELN responsible for violence": "p42a",
    "FARC responsible for violence": "p42b",
    "? responsible for violence": "p42c",
    "Know farc member": "p38_b",
    "Comfortable with farc member": "p47",

    "satag":"p34",
    "satimp":"p35",
    "victim":"p52",
}

b = voi["satimp"]  
#a = "p10"
a = voi["victim"] 

def makeCompPlot(data,a,b):
    data = data[[a,b]]
    data = data.rename(columns = {
        a:"a",
        b:"b",
    })


    data["a"] = ((data["a"])
        .apply(fixMissing)
        .dropna()
        .apply(lambda x: codebook[a.upper()][str(int(x))])
        )

    data["b"] = ((data["b"])
        .apply(fixMissing)
        .dropna()
        .apply(lambda x: codebook[b.upper()][str(int(x))])
        )

    g = (data.groupby("a")["b"]
        .value_counts(normalize=True)
        .mul(100)
        #.value_counts()
        .rename("percentage")
        .reset_index()
        .sort_values("a")
        )

    plt.clf()
    cp = sns.catplot(x="b",y="percentage",hue="a",kind="bar",data=g,height=7,aspect=1.1,
        palette = cfloats(mapsColors))
    plt.title("\n".join(textwrap.wrap(desc[b.upper()],70)))
    cp._legend.set_title("\n".join(textwrap.wrap(desc[a.upper()],15)))
    cp.set(xlabel = "",ylabel = "Percentage")
    #cp.set_xticklabels(rotation=45)
    plt.subplots_adjust(left = 0.1,right=0.75,top=0.90,bottom=0.1)
    plt.savefig(f"plots/cor_{a}_{b}.png")

d = pd.read_csv("raw/merged_data_PDET.csv",encoding="latin1",low_memory=False)
#d[voi["FARC responsible for violence"]] = d[voi["FARC responsible for violence"]] + 1

makeCompPlot(d,voi["satimp"],voi["victim"])
makeCompPlot(d,voi["satag"],voi["victim"])
makeCompPlot(d,voi["FARC responsible for violence"],voi["Know farc member"])
makeCompPlot(d,voi["FARC responsible for violence"],voi["Comfortable with farc member"])

"""
    "ELN responsible for violence": "p42a",
    "FARC responsible for violence": "p42b",
    "? responsible for violence": "p42c",
    "Know farc member": "p38_b",
    "Comfortable with farc member": "p47",
    """
