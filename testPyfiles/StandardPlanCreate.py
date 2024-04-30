# Script recorded 03 Dec 2018

#   RayStation version: 6.2.0.7
#   Selected patient: ...

from connect import *
import collections
import re
import sys
sys.path.append(r"F:\Proton\RayStation\Script\create file")
from GUI import *
from System.Windows.Forms import *
import wpf
from System.Windows import *
from System.Windows.Controls import *
from ctypes import *
from decimal import *

case = get_current("Case")
exam = get_current("Examination")

# msgbox = windll.user32.MessageBoxW
roi_list =[roi.Name for roi in case.PatientModel.RegionsOfInterest]
plan_list =[plan.Name for plan in case.TreatmentPlans]


if type(case.TreatmentPlans) !='NoneType':
	plan_list =[plan.Name for plan in case.TreatmentPlans]
	plan_name = 'Prostate'
	if plan_name in plan_list:
		# msgbox(None,'There is already Plan named "Prostate"','Warning',0x0000040)
		# msgbox
		# sys.exit()
		msgbox=MessageBox('Warning','YesNo','There is already Plan named "Prostate"')
		msgbox.ShowDialog()
		if msgbox.DialogResult:
			if msgbox.YNBool == 2:
				sys.exit()
			else:
				i=1
				cnt=0
				while plan_name in plan_list:
					cnt += 1
					re_pran_name=re.search('[0-9]+',plan_name)
					if not re_pran_name == None:
						i=int(re_pran_name.group()) + 1
					plan_name += str(i)
					if cnt > 99:
						sys.exit()
		else:
			sys.exit()

class PlanForm(Window):
	def __init__(self):
		wpf.LoadComponent(self, r'F:\Proton\RayStation\Script\create file\StandardPlanForm.xaml')
		#self.Topmost = True
		# Start up window at the center of the screen.
		self.WindowStartupLocation = WindowStartupLocation.CenterScreen
		# IsBoost_bool initialize
		self.IsBoost_bool = False
		#Radio button initialize
		for radio in self.RadioStack.Children:
			radio.IsEnabled = False
		#ComboBox initialize
		CTV_list=[ctv for ctv in roi_list if re.match('^(CTV|Ctv)(\W|_)*[0-9]*$',ctv)]
		for ctv in CTV_list:
			self.InitialCTV_Combo.Items.Add(ctv)
			self.BoostCTV_Combo.Items.Add(ctv)
	def IsMarkerCombo_Changed(self, sender, event):
		if self.IsMarkerCombo.SelectedItem == 'With Marker':
			for radio in self.RadioStack.Children:
				radio.IsEnabled = True
			self.IsInitial.IsChecked = True
			self.IsMarker = True
		else:
			for radio in self.RadioStack.Children:
				radio.IsEnabled = False
			self.IsBoost.IsChecked = True
			self.IsMarker = False
	def InitialPlanChecked(self, sender, event):
		self.IsInitial_bool = self.IsInitial.IsChecked
		self.IsBoost_bool = self.IsBoost.IsChecked
		self.BoostText.Visibility = Visibility.Collapsed
		self.BoostCTV_Combo.Visibility = Visibility.Collapsed
		self.InitialText.Text = "Please select ROI used as CTV"
	def BoostPlanChecked(self, sender, event):
		self.IsBoost_bool = self.IsBoost.IsChecked
		self.IsInitial_bool = self.IsInitial.IsChecked
		self.BoostText.Visibility = Visibility.Visible
		self.BoostCTV_Combo.Visibility = Visibility.Visible
		self.InitialText.Text = "Please select ROI used as CTV for Initial plan"
	def OKClicked(self, sender, event):
		self.InitialCTV = self.InitialCTV_Combo.SelectedItem
		if self.InitialCTV == None:
			msgbox('Warning','OKOnly','CTV is not selected')
			return
		if self.IsBoost_bool == True:
			self.BoostCTV = self.BoostCTV_Combo.SelectedItem
			if self.BoostCTV == None:
				msgbox('Warning','OKOnly','Boost CTV is not selected')
				return
		
		self.DialogResult=True
	def CancelClicked(self, sender, event):
		self.DialogResult=False


dialog = PlanForm()
dialog.ShowDialog()
if dialog.DialogResult == False:
	sys.exit()


