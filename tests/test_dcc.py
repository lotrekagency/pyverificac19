import os
import pytest

from dcc_utils import from_image

from verificac19 import sum
from verificac19.exceptions import VerificaC19Error


def test_sum():
    assert sum(1, 2) == 3
    assert sum(5, 5) == 10


def test_wrong_sum():
    with pytest.raises(VerificaC19Error):
        sum(-1, 2)


def test_dcc_utils():
    dcc = from_image(os.path.join("tests", "data", "2.png"))
    assert dcc.payload["nam"]["fn"] == "Sčasný"
