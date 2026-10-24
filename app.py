import os
import streamlit as st
from datetime import datetime
from pathlib import Path

# Set page config FIRST before any other streamlit call
st.set_page_config(
    page_title="MindPal - Student Thought Companion",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

from src.config import KB_DIR, DATA_DIR
from src.db import (
    init_db,
    create_session,
    list_sessions,
    get_session,
    delete_session,
    get_session_messages,
    save_mood_entry,
    get_recent_mood_entries
)
from src.rag import get_vector_store
from src.llm import chat_turn

# Initialize database and vector store
init_db()
vector_store = get_vector_store()
if not vector_store.chunks:
    vector_store.sync_knowledge_base()

# Theme state management
if "app_theme" not in st.session_state:
    st.session_state.app_theme = "☀️ Light"

# Sidebar Theme Selector (Placed at top of sidebar)
with st.sidebar:
    st.markdown("### 🌱 MindPal")
    theme_choice = st.radio(
        "Theme Mode",
        ["☀️ Light", "🌙 Dark"],
        index=0 if "Light" in st.session_state.app_theme else 1,
        horizontal=True,
        label_visibility="collapsed"
    )
    st.session_state.app_theme = theme_choice

# Inject mode-specific CSS with 100% contrast guarantees
is_dark = "Dark" in st.session_state.app_theme

if is_dark:
    # DARK MODE CSS
    st.markdown("""
    <style>
        /* Base and background */
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: #0b0f19 !important;
            color: #f8fafc !important;
        }
        [data-testid="stSidebar"] {
            background-color: #111827 !important;
            border-right: 1px solid #1f2937 !important;
        }
        
        /* Text elements */
        .stApp p, .stApp span, .stApp label, .stApp div, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
            color: #f8fafc !important;
        }
        .stApp caption, .stCaption, small {
            color: #94a3b8 !important;
        }

        /* Hero container */
        .hero-container {
            padding: 1.2rem 1.6rem;
            background: linear-gradient(135deg, #1e1b4b 0%, #1e293b 100%) !important;
            border-radius: 14px;
            margin-bottom: 1.5rem;
            border: 1px solid #334155 !important;
        }
        .hero-title {
            color: #ffffff !important;
            font-size: 1.7rem;
            font-weight: 700;
            margin: 0;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .hero-subtitle {
            color: #cbd5e1 !important;
            font-size: 0.95rem;
            margin-top: 0.3rem;
            margin-bottom: 0;
        }

        /* Chat messages */
        [data-testid="stChatMessage"] {
            background-color: #111827 !important;
            border: 1px solid #1f2937 !important;
            border-radius: 12px !important;
            margin-bottom: 0.8rem !important;
            padding: 0.8rem 1rem !important;
        }
        [data-testid="stChatMessage"] p, [data-testid="stChatMessage"] div {
            color: #f8fafc !important;
        }

        /* Citation badge */
        .citation-tag {
            display: inline-block;
            background-color: #312e81 !important;
            color: #c7d2fe !important;
            font-size: 0.78rem;
            font-weight: 600;
            padding: 0.25rem 0.65rem;
            border-radius: 9999px;
            margin-right: 0.4rem;
            margin-top: 0.4rem;
            border: 1px solid #4338ca !important;
        }

        /* Form inputs, text inputs & text areas */
        .stTextInput input, .stTextArea textarea, [data-testid="stChatInput"] textarea, [data-testid="stSelectbox"] div {
            background-color: #1f2937 !important;
            color: #f8fafc !important;
            border: 1px solid #374151 !important;
        }

        /* Buttons */
        .stButton button {
            background-color: #1f2937 !important;
            color: #f8fafc !important;
            border: 1px solid #374151 !important;
            border-radius: 8px !important;
        }
        .stButton button:hover {
            background-color: #374151 !important;
            border-color: #6366f1 !important;
            color: #ffffff !important;
        }

        /* Tabs styling */
        button[data-baseweb="tab"] {
            color: #94a3b8 !important;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            color: #818cf8 !important;
            border-bottom-color: #818cf8 !important;
        }

        /* Expanders */
        [data-testid="stExpander"] {
            background-color: #111827 !important;
            border: 1px solid #1f2937 !important;
            border-radius: 8px !important;
        }
    </style>
    """, unsafe_allow_html=True)
else:
    # LIGHT MODE CSS
    st.markdown("""
    <style>
        /* Base and background */
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: #f8fafc !important;
            color: #0f172a !important;
        }
        [data-testid="stSidebar"] {
            background-color: #ffffff !important;
            border-right: 1px solid #e2e8f0 !important;
        }
        
        /* Text elements */
        .stApp p, .stApp span, .stApp label, .stApp div, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
            color: #0f172a !important;
        }
        .stApp caption, .stCaption, small {
            color: #475569 !important;
        }

        /* Hero container */
        .hero-container {
            padding: 1.2rem 1.6rem;
            background: linear-gradient(135deg, #e0f2fe 0%, #ede9fe 100%) !important;
            border-radius: 14px;
            margin-bottom: 1.5rem;
            border: 1px solid #cbd5e1 !important;
        }
        .hero-title {
            color: #0f172a !important;
            font-size: 1.7rem;
            font-weight: 700;
            margin: 0;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .hero-subtitle {
            color: #334155 !important;
            font-size: 0.95rem;
            margin-top: 0.3rem;
            margin-bottom: 0;
        }

        /* Chat messages */
        [data-testid="stChatMessage"] {
            background-color: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 12px !important;
            margin-bottom: 0.8rem !important;
            padding: 0.8rem 1rem !important;
        }
        [data-testid="stChatMessage"] p, [data-testid="stChatMessage"] div {
            color: #0f172a !important;
        }

        /* Citation badge */
        .citation-tag {
            display: inline-block;
            background-color: #e0e7ff !important;
            color: #3730a3 !important;
            font-size: 0.78rem;
            font-weight: 600;
            padding: 0.25rem 0.65rem;
            border-radius: 9999px;
            margin-right: 0.4rem;
            margin-top: 0.4rem;
            border: 1px solid #c7d2fe !important;
        }

        /* Form inputs, text inputs & text areas */
        .stTextInput input, .stTextArea textarea, [data-testid="stChatInput"] textarea, [data-testid="stSelectbox"] div {
            background-color: #ffffff !important;
            color: #0f172a !important;
            border: 1px solid #cbd5e1 !important;
        }

        /* Buttons */
        .stButton button {
            background-color: #ffffff !important;
            color: #0f172a !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 8px !important;
        }
        .stButton button:hover {
            background-color: #f1f5f9 !important;
            border-color: #6366f1 !important;
            color: #4338ca !important;
        }

        /* Tabs styling */
        button[data-baseweb="tab"] {
            color: #64748b !important;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            color: #4f46e5 !important;
            border-bottom-color: #4f46e5 !important;
        }

        /* Expanders */
        [data-testid="stExpander"] {
            background-color: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 8px !important;
        }
    </style>
    """, unsafe_allow_html=True)

# Session state initialization
if "current_session_id" not in st.session_state:
    sessions = list_sessions()
    if sessions:
        st.session_state.current_session_id = sessions[0]["id"]
    else:
        st.session_state.current_session_id = create_session("First Reflection")

if "starter_prompt" not in st.session_state:
    st.session_state.starter_prompt = ""

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.caption("Confidential student thought companion & study mentor.")

    # 1. New Chat Button
    if st.button("➕ New Conversation", use_container_width=True, type="primary"):
        new_id = create_session("New Reflection")
        st.session_state.current_session_id = new_id
        st.session_state.starter_prompt = ""
        st.rerun()

    st.markdown("---")
    
    # 2. Conversation History (Sessions)
    st.markdown("#### 💬 Past Conversations")
    sessions = list_sessions()
    if not sessions:
        st.caption("No past conversations yet.")
    else:
        for s in sessions:
            col_s1, col_s2 = st.columns([0.80, 0.20])
            is_active = (s["id"] == st.session_state.current_session_id)
            title = s["title"] if s["title"] else "Untitled Session"
            display_title = title if len(title) <= 22 else title[:19] + "..."
            
            with col_s1:
                if st.button(
                    f"{'📌 ' if is_active else '🗨️ '}{display_title}",
                    key=f"sess_{s['id']}",
                    use_container_width=True
                ):
                    st.session_state.current_session_id = s["id"]
                    st.session_state.starter_prompt = ""
                    st.rerun()
            with col_s2:
                if st.button("🗑️", key=f"del_{s['id']}", help="Delete conversation"):
                    delete_session(s["id"])
                    rem = list_sessions()
                    if rem:
                        st.session_state.current_session_id = rem[0]["id"]
                    else:
                        st.session_state.current_session_id = create_session("New Reflection")
                    st.rerun()

    st.markdown("---")

    # 3. Knowledge Base Manager & Uploader
    st.markdown("#### 📚 Knowledge Base (RAG)")
    kb_files = list(KB_DIR.glob("*.md")) + list(KB_DIR.glob("*.txt")) + list(KB_DIR.glob("*.pdf"))
    total_chunks = len(vector_store.chunks)
    
    st.caption(f"**{len(kb_files)}** documents • **{total_chunks}** semantic chunks")
    
    with st.expander("📥 Upload Study Notes / Guides"):
        uploaded_files = st.file_uploader(
            "Upload course notes or tips (.md, .txt, .pdf)",
            type=["md", "txt", "pdf"],
            accept_multiple_files=True
        )
        if uploaded_files:
            new_file_added = False
            for uploaded_file in uploaded_files:
                save_path = KB_DIR / uploaded_file.name
                if not save_path.exists():
                    with open(save_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    new_file_added = True
            
            if new_file_added:
                with st.spinner("Embedding and updating vector index..."):
                    sync_info = vector_store.sync_knowledge_base()
                    st.success(f"Indexed {sync_info['added_chunks']} new chunks from uploaded files!")
                    st.rerun()

    if st.button("🔄 Sync Knowledge Base", use_container_width=True):
        with st.spinner("Re-syncing vector database..."):
            sync_info = vector_store.sync_knowledge_base(force=True)
            st.success(f"Synced {sync_info['total_files']} files ({sync_info['total_chunks']} chunks).")
            st.rerun()

    st.markdown("---")

    # 4. Quick Mood Check-in Widget
    st.markdown("#### 🧠 Quick Mood Check-in")
    with st.form("quick_mood_form"):
        mood_selected = st.selectbox(
            "Headspace right now:",
            ["😊 Calm & Content", "🎯 Focused & Driven", "🤯 Stressed & Overwhelmed", "😴 Mentally Exhausted", "🌧️ Low & Discouraged"]
        )
        energy = st.slider("Energy Level (1=Low, 5=Peak)", 1, 5, 3)
        quick_thought = st.text_input("Quick note (optional)", placeholder="e.g. Studying for upcoming exam")
        submitted = st.form_submit_button("Log Check-in", use_container_width=True)
        if submitted:
            save_mood_entry(mood=mood_selected, energy_level=energy, note=quick_thought)
            st.success("Logged to your local thought journal!")

# ----------------- MAIN CONTENT AREA -----------------
tab_chat, tab_journal, tab_kb = st.tabs(["💬 Companion Chat", "📓 My Thought Journal", "📖 Browse Knowledge Base"])

# --- TAB 1: COMPANION CHAT ---
with tab_chat:
    # Hero Banner
    st.markdown("""
    <div class="hero-container">
        <h2 class="hero-title">🌱 MindPal</h2>
        <p class="hero-subtitle">
            A safe space to share your thoughts, untangle academic stress, and access evidence-based learning techniques. 
            All thoughts are stored <strong>privately on your device</strong>.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Current Session Info
    curr_session = get_session(st.session_state.current_session_id)
    session_title = curr_session["title"] if curr_session else "Chat Session"
    st.subheader(f"💬 {session_title}")

    # Fetch conversation history
    messages = get_session_messages(st.session_state.current_session_id)

    # Display starter prompts if session is fresh
    if len(messages) == 0:
        st.markdown("**Not sure where to begin? Try one of these:**")
        starters = [
            ("😫 Overwhelmed by deadlines", "I have so many assignments due soon and I feel paralyzed with anxiety. I don't know where to start."),
            ("🧠 Learn the Feynman Technique", "How does the Feynman Technique work, and how can I use it to master tough concepts?"),
            ("🛑 Break my procrastination cycle", "I keep putting off studying and getting distracted by my phone. How can I kickstart my focus?"),
            ("🌙 Pre-exam panic & sleep", "My test is tomorrow and my heart is pounding every time I look at my notes. Can you help me calm down?")
        ]
        cols = st.columns(2)
        for i, (label, prompt_text) in enumerate(starters):
            with cols[i % 2]:
                if st.button(label, key=f"starter_{i}", use_container_width=True):
                    st.session_state.starter_prompt = prompt_text
                    st.rerun()

    # Render message history
    for msg in messages:
        if msg["role"] == "user":
            with st.chat_message("user", avatar="🎓"):
                st.write(msg["content"])
        else:
            with st.chat_message("assistant", avatar="🌱"):
                st.markdown(msg["content"])
                # Show citations badge if available
                if msg.get("citations"):
                    citations = [c.strip() for c in msg["citations"].split(",") if c.strip()]
                    if citations:
                        cit_html = " ".join([f"<span class='citation-tag'>📖 {c}</span>" for c in citations])
                        st.markdown(cit_html, unsafe_allow_html=True)

    # Input handling
    user_input = st.chat_input("Share your thoughts or ask a study question...")
    
    # Check if a starter prompt was clicked
    if st.session_state.starter_prompt and not user_input:
        user_input = st.session_state.starter_prompt
        st.session_state.starter_prompt = ""

    if user_input:
        with st.chat_message("user", avatar="🎓"):
            st.write(user_input)

        with st.chat_message("assistant", avatar="🌱"):
            with st.spinner("MindPal is reflecting..."):
                response = chat_turn(
                    session_id=st.session_state.current_session_id,
                    user_message=user_input
                )
                st.markdown(response["reply"])
                
                # Show citations & retrieval details
                if response.get("citations"):
                    cit_html = " ".join([f"<span class='citation-tag'>📖 {c}</span>" for c in response["citations"]])
                    st.markdown(cit_html, unsafe_allow_html=True)
                    
                if response.get("retrieved_chunks"):
                    with st.expander("🔍 Inspected Knowledge Base Context"):
                        for ch in response["retrieved_chunks"]:
                            st.markdown(f"**From `{ch['source']}`** *(Relevance Score: {ch['score']})*")
                            st.caption(ch["text"])
                            st.markdown("---")
        st.rerun()

# --- TAB 2: MY THOUGHT JOURNAL & MOODS ---
with tab_journal:
    st.subheader("📓 My Local Thought Journal & Emotional Log")
    st.markdown("Track how your headspace shifts over time. This data is stored strictly in your local SQLite database.")
    
    mood_entries = get_recent_mood_entries(limit=20)
    if not mood_entries:
        st.info("No check-ins logged yet. Use the 'Quick Mood Check-in' widget on the sidebar to log your first one!")
    else:
        for entry in mood_entries:
            try:
                dt = datetime.fromisoformat(entry["timestamp"]).strftime("%b %d, %Y • %I:%M %p")
            except Exception:
                dt = entry["timestamp"]
            
            with st.container():
                st.markdown(f"**{entry['mood']}** &nbsp;&nbsp; *(Energy: {entry['energy_level']}/5)* &nbsp; • &nbsp; `{dt}`")
                if entry["note"]:
                    st.info(f"💭 {entry['note']}")
                st.markdown("---")

# --- TAB 3: BROWSE KNOWLEDGE BASE ---
with tab_kb:
    st.subheader("📖 Evidence-Based Knowledge Base")
    st.markdown("These guides ground MindPal's recommendations. You can also add your own course summaries via the sidebar uploader.")

    kb_files = sorted(list(KB_DIR.glob("*.md")) + list(KB_DIR.glob("*.txt")))
    if not kb_files:
        st.warning("No knowledge base documents found.")
    else:
        for kb_file in kb_files:
            with st.expander(f"📄 {kb_file.name}"):
                try:
                    with open(kb_file, "r", encoding="utf-8", errors="ignore") as f:
                        st.markdown(f.read())
                except Exception as e:
                    st.error(f"Error reading {kb_file.name}: {e}")
