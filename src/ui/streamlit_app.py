"""
Streamlit UI for the Product Search Engine.

This app provides a simple web interface for searching products
using natural language queries.

Prerequisites:
    - Docker containers must be running: docker-compose up -d
    - Database must be populated with products
    - Embeddings must be generated and stored in pgvector

Usage:
    source venv/bin/activate
    pip install -r requirements.txt
    docker-compose up -d
    streamlit run src/ui/streamlit_app.py
"""

import streamlit as st
from dotenv import load_dotenv

load_dotenv(".env.local")

@st.cache_resource
def load_model():
    """Load and cache the embedding model."""
    return SentenceTransformer("all-MiniLM-L6-v2")


def main():
    #initialise model at app start
    model = load_model()
    
    st.set_page_config(
        page_title="Product Search",
        page_icon="🔍",
        layout="wide"
    )
    
    st.title("🔍 Product Search Engine")
    st.markdown("Search for products using natural language queries")
    
    # Search input
    query = st.text_input(
        "Enter your search query",
        placeholder="e.g., red dress for summer, casual shoes for men...",
        key="search_query"
    )


if __name__ == "__main__":
    main()