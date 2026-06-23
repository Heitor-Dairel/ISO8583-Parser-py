from binascii import unhexlify
from typing import Tuple


class ParseHexadecimal:
    def parse(self, data: bytes, length: int, encoding: str) -> str:
        return data.hex().upper()

    def unparse(self, value: str, encoding: str) -> Tuple[bytes, int]:
        data: bytes = unhexlify(value)
        logicalLength: int = len(data)
        return data, logicalLength

    def byteLength(self, length: int) -> int:
        return length
