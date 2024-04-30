from connect import *
import clr, System, math, numpy

clr.AddReference('System.Windows.Forms', 'System.Drawing')
from System.Windows.Forms import *
from System.Drawing import *

case = get_current("Case")
examination = get_current("Examination")
image_list = [exam.Name for exam in case.Examinations]
poi_name_list = []
empty_coord = -1.7976931348623157e+308

# Set Initial parameter
bin_size = 0.1
rounding_val = 1
ct_val_list = [-1000.0, -779.22, -508.47, -67.02, -32.32, -4.77, 39.02, 58.25, 210.57, 843.08, 1288.03, 3068.47]
density_val_list = [0.00121, 0.205, 0.507, 0.96, 0.991, 1.0, 1.062, 1.072, 1.161, 1.53, 1.82, 4.51]

### GUI Start ###
first_back_color = Color.FromArgb(100, 100, 100)
second_back_color = Color.FromArgb(175, 175, 175)

form = Form(MaximumSize=Size(1000, 1000), AutoSize=True, Text="Please select image and POIs and Co or NonCo")
tableLayoutPanel_main = TableLayoutPanel(AutoScroll=True, Padding=Padding(10), AutoSize=True, Dock=DockStyle.Fill,
                                         BackColor=Color.FromArgb(50, 50, 50), ForeColor=Color.FromArgb(220, 220, 220),
                                         Font=Font("MS UI Gothic", 20), RowCount=3, ColumnCount=1)


def ComboBoxSelectAtionAfterImage(sender, e):
    poi_name_list = [poi.OfPoi.Name for poi in
                     case.PatientModel.StructureSets[combobox_image.SelectedItem].PoiGeometries if
                     poi.Point.x != empty_coord]
    combobox_start_poi.Items.Clear()
    combobox_end_poi.Items.Clear()
    combobox_start_poi.Items.AddRange(System.Array[System.Object](poi_name_list))
    combobox_end_poi.Items.AddRange(System.Array[System.Object](poi_name_list))


tableLayoutPanel_sub_1 = TableLayoutPanel(Padding=Padding(10), AutoSize=True, Dock=DockStyle.Fill,
                                          BackColor=first_back_color, RowCount=2, ColumnCount=1)
label_image = Label(Text="Please select image", Dock=DockStyle.Fill, Padding=Padding(10),
                    Font=Font("MS UI Gothic", 18, FontStyle.Bold), BackColor=first_back_color, AutoSize=True)
combobox_image = ComboBox(BackColor=second_back_color, Dock=DockStyle.Fill, Padding=Padding(10),
                          Font=Font("MS UI Gothic", 18, FontStyle.Bold), AutoSize=True)
combobox_image.Items.AddRange(System.Array[System.Object](image_list))
combobox_image.SelectedIndexChanged += ComboBoxSelectAtionAfterImage
tableLayoutPanel_sub_1.Controls.AddRange(System.Array[Control]([label_image, combobox_image]))

tableLayoutPanel_sub_2 = TableLayoutPanel(Padding=Padding(10), AutoSize=True, Dock=DockStyle.Fill,
                                          BackColor=first_back_color, RowCount=2, ColumnCount=1)
label_start_poi = Label(Text="Please select Start POI", Dock=DockStyle.Fill, Padding=Padding(10),
                        Font=Font("MS UI Gothic", 18, FontStyle.Bold), BackColor=first_back_color, AutoSize=True)
combobox_start_poi = ComboBox(BackColor=second_back_color, Dock=DockStyle.Fill, Padding=Padding(10),
                              Font=Font("MS UI Gothic", 18, FontStyle.Bold), AutoSize=True)
combobox_start_poi.Items.AddRange(System.Array[System.Object](poi_name_list))
tableLayoutPanel_sub_2.Controls.AddRange(System.Array[Control]([label_start_poi, combobox_start_poi]))

tableLayoutPanel_sub_3 = TableLayoutPanel(Padding=Padding(10), AutoSize=True, Dock=DockStyle.Fill,
                                          BackColor=first_back_color, RowCount=2, ColumnCount=1)
