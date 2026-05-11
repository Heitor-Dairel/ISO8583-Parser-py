import csv
import json
from pathlib import Path
from typing import Final, List

from ..models import TypeIpm


class FilesDataSaving:
    def __init__(self) -> None:
        self._output_path_abs: Path = self._output_path()

    def _output_path(self) -> Path:

        BASE_DIR: Final[Path] = Path(__file__).parent.parent.parent
        DATA_DIR: Final[Path] = BASE_DIR / "output"
        DATA_DIR.mkdir(exist_ok=True)

        for item in DATA_DIR.iterdir():
            if item.is_file():
                item.unlink()

        return DATA_DIR

    def _save_csv(self, data: TypeIpm, headers: List[str], file_name: str) -> None:

        file_path = self._output_path_abs / f"{file_name}.csv"
        with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(
                f, fieldnames=headers, extrasaction="ignore", delimiter=";"
            )

            writer.writeheader()

            if headers:
                writer.writerows(data)

        return None

    def _save_txt(self, data: TypeIpm, file_name: str) -> None:

        with open(
            self._output_path_abs / f"{file_name}.txt.log", "w", encoding="utf-8"
        ) as arquivo:
            for i in data:
                json_dict = json.dumps(i, indent=4, ensure_ascii=False)
                arquivo.write(f"{json_dict}\n")

        return None


if __name__ == "__main__":
    teste = ""
