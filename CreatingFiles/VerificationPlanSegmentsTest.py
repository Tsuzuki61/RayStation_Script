from connect import *

def test():
    patient = get_current('Patient')
    current_plan = get_current('Plan')

    VeriPlan = current_plan.VerificationPlans[0]
    for veri_beam in VeriPlan.BeamSet.Beams:
        for segment in veri_beam.Segments:
            print(segment.NominalEnergy)

if __name__ == '__main__':
    test()

