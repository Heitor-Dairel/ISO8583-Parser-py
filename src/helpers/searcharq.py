from datetime import datetime
from pathlib import Path
from typing import (
    Final,
    Generator,
    Iterator,
    Optional,
)

from ..models import TupleManagerFile, TypeCycleIpm

_BASE_DIR: Final[Path] = Path(
    r"C:\Users\heitor.tavares\OneDrive - TRIVALE ADMINISTRACAO LTDA"
    r"\Operação Processadora - Arquivos CSU"
)
_FLAG_DIR: Final[str] = "(1)"


class DateInvalidFormat(ValueError): ...


def file_search(file_date: str, cycle: TypeCycleIpm) -> Optional[TupleManagerFile]:

    _validate_date(date=file_date)

    file_date_format: str = datetime.strptime(file_date, "%d/%m/%Y").strftime("%d%m%Y")
    files: Iterator[Path] = _BASE_DIR.rglob(
        f"CSU_ACQ_MASTER_OUTGOING_{cycle}_{file_date_format}*.TXT"
    )

    file: Generator[TupleManagerFile] = (
        TupleManagerFile(file_name=arq.stem, bytes_file=_file_bytes(arq))
        for arq in files
        if _FLAG_DIR not in arq.parent.name
    )

    return next(file, None)


def _validate_date(date: str) -> None:

    formato: str = "%d/%m/%Y"
    msg: str = f"Formato de data está inválido '{date}'"
    try:
        datetime.strptime(date, formato)
    except ValueError as e:
        raise DateInvalidFormat(msg) from e


def _file_bytes(file_path: Path) -> memoryview:
    data_bytes: bytes = file_path.read_bytes()
    raw: memoryview = memoryview(data_bytes)

    return raw
