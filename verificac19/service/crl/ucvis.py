from verificac19.service._settings import *
from verificac19.service.crl.mongo import MongoCRL

UciviList = list[str]
UciviTuple = tuple[str]



class UcviData:

    def __init__(self, new: UciviList=[], removed: UciviList=[]) -> None:
        self._new: UciviList = new
        self._removed: UciviList = removed

    def add_ucvis(self, new: UciviList=[], removed: UciviList=[]) -> None:
        self._new += new
        self._removed += removed

    def get_new(self) -> UciviList:
        return self._new

    def get_removed(self) -> UciviList:
        return self._removed
