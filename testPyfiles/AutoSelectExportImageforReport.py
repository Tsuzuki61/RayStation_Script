# Script recorded 24 Jul 2019

#   RayStation version: 6.2.0.7
#   Selected patient: ...

from connect import *
from decimal import *

case = get_current("Case")
plan = get_current("Plan")
examination = plan.TreatmentCourse.TotalDose.OnDensity.FromExamination

Pos = plan.BeamSets[0].Beams[0].Isocenter.Position
POI_list = [POI.Name for POI in case.PatientModel.PointsOfInterest]
target_list = []
point_list = []

for BeamSet in plan.BeamSets:
	if not BeamSet.Prescription.PrimaryDosePrescription.OnStructure.Name in target_list:
		target_list.append(BeamSet.Prescription.PrimaryDosePrescription.OnStructure.Name)

robust_sup = []
robust_inf = []
for PlanOpt in plan.PlanOptimizations:
	robust_sup.append(PlanOpt.OptimizationParameters.RobustnessParameters.PositionUncertaintySuperior)
	robust_inf.append(PlanOpt.OptimizationParameters.RobustnessParameters.PositionUncertaintyInferior)

target_pos_z_list = []
for target in target_list:
	roi = case.PatientModel.StructureSets[examination.Name].RoiGeometries[target]
	for contour in roi.PrimaryShape.Contours:
		target_pos_z_list.append(contour[0].z)

Sup_z = Decimal(max(target_pos_z_list) + max(robust_sup)).quantize(Decimal('0.1'),rounding = ROUND_HALF_UP)
Inf_z = Decimal(min(target_pos_z_list) - max(robust_inf)).quantize(Decimal('0.1'),rounding = ROUND_HALF_UP)

# Slice_Number = 10

# if not float(Decimal((Sup_z - Inf_z)/Slice_Number).quantize(Decimal('0.1'),rounding = ROUND_HALF_UP)) < 0.1:
	# Thickness = Decimal(0.1)
	# Slice_Number = int(Decimal((Sup_z - Inf_z)/0.1).quantize(Decimal('1'),rounding = ROUND_HALF_UP))
# else:
	# Thickness = Decimal((Sup_z - Inf_z)/Slice_Number).quantize(Decimal('0.1'),rounding = ROUND_HALF_UP)

Thickness = Decimal(examination.Series[0].ImageStack.SlicePositions[1] * 2 )
Slice_Number = int(Decimal((Sup_z - Inf_z)/Thickness).quantize(Decimal('1'),rounding = ROUND_HALF_UP)) + 3*2 #Sup3+Inf3

for i in range(Slice_Number):
	coor_dict = { 'x': Pos.x, 'y': Pos.y, 'z': float(Sup_z) +  float(Thickness)*(3 - i) }
	point_list.append(coor_dict)

plan.SetReportViewPositions(Coordinates=point_list)


