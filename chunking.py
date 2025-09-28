from pathlib import Path
import json
import re
import tiktoken
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

# ── parameters ───────────────────────────────────────────────────────────────
HEADERS_TO_SPLIT_ON = [("#", "section"), ("##", "clause"), ("###", "subclause")]
CHUNK_SIZE          = 300      # GPT tokens
CHUNK_OVERLAP       = 100
OUT_DIR_NAME        = "chunked123"
# ─────────────────────────────────────────────────────────────────────────────

# tokenizer
enc = tiktoken.get_encoding("cl100k_base")
def token_len(txt: str) -> int:
    return len(enc.encode(txt))


def parse_page_markers(text: str) -> list[dict]:
    """
    Split text into pages using --- Page N --- markers.
    Returns list of {page_number, content}.
    """
    pages = []
    pattern = re.compile(r"--- Page (\d+) ---")
    parts = pattern.split(text)

    # parts[0] is before the first marker (empty usually)
    for i in range(1, len(parts), 2):
        page_number = int(parts[i])
        page_text = parts[i+1].strip()
        pages.append({"page_number": page_number, "content": page_text})

    return pages


def chunk_markdown_files(folder: Path, out_subdir: str = OUT_DIR_NAME) -> None:
    out_dir = folder / out_subdir
    out_dir.mkdir(exist_ok=True)

    # heading splitter
    header_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=HEADERS_TO_SPLIT_ON)

    # token-aware splitter
    token_splitter = RecursiveCharacterTextSplitter(
        chunk_size      = CHUNK_SIZE,
        chunk_overlap   = CHUNK_OVERLAP,
        length_function = token_len,
        separators      = ["\n\n", "\n", ". ", " ", ""],
    )

    for md in sorted(folder.glob("*.md")):
        raw_markdown = md.read_text(encoding="utf-8")
        if not raw_markdown.strip():
            print(f"⚠ {md.name} is empty, skipping")
            continue

        # split by pages
        pages = parse_page_markers(raw_markdown)

        all_chunks = []
        last_header_context = {}  # Track headers across pages
        
        for page in pages:
            page_number = page["page_number"]
            page_text   = page["content"]

            # Clean OCR markers and table artifacts for better processing
            cleaned_text = re.sub(r'--- Page \d+ \(OCR\) ---', '', page_text)
            cleaned_text = re.sub(r'\|\s*\|\s*\|\s*\n\|\s*---\s*\|\s*---\s*\|', '', cleaned_text)
            cleaned_text = cleaned_text.strip()

            # 1) heading-aware split → list[Document]
            header_docs = header_splitter.split_text(cleaned_text)

            # 2) token-aware split on each Document's .page_content
            for doc in header_docs:
                # Build current header context
                current_headers = doc.metadata.copy()
                
                # If no headers found on this page, inherit from previous page
                if not current_headers and last_header_context:
                    current_headers = last_header_context.copy()
                
                # Update the persistent header context
                if current_headers:
                    last_header_context.update(current_headers)
                
                # Create header path
                header_path = " > ".join(f"{lvl}:{val}" for lvl, val in current_headers.items()) if current_headers else "document_content"
                
                splits = token_splitter.split_text(doc.page_content)

                for i, chunk in enumerate(splits, 1):
                    # Clean chunk content
                    clean_content = chunk.strip()
                    if not clean_content:
                        continue
                        
                    chunk_entry = {
                        "chunk_id": f"{md.stem}_p{page_number}_c{len(all_chunks)+1}",
                        "page_number": page_number,
                        "header_path": header_path,
                        "chunk_index": i,
                        "content": clean_content,
                        "token_count": token_len(clean_content),
                        "source_file": md.name,
                        "document_type": "legal_contract"
                    }
                    all_chunks.append(chunk_entry)

        # save all chunks from this file into JSON
        out_path = out_dir / f"{md.stem}_chunks.json"
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(all_chunks, f, indent=2, ensure_ascii=False)

        print(f"{md.name}: wrote {len(all_chunks)} chunks → {out_path}")


if __name__ == "__main__":
    # Look for markdown files in the outputs directory
    outputs_dir = Path("outputs")
    if outputs_dir.exists():
        print(f"Looking for markdown files in: {outputs_dir}")
        chunk_markdown_files(outputs_dir)
    else:
        print("outputs/ directory not found, looking in current directory")
        chunk_markdown_files(Path("."))