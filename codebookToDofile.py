
from util import getCodebookFromExcel
import pandas as pd
import sys

cb = getCodebookFromExcel(sys.argv[1])

frames = []
for var, valMap in cb.items():
    keys = []
    values = []

    for key,val in valMap.items():
        keys.append(key)
        values.append('"'+val+'"')

    frames.append(pd.DataFrame({
        "variable": var,
        "key": keys,
        "val": values
    }))

codebookSheet = pd.concat(frames)

# Making a stata file

codebookSheet["pair"] = codebookSheet["key"] + " " + codebookSheet["val"]

vlines = (codebookSheet[["variable","pair"]]
    .groupby("variable")
    .agg(lambda x: " ".join(x))
    .reset_index()
)

dolines = []

print("Writing some STATA code...")
for idx,ln in vlines.iterrows():
    dolines.append(" ".join(["label define",ln["variable"],ln["pair"]+",","replace"]))
    dolines.append(" ".join(["label values",ln["variable"],ln["variable"]]))
with open("dofiles/translate.do","w") as f:
    f.write("\n".join(dolines))
print("done!")
