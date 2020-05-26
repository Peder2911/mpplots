
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
from util import *
from functools import reduce
from operator import add
import numpy as np
import textwrap

sns.set()

codebook = getCodebookFromExcel("docs/codebook_merged.xlsx")

dat = pd.read_csv("raw/merged_data_PDET.csv",encoding="latin1")
dat.columns = [c.upper() for c in dat.columns]


nlwrap = lambda x,w: "\n".join(textwrap.wrap(x,w))

"""
(1) 
look at the association between substitution of illicit crops and support for
the peace process. I think we should set it up as a regression where you
regress support for the peace process (P34 or P35) on the relevant illicit
crops variables (abbey steele (Guest), Michael Lee Weintraub (Guest), Helga
Malmin Binningsbø or Marianne Dahl, question numbers please) as well as a
minimal set of standard controls, let's do age, gender, and PDET fixed effects.
If you can set that up as a simple regression and then, if the association is
significant, simulate and graph the effect?
"""

# Satisfied with peace agreement ...
DEP = [
    "P34", # Content
    "P35" # Implementation
]

INDEP = [
    "P36_C", # Support crop subs.
    "P37_C", # Happy with crop subs.
    "P74_X", # Biggest problem in community.
]

DESCR = {
    "P34":"Satisfaction with content of peace agreement (mean)",
    "P35":"Satisfaction with implementation of peace agreement (mean)",
    "P36_C":"Do you support crop substitution?",
    "P37_C":"How well do you think that crop substitution is being implemented?",
    "P74_X":"What is the biggest problem in your community?",
}

ALL = DEP+INDEP

fixNa = lambda x: np.nan if x < 0 else x
for v in ALL:
    dat[v] = dat[v].apply(fixNa)

comb = lambda dep,indep: [(dep,var) for var in indep]
COMBINATIONS = reduce(add,[comb(var,INDEP) for var in DEP])

def corrPlot(data,dep,indep):
    sub = data[[dep,indep]].dropna()

    grp = sub.groupby(indep)
    agg = grp.agg("mean").reset_index()

    plt.clf()
    fig,ax = plt.subplots()
    fig.set_size_inches(8,6)
    bp = sns.barplot(x=dep,y=indep,data=agg,orient="h",ax=ax)

    plt.xlabel(DESCR[dep])
    plt.title(nlwrap(DESCR[indep],40))
    plt.ylabel("")

    ticks = [nlwrap(t,20) for t in codebook[indep].values()]
    plt.yticks(np.arange(sub[indep].max()),ticks)

    plt.subplots_adjust(left=0.3)

    plt.savefig(f"plots/corr/{dep}_{indep}_bar.png")

    #print(agg)

for dep,indep in COMBINATIONS:
    try:
        corrPlot(dat,dep,indep)
    except pd.core.base.DataError as e:
        print(f"{dep} x {indep} failed: {e}")
    else:
        print(f"{dep} x {indep} succeeded")



"""
(2)
something that looks at the association between support for the peace accord
(both if voted for and the support variable) vs support for implementation.
Here they want to look at the 'off diagonal' ones, i.e. those that did NOT like
the agreement but who now nevertheless support the implementation. Are there
many of these, if yes where are they (maybe map?), can we say anything about
their profiles (in terms of other background characteristics)?  
"""


