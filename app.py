import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import streamlit as st
import uuid
import datetime
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

from core.graph import build_graph
from core.state import AgentState
from core.checkpointer import Checkpointer

st.set_page_config(page_title="AgentFlow // JARVIS", page_icon="⬡", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700;800;900&display=swap');

:root {
    --obsidian: #050505;
    --obsidian2: #080c12;
    --cyan: #00ffff;
    --cyan4: rgba(0,255,255,0.05);
    --purple: #8a2be2;
    --glass: rgba(255,255,255,0.03);
    --border: rgba(0,255,255,0.08);
    --border2: rgba(0,255,255,0.2);
    --text3: rgba(0,255,255,0.4);
    --red: #ff2d55;
    --green: #00ff88;
    --yellow: #ffcc00;
}

*, *::before, *::after { box-sizing: border-box; }
html, body { background: var(--obsidian) !important; font-family: 'JetBrains Mono', monospace !important; }
.stApp { background: var(--obsidian) !important; }

.stApp::before {
    content: '';
    position: fixed; inset: 0;
    background-image:
        linear-gradient(rgba(0,255,255,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,255,255,0.03) 1px, transparent 1px);
    background-size: 60px 60px;
    animation: gridMove 25s linear infinite;
    pointer-events: none; z-index: 0;
}
@keyframes gridMove { 0%{background-position:0 0} 100%{background-position:60px 60px} }

.stApp::after {
    content: '';
    position: fixed; top: -20vh; right: -15vw;
    width: 70vw; height: 70vh;
    background: radial-gradient(ellipse, rgba(138,43,226,0.05) 0%, transparent 65%);
    pointer-events: none; z-index: 0;
    animation: orbPulse 10s ease-in-out infinite;
}
@keyframes orbPulse { 0%,100%{opacity:0.5} 50%{opacity:1} }

section[data-testid="stSidebar"] {
    background: rgba(4,4,8,0.98) !important;
    border-right: 1px solid var(--border2) !important;
}
section[data-testid="stSidebar"] > div { padding: 1.75rem 1.5rem !important; z-index: 1; position: relative; }

.block-container { padding: 2.5rem 3.5rem 5rem !important; position: relative; z-index: 1; max-width: 100% !important; }

.scanline {
    position: fixed; inset: 0;
    background: repeating-linear-gradient(0deg, transparent, transparent 3px, rgba(0,255,255,0.006) 3px, rgba(0,255,255,0.006) 4px);
    pointer-events: none; z-index: 9999;
}

.neural-bg { position: fixed; top:0; left:0; width:100vw; height:100vh; pointer-events:none; z-index:0; opacity:0.35; }

/* STATUS BAR */
.status-bar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.75rem 2rem;
    background: rgba(0,255,255,0.02);
    border: 1px solid rgba(0,255,255,0.1);
    border-radius: 10px;
    margin-bottom: 3rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: var(--text3);
    letter-spacing: 0.08em;
}
.s-dot { display:inline-flex; align-items:center; gap:0.5rem; }
.dot { width:6px; height:6px; border-radius:50%; }
.dot.green { background:var(--green); box-shadow:0 0 10px var(--green); animation:blink 2s ease infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.2} }

/* HERO */
.hero { padding: 2rem 0 3rem; margin-bottom: 3rem; border-bottom: 1px solid rgba(0,255,255,0.06); }

.hero-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem; letter-spacing: 0.4em;
    color: var(--cyan); text-transform: uppercase;
    margin-bottom: 1.25rem; opacity: 0.6;
    display: flex; align-items: center; gap: 1rem;
}
.hero-eyebrow::before { content:''; width:32px; height:1px; background:var(--cyan); }

