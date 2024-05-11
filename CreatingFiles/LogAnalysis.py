import pandas as pd
import numpy as np
import csv
import os
import glob
import re
import math


def RangeToEnergy(water_range):
    x1 = 5.5919E-01
    x2 = -4.0274E-03
    x3 = 1.5739E-03
    intercept = 3.4658
    return math.exp((x3 * pow(math.log(water_range), 3)) + (x2 * pow(math.log(water_range), 2)) + (
            x1 * math.log(water_range)) + intercept)


def create_record_and_specif_dataframe(directory_path):
    if directory_path == "":
        return
    re_record_compile = re.compile(r'.*[0-9]{8}_[0-9]{6}_[0-9]{3}\.burst_record_([0-9]{3})_part_([0-9]{2})\.csv')
    file_list = [p for p in glob.glob(os.path.join(directory_path, '*')) if
                 re_record_compile.search(p)]
    file_list.sort()
    record_df_list = []
    specif_df_list = []
    beam_config_file_name = re.sub(r'burst_record_([0-9]{3})_part_([0-9]{2})', r'beam_config', file_list[0])

    with open(beam_config_file_name) as f:
        l_split = [s.strip() for s in f.readlines()]
    x_pos_iso_rate = 0.0
    y_pos_iso_rate = 0.0
    dist_from_ic1_iso_x = 0.0
    dist_from_ic1_iso_y = 0.0
    dist_from_ic2_iso_x = 0.0
    dist_from_ic2_iso_y = 0.0
    primary_charge_per_MU = 0.0
    for i in range(len(l_split)):
        ic1_match = re.search(
            r'CGTR;distanceFromIc1ToIsocenter;Distance from Ic1 to Isocenter \(X,Y\);([0-9]*\.[0-9]*),([0-9]*\.[0-9]*)',
            l_split[i]
        )
        ic2_match = re.search(
            r'CGTR;distanceFromIcToIsocenter;Distance from Ic2 to Isocenter \(X,Y\);([0-9]*\.[0-9]*),([0-9]*\.[0-9]*)',
            l_split[i]
        )
        primary_charge_per_MU_match = re.search(
            r'CGTR;chargePerMuPrimary;Charge per MU on the primary IC;([-+]?[0-9]+\.?[0-9]+([eE][-+]?[0-9]+))',
            l_split[i]
        )
        if ic1_match:
            dist_from_ic1_iso_x, dist_from_ic1_iso_y = ic1_match.groups()
        if ic2_match:
            dist_from_ic2_iso_x, dist_from_ic2_iso_y = ic2_match.groups()
        if primary_charge_per_MU_match:
            primary_charge_per_MU = float(primary_charge_per_MU_match.groups()[0])
        try:
            x_pos_iso_rate = float(dist_from_ic1_iso_x) / (float(dist_from_ic1_iso_x) - float(dist_from_ic2_iso_x))
            y_pos_iso_rate = float(dist_from_ic1_iso_y) / (float(dist_from_ic1_iso_y) - float(dist_from_ic2_iso_y))
        except:
            continue
        else:
            if primary_charge_per_MU != 0.0:
                break

    for file in file_list:
        first_index = 0
        layer_number = re_record_compile.search(file).groups()[0]
        burst_number = re_record_compile.search(file).groups()[1]
        specif_file = re.sub(r'burst_record', r'burst_specif', file)
        Range = 0.0
        with open(specif_file) as f:
            specif_reader = csv.reader(f)
            reader_list = [row for row in specif_reader]
            for i in range(len(reader_list)):
                if i >= 1:
                    if len(reader_list[i]) > 0 and reader_list[i][1] == 'RANGE':
                        Range = reader_list[i + 1][1]
                    elif len(reader_list[i]) > 0 and reader_list[i][0] == '#ELEMENT_ID':
                        specif_columns = reader_list[i]
                        specif_first_index = i
                        break
        tmp_specif_df = pd.read_csv(specif_file, header=specif_first_index)
        tmp_specif_df.columns = specif_columns
        tmp_specif_df['RANGE'] = float(Range)
        tmp_specif_df['ENERGY'] = RangeToEnergy(float(Range))
        tmp_specif_df['ISO_X_POSITION'] = (((tmp_specif_df['PRIM_EXP_IC_X_POSITION']) - (
            tmp_specif_df['SEC_EXP_IC_X_POSITION'])) * x_pos_iso_rate) + tmp_specif_df['SEC_EXP_IC_X_POSITION']
        tmp_specif_df['ISO_Y_POSITION'] = (((tmp_specif_df['PRIM_EXP_IC_Y_POSITION']) - (
            tmp_specif_df['SEC_EXP_IC_Y_POSITION'])) * y_pos_iso_rate) + tmp_specif_df['SEC_EXP_IC_Y_POSITION']
        tmp_specif_df['PRIM_IC_X_WIDTH'] = np.mean(tmp_specif_df[['PRIM_IC_X_WIDTH_MIN', 'PRIM_IC_X_WIDTH_MAX']],
                                                   axis=1)
        tmp_specif_df['PRIM_IC_Y_WIDTH'] = np.mean(tmp_specif_df[['PRIM_IC_Y_WIDTH_MIN', 'PRIM_IC_Y_WIDTH_MAX']],
                                                   axis=1)
        tmp_specif_df['GROUP'] = 'specif'
        tmp_specif_df['LAYER'] = int(layer_number)
        tmp_specif_df['BURST'] = int(burst_number)
        tmp_specif_df = tmp_specif_df.dropna()
        tmp_specif_df = tmp_specif_df.astype({'#ELEMENT_ID': int})
        specif_df_list.append(tmp_specif_df)

        with open(file) as record_file:
            reader = csv.reader(record_file)
            reader_list = [row for row in reader]
            for i in range(len(reader_list)):
                if len(reader_list[i]) > 0 and reader_list[i][0] == '#DISCARD':
                    for j in range(len(reader_list[i])):
                        if reader_list[i][j] == 'SMX_OFFSET':
                            SMX_OFFSET = reader_list[i + 1][j]
                        if reader_list[i][j] == 'SMY_OFFSET':
                            SMY_OFFSET = reader_list[i + 1][j]
                        if reader_list[i][j] == 'ICX_OFFSET':
                            ICX_OFFSET = reader_list[i + 1][j]
                        if reader_list[i][j] == 'ICY_OFFSET':
                            ICY_OFFSET = reader_list[i + 1][j]
                        if reader_list[i][j] == 'IC1X_OFFSET':
                            IC1X_OFFSET = reader_list[i + 1][j]
                        if reader_list[i][j] == 'IC1Y_OFFSET':
                            IC1Y_OFFSET = reader_list[i + 1][j]
                if len(reader_list[i]) > 0 and reader_list[i][0] == '#ELEMENT_ID':
                    columns = reader_list[i]
                    first_index = i
                    break
        tmp_df = pd.read_csv(file, header=first_index)
        tmp_df.columns = columns
        tmp_df['RANGE'] = float(Range)
        tmp_df['ENERGY'] = RangeToEnergy(float(Range))
        tmp_df['SMX_OFFSET'] = float(SMX_OFFSET)
        tmp_df['SMY_OFFSET'] = float(SMY_OFFSET)
        tmp_df['ICX_OFFSET'] = float(ICX_OFFSET)
        tmp_df['ICY_OFFSET'] = float(ICY_OFFSET)
        tmp_df['IC1X_OFFSET'] = float(IC1X_OFFSET)
        tmp_df['IC1Y_OFFSET'] = float(IC1Y_OFFSET)
        tmp_df['ISO_X_POSITION'] = (((tmp_df['PRIM_IC_X_POSITION']) - (tmp_df['SEC_IC_X_POSITION'])) * x_pos_iso_rate) + \
                                   tmp_df['SEC_IC_X_POSITION']
        tmp_df['ISO_Y_POSITION'] = (((tmp_df['PRIM_IC_Y_POSITION']) - (tmp_df['SEC_IC_Y_POSITION'])) * y_pos_iso_rate) + \
                                   tmp_df['SEC_IC_Y_POSITION']
        # tmp_df['ISO_X_POSITION_OFFSET'] = (((tmp_df['PRIM_IC_X_POSITION'] + tmp_df['ICX_OFFSET']) - (
        #         tmp_df['SEC_IC_X_POSITION'] + tmp_df['IC1X_OFFSET'])) * x_pos_iso_rate) + tmp_df['SEC_IC_X_POSITION'] + \
        #                                   tmp_df['IC1X_OFFSET']
        # tmp_df['ISO_Y_POSITION_OFFSET'] = (((tmp_df['PRIM_IC_Y_POSITION'] + tmp_df['ICY_OFFSET']) - (
        #         tmp_df['SEC_IC_Y_POSITION'] + tmp_df['IC1Y_OFFSET'])) * y_pos_iso_rate) + tmp_df['SEC_IC_Y_POSITION'] + \
        #                                   tmp_df['IC1Y_OFFSET']
        tmp_df['GROUP'] = 'record'
        tmp_df['LAYER'] = int(layer_number)
        tmp_df['BURST'] = int(burst_number)
        tmp_df['MU'] = tmp_df['PRIM_IC_CHARGE'].astype(float) / primary_charge_per_MU
        record_df_list.append(tmp_df)
    record_spot_df = pd.concat(record_df_list)
    specif_spot_df = pd.concat(specif_df_list)
    irradiation_record_df = record_spot_df[
        (record_spot_df['SPOT_ID'] > 0) & (record_spot_df['SEC_SPOT_ID'] > 0) & (record_spot_df['#ELEMENT_ID'] > 1)
        & (record_spot_df['MAP_EXEC_STATUS'] == record_spot_df['MAP_EXEC_STATUS_SEC'])]
    irradiation_record_df.loc[:,'MU_RATE'] = irradiation_record_df['MU'] / irradiation_record_df['MU'].sum()
    irradiation_specif_df = specif_spot_df[(specif_spot_df['SPOT_ID'] > 0) & (specif_spot_df['#ELEMENT_ID'] > 1)]
    return irradiation_record_df, irradiation_specif_df


if __name__ == "__main__":
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    directory = filedialog.askdirectory(initialdir=os.path.expanduser('~/Desktop'))
    df, _ = create_record_and_specif_dataframe(directory_path=directory)
    for name , _ in df.groupby('ENERGY'):
        print(name)

    print(df['MU_RATE'].sum())