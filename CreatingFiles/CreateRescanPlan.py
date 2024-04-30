from connect import *
import tkinter as tk
from tkinter import messagebox
import re


class rescan_plan_form(tk.Frame):
    def __init__(self, root=None, plan_name="", beamset_names=[]):
        super().__init__(root)
        self.flag = False
        self.pack(fill=tk.BOTH, expand=True)
        self.plan_name = tk.StringVar(self, plan_name)
        if len(beamset_names) == 0:
            beamset_names.append(plan_name + '-1')
        self.beamset_name = tk.StringVar(self, beamset_names[0])
        self.root = root
        self.root.title('Rescan Plan')
        self.planNameFrame = tk.Frame(self, padx=5, pady=5)
        self.planNameFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.planNameLabel = tk.Label(self.planNameFrame, text="Plan Name")
        self.planNameLabel.pack(side=tk.LEFT)
        self.planNameEntry = tk.Entry(self.planNameFrame, textvariable=self.plan_name)
        self.planNameEntry.pack(side=tk.LEFT, fill='x', expand=True)
        i = 1
        for beamset_name in beamset_names:
            setattr(self, 'beamset_name_{}'.format(i), tk.StringVar(self, beamset_name))
            setattr(self, 'beamSetNamesFrame_{}'.format(i), tk.Frame(self, padx=5, pady=5))
            getattr(self, 'beamSetNamesFrame_{}'.format(i)).pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            setattr(self, 'beamset_check_value_{}'.format(i), tk.BooleanVar(value=True))
            setattr(self, 'beamsetCheck_{}'.format(i), tk.Checkbutton(getattr(self, 'beamSetNamesFrame_{}'.format(i)),
                                                                      variable=getattr(self,
                                                                                       'beamset_check_value_{}'.format(
                                                                                           i))))
            getattr(self, 'beamsetCheck_{}'.format(i)).pack(side=tk.LEFT)
            setattr(self, 'beamSetNameLabel_{}'.format(i),
                    tk.Label(getattr(self, 'beamSetNamesFrame_{}'.format(i)), text='Beamset Name{}'.format(i)))
            getattr(self, 'beamSetNameLabel_{}'.format(i)).pack(side=tk.LEFT)
            setattr(self, 'beamSetNameEntry_{}'.format(i),
                    tk.Entry(getattr(self, 'beamSetNamesFrame_{}'.format(i)),
                             textvariable=getattr(self, 'beamset_name_{}'.format(i))))
            getattr(self, 'beamSetNameEntry_{}'.format(i)).pack(side=tk.LEFT)
            i += 1

        self.buttonFrame = tk.Frame(self, padx=5, pady=5)
        self.buttonFrame.pack(side=tk.BOTTOM, fill=tk.X, expand=True)
        self.cancelButton = tk.Button(self.buttonFrame, text='Cancel', command=self.click_cancel)
        self.cancelButton.pack(side=tk.RIGHT, padx=5)
        self.okButton = tk.Button(self.buttonFrame, text='OK', command=self.click_ok)
        self.okButton.pack(side=tk.RIGHT, padx=5)

    def click_cancel(self):
        self.root.destroy()

    def click_ok(self):
        self.flag = True
        self.root.destroy()


def create_rescan_plan():
    base_plan = get_current('Plan')
    case = get_current('Case')
    root = tk.Tk()
    root.withdraw()
    beamset_names = [beamset.DicomPlanLabel for beamset in base_plan.BeamSets]
    form = rescan_plan_form(root, plan_name='A1-1', beamset_names=beamset_names)
    if messagebox.askyesno(title='Create Rescan Plan', message='Is "Auto scale to prescription" button turned off?'):
        root.deiconify()
        form.mainloop()
    else:
        exit()

    if not form.flag:
        exit()
    case.CopyPlan(PlanName=base_plan.Name, NewPlanName=form.plan_name.get())
    copied_plan = case.TreatmentPlans[form.plan_name.get()]

    for i in range(len(beamset_names), 0, -1):
        if getattr(form, 'beamset_check_value_{}'.format(i)).get():
            copied_plan.BeamSets[i - 1].DicomPlanLabel = getattr(form, 'beamset_name_{}'.format(i)).get()
        else:
            copied_plan.BeamSets[i - 1].DeleteBeamSet()

