from .chunk import Chunk

class ChunkList:

    def __init__(self, first_chunk: Chunk=None) -> None:
        self._first_chunk = first_chunk
        self._last_chunk = self._first_chunk

    def __iter__(self):
        return self._first_chunk

    def add_chunk(self, new_chunk: Chunk):
        if self.is_empty():
            self.__init__(new_chunk)
            return

        self._last_chunk.set_next_chunk(new_chunk)
        self._last_chunk = new_chunk


    def is_empty(self):
        if self._first_chunk is None:
            return True

        return False
