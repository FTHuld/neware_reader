import os
import pathlib

import pytest

import new_nda
import old_nda
import neware


old_nda_file = pathlib.Path("testdata") / "test.nda"


def test_nothing():
    print("If this fails, then there is something seriously wrong")
    pass


@pytest.mark.xfail
def test_fail():
    assert 1 == 2
