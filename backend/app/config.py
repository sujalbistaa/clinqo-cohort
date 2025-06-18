# backend/app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # API Keys
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "your-api-key-here")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./medical_ai.db")
    
    # Server
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    
    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = ENVIRONMENT == "development"
    
    # CORS
    ALLOWED_ORIGINS = [
        "http://localhost:3000",  # React default
        "http://localhost:3001",
        "http://localhost:5173",  # Vite default
        "http://127.0.0.1:3000",
    ]

settings = Settings()