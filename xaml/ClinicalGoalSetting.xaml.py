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

class msgBox(Window):
	def __init__(self):
		wpf.LoadComponent(self, r'F:\Proton\RayStation\Script\create file\messagebox.xaml')
		self.Topmost = True
		# Start up window at the center of the screen.
		self.WindowStartupLocation = WindowStartupLocation.CenterScreen
		self.Caption.Title="Confirmation"
		textblock1 = TextBlock()
		textblock1.Text = "There are changes in the data"
		textblock1.Margin = Thickness(5)
		textblock2 = TextBlock()
		textblock2.Text = "OverWrite it?"
		textblock2.Margin = Thickness(5)
		self.SPanel.Children.Add(textblock1)
		self.SPanel.Children.Add(textblock2)
		OKbutton = Button()
		OKbutton.Name = "OK_btn"
		OKbutton.Content = "OK"
		OKbutton.Width = 50
		OKbutton.Margin = Thickness(10)
		OKbutton.Click += self.OK_Clicked
		self.ButtomSPanel.Children.Add(OKbutton)
		CanButton = Button()
		CanButton.Name = "Cancel_btn"
		CanButton.Content = "Cancel"
		CanButton.Width = 50
		CanButton.Margin = Thickness(10)
		CanButton.Click += self.Cancel_Clicked
		self.ButtomSPanel.Children.Add(CanButton)
	def OK_Clicked(self,sender,event):
		self.DialogResult = True
	def Cancel_Clicked(self,sender,event):
		self.DialogResult = False

class CGForm(Window):
	def __init__(self,ClinicalGoalJson):
		wpf.LoadComponent(self, r'F:\Proton\RayStation\Script\create file\xaml\ClinicalGoalSetting.xaml')
		self.Topmost = True
		# Start up window at the center of the screen.
		self.WindowStartupLocation = WindowStartupLocation.CenterScreen
		self.DataContext = ClinicalGoalJson
		roitype_list=['Target','OrganAtRisk']
		self.ROITypeCombo.ItemsSource = roitype_list
	def PartCombo_Changed(self,sender,event):
		tmpBinding = Binding()
		tmpBinding.Source = self.DataContext
		tmpBinding.Path =PropertyPath('[{}]'.format(self.PartCombo.SelectedItem))
		self.ProtocolCombo.SetBinding(ComboBox.ItemsSourceProperty,tmpBinding)
	def SaveClicked(self,sender,event):
		global CurrentClinicalGoal
		if CurrentClinicalGoal != self.DataContext:
			msg = msgBox()
			msg.ShowDialog()
			if msg.DialogResult == False:
				return
		self.DialogResult=True
	def CancelClicked(self,sender,event):
		self.DialogResult=False
	def AddNewPartClicked(self,sender,event):
		print(sender)
	def ProtocolCombo_Changed(self,sender,event):
		self.RoiStack.DataContext=self.DataContext[self.PartCombo.SelectedItem][self.ProtocolCombo.SelectedItem]
		tmpBinding = Binding()
		tmpBinding.Source = self.RoiStack.DataContext
		tmpBinding.Path =PropertyPath('')
		self.ROICombo.SetBinding(ComboBox.ItemsSourceProperty,tmpBinding)
	def ROICombo_Changed(self,sender,event):
		self.ROITypeCombo.SelectedItem = self.RoiStack.DataContext[self.ROICombo.SelectedItem]['RoiType']
		self.ConstraintDataGrid.ItemsSource = self.RoiStack.DataContext[self.ROICombo.SelectedItem]['Constraint']

with open(r"F:\Proton\RayStation\Script\create file\Data\ClinicalGoalSetting.json") as f:
	ClinicalGoalJson = json.load(f,object_pairs_hook = collections.OrderedDict)

with open(r"F:\Proton\RayStation\Script\create file\Data\ClinicalGoalSetting.json") as f:
	CurrentClinicalGoal = json.load(f,object_pairs_hook = collections.OrderedDict)

form = CGForm(ClinicalGoalJson)
form.ShowDialog()

if form.DialogResult == True:
	with open(r"F:\Proton\RayStation\Script\create file\Data\ClinicalGoalSetting.json",'w') as f:
		json.dump(ClinicalGoalJson,f,indent=2)

