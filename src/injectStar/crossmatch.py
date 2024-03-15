import argparse
import os
import shutil
import numpy as np
import pandas as pd
import injectStar.utils.config_actions as config_actions


def distance(x1, x2, y1, y2):
    '''
    Calculate the distance between (x1, y1) and (x2, y2)
    coordinate sets.
    '''
    return np.hypot(x2 - x1, y2 - y1)


def main(args):

    config = config_actions.read_config(
             config_file=f"{args['workdir']}/config.txt")
    hscconfig = config['hscPipe']
    dirconfig = config['dirs']

    inputdir = os.path.normpath(dirconfig['input']).replace(os.sep, '/')
    outputdir = os.path.normpath(dirconfig['output']).replace(os.sep, '/')

    filters = [hscconfig[key] for key in sorted(hscconfig.keys())
               if key.startswith('filter')]
    magstring = args['magstring']
    mags = magstring.spli('_')
    rerun = os.path.basename(os.path.normpath(hscconfig['rerun']))

    # Define column names
    columns = []
    for f in filters:
        columns.append([f"{f}_mag", f"{f}_matches", f"{f}_total",
                        f"{f}_ratio", f"{f}_ratio_err"])

    # Create an empty DataFrame with specified column names
    matches = pd.DataFrame(columns=columns)

    # Requirements for an acceptable match
    mindist = 1/3600  # 1 arcsec
    minmag = 0.1

    csv_kwargs = {'delim_whitespace': True,
                  'header': None}
    for i, f in enumerate(filters):
        matches[f"{f}_total"] = float(mags[i])
        input_path = inputdir+f"input_{rerun}_{f}_{magstring}.txt"
        output_path = outputdir+f"output_{rerun}_{f}_{magstring}.csv"

        input_df = pd.read_csv(input_path, **csv_kwargs)
        input_df.columns = ['ra', 'dec', 'mag']
        output_df = pd.read_csv(output_path, **csv_kwargs)
        output_df.columns = ['id', 'ra', 'dec', 'mag', 'mag_err', 'flag']
        # This picks out fake stars only
        output_df = output_df[output_df['flag']].reset_index(drop=True)

        match_count = 0
        for j in range(len(input_df)):
            # If there's a star within 1 arcsec and 0.1 mag, it's a match
            # TODO: better distance calculation with ra/dec
            mask = (distance(input_df['ra'].iloc[j], output_df['ra'],
                             input_df['dec'].iloc[j],
                             output_df['dec']) < mindist**2)
            mask = mask & (np.abs(input_df['mag'].iloc[j] - output_df['mag'])
                           < minmag)
            if np.sum(mask) > 0:
                match_count += 1
        matches[f"{f}_total"] = len(input_df)
        matches[f"{f}_matches"] = match_count
        matches[f"{f}_ratio"] = match_count/len(input_df)
        matches[f"{f}_ratio_err"] = np.sqrt(match_count)/len(input_df)

    # Save the matches
    sname = f"{args['workdir']}/matches.csv"
    if os.path.exists(sname):
        matches_df = pd.read_csv(sname, **csv_kwargs)
        if set(matches_df.columns) != set(matches.keys()):
            print('WARNING: matches.csv has different filters'
                  'than the current ast run.')
            print('Making a copy of the original matches.csv file.')
            shutil.copyfile(sname, f"{args['workdir']}/matches_copy.csv")
            matches.to_csv(sname, index=False)
        else:
            matches = matches_df.append(matches, ignore_index=True)
    matches.to_csv(sname, index=False)


def parse_args():
    parser = argparse.ArgumentParser(
        description='Use crossmatch.py to crossmatch '
                    'the input and output files.\n'
                    'This script is intended to be '
                    'run via a job file and not manually.'
        )
    parser.add_argument('workdir',
                        help='Workspace where config.txt is located.')
    parser.add_argument('magstring',
                        help='A string representing the'
                        'magnitudes used in this run.')
    return parser.parse_args()


if __name__ == '__main__':
    main(parse_args())
