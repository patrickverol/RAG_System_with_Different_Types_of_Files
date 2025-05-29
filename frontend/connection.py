"""
This module handles database connections for the application.
"""

# Import psycopg2 for PostgreSQL database connection
import psycopg2

# Import RealDictCursor for dictionary-style result access
from psycopg2.extras import RealDictCursor


def postgre_connection():
    """
    Establish a connection to the PostgreSQL database.
    
    Returns:
        tuple: A tuple containing:
            - conn: PostgreSQL connection object
            - cur: Database cursor using RealDictCursor for dictionary-style results
    """
    
    # Create connection to PostgreSQL database
    conn = psycopg2.connect(
        dbname="admin",
        user="admin",
        password="admin",
        host="postgres", 
        port="5432"
    )

    # Create cursor with RealDictCursor for dictionary-style results
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Return connection and cursor for application use
    return conn, cur
