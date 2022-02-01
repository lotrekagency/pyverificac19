import requests
from typing import Union
from verificac19.service.crl.mongo import MongoCRL
from verificac19.service._settings import CHECK_CRL_URL


class CrlCheck:
    def __init__(self) -> None:
        self._db = MongoCRL()

    def fetch_crl_check(self) -> None:
        response = requests.get(CHECK_CRL_URL)
        self._crl_check = response.json()

    def is_crl_update_available(self) -> bool:
        if self._crl_check is None:
            self.fetch_crl_check()

        stored_version = self._db.get_meta_data_field("version")
        if stored_version == self._crl_check["version"]:
            return False

        return True

    def get_server_version(self) -> Union[int, None]:
        if self._crl_check is None:
            self.fetch_crl_check()

        return self._crl_check["version"]
