# ArtificialStarTest_for_hscPipe
This repositry describes a method for calculating a detection completeness using artificial stars in hscPipe 6 and beyond.

## Flow of obtaining detection completeness
1. Copy `rerun` containing the image in which you want to embed the artificial star.
  - Since `injectStar.py` embeds the artificial star directly into the image, it is necessary to make a backup of the original.
  - Also, the copy of rerun must be executed every time the artificial star test is performed.
  - This is because the artificial star is embedded again in the image in which the artificial star is embedded.
 
2. Run `injectStar.py` to embed the artificial star in the coadd-image (`calexp~.fits`).
  - `injectStar.py` is to embed an artificial star of any magnitude in `~/<rerun>/deepCoadd-results/<filter>/<tract>/<patch>/calexp-<filter>-<tract>-<patch>.fits`.
  - Run `injectStar.py` as follows
    `python3 injectStar.py <rerun> <filter> <tract> <magnitude of artificial star to be embedded>`
    - `<rerun>` must be full path.
    - `<filter>` should be the same as hscPipe, such as `HSC-G`, `HSC-R`, `HSC-I2`, `NB0515`.
    - When you finish executing `injectStar.py`, the artificial star is embedded in the image.
    - The catalog of each patch of artificial stars you input is constructed as `~/<rerun>/deepCoadd-results/<filter>/<tract>/<patch>/calexp-<filter>-<tract>-<patch>.fits.txt`.

3. Run `multiBandDriver.py` to perform the detection and photometry of images with embedded artificial stars.
  - `multiBandDriver.py` is executed as follows:
    > `multiBandDriver.py ~/HSC --calib ~/HSC/CALIB --rerun <rerun> --id filter=<filter> tract=<tract> --configfile config.py --clobber-config -- clobber-versions`
    - Be sure to describe all `<filter>` being analyzed.
    - You can specify multiple `<tract>`s.
    - `config.py` should be as follows.
      > config.doDetection=True
      > config.measureCoaddSources.measurement.plugins['base_PixelFlags'].masksFpAnywhere=['CLIPPED', 'SENSOR_EDGE', 'INEXACT_PSF', 'BRIGHT_ OBJECT', 'FAKE']]
      > config.measureCoaddSources.measurement.plugins['base_PixelFlags'].masksFpCenter=['CLIPPED', 'SENSOR_EDGE', 'INEXACT_PSF', 'BRIGHT_ OBJECT', 'FAKE']]
      > config.forcedPhotCoadd.measurement.plugins['base_PixelFlags'].masksFpAnywhere=['CLIPPED', 'SENSOR_EDGE', 'REJECTED', 'INEXACT_PSF', ' BRIGHT_OBJECT', 'FAKE']]
      > config.forcedPhotCoadd.measurement.plugins['base_PixelFlags'].masksFpCenter=['CLIPPED', 'SENSOR_EDGE', 'REJECTED', 'INEXACT_PSF', ' BRIGHT_OBJECT', 'FAKE']]

4. Create a catalog of output data.
  - The catalog should be created for objects with 'extendedness==0' and 'flux>0'.
  - In science catalogs, flags such as 'detect_isPrimary', 'base_PixelFlags_flag_edge', and 'base_PixelFlags_flag_offimage' must be set to 'True', but 'injectStar.py' does not handle these flags. (Actually, it is necessary to do so). Therefore, do not use these flags.
  - When building the catalog, also include `tract` information. This is necessary for cross-matching input data and output data. This process is not a problem when creating a catalog for each tract, individually.
 
5. Create a catalog for input data.
  - After running `injectStar.py`, a file named `calexp~.fits.txt1 will be created under `~/<rerun>/deepCoadd-results/<filter>/<tract>/<patch>`. This is the catalog of artificial stars embedded in a patch of a tract.
  - These catalogs of input data (for each tract) are combined into one catalog, as follows:
    > `cat ~/<rerun>/deepCoadd/<filter>/<tract>/*.fits.txt > tract.txt`

6. Cross-match input data and output data.
  - Cross-match the input and output data based on the magnitude and coordinate information, and check whether the input artificial star was detected or not. At this time, the tract information should also be added to the cross-match.
  - In `injectStar.py`, the artificial star is buried in the overlapping part of the tract, so if the tract information is not added to the cross-match, there is a possibility that a missed cross-match will occur in the crowding region of the tract.
  - Coordinate information is acceptable up to a limit of about 0.5 arcsec.

7. Repeat steps 1 ~ 6 for each magnitude you want to examine.
