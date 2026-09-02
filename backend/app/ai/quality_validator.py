"""
AI Receipt Quality Validator

Author: Pravin Shanmugavel
Project: ExpenseIQ

Implements the approved proposal's pipeline step 2 ("AI Receipt
Quality Validator checks image (blur, crop, low light) -> prompts
re-upload if poor quality") and the Week 8 deliverable of the same
name.

Runs as the FIRST step of the pipeline, before any OCR/AI call - a
receipt that's too blurry, too dark, or too small/oddly cropped to
read reliably should be flagged before spending an OCR/Gemini/Ollama
call on it, and the employee should be told which specific problem to
fix (not just "processing failed").

No external CV library required - Tesseract/Gemini/Ollama already
cover the heavy lifting; this uses plain Pillow (already a project
dependency) for three independent, well-established heuristics:

  - Sharpness: edge-detect (Pillow's own edge-finding kernel) and
    measure the variance of the resulting pixel intensities - a flat,
    blurry image has almost no strong edges anywhere, so this
    variance stays low; a sharp image (even a busy, detailed one) has
    lots of strong edges, so it stays high. Same idea as the
    classic Laplacian-variance blur detector, without needing OpenCV.
  - Brightness: mean grayscale pixel value - a genuinely dark/low
    light photo averages low; a normally lit or white-background
    receipt does not.
  - Framing: minimum pixel dimensions and aspect ratio - catches
    receipts cropped down to an unreadable sliver or a near-blank
    corner of the original photo.
"""

from dataclasses import dataclass
from dataclasses import field

from PIL import Image
from PIL import ImageFilter
from PIL import ImageStat

SHARPNESS_VARIANCE_THRESHOLD = 200.0
BRIGHTNESS_THRESHOLD = 70.0
MIN_DIMENSION_PX = 200
MAX_ASPECT_RATIO = 4.0


@dataclass
class QualityResult:

    is_acceptable: bool
    score: float
    issues: list[str] = field(default_factory=list)
    reason: str = ""

    sharpness_variance: float = 0.0
    brightness_mean: float = 0.0
    width: int = 0
    height: int = 0


class ReceiptQualityValidator:
    """
    Pre-flight image quality check - blur, crop/framing, low light.
    """

    def assess(self, image_path: str) -> QualityResult:

        try:

            with Image.open(image_path) as img:

                img = img.convert("L")

                width, height = img.size

                edges = img.filter(ImageFilter.FIND_EDGES)
                sharpness_variance = ImageStat.Stat(edges).var[0]

                brightness_mean = ImageStat.Stat(img).mean[0]

        except Exception as ex:

            # An image Pillow can't even open is itself a quality
            # failure worth surfacing, not a hard pipeline crash -
            # OCR/AI steps downstream have their own try/except and
            # will fail gracefully too.
            return QualityResult(
                is_acceptable=False,
                score=0.0,
                issues=["unreadable_file"],
                reason=f"Could not read image file: {ex}",
            )

        issues: list[str] = []

        if sharpness_variance < SHARPNESS_VARIANCE_THRESHOLD:
            issues.append("blurry")

        if brightness_mean < BRIGHTNESS_THRESHOLD:
            issues.append("low_light")

        aspect_ratio = max(width, height) / max(min(width, height), 1)

        if (
            width < MIN_DIMENSION_PX
            or height < MIN_DIMENSION_PX
            or aspect_ratio > MAX_ASPECT_RATIO
        ):
            issues.append("poorly_cropped")

        # Composite 0-100 score - each heuristic contributes a third,
        # scaled against its own threshold so no single dimension
        # alone drags a genuinely fine receipt below the acceptance
        # line.
        sharpness_component = min(
            sharpness_variance / (SHARPNESS_VARIANCE_THRESHOLD * 2), 1.0
        )
        brightness_component = min(
            brightness_mean / (BRIGHTNESS_THRESHOLD * 2), 1.0
        )
        framing_component = (
            0.0
            if "poorly_cropped" in issues
            else 1.0
        )

        score = round(
            (
                sharpness_component
                + brightness_component
                + framing_component
            )
            / 3
            * 100,
            2,
        )

        is_acceptable = len(issues) == 0

        if is_acceptable:
            reason = "Image quality acceptable - clear, well lit, properly framed."
        else:
            labels = {
                "blurry": "appears blurry",
                "low_light": "was taken in low light",
                "poorly_cropped": "is cropped too tightly or has an unusual aspect ratio",
            }
            described = ", and ".join(labels[i] for i in issues)
            reason = (
                f"This receipt {described} - extraction accuracy may "
                "be reduced. Consider re-uploading a clearer photo."
            )

        return QualityResult(
            is_acceptable=is_acceptable,
            score=score,
            issues=issues,
            reason=reason,
            sharpness_variance=round(sharpness_variance, 2),
            brightness_mean=round(brightness_mean, 2),
            width=width,
            height=height,
        )


quality_validator = ReceiptQualityValidator()