# -----beamset and beams copy-----
    re_compile_beam_name = re.compile(r'(.*?)(\d+)$')
    for beamset in copied_plan.BeamSets:
        beam_name_list = [beam.Name for beam in beamset.Beams]
        MU_coefficient = int(6 / len(beam_name_list))
        for beam_name in beam_name_list:
            for i in range(MU_coefficient - 1):
                beamset.CopyBeam(BeamName=beam_name)
                if re_compile_beam_name.match(beam_name):
                    copied_beam_name = re_compile_beam_name.sub(lambda m: m.group(1) + str(int(m.group(2)) + 1),
                                                                beam_name)
                else:
                    copied_beam_name = beam_name + ' 1'
                copied_beam = beamset.Beams[copied_beam_name]
                tmp_beam_MU = beamset.Beams[beam_name].BeamMU
                input_temp_beam_MU = tmp_beam_MU / MU_coefficient
                copied_beam.BeamMU = input_temp_beam_MU
            beamset.Beams[beam_name].BeamMU = input_temp_beam_MU
        beamset.ComputeDose(ComputeBeamDoses=True,
                            DoseAlgorithm=beamset.AccurateDoseAlgorithm.DoseAlgorithm, ForceRecompute=False)
        beamset.NormalizeToPrescription(RoiName=beamset.Prescription.DosePrescriptions[0].OnStructure.Name,
                                        DoseValue=beamset.Prescription.DosePrescriptions[0].DoseValue,
                                        PrescriptionType=beamset.Prescription.DosePrescriptions[0].PrescriptionType)
        re_beam_name_list = [beam.Name for beam in beamset.Beams]
        re_compile_beam_number = re.compile(".*?([0-9]+)$")
        re_beam_name_list.sort(
            key=lambda x: re_compile_beam_number.match(x).group(1) if re_compile_beam_number.match(x) else x)
        # beam re-numbering and write description
        for new_beam_name in re_beam_name_list:
            beamset.Beams[new_beam_name].Number = beamset.Beams[new_beam_name].Number + 10
        i = 1
        j = 1
        pre_tmp_description = ''
        for new_beam_name in re_beam_name_list:
            beamset.Beams[new_beam_name].Number = i
            tmp_description = 'G{:03d}C{:03d}'.format(int(beamset.Beams[new_beam_name].GantryAngle),
                                                      int(beamset.Beams[new_beam_name].CouchRotationAngle))
            if pre_tmp_description != tmp_description:
                pre_tmp_description = tmp_description
                j = 1
            else:
                j += 1
            tmp_description += '_{}'.format(j)
            beamset.Beams[new_beam_name].Description = tmp_description
            i += 1


def test_create_rescan_plan():
    # base_plan = get_current('Plan')
    # case = get_current('Case')
    # root = tk.Tk()
    # form = rescan_plan_form(root, plan_name='A1-1', beamset_names=['A1-1-1', 'A1-1-2'])
    # form.mainloop()
    # if not form.flag:
    #     exit()
    # else:
    #     print(form.plan_name.get())
    # copied_plan = case.CopyPlan(PlanName=base_plan.Name, NewPlanName=form.plan_name.get())
    root = tk.Tk()
    root.withdraw()
    form = rescan_plan_form(root, plan_name='A1-1', beamset_names=['A1-1-1', 'A1-1-2'])

    if messagebox.askyesno(title='Create Rescan Plan', message='Is "Auto scale to prescription" button turned off?'):
        root.deiconify()
        form.mainloop()
    else:
        print('No')


if __name__ == '__main__':
    create_rescan_plan()
