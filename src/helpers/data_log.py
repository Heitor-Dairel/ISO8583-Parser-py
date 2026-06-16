import copy
import json
from pathlib import Path
from typing import Any, Dict, Final, List, Literal, Optional

import polars as pl
from polars import DataFrame

from ..models import TypeIpm


class DataLogging:
    def __init__(self) -> None:
        self._output_path_abs: Path = self._output_path()
        return None

    def logging_file(
        self, data: TypeIpm, file_name: str, type_logg: List[Literal["csv", "txt"]]
    ) -> None:

        if "csv" in type_logg:
            self._logging_csv(data=data, file_name=file_name)

        if "txt" in type_logg:
            self._logging_txt(data=data, file_name=file_name)

        return None

    def _output_path(self) -> Path:

        BASE_DIR: Final[Path] = Path(__file__).parent.parent.parent
        DATA_DIR: Final[Path] = BASE_DIR / "output"
        DATA_DIR.mkdir(exist_ok=True)

        for item in DATA_DIR.iterdir():
            if item.is_file():
                item.unlink()

        return DATA_DIR

    def _key_delete(self, data: Dict[str, Any], *args: str) -> Dict[str, Any]:
        data_copy: Dict[str, Any] = copy.deepcopy(data)
        for i in args:
            data_copy.pop(i)
        return data_copy

    def _logging_csv(self, data: TypeIpm, file_name: str) -> None:
        data_csv: TypeIpm = [
            self._key_delete(i, "BMP", "DE001", "Length")
            for i in data
            if i["MTI"] == "1240"
        ]

        df: DataFrame = pl.DataFrame(data=data_csv).unnest("PDS")
        df = df.with_row_index("ID", offset=1)
        df.write_csv(
            self._output_path_abs / f"{file_name}.CSV",
            separator=";",
            decimal_comma=True,
        )

        return None

    def _logging_txt(self, data: TypeIpm, file_name: str) -> None:

        json_dict: Optional[str] = None
        with open(
            self._output_path_abs / f"{file_name}.TXT.LOG", "w", encoding="utf-8"
        ) as arquivo:
            for i in data:
                json_dict = json.dumps(i, indent=4, ensure_ascii=False)
                arquivo.write(f"{json_dict}\n")

        return None
