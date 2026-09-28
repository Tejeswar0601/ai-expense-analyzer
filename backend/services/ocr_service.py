"""
OCR receipt parsing: extracts raw text from an uploaded receipt image
via Tesseract OCR, then applies simple heuristics to guess the amount,
date, and vendor name.

These are SUGGESTIONS ONLY. The frontend always shows the raw
extracted text alongside the guesses, and never auto-submits an
expense - the person reviews and edits before saving, same as the ML
category suggestion in Phase 18.
"""

import io
import os
import re
from datetime import date
from typing import Optional

import numpy as np
from PIL import Image, ImageOps
import pytesseract
from dotenv import load_dotenv

load_dotenv()

_TESSERACT_CMD = os.getenv("TESSERACT_CMD")
if _TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = _TESSERACT_CMD

OCR_TARGET_MAX_DIMENSION = 1800


def _resize_if_small(grayscale: Image.Image) -> Image.Image:
    if max(grayscale.size) < OCR_TARGET_MAX_DIMENSION:
        scale = OCR_TARGET_MAX_DIMENSION / max(grayscale.size)
        new_size = (int(grayscale.width * scale), int(grayscale.height * scale))
        return grayscale.resize(new_size, Image.LANCZOS)
    return grayscale


def _preprocess_for_ocr(image: Image.Image) -> Image.Image:
    grayscale = _resize_if_small(image.convert("L"))
    return ImageOps.autocontrast(grayscale)


def _otsu_threshold(arr: np.ndarray) -> int:
    """Otsu's method via numpy (no extra dependency): finds the
    brightness cutoff that best separates text from background by
    maximizing the variance between the two classes."""
    histogram, _ = np.histogram(arr, bins=256, range=(0, 256))
    total = arr.size
    sum_total = np.dot(np.arange(256), histogram)

    sum_bg, weight_bg, best_variance, best_threshold = 0.0, 0.0, 0.0, 0
    for t in range(256):
        weight_bg += histogram[t]
        if weight_bg == 0:
            continue
        weight_fg = total - weight_bg
        if weight_fg == 0:
            break
        sum_bg += t * histogram[t]
        mean_bg = sum_bg / weight_bg
        mean_fg = (sum_total - sum_bg) / weight_fg
        variance = weight_bg * weight_fg * (mean_bg - mean_fg) ** 2
        if variance > best_variance:
            best_variance, best_threshold = variance, t
    return best_threshold


def _binarize_for_ocr(image: Image.Image) -> Image.Image:
    """Pure black/white via Otsu's threshold - often reads better than
    plain grayscale on receipts with uneven lighting or faded thermal
    ink. Used as a second-pass fallback when the first pass isn't
    confident."""
    grayscale = _resize_if_small(image.convert("L"))
    arr = np.array(grayscale)
    threshold = _otsu_threshold(arr)
    binary_arr = np.where(arr > threshold, 255, 0).astype(np.uint8)
    return Image.fromarray(binary_arr)


class OCRError(Exception):
    """Raised when OCR can't run at all (bad image, Tesseract missing, etc.)."""
    pass


AMOUNT_PATTERN_STRICT = re.compile(r"(?:rs\.?|inr|₹)?\s?([\d,]{1,7}\.\d{2})", re.IGNORECASE)
AMOUNT_PATTERN_LOOSE = re.compile(r"(?:rs\.?|inr|₹)?\s?([\d,]{1,7}(?:\.\d{1,2})?)", re.IGNORECASE)

