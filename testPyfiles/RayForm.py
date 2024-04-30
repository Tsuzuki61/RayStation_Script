from connect import *
import clr

clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")

from System.Windows.Forms import *
from System.Drawing import Point, Size

class DeformForm(Form):
	
	def __init__(self,case):
		#Set the size of the form
		self.Size = Size(260,280)
		#Set title of the form
		self.Text = 'Select Deform Exam'
		self.StartPosition = FormStartPosition.CenterScreen
		#Add Labels
		label1 = Label()
		label1.Text = 'Please select PlanningCT examination'
		label1.Location = Point(15,15)
		label1.AutoSize = True
		self.Controls.Add(label1)
		
		label2 = Label()
		label2.Text = 'Please select DeformCT examination'
		label2.Location = Point(15,75)
		label2.AutoSize = True
		self.Controls.Add(label2)
		
		label3 = Label()
		label3.Text = 'Please enter the shift value(cm)'
		label3.Location = Point(15,135)
		label3.AutoSize = True
		self.Controls.Add(label3)
		
		#Add 2 ComboBoxies
		exam_names1 = [exam.Name for exam in case.Examinations if exam.EquipmentInfo.Modality == 'CT']
		self.combobox1 = ComboBox()
		self.combobox1.DataSource = exam_names1
		self.combobox1.Location = Point(15,45)
		self.combobox1.Width = 150
		self.Controls.Add(self.combobox1)
		
		exam_names2 = [exam.Name for exam in case.Examinations if exam.EquipmentInfo.Modality == 'CT']
		self.combobox2 = ComboBox()
		self.combobox2.DataSource = exam_names2
		self.combobox2.Location = Point(15,105)
		self.combobox2.Width = 150
		self.Controls.Add(self.combobox2)
		
		#Add TextBox
		self.textbox = TextBox()
		self.textbox.Location = Point(15,165)
		self.textbox.Width = 50
		self.Controls.Add(self.textbox)
		
		#Add button to press OK and close the form
		button = Button()
		button.Text = 'OK'
		button.AutoSize = True
		button.Location = Point(160,210)
		button.Click += self.ok_button_clicked
		self.Controls.Add(button)
		
		#form close boolean
		self.close_bool = False
		
	def ok_button_clicked(self, sender, event):
		#Method invoked when the button is clicked
		#Save the selected Exam name
		self.planning_exam_name = self.combobox1.SelectedValue
		self.deform_exam_name = self.combobox2.SelectedValue
		self.shift_value = self.textbox.Text
		self.close_bool = True
		#Close the form
		self.Close()

class DeformRegistrationCreateForm(Form):
	
	def __init__(self,case):
		#Set the size of the form
		self.Size = Size(330,210)
		#Set title of the form
		self.Text = 'Select Deform Exam'
		self.StartPosition = FormStartPosition.CenterScreen
		#Add Labels
		label1 = Label()
		label1.Text = 'Please select Reference image set (ex.DeformCT)'
		label1.Location = Point(15,15)
		label1.AutoSize = True
		self.Controls.Add(label1)
		
		label2 = Label()
		label2.Text = 'Please select Target image set (ex.PlanningCT_20180901)'
		label2.Location = Point(15,75)
		label2.AutoSize = True
		self.Controls.Add(label2)

		
		#Add 2 ComboBoxies
		exam_names1 = [exam.Name for exam in case.Examinations if exam.EquipmentInfo.Modality == 'CT']
		self.combobox1 = ComboBox()
		self.combobox1.DataSource = exam_names1
		self.combobox1.Location = Point(15,45)
		self.combobox1.Width = 150
		self.Controls.Add(self.combobox1)
		
		exam_names2 = [exam.Name for exam in case.Examinations if exam.EquipmentInfo.Modality == 'CT']
		self.combobox2 = ComboBox()
		self.combobox2.DataSource = exam_names2
		self.combobox2.Location = Point(15,105)
		self.combobox2.Width = 150
		self.Controls.Add(self.combobox2)
		

		#Add button to press OK and close the form
		button = Button()
		button.Text = 'OK'
		button.AutoSize = True
		button.Location = Point(230,140)
		button.Click += self.ok_button_clicked
		self.Controls.Add(button)
		
		#form close boolean
		self.close_bool = False
		
	def ok_button_clicked(self, sender, event):
		#Method invoked when the button is clicked
		#Save the selected Exam name
		self.reference_name = self.combobox1.SelectedValue
		self.target_name = self.combobox2.SelectedValue
		self.close_bool = True
		#Close the form
		self.Close()

class ClinicalGoalSelectForm(Form):
	
	def __init__(self,plan):
		BeamSet = get_current('BeamSet')
		#Set the size of the form
		self.Size = Size(220,160)
		#Set title of the form
		self.Text = 'Select for viewing Clinical Goal'
		self.StartPosition = FormStartPosition.CenterScreen
		#Add Label
		label1 = Label()
		label1.Text = 'Please select plan or BeamSet'
		label1.Location = Point(15,15)
		label1.AutoSize = True
		self.Controls.Add(label1)
		

		
		#Add  ComboBox
		forClinicalGoal_list = [beamset.DicomPlanLabel for beamset in plan.BeamSets]
		forClinicalGoal_list.append(plan.Name)
		
		self.combobox1 = ComboBox()
		self.combobox1.DataSource = forClinicalGoal_list
		self.combobox1.Location = Point(15,45)
		self.combobox1.Width = 150
		self.Controls.Add(self.combobox1)
		

		#Add button to press OK and close the form
		button = Button()
		button.Text = 'OK'
		button.AutoSize = True
		button.Location = Point(110,80)
		button.Click += self.ok_button_clicked
		self.Controls.Add(button)
		
		#form close boolean
		self.close_bool = False
		
	def ok_button_clicked(self, sender, event):
		#Method invoked when the button is clicked
		#Save the selected Exam name
		self.forClinicalGoal = self.combobox1.SelectedValue
		self.close_bool = True
		#Close the form
		self.Close()

class isMarkerForm(Form):
	
	def __init__(self):
		#Set the size of the form
		self.Size = Size(300,160)
		#Set title of the form
		self.Text = 'With marker or not'
		self.StartPosition = FormStartPosition.CenterScreen
		#Add Label
		label1 = Label()
		label1.Text = 'Please select the presence or absence of marker'
		label1.Location = Point(15,15)
		label1.AutoSize = True
		self.Controls.Add(label1)
		

		
		#Add  ComboBox
		select_list = ['With Marker','Without Marker']
		
		self.combobox1 = ComboBox()
		self.combobox1.DataSource = select_list
		self.combobox1.Location = Point(50,45)
		self.combobox1.Width = 150
		self.Controls.Add(self.combobox1)
		

		#Add button to press OK and close the form
		button = Button()
		button.Text = 'OK'
		button.AutoSize = True
		button.Location = Point(200,80)
		button.Click += self.ok_button_clicked
		self.Controls.Add(button)
		
		#form close boolean
		self.close_bool = False
		self.isMarker = True
	def ok_button_clicked(self, sender, event):
		#Method invoked when the button is clicked
		#Save the selected 
		if self.combobox1.SelectedValue == 'With Marker':
			self.isMarker = True
		else:
			self.isMarker = False
		
		self.close_bool = True
		#Close the form
		self.Close()
