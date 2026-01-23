from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass
class SearchResult:
    product_id: int
    product_name: str
    product_brand: Optional[str]
    gender: Optional[str]
    price_inr: Optional[float]
    num_images: Optional[int]
    description: Optional[str]
    primary_color: Optional[str]
    similarity_score: float

@dataclass
class SearchFilters:
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    gender: Optional[str] = None
    brand: Optional[str] = None
    color: Optional[str] = None
    
class ProductSearchEngine:
    def __init__(self, db_connection, embedding_model):
        self.db = db_connection
        self.model = embedding_model

    from typing import Optional, List

    def search(self, query: str, top_k: int = 5, filters: Optional[SearchFilters] = None) -> List[SearchResult]:
        """
        Orchestrate the product search process:
        1. Convert the natural language query into an embedding vector.
        2. Build the base SQL query joining products and embeddings.
        3. Modify the query to include structured filters and prepare parameters.
        4. Execute the query and fetch results.
        5. Return the list of SearchResult objects.

        Args:
            query (str): The natural language search query.
            top_k (int): Number of top results to return.
            filters (Optional[SearchFilters]): Optional structured filters.

        Returns:
            List[SearchResult]: Ranked list of search results with similarity scores.
        """
        # Step 1: Convert query to embedding
        query_embedding = self.model.encode([query])[0]

        # Step 2: Build base SQL query joining products and embeddings
        base_query = self._build_similarity_query(top_k)

        # Step 3: Build full query with filters and prepare parameters
        filters_dict = filters.__dict__ if filters else None
        full_query, params = self._build_query_with_filters_and_params(
            base_query=base_query,
            query_embedding=query_embedding,
            top_k=top_k,
            filters=filters_dict
        )

        # Step 4: Execute the query
        cursor = self._execute_query(full_query, params)

        # Step 5: Fetch and return results
        results = self._fetch_results(cursor)
        return results

    def _build_similarity_query(self, top_k: int) -> str:
        return """
            SELECT p.id, p.product_name, p.product_brand, p.gender, p.price_inr, 
                p.num_images, p.description, p.primary_color,
                1 - (pe.embedding <=> %s) as similarity
            FROM products p
            JOIN product_embeddings pe ON p.id = pe.product_id
            ORDER BY similarity DESC
            LIMIT %s
        """

    def _build_query_with_filters_and_params(
        self,
        base_query: str,
        query_embedding: list,
        top_k: int,
        filters: Optional[dict] = None
    ) -> Tuple[str, List]:
        """
        Modify the base SQL query to include WHERE clauses for structured filters,
        and prepare the parameters list including the query embedding and top_k.

        Args:
            base_query (str): The initial SQL query string before applying filters.
            query_embedding (list): The embedding vector for the query.
            top_k (int): Number of top results to return.
            filters (Optional[dict]): Dictionary of filter criteria (min_price, max_price, gender, brand, color).

        Returns:
            Tuple[str, List]: 
                - Modified SQL query string with WHERE conditions and ordering.
                - List of parameters to be passed to the database cursor execute method.
        """
        # Initialize the query and parameters list
        query = base_query
        params = []
        
        # Add query embedding to parameters
        params.append(query_embedding)
        
        # Add top_k to parameters
        params.append(top_k)

        if filters:
            query += " WHERE 1=1"
            if filters.get('min_price'):
                query += " AND price_inr >= %s"
                params.append(filters['min_price'])
            if filters.get('max_price'):
                query += " AND price_inr <= %s"
                params.append(filters['max_price'])
            if filters.get('gender'):
                query += " AND gender = %s"
                params.append(filters['gender'])
            if filters.get('brand'):
                query += " AND product_brand = %s"
                params.append(filters['brand'])
            if filters.get('color'):
                query += " AND primary_color = %s"
                params.append(filters['color'])
        
        # Return the tuple with query and parameters
        return (query, params)
        
    def _execute_query(self, query: str, params: list):
        """
        Execute the given SQL query with parameters using the stored database connection.

        This method runs the full search query that:
        - Joins the products and product_embeddings tables
        - Performs vector similarity search using the query embedding
        - Applies structured filters (price, gender, brand, color)
        - Orders results by similarity score
        - Limits the results to the specified top_k

        Args:
            query: The complete SQL query string to execute, including joins, filters, ordering, and limits
            params: List of parameters to pass to the query, including the query embedding vector and filter values

        Returns:
            Raw database cursor after executing the query, which can be used to fetch the search results
        """
        # Create a cursor from the database connection
        cursor = self.db.cursor()
        
        # Execute the query with parameters
        cursor.execute(query, params)
        
        # Return the cursor
        return cursor

    def _fetch_results(self, cursor) -> List[SearchResult]:
        """
        Fetch all results from the executed query cursor and return them in a suitable format.

        Args:
            cursor: Database cursor after query execution

        Returns:
            List of SearchResult objects with product data and similarity scores
        """
        # Fetch all rows from the cursor
        rows = cursor.fetchall()
        
        # Return the rows as a search result
        return [
        SearchResult(
            product_id=row[0],
            product_name=row[1],
            product_brand=row[2],
            gender=row[3],
            price_inr=row[4],
            num_images=row[5],
            description=row[6],
            primary_color=row[7],
            similarity_score=row[8]
        )
        for row in rows
        ]