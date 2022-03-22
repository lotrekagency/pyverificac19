from typing import Tuple
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
        return self._get_many_delta_hours_settings("molecular_test_start_hours", "molecular_test_end_hours")

    def _get_rapid_hours(self):
        return self._get_many_delta_hours_settings("rapid_test_start_hours", "rapid_test_end_hours")

    def _get_test_date(self) -> datetime:
        test_datetime = datetime.strptime(self.last_test["sc"], "%Y-%m-%dT%H:%M:%S%z")
        return test_datetime

    def _is_test_rapid(self):
        return self.last_test["tt"] == TEST_RAPID

    def _is_test_molecular(self):
        return self.last_test["tt"] == TEST_MOLECULAR

    def _get_molecular_time_validator(self) -> DateTimeValidator:
        test_datetime = self._get_test_date()
        start, end = self._get_molecular_hours()
        time_validator = DateTimeValidator(test_datetime, start, end)
        return time_validator

    def _get_rapid_time_validator(self) -> DateTimeValidator:
        test_datetime = self._get_test_date()
        start, end = self._get_rapid_hours()
        time_validator = DateTimeValidator(test_datetime, start, end)
        return time_validator

    def _simple_timing_check(self):
        if self._is_test_rapid():
            tv = self._get_rapid_time_validator()
        else:
            tv = self._get_molecular_time_validator()

        timing = tv.check()
        if timing is Timing.TOO_EARLY:
            return Result(
                Codes.NOT_VALID_YET.value,
                False,
                f'Test Result is not valid yet, starts at : {tv.start_time_string}',
            )

        elif timing is Timing.TOO_LATE:
            return Result(
                Codes.NOT_VALID.value,
                False,
                f'Test Result is expired at : {tv.end_time_string}',
            )

        return Result(
            Codes.VALID.value,
            True,
            f'Test Result is valid [{tv.start_time_string} - {tv.end_date_string}]'
        )


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
