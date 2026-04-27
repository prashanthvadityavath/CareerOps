# 🚀 CareerOps – The Autonomous Career Command Center

CareerOps is a modern, AI-powered SaaS dashboard built to revolutionize how job seekers manage their career search. It combines dynamic resume tailoring, intelligent job matching, and comprehensive application tracking into a single, seamless platform.

Whether you are an **End User** trying to land your dream job or a **Developer** looking to contribute to a full-stack Python AI application, this guide has you covered.

---

## 🌟 Features (For Users)

CareerOps acts as your personal AI recruiter and career coach.

*   **🎭 Multi-Profile Management:** Manage different master candidate profiles. Perfect if you are applying for distinctly different roles (e.g., Data Scientist vs. Software Engineer).
*   **🤖 AI Resume Tailoring:** Paste a job description and let AI (Gemini, OpenAI, Grok, Qwen, or local Ollama models) rewrite your master resume to highlight the most relevant skills.
*   **📊 Match Scoring & Analysis:** Automatically calculate a "Match Score" between your profile and a job description. Get actionable insights on missing keywords and a checklist of requirements.
*   **📋 Kanban Application Tracking:** Visually track your job applications through customizable stages (`Saved`, `Applied`, `Interviewing`, `Offered`, `Rejected`).
*   **🎯 Daily Goals & Analytics:** Set daily application goals, monitor your conversion rates via dynamic Sparklines, and view a rich timeline of your recent job search activity.

---

## 🛠️ Architecture & Tech Stack (For Developers)

CareerOps is built using a pure Python full-stack approach, leveraging Streamlit for the frontend UI, PostgreSQL for data persistence, and LangChain for agentic AI workflows.

### Tech Stack
*   **Frontend / UI:** Streamlit (with custom injected CSS for a modern, sticky-header SaaS look).
*   **Backend Logic:** Python 3.11+
*   **Database:** PostgreSQL (accessed via `psycopg2` with automatic connection pooling and reconnects).
*   **AI Integration:** LangChain, Google Generative AI SDK, OpenAI SDK, Groq SDK. Supports cloud models and local inference via Ollama.
*   **Data Viz:** Pandas and Plotly (for analytics and dashboard sparklines).

### Database Schema Highlights
The PostgreSQL database is fully relational. Key tables include:
*   `candidate`: The master profile entity.
*   *Profile Data:* `technical_skills`, `work_experience`, `education`, `projects`, `certifications` (all foreign keyed to `candidate`).
*   `applications`: Tracks individual job applications, associated match scores, and current Kanban `column_id`.
*   `activity_log`: An audit trail of user actions (e.g., status changes, profile creations) for the timeline view.

### AI Agentic Workflow (`intelligence/agents.py`)
CareerOps uses LangChain to string together expert AI personas:
1.  **Extractor Agent:** Parses raw job descriptions into structured `Company` and `Role` JSON.
2.  **Matcher Agent:** Calculates a 0-100 match score and identifies missing keywords.
3.  **Researcher Agent:** Summarizes company culture and recent trends.
4.  **Writer Agent:** Rewrites the resume using the missing keywords and company research, maintaining factual accuracy and Markdown formatting.

---

## ⚙️ Setup & Installation

Follow these steps to get a local development environment running.

### Prerequisites
- **Python 3.11+** installed.
- **PostgreSQL** running locally (e.g., via Homebrew `postgresql@16`, Postgres.app, or Docker).
- API Keys for your preferred AI models (can be configured in the app UI later).

### 1. Clone & Create Virtual Environment

```bash
git clone <your-repo-url>
cd CareerOps
python3 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Database Configuration

CareerOps uses Streamlit's secrets management for database credentials.

```bash
cp .streamlit/secrets.example.toml .streamlit/secrets.toml
```

Open `.streamlit/secrets.toml` and configure your local PostgreSQL credentials:
```toml
[postgres]
host = "localhost"
port = 5432
dbname = "careerops"
user = "postgres"
password = "your_password"
```
*(Note: The database `careerops` does not need to exist yet; the initialization script will create it.)*

### 4. Initialize Database & Schema

Run the database initialization script to create the DB and apply `data/schema.sql`:

```bash
python scripts/init_db.py
```

*Optional Flags:*
*   `--db-only`: Only run `CREATE DATABASE`.
*   `--schema-only`: Only apply the schema (useful if you created the DB manually).

### 5. Run the Application

```bash
streamlit run app.py
```
The app will open automatically in your browser at `http://localhost:8501`.

---

## 📁 Project Structure

```text
CareerOps/
├── app.py                     # Main application entry point & routing
├── config.py                  # Global configurations and Session State keys
├── components/                # Reusable Streamlit UI components
│   ├── header.py              # Sticky top nav & daily goal progress
│   ├── kanban.py              # Kanban board cards and logic
│   ├── kpi_card.py            # Dashboard metrics with Sparklines
│   └── timeline.py            # Activity history feed
├── data/
│   ├── db_utils.py            # Postgres connection pool and CRUD operations
│   └── schema.sql             # SQL definitions for all database tables
├── intelligence/              # AI and LLM logic
│   ├── agents.py              # LangChain agent chains and Pydantic models
│   └── llm_matcher.py         # Direct API wrappers for Gemini, OpenAI, Ollama
├── pages/                     # Application Screens
│   ├── dashboard.py           # Home screen (KPIs, Pipeline, Activity)
│   ├── applications.py        # Full-page Kanban view
│   ├── generate_resume.py     # AI tailoring workflow
│   ├── analytics.py           # Deep-dive charts
│   ├── master_profile.py      # Candidate CRUD UI
│   └── settings.py            # API key management and DB tests
├── scripts/
│   └── init_db.py             # Database creation script
└── .streamlit/
    ├── config.toml            # Streamlit theme config
    ├── secrets.toml           # (Git ignored) Database & API secrets
    └── style.css              # Custom global CSS injections
```

---

## 🔐 Security & Secrets

API Keys and Database credentials should **never** be committed to version control.
*   **API Keys** can be entered directly in the `Settings` page of the UI (saved to a local `user_keys.json`), added to `.streamlit/secrets.toml`, or exported as standard environment variables (e.g., `OPENAI_API_KEY`).
*   **PostgreSQL credentials** must live strictly in `.streamlit/secrets.toml`.

---

## 🗺️ Roadmap & Future Enhancements

- [ ] **PDF Export:** Allow users to export the AI-generated tailored resumes directly to cleanly formatted PDFs.
- [ ] **Email Integration:** Connect via IMAP/Gmail API to automatically move Kanban cards based on interview invite emails.
- [ ] **Browser Extension:** A companion Chrome extension to parse job descriptions directly from LinkedIn/Indeed and send them to the CareerOps database.
- [ ] **Advanced Agentic Research:** Grant the Research Agent direct web-search capabilities (e.g., via Tavily or SerpAPI) for real-time company news.
