#!/usr/bin/env python3
"""
Test script to query the contract embeddings in ChromaDB.

Usage:
    python test_contract_embeddings.py --query "provider compensation terms"
"""

import argparse
import json
import requests
import numpy as np
from pathlib import Path
from typing import Dict, List, Any

import chromadb
from chromadb.config import Settings

class OllamaQueryClient:
    """Client for generating query embeddings using Ollama."""
    
    def __init__(self, model_name: str = "qwen3-embedding:0.6b", ollama_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.ollama_url = ollama_url
        self.embed_url = f"{ollama_url}/api/embeddings"
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for query text."""
        try:
            payload = {
                "model": self.model_name,
                "prompt": text
            }
            
            response = requests.post(
                self.embed_url,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                embedding = result.get('embedding', [])
                if embedding:
                    # Normalize the embedding
                    embedding = np.array(embedding)
                    embedding = embedding / np.linalg.norm(embedding)
                    return embedding.tolist()
            else:
                print(f"Ollama API error: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []

def query_contract_embeddings(query_text: str, 
                            collection_name: str = "redacted",
                            db_path: str = "../chroma_db_qwen",
                            model_name: str = "qwen3-embedding:0.6b",
                            n_results: int = 5) -> None:
    """Query the ChromaDB collection with a text query using Qwen embeddings."""
    
    # Initialize Ollama client
    print("Initializing Ollama client for query embedding...")
    ollama_client = OllamaQueryClient(model_name=model_name)
    
    # Generate query embedding
    print(f"Generating Qwen embedding for query: '{query_text}'")
    query_embedding = ollama_client.generate_embedding(query_text)
    
    if not query_embedding:
        print("Failed to generate query embedding")
        return
    
    # Connect to ChromaDB
    print(f"Connecting to ChromaDB at {db_path}")
    client = chromadb.PersistentClient(
        path=db_path,
        settings=Settings(anonymized_telemetry=False)
    )
    
    try:
        collection = client.get_collection(name=collection_name)
        print(f"Found collection '{collection_name}' with {collection.count()} documents")
    except Exception as e:
        print(f"Error accessing collection: {e}")
        return
    
    # Query similar documents
    print(f"Searching for {n_results} most similar documents...")
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=['documents', 'metadatas', 'distances']
    )
    
    # Display results
    print("\n" + "="*80)
    print(f"CONTRACT SEARCH RESULTS FOR: '{query_text}'")
    print("="*80)
    
    if results['documents'] and results['documents'][0]:
        for i, (doc, metadata, distance) in enumerate(zip(
            results['documents'][0], 
            results['metadatas'][0], 
            results['distances'][0]
        )):
            print(f"\n--- Result {i+1} (Similarity: {1-distance:.4f}) ---")
            print(f"Page: {metadata.get('page_number', 'N/A')}")
            print(f"Header Path: {metadata.get('header_path', 'N/A')}")
            print(f"Chunk ID: {metadata.get('chunk_id', 'N/A')}")
            print(f"Token Count: {metadata.get('token_count', 'N/A')}")
            print(f"Document Type: {metadata.get('document_type', 'N/A')}")
            
            # Show content flags
            flags = []
            for key, value in metadata.items():
                if key.startswith('contains_') and value:
                    flag_name = key.replace('contains_', '').replace('_', ' ').title()
                    flags.append(flag_name)
                elif key.startswith('is_') and value:
                    flag_name = key.replace('is_', '').replace('_', ' ').title()
                    flags.append(flag_name)
            
            if flags:
                print(f"Content Flags: {', '.join(flags)}")
            
            # Show document content
            doc_preview = doc[:300] + "..." if len(doc) > 300 else doc
            print(f"Content: {doc_preview}")
            print("-" * 60)
    else:
        print("No results found!")

def list_contract_collection_stats(collection_name: str = "redacted", db_path: str = "../chroma_db_qwen") -> None:
    """Display statistics about the contract embeddings collection."""
    
    print(f"Connecting to ChromaDB at {db_path}")
    client = chromadb.PersistentClient(
        path=db_path,
        settings=Settings(anonymized_telemetry=False)
    )
    
    try:
        collection = client.get_collection(name=collection_name)
        count = collection.count()
        
        print(f"\n📊 Contract Embeddings Collection Statistics:")
        print(f"Collection Name: {collection_name}")
        print(f"Total Documents: {count}")
        print(f"Collection Metadata: {collection.metadata}")
        
        if count > 0:
            # Get a sample of documents to analyze metadata
            sample = collection.get(limit=min(count, 100), include=['metadatas'])
            
            if sample['metadatas']:
                # Analyze content types
                content_flags = {}
                document_types = {}
                page_distribution = {}
                
                for metadata in sample['metadatas']:
                    # Count document types
                    doc_type = metadata.get('document_type', 'unknown')
                    document_types[doc_type] = document_types.get(doc_type, 0) + 1
                    
                    # Count page distribution
                    page = metadata.get('page_number', 0)
                    page_range = f"pages_{page//5 * 5 + 1}-{(page//5 + 1) * 5}"
                    page_distribution[page_range] = page_distribution.get(page_range, 0) + 1
                    
                    # Count content flags
                    for key, value in metadata.items():
                        if (key.startswith('contains_') or key.startswith('is_')) and value:
                            flag_name = key.replace('contains_', '').replace('is_', '').replace('_', ' ').title()
                            content_flags[flag_name] = content_flags.get(flag_name, 0) + 1
                
                print(f"\n📄 Document Types:")
                for doc_type, count in sorted(document_types.items(), key=lambda x: x[1], reverse=True):
                    print(f"  {doc_type}: {count}")
                
                print(f"\n📋 Content Analysis (from sample of {len(sample['metadatas'])} docs):")
                for flag, count in sorted(content_flags.items(), key=lambda x: x[1], reverse=True)[:10]:
                    print(f"  {flag}: {count}")
                
                print(f"\n📖 Page Distribution:")
                for page_range, count in sorted(page_distribution.items()):
                    print(f"  {page_range}: {count}")
        
    except Exception as e:
        print(f"Error accessing collection: {e}")

def compare_collections(query_text: str,
                       contract_collection: str = "redacted",
                       attribute_collection: str = "attribute",
                       db_path: str = "../chroma_db_qwen",
                       n_results: int = 3) -> None:
    """Compare results from contract vs attribute collections."""
    
    print(f"\n🔍 COMPARING COLLECTIONS FOR QUERY: '{query_text}'")
    print("="*80)
    
    # Query contract collection
    print(f"\n--- CONTRACT COLLECTION ({contract_collection}) ---")
    try:
        query_contract_embeddings(query_text, contract_collection, db_path, n_results=n_results)
    except Exception as e:
        print(f"Error querying contract collection: {e}")
    
    # Query attribute collection
    print(f"\n--- ATTRIBUTE COLLECTION ({attribute_collection}) ---")
    try:
        # Initialize Ollama client
        ollama_client = OllamaQueryClient()
        query_embedding = ollama_client.generate_embedding(query_text)
        
        if query_embedding:
            client = chromadb.PersistentClient(
                path=db_path,
                settings=Settings(anonymized_telemetry=False)
            )
            
            collection = client.get_collection(name=attribute_collection)
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )
            
            if results['documents'] and results['documents'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0], 
                    results['metadatas'][0], 
                    results['distances'][0]
                )):
                    print(f"\n--- Result {i+1} (Similarity: {1-distance:.4f}) ---")
                    print(f"Title: {metadata.get('title', 'N/A')}")
                    print(f"Primary Attribute: {metadata.get('primary_attribute', 'N/A')}")
                    doc_preview = doc[:200] + "..." if len(doc) > 200 else doc
                    print(f"Content: {doc_preview}")
            else:
                print("No results found in attribute collection!")
                
    except Exception as e:
        print(f"Error querying attribute collection: {e}")

def main():
    parser = argparse.ArgumentParser(description="Test ChromaDB contract embeddings")
    parser.add_argument("--query", type=str, help="Text query to search for")
    parser.add_argument("--collection-name", type=str, default="redacted", help="ChromaDB collection name")
    parser.add_argument("--db-path", type=str, default="../chroma_db_qwen", help="ChromaDB database path")
    parser.add_argument("--model-name", type=str, default="qwen3-embedding:0.6b", help="Ollama model name")
    parser.add_argument("--n-results", type=int, default=5, help="Number of results to return")
    parser.add_argument("--stats", action="store_true", help="Show collection statistics")
    parser.add_argument("--compare", action="store_true", help="Compare with attribute collection")
    
    args = parser.parse_args()
    
    if args.stats:
        list_contract_collection_stats(args.collection_name, args.db_path)
    
    if args.query:
        if args.compare:
            compare_collections(
                query_text=args.query,
                contract_collection=args.collection_name,
                db_path=args.db_path,
                n_results=args.n_results
            )
        else:
            query_contract_embeddings(
                query_text=args.query,
                collection_name=args.collection_name,
                db_path=args.db_path,
                model_name=args.model_name,
                n_results=args.n_results
            )
    
    if not args.query and not args.stats:
        print("Please provide either --query or --stats option")
        print("Example: python test_contract_embeddings.py --query 'provider compensation'")
        print("Example: python test_contract_embeddings.py --stats")
        print("Example: python test_contract_embeddings.py --query 'medicaid requirements' --compare")

if __name__ == "__main__":
    main()
