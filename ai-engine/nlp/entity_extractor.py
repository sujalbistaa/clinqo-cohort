"""
Medical Entity Extractor for Patient Voice Notes

This module extracts key medical entities from patient transcripts including:
- Age
- Gender  
- Symptoms
- Duration of symptoms
"""

import re
import json
from typing import Dict, List, Optional, Any


class MedicalEntityExtractor:
    """Extract medical entities from patient voice note transcripts."""
    
    def __init__(self):
        # Predefined symptoms list
        self.symptoms_list = [
            "fever", "headache", "cough", "body pain", "fatigue", 
            "nausea", "vomiting", "diarrhea", "constipation", "dizziness",
            "chest pain", "back pain", "stomach pain", "sore throat",
            "runny nose", "stuffy nose", "shortness of breath", "weakness",
            "joint pain", "muscle pain", "chills", "sweating", "rash",
            "itching", "swelling", "bruising", "bleeding", "numbness",
            "tingling", "blurred vision", "ear pain", "tooth pain",
            "difficulty swallowing", "loss of appetite", "weight loss",
            "weight gain", "insomnia", "drowsiness", "anxiety", "depression"
        ]
        
        # Regex patterns
        self.age_patterns = [
            r'(\d{1,3})\s*[-–]\s*year[-\s]*old',
            r'(\d{1,3})\s*years?\s*old',
            r'(\d{1,3})\s*yr[-\s]*old',
            r'(\d{1,3})\s*y\.?o\.?',
            r'age\s*(?:is\s*|of\s*)?(\d{1,3})',
            r'I\'?m\s*(\d{1,3})',
            r'(\d{1,3})\s*years?\s*of\s*age'
        ]
        
        self.gender_patterns = [
            r'\b(male|man|boy|gentleman)\b',
            r'\b(female|woman|girl|lady)\b'
        ]
        
        self.duration_patterns = [
            r'(?:for\s+)?(?:the\s+)?(?:last|past)\s+(\w+\s+\w+|\w+)',
            r'(?:for\s+)?(\w+\s+(?:days?|weeks?|months?|years?))',
            r'since\s+(\w+(?:\s+\w+)?)',
            r'(\w+\s+(?:days?|weeks?|months?|years?))\s+(?:ago|back)',
            r'about\s+(\w+\s+(?:days?|weeks?|months?|years?))',
            r'around\s+(\w+\s+(?:days?|weeks?|months?|years?))',
            r'maybe\s+(?:the\s+)?(?:last\s+)?(\w+\s+(?:days?|weeks?|months?|years?))',
            r'(?:for\s+)?(?:about\s+)?(\d+\s+(?:days?|weeks?|months?|years?))'
        ]

    def extract_age(self, text: str) -> Optional[int]:
        """Extract age from text using regex patterns."""
        text_lower = text.lower()
        
        for pattern in self.age_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                try:
                    age = int(match.group(1))
                    # Validate reasonable age range
                    if 0 <= age <= 120:
                        return age
                except (ValueError, IndexError):
                    continue
        return None

    def extract_gender(self, text: str) -> Optional[str]:
        """Extract gender from text using regex patterns."""
        text_lower = text.lower()
        
        for pattern in self.gender_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                gender_term = match.group(1).lower()
                if gender_term in ['male', 'man', 'boy', 'gentleman']:
                    return 'male'
                elif gender_term in ['female', 'woman', 'girl', 'lady']:
                    return 'female'
        return None

    def extract_symptoms(self, text: str) -> List[str]:
        """Extract symptoms using list matching."""
        text_lower = text.lower()
        found_symptoms = []
        
        for symptom in self.symptoms_list:
            # Create pattern to match the symptom with word boundaries
            pattern = r'\b' + re.escape(symptom) + r'\b'
            if re.search(pattern, text_lower):
                found_symptoms.append(symptom)
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(found_symptoms))

    def extract_duration(self, text: str) -> Optional[str]:
        """Extract duration phrases from text."""
        text_lower = text.lower()
        
        for pattern in self.duration_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                duration = match.group(1).strip()
                # Clean up the duration text
                duration = re.sub(r'\s+', ' ', duration)
                return duration
        return None

    def extract_entities(self, transcript: str) -> Dict[str, Any]:
        """
        Extract all medical entities from a patient transcript.
        
        Args:
            transcript (str): Raw transcript of patient's voice note
            
        Returns:
            dict: Dictionary containing extracted entities
        """
        if not transcript or not isinstance(transcript, str):
            return {
                "age": None,
                "gender": None,
                "symptoms": [],
                "duration": None
            }
        
        # Extract each entity type
        age = self.extract_age(transcript)
        gender = self.extract_gender(transcript)
        symptoms = self.extract_symptoms(transcript)
        duration = self.extract_duration(transcript)
        
        return {
            "age": age,
            "gender": gender,
            "symptoms": symptoms,
            "duration": duration
        }


def extract_medical_entities(transcript: str) -> Dict[str, Any]:
    """
    Convenience function to extract medical entities from transcript.
    
    Args:
        transcript (str): Raw transcript of patient's voice note
        
    Returns:
        dict: Dictionary containing extracted entities
    """
    extractor = MedicalEntityExtractor()
    return extractor.extract_entities(transcript)


if __name__ == "__main__":
    # Read transcript from saved text file
    transcript_file = "/Users/sujalbist/clinqo-cohort/ai-engine/test-dataset/test_audio_2.txt"
    
    try:
        # Read transcript from file
        with open(transcript_file, 'r', encoding='utf-8') as f:
            transcript = f.read().strip()
        
        print("Transcript:")
        print(f'"{transcript}"')
        
        # Extract medical entities
        extractor = MedicalEntityExtractor()
        entities = extractor.extract_entities(transcript)
        
        # Show results
        print("\nExtracted Entities:")
        print(json.dumps(entities, indent=2))
        
    except FileNotFoundError:
        print(f"Transcript file not found: {transcript_file}")
    except Exception as e:
        print(f"Error: {e}")