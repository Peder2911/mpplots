
import os
import json
import pandas as pd

from mytypes import Codebook,Descriptions
from typing import List,Dict,Union

from collections import defaultdict 

import yaml

import numpy as np

from toolz import curry
import re


fixedVname = lambda x: re.sub("(_AT|_FW)$","",x)

stripPrefix = lambda x: re.sub("(_FW|_AT)$","",x)

def daneCode(v):
    try:
        return "{0:05d}".format(int(v))
    except ValueError:
        return pd.NA

def genDeptName(name):
    return re.sub("[^A-Za-z]","",name)[:3].lower()

def cache(location):
    """
    Cache the result of a function as JSON, removing the need for repeated execution.
    """
    def cached(fn):
        def wrapper(*args,**kwargs):
            if os.path.exists(location):
                with open(location) as f:
                    d = json.load(f)
            else:
                d = fn(*args,**kwargs)
                with open(location,"w") as f:
                    json.dump(d,f,indent=4)
            return d

        return wrapper
    return cached

def getOldCodebook(dat: pd.DataFrame)-> Codebook:
    """
    Makes a dictionary of dictionaries mapping values to strings, used to annotate plots.
    """
    d = dict()
    for v in set(dat["Variable"]):
        vd = dict()
        for idx,r in dat[dat["Variable"] == v].iterrows():
            vd.update({str(r["Valor"]):str(r["Valor_Etiqueta"])})
        d.update({v:vd})
    return d

def getMergedCodebook(raw: pd.DataFrame)-> Dict[str,Dict[str,str]]:
    dat: Dict[str,Union[Dict,None]] = dict()
    nones = defaultdict(list) 

    replacements = {
        "Apply": "Yes",
        "Does not apply": "No"
    }
    def fixValue(value):
        try:
            return replacements[value]
        except KeyError:
            return value

    for idx,r in raw.iterrows():
        vname = r["Variablename"].upper()
        vname = fixedVname(vname)

        try:
            v = yaml.safe_load(r["Alternatives"])
            print(v)
            v = {k:fixValue(v) for k,v in v.items()}
        except: 
            dat[vname] = None
            continue

        try:
            if any([x is None for x in v.values()]):
                nones[json.dumps(v,indent=4)].append(vname)
                dat[vname] = None
                continue

        except AttributeError:
            dat[vname] = None
            continue
            
        dat[vname] = v

    def fixValue(value):
        if value is True:
            return "Yes"
        elif value is False:
            return "No"
        else:
            return str(value)

    try:
        comp = {k:v for k,v in dat.items() if v is not None}
        comp = {ko:{str(k):fixValue(v) for k,v in vo.items()} for ko,vo, in comp.items()}
    except:
        pass
    return comp

def getDescriptions(dat: pd.DataFrame) -> Descriptions:
    """
    Makes a dictionary of variable descriptions used to annotate plots
    """
    d = dict()
    for idx,r in dat.iterrows():
        label = r["Etiqueta"].split(".")[-1]
        d.update({fixedVname(r["Variable"]):label})
    return d

def getMergedDescriptions(dat: pd.DataFrame) -> Descriptions:
    """
    Makes a dictionary of variable descriptions used to annotate plots
    """
    dat.columns = [c.strip() for c in dat.columns]

    d = dict()
    for idx,r in dat.iterrows():
        d.update({fixedVname(r["Variablename"]).upper():r["Question"]})
    return d

@cache("cache/descr.json")
def getDescriptionsFromExcel(*args,**kwargs):
    return getMergedDescriptions(pd.read_excel(*args,**kwargs))

@cache("cache/codebook.json")
def getCodebookFromExcel(*args,**kwargs):
    return getMergedCodebook(pd.read_excel(*args,**kwargs))

@curry
def lookup(values: np.array,idx:str,cb: Codebook)-> pd.Series:
    lookup = lambda x: cb[idx].get(str(x),pd.NA)

    try:
        [int(v) for v in values]
    except ValueError:
        dtype = pd.CategoricalDtype(set(values),ordered=False)
    else:
        uval = set(values)
        res = [(lookup(v),v) for v in uval if lookup(v) is not pd.NA]
        res.sort(key=lambda x: int(x[1]))
        dtype = pd.CategoricalDtype([v[0] for v in res],ordered=True)

    uval = set(values)

    return pd.Series([*map(lookup,values)],dtype=dtype)

def fixMissing(v):
    if v > -1:
        return v
    else:
        return pd.NA

if __name__ == "__main__":
    codebook = getCodebookFromExcel("docs/codebook_merged.xlsx")
    desc = getDescriptionsFromExcel("docs/codebook_merged.xlsx")
    lkp = lookup(cb=codebook)
    lkp = lkp(idx="P32BC")

    x = lkp(["1","0","1","3"])

    print(lkp(["1","0","1"]))

