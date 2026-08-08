from uuid import uuid4

SEEDS = [
 (4,"Explain how a RAG system turns a user question into a grounded answer."),
 (10,"What are embeddings, and why are they useful for semantic retrieval?"),
 (13,"How would you make an LLM reliably return valid JSON?"),
 (16,"What makes an AI agent different from a simple LLM call?"),
 (19,"What problem does MCP solve in an AI application architecture?"),
 (7,"How would you choose chunk size and overlap for a long technical document?"),
 (22,"You need to deploy this interview agent for 10,000 users. What would you consider first?"),
 (25,"How would you evaluate whether your interview agent is producing useful assessments?")
]

sessions = {}

def start_session(candidate):
    seeds = [x for x in SEEDS if x[0] in candidate["completed_days"]]
    if len(set(d for d,_ in seeds)) < 4:
        raise ValueError("Candidate needs at least 4 completed curriculum days.")
    sid = str(uuid4())
    sessions[sid] = {
        "id": sid, "candidate_id": candidate["id"], "n": 1,
        "scores": [], "covered": [], "history": [], "seeds": seeds, "finished": False
    }
    return sessions[sid]

def score(text):
    n = len(text.split())
    return 45 if n < 8 else 65 if n < 25 else 78 if n < 60 else 88

def submit_answer(session, text):
    sc = score(text)
    session["scores"].append(sc)
    day,_ = session["seeds"][(session["n"]-1) % len(session["seeds"])]
    session["covered"].append(day)
    session["history"].append({"role":"candidate","content":text})

    if session["n"] >= 8:
        session["finished"] = True
        return None

    if sc < 70:
        q = "What specific failure mode or trade-off would you watch for in production?"
    elif sc < 82:
        q = "Give a concrete example and explain why you would choose that approach."
    else:
        q = "How would you evaluate and monitor this design after deployment?"

    session["n"] += 1
    session["history"].append({"role":"assistant","content":q})
    return q

def feedback(session):
    return {
        "overall_score": round(sum(session["scores"]) / len(session["scores"])),
        "questions": len(session["scores"]),
        "curriculum_days_covered": sorted(set(session["covered"])),
        "strengths": [
            "Explains core AI concepts with structure.",
            "Connects concepts to engineering decisions."
        ],
        "improvements": [
            "Use more concrete production examples.",
            "Discuss trade-offs, evaluation and failure modes explicitly."
        ],
        "next_learning_steps": [
            "Practice senior-level RAG and agent system design.",
            "Document evaluation and monitoring for one production AI project."
        ]
    }
