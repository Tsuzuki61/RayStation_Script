# Script recorded 08 Nov 2018

#   RayStation version: 6.2.0.7
#   Selected patient: ...

from connect import *
from collections import Counter
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../common_processing'))
from CommonModules import create_new_patient_folder


def create_plan_check_csv():
    case = get_current("Case")
    plan = get_current("Plan")
    patient = get_current("Patient")
    Pt_name = patient.Name
    ID = patient.PatientID

    file_path = create_new_patient_folder()
    os.chdir("M:\\")

    os.chdir(os.getcwd() + file_path)

    file_name = "PlanDoubleCheck_{0}_{1}.csv".format(ID, Pt_name)

    with open(file_name, "w") as file:
        file.write('Patient ID : {0}  Patient Name : {1}\n'.format(ID, Pt_name))
        file.write("Plan Name : {}\n".format(plan.Name))
        BS_List = [bs.DicomPlanLabel for bs in plan.BeamSets]
        file.write("BeamSet : ")
        for BS in BS_List:
            file.write("{} ".format(BS))
        file.write('\n')
        file.write("\n" + "CT Name : {}\n".format(plan.TreatmentCourse.TotalDose.OnDensity.FromExamination.Name))
        file.write("CT-mass Density Table : {}\n".format(
            plan.TreatmentCourse.TotalDose.OnDensity.FromExamination.EquipmentInfo.ImagingSystemReference.ImagingSystemName))
        file.write('Patient scanning position : {}\n'.format(
            plan.TreatmentCourse.TotalDose.OnDensity.FromExamination.PatientPosition))
        file.write('Patient treatment position\n')
        for BS in plan.BeamSets:
            file.write('	{0} : {1}\n'.format(BS.DicomPlanLabel, BS.PatientPosition))
        file.write("CT Center Coordinate\n")
        file.write("	POI Name : {}\n".format(case.PatientModel.StructureSets[
                                                    plan.TreatmentCourse.TotalDose.OnDensity.FromExamination.Name].LocalizationPoiGeometry.OfPoi.Name))
        coo = case.PatientModel.StructureSets[
            plan.TreatmentCourse.TotalDose.OnDensity.FromExamination.Name].LocalizationPoiGeometry.Point
        file.write('	X : {0:.2f} Y : {1:.2f} Z : {2:.2f}\n'.format(coo.x, coo.z, -coo.y))
        file.write('\nIsocenter Coordinate\n')
        for Beam_set in plan.BeamSets:
            file.write('	BeamSet Name : {}\n'.format(Beam_set.DicomPlanLabel))
            tmp_Beam_List = sorted(Beam_set.Beams, key=lambda x: x.Number)
            for beam in tmp_Beam_List:
                file.write('		Beam Name : {}\n'.format(beam.Name))
                BIC = beam.Isocenter.Position
                file.write('		X : {0:.2f} Y : {1:.2f} Z : {2:.2f}\n'.format(BIC.x, BIC.z, -BIC.y))
        file.write("\nDensityOverrides\n")
        for OverrideROI in plan.TreatmentCourse.TotalDose.OnDensity.DensityOverrides:
            ROI = OverrideROI.RoiGeometry.OfRoi
            file.write("	ROI Name : {}\n".format(ROI.Name))
            file.write("	ROI Material\n")
            file.write("		Material Name : {}\n".format(ROI.RoiMaterial.OfMaterial.Name))
            file.write("		Mass Density : {}\n".format(ROI.RoiMaterial.OfMaterial.MassDensity))
        file.write('\n' + 'Beam Parameters\n')
        for beam_set in plan.BeamSets:
            file.write("BeamSet Name : {}\n".format(beam_set.DicomPlanLabel))
            file.write("Treatment Technique : {}\n".format(beam_set.DeliveryTechnique))
            file.write("Treatment Machine : {}\n".format(beam_set.MachineReference.MachineName))
            tmp_Beam_List = sorted(beam_set.Beams, key=lambda x: x.Number)
            for beam in tmp_Beam_List:
                file.write("Beam Name : {}\n".format(beam.Name))
                file.write("	Gantry Angle : {}\n".format(beam.GantryAngle))
                file.write("	Couch Angle : {}\n".format(beam.CouchRotationAngle))
                file.write("	Snout Position : {}\n".format(beam.SnoutPosition))
                file.write("	Snout ID : {}\n".format(beam.SnoutId))
                file.write("	Spot Tune ID : {}\n".format(beam.Segments[0].Spots.SpotTuneId))
                file.write(
                    "	Range Shifter : {}\n".format("No" if beam.RangeShifterId is None else beam.RangeShifterId))
                file.write("	Range Modulator : {}\n".format(
                    "No" if beam.RangeModulatorId == '00000000-0000-0000-0000-000000000000' else beam.RangeModulatorId))
                file.write(
                    "	Block : {}\n".format("No" if len(Counter(beam.Blocks).most_common()) == 0 else beam.Blocks))
                file.write("\n")
        voxel_size = plan.TreatmentCourse.TotalDose.InDoseGrid.VoxelSize
        file.write("Dose Grid[x,y,z] : [{0},{1},{2}]\n".format(voxel_size.x, voxel_size.y, voxel_size.z))
        file.write("Accurate Dose Algorithm : {}\n".format(
            plan.TreatmentCourse.TotalDose.DoseValues.AlgorithmProperties.DoseAlgorithm))
        file.write("Minimum MU >=0.0105MU\n")
        for beam_set in plan.BeamSets:
            SpotMU = []
            for Beams in beam_set.Beams:
                for Segment in Beams.Segments:
                    for Spot_Weight in Segment.Spots.Weights:
                        SpotMU.append(Beams.BeamMU * Spot_Weight)
            file.write("	{0} : {1:.4f}MU\n".format(beam_set.DicomPlanLabel, min(SpotMU)))
        file.write("\nRobustness\n")
        for PlanOptimization in plan.PlanOptimizations:
            file.write("\nOptimized BeamSet\n ")
            for POBeamSet in PlanOptimization.OptimizedBeamSets:
                file.write(POBeamSet.DicomPlanLabel + "\n")
            file.write("	Robustness Setting\n")
            file.write('		Superior : {}\n'.format(
                PlanOptimization.OptimizationParameters.RobustnessParameters.PositionUncertaintyParameters.PositionUncertaintySuperior))
            file.write('		Inferior : {}\n'.format(
                PlanOptimization.OptimizationParameters.RobustnessParameters.PositionUncertaintyParameters.PositionUncertaintyInferior))
            file.write('		Right : {}\n'.format(
                PlanOptimization.OptimizationParameters.RobustnessParameters.PositionUncertaintyParameters.PositionUncertaintyRight))
            file.write('		Left : {}\n'.format(
                PlanOptimization.OptimizationParameters.RobustnessParameters.PositionUncertaintyParameters.PositionUncertaintyLeft))
            file.write('		Anterior : {}\n'.format(
                PlanOptimization.OptimizationParameters.RobustnessParameters.PositionUncertaintyParameters.PositionUncertaintyAnterior))
            file.write('		Posterior : {}\n'.format(
                PlanOptimization.OptimizationParameters.RobustnessParameters.PositionUncertaintyParameters.PositionUncertaintyPosterior))
            file.write('		DensityUncertainty : {}%\n'.format(
                PlanOptimization.OptimizationParameters.RobustnessParameters.DensityUncertaintyParameters.DensityUncertainty * 100))
        file.write("\nPrescription\n")
        for beam_set in plan.BeamSets:
            file.write("BeamSet : {}\n".format(beam_set.DicomPlanLabel))
            file.write("	Target : {}\n".format(beam_set.Prescription.PrimaryDosePrescription.OnStructure.Name))
            file.write("	Prescription : {}\n".format(
                "D50%" if beam_set.Prescription.PrimaryDosePrescription.PrescriptionType == "MedianDose" else beam_set.Prescription.PrimaryDosePrescription.PrescriptionType))
            file.write("	{0} cGyRBE/fr. * {1} fr.\n".format(
                beam_set.Prescription.PrimaryDosePrescription.DoseValue / beam_set.FractionationPattern.NumberOfFractions,
                beam_set.FractionationPattern.NumberOfFractions))


# test
if __name__ == '__main__':
    create_plan_check_csv()
