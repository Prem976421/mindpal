import json
import uvicorn
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional

from src.config import STATIC_DIR, GEMINI_MODEL
from src.db import (
    init_db,
    create_session,
    list_sessions,
    get_session,
    delete_session,
    get_session_messages,
    log_mood,
    get_mood_logs
)
from src.gemini_service import stream_chat_turn, get_client
from src.rag import get_vector_store

# Initialize DB and Knowledge Base vector store
init_db()
vs = get_vector_store()
if not vs.chunks:
    vs.sync_knowledge_base()

app = FastAPI(title="MindPal - Student Mental Well-being Companion")

# Mount static directory
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

class CreateSessionRequest(BaseModel):
    title: Optional[str] = "New Reflection"

class ChatRequest(BaseModel):
    session_id: str
    message: str

class MoodRequest(BaseModel):
    mood: str
    energy: int = 3
    note: Optional[str] = ""

class WorryTriageRequest(BaseModel):
    worry_dump: str

class ReframeRequest(BaseModel):
    catastrophic_thought: str

class MicroStarterRequest(BaseModel):
    intimidating_task: str

@app.get("/")
def serve_index():
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="Index file not found")
    return FileResponse(index_file)

@app.get("/api/sessions")
def get_sessions():
    return list_sessions()

@app.post("/api/sessions")
def create_new_session(req: CreateSessionRequest):
    session_id = create_session(req.title or "New Reflection")
    return {"id": session_id, "title": req.title}

@app.get("/api/sessions/{session_id}/messages")
def get_messages(session_id: str):
    sess = get_session(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    messages = get_session_messages(session_id)
    return {
        "session": sess,
        "messages": messages
    }

@app.delete("/api/sessions/{session_id}")
def remove_session(session_id: str):
    delete_session(session_id)
    return {"status": "deleted", "id": session_id}

@app.post("/api/chat/stream")
def chat_stream(req: ChatRequest):
    sess = get_session(req.session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    
    def event_generator():
        try:
            for token in stream_chat_turn(req.session_id, req.message):
                data_json = json.dumps({"token": token})
                yield f"data: {data_json}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            err_json = json.dumps({"error": str(e)})
            yield f"data: {err_json}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# ----------------- ACTION TOOLS FOR STUDENT WELL-BEING -----------------

@app.post("/api/tools/worry-triage")
def triage_worry_dump(req: WorryTriageRequest):
    """Parses racing student worries into:
    1. Things in your direct control today (with bite-sized micro-steps)
    2. Things outside your control to release
    3. Comforting summary
    """
    client = get_client()
    prompt = f"""You are MindPal's Worry Triage Specialist for students.
Analyze this raw student worry dump:
"{req.worry_dump}"

Provide a warm, structured, highly calming breakdown:
1. **Immediate Controllables (What you CAN do today)**: Pick 2-3 specific small things and pair each with a tiny, zero-stress 5-minute action step.
2. **Uncontrollables to Release Tonight**: Name what is outside their immediate control (e.g. how hard the exam might be, other people's opinions, past mistakes) and provide a 1-sentence permission to let it go for right now.
3. **Your Single Next Step**: ONE gentle action to do in the next 10 minutes, followed by a warm encouraging note.

Use clean markdown, comforting bullet points, and an empathetic, soothing tone.
"""
    try:
        res = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )
        return {"result": res.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tools/reframe")
def reframe_thought(req: ReframeRequest):
    """Identifies the cognitive distortion in a student's spiral and generates a balanced reframe."""
    client = get_client()
    prompt = f"""You are MindPal's Cognitive Behavioral Therapy (CBT) Thought Specialist for students.
A student is having this overwhelming thought:
"{req.catastrophic_thought}"

Provide a compassionate, structured cognitive reframe:
1. **The Pattern**: Name the cognitive trap in friendly student terms (e.g., Catastrophizing / The 'All-or-Nothing' Trap / Fortune Telling).
2. **Reality Check**: Objectively test the thought without invalidating their emotion. Why is the worst-case scenario unlikely or survivable?
3. **Balanced Reframe**: A realistic, empowering statement they can tell themselves right now that replaces panic with perspective.

Keep it bite-sized, constructive, and warm. Use markdown.
"""
    try:
        res = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )
        return {"result": res.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tools/micro-starter")
def generate_micro_starter(req: MicroStarterRequest):
    """Deconstructs an overwhelming assignment or study task into a tiny 5-minute activation step."""
    client = get_client()
    prompt = f"""You are MindPal's Academic Procrastination & Activation Coach.
A student is paralyzed by this task:
"{req.intimidating_task}"

Procrastination is an emotional defense mechanism against overwhelm.
Create the ultimate low-friction "Micro-Kickstart":
1. **The 5-Minute Micro-Action**: Design an initial step so absurdly small and easy that their brain cannot resist starting (e.g. 'Just open Google Docs, title it Lab Report, and write 1 bullet point').
2. **Activation Mantra**: A 1-sentence calming reminder to lower perfectionist pressure.
3. **Permission to Stop**: Explicitly remind them they only need to commit to 5 minutes—if they want to stop after 5 minutes, they can, but starting breaks the freeze state.

Format cleanly with markdown.
"""
    try:
        res = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )
        return {"result": res.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/mood")
def add_mood_entry(req: MoodRequest):
    log_mood(req.mood, req.energy, req.note or "")
    return {"status": "logged"}

@app.get("/api/mood")
def list_mood_entries():
    return get_mood_logs(20)

if __name__ == "__main__":
    print("🌱 Starting MindPal Student Companion on http://localhost:8000 ...")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
