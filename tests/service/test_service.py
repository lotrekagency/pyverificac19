from tests.service.setup import run_setup
from verificac19 import service
import pook
from tests.utils import open_json


class TestService:
    @pook.on
    def test_setup(self):
        run_setup()

    @pook.on
    def test_dsc_settings(self):
        settings_data = open_json("settings.json")
        for setting in settings_data:
            st_name = setting["name"]
            st_type = setting["type"]
            assert service.get_setting(st_name, st_type) == setting

    @pook.on
    def test_dsc_certificates(self):
        not_whitelisted_dsc = ["nJkLGpmXT68=", "b32660V8q5A=", "gBG2e8Vypv0="]
        dsc_list = open_json("dsc_validation.json")
        for dsc in dsc_list:
            kid = dsc["kid"]
            data = dsc["raw_data"]
            stored_dsc = service.get_dsc(kid)

            if kid in not_whitelisted_dsc:
                assert stored_dsc is None
            else:
                assert stored_dsc == data
