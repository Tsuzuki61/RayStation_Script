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

deform_info_list = []
deform_info_key = []
for eval_dose in case.TreatmentDelivery.FractionEvaluations[0].DoseOnExaminations:
	for doseEval in eval_dose.DoseEvaluations:
		if doseEval.PerturbedDoseProperties == None and doseEval.Name == "":
			
			deform_cood_info = {}
			original_bst_name = doseEval.ForBeamSet.DicomPlanLabel
			
			deform_cood_info.setdefault("BeamSet",original_bst_name)
			deform_cood_info.setdefault("DeformCTName",doseEval.OnDensity.FromExamination.Name)
			
			if original_bst_name not in deform_info_key:
				deform_info_key.append(original_bst_name)
				deform_info_key.sort()
			
			num_of_fraction = doseEval.ForBeamSet.FractionationPattern.NumberOfFractions
			dose_data_1fx = []
			dose_data_1fx = doseEval.GetDoseAtRelativeVolumes(RoiName=roi_name, RelativeVolumes=volume_list)
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

file_name = "deform_Dose_for_Excel_Report_{0}({1}).csv".format(get_current("Patient").PatientName,roi_name)

with open(file_name, "w") as file:
	file.write("ROI Name : {0}\n".format(roi_name))
	file.write("Deform CT Dose Report")
	file.write("Relative Volume : cGy\n")
	for BeamSetName in deform_info_key:
		file.write(BeamSetName + "\n")
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

