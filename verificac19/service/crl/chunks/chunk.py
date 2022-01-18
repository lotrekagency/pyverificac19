from __future__ import annotations
from verificac19.service.crl.ucvis import UcviData

class Chunk:

    def __new__(cls, chunk_data: dict, next_chunk: Chunk) -> Chunk:
        if cls.is_chunk_diff(chunk_data):
            return DiffChunk(chunk_data, next_chunk)

        return cls(chunk_data, next_chunk)


    def __init__(self, chunk_data: dict, next_chunk: Chunk=None) -> None:
        self._next_chunk = next_chunk
        self._chunk_data = chunk_data
        self._store_general_chunk_data()
        self._store_revoked_ucvis()

    def __next__(self):
        if self._next_chunk is None:
            raise StopIteration

        return self._next_chunk


    def _store_general_chunk_data(self):
        self._version = self._chunk_data['version']
        self._number = self._chunk_data['chunk']


    def _store_revoked_ucvis(self):
        revoked_ucvis = self._chunk_data['revokedUcvi']
        self._ucvis = UcviData(new=revoked_ucvis)

    def is_chunk_last(self) -> bool:
        """
        Checks whether this chunk is the last one in the crl.

        Returns
        -------
        bool
        """
        return self._chunk_data['lastChunk'] == self._number

    def set_next_chunk(self, next_chunk: Chunk) -> None:
        """Saves next chunk reference.

        Useful for iterating chunk objects of the same crl.
        """
        self._next_chunk = next_chunk

    @staticmethod
    def is_chunk_diff(chunk_data: dict) -> bool:
        """
        Checks whether the chunk belongs to a diff or not.

        Parameters
        ----------
        chunk_data: dict
            a dictionary representing the http response of the chunk

        Returns
        -------
        bool

        Raises
        ------
        ValueError
            If chunk_data does not contain a valid value
        """
        revoked_ucvis = chunk_data.get('revokedUcvi')
        if revoked_ucvis is not None:
            return False

        delta = chunk_data.get('delta')
        if delta is not None:
            return True

        raise ValueError(f'chunk data is not valid: {chunk_data}')

    

class DiffChunk(Chunk):

    def _store_general_chunk_data(self):
        super()._store_general_chunk_data()
        self._from_version = self._chunk_data['from_version']

    def _store_revoked_ucvis(self):
        new_revoked_ucvis = self._chunk_data['delta']['insertions']
        removed_revoked_ucvis = self._chunk_data['delta']['deletions']
        self._ucvis = UcviData(new_revoked_ucvis, removed_revoked_ucvis)
