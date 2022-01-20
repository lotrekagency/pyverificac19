from json.decoder import JSONDecodeError
import requests
from requests import RequestException
from verificac19.service._settings import *
from .check import CrlCheck
from .mongo import MongoCRL

from verificac19.service._settings import DOWNLOAD_CRL_URL
from .chunk import Chunk

DOWNLOAD_SUCCESSFUL = 0
DOWNLOAD_FAILED = -1
DOWNLOAD_NOT_NEEDED = 1

class CrlDownloader:
    _db = MongoCRL()
    _params = {}
    _check = CrlCheck()
    _is_local_crl_up_to_date = None

    @classmethod
    def run(cls) -> int:
        """Updates the CRL.

        It updates the CRL by understanding the current state of the database
        and fetching from the API with the correct parameters based on the
        locally stored data.
        If some error occures while retrieving the chunks,
        it will try again for a limit specified in the settings file.

        Returns
        -------
        int
            Wether the updata has been successful or not. It will return the
            value of either DOWNLOAD_SUCCESSFUL, DOWNLOAD_NOT_NEEDED or
            DOWNLOAD_FAILED
        """
        errors_left = MAX_ERRORS_CRL_DOWNLOAD
        while errors_left > 0:
            cls._prepare_for_download()
            if not cls._is_local_crl_up_to_date:
                return DOWNLOAD_NOT_NEEDED

            cls._set_download_started_in_db()
            try:
                chunks = cls._download_crl(cls._params)
                return DOWNLOAD_SUCCESSFUL
            except (RequestException, JSONDecodeError):
                errors_left -= 1

        return DOWNLOAD_FAILED


    @classmethod
    def _prepare_for_download(cls):
        cls._check.fetch_crl_check()
        cls._is_local_crl_up_to_date = True

        if cls._db.is_db_empty():
            print('downloading entire crl')
            cls._params = {}
        elif cls._was_download_interrupted():
            print('download interrupted found')
            cls._prepare_to_resume_interrupted_download()
        elif cls._check.is_crl_update_available():
            print('update available')
            stored_version = cls._db.get_meta_data_field('version')
            cls._params = {'version': stored_version}
        else:
            print('no download needed')
            cls._is_local_crl_up_to_date = False


    @classmethod
    def _prepare_to_resume_interrupted_download(cls) -> None:
        cls._params = {}
        updating_to_version = cls._get_interrupted_download_version()
        current_server_version = cls._check.get_server_version()

        if current_server_version != updating_to_version:
            cls._db.clean_ucvis()
            return

        last_stored_chunk = cls._db.get_meta_data_field('last_stored_chunk')
        cls._params = {
            'chunk': last_stored_chunk
        }


    @classmethod
    def _was_download_interrupted(cls) -> bool:
        return bool(cls._db.get_meta_data_field('in_progress'))

    @classmethod
    def _get_interrupted_download_version(cls) -> int | None:
        version = cls._db.get_meta_data_field('updating_to_version')
        return version


    @classmethod
    def _set_download_started_in_db(cls):
        data = {
            'in_progress': True,
            'updating_to_version': cls._check.get_server_version()
        }
        cls._db.set_meta_data(**data)

    @classmethod
    def _download_crl(cls, params: dict):
        download_not_completed = True
        if not params.get('chunk'):
            params['chunk'] = 1
        while download_not_completed:
            chunk = cls._download_chunk(params)
            download_not_completed = not chunk.is_chunk_last()
            cls._save_chunk_to_db(chunk)
            params['chunk'] += 1

        downloaded_version = cls._check.get_server_version()
        cls._db.set_meta_data(in_progress=False, version=downloaded_version)

    @classmethod
    def _download_chunk(cls, request_params: dict) -> Chunk:
        response = requests.get(DOWNLOAD_CRL_URL, params=request_params)
        response.raise_for_status()
        chunk_data = response.json()
        return Chunk(chunk_data)

    @classmethod
    def _save_chunk_to_db(cls, chunk: Chunk) -> None:
        ucvis = chunk.get_ucvis()
        cls._db.update_crl(ucvis.get_new(), ucvis.get_removed())
        cls._db.set_meta_data(last_stored_chunk=chunk.get_number())

    @classmethod
    def is_local_crl_valid(cls) -> bool:
        if cls._was_download_interrupted:
            return False

        if cls._check.is_crl_update_available():
            return False

        return True
