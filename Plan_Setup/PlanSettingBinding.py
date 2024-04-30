import collections
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../Data'))
import wpf
from System.Windows import *
from System.Windows.Controls import *
from System.Windows.Data import *
import json
from testPyfiles.objectbuilder import ObjectBuilder, MAPPING_ROOT_CLASS, ClassToJason_method
import shutil
import datetime


class AddSiteForm(Window):
    def __init__(self, jsonClass):
        wpf.LoadComponent(self, os.path.join(os.path.dirname(__file__), './xaml/AddNew.xaml'))
        self.Topmost = True
        # Start up window at the center of the screen.
        self.MessageText.Text = "Please input the irradiation site"
        self.Title="Add new site"
        self.WindowStartupLocation = WindowStartupLocation.CenterScreen
        self.DataContext = jsonClass

    def AddClicked(self, sender, event):
        if self.NewTextBox.Text == "":
            return
        AddPart = Part()
        AddPart.PartName = self.NewTextBox.Text
        AddPart.PlanSetting = PlanSetting()
        AddPart.PlanSetting.DoseGrid = DoseGrid()
        AddPart.PlanSetting.DoseGrid.x = 0.2
        AddPart.PlanSetting.DoseGrid.y = 0.2
        AddPart.PlanSetting.DoseGrid.z = 0.2
        AddPart.PlanSetting.PlanProtocol = []
        self.DataContext.Part.append(AddPart)
        self.DialogResult = True

    def CancelClicked(self, sender, event):
        self.DialogResult = False


class AddProtocolForm(Window):
    def __init__(self, jsonClass):
        wpf.LoadComponent(self, os.path.join(os.path.dirname(__file__), './xaml/AddNew.xaml'))
        self.Topmost = True
        # Start up window at the center of the screen.
        self.MessageText.Text = "Please input the Protocol Name"
        self.Title='Add new protocol'
        self.WindowStartupLocation = WindowStartupLocation.CenterScreen
        self.DataContext = jsonClass

    def AddClicked(self, sender, event):
        if self.NewTextBox.Text == "":
            return
        AddProtocol = PlanProtocol()
        AddProtocol.ProtocolName = self.NewTextBox.Text
        AddProtocol.BeamSet = []
        self.DataContext.append(AddProtocol)
        self.DialogResult = True

    def CancelClicked(self, sender, event):
        self.DialogResult = False


class AddBeamSetForm(Window):
    def __init__(self, jsonClass):
        wpf.LoadComponent(self, os.path.join(os.path.dirname(__file__), './xaml/AddNew.xaml'))
        self.Topmost = True
        # Start up window at the center of the screen.
        self.MessageText.Text = "Please input the BeamSet Name"
        self.Title='Add new beamset'
        self.WindowStartupLocation = WindowStartupLocation.CenterScreen
        self.DataContext = jsonClass

    def AddClicked(self, sender, event):
        if self.NewTextBox.Text == "":
            return
        AddBeamSet = BeamSet()
        AddBeamSet.Name = self.NewTextBox.Text
        AddBeamSet.NumberOfFractions = ""
        AddBeamSet.DoseValue = ""
        AddBeamSet.Dose_fr = ""
        AddBeamSet.Beams = []
        AddBeamSet.RobustnessSetting = RobustnessSetting()
        AddBeamSet.RobustnessSetting.Sup = 0.1
        AddBeamSet.RobustnessSetting.Inf = 0.1
        AddBeamSet.RobustnessSetting.R = 0.1
        AddBeamSet.RobustnessSetting.L = 0.1
        AddBeamSet.RobustnessSetting.Ant = 0.1
        AddBeamSet.RobustnessSetting.Pos = 0.1
        AddBeamSet.RobustnessSetting.Uncertainty = 0.035
        self.DataContext.append(AddBeamSet)
        self.DialogResult = True

    def CancelClicked(self, sender, event):
        self.DialogResult = False


