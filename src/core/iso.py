from typing import Any, Dict, Final, List, Optional, Tuple

import pyfiglet
from starkbank import iso8583
from term_image.image import BaseImage, from_file

from ..helpers import (
    DataLogging,
    file_search,
    format_date,
    format_size,
    format_space,
)
from ..models import (
    CompMC8583,
    TupleFileManager,
    TypeCycleIpm,
    TypeIpm,
    TypeIpmDb,
    TypeParseIpm,
    TypeParseIpmDb,
)
from ..template import custom_mastercard, mastercard_db
from ..utils import BeautifyIpmDb, print_custom_text


class ISO8583ParseError(Exception): ...


class MC8583(DataLogging):
    _TITLE: Final[str] = pyfiglet.figlet_format(
        " MASTERCARD PARSE\n", font="ansi_shadow", width=200
    ) + pyfiglet.figlet_format(" ISO 8583-1993", font="ansi_shadow", width=200)

    _PATH: str = r"src\img\mastercard_logo.png"

    def __init__(self) -> None:
        super().__init__()

        self._file_info: Optional[TupleFileManager] = None
        self._len_raw: int = 0
        self._file_date: Optional[str] = None
        self._file_cycle: Optional[str] = None

        self._img: BaseImage = from_file(filepath=self._PATH)
        self._img.set_size(width=34, height=10)
        print(str(self._img).rstrip(), end="\n")

        print_custom_text(
            text=self._TITLE, highlight=["Bold"], color_foreground="Orange1", end="\n"
        )

        return None

    def search_ipm(self, file_date: str, file_cycle: TypeCycleIpm) -> None:

        self._file_date, self._file_cycle = file_date, file_cycle
        self._file_infos: Optional[TupleFileManager] = file_search(
            file_date=file_date, file_cycle=file_cycle
        )

        return None

    def parse_ipm(
        self,
        logging: bool = True,
    ) -> TypeParseIpm:

        file_name: Optional[str] = None
        file_bytes: Optional[memoryview] = None
        parse_ipm: Optional[TypeIpm] = None
        msg_count: Optional[int] = None
        if self._file_infos:
            file_name, file_bytes = self._file_infos
            parse_ipm, msg_count = self._playload_iso_file(raw=file_bytes)
            if logging:
                self._logging(file_name=file_name, row_count=msg_count, data=parse_ipm)

            return parse_ipm, file_name

        return None

    def parse_ipm_db(
        self,
        logging: bool = True,
    ) -> TypeParseIpmDb:

        file_name: Optional[str] = None
        file_bytes: Optional[memoryview] = None
        parse_ipm: Optional[TypeIpm] = None
        msg_count: Optional[int] = None

        if self._file_infos:
            file_name, file_bytes = self._file_infos
            parse_ipm, msg_count = self._playload_iso_file(raw=file_bytes)
            if logging:
                self._logging(file_name=file_name, row_count=msg_count, data=parse_ipm)

            ipm_db: BeautifyIpmDb = BeautifyIpmDb(
                template=mastercard_db, elements=parse_ipm
            )

            parse_db: List[List[TypeIpmDb]] = ipm_db.parse()

            return parse_db, file_name

        return None

    def _extract_iso_payload(
        self, raw: memoryview, index: int, len_raw: int
    ) -> Tuple[bytes, int]:

        start: int = index
        payload: bytearray = bytearray()
        index_current: int = index
        payload_extend = payload.extend

        while True:
            if index_current + 4 > len_raw:
                break

            seg_id: int = raw[index_current + 2] & 0xFF
            seg_len: int = ((raw[index_current] & 0xFF) << 8) | (
                raw[index_current + 1] & 0xFF
            )

            payload_len: int = seg_len - 4
            payload_extend(raw[index_current + 4 : index_current + 4 + payload_len])
            index_current += 4 + payload_len

            if not seg_id:
                break
            if index_current + 2 < len_raw and raw[index_current + 2] == 0:
                break

        return bytes(payload), index_current - start

    def _playload_iso_file(self, raw: memoryview) -> Tuple[TypeIpm, int]:

        self._len_raw: int = len(raw)
        index: int = 0
        msg_count: int = 0
        mti_parse: TypeIpm = []
        msg_parse: Dict[str, Any] = {}
        extract_iso = self._extract_iso_payload
        append_mti = mti_parse.append

        try:
            while index < self._len_raw:
                payload, consumed = extract_iso(
                    raw=raw, index=index, len_raw=self._len_raw
                )
                index += consumed

                msg_parse = iso8583.parse(
                    message=payload, template=custom_mastercard, encoding="cp500"
                )

                append_mti(msg_parse)

                msg_count += 1

        except Exception as e:
            msg_error: str = f"Erro na mensagem #{msg_count + 1} (offset {index})"
            raise ISO8583ParseError(msg_error) from e

        return mti_parse, msg_count

    def _logging(self, file_name: str, row_count: int, data: TypeIpm) -> None:

        row_count_format: str = f"{row_count:,}".replace(",", ".")
        space: Optional[str] = None
        rows: List[str] = [
            f" ◉ 📄 File Name  {CompMC8583.SIDE} {file_name}",
            f" ◉ 📄 File Date  {CompMC8583.SIDE} {format_date(file_name=file_name)}",
            f" ◉ 📄 File Cycle {CompMC8583.SIDE} {self._file_cycle}",
            f" ◉ 📄 File Size  {CompMC8583.SIDE} {format_size(self._len_raw)}",
            f" ◉ 📄 File Row   {CompMC8583.SIDE} {row_count_format}",
        ]

        body: str = f"    {CompMC8583.PARTING}\n"

        for idx, row in enumerate(rows):
            space = format_space(text1=CompMC8583.HEADER, text2=row)

            if not idx:
                body += (
                    f"    {CompMC8583.HEADER_CONTOUR}"
                    f"    {CompMC8583.SIDE_CONTOUR} {CompMC8583.HEADER} {CompMC8583.SIDE_CONTOUR}\n"
                    f"    {CompMC8583.ROW_CUSTOM_INIT}{row + space}{CompMC8583.ROW_CUSTOM_END}\n"
                )

            if idx:
                body += f"    {CompMC8583.ROW_CUSTOM_INIT}{row + space}{CompMC8583.ROW_CUSTOM_END}\n"

        body += (
            f"    {CompMC8583.SIDE_CONTOUR} {CompMC8583.FOOTER} {CompMC8583.SIDE_CONTOUR}\n"
            f"    {CompMC8583.FOOTER_CONTOUR}"
        )

        self.logging_file(data=data, file_name=file_name, type_logg=["csv", "txt"])

        print(body)

        return None
