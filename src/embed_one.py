from sentence_transformers import SentenceTransformer

if __name__ == "__main__":
    print("🚀 Starting embedding demo...")

    model = SentenceTransformer("all-MiniLM-L6-v2")
    sentence = "Red cotton T-shirt for men"
    embedding = model.encode(sentence)

    print("✅ Embedding created!")
    print(embedding)
    print(f"✅ Embedding shape: {embedding.shape}")
