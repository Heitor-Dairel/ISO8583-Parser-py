from datetime import datetime
from pathlib import Path
from typing import (
    Final,
    Generator,
    Iterator,
    Optional,
)

from ..models import TupleFileManager, TypeCycleIpm

_BASE_DIR: Final[Path] = Path(
    r"C:\Users\heitor.tavares\OneDrive - TRIVALE ADMINISTRACAO LTDA"
    r"\Operação Processadora - Arquivos CSU"
)
_FLAG_DIR: Final[str] = "(1)"


class DateInvalidFormat(ValueError): ...


def file_search(file_date: str, file_cycle: TypeCycleIpm) -> Optional[TupleFileManager]:

    _validate_date(date=file_date)

    file_date_format: str = datetime.strptime(file_date, "%d/%m/%Y").strftime("%d%m%Y")
    files: Iterator[Path] = _BASE_DIR.rglob(
        f"CSU_ACQ_MASTER_OUTGOING_{file_cycle}_{file_date_format}*.TXT"
    )

    file: Generator[TupleFileManager] = (
        TupleFileManager(file_name=arq.stem, file_bytes=_file_bytes(arq))
        for arq in files
        if _FLAG_DIR not in arq.parent.name
    )

    return next(file, None)


def _validate_date(date: str) -> None:

    FORMATO: Final[str] = "%d/%m/%Y"
    msg_error: str = f"Formato de data está inválido '{date}'"
    try:
        datetime.strptime(date, FORMATO)
    except ValueError as e:
        raise DateInvalidFormat(msg_error) from e


def _file_bytes(file_path: Path) -> memoryview:
    data_bytes: bytes = file_path.read_bytes()
    raw: memoryview = memoryview(data_bytes)

    return raw
