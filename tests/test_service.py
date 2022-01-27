import os
from verificac19 import service
import pook
import json
from verificac19.service._settings import (
    DSC_URL,
    STATUS_URL,
    SETTINGS_URL,
    CHECK_CRL_URL,
    DOWNLOAD_CRL_URL,
)

class TestService:

    def open_json(self, name: str) -> dict:
        path = os.path.join("tests", "data", "mock_request", name)
        with open(path, "r") as file:
            return json.load(file)

    def setup_mock_for_settings(self):
        settings_data = self.open_json("settings.json")
        pook.get(SETTINGS_URL, reply=200, response_json=settings_data)

    def setup_mock_for_dsc_certificates(self):
        FINISHED = 'finished'
        pook.get(STATUS_URL, reply=200, response_json=self.open_json("dsc_whitelist.json"))
        dsc_validation: list = self.open_json("dsc_validation.json")
        dsc_validation.append(FINISHED)
        for index, dsc in enumerate(dsc_validation):
            kwargs = {}
            headers = {"content-type": "text/plain"}
            kwargs['reply'] = 200
            if 0 < index:
                headers["X-RESUME-TOKEN"] = str(index)
            kwargs['headers'] = headers
            if dsc == FINISHED:
                kwargs['reply'] = 204
                pook.get(DSC_URL, **kwargs)
                continue

            kwargs['response_body'] = dsc["raw_data"]
            kwargs['response_headers'] = {
                "X-KID": dsc["kid"],
                "X-RESUME-TOKEN": str(index + 1),
            }
            pook.get(DSC_URL, **kwargs)

    def setup_mock_for_crl(self):
        pook.get(CHECK_CRL_URL, reply=200, response_json=self.open_json("CRL-check-v1.json"))
        pook.get(
            f"{DOWNLOAD_CRL_URL}?chunk=1",
            reply=200,
            response_json=self.open_json("CRL-v1-c1.json"),
        )
        pook.get(
            f"{DOWNLOAD_CRL_URL}?chunk=2",
            reply=200,
            response_json=self.open_json("CRL-v1-c2.json"),
        )

    @pook.on
    def test_setup(self):
        self.setup_mock_for_settings()
        self.setup_mock_for_dsc_certificates()
        self.setup_mock_for_crl()
        service.clear_all_cache()
        service.update_all()

    @pook.on
    def test_dsc_settings(self):
        settings_data = self.open_json("settings.json")
        for setting in settings_data:
            st_name = setting['name']
            st_type = setting['type']
            assert service.get_setting(st_name, st_type) == setting

    @pook.on
    def test_dsc_certificates(self):
        not_whitelisted_dsc = ["nJkLGpmXT68=", "b32660V8q5A=", "gBG2e8Vypv0="]
        dsc_list = self.open_json("dsc_validation.json")
        for dsc in dsc_list:
            kid = dsc['kid']
            data = dsc['raw_data']
            stored_dsc = service.get_dsc(kid)

            if kid in not_whitelisted_dsc:
                assert stored_dsc is None
            else:
                assert stored_dsc == data
