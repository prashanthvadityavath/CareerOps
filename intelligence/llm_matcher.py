"""AI integration for analyzing candidate profiles against job descriptions."""
import json
import google.generativeai as genai
import streamlit as st
import os
from dotenv import load_dotenv


@st.cache_resource
def _get_model() -> genai.GenerativeModel:
    """Initializes and caches the Gemini client to avoid reconfiguring on every call."""
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file")

    genai.configure(api_key=api_key)
    # Comment and model name now agree
    return genai.GenerativeModel("gemini-2.5-flash")


def analyze_job_match(profile_text: str, job_description: str) -> dict:
    """
    Uses Google Gemini to analyze the match between a candidate profile
    and a job description. Returns a dict with 'score' (int) and 'keywords' (list).
    """
    # Validate inputs before making a (paid) API call
    if not profile_text or not profile_text.strip():
        raise ValueError("profile_text must not be empty.")
    if not job_description or not job_description.strip():
        raise ValueError("job_description must not be empty.")

    model = _get_model()

    prompt = f"""
    You are an expert ATS (Applicant Tracking System) and senior technical recruiter.
    Review the following candidate resume profile and the provided job description.

    1. Calculate a match score from 0 to 100 based on how well the candidate's skills and experience fit the job.
    2. Extract up to 6 'matching_keywords' (skills the candidate has that the job requires).
    3. Extract up to 4 'missing_keywords' (skills the job requires that the candidate lacks).
    4. Extract a 'checklist' summarizing key requirements. Use booleans for yes/no fields.
    5. Provide a short 1-sentence 'recommendation' on whether they should apply.

    Return the result STRICTLY as a JSON object with this exact structure:
    {{
        "score": 85,
        "matching_keywords": ["Python", "SQL", "PostgreSQL"],
        "missing_keywords": ["Docker", "AWS"],
        "checklist": {{
            "years_of_experience_required": "3-5 years",
            "visa_sponsorship_offered": false,
            "accepts_opt_cpt": false,
            "certifications_required": "None explicitly mentioned"
        }},
        "recommendation": "Strong fit - Apply immediately."
    }}

    --- Candidate Profile ---
    {profile_text}

    --- Job Description ---
    {job_description}
    """

    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.0,
            ),
        )
        result = json.loads(response.text)

        # Validate the response shape before returning to avoid downstream KeyErrors
        if "score" not in result or "matching_keywords" not in result:
            raise ValueError(f"Unexpected response structure: {result}")

        return result
    except json.JSONDecodeError as e:
        raise ValueError(f"Gemini returned non-JSON content: {response.text}") from e
    except Exception:
        raise  # Re-raise cleanly, preserving the original traceback