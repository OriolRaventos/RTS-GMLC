# The RTS-GMLC model in PyPSA

## Description

We have imported the RTS-GMLC ("Reliability Test System Grid Modernization Lab 
Consortium") model to PyPSA. The imported model can be used both to calculate 
the AC power flow at the peak load and the DC optimal power flow for the whole
year with houly resolution (that means that we use the "DAY_AHEAD" files from 
the time series data files).

## Installation

conda/mamba environment: 
```
$ conda create-n myenv pypsa==25.1
```
pip:
```
$ pip install pypsa==25.1
```

## Create a PyPSA network from RTS-GMLC source data

activate the environment
```
$ conda activate myenv
```
go to the PyPSA folder in RTS-GMLC
```
$ cd RTS_Data/FormattedData/PyPSA
```
run the code and overwrite the exported PyPSA network
```
$python script.py
```
the attributes "input_folder", "output_format", and "output" can be used to 
modify the default values for the folder with the RTS-GMLC source data folder,
the format of the output data (netcdf, hdf5 or csv) and the output file or 
folder name.

## Calculate the AC-power flow at the peak load using PyPSA

Import pypsa
```
import pypsa
```
import the network form the appropiate folder
```
n = pypsa.Network('/Myfolder/PyPSA_RTS-GMLC.netcdf')
```
run the AC-simulation at the load peak
```
pypsa.pf(snapshot=n.load_t.p_set.sum().max().index)
```

plot results
```
n.generators_t.p.plot()
n.plot()
```
get statistics
```
n.statistics()
n.statistics.energy_balance()
```
drop the power set, optimize and recompute the AC-powerflow
```
TBD
```

## Comments

- PyPSA is mainly used to calculate the DC optimal power flow first and use
its output to compute the AC power flow, see [Non-linear power flow after LOPF
](https://pypsa.readthedocs.io/en/latest/examples/scigrid-lopf-then-pf.html). 
Hence, setting p_set and q_set for the generators is somehow unnatural, since
this is the output of the DC optimal power flow (which is writen in p and q and 
is copied to p_set and q_set before performing the AC power flow).

- Mainly following the function in PyPSA importing from PyPower [import_from_pypower_ppc
](https://github.com/PyPSA/PyPSA/blob/a0027f50a24744251e58ea6577f446bfdc90f1f6/
pypsa/io.py#L993) and alos the implementation in PyPower and MATPOWER but adding 
what is missing (e.g. AC-lines and storage units). Notice that PyPSA uses a 
1 MVA base instead of the 100 MVA base in the data.

- In general attributs of components not used by PyPSA are added for 
completness as extra columns. Other attributes in PyPSA were not present in
the source data mainly used the default value (compare [PyPSA Components](
https://pypsa.readthedocs.io/en/latest/components.html) and [
RTS-GMLC Source Data](
https://github.com/GridMod/RTS-GMLC/tree/master/RTS_Data/SourceData)). More 
prominently:

  - The control attribute for buses (PV, PQ or Slack).
  - The v_mag_pu_min and v_mag_pu_max for buses, not in the original data and 
  not used by PyPSA, although other simulators take 0.95 and 1.05 by default.
  - The control attribute for generators is set PV for Solar and Wind, and PQ for
  the rest.
  - The p_nom for generators is taken as teh PMax MW, hence p_max_pu is set to 1
  and p_min_pu is set to PMin MW / PMax MW.
  - The generators as suposed to be non extendable, hence there is no data
  for the limits of exentability.
  - The generators ramp_limit_up, ramp_limit_down, ramp_limit_start_up and 
  ramp_limit_shut_down get all the same value from Ramp Rate MW/Min.
  - The generators down_time_before and up_time_before is not included in 
  RTS-GMLC.
  - PyPSA does not use an MVA base. The power units are assumed to be MW and 
  MVA.
  - PyPSA uses a constant marginal cost, hence not using the data about
  heat rate curve
  - The investment costs are not included in the data, so the model is not
  complete for an expansion planning optimization.
  - The emissions in PyPSA are modeled per fuel (just CO2 by default), not at 
  each generator, so we do not implement that (although only Oil has different
  values for CT and Steam, and we could just take the maximum).
  - Solar, Wind and Hydro are set as non-commitable.
  - Synchronous converters are not modeled in PyPSA
  - Reserves are not modeled.
  - We set the storage marginal costs to 0. 

## Copyright notice

Oriol Raventós, DLR-VE

This adaptation of the original RTS-GMLC model was created by Oriol Raventós, 
DLR-VE, Oldenburg, Germany in the years 2023.

We adapted the RTS-GMLC created by DOE/NREL/ALLIANCE. All changes done were of 
technical nature to make the model run under PyPSA. We did not add any 
essential features. Therefore we cannot claim originality or ownership of the 
model. The copyright fully remains with DOE/NREL/ALLIANCE and their Data Use 
Disclaimer Agreement remains valid which we print here below:

## DATA USE DISCLAIMER AGGREEMENT
*(“Agreement”)*

These data (“Data”) are provided by the National Renewable Energy Laboratory
(“NREL”), which is operated by Alliance for Sustainable Energy, LLC
(“ALLIANCE”) for the U.S. Department Of Energy (“DOE”).

Access to and use of these Data shall impose the following obligations on the
user, as set forth in this Agreement. The user is granted the right, without
any fee or cost, to use, copy, and distribute these Data for any purpose
whatsoever, provided that this entire notice appears in all copies of the Data.
Further, the user agrees to credit DOE/NREL/ALLIANCE in any publication that
results from the use of these Data. The names DOE/NREL/ALLIANCE, however, may
not be used in any advertising or publicity to endorse or promote any products
or commercial entities unless specific written permission is obtained from
DOE/NREL/ ALLIANCE. The user also understands that DOE/NREL/Alliance is not
obligated to provide the user with any support, consulting, training or
assistance of any kind with regard to the use of these Data or to provide the
user with any updates, revisions or new versions of these Data.

**YOU AGREE TO INDEMNIFY DOE/NREL/ALLIANCE, AND ITS SUBSIDIARIES, AFFILIATES,
OFFICERS, AGENTS, AND EMPLOYEES AGAINST ANY CLAIM OR DEMAND, INCLUDING
REASONABLE ATTORNEYS' FEES, RELATED TO YOUR USE OF THESE DATA. THESE DATA ARE
PROVIDED BY DOE/NREL/Alliance "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
DOE/NREL/ALLIANCE BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES
OR ANY DAMAGES WHATSOEVER, INCLUDING BUT NOT LIMITED TO CLAIMS ASSOCIATED WITH
THE LOSS OF DATA OR PROFITS, WHICH MAY RESULT FROM AN ACTION IN CONTRACT,
NEGLIGENCE OR OTHER TORTIOUS CLAIM THAT ARISES OUT OF OR IN**


## Change log

-...