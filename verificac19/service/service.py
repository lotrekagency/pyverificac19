import requests
from typing import Union, Dict
from datetime import datetime, timedelta

from ._cache import dump_to_cache, fetch_with_smart_cache
from ..exceptions import VerificaC19Error

Dsc = Dict[str, str]


API_URL = "https://get.dgc.gov.it/v1/dgc"

DSC_URL = f"{API_URL}/signercertificate/update"
STATUS_URL = f"{API_URL}/signercertificate/status"
SETTINGS_URL = f"{API_URL}/settings"

DSC_FILE_CACHE_PATH = "dsc.json"
SETTINGS_FILE_CACHE_PATH = "settings.json"


class Service:
    def __init__(self):
        self._allowed_kids = []
        self._load_from_cache()

    def update_all(self) -> None:
        """Updates dsc and settings data.

        Restores dsc and settings data from cache if possible.
        Otherwise it retrieves them from the api.
        """
        self._dsc_collection: Dsc = fetch_with_smart_cache(
            DSC_FILE_CACHE_PATH, self._fetch_dsc
        )
        self._settings: list = fetch_with_smart_cache(
            SETTINGS_FILE_CACHE_PATH, self._fetch_settings
        )

    def update_settings(self) -> None:
        """Force update settings from apis."""
        self._settings = self._fetch_settings()

    def update_dsc(self) -> None:
        """Force update dsc from apis."""
        self._dsc_collection = self._fetch_dsc()

    def get_dsc(self, kid) -> Union[str, None]:
        """Retrieves dsc from kid."""
        self._need_reload_from_cache()
        return self._dsc_collection.get(kid)

    def is_blacklisted(self, uvci: str) -> bool:
        """Checks whether a green pass is blacked list.

        Parameters
        ----------
        uvci: str
            the identifier of the green pass

        Returns
        -------
        bool
            whether is blacked list or not
        """
        self._need_reload_from_cache()
        blacklist = self.get_setting("black_list_uvci", "black_list_uvci")
        blacklisted_ucvi = blacklist.get("value", "").split(";")
        return uvci in blacklisted_ucvi

    def get_setting(self, setting_name: str, setting_type: str) -> dict:
        """Get the setting.

        Returns an empty dict if the option is not found.
        """
        self._need_reload_from_cache()
        try:
            setting_data: dict = next(
                iter(
                    [
                        setting
                        for setting in self._settings
                        if setting["name"] == setting_name
                        and setting["type"] == setting_type
                    ]
                )
            )
            return setting_data
        except StopIteration:
            return {}

    def _need_reload_from_cache(self) -> None:
        if (
            datetime.now() > self._next_load_from_cache
            or not self._dsc_collection
            or not self._settings
        ):
            self._load_from_cache()
            if not self._dsc_collection or not self._settings:
                raise VerificaC19Error(
                    "You need to initialize your cache. Call service.update_all()."
                )

    def _load_from_cache(self) -> None:
        self._dsc_collection: Dsc = (
            fetch_with_smart_cache(DSC_FILE_CACHE_PATH, self._fetch_dsc, True) or {}
        )
        self._settings: list = (
            fetch_with_smart_cache(SETTINGS_FILE_CACHE_PATH, self._fetch_settings, True)
            or []
        )
        self._next_load_from_cache = datetime.now() + timedelta(hours=1)

    def _update_from_apis(self) -> None:
        self._settings = self._fetch_settings()

    def _fetch_status(self) -> dict:
        response = requests.get(STATUS_URL)
        if response.status_code == 200:
            return response.json()
        raise VerificaC19Error("Error fetching status")

    def _fetch_dsc(self, token: str = None, dsc_collection: dict = {}) -> dict:
        if not token:
            self._allowed_kids = self._fetch_status()
        headers = {"X-RESUME-TOKEN": token}
        response = requests.get(DSC_URL, headers=headers)

        if response.status_code == 200:
            pass
        elif response.status_code == 204:
            dump_to_cache(DSC_FILE_CACHE_PATH, dsc_collection)
            return dsc_collection
        else:
            raise VerificaC19Error("Error fetching DSC")

        x_kid = response.headers.get("X-KID")
        if x_kid in self._allowed_kids:
            dsc_collection[x_kid] = response.text
        x_resume_token = response.headers.get("X-RESUME-TOKEN")
        return self._fetch_dsc(x_resume_token, dsc_collection)

    def _fetch_settings(self) -> list:
        response = requests.get(SETTINGS_URL)
        if not response.status_code == 200:
            raise VerificaC19Error("Error fetching settings")
        settings_data = response.json()
        dump_to_cache(SETTINGS_FILE_CACHE_PATH, settings_data)
        return settings_data


_service = Service()
