from typing import List

UvciList = List[str]


class UvciData:
    def __init__(self, new: UvciList = [], removed: UvciList = []) -> None:
        self._new: UvciList = new
        self._removed: UvciList = removed

    def add_uvcis(self, new: UvciList = [], removed: UvciList = []) -> None:
        self._new += new
        self._removed += removed

    def get_new(self) -> UvciList:
        return self._new

    def get_removed(self) -> UvciList:
        return self._removed
