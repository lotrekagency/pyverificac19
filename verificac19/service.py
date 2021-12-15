import requests

class Service:

    DSC_URL = 'https://get.dgc.gov.it/v1/dgc/signercertificate/update'
    SETTINGS_URL = 'https://get.dgc.gov.it/v1/dgc/settings'

    settings = []
    dscs = []

    @classmethod
    def update_all(cls):
        cls.settings = cls._fetch_settings()
        cls.dscs = cls._fetch_dsc()

    @classmethod
    def update_settings(cls):
        cls.settings = cls._fetch_settings()

    @classmethod
    def update_dsc(cls):
        cls.dscs = cls._fetch_dsc()

    @classmethod
    def get_dsc(cls, kid):
        return cls.dscs.get(kid)

    @classmethod
    def is_blacklisted(cls, uvci):
        blacklist = cls.get_setting('black_list_uvci', 'black_list_uvci')
        blacklisted_ucvi = blacklist.get('value').split(';')
        return uvci in blacklisted_ucvi
        
    @classmethod
    def get_setting(cls, dsc_name, dsc_type):
        return next([ setting for setting in cls.settings if setting['name'] == dsc_name and setting['type'] == dsc_type])

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

