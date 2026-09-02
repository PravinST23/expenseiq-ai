"""
Tests for the AI Receipt Quality Validator.

Author: Pravin Shanmugavel
Project: ExpenseIQ

Pure image-processing logic - no database or API dependency, so
these run standalone regardless of the test database setup.
"""

import glob
import os

import pytest
from PIL import Image
from PIL import ImageEnhance
from PIL import ImageFilter

from app.ai.quality_validator import quality_validator

RECEIPT_SAMPLES = glob.glob(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "uploads",
        "receipts",
        "*.jpg",
    )
)


@pytest.mark.skipif(
    not RECEIPT_SAMPLES,
    reason="No sample receipt images available in uploads/receipts/.",
)
def test_real_receipts_pass_quality_check():
    """
    Every genuine, clean receipt image already in the repo should be
    accepted - this is the guard against an over-aggressive
    validator that would reject perfectly good photos.
    """

    for path in RECEIPT_SAMPLES[:10]:

        result = quality_validator.assess(path)

        assert result.is_acceptable, (
            f"{path} unexpectedly failed quality check: "
            f"{result.issues} (score={result.score})"
        )


@pytest.mark.skipif(
    not RECEIPT_SAMPLES,
    reason="No sample receipt images available in uploads/receipts/.",
)
def test_blurry_image_is_flagged(tmp_path):

    src = Image.open(RECEIPT_SAMPLES[0])
    blurred = src.filter(ImageFilter.GaussianBlur(radius=6))

    blurry_path = tmp_path / "blurry.jpg"
    blurred.save(blurry_path)

    result = quality_validator.assess(str(blurry_path))

    assert not result.is_acceptable
    assert "blurry" in result.issues


@pytest.mark.skipif(
    not RECEIPT_SAMPLES,
    reason="No sample receipt images available in uploads/receipts/.",
)
def test_dark_image_is_flagged(tmp_path):

    src = Image.open(RECEIPT_SAMPLES[0])
    dark = ImageEnhance.Brightness(src).enhance(0.15)

    dark_path = tmp_path / "dark.jpg"
    dark.save(dark_path)

    result = quality_validator.assess(str(dark_path))

    assert not result.is_acceptable
    assert "low_light" in result.issues


@pytest.mark.skipif(
    not RECEIPT_SAMPLES,
    reason="No sample receipt images available in uploads/receipts/.",
)
def test_badly_cropped_image_is_flagged(tmp_path):

    src = Image.open(RECEIPT_SAMPLES[0])
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


def test_quality_score_is_bounded():
    """
    The composite score must always stay within 0-100 regardless of
    how the three underlying heuristics combine.
    """

    for path in RECEIPT_SAMPLES[:5]:
        result = quality_validator.assess(path)
        assert 0.0 <= result.score <= 100.0
