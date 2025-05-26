# Projeto 7 - Deploy de Aplicação de IA Generativa com Airflow, LLM, RAG, Qdrant e Grafana

# Imports
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer

# Initialize the sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Function to establish connection with Qdrant
def getQdrantClient():
    # Initialize Qdrant client pointing to the service URL
    # Edit the line below with your Qdrant hostname as shown in the classes
    qdrant_client = QdrantClient("http://qdrant:6333")
    return qdrant_client

# Function to perform search in Qdrant
def qdrantSearch(qdrant_client, query, collection_name):
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