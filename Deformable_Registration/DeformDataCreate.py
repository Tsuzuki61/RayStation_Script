# Script recorded 04 Dec 2018

#   RayStation version: 6.2.0.7
#   Selected patient: ...
# use Ironpython

from connect import *
import os
import sys

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), '../common_processing'))
from CommonModules import create_new_patient_folder
# Import custom from module
from RayForm import *
import clr

clr.AddReference('System.Windows.Forms')
from System.Windows.Forms import *


def deform_data_create():
    """this function creates deform data and exports it as mhd file"""
    # connection with RayStation
    case = get_current("Case")
    plan = get_current("Plan")

    regi_group = [regi_groups.Name for regi_groups in case.PatientModel.StructureRegistrationGroups]

    # Retrieve Deform ROI
    deform_roi_list = []
    for roi in case.PatientModel.RegionsOfInterest:
        if "Deform" in roi.Name:
            if not roi.Name == "DeformBone":
                deform_roi_list.append(roi.Name)

    # Create an instance of the custom form
    form = DeformRegistrationCreateForm(case)
    Application.Run(form)

    if form.close_bool == False:
        sys.exit()
    # Retrieve information from the form
    ref_CT = form.reference_name
    tag_CT = form.target_name

    # Create registration group
    RGNameList = []
    for deform_roi in deform_roi_list:
        tmpRGName = plan.Name + '_' + deform_roi
        RGNameList.append(tmpRGName)
        if not tmpRGName in regi_group:
            case.PatientModel.CreateHybridDeformableRegistrationGroup(RegistrationGroupName=tmpRGName,
                                                                      ReferenceExaminationName=ref_CT,
                                                                      TargetExaminationNames=[tag_CT],
                                                                      ControllingRoiNames=[deform_roi],
                                                                      ControllingPoiNames=[],
                                                                      FocusRoiNames=[],
                                                                      AlgorithmSettings={'NumberOfResolutionLevels': 3,
                                                                                         'InitialResolution': {'x': 0.5,
                                                                                                               'y': 0.5,
                                                                                                               'z': 0.5},
                                                                                         'FinalResolution': {'x': 0.25,
                                                                                                             'y': 0.25,
                                                                                                             'z': 0.25},
                                                                                         'InitialGaussianSmoothingSigma': 2,
                                                                                         'FinalGaussianSmoothingSigma': 0.333333333333333,
                                                                                         'InitialGridRegularizationWeight': 400,
                                                                                         'FinalGridRegularizationWeight': 400,
                                                                                         'ControllingRoiWeight': 0.5,
                                                                                         'ControllingPoiWeight': 0.1,
                                                                                         'MaxNumberOfIterationsPerResolutionLevel': 1000,
                                                                                         'ImageSimilarityMeasure': "CorrelationCoefficient",
                                                                                         'DeformationStrategy': "Default",
                                                                                         'ConvergenceTolerance': 1E-05})

    # Create the patient folder
    file_path = create_new_patient_folder()

    os.chdir("M:\\")
    if not os.path.isdir(os.getcwd() + file_path + '\\DeformData'):
        os.mkdir(os.getcwd() + file_path + '\\DeformData')

    os.chdir(os.getcwd() + file_path + '\\DeformData')

    # Create mhd file
    for SRG in case.PatientModel.StructureRegistrationGroups:
        if SRG.Name in RGNameList:
            for DSR in SRG.DeformableStructureRegistrations:
                DSR.ExportDeformedMetaImage(MetaFileName=os.getcwd() + '\\' + DSR.Name + '.mhd')
                if not os.path.isdir(os.getcwd() + '\\' + DSR.Name):
                    os.mkdir(os.getcwd() + '\\' + DSR.Name)


# test
if __name__ == '__main__':
    deform_data_create()
