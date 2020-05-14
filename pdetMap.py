
import geopandas as gpd
import pandas as pd
import topojson

raw = gpd.read_file("shp/mun_geo.shp")

key = pd.read_csv("raw/MunicipiosPDET.csv")

print("fixing")
key = key.rename(columns = {
    "CodigoMunicipio":"code",
    "CodigoSubregion":"PDET",
    "NombreSubregion":"PDETname"
})


key = key[["code","PDET","PDETname"]]

codeFmt = lambda x: "{0:05d}".format(int(x))
key["code"] = key["code"].apply(codeFmt)
raw["code"] = raw["CODANE2"].apply(codeFmt)

print("merging")
raw = raw.merge(key,on="code")
print("dissolving")
pdets = raw.dissolve("PDET")
pdets.to_file("cache/pdet.geojson",driver="GeoJSON")
print("topo-simplifying")
t = topojson.Topology(pdets)
t = t.toposimplify(0.03)
t.to_gdf().to_file("cache/s_pdet.geojson",driver="GeoJSON")
print("done!")
