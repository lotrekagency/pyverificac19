import pathlib
import os
import json
from typing import Any, Callable, Tuple
from datetime import datetime, timedelta

VALID_CACHE_PERIOD = timedelta(days=1)

CACHE_DATA_DIRECTORY = os.environ.get(
    "VC19_CACHE_FOLDER",
    os.path.join(str(pathlib.Path(__file__).parent.resolve()), "cache_data"),
)
if not os.path.exists(CACHE_DATA_DIRECTORY):
    os.makedirs(CACHE_DATA_DIRECTORY, 0o777, True)


def dump_to_cache(file_name: str, data: Any) -> None:
    """Stores data in cached file along with current time.

    The current time is needed when loading the file
    to check whether the data is too old and needs to
    be refetched.
    """

    file_path = os.path.join(CACHE_DATA_DIRECTORY, file_name)

    currect_time = datetime.now().isoformat()
    data_with_date = {"data": data, "time": currect_time}
    with open(file_path, "w") as output:
        json.dump(data_with_date, output, indent=2)


def fetch_with_smart_cache(
    file_name: str, fetch_from_source: Callable, force_cache=False
) -> Any:
    """Uses cache if possible otherwiser returns callback.

    If the file exists and the date registered is not older than the maximum
    valid cache period, the data is loaded from the  cached file.
    Otherwise, the result of the `fetch_from_source` callable will be returned.
    """
    file_path = os.path.join(CACHE_DATA_DIRECTORY, file_name)

    if not os.path.exists(file_path):
        return fetch_from_source()

    data, creation_date = _load_cached_file(file_path)

    if force_cache:
        return data

    if _is_date_valid(creation_date):
        return data

    return fetch_from_source()


def _load_cached_file(file_path: str) -> Tuple[dict, datetime]:
    with open(file_path, "r") as input:
        data_with_date = json.load(input)

    data = data_with_date["data"]

    data_creation_isotime: str = data_with_date["time"]
    data_creation_datetime = datetime.fromisoformat(data_creation_isotime)
    return data, data_creation_datetime


def _is_date_valid(date: datetime) -> bool:
    current_time = datetime.now()
    data_age = current_time - date

    return data_age < VALID_CACHE_PERIOD
