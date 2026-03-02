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
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv(".env.streamlit")

import streamlit as st
from sentence_transformers import SentenceTransformer
from pgvector.psycopg2 import register_vector
import psycopg2
from product_search_engine import ProductSearchEngine
from product_search_engine import SearchFilters


@st.cache_resource
def load_model():
    """Load and cache the embedding model."""
    return SentenceTransformer("all-MiniLM-L6-v2")

@st.cache_resource
def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 5432))
    )
    register_vector(conn)
    return conn

@st.cache_resource
def load_search_engine():
    model = load_model()
    conn = get_db_connection()
    return ProductSearchEngine(conn, model)


def main():
    st.set_page_config(
        page_title="Product Search",
        page_icon="🔍",
        layout="wide"
    )

    with st.sidebar:
        st.header("Filters")
        price_range = st.slider("Price range (INR)", 0, 10000, (0, 10000))
        gender = st.selectbox("Gender", ["All", "Men", "Women", "Boys", "Girls", "Unisex"])
        color = st.selectbox("Color", ["All", "Black", "White", "Red", "Blue", "Green", "Yellow", "Pink", "Grey", "Brown", "Navy Blue"])

    search_engine = load_search_engine()

    # Build filters from sidebar widgets
    filters = SearchFilters(
        min_price=price_range[0] if price_range[0] > 0 else None,
        max_price=price_range[1] if price_range[1] < 10000 else None,
        gender=gender if gender != "All" else None,
        color=color if color != "All" else None
    )
    
    st.title("🔍 Product Search Engine")
    st.markdown("Search for products using natural language queries")
    
    # Search input
    query = st.text_input(
        "Enter your search query",
        placeholder="e.g., red dress for summer, casual shoes for men...",
        key="search_query"
    )

    # Search button
    if st.button("🔍 Search", type="primary"):
        if query.strip():
            with st.spinner("Searching..."):
                results = search_engine.search(query, filters=filters)
            if results:
                for r in results:
                    with st.container(border=True):
                        st.subheader(r.product_name)
                        cols = st.columns(4)
                        cols[0].metric("Brand", r.product_brand or "N/A")
                        cols[1].metric("Price (INR)", r.price_inr or "N/A")
                        cols[2].metric("Color", r.primary_color or "N/A")
                        cols[3].metric("Similarity", f"{r.similarity_score:.2%}")
                        if r.description:
                            st.caption(r.description)
            else:
                st.info("No results found.")
        else:
            st.warning("Please enter a search query")

if __name__ == "__main__":
    main()