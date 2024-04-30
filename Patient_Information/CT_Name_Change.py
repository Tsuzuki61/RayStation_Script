"""This module only works with  IronPython
"""
from connect import *
import os
import re
import sys
import wpf
from System.Windows import *
from System.Windows.Controls import *

import datetime as dt

# Connection with RayStation
case = get_current("Case")
exam_groups = [ExamG.Name for ExamG in case.ExaminationGroups]


class MessageBox(Window):
    def __init__(self):
        wpf.LoadComponent(self, os.path.join(os.path.dirname(__file__), "./xaml/messagebox(OKonly).xaml"))
        self.Topmost = True
        # Start up window at the center of the screen.
        self.WindowStartupLocation = WindowStartupLocation.CenterScreen
        self.Caption.Title = "Warning"
        self.msg.Text = "Examination Groups is not exist"

    def OK_Clicked(self, sender, event):
        self.DialogResult = True


class ComboBoxForm(Window):
    def __init__(self):
        wpf.LoadComponent(self, os.path.join(os.path.dirname(__file__), './xaml/CTNameCombo.xaml'))
        self.Topmost = True
        # Start up window at the center of the screen.
        self.WindowStartupLocation = WindowStartupLocation.CenterScreen
        self.ExamGName = ''
        for EN in exam_groups:
            self.CTgroupCombo.Items.Add(EN)

    def OKClicked(self, sender, event):
        self.ExamGName = self.CTgroupCombo.SelectedItem
        self.DialogResult = True

    def CancelClicked(self, sender, event):
        self.DialogResult = False


def change_grouped_CT_names():
    """This function renames the CT grouped into 4DCT """

    if len(exam_groups) == 0:
        msgbox = MessageBox()
        msgbox.ShowDialog()
        sys.exit()

    # Select the examination group
    ComboForm = ComboBoxForm()
    ComboForm.ShowDialog()
    if not ComboForm.DialogResult:
        sys.exit()

# -----Modify the name of the selected examination group and the name of CTs within the group-----
    for exam in case.ExaminationGroups[ComboForm.ExamGName].Items:
        data = exam.Examination.GetAcquisitionDataFromDicom()
        exam_date = dt.datetime.strptime(str(exam.Examination.GetExaminationDateTime()), '%m/%d/%Y %I:%M:%S %p')
        tmp = {'100Ex': '0%', '80Ex': '10%', '60Ex': '20%', '40Ex': '30%', '20Ex': '40%', '0Ex': '50%', '20In': '60%',
               '40In': '70%', '60In': '80%', '80In': '90%'}
        exam.Examination.Name = re.sub('(.*4DCT_).*', r'\1', ComboForm.ExamGName) + \
                                exam_date.strftime("%Y%m%d") + '_' + \
                                tmp[re.sub('.* ([0-9]*) (Ex|In).*',
                                           r'\1\2',
                                           data['SeriesModule'][
                                               'SeriesDescription'])]


# test
if __name__ == '__main__':
    change_grouped_CT_names()
