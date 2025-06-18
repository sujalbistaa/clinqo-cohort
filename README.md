# Clinqo MCP Hackathon

Smart AI assistant backend for streamlined clinic management and doctor support

🚀 **Project Overview**

This project is the intelligence and backend core for a medical clinic assistant system designed to:

- Transcribe patient voice recordings to text using OpenAI Whisper
- Extract patient information (age, gender, symptoms, duration) with NLP
- Suggest prescriptions via AI models (GPT-4 / LLaMA via Together.ai)
- Manage appointments, doctors, patients, and prescriptions through a FastAPI server
- Provide real-time updates between receptionist and doctors with WebSockets
- Support an AI feedback loop to learn doctor preferences and improve suggestions

Built as a Minimum Viable Product (MVP) for a hackathon, all core modules are open source and modular.

---

🧱 **Tech Stack**

| Component               | Technology / Library                  |
|------------------------|-------------------------------------|
| Speech-to-Text         | OpenAI Whisper (openai-whisper)     |
| NLP & Entity Extraction |  regex                        |
| AI Prescription Generation |  LLaMA via Together.ai API |
| Backend Framework      | FastAPI                             |
| Real-time Sync         | WebSockets (socket.io / Redis PubSub) |
| Database               | SQL  |
| Hosting                | Render                    |
