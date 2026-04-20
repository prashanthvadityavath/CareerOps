-- CareerOps PostgreSQL schema (run once against the database from secrets.toml)
-- CareerOps PostgreSQL schema (Fresh Install)

-- 1. Candidate Table
CREATE TABLE IF NOT EXISTS candidate (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(50),
    linkedin_url VARCHAR(255),
    github_url VARCHAR(255),
    portfolio_url VARCHAR(255),
    career_objective TEXT,
    professional_summary JSONB,
    profile_name VARCHAR(255) DEFAULT 'Default Profile',
    daily_goal INTEGER DEFAULT 5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Technical Skills Table
CREATE TABLE IF NOT EXISTS technical_skills (
    id SERIAL PRIMARY KEY,
    candidate_id INTEGER REFERENCES candidate(id) ON DELETE CASCADE,
    category VARCHAR(100) NOT NULL,
    skills_list JSONB NOT NULL
);

-- 3. Work Experience Table
CREATE TABLE IF NOT EXISTS work_experience (
    id SERIAL PRIMARY KEY,
    candidate_id INTEGER REFERENCES candidate(id) ON DELETE CASCADE,
    company_name VARCHAR(255) NOT NULL,
    role_title VARCHAR(255) NOT NULL,
    start_date DATE,
    end_date DATE,
    location VARCHAR(255),
    project_name TEXT,
    project_description TEXT,
    role_and_contributions JSONB,
    technologies_utilized JSONB
);

-- 4. Education Table
CREATE TABLE IF NOT EXISTS education (
    id SERIAL PRIMARY KEY,
    candidate_id INTEGER REFERENCES candidate(id) ON DELETE CASCADE,
    degree VARCHAR(255) NOT NULL,
    field_of_study VARCHAR(255),
    institution VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    start_year INTEGER,
    end_year INTEGER
);

-- 5. Projects Table
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    candidate_id INTEGER REFERENCES candidate(id) ON DELETE CASCADE,
    project_name VARCHAR(255) NOT NULL,
    description TEXT,
    technologies_utilized JSONB,
    project_url VARCHAR(255),
    start_date DATE,
    end_date DATE
);

-- 6. Certifications Table
CREATE TABLE IF NOT EXISTS certifications (
    id SERIAL PRIMARY KEY,
    candidate_id INTEGER REFERENCES candidate(id) ON DELETE CASCADE,
    certificate_name VARCHAR(255) NOT NULL,
    issuing_organization VARCHAR(255),
    issue_date DATE,
    expiration_date DATE,
    credential_url VARCHAR(255)
);

-- 7. Applications Tracking Table (ATS)
CREATE TABLE IF NOT EXISTS applications (
    id SERIAL PRIMARY KEY,
    candidate_id INTEGER REFERENCES candidate(id) ON DELETE CASCADE,
    company VARCHAR(255) NOT NULL,
    role VARCHAR(255) NOT NULL,
    resume_tag VARCHAR(255),
    match_score INTEGER,
    column_id VARCHAR(50) DEFAULT 'saved',
    date_applied DATE DEFAULT CURRENT_DATE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. Activity Timeline Table
CREATE TABLE IF NOT EXISTS activity_log (
    id SERIAL PRIMARY KEY,
    candidate_id INTEGER REFERENCES candidate(id) ON DELETE CASCADE,
    event_type VARCHAR(50),
    label TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);