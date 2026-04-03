"""Core ASCII art conversion logic."""

from pathlib import Path

from PIL import Image

# Default character ramp: dark → light
DEFAULT_CHARS = "B S#&@$%*!:. "


def load_image(path: str | Path) -> Image.Image:
    """Load an image from disk."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")
    return Image.open(path)


def resize_image(img: Image.Image, new_width: int = 120) -> Image.Image:
    """Resize image while preserving aspect ratio.

    The 0.55 factor compensates for terminal characters being taller than wide.
    """
    width, height = img.size
    aspect_ratio = height / width
    new_height = int(aspect_ratio * new_width * 0.55)
    return img.resize((new_width, new_height))


def pixels_to_ascii(img: Image.Image, chars: str = DEFAULT_CHARS) -> str:
    """Map grayscale pixel values to ASCII characters.

    Args:
        img: A grayscale (mode 'L') image.
        chars: Character ramp from dark to light.

    Returns:
        A single string of ASCII characters (no newlines).
    """
    pixels = list(img.getdata())
    divisor = 256 // len(chars)
    return "".join(chars[min(pixel // divisor, len(chars) - 1)] for pixel in pixels)


def image_to_ascii(
    path: str | Path,
    width: int = 120,
    chars: str = DEFAULT_CHARS,
) -> str:
    """Convert an image file to plain ASCII art.

    Args:
        path: Path to the image file.
        width: Output width in characters.
        chars: Character ramp from dark to light.

    Returns:
        Multi-line ASCII art string.
    """
    img = load_image(path)
    img = resize_image(img, new_width=width)

    grayscale = img.convert("L")
    ascii_str = pixels_to_ascii(grayscale, chars)

    # Split into rows
    lines = [ascii_str[i : i + width] for i in range(0, len(ascii_str), width)]
    return "\n".join(lines)


def get_color_data(
    path: str | Path,
    width: int = 120,
    chars: str = DEFAULT_CHARS,
) -> list[list[tuple[str, tuple[int, int, int]]]]:
    """Convert an image to ASCII with per-character RGB color data.

    Returns a list of rows, each row a list of (char, (r, g, b)) tuples.
    """
    img = load_image(path)
    img = resize_image(img, new_width=width)

    # Get RGB values from the resized image
    rgb_img = img.convert("RGB")
    rgb_pixels = list(rgb_img.getdata())

    # Get ASCII characters from grayscale
    grayscale = img.convert("L")
    ascii_str = pixels_to_ascii(grayscale, chars)

    # Pair each character with its color
    rows: list[list[tuple[str, tuple[int, int, int]]]] = []
    for y in range(rgb_img.height):
        row = []
        for x in range(rgb_img.width):
            idx = y * rgb_img.width + x
            char = ascii_str[idx] if idx < len(ascii_str) else " "
            color = rgb_pixels[idx] if idx < len(rgb_pixels) else (0, 0, 0)
            row.append((char, color))
        rows.append(row)

    return rows
