import configparser
from io import StringIO
from unittest.mock import patch, MagicMock
import pytest
from injectStar.utils import bash_actions


@pytest.fixture(scope="function", name="file_object")
def fixture_file_object():
    return StringIO()


@pytest.fixture(scope="function", name="config")
def fixture_config():
    configdict = configparser.ConfigParser()
    configdict.read('./tests/config_default.txt')
    return configdict


# shebang
def test_shebang_default(file_object):
    bash_actions.shebang(file_object)
    file_object.seek(0)
    assert file_object.readline() == '#!/bin/bash\n'


def test_shebang_no_write():
    non_writable_file = MagicMock()
    non_writable_file.write.side_effect = AttributeError("Not writable")
    with pytest.raises(AttributeError):
        bash_actions.shebang(non_writable_file)


# sbatch
def test_sbatch_default(file_object, config):
    bash_actions.sbatch(config, file_object, 24.5)
    file_object.seek(0)
    lines = file_object.readlines()
    assert lines[0].strip() == '#SBATCH -p all'
    assert lines[1].strip() == '#SBATCH --ntasks=1'
    assert lines[2].strip() == '#SBATCH --cpus-per-task=8'
    assert lines[3].strip() == '#SBATCH --job-name=m31_artest_24.5'
    assert lines[4].strip() == '#SBATCH --time=240:00:00'
    assert lines[5].strip() == '#SBATCH --mem=200G'
    assert lines[6].strip() == '#SBATCH --mail-type=END'
    assert lines[7].strip() == '#SBATCH --mail-user=your.email@email.com'


def test_sbatch_no_mail(file_object, config):
    config.remove_option('slurm', 'mail-type')
    config.remove_option('slurm', 'mail-user')
    bash_actions.sbatch(config, file_object, 24)
    file_object.seek(0)
    lines = file_object.readlines()
    assert '#SBATCH --mail-type=' not in lines
    assert '#SBATCH --mail-user=' not in lines


# hsc_init
def test_hsc_init(file_object, config):
    setuphsc = 'setup-hscpipe'
    bash_actions.hsc_init(config, setuphsc, file_object)
    file_object.seek(0)
    lines = file_object.readlines()
    assert lines[0].strip() == ''
    assert lines[1].strip() == 'setup-hscpipe'
    assert lines[2].strip() == 'export OMP_NUM_THREADS=1'
    assert lines[3].strip() == "export HSC='/absolute/path/to/HSC'"
    assert lines[4].strip() == "export origrerun='/absolute/path/" \
                               "to/HSC/rerun/m31'"
    assert lines[5].strip() == "export rerun='/absolute/path/" \
                               "to/HSC/rerun/artest'"


# detect_coadd
def test_detect_coadd(file_object, config):
    bash_actions.detect_coadd(config, file_object, "filter1")
    file_object.seek(0)
    # lines = file_object.readlines()
    assert file_object.readline() == "detectCoaddSources.py " \
        "$HSC --calib $HSC/CALIB "\
        "--rerun $rerun --id filter=HSC-G tract=0 --clobber-config " \
        "--clobber-versions\n"
