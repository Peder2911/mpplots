from typing import List,Tuple
from matplotlib.colors import ListedColormap

mapsColors = [
    (255,194,0),
    (237,125,47),
    (165,163,166),
    (68,115,197),
]

def cfloats(colors: List[Tuple[int,int,int]])->List[List[float]]:
    return [[c/255 for c in rgb] for rgb in colors]
mapsCmap = ListedColormap(cfloats(mapsColors))
barColor = "#66BDE7"

