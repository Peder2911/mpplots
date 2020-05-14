
import pandas as pd
from string import ascii_letters

from util import getCodebookFromExcel, getDescriptionsFromExcel

import seaborn as sns
from matplotlib import pyplot as plt

from style import mapsColors,cfloats

import textwrap

import re

sns.set()

# ========================================================

dat = pd.read_csv("raw/merged_data_PDET.csv",encoding="latin1",low_memory=False)
codebook = getCodebookFromExcel("docs/codebook_merged.xlsx")
desc = getDescriptionsFromExcel("docs/codebook_merged.xlsx")

columns = ["p19_" + l for l in ascii_letters[:8] + ascii_letters[11:15]]

# ========================================================

# ========================================================

data = dat[columns]# + ["PDET"]]
#data["PDET"] = data["PDET"].apply(lambda x: str(int(x)))

def varTgt(c):
    fullDesc = desc[c.upper()]
    m = re.search("(?<=trust ).*",fullDesc)
    if m:
        ent = m[0]
        ent = re.sub("([Ii]n )?([Tt]he )?","",ent).title()
        ent = "\n".join(textwrap.wrap(ent,40))
        return ent
    else:
        return "NA"

def fixMissing(v):
    if v > 0:
        return v
    else:
        return pd.NA
for c in columns:
    data[c] = data[c].apply(fixMissing)

data.columns = [varTgt(c) for c in data.columns]

data = data.dropna()
data = data.melt()

data["Trust"] = data["value"]

plt.clf()
cp = sns.catplot(x="Trust",col="variable",
    height=3,aspect=1.4, col_wrap=4,
    palette = cfloats(mapsColors[::-1]),
    kind="count",data=data)

cp.set_titles("{col_name}")
cp.despine()
cp.set_xticklabels(["None","Little","Some","Much"])
plt.savefig("plots/11_P19.png")
