# Script recorded 11 Apr 2020

#   RayStation version: 7.0.0.19
#   Selected patient: ...

from connect import *

case = get_current("Case")

case.GenerateOrganMotionExaminationGroup(SourceExaminationName="PlanningCT_20200409",
                                         ExaminationGroupName="Simulated organ motion", MotionRoiName="DeformBone",
                                         FixedRoiNames=["CTV_7800"],
                                         OrganUncertaintySettings={'Superior': 0.5, 'Inferior': 0.5, 'Anterior': 0.5,
                                                                   'Posterior': 0.5, 'Right': 0, 'Left': 0},
                                         OnlySimulateMaxOrganMotion=False)
