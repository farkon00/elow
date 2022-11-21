import struct

from typing import Iterator, Iterable

def next_bytes(bytes_iter: Iterator, size: int):
    return bytes([next(bytes_iter) for _ in range(size)])

def next_int(bytes_iter: Iterator, size: int = 4):
    return int.from_bytes(next_bytes(bytes_iter, size), "little")

def next_float(bytes_iter: Iterator):
    return struct.unpack("f", next_bytes(bytes_iter, 4))[0]

def next_length_str(bytes_iter: Iterator):
    return next_bytes(bytes_iter, size=next_int(bytes_iter)).decode("utf-8")

class QueuedIter:
    def __init__(self, base: list):
        self._queue = base
        self._cursor = 0

    def add(self, obj: object):
        self._queue.insert(self._cursor, obj)

    def __next__(self):
        try:
            self._cursor += 1
            return self._queue[self._cursor-1]
        except IndexError:
            raise StopIteration

    def __iter__(self):
        return self