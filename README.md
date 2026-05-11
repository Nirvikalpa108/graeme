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
- ✅ Streamlit UI for interactive natural language search
- 🔜 Cloud deployment with AWS/GCP

---

## 🛠️ Tech Stack

- **Python 3.11**
- **PostgreSQL 17 + pgvector**
- **Pandas, SentenceTransformers, NumPy**
- **Streamlit**
- **Docker & Docker Compose**
- **pytest**
---

## 🚀 Setup Instructions

### Clone the Repo

```bash
git clone https://github.com/Nirvikalpa108/graeme
cd graeme
```

### Create a `.env` file

Before running Docker, create a `.env` file in the project root with your database credentials:

```
DB_NAME=db
DB_USER=docker
DB_PASSWORD=docker
DB_HOST=localhost
DB_PORT=5433
```

This file is required by `docker-compose.yaml` and by `src/utils.py` to connect to the database.

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

### Run the Streamlit UI

```bash
docker-compose up --build
```

Then open http://localhost:8501 in your browser.

### Stop & Clean Up
This stops all containers and deletes volumes (DB data).

`docker-compose down -v`

### Run the Production Docker Compose Locally

The prod compose (`docker-compose.prod.yaml`) runs only the Streamlit app and expects a remote/cloud database — the DB connection comes entirely from environment variables.

**Step 1 — Create a `.env.prod` file**

```
DB_NAME=<your-prod-db-name>
DB_USER=<your-prod-db-user>
DB_PASSWORD=<your-prod-db-password>
DB_HOST=<your-prod-db-host>
DB_PORT=5432
DB_SSLMODE=require
```

> If you don't have a remote DB yet and want to test the prod compose locally, run `docker-compose up -d db` first (using the dev compose), then set `DB_HOST=host.docker.internal` in `.env.prod`.

**Step 2 — Run the prod compose**

```bash
docker compose -f docker-compose.prod.yaml --env-file .env.prod up --build
```

**Step 3 — Open the app**

Navigate to http://localhost:8501 in your browser.

**To stop:**

```bash
docker compose -f docker-compose.prod.yaml down
```