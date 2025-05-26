# Projeto 9 - IA Generativa e RAG Para App de Sistema Inteligente de Busca em Documentos - Backend e API
# Módulo da API

# Importa o módulo os
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Importa a classe FastAPI do módulo fastapi para criar a API
from fastapi import FastAPI

# Importa a classe Qdrant do módulo langchain_qdrant para instanciar o banco vetorial
from langchain_qdrant import Qdrant

# Importa a classe QdrantClient do módulo qdrant_client para conectar no banco vetorial
from qdrant_client import QdrantClient

# Importa a classe BaseModel do módulo pydantic para validar os dados enviados para a API
from pydantic import BaseModel

# Importa a classe HuggingFaceEmbeddings do módulo langchain_huggingface para gerar as embeddings
from langchain_huggingface import HuggingFaceEmbeddings

# Define a classe Item que herda de BaseModel
class Item(BaseModel):
    query: str

# Define o nome do modelo (tokenizador)
model_name = "sentence-transformers/msmarco-bert-base-dot-v5"

# Define os argumentos do modelo
model_kwargs = {'device': 'cpu'}

# Define os argumentos de codificação
encode_kwargs = {'normalize_embeddings': True}

# Cria uma instância de HuggingFaceEmbeddings
hf = HuggingFaceEmbeddings(
    model_name = model_name,
    model_kwargs = model_kwargs,
    encode_kwargs = encode_kwargs)

# Define a variável use_nvidia_api como False
use_nvidia_api = False

# Verifica se a chave da Nvidia está disponível
nvidia_key = os.getenv('NVIDIA_KEY')
if nvidia_key:

    # Importa a classe OpenAI do módulo openai
    from openai import OpenAI
    
    # Cria uma instância de OpenAI com a URL base e a chave da API
    client_ai = OpenAI(base_url = "https://integrate.api.nvidia.com/v1", api_key = nvidia_key)

    # Define use_nvidia_api como True
    use_nvidia_api = True

else:

    # Imprime uma mensagem indicando que não é possível usar um LLM
    print("Não é possível usar um LLM. NVIDIA_KEY não encontrada nas variáveis de ambiente.")

# Cria uma instância para conectar ao banco vetorial
client = QdrantClient("http://qdrant:6333")

# Define o nome da coleção
collection_name = "DSAVectorDB"

# Cria uma instância de Qdrant para enviar os dados para o banco vetorial
qdrant = Qdrant(client, collection_name, hf)

# Cria uma instância de FastAPI
app = FastAPI()

# Define a rota raiz com o método GET
@app.get("/")
async def root():
    return {"message": "DSA Projeto 9"}

# Define a rota /dsa_api com o método POST
@app.post("/dsa_api")
async def dsa_api(item: Item):

    # Obtém a query do item
    query = item.query
    
    # Realiza a busca de similaridade
    search_result = qdrant.similarity_search(query = query, k = 10)
    
    # Inicializa a lista de resultados, contexto e mapeamento
    list_res = []
    context = ""
    mappings = {}
    
    # Constrói o contexto e a lista de resultados
    for i, res in enumerate(search_result):
        context += f"{i}\n{res.page_content}\n\n"
        mappings[i] = res.metadata.get("path")
        list_res.append({"id": i, "path": res.metadata.get("path"), "content": res.page_content})

    # Define a mensagem de sistema
    rolemsg = {"role": "system",
               "content": "Responda à pergunta do usuário usando documentos fornecidos no contexto. No contexto estão documentos que devem conter uma resposta. Sempre faça referência ao ID do documento (entre colchetes, por exemplo [0],[1]) do documento que foi usado para fazer uma consulta. Use quantas citações e documentos forem necessários para responder à pergunta."}
    
    # Define as mensagens
    messages = [rolemsg, {"role": "user", "content": f"Documents:\n{context}\n\nQuestion: {query}"}]
    
    # Verifica se a API da Nvidia está sendo usada
    if use_nvidia_api:

        # Cria a instância do LLM usando a API da Nvidia
        resposta = client_ai.chat.completions.create(model = "meta/llama3-70b-instruct",
                                                     messages = messages,
                                                     temperature = 0.5,
                                                     top_p = 1,
                                                     max_tokens = 1024,
                                                     stream = False)
        
        # Obtém a resposta do LLM
        response = resposta.choices[0].message.content
    
    else:

        # Imprime uma mensagem indicando que não é possível usar um LLM
        print("Não é possível usar um LLM.")
    
    return {"context": list_res, "answer": response}




