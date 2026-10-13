from app.services.parser_service import ExtractedPage
from app.services.chunking_service import ChunkingService


def test_chunking_preserves_single_page_within_target_size():
    pages = [
        ExtractedPage(page_number=1, text="Simple short document content for testing.", char_count=42),
    ]

    chunks = ChunkingService.chunk_pages(pages, target_tokens=500)

    assert len(chunks) == 1
    assert chunks[0].chunk_index == 0
    assert chunks[0].page_number == 1
    assert chunks[0].content == "Simple short document content for testing."
    assert chunks[0].token_count > 0


def test_chunking_preserves_page_numbers_across_multiple_pages():
    pages = [
        ExtractedPage(page_number=1, text="Page 1 discussion on Q1 financial results.", char_count=42),
        ExtractedPage(page_number=2, text="Page 2 discussion on Q2 marketing strategy.", char_count=43),
        ExtractedPage(page_number=3, text="Page 3 discussion on Q3 product engineering.", char_count=44),
    ]

    chunks = ChunkingService.chunk_pages(pages, target_tokens=500)

    assert len(chunks) == 3
    assert [c.page_number for c in chunks] == [1, 2, 3]
    assert [c.chunk_index for c in chunks] == [0, 1, 2]
    assert "Q1" in chunks[0].content
    assert "Q2" in chunks[1].content
    assert "Q3" in chunks[2].content


def test_chunking_splits_large_page_with_sliding_overlap():
    # Construct a long text (~300 words, ~1500 chars) with sentences
    sentences = [f"This is sentence number {i} discussing domain evidence and facts." for i in range(1, 40)]
    long_text = " ".join(sentences)

    page = ExtractedPage(page_number=1, text=long_text, char_count=len(long_text))

    # Chunk with small target (e.g. 50 tokens ~ 200 chars) to trigger splitting
    chunks = ChunkingService.chunk_pages([page], target_tokens=50, token_overlap=10)

    assert len(chunks) > 1
    # Verify strict monotonic indexing
    for idx, c in enumerate(chunks):
        assert c.chunk_index == idx
        assert c.page_number == 1
        assert len(c.content) > 0
