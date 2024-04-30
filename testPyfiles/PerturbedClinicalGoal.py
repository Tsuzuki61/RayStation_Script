from connect import *
from collections import OrderedDict
import re
import sys
sys.path.append(r"F:\Proton\RayStation\Script\create file")
import wpf
from System.Windows import *
from System.Windows.Controls import *
from ctypes import *
from decimal import *
import datetime as dt
import json

case = get_current("Case")
beam_set = get_current("BeamSet")
plan = get_current("Plan")

with open("F:\Proton\RayStation\Script\create file\Data\ClinicalGoalSetting.json") as f:
	CGSettings = json.load(f,object_pairs_hook=OrderedDict)

class ComboBoxForm(Window):
	def __init__(self):
		wpf.LoadComponent(self, r'F:\Proton\RayStation\Script\create file\ClinicalGoalSelectCombo.xaml')
		#self.Topmost = True
		# Start up window at the center of the screen.
		self.WindowStartupLocation = WindowStartupLocation.CenterScreen
		self.PlanPart=''
		for PP in CGSettings.keys():
			self.TPartCombo.Items.Add(PP)
	def OKClicked(self,sender,event):
		self.PlanPart=self.TPartCombo.SelectedItem
		self.DialogResult=True
	def CancelClicked(self,sender,event):
		self.DialogResult=False

ComboForm = ComboBoxForm()
ComboForm.ShowDialog()

if ComboForm.DialogResult == False:
	sys.exit()

CGSetting = CGSettings[ComboForm.PlanPart]

PlanFractions=0
for BeamSet in plan.BeamSets:
	PlanFractions += BeamSet.FractionationPattern.NumberOfFractions

roi_name_list = [roi.Name for roi in case.PatientModel.RegionsOfInterest]
PrescriptionDose = 0
for BeamSet in plan.BeamSets:
	PrescriptionDose += BeamSet.Prescription.PrimaryDosePrescription.DoseValue

perturbed_info_list = []
perturbed_info_key = []
bst_name_list = [bst.DicomPlanLabel for bst in plan.BeamSets]
for DoseOnE in case.TreatmentDelivery.FractionEvaluations[0].DoseOnExaminations:
	for eval_dose in DoseOnE.DoseEvaluations:
		if eval_dose.PerturbedDoseProperties != None and eval_dose.ForBeamSet.DicomPlanLabel in bst_name_list:
			#purturbedSetting
			perturbed_cood_info = {}
			original_bst_name = eval_dose.ForBeamSet.DicomPlanLabel
			perturbed_info = "x:{0},y:{1},z:{2},density:{3}".format(str(eval_dose.PerturbedDoseProperties.IsoCenterShift.x), str(eval_dose.PerturbedDoseProperties.IsoCenterShift.y), str(eval_dose.PerturbedDoseProperties.IsoCenterShift.z), str(eval_dose.PerturbedDoseProperties.RelativeDensityShift))
			
			perturbed_cood_info.setdefault("BeamSet",original_bst_name)
			perturbed_cood_info.setdefault("X",str(eval_dose.PerturbedDoseProperties.IsoCenterShift.x))
			perturbed_cood_info.setdefault("Y",str(eval_dose.PerturbedDoseProperties.IsoCenterShift.z))
			perturbed_cood_info.setdefault("Z",str(eval_dose.PerturbedDoseProperties.IsoCenterShift.y * -1))
			perturbed_cood_info.setdefault("density",str(eval_dose.PerturbedDoseProperties.RelativeDensityShift))
			#File Writing Key
			if original_bst_name not in perturbed_info_key:
				perturbed_info_key.append(original_bst_name)
				perturbed_info_key.sort()
			
			#Dose Data collection
			dose_data_total_dict = {}
			dose_data_total_dict.setdefault("Perturbed_Info",perturbed_cood_info)
			Dose_Statistics = {}
			ClinicalGoal={}
			for roi in CGSetting.keys():
				num_of_fraction = eval_dose.ForBeamSet.FractionationPattern.NumberOfFractions
				dose_data_1fx = []
				DaVParameterValue=[]
                VaDParameterValue=[]
                MaxParameterValue=[]
				if CGSetting[roi]['RoiType'] == 'Target':
					current_roi = eval_dose.ForBeamSet.Prescription.PrimaryDosePrescription.OnStructure.Name
				else:
                    current_roi = roi
                for constraint in CGSetting[roi]['Constraint']:
                    if constraint['Type'] == 'DoseAtVolume':
                        DaVParameterValue.append(constraint['ParameterValue'])
                    elif constraint['Type'] == 'VolumeAtDose':
                        VaDParameterValue.append(constraint['ParameterValue'])
                    elif constraint['Type'] == 'MaxDose':
                        MaxParameterValue.append(constraint['ParameterValue'])
				dose_data_total_dict={}
                if len(DaVParameterValue) != 0:
                    #DoseAtRelativeVolumes
					dose_data_1fx_dose=[]
                    dose_data_1fx_dose = eval_dose.GetDoseAtRelativeVolumes(RoiName=current_roi, RelativeVolumes=DaVParameterValue)
					for volume,dose in zip(DaVParameterValue,dose_data_1fx_dose):
						dose_data_total_dict.setdefault(volume,dose * num_of_fraction)
                if len(VaDParameterValue) != 0:
                    #RelativeVolumesAtDoseValues
					dose_data_1fx_volume=[]
                    dose_data_1fx_volume = eval_dose.GetRelativeVolumeAtDoseValues(RoiName=current_roi, RelativeVolumes=VaDParameterValue)
					for volume,dose in zip(VaDParameterValue,dose_data_1fx_volume):
						dose_data_total_dict.setdefault(volume,dose * num_of_fraction)
                if len(MaxParameterValue) != 0:
                    #MaxDose
					dose_data_1fx_max=[]
                    for maxPara in MaxParameterValue:
                        dose_data_1fx_max.append(eval_dose.GetDoseStatistic(RoiName=current_roi, DoseType=MaxPara))
						for volume,dose in zip(MaxPara,dose_data_1fx_max):
							dose_data_total_dict.setdefault(volume,dose * num_of_fraction)
				roi_dose_dict = {}
				ClinicalJudge={}
				for volume , dose in zip(ParameterValue,dose_data_total):
					roi_dose_dict.setdefault(str(100*volume),dose)
					for constraint in CGSetting[roi]['Constraint']:
						if float(constraint['ParameterValue']) == volume:
							if constraint['GoalCriteria'] == "AtMost":
								ClinicalJudge.setdefault(str(100*volume),dose < int(constraint["AcceptanceLevel"])*(eval_dose.ForBeamSet.Prescription.PrimaryDosePrescription.DoseValue / PrescriptionDose))
							elif constraint['GoalCriteria'] == "AtLeast":
								ClinicalJudge.setdefault(str(100*volume),dose > int(constraint["AcceptanceLevel"])*(eval_dose.ForBeamSet.Prescription.PrimaryDosePrescription.DoseValue / PrescriptionDose))
				roi_dose_dict.setdefault('ClinicalJudge',ClinicalJudge)
				Dose_Statistics.setdefault(roi,roi_dose_dict)
			dose_data_total_dict.setdefault('DoseStatistics',Dose_Statistics)
			perturbed_info_list.append(dose_data_total_dict)
#ComboBoxForm.PlanPart
