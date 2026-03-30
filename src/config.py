import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY is not set in the environment.")

# Default openrouter model (can be adjusted)
LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-4o-mini")

def get_llm():
    """Returns the configured LLM instance using OpenRouter."""
    return ChatOpenAI(
        model=LLM_MODEL,
        openai_api_key=OPENROUTER_API_KEY,
        openai_api_base="https://openrouter.ai/api/v1",
        default_headers={"HTTP-Referer": "http://localhost:8000", "X-Title": "Financial Intelligence System"},
    )
