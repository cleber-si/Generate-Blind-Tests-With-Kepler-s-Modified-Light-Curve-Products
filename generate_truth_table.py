from astropy.io import ascii
import numpy as np
import pandas as pd


def generate_truth_table(groups, tables, relation):
    status_relation = {
        'inj1' : 'planet',
        'inj2' : 'background_interference',
        'inj3' : 'eclipsing_binary'
    }

    with open('blind_test/blind_test_truth_table.csv', 'w') as log:
        log.write(f"#Truth table for 30 light curves extracted from Kepler's Simulated Data injections 1, 2 and 3. \n")
        log.write("#(For more details, refer to https://exoplanetarchive.ipac.caltech.edu/docs/KeplerSimulated.html) \n")
        log.write(f"#Author: Cleber Silva.\n#April, 2025.\n#Stellar Team.\n")
        log.write(f"#The comments below indicate each column value.\n")
        log.write("#file: File name for a given light curve;\n")
        log.write("#id: KIC number for the target;\n") 
        log.write("#group: Injected group;\n")
        log.write("#planet_status: Nature of the injected signal;\n")
        log.write("#period: Period of the injected signal;\n")
        log.write("#epoch: Epoch of the injected signal;\n")
        log.write("#num_tran: Number of transits/drops present in the lightcurve;\n")
        log.write("#depth: Depth of the transit/drops;\n")
        log.write("#duration: Duration of the transit/drops;\n")
        log.write("#R_p: Planet radius;\n")
        log.write("#R_s: Star radius;\n")
        log.write("#R_p/R_s: Planet to star radius ratio;\n")
        log.write("#a: Semi-major axis.\n")
        
        log.write(f'file,id,group,planet_status,period,epoch,num_tran,depth,duration,R_p,R_s,R_p/R_s,a\n')

        for i, table in enumerate(tables):
            status = status_relation[groups[i]]

            for row in table:
                folder = f'kplr{row['TCE_ID'].split('-')[0]}'
                index = relation[relation['id'] == folder]['file'].values[0].split('_')[1]

                period = row['period']
                epoch = row['epoch']
                num_tran = row['NTran']
                depth = row['depth']
                duration = row['duration']
                R_p = row['Rp']
                R_s = row['Rs']
                R_p_R_s_ratio = row['Rp/Rs']
                a = row['a']
                
                log.write(f"file_{index},{folder},{groups[i]},{status},{period},{epoch},{num_tran},{depth},{duration},{R_p},{R_s},{R_p_R_s_ratio},{a}\n")


# Load Table
ipac_files = ['kplr_dr25_inj1_tces.txt', 'kplr_dr25_inj2_tces.txt', 'kplr_dr25_inj3_tces.txt']
ipac_data_1 = ascii.read(ipac_files[0])
ipac_data_2 = ascii.read(ipac_files[1])
ipac_data_3 = ascii.read(ipac_files[2])

relation = pd.read_csv('blind_test/blind_test_ids.csv')

data_files_numbers = [int(data_file.split('r')[1]) for data_file in list(relation['id'])]


mask_1 = np.isin(ipac_data_1['KIC'], data_files_numbers)
filtered_1 = ipac_data_1[mask_1]

mask_2 = np.isin(ipac_data_2['KIC'], data_files_numbers)
filtered_2 = ipac_data_2[mask_2]

mask_3 = np.isin(ipac_data_3['KIC'], data_files_numbers)
filtered_3 = ipac_data_3[mask_3]

generate_truth_table(['inj1','inj2','inj3'], [filtered_1, filtered_2, filtered_3], relation)
