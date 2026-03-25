
import psycopg2
import psycopg2.extras
import streamlit as st

@st.cache_resource
def init_connection():
    """Initialize and cache the PostgreSQL connection."""
    try:
        conn = psycopg2.connect(
            host=st.secrets["postgres"]["host"],
            database=st.secrets["postgres"]["dbname"],
            user=st.secrets["postgres"]["user"],
            password=st.secrets["postgres"]["password"],
            port=st.secrets["postgres"]["port"]
        )
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

def run_query(query, params=None, fetch_results=True):
    """Execute a query and optionally return results as dictionaries."""
    conn = init_connection()
    if conn is None:
        return []
    
    # Use RealDictCursor to return rows as dictionaries (like JSON)
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        try:
            cur.execute(query, params)
            if fetch_results:
                results = cur.fetchall()
            else:
                conn.commit()
                results = []
            return results
        except Exception as e:
            conn.rollback()
            st.error(f"Query failed: {e}")
            return []