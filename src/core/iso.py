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
    FG_COLORS_SEARCH,
    HIGHLIGHT,
    TupleManagerFile,
    TypeCycleIpm,
    TypeIpm,
    TypeIpmDb,
    TypeParseIpm,
    TypeParseIpmDb,
)
from ..template import mastercard, mastercard_db
from ..utils import BeautifyIpmDb, print_custom_text


class ISO8583ParseError(Exception): ...


class MC8583(DataLogging):
    _TITLE: Final[str] = pyfiglet.figlet_format(
        " MASTERCARD PARSE\n", font="ansi_shadow", width=200
    ) + pyfiglet.figlet_format(" ISO 8583-1993", font="ansi_shadow", width=200)

    _PATH: str = r"src\img\mastercard_logo.png"

    _RESET: Final[str] = "\x1b[0m"
    _BOLD: Final[str] = HIGHLIGHT["Bold"]
    _COLOR_DEFAULT: Final[str] = FG_COLORS_SEARCH["White"]
    _COLOR_CUSTOM: Final[str] = FG_COLORS_SEARCH["Red"]
    _PARTING: Final[str] = (
        f"{_RESET}{_BOLD}{_COLOR_CUSTOM}══════════════════════════════════ ◆ ═══════════════════════════════════{_RESET}\n"
    )
    _HEADER_CONTOUR: Final[str] = (
        f"{_RESET}{_BOLD}{_COLOR_CUSTOM}╔══════════════════════════════════════════════════════════════════════╗{_RESET}\n"
    )
    _FOOTER_CONTOUR: Final[str] = (
        f"{_RESET}{_BOLD}{_COLOR_CUSTOM}╚══════════════════════════════════════════════════════════════════════╝{_RESET}\n\n"
    )
    _SIDE_CONTOUR: Final[str] = f"{_RESET}{_COLOR_CUSTOM}║{_RESET}"
    _HEADER: Final[str] = (
        f"{_RESET}{_BOLD}{_COLOR_CUSTOM}╭─────────────────┬───────── Parse IPM ────────────────────────────╮{_RESET}"
    )
    _FOOTER: Final[str] = (
        f"{_RESET}{_BOLD}{_COLOR_CUSTOM}╰─────────────────┴────────────────────────────────────────────────╯{_RESET}"
    )
    _SIDE: Final[str] = f"{_RESET}{_COLOR_CUSTOM}│{_RESET}{_BOLD}{_COLOR_DEFAULT}"
    _ROW_CUSTOM_INIT: Final[str] = (
        f"{_SIDE_CONTOUR} {_SIDE}{_RESET}{_BOLD}{_COLOR_DEFAULT}"
    )
    _ROW_CUSTOM_END: Final[str] = f"{_RESET}{_SIDE} {_SIDE_CONTOUR}"

    def __init__(self) -> None:
        super().__init__()

        self._file_info: Optional[TupleManagerFile] = None
        self._len_raw: int = 0
        self._file_date: Optional[str] = None
        self._cycle: Optional[str] = None

        img: BaseImage = from_file(filepath=self._PATH)
        img.set_size(width=34, height=10)
        print(str(img).rstrip(), end="\n")

        print_custom_text(
            text=self._TITLE, highlight=["Bold"], color_foreground="Orange1", end="\n"
        )

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

    def _playload_ipm_file(self, raw: memoryview) -> Tuple[TypeIpm, int]:

        self._len_raw: int = len(raw)
        index: int = 0
        msg_count: int = 0
        parse_mti: List[Dict[str, Any]] = []
        extract_iso = self._extract_iso_payload
        append_mti = parse_mti.append

        try:
            while index < self._len_raw:
                payload, consumed = extract_iso(
                    raw=raw, index=index, len_raw=self._len_raw
                )
                index += consumed

                message_parser: Dict[str, Any] = iso8583.parse(
                    message=payload, template=mastercard, encoding="cp500"
                )

                append_mti(message_parser)

                msg_count += 1

        except Exception as e:
            msg_error = f"Erro na mensagem #{msg_count + 1} (offset {index})"
            raise ISO8583ParseError(msg_error) from e

        return parse_mti, msg_count

    def _logging(self, file_name: str, row_count: int, data: TypeIpm) -> None:

        row_count_format: str = f"{row_count:,}".replace(",", ".")

        rows: List[str] = [
            f" ◉ 📄 File Name  {self._SIDE} {file_name}",
            f" ◉ 📄 File Date  {self._SIDE} {format_date(file_name=file_name)}",
            f" ◉ 📄 File Cycle {self._SIDE} {self._cycle}",
            f" ◉ 📄 File Size  {self._SIDE} {format_size(self._len_raw)}",
            f" ◉ 📄 File Row   {self._SIDE} {row_count_format}",
        ]

        body: str = f"    {self._PARTING}\n"

        for idx, row in enumerate(rows):
            space = format_space(text1=self._HEADER, text2=row)

            if not idx:
                body += (
                    f"    {self._HEADER_CONTOUR}"
                    f"    {self._SIDE_CONTOUR} {self._HEADER} {self._SIDE_CONTOUR}\n"
                    f"    {self._ROW_CUSTOM_INIT}{row + space}{self._ROW_CUSTOM_END}\n"
                )

            if idx:
                body += (
                    f"    {self._ROW_CUSTOM_INIT}{row + space}{self._ROW_CUSTOM_END}\n"
                )

        body += (
            f"    {self._SIDE_CONTOUR} {self._FOOTER} {self._SIDE_CONTOUR}\n"
            f"    {self._FOOTER_CONTOUR}"
        )

        self.logging_file(data=data, file_name=file_name, type_logg=["csv", "txt"])

        print(body)

        return None

    def search_ipm(self, file_date: str, cycle: TypeCycleIpm) -> None:

        self._file_date, self._cycle = file_date, cycle
        self._file_infos: Optional[TupleManagerFile] = file_search(
            file_date=file_date, cycle=cycle
        )

    def parse_ipm(
        self,
        logging: bool = True,
    ) -> TypeParseIpm:

        if self._file_infos:
            file_name, bytes_file = self._file_infos
            parse_ipm, msg_count = self._playload_ipm_file(raw=bytes_file)
            if logging:
                self._logging(file_name=file_name, row_count=msg_count, data=parse_ipm)

            return parse_ipm, file_name

        return None

    def parse_ipm_db(
        self,
        logging: bool = True,
    ) -> TypeParseIpmDb:

        if self._file_infos:
            file_name, bytes_file = self._file_infos
            parse_ipm, msg_count = self._playload_ipm_file(raw=bytes_file)
            if logging:
                self._logging(file_name=file_name, row_count=msg_count, data=parse_ipm)

            ipm_db: BeautifyIpmDb = BeautifyIpmDb(
                template=mastercard_db, elements=parse_ipm
            )

            parse_db: List[List[TypeIpmDb]] = ipm_db.parse()

            return parse_db, file_name

        return None


if __name__ == "__main__":
    master = MC8583()
    file = master.search_ipm(file_date="01/04/2026", cycle="CIC2")
    parse = master.parse_ipm()
    count = 0
    if parse:
        iso, name = parse
        for i in iso:
            if i["MTI"] == "1240":
                count += 1
        # print(count)
