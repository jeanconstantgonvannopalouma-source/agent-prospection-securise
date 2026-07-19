(function () {
  const BASE_URL = "";
  const messagesEl = document.getElementById("messages");
  const msgInput = document.getElementById("msgInput");
  const sendBtn = document.getElementById("sendBtn");
  const tokenInput = document.getElementById("tokenInput");
  const saveTokenBtn = document.getElementById("saveTokenBtn");

  const TOKEN_KEY = "AGENT_TOKEN";

  function addMessage(role, text, cls = "") {
    const div = document.createElement("div");
    div.className = `msg ${role} ${cls}`.trim();
    div.innerHTML = `
      <div class="role">${role.toUpperCase()}</div>
      <div class="bubble"></div>
    `;
    div.querySelector(".bubble").textContent = text;
    messagesEl.appendChild(div);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function getToken() {
    return localStorage.getItem(TOKEN_KEY) || "";
  }

  function setToken(t) {
    localStorage.setItem(TOKEN_KEY, t);
  }

  async function callChat(message) {
    const token = getToken();
    const headers = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const res = await fetch(`${BASE_URL}/api/chat`, {
      method: "POST",
      headers,
      body: JSON.stringify({ message })
    });

    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
    return data;
  }

  async function onSend() {
    const message = (msgInput.value || "").trim();
    if (!message) return;
    msgInput.value = "";
    addMessage("user", message);

    try {
      const data = await callChat(message);
      addMessage("agent", data.reply || "(pas de réponse)");
    } catch (e) {
      addMessage("error", String(e.message || e), "error");
    }
  }

  saveTokenBtn.addEventListener("click", () => {
    const t = (tokenInput.value || "").trim();
    setToken(t);
    addMessage("agent", t ? "Token sauvegardé. Tu peux envoyer des commandes." : "Token effacé.");
    tokenInput.value = "";
  });

  sendBtn.addEventListener("click", onSend);
  msgInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") onSend();
  });

  // Auto message
  addMessage("agent", "Bienvenue. Colle ton INTERNAL_API_TOKEN puis essaye: /help");
})();
