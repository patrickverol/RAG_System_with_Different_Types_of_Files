"""
API Module
This module implements the FastAPI endpoints for the RAG system.
It handles document queries and provides responses using the RAG system.
"""

# Import os module
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import FastAPI class from fastapi module to create the API
from fastapi import FastAPI

# Import QdrantVectorStore class from langchain_qdrant module to instantiate the vector database
from langchain_qdrant import QdrantVectorStore

# Import QdrantClient class from qdrant_client module to connect to the vector database
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

# Import BaseModel class from pydantic module to validate data sent to the API
from pydantic import BaseModel

# Import HuggingFaceEmbeddings class from langchain_huggingface module to generate embeddings
from langchain_huggingface import HuggingFaceEmbeddings

# Define Item class that inherits from BaseModel
class Item(BaseModel):
    query: str

# Define model name (tokenizer)
model_name = "sentence-transformers/msmarco-bert-base-dot-v5"

# Define model arguments
model_kwargs = {'device': 'cpu'}

# Define encoding arguments
encode_kwargs = {'normalize_embeddings': True}

# Create HuggingFaceEmbeddings instance
hf = HuggingFaceEmbeddings(
    model_name = model_name,
    model_kwargs = model_kwargs,
    encode_kwargs = encode_kwargs)

# Define use_nvidia_api variable as False
use_nvidia_api = False

# Check if Nvidia key is available
nvidia_key = os.getenv('NVIDIA_KEY')

if nvidia_key:

    # Import OpenAI class from openai module
    from openai import OpenAI
    
    # Create OpenAI instance with base URL and API key
    client_ai = OpenAI(base_url = "https://integrate.api.nvidia.com/v1", api_key = nvidia_key)

    # Set use_nvidia_api to True
    use_nvidia_api = True
else:
    
    # Print message indicating that LLM cannot be used
    print("Cannot use LLM. NVIDIA_KEY not found in environment variables.")

# Create instance to connect to vector database
client = QdrantClient("http://qdrant:6333")

# Define collection name
collection_name = "RAGVectorDB"

# Create collection if it doesn't exist
if not client.collection_exists(collection_name):
    print(f"Creating collection: {collection_name}")
    client.create_collection(
        collection_name,
        vectors_config=VectorParams(size=768, distance=Distance.COSINE)
    )

# Create Qdrant instance to send data to vector database
qdrant = QdrantVectorStore(
    client=client,
    collection_name=collection_name,
    embedding=hf,
    distance=Distance.COSINE
)

# Initialize FastAPI app
app = FastAPI()

# Define root route with GET method
@app.get("/")
async def root():
    
    # Check Qdrant collection status
    try:
        collection_info = client.get_collection(collection_name)
        points_count = client.count(collection_name).count
        return {
            "message": "RAG Project",
            "collection_status": {
                "name": collection_name,
                "points_count": points_count,
                "status": collection_info.status
            }
        }
    except Exception as e:
        return {
            "message": "RAG Project",
            "error": f"Failed to get collection status: {str(e)}"
        }

# Define /rag_api route with POST method
@app.post("/rag_api")
async def rag_api(item: Item):

    # Get query from item
    query = item.query
    
    # Perform similarity search
    search_result = qdrant.similarity_search(query = query, k = 10)
    print(f"Similarity search results: {search_result}")  # Debug log
    
    # Initialize results list, context and mapping
    list_res = []
    context = ""
    mappings = {}
    
    # Build context and results list
    for i, res in enumerate(search_result):

        print(f"Processing result {i}: {res.page_content[:100]}...")  # Debug log
        # Add content to context
        context += f"[{i}]\n{res.page_content}\n\n"
        # Add ID to document path mapping
        mappings[i] = res.metadata.get("path", "")
        # Add result to list
        list_res.append({
            "id": i,
            "path": res.metadata.get("path", ""),
            "content": res.page_content
        })

    print(f"Final context: {context[:200]}...")  # Debug log
    print(f"Final list_res: {list_res}")  # Debug log
    
    # Define system message
    rolemsg = {"role": "system",
               "content": "Answer the user's question using documents provided in the context. The context contains documents that should contain an answer. Always reference the document ID (in brackets, for example [0],[1]) of the document used to make a query. Use as many citations and documents as necessary to answer the question."}
    
    # Define messages
    messages = [rolemsg, {"role": "user", "content": f"Documents:\n{context}\n\nQuestion: {query}"}]
    
    # Check if Nvidia API is being used
    if use_nvidia_api:

        # Create LLM instance using Nvidia API
        resposta = client_ai.chat.completions.create(
            model = "meta/llama3-70b-instruct",
            messages = messages,
            temperature = 0.5,
            top_p = 1,
            max_tokens = 1024,
            stream = False
        )
        
        # Get response from LLM
        response = resposta.choices[0].message.content
    else:
        # Print message indicating that LLM cannot be used
        print("Cannot use LLM.")
        response = "Error: LLM not available."
    
    # Debug log
    print(f"Response: {response}")
    print(f"Documents: {list_res}")
    
    return {
        "context": list_res,
        "answer": response,
        "mappings": mappings
    }




