"""This module only works with IronPython"""
from connect import *
import os
import sys
import wpf
from System.Windows import *
from System.Windows.Controls import *
from System.Windows.Data import *


class CopyPlanSetting:
    def __init__(self):
        self.PlanName = ''
        self.BeamSets = []


class BeamSetPrameter:
    def __init__(self, BSName):
        self.BeamSetName = BSName
        self.IsInitial = True
        self.IsBoost = False


class ReportSettingForm(Window):
    def __init__(self, CopyPlanData):
        wpf.LoadComponent(self, os.path.join(os.path.dirname(__file__),'./xaml/CopyPlanForReportSetting.xaml'))
        self.Topmost = True
        self.WindowStartupLocation = WindowStartupLocation.CenterScreen
        self.DataContext = CopyPlanData

    def CreateCopyPlanClick(self, sender, event):
        self.DialogResult = True

    def CancelClick(self, sender, event):
        self.DialogResult = False


def create_plan_for_report():
    """This function copies the selected plan and splits it into initial plan and boost plan"""
    patient = get_current("Patient")
    case = get_current("Case")
    CopyPlanList = []
    for tmpPlan in case.TreatmentPlans:
        tmpSetting = CopyPlanSetting()
        tmpSetting.PlanName = tmpPlan.Name
        for tmpBeamSet in tmpPlan.BeamSets:
            tmpBSetting = BeamSetPrameter(tmpBeamSet.DicomPlanLabel)
            tmpSetting.BeamSets.append(tmpBSetting)
        CopyPlanList.append(tmpSetting)

    form = ReportSettingForm(CopyPlanList)
    form.ShowDialog()

    if form.DialogResult == False:
        sys.exit()

    ReportPlanData = form.CopyPlanCombo.SelectedItem

    case.CopyPlan(PlanName=ReportPlanData.PlanName,
                  NewPlanName="InitialPlanForReport_{}".format(ReportPlanData.PlanName))
    InitialPlan = case.TreatmentPlans["InitialPlanForReport_{}".format(ReportPlanData.PlanName)]
    case.CopyPlan(PlanName=ReportPlanData.PlanName, NewPlanName="BoostPlanForReport_{}".format(ReportPlanData.PlanName))
    BoostPlan = case.TreatmentPlans["BoostPlanForReport_{}".format(ReportPlanData.PlanName)]

    for PlanBS, IniBS, BooBS in zip(case.TreatmentPlans[ReportPlanData.PlanName].BeamSets, InitialPlan.BeamSets,
                                    BoostPlan.BeamSets):
        IniBS.DicomPlanLabel = PlanBS.DicomPlanLabel
        BooBS.DicomPlanLabel = PlanBS.DicomPlanLabel

    for BS in ReportPlanData.BeamSets:
        if BS.IsInitial:
            BoostPlan.BeamSets[BS.BeamSetName].DeleteBeamSet()
        elif BS.IsBoost:
            InitialPlan.BeamSets[BS.BeamSetName].DeleteBeamSet()

    # PL = form.CopyPlanCombo.SelectedItem
    # print(PL.PlanName)
    # for BS in PL.BeamSets:
    # print(BS.BeamSetName)
    # print(BS.IsInitial)
    # print(BS.IsBoost)

    patient.Save()


# test
if __name__ == '__main__':
    create_plan_for_report()
