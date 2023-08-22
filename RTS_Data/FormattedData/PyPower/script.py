import numpy as np
import os
import io
import re

def caseRTSGMLC():
    # Read the m file from the MATPOWER repository
    path = os.path.join("..", "MATPOWER")
    with open(os.path.join(path, "RTS_GMLC.m"), 'r') as file:
        m = file.read()
    
    # inicialize a dictionary
    ppc = {}

    # get the single entries
    ppc['version'] = re.search("mpc\.version *= *'(.*?)'\;", m)[1]
    ppc['baseMVA'] = float(re.search("mpc\.baseMVA *= *(.*?)\;", m)[1])

    # get all numeric array entries
    d = dict(re.findall("mpc\.(\w+) *= *\[(.*?)\]", m, re.DOTALL))

    for k in ['bus', 'gen', 'branch', 'gencost']:
        aux = np.genfromtxt(io.StringIO(d[k].replace('\t\t','\t')), missing_values="nan",
            delimiter="\t")
        ppc[k] = aux[:,~np.isnan(aux).any(axis=0)]

    aux = np.genfromtxt(io.StringIO(d['areas'].replace(";", " ")),
        missing_values="nan", dtype = "int")
    ppc['areas'] = aux[:,~np.isnan(aux).any(axis=0)]

    aux = np.genfromtxt(io.StringIO(d['dcline']), missing_values="nan",
        delimiter=" ")
    ppc['dcline'] = aux[:,~np.isnan(aux).any(axis=0)]

    
    # get all string array entries (although not really used in PyPower)
    e = dict(re.findall("mpc\.(\w+) *= *\{(.*?)\}", m, re.DOTALL))

    for k in e.keys():
        aux = e[k].split('\n')[1:-1]
        aux2 = [x.split('\t') for x in aux]
        aux3 = [x[1:] for x in aux2]
        ppc[k] = [[x[i][1:-2] for i in range(0,len(x))] for x in aux3]
    
    return ppc