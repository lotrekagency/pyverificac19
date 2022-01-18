import os
from pymongo import MongoClient
from pymongo.errors import BulkWriteError, DuplicateKeyError

from ._crl import CRL

MONGO_DB_CONNECTION_URL = os.environ.get(
    "VC19_MONGODB_URL", "mongodb://root:example@localhost:27017/VC19?authSource=admin"
)


class MongoCRL(CRL):
    def __init__(self):
        self._client = MongoClient(MONGO_DB_CONNECTION_URL)
        self._db = self._client.VC19
        self._db_uvci = self._db.uvci

    def store_revoked_uvci(self, revoked_uvci=[], deleted_revoked_uvci=[]) -> None:
        try:
            self._db_uvci.insert_many(map(lambda uvci: {"_id": uvci}, revoked_uvci))
        except BulkWriteError:
            for uvci_to_insert in revoked_uvci:
                try:
                    self._db_uvci.insert_one({"_id": uvci_to_insert})
                except DuplicateKeyError:
                    pass
        for uvci_to_remove in deleted_revoked_uvci:
            self._db_uvci.delete_one({"_id": uvci_to_remove})

    def is_uvci_revoked(self, uvci: str) -> bool:
        return self._db_uvci.find_one({"_id": uvci}) is not None

    def clean(self) -> None:
        self._db_uvci.delete_many({})


    def store_current_version(self, version: int) -> None:
        collection_to_find = {'_id': 0}
        updated_data = {
            '$set': {
                'version': version
            }
        }
        previous = self._db.version.find_one_and_update(
            collection_to_find,
            updated_data
        )

        if previous is not None:
            return

        self._db.version.insert_one({
            '_id': 0,
            'version': version
        })

    def get_version(self) -> int|None:
        document = self._db.version.find_one()
        if document is None:
            return None

        return document['version']
