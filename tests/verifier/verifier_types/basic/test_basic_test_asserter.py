from datetime import datetime
from verificac19.verifier.common.info import Codes
from tests.utils.dcc import get_dcc_from_image
from verificac19.verifier.verifier_types.basic.asserters.test import TestAsserter
import time_machine
import logging

def test_too_late(caplog):
    caplog.set_level(logging.DEBUG)
    dcc = get_dcc_from_image("TEST.png")
    asserter = TestAsserter(dcc)
    result = asserter.run_checks()
    assert result.payload["code"] == Codes.NOT_VALID.value
    assert result.payload["message"] == "Test Result is expired at : 2021-08-20 10:06:03+0000"

def test_valid(caplog):
    caplog.set_level(logging.DEBUG)
    dcc = get_dcc_from_image("TEST.png")
    with time_machine.travel(datetime(2021, 8, 19)):
        asserter = TestAsserter(dcc)
        result = asserter.run_checks()
        assert result.payload["code"] == Codes.VALID.value

def test_too_early(caplog):
    caplog.set_level(logging.DEBUG)
    dcc = get_dcc_from_image("TEST.png")
    with time_machine.travel(datetime(2021, 8, 17)):
        asserter = TestAsserter(dcc)
        result = asserter.run_checks()
        assert result.payload["code"] == Codes.NOT_VALID_YET.value
