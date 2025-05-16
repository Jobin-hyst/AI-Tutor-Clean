const API_BASE = "http://localhost:8000"; // Change if your backend runs elsewhere

export async function startSession() {
  const res = await fetch(`${API_BASE}/start`, { method: "POST" });
  return res.json();
}

export async function setLanguage(session_id, message) {
  const res = await fetch(`${API_BASE}/set-language`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id, message }),
  });
  return res.json();
}

export async function processPrompt(session_id, message) {
  const res = await fetch(`${API_BASE}/process-prompt`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id, message }),
  });
  return res.json();
} 