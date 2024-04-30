from connect import *


def perturbed_dose_to_shift_robust_value():
    """
    Generate multiple perturbed dose distributions based on the specified amount of move from the Robust value setting of the plan
    """
    # Connection with RayStation
    plan = get_current("Plan")

    exam_name = plan.TreatmentCourse.TotalDose.OnDensity.FromExamination.Name

# -----# Generate a dictionary of robust value parameters-----
    Robust_para_Dict = {}

    for opt in plan.PlanOptimizations:
        beamset_name = []
        for OBS in opt.OptimizedBeamSets:
            beamset_name.append(OBS.DicomPlanLabel)
        robust_para = {
            "Ant": format(
                opt.OptimizationParameters.RobustnessParameters.PositionUncertaintyParameters.PositionUncertaintyAnterior,
                '.2f'),
            "Pos": format(
                opt.OptimizationParameters.RobustnessParameters.PositionUncertaintyParameters.PositionUncertaintyPosterior,
                '.2f'),
            "Sup": format(
                opt.OptimizationParameters.RobustnessParameters.PositionUncertaintyParameters.PositionUncertaintySuperior,
                '.2f'),
            "Inf": format(
                opt.OptimizationParameters.RobustnessParameters.PositionUncertaintyParameters.PositionUncertaintyInferior,
                '.2f'),
            "Left": format(
                opt.OptimizationParameters.RobustnessParameters.PositionUncertaintyParameters.PositionUncertaintyLeft,
                '.2f'),
            "Right": format(
                opt.OptimizationParameters.RobustnessParameters.PositionUncertaintyParameters.PositionUncertaintyRight,
                '.2f'),
            "D_Unceretain": format(
                opt.OptimizationParameters.RobustnessParameters.DensityUncertaintyParameters.DensityUncertainty, '.4f')}
        if len(beamset_name) == 1:
            Robust_para_Dict.setdefault(beamset_name[0], robust_para)
        else:
            for BSN in beamset_name:
                Robust_para_Dict.setdefault(BSN, robust_para)

# -----Generate multiple perturbed dose distribution-----
    for key in Robust_para_Dict.keys():
        x_shift = [-float(Robust_para_Dict[key]['Right']), float(Robust_para_Dict[key]['Left'])]
        y_shift = [float(Robust_para_Dict[key]['Pos']), -float(Robust_para_Dict[key]['Ant'])]
        z_shift = [-float(Robust_para_Dict[key]['Inf']), float(Robust_para_Dict[key]['Sup'])]
        d_shift = [0, float(Robust_para_Dict[key]['D_Unceretain']), -float(Robust_para_Dict[key]['D_Unceretain'])]

        plan.BeamSets[key].ComputePerturbedDose(DensityPerturbation=float(Robust_para_Dict[key]['D_Unceretain']),
                                                PatientShift={'x': 0, 'y': 0, 'z': 0}, OnlyOneDosePerImageSet=False,
                                                AllowGridExpansion=False, ExaminationNames=[exam_name],
                                                FractionNumbers=[0], ComputeBeamDoses=True)
        plan.BeamSets[key].ComputePerturbedDose(DensityPerturbation=-float(Robust_para_Dict[key]['D_Unceretain']),
                                                PatientShift={'x': 0, 'y': 0, 'z': 0}, OnlyOneDosePerImageSet=False,
                                                AllowGridExpansion=False, ExaminationNames=[exam_name],
                                                FractionNumbers=[0], ComputeBeamDoses=True)

        for d in d_shift:
            for x in x_shift:
                for y in y_shift:
                    for z in z_shift:
                        plan.BeamSets[key].ComputePerturbedDose(DensityPerturbation=d,
                                                                PatientShift={'x': x, 'y': y, 'z': z},
                                                                OnlyOneDosePerImageSet=False, AllowGridExpansion=False,
                                                                ExaminationNames=[exam_name], FractionNumbers=[0],
                                                                ComputeBeamDoses=True)


# test
if __name__ == '__main__':
    perturbed_dose_to_shift_robust_value()
