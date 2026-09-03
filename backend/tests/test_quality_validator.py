"""
Tests for the AI Receipt Quality Validator.

Author: Pravin Shanmugavel
Project: ExpenseIQ

Pure image-processing logic - no database or API dependency, so
these run standalone regardless of the test database setup.

Sample images are generated fresh in a tmp dir per test session
rather than glob-scanned from `uploads/receipts/` - that directory is
the app's real runtime upload storage (local, gitignored), which
accumulates whatever anyone has actually uploaded through the running
app, including deliberately-bad images from manual quality-validator
testing. A test asserting "every real receipt passes" broke the first
time this suite ever ran to completion locally, because one such
deliberately-poorly-cropped manual-test upload was sitting in that
directory - a real bug in test hermeticity, not in the validator.
"""

import pytest
from PIL import Image
from PIL import ImageDraw
from PIL import ImageEnhance
from PIL import ImageFilter
from PIL import ImageFont

from app.ai.quality_validator import quality_validator


def _make_clean_receipt(path, variant=0):
    """
    Draws a plain, high-contrast, well-lit, correctly-framed
    receipt-like image - guaranteed to clear every quality heuristic
    (sharp text edges, bright background, well over the minimum
    dimension, a normal portrait aspect ratio) regardless of what's
    sitting in any local upload directory.

    Sized to match a realistic phone-camera photo (1200x1600), not
    just "big enough" for the MIN_DIMENSION_PX check: the sharpness
    heuristic's edge-detect filter leaves a thin, unfiltered border
    around the whole image, and that border's contribution to the
    variance calculation is proportional to perimeter/area - on a
    small canvas (e.g. 480x640) it dominates enough that even a
    genuinely blurred image never drops below the blur threshold, no
    matter how blurry. At a realistic resolution that border
    contribution is small enough for blur to behave the way the
    validator's own docstring describes.
    """

    width, height = 1200, 1600
    image = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    lines = [
        f"SAMPLE MERCHANT #{variant}",
        "TAX INVOICE",
        "",
        "1 x Item          Rs.100.00",
        "2 x Item          Rs.200.00",
        "",
        "Subtotal          Rs.300.00",
        "GST (18%)          Rs.54.00",
        "TOTAL             Rs.354.00",
        "",
        "THANK YOU",
    ]

    y = 60

    for line in lines:
        draw.text((70, y), line, fill="black", font=font)
        y += 60

    image.save(path)

    return str(path)


@pytest.fixture(scope="module")
def clean_receipts(tmp_path_factory):
    """
    A handful of independently-generated clean sample images, shared
    across this module's tests.
    """

    base_dir = tmp_path_factory.mktemp("clean_receipts")

    return [
        _make_clean_receipt(base_dir / f"receipt_{i}.jpg", variant=i)
        for i in range(5)
    ]


def test_real_receipts_pass_quality_check(clean_receipts):
    """
    Every genuine, clean receipt image should be accepted - this is
    the guard against an over-aggressive validator that would reject
    perfectly good photos.
    """

    for path in clean_receipts:

        result = quality_validator.assess(path)

        assert result.is_acceptable, (
            f"{path} unexpectedly failed quality check: "
            f"{result.issues} (score={result.score})"
        )


def test_blurry_image_is_flagged(clean_receipts, tmp_path):

    src = Image.open(clean_receipts[0])
    blurred = src.filter(ImageFilter.GaussianBlur(radius=6))

    blurry_path = tmp_path / "blurry.jpg"
    blurred.save(blurry_path)

    result = quality_validator.assess(str(blurry_path))

    assert not result.is_acceptable
    assert "blurry" in result.issues


def test_dark_image_is_flagged(clean_receipts, tmp_path):

    src = Image.open(clean_receipts[0])
    dark = ImageEnhance.Brightness(src).enhance(0.15)

    dark_path = tmp_path / "dark.jpg"
    dark.save(dark_path)

    result = quality_validator.assess(str(dark_path))

    assert not result.is_acceptable
    assert "low_light" in result.issues


def test_badly_cropped_image_is_flagged(clean_receipts, tmp_path):

    src = Image.open(clean_receipts[0])
    cropped = src.crop((0, 0, 60, 400))

    cropped_path = tmp_path / "cropped.jpg"
    cropped.save(cropped_path)

    result = quality_validator.assess(str(cropped_path))

    assert not result.is_acceptable
    assert "poorly_cropped" in result.issues


def test_unreadable_file_fails_gracefully(tmp_path):
    """
    A corrupt/non-image file should be reported as a quality
    failure, not raise an unhandled exception up through the
    pipeline.
    """

    bad_file = tmp_path / "not_an_image.jpg"
    bad_file.write_bytes(b"this is not a real image")

    result = quality_validator.assess(str(bad_file))

    assert result.is_acceptable is False
    assert result.score == 0.0
    assert "unreadable_file" in result.issues


def test_quality_score_is_bounded(clean_receipts):
    """
    The composite score must always stay within 0-100 regardless of
    how the three underlying heuristics combine.
    """

    for path in clean_receipts:
        result = quality_validator.assess(path)
        assert 0.0 <= result.score <= 100.0
