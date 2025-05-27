from abc import ABC, abstractmethod
import os
import tempfile
import requests
from pathlib import Path
import boto3
from botocore.exceptions import ClientError

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
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')

    def list_documents(self):
        response = requests.get(f"{self.base_url}/documents")
        response.raise_for_status()
        return response.json()

    def get_document(self, document_path):
        response = requests.get(f"{self.base_url}/documents/{document_path}")
        response.raise_for_status()
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(response.content)
        temp_file.close()
        return temp_file.name

    def get_document_url(self, document_path):
        return f"{self.base_url}/documents/{document_path}"

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