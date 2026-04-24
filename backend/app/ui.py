"""Embedded single-page chat UI served at /ui."""
from __future__ import annotations

# The entire frontend is a single self-contained HTML page with vanilla JS.
# No build step, no extra dependencies — just open /ui in any browser.
_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>AI-AGENT Chat</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: system-ui, -apple-system, sans-serif;
      background: #0f172a;
      color: #e2e8f0;
      height: 100dvh;
      display: flex;
      flex-direction: column;
    }
    header {
      background: #1e293b;
      padding: 12px 16px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid #334155;
    }
    header h1 { font-size: 1.1rem; font-weight: 700; letter-spacing: .02em; }
    header .badge {
      font-size: .7rem;
      background: #6366f1;
      color: #fff;
      border-radius: 99px;
      padding: 2px 8px;
    }
    #settings-row {
      background: #1e293b;
      padding: 8px 16px;
      display: flex;
      gap: 8px;
      align-items: center;
      border-bottom: 1px solid #334155;
      flex-wrap: wrap;
    }
    #settings-row label { font-size: .8rem; color: #94a3b8; white-space: nowrap; }
    #settings-row input, #settings-row select {
      flex: 1;
      min-width: 140px;
      background: #0f172a;
      border: 1px solid #475569;
      border-radius: 6px;
      color: #e2e8f0;
      padding: 5px 8px;
      font-size: .85rem;
    }
    #chat-window {
      flex: 1;
      overflow-y: auto;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .msg {
      max-width: 80%;
      padding: 10px 14px;
      border-radius: 12px;
      font-size: .9rem;
      line-height: 1.5;
      white-space: pre-wrap;
      word-break: break-word;
    }
    .msg.user   { background: #6366f1; color: #fff; align-self: flex-end; border-bottom-right-radius: 4px; }
    .msg.assistant { background: #1e293b; border: 1px solid #334155; align-self: flex-start; border-bottom-left-radius: 4px; }
    .msg.system { background: #0f172a; border: 1px dashed #475569; align-self: center; font-size: .78rem; color: #64748b; }
    #input-row {
      padding: 12px 16px;
      background: #1e293b;
      border-top: 1px solid #334155;
      display: flex;
      gap: 8px;
      align-items: flex-end;
    }
    #user-input {
      flex: 1;
      background: #0f172a;
      border: 1px solid #475569;
      border-radius: 8px;
      color: #e2e8f0;
      padding: 10px 12px;
      font-size: .9rem;
      resize: none;
      min-height: 44px;
      max-height: 160px;
      line-height: 1.4;
    }
    #user-input:focus { outline: 2px solid #6366f1; border-color: transparent; }
    #send-btn {
      background: #6366f1;
      color: #fff;
      border: none;
      border-radius: 8px;
      padding: 10px 18px;
      font-size: .9rem;
      font-weight: 600;
      cursor: pointer;
      transition: background .15s;
      white-space: nowrap;
    }
    #send-btn:hover:not(:disabled) { background: #4f46e5; }
    #send-btn:disabled { background: #334155; cursor: not-allowed; }
    #new-chat-btn {
      background: transparent;
      border: 1px solid #475569;
      color: #94a3b8;
      border-radius: 8px;
      padding: 10px 14px;
      font-size: .85rem;
      cursor: pointer;
    }
    #new-chat-btn:hover { border-color: #6366f1; color: #6366f1; }
    .thinking { font-style: italic; color: #64748b; }
  </style>
</head>
<body>
  <header>
    <h1>🤖 AI-AGENT Chat</h1>
    <span class="badge" id="model-label">no model</span>
  </header>

  <div id="settings-row">
    <label for="base-url">Backend URL</label>
    <input id="base-url" type="url" placeholder="http://localhost:8000" />
    <label for="intent-sel">Intent</label>
    <select id="intent-sel">
      <option value="chat">chat</option>
      <option value="explain">explain</option>
      <option value="generate">generate</option>
      <option value="refactor">refactor</option>
      <option value="fix">fix</option>
    </select>
    <button id="new-chat-btn" title="Start a new conversation">＋ New chat</button>
  </div>

  <div id="chat-window">
    <div class="msg system">👋 Type a message below to start chatting. Make sure the Backend URL above points to your running AI-AGENT server.</div>
  </div>

  <div id="input-row">
    <textarea id="user-input" rows="1" placeholder="Ask anything…"></textarea>
    <button id="send-btn">Send</button>
  </div>

  <script>
    const chatWindow = document.getElementById('chat-window');
    const userInput  = document.getElementById('user-input');
    const sendBtn    = document.getElementById('send-btn');
    const baseUrlEl  = document.getElementById('base-url');
    const intentEl   = document.getElementById('intent-sel');
    const modelLabel = document.getElementById('model-label');
    const newChatBtn = document.getElementById('new-chat-btn');

    // Default to same origin so it works out-of-the-box when served by FastAPI.
    baseUrlEl.value = localStorage.getItem('ai-agent-url') || window.location.origin;

    let sessionId = null;

    baseUrlEl.addEventListener('change', () => {
      localStorage.setItem('ai-agent-url', baseUrlEl.value.trim());
    });

    function baseUrl() {
      return baseUrlEl.value.trim().replace(/\/$/, '');
    }

    function addMessage(role, text) {
      const div = document.createElement('div');
      div.className = 'msg ' + role;
      div.textContent = text;
      chatWindow.appendChild(div);
      chatWindow.scrollTop = chatWindow.scrollHeight;
      return div;
    }

    function setSending(on) {
      sendBtn.disabled = on;
      sendBtn.textContent = on ? '…' : 'Send';
      userInput.disabled = on;
    }

    async function sendMessage() {
      const text = userInput.value.trim();
      if (!text) return;
      userInput.value = '';
      userInput.style.height = 'auto';
      addMessage('user', text);
      setSending(true);

      const thinkingEl = addMessage('assistant', '');
      thinkingEl.classList.add('thinking');
      thinkingEl.textContent = 'Thinking…';

      try {
        const body = {
          messages: [{ role: 'user', content: text }],
          intent: intentEl.value,
        };
        if (sessionId) body.session_id = sessionId;

        const res = await fetch(baseUrl() + '/v1/chat/completions', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        });

        if (!res.ok) {
          const err = await res.text();
          throw new Error(res.status + ': ' + err);
        }

        const data = await res.json();
        sessionId = data.session_id;
        thinkingEl.classList.remove('thinking');
        thinkingEl.textContent = data.content;
        modelLabel.textContent = data.model || 'unknown';
      } catch (e) {
        thinkingEl.classList.remove('thinking');
        thinkingEl.classList.add('system');
        thinkingEl.textContent = '⚠️ Error: ' + e.message;
      } finally {
        setSending(false);
        userInput.focus();
      }
    }

    sendBtn.addEventListener('click', sendMessage);

    userInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });

    // Auto-grow textarea
    userInput.addEventListener('input', () => {
      userInput.style.height = 'auto';
      userInput.style.height = Math.min(userInput.scrollHeight, 160) + 'px';
    });

    newChatBtn.addEventListener('click', () => {
      sessionId = null;
      chatWindow.innerHTML = '<div class="msg system">🆕 New conversation started.</div>';
      modelLabel.textContent = 'no model';
    });
  </script>
</body>
</html>
"""


def get_chat_ui_html() -> str:
    return _HTML
