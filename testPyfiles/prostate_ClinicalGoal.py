# Script recorded 10 Jan 2019

#   RayStation version: 6.2.0.7
#   Selected patient: ...

from connect import *
import sys
sys.path.append("F:\Proton\RayStation\Script\create file")
from RayForm import *
from System.Windows.Forms import *
from ctypes import *
from decimal import *
import re

case = get_current('Case')
plan = get_current("Plan")


form = ClinicalGoalSelectForm(plan)
Application.Run(form)

if form.close_bool ==False:
	sys.exit()

if form.forClinicalGoal =="":
	msgbox(None,'Target is not entered','Caution',0x0000040)
	sys.exit()

for EF in plan.TreatmentCourse.EvaluationSetup.EvaluationFunctions:
	plan.TreatmentCourse.EvaluationSetup.DeleteClinicalGoal(FunctionToRemove = EF)


prescription=0
fraction = 0
plan_pre = 0
for beamset in plan.BeamSets:
	for pre in beamset.Prescription.DosePrescriptions:
		plan_pre += pre.DoseValue

if form.forClinicalGoal == plan.Name:
	plan_bool = True
	for beamset in plan.BeamSets:
		fraction += beamset.FractionationPattern.NumberOfFractions
		for pre in beamset.Prescription.DosePrescriptions:
			prescription += pre.DoseValue
		
else:
	plan_bool = False
	fraction = plan.BeamSets[form.forClinicalGoal].FractionationPattern.NumberOfFractions
	for pre in plan.BeamSets[form.forClinicalGoal].Prescription.DosePrescriptions:
		prescription += pre.DoseValue

roi_name_list = [roi.Name for roi in case.PatientModel.RegionsOfInterest]

class ClinicalGoalSetting():
	def __init__(self,goalcriteria,goaltype,acceptancelevel,parametervalue):
		self.GoalCriteria=goalcriteria
		self.GoalType=goaltype
		self.AcceptanceLevel=acceptancelevel
		self.ParameterValue=parametervalue

class ROIClinicalGoal():
	def __init__(self,roiname):
		self.RoiName = roiname
		self.CGsettings=[]
	def SetCrinicalGoal(self,goalcriteria,goaltype,acceptancelevel,parametervalue):
		instance = ClinicalGoalSetting(goalcriteria,goaltype,acceptancelevel,parametervalue)
		self.CGsettings.append(instance)
		



#clinical goal setting
CG_39 = {}
#Rectum Setting
rectum = {}
rectum.setdefault('7000',0.02)
rectum.setdefault('6000',0.10)
rectum.setdefault('5000',0.17)
rectum.setdefault('4000',0.30)
#Bladder Setting
bladder = {}
bladder.setdefault('6500',0.25)
bladder.setdefault('4000',0.50)
#Femoral Setting
femoral = {'FemoralHead (Right)' : '5000' ,'FemoralHead (Left)' : '5000'}
#Intestine Setting
intestine = {'L Intestine':'6100','S Intestine':'5500'}

CG_39.setdefault('rectum',rectum)
CG_39.setdefault('bladder',bladder)
CG_39.setdefault('femoral',femoral)
CG_39.setdefault('intestine',intestine)

CG_Hypo = {}

#Rectum Setting
rectum = {}
rectum.setdefault('5350',0.15)
rectum.setdefault('5000',0.18)
rectum.setdefault('3450',0.30)
#Bladder Setting
bladder = {}
bladder.setdefault('5450',0.25)
bladder.setdefault('3450',0.50)
#Femoral Setting
femoral = {'FemoralHead (Right)' : '4250' ,'FemoralHead (Left)' : '4250'}
#Intestine Setting
intestine = {'L Intestine':'5100','S Intestine':'4600'}

CG_Hypo.setdefault('rectum',rectum)
CG_Hypo.setdefault('bladder',bladder)
CG_Hypo.setdefault('femoral',femoral)
CG_Hypo.setdefault('intestine',intestine)

clinical_goal = {39:CG_39,'Hypo':CG_Hypo}

if prescription / fraction == 200:
	CG_setting = clinical_goal[39]
else:
	CG_setting = clinical_goal['Hypo']

prescription = Decimal(int(prescription))

#CTV
if plan_bool:
	CTV_Names=list(set([beamset.Prescription.PrimaryDosePrescription.OnStructure.Name for beamset in plan.BeamSets]))
else:
	CTV_Names=[plan.BeamSets[form.forClinicalGoal].Prescription.PrimaryDosePrescription.OnStructure.Name]

for CTV_Name in CTV_Names:
	plan.TreatmentCourse.EvaluationSetup.AddClinicalGoal(RoiName=CTV_Name, GoalCriteria="AtLeast", GoalType="DoseAtVolume", AcceptanceLevel= int(prescription * Decimal('0.93')), ParameterValue=0.98, IsComparativeGoal=False, Priority=2147483647)

#Rectum
for key,item in CG_setting['rectum'].items():
	plan.TreatmentCourse.EvaluationSetup.AddClinicalGoal(RoiName="Rectum", GoalCriteria="AtMost", GoalType="VolumeAtDose", AcceptanceLevel=item, ParameterValue=int(Decimal(key) / Decimal(int(plan_pre)) * prescription), IsComparativeGoal=False, Priority=2147483647)

#Bladder
for key,item in CG_setting['bladder'].items():
	plan.TreatmentCourse.EvaluationSetup.AddClinicalGoal(RoiName="Bladder", GoalCriteria="AtMost", GoalType="VolumeAtDose", AcceptanceLevel=item, ParameterValue=int(Decimal(key) / Decimal(int(plan_pre)) * prescription), IsComparativeGoal=False, Priority=2147483647)

#FemoralHead
for part,item in CG_setting['femoral'].items():
	plan.TreatmentCourse.EvaluationSetup.AddClinicalGoal(RoiName=part, GoalCriteria="AtMost", GoalType="DoseAtVolume", AcceptanceLevel=item, ParameterValue=0, IsComparativeGoal=False, Priority=2147483647)

#Intestine
for part,item in CG_setting['intestine'].items():
	if part in roi_name_list:
		plan.TreatmentCourse.EvaluationSetup.AddClinicalGoal(RoiName=part, GoalCriteria="AtMost", GoalType="DoseAtVolume", AcceptanceLevel=int(Decimal(item) / Decimal(int(plan_pre)) * prescription), ParameterValue=0, IsComparativeGoal=False, Priority=2147483647)
