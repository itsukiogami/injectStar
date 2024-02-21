import os
import numpy as np
import utils.bash_actions as bash_actions
import argparse
from utils.config_actions import read_config


def main(args):
    # Read in config and generate magnitudes
    config = read_config('hscPipe')

    # TODO Are same-magnitude pairs enough, or should we make a grid?
    mags = np.arange(float(config['mag_start']), float(config['mag_end']) + float(config['mag_step']), float(config['mag_step']))
    
    if args.use_slurm:
        suffix = 'sbatch'
    else:
        suffix = 'sh'

    # Iterate over magnitudes and fill in the .sbatch files
    for mag in mags:
        # Generate file
        fname = f'{os.path.basename(os.path.normpath(config['rerun']))}_{mag}.{suffix}'
        file = open(fname, 'w')

        # Write bash/slurm/hscpipe initialisations
        bash_actions.write_shebang(file)
        if args.use_slurm:
            bash_actions.write_sbatch(file, mag)
        bash_actions.write_hscInit(file)

        file.write('\n# Step 1: Copy the rerun directory.\n')
        file.write('echo "Copying the rerun directory."\n')
        bash_actions.write_copyRerun(file)

        file.write('\n# Step 2: Run injectStar on all filters.\n')
        file.write('echo "Running injectStar."\n')
        filtkeys = [key for key in sorted(config.keys()) if key.startswith('filter')]
        for key in filtkeys:
            bash_actions.write_injectStar(file, key, mag)
        
        file.write('\n# Step 3: Run detectCoaddSources on all filters.\n')
        file.write('echo "Running detectCoaddSources."\n')
        for key in filtkeys:
            bash_actions.write_detectCoadd(file, key, mag)

        file.write('\n# Step 4: Run multiBandDriver on all filters simultaneously.\n')
        file.write('echo "Running multiBandDriver."\n')
        filtstring = '^'.join([config[key] for key in filtkeys])
        bash_actions.write_multiBand(file, filtstring, mag)

        # TODO: Output catalog creation command (Might need to write a separate script for that!)
        file.write('\n# Step 5: Generate a catalogue of output data.\n')
        file.write('echo "Generating output catalogue."\n')

        # TODO: Check if one filter is enough for this
        file.write('\n# Step 6: Generate a catalogue of all input sources.\n')
        file.write('echo "Generating input catalogue."\n')
        bash_actions.write_inputCat(file)

        # TODO: Cross-match command (Might need to write a separate script for that!)
        file.write('\n# Step 7: Cross-match input and output catalogues.\n')
        file.write('echo "Cross-matching catalogues."\n')

        file.write('\n# Step 8: Delete the temporary coadd directory.\n')
        file.write('echo "Deleting the temporary rerun directory."\n')
        bash_actions.write_copyRerun(file)

        file.write('\necho "Job completed successfully!"\n')
        file.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Use makeJobs.py to generate BASH or SLURM batch files.')
    parser.add_argument('--use_slurm', action='store_true', help='Use SLURM for execution')
    args = parser.parse_args()
    main(args)