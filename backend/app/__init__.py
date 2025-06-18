# backend/app/__init__.py
"""Medical AI MCP Server Package"""

# backend/app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL - use SQLite for development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./medical_ai.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def create_tables():
    """Create all database tables"""
    from . import models  # Import here to avoid circular imports
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# backend/app/schemas.py
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class PatientCreate(BaseModel):
    id: str
    name: str
    age: int
    gender: str
    phone: Optional[str] = None
    email: Optional[str] = None
    medical_history: Optional[List[str]] = []
    allergies: Optional[List[str]] = []

class Patient(PatientCreate):
    created_at: datetime
    
    class Config:
        from_attributes = True

class AppointmentCreate(BaseModel):
    patient_id: str
    doctor_id: str
    scheduled_time: datetime
    chief_complaint: Optional[str] = None

class Appointment(AppointmentCreate):
    id: int
    status: str = "scheduled"
    created_at: datetime
    
    class Config:
        from_attributes = True

class PrescriptionRequest(BaseModel):
    age: int
    gender: str
    symptoms: List[str]
    medical_history: Optional[List[str]] = []
    allergies: Optional[List[str]] = []
    current_medications: Optional[List[str]] = []

class PrescriptionSubmit(BaseModel):
    patient_id: str
    doctor_id: str
    appointment_id: Optional[int] = None
    diagnosis: str
    medications: List[Dict[str, Any]]
    instructions: str
    ai_assessment_id: Optional[str] = None
    original_ai_assessment: Optional[Dict] = None
    final_prescription: Dict
    was_overridden: bool = False
    override_reason: Optional[str] = None

class AudioInput(BaseModel):
    audio_data: str  # Base64 encoded
    format: str = "wav"

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