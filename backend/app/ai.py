import json
import os
from typing import Any

import httpx
from dotenv import load_dotenv


load_dotenv()


AI_API_KEY = os.getenv("AI_API_KEY")
AI_MODEL = os.getenv("AI_MODEL")
AI_API_URL = os.getenv(
    "AI_API_URL",
    "https://api.openai.com/v1/chat/completions",
)


def ai_available() -> bool:
    return bool(AI_API_KEY and AI_MODEL)


def evaluate_answer(
    question: str,
    answer: str,
    candidate: dict[str, Any],
) -> dict[str, Any]:

    if not ai_available():
        return fallback_evaluation(answer)

    prompt = f"""
You are a senior technical interviewer.

Evaluate the candidate's answer to the interview question.

Candidate:
Name: {candidate.get("name")}
Role: {candidate.get("job_role")}
Experience: {candidate.get("years_experience")} years

Question:
{question}

Candidate answer:
{answer}

Return ONLY valid JSON with this structure:

{{
  "score": 0,
  "quality": "strong|adequate|weak",
  "what_was_good": "short explanation",
  "what_is_missing": "short explanation",
  "suggestion": "specific actionable improvement",
  "should_follow_up": true,
  "follow_up_direction": "what the interviewer should probe next"
}}

Rules:

- Evaluate technical correctness, not answer length.
- Do not invent knowledge the candidate did not demonstrate.
- Be fair.
- A short but technically correct answer can score highly.
- A long but incorrect answer should score poorly.
- Suggestions must be specific.
"""

    result = call_ai(prompt)

    if not result:
        return fallback_evaluation(answer)

    return result


def generate_final_feedback(
    candidate: dict[str, Any],
    transcript: list[dict[str, Any]],
) -> dict[str, Any]:

    if not ai_available():
        return fallback_final_feedback(transcript)

    prompt = f"""
You are a senior AI engineering interviewer.

Create a personalized interview report.

Candidate:
Name: {candidate.get("name")}
Role: {candidate.get("job_role")}
Experience: {candidate.get("years_experience")} years
Education: {candidate.get("education")}

Interview transcript:
{json.dumps(transcript, indent=2)}

Return ONLY valid JSON:

{{
  "overall_score": 0,
  "summary": "short overall assessment",
  "strengths": [
    "specific strength"
  ],
  "improvements": [
    "specific weakness"
  ],
  "topic_gaps": [
    "topic the candidate should revise"
  ],
  "next_learning_steps": [
    "specific actionable learning step"
  ]
}}

Important:

- Base the report ONLY on the interview evidence.
- Do not give generic advice.
- Mention specific technical concepts demonstrated or missed.
- Suggestions should be useful for interview preparation.
"""

    result = call_ai(prompt)

    if result:
        return result

    return fallback_final_feedback(transcript)


def call_ai(prompt: str) -> dict[str, Any] | None:

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
                    "You are a precise technical interviewer. "
                    "Return only valid JSON."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "temperature": 0.3,
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

        content = data["choices"][0]["message"]["content"]

        return json.loads(content)

    except Exception as error:
        print(f"AI evaluation failed: {error}")
        return None


def fallback_evaluation(answer: str) -> dict[str, Any]:

    words = len(answer.split())

    if words < 8:
        score = 45
        quality = "weak"
    elif words < 25:
        score = 65
        quality = "adequate"
    elif words < 60:
        score = 78
        quality = "adequate"
    else:
        score = 88
        quality = "strong"

    return {
        "score": score,
        "quality": quality,
        "what_was_good": "The candidate attempted the question.",
        "what_is_missing": "More technical detail may be needed.",
        "suggestion": "Use a concrete example and explain the engineering trade-offs.",
        "should_follow_up": score < 80,
        "follow_up_direction": "Probe the candidate's reasoning and trade-offs.",
    }


def fallback_final_feedback(
    transcript: list[dict[str, Any]],
) -> dict[str, Any]:

    candidate_answers = [
        item
        for item in transcript
        if item.get("role") == "candidate"
    ]

    return {
        "overall_score": 0,
        "summary": "AI feedback is unavailable. Please configure the AI API key.",
        "strengths": [
            "Candidate completed the interview."
        ],
        "improvements": [
            "Configure AI evaluation for detailed feedback."
        ],
        "topic_gaps": [],
        "next_learning_steps": [
            "Review the concepts discussed during the interview.",
            "Practice explaining technical decisions with concrete examples.",
        ],
    }