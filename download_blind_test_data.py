import os
import subprocess
import shlex
import gzip
import shutil


# Examples of targets in each injected group.
inj1 = ('000757280', '000892667', '000892772', '001026328', '002303900',
        '001870424', '001026838', '012783889', '001432934', '012734617',
        '000893647', '000892713', '000892195', '001161338', '011722170')

inj2 = ('001725457', '001725555', '012599063', '012401597', '012553588',
        '001726045', '012598743', '001872349', '002447832', '012302919')

inj3 = ('005168382', '005168931', '011453605',
        '005168334', '005256626')


def get_file_info(target, file_name):
    '''
    Opens a .sh file with wget commands, read all the lines and get each star's id.

    Parameters
    ----------
    target      :   string_like
                    KIC number (like xxxxxxxxx) of the star to search for.
    file_name   :   string_like
                    Path to .sh file.
    
    Returns
    -------
    lines : list
            List of strings with all wget commands.
    ids   : list
            List of strings containing only the star's ids.    
    '''

    target = f'kplr{target}'

    with open(file_name, 'r') as file:
        lines = []
        ids = []
        for line in file:
            if (line[0] != '#'):
                if (line[0] != '\n'):
                    id = line.split(' ')[2].split('-')[0]
                    if id == target:
                        lines.append(line)
                        ids.append(id)

    return lines, ids


def download_blind_test_data(target, dv_file_name, lc_file_name):
    '''
    Downloads the files from the .sh files.

    Parameters
    ----------
    target          :   string_like
                        KIC number (like xxxxxxxxx) of the star to search for.
    dv_file_name    :   string_like
                        Path to Data Validation Reports .sh file.
    lc_file_name    :   string_like
                        Path to Light Curves .sh file.
    '''

    lines_dv, ids_dv = get_file_info(target, dv_file_name)
    lines_lc, ids_lc = get_file_info(target, lc_file_name)

    lc_relation = {}

    for position, id in enumerate(ids_dv):
        indices = [i for i, x in enumerate(ids_lc) if x == id]

        lc_relation[id] = {
            'dv_file': lines_dv[position],
            'quarters': [lines_lc[i] for i in indices]
        }

        # Construct the folder path for this id
        save_folder = f'data/{id}'
        print(f"Saving files in folder '{save_folder}'.")
        print()

        # Check if the folder exists; if not, create it
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)
            print(f"Folder created at: {save_folder}")
            print()


        # Download PDF DV
        print(f'Downloading DV PDF file...')
        cmd = lc_relation[id]['dv_file'].strip()
        args = shlex.split(cmd)
        # Execute the command in the specified directory
        # This makes sure that the downloaded file and log file are saved in save_folder.
        result = subprocess.run(args, cwd=save_folder, capture_output=True, text=True)
        # Optionally, check for errors or print the stdout/stderr
        if result.returncode != 0:
            print(f"Error executing command: {result.stderr}")
            print()
        

        # Loop over each wget command (assuming these are the commands with -O and -a options)
        for i, cmd in enumerate(lc_relation[id]['quarters']):
            # Remove any extra whitespace or newline characters
            cmd = cmd.strip()
            print(f"Downloading data for quarter q{i+1}")
            
            # Safely split the command string into arguments
            args = shlex.split(cmd)
            
            # Execute the command in the specified directory
            # This makes sure that the downloaded file and log file are saved in save_folder.
            result = subprocess.run(args, cwd=save_folder, capture_output=True, text=True)

            # Optionally, check for errors or print the stdout/stderr
            if result.returncode != 0:
                print(f"Error executing command: {result.stderr}")


        print()
        print('Unpacking files...')

        # Loop through all files in the folder
        for filename in os.listdir(save_folder):
            if filename.endswith('.gz'):
                gz_file_path = os.path.join(save_folder, filename)
                # Remove the ".gz" extension for the new file name
                output_file_path = os.path.join(save_folder, filename[:-3])
                
                # Unpack the .gz file
                with gzip.open(gz_file_path, 'rb') as f_in:
                    with open(output_file_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # Delete the original .gz file
                os.remove(gz_file_path)

        print(f'Files unpacked at {save_folder}.')



for inj_num, injection in enumerate((inj1, inj2, inj3)):
    dv_file = f'injected-dv-reports-dr25-inj{inj_num+1}.sh'
    lc_file = f'injected-light-curves-dr25-inj{inj_num+1}.sh'

    for target in inj1:
        download_blind_test_data(target, dv_file, lc_file)