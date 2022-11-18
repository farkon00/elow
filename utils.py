import struct

from typing import Iterator

def next_bytes(bytes_iter: Iterator, size: int):
    return bytes([next(bytes_iter) for _ in range(size)])

def next_int(bytes_iter: Iterator, size: int = 4):
    return int.from_bytes(next_bytes(bytes_iter, size), "little")

def next_float(bytes_iter: Iterator):
    return struct.unpack("f", next_bytes(bytes_iter, 4))[0]