// MindPal - Client Application Logic

let currentSessionId = null;
let sessions = [];
let isGenerating = false;
let breathingInterval = null;
let selectedMood = "Calm";

// DOM Elements
const sidebar = document.getElementById("sidebar");
const sidebarCollapseBtn = document.getElementById("sidebarCollapseBtn");
const sidebarExpandBtn = document.getElementById("sidebarExpandBtn");
const newChatBtn = document.getElementById("newChatBtn");
const sessionsList = document.getElementById("sessionsList");
const chatHeaderTitle = document.getElementById("chatHeaderTitle");
const messagesContainer = document.getElementById("messagesContainer");
const heroScreen = document.getElementById("heroScreen");
const messagesList = document.getElementById("messagesList");
const chatInput = document.getElementById("chatInput");
const sendBtn = document.getElementById("sendBtn");
const themeToggleBtn = document.getElementById("themeToggleBtn");
const themeIcon = document.getElementById("themeIcon");

// Modals
const breathingModal = document.getElementById("breathingModal");
const openBreathingModalBtn = document.getElementById("openBreathingModalBtn");
const closeBreathingModal = document.getElementById("closeBreathingModal");
const startBreathingBtn = document.getElementById("startBreathingBtn");
const breathingCircle = document.getElementById("breathingCircle");
const breathingInstruction = document.getElementById("breathingInstruction");
const breathingSubtext = document.getElementById("breathingSubtext");

const moodModal = document.getElementById("moodModal");
const openMoodModalBtn = document.getElementById("openMoodModalBtn");
const closeMoodModal = document.getElementById("closeMoodModal");
const moodChips = document.querySelectorAll(".mood-chip");
const moodEnergy = document.getElementById("moodEnergy");
const moodNote = document.getElementById("moodNote");
const saveMoodBtn = document.getElementById("saveMoodBtn");

// ----------------- THEME INITIALIZATION -----------------
function initTheme() {
  const savedTheme = localStorage.getItem("mindpal_theme") || "dark";
  document.documentElement.setAttribute("data-theme", savedTheme);
  themeIcon.textContent = savedTheme === "dark" ? "☀️" : "🌙";
}

themeToggleBtn.addEventListener("click", () => {
  const current = document.documentElement.getAttribute("data-theme");
  const next = current === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", next);
  localStorage.setItem("mindpal_theme", next);
  themeIcon.textContent = next === "dark" ? "☀️" : "🌙";
});

// ----------------- SIDEBAR TOGGLE -----------------
sidebarCollapseBtn.addEventListener("click", () => {
  sidebar.classList.add("collapsed");
});

sidebarExpandBtn.addEventListener("click", () => {
  sidebar.classList.remove("collapsed");
});

// ----------------- AUTO-EXPAND TEXTAREA & INPUT -----------------
chatInput.addEventListener("input", () => {
  chatInput.style.height = "auto";
  chatInput.style.height = Math.min(chatInput.scrollHeight, 140) + "px";
  sendBtn.disabled = chatInput.value.trim().length === 0 || isGenerating;
});

chatInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    if (!sendBtn.disabled) {
      sendMessage();
    }
  }
});

sendBtn.addEventListener("click", () => {
  if (!sendBtn.disabled) {
    sendMessage();
  }
});

// Starter prompt cards
document.querySelectorAll(".starter-card").forEach(card => {
  card.addEventListener("click", () => {
    const prompt = card.getAttribute("data-prompt");
    chatInput.value = prompt;
    chatInput.style.height = "auto";
    sendBtn.disabled = false;
    sendMessage();
  });
});

// ----------------- SESSIONS MANAGEMENT -----------------
async function fetchSessions() {
  try {
    const res = await fetch("/api/sessions");
    sessions = await res.json();
    renderSessionsList();
    if (sessions.length > 0 && !currentSessionId) {
      selectSession(sessions[0].id);
    } else if (sessions.length === 0) {
      createNewSession();
    }
  } catch (err) {
    console.error("Failed to load sessions:", err);
  }
}

