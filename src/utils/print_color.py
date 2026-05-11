from typing import List, Optional

from ..models import BG_COLORS_SEARCH, COLORS, FG_COLORS_SEARCH, HIGHLIGHT, HIGHLIGHTS


def print_custom_text(
    text: str,
    highlight: Optional[List[HIGHLIGHTS]] = None,
    color_foreground: Optional[COLORS] = None,
    color_background: Optional[COLORS] = None,
    sep: str = " ",
    end: str = "\n",
) -> None:

    reset: str = "\033[0m"
    hgl: str = "".join(HIGHLIGHT[hg] for hg in highlight) if highlight else ""
    color_fg: str = FG_COLORS_SEARCH[color_foreground] if color_foreground else ""
    color_bg: str = BG_COLORS_SEARCH[color_background] if color_background else ""

    print(f"{reset}{hgl}{color_fg}{color_bg}{text}{reset}", sep=sep, end=end)

    return None


if __name__ == "__main__":
    print_custom_text("HEITOR", highlight=["Bold"], color_background="Orange1")
