# Script recorded 12 Feb 2019

#   RayStation version: 6.2.0.7
#   Selected patient: ...

from connect import *


def create_QA_plan():
    plan = get_current("Plan")

    for beamset in plan.BeamSets:
        DoseGridCoo = beamset.FractionDose.InDoseGrid.VoxelSize
        beamset.CreateQAPlan(PhantomName="QA AbsoluteDose Phantom", PhantomId="00000010",
                             QAPlanName="QA_{}".format(beamset.DicomPlanLabel), IsoCenter={'x': 0, 'y': -40, 'z': 0},
                             DoseGrid={'x': DoseGridCoo.x, 'y': DoseGridCoo.y, 'z': DoseGridCoo.z}, GantryAngle=0,
                             CollimatorAngle=None, CouchRotationAngle=0, ComputeDoseWhenPlanIsCreated=True,
                             NumberOfMonteCarloHistories=None,
                             MotionSynchronizationTechniqueSettings={'DisplayName': None,
                                                                     'MotionSynchronizationSettings': None,
                                                                     'RespiratoryIntervalTime': None,
                                                                     'RespiratoryPhaseGatingDutyCycleTimePercentage': None},
                             RemoveCompensators=False, EnableDynamicTracking=False)

        # test
        if __name__ == '__main__':
            create_QA_plan()
