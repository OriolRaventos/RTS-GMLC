import os
import argparse

import numpy as np
import pandas as pd

import pypsa

def _read_csv(input_folder, table):
    return pd.read_csv(os.path.join(input_folder, table + ".csv"))

def create_buses(n, input_folder):
    busdata = _read_csv(input_folder, "bus")

    #dictionary for bus type
    buscontrol_dic = {"PV": "PV", "PQ": "PQ", "Ref": "Slack"}

    for i in busdata.index:
        # Add each bus with the corresponding attributes
        # the non-assined attributes get the default value
        n.add("Bus", str(busdata.loc[i, "Bus ID"]),
            v_nom = busdata.loc[i, "BaseKV"],
            x = busdata.loc[i, "lng"],
            y = busdata.loc[i, "lat"],
            carrier = "AC" ,
            v_mag_pu_set = busdata.loc[i, "V Mag"] ,
            #v_mag_pu_min = , # NOTE: oder simulators use 0.95 as default
            #v_mag_pu_max = , # NOTE: oder simulators use 1.05 as default
            control = buscontrol_dic[busdata.loc[i, "Bus Type"]])
        
        # Additional data not part of the PyPSA format
        busadditional = ["Bus Name", "Area", "Sub Area", "Zone", "V Angle", 
            "MW Shunt G", "MVAR Shunt B"]
        for col in busadditional: 
            n.buses.loc[busdata.loc[i, "Bus ID"], col] = \
                busdata.loc[i, col]
    
    # Convert the index values into strings
    n.buses.index = n.buses.index.astype(str)

def create_loads(n, input_folder):
    busdata = _read_csv(input_folder, "bus")

    for i in busdata.index:
        n.add("Load", str(busdata.loc[i, "Bus ID"]),
            bus = str(busdata.loc[i, "Bus ID"]),
            carrier = "AC",
            p_set = busdata.loc[i, "MW Load"],
            q_set = busdata.loc[i, "MVAR Load"])
    
    n.loads.index = n.loads.index.astype(str)

