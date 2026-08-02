import os
from langchain_openai import ChatOpenAI
from app.config import settings

def get_llm(model_name: str = "gpt-4o-mini", temperature: float = 0.7) -> ChatOpenAI:
    api_key = getattr(settings, "OPENAI_API_KEY", "") or os.getenv("OPENAI_API_KEY", "")
    
    if not api_key:
        print("OPENAI_API_KEY ??? Please set the environment variable or configure it in settings.")

    return ChatOpenAI(
        model=model_name,
        temperature=temperature,
        api_key=api_key
    )