import configparser
import re
 
def read_config(section):
   config = configparser.ConfigParser()
   # config.read('./test_config.ini')
   config.read('./config.txt')
   return config[section]

def make_config(loc):
   config = configparser.ConfigParser()
   config['hscPipe'] = {'tract': 0, 
                           'rerun': '/absolute/path/to/rerun/',
                           'cores': 8,
                           'mag_start': 24,
                           'mag_end': 25,
                           'mag_step': 0.5,
                           'filter1': 'HSC-G'
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
   file = open(loc+'artest_config.py', 'w')

   file.write('config.doDetection=True\n')
   file.write('config.measureCoaddSources.measurement.plugins[\'base_PixelFlags\'].masksFpAnywhere=[\'CLIPPED\', \'SENSOR_EDGE\', \'INEXACT_PSF\', \'BRIGHT_ OBJECT\', \'FAKE\']\n')
   file.write('config.measureCoaddSources.measurement.plugins[\'base_PixelFlags\'].masksFpCenter=[\'CLIPPED\', \'SENSOR_EDGE\', \'INEXACT_PSF\', \'BRIGHT_ OBJECT\', \'FAKE\']\n') 
   file.write('config.forcedPhotCoadd.measurement.plugins[\'base_PixelFlags\'].masksFpAnywhere=[\'CLIPPED\', \'SENSOR_EDGE\', \'REJECTED\', \'INEXACT_PSF\', \'BRIGHT_OBJECT\', \'FAKE\']\n') 
   file.write('config.forcedPhotCoadd.measurement.plugins[\'base_PixelFlags\'].masksFpCenter=[\'CLIPPED\', \'SENSOR_EDGE\', \'REJECTED\', \'INEXACT_PSF\', \'BRIGHT_OBJECT\', \'FAKE\']\n')
   
   file.close()


def join_filter(config):
   # Join filter values with '^' separator
   filter_string = '^'.join([config[key] for key in sorted(config.keys()) if key.startswith('filter')])

   return filter_string