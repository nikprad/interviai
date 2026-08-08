from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .data import CANDIDATES, candidate_by_id
from .interview import start_session, sessions, submit_answer, feedback


app = FastAPI(title="InterviAI API", version="0.1.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class StartRequest(BaseModel):
    candidate_id: str


class AnswerRequest(BaseModel):
    session_id: str
    answer: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/candidates")
def candidates():
    return CANDIDATES


@app.post("/api/interview/start")
def start(req: StartRequest):
    candidate = candidate_by_id(req.candidate_id)

    if not candidate:
        raise HTTPException(404, "Candidate not found")

    try:
        session = start_session(candidate)
    except ValueError as exc:
        raise HTTPException(400, str(exc))

    question = session["seeds"][0][1]

    session["history"].append(
        {"role": "assistant", "content": question}
    )

    return {
        "session_id": session["id"],
        "candidate": candidate,
        "question_no": 1,
        "total_questions": 8,
        "question": question,
    }


@app.post("/api/interview/answer")
def answer(req: AnswerRequest):
    session = sessions.get(req.session_id)

    if not session:
        raise HTTPException(404, "Session not found")

    if session["finished"]:
        return {
            "finished": True,
            "feedback": feedback(session),
        }

    question = submit_answer(session, req.answer)

    if session["finished"]:
        return {
            "finished": True,
            "feedback": feedback(session),
            "covered_days": sorted(set(session["covered"])),
        }

    return {
        "finished": False,
        "question_no": session["n"],
        "question": question,
        "covered_days": sorted(set(session["covered"])),
    }


 # @app.get("/curriculum")
# def curriculum():
     #try:
       # data = get_curriculum()

       # return {
         #   "success": True,
           # "curriculum": data,
       # }

    # except FileNotFoundError as error:
        # raise HTTPException(
          #  status_code=404,
           # detail=str(error),
       # )

   # except ValueError as error:
   #     raise HTTPException(
   #         status_code=400,
   #         detail=str(error),
      #  )


# @app.get("/candidate/{candidate_id}")
# def candidate(candidate_id: str):
   # try:
      #  data = get_candidate(candidate_id)

       # return {
       #     "success": True,
      #      "candidate": data,
      #  }

  #  except FileNotFoundError as error:
       # raise HTTPException(
       #     status_code=404,
      #      detail=str(error),
     #   )

   # except ValueError as error:
       # raise HTTPException(
        #    status_code=404,
      #      detail=str(error),
     #   ) 