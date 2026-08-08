# InterviAI

Personalized AI Technical Interview Agent for the Vidothon AI Interview Agent challenge.

## MVP
- Candidate profile selection
- Curriculum-aware interview
- Multi-turn session
- 8-question interview
- Adaptive follow-ups
- Structured feedback

## Run

Backend:
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173
Backend: http://localhost:8000

NOTE: the official Technical Specification attachment was not readable in this chat, so the API is currently an MVP contract. Replace/align the routes with the organizer's exact contract when that file is available.
