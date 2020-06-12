
from util import getCodebookFromExcel
import pandas as pd

cb = getCodebookFromExcel("docs/cb2.xlsx")


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
codebookSheet.to_csv("cache/cbsheet.csv",index=False)
print("done!")
