# Script recorded 15 Nov 2018

#   RayStation version: 6.2.0.7
#   Selected patient: ...
import sys
sys.path.append("F:\Proton\RayStation\Script\create file")
from RayForm import DeformForm
from connect import *
from System.Windows.Forms import *

case = get_current("Case")

form = DeformForm(case)
#form.StartPosition = FormStartPosition.CenterScreen
Application.Run(form)

# Access the user interface.
ui = get_current('ui')
# Open Deformable Registration.
menu_item = ui.TitleBar.MenuItem
menu_item['Patient Modeling'].Click()
menu_item['Patient Modeling'].Popup.MenuItem['Deformable Registration'].Click()

current_registration = ui.TabControl_ToolBar.ToolBarGroup['CURRENT REGISTRATION']
current_registration.RayPanelDropDownItem['Select registration'].DropDownButton_SelectRegistration.Click()


case.PatientModel.StructureSets['PlanningCT_20181114'].RoiGeometries['Illiac Bone'].GetRoiVolume()