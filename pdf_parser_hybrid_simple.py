#!/usr/bin/env python3
"""
Hybrid PDF Parser: pdfplumber + PyMuPDF + PyTesseract
- Uses pdfplumber for text extraction and table extraction
- Uses PyMuPDF to detect images on textless pages
- Uses PyTesseract for OCR when pdfplumber fails
"""

import pdfplumber
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Any
import json
import os

import re


def normalize_text(text: str) -> str:
    if not text:
        return ""
    # unify line endings
    text = text.replace("\r", "\n")

    # fix hyphenation across line breaks (e.g., reimburse-\nment → reimbursement)
    text = re.sub(r"-\n\s*", "", text)

    # collapse multiple spaces/newlines
    text = re.sub(r"[ \t]+", " ", text)       # multiple spaces → one
    text = re.sub(r"\n{2,}", "\n\n", text)    # multiple blank lines → one

    # normalize punctuation
    text = text.translate(str.maketrans({
        "“": '"', "”": '"',
        "‘": "'", "’": "'",
        "—": "-", "–": "-"
    }))

    # strip leading/trailing whitespace
    return text.strip()

def normalize_parsed_json(parsed_json):
    for page in parsed_json["pages"]:
        for block in page["blocks"]:
            if "text" in block:
                block["text_normalized"] = normalize_text(block["text"])
                # optional: also keep lowercase version
                block["text_lower"] = block["text_normalized"].lower()
    return parsed_json


def remove_headers_footers(parsed_json, threshold=0.5):
    """
    Remove repeated headers and footers from parsed JSON.
    - threshold: fraction of pages a line must appear in to be considered header/footer
    """
    num_pages = len(parsed_json["pages"])
    header_candidates = {}
    footer_candidates = {}

    # Step 1: Count first and last lines
    for page in parsed_json["pages"]:
        text_blocks = [b["text_normalized"] for b in page["blocks"] if "text_normalized" in b]
        if not text_blocks:
            continue
        lines = text_blocks[0].split("\n")
        if lines:
            header_line = lines[0].strip()
            footer_line = lines[-1].strip()
            header_candidates[header_line] = header_candidates.get(header_line, 0) + 1
            footer_candidates[footer_line] = footer_candidates.get(footer_line, 0) + 1

    # Step 2: Determine repeated headers/footers
    header_to_remove = {line for line, count in header_candidates.items() if count / num_pages >= threshold}
    footer_to_remove = {line for line, count in footer_candidates.items() if count / num_pages >= threshold}

    # Step 3: Remove from each page
    for page in parsed_json["pages"]:
        new_blocks = []
        for block in page["blocks"]:
            if "text_normalized" in block:
                lines = block["text_normalized"].split("\n")
                # Remove header/footer if detected
                if lines and lines[0].strip() in header_to_remove:
                    lines = lines[1:]
                if lines and lines[-1].strip() in footer_to_remove:
                    lines = lines[:-1]
                block["text_normalized"] = "\n".join(lines).strip()
            new_blocks.append(block)
        page["blocks"] = new_blocks

    return parsed_json


def extract_clauses_from_text(text: str) -> list:
    """
    Extract clauses starting with numbers like 1., 2.3, 3.4.5, or bullet points A., B., C., etc.
    Returns a list of tuples (clause_number, clause_text).
    """
    clause_pattern = re.compile(
        r'('
        r'(?:\d+\.)+\d*|'   # Numbered clauses like 1., 2.3, 3.4.5
        r'[A-Z]\.'          # Bullet points like A., B., C.
        r')\s+(.*?)(?='
        r'(?:\d+\.)+\d*|'    # Lookahead for next numbered clause
        r'[A-Z]\.|$'         # Or next bullet or end of text
        r')', re.DOTALL)
    matches = clause_pattern.findall(text)
    return [(m[0], m[1].strip()) for m in matches]

def extract_all_clauses(parsed_json):
    """
    Extract all clauses from normalized parsed JSON, excluding text within tables.
    Returns a dictionary: {page_num: [(clause_num, clause_text), ...]}
    """
    clauses_per_page = {}
    for page in parsed_json["pages"]:
        page_num = page["page_num"]

        # Combine only text from blocks, exclude tables entirely
        # so no text extracted from tables is considered
        combined_text = "\n".join(
            b.get("text_normalized", "") for b in page["blocks"] if b.get("processing_method") != "table"
        )
        clauses = extract_clauses_from_text(combined_text)
        clauses_per_page[page_num] = clauses
    return clauses_per_page


