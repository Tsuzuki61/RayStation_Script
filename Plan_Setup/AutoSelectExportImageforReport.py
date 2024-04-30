# Script recorded 24 Jul 2019

#   RayStation version: 6.2.0.7
#   Selected patient: ...

from connect import *
from decimal import *
import os
import sys
import wpf
from System.Windows import *
from System.Windows.Controls import *
from System.Windows.Data import *


class RoiProperty:
    def __init__(self, name):
        self.ROI = name
        self.View = False


class Rois:
    def __init__(self):
        self.Type = ""
        self.RoiPropertys = []


class ReportSettingForm(Window):
    def __init__(self, CTSliceThickness, ThicknessCoefficient, Thickness, Slice_Number, AddImageNumber, RoiTypeDict,
                 target, Sup_z, Inf_z):
        wpf.LoadComponent(self, os.path.join(os.path.dirname(__file__), './xaml/ReportSetting.xaml'))
        self.Topmost = True
        # Start up window at the center of the screen.
        self.Sup_z = Sup_z
        self.Inf_z = Inf_z
        self.WindowStartupLocation = WindowStartupLocation.CenterScreen
        self.TargetTextBlock.Text = 'TargetROI is {}'.format(target)
        self.RoiListBox.ItemsSource = RoiTypeDict.values()
        for i in range(1, 6):
            self.IntervalCombo.Items.Add(
                str(Decimal(str(CTSliceThickness * i)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)))
        self.IntervalCombo.SelectedValue = str(Decimal(str(Thickness)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
        self.AdditionalTextBox.Text = str(AddImageNumber)
        self.NumberTextBlock.Text = str(Slice_Number)
        self.ViewEnableCheckBox.IsChecked = True
        self.Thickness = Decimal(str(Thickness)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
        self.Slice_Number = Slice_Number

    def OKClicked(self, sender, event):
        self.Thickness = Decimal(self.IntervalCombo.SelectedValue)
        self.Slice_Number = int(self.NumberTextBlock.Text)
        self.DialogResult = True

    def CancelClicked(self, sender, event):
        self.DialogResult = False

    def AdditionalTextBoxChanged(self, sender, event):
        if not self.IntervalCombo.SelectedValue == None and not sender.Text == "":
            self.NumberTextBlock.Text = str(int(
                Decimal((self.Sup_z - self.Inf_z) / Decimal(self.IntervalCombo.SelectedValue)).quantize(Decimal('1'),
                                                                                                        rounding=ROUND_HALF_UP)) + int(
                sender.Text) * 2)

    def IntervalCombo_Changed(self, sender, event):
        if not self.IntervalCombo.SelectedValue == None:
            self.NumberTextBlock.Text = str(int(
                Decimal((self.Sup_z - self.Inf_z) / Decimal(self.IntervalCombo.SelectedValue)).quantize(Decimal('1'),
                                                                                                        rounding=ROUND_HALF_UP)) + int(
                self.AdditionalTextBox.Text) * 2)

    def ListItemClick(self, sender, event):
        sender.SelectedItem = None

    def CheckBoxCheckd(self, sender, event):
        self.RoiListBox.IsEnabled = True

    def CheckBoxUncheckd(self, sender, event):
        self.RoiListBox.IsEnabled = False


def insert_report_point():
    patient = get_current("Patient")
    case = get_current("Case")
    plan = get_current("Plan")
    examination = plan.TreatmentCourse.TotalDose.OnDensity.FromExamination

    Pos = plan.BeamSets[0].Beams[0].Isocenter.Position
    target_list = []
    control_list = []
    point_list = []
    target_pos_z_list = []

    for BeamSet in plan.BeamSets:
        if not BeamSet.Prescription.PrimaryDosePrescription.OnStructure.Name in target_list:
            target_list.append(BeamSet.Prescription.PrimaryDosePrescription.OnStructure.Name)

    RoiTypeDict = {}
    for roi in case.PatientModel.RegionsOfInterest:
        if not roi.OrganData.OrganType in RoiTypeDict.keys():
            RoiTypeDict.setdefault(roi.OrganData.OrganType, Rois())
            RoiTypeDict[roi.OrganData.OrganType].Type = roi.OrganData.OrganType
            RoiTypeDict[roi.OrganData.OrganType].RoiPropertys.append(RoiProperty(roi.Name))
        else:
            RoiTypeDict[roi.OrganData.OrganType].RoiPropertys.append(RoiProperty(roi.Name))
        if roi.Type == 'Control':
            control_list.append(roi.Name)

    for key, value in RoiTypeDict.items():
        if key == 'OrganAtRisk':
            for roipro in value.RoiPropertys:
                roipro.View = True
        elif key == 'Target':
            for roipro in value.RoiPropertys:
                if roipro.ROI in target_list:
                    roipro.View = True

    robust_sup = []
    robust_inf = []

    for PlanOpt in plan.PlanOptimizations:
        try:
            robust_sup.append(PlanOpt.OptimizationParameters.RobustnessParameters.PositionUncertaintySuperior)
            robust_inf.append(PlanOpt.OptimizationParameters.RobustnessParameters.PositionUncertaintyInferior)
        except:
            break

    if len(control_list) == 0:
        for target in target_list:
            roi = case.PatientModel.StructureSets[examination.Name].RoiGeometries[target]
            for contour in roi.GetBoundingBox():  # PrimaryShape.Contours
                target_pos_z_list.append(contour.z)  # contour[0].z
        Sup_z = Decimal(max(target_pos_z_list) + max(robust_sup)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
        Inf_z = Decimal(min(target_pos_z_list) - max(robust_inf)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
        AddImageNumber = 3
        target = 'PrescriptionROI'
    else:
        for control in control_list:
            roi = case.PatientModel.StructureSets[examination.Name].RoiGeometries[control]
            for contour in roi.GetBoundingBox():  # PrimaryShape.Contours
                target_pos_z_list.append(contour.z)  # contour[0].z
        Sup_z = Decimal(max(target_pos_z_list)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
        Inf_z = Decimal(min(target_pos_z_list)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
        AddImageNumber = 1
        target = 'ControlROI'

    CTSliceThickness = examination.Series[0].ImageStack.SlicePositions[1] - \
                       examination.Series[0].ImageStack.SlicePositions[
                           0]
    ThicknessCoefficient = 2

    Thickness = Decimal(CTSliceThickness * ThicknessCoefficient).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)

    Slice_Number = int(Decimal((Sup_z - Inf_z) / Thickness).quantize(Decimal('1'),
                                                                     rounding=ROUND_HALF_UP)) + AddImageNumber * 2  # Sup3+Inf3

    form = ReportSettingForm(CTSliceThickness, ThicknessCoefficient, Thickness, Slice_Number, AddImageNumber,
                             RoiTypeDict,
                             target, Sup_z, Inf_z)
    form.ShowDialog()

    if form.DialogResult == False:
        sys.exit()

    for key, item in RoiTypeDict.items():
        print(key)
        for pro in item.RoiPropertys:
            print(' ' + pro.ROI + ' ' + str(pro.View))

    for i in range(form.Slice_Number):
        coor_dict = {'x': Pos.x, 'y': Pos.y,
                     'z': float(Sup_z) + float(form.Thickness) * (int(form.AdditionalTextBox.Text) - i)}
        point_list.append(coor_dict)

    plan.SetReportViewPositions(Coordinates=point_list)

    if form.ViewEnableCheckBox.IsChecked:
        for key, item in RoiTypeDict.items():
            for pro in item.RoiPropertys:
                patient.SetRoiVisibility(RoiName=pro.ROI, IsVisible=pro.View)


# test
if __name__ == '__main__':
    insert_report_point()
