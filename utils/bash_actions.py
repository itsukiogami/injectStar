import os
from utils.config_actions import read_config

def write_shebang(file):
    file.write('#!/bin/bash\n')

def write_sbatch(file, mag):
    config = read_config('slurm')
    hscconfig = read_config('hscPipe')
    jname = f'{os.path.basename(os.path.normpath(hscconfig['rerun']))}_artest_{str(mag)}'
    file.write('#SBATCH -p all\n')
    file.write('#SBATCH --ntasks=1\n')
    file.write(f'#SBATCH --cpus-per-task={hscconfig['cores']}\n')
    file.write(f'#SBATCH --job-name={jname}\n')
    file.write(f'#SBATCH --time={config['time']}\n')
    file.write(f'#SBATCH --mem={config['memory']}\n')

    if config['mail-type'] is not None and config['mail-user'] is not None:
        file.write(f'#SBATCH --mail-type={config['mail-type']}\n')
        file.write(f'#SBATCH --mail-user={config['mail-user']}\n')

def write_hscInit(file):
    file.write('\nexport OMP_NUM_THREADS = 1\n')
    file.write('setup-hscpipe\n')

def write_detectCoadd(file, filtkey, mag):
    config = read_config('hscPipe')

    command = 'detectCoaddSources.py'
    command += f' {os.path.dirname(os.path.dirname(os.path.normpath(config['rerun'])))}'
    command += f' --calib {os.path.dirname(os.path.normpath(config['rerun']))}/CALIB'
    command += f' --rerun {os.path.normpath(config['rerun']).rstrip('/') + '_artest/'}'
    command += f' --id filter={config[filtkey]}'
    command += f' tract={config['tract']}'
    command += ' --clobber-config'
    command += ' --clobber-versions'
    command += '\n'

    file.write(command)

def write_multiBand(file, filtstring, mag):
    config = read_config('hscPipe')
    
    command = 'multiBandDriver.py'
    command += f' {os.path.dirname(os.path.dirname(os.path.normpath(config['rerun'])))}'
    command += f' --calib {os.path.dirname(os.path.normpath(config['rerun']))}/CALIB'
    command += f' --rerun {os.path.normpath(config['rerun']).rstrip('/') + '_artest/'}'
    command += f' --id filter={filtstring}'
    command += f' tract={config['tract']}'
    command += ' --configfile artest_config.py'
    command += ' --clobber-config'
    command += ' --clobber-versions'
    command += ' --batch-type=smp'
    command += f' --cores={config['cores']}'
    
    command += '\n'

    file.write(command)

def write_injectStar(file, filter, mag):
    config = read_config('hscPipe')
    command = 'python3 injectStar_ver4.py'
    command += f' {os.path.normpath(config['rerun']).rstrip('/') + '_artest/'}'
    command += f' {config[filter]}'
    command += f' {config['tract']}'
    command += f' {mag}'
    command += '\n'

    file.write(command)

def write_inputCat(file):
    config = read_config('hscPipe')
    rerun = os.path.normpath(config['rerun']).rstrip('/') + '_artest/'
    command = f'cat {rerun}deepCoadd/{config['filter1']}/{config['tract']}/*.fits.txt > inputCat.txt'
    command += '\n'

    file.write(command)

def write_copyRerun(file):
    config = read_config('hscPipe')
    artest_path = os.path.normpath(config['rerun']).rstrip('/') + '_artest/'
    command = f'cp -r {os.path.normpath(config['rerun'])} {artest_path}\n'

    file.write(command)

def write_removeRerun(file):
    config = read_config('hscPipe')
    artest_path = os.path.normpath(config['rerun']).rstrip('/') + '_artest/'
    command = f'rm -r {artest_path}\n'

    file.write(command)
