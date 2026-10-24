# 🌱 MindPal - Student Mental Well-being & Thought Companion

MindPal is a modern, empathetic AI companion designed specifically for student mental wellness and academic growth. Built with a sleek, responsive interface inspired by **ChatGPT & Gemini**, it provides students with a confidential space to voice thoughts, navigate academic stress, and access evidence-based learning strategies.

---

## ✨ Features

- **Modern ChatGPT & Gemini-Inspired Interface**:
  - **Collapsible Sidebar**: Organized conversation history, active chat indicator, and "+ New reflection" button.
  - **Fluid Real-Time Token Streaming**: Text streams token-by-token using Server-Sent Events (SSE).
  - **Floating Pill Input Box**: Centered input with auto-expanding textarea, Shift+Enter multiline support, and responsive send button.
  - **Seamless Dark & Light Themes**: Zero contrast bugs, complete visual fidelity in both modes.
  - **Quick Prompt Starters**: Instant suggestions for exam anxiety, breaking procrastination guilt, Feynman technique, and burnout.

- **Student Mental Well-being Focus**:
  - **Empathetic AI Persona**: Validates feelings first, listens actively, and uses gentle cognitive reframing (CBT).
  - **Integrated 60-Second Guided Box Breathing Tool**: Animated 4-4-4-4 breathing circle to physically downregulate acute panic.
  - **Mental State & Headspace Logger**: Track emotional states (Calm, Focused, Stressed, Exhausted, Low) and energy levels stored locally.
  - **Evidence-Based Knowledge Grounding**: Draws upon study and wellness guides (Active Recall, Spaced Repetition, sleep hygiene, worry journal).
  - **Crisis Safety Net**: Compassionate crisis line information if severe distress is detected.

- **Privacy & Local Context**:
  - All chat sessions, messages, and mood logs are persisted locally on your device in **SQLite** (`data/mindpal.db`).
  - Powered directly by the **Google Gemini API** (`gemini-3.5-flash-lite`).

---

## 🚀 Quick Start

### 1. Requirements
- Python 3.10+
- Google Gemini API key (already configured in `.env`)

### 2. Run the Application
Open your terminal in this project folder and run:
```bash
python main.py
```
*(Or double-click `run.bat` on Windows)*

Open your browser and navigate to:
👉 **[http://localhost:8000](http://localhost:8000)**

---

## 📁 Project Architecture

```
mindpal/
├── main.py                     # FastAPI application serving endpoints & UI
├── run.bat                     # Windows one-click launcher
├── .env                        # Gemini API configuration
├── static/
│   ├── index.html              # ChatGPT / Gemini style modern SPA
│   ├── css/
│   │   └── styles.css          # Full design system (Dark & Light themes)
│   └── js/
│       └── app.js              # State, SSE streaming, sessions, breathing tool
├── src/
│   ├── config.py               # Settings, system persona, paths
│   ├── db.py                   # Local SQLite storage (sessions, messages, moods)
│   ├── gemini_service.py       # Direct Gemini API integration & token streaming
│   └── rag.py                  # Knowledge base vector index & grounding
├── knowledge_base/             # Evidence-based student guides
└── data/
    └── mindpal.db              # Local SQLite database
```
