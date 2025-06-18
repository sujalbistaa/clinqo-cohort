import requests
import json
import re
from typing import Dict, List, Optional
from datetime import datetime

# ✅ Your API Key
API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "meta-llama/llama-3.1-8b-instruct:free"  # Fixed model name

class SimpleEntityExtractor:
    """Simple keyword-based medical entity extraction (no spaCy needed)"""
    
    def __init__(self):
        self.symptom_keywords = [
            "pain", "ache", "fever", "cough", "nausea", "vomiting", 
            "diarrhea", "headache", "dizziness", "fatigue", "weakness", 
            "shortness of breath", "chest pain", "sore throat", 
            "runny nose", "congestion", "rash", "itching", "chills",
            "sweating", "muscle pain", "joint pain", "stomach ache"
        ]
    
    def extract_symptoms(self, text: str) -> List[str]:
        """Extract symptoms using simple keyword matching"""
        text_lower = text.lower()
        found_symptoms = []
        
        for symptom in self.symptom_keywords:
            if symptom in text_lower:
                found_symptoms.append(symptom)
        
        # If no keywords found, return the original text as symptom
        return found_symptoms if found_symptoms else [text.strip()]

class PrescriptionAI:
    """Clinqo-AI prescription suggestion system"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = MODEL
        self.entity_extractor = SimpleEntityExtractor()
    
    def build_medical_prompt(self, patient_info: dict) -> str:
        """Create structured prompt for AI model"""
        age = patient_info.get("age", "unknown")
        gender = patient_info.get("gender", "unknown")
        symptoms = patient_info.get("symptoms", [])
        
        if isinstance(symptoms, str):
            symptoms = [symptoms]
        
        symptoms_text = ", ".join(symptoms)
        
        prompt = f"""
EDUCATIONAL MEDICAL SIMULATION - NOT FOR REAL USE

Patient Information:
- Age: {age}
- Gender: {gender}
- Symptoms: {symptoms_text}

Create a SIMULATED medical assessment in this EXACT JSON format:
{{
  "clinical_summary": "Brief assessment of the patient's condition",
  "possible_diagnoses": ["Most likely condition", "Alternative possibility"],
  "confidence_score": 0.75,
  "medications": [
    {{
      "medicine_name": "[SIMULATED] Medicine Name",
      "dosage": "XXmg",
      "frequency": "X times daily", 
      "duration": "X days",
      "instructions": "Take with food/water"
    }}
  ],
  "recommended_tests": ["Test 1", "Test 2"],
  "urgent_flags": [],
  "disclaimer": "SIMULATION ONLY - Not for real medical use"
}}

