import os

try:
  from sys import _MEIPASS
  ROOT_PATH = _MEIPASS
  IS_RUNNING_FROM_SOURCE = False
except:
  ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
  IS_RUNNING_FROM_SOURCE = True

DATA_PATH = os.path.join(ROOT_PATH,"data")
SCRIPT_PATH = os.path.join(ROOT_PATH,"scripts")

INPUT_PATH = os.path.join(DATA_PATH,"input")
OUTPUT_PATH = os.path.join(DATA_PATH,"output")
DATA_FILE = os.path.join(INPUT_PATH,"data.yaml")

LOGIC_PATH = os.path.join(INPUT_PATH,"logic")
LOCALE_PATH = os.path.join(INPUT_PATH,"locale")