class FractionOptForm(Window):
	def __init__(self):
		wpf.LoadComponent(self, r'F:\Proton\RayStation\Script\create file\BoostOption.xaml')
		#self.Topmost = True
		# Start up window at the center of the screen.
		self.WindowStartupLocation = WindowStartupLocation.CenterScreen
		#Grid setting
		if dialog.IsBoost_bool:
			tmpDic=collections.OrderedDict({'Prostate_A_1':10,'Prostate_A_2':10,'Prostate_B_1':10,'Prostate_B_2':9})
		else:
			tmpDic=collections.OrderedDict({'Prostate_A_1':20,'Prostate_A_2':19})
		BeamSetOptDict=collections.OrderedDict(sorted(tmpDic.items(), key=lambda x: x[0]))
		self.TotalFr = 0
		for key in BeamSetOptDict.keys():
			self.TotalFr += BeamSetOptDict[key]
			self.add_row(key,str(BeamSetOptDict[key]))
		self.TotalFractions.Text = "Total Fractions {}fr".format(str(self.TotalFr))
		self.TotalDose=0
		self.FO_dict = collections.OrderedDict()
	def add_row(self,BeamSetName,Fractions):
		row = self.BoostOptGrid.RowDefinitions.Count
		self.BoostOptGrid.RowDefinitions.Add(RowDefinition())
		tb = TextBlock()
		tb.Text = BeamSetName
		tb.Margin = Thickness(5)
		tb.TextAlignment = TextAlignment.Left
		tb.VerticalAlignment = VerticalAlignment.Center
		tb.SetValue(Grid.RowProperty, row)
		tb.SetValue(Grid.ColumnProperty,0)
		self.BoostOptGrid.Children.Add(tb)
		
		tbx = TextBox()
		tbx.Name = tb.Text
		tbx.Text = Fractions
		tbx.Margin = Thickness(5)
		tbx.TextAlignment = TextAlignment.Left
		tbx.VerticalAlignment = VerticalAlignment.Center
		tbx.SetValue(Grid.RowProperty, row)
		tbx.SetValue(Grid.ColumnProperty,1)
		tbx.TextChanged += self.TextChanged
		self.BoostOptGrid.Children.Add(tbx)
	def PreDoseChanged(self,sender,event):
		self.DosePopUp.IsOpen = False
	def TextChanged(self,sender,event):
		TF=0
		for r in self.BoostOptGrid.Children:
			if r.GetValue(Grid.ColumnProperty) == 1:
				if r.Text.isdecimal():
					TF += int(r.Text)
		self.TotalFr = int(TF)
		self.FrPopUp.IsOpen=False
		self.TotalFractions.Text = "Total Fractions {}fr".format(str(TF))
	def OK_Clicked(self,sender,event):
		if not self.PreDose.Text.isdecimal():
			self.DosePopUp.IsOpen = True
			return
		elif int(self.PreDose.Text) % self.TotalFr != 0:
			self.FrPopUp.IsOpen=True
			return
		else:
			for r in self.BoostOptGrid.Children:
				if r.GetValue(Grid.ColumnProperty) == 1:
					self.FO_dict.setdefault(r.Name,r.Text)
			self.TotalDose = int(self.PreDose.Text)
			self.DialogResult=True
	def Cancel_Clicked(self,sender,event):
		self.DialogResult=False

FOptForm = FractionOptForm()
FOptForm.ShowDialog()

class BeamSetSetting():
	def __init__(self,TargetROI='',BeamSetName='',NumberOfFractions=0,DoseValue=0,GantryAngle=90,CouchAngle=0,Robust={}):
		self.TR = TargetROI
		self.BeamSetName = BeamSetName
		self.NOF = NumberOfFractions
		self.DV = DoseValue
		self.GA = GantryAngle
		self.CA = CouchAngle
		self.RobustSet = Robust

BeamSetList = []

DosePerFractions = FOptForm.TotalDose/FOptForm.TotalFr

for key,item in FOptForm.FO_dict.items():
# CouchAngle
	if re.search('[0-9]$',key).group() == str(1):
		CA = 0
	elif re.search('[0-9]$',key).group() == str(2):
		CA = 180
#CTV setting
	if 'Prostate_A' in key:
		TargetCTV=dialog.InitialCTV
		if dialog.IsMarker == True:
			Robust_dict={"Sup":0.3,"Inf":0.3,"R":0.3,"L":0.3,"Ant":0.3,"Pos":0.2,"Uncertainty":0.035}
		else:
			Robust_dict={"Sup":0.5,"Inf":0.5,"R":0.5,"L":0.5,"Ant":0.5,"Pos":0.3,"Uncertainty":0.035}
	elif 'Prostate_B' in key:
		TargetCTV=dialog.BoostCTV
		Robust_dict={"Sup":0.3,"Inf":0.3,"R":0.3,"L":0.3,"Ant":0.3,"Pos":0.2,"Uncertainty":0.035}
# Dose for BeamSetList
	tmpDV=DosePerFractions*int(item)
	print(tmpDV)
