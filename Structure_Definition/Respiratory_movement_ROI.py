"""This module only works with  IronPython
export csv only
"""
from connect import *
import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../common_processing'))
from CommonModules import create_new_patient_folder

import wpf
from System.Windows import *
from System.Windows.Controls import *

import datetime as dt

case = get_current("Case")


class TextBoxForm(Window):
    def __init__(self):
        wpf.LoadComponent(self, os.path.join(os.path.dirname(__file__), './xaml/ROINameSearch.xaml'))
        self.Topmost = True
        # Start up window at the center of the screen.
        self.WindowStartupLocation = WindowStartupLocation.CenterScreen
        self.RoiName = ''

    def OKClicked(self, sender, event):
        self.RoiName = self.RoiNameText.Text
        self.DialogResult = True

    def CancelClicked(self, sender, event):
        self.DialogResult = False


class RoiCoordinate:
    def __init__(self, roi_name, x, y, z):
        self.Name = roi_name
        self.RL = x
        self.IS = z
        self.PA = -y

    def get_sort_number(self):
        if re.match('.*(EX|Ex)$', self.Name):
            return -2
        if re.match('.*(IN|In)$', self.Name):
            return -1
        tmp_re = re.match('.*[ _]([0-9]{1,2})', self.Name)
        if tmp_re:
            return int(tmp_re.group(1))


class RoiCoordinateList:
    def __init__(self):
        self.coordinates = []

    def sort(self):
        self.coordinates.sort(key=lambda x: x.get_sort_number())

    def add(self, roi_name, x, y, z):
        self.coordinates.append(RoiCoordinate(roi_name, x, y, z))

    def get_value_list(self, direction):
        ret_list = [getattr(coordinate, direction) for coordinate in self.coordinates]
        return ret_list


def Acquiring_coordinates_of_respiratory_movement_ROI():
    """This function renames the CT grouped into 4DCT """
    examination = get_current('Examination')
    patient = get_current('Patient')
    Pt_name = patient.Name
    ID = patient.PatientID
    TextForm = TextBoxForm()
    TextForm.ShowDialog()
    if not TextForm.DialogResult:
        sys.exit()
    tmp_match = re.match('.*?(\w+).*', TextForm.RoiName)
    if tmp_match:
        roi_name = tmp_match.group(1)
    roi_coordinate_list = RoiCoordinateList()
    re_str = "^" + TextForm.RoiName + "[ _]((EX|Ex)|(IN|In)|([0-9]+))"
    for roi_geometry in case.PatientModel.StructureSets[examination.Name].RoiGeometries:
        tmp_roi_name = roi_geometry.OfRoi.Name
        if re.match(re_str, tmp_roi_name):
            tmp_roi_coordinate = roi_geometry.GetCenterOfRoi()
            roi_coordinate_list.add(tmp_roi_name, tmp_roi_coordinate.x, tmp_roi_coordinate.y, tmp_roi_coordinate.z)

    roi_coordinate_list.sort()

    file_path = create_new_patient_folder()

    os.chdir("M:\\")
    os.chdir(os.getcwd() + file_path)

    file_name = "Center_of_selected_ROI_for_Excel_Report_{0}({1}).csv".format(Pt_name,
                                                                              roi_name)
    with open(file_name, "w") as file:
        file.write('PatientID,{}\n'.format(ID))
        file.write('PatientName,{}\n'.format(Pt_name))
        file.write('---ROI center(cm)---\n')
        file.write('ROI Name,R-L direction,I-S direction,P-A direction\n')
        for roi_coordinate in roi_coordinate_list.coordinates:
            file.write(
                "{0},{1},{2},{3},\n".format(roi_coordinate.Name, roi_coordinate.RL, roi_coordinate.IS,
                                            roi_coordinate.PA))


# test
if __name__ == '__main__':
    Acquiring_coordinates_of_respiratory_movement_ROI()
