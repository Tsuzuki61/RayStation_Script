from connect import *
import collections
import re
import sys
sys.path.append(r"F:\Proton\RayStation\Script\create file")
import wpf
from System.Windows import *
from System.Windows.Controls import *
from System.Windows.Data import *
from ctypes import *
from decimal import *
import json

case = get_current("Case")
beam_set = get_current("BeamSet")
plan = get_current("Plan")

Total_Prescription_Dose = 0
for beamset in plan.BeamSets:
	Total_Prescription_Dose += beamset.Prescription.PrimaryDosePrescription.DoseValue

class CGForm(Window):
	def __init__(self,ClinicaGoalJson):
		wpf.LoadComponent(self, r'F:\Proton\RayStation\Script\create file\xaml\ClinicalGoal.xaml')
		self.Topmost = True
		# Start up window at the center of the screen.
		self.WindowStartupLocation = WindowStartupLocation.CenterScreen
		self.DataContext = ClinicaGoalJson
	def ClearClinicalGoals(self):
		for EF in plan.TreatmentCourse.EvaluationSetup.EvaluationFunctions:
			plan.TreatmentCourse.EvaluationSetup.DeleteClinicalGoal(FunctionToRemove = EF)
	def CancelClicked(self,sender,event):
		self.DialogResult=False
	def PartCombo_Changed(self,sender,event):
		tmpBinding = Binding()
		tmpBinding.Source = self.DataContext
		tmpBinding.Path =PropertyPath('[{}]'.format(self.PartCombo.SelectedItem))
		self.ProtocolCombo.SetBinding(ComboBox.ItemsSourceProperty,tmpBinding)
	def PlanClicked(self,sender,event):
		self.ClearClinicalGoals()
		Protocol = self.DataContext[self.PartCombo.SelectedItem][self.ProtocolCombo.SelectedItem]
		roi_names = [beamset.Prescription.PrimaryDosePrescription.OnStructure.Name for beamset in plan.BeamSets]
		for roi in Protocol.keys():
			if Protocol[roi]["RoiType"] == "Target":
				for roiname in roi_names:
					for Constraint in Protocol[roi]["Constraint"]:
						try:
							plan.TreatmentCourse.EvaluationSetup.AddClinicalGoal(RoiName=roiname, GoalCriteria=Constraint["GoalCriteria"], GoalType=Constraint["GoalType"], AcceptanceLevel= float(Decimal(Total_Prescription_Dose) * Decimal(Constraint["AcceptanceLevel"])), ParameterValue=float(Decimal(Constraint["ParameterValue"])), IsComparativeGoal=False, Priority=2147483647)
						except:
							break
			else:
				for Constraint in Protocol[roi]["Constraint"]:
					plan.TreatmentCourse.EvaluationSetup.AddClinicalGoal(RoiName=roi, GoalCriteria=Constraint["GoalCriteria"], GoalType=Constraint["GoalType"], AcceptanceLevel= float(Constraint["AcceptanceLevel"]), ParameterValue=float(Constraint["ParameterValue"]), IsComparativeGoal=False, Priority=2147483647)
		self.DialogResult = True
	def BeamSetClicked(self,sender,event):
		self.ClearClinicalGoals()
		Protocol = self.DataContext[self.PartCombo.SelectedItem][self.ProtocolCombo.SelectedItem]
		roiname = beam_set.Prescription.PrimaryDosePrescription.OnStructure.Name
		BeamSetPrescriptionDose = beam_set.Prescription.PrimaryDosePrescription.DoseValue
		ReCompileVolume = re.compile('.*(Volume)$')
		ReCompileDose = re.compile('.*(Dose)$')
		for roi in Protocol.keys():
			#Target AcceptanceLevel is rate to prescription dose
			if Protocol[roi]["RoiType"] == "Target":
				for Constraint in Protocol[roi]["Constraint"]:
					try:
						plan.TreatmentCourse.EvaluationSetup.AddClinicalGoal(RoiName=roiname, GoalCriteria=Constraint["GoalCriteria"], GoalType=Constraint["GoalType"], AcceptanceLevel= float(BeamSetPrescriptionDose * float(Constraint["AcceptanceLevel"])), ParameterValue=float(Constraint["ParameterValue"]), IsComparativeGoal=False, Priority=2147483647)
					except:
						break
			else:
				for Constraint in Protocol[roi]["Constraint"]:
					if ReCompileVolume.match(Constraint["GoalType"]): 
						plan.TreatmentCourse.EvaluationSetup.AddClinicalGoal(RoiName=roi, GoalCriteria=Constraint["GoalCriteria"], GoalType=Constraint["GoalType"], AcceptanceLevel= float((BeamSetPrescriptionDose / Total_Prescription_Dose) * float(Constraint["AcceptanceLevel"])), ParameterValue=float(Constraint["ParameterValue"]), IsComparativeGoal=False, Priority=2147483647)
					elif ReCompileDose.match(Constraint["GoalType"]):
						plan.TreatmentCourse.EvaluationSetup.AddClinicalGoal(RoiName=roi, GoalCriteria=Constraint["GoalCriteria"], GoalType=Constraint["GoalType"], AcceptanceLevel= float(Constraint["AcceptanceLevel"]), ParameterValue=int((BeamSetPrescriptionDose / Total_Prescription_Dose) * float(Constraint["ParameterValue"])), IsComparativeGoal=False, Priority=2147483647)
		self.DialogResult = True


with open(r"F:\Proton\RayStation\Script\create file\Data\ClinicalGoalSetting.json") as f:
	ClinicaGoalJson = json.load(f,object_pairs_hook = collections.OrderedDict)

form = CGForm(ClinicaGoalJson)
form.ShowDialog()

if form.DialogResult == False:
	sys.exit()