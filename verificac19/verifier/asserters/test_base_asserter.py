from verificac19.verifier.common.result import NOT_EU_DCC, Result
from datetime import timedelta, datetime
from .base_asserter import BaseAsserter
from verificac19.service import _service as service
from verificac19.verifier.verifier_types.utils.time import DateTimeValidator, Timing
from verificac19.verifier.decorators import AsserterCheck

from verificac19.verifier.common.info import (
    TEST_DETECTED,
    TEST_MOLECULAR,
    TEST_RAPID,
    GENERIC_TYPE,
    Codes
)

class TestBaseAsserter(BaseAsserter):

    def _get_molecular_hours(self):
        settings = self._get_many_delta_hours_settings("molecular_test_start_hours", "molecular_test_end_hours")
        return settings

    def _get_molecular_test_date(self) -> Timing:
        test_datetime = datetime.strptime(self.last_test["sc"], "%Y-%m-%dT%H:%M:%S%z")
        start, end = self._get_molecular_hours()
        time_validator = DateTimeValidator(test_datetime, start, end)
        return time_validator.check()

    def _is_test_rapid(self):
        return self.last_test["tt"] == TEST_RAPID

    def _is_test_molecular(self):
        return self.last_test["tt"] == TEST_MOLECULAR


    @AsserterCheck()
    def check_content(self):
        content_length = len(self.payload["t"])
        if content_length == 0:
            return NOT_EU_DCC

        self.last_test = self.payload["t"][-1]

    @AsserterCheck()
    def check_detected(self):
        if self.last_test["tr"] == TEST_DETECTED:
            return Result(
                Codes.NOT_VALID.value,
                False,
                "Test Result is DETECTED",
            )
