# Script recorded 24 Jul 2019

#   RayStation version: 6.2.0.7
#   Selected patient: ...

from connect import *

case = get_current("Case")
plan = get_current("Plan")
examination = plan.TreatmentCourse.TotalDose.OnDensity.FromExamination

Pos = plan.BeamSets[0].Beams[0].Isocenter.Position
retval_0 = case.PatientModel.CreatePoi(Examination=examination, Point={ 'x': Pos.x, 'y': Pos.y, 'z': Pos.z+3 }, Volume=0, Name="StartPoint", Color="Lime", Type="Control")

retval_1 = case.PatientModel.CreatePoi(Examination=examination, Point={ 'x': Pos.x, 'y': Pos.y, 'z': Pos.z-3 }, Volume=0, Name="EndPoint", Color="Lime", Type="Control")

