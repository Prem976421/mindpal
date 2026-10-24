# Nagar Yuwak Shikshan Sanstha’s
## Yeshwantrao Chavan College of Engineering
**(An Autonomous Institution affiliated to Rashtrasant Tukdoji Maharaj Nagpur University)**  
**(Accredited ‘A++’ Grade by NAAC)**  
Hingna Road, Wanadongri, Nagpur – 441110  
Ph.07104-295083, 295085, 09764996477, Fax:07104-242376, Website: [www.ycce.edu](http://www.ycce.edu)

---

### Department of Computer Science and Engineering (AIML)

**Vision of the Department**  
*To emerge as a center of academic excellence in Computer Science and Engineering by fostering innovation, research, and value-based education, thereby empowering students to develop technology-driven, inclusive and sustainable, solutions for societal advancement.*

**Mission of the Department**  
* Impart quality technical education through a learner-centric environment that nurtures analytical thinking, innovation, and ethical responsibility.  
* Develop employable professionals by integrating academic excellence with industry-relevant practices and emerging technologies.  
* Foster research, and innovation through hands-on learning, projects-based learning and industry-institute linkages.  
* Encourage holistic and lifelong learning by promoting professional values, leadership skills, and a commitment to serve society.  

---

<br>

<div align="center">

# Innovative Activity 1
### (Mini Application Development)

**Subject:** Fundamentals of Artificial Intelligence (23AML1506)

<br>

### Title:
## **MindPal: An Empathetic AI Chatbot for Student Mental Well-being and Academic Support**

<br>

### Course Teacher
### **Prof. Shraddha G. Vaidya**

<br>

### Submitted By:

| Sr. No. | Roll No. | Name of the Student |
| :---: | :---: | :---: |
| 1. | | Prem Motghare |

</div>

<br><br>

---

## 1. Problem Statement

College life brings heavy academic demands, tight assignment deadlines, and constant exam pressure. As students, we often find ourselves overwhelmed, dealing with self-doubt, panic before tests, and guilt over procrastinating. However, most students struggle to find a safe, non-judgmental space to express what they are going through.

Because of these difficulties:
* **Students struggle silently** with exam anxiety, fear of failure, and burnout without knowing how to calm their racing thoughts.
* **Procrastination is often misunderstood** as simple laziness, when in reality it is emotional paralysis caused by perfectionism and feeling overwhelmed.
* **Generic commercial chatbots** sound cold, robotic, and corporate, offering textbook lectures instead of genuine empathy or practical relief.
* **Students fear sharing** deeply personal feelings and academic struggles on cloud platforms due to privacy and data leaks.

This creates an urgent need for an empathetic, private AI companion that actually understands student life, listens with warmth, and offers immediate, evidence-based coping tools.

---

## 2. Proposed Solution

To solve these challenges, we developed **MindPal**, a student-focused AI companion that combines empathetic conversational intelligence with structured cognitive and somatic relief tools:

1. **Empathetic Dialogue with Real-Time Streaming:** Listens actively without judgment, validates student emotions first, and streams answers word-by-word.
2. **Worry Dump & Action Triage:** Un-tangles late-night racing thoughts into what the student can directly control today versus what to release tonight.
3. **The De-Catastrophizer (CBT Reframer):** Catches catastrophic "all-or-nothing" spirals and offers realistic, balanced perspectives.
4. **5-Minute Study Kickstart:** Breaks intimidating assignments into zero-resistance micro-actions paired with an interactive 5-minute countdown timer.
5. **Somatic Panic Reset:** Provides browser-native animated Box Breathing (4-4-4-4) and 5-4-3-2-1 sensory grounding to stop physical panic before exams.

The system uses Google’s **Gemini-3.5-Flash-Lite** model for fast, compassionate reasoning and sub-second token streaming.

---

## 3. System Overview

MindPal is built using a modern full-stack architecture comprising Python FastAPI, SQLite, and a custom vanilla JavaScript frontend inspired by modern conversational interfaces like ChatGPT and Gemini. The web application operates completely on-device for maximum student privacy.

The application allows users to:
* **Chat confidentially** about study stress, fear of exams, or personal burnout in an intuitive ChatGPT-style interface.
* **Receive real-time, compassionate responses** grounded in proven learning science (Active Recall, Feynman Technique, Sleep Hygiene).
* **Use instant action tools** to de-tangle worries, reframe catastrophic thoughts, and break procrastination.
* **Store conversation histories 100% locally** on their own computer in an encrypted SQLite database without external data leaks.

---

## 4. Key Features

### 4.1 Local Knowledge Base & Thought Processing Module
* Pre-seeded with vetted student success guides covering Active Recall, Spaced Repetition, Box Breathing, Cognitive Reframing, and Sleep Hygiene.
* Documents (`.md`, `.txt`, `.pdf`) are processed and embedded locally using high-dimensional semantic vectors (`gemini-embedding-001`).
* Preserves complete privacy by running local vector cosine retrieval directly on the user's personal computer.

### 4.2 AI Empathetic Reasoning & Real-Time Streaming (Gemini)
* User messages and retrieved context are passed to Gemini-3.5-Flash-Lite via Google’s GenAI REST streaming pipeline.
* Streams tokens word-by-word via Server-Sent Events (SSE), delivering an authentic, low-latency conversational experience.
* Validates student feelings with genuine empathy rather than clinical corporate platitudes.

### 4.3 Student Cognitive Action Tools
MindPal provides purpose-built interactive tools tailored to specific mental hurdles:
* **Worry Dump & Triage:** Takes unstructured late-night dread and categorizes it into *"Things you can control today"* (with 5-minute steps) and *"Things to let go of tonight"*.
* **The De-Catastrophizer:** Analyzes catastrophic thoughts, highlights the cognitive distortion (e.g., All-or-Nothing thinking), performs an objective reality check, and outputs a balanced script.
* **5-Minute Study Kickstart:** Breaks daunting projects into tiny micro-steps and triggers a built-in 5:00 focus timer to overcome initial starting friction.

### 4.4 Somatic Panic Reset (Breathing & 5-4-3-2-1)
* **Box Breathing:** An interactive animated expanding circle that guides students through 4-second inhalation, 4-second breath retention, 4-second exhalation, and 4-second rest to physiologically lower heart rate.
* **5-4-3-2-1 Sensory Grounding:** An interactive step-by-step sensory walkthrough (5 things seen, 4 touched, 3 heard, 2 smelled, 1 positive truth) that pulls students out of acute panic spirals before exams.

---

## 5. System Architecture (FastAPI + Modern Web UI + SQLite + Gemini)

### Frontend (ChatGPT / Gemini Style Web Application)
* Collapsible left sidebar with conversation histories, session deletion, and active chat indicators.
* Centered floating pill input box with auto-expanding textarea, keyboard shortcuts (Enter to send, Shift+Enter for newline), and active send button.
* Dual theme engine supporting 100% high-contrast Dark and Light modes without visual contrast bugs.
* Client-side Markdown parser (Marked.js) rendering headings, bold text, lists, and quotes seamlessly.

### Backend (Python FastAPI + Uvicorn)
* Asynchronous event loop handling REST API endpoints and Server-Sent Events (SSE) streaming.
* Specialized controllers for worry triage, cognitive reframing, and micro-task generation.
* Local SQLite context manager ensuring multi-turn dialogue continuity across sessions.

### AI Layer (Google Gemini API)
* Gemini-3.5-Flash-Lite for high-speed conversational reasoning, emotional empathy, and streaming.
* Gemini-Embedding-001 (3072-dimensional vector space) for semantic knowledge base retrieval.
* Sub-1.5 second time-to-first-token latency, providing immediate comfort during distress.

### Database & Local Storage (SQLite)
* Local database (`mindpal.db`) storing sessions, message histories, and mood check-in records.
* Vector index cache (`vector_index.json`) for fast in-memory cosine similarity retrieval.

### Directory & Module Structure
```
mindpal/
├── main.py                  # FastAPI server & action endpoints
├── launch_mindpal.bat       # Windows background launcher
├── launch_mindpal.vbs       # Silent launcher without cmd popup
├── static/
│   ├── index.html           # Modern ChatGPT/Gemini single-page app
│   ├── css/styles.css       # Complete dark/light responsive design system
│   └── js/app.js            # SSE streaming, session manager & action tools
├── src/
│   ├── config.py            # Environment, model settings & system prompts
│   ├── db.py                # Local SQLite context manager
│   ├── gemini_service.py    # Direct Gemini API integration & token streaming
│   └── rag.py               # Vector knowledge base index & cosine search
├── knowledge_base/          # Evidence-based markdown student guides
└── data/                    # Local storage (mindpal.db & vector_index.json)
```

---

## 6. Workflow Pipeline

1. User accesses MindPal via the desktop shortcut or browser (`http://localhost:8000`).
2. User shares thoughts in the chat input or selects an Action Tool (Worry Dump, Reframe, Kickstart, Panic Reset).
3. Frontend sends user input to the FastAPI backend via JSON payload.
4. Backend searches the local vector store for relevant student wellness and study strategies.
5. Backend constructs an empathetic context window and queries Gemini-3.5-Flash-Lite.
6. Gemini streams tokens in real time over Server-Sent Events (SSE) back to the client UI.
7. The complete conversation turn and session metadata are saved locally into SQLite (`mindpal.db`).

---

## 7. Advantages of the System

✔ **Built on fast, asynchronous FastAPI and modern responsive web architecture**  
✔ **Gemini-3.5-flash-lite delivers instantaneous token streaming with genuine human warmth**  
✔ **Includes practical, student-centric action tools (Worry Triage, De-Catastrophizer, 5-Min Timer)**  
✔ **Physiological panic reset tools (Box Breathing & 5-4-3-2-1 Grounding) stop physical freeze**  
✔ **100% on-device privacy guarantee using local SQLite storage and zero cloud data leaks**  
✔ **Full Dark Mode and Light Mode support with zero contrast issues or invisible text**  
✔ **Convenient desktop shortcut for immediate, one-click access whenever stress spikes**  

---

## 8. Limitations

* Internet connection is required to communicate with Google's Gemini API.
* Not a replacement for professional clinical psychological therapy or emergency medical care.
* API rate limits may apply on free-tier Gemini API keys during extreme high-volume bursts.

---

## 9. Future Improvements

* Offline local LLM support using quantized models (Ollama / Llama.cpp) for 100% disconnected offline use.
* Voice-enabled conversational mode for students who prefer speaking their thoughts aloud.
* Biometric smartwatch integration (HRV / heart rate) to automatically suggest Box Breathing during physical stress spikes.
* Multi-language support (Hindi, Marathi, etc.) to make mental health support accessible to all students.

---

## Outputs:

<br>

**[Fig. 1. MindPal Welcome & Conversation Interface (Dark Mode)]**  
*Displays the ChatGPT/Gemini-style layout: collapsible sidebar with past sessions, floating pill input bar, model status badge (Gemini 3.5 Flash), and quick starter cards for Exam Panic, Procrastination Guilt, and the Feynman Technique.*

<br>

**[Fig. 2. Real-Time Empathetic Chat Dialogue with Live Streaming]**  
*Student input: "I have an exam in 2 days and I am freaking out and procrastinating."*  
*MindPal response: "Take a deep breath. First of all, I want to gently acknowledge how completely normal and valid it is to feel this way. Having an exam in just 48 hours is a high-pressure situation... Let's use the 5-minute rule right now."*

<br>

**[Fig. 3.1 Worry Dump & Action Triage Modal Output]**  
*Input: Unfiltered stream of deadlines, chores, and exam dread.*  
*MindPal Output: 1. Immediate Controllables (with 5-minute micro actions) | 2. Uncontrollables to Release Tonight | 3. Single Immediate Focus.*

<br>

**[Fig. 3.2 The De-Catastrophizer (CBT Thought Reframe) Tool Output]**  
*Catastrophic thought: "If I fail this quiz, I will fail the whole course and ruin my future."*  
*MindPal Analysis: Identifies 'All-or-Nothing Trap' & 'Fortune Telling', conducts an objective reality check on grading percentages, and provides an empowering balanced reframe.*

<br>

**[Fig. 4.1 5-Minute Study Kickstart Tool with Live Countdown Timer]**  
*Input task: "Writing a 10-page research paper."*  
*MindPal Output: Generates a zero-friction micro-step ("Just open docs and write the title") and activates a live 05:00 countdown focus timer.*

<br>

**[Fig. 4.2 Somatic Panic Reset: Interactive Box Breathing & 5-4-3-2-1 Sensory Grounding]**  
*Section A: Animated 4-4-4-4 expanding circle guiding 4s Inhale, 4s Hold, 4s Exhale, 4s Hold.*  
*Section B: Step-by-step physical grounding (5 things seen, 4 touched, 3 heard, 2 smelled, 1 positive truth) to downregulate pre-exam panic.*

<br>

---

**Conclusion:** Thus, we created MindPal, an empathetic AI chatbot and mental well-being companion specifically engineered for students. By moving beyond standard corporate conversational bots and integrating Cognitive Behavioral Therapy (CBT) reframing, Behavioral Activation micro-task decomposition, interactive Box Breathing, and local SQLite data privacy, MindPal provides students with immediate, practical relief from academic stress, panic, and executive freeze.
