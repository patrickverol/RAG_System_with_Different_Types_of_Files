from abc import ABC, abstractmethod
import os
import tempfile
import requests
from pathlib import Path
import boto3
from botocore.exceptions import ClientError
from typing import List

class StorageInterface(ABC):
    @abstractmethod
    def list_documents(self):
        """List all available documents."""
        pass

    @abstractmethod
    def get_document(self, document_path):
        """Get a document and return its local path."""
        pass

    @abstractmethod
    def get_document_url(self, document_path):
        """Get a URL to access the document."""
        pass

class LocalStorage(StorageInterface):
    def __init__(self, base_path):
        self.base_path = Path(base_path)

    def list_documents(self):
        documents = []
        for root, _, files in os.walk(self.base_path):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), self.base_path)
                documents.append(rel_path)
        return documents

    def get_document(self, document_path):
        full_path = self.base_path / document_path
        if not full_path.exists():
            raise FileNotFoundError(f"Document not found: {document_path}")
        return str(full_path)

    def get_document_url(self, document_path):
        return f"/documents/{document_path}"

class S3Storage(StorageInterface):
    def __init__(self, bucket_name, region_name=None, endpoint_url=None):
        self.bucket_name = bucket_name
        self.s3_client = boto3.client(
            's3',
            region_name=region_name,
            endpoint_url=endpoint_url
        )

    def list_documents(self):
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)
            return [obj['Key'] for obj in response.get('Contents', [])]
        except ClientError as e:
            raise Exception(f"Error listing documents: {str(e)}")

    def get_document(self, document_path):
        try:
            # Create a temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            # Download the file from S3
            self.s3_client.download_fileobj(self.bucket_name, document_path, temp_file)
            temp_file.close()
            return temp_file.name
        except ClientError as e:
            raise Exception(f"Error downloading document: {str(e)}")

    def get_document_url(self, document_path):
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
    def __init__(self, base_url: str = 'http://document_storage:8080'):
        self.base_url = base_url.rstrip('/')
        print(f"Initialized HTTPStorage with base URL: {self.base_url}")

    def get_document_url(self, path: str) -> str:
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
            return temp_file.name
            
        except requests.exceptions.RequestException as e:
            print(f"Request error: {str(e)}")
            raise Exception(f"Error downloading document: {str(e)}")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            raise Exception(f"Error downloading document: {str(e)}")

    def list_documents(self) -> List[str]:
        try:
            response = requests.get(f"{self.base_url}/documents")
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Error listing documents: {response.text}")
        except Exception as e:
            raise Exception(f"Error listing documents: {str(e)}")

def get_storage(storage_type, **kwargs):
    """Factory function to create storage instances."""
    storage_types = {
        'local': LocalStorage,
        's3': S3Storage,
        'http': HTTPStorage
    }
    
    if storage_type not in storage_types:
        raise ValueError(f"Unsupported storage type: {storage_type}")
        
    return storage_types[storage_type](**kwargs) 