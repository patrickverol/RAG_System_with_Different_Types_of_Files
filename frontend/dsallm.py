# Projeto 7 - Deploy de Aplicação de IA Generativa com Airflow, LLM, RAG, ElasticSearch e Grafana

# Imports
import hashlib
from dsaconnection import postgre_connection

# Função para gerar um ID único para o documento, combinando a consulta do usuário e a resposta gerada
def dsa_gera_documento_id(userQuery, answer):

    # Combina as primeiras 10 letras da consulta e da resposta para criar uma string única
    combined = f"{userQuery[:10]}-{answer[:10]}"
    
    # Gera um hash MD5 da string combinada
    hash_object = hashlib.md5(combined.encode())
    
    # Converte o hash em hexadecimal
    hash_hex = hash_object.hexdigest()
    
    # Extrai os primeiros 8 caracteres do hash para usar como ID do documento
    document_id = hash_hex[:8]
    
    # Retorna o ID do documento
    return document_id

# Função para capturar a entrada do usuário e salvar os dados de avaliação no banco de dados
def dsa_captura_user_input(docId, userQuery, result, llmScore, responseTime):

    # Estabelece a conexão e o cursor com o banco de dados PostgreSQL
    conn, cur = postgre_connection()
    
    try:
        # Define a query SQL para criar a tabela de avaliação, se ainda não existir
        create = """
            CREATE TABLE dsa_avaliacao (
                id SERIAL PRIMARY KEY,
                doc_id VARCHAR(10) NOT NULL,
                user_input TEXT NOT NULL,
                result TEXT NOT NULL,
                llm_score DOUBLE PRECISION NOT NULL,
                response_time DOUBLE PRECISION NOT NULL,
                created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """

        # Executa a query de criação da tabela
        cur.execute(create)

    except Exception as e:
        # Em caso de erro, imprime a exceção e desfaz a transação
        print(e)
        conn.rollback() 

    try:

        # Define a query SQL para inserir os dados de avaliação na tabela
        sql = f"""
            INSERT INTO dsa_avaliacao
            (doc_id, user_input, result, llm_score, response_time)
            VALUES
            ('{docId}', '{userQuery}', '{result}', {llmScore}, {responseTime})
        """

        # Executa a query de inserção
        cur.execute(sql)

    except Exception as e:
        # Em caso de erro, imprime a exceção e desfaz a transação
        print(e)
        conn.rollback() 

    # Confirma as operações e fecha a conexão com o banco de dados
    conn.commit()
    cur.close()
    conn.close()
    
    # Retorna uma mensagem de confirmação da inserção
    return "Dados de Avaliação Inseridos"

# Função para capturar o feedback do usuário e salvar no banco de dados
def dsa_captura_user_feedback(docId, userQuery, result, feedback):

    # Estabelece a conexão e o cursor com o banco de dados PostgreSQL
    conn, cur = postgre_connection()
    
    try:

        # Define a query SQL para criar a tabela de feedback, se ainda não existir
        create = """
            CREATE TABLE dsa_feedback (
                id SERIAL PRIMARY KEY,
                doc_id VARCHAR(10) NOT NULL,
                user_input TEXT NOT NULL,
                result TEXT NOT NULL,
                is_satisfied BOOLEAN NOT NULL,
                created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """

        # Executa a query de criação da tabela
        cur.execute(create)

    except Exception as e:
        # Em caso de erro, imprime a exceção e desfaz a transação
        print(e)
        conn.rollback() 

    try:

        # Define a query SQL para inserir os dados de feedback na tabela
        sql = f"""
            INSERT INTO dsa_feedback
            (doc_id, user_input, result, is_satisfied)
            VALUES
            ('{docId}', '{userQuery}', '{result}', {feedback})
        """

        # Executa a query de inserção
        cur.execute(sql)

    except Exception as e:
        # Em caso de erro, imprime a exceção e desfaz a transação
        print(e)
        conn.rollback() 

    # Confirma as operações e fecha a conexão com o banco de dados
    conn.commit()
    cur.close()
    conn.close()

    # Retorna uma mensagem de confirmação da inserção
    return "Dados de Feedback Inseridos"
