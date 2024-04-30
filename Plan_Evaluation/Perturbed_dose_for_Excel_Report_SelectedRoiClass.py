#
# 1) Change CTV name and volume list on Initial parameter.
# 2) Create perturbed dose.
# 3) Script execute.
#

from connect import *
import clr, time, System

clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Drawing')
clr.AddReference('System.Windows.Forms.DataVisualization')
from System.Windows.Forms import *
from System.Drawing import *
from System.Windows.Forms.DataVisualization.Charting import *
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../common_processing'))
from CommonModules import create_new_patient_folder

from System.Collections import ArrayList


class PerturbedData():
    def __init__(self):
        self.DoseData_info = []

    def getBeamSetData(self, BeamSetName):
        tmpList = [PDP for PDP in self.DoseData_info if PDP.BeamSetName == BeamSetName]
        return tmpList

    def getPerturbedPropertyAtMaxDose(self, BeamSetName, Dx):
        tmpList = [PDP for PDP in self.DoseData_info if PDP.BeamSetName == BeamSetName]
        tmpList.sort(key=lambda x: getattr(x.DoseData, Dx), reverse=True)
        return tmpList[0]

    def getPerturbedPropertyAtMinDose(self, BeamSetName, Dx):
        tmpList = [PDP for PDP in self.DoseData_info if PDP.BeamSetName == BeamSetName]
        tmpList.sort(key=lambda x: getattr(x.DoseData, Dx))
        return tmpList[0]

    def DoseData_Info_Sort(self):
        self.DoseData_info = sorted(self.DoseData_info)


class DoseData():
    def setDx(self, VolumeList, DoseList):
        for volume, dose in zip(VolumeList, DoseList):
            setattr(self, "D" + str(int(volume * 100)), dose)

    def getDict(self):
        return self.__dict__

    def setMax(self, MaxDose):
        setattr(self, 'MaxDose', MaxDose)

    def setMin(self, MinDose):
        setattr(self, 'MinDose', MinDose)

    def setAverage(self, AverageDose):
        setattr(self, 'AverageDose', AverageDose)


class PerturbedDoseProperty():
    def __init__(self):
        self.BeamSetName = ''
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.density = 0.0
        self.DoseData = DoseData()

    def __lt__(self, other):
        """This method defines the sort condition"""
        if self.BeamSetName < other.BeamSetName:
            return True
        elif self.BeamSetName == other.BeamSetName:
            if self.density == other.density == 0.0:
                if self.x == self.y == self.z == 0:
                    return True
                elif other.x == other.y == other.z == 0:
                    return False
                elif self.x > other.x:
                    return True
                elif self.x < other.x:
                    return False
                elif self.y > other.y:
                    return True
                elif self.y < other.y:
                    return False
                elif self.z > other.z:
                    return True
                elif self.z < other.z:
                    return False
                else:
                    return True
            elif self.density == 0.0 and other.density != 0.0:
                return True
            elif other.density == 0.0 and self.density != 0.0:
                return False
            elif self.density > other.density:
                return True
            elif self.density < other.density:
                return False
            elif self.density == other.density:
                if self.x == self.y == self.z == 0:
                    return True
                elif other.x == other.y == other.z == 0:
                    return False
                elif self.x > other.x:
                    return True
                elif self.x < other.x:
                    return False
                elif self.y > other.y:
                    return True
                elif self.y < other.y:
                    return False
                elif self.z > other.z:
                    return True
                elif self.z < other.z:
                    return False
                else:
                    return True


# Initial parameter
roi_name = ""


