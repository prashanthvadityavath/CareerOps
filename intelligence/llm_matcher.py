"""AI integration for analyzing candidate profiles against job descriptions."""
import json
import os

import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from openai import OpenAI


@st.cache_resource
def _get_gemini_model() -> genai.GenerativeModel:
    """Initializes and caches the Gemini client to avoid reconfiguring on every call."""
    load_dotenv()
    api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file or Streamlit secrets")

    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.5-flash")


@st.cache_resource
def _get_grok_client() -> Groq:
    """Initializes and caches the Groq client."""
    load_dotenv()
    api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in .env file or Streamlit secrets")
    return Groq(api_key=api_key)


@st.cache_resource
def _get_qwen_client() -> OpenAI:
    """Initializes and caches the OpenAI client for Qwen (DashScope API)."""
    load_dotenv()
    
    try:
        api_key = st.secrets.get("QWEN_API_KEY")
    except Exception:
        api_key = None
    api_key = api_key or os.getenv("QWEN_API_KEY")
    if not api_key:
        raise ValueError("QWEN_API_KEY not found in .env file or Streamlit secrets")
    return OpenAI(api_key=api_key, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")


def analyze_job_match(
    profile_text: str,
    job_description: str,
    model_provider: str = "Gemini"
) -> dict:
    """
    Uses the selected AI provider to analyze the match between a candidate profile
    and a job description. Returns a dict with 'score' (int) and 'keywords' (list).
    """
    # Validate inputs before making a (paid) API call
    if not profile_text or not profile_text.strip():
        raise ValueError("profile_text must not be empty.")
    if not job_description or not job_description.strip():
        raise ValueError("job_description must not be empty.")

    prompt = f"""
    You are an expert ATS (Applicant Tracking System) and senior technical recruiter.
    Review the following candidate resume profile and the provided job description.

    1. Calculate a match score from 0 to 100 based on how well the candidate's skills and experience fit the job.
    2. Extract up to 10 'matching_keywords' (skills the candidate has that the job requires).
    3. Extract up to 10 'missing_keywords' (skills the job requires that the candidate lacks).
    4. Extract a 'checklist' summarizing key requirements. Use booleans for yes/no fields.
    5. Provide a short 1-sentence 'recommendation' on whether they should apply.

    Return the result STRICTLY as a JSON object with this exact structure:
    {{
        "score": 85,
        "matching_keywords": ["Python", "SQL", "PostgreSQL"],
        "missing_keywords": ["Docker", "AWS"],
        "checklist": {{
            "years_of_experience_required": "3-5 years",
            "visa_sponsorship_offered": false/ or not mentioned in the description,
            "accepts_opt_cpt": false/ or not mentioned in the description,
            "certifications_required": list out/ "None explicitly mentioned"
        }},
        "recommendation": "Strong fit - Apply immediately."
    }}

    --- Candidate Profile ---
    {profile_text}

    --- Job Description ---
    {job_description}
    """

    raw_text = ""
    try:
        if model_provider == "Gemini":
            model = _get_gemini_model()
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0.0,
                ),
            )
            raw_text = response.text
        elif model_provider == "Grok":
            client = _get_grok_client()
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="grok-4.20-reasoning",
                temperature=0.0,
                response_format={"type": "json_object"},
            )
            raw_text = chat_completion.choices[0].message.content
        elif model_provider == "Qwen":
            client = _get_qwen_client()
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="qwen-plus",
                temperature=0.0,
                response_format={"type": "json_object"},
            )
            raw_text = chat_completion.choices[0].message.content
        else:
            raise ValueError(f"Unsupported model provider: {model_provider}")

        result = json.loads(raw_text)

        # Validate the response shape before returning to avoid downstream KeyErrors
        if "score" not in result or "matching_keywords" not in result:
            raise ValueError(f"Unexpected response structure: {result}")

        return result
    except json.JSONDecodeError as e:
        raise ValueError(
            f"{model_provider} returned non-JSON content: {raw_text}"
        ) from e
    except Exception:
        raise  # Re-raise cleanly, preserving the original traceback