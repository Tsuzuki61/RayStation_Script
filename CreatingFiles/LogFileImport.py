import sys
import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from connect import *

sys.path.append(os.path.dirname(__file__))
from LogFileAnalysis import create_record_and_specif_dataframe, RangeToEnergy


def copyPlanAndImportLogFileData():
    # prostate only
    # Only one beam


    # root = tk.Tk()
    # root.withdraw()
    # directory = filedialog.askdirectory(initialdir=os.path.expanduser('~/Desktop'))
    directory = r"M:\Script\create file\CreatingFiles\20230410_074807_527.PBS.2.8_DailyQAAbsoluteDose"
    if directory == '':
        return
    df, _ = create_record_and_specif_dataframe(directory_path=directory)
    energy_group_df = df.groupby('ENERGY')
    # Copy Plan
    case = get_current('Case')
    plan = get_current('Plan')
    new_plan_name = '{}_LogSegments'.format(plan.Name)
    case.CopyPlan(PlanName=plan.Name, NewPlanName=new_plan_name, KeepBeamSetNames=True)
    copied_plan = case.TreatmentPlans[new_plan_name]
    # get beamset data
    for beamset in copied_plan.BeamSets:
        delete_beam_list = []
        copied_beam_data_list = []
        for beam in beamset.Beams:
            copied_beam_data = beam_data(MU=df['MU'].sum(),
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
            # pandas dataframe to Segment Class
            segment_SpotTuneId = ''
            for beam_segment in beam.Segments:
                if segment_SpotTuneId != beam_segment.Spots.SpotTuneId:
                    segment_SpotTuneId = beam_segment.Spots.SpotTuneId
            for energy, positions_df in energy_group_df:
                tmp_segment = Segment(energy=energy,
                                      SpotTuneId=segment_SpotTuneId)
                for position_x, position_y, mu_weight in zip(positions_df['ISO_X_POSITION'],
                                                             positions_df['ISO_Y_POSITION'],
                                                             positions_df['MU_RATE']):
                    tmp_segment.add_spot(x=position_x / 10,
                                         y=position_y / 10,
                                         weight=mu_weight)
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
                                                     SpotPositionsX=insert_segment.get_spotsPositionsX(),
                                                     SpotPositionsY=insert_segment.get_spotsPositionsY(),
                                                     SpotWeights=insert_segment.get_spotsWeights())
            for insert_segment, setting_segment in zip(copied_beam.Segments, setting_beam.Segments):
                print(insert_segment.get_RelativeWeight())
                setting_segment.RelativeWeight = insert_segment.get_RelativeWeight()
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
        self.Name = 'Log_' + Name
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
    def __init__(self, energy, SpotTuneId):
        self.Energy = energy
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

    def get_RelativeWeight(self):
        return sum([spot.weight for spot in self.Spots])


class Spot:
    def __init__(self, x, y, weight):
        self.x = x
        self.y = y
        self.weight = weight


if __name__ == "__main__":
    copyPlanAndImportLogFileData()
