# app.py
from flask import Flask, request, jsonify, render_template_string
from banking_bot.core import build_orchestrator
from banking_bot.models import ChatMessage

app = Flask(__name__)
orchestrator = build_orchestrator()

CHAT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>UNH Banking Assistant</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    :root {
      --bg: #020617;
      --bot: #111827;
      --user: #2563eb;
      --text: #e5e7eb;
      --muted: #9ca3af;
      --accent: #38bdf8;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: radial-gradient(circle at top, #0f172a 0%, #020617 50%, #000 100%);
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--text);
      height: 100vh;
      display: flex;
      justify-content: center;
    }
    .shell {
      width: min(1100px, 100%);
      display: flex;
      flex-direction: column;
    }
    header {
      padding: 1rem 1.5rem;
      border-bottom: 1px solid rgba(148, 163, 184, 0.3);
      display: flex;
      justify-content: space-between;
      align-items: center;
      backdrop-filter: blur(6px);
    }
    header h1 {
      margin: 0;
      font-size: 1.05rem;
    }
    .sub {
      font-size: 0.8rem;
      color: var(--muted);
      margin-top: 0.2rem;
    }
    .pill {
      background: rgba(34, 197, 94, 0.15);
      color: #22c55e;
      padding: 0.2rem 0.6rem;
      border-radius: 999px;
      font-size: 0.7rem;
    }
    .chat {
      flex: 1;
      overflow-y: auto;
      padding: 1rem 1.5rem 7rem;
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }
    .msg {
      display: flex;
      gap: 0.6rem;
      align-items: flex-start;
    }
    .msg.user {
      flex-direction: row-reverse;
    }
    .avatar {
      width: 32px;
      height: 32px;
      border-radius: 999px;
      background: rgba(148, 163, 184, 0.18);
      display: grid;
      place-items: center;
      font-size: 0.75rem;
      flex-shrink: 0;
    }
    .bubble {
      background: rgba(15, 23, 42, 0.9);
      border-radius: 1.1rem;
      padding: 0.65rem 0.85rem;
      max-width: 75%;
      border: 1px solid rgba(148, 163, 184, 0.25);
      font-size: 0.9rem;
      line-height: 1.4;
      white-space: pre-wrap;
    }
    .msg.user .bubble {
      background: #2563eb;
      border-color: rgba(37, 99, 235, 0.8);
      text-align: right;
    }
    .input-bar {
      position: fixed;
      bottom: 0;
      left: 50%;
      transform: translateX(-50%);
      width: min(1100px, 100%);
      padding: 0.9rem 1.5rem 1.25rem;
      display: flex;
      gap: 0.6rem;
      background: linear-gradient(180deg, rgba(2, 6, 23, 0) 0%, rgba(2, 6, 23, 0.9) 40%, rgba(2, 6, 23, 1) 100%);
    }
    .input-bar input {
      flex: 1;
      border-radius: 999px;
      border: 1px solid rgba(148, 163, 184, 0.4);
      padding: 0.7rem 1rem;
      background: rgba(15, 23, 42, 0.8);
      color: var(--text);
      outline: none;
    }
    .input-bar button {
      border-radius: 999px;
      border: none;
      padding: 0.7rem 1rem;
      background: var(--accent);
      color: #0b1120;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.3rem;
    }
    .thinking {
      font-size: 0.75rem;
      color: var(--muted);
    }
    @media (max-width: 700px) {
      .chat { padding: 0.8rem 0.8rem 6.5rem; }
      .input-bar { padding-inline: 0.8rem; }
      .bubble { max-width: 100%; }
    }
  </style>
</head>
<body>
  <div class="shell">
    <header>
      <div>
        <h1>UNH Banking Assistant</h1>
        <div class="sub">Ask about cards, branch timings, KYC, loans. Risky or account-specific requests will be safely refused.</div>
      </div>
      <div class="pill">online</div>
    </header>
    <div id="chat" class="chat">
      <div class="msg">
        <div class="avatar">B</div>
        <div class="bubble">Hello 👋 I’m your banking assistant. You can ask about blocking cards, branch timings, KYC requirements, or general loan information.</div>
      </div>
    </div>
    <div class="input-bar">
      <input id="msg" placeholder="Type your banking question..." onkeydown="if(event.key==='Enter'){sendMsg();}">
      <button onclick="sendMsg()">
        <span>Send</span> ➤
      </button>
    </div>
  </div>
  <script>
    const chat = document.getElementById('chat');
    let history = [];

    function appendMessage(text, sender="bot") {
      const m = document.createElement('div');
      m.className = 'msg' + (sender === 'user' ? ' user' : '');
      const avatar = document.createElement('div');
      avatar.className = 'avatar';
      avatar.textContent = sender === 'user' ? 'U' : 'B';
      const bubble = document.createElement('div');
      bubble.className = 'bubble';
      bubble.textContent = text;
      m.appendChild(avatar);
      m.appendChild(bubble);
      chat.appendChild(m);
      chat.scrollTop = chat.scrollHeight;
      return m;
    }

    let thinkingNode = null;
    function showThinking() {
      thinkingNode = appendMessage("Thinking…", "bot");
      const span = document.createElement('span');
      span.className = 'thinking';
      span.textContent = "Thinking…";
      thinkingNode.querySelector('.bubble').textContent = "";
      thinkingNode.querySelector('.bubble').appendChild(span);
    }

    function hideThinking() {
      if (thinkingNode) {
        thinkingNode.remove();
        thinkingNode = null;
      }
    }

    async function sendMsg() {
      const input = document.getElementById('msg');
      const text = input.value.trim();
      if (!text) return;
      appendMessage(text, "user");
      history.push({role: "user", content: text});
      input.value = "";

      showThinking();

      try {
        const res = await fetch('/api/chat', {
          method: 'POST',
          headers: {'Content-Type':'application/json'},
          body: JSON.stringify({message: text, history: history})
        });
        const j = await res.json();
        hideThinking();
        let respText = j.response || "No response.";
        if (j.intent === "risky" || j.intent === "sensitive") {
          respText = "⚠️ " + respText;
        }
        appendMessage(respText, "bot");
        history.push({role: "assistant", content: respText});
      } catch (e) {
        hideThinking();
        appendMessage("⚠️ Error contacting the assistant.", "bot");
      }
    }
  </script>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(CHAT_TEMPLATE)


@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json(force=True)
    user_msg = data.get("message", "").strip()
    raw_history = data.get("history", []) or []
    history = [ChatMessage(role=h.get("role", "user"), content=h.get("content", "")) for h in raw_history]

    if not user_msg:
        return jsonify({"error": "message is required"}), 400

    result = orchestrator.handle_message(user_msg, history)
    return jsonify(result)


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8501))
    app.run(host="0.0.0.0", port=port, debug=True)
