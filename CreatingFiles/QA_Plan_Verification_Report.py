# import sys
from connect import *
import os
import openpyxl as px
import sys
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '../common_processing'))
# if __name__ == '__main__':
#     # for test
#     sys.path.append(r'M:\Script\create file\common_processing')
from CommonModules import create_new_patient_folder


class InterpolateDose:
    def __init__(self):
        self.BeamSetName = ''
        self.DoseData = []

    def setDoseData(self, coodinate, dose):
        self.DoseData.append((coodinate, dose))

    def get_QA_prescription_dose(self):
        plan = get_current('Plan')
        for beam_set in plan.BeamSets:
            if beam_set.DicomPlanLabel in self.BeamSetName:
                currentQABeamSet = beam_set
                break
        fraction = currentQABeamSet.FractionationPattern.NumberOfFractions
        total_beamset_prescription = currentQABeamSet.Prescription.PrimaryDosePrescription.DoseValue
        return total_beamset_prescription / fraction

    def get_SOBP_center(self):
        maxdose = max([dose_data[1] for dose_data in self.DoseData])
        NormalizedDoseData = [(dose_data[0], dose_data[1] / maxdose) for dose_data in self.DoseData]
        for normalizedDoseData in NormalizedDoseData[::-1]:
            if normalizedDoseData[1] > 0.95:
                Shallower98_depth = normalizedDoseData[0]['y']
                break
        for normalizedDoseData in NormalizedDoseData:
            if normalizedDoseData[1] > 0.95:
                Deeper98_depth = normalizedDoseData[0]['y']
                break
        return (Shallower98_depth + Deeper98_depth) / 2

    def get_SOBP_prox(self):
        maxdose = max([dose_data[1] for dose_data in self.DoseData])
        NormalizedDoseData = [(dose_data[0], dose_data[1] / maxdose) for dose_data in self.DoseData]
        for normalizedDoseData in NormalizedDoseData[::-1]:
            if normalizedDoseData[1] > 0.95:
                return normalizedDoseData[0]['y'] + 0.8

    def get_SOBP_dist(self):
        maxdose = max([dose_data[1] for dose_data in self.DoseData])
        NormalizedDoseData = [(dose_data[0], dose_data[1] / maxdose) for dose_data in self.DoseData]
        for normalizedDoseData in NormalizedDoseData:
            if normalizedDoseData[1] > 0.95:
                return normalizedDoseData[0]['y'] - 0.8

    def get_build_up(self):
        SOBP_center = self.get_SOBP_center()
        for dose_data in self.DoseData:
            if dose_data[0]['y'] <= SOBP_center:
                center_dose = dose_data[1]
                break
        NormalizedDoseData = [(dose_data[0], dose_data[1] / center_dose) for dose_data in self.DoseData]
        for relative_dose in NormalizedDoseData[::-1]:
            if relative_dose[1] > 0.93:
                return relative_dose[0]['y']

    def get_dose_falloff(self):
        maxdose = max([dose_data[1] for dose_data in self.DoseData])
        NormalizedDoseData = [(dose_data[0], dose_data[1] / maxdose) for dose_data in self.DoseData]
        for normalizedDoseData in NormalizedDoseData:
            if normalizedDoseData[1] > 0.5:
                return normalizedDoseData[0]['y']

        # continue


