"""Command-line interface for ascii-art."""

import argparse
import sys
from pathlib import Path

from .color import render_colored
from .core import DEFAULT_CHARS, get_color_data, image_to_ascii
from .html_output import save_html
from .svg_output import save_svg


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ascii-art",
        description="Generate ASCII art from images.",
    )
    parser.add_argument("image", type=Path, help="Path to the input image")
    parser.add_argument(
        "-w", "--width", type=int, default=120, help="Output width in characters (default: %(default)s)"
    )
    parser.add_argument(
        "-c",
        "--chars",
        type=str,
        default=DEFAULT_CHARS,
        help='Character ramp from dark to light (default: "B S#&@$%%*!:. ")',
    )
    parser.add_argument(
        "-m",
        "--mode",
        choices=["plain", "color", "html", "svg"],
        default="color",
        help="Output mode (default: color)",
    )
    parser.add_argument(
        "--color-mode",
        choices=["auto", "truecolor", "256", "none"],
        default="auto",
        help="Terminal color mode (default: auto-detect)",
    )
    parser.add_argument(
        "-s",
        "--saturation",
        type=float,
        default=1.0,
        help="Saturation multiplier for color modes (default: 1.0, try 1.5-2.0 for more vibrant)",
    )
    parser.add_argument(
        "-b",
        "--brightness",
        type=float,
        default=1.0,
        help="Brightness multiplier for color modes (default: 1.0, try 1.2-1.5 for brighter)",
    )
    parser.add_argument(
        "--pixel-width",
        type=int,
        default=None,
        help="Output width in pixels for HTML mode (calculates font-size automatically)",
    )
    parser.add_argument(
        "--invert",
        action="store_true",
        help="Invert the image colors (black becomes white, white becomes black)",
    )
    parser.add_argument(
        "--rainbow",
        action="store_true",
        help="Apply rainbow gradient colors instead of original image colors",
    )
    parser.add_argument(
        "--gradient",
        type=str,
        default=None,
        help="Apply custom gradient from top-left to bottom-right with 2+ colors (e.g., '#FF0000,#0000FF' or '#3D1A4D,#9B59B6,#FFD700,#B8860B')",
    )
    parser.add_argument(
        "-o", "--output", type=Path, default=None, help="Save output to file instead of stdout"
    )
    return parser


def parse_gradient(gradient_str: str) -> list[tuple[int, int, int]] | None:
    """Parse a gradient string like '#FF0000,#0000FF' or '#3D1A4D,#9B59B6,#FFD700' into a list of RGB tuples."""
    if not gradient_str:
        return None

    parts = gradient_str.split(',')
    if len(parts) < 2:
        raise ValueError(f"Gradient must have at least 2 colors separated by commas (e.g., '#FF0000,#0000FF'), got {len(parts)} part(s)")

    def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
        hex_color = hex_color.strip().lstrip('#')
        if len(hex_color) != 6:
            raise ValueError(f"Invalid hex color '#{hex_color}' - must be 6 characters")
        try:
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except ValueError:
            raise ValueError(f"Invalid hex color '#{hex_color}' - must contain only hex digits (0-9, A-F)")

    return [hex_to_rgb(part) for part in parts]


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.image.exists():
        print(f"Error: file not found: {args.image}", file=sys.stderr)
        return 1

    # Parse and validate gradient parameter
    gradient_colors = None
    if args.gradient:
        try:
            gradient_colors = parse_gradient(args.gradient)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    if args.mode == "plain":
        result = image_to_ascii(args.image, width=args.width, chars=args.chars, invert=args.invert)
        if args.output:
            args.output.write_text(result, encoding="utf-8")
            print(f"Saved to {args.output}")
        else:
            print(result)

    elif args.mode == "color":
        rows = get_color_data(
            args.image,
            width=args.width,
            chars=args.chars,
            saturation=args.saturation,
            brightness=args.brightness,
            invert=args.invert,
            rainbow=args.rainbow,
            gradient=gradient_colors,
        )
        color_mode = None if args.color_mode == "auto" else args.color_mode
        result = render_colored(rows, mode=color_mode)
        if args.output:
            args.output.write_text(result, encoding="utf-8")
            print(f"Saved to {args.output}")
        else:
            print(result)

    elif args.mode == "html":
        rows = get_color_data(
            args.image,
            width=args.width,
            chars=args.chars,
            saturation=args.saturation,
            brightness=args.brightness,
            invert=args.invert,
            rainbow=args.rainbow,
            gradient=gradient_colors,
        )
        output_path = args.output or Path("ascii_art.html")
        save_html(rows, output_path, title=args.image.stem, pixel_width=args.pixel_width)
        print(f"Saved HTML to {output_path}")

    elif args.mode == "svg":
        rows = get_color_data(
            args.image,
            width=args.width,
            chars=args.chars,
            saturation=args.saturation,
            brightness=args.brightness,
            invert=args.invert,
            rainbow=args.rainbow,
            gradient=gradient_colors,
        )
        output_path = args.output or Path("ascii_art.svg")
        # Calculate char dimensions based on pixel width if provided
        if args.pixel_width and rows:
            char_count = len(rows[0])
            char_width = args.pixel_width / char_count
            char_height = char_width * 1.6  # Maintain aspect ratio
        else:
            char_width = 10.0
            char_height = 16.0
        save_svg(rows, output_path, title=args.image.stem, char_width=char_width, char_height=char_height)
        print(f"Saved SVG to {output_path}")

    return 0