def create_generators(n, input_folder):
    gendata = _read_csv(input_folder, "gen")

    #storage is stored in a separate table
    gendata.drop(gendata[gendata["Fuel"] == "Storage"].index, inplace = True)

    #we do not model synchronous condensors
    gendata.drop(gendata[gendata["Fuel"] == "Sync_Cond"].index, inplace = True)

    # dictionary for generator type
    gencontrol_dic = {}
    for c in gendata["Fuel"].unique():
        if c in ['Wind', 'Solar']:
            gencontrol_dic[c] = "PV"
        else:
            gencontrol_dic[c] = "PQ"
    
    gencommitable_dic = {}
    for c in gendata["Fuel"].unique():
        if c in ['Wind', 'Solar', 'Hydro']:
            gencommitable_dic[c] = False
        else:
            gencommitable_dic[c] = True
    
    for i in gendata.index:
        n.add("Generator", str(gendata.loc[i, "GEN UID"]),
            bus = gendata.loc[i, "Bus ID"],
            control = gencontrol_dic[gendata.loc[i, "Fuel"]],
            p_nom = gendata.loc[i, "PMax MW"],
                # NOTE: p_min_pu and p_max_pu need to be set accordingly
            #p_nom_extendable = , # NOTE: Not extendable by default
            #p_nom_min = ,
            #p_nom_max = ,
            p_min_pu = gendata.loc[i, "PMin MW"]/gendata.loc[i, "PMax MW"],
            p_max_pu = 1,
            p_set = gendata.loc[i, "MW Inj"],
            q_set = gendata.loc[i, "MVAR Inj"],
            carrier = gendata.loc[i, "Fuel"],
            marginal_cost = gendata.loc[i, "Fuel Price $/MMBTU"] *\
                gendata.loc[i, "HR_avg_0"] / 1000,
            #marginal_cost_quadratic = ,
            #build_year = ,
            #lifetime = ,
            #capital_cost = ,
            #efficiency = ,
            committable = gencommitable_dic[gendata.loc[i, "Fuel"]],
            start_up_cost = gendata.loc[i, "Non Fuel Start Cost $"],
            shut_down_cost = gendata.loc[i, "Non Fuel Shutdown Cost $"],
            #stand_by_cost = ,
            min_up_time = gendata.loc[i, "Min Up Time Hr"],
            min_down_time = gendata.loc[i, "Min Down Time Hr"],
            #up_time_before = ,
            #down_time_before = ,
            ramp_limit_up = gendata.loc[i, "Ramp Rate MW/Min"]*60,
            ramp_limit_down = gendata.loc[i, "Ramp Rate MW/Min"]*60,
            ramp_limit_start_up = gendata.loc[i, "Ramp Rate MW/Min"]*60,
            ramp_limit_shut_down = gendata.loc[i, "Ramp Rate MW/Min"]*60)
        
        genadditional = ["Gen ID", "Unit Group", "Unit Type", "Category", 
            "V Setpoint p.u.", "QMax MVAR", "QMin MVAR", "Start Time Cold Hr",
            "Start Time Warm Hr", "Start Time Hot Hr", "Start Heat Cold MBTU",
            "Start Heat Warm MBTU", "Start Heat Hot MBTU", "FOR", "MTTF Hr",
            "MTTR Hr", "Scheduled Maint Weeks", "Output_pct_0", "Output_pct_1",
            "Output_pct_2", "Output_pct_3", "Output_pct_4", "HR_avg_0", 
            "HR_incr_1", "HR_incr_2", "HR_incr_3", "HR_incr_4", "VOM",
            "Fuel Sulfur Content %", "Emissions SO2 Lbs/MMBTU", 
            "Emissions NOX Lbs/MMBTU", "Emissions Part Lbs/MMBTU", 
            "Emissions CO2 Lbs/MMBTU", "Emissions CH4 Lbs/MMBTU",
            "Emissions N2O Lbs/MMBTU", "Emissions CO Lbs/MMBTU",
            "Emissions VOCs Lbs/MMBTU", "Damping Ratio", "Inertia MJ/MW",
            "Base MVA", "Transformer X p.u.", "Unit X p.u.", "Pump Load MW",
            "Storage Roundtrip Efficiency"]
        for col in genadditional:
            #/ are not allowed as column names in netcdf and hcdf5
            if "/" in col:
                col2 = col.replace("/", " per ")
            else:
                col2 = col

            n.generators.loc[gendata.loc[i, "GEN UID"], col2] = \
                gendata.loc[i, col]

    n.generators.index = n.generators.index.astype(str)

def create_storage_units(n, input_folder):
    gendata = _read_csv(input_folder, "gen")
    storagedata = _read_csv(input_folder, "storage")

    for i in storagedata.index:
        igen =  gendata[gendata["GEN UID"] == storagedata.loc[i, "GEN UID"]].\
            index[0]
        print(igen)

        n.add("StorageUnit", str(storagedata.loc[i, "Storage"]),
            bus = gendata.loc[igen, "Bus ID"],
            control = "PQ",
            p_nom = gendata.loc[igen, "PMax MW"], # actually same as Rating MVA
                # NOTE: p_min_pu and p_max_pu need to be set accordingly
            #p_nom_extendable = , # NOTE: Not extendable by default
            #p_nom_min = ,
            #p_nom_max = ,
            p_min_pu = gendata.loc[igen,
                "PMin MW"]/gendata.loc[igen, "PMax MW"],
            p_max_pu = 1,
            carrier = gendata.loc[igen, "Fuel"],
            marginal_cost = 0, # set storage costs to zero
            #marginal_cost_quadratic = ,
            #capital_cost = ,
            #build_year = ,
            #lifetime = ,
            state_of_charge_initial = storagedata.loc[i,
                "Initial Volume GWh"]/1000,
            #state_of_charge_initial_per_period = ,
            #state_of_charge_set = ,
            cyclic_state_of_charge = False,
            #cyclic_state_of_charge_per_period = ,
            max_hours = storagedata.loc[i, "Max Volume GWh"] /\
                (1000 * gendata.loc[igen, "PMax MW"]),
            #efficiency_store = ,
            #efficiency_dispatch = ,
            #standing_loss = ,
            inflow = storagedata.loc[i, "Inflow Limit GWh"]/1000)
        
        storageadditional = ["GEN UID", "Start Energy", "position"]
        for col in storageadditional:
            #/ are not allowed as column names in netcdf and hcdf5
            if "/" in col:
                col2 = col.replace("/", " per ")
            else:
                col2 = col

            n.storage_units.loc[storagedata.loc[i, "GEN UID"], col2] = \
                storagedata.loc[i, col]

    n.storage_units.index = n.storage_units.index.astype(str)
