import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
    MODEL_NAME: str = "llama-3.3-70b-versatile"
    MAX_TOKENS: int = 4096
    TEMPERATURE: float = 0.0
    MAX_ITERATIONS: int = 10
    DB_PATH: str = "agentflow.db"

config = Config()