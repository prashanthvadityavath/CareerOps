"""
Multi-Agent orchestration for AI Resume Tailoring using LangChain.
Agent 1: Extractor (Job Title, Company)
Agent 2: Researcher (Web Search for interview process, culture)
Agent 3: Matcher (Compare resume vs job description)
Agent 4: Writer (Craft tailored resume based on notes)
"""

import os
import json
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langsmith import traceable

# ---------------------------------------------------------------------------
# LangSmith Tracing Setup
# ---------------------------------------------------------------------------
load_dotenv()
try:
    import streamlit as st
    for key in ["LANGCHAIN_TRACING_V2", "LANGCHAIN_API_KEY", "LANGCHAIN_PROJECT", "LANGCHAIN_ENDPOINT"]:
        if key in st.secrets and key not in os.environ:
            os.environ[key] = str(st.secrets[key])
except Exception:
    pass

if os.environ.get("LANGCHAIN_API_KEY") and "LANGCHAIN_TRACING_V2" not in os.environ:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"

def get_llm(provider: str, api_key: str, model_name: str, base_url: str = None):
    """Helper to initialize the correct LangChain chat model."""
    if provider == "Gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(model=model_name or "gemini-1.5-flash", google_api_key=api_key, temperature=0.2)
    elif provider == "OpenAI":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=model_name or "gpt-4o", openai_api_key=api_key, temperature=0.2)
    elif provider == "Grok":
        from langchain_groq import ChatGroq
        return ChatGroq(model=model_name or "llama3-groq-70b-8192-tool-use-preview", groq_api_key=api_key, temperature=0.2)
    elif provider == "Qwen":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=model_name or "qwen-plus", openai_api_key=api_key, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1", temperature=0.2)
    elif provider == "Ollama":
        from langchain_openai import ChatOpenAI
        # Ollama expects /v1 for OpenAI compatibility
        if base_url and not base_url.endswith("/v1"):
            base_url = base_url.rstrip("/") + "/v1"
        return ChatOpenAI(model=model_name or "llama3", openai_api_key="ollama", base_url=base_url or "http://localhost:11434/v1", temperature=0.2)
    else:
        from langchain_openai import ChatOpenAI
        # Fallback
        return ChatOpenAI(model=model_name, openai_api_key=api_key, temperature=0.2)

@traceable(run_type="chain", name="Multi-Agent_Initial_Analysis")
def run_initial_analysis_agents(job_description: str, base_resume: str, provider: str, api_key: str, model_name: str = None, base_url: str = None) -> dict:
    """
    Runs Agents 1 (Extractor), 2 (Researcher), and 3 (Matcher).
    """
    llm = get_llm(provider, api_key, model_name, base_url)

    # ---------------------------------------------------------
    # AGENT 1: Extractor
    # ---------------------------------------------------------
    extract_prompt = PromptTemplate.from_template(
        "Extract the company name and job title from the job description below.\n\n"
        "Job Description:\n{job_description}\n\n"
        "Return ONLY a valid JSON object with keys 'company' and 'title'. "
        "If not found, use 'Unknown'. Do not include markdown blocks like ```json."
    )
    extractor_chain = extract_prompt | llm | StrOutputParser()
    ext_res = extractor_chain.invoke({"job_description": job_description}, config={"run_name": "Extractor_Agent"})

    # Safe parsing
    company = "Unknown"
    title = "Unknown"
    try:
        # Clean possible markdown format
        clean_res = ext_res.strip()
        if clean_res.startswith("```json"):
            clean_res = clean_res[7:]
        if clean_res.startswith("```"):
            clean_res = clean_res[3:]
        if clean_res.endswith("```"):
            clean_res = clean_res[:-3]
        data = json.loads(clean_res.strip())
        company = data.get("company", "Unknown")
        title = data.get("title", "Unknown")
    except json.JSONDecodeError:
        pass

    # ---------------------------------------------------------
    # AGENT 2: Researcher
    # ---------------------------------------------------------
    search_results = "No external data fetched."
    if company != "Unknown" and title != "Unknown":
        try:
            from langchain_community.tools import DuckDuckGoSearchRun
            search_tool = DuckDuckGoSearchRun()
            query = f"{company} {title} interview process resume shortlist tricks company culture reviews"
            search_results = search_tool.invoke(query, config={"run_name": "Researcher_Search_Tool"})
        except ImportError:
            search_results = "Search tool not installed. (Hint: pip install duckduckgo-search)"
        except Exception as e:
            search_results = f"Search failed or unavailable: {e}"

    research_prompt = PromptTemplate.from_template(
        "You are a Career Researcher. Analyze the following web search results regarding a company's hiring process.\n"
        "Company: {company}\nRole: {title}\n"
        "Search Results: {search_results}\n\n"
        "Summarize the interview process, resume shortlist tricks, and company culture insights. "
        "Keep it concise and highly actionable for someone updating their resume."
    )
    researcher_chain = research_prompt | llm | StrOutputParser()
    research_notes = researcher_chain.invoke(
        {
            "company": company,
            "title": title,
            "search_results": search_results
        },
        config={"run_name": "Researcher_Agent"}
    )

    # ---------------------------------------------------------
    # AGENT 3: Matcher / Reviewer
    # ---------------------------------------------------------
    match_prompt = PromptTemplate.from_template(
        "You are an expert ATS Reviewer.\n"
        "Compare this Job Description:\n{job_description}\n\n"
        "With this Resume:\n{base_resume}\n\n"
        "Identify exactly where the resume is lacking relative to the job description, "
        "highlight missing skills, and provide specific improvement tips."
    )
    matcher_chain = match_prompt | llm | StrOutputParser()
    matcher_notes = matcher_chain.invoke(
        {
            "job_description": job_description,
            "base_resume": base_resume
        },
        config={"run_name": "Matcher_Agent"}
    )

    return {
        "extracted_company": company,
        "extracted_title": title,
        "research_notes": research_notes,
        "matcher_notes": matcher_notes,
    }

