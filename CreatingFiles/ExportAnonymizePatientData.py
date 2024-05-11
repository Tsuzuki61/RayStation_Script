from connect import *
import json
import os
import sys
import re


# Example on how to read the JSON error string.
def LogWarning(warning):
    try:
        jsonWarnings = json.loads(str(warning))
        # If the json.loads() works then the script was stopped due to
        # a non-blocking warning.
        print " "
        print "WARNING! Export Aborted!"
        print "Comment:"
        print " "
        print jsonWarnings["Comment"]
        print "Warnings:"
        # Here the user can handle the warnings. Continue on known warnings,
        # stop on unknown warnings.
        for w in jsonWarnings["Warnings"]:
            print " ",
        print w

    except ValueError as error:
        print "Error occurred. Could not export."
        # The error was likely due to a blocking warning, and the details should be stated
        # in the execution log.
        # This prints the successful result log in an ordered way.


def LogCompleted(completed):
    try:
        jsonWarnings = json.loads(str(completed))

        print " "
        print "Completed!"
        print "Comment:"
        print " ",
        print jsonWarnings["Comment"]
        print "Warnings:"
        for w in jsonWarnings["Warnings"]:
            print " ",
            print w
        print "Export notifications:"
        # Export notifications is a list of notifications that the user should read.
        for w in jsonWarnings["ExportNotifications"]:
            print " ",
            print w
    except ValueError as error:
        print "Error reading completion messages."


def Export_Anonymized_Patient_data(patient_number, case, examination):
    ExportFilePath = r"DirectoryPath" + '{:02}'.format(patient_number)
    if not os.path.exists(ExportFilePath):
        os.mkdir(ExportFilePath)

    try:
        # It is not necessary to assign all of the parameters, you only need to assign the
        # desired export items. In this example we try to export with
        # IgnorePreConditionWarnings=False. This is an option to handle possible warnings.
        result = case.ScriptableDicomExport(ExportFolderPath=ExportFilePath,
                                            Examinations=[examination.Name],
                                            Anonymize=True,
                                            AnonymizedName="ScriptExam{:08}".format(patient_number),
                                            AnonymizedId="Script{:08}".format(patient_number),
                                            DicomFilter="",
                                            IgnorePreConditionWarnings=False)
        # It is important to read the result event if the script was successful.
        # This gives the user a chance to see possible warnings that were ignored, if for
        # example the IgnorePreConditionWarnings was set to True by mistake. The result
        # also contains other notifications the user should read.
        LogCompleted(result)
    except SystemError as error:
        # The script failed due to warnings or errors.
        LogWarning(error)
        print " "
        print "Trying to export again with IgnorePreConditionWarnings=True"
        print " "
        result = case.ScriptableDicomExport(ExportFolderPath=ExportFilePath,
                                            Examinations=[examination.Name],
                                            Anonymize=True,
                                            AnonymizedName="ScriptExam{:08}".format(patient_number),
                                            AnonymizedId="Script{:08}".format(patient_number),
                                            DicomFilter="",
                                            IgnorePreConditionWarnings=True)
        # It is very important to read the result event if the script was successful.
        # This gives the user a chance to see any warnings that have been ignored.
        LogCompleted(result)


def get_prostate_patient_info():
    patient_db = get_current("PatientDB")
    # Get info on all patients in the database.
    all_patients_info = patient_db.QueryPatientInfo(Filter={'PatientID': '[0-9]{8}', 'LastName': '^[A-Z]+$'})

    count = 1
    end = 70
    for info in all_patients_info:
        patient = patient_db.LoadPatient(PatientInfo=info)
        for case in patient.Cases:
            for plan in case.TreatmentPlans:
                if re.match('^Prostate$', plan.Name):
                    Export_Anonymized_Patient_data(patient_number=count, case=case,
                                                   examination=plan.TreatmentCourse.TotalDose.OnDensity.FromExamination)
                    count += 1
                    break
            break
        if count > end:
            return


if __name__ == '__main__':
    get_prostate_patient_info()
