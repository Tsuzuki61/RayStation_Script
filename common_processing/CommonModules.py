"""This module summarizes common processing"""
from connect import *
import os


def create_new_patient_folder():
    """This function creates a new patient folder if one does not exist"""
    patient = get_current("Patient")
    Pt_name = patient.Name
    ID = patient.PatientID
    tmpDir = os.getcwd()
    os.chdir("M:\\")
    if not os.path.isdir(os.getcwd() + "Patient_Data_Folder"):
        os.mkdir(os.getcwd() + "Patient_Data_Folder")
    file_path = "Patient_Data_Folder\\" + str(ID) + "_" + Pt_name
    if not os.path.isdir(os.getcwd() + file_path):
        os.mkdir(os.getcwd() + file_path)
    os.chdir(tmpDir)
    return file_path


if __name__ == '__main__':
    create_new_patient_folder()