# Tiered by how unambiguous the label is - "grand total" essentially
# never refers to anything but the final payable amount, whereas a
# bare "total" can also appear in "Total Qty" / "Total Items" rows.
TOTAL_KEYWORD_TIERS = [
    [re.compile(r"grand\s*total", re.IGNORECASE)],
    [re.compile(r"(total\s*amount|amount\s*due|amount\s*payable|net\s*amount|net\s*payable|bill\s*amount)", re.IGNORECASE)],
    [re.compile(r"\btotal\b", re.IGNORECASE)],
]
QTY_LINE_PATTERN = re.compile(r"\b(qty|quantity|items?)\b", re.IGNORECASE)
# "Sub Total" is two separate words, so a plain \btotal\b boundary
# check does NOT exclude it (only fused "Subtotal" was excluded
# before) - explicitly rule it out wherever the ambiguous bare-"total"
# tier is used, so it never gets mistaken for the real payable amount.
SUBTOTAL_EXCLUDE_PATTERN = re.compile(r"sub[\s-]*total", re.IGNORECASE)

# A receipt total north of this is almost certainly a misread ID
# (phone/GSTIN/bill number), not a real amount - guards the loose,
# no-decimal-required match from grabbing the wrong kind of number.
MAX_PLAUSIBLE_AMOUNT = 500_000


def _normalize_ocr_digit_confusion(text: str) -> str:
    """Fixes the most common OCR letter/digit mixups (O<->0, l/I<->1,
    S<->5, B<->8), but ONLY inside tokens where every letter present is
    one of those known confusable ones AND the token already has at
    least one real digit - so genuine words are never touched, while
    something like "25O.OO" still correctly becomes "250.00"."""
    CONFUSABLE_LETTERS = set("OolISB")

    def fix_token(match: re.Match) -> str:
        token = match.group(0)
        letters = [c for c in token if c.isalpha()]
        has_digit = any(c.isdigit() for c in token)

        if not letters or not has_digit:
            return token  # nothing to fix, or no digit to anchor on
        if not all(c in CONFUSABLE_LETTERS for c in letters):
            return token  # contains a real letter - likely an actual word

        return (
            token.replace("O", "0").replace("o", "0")
            .replace("l", "1").replace("I", "1")
            .replace("S", "5").replace("B", "8")
        )

    # Tokens made of digits/letters/./, glued together with NO spaces -
    # deliberately excludes whitespace so a match can never bridge from
    # a real number into an unrelated adjacent word.
    return re.sub(r"[\dOolISB,.]{3,}", fix_token, text)


def _extract_amount_from_line(line: str, loose: bool = False) -> Optional[float]:
    pattern = AMOUNT_PATTERN_LOOSE if loose else AMOUNT_PATTERN_STRICT
    match = pattern.search(line)
    if not match:
        return None
    raw = match.group(1).replace(",", "")
    try:
        value = float(raw)
    except ValueError:
        return None
    return value if value <= MAX_PLAUSIBLE_AMOUNT else None


def _find_amount(text: str) -> tuple:
    """Returns (amount, confident). confident=True means it came from
    a clearly labeled total line; False means it's a best-guess from
    the largest number on the receipt (or nothing was found)."""
    text = _normalize_ocr_digit_confusion(text)
    lines = text.splitlines()
    last_tier_index = len(TOTAL_KEYWORD_TIERS) - 1

    for tier_index, tier_patterns in enumerate(TOTAL_KEYWORD_TIERS):
        is_ambiguous_tier = tier_index == last_tier_index
        line_indices = range(len(lines) - 1, -1, -1) if is_ambiguous_tier else range(len(lines))

        for i in line_indices:
            line = lines[i]
            if QTY_LINE_PATTERN.search(line):
                continue
            if is_ambiguous_tier and SUBTOTAL_EXCLUDE_PATTERN.search(line):
                continue

            keyword_match = None
            for pattern in tier_patterns:
                m = pattern.search(line)
                if m:
                    keyword_match = m
                    break
            if keyword_match is None:
                continue

            amount = _extract_amount_from_line(line[keyword_match.end():], loose=True)
            if amount is not None:
                return amount, True

            for j in range(i + 1, min(i + 3, len(lines))):
                if lines[j].strip():
                    amount = _extract_amount_from_line(lines[j], loose=True)
                    if amount is not None:
                        return amount, True
                    break

    candidates = []
    for line in lines:
        if QTY_LINE_PATTERN.search(line):
            continue
        amount = _extract_amount_from_line(line, loose=False)
        if amount is not None:
            candidates.append(amount)
    return (max(candidates), False) if candidates else (None, False)


