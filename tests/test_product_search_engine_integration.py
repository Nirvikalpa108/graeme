import pytest

def test_product_search_engine_placeholder():
    pytest.skip("Integration test not implemented yet")

class StubEmbeddingModel:
    def encode(self, texts: list) -> list:
        return [[0.1, 0.2, 0.3]]