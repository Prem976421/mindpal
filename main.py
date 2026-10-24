import json
import uvicorn
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional

from src.config import STATIC_DIR
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
from src.gemini_service import stream_chat_turn
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
                # Send JSON-encoded SSE data
                data_json = json.dumps({"token": token})
                yield f"data: {data_json}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            err_json = json.dumps({"error": str(e)})
            yield f"data: {err_json}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

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
