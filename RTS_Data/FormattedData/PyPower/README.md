# The RTS-GMLC model in PyPower

## Description

We have imported the RTS-GMLC ("Reliability Test System Grid Modernization Lab 
Consortium") model to PyPower. Since it is a port of MATPOWER to Python, it is 
directly converted from the [MATPOWER repository](https://github.com/GridMod/
RTS-GMLC/tree/master/RTS_Data/FormattedData/MATPOWER).

We also saved the data as ppc format, which is easy to load in pypower using
```
from caseRTSGMLC_ppc import caseRTSGMLC_ppc
ppc = caseRTSGMLC_ppc()
```