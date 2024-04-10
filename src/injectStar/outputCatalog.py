import argparse
import os
import numpy as np
import pandas as pd
from injectStar.utils import config_actions
from lsst.daf.persistence import Butler


def main(args):
    '''
    The main function
    '''
    zp = 27.0  # Zeropoint

    # Read in config and generate magnitudes
    config = config_actions.read_config(
             config_file=f"{args['workdir']}/config.txt")
    hscconfig = config['hscPipe']
    outputdir = os.path.normpath(config['dirs']['output']).replace(os.sep, '/')

    origrerun = os.path.normpath(hscconfig['rerun']).replace(os.sep, '/')
    hscdir = os.path.dirname(os.path.dirname(origrerun))
    filters = [hscconfig[key] for key in sorted(hscconfig.keys())
               if key.startswith('filter')]
    tract = hscconfig['tract']

    for f in filters:
        # make a butler
        butler = Butler(hscdir)
        data_all = os.listdir(f"{hscdir}/deepCoadd-results/{f}"
                              f"/{tract}/")
        n1 = len(data_all)
        for i in range(n1):
            p_num = data_all[i]
            data_id = {'tract': tract, 'patch': p_num, 'filter': f}

        # load the catalog from the butler
        sources = butler.get("deepCoadd_forced_src", data_id)  # load catalog
        meas = butler.get("deepCoadd_meas", data_id)  # load catalog
        # n = len(sources)  # count the number of catalog
        # get the psf flux and schema
        fluxpsf = sources.getPsfInstFlux()  # get psfflux
        # schema_s = sources.getSchema()  # get schema of sources
        # schema_m = meas.getSchema()  # get schema of meas
        # get specific column of sources and meas schema
        # schema_m.find().key
        # .find() is searching for strings (getting column). .key is
        # getting key of column (getting value of column).

        # keys_s, keys_m = {}, {}
        # cols_s = ['deblend_nChild', 'base_ClassificationExtendedness_value',
        #           'base_SdssCentroid_flag', 'base_PixelFlags_flag_edge',
        #           'base_PixelFlags_flag_saturatedCenter',
        #           'base_PixelFlags_flag_bad',
        #           'modelfit_CModel_flag', 'base_PixelFlags_flag_offimage']
        # cols_m = ['detect_isPatchInner', 'detect_isTractInner',
        #           'base_PixelFlags_flag_edge', 'merge_peak_g',
        #           'merge_peak_r', 'merge_peak_i', 'merge_peak_z',
        #           'merge_peak_y', 'merge_peak_N921', 'merge_footprint_sky',
        #           'base_PixelFlags_flag_offimage', 'detect_isPrimary']

        # for col in cols_s:
        #     keys_s[col] = schema_s.find(col).key
        # for col in cols_m:
        #     keys_m[col] = schema_m.find(col).key

        # TODO: I REALLY hope we don't have to for loop this
        # for i in range(n):
        s = sources  # [i]
        m = meas  # [i]
        ra = s.get('coord_ra')
        dec = s.get('coord_dec')
        flux = s.get('base_PsfFlux_instFlux')
        flux_err = s.get('base_PsfFlux_instFluxErr')
        flag = m.get('base_PixelFlags_flag_fakeCenter')
        mask = fluxpsf[i] > 0
        # TODO: Should we use the other flags below as well?
        # TODO: Probably implement Pucha et al. extendedness for masking
        # if we end up using this
        # and s.get(key_extend)== 0 :#and m.get(key_primary) == True :
        # and m.get(key_flag_edge) == True
        # and s.get(key_flag_sat) == True
        # and m.get(key_offimage) == True :
        # TODO: Check if flux and fluxpsf are different
        mag = -2.5 * np.log10(fluxpsf[mask]) + zp
        # TODO: If they're not, fix the flux (not fluxpsf) usage in errors
        mag_err = np.abs(-2.5/(np.log(10.) * flux[mask]) * flux_err[mask])
        data = {'id': s.getId(),
                'ra': ra.asDegrees(),
                'dec': dec.asDegrees(),
                'mag': mag,
                'mag_err': mag_err,
                'flag': flag
                }

        # Save to a file
        df = pd.DataFrame(data)
        df.to_csv(outputdir + f"output_{f}_{args['magstring']}.output.csv",
                  index=False)


def parse_args():
    parser = argparse.ArgumentParser(
             description='Use outputCatalog.py to create '
                         'the hscPipe output catalog of the '
                         'artificial star test run.\n'
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
