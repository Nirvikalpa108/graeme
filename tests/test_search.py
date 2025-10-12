import unittest
from unittest.mock import Mock
from src.product_search_engine import ProductSearchEngine


class TestProductSearchEngine(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures that are reused across tests"""
        self.mock_db = Mock()
        self.mock_model = Mock()
        self.search_engine = ProductSearchEngine(self.mock_db, self.mock_model)

    def test_build_query_returns_tuple(self):
        """Test that _build_query_with_filters_and_params returns a tuple with 2 elements."""
        result = self.search_engine._build_query_with_filters_and_params(
            base_query="SELECT * FROM products",
            query_embedding=[0.1, 0.2, 0.3],
            top_k=5,
            filters=None
        )

        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)

    def test_execute_query_returns_cursor(self):
        """Simplest test - verify _execute_query returns a cursor."""
        mock_cursor = Mock()
        self.mock_db.cursor.return_value = mock_cursor
        
        query = "SELECT * FROM products WHERE price < %s"
        params = [1000]
        
        result = self.search_engine._execute_query(query, params)
        
        self.assertIsNotNone(result)  # Should return something (the cursor)
        self.mock_db.cursor.assert_called_once()  # Should create a cursor

    def test_fetch_results_returns_list(self):
        """Simplest test - verify _fetch_results returns a list."""
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            (1, "Red Shoes", "Nike", "Men", 2500.0, 5, "Stylish red shoes", "Red", 0.95)
        ]
        
        results = self.search_engine._fetch_results(mock_cursor)
        
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 1)
    
    
if __name__ == '__main__':
    unittest.main()