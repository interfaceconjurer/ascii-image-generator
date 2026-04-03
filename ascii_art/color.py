"""ANSI color output for terminal rendering."""

import os
import sys


def supports_truecolor() -> bool:
    """Detect whether the terminal supports 24-bit truecolor."""
    colorterm = os.environ.get("COLORTERM", "").lower()
    return colorterm in ("truecolor", "24bit")


def supports_256color() -> bool:
    """Detect whether the terminal supports 256 colors."""
    term = os.environ.get("TERM", "")
    return "256color" in term or supports_truecolor()


def detect_color_mode() -> str:
    """Auto-detect the best color mode for the current terminal.

    Returns:
        'truecolor', '256', or 'none'
    """
    if not sys.stdout.isatty():
        return "none"
    if supports_truecolor():
        return "truecolor"
    if supports_256color():
        return "256"
    return "none"


def rgb_to_ansi_truecolor(r: int, g: int, b: int) -> str:
    """Return ANSI escape code for 24-bit truecolor foreground."""
    return f"\033[38;2;{r};{g};{b}m"


def rgb_to_ansi_256(r: int, g: int, b: int) -> str:
    """Convert RGB to the nearest ANSI 256-color and return escape code.

    Uses the 6x6x6 color cube (indices 16-231).
    """
    r_idx = round(r / 255 * 5)
    g_idx = round(g / 255 * 5)
    b_idx = round(b / 255 * 5)
    color_index = 16 + 36 * r_idx + 6 * g_idx + b_idx
    return f"\033[38;5;{color_index}m"


RESET = "\033[0m"


def colorize_char(char: str, r: int, g: int, b: int, mode: str = "truecolor") -> str:
    """Wrap a character in ANSI color escape codes.

    Args:
        char: The ASCII character.
        r, g, b: RGB color values (0-255).
        mode: 'truecolor', '256', or 'none'.
    """
    if mode == "truecolor":
        return f"{rgb_to_ansi_truecolor(r, g, b)}{char}{RESET}"
    elif mode == "256":
        return f"{rgb_to_ansi_256(r, g, b)}{char}{RESET}"
    else:
        return char


def render_colored(
    rows: list[list[tuple[str, tuple[int, int, int]]]],
    mode: str | None = None,
) -> str:
    """Render color data as an ANSI-colored string.

    Args:
        rows: Output from core.get_color_data().
        mode: 'truecolor', '256', 'none', or None for auto-detect.

    Returns:
        Multi-line string with ANSI escape codes.
    """
    if mode is None:
        mode = detect_color_mode()

    lines = []
    for row in rows:
        line = "".join(colorize_char(char, *color, mode=mode) for char, color in row)
        lines.append(line)
    return "\n".join(lines)
