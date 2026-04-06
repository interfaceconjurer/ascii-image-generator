"""HTML output renderer for colored ASCII art."""

import html
from pathlib import Path


def render_html(
    rows: list[list[tuple[str, tuple[int, int, int]]]],
    title: str = "ASCII Art",
    pixel_width: int | None = None,
) -> str:
    """Render color data as a self-contained HTML document.

    Args:
        rows: Output from core.get_color_data().
        title: HTML page title.
        pixel_width: Desired width in pixels. If provided, calculates appropriate font-size.

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

    # Calculate font size based on desired pixel width
    if pixel_width and rows:
        char_count = len(rows[0])  # Width in characters
        # Monospace char width is roughly 0.6 × font-size
        font_size = pixel_width / (char_count * 0.6)
        font_size_css = f"{font_size:.2f}px"
    else:
        font_size_css = "8px"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escaped_title}</title>
    <style>
        body {{
            display: flex;
            justify-content: center;
            padding: 20px;
        }}
        pre {{
            font-family: "Courier New", Courier, monospace;
            font-size: {font_size_css};
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
    rows: list[list[tuple[str, tuple[int, int, int]]]],
    output_path: str | Path,
    title: str = "ASCII Art",
    pixel_width: int | None = None,
) -> Path:
    """Render and save colored ASCII art as an HTML file.

    Returns the path to the saved file.
    """
    output_path = Path(output_path)
    output_path.write_text(render_html(rows, title=title, pixel_width=pixel_width), encoding="utf-8")
    return output_path
