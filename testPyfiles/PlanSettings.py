from connect import *
import collections
import re
import sys
sys.path.append(r"F:\Proton\RayStation\Script\create file")
from GUI import *
import wpf
from System.Windows import *
from System.Windows.Controls import *
from ctypes import *
from decimal import *
import json

with open(r"F:\Proton\RayStation\Script\create file\Data\PlanSetting.json") as f:
	PlanSetting = json.load(f,object_pairs_hook = collections.OrderedDict)


for part in PlanSetting.keys():
	for PS in PlanSetting[part]:
		PS