'''
def create_lines(n, input_folder):
    branchdata = _read_csv(input_folder, "branch")

name = ,
bus0 = ,
bus1 = ,
type = ,
x = ,
r = ,
g = ,
b = ,
s_nom = ,
s_nom_extendable = ,
s_nom_min = ,
s_nom_max = ,
s_max_pu = ,
capital_cost = ,
build_year = ,
lifetime = ,
length = ,
carrier = ,
terrain_factor = ,
num_parallel = ,
v_ang_min = ,
v_ang_max = ,
sub_network = ,
p0 = ,
q0 = ,
p1 = ,
q1 = ,
x_pu = ,
r_pu = ,
g_pu = ,
b_pu = ,
x_pu_eff = ,
r_pu_eff = ,
s_nom_opt = ,
mu_lower = ,
mu_upper = ,


    n.lines.index = n.lines.index.astype(str)

def create_links(n, input_folder):
    dc_branchdata = _read_csv(input_folder, "dc_branch")

name = ,
bus0 = ,
bus1 = ,
type = ,
carrier = ,
efficiency = ,
build_year = ,
lifetime = ,
p_nom = ,
p_nom_extendable = ,
p_nom_min = ,
p_nom_max = ,
p_set = ,
p_min_pu = ,
p_max_pu = ,
capital_cost = ,
marginal_cost = ,
marginal_cost_quadratic = ,
stand_by_cost = ,
length = ,
terrain_factor = ,
committable = ,
start_up_cost = ,
shut_down_cost = ,
min_up_time = ,
min_down_time = ,
up_time_before = ,
down_time_before = ,
ramp_limit_up = ,
ramp_limit_down = ,
ramp_limit_start_up = ,
ramp_limit_shut_down = ,
p0 = ,
p1 = ,
p_nom_opt = ,
status = ,
mu_lower = ,
mu_upper = ,
mu_p_set = ,
mu_ramp_limit_up = ,
mu_ramp_limit_down = ,


    n.links.index = n.links.index.astype(str)
'''

def create_pypsa_network(input_folder, output_format, output):

    # create an empty pypsa network
    n = pypsa.Network()

    # add buses
    create_buses(n, input_folder)

    # add loads
    create_loads(n, input_folder)

    # add generators
    create_generators(n, input_folder)

    # add storage_units
    create_storage_units(n, input_folder)

    # add lines

    # add links (DC-lines)


    # export the network
    if output_format == "netcdf":
        n.export_to_netcdf(output)
    if output_format == "hdf5":
        n.export_to_hdf5(output)
    if output_format == "csv":
        n.export_to_csv_folder(output)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-input_folder', type=str, default='../../SourceData/',
        help='input folder with RTS-GMLC source data. By default it assumes '\
        'working in the folder with the script.py in a cloned repository, '\
        'i.e. ../../SourceData/')
    parser.add_argument('-output_format', type=str, default='netcdf',
        choices = ['netcdf', 'hdf5', 'csv'],
        help='the format can be netcdf, hdf5 or csv')
    parser.add_argument('-output', type=str,
        default='PyPSA_RTS-GMLC.nc',
        help='output file name in case of netcdf format or folder name for '\
        'csv format. The default is /PyPSA_RTS-GML.nc')
    args = parser.parse_args()

    create_pypsa_network(input_folder=args.input_folder, 
        output_format = args.output_format, output = args.output)