def _parse_amount(text: str) -> Optional[float]:
    """Backward-compatible: just the amount, no confidence info."""
    return _find_amount(text)[0]

MONTH_MAP = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

DATE_PATTERNS = [
    (re.compile(r"(\d{4})-(\d{2})-(\d{2})"), "ymd"),
    (re.compile(r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})"), "dmy_slash"),
    (re.compile(r"(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4})", re.IGNORECASE), "dmony"),
]


def extract_text(image_bytes: bytes, binarize: bool = False) -> str:
    try:
        image = Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        raise OCRError(f"Could not read the image file: {e}")

    try:
        processed = _binarize_for_ocr(image) if binarize else _preprocess_for_ocr(image)
        return pytesseract.image_to_string(processed, config="--psm 6")
    except pytesseract.pytesseract.TesseractNotFoundError:
        raise OCRError(
            "Tesseract OCR is not installed (or not found) on this server. "
            "See the setup instructions to install it and set TESSERACT_CMD in .env."
        )
    except Exception as e:
        raise OCRError(f"OCR failed: {e}")


def _parse_date(text: str) -> Optional[str]:
    for pattern, fmt in DATE_PATTERNS:
        match = pattern.search(text)
        if not match:
            continue
        try:
            if fmt == "ymd":
                y, m, d = match.groups()
                return date(int(y), int(m), int(d)).isoformat()
            elif fmt == "dmy_slash":
                d, m, y = match.groups()
                return date(int(y), int(m), int(d)).isoformat()
            elif fmt == "dmony":
                d, mon, y = match.groups()
                month_num = MONTH_MAP.get(mon.lower()[:3])
                if month_num:
                    return date(int(y), month_num, int(d)).isoformat()
        except ValueError:
            continue  # invalid date (e.g. day 32) - try the next pattern
    return None


def _parse_vendor(text: str) -> Optional[str]:
    """Naive heuristic: receipts typically print the store name as the
    first non-trivial line."""
    for line in text.splitlines():
        cleaned = line.strip()
        if len(cleaned) >= 3 and not cleaned.replace(" ", "").isdigit():
            return cleaned[:100]
    return None


def parse_receipt(image_bytes: bytes) -> dict:
    raw_text = extract_text(image_bytes, binarize=False)

    if not raw_text.strip():
        # Primary pass found nothing at all - try binarized before giving up.
        raw_text = extract_text(image_bytes, binarize=True)
        if not raw_text.strip():
            return {
                "available": False,
                "message": "Could not read any text from this image. Try a clearer photo.",
                "raw_text": "",
            }

    amount, confident = _find_amount(raw_text)

    # If the primary pass didn't confidently find a labeled total line,
    # try a second OCR pass on a binarized (pure black/white) version -
    # this often reads faded or unevenly-lit receipts better, and we
    # use it if it gets a confident read the first pass missed.
    if not confident:
        try:
            raw_text_bin = extract_text(image_bytes, binarize=True)
        except OCRError:
            raw_text_bin = ""
        if raw_text_bin.strip():
            amount_bin, confident_bin = _find_amount(raw_text_bin)
            if confident_bin:
                raw_text, amount, confident = raw_text_bin, amount_bin, True
            elif amount_bin is not None and (amount is None or amount_bin > amount):
                # Neither pass found a labeled total, but prefer the
                # larger unlabeled guess - receipts' real totals are
                # almost always the largest legitimate figure printed.
                raw_text, amount = raw_text_bin, amount_bin

    return {
        "available": True,
        "raw_text": raw_text.strip(),
        "suggested_amount": amount,
        "amount_confidence": "high" if confident else "low",
        "suggested_date": _parse_date(raw_text),
        "suggested_note": _parse_vendor(raw_text),
    }
