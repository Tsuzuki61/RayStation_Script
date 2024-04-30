from connect import *
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../common_processing'))
from CommonModules import create_new_patient_folder
import subprocess


def open_current_patient_folder():
    """
    Open the data folder for the currently active patient.
    """
    file_path = create_new_patient_folder()
    os.chdir("M:\\")
    subprocess.call('explorer {}'.format(os.getcwd() + file_path))


if __name__ == '__main__':
    open_current_patient_folder()
