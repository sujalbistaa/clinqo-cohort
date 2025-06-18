# backend/app/models.py
from sqlalchemy import Column, Integer, String, DateTime, JSON, Float, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)
    phone = Column(String)
    email = Column(String)
    medical_history = Column(JSON)  # List of conditions
    allergies = Column(JSON)        # List of allergies
    current_medications = Column(JSON)  # Current meds
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    appointments = relationship("Appointment", back_populates="patient")
    prescriptions = relationship("Prescription", back_populates="patient")

class Doctor(Base):
    __tablename__ = "doctors"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    specialization = Column(String)
    license_number = Column(String)
    preferences = Column(JSON)  # AI learning preferences
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    appointments = relationship("Appointment", back_populates="doctor")
    prescriptions = relationship("Prescription", back_populates="doctor")

class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(String, ForeignKey("doctors.id"), nullable=False)
    scheduled_time = Column(DateTime, nullable=False)
    status = Column(String, default="scheduled")  # scheduled, in_progress, completed, cancelled
    chief_complaint = Column(Text)
    voice_notes = Column(JSON)  # Processed voice data
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")

class Prescription(Base):
    __tablename__ = "prescriptions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(String, ForeignKey("doctors.id"), nullable=False)
    appointment_id = Column(Integer, ForeignKey("appointments.id"))
    
    # AI Assessment Data
    ai_assessment = Column(JSON)  # Original AI suggestion
    ai_confidence = Column(Float)
    
    # Final Prescription
    diagnosis = Column(String)
    medications = Column(JSON)  # List of prescribed medications
    instructions = Column(Text)
    follow_up = Column(String)
    
    # Override Tracking
    was_overridden = Column(Boolean, default=False)
    override_reason = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="prescriptions")
    doctor = relationship("Doctor", back_populates="prescriptions")

class FeedbackLog(Base):
    __tablename__ = "feedback_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    doctor_id = Column(String, ForeignKey("doctors.id"), nullable=False)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False)
    
    original_assessment = Column(JSON)  # AI's original suggestion
    final_prescription = Column(JSON)   # Doctor's final decision
    override_type = Column(String)      # Type of override
    improvement_score = Column(Float)   # How much better the override was
    
    created_at = Column(DateTime, default=datetime.utcnow)