import os
import argparse
import numpy as np
import injectStar.utils.bash_actions as bash_actions
import injectStar.utils.config_actions as config_actions


def main(args):
    # Read in config and generate magnitudes
    config = config_actions.read_config()
    hscconfig = config['hscPipe']
    setuphsc = config_actions.read_setuphsc()

    # TODO Are same-magnitude pairs enough, or should we make a grid?
    mags = np.arange(float(hscconfig['mag_start']),
                     float(hscconfig['mag_end']) +
                     float(hscconfig['mag_step']),
                     float(hscconfig['mag_step']))

    # Rerun name for naming job files
    rerunname = os.path.basename(os.path.normpath(hscconfig['rerun']))

    if args.use_slurm:
        suffix = 'sbatch'
    else:
        suffix = 'sh'

    # Iterate over magnitudes and fill in the .sbatch files
    for mag in mags:
        # Generate file
        fname = f"{rerunname}_{mag}.{suffix}"
        file = open(fname, 'w')

        # Write bash/slurm/hscpipe initialisations
        bash_actions.shebang(file)
        if args.use_slurm:
            bash_actions.sbatch(config, file, mag)
        bash_actions.hsc_init(config, setuphsc, file)

        file.write('\n# Step 1: Copy the rerun directory.\n')
        file.write('echo "Copying the rerun directory."\n')
        bash_actions.copy_rerun(file)

        file.write('\n# Step 2: Run injectStar on all filters.\n')
        file.write('echo "Running injectStar."\n')
        filtkeys = [key for key in sorted(hscconfig.keys())
                    if key.startswith('filter')]
        for key in filtkeys:
            bash_actions.inject_star(config, file, hscconfig[key], mag)

        file.write('\n# Step 3: Run detectCoaddSources on all filters.\n')
        file.write('echo "Running detectCoaddSources."\n')
        for key in filtkeys:
            bash_actions.detect_coadd(config, file, key)

        file.write("\n# Step 4: Run multiBandDriver on all filters"
                   " simultaneously.\n")
        file.write('echo "Running multiBandDriver."\n')
        filtstring = '^'.join([hscconfig[key] for key in filtkeys])
        bash_actions.multi_band(config, file, filtstring)

        # TODO: Output catalog creation command
        # (Might need to write a separate script for that!)
        file.write('\n# Step 5: Generate a catalogue of output data.\n')
        file.write('echo "Generating the output catalogue."\n')

        # TODO: Check if one filter is enough for this
        file.write('\n# Step 6: Generate a catalogue of all input sources.\n')
        file.write('echo "Generating the input catalogue."\n')
        bash_actions.input_cat(config, file)

        # TODO: Cross-match command
        # (Might need to write a separate script for that!)
        file.write('\n# Step 7: Cross-match input and output catalogues.\n')
        file.write('echo "Cross-matching catalogues."\n')

        # Currently not deleting the rerun directory due to rsync
        # file.write('\n# Step 8: Delete the temporary coadd directory.\n')
        # file.write('echo "Deleting the temporary rerun directory."\n')
        # bash_actions.remove_rerun(file)

        file.write('\necho "Job completed successfully!"\n')
        file.close()


def parse_args():
    parser = argparse.ArgumentParser(
        description='Use makeJobs.py to generate BASH or SLURM batch files.'
        )
    parser.add_argument('--use_slurm', action='store_true',
                        help='Add SLURM commands to job files.')
    return parser.parse_args()


if __name__ == '__main__':
    main(parse_args())
