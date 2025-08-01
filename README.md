# 🛍️ Fashion Product Search Pipeline (ML Ops Portfolio Project)

This project builds a **production-style MLOps pipeline** that powers a hybrid **semantic + structured product search system** for an e-commerce use case.

---

## 🔍 Problem Statement

E-commerce platforms often rely on keyword search or basic filters, which fail to capture the **semantic meaning** of natural language queries like:

> *“Show me stylish travel bags for women under INR 2000.”*

This project solves that by:
- Ingesting and processing structured and unstructured product data
- Generating semantic embeddings from product descriptions
- Storing structured data in **PostgreSQL** and embeddings using **pgvector**
- Enabling hybrid retrieval using **natural language + structured filters**

---

## 🧠 Example Query Flow

User enters: `"Red formal shoes under INR 3000"`

1. Query is embedded into a vector
2. Vector DB retrieves top N similar products
3. SQL DB filters by price, color, gender, etc.
4. Ranked results are returned to the user

---

## 🧱 Architecture Overview

<pre> ```text +------------------+ | Kaggle Dataset | +--------+---------+ | [ETL: Pandas] | +------------v------------+ | PostgreSQL (SQL DB) | ← structured data +-------------------------+ | +------------+------------+ | SentenceTransformer | ← generate embeddings from descriptions +------------+------------+ | +------------v------------+ | pgvector / Postgres | ← vector search on embeddings +-------------------------+ | [Query Interface] | +------------v-------------+ | CLI / API / UI (TBD) | +--------------------------+ ``` </pre>


---

## 📚 Dataset

- **Source**: [Fashion Clothing Products Catalog – Kaggle](https://www.kaggle.com/datasets/shivamb/fashion-clothing-products-catalog)
- **Fields Used**: `product_id`, `product_name`, `product_brand`, `gender`, `price_inr`, `description`, `primary_color`
- **Size**: ~12,000 products

---

## 🤖 Embedding Model

- [`sentence-transformers/all-MiniLM-L6-v2`](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)  
  A compact transformer model used to generate dense vector embeddings from product descriptions (384 dimensions).

---

## 🧾 Database Design

**Schema**

- `products` – structured metadata about each product
- `product_embeddings` – semantic vector embeddings (stored using pgvector)

**Why PostgreSQL + pgvector?**
- Single, consistent database layer for both SQL filters and semantic search
- Fully Dockerized and extensible with pgvector extension
- Simpler than managing a separate vector DB

---

## 🧪 Features

- ✅ Load and clean structured product data into PostgreSQL
- ✅ Generate semantic embeddings from descriptions using SentenceTransformer
- ✅ Store and query vector data using pgvector
- ✅ Validate data and embedding logic with Pytest tests
- ✅ Fully containerized with Docker + docker-compose
- ✅ Logs and timing metrics for observability
- ✅ Spot-check tests for embedding quality (cosine similarity)
- 🔜 API and/or CLI interface for interactive queries
- 🔜 Cloud deployment with AWS/GCP

---

## 🛠️ Tech Stack

- **Python 3.11**
- **PostgreSQL 17 + pgvector**
- **Pandas, SentenceTransformers, NumPy**
- **Docker & Docker Compose**
- **pytest**
---

## 🚀 Setup Instructions

### Clone the Repo

```bash
git clone https://github.com/Nirvikalpa108/graeme
cd graeme
```

### Start the Pipeline with Docker
`docker-compose up --build`

This will:
- Start a PostgreSQL container with pgvector
- Run scripts to load and embed data
- Insert embeddings into the vector table
- Run integration tests and exit with success/failure status

### Run Tests Manually (Optional)
To re-run tests inside Docker:

`docker-compose run --rm app pytest`

### Stop & Clean Up
This stops all containers and deletes volumes (DB data).

`docker-compose down -v`