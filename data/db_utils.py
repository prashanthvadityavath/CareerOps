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
                results = [dict(row) for row in cur.fetchall()]
                return results  # No commit needed for a read-only SELECT
            else:
                conn.commit()
                return []
    except psycopg2.Error as e:
        conn.rollback()
        st.error(f"Query failed: {e.pgerror or str(e)}")
        return []


# ---------------------------------------------------------------------------
# Profile fetcher
# ---------------------------------------------------------------------------

def get_full_candidate_profile(candidate_id: int) -> dict | None:
    """
    Fetches the complete profile for a candidate across all tables.
    Returns a dictionary containing basic info and lists of related records.
    """
    candidate = run_query("SELECT * FROM candidate WHERE id = %s", (candidate_id,))
    if not candidate:
        return None
        
    profile = candidate[0]
    
    # Fetch related tables
    profile["skills"] = run_query("SELECT * FROM technical_skills WHERE candidate_id = %s", (candidate_id,))
    profile["experience"] = run_query("SELECT * FROM work_experience WHERE candidate_id = %s ORDER BY start_date DESC NULLS FIRST", (candidate_id,))
    profile["education"] = run_query("SELECT * FROM education WHERE candidate_id = %s ORDER BY end_year DESC NULLS FIRST", (candidate_id,))
    profile["projects"] = run_query("SELECT * FROM projects WHERE candidate_id = %s ORDER BY start_date DESC NULLS FIRST", (candidate_id,))
    profile["certifications"] = run_query("SELECT * FROM certifications WHERE candidate_id = %s ORDER BY issue_date DESC NULLS FIRST", (candidate_id,))
    
    return profile

# ---------------------------------------------------------------------------
# Tracking (Applications & Activity)
# ---------------------------------------------------------------------------

def setup_tracking_tables() -> None:
    """Creates applications and activity_log tables if they don't exist."""
    run_query("""
        CREATE TABLE IF NOT EXISTS applications (
            id SERIAL PRIMARY KEY,
            candidate_id INTEGER REFERENCES candidate(id) ON DELETE CASCADE,
            company VARCHAR(255),
            role VARCHAR(255),
            resume_tag VARCHAR(255),
            match_score INTEGER,
            column_id VARCHAR(50) DEFAULT 'saved',
            date_applied DATE DEFAULT CURRENT_DATE,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """, fetch_results=False)
    
    run_query("""
        CREATE TABLE IF NOT EXISTS activity_log (
            id SERIAL PRIMARY KEY,
            candidate_id INTEGER REFERENCES candidate(id) ON DELETE CASCADE,
            event_type VARCHAR(50),
            label TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """, fetch_results=False)

def get_applications(candidate_id: int) -> list[dict]:
    return run_query("""
        SELECT id, company, role, resume_tag, match_score, column_id, 
               to_char(date_applied, 'YYYY-MM-DD') as date_applied 
        FROM applications 
        WHERE candidate_id = %s 
        ORDER BY updated_at DESC
    """, (candidate_id,))

def move_application(app_id: int, column_id: str) -> None:
    run_query("""
        UPDATE applications SET column_id = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s
    """, (column_id, app_id), fetch_results=False)

def create_application(candidate_id: int, company: str, role: str, resume_tag: str, match_score: int, column_id: str = 'saved') -> None:
    run_query("""
        INSERT INTO applications (candidate_id, company, role, resume_tag, match_score, column_id, date_applied)
        VALUES (%s, %s, %s, %s, %s, %s, CURRENT_DATE)
    """, (candidate_id, company, role, resume_tag, match_score, column_id), fetch_results=False)

def log_activity(candidate_id: int, event_type: str, label: str) -> None:
    run_query("""
        INSERT INTO activity_log (candidate_id, event_type, label, timestamp)
        VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
    """, (candidate_id, event_type, label), fetch_results=False)

def get_activity_timeline(candidate_id: int, limit: int = 10) -> list[dict]:
    return run_query("""
        SELECT event_type as type, label, to_char(timestamp, 'Mon DD at HH24:MI') as timestamp 
        FROM activity_log 
        WHERE candidate_id = %s 
        ORDER BY timestamp DESC 
        LIMIT %s
    """, (candidate_id, limit))