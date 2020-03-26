import os
import pathlib

import pytest

from . import new_nda
from . import old_nda
from . import neware


old_nda_file = pathlib.Path("testdata") / "test.nda"


def test_nothing():
    print("If this fails, then there is something seriously wrong")
    pass


@pytest.mark.xfail
def test_fail():
    assert 1 == 2
