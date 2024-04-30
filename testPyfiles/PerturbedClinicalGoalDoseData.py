from connect import *

case = get_current("Case")
beam_set = get_current("BeamSet")
plan = get_current("Plan")
Prescription=0
for BeamSet in plan.BeamSets:
	Prescription += BeamSet.Prescription.PrimaryDosePrescription.DoseValue


class ClinicalGoalperturbedDose():
	def __init__(self):
		self.PerturbedDoses=[]

class PerturbedDoseProperty():
	def __init__(self):
		self.BeamSetName=''
		self.x=0.0
		self.y=0.0
		self.z=0.0
		self.density=0.0
		self.ClinicalGoals=[]

class ClinicalGoals():
	def __init__(self):
		self.ClinicalGoalList=[]
	def getClinicalGoalClass(self,Roi):
		if len(self.ClinicalGoalList) == 0 or not Roi in [CG.RoiName for CG in self.ClinicalGoalList]:
			tmpClinicalGoal=ClinicalGoal()
			tmpClinicalGoal.RoiName=Roi
			self.ClinicalGoalList.append(tmpClinicalGoal)
			return tmpClinicalGoal
		else:
			for CG in self.ClinicalGoalList:
				if CG.RoiName == Roi:
					return CG


class ClinicalGoal():
	def __init__(self):
		self.RoiName=''
		self.RoiType=''
		self.PlanningGoalSettings=[]
		self.DoseData=DoseData()

class PlanningGoalSetting():
	def __init__(self):
		self.AcceptanceLevel=0.0
		self.GoalType=''
		self.ParameterValue=0.0
		self.Type=''

class DoseData():
	def setRelativeVolumeAtDoseValues(self,VolumeList,DoseList):
		for volume,dose in zip(VolumeList,DoseList):
			setattr(self,"V" + str(int(dose/100)),volume)
	def setDoseAtRelativeVolumes(self,VolumeList,DoseList):
		for volume,dose in zip(VolumeList,DoseList):
			setattr(self,"D" + str(int(volume*100)),dose)
	def setRelativeVolumeAtDoseRateToPrescription(self,prescription,VolumeList,DoseList):
		for volume,dose in zip(VolumeList,DoseList):
			setattr(self,"V" + str(int((dose/prescription)*100)) + '%',dose)

test=ClinicalGoals()
tmpClinicalGoalSetting = test.getClinicalGoalClass('CTV')
tmpClinicalGoalSetting.RoiType='Target'

test.ClinicalGoalList[0].RoiType

tmp=test.getClinicalGoalClass('rectum')
