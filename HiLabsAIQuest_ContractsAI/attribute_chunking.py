#!/usr/bin/env python3
# excel_to_md_chunker.py
"""
Convert Excel content to markdown chunks with proper formatting and metadata.

Requirements:
    pip install pandas openpyxl tiktoken

Usage:
    python excel_to_md_chunker.py --excel-file "your_file.xlsx" --output-dir "./chunked_output"
"""

import argparse
import json
import re
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional

import pandas as pd
import tiktoken

# Configuration
CHUNK_SIZE = 512  # Target token size per chunk
MIN_CHUNK_SIZE = 100  # Minimum tokens to create a separate chunk
ENCODING_NAME = "cl100k_base"
OUTPUT_DIR = "chunked_excel"

# Initialize tokenizer
enc = tiktoken.get_encoding(ENCODING_NAME)

def count_tokens(text: str) -> int:
    """Count tokens in text using tiktoken."""
    return len(enc.encode(text))

def clean_text(text: str) -> str:
    """Clean and normalize text content."""
    if pd.isna(text):
        return ""
    text = str(text).strip()
    # Remove excessive whitespace while preserving paragraph breaks
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text

def create_structured_content_from_row(row_data: Dict[str, Any], row_index: int) -> Dict[str, Any]:
    """Convert a row of Excel data into structured format for embeddings."""
    
    # Extract key fields
    first_col = list(row_data.keys())[0] if row_data else "Row"
    title = clean_text(row_data.get(first_col, f"Row {row_index + 1}"))
    
    # Create structured content
    structured_content = {
        "title": title,
        "sections": {},
        "full_text": "",
        "key_fields": {}
    }
    
    text_parts = []
    if title:
        text_parts.append(title)
    
    # Process each column as a structured section
    for col_name, value in row_data.items():
        clean_value = clean_text(value)
        if clean_value:
            section_key = col_name.lower().replace(' ', '_')
            structured_content["sections"][section_key] = {
                "name": col_name,
                "content": clean_value
            }
            
            # Add to full text for embedding
            text_parts.append(f"{col_name}: {clean_value}")
            
            # Store key fields for metadata
            structured_content["key_fields"][section_key] = clean_value
    
    # Create full text for embedding
    structured_content["full_text"] = " | ".join(text_parts)
    
    return structured_content

def split_structured_content_into_chunks(structured_content: Dict[str, Any], max_tokens: int = None) -> List[Dict[str, Any]]:
    """Split structured content into chunks based on token count."""
    if max_tokens is None:
        max_tokens = CHUNK_SIZE
        
    full_text = structured_content["full_text"]
    
    if count_tokens(full_text) <= max_tokens:
        return [structured_content]
    
    chunks = []
    sections = structured_content["sections"]
    title = structured_content["title"]
    
    # Try to split by sections first
    current_chunk_sections = {}
    current_text_parts = [title] if title else []
    current_tokens = count_tokens(title) if title else 0
    
    for section_key, section_data in sections.items():
        section_text = f"{section_data['name']}: {section_data['content']}"
        section_tokens = count_tokens(section_text)
        
        # If adding this section would exceed max tokens, create a new chunk
        if current_tokens + section_tokens > max_tokens and current_chunk_sections:
            chunk_full_text = " | ".join(current_text_parts)
            chunk = {
                "title": title,
                "sections": current_chunk_sections.copy(),
                "full_text": chunk_full_text,
                "key_fields": {k: v["content"] for k, v in current_chunk_sections.items()}
            }
            chunks.append(chunk)
            
            # Start new chunk
            current_chunk_sections = {section_key: section_data}
            current_text_parts = [title, section_text] if title else [section_text]
            current_tokens = count_tokens(title) + section_tokens if title else section_tokens
        else:
            current_chunk_sections[section_key] = section_data
            current_text_parts.append(section_text)
            current_tokens += section_tokens
    
    # Add remaining content
    if current_chunk_sections:
        chunk_full_text = " | ".join(current_text_parts)
        chunk = {
            "title": title,
            "sections": current_chunk_sections,
            "full_text": chunk_full_text,
            "key_fields": {k: v["content"] for k, v in current_chunk_sections.items()}
        }
        chunks.append(chunk)
    
    return chunks if chunks else [structured_content]

