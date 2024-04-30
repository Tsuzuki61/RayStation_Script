# Script recorded 12 Nov 2018

#   RayStation version: 6.2.0.7
#   Selected patient: ...

from connect import *
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__)))
from RayForm import *
from System.Windows.Forms import *
from ctypes import *


def create_rois_for_deform_dose():
    case = get_current("Case")
    examination = get_current("Examination")
    patient = get_current("Patient")

    ROI_Names = [ROI.OfRoi.Name for ROI in case.PatientModel.StructureSets[examination.Name].RoiGeometries]

    msgbox = windll.user32.MessageBoxW

    if not "PelvicBones" in ROI_Names:
        msgbox(None, 'There is no ROI named "PelvicBones"', 'Warning', 0x0000040)
        sys.exit()

    form = DeformForm(case)
    Application.Run(form)

    if form.close_bool == False:
        sys.exit()

    if form.shift_value == "":
        msgbox(None, 'Shift value is not entered', 'Caution', 0x0000040)
        sys.exit()

    if case.PatientModel.StructureSets[form.planning_exam_name].RoiGeometries['PelvicBones'].PrimaryShape == None:
        msgbox(None, 'There is no Geometry "PelvicBones"', "Warning", 0x0000040)
        sys.exit()

    # --------------deformSetting------------------------
    shift = float(form.shift_value)  # cm
    Deform_List = ["DeformSup{:0}mm".format(shift * 10), "DeformInf{:0}mm".format(shift * 10),
                   "DeformAnt{:0}mm".format(shift * 10), "DeformPos{:0}mm".format(shift * 10)]
    shift_dic = {
        "DeformSup{:0}mm".format(shift * 10): {"x": 0, "y": 0, "z": shift},
        "DeformInf{:0}mm".format(shift * 10): {"x": 0, "y": 0, "z": -shift},
        "DeformAnt{:0}mm".format(shift * 10): {"x": 0, "y": -shift, "z": 0},
        "DeformPos{:0}mm".format(shift * 10): {"x": 0, "y": shift, "z": 0}
    }
    # ---------------------------------------------------
    ExcludeFromExportRois = []
    if not "DeformBone" in ROI_Names:
        retval_0 = case.PatientModel.CreateRoi(Name="DeformBone", Color="Teal", Type="Undefined", TissueName=None,
                                               RbeCellTypeName=None, RoiMaterial=None)
    else:
        retval_0 = case.PatientModel.RegionsOfInterest["DeformBone"]

    ExcludeFromExportRois.append(retval_0.Name)
    retval_0.CreateAlgebraGeometry(Examination=case.Examinations[form.planning_exam_name], Algorithm="Auto",
                                   ExpressionA={'Operation': "Union",
                                                'SourceRoiNames': ["Femur_L", "Femur_R"],
                                                'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0,
                                                                   'Anterior': 0, 'Posterior': 0, 'Right': 0,
                                                                   'Left': 0}},
                                   ExpressionB={'Operation': "Union", 'SourceRoiNames': ["PelvicBones"],
                                                'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0,
                                                                   'Anterior': 0, 'Posterior': 0, 'Right': 0,
                                                                   'Left': 0}}, ResultOperation="Union",
                                   ResultMarginSettings={'Type': "Expand", 'Superior': 0.1, 'Inferior': 0.1,
                                                         'Anterior': 0.1, 'Posterior': 0.1, 'Right': 0.1, 'Left': 0.1})
    retval_0.CreateAlgebraGeometry(Examination=case.Examinations[form.deform_exam_name], Algorithm="Auto",
                                   ExpressionA={'Operation': "Union",
                                                'SourceRoiNames': ["Femur_L", "Femur_R"],
                                                'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0,
                                                                   'Anterior': 0, 'Posterior': 0, 'Right': 0,
                                                                   'Left': 0}},
                                   ExpressionB={'Operation': "Union", 'SourceRoiNames': ["PelvicBones"],
                                                'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0,
                                                                   'Anterior': 0, 'Posterior': 0, 'Right': 0,
                                                                   'Left': 0}}, ResultOperation="Union",
                                   ResultMarginSettings={'Type': "Expand", 'Superior': 0.1, 'Inferior': 0.1,
                                                         'Anterior': 0.1, 'Posterior': 0.1, 'Right': 0.1, 'Left': 0.1})

    for roi_name, coo_xyz in shift_dic.items():
        if not roi_name in ROI_Names:
            tmpROI = case.PatientModel.CreateRoi(Name=roi_name, Color="Teal", Type="Undefined", TissueName=None,
                                                 RbeCellTypeName=None, RoiMaterial=None)
        else:
            tmpROI = case.PatientModel.RegionsOfInterest[roi_name]
        ExcludeFromExportRois.append(tmpROI.Name)
        tmpROI.CreateAlgebraGeometry(Examination=case.Examinations[form.planning_exam_name], Algorithm="Auto",
                                     ExpressionA={'Operation': "Union", 'SourceRoiNames': ["DeformBone"],
                                                  'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0,
                                                                     'Anterior': 0, 'Posterior': 0, 'Right': 0,
                                                                     'Left': 0}},
                                     ExpressionB={'Operation': "Union", 'SourceRoiNames': [],
                                                  'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0,
                                                                     'Anterior': 0, 'Posterior': 0, 'Right': 0,
                                                                     'Left': 0}}, ResultOperation="None",
                                     ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0,
                                                           'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        tmpROI.CreateAlgebraGeometry(Examination=case.Examinations[form.deform_exam_name], Algorithm="Auto",
                                     ExpressionA={'Operation': "Union", 'SourceRoiNames': ["DeformBone"],
                                                  'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0,
                                                                     'Anterior': 0, 'Posterior': 0, 'Right': 0,
                                                                     'Left': 0}},
                                     ExpressionB={'Operation': "Union", 'SourceRoiNames': [],
                                                  'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0,
                                                                     'Anterior': 0, 'Posterior': 0, 'Right': 0,
                                                                     'Left': 0}}, ResultOperation="None",
                                     ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0,
                                                           'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})

        case.PatientModel.StructureSets[form.deform_exam_name].RoiGeometries[roi_name].OfRoi.TransformROI3D(
            Examination=case.Examinations[form.deform_exam_name],
            TransformationMatrix={'M11': 1, 'M12': 0, 'M13': 0, 'M14': coo_xyz["x"],
                                  'M21': 0, 'M22': 1, 'M23': 0, 'M24': coo_xyz["y"],
                                  'M31': 0, 'M32': 0, 'M33': 1, 'M34': coo_xyz["z"],
                                  'M41': 0, 'M42': 0, 'M43': 0, 'M44': 1})
        patient.SetRoiVisibility(RoiName=roi_name, IsVisible=False)
    case.PatientModel.ToggleExcludeFromExport(ExcludeFromExport=True,
                                              RegionOfInterests=ExcludeFromExportRois,
                                              PointsOfInterests=[])
    # CompositeAction ends


# test
if __name__ == '__main__':
    create_rois_for_deform_dose()
