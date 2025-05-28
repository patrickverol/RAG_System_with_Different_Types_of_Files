"""
This module handles vector search operations using Qdrant and sentence transformers.
"""

# Import Qdrant client and models
from qdrant_client import QdrantClient
from qdrant_client.http import models

# Import sentence transformer for text embeddings
from sentence_transformers import SentenceTransformer


# Initialize the sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')


def getQdrantClient() -> QdrantClient:
    """
    Establish connection with Qdrant vector database.
    
    Returns:
        QdrantClient: Initialized Qdrant client instance
        
    Note:
        Uses default Qdrant service URL: http://qdrant:6333
    """
    # Initialize Qdrant client pointing to the service URL
    qdrant_client = QdrantClient("http://qdrant:6333")
    return qdrant_client


def qdrantSearch(qdrant_client: QdrantClient, query: str, collection_name: str) -> list:
    """
    Perform semantic search in Qdrant vector database.
    
    Args:
        qdrant_client (QdrantClient): Initialized Qdrant client
        query (str): Search query text
        collection_name (str): Name of the Qdrant collection to search in
        
    Returns:
        list: List of matching documents with their payloads
        
    Note:
        Uses HNSW index with ef=128 for approximate nearest neighbor search
        Returns top 5 most similar documents
    """
    # Convert query to vector using the sentence transformer
    query_vector = model.encode(query).tolist()
    
    # Define search parameters
    search_params = models.SearchParams(
        hnsw_ef=128,
        exact=False
    )
    
    # Perform the search
    search_result = qdrant_client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=5,
        search_params=search_params
    )
    
    # Initialize list to store result documents
    result_docs = []
    
    # Iterate over search results to extract document content
    for hit in search_result:
        result_docs.append(hit.payload)
    
    return result_docs 