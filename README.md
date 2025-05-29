<h1 align="center">
    RAG System with Different Types of Files
</h1>

<br>
    <div align="center">
        <a><img src="https://github.com/user-attachments/assets/57d1cbdd-3562-411b-b1c6-9f2c2aeebb41"></a> 
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

## Streamlit interface

<br>
    <div align="center">
        <a><img src="https://github.com/user-attachments/assets/6eb83664-eff1-4ec2-918b-d1a839c98a61"></a> 
    </div>
</br>

## Grafana dashboard

<br>
    <div align="center">
        <a><img src="https://github.com/user-attachments/assets/a75685db-0e83-44e2-9cbd-4aee55a38c6e"></a> 
    </div>
</br>

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

## Project Structure

```
├── backend/                                                # FastAPI backend
│   ├── app/                                                # Application code
│   ├── backend.Dockerfile                                  # Container configuration
│   └── requirements.txt                                    # Python dependencies
├── frontend/                                               # Streamlit frontend
│   ├── app.py                                              # Main application code
│   ├── frontend.Dockerfile                                 # Container configuration
│   └── requirements.txt                                    # Python dependencies
├── document_storage/                                       # Document storage service
│   ├── app/                                                # Application code
│   ├── Dockerfile                                          # Container configuration
│   └── requirements.txt                                    # Python dependencies
├── dashboardgrafana/                                       # Grafana dashboards
├── docker-compose-rag.yaml                                 # Infrastructure services
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

---

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. **Set up environment variables**
   Go to docker-compose file and put your nvidia api key.
   ```
   NVIDIA_KEY=<your_api_key>
   ```

3. **Start the services**
   ```bash
   docker-compose up -d
   ```

4. **Wait for all services to start**
   The system includes the following services:
   - Backend (FastAPI)
   - Frontend (Streamlit)
   - Qdrant
   - PostgreSQL
   - Document Storage
   - Grafana

5. **Populate the Vector Databse**
   Go to the backend container terminal and run:
   ```
   python rag.py
   ```
   This script will get data from the document_storage container, apply the embedding and send the data to Vector database container (Qdrant).

6. **Acess the Wep App**
   - Open the frontend interface at http://localhost:8501
   - Use the search functionality to query your documents
   - Example:
   <br>
    <div align="center">
        <a><img src="https://github.com/user-attachments/assets/6eb83664-eff1-4ec2-918b-d1a839c98a61"></a> 
    </div>
   </br>

7. **Acess the Grafana dashboard**
   - You can monitor system performance through Grafana dashboard
   - Open the grafana interface at http://localhost:3000
   - Username: `admin`
   - Password: `admin` (*The brownser will show a message to change the password,, just ignore that and write the same password again*)
   - Go to `Connections` and search for `PostgreSQL`
   - Click in the conncetion and after that click on `Add new data source`
   - Make the configurations like below:
      - Host URL: `<your_postgre_container_hostname>:5432` (*You can see your postgres hostname running the command below in the terminal*)
      ```
      docker exec rag_postgres hostname
      ```
      - Database name: `admin`
      - Username: `admin`
      - Password: `admin`
      - TLS/SSL Mode: `disable`
   - Click on `Save & test`
   - Click `Dashboard` > `New` > `Import`
   - Upload the dashboard saved in the folder `observability`
   - After loading the dashboard, in the first time of the visualization you need to update each pannel to run the query
   - For each visualization:
      - Click on the `three dots in the top right corner` > `Edit` > `Run query`
   - After the fisrt update, the visualizations will be update automatically according to the refresh interval configured
   <br>
    <div align="center">
        <a><img src="https://github.com/user-attachments/assets/a75685db-0e83-44e2-9cbd-4aee55a38c6e"></a> 
    </div>
   </br>

## Features

- Document processing for multiple file types
- Semantic search capabilities
- Real-time document upload and processing
- Vector similarity search
- System monitoring and metrics
- Scalable architecture
- User-friendly interface
