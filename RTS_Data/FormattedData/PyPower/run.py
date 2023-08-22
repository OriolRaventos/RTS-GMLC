from pypower.api import ppoption, runpf, printpf, savecase
from script import caseRTSGMLC

ppc = caseRTSGMLC()

ppopt = ppoption(PF_ALG=2)

r = runpf(ppc, ppopt)

#https://github.com/rwl/PYPOWER/issues/49
printpf(r[0])

savecase("caseRTSGMLC_ppc", ppc)

#need to add a line in the file to be able to directly load it later

with open("caseRTSGMLC_ppc.py", 'r+') as f:
    content = f.read()
    f.seek(0, 0)
    f.write('from numpy import array' + '\n\n' + content)
    f.truncate()