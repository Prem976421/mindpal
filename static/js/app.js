// MindPal - Client Application Logic with Student Wellness Action Tools

let currentSessionId = null;
let sessions = [];
let isGenerating = false;
let breathingInterval = null;
let countdownTimer = null;
let secondsRemaining = 300; // 5 minutes
let isTimerRunning = false;

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
const worryModal = document.getElementById("worryModal");
const openWorryModalBtn = document.getElementById("openWorryModalBtn");
const quickWorryBtn = document.getElementById("quickWorryBtn");
const closeWorryModal = document.getElementById("closeWorryModal");
const worryInput = document.getElementById("worryInput");
const runWorryTriageBtn = document.getElementById("runWorryTriageBtn");
const worryResult = document.getElementById("worryResult");

const reframeModal = document.getElementById("reframeModal");
const openReframeModalBtn = document.getElementById("openReframeModalBtn");
const closeReframeModal = document.getElementById("closeReframeModal");
const reframeInput = document.getElementById("reframeInput");
const runReframeBtn = document.getElementById("runReframeBtn");
const reframeResult = document.getElementById("reframeResult");

const kickstartModal = document.getElementById("kickstartModal");
const openKickstartModalBtn = document.getElementById("openKickstartModalBtn");
const closeKickstartModal = document.getElementById("closeKickstartModal");
const kickstartInput = document.getElementById("kickstartInput");
const runKickstartBtn = document.getElementById("runKickstartBtn");
const kickstartResult = document.getElementById("kickstartResult");
const kickstartTimerContainer = document.getElementById("kickstartTimerContainer");
const timerDisplay = document.getElementById("timerDisplay");
const toggleTimerBtn = document.getElementById("toggleTimerBtn");

const breathingModal = document.getElementById("breathingModal");
const openBreathingModalBtn = document.getElementById("openBreathingModalBtn");
const quickBreathingBtn = document.getElementById("quickBreathingBtn");
const closeBreathingModal = document.getElementById("closeBreathingModal");
const tabBreathingBtn = document.getElementById("tabBreathingBtn");
const tabGroundingBtn = document.getElementById("tabGroundingBtn");
const boxBreathingSection = document.getElementById("boxBreathingSection");
const groundingSection = document.getElementById("groundingSection");
const startBreathingBtn = document.getElementById("startBreathingBtn");
const breathingCircle = document.getElementById("breathingCircle");
const breathingInstruction = document.getElementById("breathingInstruction");
const breathingSubtext = document.getElementById("breathingSubtext");

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
      if (confirm("Delete this reflection?")) {
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
    chatHeaderTitle.textContent = "New Reflection";
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
    chatHeaderTitle.textContent = data.session.title || "Reflection";
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

  heroScreen.style.display = "none";
  messagesList.style.display = "flex";

  appendMessageToDOM("user", text);
  scrollToBottom();

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
      buffer = lines.pop();

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const payload = line.replace("data: ", "").trim();
          if (payload === "[DONE]") break;
          try {
            const parsed = JSON.parse(payload);
            if (parsed.token) {
              accumulatedReply += parsed.token;
              msgBody.innerHTML = marked.parse(accumulatedReply);
              scrollToBottom();
            }
          } catch (e) {}
        }
      }
    }
  } catch (err) {
    console.error("Streaming error:", err);
    accumulatedReply += "\n\n*(A brief connection hiccup occurred. Please take a breath and try again.)*";
    msgBody.innerHTML = marked.parse(accumulatedReply);
  } finally {
    msgBody.classList.remove("typing-cursor");
    isGenerating = false;
    sendBtn.disabled = chatInput.value.trim().length === 0;
    fetchSessions();
  }
}

// ----------------- TOOL 1: WORRY DUMP & TRIAGE -----------------
function openWorry() {
  worryModal.classList.add("active");
  worryInput.focus();
}

openWorryModalBtn.addEventListener("click", openWorry);
quickWorryBtn.addEventListener("click", openWorry);

closeWorryModal.addEventListener("click", () => {
  worryModal.classList.remove("active");
});

runWorryTriageBtn.addEventListener("click", async () => {
  const text = worryInput.value.trim();
  if (!text) return;

  runWorryTriageBtn.textContent = "De-tangling thoughts...";
  runWorryTriageBtn.disabled = true;

  try {
    const res = await fetch("/api/tools/worry-triage", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ worry_dump: text })
    });
    const data = await res.json();
    worryResult.innerHTML = marked.parse(data.result);
    worryResult.style.display = "block";
  } catch (err) {
    worryResult.innerHTML = `<span style="color: red;">Error: ${err.message}</span>`;
    worryResult.style.display = "block";
  } finally {
    runWorryTriageBtn.textContent = "De-Tangle My Thoughts";
    runWorryTriageBtn.disabled = false;
  }
});

