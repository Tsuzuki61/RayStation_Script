"""This Module works only with IronPython
# Using Json Class"""
from connect import *
import collections
import re
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../Data'))
import wpf
from System.Windows import *
from System.Windows.Controls import *
from System.Windows.Data import *
from decimal import *
import json
from testPyfiles.objectbuilder import ObjectBuilder, MAPPING_ROOT_CLASS

case = get_current("Case")
beam_set = get_current("BeamSet")
plan = get_current("Plan")


class CGForm(Window):
    def __init__(self, ClinicalGoalJson):
        wpf.LoadComponent(self, os.path.join(os.path.dirname(__file__), './xaml/ClinicalGoalUseClass.xaml'))
        self.Topmost = True
        # Start up window at the center of the screen.
        self.WindowStartupLocation = WindowStartupLocation.CenterScreen
        self.DataContext = ClinicalGoalJson
        self.BeamSetPrescriptionDose = beam_set.Prescription.PrimaryDosePrescription.DoseValue
        self.Total_Prescription_Dose = 0
        for beamset in plan.BeamSets:
            self.Total_Prescription_Dose += beamset.Prescription.PrimaryDosePrescription.DoseValue

    def ClearClinicalGoals(self):
        for EF in plan.TreatmentCourse.EvaluationSetup.EvaluationFunctions:
            plan.TreatmentCourse.EvaluationSetup.DeleteClinicalGoal(FunctionToRemove=EF)

    def CancelClicked(self, sender, event):
        self.DialogResult = False

    def PlanClicked(self, sender, event):
        self.ClearClinicalGoals()
        TargetRoiList = []
        for BS in plan.BeamSets:
            if not BS.Prescription.PrimaryDosePrescription.OnStructure.Name in TargetRoiList:
                TargetRoiList.append(BS.Prescription.PrimaryDosePrescription.OnStructure.Name)
        for roi in self.ProtocolCombo.SelectedValue:
            if roi.RoiName == "CTV":
                for TargetRoi in TargetRoiList:
                    for Constraint in roi.Constraint:
                        try:
                            plan.TreatmentCourse.EvaluationSetup.AddClinicalGoal(RoiName=TargetRoi,
                                                                                 GoalCriteria=Constraint.GoalCriteria,
                                                                                 GoalType=Constraint.GoalType,
                                                                                 AcceptanceLevel=float(Decimal(
                                                                                     self.Total_Prescription_Dose) * Decimal(
                                                                                     Constraint.AcceptanceLevel)),
                                                                                 ParameterValue=float(Decimal(
                                                                                     Constraint.ParameterValue)),
                                                                                 IsComparativeGoal=False,
                                                                                 Priority=2147483647)
                        except:
                            break
            else:
                for Constraint in roi.Constraint:
                    plan.TreatmentCourse.EvaluationSetup.AddClinicalGoal(RoiName=roi.RoiName,
                                                                         GoalCriteria=Constraint.GoalCriteria,
                                                                         GoalType=Constraint.GoalType,
                                                                         AcceptanceLevel=float(
                                                                             Constraint.AcceptanceLevel),
                                                                         ParameterValue=float(
                                                                             Constraint.ParameterValue),
                                                                         IsComparativeGoal=False, Priority=2147483647)
        self.DialogResult = True

    def BeamSetClicked(self, sender, event):
        self.ClearClinicalGoals()

        ReCompileVolume = re.compile('.*(Volume)$')
        ReCompileDose = re.compile('.*(Dose)$')
        TargetRoiList = []

        for BS in plan.BeamSets:
            if not BS.Prescription.PrimaryDosePrescription.OnStructure.Name in TargetRoiList:
                TargetRoiList.append(BS.Prescription.PrimaryDosePrescription.OnStructure.Name)
        for roi in self.ProtocolCombo.SelectedValue:
            # Target AcceptanceLevel is rate to prescription dose
            if roi.RoiName == "CTV":
                for TargetRoi in TargetRoiList:
                    for Constraint in roi.Constraint:
                        try:
                            plan.TreatmentCourse.EvaluationSetup.AddClinicalGoal(RoiName=TargetRoi,
                                                                                 GoalCriteria=Constraint.GoalCriteria,
                                                                                 GoalType=Constraint.GoalType,
                                                                                 AcceptanceLevel=float(
                                                                                     self.BeamSetPrescriptionDose * float(
                                                                                         Constraint.AcceptanceLevel)),
                                                                                 ParameterValue=float(
                                                                                     Constraint.ParameterValue),
                                                                                 IsComparativeGoal=False,
                                                                                 Priority=2147483647)
                        except:
                            break
            else:
                for Constraint in roi.Constraint:
                    if ReCompileVolume.match(Constraint.GoalType):
                        plan.TreatmentCourse.EvaluationSetup.AddClinicalGoal(RoiName=roi.RoiName,
                                                                             GoalCriteria=Constraint.GoalCriteria,
                                                                             GoalType=Constraint.GoalType,
                                                                             AcceptanceLevel=float((
                                                                                                           self.BeamSetPrescriptionDose / self.Total_Prescription_Dose) * float(
                                                                                 Constraint.AcceptanceLevel)),
                                                                             ParameterValue=float(
                                                                                 Constraint.ParameterValue),
                                                                             IsComparativeGoal=False,
                                                                             Priority=2147483647)
                    elif ReCompileDose.match(Constraint.GoalType):
                        plan.TreatmentCourse.EvaluationSetup.AddClinicalGoal(RoiName=roi.RoiName,
                                                                             GoalCriteria=Constraint.GoalCriteria,
                                                                             GoalType=Constraint.GoalType,
                                                                             AcceptanceLevel=float(
                                                                                 Constraint.AcceptanceLevel),
                                                                             ParameterValue=int((
                                                                                                        self.BeamSetPrescriptionDose / self.Total_Prescription_Dose) * float(
                                                                                 Constraint.ParameterValue)),
                                                                             IsComparativeGoal=False,
                                                                             Priority=2147483647)
        self.DialogResult = True


class Root:
    pass


class Part:
    pass


class Protocol:
    pass


class Roi:
    pass


class Constraint:
    pass


def insert_clinical_goal():
    with open(os.path.join(os.path.dirname(__file__), '../Data/NewClinicalJsonClass.json')) as f:
        ClinicalGoalJson = json.load(f, object_pairs_hook=collections.OrderedDict)

    object_mapping = {MAPPING_ROOT_CLASS: Root, 'Part': Part, 'Roi': Roi, 'Protocol': Protocol,
                      'Constraint': Constraint}

    builder = ObjectBuilder(mapping=object_mapping)
    result = builder.build(ClinicalGoalJson)

    form = CGForm(result)
    form.ShowDialog()

    if form.DialogResult == False:
        sys.exit()


# test
if __name__ == '__main__':
    insert_clinical_goal()
