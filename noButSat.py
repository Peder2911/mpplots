
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
from util import *
import textwrap
nlwrap = lambda x,y: "\n".join(textwrap.wrap(x,y))

sns.set()

cb = getCodebookFromExcel("docs/codebook_merged.xlsx")

data = pd.read_csv("raw/merged_data_PDETf.csv",encoding="latin1")
data = data[data["p22_x"] == 2]
data = data[data["p34"].apply(lambda x: x in [3,4])]

for v in ["p6","PDET_name","p9","p8"]:
    plt.clf()
    d = data.copy()
    d = d[d[v].notna()]

    try:
        d[v] = d[v].apply(lambda x: cb[v.upper()][str(int(x))])
    except Exception as e:
        print(f"{e}")
    d[v] = d[v].apply(lambda x: nlwrap(x,20))
    print(d[v].value_counts())

    try:
        fig,ax = plt.subplots()
        if v == "PDET_name":
            fig.set_size_inches(8,8)
        else: 
            fig.set_size_inches(8,5)
        fig.subplots_adjust(bottom=0.15,left=0.3)
        
        sns.countplot(y=v,data=d,ax=ax)
        plt.xlabel("")
        plt.ylabel("")

        locs,labes = plt.xticks()
        plt.xticks([int(i) for i in np.linspace(0,max(locs),8)])

        plt.savefig(f"plots/oddonesout/{v}.png")
    except Exception as e:
        print(f"Something went wrong: {e}")
        pass
    plt.close()
