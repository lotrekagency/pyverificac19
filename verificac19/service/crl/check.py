import requests
from verificac19.service.crl.mongo import MongoCRL
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

        stored_version = cls._db.get_meta_data_field('version')
        if stored_version == cls._crl_check['version']:
            return False

        return True

    @classmethod
    def get_server_version(cls) -> int | None:
        if cls._crl_check is None:
            cls.fetch_crl_check()

        return cls._crl_check['version']
