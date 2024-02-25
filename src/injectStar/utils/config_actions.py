import configparser
import re
 
def read_config(section):
   '''
    Reads the specified section from the configuration file 'config.txt'.

    Parameters:
    - section: A string representing the section name in the configuration file.

    Returns:
    A dictionary containing the configuration options from the specified section.
    '''
   config = configparser.ConfigParser()
   config.read('./config.txt')
   return config[section]

def make_config(loc):
   '''
    Creates a configuration file 'config.txt' with predefined settings and writes it to the specified location.

    Parameters:
    - loc: A string representing the directory path where the configuration file will be saved.

    Returns:
    None
    '''
   config = configparser.ConfigParser()
   config['hscPipe'] = {'tract': 0, 
                           'rerun': '/absolute/path/to/HSC/rerun/m31/',
                           'cores': 8,
                           'mag_start': 24,
                           'mag_end': 25,
                           'mag_step': 0.5,
                           'filter1': 'HSC-G',
                           'filter2': 'HSC-I2'
                           }
   config['slurm'] = {'ntasks': 1,
                      'time': '240:00:00',
                      'memory': '200G',
                      'mail-type': 'END',
                      'mail-user': 'jon.doe@email.com'
                     }
   
   # TODO: Edit this once the required features are agreed upon.
   # config['other'] = {'delete_job': False,
   #                    'create_catalogue': True,
   #                    'crossmatch_catalogue': True
   #                   }
   
   with open(loc+'config.txt', 'w') as configfile:
      config.write(configfile)

def make_configMulti(loc):
   '''
    Creates a configuration file 'artest_config.py' with predefined settings used to run multiBandDriver.py and writes it to the specified location.

    Parameters:
    - loc: A string representing the directory path where the configuration file will be saved.

    Returns:
    None
    '''
   file = open(loc+'artest_config.py', 'w')

   file.write('config.doDetection=True\n')
   file.write('config.measureCoaddSources.measurement.plugins[\'base_PixelFlags\'].masksFpAnywhere=[\'CLIPPED\', \'SENSOR_EDGE\', \'INEXACT_PSF\', \'BRIGHT_ OBJECT\', \'FAKE\']\n')
   file.write('config.measureCoaddSources.measurement.plugins[\'base_PixelFlags\'].masksFpCenter=[\'CLIPPED\', \'SENSOR_EDGE\', \'INEXACT_PSF\', \'BRIGHT_ OBJECT\', \'FAKE\']\n') 
   file.write('config.forcedPhotCoadd.measurement.plugins[\'base_PixelFlags\'].masksFpAnywhere=[\'CLIPPED\', \'SENSOR_EDGE\', \'REJECTED\', \'INEXACT_PSF\', \'BRIGHT_OBJECT\', \'FAKE\']\n') 
   file.write('config.forcedPhotCoadd.measurement.plugins[\'base_PixelFlags\'].masksFpCenter=[\'CLIPPED\', \'SENSOR_EDGE\', \'REJECTED\', \'INEXACT_PSF\', \'BRIGHT_OBJECT\', \'FAKE\']\n')
   
   file.close()