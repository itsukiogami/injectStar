import argparse
import os
import shutil
import numpy as np
import pandas as pd
from injectStar.utils import config_actions
from astropy.coordinates import SkyCoord
from astropy import units as u


def distance(x1, x2, y1, y2):
    '''
    Calculate the distance between (x1, y1) and (x2, y2)
    coordinate sets.
    '''
    return np.hypot(x2 - x1, y2 - y1)


def angular_distance(ra1, ra2, dec1, dec2, unit_ra=u.deg, unit_deg=u.deg):
    '''
    Calculate angular separation in arseconds
    '''
    c1 = SkyCoord(ra1, dec1, unit=(unit_ra, unit_deg))
    c2 = SkyCoord(ra2, dec2, unit=(unit_ra, unit_deg))
    return c1.separation(c2).degree*3600


def spatial_preselect(ra_c, ra, dec_c, dec, decdist):
    '''
    Preselect sources in a square defined by the maximum
    allowed distance (decdist).
    This function is used for a quicker but less precise
    spacial pre-selection before angular_distance() is run.
    '''
    radist = decdist/np.cos(np.deg2rad(ra_c))
    mask = (ra > ra_c - radist) & (ra < ra_c + radist)
    mask = (dec > dec_c-decdist) & (dec < dec_c + decdist)
    return mask


def main(args):
    '''
    The main function
    '''
    config = config_actions.read_config(
             config_file=f"{args.workdir}/config.txt")
    hscconfig = config['hscPipe']
    dirconfig = config['dirs']

    inputdir = os.path.normpath(dirconfig['input']).replace(os.sep, '/')
    outputdir = os.path.normpath(dirconfig['output']).replace(os.sep, '/')

    filters = [hscconfig[f"filter{i}"]
               for i in range(1, int(hscconfig['filters']) + 1)]
    magstring = args.magstring
    mags = np.array(magstring.split('_'), dtype=float)
    input_columns = ['ra', 'dec', 'mag']

    # Define column names to be saved later
    columns = []
    for f in filters:
        columns += [f"{f}_mag", f"{f}_matches", f"{f}_total",
                    f"{f}_ratio", f"{f}_ratio_err"]

    # Create an empty dictionary that will be saved
    # into a dataframe as a row
    matches = {}

    # Requirements for an acceptable match
    mindist = 1/3600  # 1 arcsec
    minmag = 0.1

    csv_kwargs = {'delim_whitespace': True,
                  'header': None}
    for i, (f, mag) in enumerate(zip(filters, mags)):
        matches[f"{f}_mag"] = mag
        input_path = inputdir+f"/input_{f}_{magstring}.txt"
        output_path = outputdir+f"/output_{f}_{magstring}.csv"
        input_df = pd.read_csv(input_path, names=input_columns, **csv_kwargs)
        output_df = pd.read_csv(output_path)
        output_df = output_df[np.abs(mag - output_df['mag']) < minmag]
        # This picks out fake stars only
        output_df = output_df[output_df['flag']].reset_index(drop=True)

        match_count = 0
        for j in range(len(input_df)):
            ra, dec = input_df['ra'].iloc[j], input_df['dec'].iloc[j]

            # If there's a star within 1 arcsec and 0.1 mag, it's a match
            mask = spatial_preselect(ra, output_df['ra'],
                                     dec, output_df['dec'], mindist)
            temp_df = output_df[mask]
            mask = (angular_distance(ra, temp_df['ra'],
                                     dec, temp_df['dec'])
                                     < mindist)
            temp_df = temp_df[mask]

            if len(temp_df) > 0:
                match_count += 1

        matches[f"{f}_total"] = len(input_df)
        matches[f"{f}_matches"] = match_count
        matches[f"{f}_ratio"] = match_count/len(input_df)
        matches[f"{f}_ratio_err"] = np.sqrt(match_count)/len(input_df)

    # Create an empty DataFrame with specified column names
    matches_df = pd.DataFrame([matches])[columns]
    matches_df.index = [magstring]

    # Save the matches
    sname = f"{args.workdir}/matches.csv"
    if os.path.exists(sname):
        matches_df_old = pd.read_csv(sname)
        if set(matches_df_old.columns) != set(matches_df.columns):
            print('Columns')
            print(set(matches_df_old.columns), set(matches_df.columns))
            print('WARNING: matches.csv has different filters '
                  'than the current ast run.')
            print('Making a copy of the original matches.csv file.')
            shutil.copyfile(sname, f"{args.workdir}/matches_copy.csv")
        else:
            matches_df = matches_df_old.append(matches_df, ignore_index=True)

    matches_df.to_csv(sname, index=False)


def parse_args():
    '''
    The argument parsing function
    '''
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
