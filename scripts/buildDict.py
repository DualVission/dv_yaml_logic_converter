import yaml
from collections import OrderedDict
import re

from scripts import andOr
from paths import *

from class_creator.class_ms import *

class locationFile:
  def __init__(self,tracker="EmoTracker"):
    with open(DATA_FILE) as f:
      data = (yaml.load(f, YamlOrderedDictLoader)).copy()
      f.close()
      del f
    self.tracker = tracker
    self.tracker_name = data["Tracker Data"]["Name"]
    self.tracker_game = data["Tracker Data"]["Game"]
    self.tracker_creator = data["Tracker Data"]["Creator"]

    self.input = data["Input"]
    self.macro = self.input["Macros"]
    self.base = self.input["Base Logic"]
    self.tags = (self.input["Data Tags"]).split(", ")
    self.mods = OrderedDict()
    self.ignore = OrderedDict([("Macros",""),("Checks","")])
    self.extra = OrderedDict([("Macros",""),("Groups","")])
    self.spec = OrderedDict([("Checks","")])
    if("Logic Modification" in self.tags):
      self.mods = self.input["Logic Mod"]
    if("Ignore" in self.tags):
      self.ignore = self.input["Ignore"]
    if("Append" in self.tags):
      self.extra = self.input["Append"]
    if("Special Case" in self.tags):
      self.spec = self.input["Special Case"]

    self.output = data["Output"]
    self.split = self.output["Locations"]["Split"]
    self.export = self.output["Locations"]["File"]
    self.keys = self.output["Keys"]
    self.item_search = OrderedDict()

    # self.processed = None
    self.processed_locales = OrderedDict()
    self.processed_groups = OrderedDict()
    self.processed_checks = OrderedDict()
    self.processed_macros = OrderedDict()

    # self.unprocessed = None
    self.unprocessed_locales = OrderedDict()
    self.unprocessed_groups = OrderedDict()
    self.unprocessed_checks = OrderedDict()
    self.unprocessed_macros = OrderedDict()

    self.text = ""

    self.raw_macros = OrderedDict()
    self.raw_checks = OrderedDict()
    self.raw_locales = OrderedDict()
    self.raw_groups = OrderedDict()
    self.raw_spec = OrderedDict()

  def __str__(self):
    macroString = ""
    for macro in self.processed_macros:
      macroString+=str(self.processed_macros[macro])
    groupsString = ""
    for group in self.processed_groups:
      groupsString+=str(self.processed_groups[group])
    return "{tracker}\n{name}\n\n\nMacros:\n{macros}\n\nGroups:\n{groups}".format(tracker=self.tracker,groups=groupsString,name=self.tracker_name,macros=macroString)

  def __add__(self,other):
    self.text = self.text+other
  def __IADD__(self,other):
    self = self + other

  def ingest(self):
    with open(os.path.join(LOGIC_PATH,self.macro)) as f:
      macros = (yaml.load(f, YamlOrderedDictLoader)).copy()
    with open(os.path.join(LOGIC_PATH,self.base)) as g:
      checks = (yaml.load(g, YamlOrderedDictLoader)).copy()
    to_del = []
    for macro in macros:
      if macro in list(self.ignore["Macros"]):
        to_del.append(macro)
    for macro in to_del:
      del macros[macro]
    to_del = []
    for check in checks:
      if check in list(self.ignore["Checks"]):
        to_del.append(check)
    for check in to_del:
      del checks[check]
    for macro in self.extra["Macros"]:
      macros[macro] = self.extra["Macros"][macro]["Needs"]
    for mod in self.mods:
      general_mode = self.mods[mod]["Logic Mode"]
      with open(os.path.join(LOGIC_PATH,mod)) as h:
        mod_data = (yaml.load(h, YamlOrderedDictLoader)).copy()
      for change in mod_data:
        spec_mode = mod_data[change]["Mode"][0]
        if spec_mode == "o":
          for i in mod_data[change]:
            if i == "Mode":
              continue
            if i == general_mode:
              if i == "Types":
                checks[change][i] = "{0}, {1}".format(mod_data[change][i],self.mods[mod]["Needs"])
              elif i == "Needs":
                checks[change][i] = "({0}) & {1}".format(mod_data[change][i],self.mods[mod]["Needs"])
              continue
            checks[change][i] = mod_data[change][i]
        elif spec_mode == "a":
          for i in mod_data[change]:
            if i == "Mode":
              continue
            if i == general_mode:
              if i == "Types":
                checks[change][i] = "{2}, {0}, {1}".format(mod_data[change][i],self.mods[mod]["Needs"],checks[change][i])
              elif i == "Needs":
                if(mod_data[change][i][0] == "|"):
                  checks[change][i] = "({2}) | (({0}) & {1})".format(mod_data[change][i][1:],self.mods[mod]["Needs"],checks[change][i])
                elif(mod_data[change][i][0] == "&"):
                  checks[change][i] = "({2}) {0} & {1}".format(mod_data[change][i],self.mods[mod]["Needs"],checks[change][i])
                checks[change][i] = "({2}) & ({0}) & {1}".format(mod_data[change][i],self.mods[mod]["Needs"],checks[change][i])
              continue
            checks[change][i] = mod_data[change][i]
        elif spec_mode == "f":
          for i in mod_data[change]:
            if i == "Mode":
              continue
            if i == general_mode:
              if i == "Types":
                checks[change][i] = "{0}, {1}".format(mod_data[change][i],self.mods[mod]["Needs"])
              elif i == "Needs":
                checks[change][i] = "({0}) & {1}".format(mod_data[change][i],self.mods[mod]["Needs"])
              continue
            elif i == "Item":
              i = "Hosted Item"
            checks[change][i] = mod_data[change][i]
        else:
          continue
    self.raw_checks = checks
    self.raw_macros = macros
    for check in checks:
      localeDict = OrderedDict()
      locale = (check.split(" - "))[0]
      check_name = " - ".join((check.split(" - ")).pop(0))
      localeDict[check_name] = checks[check]
      if locale not in self.raw_locales:
        self.raw_locales[locale] = localeDict
        self.unprocessed_locales[locale] = localeDict
      else:
        self.raw_locales[locale][check_name] = checks[check]
        self.unprocessed_locales[locale][check_name] = checks[check]
    for grp in self.spec:
      self.raw_spec[grp]=cleanSpec(self.spec[grp])


  def digest(self):
    for macro in self.raw_macros:
      items = self.raw_macros[macro]
      set_strings = checkObj(check=macro,reqStr=items)
      set_strings.setName(macro)
      if macro  not in self.unprocessed_macros:
        self.unprocessed_macros[macro] = set_strings
        if macro not in self.ignore["Macros"]:
          self.processed_macros[macro] = set_strings
    for check in self.raw_checks:
      items = self.raw_checks[check]["Need"]
      checkVar = checkObj(check=check,reqStr=items)
      if macro not in self.ignore["Checks"]:
        self.unprocessed_checks[check] = checkVar
    to_del = []
    for checks in self.raw_spec["Checks"]:
      for check in self.raw_spec["Checks"][checks]["Checks"]:
        asoc = self.raw_spec["Checks"][checks]["Checks"][check]["Associated Check"]
        if asoc != "None":
          checkStr = asoc.format(l="*",n="*")
          locl = (asoc.split(" - "))[0]
          to_del+=self.searchChecks(locl,checkStr,self.unprocessed_checks,"","")
    for check in to_del:
      del self.unprocessed_checks[check]
    check_locales = [((check.split(" - "))[0]) for check in self.unprocessed_checks]
    check_locales.sort()
    results = []
    for locale in check_locales:
      if locale not in results:
        results.append(locale)
    check_locales=results
    del results
    for locale in self.raw_locales:
      if locale not in check_locales:
        del self.unprocessed_locales[locale]
    try:
      with open(os.path.join(LOCALE_PATH,self.keys["Groups"])) as h:
        group_data = (yaml.load(h, YamlOrderedDictLoader)).copy()
      self.raw_groups = group_data
      for locale in self.unprocessed_locales:
        groupsLocale = OrderedDict()
        try:
          locale_data = group_data[locale]
          locale_data["Tags"] = (locale_data["Tags"]).split(", ")
          if "Custom Groups" in locale_data["Tags"]:
            for group in locale_data["Groups"]:
              groupVar = groupObj(locale)
              groupVar.addTag(locale_data["Tags"])
              groupVar.setName(group)
              if "Multiple Locations" in groupVar.tags:
                locations = locale_data["Groups"][group]["Locations"]
                for location in locations:
                  x = locations[location]["x"]
                  y = locations[location]["y"]
                  map = locations[location]["Map"]
                  groupVar.addLocations(map=map,x=x,y=y)
              else:
                location = locale_data["Groups"][group]["Location"]
                x = location["x"]
                y = location["y"]
                map = location["Map"]
                groupVar.addLocations(map=map,x=x,y=y)
              if "Color" in groupVar.tags:
                groupVar.setColor(locale_data["Groups"][group]["Color"])
              if "Entry" in groupVar.tags:
                groupVar.setEntry(locale_data["Groups"][group]["Entry"])
              checks = locale_data["Groups"][group]["Checks"]
              for check in checks:
                checkName = ("{0} - {1}").format(locale,check)
                self.processed_checks[checkName]=self.searchChecks(locale,checkName,self.unprocessed_checks,checks[check],groupVar)
                if type(self.processed_checks[checkName])==type([""]):
                   self.processed_checks[checkName] = [check for check in self.processed_checks[checkName] if check.check not in self.ignore["Checks"]]
              self.processed_groups[group]=groupVar
              groupsLocale[group]=groupVar
          else:
            group = locale
            groupVar = groupObj(locale)
            groupVar.addTag(locale_data["Tags"])
            if "Multiple Locations" in groupVar.tags:
              locations = locale_data["Locations"]
              for location in locations:
                x = locations[location]["x"]
                y = locations[location]["y"]
                map = locations[location]["Map"]
                groupVar.addLocations(map=map,x=x,y=y)
            else:
              location = locale_data["Location"]
              x = location["x"]
              y = location["y"]
              map = location["Map"]
              groupVar.addLocations(map=map,x=x,y=y)
            if "Color" in groupVar.tags:
              groupVar.setColor(locale_data["Color"])
            if "Entry" in groupVar.tags:
              groupVar.setEntry(locale_data["Entry"])
            if "Custom Names" in groupVar.tags:
              if "Name" in locale_data:
                groupVar.setName(locale_data["Name"])
              else:
                groupVar.setName(locale)
              for check in locale_data["Checks"]:
                checkTrue = ("{0} - {1}").format(locale,check)
                checkName = locale_data["Checks"][check]
                working=self.searchChecks(locale,checkTrue,self.unprocessed_checks,checkName,groupVar)
                self.processed_checks[checkTrue]=working
                for part in working:
                  raw_check=part.check
                  self.processed_checks[raw_check]=working
            else:
              groupVar.setName(locale)
              checkStr = locale+" - *"
              working = self.searchChecks(locale,checkStr,self.unprocessed_checks,"",groupVar)
              for part in working:
                self.processed_checks[part.check]=part
            self.processed_groups[group]=groupVar
            groupsLocale[group]=groupVar
          self.processed_locales[locale]=groupsLocale
        except:
          raise RuntimeError
    except:
      raise RuntimeError

  def specialChecks(self):
    checkDict = OrderedDict()
    for check in self.raw_checks:
      items = self.raw_checks[check]["Need"]
      checkVar = checkObj(check=check,reqStr=items)
      checkDict[check] = checkVar
    for checks in self.raw_spec["Checks"]:
      tags = self.raw_spec["Checks"][checks]["Tags"]
      orderList = []
      root = self.raw_spec["Checks"][checks]
      checksToAdd = OrderedDict()
      checksAddBack = OrderedDict()
      for check in root["Checks"]:
        asoc = root["Checks"][check]["Associated Check"]
        if asoc != "None":
          checksAddBack[check] = root["Checks"][check]
        else:
          checksToAdd[check] = root["Checks"][check]
        orderList.append(check)
      localeGrp = []
      checkGrp = []
      for check in checksAddBack:
        asoc = (checksAddBack[check]["Associated Check"]).format(l="*")
        posChecks = self.searchChecks("",asoc,checkDict,"","")
        checkGrp+=posChecks
        for pos in posChecks:
          locale = (pos.split(" - "))[0]
          if locale not in localeGrp:
            localeGrp.append(locale)
      i = 0
      mapLoc = self.raw_spec["Checks"][checks]["Map"]
      offsetX = self.raw_spec["Checks"][checks]["Location"]["x"]
      offsetY = self.raw_spec["Checks"][checks]["Location"]["y"]
      deltaX = self.raw_spec["Checks"][checks]["Location"]["dx"]
      deltaY = self.raw_spec["Checks"][checks]["Location"]["dy"]
      size = (self.raw_spec["Checks"][checks]["Size"]).split(", ")
      sizeX = int(size[0])
      sizeY = int(size[1])
      for locale in localeGrp:
        groupVar = groupObj(locale)
        rawName = self.raw_spec["Checks"][checks]["Group Name"]
        name = rawName.format(l=locale,n=i)
        groupVar.setName(name)
        groupVar.addTag(tags)
        posX = i%sizeX
        posY = i//sizeX
        newX = posX*deltaX+offsetX
        newY = posY*deltaY+offsetY
        groupVar.addLocations(mapLoc,newX,newY)
        i+=1
        for check in orderList:
          if check in checksAddBack:
            hold = checksAddBack[check]
            rawName = hold["Associated Check"]
            name = rawName.format(l=locale,n=i)
            reqStr = (checkDict[name]).reqStr
            checkVar = checkObj(check=name,reqStr=reqStr)
            checkVar.addTypes((checkDict[name]).types)
          elif check in checksToAdd:
            hold = checksToAdd[check]
            rawName = check
            name = rawName.format(l=locale,n=i)
            reqStr = hold["Need"]
            checkVar = checkObj(check="None",reqStr=reqStr)
            checkVar.addTypes(hold["Types"])
          else:
            raise RuntimeError
          groupVar.addChild(checkVar)
          if "Custom Images" in tags and "Images" in hold:
            for image in hold["Images"]:
              checkVar.addImage(image,hold["Images"][image])
          if "Hosted Item" in tags and "Hosted Item" in hold:
            part = hold["Hosted Item"]
            checkVar.setHosted(part.format(l=locale,n=i))
          checkVar.setName(check)
          self.processed_checks[checkVar.check]=checkVar
        self.processed_groups[groupVar.name]=groupVar
        if locale in self.processed_locales:
          groupsLocale = self.processed_locales[locale]
          groupsLocale[groupVar.name] = groupVar
          self.processed_locales[locale] = groupsLocale
        else:
          groupsLocale = OrderedDict()
          groupsLocale[groupVar.name] = groupVar
          self.processed_locales[locale] = groupsLocale


  def searchChecks(self,locale:str,checkStr:str,searchDict:OrderedDict,name:str,parent:groupObj):
    processed_checks = []
    if "*" in checkStr:
      possible_checks = []
      if(checkStr[-1]=="*"):
        matchDef = checkStr[:-1]
        for key in searchDict:
          if re.search(matchDef,key):
            possible_checks.append(key)
      elif(checkStr[0]=="*"):
        matchDef = checkStr[1:]
        for key in searchDict:
          if re.search(matchDef,key):
            possible_checks.append(key)
      else:
        matchDef = checkStr.split("*")
        for key in searchDict:
          if matchDef[0] in key and matchDef[1] in key:
            possible_checks.append(key)
      for check in possible_checks:
        if len(name):
          searchDict[check].setName(name)
        else:
          searchDict[check].setName(check.split(" - ")[-1])
        searchDict[check].addTypes(self.raw_checks[check]["Types"])
        if type(parent)==type(groupObj("")):
          searchDict[check].setParent(parent)
          child = searchDict[check]
          parent.addChild(child)
          processed_checks.append(child)
        else:
          processed_checks.append(check)
    else:
      if type(name)==type(""):
        searchDict[checkStr].setName(name)
      else:
        name = (checkStr.split(" - "))[-1]
        searchDict[checkStr].setName(name)
      searchDict[checkStr].addTypes(self.raw_checks[checkStr]["Types"])
      if type(parent)==type(groupObj("")):
        child = searchDict[checkStr]
        parent.addChild(child)
        processed_checks.append(child)
      else:
        processed_checks.append(checkStr)
    return processed_checks

  def toEmoJSON(self):
    emoDict = OrderedDict()
    emoDict["Images"] = OrderedDict()
    emoDict["Images"]["Opened"] = "chest_opened_img"
    emoDict["Images"]["Unopened"] = "chest_unopened_img"
    emoDict["Hosted Item"] = "hosted_item"
    self.ingest()
    self.digest()
    self.specialChecks()
    with open(os.path.join(LOCALE_PATH,self.keys["Items"])) as f:
      hold = (yaml.load(f, YamlOrderedDictLoader)).copy()
    for types in hold_search:
      self.item_search[types] = hold_search[types]
    with open(os.path.join(LOCALE_PATH,self.keys["Types"])) as f:
      hold_search = (yaml.load(f, YamlOrderedDictLoader)).copy()
    for types in hold_search:
      self.item_search[types] = hold_search[types]
    for macro in self.processed_macros:
      hold = self.processed_macros[macro]
      titl = ("@"+"_".join((hold.name.lower()).split(" "))).strip("'")
      self.item_search[macro] = titl
    output=[]
    creatorStr=""
    if len(self.tracker_creator):
      if len(self.tracker_creator)>1:
        creatorStr=',\n\t\t"Creators":'
        for name in self.tracker_creator:
          creatorStr+='\n\t\t\t"{}",'.format(name)
      else:
        creatorStr=',\n\t\t"Creators "   : "{}"'.format(self.tracker_creator[0])
      if creatorStr[-1] == ",":
        creatorStr = creatorStr[:-1]
    header='''/*
\t{open}
\t\t"Tracker Name": "{name}",
\t\t"Game Name"   : "{game}"{creators}
\t{close},
\t{open}
\t\t"Created with": "dv_yaml_logic_converter",
\t\t"Tool by"     : "Zach the DualVission"
\t{close}
*/'''.format(name=self.tracker_name,game=self.tracker_game,creators=creatorStr,open="{",close="}")
    template ='''/* template
\t{
\t\t"name": "",
\t\t"access_rules": [ "" ],
\t\t"sections": [
\t\t\t{
\t\t\t\t"name": "",
\t\t\t\t"item_count": 1,
\t\t\t\t"access_rules": [ "" ]
\t\t\t},
\t\t],
\t\t"map_locations": [
\t\t\t{
\t\t\t\t"map": "map",
\t\t\t\t"x": 0,
\t\t\t\t"y": 0
\t\t\t}
\t\t]
\t},
*/'''
    macros=""
    #{
    #  "name": "can_play_winds_requiem",
    #  "access_rules": [ "windwaker,requiem" ],
    #  "sections": [{ "name": "access", "item_count": 1 }]
    #},
    sections = '{ "name": "access", "item_count": 1 }'
    for macro in self.processed_macros:
      hold = self.processed_macros[macro]
      name = "_".join((hold.name.lower()).split(" "))
      accs = ""
      for group in hold.reqList:
        reqs = ""
        for item in group:
          if item in self.item_search:
            strg = self.item_search[item]+","
          elif re.search('Can Access Other Location "',item):
            raw_check = item[len("                           "):-1]
            check = self.unprocessed_checks[raw_check]
            group = check.parent.name
            name = check.name
            strg = "@{group}/{name},".format(group=group,name=name)
          reqs+=(strg).strip("\\")
        if reqs[-1]==",":
          reqs = reqs[:-1]
        if len(accs)==0:
          accs+='"{}",'.format(reqs)
          continue
        accs+='\n\t\t                  "{}",'.format(reqs)
      if accs!="":
        if accs[-1]==",":
          accs = accs[:-1]
      macroString = '''\n\t/* {macro} */
\t{open}
\t\t"name": "{name}",
\t\t"access_rules": [ {accs} ],
\t\t"sections": [{sections}]
\t{close},'''.format(macro=macro,name=name,accs=accs,sections=sections,open="{",close="}")
      macros+=macroString
    groupsString = ""
    groupHeader = '''\n\t/* {group} */
\t{open}
\t\t"name"         : "{name}",
\t\t"sections"     : [{sections}],
\t\t"map_locations": [{location}]{add}
\t{close},'''
    checkHeader = '''\t\t\t{open}
\t\t\t\t"name"            : "{name}",
\t\t\t\t"item_count"      : {number},
\t\t\t\t"access_rules"    : [ {items} ],
\t\t\t\t"visibility_rules": [ "{types}" ]{add}
\t\t\t{close},'''
    for groups in self.processed_groups:
      group = self.processed_groups[groups]
      checks = group.children
      addTags = ""
      locString = ""
      groupTags = group.tags
      locations = group.locations
      if "Color" in groupTags:
        addTags+=',\n\t\t"color": "{color}"'.format(color=group.color)
      if "Entry" in groupTags:
        addTags+=',\n\t\t"access_rules": [ "{entry}" ]'.format(entry=group.entry)
      for location in locations:
        locString+='''\n\t\t\t{open}
\t\t\t\t"map": "{map}",
\t\t\t\t"x"  : {x},
\t\t\t\t"y"  : {y}
\t\t\t{close},'''.format(map=location[0],x=location[1],y=location[2],open="{",close="}")
        if location == locations[-1]:
          locString+="\n\t\t"
      checksString = ""
      processed_checks = []
      name=""
      numberChest=0
      assc=""
      types=""
      for check in checks:
        if len(processed_checks)!=0:
          if check.name in processed_checks:
            numberChest+=1
            continue
          else:
            checksString+=checkHeader.format(name=name,open="{",close="}",number=numberChest,items=assc,types=types,add=addCheck)
        else:
          processed_checks = []
        name=check.name
        numberChest=1
        assc = ""
        addCheck=""
        if len(check.reqList)>1:
          for required in check.reqList:
            reqs = ""
            for item in required:
              if item in self.item_search:
                strg = self.item_search[item]+","
              elif re.search('Can Access Other Location "',item):
                raw_check = item[len("                           "):-1]
                check = self.unprocessed_checks[raw_check]
                parent = check.parent.name
                name = check.name
                strg = "@{group}/{name},".format(group=parent,name=name)
              reqs+=(strg).strip("\\")
            if reqs[-1]==",":
              reqs = reqs[:-1]
            if len(accs)==0:
              assc+='"{}",'.format(reqs)
              continue
            assc+='\n\t\t                  "{}",'.format(reqs)
        else:
          for required in check.reqList:
            reqs = ""
            for item in required:
              if item in self.item_search:
                strg = self.item_search[item]+","
              elif re.search('Can Access Other Location "',item):
                raw_check = item[len("                           "):-1]
                check = self.unprocessed_checks[raw_check]
                parent = check.parent.name
                name = check.name
                strg = "@{group}/{name},".format(group=parent,name=name)
              reqs+=(strg).strip("\\")
            if reqs[-1]==",":
              reqs = reqs[:-1]
            if len(accs)==0:
              assc+='"{}",'.format(reqs)
              continue
            assc+='"{}"'.format(reqs)
        if assc!="":
          if accs[-1]==",":
            assc = accs[:-1]
        if "Custom Images" in group.tags:
          for image in check.images:
            attr = emoDict["Images"][image]
            setn = check.images[image]
            addCheck+=(",\n"+"\t"*4+'"{attr}": "{setn}"'.format(attr=attr,setn=setn))
        if "Hosted Item" in group.tags and check.hosted != "":
          attr = emoDict["Hosted Item"]
          setn = check.hosted
          addCheck+=(",\n"+"\t"*4+'"{attr}": "{setn}"'.format(attr=attr,setn=setn))
        types=""
        for tags in check.types:
          if tags in self.item_search:
            strg = self.item_search[tags]+","
          elif re.search('Can Access Other Location "',tags):
            raw_check = tags[len("                           "):-1]
            check = self.unprocessed_checks[raw_check]
            parent = check.parent.name
            name = check.name
            strg = "@{group}/{name},".format(group=parent,name=name)
          types+=(strg).strip("\\")
        processed_checks.append(name)
      checksString+=checkHeader.format(name=name,open="{",close="}",number=numberChest,items=assc,types=types,add=addCheck)
      if checksString[-1]==",":
        checksString=checksString[:-1]
      groupsString += (groupHeader.format(group=group.locale,open="{",close="}",name=group.name,sections=checksString,location=locString,add=addTags)).strip("\\")
    if self.split == "True" or self.split == True:
      macrosFile = "{header}\n[\n{macros}\n]\n{template}\n".format(header=header,macros=macros,template=template)
      groupsFile = "{header}\n[\n{groups}\n]\n{template}\n".format(header=header,groups=groupsString,template=template)
      return [ macrosFile, groupsFile ]
    else:
      outputFile = "{header}\n[\n\t//Macros\n{macros}\n//Groups\n{groups}\n]\n{template}\n".format(header=header,macros=macros,groups=groupsString,template=template)
      return [ outputFile ]

def cleanSpec(item):
  if type(item)==type(OrderedDict()):
    baseLevel = item
    for part in baseLevel:
      if type(baseLevel[part])==type(OrderedDict()):
        baseLevel[part] = cleanSpec(baseLevel[part])
        continue
      elif type(baseLevel[part])==type(2) or type(baseLevel[part])==type(True):
        continue
      working = "{l}".join((baseLevel[part]).split("$locale"))
      working = "{n}".join(working.split("$number"))
      working = "*".join(working.split("$all"))
      working = "".join(working.split("\\"))
      if part == "Tags":
        working = working.split(", ")
      baseLevel[part]=working
    return baseLevel
  elif type(item)==type(2) or type(item)==type(True):
    return item
  working = "{l}".join(item.split("$locale"))
  working = "{n}".join(working.split("$number"))
  working = "*".join(working.split("$all"))
  working = "".join(working.split("\\"))
  if part == "Tags":
    working = working.split(", ")
  baseLevel[part]=working
  return baseLevel
