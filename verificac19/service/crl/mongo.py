import os
from pymongo import MongoClient
from pymongo.errors import BulkWriteError, DuplicateKeyError
from typing import Any, Union

from ._crl import CRL

MONGO_DB_CONNECTION_URL = os.environ.get(
    "VC19_MONGODB_URL", "mongodb://root:example@localhost:27017/VC19?authSource=admin"
)


class MongoCRL(CRL):
    def __init__(self):
        self._client = MongoClient(MONGO_DB_CONNECTION_URL)
        self._db = self._client.VC19
        self._db_uvci = self._db.uvci
        self._db_meta = self._db.meta

    def set_meta_data(self, **data) -> None:
        meta_data = self._db_meta.find_one()

        if meta_data is None:
            self._initialise_meta_info(data)
            return

        self._db_meta.find_one_and_update({}, {"$set": data})

    def get_meta_data(self, *fields: str, flat: bool = False) -> Union[dict, None]:
        if len(fields) != 1 and flat:
            raise ValueError("flat can be set only when selecting one field")

        projection_settings = {field: True for field in fields}
        projection_settings["_id"] = False
        query_result = self._db_meta.find_one(projection=projection_settings)

        if flat and query_result is not None:
            field_name = fields[0]
            return query_result.get(field_name)

        return query_result

    def get_meta_data_field(self, field) -> Union[Any, None]:
        return self.get_meta_data(field, flat=True)

    def _initialise_meta_info(self, data: dict):
        self._db_meta.insert_one(data)

    def update_crl(self, revoked_uvci=[], deleted_revoked_uvci=[]) -> None:
        self._bulk_add_uvci(revoked_uvci)
        self._remove_uvci(deleted_revoked_uvci)

    def _bulk_add_uvci(self, revoked_uvci: list = []):
        if len(revoked_uvci) == 0:
            return

        try:
            self._db_uvci.insert_many([{"_id": uvci} for uvci in revoked_uvci])
        except BulkWriteError:
            self._iterative_add_uvci(revoked_uvci)

    def _iterative_add_uvci(self, revoked_uvci: list = []):
        for uvci_to_insert in revoked_uvci:
            try:
                self._db_uvci.insert_one({"_id": uvci_to_insert})
            except DuplicateKeyError:
                pass

    def _remove_uvci(self, deleted_revoked_uvci: list = []):
        for uvci_to_remove in deleted_revoked_uvci:
            self._db_uvci.delete_one({"_id": uvci_to_remove})

    def is_uvci_revoked(self, uvci: str) -> bool:
        return self._db_uvci.find_one({"_id": uvci}) is not None

    def clean_all(self) -> None:
        self._db_uvci.delete_many({})
        self._db_meta.delete_many({})

    def clean_uvcis(self) -> None:
        self._db_uvci.delete_many({})

    def store_current_version(self, version: int) -> None:
        self.set_meta_data(version=version)

    def is_db_empty(self) -> bool:
        return self.get_meta_data() is None
