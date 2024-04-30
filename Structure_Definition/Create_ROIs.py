# Script recorded 08 Nov 2018

#   RayStation version: 6.2.0.7
#   Selected patient: ...
# 6/24 PTV margin is changed
# 2023/7/3 Shell ROI deleated Ichihara
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


def create_rois_for_prostate():
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

    # Shell = roi_property("Shell", "255,128,255,255", "Undefined")
    # roi_properties.append(Shell)
    if Form.isMarker == True:
        Marker_1 = roi_property("Marker_1", "Red", "Marker")
        roi_properties.append(Marker_1)
        Marker_2 = roi_property("Marker_2", "Blue", "Marker")
        roi_properties.append(Marker_2)

    Artifact = roi_property("Artifact", "255,255,255,128", "Undefined")
    roi_properties.append(Artifact)

    Gas = roi_property("Gas", "255, 128, 128", "Undefined")
    roi_properties.append(Gas)

    PelVic_Bones = roi_property("PelvicBones", "255, 0, 128", "Organ")
    roi_properties.append(PelVic_Bones)

    L_Intestine = roi_property('L Intestine', "255, 128, 64", "Organ")
    roi_properties.append(L_Intestine)

    S_Intestine = roi_property('S Intestine', "Olive", "Organ")
    roi_properties.append(S_Intestine)

    CTV = roi_property('CTV1_', '255, 0, 128, 255', "Ctv")
    roi_properties.append(CTV)

    # Create ROI
    # Extermnal ROI
    if not "External" in roi_list:
        external = case.PatientModel.CreateRoi(Name="External", Color="Green", Type="External", TissueName="",
                                               RbeCellTypeName=None, RoiMaterial=None)
    else:
        external = case.PatientModel.RegionsOfInterest["External"]

    external.CreateExternalGeometry(Examination=exam, ThresholdLevel=-250)

    # MBS ROIs
    case.PatientModel.MBSAutoInitializer(
        MbsRois=[{'CaseType': "PelvicMale", 'ModelName': "Prostate", 'RoiName': "Prostate", 'RoiColor': "244, 164, 96"},
                 {'CaseType': "PelvicMale", 'ModelName': "Bladder", 'RoiName': "Bladder", 'RoiColor': "255, 255, 0"},
                 {'CaseType': "PelvicMale", 'ModelName': "FemoralHead (Left)", 'RoiName': "FemoralHead (Left)",
                  'RoiColor': "0, 255, 127"},
                 {'CaseType': "PelvicMale", 'ModelName': "FemoralHead (Right)", 'RoiName': "FemoralHead (Right)",
                  'RoiColor': "23, 107, 43"},
                 {'CaseType': "PelvicMale", 'ModelName': "Rectum", 'RoiName': "Rectum", 'RoiColor': "139, 69, 19"}],
        CreateNewRois=True, Examination=exam, UseAtlasBasedInitialization=True)

    case.PatientModel.AdaptMbsMeshes(Examination=exam,
                                     RoiNames=["Prostate", "Bladder", "FemoralHead (Left)", "FemoralHead (Right)",
                                               "Rectum"], CustomStatistics=None, CustomSettings=None)

    for roi_p in roi_properties:
        if roi_p.Name not in roi_list:
            case.PatientModel.CreateRoi(Name=roi_p.Name, Color=roi_p.Color, Type=roi_p.Type, TissueName=None,
                                        RbeCellTypeName=None, RoiMaterial=None)
    # Rename ROI
    roi_list = [geometry.OfRoi.Name for geometry in case.PatientModel.StructureSets[exam.Name].RoiGeometries]
    lst = [s for s in roi_list if re.match('^FemoralHead \((Left|Right)\)$', s)]
    for roi in lst:
        tmpROI = case.PatientModel.RegionsOfInterest[roi]
        if 'Left' in roi:
            tmpROI.Name = 'Femur_L'
        elif 'Right' in roi:
            tmpROI.Name = 'Femur_R'
    elapsed_time = time.time() - start_time
    print("Elapsed time is {}sec".format(elapsed_time))

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
    create_rois_for_prostate()
