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
plan = get_current("Plan")
beam_set = get_current("BeamSet")
roi_name = ""

#form initialize
form = Form(Text="Select ROI", Size=Size(275, 160), AutoScroll=True, TopMost=True)
form.StartPosition = FormStartPosition.CenterScreen

#combo box setting
def ComboBoxSelectAction(sender, e):
    global roi_name
    roi_name = combobox.SelectedItem
    print(roi_name)
    
    # combobox.Visible = False


combo_list = [roi.Name for roi in case.PatientModel.RegionsOfInterest]

combobox = ComboBox(Location=Point(40, 40), AutoSize=True, DropDownStyle=ComboBoxStyle.DropDown)
combobox.Items.AddRange(System.Array[System.Object](combo_list))   # List is updated because items was added when it was clicked.
combobox.SelectedIndexChanged += ComboBoxSelectAction

exp_label = Label(Text="Please select the ROI used for calculation.", Location=Point(25, 5), AutoSize=True)

#button setting
ok_btn = Button(Text="OK", Location=Point(160,80),AutoSize=True)
def button_Clicked(sender, event):
    if roi_name =="":
        MessageBox.Show("ROI has not been selected yet")
    else:
        form.Close()

ok_btn.Click += button_Clicked

control_list = [combobox, exp_label, ok_btn]
for control in control_list: form.Controls.Add(control)

Application.Run(form)


# Initial parameter

volume_list = [0.99, 0.98, 0.95, 0.5, 0.02, 0.01] # D99, D98, D95, D50, D2, D1

original_bst_name_list = []
perturbed_info_list = []
original_dose_data_total_list = []
dose_data_total_list = []
target_bst_name = [ori_beam.DicomPlanLabel for ori_beam in plan.BeamSets]

for DoseOnE in case.TreatmentDelivery.FractionEvaluations[0].DoseOnExaminations:
	for eval_dose in DoseOnE.DoseEvaluations:
		if eval_dose.PerturbedDoseProperties != None and eval_dose.ForBeamSet.DicomPlanLabel in target_bst_name:
			
			original_bst_name_list.append(eval_dose.ForBeamSet.DicomPlanLabel)
			#Y-->Z,Z-->-Y
			perturbed_info_list.append("x:{0}, y:{1}, z:{2}, density:{3}".format(str(eval_dose.PerturbedDoseProperties.IsoCenterShift.x), str(eval_dose.PerturbedDoseProperties.IsoCenterShift.z), str(eval_dose.PerturbedDoseProperties.IsoCenterShift.y * -1), str(eval_dose.PerturbedDoseProperties.RelativeDensityShift)))
			# perturbed_info_list.append([eval_dose.PerturbedDoseProperties.IsoCenterShift.x, eval_dose.PerturbedDoseProperties.IsoCenterShift.y, eval_dose.PerturbedDoseProperties.IsoCenterShift.z, eval_dose.PerturbedDoseProperties.RelativeDensityShift])
			
			num_of_fraction = eval_dose.ForBeamSet.FractionationPattern.NumberOfFractions
			original_dose_data_1fx = eval_dose.ForBeamSet.FractionDose.GetDoseAtRelativeVolumes(RoiName=roi_name, RelativeVolumes=volume_list)
			original_dose_data_total = [dose * num_of_fraction for dose in original_dose_data_1fx]
			original_dose_data_total_list.append(original_dose_data_total)
			
			dose_data_1fx = eval_dose.GetDoseAtRelativeVolumes(RoiName=roi_name, RelativeVolumes=volume_list)
			dose_data_total = [dose * num_of_fraction for dose in dose_data_1fx]
			dose_data_total_list.append(dose_data_total)

ratio_data_list = [[(dose[index] - original_dose[index])*100/original_dose[index] for index in range(len(volume_list))] for dose, original_dose in zip(dose_data_total_list, original_dose_data_total_list)]
cross_ratio_data_list = [[data[index] for data in ratio_data_list] for index in range(len(ratio_data_list[0]))]
avg_list = [sum(data_set)/len(data_set) for data_set in cross_ratio_data_list]
std_list = [(sum([(data - avg)**2 for data in data_set])/len(data_set))**(1/2.0) for data_set, avg in zip(cross_ratio_data_list, avg_list)]
std_rel_list = [std/avg for std, avg in zip(std_list, avg_list)]

max_first_index = [[abs(data) for data in data_set].index(max([abs(data) for data in data_set])) for data_set in cross_ratio_data_list]
max_second_index = [[abs(cross_ratio_data_list[j][i]) for i in range(len(cross_ratio_data_list[j])) if i != max_first_index[j]].index(max([abs(cross_ratio_data_list[j][i]) for i in range(len(cross_ratio_data_list[j])) if i != max_first_index[j]])) for j in range(len(cross_ratio_data_list))]

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

file_name = "Perturbed_Dose_{0}({1}).csv".format(patient.PatientName,roi_name)

with open(file_name, "w") as file:
	file.write("ROI Name : {0}\n".format(roi_name))
	file.write("Plan : {}\n".format(plan.Name))
	file.write("x(cm) : y(cm) : z(cm) : (Multiplied 100 is %)\n")
	file.write("Relative Volume : cGy\n")
	
	file.write("\n")
	file.write("### Summary Start ###\n")
	file.write("Average\n")
	for voluem, avg in zip(volume_list, avg_list):
		file.write("D{0} : {1}\n".format(str(100*voluem), str(avg)))

	file.write("Standard Deviation\n")
	for voluem, std in zip(volume_list, std_list):
		file.write("D{0} : {1}\n".format(str(100*voluem), str(std)))

	file.write("Relative Standard Deviation\n")
	for voluem, std_rel in zip(volume_list, std_rel_list):
		file.write("D{0} : {1}\n".format(str(100*voluem), str(std_rel)))

	file.write("Max difference perturbed_info\n")
	for voluem, max_first in zip(volume_list, max_first_index):
		file.write("D{0} : {1} : {2}\n".format(str(100*voluem), perturbed_info_list[max_first], original_bst_name_list[max_first]))

	file.write("Second difference perturbed_info\n")
	for voluem, max_second in zip(volume_list, max_second_index):
		file.write("D{0} : {1} : {2}\n".format(str(100*voluem), perturbed_info_list[max_second], original_bst_name_list[max_second]))

	file.write("### Summary End ###\n")
	file.write("\n")

	for bst_name, perturbed_info, dose_data, original_dose_data in zip(original_bst_name_list, perturbed_info_list, dose_data_total_list, original_dose_data_total_list):
		file.write("BeamSet Name : {0}\n".format(bst_name))
		file.write(perturbed_info + "\n")
		for voluem, dose, original_dose in zip(volume_list, dose_data, original_dose_data):
			file.write("Perturbed D{0},{1}, Original D{0},{2}\n".format(str(100*voluem), str(dose), str(original_dose)))
		
		file.write("\n")

### End ###

