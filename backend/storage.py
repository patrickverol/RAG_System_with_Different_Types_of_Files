"""
Storage Module
This module implements different storage interfaces for document management.
It provides support for local file system, S3, and HTTP-based storage solutions.
"""

from abc import ABC, abstractmethod
import os
import tempfile
import requests
from pathlib import Path
import boto3
from botocore.exceptions import ClientError
from typing import List


class StorageInterface(ABC):
    """
    Abstract base class defining the interface for document storage implementations.
    All storage implementations must provide these methods.
    """
    
    @abstractmethod
    def list_documents(self) -> List[str]:
        """
        List all available documents in the storage.
        
        Returns:
            List[str]: List of document paths relative to the storage root
        """
        pass

    @abstractmethod
    def get_document(self, document_path: str) -> str:
        """
        Retrieve a document and return its local path.
        
        Args:
            document_path (str): Path to the document relative to storage root
            
        Returns:
            str: Local path to the downloaded document
            
        Raises:
            FileNotFoundError: If document doesn't exist
            Exception: For other retrieval errors
        """
        pass

    @abstractmethod
    def get_document_url(self, document_path: str) -> str:
        """
        Get a URL to access the document.
        
        Args:
            document_path (str): Path to the document relative to storage root
            
        Returns:
            str: URL to access the document
        """
        pass


class LocalStorage(StorageInterface):
    """
    Implementation of StorageInterface for local file system storage.
    Handles documents stored in a local directory.
    """
    
    def __init__(self, base_path: str):
        """
        Initialize local storage with base path.
        
        Args:
            base_path (str): Base directory path for document storage
        """
        self.base_path = Path(base_path)

    def list_documents(self) -> List[str]:
        """
        List all documents in the local storage directory.
        
        Returns:
            List[str]: List of document paths relative to base_path
        """
        documents = []
        for root, _, files in os.walk(self.base_path):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), self.base_path)
                documents.append(rel_path)
        return documents

    def get_document(self, document_path: str) -> str:
        """
        Get the full path to a document in local storage.
        
        Args:
            document_path (str): Path to document relative to base_path
            
        Returns:
            str: Full path to the document
            
        Raises:
            FileNotFoundError: If document doesn't exist
        """
        full_path = self.base_path / document_path
        if not full_path.exists():
            raise FileNotFoundError(f"Document not found: {document_path}")
        return str(full_path)

    def get_document_url(self, document_path: str) -> str:
        """
        Get a URL to access the document.
        
        Args:
            document_path (str): Path to document relative to base_path
            
        Returns:
            str: URL path to the document
        """
        return f"/documents/{document_path}"


class S3Storage(StorageInterface):
    """
    Implementation of StorageInterface for Amazon S3 storage.
    Handles documents stored in an S3 bucket.
    """
    
    def __init__(self, bucket_name: str, region_name: str = None, endpoint_url: str = None):
        """
        Initialize S3 storage with bucket configuration.
        
        Args:
            bucket_name (str): Name of the S3 bucket
            region_name (str, optional): AWS region name
            endpoint_url (str, optional): Custom S3 endpoint URL
        """
        self.bucket_name = bucket_name
        self.s3_client = boto3.client(
            's3',
            region_name=region_name,
            endpoint_url=endpoint_url
        )

    def list_documents(self) -> List[str]:
        """
        List all documents in the S3 bucket.
        
        Returns:
            List[str]: List of document keys in the bucket
            
        Raises:
            Exception: If listing documents fails
        """
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)
            return [obj['Key'] for obj in response.get('Contents', [])]
        except ClientError as e:
            raise Exception(f"Error listing documents: {str(e)}")

    def get_document(self, document_path: str) -> str:
        """
        Download a document from S3 to a temporary file.
        
        Args:
            document_path (str): S3 key of the document
            
        Returns:
            str: Path to the temporary file containing the document
            
        Raises:
            Exception: If downloading document fails
        """
        try:
            # Create a temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            # Download the file from S3
            self.s3_client.download_fileobj(self.bucket_name, document_path, temp_file)
            temp_file.close()
            return temp_file.name
        except ClientError as e:
            raise Exception(f"Error downloading document: {str(e)}")

    def get_document_url(self, document_path: str) -> str:
        """
        Generate a presigned URL for accessing the document.
        
        Args:
            document_path (str): S3 key of the document
            
        Returns:
            str: Presigned URL for accessing the document
            
        Raises:
            Exception: If generating URL fails
        """
        try:
            # Generate a presigned URL for the S3 object
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': document_path
                },
                ExpiresIn=3600  # URL expires in 1 hour
            )
            return url
        except ClientError as e:
            raise Exception(f"Error generating URL: {str(e)}")


