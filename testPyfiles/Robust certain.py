from connect import *

case = get_current("Case")
beam_set = get_current("BeamSet")
plan = get_current("Plan")

exam_name = plan.TreatmentCourse.TotalDose.OnDensity.FromExamination.Name

Robust_para_Dict = {}

for opt in plan.PlanOptimizations:
	beamset_name = []
	for OBS in opt.OptimizedBeamSets:
		beamset_name.append(OBS.DicomPlanLabel)
	robust_para = {"Ant":format(opt.OptimizationParameters.RobustnessParameters.PositionUncertaintyAnterior,'.2f'),"Pos":format(opt.OptimizationParameters.RobustnessParameters.PositionUncertaintyPosterior,'.2f'),"Sup":format(opt.OptimizationParameters.RobustnessParameters.PositionUncertaintySuperior,'.2f'),"Inf":format(opt.OptimizationParameters.RobustnessParameters.PositionUncertaintyInferior,'.2f'),"Left":format(opt.OptimizationParameters.RobustnessParameters.PositionUncertaintyLeft,'.2f'),"Right":format(opt.OptimizationParameters.RobustnessParameters.PositionUncertaintyRight,'.2f'),"D_Unceretain":format(opt.OptimizationParameters.RobustnessParameters.DensityUncertainty,'.4f')}
	if len(beamset_name) == 1:
		Robust_para_Dict.setdefault(beamset_name[0],robust_para)
	else:
		for BSN in beamset_name:
			Robust_para_Dict.setdefault(BSN,robust_para)
for key in Robust_para_Dict.keys():
	x_shift = [float(Robust_para_Dict[key]['Left']),-float(Robust_para_Dict[key]['Right'])]
	y_shift = [-float(Robust_para_Dict[key]['Ant']), float(Robust_para_Dict[key]['Pos'])]
	z_shift = [float(Robust_para_Dict[key]['Sup']), -float(Robust_para_Dict[key]['Inf'])]
	d_shift = [0, float(Robust_para_Dict[key]['D_Unceretain']) , -float(Robust_para_Dict[key]['D_Unceretain'])]

	plan.BeamSets[key].ComputePerturbedDose(DensityPerturbation=float(Robust_para_Dict[key]['D_Unceretain']), IsocenterShift={ 'x': 0, 'y': 0, 'z': 0 }, OnlyOneDosePerImageSet=False, AllowGridExpansion=False, ExaminationNames=[exam_name], FractionNumbers=[0], ComputeBeamDoses=True)
	plan.BeamSets[key].ComputePerturbedDose(DensityPerturbation=-float(Robust_para_Dict[key]['D_Unceretain']), IsocenterShift={ 'x': 0, 'y': 0, 'z': 0 }, OnlyOneDosePerImageSet=False, AllowGridExpansion=False, ExaminationNames=[exam_name], FractionNumbers=[0], ComputeBeamDoses=True)

	for d in d_shift:
		for x in x_shift:
			for y in y_shift:
				for z in z_shift:
					plan.BeamSets[key].ComputePerturbedDose(DensityPerturbation=d, IsocenterShift={ 'x': x, 'y': y, 'z': z }, OnlyOneDosePerImageSet=False, AllowGridExpansion=False, ExaminationNames=[exam_name], FractionNumbers=[0], ComputeBeamDoses=True)

