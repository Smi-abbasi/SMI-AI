import streamlit as st
import ollama
import json
from datetime import datetime


st.set_page_config(
    page_title="SMI AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif !important;
}
.stApp {
    background: #020617 !important;
    color: #F1F5F9 !important;
}
[data-testid="stAppViewContainer"] {
    overflow-x: hidden !important;
}

.main {
    overflow-x: hidden !important;
}
/* ── Hide Streamlit default chrome ── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

/* ── Subtle background glow ── */
.stApp::before {
    content: '';
    position: fixed; inset: 0; pointer-events: none; z-index: 0;
    background:
        radial-gradient(ellipse 80% 50% at 15% 10%, rgba(0,229,255,0.05) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 85% 85%, rgba(99,102,241,0.06) 0%, transparent 60%);
}

/* ── Main content area ──
   top: 88px header + 52px info bar = 140px + 20px gap = 160px
   bottom: 110px for fixed chat input
   NOTE: only ONE definition here — no duplicates
── */
.block-container {
    max-width: 860px !important;
    margin: 0 auto !important;
    padding-top: 160px !important;
    padding-bottom: 120px !important;
    padding-left: 24px !important;
    padding-right: 24px !important;
}

/* ════════════════════════
   HEADER
════════════════════════ */
.smi-header {
    position: fixed; top: 0; left: 0; right: 0;
    height: 88px; z-index: 1000;
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 32px;
    background: rgba(2, 6, 23, 0.92);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border-bottom: 1px solid rgba(255,255,255,0.08);
}
.smi-header-left {
    display: flex; align-items: center; gap: 14px;
}
.smi-logo {
    width: 44px; height: 44px; flex-shrink: 0;
    background: linear-gradient(135deg, #00E5FF, #6366F1);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px;
    box-shadow: 0 0 24px rgba(0,229,255,0.3);
}
.smi-header h1 {
    margin: 0; font-size: 24px; font-weight: 700; line-height: 1.2;
    background: linear-gradient(135deg, #00E5FF 0%, #818CF8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.smi-header p {
    margin: 3px 0 0 0;
    color: #64748B; font-size: 12px; line-height: 1;
}
.status-badge {
    display: flex; align-items: center; gap: 7px;
    background: rgba(16,185,129,0.1);
    border: 1px solid rgba(16,185,129,0.3);
    border-radius: 20px; padding: 6px 14px;
    font-size: 12px; font-weight: 600; color: #10B981;
    white-space: nowrap;
}
.status-dot {
    width: 7px; height: 7px;
    background: #10B981; border-radius: 50%;
    animation: pulse-dot 2s ease-in-out infinite;
}
@keyframes pulse-dot {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%       { opacity: 0.4; transform: scale(0.8); }
}

/* ════════════════════════
   INFO BAR (below header)
════════════════════════ */
.info-bar {
    position: fixed;
    top: 88px; left: 0; right: 0;
    z-index: 990;
    background: rgba(5, 10, 25, 0.95);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(255,255,255,0.06);
    padding: 8px 32px;
}
.info-bar-inner {
    max-width: 860px; margin: 0 auto;
    display: flex; align-items: center;
    justify-content: space-between; gap: 12px;
    flex-wrap: wrap;
}
.info-bar-left {
    display: flex; align-items: center; gap: 10px; flex-shrink: 0;
}
.ib-model-badge {
    display: flex; align-items: center; gap: 6px;
    background: rgba(99,102,241,0.12);
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: 8px; padding: 4px 10px;
    font-size: 12px; color: #A5B4FC; font-weight: 500;
}
.ib-temp-badge {
    display: flex; align-items: center; gap: 6px;
    background: rgba(0,229,255,0.07);
    border: 1px solid rgba(0,229,255,0.15);
    border-radius: 8px; padding: 4px 10px;
    font-size: 12px; color: #67E8F9;
}
.chips-row {
    display: flex; align-items: center; gap: 6px; flex-wrap: wrap;
}
.chip {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 16px; padding: 3px 10px;
    font-size: 11px; color: #94A3B8;
    white-space: nowrap;
}

/* ════════════════════════
   SIDEBAR
════════════════════════ */
section[data-testid="stSidebar"] {
    background: #080E1F !important;
    border-right: 1px solid rgba(255,255,255,0.07) !important;
    /* z-index lower than header but still above content */
    z-index: 999 !important;
}
/* Target only safe text elements — NOT *, NOT button, NOT input */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] div.stMarkdown {
    color: #CBD5E1 !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #F1F5F9 !important;
}
/* Sidebar collapse button — always visible */
[data-testid="collapsedControl"] {
    z-index: 1001 !important;
    visibility: visible !important;
    display: flex !important;
    color: white !important;
    background: rgba(2,6,23,0.9) !important;
    border-right: 1px solid rgba(255,255,255,0.08) !important;
}
/* Sidebar brand card */
.sb-brand {
    display: flex; align-items: center; gap: 12px;
    padding: 14px 16px; margin-bottom: 20px;
    background: linear-gradient(135deg, rgba(0,229,255,0.06), rgba(99,102,241,0.06));
    border: 1px solid rgba(99,102,241,0.15);
    border-radius: 14px;
}
.sb-brand-icon {
    width: 42px; height: 42px; flex-shrink: 0;
    background: linear-gradient(135deg, #00E5FF, #6366F1);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px;
}
.sb-brand-name {
    font-size: 16px; font-weight: 700; color: #F1F5F9 !important;
}
.sb-brand-sub {
    font-size: 11px; color: #64748B !important; margin-top: 2px;
}
/* Stat cards */
.stat-row {
    display: grid; grid-template-columns: 1fr 1fr; gap: 8px;
    margin: 12px 0;
}
.stat-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px; padding: 10px;
    text-align: center;
}
.stat-val { font-size: 22px; font-weight: 700; color: #00E5FF !important; }
.stat-lbl { font-size: 10px; color: #475569 !important; margin-top: 2px; }
/* Section labels */
.sec-label {
    font-size: 10px; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.1em;
    color: #334155 !important;
    margin: 18px 0 6px 0;
}
.sec-hint {
    font-size: 11px; color: #475569 !important;
    margin: -2px 0 8px 0;
}

/* ════════════════════════
   CHAT MESSAGES
════════════════════════ */
.stChatMessage {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    box-shadow: none !important;
}
.msg-wrap { margin-bottom: 16px; }
.msg-meta {
    font-size: 11px; color: #475569;
    margin-bottom: 5px;
    display: flex; align-items: center; gap: 5px;
}
/* User bubble — right style with directional radius */
.user-msg {
    background: linear-gradient(135deg, #1E40AF, #2563EB);
    color: #FFFFFF;
    padding: 14px 18px;
    border-radius: 18px 18px 4px 18px;
    font-size: 15px; line-height: 1.7;
    box-shadow: 0 4px 20px rgba(37,99,235,0.25);
    word-wrap: break-word; white-space: pre-wrap;
}
/* AI bubble */
.ai-msg {
    background: rgba(13, 20, 40, 0.95);
    border: 1px solid rgba(255,255,255,0.08);
    color: #E2E8F0;
    padding: 16px 20px;
    border-radius: 18px 18px 18px 4px;
    font-size: 15px; line-height: 1.85;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    word-wrap: break-word; white-space: pre-wrap;
}
.msg-foot {
    display: flex; align-items: center; gap: 8px;
    margin-top: 5px;
}
.foot-time { font-size: 11px; color: #1E293B; }
.foot-words {
    font-size: 10px; color: #334155;
    background: rgba(255,255,255,0.04);
    border-radius: 6px; padding: 1px 6px;
}

/* ════════════════════════
   TYPING INDICATOR
════════════════════════ */
.typing-wrap {
    display: flex; align-items: center; gap: 8px;
    padding: 12px 18px; width: fit-content;
    background: rgba(13,20,40,0.95);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px 18px 18px 4px;
    margin-bottom: 16px;
}
.t-dot {
    width: 7px; height: 7px;
    background: #00E5FF; border-radius: 50%;
    animation: bounce-dot 1.3s ease-in-out infinite;
}
.t-dot:nth-child(2) { animation-delay: 0.18s; }
.t-dot:nth-child(3) { animation-delay: 0.36s; }
@keyframes bounce-dot {
    0%, 60%, 100% { opacity: 0.2; transform: translateY(0); }
    30%            { opacity: 1;   transform: translateY(-6px); }
}
.t-label { font-size: 12px; color: #475569; margin-left: 4px; }

/* ════════════════════════
   CHAT INPUT — dark bg fix
════════════════════════ */
[data-testid="stChatInput"] {
    position: fixed !important;
    bottom: 20px; left: 50%; transform: translateX(-50%);
    width: min(860px, calc(100% - 32px)) !important;
    background: #080E1F !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    border-radius: 20px !important;
    padding: 8px 10px !important;
    backdrop-filter: blur(20px);
    z-index: 998 !important;
    box-shadow: 0 -2px 30px rgba(0,0,0,0.5), 0 0 0 1px rgba(0,229,255,0.04);
}
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] > div > div,
[data-testid="stChatInput"] > div > div > div,
[data-testid="stChatInput"] > div > div > div > div {
    background: #080E1F !important;
    border-radius: 14px !important;
    border: none !important;
}
[data-testid="stChatInput"] textarea {
    background: #080E1F !important;
    color: #F1F5F9 !important;
    caret-color: #00E5FF !important;
    font-size: 15px !important; font-family: 'Inter', sans-serif !important;
    border: none !important; outline: none !important; box-shadow: none !important;
    border-radius: 14px !important;
    min-height: 44px !important; padding: 10px 4px !important;
    resize: none !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #334155 !important; opacity: 1 !important;
}
[data-testid="stChatInput"] [data-baseweb="textarea"],
[data-testid="stChatInput"] [data-baseweb="base-input"],
[data-testid="stChatInput"] [data-baseweb="input"] {
    background: #080E1F !important;
    border: none !important; box-shadow: none !important;
}
[data-testid="stChatInputSubmitButton"] {
    background: linear-gradient(135deg, #00C6FF, #6366F1) !important;
    border-radius: 12px !important;
    border: none !important;
}
[data-testid="stChatInputSubmitButton"]:hover {
    opacity: 0.85 !important;
}

/* ════════════════════════
   BUTTONS
════════════════════════ */
.stButton > button {
    width: 100% !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
    padding: 9px 14px !important;
    font-weight: 600 !important; font-size: 13px !important;
    transition: all 0.2s ease !important;
    cursor: pointer !important;
    background: rgba(255,255,255,0.05) !important;
    color: #CBD5E1 !important;
}
.stButton > button:hover {
    background: rgba(255,255,255,0.09) !important;
    border-color: rgba(255,255,255,0.15) !important;
    transform: translateY(-1px) !important;
}
/* Primary button (Clear) */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #DC2626, #B91C1C) !important;
    border-color: transparent !important;
    color: white !important;
}

/* ════════════════════════
   QUICK START CARDS
════════════════════════ */
.qs-title {
    text-align: center; font-size: 13px; color: #475569;
    margin: 12px 0 10px;
}

/* ════════════════════════
   MISC
════════════════════════ */
hr { border: none !important; border-top: 1px solid rgba(255,255,255,0.07) !important; margin: 16px 0 !important; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.15); }
::selection { background: #2563EB; color: white; }

/* ════════════════════════
   MOBILE  ≤ 768px
════════════════════════ */
@media (max-width: 768px) {
    .smi-header {
        height: 60px; padding: 0 14px;
    }
    .smi-logo { width: 34px; height: 34px; font-size: 17px; border-radius: 9px; }
    .smi-header h1 { font-size: 18px; }
    .smi-header p  { font-size: 10px; }
    .status-badge  { padding: 5px 9px; font-size: 11px; }

    .info-bar { top: 60px; padding: 7px 14px; }
    .ib-model-badge, .ib-temp-badge { font-size: 11px; padding: 3px 8px; }
    .chip { font-size: 10px; padding: 2px 8px; }

    /* content clears 60px header + ~46px info bar + gap */
    .block-container {
        padding-top: 125px !important;
        padding-left: 12px !important;
        padding-right: 12px !important;
        padding-bottom: 100px !important;
    }
    .user-msg, .ai-msg { font-size: 14px; padding: 12px 14px; }
    [data-testid="stChatInput"] {
        width: calc(100% - 14px) !important;
        bottom: 10px;
        border-radius: 16px !important;
    }
    .welcome-card-fixed {
    position: sticky;
    top: 88px;
}
</style>
""", unsafe_allow_html=True)

# CONSTANTS
AVAILABLE_MODELS = ["phi3", "tinyllama", "llama3", "mistral", "gemma", "codellama", "llama2"]

PERSONALITIES = {
    "🎯 Professional":    "Be formal, concise, precise, and structured in all responses.",
    "📚 Friendly Tutor":  "Be warm and encouraging. Explain step by step like a great teacher. Use simple analogies.",
    "💻 Code Expert":     "Focus on clean, well-commented code and best practices. Always explain what the code does and WHY.",
    "🎨 Creative":        "Be imaginative and think outside the box. Use metaphors and creative analogies.",
}

BASE_SYSTEM_PROMPT = """You are SMI (Smart Mind Intelligence), a professional AI assistant created by Sami Ullah Akhtar.

Core rules:
- Your name is always SMI. Never say you are any other model.
- Be professional, precise, and intelligent at all times.
- Give practical, beginner-friendly explanations when needed.
- Help with: coding, AI, databases, web dev, productivity, learning, and projects.
- Format all code using proper markdown code blocks with language specified.
- Keep responses concise unless the user asks for detail.
- Always be respectful, encouraging, and constructive.
- When explaining code: explain the WHY, not just the WHAT.
"""


# SESSION STATE INIT

if "messages"      not in st.session_state: st.session_state.messages      = []
if "session_start" not in st.session_state: st.session_state.session_start = datetime.now().strftime("%H:%M")

# 
# SIDEBAR

with st.sidebar:

    # Brand
    st.markdown("""
    <div class="sb-brand">
        <div class="sb-brand-icon">🤖</div>
        <div>
            <div class="sb-brand-name">SMI AI</div>
            <div class="sb-brand-sub">Smart Mind Intelligence</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Stats ──
    total  = len(st.session_state.messages)
    yours  = sum(1 for m in st.session_state.messages if m["role"] == "user")
    st.markdown('<div class="sec-label">📊 Session Stats</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-card"><div class="stat-val">{total}</div><div class="stat-lbl">Total</div></div>
        <div class="stat-card"><div class="stat-val">{yours}</div><div class="stat-lbl">Yours</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr>', unsafe_allow_html=True)

    # ── Model ──
    st.markdown('<div class="sec-label">🤖 AI Model</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-hint">The local Ollama model to use</div>', unsafe_allow_html=True)
    selected_model = st.selectbox(
        "model", AVAILABLE_MODELS, index=0,
        label_visibility="collapsed"
    )

    # ── Personality ──
    st.markdown('<div class="sec-label">🎭 Personality</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-hint">Changes how SMI responds</div>', unsafe_allow_html=True)
    personality_key = st.selectbox(
        "personality", list(PERSONALITIES.keys()), index=0,
        label_visibility="collapsed"
    )

    # ── Temperature ──
    st.markdown('<div class="sec-label">🎨 Creativity</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-hint">Low = precise · High = creative</div>', unsafe_allow_html=True)
    temperature = st.slider("temp", 0.0, 1.0, 0.3, 0.05, label_visibility="collapsed")

    # ── Memory ──
    st.markdown('<div class="sec-label">🧠 Memory</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-hint">Past messages AI remembers</div>', unsafe_allow_html=True)
    memory_limit = st.slider("memory", 2, 20, 8, 1, label_visibility="collapsed")

    # ── Max tokens ──
    st.markdown('<div class="sec-label">📏 Response Length</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-hint">Max tokens · 300 tokens ≈ 225 words</div>', unsafe_allow_html=True)
    max_tokens = st.slider("tokens", 100, 1000, 400, 50, label_visibility="collapsed")

    st.markdown('<hr>', unsafe_allow_html=True)

    # ── Export ──
    st.markdown('<div class="sec-label">💾 Export</div>', unsafe_allow_html=True)

    if st.button("📋 View as Text"):
        if st.session_state.messages:
            lines = [f"SMI AI — Export\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n{'─'*36}\n"]
            for m in st.session_state.messages:
                role = "You" if m["role"] == "user" else "SMI"
                t    = m.get("time", "")
                lines.append(f"[{role}  {t}]\n{m['content']}\n")
            st.code("\n".join(lines), language=None)
        else:
            st.info("No messages to export yet.")

    if st.session_state.messages:
        export_data = json.dumps({
            "app": "SMI AI",
            "exported_at": datetime.now().isoformat(),
            "model": selected_model,
            "messages": [
                {"role": m["role"], "content": m["content"], "time": m.get("time","")}
                for m in st.session_state.messages
            ]
        }, indent=2, ensure_ascii=False)
        st.download_button(
            "⬇️ Download JSON", data=export_data,
            file_name=f"smi_chat_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json"
        )

    st.markdown('<hr>', unsafe_allow_html=True)

    if st.button("🗑️ Clear Conversation", type="primary"):
        st.session_state.messages = []
        st.rerun()

    # Footer
    st.markdown(f"""
    <div style="font-size:11px; color:#1E293B; text-align:center; line-height:2; margin-top:14px;">
        Started: {st.session_state.session_start}<br>
        Model: <span style="color:#00E5FF">{selected_model}</span>
        · Temp: <span style="color:#67E8F9">{temperature}</span><br>
        <span style="color:#6366F1; font-weight:600;">Built by Sami Ullah Akhtar</span>
    </div>
    """, unsafe_allow_html=True)

# ACTIVE SYSTEM PROMPT (base + personality)
active_prompt = BASE_SYSTEM_PROMPT + "\nPersonality instruction: " + PERSONALITIES[personality_key]

#
# FIXED HEADER
st.markdown("""
<div class="smi-header">
    <div class="smi-header-left">
        <div class="smi-logo">🤖</div>
        <div>
            <h1>SMI AI</h1>
            <p>Smart Mind Intelligence · by Sami Ullah Akhtar</p>
        </div>
    </div>
    <div class="status-badge">
        <div class="status-dot"></div>
        Online
    </div>
</div>
""", unsafe_allow_html=True)


# FIXED INFO BAR (always visible, shows current settings)
st.markdown(f"""
<div class="info-bar">
    <div class="info-bar-inner">
        <div class="info-bar-left">
            <div class="ib-model-badge">🤖 {selected_model}</div>
            <div class="ib-temp-badge">🎨 {temperature}</div>
        </div>
        <div class="chips-row">
            <div class="chip">💻 Coding</div>
            <div class="chip">📚 Learning</div>
            <div class="chip">🛠️ Projects</div>
            <div class="chip">🧠 AI</div>
            <div class="chip">🗄️ Databases</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════
# QUICK START (only when no messages yet)
# ═══════════════════════════════════════════
if len(st.session_state.messages) == 0:
    st.markdown("""
    <div style="text-align:center; margin: 32px 0 8px;">
        <div style="font-size:48px; margin-bottom:10px;">🤖</div>
        <div style="font-size:22px; font-weight:700; color:#F1F5F9; margin-bottom:8px;">Welcome to SMI AI</div>
        <div style="font-size:14px; color:#64748B; max-width:440px; margin:0 auto; line-height:1.7;">
            Your intelligent local AI assistant — private, offline, powered by Ollama.
            Open the sidebar to change model and settings.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="qs-title">✨ Try a quick start:</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    qs = [
        ("💡 Explain OOP",  "Explain Object Oriented Programming with a simple real-world example"),
        ("🐍 Python Tips",  "What are the most important Python concepts a CS student must know?"),
        ("🗄️ SQL JOINs",   "Explain SQL JOINs with clear examples — when to use each type?"),
    ]
    for col, (label, prompt) in zip([c1, c2, c3], qs):
        with col:
            if st.button(label):
                st.session_state.messages.append({
                    "role": "user", "content": prompt,
                    "time": datetime.now().strftime("%H:%M")
                })
                st.rerun()

# CHAT INPUT 

user_input = st.chat_input(f"Ask SMI anything… ({selected_model})")

# DISPLAY HISTORY

for msg in st.session_state.messages:
    t  = msg.get("time", "")
    wc = len(msg["content"].split())
    with st.chat_message(msg["role"]):
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="msg-wrap">
                <div class="msg-meta">🧑 You &nbsp;·&nbsp; {t}</div>
                <div class="user-msg">{msg["content"]}</div>
            </div>""", unsafe_allow_html=True)
        else:
            rt = msg.get("response_time", "–")
            st.markdown(f"""
            <div class="msg-wrap">
                <div class="msg-meta">🤖 SMI &nbsp;·&nbsp; {t}</div>
                <div class="ai-msg">{msg["content"]}</div>
                <div class="msg-foot">
                    <span class="foot-time">⏱ {rt}s</span>
                    <span class="foot-words">~{wc} words</span>
                </div>
            </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════
# NEW MESSAGE + AI RESPONSE
# ═══════════════════════════════════════════
if user_input:
    now = datetime.now().strftime("%H:%M")

    # 1️⃣ Append user message to history
    st.session_state.messages.append({
        "role": "user", "content": user_input, "time": now
    })

    # 2️⃣ Render user bubble once
    with st.chat_message("user"):
        st.markdown(f"""
        <div class="msg-wrap">
            <div class="msg-meta">🧑 You &nbsp;·&nbsp; {now}</div>
            <div class="user-msg">{user_input}</div>
        </div>""", unsafe_allow_html=True)

    # 3️⃣ Stream AI response
    with st.chat_message("assistant"):
        typing_slot = st.empty()
        typing_slot.markdown("""
        <div class="typing-wrap">
            <div class="t-dot"></div>
            <div class="t-dot"></div>
            <div class="t-dot"></div>
            <span class="t-label">SMI is thinking…</span>
        </div>""", unsafe_allow_html=True)

        stream_slot   = st.empty()
        full_response = ""
        start_time    = datetime.now()
        response_time = 0

        try:
            # Build history for context — only role + content, no extra keys
            history = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages[-memory_limit:]
            ]

            stream = ollama.chat(
                model=selected_model,
                messages=[{"role": "system", "content": active_prompt}] + history,
                stream=True,
                options={"temperature": temperature, "num_predict": max_tokens}
            )

            typing_slot.empty()  # remove typing dots once streaming starts

            for chunk in stream:
                token          = chunk["message"]["content"]
                full_response += token
                # Live streaming — show cursor ▌ while generating
                stream_slot.markdown(
                    f'<div class="ai-msg">{full_response}▌</div>',
                    unsafe_allow_html=True
                )

            response_time = round((datetime.now() - start_time).total_seconds(), 2)
            wc            = len(full_response.split())
            resp_now      = datetime.now().strftime("%H:%M")

            # Final render — cursor gone, footer added
            stream_slot.markdown(f"""
            <div class="msg-wrap">
                <div class="msg-meta">🤖 SMI &nbsp;·&nbsp; {resp_now}</div>
                <div class="ai-msg">{full_response}</div>
                <div class="msg-foot">
                    <span class="foot-time">⏱ {response_time}s</span>
                    <span class="foot-words">~{wc} words</span>
                </div>
            </div>""", unsafe_allow_html=True)

        except Exception as e:
            typing_slot.empty()
            response_time = round((datetime.now() - start_time).total_seconds(), 2)
            full_response = (
                f"❌ Could not connect to Ollama.\n\n"
                f"Error: {str(e)}\n\n"
                f"Fix:\n"
                f"1. Open a terminal and run:  ollama serve\n"
                f"2. Install the model:        ollama pull {selected_model}\n"
                f"3. Refresh this page."
            )
            stream_slot.markdown(
                f'<div class="ai-msg">{full_response}</div>',
                unsafe_allow_html=True
            )

    # 4️⃣ Save AI response, then rerun for clean single render
    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response,
        "time": datetime.now().strftime("%H:%M"),
        "response_time": response_time
    })
    st.rerun()

# Bottom breathing room above fixed input bar
st.markdown("<div style='height:90px'></div>", unsafe_allow_html=True)