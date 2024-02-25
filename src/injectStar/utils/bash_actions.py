import os
from injectStar.utils.config_actions import read_config

def write_shebang(file):
    '''
    Writes a shebang line to the beginning of the specified file.

    Parameters:
    - file: The file object to write the shebang line to.

    Returns:
    None
    '''
    file.write('#!/bin/bash\n')

def write_sbatch(file, mag):
    '''
    Writes Slurm batch job configuration to the specified file based on provided parameters.

    Parameters:
    - file: The file object to write Slurm configuration to.
    - mag: An integer representing the magnitude.

    Returns:
    None
    '''
    config = read_config('slurm')
    hscconfig = read_config('hscPipe')
    jname = f"{os.path.basename(os.path.normpath(hscconfig['rerun']))}_artest_{mag}"
    file.write('#SBATCH -p all\n')
    file.write('#SBATCH --ntasks=1\n')
    file.write(f"#SBATCH --cpus-per-task={hscconfig['cores']}\n")
    file.write(f"#SBATCH --job-name={jname}\n")
    file.write(f"#SBATCH --time={config['time']}\n")
    file.write(f"#SBATCH --mem={config['memory']}\n")

    if config['mail-type'] is not None and config['mail-user'] is not None:
        file.write(f"#SBATCH --mail-type={config['mail-type']}\n")
        file.write(f"#SBATCH --mail-user={config['mail-user']}\n")

def write_hscInit(file):
    '''
    Writes initialization parameters and exports for hscPipe to the specified file.

    Parameters:
    - file: The file object to write initialization parameters and exports to.

    Returns:
    None
    '''
    config = read_config('hscPipe')
    hscdir = os.path.dirname(os.path.dirname(os.path.normpath(config['rerun'])))
    origrerun = os.path.normpath(config['rerun'])
    rerun = os.path.dirname(os.path.normpath(config['rerun'])) + '/artest'

    file.write('\nexport OMP_NUM_THREADS = 1\n')
    file.write('setup-hscpipe\n')
    file.write(f"export HSC={hscdir}\n")
    file.write(f"export origrerun=\'{origrerun}\'\n")
    file.write(f"export rerun={rerun}\n")

def write_detectCoadd(file, filtkey):
    '''
    Writes down the command to run detectCoaddSources to the specified file.

    Parameters:
    - file: The file object to write the detectCoaddSources command to.
    - filtkey: A string representing the filter.

    Returns:
    None
    '''
    config = read_config('hscPipe')

    command = 'detectCoaddSources.py'
    command += f' $HSC'
    command += f' --calib $HSC/CALIB'
    command += f' --rerun $rerun'
    command += f" --id filter={config[filtkey]}"
    command += f" tract={config['tract']}"
    command += ' --clobber-config'
    command += ' --clobber-versions'
    command += '\n'

    file.write(command)

def write_multiBand(file, filtstring):
    '''
    Writes down the command to run multiBandDriver.py to the specified file.

    Parameters:
    - file: The file object to write the multiBandDriver command to.
    - filtstring: A string representing filters joined with "^".

    Returns:
    None
    '''
    config = read_config('hscPipe')
    
    command = 'multiBandDriver.py'
    command += ' $HSC'
    command += ' --calib $HSC/CALIB'
    command += ' --rerun $rerun'
    command += f" --id filter={filtstring}"
    command += f" tract={config['tract']}"
    command += ' --configfile artest_config.py'
    command += ' --clobber-config'
    command += ' --clobber-versions'
    command += ' --batch-type=smp'
    command += f" --cores={config['cores']}"
    
    command += '\n'

    file.write(command)

def write_injectStar(file, filter, mag):
    '''
    Writes down the command to run injectStar_ver4 from the injectStar module to the specified file.

    Parameters:
    - file: The file object to write the injectStar command to.
    - filter: A string representing the filter.
    - mag: An integer representing the magnitude.

    Returns:
    None
    '''
    config = read_config('hscPipe')
    command = 'python3 -m injectStar.injectStar_ver4'
    command += ' $rerun'
    command += f" {config[filter]}"
    command += f" {config['tract']}"
    command += f" {mag}"
    command += '\n'

    file.write(command)

def write_inputCat(file):
    '''
    Writes down the command to concatenate input catalogs to the specified file.

    Parameters:
    - file: The file object to write the command to.

    Returns:
    None
    '''
    config = read_config('hscPipe')
    rerun = os.path.normpath(config['rerun']).rstrip('/') + '_artest/'
    command = f"cat $rerun/deepCoadd/{config['filter1']}/{config['tract']}/*.fits.txt > inputCat.txt"
    command += '\n'

    file.write(command)

def write_copyRerun(file):
    '''
    Writes down the command to copy the rerun directory to a new temporary directory named "artest/".

    Parameters:
    - file: The file object to write the command to.

    Returns:
    None
    '''
    config = read_config('hscPipe')
    artest_path = os.path.normpath(config['rerun']).rstrip('/') + '_artest/'
    command = 'cp -r $origrerun $rerun\n'

    file.write(command)

def write_removeRerun(file):
    '''
    Writes down the command to remove the temporary rerun directory.

    Parameters:
    - file: The file object to write the command to.

    Returns:
    None
    '''
    config = read_config('hscPipe')
    command = 'rm -r $rerun\n'

    file.write(command)
