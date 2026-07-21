import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
    
    # AI Engine Selection (default to gemini if available, otherwise openai, otherwise mock)
    @classmethod
    def get_ai_engine(cls):
        if cls.GEMINI_API_KEY:
            return "gemini"
        elif cls.OPENAI_API_KEY:
            return "openai"
        return "demo"

    PORT = int(os.getenv("PORT", 8000))
    HOST = os.getenv("HOST", "127.0.0.1")