IMPORTANT RULES:
1. Return ONLY valid JSON (no extra text)
2. All medicine names must start with [SIMULATED]
3. Use realistic but clearly marked fake medications
4. Include safety disclaimers
5. Consider age-appropriate recommendations
"""
        return prompt
    
    def suggest_prescription(self, patient_info: dict) -> dict:
        """Generate AI prescription suggestion"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "Medical AI Simulation"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "system", 
                    "content": "You are a medical AI with 100000 years of experience in medical field , suggest according to that , your name is Clinqo-AI."
                },
                {
                    "role": "user", 
                    "content": self.build_medical_prompt(patient_info)
                }
            ],
            "temperature": 0.3,
            "max_tokens": 600
        }
        
        try:
            print(f"🤖 Sending request to: {API_URL}")
            print(f"📡 Using model: {self.model}")
            
            response = requests.post(API_URL, headers=headers, json=data, timeout=30)
            
            print(f"📊 Response status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Error response: {response.text}")
                return {
                    "error": f"API returned status {response.status_code}", 
                    "details": response.text,
                    "fallback": self._create_fallback_response(patient_info)
                }
            
            response_json = response.json()
            
            if 'choices' not in response_json or len(response_json['choices']) == 0:
                return {
                    "error": "No choices in response", 
                    "full_response": response_json,
                    "fallback": self._create_fallback_response(patient_info)
                }
            
            content = response_json['choices'][0]['message']['content']
            print(f"🔍 Raw AI response: {content}")
            
            # Extract JSON from response
            parsed_json = self._extract_json_from_response(content)
            
            if parsed_json:
                return {
                    "status": "success",
                    "ai_assessment": parsed_json,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "error": "Failed to parse JSON",
                    "raw_content": content,
                    "fallback": self._create_fallback_response(patient_info)
                }
                
        except requests.exceptions.Timeout:
            return {"error": "Request timed out", "fallback": self._create_fallback_response(patient_info)}
        except requests.exceptions.RequestException as e:
            return {"error": f"Request failed: {str(e)}", "fallback": self._create_fallback_response(patient_info)}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}", "fallback": self._create_fallback_response(patient_info)}
    
    def _extract_json_from_response(self, content: str) -> dict:
        """Extract JSON from AI response with multiple fallback methods"""
        try:
            # Method 1: Look for JSON code blocks
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_content = content[json_start:json_end].strip()
                return json.loads(json_content)
            
            # Method 2: Look for curly braces
            if "{" in content and "}" in content:
                json_start = content.find("{")
                json_end = content.rfind("}") + 1
                json_content = content[json_start:json_end]
                return json.loads(json_content)
            
            # Method 3: Try to parse the entire content
            return json.loads(content.strip())
            
        except json.JSONDecodeError as e:
            print(f"⚠️  JSON parsing failed: {e}")
            return None
    
    def _create_fallback_response(self, patient_info: dict) -> dict:
        """Create fallback response when AI fails"""
        symptoms = patient_info.get("symptoms", ["general symptoms"])
        if isinstance(symptoms, str):
            symptoms = [symptoms]
        
        return {
            "clinical_summary": f"Assessment needed for patient with {', '.join(symptoms)}",
            "possible_diagnoses": ["Requires professional medical evaluation"],
            "confidence_score": 0.0,
            "medications": [],
            "recommended_tests": ["Complete medical examination"],
            "urgent_flags": ["AI system unavailable - seek professional care"],
            "disclaimer": "SYSTEM ERROR - Consult healthcare provider immediately"
        }

def test_prescription_system():
    """Test the prescription system with sample data"""
    print("🏥 Medical AI Prescription System Test")
    print("⚠️  WARNING: This is for educational/testing purposes only!")
    print("⚠️  Never use AI for real medical decisions!")
    print("-" * 60)
    
    # Initialize the AI system
    ai_system = PrescriptionAI(API_KEY)
    
    # Test cases
    test_cases = [
        {
            "age": 25,
            "gender": "Female",
            "symptoms": ["fever", "sore throat", "fatigue"]
        },
        {
            "age": 45,
            "gender": "Male", 
            "symptoms": ["chest pain", "shortness of breath"]
        },
        {
            "age": 30,
            "gender": "Female",
            "symptoms": ["headache", "nausea", "dizziness"]
        }
    ]
    
    for i, patient in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}:")
        print(f"   Patient: {patient['age']}-year-old {patient['gender']}")
        print(f"   Symptoms: {', '.join(patient['symptoms'])}")
        
        # Get AI suggestion
        result = ai_system.suggest_prescription(patient)
        
        if result.get("status") == "success":
            assessment = result["ai_assessment"]
            print(f"   ✅ AI Assessment:")
            print(f"      Summary: {assessment.get('clinical_summary', 'N/A')}")
            print(f"      Diagnoses: {assessment.get('possible_diagnoses', [])}")
            print(f"      Confidence: {assessment.get('confidence_score', 0)}")
            
            medications = assessment.get('medications', [])
            if medications:
                print(f"      Medications:")
                for med in medications:
                    print(f"        - {med.get('medicine_name', 'N/A')}")
                    print(f"          {med.get('dosage', 'N/A')}, {med.get('frequency', 'N/A')}")
                    print(f"          Duration: {med.get('duration', 'N/A')}")
            else:
                print(f"      Medications: None recommended")
        else:
            print(f"   ❌ AI Assessment Failed:")
            print(f"      Error: {result.get('error', 'Unknown error')}")
            
            if "fallback" in result:
                fallback = result["fallback"]
                print(f"      Fallback: {fallback.get('clinical_summary', 'N/A')}")
        
        print(f"   📝 Timestamp: {result.get('timestamp', 'N/A')}")

if __name__ == "__main__":
    test_prescription_system()