from connect import *
import collections
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../Data'))
import wpf
from System.Windows import *
from System.Windows.Controls import *
from System.Windows.Data import *
from decimal import *
import time
import json
import re
from testPyfiles.objectbuilder import ObjectBuilder, MAPPING_ROOT_CLASS

case = get_current("Case")

# Change this variable if you change the beam model
Machine_Name = "CGTRn_06"


class AddSiteForm(Window):
    def __init__(self, jsonClass):
        wpf.LoadComponent(self, os.path.join(os.path.dirname(__file__), './xaml/AddNew.xaml'))
        self.Topmost = True
        # Start up window at the center of the screen.
        self.MessageText.Text = "Please input the irradiation site"
        self.WindowStartupLocation = WindowStartupLocation.CenterScreen
        self.DataContext = jsonClass

    def AddClicked(self, sender, event):
        if self.NewTextBox.Text == "":
            return
        AddPart = Part()
        AddPart.PartName = self.NewTextBox.Text
        AddPart.PlanSetting = PlanSetting()
        AddPart.PlanSetting.DoseGrid = DoseGrid()
        AddPart.PlanSetting.DoseGrid.x = 0.2
        AddPart.PlanSetting.DoseGrid.y = 0.2
        AddPart.PlanSetting.DoseGrid.z = 0.2
        AddPart.PlanSetting.PlanProtocol = []
        self.DataContext.Part.append(AddPart)
        self.DialogResult = True

    def CancelClicked(self, sender, event):
        self.DialogResult = False


class AddProtocolForm(Window):
    def __init__(self, jsonClass):
        wpf.LoadComponent(self, os.path.join(os.path.dirname(__file__), './xaml/AddNew.xaml'))
        self.Topmost = True
        # Start up window at the center of the screen.
        self.MessageText.Text = "Please input the Protocol Name"
        self.WindowStartupLocation = WindowStartupLocation.CenterScreen
        self.DataContext = jsonClass

    def AddClicked(self, sender, event):
        if self.NewTextBox.Text == "":
            return
        AddProtocol = PlanProtocol()
        AddProtocol.ProtocolName = self.NewTextBox.Text
        AddProtocol.BeamSet = []
        self.DataContext.append(AddProtocol)
        self.DialogResult = True

    def CancelClicked(self, sender, event):
        self.DialogResult = False


class AddBeamSetForm(Window):
    def __init__(self, jsonClass):
        wpf.LoadComponent(self, os.path.join(os.path.dirname(__file__), './xaml/AddNew.xaml'))
        self.Topmost = True
        # Start up window at the center of the screen.
        self.MessageText.Text = "Please input the BeamSet Name"
        self.WindowStartupLocation = WindowStartupLocation.CenterScreen
        self.DataContext = jsonClass

    def AddClicked(self, sender, event):
        if self.NewTextBox.Text == "":
            return
        AddBeamSet = BeamSet()
        AddBeamSet.Name = self.NewTextBox.Text
        AddBeamSet.NumberOfFractions = ""
        AddBeamSet.DoseValue = ""
        AddBeamSet.Dose_fr = ""
        AddBeamSet.Beams = []
        AddBeamSet.RobustnessSetting = RobustnessSetting()
        AddBeamSet.RobustnessSetting.Sup = 0.3
        AddBeamSet.RobustnessSetting.Inf = 0.3
        AddBeamSet.RobustnessSetting.R = 0.3
        AddBeamSet.RobustnessSetting.L = 0.3
        AddBeamSet.RobustnessSetting.Ant = 0.3
        AddBeamSet.RobustnessSetting.Pos = 0.3
        AddBeamSet.RobustnessSetting.Uncertainty = 0.035
        self.DataContext.append(AddBeamSet)
        self.DialogResult = True

    def CancelClicked(self, sender, event):
        self.DialogResult = False


