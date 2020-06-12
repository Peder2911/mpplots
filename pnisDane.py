
import geopandas as gpd
import pandas as pd
from matplotlib import pyplot as plt

pnis = pd.read_excel("raw/pnis.xlsx")
muni = gpd.read_file("shp/mun_geo.shp")

pnis["dane"] = pnis[pnis.columns[2]].apply(lambda x: f"{x:05d}")

muni["dane"] = muni["CODANE2"]
pnismuni = muni.merge(pnis,on="dane")

pnismuni["col"] = pnismuni[pnis.columns[6]]
ax = muni.plot(color="white",edgecolor="gray",alpha=0.2,figsize=(10,13))
pnismuni.plot(ax=ax,color="green")
plt.savefig("/tmp/p.png")