label_end_poi = Label(Text="Please select End POI", Dock=DockStyle.Fill, Padding=Padding(10),
                      Font=Font("MS UI Gothic", 18, FontStyle.Bold), BackColor=first_back_color, AutoSize=True)
combobox_end_poi = ComboBox(BackColor=second_back_color, Dock=DockStyle.Fill, Padding=Padding(10),
                            Font=Font("MS UI Gothic", 18, FontStyle.Bold), AutoSize=True)
combobox_end_poi.Items.AddRange(System.Array[System.Object](poi_name_list))
tableLayoutPanel_sub_3.Controls.AddRange(System.Array[Control]([label_end_poi, combobox_end_poi]))

tableLayoutPanel_sub_4 = TableLayoutPanel(Padding=Padding(10), AutoSize=True, Dock=DockStyle.Fill,
                                          BackColor=first_back_color, RowCount=3, ColumnCount=1)
label_CoOrNonCo = Label(Text="Please select Co-planar or Non-Conplanar direction", Dock=DockStyle.Fill,
                        Padding=Padding(10), Font=Font("MS UI Gothic", 18, FontStyle.Bold), BackColor=first_back_color,
                        AutoSize=True)
combobox_CoOrNonCo = ComboBox(BackColor=second_back_color, Dock=DockStyle.Fill, Padding=Padding(10),
                              Font=Font("MS UI Gothic", 18, FontStyle.Bold), AutoSize=True)
combobox_CoOrNonCo.Items.AddRange(System.Array[System.Object](["Co-planar", "Non-Coplanar"]))
tableLayoutPanel_sub_4.Controls.AddRange(System.Array[Control]([label_CoOrNonCo, combobox_CoOrNonCo]))


def execute_button(sender, event):
    form.Close()


button = Button(Margin=Padding(10, 10, 0, 0), Dock=DockStyle.Right, Text="OK", AutoSize=True,
                BackColor=first_back_color)
button.Click += execute_button

tableLayoutPanel_main.Controls.AddRange(System.Array[Control](
    [tableLayoutPanel_sub_1, tableLayoutPanel_sub_2, tableLayoutPanel_sub_3, tableLayoutPanel_sub_4, button]))
form.Controls.AddRange(System.Array[Control]([tableLayoutPanel_main]))
Form.ShowDialog(form)
### GUI End ###

# Set Parameter
selected_image = combobox_image.SelectedItem
start_poi_name = combobox_start_poi.SelectedItem
end_poi_name = combobox_end_poi.SelectedItem
mini_box_size = 0.2 if combobox_CoOrNonCo.SelectedItem == "Co-planar" else 0.75
mini_box_size_without_mesh = mini_box_size * 1.5 if combobox_CoOrNonCo.SelectedItem == "Co-planar" else mini_box_size * 1.0

a_list = [(density_val_list[i + 1] - density_val_list[i]) / (ct_val_list[i + 1] - ct_val_list[i]) for i in
          range(len(ct_val_list) - 1)]
b_list = [density_val_list[i] - a_list[i] * ct_val_list[i] for i in range(len(ct_val_list) - 1)]

start_point = case.PatientModel.StructureSets[selected_image].PoiGeometries[start_poi_name].Point
end_point = case.PatientModel.StructureSets[selected_image].PoiGeometries[end_poi_name].Point

dx = round(end_point.x - start_point.x, rounding_val)
dy = round(end_point.y - start_point.y, rounding_val)
dz = round(end_point.z - start_point.z, rounding_val)

dr = math.sqrt(dx ** 2 + dy ** 2 + dz ** 2)
num_of_point = int(math.ceil(dr / bin_size))

x_increment = dx / num_of_point
y_increment = dy / num_of_point
z_increment = dz / num_of_point

