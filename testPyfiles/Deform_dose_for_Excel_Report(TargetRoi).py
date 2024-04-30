#
# 1) Change CTV name and volume list on Initial parameter.
# 2) Create deform dose.
# 3) Script execute.
#

from connect import *
import clr, time, System
clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Drawing')
clr.AddReference('System.Windows.Forms.DataVisualization')
from System.Windows.Forms import *
from System.Drawing import *
from System.Windows.Forms.DataVisualization.Charting import *

from System.Collections import ArrayList

case = get_current("Case")
beam_set = get_current("BeamSet")
plan = get_current("Plan")
beam_set_name=[]
roi_name = []
for bs in plan.BeamSets:
	beam_set_name.append(bs.DicomPlanLabel)
	if not bs.Prescription.PrimaryDosePrescription.OnStructure.Name in roi_name:
		roi_name.append(bs.Prescription.PrimaryDosePrescription.OnStructure.Name)

# Initial parameter

volume_list = [0.99, 0.98, 0.95, 0.5, 0.02, 0.01] # D99, D98, D95, D50, D2, D1

deform_info_list = []
deform_info_key = []
for eval_dose in case.TreatmentDelivery.FractionEvaluations[0].DoseOnExaminations:
	for doseEval in eval_dose.DoseEvaluations:
		if doseEval.PerturbedDoseProperties == None and doseEval.Name == "" and doseEval.ForBeamSet.DicomPlanLabel in beam_set_name:
			
			deform_cood_info = {}
			original_bst_name = doseEval.ForBeamSet.DicomPlanLabel
			
			deform_cood_info.setdefault("BeamSet",original_bst_name)
			deform_cood_info.setdefault("DeformCTName",doseEval.OnDensity.FromExamination.Name)
			
			if original_bst_name not in deform_info_key:
				deform_info_key.append(original_bst_name)
				deform_info_key.sort()
			
			num_of_fraction = doseEval.ForBeamSet.FractionationPattern.NumberOfFractions
			dose_data_1fx = []
			dose_data_1fx = doseEval.GetDoseAtRelativeVolumes(RoiName=doseEval.ForBeamSet.Prescription.PrimaryDosePrescription.OnStructure.Name, RelativeVolumes=volume_list)
			dose_data_total = [dose * num_of_fraction for dose in dose_data_1fx]
			dose_data_total_dict = {}
			dose_data_total_dict.setdefault("deform_Info",deform_cood_info)
			for volume , dose in zip(volume_list,dose_data_total):
				dose_data_total_dict.setdefault(str(100*volume),dose)
				
			#s_data_total_dict ={}
			#s_data_total_list = sorted(dose_data_total_dict.items(), key = lambda x:x[0],reverse = True)
			#s_data_total_dict = dict(sorted(dose_data_total_dict.items(), key = lambda x:x[0],reverse = True))
			deform_info_list.append(dose_data_total_dict)
				

#create file & folder
patient = get_current("Patient")
ID = patient.PatientID
Pt_name = patient.PatientName
beamset_name = beam_set.DicomPlanLabel

direction_list = ['Sup','Inf','Ant','Pos']
import os
os.chdir("M:\\")
if not os.path.isdir(os.getcwd()  + "Patient_Data_Folder"):
	os.mkdir(os.getcwd()  + "Patient_Data_Folder")

file_path = "Patient_Data_Folder\\" + str(ID) + "_" + Pt_name

if not os.path.isdir(os.getcwd()  + file_path):
	os.mkdir(os.getcwd()  + file_path)

os.chdir(os.getcwd()  + file_path)

file_name = "deform_Dose_for_Excel_Report_{0}.csv".format(get_current("Patient").PatientName)

with open(file_name, "w") as file:
	file.write("Deform CT Dose Report")
	file.write("Relative Volume : cGy\n")
	for BeamSetName in deform_info_key:
		file.write(BeamSetName + "\n")
		file.write("Target ROI,{}".format(plan.BeamSets[BeamSetName].Prescription.PrimaryDosePrescription.OnStructure.Name) + "\n")
		file.write(",")
		for volume in volume_list:
					file.write(str(volume*100)+ ",")
		file.write("\n")
		
		for direction in direction_list:
			for DDT_dict in deform_info_list:
				if DDT_dict["deform_Info"]["BeamSet"] == BeamSetName:
					if direction in DDT_dict["deform_Info"]["DeformCTName"]:
						file.write(DDT_dict["deform_Info"]["DeformCTName"] + ",")
						for volume in volume_list:
							file.write(str(DDT_dict[str(100*volume)]) + ",")
						file.write("\n")
				else:
					continue
		
				
		file.write("\n")
	

### End ###

