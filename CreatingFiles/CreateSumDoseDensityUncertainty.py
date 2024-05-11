# import sys
# sys.path.append("DirectoryPath")
from connect import *


class DoseDistributions:

    def __init__(self):
        self.dose_distribution_list = []


def create_sum_dose_Density_Uncertainty():
    case = get_current('Case')
    DoseDistributionsClass = DoseDistributions()
    for FractionEvaluation in case.TreatmentDelivery.FractionEvaluations:
        for DoseOnExamination in FractionEvaluation.DoseOnExaminations:
            try:
                for DoseEvaluation in DoseOnExamination.DoseEvaluations:
                    if DoseEvaluation.PerturbedDoseProperties is not None:
                        if DoseEvaluation.PerturbedDoseProperties.IsoCenterShift.x == 0:
                            if DoseEvaluation.PerturbedDoseProperties.IsoCenterShift.y == 0:
                                if DoseEvaluation.PerturbedDoseProperties.IsoCenterShift.z == 0:
                                    DoseDistributionsClass.dose_distribution_list.append(DoseEvaluation)
            except:
                continue
    for dd in DoseDistributionsClass.dose_distribution_list:
        print(dd.PerturbedDoseProperties.RelativeDensityShift)

if __name__ == '__main__':
    create_sum_dose_Density_Uncertainty()
