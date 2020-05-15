from typing import List,Tuple
from matplotlib.colors import ListedColormap

mapsColors = [
    (255,194,0),
    (237,125,47),
    (165,163,166),
    (90,155,214),
    (68,115,197),
]

extendedColors = [
    (69, 113, 197),
    (202, 72, 161),
    (233, 58, 59),
    (237, 124, 47),
    (255, 193, 1),
    (162, 199, 6),
    (90, 155, 214),
    (208, 134, 185),
    (228, 135, 135),
    (165,163,166),
]

def cfloats(colors: List[Tuple[int,int,int]])->List[List[float]]:
    return [[c/255 for c in rgb] for rgb in colors]
mapsCmap = ListedColormap(cfloats(mapsColors))
barColor = "#66BDE7"

