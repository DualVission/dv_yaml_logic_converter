from collections import OrderedDict

def minMax(input:int,min=0,max=48):
  if input<min:
    return False
  if max<input:
    return False
  return input

islandNum = [
  "Forsaken Fortress",
  "Star Island",
  "Northern Fairy Island",
  "Gale Isle",
  "Crescent Moon Island",
  "Seven-Star Isles",
  "Overlook Island",

  "Four-Eye Reef",
  "Child Isle",
  "Spectacle Island",
  "Windfall Island",
  "Pawprint Isle",
  "Dragon Roost Island",
  "Flight Control Platform",

  "Western Fairy Island",
  "Rock Spire Isle",
  "Tingle Island",
  "Northern Triangle Island",
  "Eastern Fairy Island",
  "Fire Mountain",
  "Star Belt Archipelago",

  "Three-Eye Reef",
  "Greatfish Isle",
  "Cyclops Reef",
  "Six-Eye Reef",
  "Tower of the Gods",
  "Eastern Triangle Island",
  "Thorned Fairy Island",

  "Needle Rock Isle",
  "Islet of Steel",
  "Stone Watcher Island",
  "Southern Triangle Island",
  "Private Oasis",
  "Bomb Island",
  "Bird's Peak Rock",

  "Diamond Steppe Island",
  "Five-Eye Reef",
  "Shark Island",
  "Southern Fairy Island",
  "Ice Ring Isle",
  "Forest Haven",
  "Cliff Plateau Isles",

  "Horseshoe Island",
  "Outset Island",
  "Headstone Island",
  "Two-Eye Reef",
  "Angular Isles",
  "Boating Course",
  "Five-Star Isles"
]

warpLocation = [ "Forsaken Fortress", "Windfall Island", "Dragon Roost Island", "Tingle Island", "Greatfish Isle", "Tower of the Gods", "Southern Fairy Island", "Forest Haven", "Outset Island" ]

islandDict = OrderedDict()
for i in range(49):
  islandDict[islandNum[i]] = i

neighbors = []
for i in range(49):
  hold = []
  posX = i%7
  posY = i//7
  minCol = posY*7
  maxCol = minMax(minCol+6)
  west = minMax(i-1,minCol,maxCol)
  east = minMax(i+1,minCol,maxCol)
  nrth = minMax(i-7)
  suth = minMax(i+7)
  for dirc in [nrth,east,suth,west]:
    if dirc :
      if i!=dirc :
        hold.append(dirc)
  neighbors.append(hold)

print(neighbors)

neighborDict = OrderedDict()
i=0
for neighborhood in neighbors:
  hold = []
  for neighbor in neighborhood:
    hold.append(islandNum[neighbor])
  neighborDict[islandNum[i]]=hold
  i+=1

neighborLocales = OrderedDict()
baseString = "( Starting Island {} & Can Sail )"
for island in islandDict:
  if island not in neighborLocales:
    neighborLocales[island] = "Starting Island {}".format(island)
  else:
    neighborLocales[island] += " | Starting Island {}".format(island)
  if island in warpLocation:
    neighborLocales[island] += " | Can Play Ballad of Gales"
  for neighbors in neighborDict[island]:
    modString=baseString.format(island)
    if neighbors not in neighborLocales:
      neighborLocales[neighbors] = modString
      continue
    neighborLocales[neighbors] += " | {}".format(modString)

for island in neighborLocales:
  islandList = (neighborLocales[island]).split(" | ")
  islandList.sort()
  islandString = " | ".join(islandList)
  neighborLocales[island] = islandString
  print(island,"\n\t",neighborLocales[island])

def locale
