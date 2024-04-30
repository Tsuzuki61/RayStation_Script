from connect import *
from decimal import *
import collections
import re
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../common_processing'))
from CommonModules import create_new_patient_folder


def create_prostate_dose_check_csv():
    global volume_list
    plan = get_current("Plan")
    case = get_current("Case")

    BeamSetNames = [BeamSet.DicomPlanLabel for BeamSet in plan.BeamSets]
    roi_list = [roi.Name for roi in case.PatientModel.RegionsOfInterest]
    tmpList = [beamset.Prescription.PrimaryDosePrescription.OnStructure.Name for beamset in plan.BeamSets]
    dose_roi_list = sorted(set(tmpList), key=tmpList.index)
    CTV_Name_List = sorted(set(tmpList), key=tmpList.index)
    vPTV_Name_List = []
    ePTV_Name_List = []
    PrescriptionDose = 0
    for BS in plan.BeamSets:
        PrescriptionDose += BS.Prescription.PrimaryDosePrescription.DoseValue

    for CTV_Name in CTV_Name_List:
        vPTV_Name = CTV_Name.replace('CTV', 'vPTV')
        PTV_Name = CTV_Name.replace('CTV', 'PTV')

        for PTVName in roi_list:
            rm1 = re.match(vPTV_Name, PTVName)
            rm2 = re.match(PTV_Name, PTVName)
            if rm1:
                vPTV_Name_List.append(rm1.group(0))
                dose_roi_list.append(rm1.group(0))
            elif rm2:
                ePTV_Name_List.append(rm2.group(0))
                dose_roi_list.append(rm2.group(0))

    append_dose_roi_list = ['Rectum', 'Bladder', 'Femur_R', 'Femur_L', 'S Intestine',
                            'L Intestine',
                            'MaxDose']
    for adr in append_dose_roi_list:
        dose_roi_list.append(adr)

    Fraction = 0
    for TF in plan.TreatmentCourse.TreatmentFractions:
        Fraction += 1
    relative_name_list = ['D98%', 'D95%', 'D50%']
    relative_V_list = ['V95%']
    volume_list = [0.98, 0.95, 0.50]
    dose_list = [0.95 * PrescriptionDose]
    if Fraction >= 38:
        rectum_list = ['V70Gy', 'V60Gy', 'V50Gy', 'V40Gy']
        rectum_dose_list = [7000, 6000, 5000, 4000]
        bladder_list = ['V65Gy', 'V40Gy']
        bladder_dose_list = [6500, 4000]
    elif Fraction >= 20:
        rectum_list = ['V70Gy', 'V60Gy', 'V50Gy', 'V40Gy', 'V30Gy', 'V20Gy', 'V10Gy']
        rectum_dose_list = [7000, 6000, 5000, 4000, 3000, 2000, 1000]
        bladder_list = ['V54.5Gy', 'V34.5Gy']
        bladder_dose_list = [5450, 3450]
    else:
        rectum_list = ['V51.2Gy', 'V46.1Gy', 'V41Gy', 'V35.8Gy', 'V25.6Gy']
        rectum_dose_list = [5120, 4610, 4100, 3580, 2560]
        bladder_list = ['V44.5Gy', 'V28.8Gy']
        bladder_dose_list = [4450, 2880]

    DDDic = collections.OrderedDict()
    # -----------------CTV--------------------

    for CTV_Name in CTV_Name_List:
        CTV = collections.OrderedDict()
        CTV_doses = plan.TreatmentCourse.TotalDose.GetDoseAtRelativeVolumes(RoiName=CTV_Name,
                                                                            RelativeVolumes=volume_list)
        for rela, dose in zip(relative_name_list, CTV_doses):
            CTV.setdefault(rela, Decimal(str(dose / 100)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
        CTV_Vol = plan.TreatmentCourse.TotalDose.GetRelativeVolumeAtDoseValues(RoiName=CTV_Name, DoseValues=dose_list)
        for relaV, Vol in zip(relative_V_list, CTV_Vol):
            CTV.setdefault(relaV, Decimal(str(Vol * 100)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
        DDDic.setdefault(CTV_Name, CTV)

    # -----------------Virtual_PTV--------------------
    for vPTV_Name in vPTV_Name_List:
        Virtual_PTV = collections.OrderedDict()
        StructureSets = plan.GetStructureSet()
        ROI = StructureSets.RoiGeometries[vPTV_Name]
        if ROI.OfRoi.DerivedRoiExpression is not None:
            DRE = "\n" + 'Sup:' + str(ROI.OfRoi.DerivedRoiExpression.SuperiorDistance) + ',' + 'Inf:' + str(
                ROI.OfRoi.DerivedRoiExpression.InferiorDistance) + ',' + 'Right:' + str(
                ROI.OfRoi.DerivedRoiExpression.RightDistance) + ',' + 'Left:' + str(
                ROI.OfRoi.DerivedRoiExpression.LeftDistance) + ',' + 'Ant:' + str(
                ROI.OfRoi.DerivedRoiExpression.AnteriorDistance) + ',' + 'Pos:' + str(
                ROI.OfRoi.DerivedRoiExpression.PosteriorDistance)
            Virtual_PTV.setdefault('DerivedROIExpression', DRE)
        Virtual_PTV_doses = plan.TreatmentCourse.TotalDose.GetDoseAtRelativeVolumes(RoiName=vPTV_Name,
                                                                                    RelativeVolumes=volume_list)
        for rela, dose in zip(relative_name_list, Virtual_PTV_doses):
            Virtual_PTV.setdefault(rela, Decimal(str(dose / 100)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
        Virtual_PTV_Vol = plan.TreatmentCourse.TotalDose.GetRelativeVolumeAtDoseValues(RoiName=vPTV_Name,
                                                                                       DoseValues=dose_list)
        for relaV, Vol in zip(relative_V_list, Virtual_PTV_Vol):
            Virtual_PTV.setdefault(relaV, Decimal(str(Vol * 100)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
        DDDic.setdefault(vPTV_Name, Virtual_PTV)

    # -----------------Evaluative_PTV--------------------
    for ePTV_Name in ePTV_Name_List:
        Evaluative_PTV = collections.OrderedDict()
        StructureSets = plan.GetStructureSet()
        ROI = StructureSets.RoiGeometries[ePTV_Name]
        if ROI.OfRoi.DerivedRoiExpression is not None:
            DRE = "\n" + 'Sup:' + str(ROI.OfRoi.DerivedRoiExpression.SuperiorDistance) + ',' + 'Inf:' + str(
                ROI.OfRoi.DerivedRoiExpression.InferiorDistance) + ',' + 'Right:' + str(
                ROI.OfRoi.DerivedRoiExpression.RightDistance) + ',' + 'Left:' + str(
                ROI.OfRoi.DerivedRoiExpression.LeftDistance) + ',' + 'Ant:' + str(
                ROI.OfRoi.DerivedRoiExpression.AnteriorDistance) + ',' + 'Pos:' + str(
                ROI.OfRoi.DerivedRoiExpression.PosteriorDistance)
            Evaluative_PTV.setdefault('DerivedROIExpression', DRE)
        Evaluative_PTV_doses = plan.TreatmentCourse.TotalDose.GetDoseAtRelativeVolumes(RoiName=ePTV_Name,
                                                                                       RelativeVolumes=volume_list)
        for rela, dose in zip(relative_name_list, Evaluative_PTV_doses):
            Evaluative_PTV.setdefault(rela, Decimal(str(dose / 100)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
        Evaluative_PTV_Vol = plan.TreatmentCourse.TotalDose.GetRelativeVolumeAtDoseValues(RoiName=ePTV_Name,
                                                                                          DoseValues=dose_list)
        for relaV, Vol in zip(relative_V_list, Evaluative_PTV_Vol):
            Evaluative_PTV.setdefault(relaV, Decimal(str(Vol * 100)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
        DDDic.setdefault(ePTV_Name, Evaluative_PTV)

    # -----------------Rectum--------------------
    Rectum = collections.OrderedDict()
    rectum_RelaVol = plan.TreatmentCourse.TotalDose.GetRelativeVolumeAtDoseValues(RoiName='Rectum',
                                                                                  DoseValues=rectum_dose_list)
    Rectum.setdefault('DMax', Decimal(
        plan.TreatmentCourse.TotalDose.GetDoseStatistic(RoiName='Rectum', DoseType='Max') / 100).quantize(
        Decimal('0.1'),
        rounding=ROUND_HALF_UP))
    StructureSets = plan.GetStructureSet()
    rectumROI_Vol = StructureSets.RoiGeometries['Rectum'].GetRoiVolume()

    for rela, Vol in zip(rectum_list, rectum_RelaVol):
        if Fraction >= 38:
            Rectum.setdefault(rela, Decimal(str(Vol * 100)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
        elif Fraction >= 20:
            Rectum.setdefault(rela, str(
                Decimal(str(Vol * rectumROI_Vol)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)) + 'cc')
        else:
            Rectum.setdefault(rela, Decimal(str(Vol * 100)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))

    DDDic.setdefault('Rectum', Rectum)

    # -----------------Bladder--------------------

    Bladder = collections.OrderedDict()
    bladder_doses = plan.TreatmentCourse.TotalDose.GetRelativeVolumeAtDoseValues(RoiName='Bladder',
                                                                                 DoseValues=bladder_dose_list)
    Bladder.setdefault('DMax', Decimal(
        plan.TreatmentCourse.TotalDose.GetDoseStatistic(RoiName='Bladder', DoseType='Max') / 100).quantize(
        Decimal('0.1'),
        rounding=ROUND_HALF_UP))
    for rela, dose in zip(bladder_list, bladder_doses):
        Bladder.setdefault(rela, Decimal(str(dose * 100)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))

    DDDic.setdefault('Bladder', Bladder)

    # -----------------FemoralHeads--------------------

    FemoralHeadR = {'DMax': Decimal(
        plan.TreatmentCourse.TotalDose.GetDoseStatistic(RoiName='Femur_R', DoseType='Max') / 100).quantize(
        Decimal('0.1'), rounding=ROUND_HALF_UP)}
    DDDic.setdefault('Femur_R', FemoralHeadR)
    FemoralHeadL = {'DMax': Decimal(
        plan.TreatmentCourse.TotalDose.GetDoseStatistic(RoiName='Femur_L', DoseType='Max') / 100).quantize(
        Decimal('0.1'), rounding=ROUND_HALF_UP)}
    DDDic.setdefault('Femur_L', FemoralHeadL)

    # -----------------Bowels--------------------

    SmallBowel = {'DMax': Decimal(
        plan.TreatmentCourse.TotalDose.GetDoseStatistic(RoiName='S Intestine', DoseType='Max') / 100).quantize(
        Decimal('0.1'), rounding=ROUND_HALF_UP)}
    DDDic.setdefault('S Intestine', SmallBowel)

    LargeBowel = {'DMax': Decimal(
        plan.TreatmentCourse.TotalDose.GetDoseStatistic(RoiName='L Intestine', DoseType='Max') / 100).quantize(
        Decimal('0.1'), rounding=ROUND_HALF_UP)}
    DDDic.setdefault('L Intestine', LargeBowel)

    # -----------------MaxDose--------------------
    MaxDosefl = Decimal(plan.TreatmentCourse.TotalDose.GetDoseStatistic(RoiName='External', DoseType='Max')).quantize(
        Decimal('0.00000000'), rounding=ROUND_HALF_UP)
    MaxDose_CTVfl = []
    MaxDose_Evaluative_PTVfl = []
    MaxDose_Virtual_PTVfl = []
    for CTV_Name in CTV_Name_List:
        MaxDose_CTVfl.append(
            Decimal(plan.TreatmentCourse.TotalDose.GetDoseStatistic(RoiName=CTV_Name, DoseType='Max')).quantize(
                Decimal('0.00000000'), rounding=ROUND_HALF_UP))

    for ePTV_Name in ePTV_Name_List:
        MaxDose_Evaluative_PTVfl.append(
            Decimal(plan.TreatmentCourse.TotalDose.GetDoseStatistic(RoiName=ePTV_Name, DoseType='Max')).quantize(
                Decimal('0.00000000'), rounding=ROUND_HALF_UP))

    for vPTV_Name in vPTV_Name_List:
        MaxDose_Virtual_PTVfl.append(
            Decimal(plan.TreatmentCourse.TotalDose.GetDoseStatistic(RoiName=vPTV_Name, DoseType='Max')).quantize(
                Decimal('0.00000000'), rounding=ROUND_HALF_UP))

    MaxDose = Decimal(MaxDosefl / 100).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
    PersentMaxDose = str(
        Decimal(MaxDosefl / Decimal(PrescriptionDose) * 100).quantize(Decimal("0"), rounding=ROUND_HALF_UP)) + '%'

    if MaxDosefl in MaxDose_CTVfl:
        MaxDose_bool = 'Inside CTV'
    elif MaxDosefl in MaxDose_Evaluative_PTVfl:
        MaxDose_bool = 'Inside Evaluative_PTV'
    elif MaxDosefl in MaxDose_Virtual_PTVfl:
        MaxDose_bool = 'Inside Virtual_PTV'
    else:
        MaxDose_bool = 'Outside PTV'

    MaxDose_dict = collections.OrderedDict()
    MaxDose_dict.setdefault('DMax', MaxDose)
    MaxDose_dict.setdefault('Ratio to Prescription Dose', PersentMaxDose)
    MaxDose_dict.setdefault('Place of existence', MaxDose_bool)
    DDDic.setdefault('MaxDose', MaxDose_dict)
    # -----------------CSV Export--------------------

    patient = get_current("Patient")
    Pt_name = patient.Name
    ID = patient.PatientID

    file_path = create_new_patient_folder()
    os.chdir("M:\\")
    os.chdir(os.getcwd() + file_path)

    file_name = "DoseStatistics({0})_{1}_{2}.csv".format(plan.Name, ID, Pt_name)

    with open(file_name, "w") as file:
        file.write("PatientID:{0}\nPatientName:{1}\n".format(ID, Pt_name))
        file.write('Plan Name:{}\n'.format(plan.Name))
        file.write("Beam Set:\n")
        for beamsetname in BeamSetNames:
            file.write(beamsetname + '\n')
        for RoiName in dose_roi_list:
            file.write(RoiName + '\n')
            for key in DDDic[RoiName].keys():
                file.write(key + ':' + str(DDDic[RoiName][key]) + '\n')
            file.write('\n')


# test
if __name__ == '__main__':
    create_prostate_dose_check_csv()
