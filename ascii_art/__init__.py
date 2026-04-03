"""ascii_art — Generate ASCII art from images.

Usage:
    from ascii_art import image_to_ascii, get_color_data

    # Plain text ASCII art
    art = image_to_ascii("photo.jpg", width=100)

    # With color data for custom rendering
    rows = get_color_data("photo.jpg", width=100)
"""

from .core import DEFAULT_CHARS, get_color_data, image_to_ascii

__all__ = ["image_to_ascii", "get_color_data", "DEFAULT_CHARS"]
__version__ = "0.1.0"
