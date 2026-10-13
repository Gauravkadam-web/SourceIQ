from dataclasses import dataclass
from typing import List
import fitz  # PyMuPDF
from app.core.errors import ParsingError
from app.core.logging import logger


@dataclass
class ExtractedPage:
    page_number: int  # 1-based human readable page index
    text: str
    char_count: int


class ParserService:
    @staticmethod
    def extract_pages(file_path: str) -> List[ExtractedPage]:
        """
        Extracts page-by-page text from a digital PDF using PyMuPDF.
        Detects scanned/image-only PDFs and enforces 1-based page numbering.
        """
        try:
            doc = fitz.open(file_path)
        except Exception as e:
            logger.error(f"Failed to open PDF at {file_path}: {str(e)}")
            raise ParsingError(f"Corrupted or invalid PDF file: {str(e)}")

        if len(doc) == 0:
            doc.close()
            raise ParsingError("PDF contains zero pages.")

        pages: List[ExtractedPage] = []
        total_chars = 0

        for page_idx in range(len(doc)):
            page = doc[page_idx]
            # Extract plain text
            raw_text = page.get_text("text") or ""
            clean_text = raw_text.strip()
            char_count = len(clean_text)
            total_chars += char_count

            pages.append(
                ExtractedPage(
                    page_number=page_idx + 1,  # 1-based index
                    text=clean_text,
                    char_count=char_count,
                )
            )

        doc.close()

        # Scanned/empty PDF check: If entire document has fewer than 20 characters,
        # it is either an empty file or a scanned bitmap PDF without an OCR text layer.
        if total_chars < 20:
            raise ParsingError(
                "Scanned or image-only PDFs are not supported in the MVP. "
                "No selectable text layer was detected in this document."
            )

        return pages
