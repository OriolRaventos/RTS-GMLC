import numpy as np
import os

def caseRTS-GMLC():
    # Read the m file from the MATPOWER repository
    path = os.path.join("..", "MATPOWER")
    with open(os.path.join(input_folder, "RTS_GMLC.m"), 'r') as file:
        m = file.read()
    
    #serach each mpc. in the text and drop commented lines %
    
    ppc = {f: getattr(s, f)
            for f in {'version', 'baseMVA', 'areas', 'bus',
                      'gen', 'branch', 'gencost', 'bus_name', 'gen_name',
                      'dcline'}
            if hasattr(s, f)}
    
    return ppc