function renderSessionsList() {
  sessionsList.innerHTML = "";
  sessions.forEach(sess => {
    const item = document.createElement("div");
    item.className = `session-item ${sess.id === currentSessionId ? "active" : ""}`;
    item.innerHTML = `
      <span class="session-title">${escapeHtml(sess.title || "Reflection")}</span>
      <button class="session-delete-btn" title="Delete conversation">&times;</button>
    `;

    item.addEventListener("click", (e) => {
      if (e.target.classList.contains("session-delete-btn")) return;
      selectSession(sess.id);
    });

    const delBtn = item.querySelector(".session-delete-btn");
    delBtn.addEventListener("click", async (e) => {
      e.stopPropagation();
      if (confirm("Delete this conversation?")) {
        await deleteSession(sess.id);
      }
    });

    sessionsList.appendChild(item);
  });
}

async function createNewSession() {
  try {
    const res = await fetch("/api/sessions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: "New Reflection" })
    });
    const data = await res.json();
    currentSessionId = data.id;
    chatHeaderTitle.textContent = "New Conversation";
    await fetchSessions();
    renderConversationView([]);
  } catch (err) {
    console.error("Error creating session:", err);
  }
}

newChatBtn.addEventListener("click", () => {
  createNewSession();
});

async function selectSession(sessionId) {
  currentSessionId = sessionId;
  renderSessionsList();
  try {
    const res = await fetch(`/api/sessions/${sessionId}/messages`);
    const data = await res.json();
    chatHeaderTitle.textContent = data.session.title || "Conversation";
    renderConversationView(data.messages || []);
  } catch (err) {
    console.error("Error loading session messages:", err);
  }
}

async function deleteSession(sessionId) {
  try {
    await fetch(`/api/sessions/${sessionId}`, { method: "DELETE" });
    if (currentSessionId === sessionId) {
      currentSessionId = null;
    }
    await fetchSessions();
  } catch (err) {
    console.error("Error deleting session:", err);
  }
}

// ----------------- MESSAGES RENDERING -----------------
function renderConversationView(messages) {
  if (!messages || messages.length === 0) {
    heroScreen.style.display = "flex";
    messagesList.style.display = "none";
    messagesList.innerHTML = "";
  } else {
    heroScreen.style.display = "none";
    messagesList.style.display = "flex";
    messagesList.innerHTML = "";
    messages.forEach(msg => {
      appendMessageToDOM(msg.role, msg.content);
    });
    scrollToBottom();
  }
}

function appendMessageToDOM(role, content) {
  const row = document.createElement("div");
  row.className = `message-row ${role}`;

  if (role === "assistant") {
    row.innerHTML = `
      <div class="msg-avatar">🌱</div>
      <div class="msg-body">${marked.parse(content || "")}</div>
    `;
  } else {
    row.innerHTML = `
      <div class="msg-body">${escapeHtml(content || "")}</div>
    `;
  }

  messagesList.appendChild(row);
  return row;
}

function scrollToBottom() {
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function escapeHtml(text) {
  const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
  return text.replace(/[&<>"']/g, m => map[m]);
}

// ----------------- STREAMING CHAT TURN -----------------
async function sendMessage() {
  const text = chatInput.value.trim();
  if (!text || isGenerating) return;

  isGenerating = true;
  chatInput.value = "";
  chatInput.style.height = "auto";
  sendBtn.disabled = true;

  // Make sure hero screen is hidden
  heroScreen.style.display = "none";
  messagesList.style.display = "flex";

  // Append user message
  appendMessageToDOM("user", text);
  scrollToBottom();

  // Create assistant placeholder with cursor
  const assistantRow = document.createElement("div");
  assistantRow.className = "message-row assistant";
  assistantRow.innerHTML = `
    <div class="msg-avatar">🌱</div>
    <div class="msg-body typing-cursor"></div>
  `;
  messagesList.appendChild(assistantRow);
  const msgBody = assistantRow.querySelector(".msg-body");
  scrollToBottom();

  let accumulatedReply = "";

  try {
    const response = await fetch("/api/chat/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: currentSessionId,
        message: text
      })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n\n");
      buffer = lines.pop(); // keep remainder

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const payload = line.replace("data: ", "").trim();
          if (payload === "[DONE]") {
            break;
          }
          try {
            const parsed = JSON.parse(payload);
            if (parsed.token) {
              accumulatedReply += parsed.token;
              msgBody.innerHTML = marked.parse(accumulatedReply);
              scrollToBottom();
            }
          } catch (e) {
            // non-json line
          }
        }
      }
    }
  } catch (err) {
    console.error("Streaming error:", err);
    accumulatedReply += "\n\n*(A brief connection error occurred. Please try again in a moment.)*";
    msgBody.innerHTML = marked.parse(accumulatedReply);
  } finally {
    msgBody.classList.remove("typing-cursor");
    isGenerating = false;
    sendBtn.disabled = chatInput.value.trim().length === 0;
    
    // Refresh sessions so auto-generated title reflects in sidebar
    fetchSessions();
  }
}

