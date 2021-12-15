import requests

class Service:

    DSC_URL = 'https://get.dgc.gov.it/v1/dgc/signercertificate/update'
    SETTINGS_URL = 'https://get.dgc.gov.it/v1/dgc/settings'

    settings = []
    _dsc_collection = {}

    @classmethod
    def update_all(cls):
        cls.settings = cls._fetch_settings()
        cls._dsc_collection = cls._fetch_dsc()

    @classmethod
    def update_settings(cls):
        cls.settings = cls._fetch_settings()

    @classmethod
    def update_dsc(cls):
        cls._dsc_collection = cls._fetch_dsc()

    @classmethod
    def get_dsc(cls, kid):
        return cls._dsc_collection.get(kid)

    @classmethod
    def is_blacklisted(cls, uvci: str):
        blacklist = cls.get_setting('black_list_uvci', 'black_list_uvci')
        blacklisted_ucvi = blacklist.get('value').split(';')
        return uvci in blacklisted_ucvi
        
    @classmethod
    def get_setting(cls, setting_name: str, setting_type: str) -> dict:
        try:
            setting_data: dict = next(iter([ setting for setting in cls.settings if setting['name'] == setting_name and setting['type'] == setting_type]))
            return setting_data
        except StopIteration:
            return {}


    @classmethod
    def _fetch_dsc(cls, token: str=None, dsc_collection: dict={}) -> dict:
        headers = {
            'X-RESUME-TOKEN': token
        }
        response = requests.get(cls.DSC_URL, headers=headers)

        if not response.status_code == 200:
            return dsc_collection

        x_kid = response.headers.get('X-KID')
        dsc_collection[x_kid] = response.text
        x_resume_token = response.headers.get('X-RESUME-TOKEN')
        return cls._fetch_dsc(x_resume_token, dsc_collection)

    @classmethod
    def _fetch_settings(cls) -> dict:
        response = requests.get(cls.SETTINGS_URL)
        if response.status_code == 200:
            return response.json()
        return {}

service = Service

