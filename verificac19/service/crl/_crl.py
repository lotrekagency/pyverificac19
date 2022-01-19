class CRL:
    def __init__(self):
        pass

    def store_revoked_uvci(self, revoked_uvci=[], deleted_revoked_uvci=[]) -> None:
        raise NotImplementedError()

    def is_uvci_revoked(self, uvci: str) -> bool:
        raise NotImplementedError()

    def clean(self) -> None:
        raise NotImplementedError()
