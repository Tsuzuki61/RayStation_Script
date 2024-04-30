from connect import *


def copyPlanAndSegmentReplace():
    case = get_current('Case')
    plan = get_current('Plan')
    new_plan_name = 'ReplaceSegmentsPlan'
    case.CopyPlan(PlanName=plan.Name, NewPlanName=new_plan_name, KeepBeamSetNames=True)
    copied_plan = case.TreatmentPlans[new_plan_name]
    for beamset in copied_plan.BeamSets:
        delete_beam_list = []
        copied_beam_data_list = []
        for beam in beamset.Beams:
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
                                      SpotTuneId=beam_segment.Spots.SpotTuneId)
                for beam_spot_position, beam_spot_weight in zip(beam_segment.Spots.Positions,
                                                                beam_segment.Spots.Weights):
                    tmp_segment.add_spot(x=beam_spot_position.x,
                                         y=beam_spot_position.y,
                                         weight=beam_spot_weight)
                copied_beam_data.add_segment(tmp_segment)
            copied_beam_data_list.append(copied_beam_data)
            delete_beam_list.append(beam.Name)
        for copied_beam in copied_beam_data_list:
            beamset.CreatePBSIonBeam(SnoutId=copied_beam.Snoutid,
                                     SpotTuneId=copied_beam.SpotTuneId,
                                     RangeShifter=copied_beam.RangeShifter,
                                     MinimumAirGap=copied_beam.MinimumAirGap,
                                     IsocenterData=beamset.CreateDefaultIsocenterData(
                                         Position={'x': copied_beam.isocenterData.x,
                                                   'y': copied_beam.isocenterData.y,
                                                   'z': copied_beam.isocenterData.z}
                                     ),
                                     Name=copied_beam.Name,
                                     Description=copied_beam.Description,
                                     GantryAngle=copied_beam.GantryAngle,
                                     CouchRotationAngle=copied_beam.CouchRotationAngle,
                                     CouchPitchAngle=copied_beam.CouchPitchAngle,
                                     CouchRollAngle=copied_beam.CouchRollAngle,
                                     CollimatorAngle=copied_beam.CollimatorAngle
                                     )
            setting_beam = beamset.Beams[copied_beam.Name]
            setting_beam.BeamMU = copied_beam.BeamMU
            for insert_segment in copied_beam.Segments:
                setting_beam.AddEnergyLayerWithSpots(Energy=insert_segment.Energy,
                                                     # X is shifted
                                                     SpotPositionsX=insert_segment.get_shiftedspotsPositionsX(1),
                                                     SpotPositionsY=insert_segment.get_spotsPositionsY(),
                                                     SpotWeights=insert_segment.get_spotsWeights())
            for insert_segment, setting_segment in zip(copied_beam.Segments, setting_beam.Segments):
                setting_segment.RelativeWeight = insert_segment.RelativeWeight
        beamset.ClearBeams(BeamNames=delete_beam_list)
        beamset.ComputeDose(DoseAlgorithm=beamset.AccurateDoseAlgorithm.DoseAlgorithm)


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
        self.Name = 'Shifted' + Name
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
    def __init__(self, energy, RelativeWeight, SpotTuneId):
        self.Energy = energy
        self.RelativeWeight = RelativeWeight
        self.SpotTuneId = SpotTuneId
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
