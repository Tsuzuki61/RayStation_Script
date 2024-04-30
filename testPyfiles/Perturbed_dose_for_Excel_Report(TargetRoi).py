#
# 1) Change CTV name and volume list on Initial parameter.
# 2) Create perturbed dose.
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
roi_name = []
for bs in plan.BeamSets:
	if not bs.Prescription.PrimaryDosePrescription.OnStructure.Name in roi_name:
		roi_name.append(bs.Prescription.PrimaryDosePrescription.OnStructure.Name)

# Initial parameter

volume_list = [0.99, 0.98, 0.95, 0.5, 0.02, 0.01] # D99, D98, D95, D50, D2, D1

perturbed_info_list = []
perturbed_info_key = []
bst_name_list = [bst.DicomPlanLabel for bst in plan.BeamSets]
for DoseOnE in case.TreatmentDelivery.FractionEvaluations[0].DoseOnExaminations:
	for eval_dose in DoseOnE.DoseEvaluations:
		if eval_dose.PerturbedDoseProperties != None and eval_dose.ForBeamSet.DicomPlanLabel in bst_name_list:
			
			perturbed_cood_info = {}
			original_bst_name = eval_dose.ForBeamSet.DicomPlanLabel
			perturbed_info = "x:{0},y:{1},z:{2},density:{3}".format(str(eval_dose.PerturbedDoseProperties.IsoCenterShift.x), str(eval_dose.PerturbedDoseProperties.IsoCenterShift.y), str(eval_dose.PerturbedDoseProperties.IsoCenterShift.z), str(eval_dose.PerturbedDoseProperties.RelativeDensityShift))
			
			perturbed_cood_info.setdefault("BeamSet",original_bst_name)
			perturbed_cood_info.setdefault("X",str(eval_dose.PerturbedDoseProperties.IsoCenterShift.x))
			perturbed_cood_info.setdefault("Y",str(eval_dose.PerturbedDoseProperties.IsoCenterShift.z))
			perturbed_cood_info.setdefault("Z",str(eval_dose.PerturbedDoseProperties.IsoCenterShift.y * -1))
			perturbed_cood_info.setdefault("density",str(eval_dose.PerturbedDoseProperties.RelativeDensityShift))
			if original_bst_name not in perturbed_info_key:
				perturbed_info_key.append(original_bst_name)
				perturbed_info_key.sort()
			
			num_of_fraction = eval_dose.ForBeamSet.FractionationPattern.NumberOfFractions
			dose_data_1fx = []
			dose_data_1fx = eval_dose.GetDoseAtRelativeVolumes(RoiName=eval_dose.ForBeamSet.Prescription.PrimaryDosePrescription.OnStructure.Name, RelativeVolumes=volume_list)
			dose_data_total = [dose * num_of_fraction for dose in dose_data_1fx]
			dose_data_total_dict = {}
			dose_data_total_dict.setdefault("Perturbed_Info",perturbed_cood_info)
			for volume , dose in zip(volume_list,dose_data_total):
				dose_data_total_dict.setdefault(str(100*volume),dose)
				
			#s_data_total_dict ={}
			#s_data_total_list = sorted(dose_data_total_dict.items(), key = lambda x:x[0],reverse = True)
			#s_data_total_dict = dict(sorted(dose_data_total_dict.items(), key = lambda x:x[0],reverse = True))
			perturbed_info_list.append(dose_data_total_dict)
					

#create file & folder
patient = get_current("Patient")
ID = patient.PatientID
Pt_name = patient.PatientName
beamset_name = beam_set.DicomPlanLabel


import os
os.chdir("M:\\")
if not os.path.isdir(os.getcwd()  + "Patient_Data_Folder"):
	os.mkdir(os.getcwd()  + "Patient_Data_Folder")

file_path = "Patient_Data_Folder\\" + str(ID) + "_" + Pt_name

if not os.path.isdir(os.getcwd()  + file_path):
	os.mkdir(os.getcwd()  + file_path)

os.chdir(os.getcwd()  + file_path)

file_name = "Perturbed_Dose_for_Excel_Report_{0}_{1}.csv".format(get_current("Patient").PatientName,plan.Name)

with open(file_name, "w") as file:
	file.write('PatientID,{}\n'.format(ID))
	file.write('PatientName,{}\n'.format(Pt_name))
	file.write("x(cm) : y(cm) : z(cm) : (Multiplied 100 is %)\n")
	file.write("Relative Volume : cGy\n")
	for BeamSetName in perturbed_info_key:
		file.write(BeamSetName + "\n")
		file.write("Target ROI,{}".format(plan.BeamSets[BeamSetName].Prescription.PrimaryDosePrescription.OnStructure.Name) + "\n")
		file.write("Density(%),X(cm),Y(cm),Z(cm),")
		for volume in volume_list:
			file.write(str(volume*100)+ ",")
		file.write("\n")
		
		for DDT_dict in perturbed_info_list:
			if DDT_dict["Perturbed_Info"]["BeamSet"] == BeamSetName:
				file.write("{3},{0},{1},{2},".format(DDT_dict["Perturbed_Info"]["X"],DDT_dict["Perturbed_Info"]["Y"],DDT_dict["Perturbed_Info"]["Z"],str(float(DDT_dict["Perturbed_Info"]["density"])*100)))
				
				for volume in volume_list:
					file.write(str(DDT_dict[str(100*volume)]) + ",")
			else:
				continue
    
			file.write("\n")
	

### End ###


