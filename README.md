# 🛍️ Fashion Product Search Pipeline (ML Ops Portfolio Project)

This project builds a **production-style ML Ops pipeline** that powers a hybrid **semantic + structured product search system** for an e-commerce use case.

---

## 🔍 Problem Statement

E-commerce platforms store rich structured data (e.g., product name, price, category) and unstructured data (e.g., descriptions, reviews, images). However, search functionality is often limited to keyword or filter-based systems, which fail to capture the **semantic meaning** behind user queries like:

> *“Show me stylish travel bags for women under INR 2000.”*

This project solves that by:
- Ingesting and processing structured and unstructured data
- Creating embeddings from text descriptions using modern LLMs
- Storing structured data in a SQL database and embeddings in a vector database
- Allowing **natural language queries** that return semantically relevant, filterable results

## 🧠 Example Query Flow
User enters: "Red formal shoes under INR 3000"

Query is embedded into a vector

Vector DB retrieves top 10 semantically similar products

SQL DB filters for price, color, gender, etc.

Results are ranked + displayed via a UI

---

## 🧱 Architecture Overview

        +------------------+
        |  Kaggle Dataset  |
        +--------+---------+
                 |
           [ETL: Pandas]
                 |
    +------------v------------+
    |   PostgreSQL (SQL DB)   |  ← structured data
    +-------------------------+
                 |
    +------------+------------+
    |   SentenceTransformer   |  ← generate embeddings from descriptions
    +------------+------------+
                 |
    +------------v------------+
    |    FAISS / Qdrant DB    |  ← unstructured semantic data
    +-------------------------+
                 |
         [Query Interface]
                 |
    +------------v-------------+
    | Streamlit (or Flask App) |
    +--------------------------+

---

## 🧾 Dataset

- **Source**: [Fashion Clothing Products Catalog – Kaggle](https://www.kaggle.com/datasets/shivamb/fashion-clothing-products-catalog)
- **Format**: CSV
- **Fields Used**:
  - `product_id`, `product_name`, `product_brand`, `gender`, `price_inr`, `description`, `primary_color`
- **Size**: ~12,000 products

---

## 🧠 Embedding Model

- [`sentence-transformers/all-MiniLM-L6-v2`](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)  
  A lightweight transformer model for generating dense vector embeddings from product descriptions.

---

## 🧪 Features

- ✅ ETL pipeline to clean and load structured product data into PostgreSQL
- ✅ Embedding generation from unstructured `description` text
- ✅ Vector DB for similarity search
- ✅ Natural language query → vector search → SQL join → user results
- ✅ Dockerized setup with `docker-compose`
- ✅ Tests for data loading and transformation logic
- ✅ Cloud deployment

---

## 📦 Setup

### Requirements

TBD

### Run Locally

TBD

---

## 📜 License
This project is for educational and portfolio use only. Data provided by Kaggle under Creative Commons.