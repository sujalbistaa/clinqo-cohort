from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import sys
import os
import json
from datetime import datetime
from typing import List

sys.path.append(os.path.join(os.path.dirname(__file__), '../../ai-engine/nlp'))

try:
    from prescription_generator import PrescriptionAI
    AI_AVAILABLE = True
    print("✅ AI system imported successfully")
except ImportError as e:
    print(f"⚠️  Could not import AI system: {e}")
    AI_AVAILABLE = False

from . import models, schemas, database
from .config import settings

app = FastAPI(
    title="Medical AI MCP Server",
    description="AI-powered medical prescription system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ai_system = None

@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    global ai_system
    
    database.create_tables()
    
    if AI_AVAILABLE:
        try:
            ai_system = PrescriptionAI(settings.OPENROUTER_API_KEY)
            print("🤖 AI system initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize AI system: {e}")
    
    print(f"🚀 Medical AI MCP Server started on {settings.HOST}:{settings.PORT}")

@app.get("/")
async def root():
    return {
        "message": "Medical AI MCP Server",
        "status": "online",
        "ai_available": AI_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "ai_system": "online" if ai_system else "offline",
        "database": "connected",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/patients", response_model=schemas.Patient)
async def create_patient(
    patient: schemas.PatientCreate,
    db: Session = Depends(database.get_db)
):
    """Create a new patient"""
    # Check if patient already exists
    existing = db.query(models.Patient).filter(models.Patient.id == patient.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Patient already exists")
    
    db_patient = models.Patient(**patient.dict())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    
    return db_patient

@app.get("/patients/{patient_id}", response_model=schemas.Patient)
async def get_patient(
    patient_id: str,
    db: Session = Depends(database.get_db)
):
    """Get patient by ID"""
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

# === APPOINTMENT ENDPOINTS ===
@app.post("/appointments", response_model=schemas.Appointment)
async def create_appointment(
    appointment: schemas.AppointmentCreate,
    db: Session = Depends(database.get_db)
):
    """Create new appointment"""
    db_appointment = models.Appointment(**appointment.dict())
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    
    print(f"📅 New appointment created: {db_appointment.id}")
    return db_appointment

@app.get("/doctor/{doctor_id}/appointments", response_model=List[schemas.Appointment])
async def get_doctor_appointments(
    doctor_id: str,
    db: Session = Depends(database.get_db)
):
    """Get appointments for a specific doctor"""
    appointments = db.query(models.Appointment).filter(
        models.Appointment.doctor_id == doctor_id
    ).all()
    
    return appointments

# === AI PRESCRIPTION ENDPOINTS ===
@app.post("/prescription/suggest")
async def suggest_prescription(request: schemas.PrescriptionRequest):
    """Generate AI prescription suggestion"""
    if not ai_system:
        raise HTTPException(
            status_code=503, 
            detail="AI system not available. Please check configuration."
        )
    
    try:
        # Convert request to format expected by AI system
        patient_info = {
            "age": request.age,
            "gender": request.gender,
            "symptoms": request.symptoms,
            "medical_history": request.medical_history or [],
            "allergies": request.allergies or []
        }
        
        # Get AI suggestion
        result = ai_system.suggest_prescription(patient_info)
        
        return {
            "status": "success",
            "patient_info": patient_info,
            "ai_result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"AI assessment failed: {str(e)}"
        )

@app.post("/prescription/submit")
async def submit_prescription(
    prescription: schemas.PrescriptionSubmit,
    db: Session = Depends(database.get_db)
):
    """Submit final prescription and log override data"""
    
    # Save prescription to database
    db_prescription = models.Prescription(**prescription.dict())
    db.add(db_prescription)
    db.commit()
    db.refresh(db_prescription)
    
    print(f"💊 Prescription submitted: {db_prescription.id}")
    
    return {
        "status": "prescription_saved",
        "prescription_id": db_prescription.id,
        "timestamp": datetime.now().isoformat()
    }

# === VOICE PROCESSING ENDPOINTS ===
@app.post("/voice/upload")
async def upload_voice(audio: UploadFile = File(...)):
    """Upload and process voice file (placeholder for now)"""
    if not audio.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="File must be audio format")
    
    # For now, return mock extracted data
    # TODO: Integrate with whisper_stt.py
    mock_extraction = {
        "transcript": "Patient complains of fever and headache for 2 days",
        "extracted_info": {
            "symptoms": ["fever", "headache"],
            "duration": "2 days",
            "age": None,
            "confidence": 0.85
        }
    }
    
    return {
        "status": "processed",
        "filename": audio.filename,
        "extraction": mock_extraction,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/voice/to-prescription")
async def voice_to_prescription(
    audio: UploadFile = File(...),
    age: int = 25,
    gender: str = "Unknown"
):
    """Complete pipeline: Voice → AI Prescription"""
    
    # Step 1: Process voice (mock for now)
    voice_result = await upload_voice(audio)
    
    if voice_result["status"] != "processed":
        return voice_result
    
    # Step 2: Extract symptoms from voice processing
    extraction = voice_result["extraction"]
    symptoms = extraction["extracted_info"]["symptoms"]
    
    # Step 3: Generate AI prescription
    prescription_request = schemas.PrescriptionRequest(
        age=age,
        gender=gender,
        symptoms=symptoms
    )
    
    ai_result = await suggest_prescription(prescription_request)
    
    return {
        "voice_processing": voice_result,
        "ai_prescription": ai_result,
        "pipeline_status": "complete"
    }

# === TEST ENDPOINTS ===
@app.get("/test/ai")
async def test_ai_system():
    """Test the AI prescription system"""
    if not ai_system:
        return {"error": "AI system not available"}
    
    # Test with sample data
    test_patient = {
        "age": 30,
        "gender": "Female",
        "symptoms": ["fever", "cough", "fatigue"]
    }
    
    try:
        result = ai_system.suggest_prescription(test_patient)
        return {
            "test_status": "success",
            "test_patient": test_patient,
            "ai_response": result
        }
    except Exception as e:
        return {
            "test_status": "failed",
            "error": str(e)
        }

# === ERROR HANDLERS ===
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    print(f"❌ Unhandled exception: {exc}")
    return HTTPException(
        status_code=500,
        detail=f"Internal server error: {str(exc)}"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host=settings.HOST, 
        port=settings.PORT, 
        reload=settings.DEBUG
    )