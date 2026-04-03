"""HTML output renderer for colored ASCII art."""

import html
from pathlib import Path
from typing import List, Tuple, Union


def render_html(
    rows: List[List[Tuple[str, Tuple[int, int, int]]]],
    title: str = "ASCII Art",
) -> str:
    """Render color data as a self-contained HTML document.

    Args:
        rows: Output from core.get_color_data().
        title: HTML page title.

    Returns:
        Complete HTML document as a string.
    """
    escaped_title = html.escape(title)

    lines = []
    for row in rows:
        chars = []
        for char, (r, g, b) in row:
            escaped = html.escape(char)
            chars.append(f'<span style="color:rgb({r},{g},{b})">{escaped}</span>')
        lines.append("".join(chars))

    body = "\n".join(lines)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escaped_title}</title>
    <style>
        body {{
            background: #000;
            display: flex;
            justify-content: center;
            padding: 20px;
        }}
        pre {{
            font-family: "Courier New", Courier, monospace;
            font-size: 8px;
            line-height: 1.0;
            letter-spacing: 0px;
        }}
    </style>
</head>
<body>
    <pre>{body}</pre>
</body>
</html>"""


def save_html(
    rows: List[List[Tuple[str, Tuple[int, int, int]]]],
    output_path: Union[str, Path],
    title: str = "ASCII Art",
) -> Path:
    """Render and save colored ASCII art as an HTML file.

    Returns the path to the saved file.
    """
    output_path = Path(output_path)
    output_path.write_text(render_html(rows, title=title), encoding="utf-8")
    return output_path