class QADoseData:
    def __init__(self):
        self.DoseList = []

    def get_Beamset_Interpolate_dose(self, BeamSetName):
        for interpolate_dose in self.DoseList:
            if interpolate_dose.BeamSetName == BeamSetName:
                tmpDoseData = interpolate_dose.DoseData
        return tmpDoseData

    def average_SOBP_center(self):
        SOBP_center_list = [interpolate_dose.get_SOBP_center() for interpolate_dose in self.DoseList]
        return round(sum(SOBP_center_list) / len(SOBP_center_list), 1)

    def average_SOBP_center_select_beamsets(self, beam_set_names):
        SOBP_center_list = [interpolate_dose.get_SOBP_center() for interpolate_dose in self.DoseList if
                            interpolate_dose.BeamSetName in beam_set_names]
        return round(sum(SOBP_center_list) / len(SOBP_center_list), 1)

    def get_SOBP_centers(self):
        return [interpolate_dose.get_SOBP_center() for interpolate_dose in self.DoseList]

    def get_SOBP_centers_max_min_deff(self):
        deff_list = [interpolate_dose.get_SOBP_center() for interpolate_dose in self.DoseList]
        return max(deff_list) - min(deff_list)

    def get_SOBP_centers_dev(self):
        center_list = [interpolate_dose.get_SOBP_center() for interpolate_dose in self.DoseList]
        return np.std(center_list)

    def average_SOBP_prox(self):
        SOBP_prox_list = [interpolate_dose.get_SOBP_prox() for interpolate_dose in self.DoseList]
        return round(sum(SOBP_prox_list) / len(SOBP_prox_list), 1)

    def average_SOBP_prox_select_beamsets(self, beam_set_names):
        SOBP_prox_list = [interpolate_dose.get_SOBP_prox() for interpolate_dose in self.DoseList if
                          interpolate_dose.BeamSetName in beam_set_names]
        return round(sum(SOBP_prox_list) / len(SOBP_prox_list), 1)

    def average_SOBP_dist(self):
        SOBP_dist_list = [interpolate_dose.get_SOBP_dist() for interpolate_dose in self.DoseList]
        return round(sum(SOBP_dist_list) / len(SOBP_dist_list), 1)

    def average_SOBP_dist_select_beamsets(self, beam_set_names):
        SOBP_dist_list = [interpolate_dose.get_SOBP_dist() for interpolate_dose in self.DoseList if
                          interpolate_dose.BeamSetName in beam_set_names]
        return round(sum(SOBP_dist_list) / len(SOBP_dist_list), 1)

    def average_buildup(self):
        buildup_list = [interpolate_dose.get_build_up() for interpolate_dose in self.DoseList]
        return round(sum(buildup_list) / len(buildup_list), 1)

    def average_buildup_select_beamsets(self, beam_set_names):
        buildup_list = [interpolate_dose.get_build_up() for interpolate_dose in self.DoseList if
                        interpolate_dose.BeamSetName in beam_set_names]
        return round(sum(buildup_list) / len(buildup_list), 1)

    def average_dose_falloff(self):
        dose_falloff_list = [interpolate_dose.get_dose_falloff() for interpolate_dose in self.DoseList]
        return round(sum(dose_falloff_list) / len(dose_falloff_list), 1)

    def average_dose_falloff_select_beamsets(self, beam_set_names):
        dose_falloff_list = [interpolate_dose.get_dose_falloff() for interpolate_dose in self.DoseList if
                             interpolate_dose.BeamSetName in beam_set_names]
        return round(sum(dose_falloff_list) / len(dose_falloff_list), 1)


def create_QA_plan_report():
    plan = get_current("Plan")

    QA_dose_data = create_QA_dose_data()

    if QA_dose_data.get_SOBP_centers_dev() < 0.15:
        for VerificationPlan in plan.VerificationPlans:
            if VerificationPlan.ForTreatmentPlan.Name == plan.Name:
                for VeriBeam in VerificationPlan.BeamSet.Beams:
                    VeriBeam.Isocenter.EditIsocenter(Position={'x': 0, 'y': QA_dose_data.average_SOBP_center(), 'z': 0})
                    tmpAlgorism = VerificationPlan.BeamSet.AccurateDoseAlgorithm.DoseAlgorithm
                    try:
                        VerificationPlan.BeamSet.ComputeDose(ComputeBeamDoses=True, DoseAlgorithm=tmpAlgorism,
                                                             ForceRecompute=False)
                    except:
                        continue
        QA_dose_data = create_QA_dose_data()
        measurement_buildup = QA_dose_data.average_buildup()
        print('entrance', 5.0 - 47.5, 5.0)
        print('buildup', measurement_buildup, measurement_buildup + 47.5)
        SOBP_prox = QA_dose_data.average_SOBP_prox()
        SOBP_dist = QA_dose_data.average_SOBP_dist()
        SOBP_center = QA_dose_data.average_SOBP_center()

        measurement_SOBP_prox, measurement_SOBP_center, measurement_SOBP_dist = get_SOBP_measurement_points(SOBP_prox,
                                                                                                            SOBP_center,
                                                                                                            SOBP_dist)

        print('SOBP_prox', measurement_SOBP_prox, measurement_SOBP_prox + 47.5)
        print('SOBP_center', measurement_SOBP_center, measurement_SOBP_center + 47.5)
        print('SOBP_dist', measurement_SOBP_dist, measurement_SOBP_dist + 47.5)

        measurement_dose_falloff = QA_dose_data.average_dose_falloff()
        print('dose_falloff', measurement_dose_falloff, measurement_dose_falloff + 47.5)
    else:
        QA_beams_list = []
        for VerificationPlan in plan.VerificationPlans:
            if VerificationPlan.ForTreatmentPlan.Name == plan.Name:
                QA_beams_list.append(VerificationPlan.BeamSet)
        beam_grouping_dict = beam_grouped_by_angles(QA_beams_list)
        for VerificationPlan in plan.VerificationPlans:
            if VerificationPlan.ForTreatmentPlan.Name == plan.Name:
                for VeriBeam in VerificationPlan.BeamSet.Beams:
                    for key, item in beam_grouping_dict.items():
                        if VerificationPlan.BeamSet.DicomPlanLabel in item:
                            VeriBeam.Isocenter.EditIsocenter(
                                Position={'x': 0, 'y': QA_dose_data.average_SOBP_center_select_beamsets(item), 'z': 0})
                            tmpAlgorism = VerificationPlan.BeamSet.AccurateDoseAlgorithm.DoseAlgorithm
                    try:
                        VerificationPlan.BeamSet.ComputeDose(ComputeBeamDoses=True, DoseAlgorithm=tmpAlgorism,
                                                             ForceRecompute=False)
                    except:
                        continue
        QA_dose_data = create_QA_dose_data()
        for key, item in beam_grouping_dict.items():
            print(item)
            measurement_buildup = QA_dose_data.average_buildup_select_beamsets(item)
            print('entrance', 5.0 - 47.5, 5.0)
            print('buildup', measurement_buildup, measurement_buildup + 47.5)

            SOBP_prox = QA_dose_data.average_SOBP_prox_select_beamsets(item)
            SOBP_dist = QA_dose_data.average_SOBP_dist_select_beamsets(item)
            SOBP_center = QA_dose_data.average_SOBP_center_select_beamsets(item)
            measurement_SOBP_prox, measurement_SOBP_center, measurement_SOBP_dist = get_SOBP_measurement_points(
                SOBP_prox,
                SOBP_center,
                SOBP_dist)

            print('SOBP_prox', measurement_SOBP_prox, measurement_SOBP_prox + 47.5)
            print('SOBP_center', measurement_SOBP_center, measurement_SOBP_center + 47.5)
            print('SOBP_dist', measurement_SOBP_dist, measurement_SOBP_dist + 47.5)

            measurement_dose_falloff = QA_dose_data.average_dose_falloff_select_beamsets(item)
            print('dose_falloff', measurement_dose_falloff, measurement_dose_falloff + 47.5)



