#!/usr/bin/env python3
"""
Create the PostgreSQL database from .streamlit/secrets.toml (before running Streamlit).

Connects to the maintenance DB (default: postgres), creates [postgres].dbname if missing,
then optionally runs data/schema.sql.

Usage (from project root):
  python scripts/init_db.py              # create DB + apply schema
  python scripts/init_db.py --db-only  # only CREATE DATABASE
  python scripts/init_db.py --schema-only
"""

from __future__ import annotations

import argparse
import sys
import tomllib
from pathlib import Path

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

ROOT = Path(__file__).resolve().parent.parent
SECRETS_PATH = ROOT / ".streamlit" / "secrets.toml"
SCHEMA_PATH = ROOT / "data" / "schema.sql"


def load_postgres_secrets() -> dict:
    if not SECRETS_PATH.is_file():
        print(f"Missing secrets file: {SECRETS_PATH}", file=sys.stderr)
        print("Create .streamlit/secrets.toml with a [postgres] section (host, dbname, user, password, port).", file=sys.stderr)
        sys.exit(1)
    with SECRETS_PATH.open("rb") as f:
        data = tomllib.load(f)
    pg = data.get("postgres")
    if not isinstance(pg, dict):
        print("secrets.toml must contain a [postgres] table.", file=sys.stderr)
        sys.exit(1)
    required = ("host", "dbname", "user", "port")
    for key in required:
        if key not in pg:
            print(f"secrets [postgres] is missing required key: {key}", file=sys.stderr)
            sys.exit(1)
    return pg


def connect_db(database: str, pg: dict):
    return psycopg2.connect(
        host=pg["host"],
        database=database,
        user=pg["user"],
        password=pg.get("password") or "",
        port=int(pg["port"]),
    )


def database_exists(cur, name: str) -> bool:
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (name,))
    return cur.fetchone() is not None


def ensure_database(pg: dict, maintenance_db: str) -> None:
    target = pg["dbname"]
    conn = connect_db(maintenance_db, pg)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    try:
        with conn.cursor() as cur:
            if database_exists(cur, target):
                print(f"Database {target!r} already exists — skipping CREATE DATABASE.")
            else:
                cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(target)))
                print(f"Created database {target!r}.")
    finally:
        conn.close()


def iter_sql_statements(sql_text: str):
    """Split schema file into executable statements; drop full-line and simple inline -- comments."""
    cleaned_lines: list[str] = []
    for raw in sql_text.splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("--"):
            continue
        if "--" in raw:
            base = raw.split("--", 1)[0].rstrip()
            if base.strip():
                cleaned_lines.append(base)
        else:
            cleaned_lines.append(raw.rstrip())
    blob = "\n".join(cleaned_lines)
    for part in blob.split(";"):
        stmt = part.strip()
        if stmt:
            yield stmt


def apply_schema(pg: dict) -> None:
    if not SCHEMA_PATH.is_file():
        print(f"Schema file not found: {SCHEMA_PATH}", file=sys.stderr)
        sys.exit(1)
    sql_text = SCHEMA_PATH.read_text(encoding="utf-8")
    statements = list(iter_sql_statements(sql_text))
    conn = connect_db(pg["dbname"], pg)
    try:
        with conn.cursor() as cur:
            for stmt in statements:
                cur.execute(stmt)
        conn.commit()
        print(f"Applied {len(statements)} statements from data/schema.sql.")
    except Exception as e:
        conn.rollback()
        print(f"Schema apply failed: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Create CareerOps PostgreSQL database and/or apply schema.")
    parser.add_argument("--db-only", action="store_true", help="Only CREATE DATABASE (no schema.sql)")
    parser.add_argument("--schema-only", action="store_true", help="Only run schema.sql (database must exist)")
    parser.add_argument(
        "--maintenance-db",
        default="postgres",
        help="Existing database to connect to for CREATE DATABASE (default: postgres)",
    )
    args = parser.parse_args()
    if args.db_only and args.schema_only:
        print("Use only one of --db-only and --schema-only.", file=sys.stderr)
        sys.exit(1)

    pg = load_postgres_secrets()

    if args.schema_only:
        apply_schema(pg)
        return

    ensure_database(pg, args.maintenance_db)
    if not args.db_only:
        apply_schema(pg)


if __name__ == "__main__":
    main()
