from connect import *
import collections
import re
import sys
sys.path.append(r"F:\Proton\RayStation\Script\create file")
from GUI import MessageBox
import wpf
from System.Windows import *
from System.Windows.Controls import *
from System.Windows.Data import *
from ctypes import *
from decimal import *
import json

class PlanSettingForm(Window):
	def __init__(self,PlanJson):
		wpf.LoadComponent(self, r'F:\Proton\RayStation\Script\create file\PlanSettingBinding.xaml')
		#self.Topmost = True
		# Start up window at the center of the screen.
		self.WindowStartupLocation = WindowStartupLocation.CenterScreen
		self.DataContext = PlanJson
	def OKClicked(self,sender,event):
		
		self.DialogResult = True
	def CancelClicked(self,sender,event):
		self.DialogResult = False
	def DoseGridXLostFocus(self,sender,event):
		if self.Is_float_exp(self.GridX.Text) == False:
			self.GridXPopUp.IsOpen = True
			self.GridX.Focus()
		else:
			self.GridXPopUp.IsOpen = False
	def DoseGridYLostFocus(self,sender,event):
		if self.Is_float_exp(self.GridY.Text) == False:
			self.GridYPopUp.IsOpen = True
			self.GridY.Focus()
		else:
			self.GridYPopUp.IsOpen = False
	def DoseGridZLostFocus(self,sender,event):
		if self.Is_float_exp(self.GridZ.Text) == False:
			self.GridZPopUp.IsOpen = True
			self.GridZ.Focus()
		else:
			self.GridZPopUp.IsOpen = False
	def PartCombo_Changed(self,sender,event):
		tmpBinding = Binding()
		tmpBinding.Source = self.DataContext
		tmpBinding.Path =PropertyPath('[{}][PlanSetting][PlanProtocol]'.format(self.PartCombo.SelectedItem))
		self.ProtocolCombo.SetBinding(ComboBox.ItemsSourceProperty,tmpBinding)
	def ProtocolCombo_Changed(self,sender,event):
		self.BeamSetStack.Children.Clear()
		if not self.ProtocolCombo.SelectedItem == None:
			grid_list=[]
			for beamset in self.DataContext[self.PartCombo.SelectedItem]['PlanSetting']['PlanProtocol'][self.ProtocolCombo.SelectedItem]['BeamSet']:
				beamset_Dock = DockPanel()
				beamset_Dock.Name = "beamset_Dock"
				beamset_Dock.LastChildFill = False
				BeamSetParameterGrid = Grid()
				BeamSetParameterGrid.Name = 'BeamSetParameterGrid'
				RobustnessParameterStack = StackPanel()
				RobustnessParameterStack.Name = 'RobustnessParameterStack'
				RobustnessParameterStack.Orientation = Orientation.Horizontal
				BeamParametersStack = StackPanel()
				BeamParametersStack.Name = 'BeamParametersStack'
				BeamParametersStack.Margin = Thickness(5)
				BeamParametersStack.Orientation = Orientation.Horizontal
				BeamParametersStack.HorizontalAlignment = HorizontalAlignment.Center
				#beamset name
				BeamSetNameText = TextBlock()
				BeamSetNameText.Text = beamset['Name']
				BeamSetNameText.TextAlignment=TextAlignment.Left
				DockPanel.SetDock(BeamSetNameText,Dock.Top)
				beamset_Dock.Children.Add(BeamSetNameText)
				#beamset parameter
				BeamSetParameterGrid.RowDefinitions.Add(RowDefinition())
				BeamSetParaName = TextBlock()
				BeamSetParaName.Text = 'BeamSet Parameter'
				BeamSetParaName.TextAlignment=TextAlignment.Left
				BeamSetParaName.SetValue(Grid.RowProperty,0)
				BeamSetParaName.SetValue(Grid.RowProperty,0)
				BeamSetParameterGrid.ColumnDefinitions.Add(ColumnDefinition())
				BeamSetParameterGrid.ColumnDefinitions.Add(ColumnDefinition())
				BeamSetParameterGrid.Children.Add(BeamSetParaName)
				for key in beamset.keys(): 
					if type(beamset[key]) in (str,int):
						BSParaGridrow = BeamSetParameterGrid.RowDefinitions.Count
						BeamSetParameterGrid.RowDefinitions.Add(RowDefinition())
						tmpText = TextBlock()
						tmpText.Text = key
						tmpText.Margin = Thickness(5)
						tmpText.TextAlignment=TextAlignment.Left
						tmpText.SetValue(Grid.RowProperty,BSParaGridrow)
						tmpText.SetValue(Grid.ColumnProperty,0)
						BeamSetParameterGrid.Children.Add(tmpText)
						tmpTextBox = TextBox()
						tmpTextBox.Text = str(beamset[key])
						tmpTextBox.Margin = Thickness(5)
						tmpTextBox.TextAlignment=TextAlignment.Right
						tmpTextBox.VerticalContentAlignment = VerticalAlignment.Center
						tmpTextBox.SetValue(Grid.RowProperty,BSParaGridrow)
						tmpTextBox.SetValue(Grid.ColumnProperty,1)
						BeamSetParameterGrid.Children.Add(tmpTextBox)
				#Robustness parameter
				for R_Marker in beamset['RobustnessSetting'].keys():
					RobustnessParameterGrid = Grid()
					RobustnessParameterGrid.RowDefinitions.Add(RowDefinition())
					RobustnessParaName = TextBlock()
					RobustnessParaName.Text = 'Robustness "{}"'.format(R_Marker)
					RobustnessParaName.TextAlignment=TextAlignment.Left
					RobustnessParaName.SetValue(Grid.RowProperty,0)
					RobustnessParaName.SetValue(Grid.RowProperty,0)
					RobustnessParameterGrid.Children.Add(RobustnessParaName)
					RobustnessParameterGrid.ColumnDefinitions.Add(ColumnDefinition())
					RobustnessParameterGrid.ColumnDefinitions.Add(ColumnDefinition())
					for key,item in beamset['RobustnessSetting'][R_Marker].items():
						RobustParaGridrow = RobustnessParameterGrid.RowDefinitions.Count
						RobustnessParameterGrid.RowDefinitions.Add(RowDefinition())
						tmpText = TextBlock()
						tmpText.Text = key
						tmpText.Margin = Thickness(5)
						tmpText.TextAlignment=TextAlignment.Left
						tmpText.SetValue(Grid.RowProperty,RobustParaGridrow)
						tmpText.SetValue(Grid.ColumnProperty,0)
						RobustnessParameterGrid.Children.Add(tmpText)
						tmpTextBox = TextBox()
						tmpTextBox.Text = str(item)
						tmpTextBox.Margin = Thickness(5)
						tmpTextBox.TextAlignment=TextAlignment.Right
						tmpTextBox.SetValue(Grid.RowProperty,RobustParaGridrow)
						tmpTextBox.SetValue(Grid.ColumnProperty,1)
						RobustnessParameterGrid.Children.Add(tmpTextBox)
					RobustnessParameterStack.Children.Add(RobustnessParameterGrid)
				#Beams parameter
				for beam in beamset['Beams']:
					BeamParameterGrid = Grid()
					BeamParaGridcolumn = BeamParameterGrid.ColumnDefinitions.Count
					BeamParameterGrid.ColumnDefinitions.Add(ColumnDefinition())
					BeamParameterGrid.ColumnDefinitions.Add(ColumnDefinition())
					for key,item in beam.items():
						BeamParaGridrow = BeamParameterGrid.RowDefinitions.Count
						BeamParameterGrid.RowDefinitions.Add(RowDefinition())
						tmpText = TextBlock()
						tmpText.Text = key
						tmpText.Margin = Thickness(5)
						tmpText.TextAlignment=TextAlignment.Left
						tmpText.SetValue(Grid.RowProperty,BeamParaGridrow)
						tmpText.SetValue(Grid.ColumnProperty,BeamParaGridcolumn)
						BeamParameterGrid.Children.Add(tmpText)
						tmpTextBox = TextBox()
						tmpTextBox.Text = str(item)
						tmpTextBox.Margin = Thickness(5)
						tmpTextBox.TextAlignment=TextAlignment.Right
						tmpTextBox.SetValue(Grid.RowProperty,BeamParaGridrow)
						tmpTextBox.SetValue(Grid.ColumnProperty,BeamParaGridcolumn + 1)
						BeamParameterGrid.Children.Add(tmpTextBox)
					BeamParametersStack.Children.Add(BeamParameterGrid)
				#BeamSetParameter insert setting
				DockPanel.SetDock(BeamSetParameterGrid,Dock.Left)
				#RobustnessParameter insert setting
				DockPanel.SetDock(RobustnessParameterStack,Dock.Left)
				#BeamsPrameter
				DockPanel.SetDock(BeamParametersStack,Dock.Bottom)
				tmpText=TextBlock()
				tmpText = TextBlock()
				tmpText.Text = 'Beam Parameters'
				tmpText.Margin = Thickness(5)
				tmpText.TextAlignment=TextAlignment.Center
				DockPanel.SetDock(tmpText,Dock.Bottom)
				
				beamset_Dock.Children.Add(BeamParametersStack)
				beamset_Dock.Children.Add(tmpText)
				beamset_Dock.Children.Add(BeamSetParameterGrid)
				beamset_Dock.Children.Add(RobustnessParameterStack)
				self.BeamSetStack.Children.Add(beamset_Dock)
	def Is_float_exp(self,f_str):
		if re.match('^-?\d+\.\d+$',f_str) is None:
			return False
		else:
			return True
	def Dictionary_Update(self):
		#Grid setting
		self.pj[self.PartCombo.SelectedItem]['PlanSetting']['DoseGrid']['x']=self.GridX.Text
		self.pj[self.PartCombo.SelectedItem]['PlanSetting']['DoseGrid']['y']=self.GridY.Text
		self.pj[self.PartCombo.SelectedItem]['PlanSetting']['DoseGrid']['z']=self.GridZ.Text
		#BeamSet Parameter
		for obj in self.BeamSetParameterGrid.Children:
			if type(obj) is TextBlock:
				row = obj.GetValue(Grid.RowProperty)
				
					
		

with open(r"F:\Proton\RayStation\Script\create file\Data\PlanSetting.json") as f:
	PlanSetting = json.load(f,object_pairs_hook = collections.OrderedDict)

PSF = PlanSettingForm(PlanSetting)
PSF.ShowDialog()
