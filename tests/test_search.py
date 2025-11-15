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

    def test_build_query_with_filters_modifies_query(self):
        """Test that _build_query_with_filters_and_params applies filters to the query."""
        filters = {
            'min_price': 1000,
            'max_price': 5000,
            'gender': 'Men',
            'brand': 'Nike',
            'color': 'Red'
        }

        query, params = self.search_engine._build_query_with_filters_and_params(
            base_query="SELECT * FROM products",
            query_embedding=[0.1, 0.2, 0.3],
            top_k=5,
            filters=filters
        )

        self.assertIn('WHERE', query)
        self.assertIn(1000, params)
        self.assertIn(5000, params)
        self.assertIn('Men', params)
        self.assertIn('Nike', params)
        self.assertIn('Red', params)
        self.assertEqual(query.count('%s'), len(params) - 2)

    def test_build_query_with_partial_filters(self):
        """Test that _build_query_with_filters_and_params works with partial filters."""
        filters = {'gender': 'Women', 'max_price': 3000}

        query, params = self.search_engine._build_query_with_filters_and_params(
            base_query="SELECT * FROM products",
            query_embedding=[0.1, 0.2, 0.3],
            top_k=5,
            filters=filters
        )

        self.assertIn('WHERE', query)
        self.assertIn('Women', params)
        self.assertIn(3000, params)
        self.assertEqual(len(params), 4)

    def test_build_query_with_empty_filters(self):
        """Test that empty filters dict doesn't modify query."""
        query, params = self.search_engine._build_query_with_filters_and_params(
            base_query="SELECT * FROM products",
            query_embedding=[0.1, 0.2, 0.3],
            top_k=5,
            filters={}
        )

        self.assertNotIn('WHERE', query)
        self.assertEqual(len(params), 2)

    def test_execute_query_returns_cursor(self):
        """Test that _execute_query creates a cursor, executes it with correct query and params, and returns it."""
        mock_cursor = Mock()
        self.mock_db.cursor.return_value = mock_cursor

        query = "SELECT * FROM products WHERE price < %s"
        params = [1000]

        result = self.search_engine._execute_query(query, params)

        self.assertIsNotNone(result)  # Should return something (the cursor)
        self.mock_db.cursor.assert_called_once()  # Should create a cursor
        mock_cursor.execute.assert_called_once_with(query, params)

    def test_execute_query_returns_same_cursor_instance(self):
        """Verify that _execute_query returns the exact cursor instance created by the DB."""
        mock_cursor = Mock()
        self.mock_db.cursor.return_value = mock_cursor

        query = "SELECT * FROM products"
        params = []

        result = self.search_engine._execute_query(query, params)

        self.assertIs(result, mock_cursor)

    def test_execute_query_propagates_database_exceptions(self):
        """Ensure exceptions raised during cursor.execute are not swallowed."""
        mock_cursor = Mock()
        self.mock_db.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Database connection failed")

        query = "SELECT * FROM products"
        params = []

        with self.assertRaises(Exception) as context:
            self.search_engine._execute_query(query, params)

        self.assertIn("Database connection failed", str(context.exception))

    def test_execute_query_with_empty_params(self):
        """Verify that _execute_query handles queries with no parameters correctly."""
        mock_cursor = Mock()
        self.mock_db.cursor.return_value = mock_cursor

        query = "SELECT * FROM products"
        params = []

        result = self.search_engine._execute_query(query, params)

        mock_cursor.execute.assert_called_once_with(query, [])
        self.assertIsNotNone(result)

    # next step - change the test so that it returns SearchResult objects
    # It's the next logical step from "returns a list" to "returns a list of the right type"
    # It's essential for the search() method to work correctly
    # It validates the data mapping from database columns to the dataclass fields
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