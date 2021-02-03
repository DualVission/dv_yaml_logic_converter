#from class_creator.class_ms import *
import itertools as iter
from sys import setrecursionlimit
import re
setrecursionlimit(100)

testComplex = """
(
  Can Access Forest Haven
  & (Grappling Hook | (Tricked Logic & Wind Waker))
  & Can Fly With Deku Leaf Outdoors
  & (Can Cut Grass | Magic Meter Upgrade)
)
| (Complex Logic & Wind Waker)
"""

def isAnd(input):
  return "&" in input

def isOr(input):
  return "|" in input

def isPara(input):
  return "(" in input and ")" in input

def isSub(input):
  output = False
  for part in input:
    if type(part)==type([""]):
      output = True
  return output

def getMaxDepth(input):
  output=0
  if isSub(input):
    output+=1
    subDepth=0
    curDepth=0
    for part in input:
      subDepth=getDepth(part)
      if subDepth>curDepth:
        curDepth=subDepth
    output+=curDepth
  return output

def parse_logic_expression(string):
  #Stolen directly from Lago's Randomizer
  string = "{".join(string.split("("))
  string = "}".join(string.split(")"))
  r = "([&|{}])"
  tokens = [str.strip() for str in re.split(r, string)]
  tokens = [token for token in tokens if token != ""]

  stack = []
  for token in tokens:
    if token == "{":
      stack.append("{")
    elif token == "}":
      nested_tokens = []

      nested_parentheses_level = 0
      while len(stack) != 0:
        exp = stack.pop()
        if exp == "{":
          if nested_parentheses_level == 0:
            break
          else:
            nested_parentheses_level -= 1
        if exp == "}":
          nested_parentheses_level += 1
        nested_tokens.append(exp)

      nested_tokens.reverse()
      stack.append("(")
      stack.append(nested_tokens)
      stack.append(")")
    else:
      stack.append(token)

  return stack

def cleanProduct(input1,input2):
  working = [*(iter.product(input1,input2))]
  output = []
  for item in working:
    result = []
    hold = [*item]
    for part in hold:
      result+=part
    output.append(result)
  return output

def getType(input):
  if isSub(input):
    return "isSub"
  elif isPara(input):
    return "isPara"
  elif isAnd(input):
    return "isAnd"
  elif isOr(input):
    return "isOr"
  else:
    return "isOther"

def convertToLists(input:str):
  elements = ["|","&","(",")"]
  output = []
  stack = parse_logic_expression(input)
  if isSub(stack) or isPara(stack):
    working = convertToListsSub(stack,elements)
  elif isOr(stack):
    working = convertToListsOr(stack,elements)
  elif isAnd(stack):
    working = convertToListsAnd(stack,elements)
  else:
    working = convertToListsNull(stack,elements)
  for part in working:
    result = []
    if type(part)==type([]):
      for subpart in part:
        if subpart not in result:
          result.append(subpart)
      if result not in output:
        result = fullSort(result)
        output.append(result)
    else:
      if [part] not in output:
        result = [part]
        output.append(result)
  return output

def fullSort(input:list):
  curLen = 100
  minLen = 100
  for part in input:
    curLen = len(part)
    if minLen>curLen:
      minLen = curLen
  fullLen = [i for i in range(minLen)]
  fullLen.sort(reverse=True)
  working = input[:]
  for i in fullLen:
    working.sort(key=lambda x: x[i])
  output = working[:]
  return output

def convertToListsOr(input,banned):
  output = []
  for part in input:
    if part not in banned:
      output.append([part])
  return output

def convertToListsAnd(input,banned):
  output = []
  for part in input:
    if part not in banned:
      output.append(part)
  return [output]

def convertToListsNull(input,banned):
  output = []
  for part in input:
    if part not in banned:
      output.append(part)
  return [output]

def convertToListsSub(input,banned):
  output = []

  if isSub(input) or isPara(input):
    if isOr(input):
      for part in input:
        result = convertToListsSub(part,banned)
        if type(result)==type([""]):
          for subpart in result:
            if type(subpart)==type(""):
              output.append(result)
              break
            elif type(subpart)==type([""]):
              output.append(subpart)
        elif type(result)==type(""):
          output.append(result)
    elif isAnd(input):
      working = input[:]
      working.sort(key=lambda x: x[0])
      working.sort(key=lambda x: type(x)==type([""]))
      options = []
      andStrs = []
      orLists = []
      for part in working:
        if type(part)==type(""):
          if part not in banned:
            andStrs.append(part)
        elif type(part)==type([""]):
          orLists.append(part)
      for part in orLists:
        if isSub(part):
          options.append(convertToListsSub(part,banned))
          continue
        elif isAnd(part):
          andStrs+=convertToListsAnd(part,banned)
          continue
        elif isOr(part):
          options.append(convertToListsOr(part,banned))
          continue
        elif len(part)==1:
          andStrs+=part
          continue
      mix = options[0]
      for i in range(1,len(options)):
        mix = cleanProduct(mix,options[1])
      for part in mix:
        output.append(part+andStrs)
  elif isOr(input):
    output = convertToListsOr(input,banned)
  elif isAnd(input):
    output = convertToListsAnd(input,banned)

  elif type(input)==type(""):
    if input not in banned:
      output = [input]
    else:
      return
  for part in output:
    if not len(part):
      index = output.index(part)
      output.pop(index)
  return output
