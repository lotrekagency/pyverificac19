import requests
from verificac19.service._mongo_crl import MongoCRL
from verificac19.service._settings import *

class CrlCheck:

    def __init__(self) -> None:
        self._crl_check = None
        self.db = MongoCRL()

    def fetch_crl_check(self) -> None:
        response = requests.get(CHECK_CRL_URL)
        self._crl_check = response.json()

    def is_crl_update_available(self) -> bool:
        if self._crl_check is None:
            self.fetch_crl_check()

        stored_version = self.db.get_version()
        if stored_version == self._crl_check['version']:
            return False

        return True