import os
from typing import Generator, List, Dict, Any, Optional
from google import genai
from google.genai import types

from src.config import GEMINI_API_KEY, GEMINI_MODEL, SYSTEM_PROMPT
from src.db import add_message, get_session_messages, update_session_title
from src.rag import get_vector_store

def get_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY", GEMINI_API_KEY)
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not configured.")
    return genai.Client(api_key=api_key)

def auto_generate_title(first_user_message: str) -> str:
    """Generate a clean, friendly 3-5 word title for the session."""
    client = get_client()
    try:
        prompt = (
            f"Generate a brief 3 to 4 word conversational title summarizing this student thought:\n"
            f"'{first_user_message}'\n"
            f"Only return the title text, no quotes, no extra punctuation."
        )
        res = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )
        title = res.text.strip().replace('"', '').replace("'", "")
        return title[:45] if title else "Thoughts & Well-being"
    except Exception as e:
        print(f"Error generating session title: {e}")
        return "Student Reflection"

def stream_chat_turn(session_id: str, user_message: str) -> Generator[str, None, None]:
    """Process a chat turn with real-time streaming output:
    1. Persist user message to SQLite.
    2. Auto-generate title if this is the first turn.
    3. Retrieve relevant student wellness / learning chunks from Knowledge Base.
    4. Stream the generated response tokens.
    5. Persist assistant reply to SQLite when complete.
    """
    client = get_client()
    
    # 1. Check message count to generate title if first turn
    existing_messages = get_session_messages(session_id)
    if len(existing_messages) == 0:
        new_title = auto_generate_title(user_message)
        update_session_title(session_id, new_title)
        
    # 2. Add user message locally
    add_message(session_id, "user", user_message)

    # 3. Retrieve relevant Knowledge Base context
    vector_store = get_vector_store()
    retrieved_chunks = vector_store.search(user_message, top_k=2, threshold=0.48)
    
    context_addon = ""
    if retrieved_chunks:
        snippets = []
        for ch in retrieved_chunks:
            snippets.append(f"[{ch['source']}]:\n{ch['text']}")
        context_addon = "\n\n=== RELEVANT STUDENT WELLNESS CONTEXT ===\n" + "\n\n".join(snippets) + "\n========================================="

    # 4. Assemble system instruction and history
    system_instruction = SYSTEM_PROMPT + context_addon
    
    history = get_session_messages(session_id, limit=12)
    contents = []
    
    for msg in history[:-1]:  # previous turns
        role = "user" if msg["role"] == "user" else "model"
        contents.append(types.Content(
            role=role,
            parts=[types.Part.from_text(text=msg["content"])]
        ))
        
    # Current turn
    contents.append(types.Content(
        role="user",
        parts=[types.Part.from_text(text=user_message)]
    ))

    # 5. Stream response
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.7,
        top_p=0.95,
    )
    
    full_response_text = ""
    try:
        stream = client.models.generate_content_stream(
            model=GEMINI_MODEL,
            contents=contents,
            config=config
        )
        for chunk in stream:
            if chunk.text:
                full_response_text += chunk.text
                yield chunk.text
    except Exception as e:
        err_msg = f"\n\n*MindPal note: A connection hiccup occurred ({str(e)[:100]}). Please take a gentle breath and try again.*"
        full_response_text += err_msg
        yield err_msg

    # 6. Save assistant response locally
    if full_response_text.strip():
        add_message(session_id, "assistant", full_response_text)
