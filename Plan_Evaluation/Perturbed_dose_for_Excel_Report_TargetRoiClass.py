#
# 1) Change CTV name and volume list on Initial parameter.
# 2) Create perturbed dose.
# 3) Script execute.
#

from connect import *
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../common_processing'))
from CommonModules import create_new_patient_folder


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


class DoseData():
    def __init__(self):
        pass

    def setDx(self, VolumeList, DoseList):
        for volume, dose in zip(VolumeList, DoseList):
            setattr(self, "D" + str(int(volume * 100)), dose)

    def getDict(self):
        return self.__dict__

    def setMax(self, MaxDose):
        setattr(self, 'MaxDose', MaxDose)

    def setMin(self, MinDose):
        setattr(self, 'MinDose', MinDose)


class PerturbedDoseProperty():
    def __init__(self):
        self.BeamSetName = ''
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.density = 0.0
        self.DoseData = DoseData()




def export_perturbed_dose_of_target_roi():
    # Initial parameter
    case = get_current("Case")
    beam_set = get_current("BeamSet")
    plan = get_current("Plan")
    roi_name = []
    for bs in plan.BeamSets:
        if not bs.Prescription.PrimaryDosePrescription.OnStructure.Name in roi_name:
            roi_name.append(bs.Prescription.PrimaryDosePrescription.OnStructure.Name)

    volume_list = [0.99, 0.98, 0.95, 0.5, 0.02, 0.01]  # D99, D98, D95, D50, D2, D1

    bst_name_list = [bst.DicomPlanLabel for bst in plan.BeamSets]
    PerturbedDoseData = PerturbedData()
    for DoseOnE in case.TreatmentDelivery.FractionEvaluations[0].DoseOnExaminations:
        for eval_dose in DoseOnE.DoseEvaluations:
            if eval_dose.PerturbedDoseProperties != None and eval_dose.ForBeamSet.DicomPlanLabel in bst_name_list:
                tmpPerturbedData = PerturbedDoseProperty()
                tmpPerturbedData.BeamSetName = eval_dose.ForBeamSet.DicomPlanLabel
                tmpPerturbedData.x = -eval_dose.PerturbedDoseProperties.IsoCenterShift.x
                tmpPerturbedData.y = -eval_dose.PerturbedDoseProperties.IsoCenterShift.z
                tmpPerturbedData.z = eval_dose.PerturbedDoseProperties.IsoCenterShift.y # Ver.10A
                tmpPerturbedData.density = eval_dose.PerturbedDoseProperties.RelativeDensityShift

                num_of_fraction = eval_dose.ForBeamSet.FractionationPattern.NumberOfFractions
                dose_data_1fx = eval_dose.GetDoseAtRelativeVolumes(
                    RoiName=eval_dose.ForBeamSet.Prescription.PrimaryDosePrescription.OnStructure.Name,
                    RelativeVolumes=volume_list)
                dose_data_total = [dose * num_of_fraction for dose in dose_data_1fx]

                tmpPerturbedData.DoseData.setDx(volume_list, dose_data_total)

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

    file_name = "Perturbed_Dose_for_Excel_Report_{0}_{1}.csv".format(Pt_name, plan.Name)

    with open(file_name, "w") as file:
        file.write('PatientID,{}\n'.format(ID))
        file.write('PatientName,{}\n'.format(Pt_name))
        file.write("x(cm) : y(cm) : z(cm) : (Multiplied 100 is %)\n")
        file.write("Relative Volume : cGy\n")
        for BeamSetName in bst_name_list:
            file.write('\n-----' + BeamSetName + "-----\n")
            file.write("Target ROI,{}".format(
                plan.BeamSets[BeamSetName].Prescription.PrimaryDosePrescription.OnStructure.Name) + "\n")
            file.write("Density(%),X(cm),Y(cm),Z(cm),")
            for volume in volume_list:
                file.write('D' + str(int(volume * 100)) + ",")
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
    export_perturbed_dose_of_target_roi()
