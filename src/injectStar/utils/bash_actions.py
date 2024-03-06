import os


def shebang(file):
    '''
    Writes a shebang line to the beginning of the specified file.

    Parameters:
    - file: The file object to write the shebang line to.

    Returns:
    None
    '''
    file.write('#!/bin/bash\n')


def sbatch(config, file, mag):
    '''
    Writes Slurm batch job configuration to the specified file
    based on provided parameters.

    Parameters:
    - config: The config instance containing the configuration parameters.
    - file: The file object to write Slurm configuration to.
    - mag: An integer representing the magnitude.

    Returns:
    None
    '''
    slurmconfig = config['slurm']
    hscconfig = config['hscPipe']
    jname = f"{os.path.basename(os.path.normpath(hscconfig['rerun']))}" \
            f"_artest_{mag}"
    file.write('#SBATCH -p all\n')
    file.write(f"#SBATCH --ntasks={slurmconfig['ntasks']}\n")
    file.write(f"#SBATCH --cpus-per-task={hscconfig['cores']}\n")
    file.write(f"#SBATCH --job-name={jname}\n")
    file.write(f"#SBATCH --time={slurmconfig['time']}\n")
    file.write(f"#SBATCH --mem={slurmconfig['memory']}\n")

    if 'mail-type' in slurmconfig \
            and 'mail-user' in slurmconfig:
        file.write(f"#SBATCH --mail-type={slurmconfig['mail-type']}\n")
        file.write(f"#SBATCH --mail-user={slurmconfig['mail-user']}\n")


def hsc_init(config, setuphsc, file):
    '''
    Writes initialization parameters and exports for hscPipe
    to the specified file.

    Parameters:
    - config: The config instance containing the configuration parameters.
    - hscpipe: A string containing lines to setup hscPipe.
    - file: The file object to write initialization parameters and exports to.

    Returns:
    None
    '''
    hscconfig = config['hscPipe']
    hscdir = os.path.dirname(
        os.path.dirname(os.path.normpath(hscconfig['rerun'])))
    origrerun = os.path.normpath(hscconfig['rerun'])
    rerun = os.path.dirname(os.path.normpath(hscconfig['rerun'])) + '/artest'

    file.write(f"\n{setuphsc}")
    file.write('\nexport OMP_NUM_THREADS=1\n')
    file.write(f"export HSC=\'{hscdir}\'\n")
    file.write(f"export origrerun=\'{origrerun}\'\n")
    file.write(f"export rerun=\'{rerun}\'\n")


def detect_coadd(config, file, filtkey):
    '''
    Writes down the command to run detectCoaddSources to the specified file.

    Parameters:
    - config: The config instance containing the configuration parameters.
    - file: The file object to write the detectCoaddSources command to.
    - filtkey: A string representing the filter.

    Returns:
    None
    '''
    hscconfig = config['hscPipe']

    command = 'detectCoaddSources.py'
    command += ' $HSC'
    command += ' --calib $HSC/CALIB'
    command += ' --rerun $rerun'
    command += f" --id filter={hscconfig[filtkey]}"
    command += f" tract={hscconfig['tract']}"
    command += ' --clobber-config'
    command += ' --clobber-versions'
    command += '\n'

    file.write(command)


def multi_band(config, file, filtstring):
    '''
    Writes down the command to run multiBandDriver.py to the specified file.

    Parameters:
    - config: The config instance containing the configuration parameters.
    - file: The file object to write the multiBandDriver command to.
    - filtstring: A string representing filters joined with "^".

    Returns:
    None
    '''
    hscconfig = config['hscPipe']

    command = 'multiBandDriver.py'
    command += ' $HSC'
    command += ' --calib $HSC/CALIB'
    command += ' --rerun $rerun'
    command += f" --id filter={filtstring}"
    command += f" tract={hscconfig['tract']}"
    command += ' --configfile artest_config.py'
    command += ' --clobber-config'
    command += ' --clobber-versions'
    command += ' --batch-type=smp'
    command += f" --cores={hscconfig['cores']}"

    command += '\n'

    file.write(command)


def inject_star(config, file, filt, mag):
    '''
    Writes down the command to run injectStar_ver4 from the
    injectStar module to the specified file.

    Parameters:
    - config: The config instance containing the configuration parameters.
    - file: The file object to write the injectStar command to.
    - filter: A string representing the filter ID.
    - mag: An integer representing the magnitude.

    Returns:
    None
    '''
    hscconfig = config['hscPipe']
    command = 'python3 -m injectStar.injectStar_ver4'
    command += ' $rerun'
    command += f" {filt}"
    command += f" {hscconfig['tract']}"
    command += f" {mag}"
    command += '\n'

    file.write(command)


def input_cat(config, file):
    '''
    Writes down the command to concatenate input catalogs
    to the specified file.

    Parameters:
    - config: The config instance containing the configuration parameters.
    - file: The file object to write the command to.

    Returns:
    None
    '''
    hscconfig = config['hscPipe']
    command = f"cat $rerun/deepCoadd/{hscconfig['filter1']}" \
              f"/{hscconfig['tract']}*.fits.txt > inputCat.txt"
    command += '\n'

    file.write(command)


def copy_rerun(file):
    '''
    Writes down the command to copy the rerun directory to a
    new temporary directory named "artest/".

    Parameters:
    - file: The file object to write the command to.

    Returns:
    None
    '''
    command = 'rsync -a --delete --inplace --progress ' \
        '--exclude=\'$origrerun/postISRCCD\' $origrerun/ $rerun\n'
    file.write(command)


def remove_rerun(file):
    '''
    Writes down the command to remove the temporary rerun directory.

    Parameters:
    - file: The file object to write the command to.

    Returns:
    None
    '''
    command = 'rm -r $rerun\n'
    file.write(command)
