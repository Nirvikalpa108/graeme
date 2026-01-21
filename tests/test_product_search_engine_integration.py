import pytest
from src.product_search_engine import ProductSearchEngine, SearchFilters

class StubEmbeddingModel:
    def encode(self, texts: list) -> list:
        return [[0.1, 0.2, 0.3]]

class FakeDBConnection:
    def __init__(self, results):
        self.executed_sql = []
        self._results = results

    def cursor(self):
        return self  # Returns itself as the cursor

    def execute(self, query, params=None):
        self.executed_sql.append((query, params))  # Record the SQL execution

    def fetchall(self):
        return self._results  # Return mock results

    def commit(self):
        pass  # No-op for testing

    def reset_executed_sql(self):
        self.executed_sql = []

def test_product_search_engine():
    fake_db = FakeDBConnection(results=[
        (1, "Blue Denim Jeans", "Levi's", "Men", 2999.0, 3, "Classic straight fit denim jeans", "Blue", 0.95),
        (2, "Red Cotton T-Shirt", "Nike", "Women", 1499.0, 2, "Comfortable cotton t-shirt", "Red", 0.89),
        (3, "Black Leather Jacket", "Zara", "Unisex", 5999.0, 4, "Premium leather jacket", "Black", 0.82),
    ])
    stub_model = StubEmbeddingModel()
    search_engine = ProductSearchEngine(fake_db, stub_model)

    results = search_engine.search(
        query="blue jeans",
        top_k=3,
        filters=SearchFilters(min_price=1000, max_price=4000, gender="Men")
    )
    
    assert len(results) == 3
    assert results[0].product_name == "Blue Denim Jeans"
    
    fake_db = search_engine.db
    assert len(fake_db.executed_sql) == 1
    
    executed_query, executed_params = fake_db.executed_sql[0]
    
    # Verify embedding and top_k are first two params
    assert executed_params[0] == [0.1, 0.2, 0.3]
    assert executed_params[1] == 3
    
    # Verify filter params 
    assert 1000 in executed_params
    assert 4000 in executed_params
    assert "Men" in executed_params
    
    # Verify SQL structure
    assert executed_query.count("WHERE") == 1
    assert "price_inr >= %s" in executed_query
    assert "price_inr <= %s" in executed_query
    assert "gender = %s" in executed_query

    # Add to existing assertions:
    assert "ORDER BY similarity DESC" in executed_query
    assert "LIMIT %s" in executed_query
    assert "JOIN product_embeddings pe" in executed_query

    # Verify all result fields
    assert results[0].product_id == 1
    assert results[0].price_inr == 2999.0
    assert results[0].similarity_score == 0.95