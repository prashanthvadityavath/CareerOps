"""
PostgreSQL connection and query execution for CareerOps.
Uses a cached connection pool with automatic reconnection on stale connections.
"""
import psycopg2
import psycopg2.extras
import streamlit as st


# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------

@st.cache_resource
def _get_connection_pool():
    """
    Create and cache a psycopg2 connection using Streamlit secrets.
    Returns the connection or None if credentials are missing/invalid.
    """
    try:
        conn = psycopg2.connect(
            host=st.secrets["postgres"]["host"],
            dbname=st.secrets["postgres"]["dbname"],
            user=st.secrets["postgres"]["user"],
            password=st.secrets["postgres"]["password"],
            port=st.secrets["postgres"]["port"],
            connect_timeout=5,
            # Keep connection alive across idle periods
            keepalives=1,
            keepalives_idle=30,
            keepalives_interval=10,
            keepalives_count=5,
        )
        return conn
    except psycopg2.OperationalError as e:
        st.error(
            f"Could not connect to PostgreSQL. "
            f"Check your `.streamlit/secrets.toml` credentials. Detail: {e}"
        )
        return None


def _get_conn():
    """
    Return a healthy connection, reconnecting automatically if the cached
    connection has gone stale (e.g. after a server-side idle timeout).
    """
    conn = _get_connection_pool()
    if conn is None:
        return None
    try:
        # Cheapest possible liveness check — no round-trip needed
        conn.isolation_level  # raises if connection is closed
        if conn.closed:
            raise psycopg2.OperationalError("Connection closed.")
    except Exception:
        # Clear the cached resource and force a fresh connection next call
        st.cache_resource.clear()
        conn = _get_connection_pool()
    return conn


# ---------------------------------------------------------------------------
# Query runner
# ---------------------------------------------------------------------------

def run_query(
    query: str,
    params: tuple | None = None,
    fetch_results: bool = True,
) -> list[dict]:
    """
    Execute a parameterized SQL query.

    Args:
        query:         SQL string with %s placeholders.
        params:        Tuple of values to bind. Never use f-strings for this.
        fetch_results: If True, return rows as a list of dicts.
                       If False, commit the write and return [].

    Returns:
        List of dicts (RealDictRow) for SELECT queries, [] for writes or errors.
    """
    conn = _get_conn()
    if conn is None:
        return []

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, params)
            if fetch_results:
                return [dict(row) for row in cur.fetchall()]
            else:
                conn.commit()
                return []
    except psycopg2.Error as e:
        conn.rollback()
        st.error(f"Query failed: {e.pgerror or str(e)}")
        return []