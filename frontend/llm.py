"""
This module handles document ID generation, user input capture, and feedback collection.
"""

# Import hashlib for document ID generation
import hashlib

# Import database connection function
from connection import postgre_connection


def gera_documento_id(userQuery: str, answer: str) -> str:
    """
    Generate a unique document ID by combining user query and generated answer.
    
    Args:
        userQuery (str): The user's query text
        answer (str): The generated answer text
        
    Returns:
        str: A unique 8-character document ID generated from MD5 hash
    """
    
    # Combine first 10 characters of query and answer
    combined = f"{userQuery[:10]}-{answer[:10]}"
    
    # Generate MD5 hash of combined string
    hash_object = hashlib.md5(combined.encode())
    
    # Convert hash to hexadecimal
    hash_hex = hash_object.hexdigest()
    
    # Extract first 8 characters for document ID
    document_id = hash_hex[:8]
    
    return document_id


def captura_user_input(docId: str, userQuery: str, result: str, llmScore: float, responseTime: float) -> str:
    """
    Capture user input and save evaluation data to database.
    
    Args:
        docId (str): Document ID
        userQuery (str): User's query text
        result (str): Generated result text
        llmScore (float): LLM model score
        responseTime (float): Response time in seconds
        
    Returns:
        str: Confirmation message
        
    Note:
        Creates avaliacao table if it doesn't exist
    """
    
    # Establish database connection
    conn, cur = postgre_connection()
    
    try:
        # SQL query to create evaluation table if not exists
        create = """
            CREATE TABLE avaliacao (
                id SERIAL PRIMARY KEY,
                doc_id VARCHAR(10) NOT NULL,
                user_input TEXT NOT NULL,
                result TEXT NOT NULL,
                llm_score DOUBLE PRECISION NOT NULL,
                response_time DOUBLE PRECISION NOT NULL,
                created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """

        # Execute table creation query
        cur.execute(create)

    except Exception as e:
        # Print exception and rollback transaction on error
        print(e)
        conn.rollback() 

    try:
        # SQL query to insert evaluation data
        sql = f"""
            INSERT INTO avaliacao
            (doc_id, user_input, result, llm_score, response_time)
            VALUES
            ('{docId}', '{userQuery}', '{result}', {llmScore}, {responseTime})
        """

        # Execute insert query
        cur.execute(sql)

    except Exception as e:
        # Print exception and rollback transaction on error
        print(e)
        conn.rollback() 

    # Commit operations and close database connection
    conn.commit()
    cur.close()
    conn.close()
    
    return "Dados de Avaliação Inseridos"


def captura_user_feedback(docId: str, userQuery: str, result: str, feedback: bool) -> str:
    """
    Capture user feedback and save to database.
    
    Args:
        docId (str): Document ID
        userQuery (str): User's query text
        result (str): Generated result text
        feedback (bool): User satisfaction feedback (True/False)
        
    Returns:
        str: Confirmation message
        
    Note:
        Creates feedback table if it doesn't exist
    """
    
    # Establish database connection
    conn, cur = postgre_connection()
    
    try:
        # SQL query to create feedback table if not exists
        create = """
            CREATE TABLE feedback (
                id SERIAL PRIMARY KEY,
                doc_id VARCHAR(10) NOT NULL,
                user_input TEXT NOT NULL,
                result TEXT NOT NULL,
                is_satisfied BOOLEAN NOT NULL,
                created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """

        # Execute table creation query
        cur.execute(create)

    except Exception as e:
        # Print exception and rollback transaction on error
        print(e)
        conn.rollback() 

    try:
        # SQL query to insert feedback data
        sql = f"""
            INSERT INTO feedback
            (doc_id, user_input, result, is_satisfied)
            VALUES
            ('{docId}', '{userQuery}', '{result}', {feedback})
        """

        # Execute insert query
        cur.execute(sql)

    except Exception as e:
        # Print exception and rollback transaction on error
        print(e)
        conn.rollback() 

    # Commit operations and close database connection
    conn.commit()
    cur.close()
    conn.close()

    return "Dados de Feedback Inseridos"
