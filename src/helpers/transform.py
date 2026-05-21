from datetime import datetime
from typing import List


def format_size(size_bytes: int) -> str:
    if size_bytes >= 1024**2:
        return f"{size_bytes / (1024**2):.2f} MB"
    if size_bytes >= 1024:
        return f"{size_bytes / 1024:.2f} KB"
    return f"{size_bytes} Bytes"


def format_date(file_name: str) -> str:

    file_split: List[str] = file_name.split("_")

    date_time: str = f"{file_split[-2]}{file_split[-1]}"

    return datetime.strptime(date_time, "%d%m%Y%H%M%S").strftime("%d/%m/%Y %H:%M:%S")


def format_space(text1: str, text2: str) -> str:

    return " " * (len(text1) - len(text2) + 7)
