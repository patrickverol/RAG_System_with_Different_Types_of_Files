# Projeto 10 - IA Generativa e RAG Para App de Sistema Inteligente de Busca em Documentos - Frontend
# Módulo da Interface Web e Consulta à API

# Importa o módulo re de expressão regular
import re

# Importa o módulo streamlit com o alias st
import streamlit as st

# Importa o módulo requests
import requests

# Importa o módulo json
import json

# Importa o módulo time
import time

# Filtra warnings
import warnings
warnings.filterwarnings('ignore')

# Importa módulos para avaliação e feedback
from dsallm import dsa_gera_documento_id, dsa_captura_user_input, dsa_captura_user_feedback


def main():
    # Configurando o título da página e outras configurações (favicon)
    st.set_page_config(page_title="DSA Projeto 10", page_icon=":100:", layout="centered")

    # Define o título do aplicativo Streamlit
    st.title('_:green[DSA - Projeto 10]_')
    st.title('_:blue[Busca com IA Generativa e RAG]_')

    # Inicializando variáveis de sessão
    if 'result' not in st.session_state:
        st.session_state.result = None
    if 'docId' not in st.session_state:
        st.session_state.docId = None
    if 'userInput' not in st.session_state:
        st.session_state.userInput = ""
    if 'feedbackSubmitted' not in st.session_state:
        st.session_state.feedbackSubmitted = False

    # Cria uma caixa de texto para entrada de perguntas
    question = st.text_input("Digite Uma Pergunta Para a IA Executar Consulta nos Documentos:", "")

    # Verifica se o botão "Perguntar" foi clicado
    if st.button("Enviar"):
        if not question:
            st.warning("Digite sua pergunta para continuar.")
            return
            
        # Exibe a pergunta feita
        st.write("A pergunta foi: \"", question+"\"")
        
        # Define a URL da API
        url = "http://backend:8000/dsa_api"

        # Cria o payload da requisição em formato JSON
        payload = json.dumps({"query": question})
        
        # Define os cabeçalhos da requisição
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

        # Faz a requisição POST à API
        start_time = time.time()  # Adiciona medição de tempo
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx, 5xx)
            
            # Debug information
            print(f"Response Status Code: {response.status_code}")
            print(f"Response Headers: {response.headers}")
            print(f"Response Content: {response.text[:200]}...")  # Print first 200 chars of response
            
            # Verifica se a resposta está vazia
            if not response.text:
                st.error("A API retornou uma resposta vazia. Verifique o backend.")
                return
                
            # Tenta fazer o parse do JSON
            try:
                response_data = json.loads(response.text)
            except json.JSONDecodeError as e:
                st.error(f"Erro ao decodificar resposta JSON: {str(e)}")
                print(f"Resposta recebida: {response.text}")
                return
                
            end_time = time.time()    # Finaliza medição de tempo
            responseTime = round(end_time - start_time, 2)  # Calcula tempo de resposta

            # Obtém a resposta da API e extrai o texto da resposta à pergunta
            answer = response_data.get("answer")
            if not answer:
                st.error("A resposta da API não contém o campo 'answer'")
                return
                
            score = response_data.get("score", 1.0)  # Obtém score da resposta, usa 1.0 como padrão se não existir

            # Compila uma expressão regular para encontrar referências a documentos
            rege = re.compile("\[Document\ [0-9]+\]|\[[0-9]+\]")
            
            # Encontra todas as referências a documentos na resposta
            m = rege.findall(answer)
            
            # Inicializa uma lista para armazenar os números dos documentos
            num = []
            
            # Extrai os números dos documentos das referências encontradas
            for n in m:
                num = num + [int(s) for s in re.findall(r'\b\d+\b', n)]

            # Exibe a resposta da pergunta usando markdown
            st.markdown(answer)
            
            # Obtém os documentos do contexto da resposta
            documents = response_data.get('context', [])
            
            # Inicializa uma lista para armazenar os documentos que serão exibidos
            show_docs = []
            
            # Adiciona os documentos correspondentes aos números extraídos à lista show_docs
            for n in num:
                for doc in documents:
                    if int(doc['id']) == n:
                        show_docs.append(doc)
                        
            # Inicializa uma variável para o identificador dos botões de download
            dsa_id = 10231718414897291
            
            # Exibe os documentos expandidos com botões de download
            for doc in show_docs:
                
                # Cria um expansor para cada documento
                with st.expander(str(doc['id'])+" - "+doc['path']):
                    
                    # Exibe o conteúdo do documento
                    st.write(doc['content'])
                    
                    # Abre o arquivo do documento e cria um botão de download
                    with open(doc['path'], 'rb') as f:
                        
                        st.download_button("Download do Arquivo", f, file_name = doc['path'].split('/')[-1], key = dsa_id)
                        
                        # Incrementa o identificador do botão para download
                        dsa_id = dsa_id + 1

            # Adiciona avaliação e feedback
            try:
                # Gera um ID de documento
                docId = dsa_gera_documento_id(question, answer)
                
                # Captura entrada do usuário
                dsa_captura_user_input(
                    docId,
                    question.replace("'", ""), 
                    answer, 
                    score,  # Usa o score obtido da API
                    responseTime,  # Usa o tempo de resposta calculado
                )

                # Atualiza o estado da sessão
                st.session_state.result = answer
                st.session_state.docId = docId
                st.session_state.userInput = question.replace("'", "")
                st.session_state.feedbackSubmitted = False

            except Exception as e:
                print(e)
                st.error("Erro ao processar a avaliação. Verifique o Qdrant e tente novamente.")

        except requests.exceptions.RequestException as e:
            st.error(f"Erro na requisição à API: {str(e)}")
        except Exception as e:
            st.error(f"Erro inesperado: {str(e)}")

    # Exibindo o resultado da consulta e feedback fora do bloco do botão Enviar
    if st.session_state.result:
        # Seção de feedback de satisfação
        if not st.session_state.feedbackSubmitted:
            st.write("Você está satisfeito com a resposta?")
            feedback_col1, feedback_col2 = st.columns(2)
            with feedback_col1:
                if st.button("Satisfeito"):
                    dsa_captura_user_feedback(st.session_state.docId, st.session_state.userInput, st.session_state.result, True)
                    st.session_state.feedbackSubmitted = True
                    st.success("Feedback registrado: Satisfeito")
            with feedback_col2:
                if st.button("Não Satisfeito"):
                    dsa_captura_user_feedback(st.session_state.docId, st.session_state.userInput, st.session_state.result, False)
                    st.session_state.feedbackSubmitted = True
                    st.warning("Feedback registrado: Não Satisfeito")

if __name__ == "__main__":
    main()
