<h1 align="center">
    RAG System with Different Types of Files
</h1>

<br>
    <div align="center">
        <a><img src="https://github.com/user-attachments/assets/f867038e-4d7f-451f-9398-b9f9cd0ad3db"></a> 
    </div>
</br>

<div align="center">
    <a href = "https://www.python.org/" target="_blank"><img src="https://img.shields.io/badge/Python-3776AB.svg?style=for-the-badge&logo=Python&logoColor=white" target="_blank"></a>
    <a href = "https://docs.docker.com/"><img src="https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white" target="_blank"></a>
    <a href = "https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-009688.svg?style=for-the-badge&logo=FastAPI&logoColor=white" target="_blank"></a>
    <a href = "https://qdrant.tech/"><img src="https://img.shields.io/badge/Qdrant-FF4B4B.svg?style=for-the-badge&logo=Qdrant&logoColor=white" target="_blank"></a>
    <a href = "https://docs.streamlit.io/"><img src="https://img.shields.io/badge/Streamlit-FF4B4B.svg?style=for-the-badge&logo=Streamlit&logoColor=white" target="_blank"></a>
    <a href = "https://www.postgresql.org/"><img src="https://img.shields.io/badge/PostgreSQL-336791.svg?style=for-the-badge&logo=PostgreSQL&logoColor=white" target="_blank"></a>
    <a href = "https://grafana.com/"><img src="https://img.shields.io/badge/Grafana-F46800.svg?style=for-the-badge&logo=Grafana&logoColor=white" target="_blank"></a>
</div> 

## About the project

This project implements a Retrieval-Augmented Generation (RAG) system that can handle different types of files. The system uses FastAPI for the backend, Qdrant as a vector database, Streamlit for the frontend interface, and includes monitoring capabilities with Grafana. The system is designed to process, store, and retrieve information from various document types efficiently.

## Architecture Overview

The system is designed with a microservices architecture, divided into several components for better scalability and maintainability:

1. **Backend Environment (FastAPI)**
   - Handles document processing and embedding
   - Manages interactions with Qdrant vector database
   - Provides REST API endpoints
   - Advantages:
     - Fast and efficient API handling
     - Async support for better performance
     - Easy integration with vector database
     - Scalable document processing

2. **Frontend Environment (Streamlit)**
   - Provides user interface for document upload and query
   - Displays search results and document information
   - Advantages:
     - User-friendly interface
     - Real-time updates
     - Easy to customize and extend
     - Responsive design

3. **Storage Environment**
   - Qdrant for vector storage
   - PostgreSQL for metadata storage
   - Document storage service for file management
   - Advantages:
     - Efficient vector similarity search
     - Reliable metadata management
     - Flexible document storage options
     - Scalable architecture

## Data Flow and Storage Strategy

The system implements a sophisticated data handling strategy:

1. **Document Processing**
   - Supports multiple file types
   - Converts documents to embeddings
   - Stores metadata and vectors separately
   - Advantages:
     - Flexible document handling
     - Efficient storage
     - Quick retrieval
     - Easy to extend

2. **Vector Storage (Qdrant)**
   - Stores document embeddings
   - Enables semantic search
   - Advantages:
     - Fast similarity search
     - Scalable vector storage
     - Efficient querying
     - Real-time updates

3. **Metadata Storage (PostgreSQL)**
   - Stores document metadata
   - Manages relationships
   - Advantages:
     - Reliable data storage
     - ACID compliance
     - Easy querying
     - Data integrity

## Project Structure

```
├── backend/                                                    # FastAPI backend
│   ├── app/                                                   # Application code
│   ├── backend.Dockerfile                                     # Container configuration
│   └── requirements.txt                                       # Python dependencies
├── frontend/                                                  # Streamlit frontend
│   ├── app.py                                                # Main application code
│   ├── frontend.Dockerfile                                   # Container configuration
│   └── requirements.txt                                      # Python dependencies
├── document_storage/                                         # Document storage service
│   ├── app/                                                 # Application code
│   ├── Dockerfile                                          # Container configuration
│   └── requirements.txt                                    # Python dependencies
├── dashboardgrafana/                                        # Grafana dashboards
├── docker-compose-rag.yaml                                  # Infrastructure services
└── README.md                                               # Project documentation
```

---

## Accessing the Services

1. **Backend API**
   - URL: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

2. **Frontend Interface**
   - URL: http://localhost:8501

3. **Grafana Dashboard**
   - URL: http://localhost:3000
   - Default credentials:
     - Username: admin
     - Password: admin

---

## Requirements

- Docker
- Docker Compose
- Python 3.9+
- NVIDIA GPU (optional, for faster processing)

---

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. **Set up environment variables**
   Create a `.env` file in the root directory with the following variables:
   ```
   STORAGE_TYPE=local
   DOCUMENTS_PATH=/app/documents
   GRAFANA_ADMIN_PASSWORD=admin
   ```

3. **Start the services**
   ```bash
   docker-compose -f docker-compose-rag.yaml up -d
   ```

4. **Wait for all services to start**
   The system includes the following services:
   - Backend (FastAPI)
   - Frontend (Streamlit)
   - Qdrant
   - PostgreSQL
   - Document Storage
   - Grafana

5. **Access the services**
   - Open the frontend interface at http://localhost:8501
   - Upload documents through the interface
   - Use the search functionality to query your documents
   - Monitor system performance through Grafana dashboard

## Features

- Document processing for multiple file types
- Semantic search capabilities
- Real-time document upload and processing
- Vector similarity search
- System monitoring and metrics
- Scalable architecture
- User-friendly interface