class HTTPStorage(StorageInterface):
    """
    Implementation of StorageInterface for HTTP-based storage.
    Handles documents served through an HTTP API.
    """
    
    def __init__(self, base_url: str = 'http://document_storage:8080'):
        """
        Initialize HTTP storage with base URL.
        
        Args:
            base_url (str): Base URL of the document storage service
        """
        self.base_url = base_url.rstrip('/')
        print(f"Initialized HTTPStorage with base URL: {self.base_url}")

    def get_document_url(self, path: str) -> str:
        """
        Get the URL to access a document.
        
        Args:
            path (str): Path to the document
            
        Returns:
            str: Full URL to access the document
        """
        # Ensure path is relative and remove leading slashes
        path = path.lstrip('/')
        print(f"Original path: {path}")
        
        # URL encode each part of the path, preserving forward slashes
        encoded_path = '/'.join(requests.utils.quote(part, safe='') for part in path.split('/'))
        print(f"Encoded path: {encoded_path}")
        
        # Construct full URL with proper scheme
        url = f"{self.base_url}/documents/{encoded_path}"
        print(f"Generated document URL: {url}")
        return url

    def get_document(self, document_path: str) -> str:
        """
        Download a document from the HTTP API to a temporary file.
        
        Args:
            document_path (str): Path to the document
            
        Returns:
            str: Path to the temporary file containing the document
            
        Raises:
            Exception: If download fails or document not found
        """
        try:
            # Get the URL for the document
            url = self.get_document_url(document_path)
            print(f"Attempting to download document from URL: {url}")
            
            # Make the request
            response = requests.get(url)
            print(f"Response status code: {response.status_code}")
            print(f"Response headers: {response.headers}")
            
            if response.status_code == 404:
                print(f"Document not found at URL: {url}")
                print(f"Response content: {response.text}")
                raise Exception(f"Document not found: {document_path}")
            
            # Create a temporary file with the correct extension
            file_ext = os.path.splitext(document_path)[1]
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_ext)
            temp_file.write(response.content)
            temp_file.close()
            print(f"Document downloaded successfully to: {temp_file.name}")
            
            # Return the temporary file path
            return temp_file.name
            
        except requests.exceptions.RequestException as e:
            print(f"Request error: {str(e)}")
            raise Exception(f"Error downloading document: {str(e)}")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            raise Exception(f"Error downloading document: {str(e)}")

    def list_documents(self) -> List[str]:
        """
        List all documents available through the HTTP API.
        
        Returns:
            List[str]: List of document paths
            
        Raises:
            Exception: If API request fails
        """
        try:
            response = requests.get(f"{self.base_url}/documents")
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Error listing documents: {response.text}")
        except Exception as e:
            raise Exception(f"Error listing documents: {str(e)}")


def get_storage(storage_type: str, **kwargs) -> StorageInterface:
    """
    Factory function to create storage instances.
    
    Args:
        storage_type (str): Type of storage to create ('local', 's3', or 'http')
        **kwargs: Additional arguments specific to the storage type
        
    Returns:
        StorageInterface: Instance of the requested storage type
        
    Raises:
        ValueError: If storage_type is not supported
    """
    storage_types = {
        'local': LocalStorage,
        's3': S3Storage,
        'http': HTTPStorage
    }
    
    if storage_type not in storage_types:
        raise ValueError(f"Unsupported storage type: {storage_type}")
        
    return storage_types[storage_type](**kwargs) 