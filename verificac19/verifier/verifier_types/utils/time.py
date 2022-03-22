from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class Timing(Enum):
    TOO_EARLY = -1
    VALID = 0
    TOO_LATE = 1


class DateTimeValidator:

    def __init__(self, reference_date: datetime, after: timedelta, before: timedelta) -> None:
        self.start_time = reference_date + after
        self.end_time = reference_date + before
        self.now = datetime.now(reference_date.tzinfo)

    def check(self) -> Timing:
        logger.debug(f"Checking between {self.start_time} and {self.end_time}. Now is {self.now}")
        if self.now < self.start_time:
            return Timing.TOO_EARLY
        elif self.now > self.end_time:
            return Timing.TOO_LATE

        return Timing.VALID

    @property
    def start_time_string(self) -> str:
        return self.start_time.strftime("%Y-%m-%d %H:%M:%S%z")

    @property
    def start_date_string(self) -> str:
        return self.start_time.strftime("%Y-%m-%d")


    @property
    def end_time_string(self) -> str:
        return self.end_time.strftime("%Y-%m-%d %H:%M:%S%z")

    @property
    def end_date_string(self) -> str:
        return self.end_time.strftime("%Y-%m-%d")
