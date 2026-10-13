import fitz  # PyMuPDF
import pytest
from app.core.errors import ParsingError
from app.services.parser_service import ParserService


def create_synthetic_pdf(tmp_path, filename: str, pages_text: list[str]) -> str:
    """Helper to generate a real digital PDF using PyMuPDF."""
    doc = fitz.open()
    for text in pages_text:
        page = doc.new_page()
        if text:
            # Insert text at top of page
            page.insert_text((50, 72), text, fontsize=11)
    file_path = str(tmp_path / filename)
    doc.save(file_path)
    doc.close()
    return file_path


def test_parser_extracts_digital_pdf_with_page_provenance(tmp_path):
    pages_text = [
        "First page content with important revenue and financial metrics for 2024.",
        "Second page detailing operations, expansion strategies, and key customer acquisitions.",
    ]
    pdf_path = create_synthetic_pdf(tmp_path, "sample.pdf", pages_text)

    extracted = ParserService.extract_pages(pdf_path)

    assert len(extracted) == 2
    assert extracted[0].page_number == 1
    assert "revenue and financial metrics" in extracted[0].text
    assert extracted[1].page_number == 2
    assert "expansion strategies" in extracted[1].text


def test_parser_rejects_empty_or_scanned_pdf(tmp_path):
    # PDF with zero text (simulating image-only/scanned document)
    pdf_path = create_synthetic_pdf(tmp_path, "scanned.pdf", ["", "   "])

    with pytest.raises(ParsingError) as exc_info:
        ParserService.extract_pages(pdf_path)

    assert "Scanned or image-only PDFs are not supported in the MVP" in str(exc_info.value)


def test_parser_rejects_corrupted_file(tmp_path):
    bad_file = tmp_path / "corrupted.pdf"
    bad_file.write_bytes(b"%PDF-1.4\nCorrupted content without valid xref table")

    with pytest.raises(ParsingError) as exc_info:
        ParserService.extract_pages(str(bad_file))

    assert "Corrupted or invalid PDF file" in str(exc_info.value)
