from connect import *
from datetime import date
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../common_processing'))
from CommonModules import create_new_patient_folder


def export_roi_mean_dose():
    patient = get_current("Patient")
    plan = get_current("Plan")

    ID = patient.PatientID
    Pt_name = patient.Name
    QA_beamset_list = []
    QA_beam_dict = {}
    veri_plan_dict = {}
    beam_set_list = []
    all_roi_list = []  # type: List[Any]
    for beamset in plan.BeamSets:
        beam_set_list.append(beamset.DicomPlanLabel)

    ### Extract mean dose on all ROI End ###

    for veri_plan in plan.VerificationPlans:
        if veri_plan.ForTreatmentPlan.Name != plan.Name:
            continue
        beam_set = veri_plan.BeamSet
        QA_beamset_list.append(beam_set.DicomPlanLabel)
        beam_set.FractionDose.UpdateDoseGridStructures()
        roi_name_list = [roi.OfRoi.Name for roi in beam_set.PatientSetup.LocalizationPoiGeometrySource.RoiGeometries if
                         roi.OfRoi.Type != "External"]
        mean_dose_dict = {}
        per_beam_dict = {}
        beam_list = []
        for beam_dose in beam_set.FractionDose.ForBeamSet.FractionDose.BeamDoses:  # per beam Dictionary create
            beam_list.append(beam_dose.ForBeam.Name)
            for roi_name in roi_name_list:
                mean_dose = beam_dose.GetDoseStatistic(RoiName=roi_name, DoseType="Average")
                mean_dose_dict.setdefault(roi_name, mean_dose)
            per_beam_dict.setdefault(beam_dose.ForBeam.Name, mean_dose_dict)
        beam_list.sort()
        QA_beam_dict.setdefault(beam_set.DicomPlanLabel, beam_list)
        veri_plan_dict.setdefault(beam_set.DicomPlanLabel, per_beam_dict)
        for roi in roi_name_list:
            if not roi in all_roi_list:
                all_roi_list.append(roi)

    QA_beamset_list.sort()

    file_path = create_new_patient_folder()
    QA_folder_path = file_path + '\\QA_Plane_Dose_Data'

    os.chdir("M:\\")

    if not os.path.isdir(os.getcwd() + QA_folder_path):
        os.mkdir(os.getcwd() + QA_folder_path)
    for tmp_veri_plan in plan.VerificationPlans:
        tmp_qa_beamset_name = tmp_veri_plan.BeamSet.DicomPlanLabel
        tmp_qa_beamset_path = os.getcwd() + QA_folder_path + '\\' + tmp_qa_beamset_name
        if not os.path.isdir(tmp_qa_beamset_path):
            os.mkdir(tmp_qa_beamset_path)

    os.chdir(os.getcwd() + file_path)

    # Write dose as text file
    file_name = "QA_Plan_mean_dose_{0}_{1}_{2}.csv".format(ID, Pt_name, plan.Name)
    with open(file_name, 'w') as file:
        file.write("Created Date," + str(date.today()) + "\n")
        file.write("Patient ID," + ID + "\n" + "Patient Name," + Pt_name + "\n")
        file.write("Plan Name," + plan.Name + "\n")
        file.write("BeamSet Name,")
        for beamset_name in beam_set_list:
            file.write(beamset_name + ",")
        file.write("\n")
        file.write("\n" + "QA Plan Name" + "\n")
        for i in range(len(QA_beamset_list)):
            file.write(QA_beamset_list[i])
            file.write("\n")
        file.write(",")
        for i in range(len(QA_beamset_list)):
            file.write("{}_Mean_Dose(cGy)".format(QA_beamset_list[i]))
            file.write("," * len(QA_beam_dict[QA_beamset_list[i]]))
        file.write("\n")
        file.write("ROI_NAME,")

        for i in range(len(QA_beamset_list)):
            for j in range(len(QA_beam_dict[QA_beamset_list[i]])):
                file.write(QA_beam_dict[QA_beamset_list[i]][j])
                file.write(",")
        file.write('\n')

        for roi in all_roi_list:
            if roi == "PPC05 Center":
                continue
            file.write(roi + ",")
            for QA_beamset_name in QA_beamset_list:
                for QAbeam in QA_beam_dict[QA_beamset_name]:
                    if roi in veri_plan_dict[QA_beamset_name][QAbeam].keys():
                        file.write(str(veri_plan_dict[QA_beamset_name][QAbeam][roi]) + ",")
                    else:
                        file.write(",")
            file.write("\n")


# test
if __name__ == '__main__':
    export_roi_mean_dose()
