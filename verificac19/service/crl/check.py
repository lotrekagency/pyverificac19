import requests
from verificac19.service._mongo_crl import MongoCRL
from verificac19.service._settings import CHECK_CRL_URL

class CrlCheck:

    _crl_check = None
    _db = MongoCRL()

    @classmethod
    def fetch_crl_check(cls) -> None:
        response = requests.get(CHECK_CRL_URL)
        cls._crl_check = response.json()

    @classmethod
    def is_crl_update_available(cls) -> bool:
        if cls._crl_check is None:
            cls.fetch_crl_check()

        stored_version = cls._db.get_version()
        if stored_version == cls._crl_check['version']:
            return False

        return True
