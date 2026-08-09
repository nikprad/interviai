import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const API = "https://backend-22b-8000.ny1.zerops.app";

function App() {
  const [candidates, setCandidates] = useState([]);
  const [candidate, setCandidate] = useState(null);
  const [session, setSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [covered, setCovered] = useState([]);
  const [error, setError] = useState("");

  // ==============================
  // LOAD CANDIDATES
  // ==============================

  useEffect(() => {
    async function loadCandidates() {
      try {
        setError("");

        const response = await fetch(`${API}/api/candidates`);

        if (!response.ok) {
          throw new Error("Unable to load candidates.");
        }

        const data = await response.json();

        const rawCandidates = Array.isArray(data)
          ? data
          : Array.isArray(data.candidates)
          ? data.candidates
          : [];

        const normalizedCandidates = rawCandidates.map((item) => {
          return item.member || item;
        });

        setCandidates(normalizedCandidates);

        if (normalizedCandidates.length === 0) {
          setError("No candidates available.");
        }
      } catch (err) {
        console.error("Candidate loading error:", err);
        setError(
          "Could not connect to the backend. Make sure FastAPI is running on port 8000."
        );
      }
    }

    loadCandidates();
  }, []);

  // ==============================
  // START INTERVIEW
  // ==============================

  async function startInterview() {
    if (!candidate) {
      setError("Please select a candidate first.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API}/api/interview/start`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          candidate_id: candidate.id,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to start the interview."
        );
      }

      setSession(data);

      setMessages([
        {
          role: "assistant",
          content: data.question,
        },
      ]);

      setCovered([]);
      setResult(null);
      setAnswer("");
    } catch (err) {
      console.error("Start interview error:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  // ==============================
  // SUBMIT ANSWER
  // ==============================

  async function sendAnswer() {
    if (!answer.trim() || !session || loading) {
      return;
    }

    const text = answer.trim();

    setMessages((current) => [
      ...current,
      {
        role: "candidate",
        content: text,
      },
    ]);

    setAnswer("");
    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API}/api/interview/answer`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          session_id: session.session_id,
          answer: text,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to submit answer."
        );
      }

      setCovered(data.covered_days || []);

      if (data.finished) {
        setResult(data.feedback);
      } else {
        setMessages((current) => [
          ...current,
          {
            role: "assistant",
            content: data.question,
          },
        ]);

        setSession((current) => ({
          ...current,
          question_no: data.question_no,
        }));
      }
    } catch (err) {
      console.error("Answer error:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  // ==============================
  // RESET INTERVIEW
  // ==============================

  function resetInterview() {
    setCandidate(null);
    setSession(null);
    setMessages([]);
    setAnswer("");
    setResult(null);
    setCovered([]);
    setLoading(false);
    setError("");
  }

  // ==============================
  // SHARED: LEDGER (signature element)
  // Renders curriculum days like a commit log — a filled marker
  // for each day actually covered in this interview, in order.
  // ==============================

  function Ledger({ days, dense }) {
    if (!days || days.length === 0) {
      return (
        <p className="ledger-empty">
          No days logged yet — the ledger fills in as the
          interview progresses.
        </p>
      );
    }

    return (
      <ol className={`ledger ${dense ? "ledger-dense" : ""}`}>
        {days.map((day, idx) => (
          <li key={day} className="ledger-row">
            <span className="ledger-index">
              {String(idx + 1).padStart(2, "0")}
            </span>
            <span className="ledger-marker" aria-hidden="true" />
            <span className="ledger-day">Day {day}</span>
          </li>
        ))}
      </ol>
    );
  }

  // ==============================
  // SCREEN 1 — CANDIDATE SELECT
  // ==============================

  if (!session && !result) {
    return (
      <div className="shell">
        <header className="topbar">
          <div className="wordmark">
            <span className="wordmark-mark">IA</span>
            <div className="wordmark-text">
              <strong>InterviAI</strong>
              <small>Curriculum-grounded technical interviews</small>
            </div>
          </div>
          <div className="pill pill-live">
            <span className="pulse" />
            system online
          </div>
        </header>

        <main className="landing">
          <section className="landing-intro">
            <span className="eyebrow">adaptive · agentic · grounded</span>
            <h1>
              An interviewer that only asks
              <br />
              what you actually learned.
            </h1>
            <p className="lede">
              Every question here traces back to a specific day in the
              candidate's curriculum record. Answer well, and the agent
              digs deeper on the same topic. Answer thin, and it gives
              you a second angle before moving on.
            </p>

            <dl className="stat-row">
              <div>
                <dt>08</dt>
                <dd>questions per session</dd>
              </div>
              <div>
                <dt>31</dt>
                <dd>day curriculum pool</dd>
              </div>
              <div>
                <dt>1:1</dt>
                <dd>question to real progress</dd>
              </div>
            </dl>
          </section>

          <section className="picker">
            <div className="picker-head">
              <div>
                <span className="eyebrow">step 01</span>
                <h2>Select a candidate</h2>
              </div>
              <span className="count-tag">{candidates.length}</span>
            </div>

            {error && <div className="notice notice-error">{error}</div>}

            <div className="roster" role="list">
              {candidates.length === 0 ? (
                <div className="empty-row">
                  {error ? "Unable to load candidates." : "Loading candidates…"}
                </div>
              ) : (
                candidates.map((item, idx) => {
                  const isSelected = candidate?.id === item.id;
                  return (
                    <button
                      key={item.id}
                      type="button"
                      role="listitem"
                      className={`roster-row ${isSelected ? "is-selected" : ""}`}
                      onClick={() => {
                        setCandidate(item);
                        setError("");
                      }}
                    >
                      <span className="roster-index">
                        {String(idx + 1).padStart(2, "0")}
                      </span>
                      <span className="roster-id">{item.id}</span>
                      <span className="roster-main">
                        <strong>{item.name || "Unknown candidate"}</strong>
                        <em>{item.jobRole || item.job_role || "Technical candidate"}</em>
                      </span>
                      <span className="roster-years">
                        {item.yearsExperience ?? item.years_experience ?? 0}
                        <small>yrs</small>
                      </span>
                      <span className="roster-go" aria-hidden="true">
                        {isSelected ? "✓" : "→"}
                      </span>
                    </button>
                  );
                })
              )}
            </div>

            {candidate && (
              <div className="selected-bar">
                <div>
                  <small>selected</small>
                  <strong>{candidate.name}</strong>
                </div>
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={startInterview}
                  disabled={loading}
                >
                  {loading ? "Starting…" : "Start interview"}
                </button>
              </div>
            )}
          </section>
        </main>

        <footer className="foot">
          <span>InterviAI</span>
          <span>Adaptive technical assessment</span>
        </footer>
      </div>
    );
  }

  // ==============================
  // SCREEN 2 — INTERVIEW
  // ==============================

  if (session && !result) {
    const questionNumber = session.question_no || 1;
    const progressPercentage = Math.min(100, (questionNumber / 8) * 100);
    const barCells = Array.from({ length: 8 }, (_, i) => i < questionNumber);

    return (
      <div className="shell">
        <header className="topbar topbar-session">
          <div className="wordmark">
            <span className="wordmark-mark">IA</span>
            <div className="wordmark-text">
              <strong>InterviAI</strong>
              <small>Session in progress</small>
            </div>
          </div>
          <div className="session-meter" aria-label={`Question ${questionNumber} of 8`}>
            {barCells.map((filled, i) => (
              <span key={i} className={filled ? "cell cell-on" : "cell"} />
            ))}
            <span className="session-meter-label">{questionNumber}/8</span>
          </div>
        </header>

        <main className="interview">
          {error && <div className="notice notice-error notice-inline">{error}</div>}

          <div className="interview-grid">
            <section className="transcript-card">
              <div className="transcript-head">
                <div>
                  <strong>{candidate?.name}</strong>
                  <span>{candidate?.jobRole || candidate?.job_role}</span>
                </div>
                <div className="pill pill-live">
                  <span className="pulse" />
                  live
                </div>
              </div>

              <div className="transcript-body">
                {messages.map((message, index) => (
                  <div
                    key={`${message.role}-${index}`}
                    className={`bubble ${
                      message.role === "assistant" ? "bubble-agent" : "bubble-candidate"
                    }`}
                  >
                    <span className="bubble-label">
                      {message.role === "assistant" ? "InterviAI" : candidate?.name || "You"}
                    </span>
                    <p>{message.content}</p>
                  </div>
                ))}

                {loading && (
                  <div className="thinking">
                    <span />
                    <span />
                    <span />
                    evaluating response…
                  </div>
                )}
              </div>

              <div className="composer">
                <textarea
                  value={answer}
                  onChange={(event) => setAnswer(event.target.value)}
                  placeholder="Write your technical answer…"
                  disabled={loading}
                  onKeyDown={(event) => {
                    if (event.key === "Enter" && !event.shiftKey) {
                      event.preventDefault();
                      sendAnswer();
                    }
                  }}
                />
                <div className="composer-foot">
                  <span>Enter to submit · Shift+Enter for a new line</span>
                  <button
                    type="button"
                    className="btn btn-primary"
                    onClick={sendAnswer}
                    disabled={!answer.trim() || loading}
                  >
                    {loading ? "Evaluating…" : "Submit answer"}
                  </button>
                </div>
              </div>
            </section>

            <aside className="ledger-card">
              <div className="ledger-card-head">
                <span className="eyebrow">curriculum ledger</span>
                <h3>Days covered</h3>
              </div>
              <Ledger days={covered} />

              <div className="ledger-card-foot">
                <span className="eyebrow">candidate</span>
                <strong>{candidate?.name}</strong>
                <small>{candidate?.jobRole || candidate?.job_role}</small>
              </div>
            </aside>
          </div>
        </main>
      </div>
    );
  }

  // ==============================
  // SCREEN 3 — RESULTS
  // ==============================

  const score = result?.overall_score ?? 0;
  const verdict =
    score >= 85 ? "Excellent" : score >= 70 ? "Strong performance" : score >= 55 ? "Developing" : "Needs improvement";
  const filledCells = Math.round((score / 100) * 20);

  return (
    <div className="shell">
      <header className="topbar">
        <div className="wordmark">
          <span className="wordmark-mark">IA</span>
          <div className="wordmark-text">
            <strong>InterviAI</strong>
            <small>Assessment complete</small>
          </div>
        </div>
        <div className="pill">assessment complete</div>
      </header>

      <main className="results">
        <section className="results-head">
          <span className="eyebrow">interview complete</span>
          <h1>Technical assessment report</h1>
        </section>

        <section className="score-card">
          <div className="score-block">
            <div className="score-bar" aria-label={`Score ${score} of 100`}>
              {Array.from({ length: 20 }, (_, i) => (
                <span key={i} className={i < filledCells ? "sb-cell sb-on" : "sb-cell"} />
              ))}
            </div>
            <div className="score-numbers">
              <span className="score-value">{score}</span>
              <span className="score-max">/100</span>
            </div>
            <strong className="score-verdict">{verdict}</strong>
            <small>
              Based on {result?.questions ?? 0} technical interview questions
            </small>
          </div>

          <div className="score-grid">
            <div className="score-col">
              <div className="score-col-head">
                <span className="marker marker-strong" />
                <h4>Strengths</h4>
              </div>
              {result?.strengths?.map((item, index) => (
                <p key={`s-${index}`} className="score-item">{item}</p>
              ))}
            </div>

            <div className="score-col">
              <div className="score-col-head">
                <span className="marker marker-weak" />
                <h4>Areas to improve</h4>
              </div>
              {result?.improvements?.map((item, index) => (
                <p key={`i-${index}`} className="score-item">{item}</p>
              ))}
            </div>
          </div>

          <div className="next-steps">
            <div className="score-col-head">
              <span className="marker marker-accent" />
              <h4>Recommended next steps</h4>
            </div>
            <ol className="steps-list">
              {result?.next_learning_steps?.map((item, index) => (
                <li key={`n-${index}`}>{item}</li>
              ))}
            </ol>
          </div>

          <div className="results-ledger">
            <div className="score-col-head">
              <span className="marker marker-accent" />
              <h4>Curriculum covered</h4>
            </div>
            <Ledger days={result?.curriculum_days_covered} dense />
          </div>

          <div className="results-actions">
            <button type="button" className="btn btn-ghost" onClick={resetInterview}>
              Start new interview
            </button>
          </div>
        </section>
      </main>
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);