class PSForm(Window):
    def __init__(self, PlanSettingJson):
        wpf.LoadComponent(self, os.path.join(os.path.dirname(__file__), './xaml/PlanCreateSettingBinding.xaml'))
        self.Topmost = True
        # Start up window at the center of the screen.
        self.WindowStartupLocation = WindowStartupLocation.CenterScreen
        self.DataContext = PlanSettingJson
        self.ExamCombo.ItemsSource = [exam.Name for exam in case.Examinations if exam.EquipmentInfo.Modality == "CT"]
        self.DataChangeFlag = False

    def Refresh(self):
        self.DataContext = None
        global result
        self.DataContext = result
        self.DataChangeFlag = True

    def TextBoxLostFocus(self, sender, event):
        tmpSelected = self.BeamSetTabControl.SelectedItem
        self.Refresh()
        self.BeamSetTabControl.SelectedItem = tmpSelected

    def OKClicked(self, sender, event):
        tmpTargetList = [beamset.TargetROI for beamset in self.ProtocolCombo.SelectedItem.BeamSet]
        if '' in tmpTargetList:
            msg = msgbox("Check", "TargetROI is Nothing")
            msg.ShowDialog()
            return
        if not type(self.ExamCombo.SelectedValue) is str:
            msg = msgbox("Check", "PlanningCT is Nothing")
            msg.ShowDialog()
            return
        self.DialogResult = True

    def CancelClicked(self, sender, event):
        self.DialogResult = False

    def AddNewSiteClicked(self, sender, event):
        AddForm = AddSiteForm(self.DataContext)
        AddForm.ShowDialog()
        if AddForm.DialogResult:
            self.Refresh()
            self.PartCombo.SelectedItem = self.PartCombo.ItemsSource[-1]

    def DeleteSiteClicked(self, sender, event):
        if not self.PartCombo.SelectedItem == None:
            self.DataContext.Part.remove(self.PartCombo.SelectedItem)
            self.PartCombo.SelectedItem = None
            self.Refresh()

    def AddNewProtocolClicked(self, sender, event):
        if not self.PartCombo.SelectedItem == None:
            AddForm = AddProtocolForm(self.ProtocolCombo.ItemsSource)
            AddForm.ShowDialog()
            if AddForm.DialogResult:
                self.Refresh()
                self.ProtocolCombo.SelectedItem = self.ProtocolCombo.ItemsSource[-1]

    def DeleteProtocolClicked(self, sender, event):
        if not self.ProtocolCombo.SelectedItem == None:
            self.ProtocolCombo.ItemsSource.remove(self.ProtocolCombo.SelectedItem)
            self.ProtocolCombo.SelectedItem = None
            self.Refresh()

    def ProtocolComboChanged(self, sender, event):
        if not self.ProtocolCombo.SelectedItem == None and not self.BeamSetTabControl.ItemsSource == None:
            self.BeamSetTabControl.SelectedItem = self.BeamSetTabControl.ItemsSource[0]

    def AddNewBeamSetClicked(self, sender, event):
        if not self.ProtocolCombo.SelectedItem == None:
            AddForm = AddBeamSetForm(self.BeamSetCombo.ItemsSource)
            AddForm.ShowDialog()
            if AddForm.DialogResult:
                self.Refresh()
                self.BeamSetCombo.SelectedItem = self.BeamSetCombo.ItemsSource[-1]

    def DeleteBeamSetClicked(self, sender, event):
        if not self.BeamSetCombo.SelectedItem == None:
            self.BeamSetCombo.ItemsSource.remove(self.BeamSetCombo.SelectedItem)
            self.BeamSetCombo.SelectedItem = None
            self.Refresh()

    def AddNewBeam(self, sender, event):
        if not self.BeamSetTabControl.SelectedItem == None:
            selectedItem = self.BeamSetTabControl.SelectedItem
            AddBeam = Beams()
            AddBeam.BeamName = ""
            AddBeam.Description = ""
            AddBeam.GantryAngle = ""
            AddBeam.CouchAngle = ""
            self.BeamSetTabControl.SelectedItem.Beams.append(AddBeam)
            self.Refresh()
            self.BeamSetTabControl.SelectedItem = selectedItem

    def TextBoxGotFocus(self, sender, event):
        sender.SelectAll()

    def DoseValueChanged(self, sender, event):
        if self.BeamSetTabControl.SelectedItem.NumberOfFractions <> 0:
            self.BeamSetTabControl.SelectedItem.Dose_fr = int(int(self.BeamSetTabControl.SelectedItem.DoseValue) / int(
                self.BeamSetTabControl.SelectedItem.NumberOfFractions))

    def Dose_frChanged(self, sender, event):
        self.BeamSetTabControl.SelectedItem.DoseValue = int(int(self.BeamSetTabControl.SelectedItem.Dose_fr) * int(
            self.BeamSetTabControl.SelectedItem.NumberOfFractions))


