"""Core ASCII art conversion logic."""

import colorsys
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


def adjust_color(
    r: int, g: int, b: int, saturation: float = 1.0, brightness: float = 1.0
) -> tuple[int, int, int]:
    """Adjust the saturation and brightness of an RGB color.

    Args:
        r, g, b: RGB values (0-255).
        saturation: Saturation multiplier (1.0 = no change, >1.0 = more saturated).
        brightness: Brightness multiplier (1.0 = no change, >1.0 = brighter).

    Returns:
        Adjusted (r, g, b) tuple.
    """
    if saturation == 1.0 and brightness == 1.0:
        return (r, g, b)

    # Convert RGB to HSV
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)

    # Adjust saturation and brightness, clamp to [0, 1]
    s = min(s * saturation, 1.0)
    v = min(v * brightness, 1.0)

    # Convert back to RGB
    r_new, g_new, b_new = colorsys.hsv_to_rgb(h, s, v)
    return (int(r_new * 255), int(g_new * 255), int(b_new * 255))


def pixels_to_ascii(img: Image.Image, chars: str = DEFAULT_CHARS, invert: bool = False) -> str:
    """Map grayscale pixel values to ASCII characters.

    Args:
        img: A grayscale (mode 'L') image.
        chars: Character ramp from dark to light.
        invert: If True, invert the grayscale values (white becomes black, black becomes white).

    Returns:
        A single string of ASCII characters (no newlines).
    """
    pixels = list(img.get_flattened_data())
    if invert:
        pixels = [255 - pixel for pixel in pixels]
    divisor = 256 // len(chars)
    return "".join(chars[min(pixel // divisor, len(chars) - 1)] for pixel in pixels)


def image_to_ascii(
    path: str | Path,
    width: int = 120,
    chars: str = DEFAULT_CHARS,
    invert: bool = False,
) -> str:
    """Convert an image file to plain ASCII art.

    Args:
        path: Path to the image file.
        width: Output width in characters.
        chars: Character ramp from dark to light.
        invert: If True, invert the grayscale values.

    Returns:
        Multi-line ASCII art string.
    """
    img = load_image(path)
    img = resize_image(img, new_width=width)

    grayscale = img.convert("L")
    ascii_str = pixels_to_ascii(grayscale, chars, invert=invert)

    # Split into rows
    lines = [ascii_str[i : i + width] for i in range(0, len(ascii_str), width)]
    return "\n".join(lines)


def get_color_data(
    path: str | Path,
    width: int = 120,
    chars: str = DEFAULT_CHARS,
    saturation: float = 1.0,
    brightness: float = 1.0,
    invert: bool = False,
    rainbow: bool = False,
    gradient: list[tuple[int, int, int]] | None = None,
) -> list[list[tuple[str, tuple[int, int, int]]]]:
    """Convert an image to ASCII with per-character RGB color data.

    Args:
        path: Path to the image file.
        width: Output width in characters.
        chars: Character ramp from dark to light.
        saturation: Saturation multiplier (1.0 = no change, >1.0 = more vibrant).
        brightness: Brightness multiplier (1.0 = no change, >1.0 = brighter).
        invert: If True, invert the grayscale values for character mapping.
        rainbow: If True, apply rainbow gradient colors instead of original colors.
        gradient: If provided, apply custom gradient from top-left to bottom-right.
                 List of 2+ RGB tuples: [(r1,g1,b1), (r2,g2,b2), ...].
                 Colors are interpolated along the diagonal gradient path.

    Returns a list of rows, each row a list of (char, (r, g, b)) tuples.
    """
    img = load_image(path)
    img = resize_image(img, new_width=width)

    # Get RGB values from the resized image
    rgb_img = img.convert("RGB")
    rgb_pixels = list(rgb_img.get_flattened_data())

    # Invert RGB colors if requested
    if invert:
        rgb_pixels = [(255 - r, 255 - g, 255 - b) for r, g, b in rgb_pixels]

    # Get ASCII characters from grayscale
    grayscale = img.convert("L")
    ascii_str = pixels_to_ascii(grayscale, chars, invert=invert)

    # Pair each character with its color
    rows: list[list[tuple[str, tuple[int, int, int]]]] = []
    for y in range(rgb_img.height):
        row = []
        for x in range(rgb_img.width):
            idx = y * rgb_img.width + x
            char = ascii_str[idx] if idx < len(ascii_str) else " "
            color = rgb_pixels[idx] if idx < len(rgb_pixels) else (0, 0, 0)

            # Apply rainbow gradient if requested
            if rainbow:
                # Get grayscale value for saturation (shape definition)
                gray_val = grayscale.getpixel((x, y)) / 255.0
                # Create rainbow based on horizontal position
                hue = x / rgb_img.width
                # Use grayscale for saturation, keep brightness at maximum
                # Dark areas = less saturated (more white), bright areas = fully saturated
                r, g, b = colorsys.hsv_to_rgb(hue, gray_val, 1.0)
                color = (int(r * 255), int(g * 255), int(b * 255))

            # Apply custom gradient if requested
            elif gradient:
                # Get grayscale value for saturation (shape definition)
                gray_val = grayscale.getpixel((x, y)) / 255.0
                # Calculate diagonal position from top-left (0.0) to bottom-right (1.0)
                t = (x / rgb_img.width + y / rgb_img.height) / 2.0

                # Find which segment of the gradient we're in
                num_colors = len(gradient)
                if num_colors == 2:
                    # Simple two-color gradient
                    color1, color2 = gradient[0], gradient[1]
                    segment_t = t
                else:
                    # Multi-stop gradient: divide t into segments
                    segment_size = 1.0 / (num_colors - 1)
                    segment_index = min(int(t / segment_size), num_colors - 2)
                    color1 = gradient[segment_index]
                    color2 = gradient[segment_index + 1]
                    # Calculate position within this segment (0.0 to 1.0)
                    segment_t = (t - segment_index * segment_size) / segment_size

                # Interpolate between color1 and color2 within this segment
                r_grad = color1[0] + (color2[0] - color1[0]) * segment_t
                g_grad = color1[1] + (color2[1] - color1[1]) * segment_t
                b_grad = color1[2] + (color2[2] - color1[2]) * segment_t

                # Convert gradient color to HSV
                h, s, v = colorsys.rgb_to_hsv(r_grad / 255.0, g_grad / 255.0, b_grad / 255.0)
                # Modulate saturation and brightness by grayscale to preserve image structure
                # Use power curve to keep colors more vibrant in darker areas
                # gray_val^0.5 reduces desaturation effect (dark areas retain more color)
                saturation_factor = gray_val ** 0.5
                brightness_factor = 0.3 + (0.7 * gray_val)  # Darker areas = 30% brightness, bright areas = 100%
                s = min(s * saturation_factor, 1.0)
                v = brightness_factor
                # Convert back to RGB
                r, g, b = colorsys.hsv_to_rgb(h, s, v)
                color = (int(r * 255), int(g * 255), int(b * 255))

            # Apply color adjustments
            color = adjust_color(*color, saturation=saturation, brightness=brightness)
            row.append((char, color))
        rows.append(row)

    return rows
