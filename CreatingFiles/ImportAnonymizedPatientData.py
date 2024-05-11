from connect import *
import os
import sys
import re


def import_patient_data(folder_path):
    patient_db = get_current('PatientDB')
    warnings = patient_db.ImportPatientFromPath(Path=folder_path,
                                                Patient={},
                                                SeriesFilter={"Modality": "CT"},
                                                ImportFilters=[])
    print(warnings)
    patient = get_current('Patient')
    case = get_current('Case')
    number = re.match('Script([0-9]{8})', patient.PatientID).group(1)
    examination = case.Examinations['CT 1']
    examination.Name = 'PlanningCT_{}'.format(number)
    examination.EquipmentInfo.SetImagingSystemReference(ImagingSystemName='SOMATOM_Body')
    patient.Save()


def import_all_anonymized_data(data_folder_path):
    files = os.listdir(data_folder_path)
    files_dir = [os.path.join(data_folder_path, f) for f in files if os.path.isdir(os.path.join(data_folder_path, f))]
    for file_dir in files_dir:
        import_patient_data(file_dir)


if __name__ == '__main__':
    import_all_anonymized_data(r"DirectoryPath")
    # import_patient_data(r"DirectoryPath")
