"""AI integration for analyzing candidate profiles against job descriptions."""
import json
import os
import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from openai import OpenAI

MODEL_DEFAULTS = {
    "Gemini": "gemini-1.5-flash",
    "Grok": "llama3-groq-70b-8192-tool-use-preview",
    "Qwen": "qwen-plus",
    "OpenAI": "gpt-4o",
    "Ollama": "llama3",
}

def _get_provider_credential(provider: str, credential_name: str) -> str | None:
    """
    Helper to retrieve a credential (e.g., API_KEY, BASE_URL) from session state,
    local JSON, secrets, or env.
    """
    key_name = f"{provider.upper()}_{credential_name.upper()}"
    
    if key_name in st.session_state and st.session_state[key_name]:
        return st.session_state[key_name]
    try:
        if os.path.exists("user_keys.json"):
            with open("user_keys.json", "r") as f:
                keys = json.load(f)
                if keys.get(key_name):
                    return keys[key_name]
    except Exception:
        pass
    load_dotenv()
    try:
        val = st.secrets.get(key_name)
        if val:
            return val
    except Exception:
        pass
    return os.getenv(key_name)


@st.cache_resource
def _get_gemini_model(api_key: str, model_name: str) -> genai.GenerativeModel:
    """Initializes and caches the Gemini client to avoid reconfiguring on every call."""
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name)


@st.cache_resource
def _get_grok_client(api_key: str) -> Groq:
    """Initializes and caches the Groq client."""
    return Groq(api_key=api_key)


@st.cache_resource
def _get_qwen_client(api_key: str) -> OpenAI:
    """Initializes and caches the OpenAI client for Qwen (DashScope API)."""
    return OpenAI(api_key=api_key, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")


@st.cache_resource
def _get_openai_client(api_key: str) -> OpenAI:
    """Initializes and caches the OpenAI client."""
    return OpenAI(api_key=api_key)


@st.cache_resource
def _get_ollama_client(base_url: str) -> OpenAI:
    """Initializes and caches an OpenAI-compatible client for Ollama."""
    # Ollama doesn't require a key for local instances, but the client needs a value.
    return OpenAI(api_key="ollama", base_url=base_url)


def analyze_job_match(
    profile_text: str,
    job_description: str,
    model_provider: str = "Gemini",
    model_name: str | None = None,
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

    # Use provided model name or get default from the config
    active_model = model_name.strip() if model_name and model_name.strip() else MODEL_DEFAULTS.get(model_provider)
    if not active_model:
        raise ValueError(f"No model name provided and no default exists for {model_provider}.")

    # Get credentials (API key or Base URL for Ollama)
    if model_provider == "Ollama":
        credential = _get_provider_credential("Ollama", "BASE_URL") or "http://localhost:11434"
    else:
        credential = _get_provider_credential(model_provider, "API_KEY")
    if not credential:
        cred_type = "Base URL" if model_provider == "Ollama" else "API Key"
        raise ValueError(f"{cred_type} for {model_provider} is missing. Please add it in the UI.")

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
            model = _get_gemini_model(credential, active_model)
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0.0,
                ),
            )
            raw_text = response.text
        elif model_provider in ["Grok", "Qwen", "OpenAI", "Ollama"]:
            client = None
            if model_provider == "Grok":
                client = _get_grok_client(credential)
            elif model_provider == "Qwen":
                client = _get_qwen_client(credential)
            elif model_provider == "OpenAI":
                client = _get_openai_client(credential)
            elif model_provider == "Ollama":
                client = _get_ollama_client(credential)

            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=active_model,
                temperature=0.0,
                response_format={"type": "json_object"},
            )
            raw_text = chat_completion.choices[0].message.content
        else:
            raise ValueError(f"Unsupported model provider: {model_provider}")

        result = json.loads(raw_text)

        # Validate the response shape before returning to avoid downstream KeyErrors
        if "score" not in result or "matching_keywords" not in result or "missing_keywords" not in result:
            raise ValueError(f"Unexpected response structure: {result}")

        return result
    except json.JSONDecodeError as e:
        raise ValueError(
            f"{model_provider} returned non-JSON content: {raw_text}"
        ) from e
    except Exception:
        raise  # Re-raise cleanly, preserving the original traceback