@traceable(run_type="chain", name="Agent_Resume_Writer")
def run_writer_agent(base_resume: str, job_description: str, research_notes: str, matcher_notes: str, provider: str, api_key: str, model_name: str = None, base_url: str = None) -> str:
    """
    Executes the LangChain Writer agent (Agent 4) to tailor a resume.
    """
    llm = get_llm(provider, api_key, model_name, base_url)
    writer_prompt = PromptTemplate.from_template(
        "You are an expert Professional Resume Writer.\n"
        "Your task is to craft an updated, tailored resume for the user based on the provided notes.\n\n"
        "CRITICAL INSTRUCTIONS:\n"
        "- Do NOT write generic starting words (e.g., 'Here is the tailored resume', 'Certainly!').\n"
        "- Do NOT use white-labeled or placeholder texts.\n"
        "- Do NOT manipulate or fabricate resume details (do not add experience they don't have).\n"
        "- ONLY tweak the context and wording to heavily emphasize matches with the job description.\n"
        "- Output MUST be purely the tailored resume in Markdown format.\n\n"
        "Input Data:\n"
        "--- Original Resume ---\n{base_resume}\n\n"
        "--- Job Description ---\n{job_description}\n\n"
        "--- Research Notes (Agent 2) ---\n{research_notes}\n\n"
        "--- Matcher Feedback (Agent 3) ---\n{matcher_notes}\n\n"
        "Draft the final tailored resume now:"
    )
    writer_chain = writer_prompt | llm | StrOutputParser()
    tailored_resume = writer_chain.invoke(
        {
            "base_resume": base_resume,
            "job_description": job_description,
            "research_notes": research_notes,
            "matcher_notes": matcher_notes
        },
        config={"run_name": "Writer_Agent"}
    )
    return tailored_resume

@traceable(run_type="chain", name="Agent_Rematcher")
def run_rematcher_agent(tailored_resume: str, job_description: str, provider: str, api_key: str, model_name: str = None, base_url: str = None) -> dict:
    """
    Executes a new analysis (Agent 5) on the tailored resume to show improvement.
    """
    llm = get_llm(provider, api_key, model_name, base_url)
    
    rematch_prompt_template = PromptTemplate.from_template("""
    You are an expert ATS (Applicant Tracking System).
    Review the following UPDATED candidate resume and the original job description.
    Your goal is to provide a NEW analysis of the improved resume.

    1. Calculate a new match score from 0 to 100.
    2. Extract up to 10 'matching_keywords'.
    3. Extract up to 5 'missing_keywords' (if any still exist).
    4. Provide a final 1-sentence 'recommendation'.

    Return the result STRICTLY as a JSON object with this exact structure:
    {{
        "score": 95,
        "matching_keywords": ["Python", "SQL", "PostgreSQL", "Docker", "AWS"],
        "missing_keywords": [],
        "recommendation": "Excellent fit. The resume is now highly tailored."
    }}

    --- Updated Candidate Resume ---
    {tailored_resume}

    --- Original Job Description ---
    {job_description}
    """)
    
    rematcher_chain = rematch_prompt_template | llm | StrOutputParser()
    
    raw_res = rematcher_chain.invoke({
        "tailored_resume": tailored_resume,
        "job_description": job_description
    }, config={"run_name": "Rematcher_Agent"})

    try:
        # Clean potential markdown
        if "```json" in raw_res:
            raw_res = raw_res.split("```json")[1].split("```")[0]
        return json.loads(raw_res.strip())
    except (json.JSONDecodeError, IndexError, TypeError, AttributeError, ValueError):
        # Fallback if JSON is malformed
        return {
            "score": 0,
            "matching_keywords": [],
            "missing_keywords": ["Error parsing rematcher response"],
            "recommendation": "Could not re-analyze the resume."
        }