// ----------------- TOOL 2: DE-CATASTROPHIZER -----------------
openReframeModalBtn.addEventListener("click", () => {
  reframeModal.classList.add("active");
  reframeInput.focus();
});

closeReframeModal.addEventListener("click", () => {
  reframeModal.classList.remove("active");
});

runReframeBtn.addEventListener("click", async () => {
  const text = reframeInput.value.trim();
  if (!text) return;

  runReframeBtn.textContent = "Analyzing cognitive pattern...";
  runReframeBtn.disabled = true;

  try {
    const res = await fetch("/api/tools/reframe", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ catastrophic_thought: text })
    });
    const data = await res.json();
    reframeResult.innerHTML = marked.parse(data.result);
    reframeResult.style.display = "block";
  } catch (err) {
    reframeResult.innerHTML = `<span style="color: red;">Error: ${err.message}</span>`;
    reframeResult.style.display = "block";
  } finally {
    runReframeBtn.textContent = "Reframe This Thought";
    runReframeBtn.disabled = false;
  }
});

// ----------------- TOOL 3: 5-MINUTE STUDY KICKSTART -----------------
openKickstartModalBtn.addEventListener("click", () => {
  kickstartModal.classList.add("active");
  kickstartInput.focus();
});

closeKickstartModal.addEventListener("click", () => {
  kickstartModal.classList.remove("active");
  stopKickstartTimer();
});

runKickstartBtn.addEventListener("click", async () => {
  const text = kickstartInput.value.trim();
  if (!text) return;

  runKickstartBtn.textContent = "Designing micro-step...";
  runKickstartBtn.disabled = true;

  try {
    const res = await fetch("/api/tools/micro-starter", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ intimidating_task: text })
    });
    const data = await res.json();
    kickstartResult.innerHTML = marked.parse(data.result);
    kickstartResult.style.display = "block";
    kickstartTimerContainer.style.display = "block";
  } catch (err) {
    kickstartResult.innerHTML = `<span style="color: red;">Error: ${err.message}</span>`;
    kickstartResult.style.display = "block";
  } finally {
    runKickstartBtn.textContent = "Generate Zero-Friction Micro-Step";
    runKickstartBtn.disabled = false;
  }
});

function formatTimer(sec) {
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  return `${m < 10 ? '0' : ''}${m}:${s < 10 ? '0' : ''}${s}`;
}

function stopKickstartTimer() {
  if (countdownTimer) {
    clearInterval(countdownTimer);
    countdownTimer = null;
  }
  isTimerRunning = false;
  secondsRemaining = 300;
  timerDisplay.textContent = "05:00";
  toggleTimerBtn.textContent = "Start 5-Minute Timer";
}

toggleTimerBtn.addEventListener("click", () => {
  if (!isTimerRunning) {
    isTimerRunning = true;
    toggleTimerBtn.textContent = "Pause Timer";
    countdownTimer = setInterval(() => {
      secondsRemaining--;
      timerDisplay.textContent = formatTimer(secondsRemaining);
      if (secondsRemaining <= 0) {
        stopKickstartTimer();
        alert("🎉 5 minutes complete! You broke the starting friction. Feel free to keep going or take a well-deserved breather!");
      }
    }, 1000);
  } else {
    clearInterval(countdownTimer);
    isTimerRunning = false;
    toggleTimerBtn.textContent = "Resume Timer";
  }
});

// ----------------- TOOL 4: SOMATIC PANIC RESET (BREATHING & 5-4-3-2-1) -----------------
function openBreathing() {
  breathingModal.classList.add("active");
}

openBreathingModalBtn.addEventListener("click", openBreathing);
quickBreathingBtn.addEventListener("click", openBreathing);

closeBreathingModal.addEventListener("click", () => {
  breathingModal.classList.remove("active");
  stopBreathingAnimation();
});

tabBreathingBtn.addEventListener("click", () => {
  boxBreathingSection.style.display = "block";
  groundingSection.style.display = "none";
});

tabGroundingBtn.addEventListener("click", () => {
  boxBreathingSection.style.display = "none";
  groundingSection.style.display = "block";
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
  let phase = 0;

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

// Close modals when clicking overlay background
window.addEventListener("click", (e) => {
  if (e.target === worryModal) worryModal.classList.remove("active");
  if (e.target === reframeModal) reframeModal.classList.remove("active");
  if (e.target === kickstartModal) {
    kickstartModal.classList.remove("active");
    stopKickstartTimer();
  }
  if (e.target === breathingModal) {
    breathingModal.classList.remove("active");
    stopBreathingAnimation();
  }
});

// Initialization
initTheme();
fetchSessions();
