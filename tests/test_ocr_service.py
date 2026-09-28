import shutil
import pytest

from backend.services.ocr_service import _parse_amount, _parse_date, _parse_vendor


def test_parse_amount_prefers_grand_total_over_subtotal():
    text = "Subtotal: 725.00\nGrand Total: 750.50\n"
    assert _parse_amount(text) == 750.50


def test_parse_amount_ignores_sub_total_as_two_separate_words():
    """Regression test: 'Sub Total' (two words) previously slipped past
    the fused-'Subtotal' check and got picked as the final amount."""
    text = "Sub Total : 1111.00\nCGST: 26.78\nSGST: 26.78\nTotal : 1165\n"
    assert _parse_amount(text) == 1165.0


def test_parse_amount_ignores_leading_number_before_label_on_same_line():
    """Regression test: a bill-sequence number printed before the
    label on the same line ('6/17 Total : 1165') was previously
    grabbed instead of the real amount after the label."""
    assert _parse_amount("6/17 Total : 1165\n") == 1165.0


def test_parse_amount_falls_back_to_max_when_no_total_label():
    text = "Coffee 120.00\nSandwich 180.00\n"
    assert _parse_amount(text) == 180.00


def test_parse_date_slash_format():
    assert _parse_date("Date: 15/09/2026") == "2026-09-15"


def test_parse_date_month_name_format():
    assert _parse_date("15 Sep 2026") == "2026-09-15"


def test_parse_date_none_when_absent():
    assert _parse_date("no date anywhere in this text") is None


def test_parse_vendor_first_line():
    assert _parse_vendor("CAFE MOCHA\n123 Main St\n") == "CAFE MOCHA"


def test_confidence_high_for_labeled_total_low_for_fallback():
    """Regression test: _find_amount reports whether the amount came
    from a clearly labeled line ('high') vs. a best guess from the
    largest number on the receipt ('low')."""
    from backend.services.ocr_service import _find_amount

    amount, confident = _find_amount("Grand Total: 500.00\n")
    assert confident is True

    amount2, confident2 = _find_amount("Coffee 120.00\nSandwich 180.00\n")
    assert confident2 is False


@pytest.mark.skipif(shutil.which("tesseract") is None, reason="Tesseract not installed on this machine")
def test_real_ocr_smoke_test():
    """Only runs if Tesseract is actually installed - a genuine
    end-to-end OCR check rather than just testing the parsing regex."""
    import io
    from PIL import Image, ImageDraw
    from backend.services.ocr_service import extract_text

    img = Image.new("RGB", (300, 100), color="white")
    d = ImageDraw.Draw(img)
    d.text((10, 10), "TEST RECEIPT 123.45", fill="black")
    buf = io.BytesIO()
    img.save(buf, format="PNG")

    text = extract_text(buf.getvalue())
    assert "123" in text or "TEST" in text.upper()
