# delete_evaluation_doses.py
# GUI application for deleting evaluation doses.
import os
import wpf
from System.Windows import *
from System.Windows.Controls import *
from connect import *

xaml_filename = os.path.join(os.path.dirname(__file__), "./xaml/delete_evaluation_doses.xaml")
# Copy the contents of the XAML file and paste them as a string in
# the parameter xaml_string.
# Replace all line breaks with "\n".
# The parameter here shall contain the contents of delete_evaluation_doses.xaml.
xaml_string = \
    """<!-- delete_evaluation_doses.xaml\n XAML code for delete_evaluation_doses.py-->
    <Window
    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
    Title="Delete evaluation doses" MaxHeight="600" Width="300" SizeToContent="WidthAndHeight">
    <DockPanel Name="mainDockPanel">
    <TextBlock Text="Select evaluation doses to delete" TextWrapping="Wrap" Margin="5" TextAlignment="Center" DockPanel.Dock="Top"/>
    <DockPanel DockPanel.Dock="Top">
    <TextBlock Text="Dose" Margin="27,5,5,5" Grid.Row="0" Grid.Column="0" DockPanel.Dock="Left"/>
    <TextBlock Text="Examination" Margin="5,5,20,5" Grid.Row="0" Grid.Column="1" DockPanel.Dock="Right" TextAlignment="Right"/>
    </DockPanel>
    <StackPanel DockPanel.Dock="Bottom" HorizontalAlignment="Center" Orientation="Horizontal">
    <Button Content="Delete doses" Margin="5" Click="DeleteClicked"/>
    <Button Content="Cancel" Margin="5" Click="CancelClicked"/>
    </StackPanel>
    <StackPanel DockPanel.Dock="Bottom" Orientation="Horizontal" HorizontalAlignment="Center">
    <Button Content="Select all" Margin="5" Click="SelectAllClicked"/>
    <Button Content="Select all perturbed doses" Margin="5" Click="SelectAllPerturbedClicked"/>
    <Button Content="Deselect all" Margin="5" Click="DeselectAllClicked"/>
    <Button Content="Select all PerturbedDose" Margin="5" Click="SelectAllPerturbedClicked"/>
    </StackPanel>
    <ScrollViewer>
    <Grid DockPanel.Dock="Top" Name="doseGrid">
    <Grid.ColumnDefinitions>
    <ColumnDefinition/>
    <ColumnDefinition MinWidth="70"/>
    </Grid.ColumnDefinitions>
    </Grid>
    </ScrollViewer>
    </DockPanel>
    </Window>"""
# Create a file
if not os.path.exists(xaml_filename):
    with open(xaml_filename, "w") as f:
        f.write(xaml_string)


class MyWindow(Window):
    def __init__(self, case):
        wpf.LoadComponent(self, xaml_filename)
        # Set window as topmost window.
        self.Topmost = True
        # Start up window at the center of the screen.
        self.WindowStartupLocation = WindowStartupLocation.CenterScreen
        self.doses = {}
        # Find all evaluation doses of the patient.
        for fe in case.TreatmentDelivery.FractionEvaluations:
            for doe in fe.DoseOnExaminations:
                examination_name = doe.OnExamination.Name
                for de in doe.DoseEvaluations:
                    self.add_row(de, examination_name)

    def DeleteClicked(self, sender, event):
        """ Method that finds all checked doses and deletes them and closes the window """
        for c in self.doseGrid.Children:
            if c.GetValue(Grid.ColumnProperty) == 0 and c.IsChecked:
                row = c.GetValue(Grid.RowProperty)
                try:
                    self.doses[row].DeleteEvaluationDose()
                except:
                    pass
        self.DialogResult = True

    def CancelClicked(self, sender, event):
        """ Method that cancels the window """
        self.DialogResult = False

    def SelectAllClicked(self, sender, event):
        """ Method that checks the checkboxes for all doses in the window """
        for c in self.doseGrid.Children:
            if c.GetValue(Grid.ColumnProperty) == 0:
                c.IsChecked = True

    def DeselectAllClicked(self, sender, event):
        """ Method that unchecks the checkboxes for all doses in the window """
        for c in self.doseGrid.Children:
            if c.GetValue(Grid.ColumnProperty) == 0:
                c.IsChecked = False

    def SelectAllPerturbedClicked(self, sender, event):
        for c in self.doseGrid.Children:
            if c.GetValue(Grid.ColumnProperty) == 0:
                c.IsChecked = False
                if "Perturbed dose of" in c.Content:
                    c.IsChecked = True

    def add_row(self, dose_distribution, examination_name):
        """ Method that adds a row with a checkbox and a text describing
        the associated evaluation dose to the window """
        row = self.doseGrid.RowDefinitions.Count
        self.doseGrid.RowDefinitions.Add(RowDefinition())
        cb = CheckBox()
        cb.Margin = Thickness(10, 5, 5, 5)
        cb.SetValue(Grid.RowProperty, row)
        cb.SetValue(Grid.ColumnProperty, 0)
        # Find out which dose type we have and set dose text accordingly.
        if dose_distribution.PerturbedDoseProperties != None:
            # Perturbed dose.
            rds = dose_distribution.PerturbedDoseProperties.RelativeDensityShift
            density = "{0:.1f} %".format(rds * 100)
            iso = dose_distribution.PerturbedDoseProperties.IsoCenterShift
            isocenter = "({0:.1f}, {1:.1f}, {2:.1f}) cm".format(iso.x, iso.z, -iso.y)
            beam_set_name = dose_distribution.ForBeamSet.DicomPlanLabel
            dose_text = "Perturbed dose of {0} : {1}, {2}".format(beam_set_name, density, isocenter)
        elif dose_distribution.Name != "":
            # This is usually a summed dose.
            dose_text = dose_distribution.Name
        elif hasattr(dose_distribution, "ByStructureRegistration"):
            # Mapped dose.
            reg_name = dose_distribution.ByStructureRegistration.Name
            name = dose_distribution.OfDoseDistribution.ForBeamSet.DicomPlanLabel
            dose_text = "Deformed dose of {0} by registration {1}".format(name, reg_name)
        else:
            # Neither perturbed, summed or mapped dose.
            dose_text = dose_distribution.ForBeamSet.DicomPlanLabel
        cb.Content = dose_text
        self.doseGrid.Children.Add(cb)
        tbe = TextBlock()
        tbe.Text = examination_name
        tbe.Margin = Thickness(5)
        tbe.TextAlignment = TextAlignment.Left
        tbe.VerticalAlignment = VerticalAlignment.Center
        tbe.SetValue(Grid.RowProperty, row)
        tbe.SetValue(Grid.ColumnProperty, 1)
        self.doseGrid.Children.Add(tbe)
        self.doses[row] = dose_distribution


# Get current patient and display dialog.

def delete_evaluation_doses():
    """This function delete evaluation doses"""
    case = get_current("Case")
    dialog = MyWindow(case)
    dialog.ShowDialog()


if __name__ == '__main__':
    delete_evaluation_doses()
