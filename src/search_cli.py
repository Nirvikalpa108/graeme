"""
Interactive CLI for the Product Search Engine.

This script provides a simple command-line interface for searching products
using natural language queries.

Prerequisites:
    - Docker containers must be running: docker-compose up -d
    - Database must be populated with products
    - Embeddings must be generated and stored in pgvector

Usage:
    source venv/bin/activate
    pip install -r requirements.txt
    docker-compose up -d
    python src/search_cli.py
    docker-compose down

Example queries:
    - "red dress for summer"
    - "casual shoes for men"
    - "formal wear"
    - "blue jeans"
    - "black leather bag"
    - "running shoes"
"""

from dotenv import load_dotenv
load_dotenv(".env.local")

from sentence_transformers import SentenceTransformer
from pgvector.psycopg2 import register_vector
from utils import db_connection
from product_search_engine import ProductSearchEngine, SearchResult
from typing import List

def format_results(results: List[SearchResult]) -> str:
    if not results:
        return "No results found."
    
    output = []
    for i, result in enumerate(results, 1):
        output.append(f"\n{i}. {result.product_name}")
        output.append(f"   Brand: {result.product_brand or 'N/A'}")
        output.append(f"   Price: ₹{result.price_inr or 'N/A'}")
        output.append(f"   Color: {result.primary_color or 'N/A'}")
        output.append(f"   Similarity: {result.similarity_score:.3f}")
        if result.description:
            desc = result.description[:100] + "..." if len(result.description) > 100 else result.description
            output.append(f"   Description: {desc}")
    
    return "\n".join(output)

def validate_query(query: str) -> tuple[bool, str]:
    query = query.strip()
    
    if query.lower() in ['exit', 'quit', 'q']:
        return False, "exit"
    
    if not query:
        return False, "empty"
    
    return True, query

def main():
    print("🔍 Initializing Product Search Engine...")
    print("\nWelcome! Type 'exit' or 'quit' to stop.")
    print("\nExample queries you can try:")
    print("  • red dress for summer")
    print("  • casual shoes for men")
    print("  • formal wear")
    print("  • blue jeans")
    print("  • black leather bag")

    model = SentenceTransformer("all-MiniLM-L6-v2")

    with db_connection() as conn:
        register_vector(conn)
        search_engine = ProductSearchEngine(conn, model)
        
        while True:
            query = input("\nEnter search query: ")
            
            is_valid, processed_query = validate_query(query)
            
            if not is_valid:
                if processed_query == "exit":
                    print("👋 Goodbye!")
                    break
                elif processed_query == "empty":
                    print("⚠️  Please enter a search query.")
                    continue
            
            print(f"\n{'='*60}")
            print(f"Query: '{processed_query}'")
            print(f"{'='*60}")
            
            results = search_engine.search(processed_query, top_k=3)
            print(format_results(results))

if __name__ == "__main__":
    main()