hu_list, coordinate_list = [], []
for i in range(num_of_point):
    roi_name = "{0:03d}".format(i)
    with CompositeAction('Create Box ROI ({0}, Image set: {1})'.format(roi_name, selected_image)):
        new_roi = case.PatientModel.CreateRoi(Name=roi_name, Color="Cyan", Type="Organ", TissueName=None,
                                              RbeCellTypeName=None, RoiMaterial=None)
        try:
            new_roi.CreateBoxGeometry(Size={'x': mini_box_size, 'y': mini_box_size, 'z': mini_box_size},
                                      Examination=examination, Center={'x': start_point.x + x_increment * i,
                                                                       'y': start_point.y + y_increment * i,
                                                                       'z': start_point.z + z_increment * i},
                                      Representation="TriangleMesh", VoxelSize=None)
        except:
            mini_box_size = mini_box_size_without_mesh
            new_roi.CreateBoxGeometry(Size={'x': mini_box_size, 'y': mini_box_size, 'z': mini_box_size},
                                      Examination=examination, Center={'x': start_point.x + x_increment * i,
                                                                       'y': start_point.y + y_increment * i,
                                                                       'z': start_point.z + z_increment * i},
                                      VoxelSize=None)

        # Script has dicom coord(like diagnosis coord) and AP is inverted (P is +) but actual window is viewed as A is +.
        coordinate_list.append({'x': start_point.x + x_increment * i, 'y': start_point.z + z_increment * i,
                                'z': -(start_point.y + y_increment * i)})
        hu_list.append([hu_avg.Key for hu_avg in
                        case.Examinations[examination.Name].Series[0].ImageStack.GetIntensityStatistics(
                            RoiName=roi_name)["Average"]][0])
        new_roi.DeleteRoi()

# Convert from HU to density.
index = 0
for i, ct_val in enumerate(ct_val_list):
    if numpy.average(hu_list) > ct_val:
        index = i

density_avg = numpy.average(hu_list) * a_list[index] + b_list[index]

density_converted_list = []
for i, hu in enumerate(hu_list):
    index = 0
    for i, ct_val in enumerate(ct_val_list):
        if hu > ct_val:
            index = i

    avg = hu * a_list[index] + b_list[index]
    density_converted_list.append(avg)

import os

os.chdir(os.getenv("HOMEDRIVE") + os.getenv("HOMEPATH") + "\\Desktop\\")
try:
    file_name = "{0}_{1}_{2}_{3}_{4}.csv".format(get_current("Patient").PatientID, get_current("Patient").Name,
                                                 examination.Name, start_poi_name, end_poi_name)
except:
    file_name = "{0}_{1}_{2}_{3}_{4}.csv".format(get_current("Patient").PatientID, get_current("Patient").PatientName,
                                                 examination.Name, start_poi_name, end_poi_name)

hu_list = numpy.array(hu_list)
with open(file_name, "w") as file:
    file.write("This is start {0} end {1}.\n".format(start_poi_name, end_poi_name))
    file.write(",Physical length(mm), Water Equivalent Length(mm), Average density, Std, Relative Std\n")
    file.write("Pre Summed HU densiy, {0}, {1}, {2}, {3}, {4}\n".format(str(round(10.0 * dr, rounding_val + 1)), str(
        round(10.0 * dr * density_avg, rounding_val + 1)), str(round(density_avg, rounding_val + 1)), str(
        round(numpy.std(hu_list), rounding_val + 1)), str(
        round((numpy.std(hu_list) / numpy.average(hu_list)), rounding_val + 1))))
    file.write("Converted CT to Density table Sum densiy, {0}, {1}, {2}, {3}, {4}\n".format(
        str(round(10.0 * dr, rounding_val + 1)),
        str(round(10.0 * dr * numpy.average(density_converted_list), rounding_val + 1)),
        str(round(numpy.average(density_converted_list), rounding_val + 1)),
        str(round(numpy.std(density_converted_list), rounding_val + 1)),
        str(round((numpy.std(density_converted_list) / numpy.average(density_converted_list)), rounding_val + 1))))
    file.write("Got Density Coordinate, HU, Density(g/cm3)\n")
    for coord, hu, density_converted in zip(coordinate_list, hu_list, density_converted_list):
        file.write("RL_{0}_AP_{1}_SI_{2}, {3}, {4}\n".format(str(coord["x"]), str(coord["z"]), str(coord["y"]), str(hu),
                                                             str(density_converted)))
    file.write("### End ###" + "\n")

### End ###
