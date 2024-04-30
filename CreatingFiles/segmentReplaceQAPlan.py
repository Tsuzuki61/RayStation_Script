from connect import *


def copyPlanAndSegmentReplace():
    case = get_current('Case')
    plan = get_current('Plan')
    beamset = get_current('BeamSet')
    for veri_plan in plan.VerificationPlans:
        if veri_plan.ForTreatmentPlan.BeamSets[0].DicomPlanLabel == beamset.DicomPlanLabel:
            iso_name = veri_plan.BeamSet.GetOrderedIsocenters()[0]
            iso_data = veri_plan.BeamSet.GetIsocenterData(Name=iso_name)

    new_QAplan_name = 'shiftQA'
    DoseGridCoo = beamset.FractionDose.InDoseGrid.VoxelSize
    beamset.CreateQAPlan(PhantomName="QA AbsoluteDose Phantom", PhantomId="00000010",
                         QAPlanName=new_QAplan_name,
                         IsoCenter={'x': iso_data['Position']['x'],
                                    'y': iso_data['Position']['y'],
                                    'z': iso_data['Position']['z']},
                         DoseGrid={'x': DoseGridCoo.x, 'y': DoseGridCoo.y, 'z': DoseGridCoo.z}, GantryAngle=0,
                         CollimatorAngle=None, CouchRotationAngle=0, ComputeDoseWhenPlanIsCreated=True,
                         NumberOfMonteCarloHistories=None,
                         MotionSynchronizationTechniqueSettings={'DisplayName': None,
                                                                 'MotionSynchronizationSettings': None,
                                                                 'RespiratoryIntervalTime': None,
                                                                 'RespiratoryPhaseGatingDutyCycleTimePercentage': None},
                         RemoveCompensators=False, EnableDynamicTracking=False)
    for veri_plan in plan.VerificationPlans:
        if veri_plan.BeamSet.DicomPlanLabel == new_QAplan_name:
            copied_plan = veri_plan
            break
    Veri_beamset = copied_plan.BeamSet
    delete_beam_list = []
    copied_beam_data_list = []
    for beam in Veri_beamset.Beams:
        copied_beam_data = beam_data(MU=beam.BeamMU,
                                     Snoutid=beam.SnoutId,
                                     MinimumAirGap=beam.GetMinAirGap(),
                                     MetersetRateSetting=beam.MetersetRateSettingId,
                                     isocenterData=beam.Isocenter.Position,
                                     Name=beam.Name,
                                     Description=beam.Description,
                                     GantryAngle=beam.GantryAngle,
                                     CouchRotationAngle=beam.CouchRotationAngle,
                                     CouchPitchAngle=beam.CouchPitchAngle,
                                     CouchRollAngle=beam.CouchRollAngle,
                                     CollimatorAngle=beam.InitialCollimatorAngle,
                                     RangeShifter=beam.RangeShifterId
                                     )
        for beam_segment in beam.Segments:
            tmp_segment = Segment(energy=beam_segment.NominalEnergy,
                                  RelativeWeight=beam_segment.RelativeWeight,
                                  SpotTuneId=beam_segment.Spots.SpotTuneId,
                                  LeafPositions=beam_segment.LeafPositions)
            for beam_spot_position, beam_spot_weight in zip(beam_segment.Spots.Positions,
                                                            beam_segment.Spots.Weights):
                tmp_segment.add_spot(x=beam_spot_position.x,
                                     y=beam_spot_position.y,
                                     weight=beam_spot_weight)
            copied_beam_data.add_segment(tmp_segment)
        copied_beam_data_list.append(copied_beam_data)

    for copied_beam in copied_beam_data_list:
        setting_beam = Veri_beamset.Beams[copied_beam.Name]
        setting_beam.BeamMU = copied_beam.BeamMU
        setting_beam.AddEnergyLayerWithSpots(Energy=99,
                                             # X is shifted
                                             SpotPositionsX=[0],
                                             SpotPositionsY=[0],
                                             SpotWeights=[1])
        for delete_segment in setting_beam.Segments:
            if delete_segment.NominalEnergy != 99:
                delete_segment.RemoveEnergyLayer()
            elif delete_segment.Spots.Weights[0] != 1:
                delete_segment.RemoveEnergyLayer()
        for insert_segment in copied_beam.Segments:
            setting_beam.AddEnergyLayerWithSpots(Energy=insert_segment.Energy,
                                                 # X is shifted
                                                 SpotPositionsX=insert_segment.get_shiftedspotsPositionsX(1),
                                                 SpotPositionsY=insert_segment.get_spotsPositionsY(),
                                                 SpotWeights=insert_segment.get_spotsWeights())
        for delete_segment in setting_beam.Segments:
            if delete_segment.NominalEnergy == 99 and delete_segment.Spots.Weights[0] == 1:
                delete_segment.RemoveEnergyLayer()
                break
        for insert_segment, setting_segment in zip(copied_beam.Segments, setting_beam.Segments):
            setting_segment.RelativeWeight = insert_segment.RelativeWeight
            setting_segment.LeafPositions = insert_segment.LeafPositions  # This may be a mistake!
        # setting_beam.EditBeamLeafPositions(LeafPositions=[insert_segment.LeafPositions for insert_segment in copied_beam.Segments])
    Veri_beamset.ComputeDose(DoseAlgorithm=Veri_beamset.AccurateDoseAlgorithm.DoseAlgorithm)


class beam_data:
    def __init__(self,
                 MU,
                 Snoutid,
                 MinimumAirGap,
                 MetersetRateSetting,
                 isocenterData,
                 Name,
                 Description,
                 GantryAngle,
                 CouchRotationAngle,
                 CouchPitchAngle,
                 CouchRollAngle,
                 CollimatorAngle,
                 RangeShifter
                 ):
        self.BeamMU = MU
        self.Segments = []
        self.Snoutid = Snoutid
        self.MinimumAirGap = MinimumAirGap
        self.MetersetRateSetting = MetersetRateSetting
        self.isocenterData = isocenterData
        self.Name = Name
        self.Description = Description
        self.GantryAngle = GantryAngle
        self.CouchRotationAngle = CouchRotationAngle
        self.CouchPitchAngle = CouchPitchAngle
        self.CouchRollAngle = CouchRollAngle
        self.CollimatorAngle = CollimatorAngle
        self.RangeShifter = RangeShifter
        self.SpotTuneId = None

    def add_segment(self, segment):
        self.Segments.append(segment)
        if len(self.Segments) == 1:
            self.SpotTuneId = segment.SpotTuneId


class Segment:
    def __init__(self, energy, RelativeWeight, SpotTuneId, LeafPositions):
        self.Energy = energy
        self.RelativeWeight = RelativeWeight
        self.SpotTuneId = SpotTuneId
        self.LeafPositions = LeafPositions
        self.Spots = []

    def add_spot(self, x, y, weight):
        self.Spots.append(Spot(x, y, weight))

    def get_spotsPositionsX(self):
        return [spot.x for spot in self.Spots]

    def get_spotsPositionsY(self):
        return [spot.y for spot in self.Spots]

    def get_spotsWeights(self):
        return [spot.weight for spot in self.Spots]

    def get_shiftedspotsPositionsX(self, shift):
        return [spot.x + shift for spot in self.Spots]


class Spot:
    def __init__(self, x, y, weight):
        self.x = x
        self.y = y
        self.weight = weight


if __name__ == "__main__":
    copyPlanAndSegmentReplace()
