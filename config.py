import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
    SUPERVISOR_MEMORY_SIZE = int(os.getenv("SUPERVISOR_MEMORY_SIZE", "10"))
    WORKER_TIMEOUT = int(os.getenv("WORKER_TIMEOUT", "30"))
    
    @classmethod
    def validate(cls):
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")
        return cls