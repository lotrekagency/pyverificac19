import verificac19
from requests import get


def http_get(*args, **kwargs):
    headers = kwargs.pop("headers", {})
    headers["User-Agent"] = f"verificac19-sdk-python/{verificac19.__version__}"
    return get(*args, headers=headers, **kwargs)
