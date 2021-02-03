from scripts.buildDict import *
from class_creator.class_ms import *
from paths import *

import os
import yaml
from collections import OrderedDict
import itertools as iter


#phrase = andOr.testComplex
#phrase = "(Wind Waker & Swift Sail) | Hookshot"
#list1 = ["blue","green","red"]
#list2 = ["red"]
#results = andOr.convertToLists(phrase)
#print("\n")
#for part in results:
#  print(part)
#with open(os.path.join(LOGIC_PATH,"macros.txt")) as f:
#  data = (yaml.load(f, YamlOrderedDictLoader)).copy()

#for macro in data:
#  andOr.parseString(data[macro])

locFile = locationFile()

results=locFile.toEmoJSON()

with open(os.path.join(OUTPUT_PATH,"locations.json"),"w") as f:
  f.write(results[0])
