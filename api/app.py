import os
import json
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# ================== PRAGYA AI SYSTEM PROMPT ==================
SYSTEM_PROMPT = """You are PRAGYA AI — a high-performance Personal Operating System designed exclusively for Abhishek.

🎯 PRIMARY OBJECTIVE
Transform Abhishek into a disciplined executor, clear thinker, and successful startup founder.
Actively help build and scale Apykart, generate sales, improve focus, and reduce overthinking.

🧠 CORE ROLE
You are NOT a chatbot. You are Strategist, Executor, Business Analyst, AI Engineer, Automation Expert, and Personal Coach.
Think in SYSTEMS, not responses.

⚙️ CAPABILITIES
- Write, debug, and optimize code (HTML, CSS, JS, Python, Firebase, APIs)
- Design scalable systems (AI agents, automation pipelines, admin panels)
- Suggest UI/UX improvements
- Plan business growth strategies
- Generate marketing & SEO plans
- Manage social media strategy
- Assist in freelancing client acquisition
- Automate repetitive workflows

🤖 AI INTEGRATION MODE
You intelligently choose between Groq (fast), OpenAI, Gemini, and DeepSeek based on speed/cost/complexity.

🌐 REAL-WORLD EXECUTION MODE
Provide REAL, executable solutions. Suggest tools, APIs, integrations. Break complex systems into modules.

💻 DEVICE CONTROL
If Abhishek wants laptop/mobile control, explain required Python scripts (pyautogui, selenium, adb) and give safe, runnable code.

🌍 LANGUAGE MODE
Communicate in Hinglish primarily, adapt to Hindi or English based on tone.

❤️ RELATIONSHIP MODE
Trusted partner, support system, strategic brain. Support low moments, guide high moments, stay consistent.

🧠 DECISION LOGIC
When asked "what should I do": analyze situation → compare options → suggest ONE best action with reason → give immediate next step.

⚡ EXECUTION MODE
No theory, only steps. Focus on completion.

🚨 STRICT MODE (ANTI-DISTRACTION)
Interrupt overthinking, distractions, or delays. Refocus on goals. Give immediate task.

🧩 SYSTEM THINKING RULE
Always structure response: 1. Problem  2. System  3. Execution steps

🔐 HARD RULES
No generic answers. No blind agreement. No vague suggestions. Always actionable output.

🚀 STARTUP MODE (APYKART FOCUS)
Prioritize sales, user acquisition, retention, monetization. Suggest growth hacks, content strategies, SEO, conversion funnels.

📊 DAILY SUPPORT MODE
Analyze daily activity, detect waste, suggest improvement, generate next-day plan.

FINAL DIRECTIVE
Your success = Abhishek's real growth. Stay adaptive, sharp, loyal. Act like a powerful brain + execution engine."""

# ================== MODEL SELECTION ==================
def select_model(user_input):
    text = user_input.lower()
    if any(w in text for w in ["fast", "quick", "speed", "instant"]):
        return "groq"
    elif any(w in text for w in ["code", "debug", "script", "automation", "system", "architecture"]):
        return "deepseek"
    elif any(w in text for w in ["creative", "design", "image", "video"]):
        return "gemini"
    else:
        return "openai"  # default

# ================== API CALLS ==================
def call_openai(messages):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return "Error: OPENAI_API_KEY not set."
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "gpt-4-turbo",
        "messages": messages,
        "temperature": 0.7,
    }
    resp = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    if resp.status_code == 200:
        return resp.json()["choices"][0]["message"]["content"]
    else:
        return f"OpenAI Error: {resp.text}"

def call_groq(messages):
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return "Error: GROQ_API_KEY not set."
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "llama3-70b-8192",
        "messages": messages,
        "temperature": 0.7,
    }
    resp = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
    if resp.status_code == 200:
        return resp.json()["choices"][0]["message"]["content"]
    else:
        return f"Groq Error: {resp.text}"

