# Projeto 9 - IA Generativa e RAG Para App de Sistema Inteligente de Busca em Documentos - Backend e API
# Módulo de RAG

# Importa o módulo sys para acessar os argumentos da linha de comando
import sys

# Importa o módulo docx para manipulação de arquivos Word
import docx

# Importa o módulo PyPDF2 para manipulação de arquivos PDF
import PyPDF2

# Importa o módulo Presentation do pacote pptx para manipulação de arquivos PowerPoint
from pptx import Presentation

# Importa as funções listdir, isfile, join e isdir dos módulos os e os.path para manipulação de diretórios e arquivos
from os import listdir
from os.path import isfile, join, isdir

# Importa a classe TokenTextSplitter do pacote langchain_text_splitters para a divisão do texto em tokens
from langchain_text_splitters import TokenTextSplitter

# Importa a classe HuggingFaceEmbeddings do pacote langchain_huggingface para criar as embeddings
from langchain_huggingface import HuggingFaceEmbeddings

# Importa as classes QdrantClient, Distance e VectorParams do pacote qdrant_client
# Criaremos o cliente de acesso ao Qdrant, definindo os parâmetros de armazenamento no banco vetorial
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

# Importa a classe Qdrant do pacote langchain_qdrant para criar uma instância do Qdrant e enviar os dados para o banco vetorial
from langchain_qdrant import Qdrant

# Importa o módulo de storage
from storage import get_storage

# Importa os módulos necessários
import os
import tempfile

# Define a função que carrega o texto de um arquivo Word
def dsa_carrega_texto_word(arquivoname):
    """Carrega o texto de um arquivo Word."""
    doc = docx.Document(arquivoname)
    fullText = [para.text for para in doc.paragraphs]
    return '\n'.join(fullText)

# Define a função que carrega o texto de um arquivo PowerPoint
def dsa_carrega_texto_pptx(arquivoname):
    """Carrega o texto de um arquivo PowerPoint."""
    prs = Presentation(arquivoname)
    fullText = []
    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                fullText.append(shape.text)
    return '\n'.join(fullText)

# Define a função principal para indexação dos documentos
def main_indexing(storage_config):
    """Função principal para indexação dos documentos."""
    # Inicializa o storage
    storage = get_storage(**storage_config)
    
    # Define o nome do modelo a ser usado para criar as embeddings
    model_name = "sentence-transformers/msmarco-bert-base-dot-v5"
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': True}

    # Inicializa a classe de embeddings do HuggingFace
    hf = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )

    # Inicializa o cliente Qdrant
    client = QdrantClient("http://qdrant:6333")
    collection_name = "DSAVectorDB"

    # Se a coleção já existir, exclui
    if client.collection_exists(collection_name):
        client.delete_collection(collection_name)

    # Cria uma nova coleção com parâmetros especificados
    client.create_collection(
        collection_name,
        vectors_config=VectorParams(size=768, distance=Distance.DOT)
    )

    # Inicializa a instância Qdrant
    qdrant = Qdrant(client, collection_name, hf)

    print("\nIndexando os documentos...\n")

    # Obtém a lista de todos os documentos
    lista_arquivos = storage.list_documents()
    
    # Itera sobre cada arquivo na lista
    for arquivo in lista_arquivos:
        try:
            # Obtém o documento do storage
            temp_file = storage.get_document(arquivo)
            
            try:
                arquivo_content = ""
                
                # Verifica se o arquivo é um PDF
                if arquivo.endswith(".pdf"):
                    print("Indexando: " + arquivo)
                    reader = PyPDF2.PdfReader(temp_file)
                    for page in reader.pages:
                        arquivo_content += " " + page.extract_text()
                
                # Verifica se o arquivo é um texto simples
                elif arquivo.endswith(".txt"):
                    print("Indexando: " + arquivo)
                    with open(temp_file, 'r') as f:
                        arquivo_content = f.read()
                
                # Verifica se o arquivo é um Word
                elif arquivo.endswith(".docx"):
                    print("Indexando: " + arquivo)
                    arquivo_content = dsa_carrega_texto_word(temp_file)
                
                # Verifica se o arquivo é um PowerPoint
                elif arquivo.endswith(".pptx"):
                    print("Indexando: " + arquivo)
                    arquivo_content = dsa_carrega_texto_pptx(temp_file)
                
                else:
                    continue

                # Inicializa o divisor de texto
                text_splitter = TokenTextSplitter(chunk_size=500, chunk_overlap=50)
                textos = text_splitter.split_text(arquivo_content)
                metadata = [{"path": arquivo} for _ in textos]
                qdrant.add_texts(textos, metadatas=metadata)

            finally:
                # Remove o arquivo temporário
                os.unlink(temp_file)

        except Exception as e:
            print(f"O processo falhou para o arquivo {arquivo}: {e}")

    print("\nIndexação Concluída!\n")

# Verifica se o script está sendo executado diretamente
if __name__ == "__main__":
    # Configuração do storage
    storage_config = {
        'storage_type': os.getenv('STORAGE_TYPE', 'local'),
        'base_path': os.getenv('DOCUMENTS_PATH', '/app/documents')
    }
    
    # Se for S3, adiciona as configurações específicas
    if storage_config['storage_type'] == 's3':
        storage_config.update({
            'bucket_name': os.getenv('S3_BUCKET_NAME'),
            'region_name': os.getenv('AWS_REGION'),
            'endpoint_url': os.getenv('S3_ENDPOINT_URL')
        })
    # Se for HTTP, adiciona a URL base
    elif storage_config['storage_type'] == 'http':
        storage_config['base_url'] = os.getenv('DOCUMENT_STORAGE_URL', 'http://document_storage:8080')
    
    main_indexing(storage_config)




