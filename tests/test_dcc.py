import pytest

from verificac19 import sum
from verificac19.exceptions import VerificaC19Error


def test_sum():
    assert sum(1, 2) == 3
    assert sum(5, 5) == 10


def test_wrong_sum():
    with pytest.raises(VerificaC19Error):
        sum(-1, 2)
