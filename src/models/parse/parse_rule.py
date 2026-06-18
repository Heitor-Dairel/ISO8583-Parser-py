from binascii import unhexlify
from datetime import datetime
from typing import Tuple, Union


class ParseIntegerDb:
    def __init__(self) -> None: ...

    def field(self, data_element: str, name: str) -> Union[int, float]:
        if name == "DE004":
            return int(data_element) / 100

        return int(data_element)


class ParseStringDb:
    def __init__(self) -> None: ...

    def field(self, data_element: str, name: str, custom: bool = False) -> str:

        return data_element


class ParseDateDb:
    def __init__(self) -> None: ...

    def field(self, data_element: str, name: str) -> str:

        if name == "DE012":
            return datetime.strptime(data_element, "%y%m%d%H%M%S").strftime(
                "%d/%m/%Y %H:%M:%S"
            )

        return datetime.strptime(data_element, "%y%m").strftime("%y/%m")


class ParseHexadecimal:
    def parse(self, data: bytes, length: int, encoding: str) -> str:
        return data.hex().upper()

    def unparse(self, value: str, encoding: str) -> Tuple[bytes, int]:
        data: bytes = unhexlify(value)
        logicalLength: int = len(data)
        return data, logicalLength

    def byteLength(self, length: int) -> int:
        return length
