"""Tests for ascii_art core functionality."""

from pathlib import Path

import pytest
from PIL import Image

from ascii_art.core import (
    DEFAULT_CHARS,
    get_color_data,
    image_to_ascii,
    pixels_to_ascii,
    resize_image,
)


@pytest.fixture
def sample_image(tmp_path: Path) -> Path:
    """Create a small solid-color test image."""
    img = Image.new("RGB", (100, 100), color=(128, 64, 200))
    path = tmp_path / "test.png"
    img.save(path)
    return path


@pytest.fixture
def gradient_image(tmp_path: Path) -> Path:
    """Create a horizontal gradient test image (black → white)."""
    img = Image.new("RGB", (256, 10))
    for x in range(256):
        for y in range(10):
            img.putpixel((x, y), (x, x, x))
    path = tmp_path / "gradient.png"
    img.save(path)
    return path


class TestResizeImage:
    def test_preserves_target_width(self):
        img = Image.new("RGB", (400, 200))
        resized = resize_image(img, new_width=80)
        assert resized.width == 80

    def test_aspect_ratio_correction(self):
        img = Image.new("RGB", (400, 400))
        resized = resize_image(img, new_width=100)
        # Height should be ~55 due to 0.55 correction factor
        assert resized.height == 55


class TestPixelsToAscii:
    def test_output_length_matches_pixels(self):
        img = Image.new("L", (10, 10), color=128)
        result = pixels_to_ascii(img)
        assert len(result) == 100

    def test_dark_pixels_use_early_chars(self):
        img = Image.new("L", (1, 1), color=0)
        result = pixels_to_ascii(img, chars="AB")
        assert result == "A"

    def test_bright_pixels_use_late_chars(self):
        img = Image.new("L", (1, 1), color=255)
        result = pixels_to_ascii(img, chars="AB")
        assert result == "B"

    def test_custom_chars(self):
        img = Image.new("L", (1, 1), color=0)
        result = pixels_to_ascii(img, chars="XY")
        assert result == "X"


class TestImageToAscii:
    def test_returns_multiline_string(self, sample_image: Path):
        result = image_to_ascii(sample_image, width=40)
        lines = result.split("\n")
        assert len(lines) > 1
        assert all(len(line) == 40 for line in lines)

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            image_to_ascii("/nonexistent/image.png")

    def test_custom_width(self, sample_image: Path):
        for width in [20, 60, 150]:
            result = image_to_ascii(sample_image, width=width)
            first_line = result.split("\n")[0]
            assert len(first_line) == width


class TestGetColorData:
    def test_returns_rows_of_tuples(self, sample_image: Path):
        rows = get_color_data(sample_image, width=40)
        assert len(rows) > 0
        assert len(rows[0]) == 40

        char, color = rows[0][0]
        assert isinstance(char, str) and len(char) == 1
        assert len(color) == 3
        assert all(0 <= c <= 255 for c in color)

    def test_gradient_produces_varied_chars(self, gradient_image: Path):
        rows = get_color_data(gradient_image, width=80)
        # Flatten chars and check we get more than one unique character
        chars = {char for row in rows for char, _ in row}
        assert len(chars) > 1
