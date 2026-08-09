from uuid import uuid4
from typing import Any

from .ai import evaluate_answer, generate_final_feedback


SEEDS = [
    (
        4,
        "Explain how a RAG system turns a user question into a grounded answer.",
    ),
    (
        10,
        "What are embeddings, and why are they useful for semantic retrieval?",
    ),
    (
        13,
        "How would you make an LLM reliably return valid JSON?",
    ),
    (
        16,
        "What makes an AI agent different from a simple LLM call?",
    ),
    (
        19,
        "What problem does MCP solve in an AI application architecture?",
    ),
    (
        7,
        "How would you choose chunk size and overlap for a long technical document?",
    ),
    (
        22,
        "You need to deploy this interview agent for 10,000 users. What would you consider first?",
    ),
    (
        25,
        "How would you evaluate whether your interview agent is producing useful assessments?",
    ),
]


sessions: dict[str, dict[str, Any]] = {}


def start_session(candidate: dict[str, Any]):
    seeds = [
        item
        for item in SEEDS
        if item[0] in candidate.get("completed_days", [])
    ]

    if len(set(day for day, _ in seeds)) < 4:
        raise ValueError(
            "Candidate needs at least 4 completed curriculum days."
        )

    session_id = str(uuid4())

    sessions[session_id] = {
        "id": session_id,
        "candidate_id": candidate["id"],
        "candidate": candidate,
        "n": 1,
        "scores": [],
        "evaluations": [],
        "covered": [],
        "history": [],
        "seeds": seeds,
        "finished": False,
    }

    return sessions[session_id]


def submit_answer(
    session: dict[str, Any],
    question: str,
    text: str,
):
    """
    Evaluate the candidate's answer using AI and decide
    what the interviewer should ask next.
    """

    evaluation = evaluate_answer(
        question=question,
        answer=text,
        candidate=session["candidate"],
    )

    score = int(evaluation.get("score", 0))

    session["scores"].append(score)
    session["evaluations"].append(evaluation)

    # Save candidate answer
    session["history"].append(
        {
            "role": "candidate",
            "content": text,
        }
    )

    # Identify the curriculum day associated with this question.
    current_index = session["n"] - 1

    if current_index < len(session["seeds"]):
        day, _ = session["seeds"][current_index]
        session["covered"].append(day)

    # Minimum requirement: 8 questions.
    if session["n"] >= 8:
        session["finished"] = True

        return {
            "finished": True,
            "evaluation": evaluation,
        }

    # AI decides whether a follow-up is needed.
    if evaluation.get("should_follow_up") is True:
        direction = evaluation.get(
            "follow_up_direction",
            "Probe the candidate's reasoning further.",
        )

        next_question = build_follow_up_question(
            question=question,
            answer=text,
            direction=direction,
        )

    else:
        next_question = next_seed_question(session)

    session["n"] += 1

    session["history"].append(
        {
            "role": "assistant",
            "content": next_question,
        }
    )

    return {
        "finished": False,
        "evaluation": evaluation,
        "question": next_question,
    }


def build_follow_up_question(
    question: str,
    answer: str,
    direction: str,
) -> str:
    """
    Create a contextual follow-up question.

    This is deliberately separate from the main evaluation so
    the interviewer can react to the candidate's actual answer.
    """

    from .ai import call_ai

    prompt = f"""
You are conducting a realistic technical interview.

Original question:
{question}

Candidate answer:
{answer}

Interviewer should probe:
{direction}

Generate ONE concise technical follow-up question.

Rules:
- Do not repeat the original question.
- Do not ask for information unrelated to the answer.
- Probe the candidate's reasoning.
- Ask about a trade-off, failure mode, implementation detail,
  example, or design decision when appropriate.
- Sound like a real human interviewer.
- Return ONLY the question.
"""

    result = call_ai_text(prompt)

    if result:
        return result

    return "Can you explain your reasoning with a concrete technical example?"


def next_seed_question(session: dict[str, Any]) -> str:
    """
    Move to the next curriculum topic.
    """

    index = session["n"]

    if index < len(session["seeds"]):
        return session["seeds"][index][1]

    return (
        "Can you explain one production challenge you would expect "
        "when implementing this system?"
    )


def call_ai_text(prompt: str) -> str | None:
    """
    Small helper for text-only AI responses.
    """

    from .ai import AI_API_KEY, AI_API_URL, AI_MODEL
    import httpx

    if not AI_API_KEY or not AI_MODEL:
        return None

    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": AI_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a senior technical interviewer. "
                    "Return only the requested text."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "temperature": 0.4,
    }

    try:
        with httpx.Client(timeout=60) as client:
            response = client.post(
                AI_API_URL,
                headers=headers,
                json=payload,
            )

        response.raise_for_status()

        data = response.json()

        return data["choices"][0]["message"]["content"].strip()

    except Exception as error:
        print(f"AI follow-up generation failed: {error}")
        return None


def feedback(session: dict[str, Any]):
    """
    Generate the final personalized interview report.
    """

    report = generate_final_feedback(
        candidate=session["candidate"],
        transcript=session["history"],
    )

    return {
        **report,
        "questions": len(session["scores"]),
        "curriculum_days_covered": sorted(
            set(session["covered"])
        ),
        "answer_evaluations": session["evaluations"],
    }