# Script recorded 24 Jul 2019

#   RayStation version: 6.2.0.7
#   Selected patient: ...

from connect import *
from decimal import *

case = get_current("Case")
plan = get_current("Plan")
examination = plan.TreatmentCourse.TotalDose.OnDensity.FromExamination

coor_list=[]
Iso = plan.BeamSets[0].Beams[0].Isocenter.Position
POI_list = [POI.Name for POI in case.PatientModel.PointsOfInterest]
if not "StartPoint" and "EndPoint" in POI_list:
	
Start_Poi = case.PatientModel.StructureSets[examination.Name].PoiGeometries['StartPoint'].Point
End_Poi = case.PatientModel.StructureSets[examination.Name].PoiGeometries['EndPoint'].Point

Slice_Number = 10

Thickness = Decimal((Start_Poi.z - End_Poi.z)/Slice_Number).quantize(Decimal('0.1'),rounding = ROUND_HALF_UP)
for i in range(Slice_Number):
	coor_dict = { 'x': Start_Poi.x, 'y': Start_Poi.y, 'z': Start_Poi.z - float(Thickness)*i }
	coor_list.append(coor_dict)

plan.SetReportViewPositions(Coordinates=coor_list)
#plan.SetReportViewPositions(Coordinates=[{ 'x': -0.6, 'y': -20, 'z': -16.5 }])

