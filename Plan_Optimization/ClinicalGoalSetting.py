# from connect import *
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../Data'))
import wpf
from System.Windows import *
from System.Windows.Controls import *
from System.Windows.Data import *
import json
from objectbuilder import ObjectBuilder, MAPPING_ROOT_CLASS, ClassToJason_method
import datetime


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


class msgBox(Window):
    def __init__(self):
        wpf.LoadComponent(self, os.path.join(os.path.dirname(__file__), './xaml/messagebox.xaml'))
        self.Topmost = True
        # Start up window at the center of the screen.
        self.WindowStartupLocation = WindowStartupLocation.CenterScreen
        self.Caption.Title = "Confirmation"
        textblock1 = TextBlock()
        textblock1.Text = "There are changes in the data"
        textblock1.Margin = Thickness(5)
        textblock2 = TextBlock()
        textblock2.Text = "OverWrite it?"
        textblock2.Margin = Thickness(5)
        self.SPanel.Children.Add(textblock1)
        self.SPanel.Children.Add(textblock2)
        OKbutton = Button()
        OKbutton.Name = "OK_btn"
        OKbutton.Content = "OK"
        OKbutton.Width = 50
        OKbutton.Margin = Thickness(10)
        OKbutton.Click += self.OK_Clicked
        self.ButtomSPanel.Children.Add(OKbutton)
        CanButton = Button()
        CanButton.Name = "Cancel_btn"
        CanButton.Content = "Cancel"
        CanButton.Width = 50
        CanButton.Margin = Thickness(10)
        CanButton.Click += self.Cancel_Clicked
        self.ButtomSPanel.Children.Add(CanButton)

    def OK_Clicked(self, sender, event):
        self.DialogResult = True

    def Cancel_Clicked(self, sender, event):
        self.DialogResult = False


class AddPartForm(Window):
    def __init__(self, jsonClass):
        wpf.LoadComponent(self, os.path.join(os.path.dirname(__file__), './xaml/AddNew.xaml'))
        self.Topmost = True
        # Start up window at the center of the screen.
        self.MessageText.Text = "Please input the part of irradiation"
        self.WindowStartupLocation = WindowStartupLocation.CenterScreen
        self.DataContext = jsonClass

    def AddClicked(self, sender, event):
        if self.NewTextBox.Text == "":
            return
        AddPart = Part()
        AddPart.PartName = self.NewTextBox.Text
        AddPart.Protocol = []
        self.DataContext.Part.append(AddPart)
        self.DialogResult = True

    def CancelClicked(self, sender, event):
        self.DialogResult = False


class AddProtocolForm(Window):
    def __init__(self, jsonClass):
        wpf.LoadComponent(self, os.path.join(os.path.dirname(__file__), './xaml/AddNew.xaml'))
        self.Topmost = True
        # Start up window at the center of the screen.
        self.MessageText.Text = "Please input the Protocol name"
        self.WindowStartupLocation = WindowStartupLocation.CenterScreen
        self.DataContext = jsonClass

    def AddClicked(self, sender, event):
        if self.NewTextBox.Text == "":
            return
        AddProtocol = Protocol()
        AddProtocol.ProtocolName = self.NewTextBox.Text
        AddProtocol.Roi = []
        self.DataContext.append(AddProtocol)
        self.DialogResult = True

    def CancelClicked(self, sender, event):
        self.DialogResult = False


class AddRoiForm(Window):
    def __init__(self, jsonClass):
        wpf.LoadComponent(self, os.path.join(os.path.dirname(__file__), './xaml/AddNew.xaml'))
        self.Topmost = True
        # Start up window at the center of the screen.
        self.MessageText.Text = "Please input the Name of ROI"
        self.WindowStartupLocation = WindowStartupLocation.CenterScreen
        self.DataContext = jsonClass

    def AddClicked(self, sender, event):
        if self.NewTextBox.Text == "":
            return
        AddRoi = Roi()
        AddRoi.RoiName = self.NewTextBox.Text
        AddRoi.RoiType = ""
        AddRoi.Constraint = []
        self.DataContext.append(AddRoi)
        self.DialogResult = True

    def CancelClicked(self, sender, event):
        self.DialogResult = False


