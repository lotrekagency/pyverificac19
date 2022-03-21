import os
import re
import time_machine
import datetime as dt

from verificac19.verifier.verifier_types.base import BaseVerifier
from verificac19.verifier.verifier_types.vaccination.base import BaseVaccination
from dcc_utils.dcc import from_image


def test_base_vaccination():
    image = os.path.join("tests", "data", "eu_test_certificates", "SK_1.png")
    dcc = from_image(image)
    v = BaseVaccination(dcc)
    result = v.verify()
    assert result is None

