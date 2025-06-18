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