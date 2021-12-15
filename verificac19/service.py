import requests

class Service:

    DSC_URL = 'https://get.dgc.gov.it/v1/dgc/signercertificate/update'
    SETTINGS_URL = 'https://get.dgc.gov.it/v1/dgc/settings'

    @classmethod
    def update_all(cls):
        settings = cls._fetch_settings()
        dscs = cls._fetch_dsc()

    @classmethod
    def update_settings(cls):
        settings = cls._fetch_settings()

    @classmethod
    def update_dsc(cls):
        dscs = cls._fetch_dsc()

    @classmethod
    def get_dsc(kid):
        raise NotImplemented

    @classmethod
    def is_blacklisted(uvci):
        raise NotImplemented

    @classmethod
    def get_setting(name, type):
        raise NotImplemented

    @classmethod
    def _fetch_dsc(cls, token=None, dscs={}):
        headers = {
            'X-RESUME-TOKEN': token
        }
        response = requests.get(cls.DSC_URL, headers=headers)
        if response.status_code == 200:
            dscs[response.headers.get('X-KID')] = response.text
            return cls._fetch_dsc(response.headers.get('X-RESUME-TOKEN'), dscs)
        return dscs

    @classmethod
    def _fetch_settings(cls):
        response = requests.get(cls.SETTINGS_URL)
        if response.status_code == 200:
            return response.text
        return {}

service = Service

