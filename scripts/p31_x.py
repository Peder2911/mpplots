
import pandas as pd

d = pd.read_csv("raw/merged_data_PDET.csv",encoding="latin1")[["PDET","p31_x"]]

def reg(ser):
    m = ser.mode()
    return sum([v == m for v in ser])

g = d.groupby("PDET")
gsizes = [len(grp) for grp in g.groups.values()]
a = g.agg(reg)
a["gsizes"] = gsizes
a["prop"] = a["p31_x"] / a["gsizes"]
a["mode"] = g.agg(lambda x: x.mode())

a = a.rename(columns = {
    "p31_x": "agreeWithMode",
    "pdetSize":"gsizes",
    "prop":"propAgree"
})

print(a)

a.to_csv("stats/p31_x_pdet.csv")
