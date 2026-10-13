import re
from typing import List
from app.services.parser_service import ExtractedPage
from app.schemas.chunk import ChunkData


class ChunkingService:
    TARGET_TOKEN_SIZE: int = 500
    TOKEN_OVERLAP: int = 50
    CHARS_PER_TOKEN: int = 4  # Common heuristic: 1 token ~ 4 characters

    @classmethod
    def estimate_tokens(cls, text: str) -> int:
        # Heuristic word/token estimation
        words = text.split()
        return max(1, int(len(words) * 1.3))

    @classmethod
    def chunk_pages(
        cls,
        pages: List[ExtractedPage],
        target_tokens: int = TARGET_TOKEN_SIZE,
        token_overlap: int = TOKEN_OVERLAP,
    ) -> List[ChunkData]:
        """
        Splits extracted pages into chunks while preserving 1-based page provenance.
        Chunks do not merge across different pages without preserving page labels.
        """
        chunks: List[ChunkData] = []
        global_chunk_index = 0

        target_chars = target_tokens * cls.CHARS_PER_TOKEN
        overlap_chars = token_overlap * cls.CHARS_PER_TOKEN

        for page in pages:
            text = page.text
            if not text:
                continue

            page_tokens = cls.estimate_tokens(text)

            # If page text fits comfortably in one chunk
            if page_tokens <= target_tokens:
                chunks.append(
                    ChunkData(
                        chunk_index=global_chunk_index,
                        page_number=page.page_number,
                        content=text,
                        token_count=page_tokens,
                    )
                )
                global_chunk_index += 1
            else:
                # Recursive sliding split within page boundary
                start = 0
                text_len = len(text)

                while start < text_len:
                    end = min(start + target_chars, text_len)
                    
                    # Try snapping to paragraph or sentence boundary
                    if end < text_len:
                        break_point = max(
                            text.rfind("\n\n", start, end),
                            text.rfind("\n", start, end),
                            text.rfind(". ", start, end),
                        )
                        if break_point > start + (target_chars // 2):
                            end = break_point + 1  # Include delimiter

                    sub_text = text[start:end].strip()
                    if sub_text:
                        chunks.append(
                            ChunkData(
                                chunk_index=global_chunk_index,
                                page_number=page.page_number,
                                content=sub_text,
                                token_count=cls.estimate_tokens(sub_text),
                            )
                        )
                        global_chunk_index += 1

                    if end >= text_len:
                        break
                    start = max(start + 1, end - overlap_chars)

        return chunks