class CGForm(Window):
    def __init__(self, jsonClass):
        wpf.LoadComponent(self, os.path.join(os.path.dirname(__file__), './xaml/AddNewClinicalGoal.xaml'))
        self.Topmost = True
        # Start up window at the center of the screen.
        self.WindowStartupLocation = WindowStartupLocation.CenterScreen
        self.DataContext = jsonClass
        self.ROITypeCombo.ItemsSource = ['Target', 'OrganAtRisk']
        self.DataChangeFlag = False

    def Refresh(self):
        self.ROICombo.ItemsSource.sort(key=lambda x: x.RoiName)
        self.DataContext = None
        global result
        self.DataContext = result
        self.DataChangeFlag = True


    def SaveClicked(self, sender, event):
        if self.DataChangeFlag == True:
            msg = msgBox()
            msg.ShowDialog()
            if msg.DialogResult == False:
                return
        self.DialogResult = True

    def CancelClicked(self, sender, event):
        self.DialogResult = False

    def AddNewPartClicked(self, sender, event):
        AddForm = AddPartForm(self.DataContext)
        AddForm.ShowDialog()
        if AddForm.DialogResult:
            self.Refresh()
            self.PartCombo.SelectedItem = self.PartCombo.ItemsSource[-1]

    def DeletePartClicked(self, sender, event):
        self.DataContext.Part.remove(self.PartCombo.SelectedItem)
        self.Refresh()
        self.PartCombo.SelectedItem = None

    def AddNewProtocolClicked(self, sender, event):
        AddForm = AddProtocolForm(self.PartCombo.SelectedValue)
        AddForm.ShowDialog()
        if AddForm.DialogResult:
            self.Refresh()
            self.ProtocolCombo.SelectedItem = self.ProtocolCombo.ItemsSource[-1]

    def DeleteProtocolClicked(self, sender, event):
        self.ProtocolCombo.ItemsSource.remove(self.ProtocolCombo.SelectedItem)
        self.Refresh()
        self.ProtocolCombo.SelectedItem = None

    def AddNewROIClicked(self, sender, event):
        AddForm = AddRoiForm(self.ProtocolCombo.SelectedValue)
        AddForm.ShowDialog()
        if AddForm.DialogResult:
            self.Refresh()
            self.ROICombo.SelectedItem = self.ROICombo.ItemsSource[-1]

    def DeleteROIClicked(self, sender, event):
        self.ROICombo.ItemsSource.remove(self.ROICombo.SelectedItem)
        self.Refresh()
        self.ROICombo.SelectedItem = None

    def AddNewConstraintClicked(self, sender, event):
        AddConstraint = Constraint()
        AddConstraint.GoalCriteria = ""
        AddConstraint.AcceptanceLevel = ""
        AddConstraint.ParameterValue = ""
        AddConstraint.GoalType = ""
        self.ConstraintDataGrid.ItemsSource.append(AddConstraint)
        self.Refresh()


with open(os.path.join(os.path.dirname(__file__), '../Data/NewClinicalJsonClass.json')) as f:
    ClinicalGoalJson = json.load(f)
object_mapping = {MAPPING_ROOT_CLASS: Root, 'Part': Part, 'Roi': Roi, 'Protocol': Protocol, 'Constraint': Constraint}
builder = ObjectBuilder(mapping=object_mapping)
result = builder.build(ClinicalGoalJson)
Currentbuilder = ObjectBuilder(mapping=object_mapping)
currentjson = Currentbuilder.build(ClinicalGoalJson)

form = CGForm(result)
form.ShowDialog()
BackupFileName = 'NewClinicalJsonClass({0:%Y_%m_%d-%H_%M_%S}).json'.format(
    datetime.datetime.now())

if form.DialogResult == True and form.DataChangeFlag == True:
    with open(os.path.join(os.path.dirname(__file__), '../Data/NewClinicalJsonClass.json'), 'w') as f:
        json.dump(result, f, default=ClassToJason_method, indent=2)

    with open(os.path.join(os.path.dirname(__file__), '../Data/BackupFiles/', BackupFileName), 'w') as f:
        json.dump(currentjson, f, default=ClassToJason_method, indent=2)
