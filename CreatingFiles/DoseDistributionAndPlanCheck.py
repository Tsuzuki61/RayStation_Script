from connect import *
import numpy
import os
import re
import openpyxl as px
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../common_processing'))
if __name__ == '__main__':
    # for test
    sys.path.append(r'M:\Script\create file\common_processing')
from CommonModules import create_new_patient_folder


def create_plan_check_xlsx():
    case = get_current("Case")
    plan = get_current("Plan")
    patient = get_current("Patient")
    Pt_name = patient.Name
    ID = patient.PatientID

    file_path = create_new_patient_folder()
    os.chdir("M:\\")

    os.chdir(os.getcwd() + file_path)

