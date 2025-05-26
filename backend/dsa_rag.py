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

# Define a função que lista todos os arquivos em um diretório, incluindo os de subdiretórios
def dsa_lista_arquivos(dir):
    
    # Inicializa uma lista vazia para armazenar os caminhos dos arquivos
    arquivo_list = []
    
    # Itera sobre todos os arquivos e diretórios no diretório especificado
    for f in listdir(dir):
        
        # Se for um arquivo, adiciona à lista
        if isfile(join(dir, f)):
            arquivo_list.append(join(dir, f))
        
        # Se for um diretório, chama a função recursivamente e adiciona os resultados à lista
        elif isdir(join(dir, f)):
            arquivo_list += dsa_lista_arquivos(join(dir, f))
    
    # Retorna a lista de arquivos
    return arquivo_list

# Define a função que carrega o texto de um arquivo Word
def dsa_carrega_texto_word(arquivoname):
    
    # Abre o arquivo Word
    doc = docx.Document(arquivoname)
    
    # Extrai o texto de cada parágrafo e adiciona à lista
    fullText = [para.text for para in doc.paragraphs]
    
    # Junta todos os textos em uma única string separada por quebras de linha
    return '\n'.join(fullText)

# Define a função que carrega o texto de um arquivo PowerPoint
def dsa_carrega_texto_pptx(arquivoname):
    
    # Abre o arquivo PowerPoint
    prs = Presentation(arquivoname)
    
    # Inicializa uma lista vazia para armazenar os textos
    fullText = []
    
    # Itera sobre todos os slides
    for slide in prs.slides:
        
        # Itera sobre todas as formas no slide
        for shape in slide.shapes:
            
            # Se a forma tiver o atributo "text", adiciona o texto à lista
            if hasattr(shape, "text"):
                fullText.append(shape.text)
    
    # Junta todos os textos em uma única string separada por quebras de linha
    return '\n'.join(fullText)

# Define a função principal para indexação dos documentos
def main_indexing(mypath):
    
    # Define o nome do modelo a ser usado para criar as embeddings
    model_name = "sentence-transformers/msmarco-bert-base-dot-v5"
    
    # Define as configurações do modelo
    model_kwargs = {'device': 'cpu'}
    
    # Define as configurações de codificação
    encode_kwargs = {'normalize_embeddings': True}

    # Inicializa a classe de embeddings do HuggingFace
    hf = HuggingFaceEmbeddings(model_name = model_name,
                               model_kwargs = model_kwargs,
                               encode_kwargs = encode_kwargs)

    # Inicializa o cliente Qdrant
    client = QdrantClient("http://qdrant:6333")
    
    # Define o nome da coleção de embeddings
    collection_name = "DSAVectorDB"

    # Se a coleção já existir, exclui
    if client.collection_exists(collection_name):
        client.delete_collection(collection_name)

    # Cria uma nova coleção com parâmetros especificados
    client.create_collection(collection_name, 
                             vectors_config = VectorParams(size = 768, distance = Distance.DOT))

    # Inicializa a instância Qdrant
    qdrant = Qdrant(client, collection_name, hf)

    # Imprime mensagem informando que a indexação dos documentos está iniciando
    print("\nIndexando os documentos...\n")

    # Obtém a lista de todos os arquivos no diretório especificado
    lista_arquivos = dsa_lista_arquivos(mypath)
    
    # Itera sobre cada arquivo na lista
    for arquivo in lista_arquivos:
        
        try:
            
            # Inicializa uma string vazia para armazenar o conteúdo do arquivo
            arquivo_content = ""
            
            # Verifica se o arquivo é um PDF
            if arquivo.endswith(".pdf"):
                
                print("Indexando: " + arquivo)
                
                reader = PyPDF2.PdfReader(arquivo)
                
                for page in reader.pages:
                    arquivo_content += " " + page.extract_text()
            
            # Verifica se o arquivo é um texto simples
            elif arquivo.endswith(".txt"):
                
                print("Indexando: " + arquivo)
                
                with open(arquivo, 'r') as f:
                    arquivo_content = f.read()
            
            # Verifica se o arquivo é um Word
            elif arquivo.endswith(".docx"):
                
                print("Indexando: " + arquivo)
                
                arquivo_content = dsa_carrega_texto_word(arquivo)
            
            # Verifica se o arquivo é um PowerPoint
            elif arquivo.endswith(".pptx"):
                
                print("Indexando: " + arquivo)
                
                arquivo_content = dsa_carrega_texto_pptx(arquivo)
            
            else:
                
                # Se o arquivo não for de um formato suportado, continua para o próximo arquivo
                continue

            # Inicializa o divisor de texto com tamanho de chunk e sobreposição especificados
            text_splitter = TokenTextSplitter(chunk_size = 500, chunk_overlap = 50)
            
            # Divide o conteúdo do arquivo em chunks de texto
            textos = text_splitter.split_text(arquivo_content)
            
            # Cria metadados para cada chunk de texto
            # Isso permite que o LLM cite a referência
            metadata = [{"path": arquivo} for _ in textos]
            
            # Adiciona os textos e seus metadatas ao Qdrant
            qdrant.add_texts(textos, metadatas = metadata)

        except Exception as e:

            # Se ocorrer um erro, imprime uma mensagem de erro
            print(f"O processo falhou para o arquivo {arquivo}: {e}")

    # Imprime mensagem informando que a indexação foi concluída
    print("\nIndexação Concluída!\n")

# Verifica se o script está sendo executado diretamente
if __name__ == "__main__":

    # Obtém os argumentos da linha de comando
    arguments = sys.argv
    
    # Verifica se foi fornecido um caminho de diretório
    if len(arguments) > 1:
        main_indexing(arguments[1])
    else:
        # Se não, imprime uma mensagem de erro
        print("Você precisa fornecer um caminho para a pasta com documentos para indexar.")




