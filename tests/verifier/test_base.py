from datetime import timedelta
import os
import re
import time_machine

from verificac19.verifier.verifier_types.base import BaseVerifier
from verificac19.verifier.verifier_types.vaccination.base import BaseVaccination
from verificac19.verifier.asserters import BaseAsserter, TestBaseAsserter
from dcc_utils.dcc import from_image


def get_dcc_from_image(image_name:str):
    image = os.path.join("tests", "data", "eu_test_certificates", image_name)
    dcc = from_image(image)
    return dcc



def test_base_asserter_time_utils():
    dcc = get_dcc_from_image("TEST.png")
    asserter = BaseAsserter(dcc)
    assert 0 == asserter._get_integer_setting("molecular_test_start_hours")
    assert 72 == asserter._get_integer_setting("molecular_test_end_hours")
    assert (timedelta(hours=0), timedelta(hours=72)) == asserter._get_many_delta_hours_settings("molecular_test_start_hours", "molecular_test_end_hours")
