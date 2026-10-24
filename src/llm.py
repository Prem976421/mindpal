import os
import json
from typing import List, Dict, Any, Generator, Tuple, Optional
from google import genai
from google.genai import types

from src.config import (
    GEMINI_API_KEY,
    GEMINI_CHAT_MODEL,
    SYSTEM_PROMPT,
    MAX_HISTORY_TURNS
)
from src.db import (
    add_message,
    get_session_messages,
    update_session_title,
    update_session_summary,
    get_session
)
from src.rag import get_vector_store

def get_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY", GEMINI_API_KEY)
    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing. Please set it in .env.")
    return genai.Client(api_key=api_key)

def classify_intent_and_needs(user_input: str) -> Dict[str, Any]:
    """Lightweight rule & semantic heuristic to classify whether query needs RAG and empathetic tone."""
    input_lower = user_input.lower()
    
    # Emotional/venting keywords
    venting_cues = ["feel", "feeling", "anxious", "scared", "sad", "overwhelmed", "hate myself", 
                    "hopeless", "crying", "tired", "stressed", "exhausted", "failure", "cant do this", "can't do this"]
    # Study/factual keywords
    study_cues = ["how to", "technique", "method", "schedule", "memorize", "exam", "revision", 
                  "pomodoro", "feynman", "spaced repetition", "notes", "focus", "procrastinating", "assignment"]
    
    is_venting = any(cue in input_lower for cue in venting_cues)
    is_study = any(cue in input_lower for cue in study_cues)
    
    if is_venting and is_study:
        intent = "MIXED"
    elif is_venting:
        intent = "VENTING_REFLECTION"
    elif is_study:
        intent = "STUDY_GUIDANCE"
    else:
        intent = "CONVERSATION"
        
    return {
        "intent": intent,
        "needs_rag": is_study or is_venting  # Both benefit from grounded wellness / study insights
    }

def generate_session_title(first_user_message: str) -> str:
    """Generate a clean, 3-5 word title for a new conversation session."""
    client = get_client()
    try:
        prompt = (
            f"Create a concise 3-5 word title summarizing this student message:\n"
            f"'{first_user_message}'\n"
            f"Title only, no quotes, no extra punctuation."
        )
        response = client.models.generate_content(
            model=GEMINI_CHAT_MODEL,
            contents=prompt
        )
        title = response.text.strip().replace('"', '').replace("'", "")
        return title[:50] if title else "Study Reflection"
    except Exception as e:
        print(f"Error generating title: {e}")
        return "Study & Thoughts"

def chat_turn(session_id: str, user_message: str) -> Dict[str, Any]:
    """Process a full conversation turn:
    1. Save user message locally in SQLite.
    2. Auto-generate title if it's the first message.
    3. Retrieve relevant context from local Knowledge Base (RAG).
    4. Assemble multi-turn dialogue with local context.
    5. Query Gemini.
    6. Save assistant response locally with citations & metadata.
    """
    client = get_client()
    vector_store = get_vector_store()
    
    # 1. Classify intent
    classification = classify_intent_and_needs(user_message)
    intent = classification["intent"]

    # 2. Check previous messages count in this session to decide on title generation
    existing_messages = get_session_messages(session_id)
    if len(existing_messages) == 0:
        title = generate_session_title(user_message)
        update_session_title(session_id, title)

    # 3. Save user message
    add_message(session_id=session_id, role="user", content=user_message, intent=intent)

    # 4. RAG Retrieval
    retrieved_chunks = vector_store.search(user_message, top_k=3, threshold=0.45)
    
    context_str = ""
    citations_used = []
    if retrieved_chunks:
        context_parts = []
        for i, chunk in enumerate(retrieved_chunks):
            source = chunk["source"]
            if source not in citations_used:
                citations_used.append(source)
            context_parts.append(f"[Source: {source} (Relevance: {chunk['score']})]:\n{chunk['text']}")
        context_str = "\n\n".join(context_parts)

    # 5. Build prompt history from local SQLite (rolling window)
    history = get_session_messages(session_id, limit=MAX_HISTORY_TURNS)
    
    # Format messages for Gemini contents
    contents = []
    
    # Provide system context + KB references in the system instruction
    system_instruction = SYSTEM_PROMPT
    if context_str:
        system_instruction += f"\n\n=== RELEVANT KNOWLEDGE BASE EXCERPTS ===\n{context_str}\n=========================================\n"
        system_instruction += "\nIf these excerpts are helpful to the student's question or emotional situation, draw upon them and mention the source naturally."

    for msg in history[:-1]:  # all prior turns
        role = "user" if msg["role"] == "user" else "model"
        contents.append(types.Content(
            role=role,
            parts=[types.Part.from_text(text=msg["content"])]
        ))

    # Append current turn
    contents.append(types.Content(
        role="user",
        parts=[types.Part.from_text(text=user_message)]
    ))

    # 6. Generate response
    try:
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.7,
            top_p=0.95,
        )
        response = client.models.generate_content(
            model=GEMINI_CHAT_MODEL,
            contents=contents,
            config=config
        )
        assistant_reply = response.text if response.text else "I'm listening. Could you tell me a little more about what's on your mind?"
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        assistant_reply = (
            "I'm here with you, but I had a brief moment connecting to the reasoning service. "
            f"Please take a deep breath, and let's try again in a moment. (Error: {str(e)[:100]})"
        )

    # 7. Save assistant message with citations locally in SQLite
    citations_str = ", ".join(citations_used) if citations_used else ""
    add_message(
        session_id=session_id,
        role="assistant",
        content=assistant_reply,
        intent=intent,
        citations=citations_str
    )

    return {
        "reply": assistant_reply,
        "intent": intent,
        "citations": citations_used,
        "retrieved_chunks": retrieved_chunks
    }
