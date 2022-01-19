import requests
from verificac19.service._settings import *
from .check import CrlCheck
from .mongo import MongoCRL

from verificac19.service._settings import DOWNLOAD_CRL_URL
from .chunks import Chunk, ChunkList

class CrlDownloader:
    _db = MongoCRL()
    _params = None

    @classmethod
    def prepare_for_download(cls):
        CrlCheck.fetch_crl_check()

        if cls._db.is_db_empty():
            cls._params = {}
        elif cls._was_download_interrupted():
            cls._prepare_to_resume_interrupted_download()
        elif CrlCheck.is_crl_update_available():
            stored_version = cls._db.get_meta_data_field('version')
            cls._params = {'version': stored_version}
        else:
            cls._is_download_needed = False


    @classmethod
    def _prepare_to_resume_interrupted_download(cls) -> None:
        cls._params = {}
        updating_to_version = cls._db.get_meta_data_field('updating_to_version')
        current_server_version = CrlCheck.get_server_version()

        if current_server_version != updating_to_version:
            cls._db.clean_ucvis()
            return

        last_stored_chunk = cls._db.get_meta_data_field('last_stored_chunk')
        cls._params = {
            'version': current_server_version,
            'chunk': last_stored_chunk
        }


    @classmethod
    def _was_download_interrupted(cls) -> bool:
        return bool(cls._db.get_meta_data_field('in_progress'))

    @classmethod
    def _getinterrupted_download_version(cls) -> int | None:

        version = cls._db.get_meta_data_field('updating_to_version')
        return version


    @classmethod
    def download_crl(cls):
        if type(cls._params) is not dict:
            raise ValueError("Request parameters not valid. Maybe forgot to run prepare_for_download() ?")

        chunks = cls._download_crl(cls._params)
        return chunks

    @classmethod
    def _set_download_started_in_db(cls):
        data = {
            'in_progress': True,
            'updating_to_version': CrlCheck.get_server_version()
        }
        cls._db.set_meta_data(**data)

    @classmethod
    def _download_crl(cls, params: dict) -> ChunkList:
        chunks = ChunkList()
        download_not_completed = True
        chunk_n = 1
        while download_not_completed:
            params['chunk'] = chunk_n
            chunk = cls._download_chunk(params)
            chunks.add_chunk(chunk)
            download_not_completed = not chunk.is_chunk_last()
            chunk_n += 1

        return chunks

    @classmethod
    def _download_chunk(cls, request_params: dict) -> Chunk:
        response = requests.get(DOWNLOAD_CRL_URL, params=request_params)
        chunk_data = response.json()
        return Chunk(chunk_data)
