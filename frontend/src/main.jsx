import React, {useEffect,useState} from "react";
import {createRoot} from "react-dom/client";
import "./styles.css";

const API="http://localhost:8000";

function App(){
 const [candidates,setCandidates]=useState([]);
 const [candidate,setCandidate]=useState(null);
 const [session,setSession]=useState(null);
 const [messages,setMessages]=useState([]);
 const [answer,setAnswer]=useState("");
 const [loading,setLoading]=useState(false);
 const [result,setResult]=useState(null);
 const [covered,setCovered]=useState([]);

 useEffect(()=>{fetch(API+"/api/candidates").then(r=>r.json()).then(setCandidates)},[]);

 async function start(){
   setLoading(true);
   const r=await fetch(API+"/api/interview/start",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({candidate_id:candidate.id})});
   const d=await r.json();
   setSession(d); setMessages([{role:"assistant",content:d.question}]); setCovered([]); setResult(null); setLoading(false);
 }

 async function send(){
   if(!answer.trim()||!session)return;
   const text=answer;
   setMessages(m=>[...m,{role:"candidate",content:text}]);
   setAnswer(""); setLoading(true);
   const r=await fetch(API+"/api/interview/answer",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({session_id:session.session_id,answer:text})});
   const d=await r.json();
   setCovered(d.covered_days||[]);
   if(d.finished) setResult(d.feedback);
   else setMessages(m=>[...m,{role:"assistant",content:d.question}]);
   setLoading(false);
 }

 if(!session) return <div className="app"><header><b>Intervi<span>AI</span></b><small>Technical Interview Agent</small></header><main className="hero">
   <div><label>VIDOTHON • AI ENGINEERING</label><h1>Interview based on <span>what you learned.</span></h1><p>Adaptive technical interviews built from a candidate's learning journey.</p></div>
   <div className="card"><label>Select candidate</label><select value={candidate?.id||""} onChange={e=>setCandidate(candidates.find(c=>c.id===e.target.value))}><option value="">Choose a profile</option>{candidates.map(c=><option key={c.id} value={c.id}>{c.name}</option>)}</select>
   {candidate&&<div className="profile"><b>{candidate.name}</b><small>{candidate.completed_days.length} completed days<br/>{candidate.signal}</small></div>}
   <button disabled={!candidate||loading} onClick={start}>{loading?"Starting…":"Start interview →"}</button></div>
 </main></div>;

 return <div className="app"><header><b>Intervi<span>AI</span></b><small>Senior AI Engineer Interview</small></header><main className="layout">
   <aside className="side"><label>CANDIDATE</label><h2>{candidate.name}</h2><p>{candidate.signal}</p><label>PROGRESS</label><strong>{Math.min(session.question_no,8)}/8</strong><div className="bar"><i style={{width:`${Math.min((session.question_no-1)/8*100,100)}%`}}/></div><label>TOPICS COVERED</label>{covered.length?covered.map(d=><span className="tag" key={d}>Day {d}</span>):<em>Appears during interview</em>}</aside>
   <section className="chat"><div className="chathead"><div><label>LIVE INTERVIEW</label><h2>Adaptive technical round</h2></div><small>● Adaptive</small></div><div className="messages">{messages.map((m,i)=><div className={"msg "+m.role} key={i}><small>{m.role==="assistant"?"InterviAI":"You"}</small><p>{m.content}</p></div>)}</div>
   {result?<div className="result"><div className="score">{result.overall_score}<small>/100</small></div><div><h2>Interview complete</h2><p><b>Strengths:</b> {result.strengths.join(" ")}</p><p><b>Improve:</b> {result.improvements.join(" ")}</p><p><b>Next:</b> {result.next_learning_steps.join(" ")}</p></div></div>:<div className="composer"><textarea value={answer} onChange={e=>setAnswer(e.target.value)} placeholder="Explain your reasoning…" /><button disabled={loading||!answer.trim()} onClick={send}>{loading?"…":"Send"}</button></div>}</section>
 </main></div>
}

createRoot(document.getElementById("root")).render(<App/>);