def export_perturbed_dose_of_selected_roi():
    case = get_current("Case")
    beam_set = get_current("BeamSet")
    plan = get_current("Plan")
    global roi_name

    # form initialize
    form = Form(Text="Select ROI", Size=Size(275, 160), AutoScroll=True, TopMost=True)
    form.StartPosition = FormStartPosition.CenterScreen

    # combo box setting

    combo_list = [roi.Name for roi in case.PatientModel.RegionsOfInterest]

    combobox = ComboBox(Location=Point(40, 40), AutoSize=True, DropDownStyle=ComboBoxStyle.DropDown)

    def ComboBoxSelectAction(sender, e):
        global roi_name

        roi_name = combobox.SelectedItem

    # print(roi_name)

    # combobox.Visible = False

    combobox.Items.AddRange(
        System.Array[System.Object](combo_list))  # List is updated because items was added when it was clicked.
    combobox.SelectedIndexChanged += ComboBoxSelectAction

    exp_label = Label(Text="Please select the ROI used for calculation.", Location=Point(25, 5), AutoSize=True)

    # button setting
    def button_Clicked(sender, event):
        global roi_name
        if roi_name == "":
            MessageBox.Show("ROI has not been selected yet")
        else:
            form.Close()

    ok_btn = Button(Text="OK", Location=Point(160, 80), AutoSize=True)

    ok_btn.Click += button_Clicked

    control_list = [combobox, exp_label, ok_btn]
    for control in control_list: form.Controls.Add(control)

    Application.Run(form)

    volume_list = [0.99, 0.98, 0.95, 0.5, 0.02, 0.01]  # D99, D98, D95, D50, D2, D1

    bst_name_list = [bst.DicomPlanLabel for bst in plan.BeamSets]
    PerturbedDoseData = PerturbedData()
    for bs in plan.BeamSets:
        tmpPerturbedData = PerturbedDoseProperty()
        tmpPerturbedData.BeamSetName = bs.DicomPlanLabel
        num_of_fraction = bs.FractionationPattern.NumberOfFractions
        dose_data_1fx = bs.FractionDose.GetDoseAtRelativeVolumes(
            RoiName=roi_name,
            RelativeVolumes=volume_list)
        dose_data_total = [dose * num_of_fraction for dose in dose_data_1fx]
        tmpPerturbedData.DoseData.setDx(volume_list, dose_data_total)
        tmpPerturbedData.DoseData.setAverage(
            bs.FractionDose.GetDoseStatistic(RoiName=roi_name, DoseType="Average") * num_of_fraction)
        PerturbedDoseData.DoseData_info.append(tmpPerturbedData)

    for DoseOnE in case.TreatmentDelivery.FractionEvaluations[0].DoseOnExaminations:
        for eval_dose in DoseOnE.DoseEvaluations:
            if eval_dose.PerturbedDoseProperties != None and eval_dose.ForBeamSet.DicomPlanLabel in bst_name_list:
                tmpPerturbedData = PerturbedDoseProperty()
                tmpPerturbedData.BeamSetName = eval_dose.ForBeamSet.DicomPlanLabel
                tmpPerturbedData.x = -eval_dose.PerturbedDoseProperties.IsoCenterShift.x
                tmpPerturbedData.y = -eval_dose.PerturbedDoseProperties.IsoCenterShift.z
                tmpPerturbedData.z = eval_dose.PerturbedDoseProperties.IsoCenterShift.y  # Ver.10A
                tmpPerturbedData.density = eval_dose.PerturbedDoseProperties.RelativeDensityShift

                num_of_fraction = eval_dose.ForBeamSet.FractionationPattern.NumberOfFractions
                dose_data_1fx = []
                dose_data_1fx = eval_dose.GetDoseAtRelativeVolumes(RoiName=roi_name, RelativeVolumes=volume_list)
                dose_data_total = [dose * num_of_fraction for dose in dose_data_1fx]

                tmpPerturbedData.DoseData.setDx(volume_list, dose_data_total)
                tmpPerturbedData.DoseData.setAverage(
                    eval_dose.GetDoseStatistic(RoiName=roi_name, DoseType="Average") * num_of_fraction)

                # PerturbedDataList append
                PerturbedDoseData.DoseData_info.append(tmpPerturbedData)
    # create file & folder
    patient = get_current("Patient")
    ID = patient.PatientID
    Pt_name = patient.Name
    beamset_name = beam_set.DicomPlanLabel

    file_path = create_new_patient_folder()

    os.chdir("M:\\")
    os.chdir(os.getcwd() + file_path)

    file_name = "Perturbed_Dose_for_Excel_Report_{0}_{1}({2}).csv".format(Pt_name, plan.Name,
                                                                          roi_name)
    PerturbedDoseData.DoseData_Info_Sort()

    with open(file_name, "w") as file:
        file.write('PatientID,{}\n'.format(ID))
        file.write('PatientName,{}\n'.format(Pt_name))
        file.write("x(cm) : y(cm) : z(cm) : (Multiplied 100 is %)\n")
        file.write("Relative Volume : cGy\n")
        for BeamSetName in bst_name_list:
            file.write('\n-----' + BeamSetName + "-----\n")
            file.write("Target ROI,{}".format(roi_name) + "\n")
            file.write("Density(%),X(cm),Y(cm),Z(cm),")
            for volume in volume_list:
                file.write('D' + str(int(volume * 100)) + ",")
            file.write('AverageDose')
            file.write("\n")

            tmpPerturbedDataList = PerturbedDoseData.getBeamSetData(BeamSetName)
            for tmpPD in tmpPerturbedDataList:
                file.write("{0},{1},{2},{3},".format(tmpPD.density * 100, tmpPD.x, tmpPD.y, tmpPD.z))
                KeyList = tmpPD.DoseData.getDict().keys()

                for key in KeyList:
                    file.write(str(getattr(tmpPD.DoseData, key)) + ',')

                file.write('\n')

            file.write('---BeamSet Summary---\n')
            file.write('DoseAtRelativeVolumes,DoseType,Value,RateAtPrescription,Density(%),X(cm),Y(cm),Z(cm),\n')
            prescription = plan.BeamSets[BeamSetName].Prescription.PrimaryDosePrescription.DoseValue
            for key in KeyList:
                if len(key) >= 3:
                    tmpData = PerturbedDoseData.getPerturbedPropertyAtMinDose(BeamSetName, key)
                    file.write(key + ',Min,' + str(getattr(tmpData.DoseData, key)) + ',' + str(
                        getattr(tmpData.DoseData, key) / prescription * 100) + ',')
                else:
                    tmpData = PerturbedDoseData.getPerturbedPropertyAtMaxDose(BeamSetName, key)
                    file.write(key + ',Max,' + str(getattr(tmpData.DoseData, key)) + ',' + str(
                        getattr(tmpData.DoseData, key) / prescription * 100) + ',')
                file.write("{0},{1},{2},{3},\n".format(tmpData.density * 100, tmpData.x, tmpData.y, tmpData.z))


### End ###

# test
if __name__ == '__main__':
    export_perturbed_dose_of_selected_roi()
