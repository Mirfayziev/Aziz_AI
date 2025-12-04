const API_BASE = "/api";
const CHAT_ID = "aziz_telegram";

async function sendMessage() {
  const input = document.getElementById("chat-text");
  const text = input.value.trim();
  if (!text) return;
  appendMessage("user", text);
  input.value = "";
  const res = await fetch(`${API_BASE}/chat/`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({chat_id: CHAT_ID, message: text})
  });
  const data = await res.json();
  appendMessage("ai", data.reply || JSON.stringify(data));
}

function appendMessage(role, text) {
  const log = document.getElementById("chat-log");
  const div = document.createElement("div");
  div.className = "message " + (role === "user" ? "user" : "ai");
  div.textContent = text;
  log.appendChild(div);
  log.scrollTop = log.scrollHeight;
}

async function loadPlan() {
  const res = await fetch(`${API_BASE}/planner/day`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({})
  });
  const data = await res.json();
  const el = document.getElementById("plan");
  el.innerHTML = "";
  (data.items || []).forEach(item => {
    const div = document.createElement("div");
    div.className = "plan-item";
    div.textContent = `${item.time} – ${item.title} (${item.note || ""})`;
    el.appendChild(div);
  });
}

async function loadSummary() {
  const res = await fetch(`${API_BASE}/summary/daily`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({chat_id: CHAT_ID})
  });
  const data = await res.json();
  const el = document.getElementById("summary");
  el.innerHTML = data.summary || JSON.stringify(data);
}