def extract_clauses_from_entire_document(parsed_json):
    """
    Extract clauses from the entire document (all pages combined, excluding tables).
    Returns a list of tuples (clause_number, clause_text).
    """
    combined_text = "\n".join(
        b.get("text_normalized", "")
        for page in parsed_json["pages"]
        for b in page["blocks"]
        if b.get("processing_method") != "table"
    )
    return extract_clauses_from_text(combined_text)


def parse_pdf_hybrid_with_ocr(pdf_path: str) -> Dict[str, Any]:
    """
    Parse a PDF file using pdfplumber + OCR (PyTesseract).
    """
    filename = Path(pdf_path).stem
    result = {
        "doc_id": filename,
        "pages": [],
        "parsing_method": "pdfplumber_pytesseract_tables",
        "ocr_stats": {
            "total_pages": 0,
            "text_pages": 0,
            "ocr_processed_pages": 0,
            "empty_pages": 0
        }
    }

    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        result["ocr_stats"]["total_pages"] = total_pages
        print(f"Processing {total_pages} pages...")

        # Keep PyMuPDF doc open for OCR conversion
        doc_fitz = fitz.open(pdf_path)

        for page_num, page in enumerate(pdf.pages):
            page_data = {
                "page_num": page_num + 1,
                "blocks": [],
                "tables": [],
                "page_info": {
                    "width": page.width,
                    "height": page.height,
                    "has_text": False,
                    "text_length": 0,
                    "ocr_used": False,
                    "processing_method": "pdfplumber"
                }
            }

            # Try pdfplumber first
            page_text = page.extract_text()

            if page_text and page_text.strip():
                #  Text detected
                page_data["page_info"]["has_text"] = True
                page_data["page_info"]["text_length"] = len(page_text.strip())
                result["ocr_stats"]["text_pages"] += 1
                page_data["blocks"].append({
                    "text": page_text.strip(),
                    "processing_method": "pdfplumber"
                })

            else:
                # ❌ No text, check for images with PyMuPDF
                page_fitz = doc_fitz[page_num]
                images = page_fitz.get_images()

                if images:
                    # Convert PDF page to image
                    pix = page_fitz.get_pixmap(matrix=fitz.Matrix(2, 2))  # higher res
                    img = Image.open(io.BytesIO(pix.tobytes("png")))

                    # Run OCR
                    ocr_text = pytesseract.image_to_string(img)

                    if ocr_text.strip():
                        page_data["page_info"]["has_text"] = True
                        page_data["page_info"]["text_length"] = len(ocr_text.strip())
                        page_data["page_info"]["ocr_used"] = True
                        page_data["page_info"]["processing_method"] = "pytesseract"
                        result["ocr_stats"]["ocr_processed_pages"] += 1
                        page_data["blocks"].append({
                            "text": ocr_text.strip(),
                            "processing_method": "pytesseract"
                        })
                    else:
                        # OCR failed
                        result["ocr_stats"]["empty_pages"] += 1
                else:
                    # Truly empty page
                    result["ocr_stats"]["empty_pages"] += 1

            # --- Table detection ---
            tables = page.extract_tables()
            for table in tables:
                page_data["tables"].append(table)

            result["pages"].append(page_data)

        doc_fitz.close()

    return result


def save_parsed_json(data: Dict[str, Any], output_path: str) -> None:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def generate_markdown_from_clauses(normalized_json_path: str, output_md_path: str) -> None:
    import json

    # Load normalized JSON with clauses
    with open(normalized_json_path, "r", encoding="utf-8") as f:
        parsed = json.load(f)

    # Extract clauses from the entire document
    clauses = extract_clauses_from_entire_document(parsed)

    # Start markdown content string
    md_content = f"# Clauses Extracted from {normalized_json_path}\n\n"

    for clause_num, clause_text in clauses:
        md_content += f"## Clause {clause_num}\n\n{clause_text}\n\n"

    # Write markdown content to file
    with open(output_md_path, "w", encoding="utf-8") as md_file:
        md_file.write(md_content)

    print(f" Markdown file generated at: {output_md_path}")


