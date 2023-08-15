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
        busadditional = ["Bus name", "Area", "Sub Area", "Zone", "V Angle", 
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

    # dictionary for generator type
    gencontrol_dic = {}
    for c in gendata["Fuel"].unique():
        if c in in ['Wind', 'Solar']:
            gencontrol_dic[c] = "PV"
        else:
            gencontrol_dic[c] = "PQ"

    for i in gendata.index:
        n.add("Generator", str(gendata.loc[i, "Gen ID"])
            bus = gendata.loc[i, "Bus ID"],
            control = gencontrol_dic[gendata.loc[i, "Fuel"]],
            p_nom = gendata.loc[i, "PMax MW"], # NOTE: p_min_pu and p_max_pu 
                #set accordingly
            #p_nom_extendable = , # NOTE: Not extendable by default
            #p_nom_min = ,
            #p_nom_max = ,
            p_min_pu = gendata.loc[i, "PMin MW"]/gendata.loc[i, "PMax MW"],
            p_max_pu = 1,
            p_set = gendata.loc[i, "MW Inj"],
            q_set = gendata.loc[i, "MVAR Inj"],
            carrier = gendata.loc[i, "Fuel"],
            marginal_cost = ,
            marginal_cost_quadratic = ,
            build_year = ,
            lifetime = ,
            capital_cost = ,
            efficiency = ,
            committable = ,
            start_up_cost = ,
            shut_down_cost = ,
            stand_by_cost = ,
            min_up_time = gendata.loc[i, "Min Up Time Hr"],
            min_down_time = gendata.loc[i, "Min Down Time Hr"],
            #up_time_before = ,
            #down_time_before = ,
            ramp_limit_up = gendata.loc[i, "Ramp Rate MW/Min"]*60,
            ramp_limit_down = gendata.loc[i, "Ramp Rate MW/Min"]*60,
            ramp_limit_start_up = gendata.loc[i, "Ramp Rate MW/Min"]*60,
            ramp_limit_shut_down = gendata.loc[i, "Ramp Rate MW/Min"]*60)
        
        genadditional = ["GEN UID", "Unit Group", "Unit Type", "Category", 
            "V Setpoint p.u.", "QMax MVAR", "QMin MVAR"]
        for col in genadditional:
            n.generators.loc[gendata.loc[i, "Gen ID"], col] = \
                gendata.loc[i, col]


        "Start Time Cold Hr"
        "Start Time Warm Hr"
        "Start Time Hot Hr"
        "Start Heat Cold MBTU"
        "Start Heat Warm MBTU"
        "Start Heat Hot MBTU"
        "Non Fuel Start Cost $"
        "Non Fuel Shutdown Cost $"
        "FOR"
        "MTTF Hr"
        "MTTR Hr"
        "Scheduled Maint Weeks"
        "Fuel Price $/MMBTU"
        "Output_pct_0"
        "Output_pct_1"
        "Output_pct_2"
        "Output_pct_3"
        "Output_pct_4"
        "HR_avg_0"
        "HR_incr_1"
        "HR_incr_2"
        "HR_incr_3"
        "HR_incr_4"
        "VOM"
        "Fuel Sulfur Content %"
        "Emissions SO2 Lbs/MMBTU"
        "Emissions NOX Lbs/MMBTU"
        "Emissions Part Lbs/MMBTU"
        "Emissions CO2 Lbs/MMBTU"
        "Emissions CH4 Lbs/MMBTU"
        "Emissions N2O Lbs/MMBTU"
        "Emissions CO Lbs/MMBTU"
        "Emissions VOCs Lbs/MMBTU"
        "Damping Ratio"
        "Inertia MJ/MW"
        "Base MVA"
        "Transformer X p.u."
        "Unit X p.u."
        "Pump Load MW"
        "Storage Roundtrip Efficiency"

    n.generators.index = n.generators.index.astype(str)
    

def create_pypsa_network(input_folder, output_format, output):

    # create an empty pypsa network
    n = pypsa.Network()

    # add buses
    create_buses(n, input_folder)

    # add loads
    create_loads(n, input_folder)

    # add generators
    create_generators(n, input_folder)


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