.hero-title {
    font-family: 'Inter', sans-serif;
    font-size: clamp(5rem, 11vw, 9rem);
    font-weight: 900; line-height: 0.85;
    letter-spacing: -0.05em; margin-bottom: 1.25rem;
}
.hero-title .t1 { color: #fff; }
.hero-title .t2 {
    background: linear-gradient(90deg, var(--cyan), var(--purple));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; display: block;
}

.hero-version { font-family:'JetBrains Mono',monospace; font-size:0.78rem; color:var(--text3); letter-spacing:0.2em; margin-bottom:1.75rem; }

.hero-desc {
    font-family: 'Inter', sans-serif;
    font-size: 1.15rem; color: rgba(255,255,255,0.38);
    line-height: 1.75; max-width: 640px; font-weight: 300;
}

.live-pill {
    display: inline-flex; align-items: center; gap: 0.5rem;
    padding: 0.35rem 1.1rem;
    border: 1px solid rgba(0,255,136,0.35); border-radius: 100px;
    background: rgba(0,255,136,0.06);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem; color: var(--green);
    letter-spacing: 0.12em; margin-left: 1rem;
    vertical-align: middle; text-shadow: 0 0 12px var(--green);
}

/* PIPELINE */
.pipeline {
    display: grid; grid-template-columns: repeat(4, 1fr);
    gap: 1px; background: rgba(0,255,255,0.07);
    border: 1px solid var(--border2); border-radius: 18px;
    overflow: hidden; margin-bottom: 3rem; position: relative;
}
.pipeline::after {
    content:''; position:absolute; top:0; left:0; right:0; height:1px;
    background: linear-gradient(90deg, transparent, var(--cyan), var(--purple), transparent);
    animation: scan 3s ease infinite;
}
@keyframes scan {
    0%{transform:scaleX(0);transform-origin:left} 50%{transform:scaleX(1);transform-origin:left}
    51%{transform:scaleX(1);transform-origin:right} 100%{transform:scaleX(0);transform-origin:right}
}

.p-node { background:var(--obsidian2); padding:1.75rem 1.5rem; position:relative; transition:background 0.3s; }
.p-node:hover { background:rgba(0,255,255,0.04); }
.p-bar { position:absolute; bottom:0; left:0; right:0; height:1px; background:linear-gradient(90deg,var(--cyan),var(--purple)); opacity:0; transition:opacity 0.3s; }
.p-node:hover .p-bar { opacity:1; }
.p-num { font-family:'JetBrains Mono',monospace; font-size:0.62rem; color:var(--text3); letter-spacing:0.2em; margin-bottom:0.75rem; }
.p-name { font-family:'Inter',sans-serif; font-size:1.1rem; font-weight:700; color:#fff; margin-bottom:0.4rem; }
.p-role { font-family:'JetBrains Mono',monospace; font-size:0.72rem; color:var(--text3); line-height:1.5; }

/* TERMINAL */
.terminal-wrap {
    background: rgba(0,255,255,0.015);
    border: 1px solid var(--border2); border-radius: 18px;
    overflow: hidden; margin-bottom: 0.5rem;
}
.terminal-top {
    display:flex; align-items:center; gap:0.75rem;
    padding:1rem 1.5rem;
    background:rgba(0,255,255,0.03);
    border-bottom:1px solid var(--border);
}
.td { width:12px; height:12px; border-radius:50%; }
.td.r{background:var(--red);box-shadow:0 0 6px var(--red);}
.td.y{background:var(--yellow);box-shadow:0 0 6px var(--yellow);}
.td.g{background:var(--green);box-shadow:0 0 6px var(--green);}
.t-label { font-family:'JetBrains Mono',monospace; font-size:0.72rem; color:var(--text3); margin-left:auto; letter-spacing:0.1em; }
.t-body { padding:1.5rem 2rem 0.75rem; }
.t-prompt { font-family:'JetBrains Mono',monospace; font-size:0.8rem; color:var(--cyan); margin-bottom:0.6rem; }
.t-prompt::before { content:'> '; color:var(--purple); font-weight:700; }

/* RESULT CARDS */
.r-card {
    background: rgba(8,12,18,0.9);
    border: 1px solid rgba(0,255,255,0.1);
    border-radius: 18px; padding: 2.25rem;
    margin-bottom: 1.5rem;
    position: relative; overflow: hidden;
    animation: fadeUp 0.5s ease forwards;
}
@keyframes fadeUp { from{opacity:0;transform:translateY(20px)} to{opacity:1;transform:translateY(0)} }

.r-card::before {
    content:''; position:absolute; top:0; left:0; right:0; height:1px;
    background: linear-gradient(90deg, transparent, var(--cyan), transparent);
}

.r-top { display:flex; align-items:center; justify-content:space-between; margin-bottom:1.5rem; }

.r-badge {
    display:inline-flex; align-items:center; gap:0.6rem;
    font-family:'JetBrains Mono',monospace;
    font-size:0.68rem; font-weight:600;
    letter-spacing:0.18em; text-transform:uppercase;
    color:var(--cyan);
    background:rgba(0,255,255,0.06);
    border:1px solid rgba(0,255,255,0.18);
    border-radius:8px; padding:0.4rem 1rem;
}
.r-badge::before { content:'◈'; font-size:0.6rem; }

.r-status { font-family:'JetBrains Mono',monospace; font-size:0.65rem; color:rgba(0,255,136,0.5); letter-spacing:0.1em; }

.r-content {
    font-family: 'Inter', sans-serif;
    font-size: 1.05rem;
    color: rgba(255,255,255,0.65);
    line-height: 2; font-weight: 300;
}
.r-content strong, .r-content b { color: rgba(255,255,255,0.92); font-weight: 600; }

/* NUMBERED LIST STYLING */
.r-list-item {
    display: flex; gap: 1.25rem; padding: 0.9rem 0;
    border-bottom: 1px solid rgba(0,255,255,0.05);
    align-items: flex-start;
}
.r-list-num {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem; font-weight: 700;
    color: var(--cyan); opacity: 0.6;
    min-width: 28px; margin-top: 2px;
}
.r-list-text { font-family:'Inter',sans-serif; font-size:1rem; color:rgba(255,255,255,0.65); line-height:1.7; font-weight:300; }
.r-list-text strong { color:rgba(255,255,255,0.92); font-weight:600; }

/* FINAL ANSWER */
.final-wrap {
    background: linear-gradient(135deg, rgba(0,255,255,0.04), rgba(138,43,226,0.06));
    border: 1px solid rgba(0,255,255,0.3);
    border-radius: 22px; padding: 3.5rem;
    margin-top: 2.5rem; position: relative; overflow: hidden;
}
.final-wrap::before {
    content:''; position:absolute; top:0; left:0; right:0; height:2px;
    background: linear-gradient(90deg, var(--cyan), var(--purple), var(--cyan));
    background-size: 200% 100%;
    animation: slide 3s linear infinite;
}
@keyframes slide { 0%{background-position:0% 0%} 100%{background-position:200% 0%} }
.fg1 { position:absolute; bottom:-120px; left:-120px; width:450px; height:450px; background:radial-gradient(circle,rgba(138,43,226,0.1) 0%,transparent 65%); pointer-events:none; }
.fg2 { position:absolute; top:-120px; right:-120px; width:450px; height:450px; background:radial-gradient(circle,rgba(0,255,255,0.07) 0%,transparent 65%); pointer-events:none; }

.final-header {
    font-family:'JetBrains Mono',monospace; font-size:0.72rem;
    letter-spacing:0.3em; text-transform:uppercase;
    color:var(--cyan); margin-bottom:2rem;
    display:flex; align-items:center; gap:1rem;
    text-shadow:0 0 20px var(--cyan);
}
.final-header::after { content:''; flex:1; height:1px; background:linear-gradient(90deg,rgba(0,255,255,0.3),transparent); }

.final-content {
    font-family:'Inter',sans-serif;
    font-size:1.1rem; color:rgba(255,255,255,0.8);
    line-height:2.1; font-weight:300;
}
.final-content strong, .final-content b { color:#fff; font-weight:600; }

/* EXECUTION LOG */
.exec-log {
    font-family:'JetBrains Mono',monospace;
    font-size:0.72rem; color:rgba(0,255,255,0.25);
    margin:2.5rem 0 2rem;
    padding:1rem 1.5rem;
    background:rgba(0,255,255,0.015);
    border:1px solid rgba(0,255,255,0.06);
    border-radius:10px;
    display:flex; gap:2rem; flex-wrap:wrap;
}
.exec-log span { color:rgba(0,255,255,0.5); }

/* SIDEBAR */
.sb-head { padding:0.75rem 0 2rem; border-bottom:1px solid rgba(0,255,255,0.07); margin-bottom:1.75rem; }
.sb-sys { font-family:'JetBrains Mono',monospace; font-size:0.6rem; letter-spacing:0.3em; color:var(--cyan); opacity:0.4; margin-bottom:0.6rem; }
.sb-logo { font-family:'Inter',sans-serif; font-size:1.75rem; font-weight:900; letter-spacing:-0.03em; line-height:1; }
.sb-logo .l1{color:#fff;} .sb-logo .l2{background:linear-gradient(90deg,var(--cyan),var(--purple));-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.sb-sub { font-family:'JetBrains Mono',monospace; font-size:0.65rem; color:rgba(0,255,255,0.25); margin-top:0.5rem; }

.sb-sec { font-family:'JetBrains Mono',monospace; font-size:0.58rem; letter-spacing:0.25em; text-transform:uppercase; color:rgba(0,255,255,0.25); padding-bottom:0.5rem; border-bottom:1px solid rgba(0,255,255,0.07); margin:1.75rem 0 0.9rem; }

.ag-row { display:flex; align-items:center; gap:0.85rem; padding:0.7rem 0; border-bottom:1px solid rgba(255,255,255,0.02); }
.ag-ic { width:32px; height:32px; border-radius:9px; background:rgba(0,255,255,0.05); border:1px solid rgba(0,255,255,0.12); display:flex; align-items:center; justify-content:center; font-family:'JetBrains Mono',monospace; font-size:0.62rem; font-weight:700; color:var(--cyan); flex-shrink:0; text-shadow:0 0 8px var(--cyan); }
.ag-name { font-family:'Inter',sans-serif; font-size:0.88rem; font-weight:600; color:rgba(255,255,255,0.75); }
.ag-role { font-family:'JetBrains Mono',monospace; font-size:0.62rem; color:rgba(0,255,255,0.3); margin-top:0.15rem; }

.run-card { background:rgba(0,255,255,0.02); border:1px solid rgba(0,255,255,0.07); border-radius:9px; padding:0.7rem 0.9rem; margin-bottom:0.45rem; }
.run-id { font-family:'JetBrains Mono',monospace; font-size:0.65rem; color:var(--cyan); opacity:0.6; }
.run-ts { font-family:'JetBrains Mono',monospace; font-size:0.6rem; color:rgba(0,255,255,0.25); margin-top:0.15rem; }

.st-row { display:flex; align-items:center; gap:0.7rem; padding:0.45rem 0; border-bottom:1px solid rgba(255,255,255,0.02); }
.st-d { width:5px; height:5px; background:transparent; border:1px solid var(--cyan); transform:rotate(45deg); flex-shrink:0; opacity:0.4; }
.st-t { font-family:'JetBrains Mono',monospace; font-size:0.7rem; color:rgba(0,255,255,0.35); }

/* BUTTON */
.stButton > button {
    background:linear-gradient(135deg,rgba(0,255,255,0.08),rgba(138,43,226,0.08)) !important;
    color:var(--cyan) !important;
    border:1px solid rgba(0,255,255,0.3) !important;
    border-radius:12px !important;
    font-family:'JetBrains Mono',monospace !important;
    font-weight:600 !important; font-size:0.88rem !important;
    letter-spacing:0.12em !important; padding:0.8rem 2.5rem !important;
    transition:all 0.2s ease !important;
    text-shadow:0 0 15px var(--cyan) !important;
    box-shadow:0 0 25px rgba(0,255,255,0.06) !important;
}
.stButton > button:hover {
    background:linear-gradient(135deg,rgba(0,255,255,0.18),rgba(138,43,226,0.18)) !important;
    border-color:var(--cyan) !important;
    box-shadow:0 0 40px rgba(0,255,255,0.2),0 0 80px rgba(138,43,226,0.1) !important;
    transform:translateY(-2px) !important;
}

textarea {
    background:transparent !important; border:none !important;
    color:rgba(255,255,255,0.82) !important;
    font-family:'JetBrains Mono',monospace !important;
    font-size:0.95rem !important; line-height:1.85 !important;
    caret-color:var(--cyan) !important;
}

div[data-testid="stCodeBlock"] { border:1px solid var(--border2) !important; border-radius:14px !important; background:rgba(0,0,0,0.6) !important; }
div[data-testid="stSpinner"] p { color:var(--cyan) !important; font-family:'JetBrains Mono',monospace !important; font-size:0.82rem !important; letter-spacing:0.08em !important; text-shadow:0 0 12px var(--cyan) !important; }
</style>

<div class='scanline'></div>

<svg class='neural-bg' xmlns='http://www.w3.org/2000/svg'>
  <defs>
    <radialGradient id='ng1' cx='50%' cy='50%' r='50%'><stop offset='0%' stop-color='#00ffff' stop-opacity='0.7'/><stop offset='100%' stop-color='#00ffff' stop-opacity='0'/></radialGradient>
    <radialGradient id='ng2' cx='50%' cy='50%' r='50%'><stop offset='0%' stop-color='#8a2be2' stop-opacity='0.7'/><stop offset='100%' stop-color='#8a2be2' stop-opacity='0'/></radialGradient>
  </defs>
  <g opacity='0.35'>
    <line x1='8%' y1='15%' x2='28%' y2='42%' stroke='url(#ng1)' stroke-width='0.6'><animate attributeName='opacity' values='0.2;0.9;0.2' dur='4s' repeatCount='indefinite'/></line>
    <line x1='28%' y1='42%' x2='58%' y2='22%' stroke='url(#ng2)' stroke-width='0.6'><animate attributeName='opacity' values='0.9;0.2;0.9' dur='3s' repeatCount='indefinite'/></line>
    <line x1='58%' y1='22%' x2='82%' y2='58%' stroke='url(#ng1)' stroke-width='0.6'><animate attributeName='opacity' values='0.3;1;0.3' dur='5s' repeatCount='indefinite'/></line>
    <line x1='82%' y1='58%' x2='68%' y2='88%' stroke='url(#ng2)' stroke-width='0.6'><animate attributeName='opacity' values='0.7;0.2;0.7' dur='4s' repeatCount='indefinite'/></line>
    <line x1='12%' y1='72%' x2='42%' y2='82%' stroke='url(#ng1)' stroke-width='0.6'><animate attributeName='opacity' values='0.4;1;0.4' dur='6s' repeatCount='indefinite'/></line>
    <line x1='42%' y1='82%' x2='58%' y2='22%' stroke='url(#ng2)' stroke-width='0.6'><animate attributeName='opacity' values='0.2;0.8;0.2' dur='3.5s' repeatCount='indefinite'/></line>
    <circle cx='8%' cy='15%' r='4' fill='#00ffff'><animate attributeName='opacity' values='0.3;1;0.3' dur='4s' repeatCount='indefinite'/></circle>
    <circle cx='28%' cy='42%' r='4' fill='#8a2be2'><animate attributeName='opacity' values='1;0.3;1' dur='3s' repeatCount='indefinite'/></circle>
    <circle cx='58%' cy='22%' r='4' fill='#00ffff'><animate attributeName='opacity' values='0.5;1;0.5' dur='5s' repeatCount='indefinite'/></circle>
    <circle cx='82%' cy='58%' r='4' fill='#8a2be2'><animate attributeName='opacity' values='0.3;1;0.3' dur='4s' repeatCount='indefinite'/></circle>
    <circle cx='12%' cy='72%' r='4' fill='#00ffff'><animate attributeName='opacity' values='0.9;0.2;0.9' dur='6s' repeatCount='indefinite'/></circle>
    <circle cx='42%' cy='82%' r='4' fill='#8a2be2'><animate attributeName='opacity' values='0.4;1;0.4' dur='3.5s' repeatCount='indefinite'/></circle>
    <circle cx='68%' cy='88%' r='4' fill='#00ffff'><animate attributeName='opacity' values='0.6;0.2;0.6' dur='5s' repeatCount='indefinite'/></circle>
  </g>
</svg>
""", unsafe_allow_html=True)


def format_output(text: str) -> str:
    """Convert markdown-style text to styled HTML."""
    import re
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em style="color:rgba(255,255,255,0.75)">\1</em>', text)
    text = re.sub(r'^### (.+)$', r'<div style="font-family:Inter,sans-serif;font-size:1rem;font-weight:700;color:#00ffff;margin:1.5rem 0 0.6rem;letter-spacing:-0.01em;">\1</div>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<div style="font-family:Inter,sans-serif;font-size:1.1rem;font-weight:700;color:#fff;margin:1.75rem 0 0.75rem;">\1</div>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$', r'<div style="font-family:Inter,sans-serif;font-size:1.2rem;font-weight:800;color:#fff;margin:2rem 0 1rem;">\1</div>', text, flags=re.MULTILINE)
    lines = text.split('\n')
    result = []
    for line in lines:
        stripped = line.strip()
        if re.match(r'^\d+\.\s', stripped):
            num, rest = re.match(r'^(\d+)\.\s(.+)$', stripped).groups()
            result.append(f"<div class='r-list-item'><div class='r-list-num'>{num}.</div><div class='r-list-text'>{rest}</div></div>")
        elif stripped.startswith('- ') or stripped.startswith('* '):
            rest = stripped[2:]
            result.append(f"<div style='display:flex;gap:0.75rem;padding:0.3rem 0;align-items:flex-start;'><span style='color:#00ffff;font-size:0.6rem;margin-top:6px;'>◈</span><span style='font-family:Inter,sans-serif;font-size:1rem;color:rgba(255,255,255,0.65);line-height:1.7;'>{rest}</span></div>")
        elif stripped == '---' or stripped == '===':
            result.append("<hr style='border:none;border-top:1px solid rgba(0,255,255,0.08);margin:1.25rem 0;'>")
        elif stripped == '':
            result.append("<div style='height:0.5rem;'></div>")
        else:
            result.append(f"<div style='font-family:Inter,sans-serif;font-size:1rem;color:rgba(255,255,255,0.65);line-height:1.85;margin:0.15rem 0;'>{line}</div>")
    return '\n'.join(result)


@st.cache_resource
def get_graph():
    return build_graph()


checkpointer = Checkpointer()

# SIDEBAR
with st.sidebar:
    st.markdown("""
    <div class='sb-head'>
        <div class='sb-sys'>// SYSTEM ACTIVE</div>
        <div class='sb-logo'><span class='l1'>Agent</span><span class='l2'>Flow</span></div>
        <div class='sb-sub'>multi-agent orchestration engine</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='sb-sec'>Agent Pipeline</div>", unsafe_allow_html=True)
    for code, name, role in [
        ("S1", "Supervisor", "Task decomposition & routing"),
        ("R2", "Researcher", "Live web search & synthesis"),
        ("E3", "Executor", "Code generation & sandbox"),
        ("V4", "Reviewer", "QA & verified output")
    ]:
        st.markdown(f"""
        <div class='ag-row'>
            <div class='ag-ic'>{code}</div>
            <div><div class='ag-name'>{name}</div><div class='ag-role'>{role}</div></div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div class='sb-sec'>Run History</div>", unsafe_allow_html=True)
    runs = checkpointer.list_runs()
    if runs:
        for run in runs[:5]:
            st.markdown(f"""
            <div class='run-card'>
                <div class='run-id'>{run['id'][:20]}...</div>
                <div class='run-ts'>{run['created_at'][:16]}</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown("<div style='font-family:JetBrains Mono,monospace;font-size:0.68rem;color:rgba(0,255,255,0.18);font-style:italic;'>awaiting first run...</div>", unsafe_allow_html=True)

    st.markdown("<div class='sb-sec'>Technology Stack</div>", unsafe_allow_html=True)
    for s in ["LLaMA 3.3 70B // Groq", "LangGraph // DAG Engine", "Tavily // Web Search", "SQLite // Persistence", "AST // Sandbox"]:
        st.markdown(f"<div class='st-row'><div class='st-d'></div><div class='st-t'>{s}</div></div>", unsafe_allow_html=True)

# STATUS BAR
st.markdown(f"""
<div class='status-bar'>
    <div class='s-dot'><div class='dot green'></div> SYSTEM ONLINE</div>
    <div>// AGENTFLOW v1.0.0</div>
    <div>MODEL: LLAMA-3.3-70B</div>
    <div>INFERENCE: GROQ LPU</div>
    <div>AGENTS: 4 ACTIVE</div>
    <div>{datetime.datetime.now().strftime('%Y-%m-%d  %H:%M:%S')}</div>
</div>
""", unsafe_allow_html=True)

# HERO
st.markdown("""
<div class='hero'>
    <div class='hero-eyebrow'>Advanced Intelligence Orchestration System</div>
    <div class='hero-title'>
        <span class='t1'>Agent</span>
        <span class='t2'>Flow</span>
    </div>
    <div class='hero-version'>v1.0.0 // BUILD 2026.03 // CYBER-NOIR EDITION</div>
    <div class='hero-desc'>
        A stateful multi-agent orchestration engine. Input any task — the DAG decomposes it,
        four specialized agents research, execute sandboxed code, and deliver a verified answer.
        <span class='live-pill'><span class='dot green'></span>ALL SYSTEMS NOMINAL</span>
    </div>
</div>
""", unsafe_allow_html=True)

# PIPELINE
st.markdown("""
<div class='pipeline'>
    <div class='p-node'><div class='p-bar'></div>
        <div class='p-num'>01 // SUPERVISOR</div>
        <div class='p-name'>Orchestrate</div>
        <div class='p-role'>Decomposes task, routes to agents via typed DAG</div>
    </div>
    <div class='p-node'><div class='p-bar'></div>
        <div class='p-num'>02 // RESEARCHER</div>
        <div class='p-name'>Research</div>
        <div class='p-role'>Live web intelligence via Tavily Search API</div>
    </div>
    <div class='p-node'><div class='p-bar'></div>
        <div class='p-num'>03 // EXECUTOR</div>
        <div class='p-name'>Execute</div>
        <div class='p-role'>Writes & runs sandboxed Python via AST validator</div>
    </div>
    <div class='p-node'><div class='p-bar'></div>
        <div class='p-num'>04 // REVIEWER</div>
        <div class='p-name'>Verify</div>
        <div class='p-role'>QA, hallucination filter, verified final output</div>
    </div>
</div>
""", unsafe_allow_html=True)

# TERMINAL INPUT
st.markdown("""
<div class='terminal-wrap'>
    <div class='terminal-top'>
        <div class='td r'></div><div class='td y'></div><div class='td g'></div>
        <div class='t-label'>agentflow@system:~$ task_input</div>
    </div>
    <div class='t-body'>
        <div class='t-prompt'>ENTER TASK DIRECTIVE</div>
    </div>
</div>
""", unsafe_allow_html=True)

task = st.text_area(
    "",
    placeholder="Example: Research the top 5 AI companies by funding in 2026, compare their tech stacks, and compute their average funding using Python.",
    height=130,
    label_visibility="collapsed"
)

col1, col2 = st.columns([1, 9])
with col1:
    run_btn = st.button("EXECUTE")

# EXECUTION
if run_btn and task.strip():
    run_id = str(uuid.uuid4())[:8]
    graph = get_graph()

    initial_state = AgentState(
        task=task, plan="", research="", code="", code_output="",
        review="", final_answer="", error="", iteration=0,
        messages=[], next="supervisor", hitl_required=False, approved=True,
    )

    with st.spinner("// PIPELINE ACTIVE  —  SUPERVISOR  ->  RESEARCHER  ->  EXECUTOR  ->  REVIEWER"):
        try:
            final_state = graph.invoke(initial_state)
            checkpointer.save(run_id, {k: v for k, v in final_state.items() if k != "messages"})

            st.markdown(f"""
            <div class='exec-log'>
                <span>// EXECUTION COMPLETE</span>
                RUN_ID: {run_id} &nbsp;&nbsp; AGENTS: 4 &nbsp;&nbsp; STATUS: <span>SUCCESS</span>
            </div>""", unsafe_allow_html=True)

            if final_state.get("plan"):
                st.markdown(f"""
                <div class='r-card'>
                    <div class='r-top'>
                        <div class='r-badge'>01 — Supervisor — Execution Plan</div>
                        <div class='r-status'>PLAN GENERATED</div>
                    </div>
                    <div class='r-content'>{format_output(final_state['plan'])}</div>
                </div>""", unsafe_allow_html=True)

            if final_state.get("research"):
                st.markdown(f"""
                <div class='r-card'>
                    <div class='r-top'>
                        <div class='r-badge'>02 — Researcher — Intelligence Report</div>
                        <div class='r-status'>WEB SEARCH COMPLETE</div>
                    </div>
                    <div class='r-content'>{format_output(final_state['research'][:3000])}</div>
                </div>""", unsafe_allow_html=True)

            if final_state.get("code"):
                st.markdown("""
                <div class='r-card'>
                    <div class='r-top'>
                        <div class='r-badge'>03 — Executor — Generated Code</div>
                        <div class='r-status'>AST VALIDATED</div>
                    </div>
                </div>""", unsafe_allow_html=True)
                st.code(final_state["code"], language="python")

            if final_state.get("code_output"):
                st.markdown(f"""
                <div class='r-card'>
                    <div class='r-top'>
                        <div class='r-badge'>03 — Executor — Runtime Output</div>
                        <div class='r-status'>SANDBOXED EXECUTION</div>
                    </div>
                    <div class='r-content' style='font-family:JetBrains Mono,monospace;font-size:0.9rem;'>
                        {final_state['code_output'].replace(chr(10), '<br>')}
                    </div>
                </div>""", unsafe_allow_html=True)

            if final_state.get("final_answer"):
                st.markdown(f"""
                <div class='final-wrap'>
                    <div class='fg1'></div><div class='fg2'></div>
                    <div class='final-header'>04 — Reviewer — Verified Final Output</div>
                    <div class='final-content'>{format_output(final_state['final_answer'])}</div>
                </div>""", unsafe_allow_html=True)

            if final_state.get("error"):
                st.error(f"// ERROR: {final_state['error']}")

        except Exception as e:
            st.error(f"// PIPELINE ERROR: {str(e)}")

elif run_btn:
    st.warning("// INPUT REQUIRED: Enter a task directive before executing.")