class PSForm(Window):
    def __init__(self, PlanSettingJson):
        wpf.LoadComponent(self, os.path.join(os.path.dirname(__file__), './xaml/PlanSettingBinding.xaml'))
        self.Topmost = True
        # Start up window at the center of the screen.
        self.WindowStartupLocation = WindowStartupLocation.CenterScreen
        self.DataContext = PlanSettingJson
        self.DataChangeFlag = False

    def Refresh(self):
        self.DataContext = None
        global result
        self.DataContext = result
        self.DataChangeFlag = True

    def TextBoxLostFocus(self, sender, event):
        tmpSelected = self.BeamSetTabControl.SelectedItem
        self.Refresh()
        self.BeamSetTabControl.SelectedItem = tmpSelected

    def OKClicked(self, sender, event):
        self.DialogResult = True

    def CancelClicked(self, sender, event):
        self.DialogResult = False

    def AddNewSiteClicked(self, sender, event):
        AddForm = AddSiteForm(self.DataContext)
        AddForm.ShowDialog()
        if AddForm.DialogResult:
            self.Refresh()
            self.PartCombo.SelectedItem = self.PartCombo.ItemsSource[-1]

    def DeleteSiteClicked(self, sender, event):
        if not self.PartCombo.SelectedItem == None:
            self.DataContext.Part.remove(self.PartCombo.SelectedItem)
            self.PartCombo.SelectedItem = None
            self.Refresh()

    def AddNewProtocolClicked(self, sender, event):
        if not self.PartCombo.SelectedItem == None:
            AddForm = AddProtocolForm(self.ProtocolCombo.ItemsSource)
            AddForm.ShowDialog()
            if AddForm.DialogResult:
                self.Refresh()
                if len(self.ProtocolCombo.ItemsSource) == 0:
                    self.ProtocolCombo.SelectedItem = self.ProtocolCombo.ItemsSource[0]
                else:
                    self.ProtocolCombo.SelectedItem = self.ProtocolCombo.ItemsSource[-1]
            self.AddNewBeamSetClicked(sender, event)

    def DeleteProtocolClicked(self, sender, event):
        if not self.ProtocolCombo.SelectedItem == None:
            self.ProtocolCombo.ItemsSource.remove(self.ProtocolCombo.SelectedItem)
            self.ProtocolCombo.SelectedItem = None
            self.Refresh()

    def ProtocolComboChanged(self, sender, event):
        if not self.ProtocolCombo.SelectedItem == None and not len(
                self.ProtocolCombo.SelectedItem.BeamSet) == 0 and not self.BeamSetTabControl.ItemsSource == None:
            self.BeamSetTabControl.SelectedItem = self.BeamSetTabControl.ItemsSource[0]

    def AddNewBeamSetClicked(self, sender, event):
        if not self.ProtocolCombo.SelectedItem == None:
            AddForm = AddBeamSetForm(self.BeamSetTabControl.ItemsSource)
            AddForm.ShowDialog()
            if AddForm.DialogResult:
                self.Refresh()
                self.BeamSetTabControl.SelectedItem = self.BeamSetTabControl.ItemsSource[-1]

    def DeleteBeamSetClicked(self, sender, event):
        if not self.BeamSetTabControl.SelectedItem == None:
            self.BeamSetTabControl.ItemsSource.remove(self.BeamSetTabControl.SelectedItem)
            self.BeamSetTabControl.SelectedItem = None
            self.Refresh()

    def AddNewBeam(self, sender, event):
        if not self.BeamSetTabControl.SelectedItem == None:
            selectedItem = self.BeamSetTabControl.SelectedItem
            AddBeam = Beams()
            AddBeam.BeamName = ""
            AddBeam.Description = ""
            AddBeam.GantryAngle = ""
            AddBeam.CouchAngle = ""
            self.BeamSetTabControl.SelectedItem.Beams.append(AddBeam)
            self.Refresh()
            self.BeamSetTabControl.SelectedItem = selectedItem

    def DoseValueChanged(self, sender, event):
        if self.BeamSetTabControl.SelectedItem.NumberOfFractions <> 0 and not self.BeamSetTabControl.SelectedItem.NumberOfFractions == "":
            self.BeamSetTabControl.SelectedItem.Dose_fr = int(int(self.BeamSetTabControl.SelectedItem.DoseValue) / int(
                self.BeamSetTabControl.SelectedItem.NumberOfFractions))

    def Dose_frChanged(self, sender, event):
        if not self.BeamSetTabControl.SelectedItem.NumberOfFractions == "":
            self.BeamSetTabControl.SelectedItem.DoseValue = int(int(self.BeamSetTabControl.SelectedItem.Dose_fr) * int(
                self.BeamSetTabControl.SelectedItem.NumberOfFractions))


class Root:
    pass


class Part:
    pass


class PlanSetting:
    pass


class DoseGrid:
    pass


class PlanProtocol:
    pass


class BeamSet:
    pass


class Beams:
    pass


class RobustnessSetting:
    pass


def plan_setting():
    with open(os.path.join(os.path.dirname(__file__),'../Data/PlanSettingClass.json')) as f:
        PlanSettingJson = json.load(f, object_pairs_hook=collections.OrderedDict)

    object_mapping = {MAPPING_ROOT_CLASS: Root, 'Part': Part, 'PlanSetting': PlanSetting, 'DoseGrid': DoseGrid,
                      'PlanProtocol': PlanProtocol, 'BeamSet': BeamSet, 'Beams': Beams,
                      'RobustnessSetting': RobustnessSetting}
    builder = ObjectBuilder(mapping=object_mapping)
    global result
    result = builder.build(PlanSettingJson)

    form = PSForm(result)
    form.ShowDialog()

    if form.DialogResult:
        OriginalFilePath = os.path.join(os.path.dirname(__file__), '../Data/PlanSettingClass.json')
        BackupFilePath = os.path.join(os.path.dirname(__file__),'../Data/BackupFiles/PlanSetting/PlanSettingClass_{:%Y%m%d_%H%M%S}.json'.format(
            datetime.datetime.now()))
        shutil.copy(OriginalFilePath, BackupFilePath)

        with open(os.path.join(os.path.dirname(__file__),'../Data/PlanSettingClass.json'), 'w') as f:
            json.dump(result, f, indent=2, default=ClassToJason_method)


# test
if __name__ == '__main__':
    plan_setting()
