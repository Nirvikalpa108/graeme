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
- ✅ Cloud deployment with GCP Cloud Run

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

### Populate the Neon DB (run the pipeline against the cloud DB)

The pipeline compose (`docker-compose.pipeline.yaml`) runs the data loading and embedding pipeline against the Neon cloud DB. Run this when you need to populate or refresh the Neon DB. The DB connection comes entirely from environment variables.

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

**Step 2 — Run the pipeline compose**

```bash
docker compose -f docker-compose.pipeline.yaml --env-file .env.prod up --build
```

**To stop:**

```bash
docker compose -f docker-compose.pipeline.yaml down
```

---

### Deploy to GCP Cloud Run

GCP hosts two things for this project:

- **Cloud Run Job** — runs the data pipeline once to populate Neon (uses `Dockerfile.pipeline`)
- **Cloud Run Service** — serves the Streamlit UI (uses `Dockerfile.streamlit`)

The reason there are two Dockerfiles is that a Docker image can only have one default command. The pipeline runs `entrypoint.sh`; the Streamlit UI runs `streamlit run ...`. Splitting them means each image does exactly one thing with no overrides needed.

**Prerequisites**
- [Install the gcloud CLI](https://cloud.google.com/sdk/docs/install) and run `gcloud auth login`
- Create a GCP project and enable billing
- Enable the required APIs:

```bash
gcloud services enable run.googleapis.com artifactregistry.googleapis.com
```

**Step 1 — Create an Artifact Registry repository**

This is GCP's private Docker image store — equivalent to Docker Hub but within your GCP project.

```bash
gcloud artifacts repositories create graeme --repository-format=docker --location=europe-west2
```

**Step 2 — Authenticate Docker with GCP**

```bash
gcloud auth configure-docker europe-west2-docker.pkg.dev
```

**Step 3 — Store DB secrets in GCP Secret Manager**

```bash
echo -n "<your-db-host>" | gcloud secrets create DB_HOST --data-file=-
echo -n "<your-db-user>" | gcloud secrets create DB_USER --data-file=-
echo -n "<your-db-password>" | gcloud secrets create DB_PASSWORD --data-file=-
echo -n "<your-db-name>" | gcloud secrets create DB_NAME --data-file=-
```

**Step 4 — Build and push the pipeline image**

```bash
docker build --platform linux/amd64 -f Dockerfile.pipeline -t europe-west2-docker.pkg.dev/<your-project>/graeme/pipeline:latest .
docker push europe-west2-docker.pkg.dev/<your-project>/graeme/pipeline:latest
```

**Step 5 — Create and run the Cloud Run Job to populate Neon**

A Cloud Run Job runs a container to completion and exits — perfect for a one-off pipeline. Run this once to populate Neon, and again any time the data needs refreshing.

```bash
gcloud run jobs create graeme-pipeline \
  --image europe-west2-docker.pkg.dev/<your-project>/graeme/pipeline:latest \
  --region europe-west2 \
  --memory=1Gi \
  --set-secrets="DB_HOST=DB_HOST:latest,DB_USER=DB_USER:latest,DB_PASSWORD=DB_PASSWORD:latest,DB_NAME=DB_NAME:latest" \
  --set-env-vars="DB_SSLMODE=require,DB_PORT=5432"

gcloud run jobs execute graeme-pipeline --region europe-west2 --wait
```

**Step 6 — Build and push the Streamlit image**

This uses `Dockerfile.streamlit`, which sets `streamlit run` as its default command.

```bash
docker build --platform linux/amd64 -f Dockerfile.streamlit -t europe-west2-docker.pkg.dev/<your-project>/graeme/streamlit:latest .
docker push europe-west2-docker.pkg.dev/<your-project>/graeme/streamlit:latest
```

**Step 7 — Deploy the Streamlit UI as a Cloud Run Service**

Cloud Run pulls the image from Artifact Registry, injects the secrets as environment variables, and starts the container. The Streamlit UI is then publicly accessible via the URL Cloud Run provides.

```bash
gcloud run deploy graeme-streamlit \
  --image europe-west2-docker.pkg.dev/<your-project>/graeme/streamlit:latest \
  --platform managed \
  --region europe-west2 \
  --port 8501 \
  --max-instances=1 \
  --memory=512Mi \
  --allow-unauthenticated \
  --set-secrets="DB_HOST=DB_HOST:latest,DB_USER=DB_USER:latest,DB_PASSWORD=DB_PASSWORD:latest,DB_NAME=DB_NAME:latest" \
  --set-env-vars="DB_SSLMODE=require,TOKENIZERS_PARALLELISM=false"
```

**Step 8 — Open the app**

Cloud Run will print a public HTTPS URL when the deploy completes. Open it in your browser.