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

    @pook.on
    def test_dsc_settings(self):
        settings_data = self.open_json("settings.json")
        pook.get(SETTINGS_URL, reply=200, response_json=settings_data)
        service.update_settings()
        for setting in settings_data:
            st_name = setting['name']
            st_type = setting['type']
            assert service.get_setting(st_name, st_type) == setting

    @pook.on
    def test_update_all(self):
        pook.get(SETTINGS_URL, reply=200, response_json=self.open_json("settings.json"))
        pook.get(STATUS_URL, reply=200, response_json=self.open_json("certificate_status.json"))
        dsc_validation = self.open_json("dsc_validation.json")
        for index, dsc in enumerate(dsc_validation):
            header = {"content-type": "text/plain"}
            if index > 0:
                header["X-RESUME-TOKEN"] = str(index)

            reply = 200 if index < len(dsc_validation) - 1 else 204
            response_headers = {
                "X-KID": dsc["kid"],
                "X-RESUME-TOKEN": str(index + 1),
            }

            pook.get(
                DSC_URL,
                reply=reply,
                response_body=dsc["raw_data"],
                headers=header,
                response_headers=response_headers,
            )

        service.clear_all_cache()

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

        service.update_all()
