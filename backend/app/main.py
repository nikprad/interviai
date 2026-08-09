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
from .breeth_memory import save_memory, search_memory


app = FastAPI(
    title="InterviAI API",
    version="0.3.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST MODELS
# ============================================================

class StartRequest(BaseModel):
    candidate_id: str


class AnswerRequest(BaseModel):
    session_id: str
    answer: str


class MemorySearchRequest(BaseModel):
    query: str


class MemorySaveRequest(BaseModel):
    content: str
    session_id: str = "manual-session"


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "InterviAI API",
        "memory": "Breeth enabled",
    }


# ============================================================
# CANDIDATES
# ============================================================

@app.get("/api/candidates")
def candidates():
    return CANDIDATES


# ============================================================
# START INTERVIEW
# ============================================================

@app.post("/api/interview/start")
def start(req: StartRequest):

    # --------------------------------------------------------
    # Find candidate
    # --------------------------------------------------------

    candidate = candidate_by_id(req.candidate_id)

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found",
        )

    candidate_name = candidate.get(
        "name",
        req.candidate_id,
    )

    # --------------------------------------------------------
    # Search Breeth for previous candidate memory
    # --------------------------------------------------------

    try:
        previous_memory = search_memory(
            (
                f"Previous interview performance, "
                f"weaknesses, strengths and learning needs "
                f"of {candidate_name}"
            )
        )

    except Exception as exc:
        print(f"Breeth search warning: {exc}")

        previous_memory = {
            "edges": [],
            "note": "Memory unavailable",
        }

    # --------------------------------------------------------
    # Create interview session
    # --------------------------------------------------------

    try:
        session = start_session(candidate)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    # Store candidate in session.
    # This is required later when saving Breeth memories.
    session["candidate"] = candidate

    # Store previous memory in session.
    session["previous_memory"] = previous_memory

    # --------------------------------------------------------
    # First question
    # --------------------------------------------------------

    question = session["seeds"][0][1]

    session["history"].append(
        {
            "role": "assistant",
            "content": question,
        }
    )

    # --------------------------------------------------------
    # Save interview start event to Breeth
    # --------------------------------------------------------

    try:
        save_memory(
            (
                f"Candidate {candidate_name} started an "
                f"InterviAI interview session. "
                f"Candidate ID: {req.candidate_id}. "
                f"The interview will assess AI engineering "
                f"knowledge and practical system design."
            ),
            session["id"],
        )

    except Exception as exc:
        print(f"Breeth start memory warning: {exc}")

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {
        "session_id": session["id"],
        "candidate": candidate,
        "question_no": 1,
        "total_questions": 8,
        "question": question,
        "previous_memory": previous_memory,
        "memory_enabled": True,
    }


# ============================================================
# SUBMIT INTERVIEW ANSWER
# ============================================================

@app.post("/api/interview/answer")
def answer(req: AnswerRequest):

    # --------------------------------------------------------
    # Find session
    # --------------------------------------------------------

    session = sessions.get(req.session_id)

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    # --------------------------------------------------------
    # Already finished
    # --------------------------------------------------------

    if session["finished"]:

        final_feedback = feedback(session)

        return {
            "finished": True,
            "feedback": final_feedback,
            "memory_enabled": True,
        }

    # --------------------------------------------------------
    # Get candidate
    # --------------------------------------------------------

    candidate = session.get("candidate", {})

    candidate_name = candidate.get(
        "name",
        "Candidate",
    )

    # --------------------------------------------------------
    # Generate next question / score answer
    #
    # submit_answer() already stores the answer
    # in session history.
    # --------------------------------------------------------

    question = submit_answer(
        session,
        req.answer,
    )

    # --------------------------------------------------------
    # Save answer + score to Breeth
    # --------------------------------------------------------

    current_score = session["scores"][-1]

    try:
        save_memory(
            (
                f"Candidate {candidate_name} answered an "
                f"InterviAI interview question. "
                f"Answer: {req.answer}. "
                f"Answer score: {current_score}/100."
            ),
            req.session_id,
        )

    except Exception as exc:
        print(f"Breeth answer memory warning: {exc}")

    # --------------------------------------------------------
    # Interview finished
    # --------------------------------------------------------

    if session["finished"]:

        final_feedback = feedback(session)

        # ----------------------------------------------------
        # Save final interview result to Breeth
        # ----------------------------------------------------

        try:
            save_memory(
                (
                    f"Candidate {candidate_name} completed "
                    f"an InterviAI interview. "
                    f"Overall score: "
                    f"{final_feedback['overall_score']}/100. "
                    f"Strengths: "
                    f"{', '.join(final_feedback['strengths'])}. "
                    f"Improvements: "
                    f"{', '.join(final_feedback['improvements'])}. "
                    f"Next learning steps: "
                    f"{', '.join(final_feedback['next_learning_steps'])}."
                ),
                req.session_id,
            )

        except Exception as exc:
            print(f"Breeth feedback memory warning: {exc}")

        return {
            "finished": True,
            "feedback": final_feedback,
            "covered_days": sorted(
                set(session["covered"])
            ),
            "memory_saved": True,
        }

    # --------------------------------------------------------
    # Continue interview
    # --------------------------------------------------------

    return {
        "finished": False,
        "question_no": session["n"],
        "question": question,
        "covered_days": sorted(
            set(session["covered"])
        ),
        "memory_enabled": True,
    }


# ============================================================
# BREETH MEMORY SEARCH
# ============================================================

@app.post("/api/memory/search")
def memory_search(req: MemorySearchRequest):

    try:
        result = search_memory(req.query)

        return {
            "success": True,
            "query": req.query,
            "memory": result,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Breeth memory search failed: {str(exc)}",
        )


# ============================================================
# BREETH MEMORY SAVE
# ============================================================

@app.post("/api/memory/save")
def memory_save(req: MemorySaveRequest):

    try:
        result = save_memory(
            req.content,
            req.session_id,
        )

        return {
            "success": True,
            "result": result,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Breeth memory save failed: {str(exc)}",
        )