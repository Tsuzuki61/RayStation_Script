# Script recorded 03 Dec 2018

#   RayStation version: 6.2.0.7
#   Selected patient: ...

from connect import *
import sys
sys.path.append("F:\Proton\RayStation\Script\create file")
from RayForm import DeformForm
from System.Windows.Forms import *
from ctypes import *
from decimal import *

case = get_current("Case")
exam = get_current("Examination")

msgbox = windll.user32.MessageBoxW

plan_list =[plan.Name for plan in case.TreatmentPlans]
if type(case.TreatmentPlans) !='NoneType':
 plan_list =[plan.Name for plan in case.TreatmentPlans]
 if "Prostate" in plan_list:
  msgbox(None,'There is already Plan named "Prostate"','Warning',0x0000040)
  sys.exit()

plan = case.AddNewPlan(PlanName="Prostate", PlannedBy="", Comment="", ExaminationName=exam.Name, AllowDuplicateNames=False)
plan.SetDefaultDoseGrid(VoxelSize={ 'x': 0.2, 'y': 0.2, 'z': 0.2 })
A_1 = plan.AddNewBeamSet(Name="Prostate_A_1", ExaminationName=exam.Name, MachineName="CGTRn_03", Modality="Protons", TreatmentTechnique="ProtonPencilBeamScanning", PatientPosition="HeadFirstSupine", NumberOfFractions=20, CreateSetupBeams=False, UseLocalizationPointAsSetupIsocenter=False, Comment="", RbeModelReference=None, EnableDynamicTrackingForVero=False)

A_2 = plan.AddNewBeamSet(Name="Prostate_A_2", ExaminationName=exam.Name, MachineName="CGTRn_03", Modality="Protons", TreatmentTechnique="ProtonPencilBeamScanning", PatientPosition="HeadFirstSupine", NumberOfFractions=19, CreateSetupBeams=False, UseLocalizationPointAsSetupIsocenter=False, Comment="", RbeModelReference=None, EnableDynamicTrackingForVero=False)

# Unscriptable Action 'Change context' Completed : SetContextToRadiationSetAction(...)

A_1.AddDosePrescriptionToRoi(RoiName="CTV", DoseVolume=0, PrescriptionType="MedianDose", DoseValue=4000, RelativePrescriptionLevel=1, AutoScaleDose=False)

# Unscriptable Action 'Change context' Completed : SetContextToRadiationSetAction(...)

A_2.AddDosePrescriptionToRoi(RoiName="CTV", DoseVolume=0, PrescriptionType="MedianDose", DoseValue=3800, RelativePrescriptionLevel=1, AutoScaleDose=False)


CTV_center = plan.TreatmentCourse.TotalDose.OnDensity.RoiListSource.StructureSets[plan.TreatmentCourse.TotalDose.OnDensity.FromExamination.Name].RoiGeometries['CTV'].GetCenterOfRoi()
Iso_center = {'x':Decimal(str(CTV_center.x)).quantize(Decimal('0.1'),rounding=ROUND_HALF_UP),'y':Decimal(str(CTV_center.y)).quantize(Decimal('0.1'),rounding=ROUND_HALF_UP),'z':Decimal(str(CTV_center.z)).quantize(Decimal('0.1'),rounding=ROUND_HALF_UP)}
PrA01 = A_1.CreatePBSIonBeam(SnoutId="NoSnout", SpotTuneId="3.0", RangeShifter=None, MinimumAirGap=None, MetersetRateSetting="", IsocenterData={ 'Position': { 'x': float(Iso_center['x']), 'y': float(Iso_center['y']), 'z': float(Iso_center['z']) }, 'NameOfIsocenterToRef': "", 'Name': "Prostate_A_1", 'Color': "98, 184, 234" }, Name="PrA01", Description="G090C000", GantryAngle=90, CouchAngle=0, CollimatorAngle=0)

PrA02 = A_2.CreatePBSIonBeam(SnoutId="NoSnout", SpotTuneId="3.0", RangeShifter=None, MinimumAirGap=None, MetersetRateSetting="", IsocenterData={ 'Position': { 'x': float(Iso_center['x']), 'y': float(Iso_center['y']), 'z': float(Iso_center['z']) }, 'NameOfIsocenterToRef': "", 'Name': "Prostate_A_2", 'Color': "98, 184, 234" }, Name="PrA02", Description="G090C180", GantryAngle=90, CouchAngle=180, CollimatorAngle=0)

# CompositeAction ends 

#Next --> Optimization code

plan_opt_list = [opt for opt in plan.PlanOptimizations]

for plan_opt in plan_opt_list:
 plan_opt.AddOptimizationFunction(FunctionType="UniformDose", RoiName="CTV", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=True, RestrictToBeamSet=None, UseRbeDose=False)
 plan_opt.Objective.ConstituentFunctions[0].DoseFunctionParameters.DoseLevel = plan_opt.OptimizedBeamSets[0].Prescription.PrimaryDosePrescription.DoseValue
 plan_opt.Objective.ConstituentFunctions[0].DoseFunctionParameters.Weight = 10
 plan_opt.AddOptimizationFunction(FunctionType="DoseFallOff", RoiName="External", IsConstraint=False, RestrictAllBeamsIndividually=False, RestrictToBeam=None, IsRobust=False, RestrictToBeamSet=None, UseRbeDose=False)
 plan_opt.Objective.ConstituentFunctions[1].DoseFunctionParameters.HighDoseLevel = plan_opt.OptimizedBeamSets[0].Prescription.PrimaryDosePrescription.DoseValue
# CompositeAction ends 
 plan_opt.OptimizationParameters.SaveRobustnessParameters(PositionUncertaintyAnterior=0.3, PositionUncertaintyPosterior=0.2, PositionUncertaintySuperior=0.3, PositionUncertaintyInferior=0.3, PositionUncertaintyLeft=0.3, PositionUncertaintyRight=0.3, DensityUncertainty=0.035, IndependentBeams=False, ComputeExactScenarioDoses=False, NamesOfNonPlanningExaminations=[])
 plan_opt.RunOptimization()
 