def extract_attributes_from_content(content: str) -> List[str]:
    """Extract relevant attributes/keywords from content for labeling."""
    content_lower = content.lower()
    
    # Define attribute patterns based on your Excel data
    attribute_patterns = {
        'medicaid_timely_filing': ['medicaid', 'timely filing', 'claims submission', '120 days'],
        'medicare_timely_filing': ['medicare', 'timely filing', 'medicare advantage', '90 days'],
        'no_steerage': ['networks', 'provider panels', 'participating provider', 'steerage'],
        'medicaid_fee_schedule': ['medicaid', 'fee schedule', 'reimbursement', 'compensation'],
        'medicare_fee_schedule': ['medicare', 'fee schedule', 'medicare advantage rate', 'eligible charges'],
        'claims_processing': ['claims', 'submission', 'adjudication', 'payment'],
        'provider_requirements': ['provider', 'credentialing', 'requirements', 'participation'],
        'reimbursement': ['reimbursement', 'payment', 'compensation', 'rate'],
        'regulatory': ['regulatory requirements', 'compliance', 'policy']
    }
    
    detected_attributes = []
    
    for attribute, keywords in attribute_patterns.items():
        score = 0
        for keyword in keywords:
            if keyword in content_lower:
                score += 1
        
        # If more than half the keywords match, include this attribute
        if score >= len(keywords) * 0.3:
            detected_attributes.append(attribute.replace('_', ' ').title())
    
    return detected_attributes if detected_attributes else ['General Content']

