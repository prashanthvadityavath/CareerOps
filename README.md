# CareerOps – The Autonomous Career Command Center

A modern SaaS dashboard UI for resume tailoring and job application tracking.

**Tech stack:** Streamlit, Pandas, Plotly.

## Run locally

```bash
cd CareerOps
pip install -r requirements.txt
streamlit run app.py
```

Then open the URL shown in the terminal (typically http://localhost:8501).

**Secrets:** If you add API keys or env-specific config later, put them in `.streamlit/secrets.toml` (this file is gitignored).

## Structure

- **app.py** – Entry point; sidebar navigation and page routing
- **config.py** – Session state keys and app config
- **pages/** – Dashboard, Generate Resume, Applications, Analytics, Master Profile, Settings
- **components/** – Reusable KPI cards, Kanban, timeline, charts
- **data/mock_data.py** – Dummy data for all views

## Future

Backend integration is planned for real resume generation, persistence, and PDF export.
