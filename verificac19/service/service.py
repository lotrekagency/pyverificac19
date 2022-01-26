import requests
from typing import Union
from datetime import datetime, timedelta

from ._cache import dump_to_cache, fetch_with_smart_cache, clear_all_cache
from ..exceptions import VerificaC19Error

from ._settings import (
    DSC_URL,
    STATUS_URL,
    SETTINGS_URL,
    DSC_FILE_CACHE_PATH,
    SETTINGS_FILE_CACHE_PATH,
)

from .crl.download import CrlDownloader
from .crl.mongo import MongoCRL


class Service:
    def __init__(self):
        self._allowed_kids = []
        self._load_from_cache()

    def update_all(self) -> None:
        """Updates dsc and settings data.

        Restores dsc and settings data from cache if possible.
        Otherwise it retrieves them from the api.
        """
        self._dsc_collection = fetch_with_smart_cache(
            DSC_FILE_CACHE_PATH, self._fetch_dsc
        )
        self._settings: list = fetch_with_smart_cache(
            SETTINGS_FILE_CACHE_PATH, self._fetch_settings
        )
        CrlDownloader.run()

    def is_local_crl_valid(self) -> bool:
        """Checks whether the local CRL is valid.

        Keep in mind that to get updated results, you should run the update_all
        method first.

        Returns
        -------
        bool
        """
        if CrlDownloader.was_download_interrupted:
            return False

        if CrlDownloader.is_crl_update_available():
            return False

        return True

    def is_uvci_revoked(self, uvci: str) -> bool:
        """Checks whether the uvci is revoked or not.

        Parameters
        ----------
        uvci: str

        Returns
        -------
        bool
        """
        db = MongoCRL()
        return db.is_uvci_revoked(uvci)

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
        self._dsc_collection = (
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
        headers = {"X-RESUME-TOKEN": token, "content-type": "text/plain"}
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

    def clear_all_cache(self) -> None:
        clear_all_cache()


_service = Service()
