import os
import argparse
import numpy as np
import pandas as pd
import injectStar.utils.bash_actions as bash_actions
import injectStar.utils.config_actions as config_actions


def group_mags(hscconfig):
    '''
    Creates all possible groupings of filter magnitudes

    Parameters:
    - hscconfig: A dictionary containing the filter configuration parameters.

    Returns:
    A pandas DataFrame with magnitude groupings
    '''
    # Make all possible magnitude pairs
    filtnum = int(hscconfig['filters'])
    for i in range(1, filtnum + 1):
        filtname = hscconfig[f"filter{i}"]
        mags = np.arange(float(hscconfig[f"mag_start{i}"]),
                         float(hscconfig[f"mag_end{i}"]) +
                         float(hscconfig['mag_step']),
                         float(hscconfig['mag_step']))
        tempdf = pd.DataFrame({filtname: mags})
        tempdf['key'] = 0  # dummy key used for merging
        if i == 1:
            mags_grouped = tempdf
        else:
            mags_grouped = pd.merge(mags_grouped, tempdf,
                                    on='key', how='outer')

    return mags_grouped.drop('key', axis=1)


def main(args):
    '''
    The main function
    '''
    # Read in config
    config = config_actions.read_config()
    hscconfig = config['hscPipe']
    jobdir = os.path.normpath(config['dirs']['jobs']).replace(os.sep, '/')

    setuphsc = config_actions.read_setuphsc()

    # Generate magnitude groups
    mags_grouped = group_mags(hscconfig)
    filtstring = '^'.join(mags_grouped.columns)  # Used in HSC commands

    # Rerun name for naming job files
    rerunname = os.path.basename(os.path.normpath(hscconfig['rerun']))

    if args.use_slurm:
        suffix = 'sbatch'
    else:
        suffix = 'sh'

    # Iterate over magnitudes and fill in the .sbatch files
    for _, row in mags_grouped.iterrows():

        # Used in file naming
        magstring = [f'{value:.2f}' for _, value in row.items()]
        magstring = '_'.join(magstring)

        # Generate file
        print(jobdir)
        fname = f"{jobdir}/{rerunname}_{magstring}.{suffix}"
        file = open(fname, 'w', encoding="utf-8")

        # Write bash/slurm/hscpipe initialisations
        bash_actions.shebang(file)
        if args.use_slurm:
            bash_actions.sbatch(config, file, magstring)
        bash_actions.hsc_init(config, setuphsc, file)

        file.write('\n# Step 1: Copy the rerun directory.\n')
        file.write('echo "Copying the rerun directory."\n')
        bash_actions.copy_rerun(file)

        file.write('\n# Step 2: Run injectStar on all filters.\n')
        file.write('echo "Running injectStar."\n')
        for filt, mag in row.items():
            bash_actions.inject_star(config, file, filt, mag)

        file.write('\n# Step 3: Run detectCoaddSources on all filters.\n')
        file.write('echo "Running detectCoaddSources."\n')
        for filt, _ in row.items():
            bash_actions.detect_coadd(config, file, filt)

        file.write("\n# Step 4: Run multiBandDriver on all filters"
                   " simultaneously.\n")
        file.write('echo "Running multiBandDriver."\n')
        bash_actions.multi_band(config, file, filtstring)

        file.write('\n# Step 5: Generate a catalogue of all input sources.\n')
        file.write('echo "Generating the input catalogue."\n')
        for filt, _ in row.items():
            bash_actions.input_cat(config, file, filt, magstring)

        file.write('\n# Step 6: Generate a catalogue of output data.\n')
        file.write('echo "Generating the output catalogue."\n')
        bash_actions.output_cat(file, magstring)

        file.write('\n# Step 7: Cross-match input and output catalogues.\n')
        file.write('echo "Cross-matching catalogues."\n')
        bash_actions.crossmatch(file, magstring)

        # Currently not deleting the rerun directory due to rsync
        # file.write('\n# Step 8: Delete the temporary coadd directory.\n')
        # file.write('echo "Deleting the temporary rerun directory."\n')
        # bash_actions.remove_rerun(file)

        file.write('\necho "Job completed successfully!"\n')
        file.close()


def parse_args():
    '''
    The argument parsing function
    '''
    parser = argparse.ArgumentParser(
        description='Use makeJobs.py to generate BASH or SLURM batch files.'
        )
    parser.add_argument('--use_slurm', action='store_true',
                        help='Add SLURM commands to job files.')
    return parser.parse_args()


if __name__ == '__main__':
    main(parse_args())
