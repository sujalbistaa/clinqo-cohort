Clinic AI MCP Hackathon


Smart AI assistant backend for streamlined clinic management and doctor support

🚀 Project Overview

This project is the intelligence and backend core for a medical clinic assistant system designed to:

Transcribe patient voice recordings to text using OpenAI Whisper
Extract patient information (age, gender, symptoms, duration) with NLP
Suggest prescriptions via AI models (GPT-4 / LLaMA via Together.ai)
Manage appointments, doctors, patients, and prescriptions through a FastAPI server
Provide real-time updates between receptionist and doctors with WebSockets
Support an AI feedback loop to learn doctor preferences and improve suggestions
Built as a Minimum Viable Product (MVP) for a hackathon, all core modules are open source and modular.

🧱 Tech Stack

Component	Technology / Library
Speech-to-Text	OpenAI Whisper (openai-whisper)
NLP & Entity Extraction	spaCy, regex
AI Prescription Generation	GPT-4, LLaMA via Together.ai API
Backend Framework	FastAPI
Real-time Sync	WebSockets (socket.io / Redis PubSub)
Database	PostgreSQL / SQLite (your choice)
Hosting	Render / Railway
📁 Project Structure



🛠️ Setup & Run Locally

Clone repo:
git clone https://github.com/yourusername/clinic-ai-mcp-hackathon.git
cd clinic-ai-mcp-hackathon
Create & activate virtual environment:
python3 -m venv venv
source venv/bin/activate
Install dependencies:
pip install -r requirements.txt
brew install ffmpeg   # For Mac users
Run transcription test:
python ai-engine/stt/whisper_stt.py test-dataset/audio.mp3
Start FastAPI server:
uvicorn backend.main:app --reload
Open http://localhost:8000/docs to explore API docs
🤝 Team Roles

AI/ML/NLP Engineer: Owns voice transcription, NLP pipeline, AI prescription generator, and feedback loop
Frontend Developer: Builds UI for receptionist, doctor dashboards, and chat interface
Backend/Database Engineer: Manages FastAPI server, database schema, real-time sync, and deployment
📜 API Endpoints (Overview)

POST /appointments — Create new appointment
GET /doctor/{id}/appointments — Get doctor’s appointments
POST /prescription/suggest — AI prescription suggestion from transcribed text
POST /prescription/submit — Log override feedback
GET /patient/{id} — Patient profile info
⚠️ Disclaimer

This project is a hackathon MVP prototype only. It does not provide medical advice or diagnosis. Always consult licensed healthcare professionals for medical decisions.

📞 Contact

Created by Sujal Bist and Team.
GitHub: github.com/sujalbistaa
Email: sujal.ihrr@gmail.com

⭐️ If you find this useful, please star the repo!
