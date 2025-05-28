"""
Document Storage Service
This module implements a FastAPI service for storing and retrieving documents.
It provides endpoints for listing and downloading documents.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import os
from typing import List
import logging
import urllib.parse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Define the documents directory
DOCUMENTS_DIR = Path("/app/documents")
logger.info(f"Documents directory: {DOCUMENTS_DIR}")
logger.info(f"Documents directory exists: {DOCUMENTS_DIR.exists()}")
logger.info(f"Documents directory is dir: {DOCUMENTS_DIR.is_dir()}")

# Log directory contents and permissions
if DOCUMENTS_DIR.exists():
    logger.info(f"Documents directory permissions: {oct(DOCUMENTS_DIR.stat().st_mode)[-3:]}")
    logger.info(f"Documents directory contents: {os.listdir(DOCUMENTS_DIR)}")
    # List contents with full paths
    for item in os.listdir(DOCUMENTS_DIR):
        full_path = DOCUMENTS_DIR / item
        logger.info(f"Item: {item}, Full path: {full_path}, Exists: {full_path.exists()}, Is file: {full_path.is_file() if full_path.exists() else False}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.get("/documents")
async def list_documents() -> List[str]:
    """
    List all documents in the documents directory and its subdirectories.
    
    Returns:
        List[str]: List of document paths relative to the documents directory
        
    Raises:
        HTTPException: If there's an error listing documents
    """
    try:
        documents = []
        logger.info(f"Listing documents in {DOCUMENTS_DIR}")
        
        if not DOCUMENTS_DIR.exists():
            logger.error(f"Documents directory does not exist: {DOCUMENTS_DIR}")
            raise HTTPException(status_code=500, detail=f"Documents directory does not exist: {DOCUMENTS_DIR}")
            
        for root, dirs, files in os.walk(DOCUMENTS_DIR):
            logger.info(f"Scanning directory: {root}")
            logger.info(f"Found directories: {dirs}")
            logger.info(f"Found files: {files}")
            
            for file in files:
                # Get the relative path from DOCUMENTS_DIR
                rel_path = os.path.relpath(os.path.join(root, file), DOCUMENTS_DIR)
                documents.append(rel_path)
                logger.info(f"Added document: {rel_path}")
                
                # Log file permissions
                file_path = os.path.join(root, file)
                logger.info(f"File permissions for {file_path}: {oct(os.stat(file_path).st_mode)[-3:]}")
                
        return documents
        
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")

@app.get("/documents/{document_path:path}")
async def get_document(document_path: str):
    """
    Get a specific document by its path.
    
    Args:
        document_path (str): Path to the document relative to the documents directory
        
    Returns:
        FileResponse: The requested document file
        
    Raises:
        HTTPException: If the document is not found or there's an error retrieving it
    """
    try:
        logger.info(f"Received request for document: {document_path}")
        full_path = DOCUMENTS_DIR / document_path
        logger.info(f"Full path: {full_path}")
        logger.info(f"Path exists: {full_path.exists()}")
        logger.info(f"Path is file: {full_path.is_file()}")
        
        if not full_path.exists() or not full_path.is_file():
            logger.error(f"Document not found at path: {full_path}")
            raise HTTPException(status_code=404, detail=f"Document not found: {document_path}")
            
        logger.info(f"Returning file: {full_path}")
        return FileResponse(full_path, filename=os.path.basename(document_path))
        
    except Exception as e:
        logger.error(f"Error retrieving document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 