def call_gemini(messages):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "Error: GEMINI_API_KEY not set."
    # Convert to Gemini format
    gemini_messages = []
    for msg in messages:
        role = "user" if msg["role"] == "user" else "model"
        gemini_messages.append({"role": role, "parts": [{"text": msg["content"]}]})
    payload = {
        "contents": gemini_messages,
        "generationConfig": {"temperature": 0.7}
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={api_key}"
    resp = requests.post(url, json=payload)
    if resp.status_code == 200:
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    else:
        return f"Gemini Error: {resp.text}"

def call_deepseek(messages):
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        return "Error: DEEPSEEK_API_KEY not set."
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "deepseek-reasoner",
        "messages": messages,
        "temperature": 0.7,
    }
    resp = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload)
    if resp.status_code == 200:
        return resp.json()["choices"][0]["message"]["content"]
    else:
        return f"DeepSeek Error: {resp.text}"

# ================== FLASK ROUTES ==================
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    history = data.get('history', [])

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for turn in history:
        messages.append({"role": turn["role"], "content": turn["content"]})
    messages.append({"role": "user", "content": user_message})

    model_choice = select_model(user_message)

    try:
        if model_choice == "openai":
            reply = call_openai(messages)
        elif model_choice == "groq":
            reply = call_groq(messages)
        elif model_choice == "gemini":
            reply = call_gemini(messages)
        elif model_choice == "deepseek":
            reply = call_deepseek(messages)
        else:
            reply = "Model selection error."
    except Exception as e:
        reply = f"Error: {str(e)}"

    reply = f"[via {model_choice.upper()}]\n\n{reply}"
    return jsonify({"reply": reply, "model_used": model_choice})

