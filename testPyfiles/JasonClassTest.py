import json
import sys
sys.path.append(r"F:\Proton\RayStation\Script\create file")
from objectbuilder import ObjectBuilder,MAPPING_ROOT_CLASS,ClassToJason_method

with open(r"F:\Proton\RayStation\Script\create file\Data\NewClinicalJsonClass.json") as f:
	ClinicalGoalJson = json.load(f)

class Root:
	pass

class Part:
	pass

class Protocol:
    pass

class Roi:
    pass

class Constraint:
	pass

object_mapping ={MAPPING_ROOT_CLASS:Root,'Part':Part,'Roi':Roi,'Protocol':Protocol,'Constraint':Constraint}

builder = ObjectBuilder(mapping=object_mapping)
result = builder.build(ClinicalGoalJson)
jsonString = json.dumps(result , default=ClassToJason_method)
print(jsonString==json.dumps(ClinicalGoalJson))
print(result.Part[0].Protocol[0].Roi[0].Constraint[0].GoalCriteria)
