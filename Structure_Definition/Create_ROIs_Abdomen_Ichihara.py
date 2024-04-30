# Script recorded 2023/7/14
# Ichihara Create
#   RayStation version: 10A


from connect import *
import collections
import os
import re
import sys
import wpf
from System.Windows import *
from System.Windows.Controls import *
import time


class MessageBox(Window):
    def __init__(self):
        wpf.LoadComponent(self, os.path.join(os.path.dirname(__file__), './xaml/messagebox(OKonly).xaml'))
        # self.Topmost = True
        # Start up window at the center of the screen.
        self.WindowStartupLocation = WindowStartupLocation.CenterScreen
        self.Topmost = True
        self.Caption.Title = "Warning"
        self.msg.Text = "Please set PlanningCT as primary"

    def OK_Clicked(self, sender, event):
        self.DialogResult = True


class roi_property():
    def __init__(self, name, color, type):
        self.Name = name
        self.Color = color
        self.Type = type


class IsMarkerForm(Window):
    def __init__(self):
        wpf.LoadComponent(self, os.path.join(os.path.dirname(__file__), './xaml/IsMarkerForm.xaml'))
        # self.Topmost = True
        # Start up window at the center of the screen.
        self.WindowStartupLocation = WindowStartupLocation.CenterScreen
        self.Topmost = True

    def IsMarkerCombo_Changed(self, sender, event):
        if self.IsMarkerCombo.SelectedItem == 'With Marker':
            self.isMarker = True
        else:
            self.isMarker = False

    def OK_Clicked(self, sender, event):
        self.DialogResult = True

    def Cancel_Clicked(self, sender, event):
        sys.exit()


