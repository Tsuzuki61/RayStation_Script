#
# 1) Change CTV name and volume list on Initial parameter.
# 2) Create deform dose.
# 3) Script execute.
#

from connect import *
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../common_processing'))
from CommonModules import create_new_patient_folder


class DeformDataSet:
    def __init__(self):
        self.DeformDataList = []

    def getBeamSetData(self, BeamSetName):
        tmpList = [DD for DD in self.DeformDataList if
                   DD.BeamSetName == BeamSetName and 'Planning' not in DD.DeformCTName]
        return tmpList

    def getPrescriptionDoseData(self, BeamSetName):
        tmpList = [DD for DD in self.DeformDataList if
                   DD.BeamSetName == BeamSetName and 'Planning' in DD.DeformCTName]
        return tmpList[0]

    def getDirectionDoseData(self, BeamSetName, Direction):
        tmpList = [DD for DD in self.DeformDataList if DD.BeamSetName == BeamSetName and Direction in DD.DeformCTName]
        return tmpList[0]

    def getDeformDataAtMaxDose(self, BeamSetName, Dx):
        tmpList = [DD for DD in self.DeformDataList if DD.BeamSetName == BeamSetName]
        tmpList.sort(key=lambda x: getattr(x.DoseData, Dx), reverse=True)
        return tmpList[0]

    def getDeformDataAtMinDose(self, BeamSetName, Dx):
        tmpList = [DD for DD in self.DeformDataList if DD.BeamSetName == BeamSetName]
        tmpList.sort(key=lambda x: getattr(x.DoseData, Dx))
        return tmpList[0]


class DeformData:
    """
    Class for handling deformed dose data
    """
    def __init__(self):
        self.BeamSetName = ''
        self.DeformCTName = ''
        self.DoseData = DoseData()


class DoseData:
    def setDx(self, VolumeList, DoseList):
        for volume, dose in zip(VolumeList, DoseList):
            setattr(self, "D" + str(int(volume * 100)), dose)

    def getDict(self):
        return self.__dict__

    def setMax(self, MaxDose):
        setattr(self, 'MaxDose', MaxDose)

    def setMin(self, MinDose):
        setattr(self, 'MinDose', MinDose)


def create_excel_report_of_deform_dose():
    """
    Function to export deformed dose data to an Excel file
    """
    case = get_current("Case")
    plan = get_current("Plan")
    beam_set_name = []
    roi_name = []

    # Initial parameter

    volume_list = [0.99, 0.98, 0.95, 0.5, 0.02, 0.01]  # D99, D98, D95, D50, D2, D1
    bst_name_list = [bst.DicomPlanLabel for bst in plan.BeamSets]
    deform_data_set = DeformDataSet()

    for bs in plan.BeamSets:
        beam_set_name.append(bs.DicomPlanLabel)
        if bs.Prescription.PrimaryDosePrescription.OnStructure.Name not in roi_name:
            roi_name.append(bs.Prescription.PrimaryDosePrescription.OnStructure.Name)
        tmp_none_deform_data = DeformData()
        tmp_none_deform_data.BeamSetName = bs.DicomPlanLabel
        tmp_none_deform_data.DeformCTName = bs.FractionDose.OnDensity.FromExamination.Name
        num_of_fraction = bs.FractionationPattern.NumberOfFractions
        dose_data_1fx = bs.FractionDose.GetDoseAtRelativeVolumes(
            RoiName=bs.Prescription.PrimaryDosePrescription.OnStructure.Name,
            RelativeVolumes=volume_list)
        dose_data_total = [dose * num_of_fraction for dose in dose_data_1fx]
        tmp_none_deform_data.DoseData.setDx(volume_list, dose_data_total)
        deform_data_set.DeformDataList.append(tmp_none_deform_data)

    for eval_dose in case.TreatmentDelivery.FractionEvaluations[0].DoseOnExaminations:
        for doseEval in eval_dose.DoseEvaluations:
            if doseEval.PerturbedDoseProperties is None and doseEval.Name == "" \
                    and doseEval.ForBeamSet.DicomPlanLabel in beam_set_name:
                tmp_deform_data = DeformData()
                tmp_deform_data.BeamSetName = doseEval.ForBeamSet.DicomPlanLabel
                tmp_deform_data.DeformCTName = doseEval.OnDensity.FromExamination.Name

                num_of_fraction = doseEval.ForBeamSet.FractionationPattern.NumberOfFractions

                dose_data_1fx = doseEval.GetDoseAtRelativeVolumes(
                    RoiName=doseEval.ForBeamSet.Prescription.PrimaryDosePrescription.OnStructure.Name,
                    RelativeVolumes=volume_list)
                dose_data_total = [dose * num_of_fraction for dose in dose_data_1fx]

                tmp_deform_data.DoseData.setDx(volume_list, dose_data_total)

                deform_data_set.DeformDataList.append(tmp_deform_data)

    # create file & folder
    patient = get_current("Patient")
    pt_name = patient.Name

    direction_list = ['Sup', 'Inf', 'Ant', 'Pos']

    file_path = create_new_patient_folder()

    os.chdir("M:\\")
    os.chdir(os.getcwd() + file_path)

    FILE_NAME = "Deform_Dose_for_Excel_Report_{0}.csv".format(pt_name)

    with open(FILE_NAME, "w") as file:
        file.write("Deform CT Dose Report")
        file.write("Relative Volume : cGy\n")
        for BeamSetName in bst_name_list:
            file.write("\n-----" + BeamSetName + "-----\n")
            file.write("Target ROI,{}".format(
                plan.BeamSets[BeamSetName].Prescription.PrimaryDosePrescription.OnStructure.Name) + "\n")
            file.write(",")
            for volume in volume_list:
                file.write('D' + str(int(volume * 100)) + ",")
            file.write("\n")

            for direction in direction_list:
                DD = deform_data_set.getDirectionDoseData(BeamSetName, direction)
                KeyList = DD.DoseData.getDict().keys()
                file.write(DD.DeformCTName + ',')
                for key in KeyList:
                    file.write(str(getattr(DD.DoseData, key)) + ",")
                file.write("\n")
            file.write("---BeamSet Summary---\n")
            file.write('DoseAtRelativeVolumes,DoseType,DeformCT,Value,RateAtPrescriptionDoseAtRelativeVolumes\n')

            prescription = deform_data_set.getPrescriptionDoseData(BeamSetName=BeamSetName)
            for key in KeyList:
                if len(key) >= 3:
                    tmpData = deform_data_set.getDeformDataAtMinDose(BeamSetName, key)
                    file.write(
                        key + ',Min,' + tmpData.DeformCTName + ',' + str(getattr(tmpData.DoseData, key)) + "," + str(
                            getattr(tmpData.DoseData, key) / getattr(prescription.DoseData,key) * 100) + '\n')
                else:
                    tmpData = deform_data_set.getDeformDataAtMaxDose(BeamSetName, key)
                    file.write(
                        key + ',Max,' + tmpData.DeformCTName + ',' + str(getattr(tmpData.DoseData, key)) + "," + str(
                            getattr(tmpData.DoseData, key) / getattr(prescription.DoseData,key) * 100) + '\n')

            file.write("\n")


# test
if __name__ == '__main__':
    create_excel_report_of_deform_dose()
