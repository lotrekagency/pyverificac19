from datetime import datetime, timedelta
from enum import Enum

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
        if self.now < self.start_time:
            return Timing.TOO_EARLY
        elif self.now > self.end_time:
            return Timing.TOO_LATE

        return Timing.VALID
