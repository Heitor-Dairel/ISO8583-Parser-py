from typing import Any, Dict, List, Optional, Tuple

from starkbank import iso8583

from ..helpers import FilesDataSaving, file_search
from ..models import (
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


class MastercardIso8583Parse(FilesDataSaving):
    def __init__(self) -> None:
        super().__init__()

        self._file_info: Optional[TupleManagerFile] = None

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

        len_raw: int = len(raw)
        index: int = 0
        msg_count: int = 0
        parse_mti: List[Dict[str, Any]] = []
        extract_iso = self._extract_iso_payload
        append_mti = parse_mti.append

        try:
            while index < len_raw:
                payload, consumed = extract_iso(raw=raw, index=index, len_raw=len_raw)
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

        separator: str = "=" * 63

        body: str = (
            f"{separator}\n"
            f" - FILE NAME: {file_name}\n"
            f" - ROW COUNT: {row_count}\n"
            f"{separator}\n"
        )

        self._save_txt(data=data, file_name=file_name)

        print_custom_text(text=body, highlight=["Bold"], color_foreground="OrangeRed1")

        return None

    def search_ipm(self, date_file: str, cycle: TypeCycleIpm) -> None:

        self._file_infos: Optional[TupleManagerFile] = file_search(
            file_date=date_file, cycle=cycle
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
    master = MastercardIso8583Parse()
    file = master.search_ipm(date_file="01/04/2026", cycle="CIC2")
    parse = master.parse_ipm()
    count = 0
    if parse:
        iso, name = parse
        for i in iso:
            if i["MTI"] == "1240":
                count += 1
        print(count)
