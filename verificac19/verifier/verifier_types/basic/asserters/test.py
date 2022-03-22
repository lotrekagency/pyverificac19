from verificac19.verifier.asserters import BaseAsserter
from verificac19.verifier.decorators import AsserterCheck
from verificac19.verifier.common.result import NOT_EU_DCC, Result
from verificac19.verifier.common.info import (
    TEST_DETECTED,
    TEST_MOLECULAR,
    TEST_RAPID,
    GENERIC_TYPE,
    Codes
)
from verificac19.service import _service as service
from verificac19.verifier.verifier_types.utils.time import DateTimeValidator, Timing
from verificac19.verifier.asserters import TestBaseAsserter

class TestAsserter(TestBaseAsserter):


    @AsserterCheck()
    def check_for_rapid(self):
        if not self._is_test_rapid():
            return
