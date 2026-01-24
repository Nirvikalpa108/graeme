"""
Demo script to showcase the ProductSearchEngine functionality.

This script demonstrates semantic search working end-to-end:
- Converts natural language queries to embeddings
- Finds similar products using pgvector cosine similarity
- Joins vector results with structured SQL data (price, brand, color)
- Ranks results by similarity score

This is NOT a test file - it's a demonstration/example of the search engine in action.
For actual tests, see the tests/ directory.

Prerequisites:
    - Docker containers must be running: docker-compose up -d
    - Database must be populated with products
    - Embeddings must be generated and stored in pgvector

Usage:
    # Ensure Docker containers are running before executing the script
    ensure docker daemon is running on your machine
    docker-compose up -d
    python src/demo_search.py
"""

from dotenv import load_dotenv
load_dotenv(".env.local")

from sentence_transformers import SentenceTransformer
from pgvector.psycopg2 import register_vector
from utils import db_connection
from product_search_engine import ProductSearchEngine

print("🔍 Initializing Product Search Engine...")

model = SentenceTransformer("all-MiniLM-L6-v2")

with db_connection() as conn:
    register_vector(conn)
    search_engine = ProductSearchEngine(conn, model)
    
    sample_queries = [
        "red dress for summer",
        "casual shoes",
        "formal wear",
        "blue jeans"
    ]
    
    for query in sample_queries:
        print(f"\n{'='*60}")
        print(f"Query: '{query}'")
        print(f"{'='*60}")
        
        results = search_engine.search(query, top_k=3)
        
        if not results:
            print("No results found.")
        else:
            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result.product_name}")
                print(f"   Brand: {result.product_brand or 'N/A'}")
                print(f"   Price: ₹{result.price_inr or 'N/A'}")
                print(f"   Color: {result.primary_color or 'N/A'}")
                print(f"   Similarity: {result.similarity_score:.3f}")
                if result.description:
                    desc = result.description[:100] + "..." if len(result.description) > 100 else result.description
                    print(f"   Description: {desc}")
    
    print(f"\n{'='*60}")
    print("✅ Search demo complete!")