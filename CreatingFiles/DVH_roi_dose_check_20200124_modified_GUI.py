from connect import *
import clr, System
clr.AddReference('System.Windows.Forms', 'System.Drawing')
from System.Windows.Forms import *
from System.Drawing import *

case = get_current("Case")
# Check point
try:
    beam_set = get_current("BeamSet")
except:
    MessageBox.Show("Please select plan using pulldown on upper right", "By python")
    sys.exit()

import os
os.chdir(os.getenv("HOMEDRIVE") + os.getenv("HOMEPATH") + "\\Desktop\\")

form = Form(Size=Size(300, 150), Text="ROI dose check.", AutoSize=True, Font=Font("MS UI Gothic", 18, FontStyle.Bold))
combobox_roi = ComboBox(Font=Font("MS UI Gothic", 18, FontStyle.Bold), AutoSize=True, Dock=DockStyle.Fill, Padding=Padding(0))
roi_name_list = [roi.OfRoi.Name for roi in case.PatientModel.StructureSets[beam_set.FractionDose.OnDensity.FromExamination.Name].RoiGeometries if roi.OfRoi.Type != "External" and roi.PrimaryShape != None]
combobox_roi.Items.AddRange(System.Array[System.Object](roi_name_list))

def ok_button(sender, event):
    roi_name = combobox_roi.SelectedItem
    roi_doses_indice = beam_set.FractionDose.GetDoseGridRoi(RoiName=roi_name).RoiVolumeDistribution.VoxelIndices
    doses = list(beam_set.FractionDose.DoseValues.DoseData)
    file_name = "DVH_roi_dose_check_{}_{}_{}.csv".format(get_current("Patient").PatientID, beam_set.DicomPlanLabel, roi_name)
    with open(file_name, 'w') as file:
        for roi_dose_index in roi_doses_indice:
            file.write(str(doses[roi_dose_index] * beam_set.FractionationPattern.NumberOfFractions) + "\n")
    
    MessageBox.Show("Export was finished :{}".format(file_name))

button_ok = Button(Text="OK", Font=Font("MS UI Gothic", 18, FontStyle.Bold), Location=Point(100, 50), Size=Size(50, 50), AutoSize=True)
button_ok.Click += ok_button

form.Controls.AddRange(System.Array[Control]([combobox_roi, button_ok]))
Form.ShowDialog(form)

### End ###
