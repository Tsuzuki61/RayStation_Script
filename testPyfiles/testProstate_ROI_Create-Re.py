# Script recorded 12 Nov 2018

#   RayStation version: 6.2.0.7
#   Selected patient: ...

from connect import *
import sys
sys.path.append("F:\Proton\RayStation\Script\create file")
from RayForm import *
from System.Windows.Forms import *
from ctypes import *

case = get_current("Case")
examination = get_current("Examination")

ROI_Names = [ROI.OfRoi.Name for ROI in case.PatientModel.StructureSets[examination.Name].RoiGeometries]

msgbox = windll.user32.MessageBoxW

if not "Illiac Bone" in ROI_Names:
	msgbox(None,'There is no ROI named "Illiac Bone"','Warning',0x0000040)
	sys.exit()


form = DeformForm(case)
Application.Run(form)

if form.close_bool ==False:
	sys.exit()
	

if form.shift_value =="":
	msgbox(None,'Shift value is not entered','Caution',0x0000040)
	sys.exit()

if case.PatientModel.StructureSets[form.planning_exam_name].RoiGeometries['Illiac Bone'].PrimaryShape == None:
	msgbox(None,'There is no Geometry "Illiac Bone"',"Warning",0x0000040)
	sys.exit()



shift = float(form.shift_value) #cm
Deform_List =["DeformSupReplan{:0}mm".format(shift*10),"DeformInfReplan{:0}mm".format(shift*10),"DeformAntReplan{:0}mm".format(shift*10),"DeformPosReplan{:0}mm".format(shift*10)]
shift_dic = {
"DeformSupReplan{:0}mm".format(shift*10):{"x":0,"y":0,"z":shift},
"DeformInfReplan{:0}mm".format(shift*10):{"x":0,"y":0,"z":-shift},
"DeformAntReplan{:0}mm".format(shift*10):{"x":0,"y":-shift,"z":0},
"DeformPosReplan{:0}mm".format(shift*10):{"x":0,"y":shift,"z":0}
}


if not "DeformBoneReplan" in ROI_Names:
	retval_0 = case.PatientModel.CreateRoi(Name="DeformBoneReplan", Color="Teal", Type="Undefined", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
	retval_0.ExcludeFromExport = True
	retval_0.CreateAlgebraGeometry(Examination=case.Examinations[form.planning_exam_name], Algorithm="Auto", ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["FemoralHead (Left)", "FemoralHead (Right)"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': ["Illiac Bone"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="Union", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0.1, 'Inferior': 0.1, 'Anterior': 0.1, 'Posterior': 0.1, 'Right': 0.1, 'Left': 0.1 })
	retval_0.CreateAlgebraGeometry(Examination=case.Examinations[form.deform_exam_name], Algorithm="Auto", ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["FemoralHead (Left)", "FemoralHead (Right)"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': ["Illiac Bone"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="Union", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0.1, 'Inferior': 0.1, 'Anterior': 0.1, 'Posterior': 0.1, 'Right': 0.1, 'Left': 0.1 })
	
	
for roi_name,coo_xyz in shift_dic.items():
	tmpROI = case.PatientModel.CreateRoi(Name=roi_name, Color="Teal", Type="Undefined", TissueName=None, RbeCellTypeName=None, RoiMaterial=None) 
	tmpROI.ExcludeFromExport = True
	tmpROI.CreateAlgebraGeometry(Examination=case.Examinations[form.planning_exam_name], Algorithm="Auto", ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["DeformBone"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
	tmpROI.CreateAlgebraGeometry(Examination=case.Examinations[form.deform_exam_name], Algorithm="Auto", ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["DeformBone"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
	
	case.PatientModel.StructureSets[form.deform_exam_name].RoiGeometries[roi_name].OfRoi.TransformROI3D(Examination=case.Examinations[form.deform_exam_name],TransformationMatrix={'M11':1, 'M12':0, 'M13':0, 'M14':coo_xyz["x"],'M21':0, 'M22':1, 'M23':0, 'M24':coo_xyz["y"],'M31':0, 'M32':0, 'M33':1, 'M34':coo_xyz["z"],'M41':0, 'M42':0, 'M43':0, 'M44':1})

		
 # CompositeAction ends 


