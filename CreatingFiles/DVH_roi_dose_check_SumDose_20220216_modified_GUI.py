from connect import *
import clr, System

clr.AddReference('System.Windows.Forms', 'System.Drawing')
from System.Windows.Forms import *
from System.Drawing import *

case = get_current("Case")
patient = get_current('Patient')
try:
    plan = get_current("Plan")
except:
    MessageBox.Show("Please select plan using pulldown on upper right", "By python")
    sys.exit()

import os

os.chdir(os.getenv("HOMEDRIVE") + os.getenv("HOMEPATH") + "\\Desktop\\")

form = Form(Size=Size(300, 150), Text="ROI dose check.", AutoSize=True, Font=Font("MS UI Gothic", 18, FontStyle.Bold))
combobox_roi = ComboBox(Font=Font("MS UI Gothic", 18, FontStyle.Bold), AutoSize=True, Dock=DockStyle.Fill,
                        Padding=Padding(0))
roi_name_list = [roi.OfRoi.Name for roi in plan.GetStructureSet().RoiGeometries if
                 roi.OfRoi.Type != "External" and roi.PrimaryShape != None]
combobox_roi.Items.AddRange(System.Array[System.Object](roi_name_list))


def ok_button(sender, event):
    roi_name = combobox_roi.SelectedItem
    if not os.path.isdir(os.path.join(os.getcwd(), patient.PatientID)):
        os.mkdir(os.path.join(os.getcwd(), patient.PatientID))
    os.chdir(os.path.join(os.getcwd(), patient.PatientID))
    for fe in case.TreatmentDelivery.FractionEvaluations:
        for doe in fe.DoseOnExaminations:
            for de in doe.DoseEvaluations:
                if de.Name != '':
                    roi_doses_indice = de.GetDoseGridRoi(
                        RoiName=roi_name).RoiVolumeDistribution.VoxelIndices
                    doses = list(de.DoseValues.DoseData)

                    file_name = "DVH_roi_dose_check_{}_{}_{}.csv".format(get_current("Patient").PatientID,
                                                                         de.Name,
                                                                         roi_name)
                    with open(file_name, 'w') as file:
                        for roi_dose_index in roi_doses_indice:
                            file.write(str(doses[roi_dose_index]) + "\n")

    MessageBox.Show("Export was finished :{}".format(file_name))


button_ok = Button(Text="OK", Font=Font("MS UI Gothic", 18, FontStyle.Bold), Location=Point(100, 50), Size=Size(50, 50),
                   AutoSize=True)
button_ok.Click += ok_button

form.Controls.AddRange(System.Array[Control]([combobox_roi, button_ok]))
Form.ShowDialog(form)

### End ###