def generate_structured_markdown_from_contract(normalized_json_path: str, output_md_path: str) -> None:
    # Load normalized JSON
    with open(normalized_json_path, "r", encoding="utf-8") as f:
        parsed = json.load(f)

    # Combine all normalized text (excluding tables)
    contract_text = "\n".join(
        b.get("text_normalized", "")
        for page in parsed["pages"]
        for b in page["blocks"]
        if b.get("processing_method") != "table"
    )

    # Preprocess: remove extra spaces, merge broken lines
    contract_text = re.sub(r"\n{2,}", "\n", contract_text)
    contract_text = re.sub(r"[ \t]+", " ", contract_text)

    # Patterns
    article_pat = re.compile(r"^(ARTICLE\s+[IVXLCDM]+|ARTICLE\s+\d+)(.*)", re.IGNORECASE)
    section_pat = re.compile(r"^(Section|SECTION)\s+([IVXLCDM\d]+[\.\d]*|[A-Z]+)[ \-–]*([A-Za-z0-9 ,\-/]*)", re.IGNORECASE)
    clause_pat = re.compile(r"^(\d+(?:\.\d+)*|[IVXLCDM]+\.[\d\.]+|[A-Z]\.|[a-z]\)|[A-Z]\))\s+(.*)", re.IGNORECASE)

    lines = contract_text.split("\n")
    md_lines = []
    current_article = None
    current_section = None
    current_clause = None
    clause_buffer = []

    def flush_clause():
        nonlocal current_clause, clause_buffer
        if current_clause and clause_buffer:
            md_lines.append(f"### {current_clause}\n" + " ".join(clause_buffer).strip() + "\n")
        clause_buffer = []
        current_clause = None

    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Article
        m = article_pat.match(line)
        if m:
            flush_clause()
            current_article = f"ARTICLE {m.group(1).split()[1]} - {m.group(2).strip()}" if m.group(2).strip() else f"ARTICLE {m.group(1).split()[1]}"
            md_lines.append(f"# {current_article}\n")
            current_section = None
            continue
        # Section
        m = section_pat.match(line)
        if m:
            flush_clause()
            section_num = m.group(2)
            section_title = m.group(3).strip()
            section_heading = f"Section {section_num} {section_title}" if section_title else f"Section {section_num}"
            md_lines.append(f"## {section_heading}\n")
            current_section = section_heading
            continue
        # Clause
        m = clause_pat.match(line)
        if m:
            flush_clause()
            current_clause = m.group(1)
            clause_buffer.append(m.group(2).strip())
            continue
        # Otherwise, part of current clause
        if current_clause:
            clause_buffer.append(line)
    flush_clause()

    # Write markdown
    with open(output_md_path, "w", encoding="utf-8") as md_file:
        md_file.write("\n".join(md_lines))
    print(f"✅ Structured Markdown file generated at: {output_md_path}")


def main():
    sample_pdf = "HiLabsAIQuest_ContractsAI/Contracts/TN/TN_Contract1_Redacted.pdf"
    print(f"Parsing {sample_pdf} with pdfplumber + PyTesseract OCR + tables")
    start_time = time.time()

    parsed = parse_pdf_hybrid_with_ocr(sample_pdf)
    elapsed = time.time() - start_time

    output_path = "outputs/parsed/TN_Contract1_hybrid_ocr_tables.json"
    save_parsed_json(parsed, output_path)

    print(f" Saved parsed JSON to {output_path}")
    print(f" Parsing time: {elapsed:.2f}s")
    print(f"Stats: {parsed['ocr_stats']}")

    # Quick preview
    for page in parsed["pages"][:1]:
        print(f"\nPage {page['page_num']} preview:")
        print(f"- Text length: {page['page_info']['text_length']}")
        print(f"- OCR used: {page['page_info']['ocr_used']}")
        print(f"- Tables detected: {len(page['tables'])}")

    input_path = "outputs/parsed/TN_Contract1_hybrid_ocr_tables.json"
    output_path = "outputs/parsed_normalized/TN_Contract1_normalized.json"

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(input_path, "r", encoding="utf-8") as f:
        parsed = json.load(f)

    normalized = normalize_parsed_json(parsed)
    normalized = remove_headers_footers(normalized, threshold=0.5)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(normalized, f, indent=2, ensure_ascii=False)

    print(f" Normalized JSON saved to: {output_path}")

    normalized = normalize_parsed_json(parsed)
    normalized = remove_headers_footers(normalized, threshold=0.5)
    generate_markdown_from_clauses(
        normalized_json_path="outputs/parsed_normalized/TN_Contract1_normalized.json",
        output_md_path="outputs/parsed/clauses_documentation.md"
    )

    generate_structured_markdown_from_contract(
        normalized_json_path="outputs/parsed_normalized/TN_Contract1_normalized.json",
        output_md_path="outputs/parsed/structured_contract_documentation.md"
    )


if __name__ == "__main__":
    main()
