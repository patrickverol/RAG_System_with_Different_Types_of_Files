# Projeto 7 - Deploy de Aplicação de IA Generativa com Airflow, LLM, RAG, ElasticSearch e Grafana

# Importa a biblioteca psycopg2 para conectar-se ao banco de dados PostgreSQL
import psycopg2

# Importa RealDictCursor para retornar resultados como dicionários, facilitando o acesso aos dados pelo nome da coluna
from psycopg2.extras import RealDictCursor

# Função para estabelecer a conexão com o banco de dados PostgreSQL
def postgre_connection():
    
    # Cria a conexão com o banco de dados PostgreSQL, especificando o nome do banco, usuário, senha, host e porta
    conn = psycopg2.connect(
        dbname="airflow",
        user="airflow",
        password="airflow",
        host="postgres", 
        port="5432"
    )

    # Cria um cursor para executar consultas, usando RealDictCursor para resultados em formato de dicionário
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Retorna a conexão e o cursor para uso na aplicação
    return conn, cur
