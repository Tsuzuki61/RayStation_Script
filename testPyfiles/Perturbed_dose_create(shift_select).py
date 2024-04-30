#
# 1) Please select perturbed plan using pull down.
# 2) Script execute.
# Supplement : If you hope beam dose evaluation, please change to ComputeBeamDoses=True from ComputeBeamDoses=False.
#
from connect import *

case = get_current("Case")
plan = get_current('Plan')



import clr, time, System
clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Drawing')
clr.AddReference('System.Windows.Forms.DataVisualization')
from System.Windows.Forms import *
from System.Drawing import *
from System.Windows.Forms.DataVisualization.Charting import *

from System.Collections import ArrayList

exam_name = ""
shift_value = ""
DP_value = ""

#form initialize
form = Form(Text="Perturb setting", Size=Size(330, 340), AutoScroll=True, TopMost=True)
form.StartPosition = FormStartPosition.CenterScreen

#combo box setting
def ComboBoxSelectAction(sender, e):
    global exam_name
    exam_name = combobox.SelectedItem
    
    
    # combobox.Visible = False


combo_list = [examination.Name for examination in case.Examinations]

combobox = ComboBox(Location=Point(40, 50), AutoSize=True, DropDownStyle=ComboBoxStyle.DropDown)
combobox.Items.AddRange(System.Array[System.Object](combo_list))   # List is updated because items was added when it was clicked.
combobox.SelectedIndexChanged += ComboBoxSelectAction

textbox1 = TextBox(Location=Point(40, 120), Width=150)

textbox2 = TextBox(Location=Point(40, 190), Width=150)
exp_label1 = Label(Text="Please select the CT Examination used for calculation.", Location=Point(25, 15), AutoSize=True)

exp_label2 = Label(Text="Please enter shift value.(cm)", Location=Point(25, 90), AutoSize=True)

exp_label3 = Label(Text="Please enter density perturbation.(%)", Location=Point(25, 160), AutoSize=True)

#button setting
ok_btn = Button(Text="OK", Location=Point(210,260),AutoSize=True)

def button_Clicked(sender, event):
	if exam_name == "":
		MessageBox.Show("Examination has not been selected yet")
	
	else:
		global shift_value,DP_value
		shift_value = textbox1.Text
		DP_value = textbox2.Text
		if shift_value == "":
			MessageBox.Show("shift has not been entered yet")
			return
		elif DP_value == "":
			MessageBox.Show("Density perturbation has not been entered yet")
			return
		form.Close()

ok_btn.Click += button_Clicked

control_list = [combobox, exp_label1, exp_label2, exp_label3, textbox1, textbox2, ok_btn]
for control in control_list: form.Controls.Add(control)

Application.Run(form)




'''
# Simple perturbation for understanding. But for statement is better.
x_shift = [0.6, 0.6, 0.6, -0.6, 0.6, -0.6, -0.6, -0.6, 0, 0.6, 0.6, 0.6, -0.6, 0.6, -0.6, -0.6, -0.6, 0, 0.6, 0.6, 0.6, -0.6, 0.6, -0.6, -0.6, -0.6]
y_shift = [0.6, 0.6, -0.6, 0.6, -0.6, -0.6, 0.6, -0.6, 0, 0.6, 0.6, -0.6, 0.6, -0.6, -0.6, 0.6, -0.6, 0, 0.6, 0.6, -0.6, 0.6, -0.6, -0.6, 0.6, -0.6]
z_shift = [0.6, -0.6, 0.6, 0.6, -0.6, 0.6, -0.6, -0.6, 0, 0.6, -0.6, 0.6, 0.6, -0.6, 0.6, -0.6, -0.6, 0, 0.6, -0.6, 0.6, 0.6, -0.6, 0.6, -0.6, -0.6]
d_shift = [0, 0, 0, 0, 0, 0, 0, 0, 0.035, 0.035, 0.035, 0.035, 0.035, 0.035, 0.035, 0.035, 0.035, -0.035, -0.035, -0.035, -0.035, -0.035, -0.035, -0.035, -0.035, -0.035]

for x, y, z, d in zip(x_shift, y_shift, z_shift, d_shift):
    beam_set.ComputePerturbedDose(DensityPerturbation=d, IsocenterShift={ 'x': x, 'y': y, 'z': z }, OnlyOneDosePerImageSet=False, AllowGridExpansion=False, ExaminationNames=[examination.Name], FractionNumbers=[0], ComputeBeamDoses=False)
'''
### End ###

i = float(shift_value)
j = float(DP_value)/100
x_shift = [i, -i]
y_shift = [i, -i]
z_shift = [i, -i]
d_shift = [0, j , -j]
for beamset in plan.BeamSets:
	beamset.ComputePerturbedDose(DensityPerturbation=j, IsocenterShift={ 'x': 0, 'y': 0, 'z': 0 }, OnlyOneDosePerImageSet=False, AllowGridExpansion=False, ExaminationNames=[exam_name], FractionNumbers=[0], ComputeBeamDoses=True)
	beamset.ComputePerturbedDose(DensityPerturbation=-j, IsocenterShift={ 'x': 0, 'y': 0, 'z': 0 }, OnlyOneDosePerImageSet=False, AllowGridExpansion=False, ExaminationNames=[exam_name], FractionNumbers=[0], ComputeBeamDoses=True)

	for d in d_shift:
		for x in x_shift:
			for y in y_shift:
				for z in z_shift:
					beamset.ComputePerturbedDose(DensityPerturbation=d, IsocenterShift={ 'x': x, 'y': y, 'z': z }, OnlyOneDosePerImageSet=False, AllowGridExpansion=False, ExaminationNames=[exam_name], FractionNumbers=[0], ComputeBeamDoses=True)
