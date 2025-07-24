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

## 🗃️ Database Schema Design

To support both **semantic search** (via vector embeddings) and **structured filtering** (via SQL), this project uses a carefully designed PostgreSQL schema centered on a single `products` table.

### 🎯 Design Goals

The schema is optimized to:

- Enable **joins** between structured data and vector search results via `product_id`
- Support **filtering** by key attributes like price, gender, and color
- Store metadata needed for **displaying relevant results**
- Stay flexible and clean for production-scale querying

---

### 🧱 Table: `products`

| Column          | Type     | Purpose                                      |
|-----------------|----------|----------------------------------------------|
| `product_id`     | INTEGER  | Primary key; used to join with vector DB     |
| `product_name`   | TEXT     | Display title for results                    |
| `product_brand`  | TEXT     | Useful for filtering or grouping             |
| `gender`         | TEXT     | Common filter (Men, Women, Unisex)           |
| `price_inr`      | INTEGER  | Used for price filtering or sorting          |
| `description`    | TEXT     | Unstructured text used to generate embeddings|
| `primary_color`  | TEXT     | Optional structured filter                   |

---

### ⚙️ Why This Works

- ✅ **Simplicity**: Single-table design keeps queries fast and easy to debug  
- ✅ **Searchable**: All common filters (gender, color, price) are first-class columns  
- ✅ **Compatible**: `product_id` links to semantic search results from FAISS   
- ✅ **Ready for Production**: Schema avoids unnecessary complexity (e.g., joins for color/brand)  

---

### 🧠 Example Use Case

When a user enters:

> “Stylish red jackets under INR 3000 for women”

The app:

1. Embeds the query and performs a **nearest-neighbor search** on the vector database  
2. Retrieves the top matching `product_id`s  
3. Filters those using SQL:

```sql
SELECT * FROM products
WHERE product_id IN (...)
  AND gender = 'Women'
  AND primary_color = 'Red'
  AND price_inr <= 3000;

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