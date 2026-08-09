from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .data import CANDIDATES, candidate_by_id
from .interview import (
    start_session,
    sessions,
    submit_answer,
    feedback,
)


app = FastAPI(
    title="InterviAI API",
    version="0.2.0",
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Request Models
# --------------------------------------------------

class StartRequest(BaseModel):
    candidate_id: str


class AnswerRequest(BaseModel):
    session_id: str
    answer: str


# --------------------------------------------------
# Health
# --------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "InterviAI",
    }


# --------------------------------------------------
# Candidates
# --------------------------------------------------

@app.get("/api/candidates")
def candidates():
    return CANDIDATES


# --------------------------------------------------
# Start Interview
# --------------------------------------------------

@app.post("/api/interview/start")
def start(req: StartRequest):

    candidate = candidate_by_id(req.candidate_id)

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found",
        )

    try:
        session = start_session(candidate)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    question = session["seeds"][0][1]

    session["history"].append(
        {
            "role": "assistant",
            "content": question,
        }
    )

    return {
        "session_id": session["id"],
        "candidate": candidate,
        "question_no": 1,
        "total_questions": 8,
        "question": question,
    }


# --------------------------------------------------
# Submit Interview Answer
# --------------------------------------------------

@app.post("/api/interview/answer")
def answer(req: AnswerRequest):

    session = sessions.get(req.session_id)

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    if session["finished"]:
        return {
            "finished": True,
            "feedback": feedback(session),
        }

    # Get the current interviewer question
    assistant_messages = [
        item
        for item in session["history"]
        if item.get("role") == "assistant"
    ]

    if not assistant_messages:
        raise HTTPException(
            status_code=400,
            detail="No active interview question found.",
        )

    current_question = assistant_messages[-1]["content"]

    # Send candidate answer to the AI interviewer
    result = submit_answer(
        session=session,
        question=current_question,
        text=req.answer,
    )

    # Interview completed
    if result["finished"]:

        return {
            "finished": True,
            "evaluation": result["evaluation"],
            "feedback": feedback(session),
            "covered_days": sorted(
                set(session["covered"])
            ),
        }

    # Continue interview
    return {
        "finished": False,
        "evaluation": result["evaluation"],
        "question_no": session["n"],
        "question": result["question"],
        "covered_days": sorted(
            set(session["covered"])
        ),
    }