# class list create
	BeamSetList.append(BeamSetSetting(TargetROI=TargetCTV,BeamSetName=key,NumberOfFractions=item,DoseValue=tmpDV,GantryAngle=90,CouchAngle=CA,Robust=Robust_dict))

plan = case.AddNewPlan(PlanName=plan_name, PlannedBy="", Comment="", ExaminationName=exam.Name, AllowDuplicateNames=False)
plan.SetDefaultDoseGrid(VoxelSize={ 'x': 0.2, 'y': 0.2, 'z': 0.2 })



for BSS in BeamSetList:
	CTV_center = plan.TreatmentCourse.TotalDose.OnDensity.RoiListSource.StructureSets[exam.Name].RoiGeometries[BSS.TR].GetCenterOfRoi()
	
	Iso_center = {'x':Decimal(str(CTV_center.x)).quantize(Decimal('0.1'),rounding=ROUND_HALF_UP),'y':Decimal(str(CTV_center.y)).quantize(Decimal('0.1'),rounding=ROUND_HALF_UP),'z':Decimal(str(CTV_center.z)).quantize(Decimal('0.1'),rounding=ROUND_HALF_UP)}
	
	tmpBeamSet = plan.AddNewBeamSet(Name=BSS.BeamSetName, ExaminationName=exam.Name, MachineName="CGTRn_03", Modality="Protons", TreatmentTechnique="ProtonPencilBeamScanning", PatientPosition="HeadFirstSupine", NumberOfFractions=BSS.NOF, CreateSetupBeams=False, UseLocalizationPointAsSetupIsocenter=False, Comment="", RbeModelReference=None, EnableDynamicTrackingForVero=False)
	
	tmpBeamSet.AddDosePrescriptionToRoi(RoiName=BSS.TR, DoseVolume=0, PrescriptionType="MedianDose", DoseValue=BSS.DV, RelativePrescriptionLevel=1, AutoScaleDose=False)
	
	BeamName=re.sub('^([A-Z][a-z])\w*_([A-Z])_[0-9]$',r'\1\2',BSS.BeamSetName)+re.sub('[A-Z][a-z]\w*_[A-Z]_([0-9]*)$',r'\1',BSS.BeamSetName).zfill(2)
	
	tmpBeam = tmpBeamSet.CreatePBSIonBeam(SnoutId="NoSnout", SpotTuneId="3.0", RangeShifter=None, MinimumAirGap=None, MetersetRateSetting="", IsocenterData={ 'Position': { 'x': float(Iso_center['x']), 'y': float(Iso_center['y']), 'z': float(Iso_center['z']) }, 'NameOfIsocenterToRef': "", 'Name': BSS.BeamSetName, 'Color': "98, 184, 234" }, Name=BeamName, Description="G{0:0=3}C{1:0=3}".format(BSS.GA,BSS.CA), GantryAngle=BSS.GA, CouchAngle=BSS.CA, CollimatorAngle=0)


plan_opt_list = [opt for opt in plan.PlanOptimizations]

for plan_opt in plan_opt_list:
	for opt_beamset in plan_opt.OptimizedBeamSets:
		for BSS in BeamSetList:
			if opt_beamset.DicomPlanLabel == BSS.BeamSetName:
				plan_opt.AddOptimizationFunction(FunctionType="UniformDose", RoiName=BSS.TR, IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=True, RestrictToBeamSet=None, UseRbeDose=False)
				plan_opt.Objective.ConstituentFunctions[0].DoseFunctionParameters.DoseLevel = plan_opt.OptimizedBeamSets[0].Prescription.PrimaryDosePrescription.DoseValue
				plan_opt.Objective.ConstituentFunctions[0].DoseFunctionParameters.Weight = 10
				plan_opt.AddOptimizationFunction(FunctionType="DoseFallOff", RoiName="External", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)
				plan_opt.Objective.ConstituentFunctions[1].DoseFunctionParameters.HighDoseLevel = plan_opt.OptimizedBeamSets[0].Prescription.PrimaryDosePrescription.DoseValue
# RobustnessParameters 
				plan_opt.OptimizationParameters.SaveRobustnessParameters(PositionUncertaintyAnterior=BSS.RobustSet["Ant"], PositionUncertaintyPosterior=BSS.RobustSet["Pos"], PositionUncertaintySuperior=BSS.RobustSet["Sup"], PositionUncertaintyInferior=BSS.RobustSet["Inf"], PositionUncertaintyLeft=BSS.RobustSet["L"], PositionUncertaintyRight=BSS.RobustSet["R"], DensityUncertainty=BSS.RobustSet["Uncertainty"], IndependentBeams=False, ComputeExactScenarioDoses=False, NamesOfNonPlanningExaminations=[])
				plan_opt.RunOptimization()
	
