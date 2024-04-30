from connect import *
import os
import re


def deform_data_import():
    """
    This function imports deform data for the currently selected patient
    """
    # Connection with RayStation
    case = get_current("Case")
    plan = get_current("Plan")
    patient = get_current("Patient")
    patient_db = get_current("PatientDB")

    pt_name = patient.Name
    ID = patient.PatientID
    FILE_PATH = "M:\\Patient_Data_Folder\\" + str(ID) + "_" + pt_name + "\\DeformData"
    files = os.listdir(FILE_PATH)
    os.chdir(FILE_PATH)
    folder_list = [os.path.join(FILE_PATH, f) for f in files if os.path.isdir(os.path.join(FILE_PATH, f))]
    planningCT_Name = plan.TreatmentCourse.TotalDose.OnDensity.FromExamination.Name
    planning_exam = plan.TreatmentCourse.TotalDose.OnDensity.FromExamination
    beam_set_name_list = [bs.DicomPlanLabel for bs in plan.BeamSets]
    deform_ct_name_list = []
    fn_list = []
    roi_name_list = [roi.OfRoi.Name for roi in case.PatientModel.StructureSets[planningCT_Name].RoiGeometries if
                   roi.HasContours()]

    for folder_name in folder_list:
        patient.Save()
        matching_patients = patient_db.QueryPatientsFromPath(Path=folder_name, SearchCriterias={'PatientID': ID})
        assert len(matching_patients) == 1, "Found more than 1 patient with ID {}".format(ID)
        matching_patient = matching_patients[0]
        # Query all the studies of the matching patient
        studies = patient_db.QueryStudiesFromPath(Path=folder_name, SearchCriterias=matching_patient)

        # Query all the series from all the matching studies
        series = []
        for study in studies:
            series += patient_db.QuerySeriesFromPath(Path=folder_name, SearchCriterias=study)

        # Filter queried series to only contain CT series
        series_to_import = [s for s in series if s['Modality'] == 'CT']
        patient.ImportDataFromPath(Path=folder_name,
                                   SeriesOrInstances=series_to_import, CaseName=case.CaseName)
        tmp_exam = case.Examinations['CT 1']
        tmp_exam.EquipmentInfo.SetImagingSystemReference(
            ImagingSystemName=case.Examinations[planningCT_Name].EquipmentInfo.ImagingSystemReference.ImagingSystemName)
        tmp_name = re.sub('[0-9]+$', '', folder_name)
        tmp_exam.Name = os.path.basename(tmp_name)
        deform_ct_name_list.append(tmp_exam.Name)
        fn_list.append(0)
        for DCName in deform_ct_name_list:
            try:
                case.SetRegistrationMatrix(FromExaminationName=DCName, ToExaminationName=planningCT_Name,
                                           TransformationMatrix={'M11': 1, 'M12': 0, 'M13': 0, 'M14': 0,
                                                                 'M21': 0, 'M22': 1, 'M23': 0, 'M24': 0,
                                                                 'M31': 0, 'M32': 0, 'M33': 1, 'M34': 0,
                                                                 'M41': 0, 'M42': 0, 'M43': 0, 'M44': 1})
            except:
                break
    case.PatientModel.CopyRoiGeometries(SourceExamination=planning_exam, TargetExaminationNames=deform_ct_name_list,
                                        RoiNames=roi_name_list)
    for BeamSetName in beam_set_name_list:
        plan.BeamSets[BeamSetName].ComputeDoseOnAdditionalSets(OnlyOneDosePerImageSet=False, AllowGridExpansion=True,
                                                               ExaminationNames=deform_ct_name_list,
                                                               FractionNumbers=fn_list, ComputeBeamDoses=True)


# test
if __name__ == '__main__':
    deform_data_import()
