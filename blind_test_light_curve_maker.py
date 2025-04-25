from astropy.io import fits
import wotan as wt
import os
import glob
import pandas as pd


def get_lightcurve(folder):
    '''
    Search for .fits files in a folder to extract time and flux values to build a light curve.

    Parameters
    ----------
    folder      :   string_like
                    Path of the folder containing the .fits data of a star.
    
    Returns
    -------
    flattened_time      :   list
                            List of floats with all time values.
    flatten_sap_lc      :   list
                            List of floats with all SAP flux values.
    flattened_pdsap_lc  :   list
                            List of floats with all PDSAP flux values.
    '''
    pattern = '*.fits'

    fits_files = glob.glob(os.path.join(folder, pattern), recursive=False)
    fits_files.sort()

    all_data = {}

    for i, fits_file in enumerate(fits_files):
        with fits.open(fits_file) as hdul:
            data = hdul[1].data

            all_data[f'q{i+1}'] = data

    keys = all_data.keys()

    all_time = []
    all_sap_flux = []
    all_pdsap_flux = []

    for key in keys:
        time = all_data[key]['TIME']
        sap_flux = all_data[key]['SAP_FLUX']
        pdsap_flux = all_data[key]['PDCSAP_FLUX']

        all_time.append(time)
        all_sap_flux.append(sap_flux)
        all_pdsap_flux.append(pdsap_flux)

    def concatenate(array):
        return [item for sublist in array for item in sublist]

    flattened_time = concatenate(all_time)
    flattened_sap_flux = concatenate(all_sap_flux)
    flattened_pdsap_flux = concatenate(all_pdsap_flux)

    flatten_sap_lc = wt.flatten(flattened_time,
                                flattened_sap_flux,
                                window_length=0.5,
                                method='biweight',
                                return_trend=False)
    
    flattened_pdsap_lc = wt.flatten(flattened_time,
                                      flattened_pdsap_flux,
                                      window_length=0.5,
                                      method='biweight',
                                      return_trend=False)
    
    
    return flattened_time, flatten_sap_lc, flattened_pdsap_lc


# Considering that all the data are in a folder called "data".
folders = os.listdir('data')

# Write all the blind test information in csv files.
with open('blind_test/blind_test_ids.csv', 'w') as log:
    log.write(f'file,id\n')

    for index, folder in enumerate(folders):
        folder_path = f'data/{folder}'

        log.write(f'file_{index},{folder}\n')

        flattened_time, flatten_sap_lc, flattened_pdsap_lc = get_lightcurve(folder_path)

        data = {
            'time' : flattened_time,
            'flux' : flattened_pdsap_lc
        }

        pd.DataFrame(data).to_csv(f'blind_test/file_{index}.csv', index=False)