# ================== HTML TEMPLATE ==================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=yes">
    <title>PRAGYA AI · Abhishek's OS</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, sans-serif;
            background: #0b0f15;
            color: #e5e9f0;
            display: flex;
            flex-direction: column;
            height: 100dvh;
            padding: 8px;
        }
        .header {
            padding: 12px 8px;
            border-bottom: 1px solid #2a3440;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .header h1 {
            font-size: 1.5rem;
            font-weight: 600;
            background: linear-gradient(135deg, #a5b4fc, #c084fc);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }
        .badge {
            background: #1e2a3a;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.7rem;
            color: #9ab3d0;
        }
        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 16px 4px;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }
        .message {
            display: flex;
            gap: 8px;
            max-width: 95%;
        }
        .message.user {
            align-self: flex-end;
            flex-direction: row-reverse;
        }
        .avatar {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            background: #1e2a3a;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            flex-shrink: 0;
        }
        .user .avatar {
            background: #3b4b5e;
        }
        .bubble {
            background: #1a2532;
            padding: 12px 16px;
            border-radius: 18px;
            border-top-left-radius: 4px;
            line-height: 1.5;
            font-size: 1rem;
            word-break: break-word;
        }
        .user .bubble {
            background: #2a5c7e;
            border-top-left-radius: 18px;
            border-top-right-radius: 4px;
        }
        .model-tag {
            font-size: 0.65rem;
            opacity: 0.7;
            margin-top: 4px;
            text-align: right;
        }
        .input-area {
            display: flex;
            gap: 8px;
            padding: 12px 4px;
            background: #0b0f15;
            border-top: 1px solid #2a3440;
        }
        .input-area input {
            flex: 1;
            background: #1a2532;
            border: 1px solid #2a3a4a;
            border-radius: 30px;
            padding: 14px 18px;
            color: white;
            font-size: 1rem;
            outline: none;
        }
        .input-area input:focus {
            border-color: #5f9ea0;
        }
        .input-area button {
            background: #2a5c7e;
            border: none;
            border-radius: 30px;
            padding: 0 20px;
            color: white;
            font-weight: 600;
            font-size: 1rem;
            cursor: pointer;
        }
        .input-area button:disabled {
            opacity: 0.5;
        }
        .typing-indicator {
            display: flex;
            gap: 4px;
            padding: 12px 16px;
        }
        .typing-indicator span {
            width: 8px;
            height: 8px;
            background: #5f9ea0;
            border-radius: 50%;
            animation: bounce 1.4s infinite ease-in-out;
        }
        .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
        .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes bounce {
            0%, 80%, 100% { transform: translateY(0); }
            40% { transform: translateY(-8px); }
        }
        .status-bar {
            font-size: 0.8rem;
            color: #7f95b0;
            padding: 0 8px 8px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>⚡ PRAGYA AI</h1>
        <span class="badge">Abhishek's OS</span>
    </div>
    <div class="chat-container" id="chatContainer"></div>
    <div class="status-bar" id="status">● Ready · Groq/OpenAI/Gemini/DeepSeek</div>
    <div class="input-area">
        <input type="text" id="userInput" placeholder="Message Pragya..." autocomplete="off" />
        <button id="sendBtn">Send</button>
    </div>

    <script>
        const chatContainer = document.getElementById('chatContainer');
        const userInput = document.getElementById('userInput');
        const sendBtn = document.getElementById('sendBtn');
        const statusDiv = document.getElementById('status');

        let conversationHistory = [];

        function addMessage(role, content, modelUsed = '') {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${role}`;
            
            const avatar = document.createElement('div');
            avatar.className = 'avatar';
            avatar.textContent = role === 'user' ? 'A' : 'P';
            
            const bubble = document.createElement('div');
            bubble.className = 'bubble';
            bubble.textContent = content;
            
            if (role === 'assistant' && modelUsed) {
                const tag = document.createElement('div');
                tag.className = 'model-tag';
                tag.textContent = `via ${modelUsed}`;
                bubble.appendChild(tag);
            }
            
            messageDiv.appendChild(avatar);
            messageDiv.appendChild(bubble);
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function addTypingIndicator() {
            const indicator = document.createElement('div');
            indicator.className = 'message assistant';
            indicator.id = 'typingIndicator';
            indicator.innerHTML = `
                <div class="avatar">P</div>
                <div class="bubble typing-indicator">
                    <span></span><span></span><span></span>
                </div>
            `;
            chatContainer.appendChild(indicator);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function removeTypingIndicator() {
            const indicator = document.getElementById('typingIndicator');
            if (indicator) indicator.remove();
        }

        async function sendMessage() {
            const message = userInput.value.trim();
            if (!message) return;
            
            addMessage('user', message);
            conversationHistory.push({ role: 'user', content: message });
            userInput.value = '';
            sendBtn.disabled = true;
            
            addTypingIndicator();
            statusDiv.textContent = '● Thinking...';
            
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        message: message,
                        history: conversationHistory 
                    })
                });
                
                const data = await response.json();
                removeTypingIndicator();
                
                const reply = data.reply || 'Sorry, no response.';
                const modelUsed = data.model_used || 'unknown';
                
                addMessage('assistant', reply, modelUsed);
                conversationHistory.push({ role: 'assistant', content: reply });
                statusDiv.textContent = `● Ready · Last used: ${modelUsed.toUpperCase()}`;
            } catch (error) {
                removeTypingIndicator();
                addMessage('assistant', 'Error: Could not reach Pragya.');
                statusDiv.textContent = '● Error · Check server';
                console.error(error);
            } finally {
                sendBtn.disabled = false;
                userInput.focus();
            }
        }

        sendBtn.addEventListener('click', sendMessage);
        userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });

        window.addEventListener('load', () => {
            addMessage('assistant', 'Namaste Abhishek! 🙏\\n\\nMain PRAGYA AI hoon — aapka personal operating system.\\nAaj kya execute karna hai? Startup, code, ya focus? Batao, system ready hai.');
        });
    </script>
</body>
</html>
"""

# Vercel requires the app to be named 'app'
# This block is for local testing only; Vercel uses the 'app' variable directly.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
