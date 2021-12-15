import requests
import os.path
import json
from typing import Any

class Service:

    DSC_URL = 'https://get.dgc.gov.it/v1/dgc/signercertificate/update'
    SETTINGS_URL = 'https://get.dgc.gov.it/v1/dgc/settings'

    DSC_FILE_CACHE_PATH = 'cache_data/dsc.json'
    SETTINGS_FILE_CACHE_PATH = 'cache_data/settings.json'

    settings = []
    _dsc_collection = {}

    @classmethod
    def update_all(cls) -> None:
        cls._dsc_collection = cls._load_from_cache(cls.DSC_FILE_CACHE_PATH) or cls._fetch_dsc()
        cls.settings = cls._load_from_cache(cls.SETTINGS_FILE_CACHE_PATH) or cls._fetch_settings()


    @classmethod
    def _update_from_apis(cls):
        cls.settings = cls._fetch_settings()


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
    def is_blacklisted(cls, uvci: str) -> bool:
        """Checks whether a green pass is blacked list
        Parameters
        ----------
        uvci: str
            the identifier of the green pass

        Returns
        -------
        bool
            whether is blacked list or not.
        """

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
            cls._dump_to_cache(cls.DSC_FILE_CACHE_PATH, dsc_collection)
            return dsc_collection

        x_kid = response.headers.get('X-KID')
        dsc_collection[x_kid] = response.text
        x_resume_token = response.headers.get('X-RESUME-TOKEN')
        return cls._fetch_dsc(x_resume_token, dsc_collection)

    @classmethod
    def _fetch_settings(cls) -> dict:
        response = requests.get(cls.SETTINGS_URL)
        if response.status_code == 200:
            settings_data = response.json()
            cls._dump_to_cache(cls.SETTINGS_FILE_CACHE_PATH, settings_data)
            return settings_data

        return {}

    @classmethod
    def _dump_to_cache(cls, file_path: str, data: Any) -> None:
        with open(file_path, 'w') as output:
            json.dump(data, output)

    @classmethod
    def _load_from_cache(cls, file_path) -> Any:
        if os.path.exists(file_path):
            with open(file_path, 'r') as input:
                return json.load(input)


service = Service
