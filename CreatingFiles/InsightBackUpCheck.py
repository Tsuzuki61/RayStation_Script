import pandas as pd
import tkinter as tk
from tkinter import filedialog
import os
import datetime
from dateutil.relativedelta import relativedelta
import openpyxl

from pathlib import Path


def backup_check_import_patient_data():
    # desktop_path = os.path.expanduser('~/Desktop')
    # GUI setting
    root = tk.Tk()
    root.withdraw()
    typ = [('', '*.csv')]
    # read a CSV file
    import_csv_path = filedialog.askopenfilename(filetypes=typ, initialdir=r"DirectoryPath")

    if import_csv_path == '':
        exit()
    patient_plan_data = pd.read_csv(import_csv_path)

    # memo
    # backup_directory_path=Path(r"DirectoryPath")

    # Format the patient backup DataFrame
    backup_patient_list = os.listdir(r"DirectoryPath")

    patient_plan_data['プラン名'] = patient_plan_data['プラン名'].str.split(',')

    def list_str_to_datetime(str_list):
        ret_list = [datetime.datetime.strptime(x, r'%Y/%m/%d') for x in str_list]
        return ret_list

    patient_plan_data['治療開始日'] = patient_plan_data['治療開始日'].str.split(',')
    patient_plan_data['治療終了日'] = patient_plan_data['治療終了日'].str.split(',')
    patient_plan_data['治療開始日'] = patient_plan_data['治療開始日'].map(list_str_to_datetime)
    patient_plan_data['治療終了日'] = patient_plan_data['治療終了日'].map(list_str_to_datetime)
    patient_plan_data['患者番号'] = patient_plan_data['患者番号'].map('{:08}'.format)
    patient_plan_data['Backup_check'] = patient_plan_data['患者番号'].isin(backup_patient_list)

    backup_patient_data = patient_plan_data[
        (patient_plan_data['Backup_check'] == False) & (patient_plan_data['治療終了日'].apply(
            lambda x: datetime.date.today() - relativedelta(months=3) > max(x).date()))]
    export_excel_path = os.path.join(r"DirectoryPath", 'backup_patient_list.xlsx')
    backup_patient_data.sort_values('治療終了日', key=lambda x: x.map(max), inplace=True)
    backup_patient_data.reset_index(drop=True, inplace=True)
    backup_patient_data['Latest_treatment_end_date'] = backup_patient_data['治療終了日'].apply(
        lambda x: max(x).strftime('%Y/%m/%d'))
    # Save Excel file
    backup_patient_data[['患者番号', '氏名', 'カナ名', '生年月日', 'プラン名', 'Latest_treatment_end_date']].to_excel(export_excel_path)

    # Format Excel file
    wb = openpyxl.load_workbook(filename=export_excel_path)
    ws = wb.worksheets[0]
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            if len(str(cell.value)) > max_length:
                max_length = len(str(cell.value))
        adjusted_width = (max_length+2)*1.2
        ws.column_dimensions[column].width = adjusted_width
    ws.page_setup.orientation=ws.ORIENTATION_LANDSCAPE
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight=0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    wb.save(export_excel_path)

if __name__ == "__main__":
    backup_check_import_patient_data()
