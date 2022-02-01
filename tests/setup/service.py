import pook
from tests.service.utils import open_json
from verificac19 import service
from verificac19.service._settings import (
    DSC_URL,
    STATUS_URL,
    SETTINGS_URL,
    CHECK_CRL_URL,
    DOWNLOAD_CRL_URL,
)


def _setup_mock_for_settings():
    settings_data = open_json("settings.json")
    pook.get(SETTINGS_URL, reply=200, response_json=settings_data)


def _setup_mock_for_dsc_certificates():
    FINISHED = "finished"
    pook.get(STATUS_URL, reply=200, response_json=open_json("dsc_whitelist.json"))
    dsc_validation: list = open_json("dsc_validation.json")
    dsc_validation.append(FINISHED)
    for index, dsc in enumerate(dsc_validation):
        kwargs = {}
        headers = {"content-type": "text/plain"}
        kwargs["reply"] = 200
        if 0 < index:
            headers["X-RESUME-TOKEN"] = str(index)
        kwargs["headers"] = headers
        if dsc == FINISHED:
            kwargs["reply"] = 204
            pook.get(DSC_URL, **kwargs)
            continue

        kwargs["response_body"] = dsc["raw_data"]
        kwargs["response_headers"] = {
            "X-KID": dsc["kid"],
            "X-RESUME-TOKEN": str(index + 1),
        }
        pook.get(DSC_URL, **kwargs)


def _setup_mock_for_crl():
    pook.get(CHECK_CRL_URL, reply=200, response_json=open_json("CRL-check-v1.json"))
    pook.get(
        f"{DOWNLOAD_CRL_URL}?chunk=1",
        reply=200,
        response_json=open_json("CRL-v1-c1.json"),
    )
    pook.get(
        f"{DOWNLOAD_CRL_URL}?chunk=2",
        reply=200,
        response_json=open_json("CRL-v1-c2.json"),
    )


def run_setup():
    _setup_mock_for_settings()
    _setup_mock_for_dsc_certificates()
    _setup_mock_for_crl()
    service.clear_all_cache()
    service.update_all()
