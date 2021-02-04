import yaml
from collections import OrderedDict
from scripts import andOr

class YamlOrderedDictLoader(yaml.SafeLoader):
  pass

YamlOrderedDictLoader.add_constructor(
  yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
  lambda loader, node: OrderedDict(loader.construct_pairs(node))
)

class groupObj:
  def __init__(self,locale,*args):
    self.children = []
    if(len([*args])):
      self.multiaddChild(args)
    self.locale = locale
    self.locations = []
    self.color = ""
    self.name = ""
    self.tags = []
    self.entry = ""

  def __add__(self,other):
    if type(other) == type(checkObj):
      self.addChild(other)
    elif type(other) == type(groupObj):
      children = other.children.copy()
      self.multiaddChild(children)
    else:
      raise ArithmeticError
  def __IADD__(self,other):
    self = self + other

  def __sub__(self,other):
    if type(other) == type(checkObj):
      index = self.children.index(other)
      self.children.pop(index)
      other.setParent= None
    elif type(other) == type(groupObj):
      children = other.children.copy()
      for child in children:
        index = self.children.index(child)
        self.children.pop(index)
    else:
      raise ArithmeticError
  def __ISUB__(self,other):
    self = self - other

  def __str__(self):
    childString = ""
    locations = ""
    for child in self.children:
      childString+=(str(child)+"\n")
    for location in self.locations:
      map = location[0]
      x = location[1]
      y = location[2]
      locations+="\n\t>Map:  {map}\n\t>Cord: [{x}, {y}]".format(map=map,x=x,y=y)
    comment="\nName: {name}\n>Tags:   {tags}\n>Locale: {locale}\n>Color:  {color}\n>Locations:{locations}\n>Children:{child}\n\n-----\n".format(name=self.name,tags=self.tags,color=self.color,locations=locations,child=childString,locale=self.locale)
    return comment


  def setEntry(self,entry):
    self.entry = entry

  def setColor(self,color:str):
    self.color = color

  def setCustomName(self,name:str):
    self.name = name
  def setName(self,name:str):
    self.setCustomName(name)

  def testName(self,name:str):
    if len(name)==0:
      self.setName(self.locale)
      return False
    elif name!=self.name:
      return False
    return True

  def addChild(self,child):
    self.children.append(child)
    child.setParent(self)

  def addLocations(self,map:str,x:int,y:int):
    self.locations.append([map,x,y])

  def addTag(self,tags):
    if type(tags)==type(""):
      tags = tags.split(",")
    assert type(tags)==type([])
    for tag in tags:
      self.tags.append(tag)

  def multiaddChild(self,children):
    if len(children)==1 and type(args)==type([]):
      for child in children:
        if type(child) == type(list):
          self.multiaddChild(child)
        elif type(child)!=type(checkObj):
          index = children.index(child)
          children.pop(index)
          continue
        child.setParent(self)
      self.children += children
    elif len(args)==0:
      pass
    else:
      for child in children:
        if type(child) == type(checkObj()):
          self.addChild(child)
        elif type(child) == type([]):
          self.multiaddChild(child)
    pass

class checkObj:
  def __init__(self,check:str,reqStr:str,*args):
    self.parent = None
    self.check = check
    self.reqStr = reqStr
    self.reqYAML = reqStr
    if type(reqStr)==type(""):
      self.reqList = andOr.convertToLists(reqStr)
    else:
      self.reqList = reqStr
    self.reqJSON = self.reqList
    self.requirements = self.reqList
    self.name = ""
    self.types = []
    self.hosted = ""
    self.images = OrderedDict()

  def __str__(self):
    comment="\n{tab}>Name: {name}\n{tab}>{tab}Types:\t{types}\n{tab}>{tab}Check:\t{check}\n{tab}>{tab}Req:  \t{req}".format(tab="\t",name=self.name,check=self.check,req=self.reqYAML,types=self.types)
    if self.hosted != "":
      comment+="\n{tab}>{tab}Item:\t{item}".format(tab="\t",item=self.hosted)
    if len(self.images):
      comment+="\n{tab}>{tab}Images:".format(tab="\t")
      for image in self.images:
        comment+="\n{tab}>{tab}>{tab}{image}:{rev}{address}".format(tab="\t",image=image,rev=((" "*10)[len(image):]),address=self.images[image])
    return comment

  def setParent(self,parent:groupObj):
    self.parent = parent

  def setCustomName(self,name:str):
    self.name = name
  def setName(self,name:str):
    self.setCustomName(name)

  def addTypes(self,types):
    if type(types)==type(""):
      types = ",".join(types.split(", "))
      types = types.split(",")
    assert type(types)==type([])
    for tag in types:
      self.types.append(tag)

  def setHosted(self,input):
    self.hosted = input

  def addImage(self,parent,child):
    self.images[parent] = child
