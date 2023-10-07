# ArtificialStarTest_for_hscPipe (under construction)
This repositry describes a method for calculating a detection completeness using artificial stars in hscPipe 6 and beyond.
The latest version of `injectStar.py` is version 4.

## Flow of obtaining detection completeness
0. As with other hscPipe commands, run `setup-hscpipe` or `setup hscPipe 8.4`.
   
1. Copy `rerun` containing the image (e.g., `~/<rerun>/deepCoadd/<filter>/4,4.fits`) in which you want to inject the artificial star.
  - Since `injectStar.py` embeds artificial stars directly into the image, it is necessary to make a backup of original images.
  - Also, a copy of rerun must be executed every time the artificial star test is performed.
  - This is because artificial stars are embedded again in the image in which artificial stars are embedded.
 
2. Run `injectStar.py` to embed artificial stars in the coadd-image (e.g., `~/<rerun>/deepCoadd/<filter>/4.4.fits`).
  - `injectStar.py` is to embed the artificial stars of any magnitude in `~/<rerun>/deepCoadd/<filter>/<tract>/<patch>/<patch>.fits`.
  - Run `injectStar.py` as follows
    `python3 injectStar.py <path-to-rerun> <filter> <tract> <magnitude of artificial stars to be embedded>`
    - `<rerun>` must be the full path.
    - `<filter>` should be the same as hscPipe, such as `HSC-G`, `HSC-R2`, `HSC-I2`, `NB0515`.
    - When you finish executing `injectStar.py`, artificial stars are embedded in the image.
    - The catalog of artificial stars you input in each patch is constructed as `~/<rerun>/deepCoadd/<filter>/<tract>/<patch>/<patch>.fits.txt`.

3. Run `detectCoaddSources.py` to perform the detection of images with embedded artificial stars.
  - Run `detectCoaddSources.py` as follows
    > `detectCoaddSources.py ~HSC --calib ~/HSC/CALIB --rerun <rerun> --id filter=<filter> tract=<tract> --clobber-config --clobber-versions`
   
4. Run `multiBandDriver.py` to perform the photometry of images with embedded artificial stars.
  - `multiBandDriver.py` is executed as follows:
    > `multiBandDriver.py ~/HSC --calib ~/HSC/CALIB --rerun <rerun> --id filter=<filter> tract=<tract> --configfile config.py --clobber-config -- clobber-versions`
    - Be sure to describe all `<filter>` being analyzed.
    - You can specify multiple `<tract>`.
    - `config.py` should be written as follows.
      > config.doDetection=True
      > config.measureCoaddSources.measurement.plugins['base_PixelFlags'].masksFpAnywhere=['CLIPPED', 'SENSOR_EDGE', 'INEXACT_PSF', 'BRIGHT_ OBJECT', 'FAKE']]
      > config.measureCoaddSources.measurement.plugins['base_PixelFlags'].masksFpCenter=['CLIPPED', 'SENSOR_EDGE', 'INEXACT_PSF', 'BRIGHT_ OBJECT', 'FAKE']]
      > config.forcedPhotCoadd.measurement.plugins['base_PixelFlags'].masksFpAnywhere=['CLIPPED', 'SENSOR_EDGE', 'REJECTED', 'INEXACT_PSF', ' BRIGHT_OBJECT', 'FAKE']]
      > config.forcedPhotCoadd.measurement.plugins['base_PixelFlags'].masksFpCenter=['CLIPPED', 'SENSOR_EDGE', 'REJECTED', 'INEXACT_PSF', ' BRIGHT_OBJECT', 'FAKE']]

5. Create a catalog of output data.
  - The catalog should be created for objects with 'extendedness==0' and 'flux>0'.
  - In science catalogs, flags such as 'detect_isPrimary', 'base_PixelFlags_flag_edge', and 'base_PixelFlags_flag_offimage' must be set to 'True', but 'injectStar.py' does not handle these flags. (Actually, it is necessary to do so). Therefore, do not use these flags.
  - When building the catalog, also include `tract` information. This is necessary for cross-matching input and output data. This process is not a problem when creating a catalog for each tract, individually.
  - The flag for artificial stars ("FAKE" flag) corresponds `to base_PixelFlags_flag_fake` and `base_PixelFlags_flag_fakeCenter`.
    - `base_PixelFlags_flag_fake`: Flag set to `True` if the footprint of the object is near the pixel that sets the "FAKE" flag.
    - `base_PixelFlags_flag_fakeCenter`: Flag set to `True` if the center of the object is near the pixel that sets the "FAKE" flag.
    - Currently, it is recommended to use `base_PixelFlags_flag_fakeCenter`.
 
6. Create a catalog for input data.
  - After running `injectStar.py`, a file named `<patch>.fits.txt` will be created under `~/<rerun>/deepCoadd/<filter>/<tract>/`. This is the catalog of artificial stars embedded in a patch of tract.
  - These catalogs of input data (for each tract) are combined into one catalog, as follows:
    > `cat ~/<rerun>/deepCoadd/<filter>/<tract>/*.fits.txt > tract.txt`

7. Cross-match input data and output data.
  - Cross-match the input and output data based on the magnitude and coordinate information, and check whether the input artificial star was detected or not. At this time, the tract information should also be added to the cross-match.
  - In `injectStar.py`, the artificial star is embedded in the overlapping part of the tract, so if the tract information is not added to the cross-match, there is a possibility that a missed cross-match will occur in the crowding region of the tract.
  - Coordinate information is acceptable up to a limit of about 0.5 arcsec.
  - Magnitude information is acceptable up to a limit of about 0.5 mag.
    -  Currently, it is confirmed that there is an offset of about 0.2 - 0.3 mag between input magnitude and output magnitude (most likely due to the difference between `coaddDriver.py` (with sky correction/subtraction) and `detectCoaddSource.py` (without sky correction/subtraction)).

8. Repeat steps 1 ~ 7 for each magnitude you want to examine.