def create_rois_for_abdomen():
    start_time = time.time()
    patient = get_current("Patient")
    ID = patient.PatientID
    Pt_name = patient.Name
    case = get_current("Case")
    exam = get_current("Examination")

    if not 'PlanningCT' in exam.Name:
        msgbox = MessageBox()
        msgbox.ShowDialog()
        sys.exit()

    roi_list = [geometry.OfRoi.Name for geometry in case.PatientModel.StructureSets[exam.Name].RoiGeometries]

    Form = IsMarkerForm()

    Form.ShowDialog()
    if Form.DialogResult == False:
        sys.exit()

    roi_properties = []

    Body = roi_property("Body", "255,128, 255, 128", "Undefined")
    roi_properties.append(Body)

    Shell = roi_property("Shell", "255,128,255,255", "Undefined")
    roi_properties.append(Shell)

    if Form.isMarker == True:
        Marker_1_Ex = roi_property("Marker_1_Ex", "Red", "Marker")
        roi_properties.append(Marker_1_Ex),
        Marker_1_In = roi_property("Marker_1_In", "Blue", "Marker")
        roi_properties.append(Marker_1_In)
        Marker_2_Ex = roi_property("Marker_2_Ex", "250, 128, 114", "Marker")
        roi_properties.append(Marker_2_Ex)
        Marker_2_In = roi_property("Marker_2_In", "64, 224, 208", "Marker")
        roi_properties.append(Marker_2_In)
    for i in range(0,90,10):
        Marker_1_i = roi_property("Marker_1_i", "128, 0, 128", "Marker")
        roi_properties.append(Marker_1_i)
        Marker_2_i = roi_property("Marker_2_i", "72, 61, 139", "Marker")
        roi_properties.append(Marker_2_i)

    Artifact = roi_property("Artifact", "255,255,255,128", "Undefined")
    roi_properties.append(Artifact)

    Gas = roi_property("Gas", "255, 128, 128", "Undefined")
    roi_properties.append(Gas)

    VB_Target = roi_property("VB_Target", "184, 134, 11", "Undefined")
    roi_properties.append(VB_Target)

    SpinalCord = roi_property("SpinalCord", "135, 206, 255", "Organ")
    roi_properties.append(SpinalCord)

    Duodenum = roi_property('Duodenum', "0, 250, 154", "Organ")
    roi_properties.append(Duodenum)

    Stomach = roi_property('Stomach', "240, 230, 140", "Organ")
    roi_properties.append(Stomach)

    Kidney_R = roi_property('Kidney_R', "220, 170, 145", "Organ")
    roi_properties.append(Kidney_R)

    Kidney_L = roi_property('Kidney_L', "220, 170, 145", "Organ")
    roi_properties.append(Kidney_L)

    GTV = roi_property('GTV_', '255, 0, 0', "GTV")
    roi_properties.append(GTV)
    CTV = roi_property('CTV_', '255, 0, 128, 255', "CTV")
    roi_properties.append(CTV)

    # Create ROI
    # Extermnal ROI
    if not "External" in roi_list:
        external = case.PatientModel.CreateRoi(Name="External", Color="Green", Type="External", TissueName="",
                                               RbeCellTypeName=None, RoiMaterial=None)
    else:
        external = case.PatientModel.RegionsOfInterest["External"]

    external.CreateExternalGeometry(Examination=exam, ThresholdLevel=-250)


    for roi_p in roi_properties:
        if roi_p.Name not in roi_list:
            case.PatientModel.CreateRoi(Name=roi_p.Name, Color=roi_p.Color, Type=roi_p.Type, TissueName=None,
                                        RbeCellTypeName=None, RoiMaterial=None)


    # if len(lst) != 0:
    #     for ctv in lst:
    #         if not re.sub('(CTV|Ctv)', 'Virtual_PTV', ctv) in roi_list:
    #             retval_0 = case.PatientModel.CreateRoi(Name=re.sub('(CTV|Ctv)', 'Virtual_PTV', ctv),
    #                                                    Color="255, 128, 255", Type="Ptv", TissueName=None,
    #                                                    RbeCellTypeName=None, RoiMaterial=None)
    #             if Form.isMarker == True:
    #                 retval_0.SetMarginExpression(SourceRoiName=ctv,
    #                                              MarginSettings={'Type': "Expand", 'Superior': 0.3, 'Inferior': 0.3,
    #                                                              'Anterior': 0.3, 'Posterior': 0.2, 'Right': 0.6,
    #                                                              'Left': 0.6})
    #             else:
    #                 if '1' in ctv:
    #                     retval_0.SetMarginExpression(SourceRoiName=ctv,
    #                                                  MarginSettings={'Type': "Expand", 'Superior': 0.5, 'Inferior': 0.5,
    #                                                                  'Anterior': 0.5, 'Posterior': 0.3, 'Right': 0.6,
    #                                                                  'Left': 0.6})
    #                 elif '2' in ctv:
    #                     retval_0.SetMarginExpression(SourceRoiName=ctv,
    #                                                  MarginSettings={'Type': "Expand", 'Superior': 0.3, 'Inferior': 0.3,
    #                                                                  'Anterior': 0.3, 'Posterior': 0.2, 'Right': 0.6,
    #                                                                  'Left': 0.6})
    #             retval_0.UpdateDerivedGeometry(Examination=exam, Algorithm="Auto")
    #
    #         if not re.sub('(CTV|Ctv)', 'Evaluative_PTV', ctv) in roi_list:
    #             retval_1 = case.PatientModel.CreateRoi(Name=re.sub('(CTV|Ctv)', 'Evaluative_PTV', ctv), Color="Magenta",
    #                                                    Type="Ptv", TissueName=None, RbeCellTypeName=None,
    #                                                    RoiMaterial=None)
    #             if Form.isMarker == True:
    #                 retval_1.SetMarginExpression(SourceRoiName=ctv,
    #                                              MarginSettings={'Type': "Expand", 'Superior': 0.3, 'Inferior': 0.3,
    #                                                              'Anterior': 0.3, 'Posterior': 0.2, 'Right': 0.3,
    #                                                              'Left': 0.3})
    #             else:
    #                 if '1' in ctv:
    #                     retval_1.SetMarginExpression(SourceRoiName=ctv,
    #                                                  MarginSettings={'Type': "Expand", 'Superior': 0.5, 'Inferior': 0.5,
    #                                                                  'Anterior': 0.5, 'Posterior': 0.3, 'Right': 0.5,
    #                                                                  'Left': 0.5})
    #                 elif '2' in ctv:
    #                     retval_1.SetMarginExpression(SourceRoiName=ctv,
    #                                                  MarginSettings={'Type': "Expand", 'Superior': 0.3, 'Inferior': 0.3,
    #                                                                  'Anterior': 0.3, 'Posterior': 0.2, 'Right': 0.3,
    #                                                                  'Left': 0.3})
    #             retval_1.UpdateDerivedGeometry(Examination=exam, Algorithm="Auto")


# test
if __name__ == '__main__':
    create_rois_for_abdomen()