// ----------------- GUIDED BOX BREATHING MODAL -----------------
openBreathingModalBtn.addEventListener("click", () => {
  breathingModal.classList.add("active");
});

closeBreathingModal.addEventListener("click", () => {
  breathingModal.classList.remove("active");
  stopBreathingAnimation();
});

function stopBreathingAnimation() {
  if (breathingInterval) {
    clearInterval(breathingInterval);
    breathingInterval = null;
  }
  breathingCircle.className = "breathing-circle";
  breathingCircle.textContent = "Ready";
  breathingInstruction.textContent = "Take a breath...";
  breathingSubtext.textContent = "Click Start when you are ready.";
  startBreathingBtn.style.display = "block";
}

startBreathingBtn.addEventListener("click", () => {
  startBreathingBtn.style.display = "none";
  let phase = 0; // 0: inhale, 1: hold, 2: exhale, 3: hold

  function runPhase() {
    if (phase === 0) {
      breathingCircle.className = "breathing-circle expand";
      breathingCircle.textContent = "Inhale";
      breathingInstruction.textContent = "Inhale slowly...";
      breathingSubtext.textContent = "Breathe in through your nose (4s)";
    } else if (phase === 1) {
      breathingCircle.className = "breathing-circle expand";
      breathingCircle.textContent = "Hold";
      breathingInstruction.textContent = "Hold gently...";
      breathingSubtext.textContent = "Keep your lungs comfortably full (4s)";
    } else if (phase === 2) {
      breathingCircle.className = "breathing-circle shrink";
      breathingCircle.textContent = "Exhale";
      breathingInstruction.textContent = "Exhale smoothly...";
      breathingSubtext.textContent = "Release out through your mouth (4s)";
    } else if (phase === 3) {
      breathingCircle.className = "breathing-circle shrink";
      breathingCircle.textContent = "Hold";
      breathingInstruction.textContent = "Hold empty...";
      breathingSubtext.textContent = "Rest before the next cycle (4s)";
    }
    phase = (phase + 1) % 4;
  }

  runPhase();
  breathingInterval = setInterval(runPhase, 4000);
});

// ----------------- MOOD CHECK-IN MODAL -----------------
openMoodModalBtn.addEventListener("click", () => {
  moodModal.classList.add("active");
});

closeMoodModal.addEventListener("click", () => {
  moodModal.classList.remove("active");
});

moodChips.forEach(chip => {
  chip.addEventListener("click", () => {
    moodChips.forEach(c => c.classList.remove("selected"));
    chip.classList.add("selected");
    selectedMood = chip.getAttribute("data-mood");
  });
});

saveMoodBtn.addEventListener("click", async () => {
  const energy = parseInt(moodEnergy.value);
  const note = moodNote.value.trim();

  try {
    await fetch("/api/mood", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        mood: selectedMood,
        energy: energy,
        note: note
      })
    });
    moodModal.classList.remove("active");
    moodNote.value = "";
    
    // Add a gentle prompt suggestion into the conversation
    chatInput.value = `I just logged my mood as "${selectedMood}" with an energy level of ${energy}/5. ${note ? 'Note: ' + note : ''}`;
    chatInput.style.height = "auto";
    sendBtn.disabled = false;
  } catch (err) {
    console.error("Failed to save mood:", err);
  }
});

// Close modals when clicking overlay background
window.addEventListener("click", (e) => {
  if (e.target === breathingModal) {
    breathingModal.classList.remove("active");
    stopBreathingAnimation();
  }
  if (e.target === moodModal) {
    moodModal.classList.remove("active");
  }
});

// Initialization
initTheme();
fetchSessions();