class msgbox(Window):
    def __init__(self, title, text):
        wpf.LoadComponent(self, os.path.join(os.path.dirname(__file__), './xaml/messagebox(OKonly).xaml'))
        self.Topmost = True
        # Start up window at the center of the screen.
        self.WindowStartupLocation = WindowStartupLocation.CenterScreen
        self.Caption.Title = title
        self.msg.Text = text

    def OK_Clicked(self, sender, event):
        self.DialogResult = True


class Root:
    pass


class Part:
    pass


class PlanSetting:
    pass


class DoseGrid:
    pass


class PlanProtocol:
    pass


class BeamSet:
    # create list of Target ROIs
    TargetROIClassList = [roi.Name for roi in case.PatientModel.RegionsOfInterest if
                          roi.OrganData.OrganType == 'Target' and not "pct" in roi.Name]

    def __init__(self):
        self.TargetROI = ''
        self.TargetROIList = self.TargetROIClassList


class Beams:
    pass


class RobustnessSetting:
    pass


class PlanSettingData():
    pass


class Protocol():
    pass


def create_plan_using_json_data():
    start_time = time.time()
    with open(os.path.join(os.path.dirname(__file__), '../Data/PlanSettingClass.json')) as f:
        PlanSettingJson = json.load(f, object_pairs_hook=collections.OrderedDict)
    object_mapping = {MAPPING_ROOT_CLASS: Root, 'Part': Part, 'PlanSetting': PlanSetting, 'DoseGrid': DoseGrid,
                      'PlanProtocol': PlanProtocol, 'BeamSet': BeamSet, 'Beams': Beams,
                      'RobustnessSetting': RobustnessSetting}
    builder = ObjectBuilder(mapping=object_mapping)
    global result
    result = builder.build(PlanSettingJson)

    form = PSForm(result)
    form.ShowDialog()

    if form.DialogResult:
        Protocol = form.ProtocolCombo.SelectedItem
    else:
        sys.exit()

    Plan_Name = form.PartCombo.SelectedItem.PartName
    PlanNameList = [tmpPlan.Name for tmpPlan in case.TreatmentPlans]
    if Plan_Name in PlanNameList:
        for i in range(99):
            tmpPlan_Name = Plan_Name + str(i + 1)
            if not tmpPlan_Name in PlanNameList:
                Plan_Name = tmpPlan_Name
            break

    ExamName = form.ExamCombo.SelectedValue
    PlanDoseGrid = form.PartCombo.SelectedItem.PlanSetting.DoseGrid

    PlanSettings = form.ProtocolCombo.SelectedItem
    angles_of_gantry_and_couch = []
    for BeamSetData in PlanSettings.BeamSet:
        for beam in BeamSetData.Beams:
            angles_of_gantry_and_couch.append((beam.GantryAngle, beam.CouchAngle))

    plan = case.AddNewPlan(PlanName=Plan_Name, PlannedBy="", Comment="", ExaminationName=ExamName,
                           AllowDuplicateNames=False)
    plan.SetDefaultDoseGrid(VoxelSize={'x': PlanDoseGrid.x, 'y': PlanDoseGrid.y, 'z': PlanDoseGrid.z})
    roi_list = [roi_geometry.OfRoi.Name for roi_geometry in case.PatientModel.StructureSets[ExamName].RoiGeometries]
    Iso_center = {'x': [],
                  'y': [],
                  'z': []}
    for BeamSetData in PlanSettings.BeamSet:
        CTV_center = case.PatientModel.StructureSets[ExamName].RoiGeometries[
            BeamSetData.TargetROI].GetCenterOfRoi()
        # create vPTV
        if (90, 0) and (90, 180) in angles_of_gantry_and_couch:
            if not re.sub('(CTV|Ctv)', 'vPTV', BeamSetData.TargetROI) in roi_list:
                retval_0 = case.PatientModel.CreateRoi(Name=re.sub('(CTV|Ctv)', 'vPTV', BeamSetData.TargetROI),
                                                       Color="255, 128, 255", Type="Ptv", TissueName=None,
                                                       RbeCellTypeName=None, RoiMaterial=None)
                retval_0.SetMarginExpression(SourceRoiName=BeamSetData.TargetROI,
                                             MarginSettings={'Type': "Expand",
                                                             'Superior': BeamSetData.RobustnessSetting.Sup,
                                                             'Inferior': BeamSetData.RobustnessSetting.Inf,
                                                             'Anterior': BeamSetData.RobustnessSetting.Ant,
                                                             'Posterior': BeamSetData.RobustnessSetting.Pos,
                                                             'Right': 0.6,
                                                             'Left': 0.6})
                retval_0.UpdateDerivedGeometry(Examination=case.Examinations[ExamName], Algorithm="Auto")
                roi_list.append(re.sub('(CTV|Ctv)', 'vPTV', BeamSetData.TargetROI))
        # create PTV
        if not re.sub('(CTV|Ctv)', 'PTV', BeamSetData.TargetROI) in roi_list:
            retval_1 = case.PatientModel.CreateRoi(Name=re.sub('(CTV|Ctv)', 'PTV', BeamSetData.TargetROI),
                                                   Color="Magenta",
                                                   Type="Ptv", TissueName=None, RbeCellTypeName=None,
                                                   RoiMaterial=None)
            retval_1.SetMarginExpression(SourceRoiName=BeamSetData.TargetROI,
                                         MarginSettings={'Type': "Expand",
                                                         'Superior': BeamSetData.RobustnessSetting.Sup,
                                                         'Inferior': BeamSetData.RobustnessSetting.Inf,
                                                         'Anterior': BeamSetData.RobustnessSetting.Ant,
                                                         'Posterior': BeamSetData.RobustnessSetting.Pos,
                                                         'Right': BeamSetData.RobustnessSetting.R,
                                                         'Left': BeamSetData.RobustnessSetting.L})
            retval_1.UpdateDerivedGeometry(Examination=case.Examinations[ExamName], Algorithm="Auto")
            roi_list.append(re.sub('(CTV|Ctv)', 'PTV', BeamSetData.TargetROI))
        # Beam Setting
        Iso_center['x'].append(Decimal(str(CTV_center.x)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
        Iso_center['y'].append(Decimal(str(CTV_center.y)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
        Iso_center['z'].append(Decimal(str(CTV_center.z)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
        # Iso_center = {'x': Decimal(str(CTV_center.x)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP),
        #               'y': Decimal(str(CTV_center.y)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP),
        #               'z': Decimal(str(CTV_center.z)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)}

        tmpBeamSet = plan.AddNewBeamSet(Name=BeamSetData.Name, ExaminationName=ExamName, MachineName=Machine_Name,
                                        Modality="Protons", TreatmentTechnique="ProtonPencilBeamScanning",
                                        PatientPosition="HeadFirstSupine",
                                        NumberOfFractions=BeamSetData.NumberOfFractions,
                                        CreateSetupBeams=False, UseLocalizationPointAsSetupIsocenter=False, Comment="",
                                        RbeModelReference=None, EnableDynamicTrackingForVero=False)

        tmpBeamSet.AddDosePrescriptionToRoi(RoiName=BeamSetData.TargetROI, DoseVolume=0, PrescriptionType="MedianDose",
                                            DoseValue=BeamSetData.DoseValue, RelativePrescriptionLevel=1,
                                            AutoScaleDose=False)

        for BeamData in BeamSetData.Beams:
            BeamName = BeamData.BeamName
            tmpBeam = tmpBeamSet.CreatePBSIonBeam(SnoutId="NoSnout", SpotTuneId="3.0", RangeShifter=None,
                                                  MinimumAirGap=None, MetersetRateSetting="", IsocenterData={
                    'Position': {'x': float(Iso_center['x'][0]), 'y': float(Iso_center['y'][0]),
                                 'z': float(Iso_center['z'][0])},
                    'NameOfIsocenterToRef': "", 'Name': BeamSetData.Name, 'Color': "98, 184, 234"}, Name=BeamName,
                                                  Description=BeamData.Description, GantryAngle=BeamData.GantryAngle,
                                                  CouchRotationAngle=BeamData.CouchAngle, CouchPitchAngle=0,
                                                  CouchRollAngle=0, CollimatorAngle=0)
    # Plan Optimization
    plan_opt_list = [opt for opt in plan.PlanOptimizations]

    for plan_opt in plan_opt_list:
        for opt_beamset in plan_opt.OptimizedBeamSets:
            for BeamSetData in PlanSettings.BeamSet:
                if opt_beamset.DicomPlanLabel == BeamSetData.Name:
                    plan_opt.AddOptimizationFunction(FunctionType="UniformDose", RoiName=BeamSetData.TargetROI,
                                                     IsConstraint=False, RestrictAllBeamsIndividually=False,
                                                     RestrictToBeam=None, IsRobust=True, RestrictToBeamSet=None,
                                                     UseRbeDose=False)
                    plan_opt.Objective.ConstituentFunctions[0].DoseFunctionParameters.DoseLevel = \
                        plan_opt.OptimizedBeamSets[0].Prescription.PrimaryDosePrescription.DoseValue
                    plan_opt.Objective.ConstituentFunctions[0].DoseFunctionParameters.Weight = 100
                    plan_opt.AddOptimizationFunction(FunctionType="DoseFallOff", RoiName="External", IsConstraint=False,
                                                     RestrictAllBeamsIndividually=False, RestrictToBeam=None,
                                                     IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)
                    plan_opt.Objective.ConstituentFunctions[1].DoseFunctionParameters.HighDoseLevel = \
                        plan_opt.OptimizedBeamSets[0].Prescription.PrimaryDosePrescription.DoseValue
                    plan_opt.AddOptimizationFunction(FunctionType="MaxDose", RoiName="External", IsConstraint=True,
                                                     RestrictAllBeamsIndividually=False, RestrictToBeam=None,
                                                     IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)
                    plan_opt.Constraints[0].DoseFunctionParameters.DoseLevel = \
                        plan_opt.OptimizedBeamSets[0].Prescription.PrimaryDosePrescription.DoseValue * 1.025

                    plan_opt.OptimizationParameters.SaveRobustnessParameters(
                        PositionUncertaintyAnterior=BeamSetData.RobustnessSetting.Ant,
                        PositionUncertaintyPosterior=BeamSetData.RobustnessSetting.Pos,
                        PositionUncertaintySuperior=BeamSetData.RobustnessSetting.Sup,
                        PositionUncertaintyInferior=BeamSetData.RobustnessSetting.Inf,
                        PositionUncertaintyLeft=BeamSetData.RobustnessSetting.L,
                        PositionUncertaintyRight=BeamSetData.RobustnessSetting.R,
                        DensityUncertainty=BeamSetData.RobustnessSetting.Uncertainty,
                        PositionUncertaintySetting='Universal',
                        IndependentLeftRight=True,
                        IndependentAnteriorPosterior=True,
                        IndependentSuperiorInferior=True,
                        ComputeExactScenarioDoses=False,
                        NamesOfNonPlanningExaminations=[])
                    plan_opt.RunOptimization()
    elapsed_time = time.time() - start_time

    print('Elapsed time is {} sec'.format(elapsed_time))


# test
if __name__ == '__main__':
    create_plan_using_json_data()
