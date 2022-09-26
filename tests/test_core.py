import os
import pathlib
import tempfile
import shutil

import pytest

from neware_reader import new_nda
from neware_reader import old_nda
from neware_reader import neware


DATA_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'testdata',
    )

old_nda_file = pathlib.Path(DATA_DIR) / "old_nda_file.nda"
new_nda_file = pathlib.Path(DATA_DIR) / "new_nda_file.nda"
out_file = pathlib.Path(DATA_DIR) / "out.csv"


@pytest.fixture()
def clean_dir():
    new_path = tempfile.mkdtemp()
    return new_path


def test_example_files_exist():
    assert old_nda_file.is_file()
    assert new_nda_file.is_file()


def test_nothing():
    print("If this fails, then there is something seriously wrong")
    pass


def test_new_file_to_csv():
    df = neware.read_nda(new_nda_file)
    assert "step_ID" in df.columns


def test_nda_to_csv(clean_dir):
    #  copy file to a temporary path
    tmp_new_nda_file = pathlib.Path(clean_dir) / new_nda_file.name
    shutil.copy(new_nda_file, tmp_new_nda_file)

    # TODO: should allow pathlib.Path objects (currently only works for strings)
    neware.nda_to_csv(
        str(tmp_new_nda_file), outpath=':auto:', testcols=False, split=False
    )


# TODO: create tests for all allowed argument options


def test_old_file_to_csv():
    df = neware.read_nda(old_nda_file)
    assert "step_ID" in df.columns


@pytest.mark.xfail
def test_fail():
    assert 1 == 2
