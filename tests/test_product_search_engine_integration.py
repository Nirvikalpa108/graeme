import pytest
from src.product_search_engine import ProductSearchEngine, SearchFilters

class StubEmbeddingModel:
    def encode(self, texts: list) -> list:
        return [[0.1, 0.2, 0.3]]

class FakeDBConnection:
    def __init__(self):
        self.executed_sql = []  # Records all SQL queries and params as tuples
        self._results = [  # Mock product data: (id, name, brand, gender, price, num_images, description, color, similarity)
            (1, "Blue Denim Jeans", "Levi's", "Men", 2999.0, 3, "Classic straight fit denim jeans", "Blue", 0.95),
            (2, "Red Cotton T-Shirt", "Nike", "Women", 1499.0, 2, "Comfortable cotton t-shirt", "Red", 0.89),
            (3, "Black Leather Jacket", "Zara", "Unisex", 5999.0, 4, "Premium leather jacket", "Black", 0.82),
        ]

    def cursor(self):
        return self  # Returns itself as the cursor

    def execute(self, query, params=None):
        self.executed_sql.append((query, params))  # Record the SQL execution

    def fetchall(self):
        return self._results  # Return mock results

    def commit(self):
        pass  # No-op for testing

# pytest automatically calls the fixture and passes the results to each test
@pytest.fixture
def search_engine():
    fake_db = FakeDBConnection()
    stub_model = StubEmbeddingModel()
    return ProductSearchEngine(fake_db, stub_model)

def test_product_search_engine(search_engine):
    # Call search() with a sample query, top_k, and SearchFilters to exercise the full pipeline.
    results = search_engine.search(
        query="blue jeans",
        top_k=3,
        filters=SearchFilters(min_price=1000, max_price=4000, gender="Men")
    )