def get_SOBP_measurement_points(SOBP_prox, SOBP_center, SOBP_dist):
    if abs(SOBP_prox - SOBP_center) == abs(SOBP_center - SOBP_dist):
        return SOBP_prox, SOBP_center, SOBP_dist
    elif abs(SOBP_prox - SOBP_center) > abs(SOBP_center - SOBP_dist):
        return SOBP_prox, SOBP_center, SOBP_center + abs(SOBP_prox - SOBP_center)
    elif abs(SOBP_prox - SOBP_center) < abs(SOBP_center - SOBP_dist):
        return SOBP_center - abs(SOBP_center - SOBP_dist), SOBP_center, SOBP_dist


def create_QA_dose_data():
    plan = get_current("Plan")

    QA_beam_set_list = []
    QA_dose_data = QADoseData()
    for VerificationPlan in plan.VerificationPlans:
        if VerificationPlan.ForTreatmentPlan.Name == plan.Name:
            tmpInterpolateDoseClass = InterpolateDose()
            tmpInterpolateDoseClass.BeamSetName = VerificationPlan.BeamSet.DicomPlanLabel
            QA_beam_set_list.append(VerificationPlan.BeamSet.DicomPlanLabel)
            roi_list = [(roi.OfRoi.Name, roi.GetCenterOfRoi()) for roi in
                        VerificationPlan.BeamSet.PatientSetup.LocalizationPoiGeometrySource.RoiGeometries if
                        roi.OfRoi.Type != "External"]
            for roi in roi_list:
                tmpInterpolateDoseClass.setDoseData(roi[1],
                                                    VerificationPlan.BeamSet.FractionDose.GetDoseStatistic(
                                                        RoiName=roi[0],
                                                        DoseType="Average"))
            QA_dose_data.DoseList.append(tmpInterpolateDoseClass)
    return QA_dose_data


def create_QA_dose_xlsx_file():
    pass


# temporaly
def create_txt(IsIsoCenterEq):
    file_path = create_new_patient_folder()
    os.chdir("M:\\")
    os.chdir(os.getcwd() + file_path)
    patient = get_current('Patient')
    plan = get_current('Plan')
    beamset
    file_name = "QA_Plan_measurement_point_{0}_{1}_{2}.csv".format(patient.PatientID, patient.Name, plan.Name)
    # with open(file_name, 'w') as file:


def beam_grouped_by_angles(beamsets_list):
    beam_group = {}
    for beamset in beamsets_list:
        for beam in beamset.Beams:
            if beam.Description not in list(beam_group.keys()):
                beam_group.setdefault(beam.Description, [beamset.DicomPlanLabel])
            else:
                beam_group[beam.Description].append(beamset.DicomPlanLabel)
    return beam_group


def list_number_equal(number_list, equal_number):
    for number in number_list:
        if number != equal_number:
            return False
    return True


if __name__ == '__main__':
    create_QA_plan_report()