def process_excel_to_chunks(excel_path: Path, output_dir: Path) -> None:
    """Main function to process Excel file and create structured JSON chunks."""
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Read Excel file
    try:
        df = pd.read_excel(excel_path, engine='openpyxl')
        print(f"Successfully loaded Excel file with {len(df)} rows and {len(df.columns)} columns")
        print(f"Columns: {list(df.columns)}")
    except Exception as e:
        raise Exception(f"Error reading Excel file: {e}")
    
    # Initialize corpus index
    corpus_index = {
        "source_file": excel_path.name,
        "total_rows_processed": 0,
        "total_chunks_created": 0,
        "attributes_summary": {},
        "chunks": []
    }
    
    chunk_counter = 1
    
    # Process each row
    for row_idx, row in df.iterrows():
        # Convert row to dictionary
        row_data = row.to_dict()
        
        # Create structured content from row
        structured_content = create_structured_content_from_row(row_data, row_idx)
        
        if not structured_content["full_text"].strip():
            continue
        
        # Split into chunks if necessary
        content_chunks = split_structured_content_into_chunks(structured_content, CHUNK_SIZE)
        
        for chunk_idx, chunk_content in enumerate(content_chunks):
            # Extract attributes
            attributes = extract_attributes_from_content(chunk_content["full_text"])
            
            # Create filename
            attr_tag = "_".join([re.sub(r'[^\w\-]+', '_', attr.lower()) for attr in attributes[:2]])
            chunk_filename = f"chunk_{chunk_counter:04d}_row_{row_idx + 1}_{chunk_idx + 1}__{attr_tag}.json"
            
            # Generate chunk ID
            chunk_id = uuid.uuid4().hex[:8]
            
            # Create comprehensive chunk structure optimized for embeddings
            chunk_data = {
                # Core identifiers
                "chunk_id": chunk_id,
                "source_file": excel_path.name,
                "source_row": row_idx + 1,
                "chunk_index": chunk_idx + 1,
                "total_chunks_from_row": len(content_chunks),
                
                # Content for embedding
                "content": {
                    "title": chunk_content["title"],
                    "full_text": chunk_content["full_text"],
                    "sections": chunk_content["sections"],
                    "key_fields": chunk_content["key_fields"]
                },
                
                # Metadata for filtering and retrieval
                "metadata": {
                    "attributes": attributes,
                    "token_count": count_tokens(chunk_content["full_text"]),
                    "character_count": len(chunk_content["full_text"]),
                    "source_columns": list(row_data.keys()),
                    "chunk_filename": chunk_filename,
                    "created_at": "2025-09-28T13:13:36+05:30"  # Current timestamp
                },
                
                # Embedding-specific fields
                "embedding_metadata": {
                    "text_for_embedding": chunk_content["full_text"],
                    "title_for_embedding": chunk_content["title"],
                    "context_tags": attributes,
                    "semantic_type": "document_chunk",
                    "domain": "healthcare_regulatory"
                }
            }
            
            # Write chunk file
            chunk_path = output_dir / chunk_filename
            chunk_path.write_text(json.dumps(chunk_data, indent=2, ensure_ascii=False), encoding='utf-8')
            
            # Update corpus index
            corpus_index["chunks"].append({
                "chunk_id": chunk_id,
                "filename": chunk_filename,
                "source_row": row_idx + 1,
                "attributes": attributes,
                "token_count": chunk_data["metadata"]["token_count"],
                "title": chunk_content["title"]
            })
            corpus_index["total_chunks_created"] += 1
            
            for attr in attributes:
                corpus_index["attributes_summary"][attr] = corpus_index["attributes_summary"].get(attr, 0) + 1
            
            print(f"Created chunk {chunk_counter}: {chunk_filename}")
            chunk_counter += 1
        
        corpus_index["total_rows_processed"] += 1
    
    # Write corpus index
    index_path = output_dir / "corpus_index.json"
    index_path.write_text(json.dumps(corpus_index, indent=2), encoding='utf-8')
    
    # Create summary report
    summary_md = f"""# Excel to JSON Chunks Conversion Summary

## Source Information
- **File**: {excel_path.name}
- **Rows Processed**: {corpus_index['total_rows_processed']}
- **Chunks Created**: {corpus_index['total_chunks_created']}

## Attribute Distribution
"""
    
    for attr, count in sorted(corpus_index['attributes_summary'].items()):
        summary_md += f"- **{attr}**: {count} chunks\n"
    
    summary_md += f"""
## Files Generated
- **JSON Chunks**: {corpus_index['total_chunks_created']} files
- **Corpus Index**: 1 file (corpus_index.json)
- **Summary Report**: 1 file (this file)

## JSON Structure for Embeddings
Each chunk contains:
- **chunk_id**: Unique identifier
- **content**: Structured content with title, full_text, sections, and key_fields
- **metadata**: Attributes, token counts, source information
- **embedding_metadata**: Optimized fields for embedding generation

## Usage Notes
- Each chunk is a standalone JSON file optimized for embedding generation
- Chunks are split to stay within {CHUNK_SIZE} token limit
- Attributes are automatically detected based on content analysis
- Full text is provided in 'content.full_text' for embedding
- Context tags and semantic metadata included for better retrieval
"""
    
    summary_path = output_dir / "conversion_summary.md"
    summary_path.write_text(summary_md, encoding='utf-8')
    
    print(f"\n✅ Conversion completed successfully!")
    print(f"📁 Output directory: {output_dir}")
    print(f"📄 Processed {corpus_index['total_rows_processed']} rows")
    print(f"📝 Created {corpus_index['total_chunks_created']} chunks")
    print(f"📊 Summary report: {summary_path}")

def main():
    global CHUNK_SIZE
    
    parser = argparse.ArgumentParser(description="Convert Excel content to markdown chunks")
    parser.add_argument("--excel-file", type=str, required=True, help="Path to Excel file")
    parser.add_argument("--output-dir", type=str, default=OUTPUT_DIR, help="Output directory name")
    parser.add_argument("--chunk-size", type=int, default=CHUNK_SIZE, help="Target chunk size in tokens")
    
    args = parser.parse_args()
    
    excel_path = Path(args.excel_file)
    output_dir = Path(args.output_dir)
    
    if not excel_path.exists():
        raise SystemExit(f"Excel file not found: {excel_path}")
    
    CHUNK_SIZE = args.chunk_size
    
    process_excel_to_chunks(excel_path, output_dir)

if __name__ == "__main__":
    main()