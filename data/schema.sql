-- CareerOps PostgreSQL schema (run once against the database from secrets.toml)
-- Matches tables used in pages/master_profile.py

-- 1. Candidate Table
CREATE TABLE IF NOT EXISTS candidate (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    linkedin_url VARCHAR(255),
    github_url VARCHAR(255),
    portfolio_url VARCHAR(255),
    career_objective TEXT,
    professional_summary JSONB, -- Stores array of bullet points
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Safely add profile_name if it was missed earlier
ALTER TABLE candidate ADD COLUMN IF NOT EXISTS profile_name VARCHAR(255) DEFAULT 'Default Profile';

-- 2. Technical Skills Table
CREATE TABLE IF NOT EXISTS technical_skills (
    id SERIAL PRIMARY KEY,
    candidate_id INTEGER REFERENCES candidate(id) ON DELETE CASCADE,
    category VARCHAR(100) NOT NULL, -- e.g., 'Backend Technologies & Frameworks'
    skills_list JSONB NOT NULL -- Stores array of skills
);

-- 3. Work Experience Table
CREATE TABLE IF NOT EXISTS work_experience (
    id SERIAL PRIMARY KEY,
    candidate_id INTEGER REFERENCES candidate(id) ON DELETE CASCADE,
    company_name VARCHAR(255) NOT NULL,
    role_title VARCHAR(255) NOT NULL,
    start_date DATE,
    end_date DATE, -- NULL can represent "Present"
    location VARCHAR(255),
    project_name TEXT,
    project_description TEXT,
    role_and_contributions JSONB, -- Stores array of bullet points
    technologies_utilized JSONB -- Stores array of technologies
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

-- 7. Applications Tracking Table (ATS) - NEW
CREATE TABLE IF NOT EXISTS applications (
    id SERIAL PRIMARY KEY,
    candidate_id INTEGER REFERENCES candidate(id) ON DELETE CASCADE,
    company VARCHAR(255) NOT NULL,
    role VARCHAR(255) NOT NULL,
    resume_tag VARCHAR(100),
    match_score INTEGER,
    date_applied DATE,
    column_id VARCHAR(50) DEFAULT 'applied'
);

-- 8. Activity Timeline Table - NEW
CREATE TABLE IF NOT EXISTS activity_events (
    id SERIAL PRIMARY KEY,
    candidate_id INTEGER REFERENCES candidate(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    timestamp VARCHAR(50),
    color VARCHAR(20) DEFAULT 'blue'
);