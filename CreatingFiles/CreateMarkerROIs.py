from connect import *


def create_marker_rois():
    """
    Create marker ROI for 4D CT
    """
    # Connection with RayStation
    case = get_current("Case")
    examination = get_current("Examination")

    ROI_Names = [ROI.OfRoi.Name for ROI in case.PatientModel.StructureSets[examination.Name].RoiGeometries]
    number_of_marker = 2

    # Create a list of marker names
    marker_list = ['Marker_{}'.format(number + 1) for number in range(number_of_marker)]
    suffix_list = ['Ex', 'In']
    color_list = [(255, 0, 0), (0, 0, 255), (0, 255, 0), (255, 255, 0)]

    # Create marker ROIs
    for i in range(10):
        suffix_list.append(str(i * 10) + 'pct')
    ExcludeFromExportRois = []
    for i in range(len(suffix_list)):
        for marker, color in zip(marker_list, color_list):
            if i == 0:
                color_str = '{0:d},{1:d},{2:d}'.format(color[0], color[1], color[2])
                case.PatientModel.CreateRoi(Name=marker + '_' + suffix_list[i], Color=color_str, Type='Undefined',
                                            TissueName=None,
                                            RbeCellTypeName=None, RoiMaterial=None)
            elif i == 1:
                color_str = '{0:d},{1:d},{2:d}'.format(color[0] / 2, color[1] / 2, color[2] / 2)
                case.PatientModel.CreateRoi(Name=marker + '_' + suffix_list[i], Color=color_str, Type='Undefined',
                                            TissueName=None,
                                            RbeCellTypeName=None, RoiMaterial=None)
            else:
                color_str = '{0:d},{1:d},{2:d}'.format(color[0] / 3, color[1] / 3, color[2] / 3)
                tmp_roi = case.PatientModel.CreateRoi(Name=marker + '_' + suffix_list[i], Color=color_str,
                                                      Type='Undefined',
                                                      TissueName=None,
                                                      RbeCellTypeName=None, RoiMaterial=None)
                ExcludeFromExportRois.append(tmp_roi.Name)

    case.PatientModel.ToggleExcludeFromExport(ExcludeFromExport=True,
                                              RegionOfInterests=ExcludeFromExportRois,
                                              PointsOfInterests=[])

    # Combine ROIs from all phases of the 4D CT into a single ROI
    Markers_4D_dict = {}
    All_phase_markers_dict = {}
    for marker in marker_list:
        Markers_4D_dict.setdefault(marker, [marker + '_' + suffix for suffix in suffix_list if
                                            ("Ex" not in suffix) and ('In' not in suffix)])
        All_phase_markers_dict.setdefault(marker, [marker + '_' + suffix for suffix in suffix_list])

    for roi_name, color in zip(marker_list, color_list):
        new_4D_roi_name = roi_name + '_4D_AllPhase'
        new_all_phase_roi_name = roi_name + '_Ex+In+4D'
        # Create a single ROI containing all phases of the 4D CT.
        if not new_4D_roi_name in ROI_Names:
            r = color[0] if color[0] != 0 else 128
            g = color[1] if color[1] != 0 else 128
            b = color[2] if color[2] != 0 else 128

            color_str = '{0:d},{1:d},{2:d}'.format(r, g, b)
            new_4D_roi = case.PatientModel.CreateRoi(Name=new_4D_roi_name, Color=color_str, Type="Undefined",
                                                     TissueName=None,
                                                     RbeCellTypeName=None, RoiMaterial=None)

        else:
            new_4D_roi = case.PatientModel.RegionsOfInterest[new_4D_roi_name]

        # Create a single ROI encompassing all phases 4D-CT and respiratory phases(exhalation and inhalation).
        if not new_all_phase_roi_name in ROI_Names:
            r = color[0] if color[0] != 0 else 128
            g = color[1] if color[1] != 0 else 128
            b = color[2] if color[2] != 0 else 128

            color_str = '{0:d},{1:d},{2:d}'.format(r / 2, g / 2, b / 2)
            new_all_phase_roi = case.PatientModel.CreateRoi(Name=new_all_phase_roi_name, Color=color_str,
                                                            Type="Undefined",
                                                            TissueName=None,
                                                            RbeCellTypeName=None, RoiMaterial=None)

        else:
            new_all_phase_roi = case.PatientModel.RegionsOfInterest[new_all_phase_roi_name]

        # Set up ROI combination settings
        new_4D_roi.SetAlgebraExpression(ExpressionA={'Operation': "Union", 'SourceRoiNames': Markers_4D_dict[roi_name],
                                                     'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0,
                                                                        'Anterior': 0, 'Posterior': 0, 'Right': 0,
                                                                        'Left': 0}},
                                        ExpressionB={'Operation': "Union", 'SourceRoiNames': [],
                                                     'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0,
                                                                        'Anterior': 0, 'Posterior': 0, 'Right': 0,
                                                                        'Left': 0}}, ResultOperation="None",
                                        ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0,
                                                              'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})
        new_all_phase_roi.SetAlgebraExpression(ExpressionA={'Operation': "Union",
                                                            'SourceRoiNames': All_phase_markers_dict[roi_name],
                                                            'MarginSettings': {'Type': "Expand", 'Superior': 0,
                                                                               'Inferior': 0,
                                                                               'Anterior': 0, 'Posterior': 0,
                                                                               'Right': 0,
                                                                               'Left': 0}},
                                               ExpressionB={'Operation': "Union", 'SourceRoiNames': [],
                                                            'MarginSettings': {'Type': "Expand", 'Superior': 0,
                                                                               'Inferior': 0,
                                                                               'Anterior': 0, 'Posterior': 0,
                                                                               'Right': 0,
                                                                               'Left': 0}}, ResultOperation="None",
                                               ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0,
                                                                     'Anterior': 0, 'Posterior': 0, 'Right': 0,
                                                                     'Left': 0})


if __name__ == '__main__':
    create_marker_rois()




