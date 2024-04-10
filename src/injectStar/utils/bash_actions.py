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


def sbatch(config, file, magstring):
    '''
    Writes Slurm batch job configuration to the specified file
    based on provided parameters.

    Parameters:
    - config: The config instance containing the configuration parameters.
    - file: The file object to write Slurm configuration to.
    - magstring: A string representing the magnitudes used in this run.

    Returns:
    None
    '''
    slurmconfig = config['slurm']
    hscconfig = config['hscPipe']
    jname = f"{os.path.basename(os.path.normpath(hscconfig['rerun']))}" \
            f"_artest_{magstring}"
    file.write('#SBATCH -p all\n')
    file.write(f"#SBATCH --ntasks={slurmconfig['ntasks']}\n")
    file.write(f"#SBATCH --cpus-per-task={hscconfig['cores']}\n")
    file.write(f"#SBATCH --job-name={jname}\n")
    file.write(f"#SBATCH --time={slurmconfig['time']}\n")
    file.write(f"#SBATCH --mem={slurmconfig['memory']}\n")

    if slurmconfig['mail-type'] != '' \
            and slurmconfig['mail-user'] != '':
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
    workdir = os.path.normpath(config['dirs']['workspace']
                               ).replace(os.sep, '/')

    origrerun = os.path.normpath(hscconfig['rerun']).replace(os.sep, '/')
    hscdir = os.path.dirname(os.path.dirname(origrerun))
    rerun = os.path.dirname(origrerun) + '/artest'

    file.write(f"\n{setuphsc}")
    file.write('\nexport OMP_NUM_THREADS=1\n')
    file.write(f"export HSC=\'{hscdir}\'\n")
    file.write(f"export origrerun=\'{origrerun}\'\n")
    file.write(f"export rerun=\'{rerun}\'\n")
    file.write(f"export workdir=\'{workdir}'\n")


def detect_coadd(config, file, filt):
    '''
    Writes down the command to run detectCoaddSources to the specified file.

    Parameters:
    - config: The config instance containing the configuration parameters.
    - file: The file object to write the detectCoaddSources command to.
    - filt: A string representing the filter (e.g. "HSC-G").

    Returns:
    None
    '''
    hscconfig = config['hscPipe']

    command = 'detectCoaddSources.py'
    command += ' $HSC'
    command += ' --calib $HSC/CALIB'
    command += ' --rerun $rerun'
    command += f" --id filter={filt}"
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
    command += ' --configfile ../artest_config.py'
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
    - filt: A string representing the filter name.
    - mag: A string representing the magnitude.

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


def input_cat(config, file, filt, magstring):
    '''
    Writes down the command to concatenate input catalogs
    to the specified job file.

    Parameters:
    - config: The config instance containing the configuration parameters.
    - file: The file object to write the command to.
    - filt: A string representing the filter name.
    - magstring: A string representing the magnitudes used in this run.

    Returns:
    None
    '''
    hscconfig = config['hscPipe']
    dirconfig = config['dirs']
    inputdir = os.path.normpath(dirconfig['input']
                                ).replace(os.sep, '/')
    command = f"cat $rerun/deepCoadd/{filt}" \
              f"/{hscconfig['tract']}/*.fits.txt >" \
              f"{inputdir}/input_{filt}_{magstring}.txt"
    command += '\n'

    file.write(command)


def output_cat(file, magstring):
    '''
    Writes down the command to run the output catalog
    creation script to the specified job file.

    Parameters:
    - file: The file object to write the command to.
    - magstring: A string representing the magnitudes used in this run.

    Returns:
    None
    '''
    command = f"python3 -m injectStar.outputCatalog {os.getcwd()}" \
              f" {magstring}\n"

    file.write(command)


def crossmatch(file, magstring):
    '''
    Writes down the command to run the crossmatch catalog
    creation script to the specified job file.

    Parameters:
    - file: The file object to write the command to.
    - magstring: A string representing the magnitudes used in this run.

    Returns:
    None
    '''
    command = f"python3 -m injectStar.crossmatch {os.getcwd()}" \
              f" {magstring}\n"

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
