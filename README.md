# CareerOps – The Autonomous Career Command Center

A modern SaaS dashboard UI for resume tailoring and job application tracking.

**Tech stack:** Streamlit, Pandas, Plotly, PostgreSQL (psycopg2).

## Prerequisites

- **Python 3.11+** (uses `tomllib` for `scripts/init_db.py`)
- **PostgreSQL** running locally (or reachable from your machine), e.g. Homebrew `postgresql@16` or Postgres.app
- **pgAdmin** (optional) — useful for inspecting databases and running SQL by hand

## Run the app (first time)

From the repository root (the folder that contains `app.py`):

### 1. Virtual environment (recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure database credentials

Copy the example secrets file and edit it to match your PostgreSQL user, host, and the database name you want:

```bash
cp .streamlit/secrets.example.toml .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml`: set `user`, `password`, `host`, `port`, and `dbname` (e.g. `careerops`). The `dbname` value is the database the app will use; it does not need to exist yet.

### 4. Create the database and tables

This connects to the maintenance database `postgres`, creates `[postgres].dbname` if missing, then runs `data/schema.sql`:

```bash
python scripts/init_db.py
```

Use `python scripts/init_db.py --db-only` to only create the database, or `--schema-only` if the database already exists and you only need tables.

### 5. Start Streamlit

```bash
streamlit run app.py
```

Open the URL shown in the terminal (typically [http://localhost:8501](http://localhost:8501)).

### 6. Verify the database (optional)

In the app, open **Settings** and use **Test Database Connection**. **Master Profile** requires a working PostgreSQL connection to load and save candidates.

## Run the app (after setup)

```bash
source .venv/bin/activate   # if you use a venv
streamlit run app.py
```

## Structure

- **app.py** – Entry point; sidebar navigation and page routing
- **config.py** – Session state keys and app config
- **pages/** – Dashboard, Generate Resume, Applications, Analytics, Master Profile, Settings
- **components/** – Reusable KPI cards, Kanban, timeline, charts
- **data/mock_data.py** – Dummy data for views that do not use the database
- **data/db_utils.py** – PostgreSQL connection and queries (reads `.streamlit/secrets.toml`)
- **data/schema.sql** – Table definitions for Master Profile
- **scripts/init_db.py** – Create database and apply schema before first run

## Future

Resume generation, richer persistence beyond the master profile, and PDF export can be extended on top of the current stack.
