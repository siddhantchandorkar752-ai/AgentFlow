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
    --obsidian3: #0c1018;
    --cyan: #00ffff;
    --cyan2: rgba(0,255,255,0.6);
    --cyan3: rgba(0,255,255,0.15);
    --cyan4: rgba(0,255,255,0.05);
    --purple: #8a2be2;
    --purple2: rgba(138,43,226,0.6);
    --purple3: rgba(138,43,226,0.15);
    --glass: rgba(255,255,255,0.03);
    --glass2: rgba(255,255,255,0.06);
    --border: rgba(0,255,255,0.08);
    --border2: rgba(0,255,255,0.2);
    --text: rgba(0,255,255,0.7);
    --text2: rgba(255,255,255,0.85);
    --text3: rgba(0,255,255,0.35);
    --red: #ff2d55;
    --green: #00ff88;
    --yellow: #ffcc00;
}
 
*, *::before, *::after { box-sizing: border-box; }
html, body { background: var(--obsidian) !important; font-family: 'JetBrains Mono', monospace !important; }
.stApp { background: var(--obsidian) !important; font-family: 'JetBrains Mono', monospace !important; }
 
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(0,255,255,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,255,255,0.04) 1px, transparent 1px);
    background-size: 50px 50px;
    animation: gridMove 20s linear infinite;
    pointer-events: none;
    z-index: 0;
}
 
@keyframes gridMove {
    0% { background-position: 0 0; }
    100% { background-position: 50px 50px; }
}
 
.stApp::after {
    content: '';
    position: fixed;
    top: -30vh; right: -20vw;
    width: 80vw; height: 80vh;
    background: radial-gradient(ellipse, rgba(138,43,226,0.06) 0%, transparent 65%);
    pointer-events: none;
    z-index: 0;
    animation: orbPulse 8s ease-in-out infinite;
}
 
@keyframes orbPulse {
    0%, 100% { opacity: 0.6; transform: scale(1); }
    50% { opacity: 1; transform: scale(1.1); }
}
 
section[data-testid="stSidebar"] {
    background: rgba(5,5,5,0.95) !important;
    border-right: 1px solid var(--border2) !important;
    backdrop-filter: blur(40px) !important;
}
 
section[data-testid="stSidebar"] > div {
    padding: 1.5rem 1.25rem !important;
    position: relative;
    z-index: 1;
}
 
.block-container {
    padding: 2rem 3rem 4rem !important;
    position: relative;
    z-index: 1;
    max-width: 100% !important;
}
 
.scanline {
    position: fixed;
    inset: 0;
    background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(0,255,255,0.008) 2px,
        rgba(0,255,255,0.008) 4px
    );
    pointer-events: none;
    z-index: 9999;
}
 
.neural-bg {
    position: fixed;
    top: 0; left: 0;
    width: 100vw; height: 100vh;
    pointer-events: none;
    z-index: 0;
    opacity: 0.4;
}
 
.status-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.6rem 1.5rem;
    background: rgba(0,255,255,0.03);
    border: 1px solid var(--border);
    border-radius: 8px;
    margin-bottom: 2.5rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    color: var(--text3);
    letter-spacing: 0.1em;
}
 
.status-dot { display: inline-flex; align-items: center; gap: 0.5rem; }
.dot { width: 5px; height: 5px; border-radius: 50%; }
.dot.green { background: var(--green); box-shadow: 0 0 8px var(--green); animation: dotBlink 2s ease infinite; }
.dot.cyan { background: var(--cyan); box-shadow: 0 0 8px var(--cyan); }
@keyframes dotBlink { 0%,100%{opacity:1} 50%{opacity:0.3} }
 
.hero { padding: 2.5rem 0 3rem; margin-bottom: 2.5rem; position: relative; }
 
.hero-sys {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.4em;
    color: var(--cyan);
    text-transform: uppercase;
    margin-bottom: 1rem;
    opacity: 0.7;
}
 
.hero-title {
    font-family: 'Inter', sans-serif;
    font-size: clamp(4rem, 9vw, 7.5rem);
    font-weight: 900;
    line-height: 0.88;
    letter-spacing: -0.04em;
    margin-bottom: 0.5rem;
}
 
.hero-title .t1 { color: #fff; }
.hero-title .t2 {
    background: linear-gradient(90deg, var(--cyan), var(--purple));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    display: block;
}
 
.hero-version {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: var(--text3);
    letter-spacing: 0.2em;
    margin-bottom: 1.5rem;
}
 
.hero-desc {
    font-family: 'Inter', sans-serif;
    font-size: 1.05rem;
    color: rgba(255,255,255,0.4);
    line-height: 1.7;
    max-width: 600px;
    font-weight: 300;
}
 
.online-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.3rem 1rem;
    border: 1px solid rgba(0,255,136,0.3);
    border-radius: 100px;
    background: rgba(0,255,136,0.06);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.58rem;
    color: var(--green);
    letter-spacing: 0.15em;
    margin-left: 1rem;
    vertical-align: middle;
    text-shadow: 0 0 10px var(--green);
}
 
.pipeline {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1px;
    background: rgba(0,255,255,0.08);
    border: 1px solid var(--border2);
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 2.5rem;
    position: relative;
}
 
.pipeline::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--cyan), var(--purple), transparent);
    animation: scanLine 3s ease infinite;
}
 
@keyframes scanLine {
    0% { transform: scaleX(0); transform-origin: left; }
    50% { transform: scaleX(1); transform-origin: left; }
    51% { transform: scaleX(1); transform-origin: right; }
    100% { transform: scaleX(0); transform-origin: right; }
}
 
.p-node {
    background: var(--obsidian2);
    padding: 1.5rem 1.25rem;
    position: relative;
    transition: background 0.3s;
}
 
.p-node:hover { background: rgba(0,255,255,0.04); }
 
.p-idx {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.55rem;
    color: var(--text3);
    letter-spacing: 0.2em;
    margin-bottom: 0.6rem;
}
 
.p-name {
    font-family: 'Inter', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: #fff;
    margin-bottom: 0.3rem;
    letter-spacing: -0.01em;
}
 
.p-role {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: var(--text3);
    line-height: 1.5;
}
 
.p-accent {
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, var(--cyan), var(--purple));
    opacity: 0;
    transition: opacity 0.3s;
}
 
.p-node:hover .p-accent { opacity: 1; }
 
.terminal-wrap {
    background: rgba(0,255,255,0.02);
    border: 1px solid var(--border2);
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 2rem;
    backdrop-filter: blur(30px);
}
 
.terminal-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.85rem 1.25rem;
    background: rgba(0,255,255,0.04);
    border-bottom: 1px solid var(--border);
}
 
.t-dot { width: 10px; height: 10px; border-radius: 50%; }
.t-dot.r { background: var(--red); }
.t-dot.y { background: var(--yellow); }
.t-dot.g { background: var(--green); }
 
.t-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: var(--text3);
    margin-left: auto;
    letter-spacing: 0.1em;
}
 
.terminal-body { padding: 1.5rem 1.5rem 0.5rem; }
 
.t-prompt {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: var(--cyan);
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
 
.t-prompt::before { content: '>'; color: var(--purple); font-weight: 700; }
 
.r-card {
    background: var(--glass);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 2rem;
    margin-bottom: 1.25rem;
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(30px);
    animation: cardIn 0.4s ease forwards;
}
 
@keyframes cardIn {
    from { opacity: 0; transform: translateY(16px); }
    to { opacity: 1; transform: translateY(0); }
}
 
.r-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--cyan), transparent);
}
 
.r-card::after {
    content: '';
    position: absolute;
    top: 0; right: 0;
    width: 200px; height: 200px;
    background: radial-gradient(circle, var(--cyan4) 0%, transparent 70%);
    pointer-events: none;
}
 
.r-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1.25rem;
}
 
.r-tag {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.58rem;
    font-weight: 600;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--cyan);
    background: var(--cyan4);
    border: 1px solid rgba(0,255,255,0.15);
    border-radius: 6px;
    padding: 0.3rem 0.8rem;
}
 
.r-ts { font-family: 'JetBrains Mono', monospace; font-size: 0.58rem; color: var(--text3); }
 
.r-body {
    font-family: 'Inter', sans-serif;
    font-size: 0.95rem;
    color: rgba(255,255,255,0.55);
    line-height: 1.85;
    font-weight: 300;
}
 
.r-body strong, .r-body b { color: rgba(255,255,255,0.9); font-weight: 600; }
 
.final-wrap {
    background: linear-gradient(135deg, rgba(0,255,255,0.04), rgba(138,43,226,0.04));
    border: 1px solid rgba(0,255,255,0.25);
    border-radius: 20px;
    padding: 3rem;
    margin-top: 2rem;
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(40px);
}
 
.final-wrap::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--cyan), var(--purple), var(--cyan));
    background-size: 200% 100%;
    animation: gradientSlide 3s linear infinite;
}
 
@keyframes gradientSlide {
    0% { background-position: 0% 0%; }
    100% { background-position: 200% 0%; }
}
 
.final-glow1 {
    position: absolute;
    bottom: -100px; left: -100px;
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(138,43,226,0.08) 0%, transparent 65%);
    pointer-events: none;
}
 
.final-glow2 {
    position: absolute;
    top: -100px; right: -100px;
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(0,255,255,0.06) 0%, transparent 65%);
    pointer-events: none;
}
 
.final-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: var(--cyan);
    margin-bottom: 2rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    text-shadow: 0 0 20px var(--cyan);
}
 
.final-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(0,255,255,0.3), transparent);
}
 
.final-body {
    font-family: 'Inter', sans-serif;
    font-size: 1.05rem;
    color: rgba(255,255,255,0.75);
    line-height: 2;
    font-weight: 300;
}
 
.sb-logo-wrap { padding: 0.5rem 0 2rem; border-bottom: 1px solid var(--border); margin-bottom: 1.5rem; }
.sb-sys { font-family: 'JetBrains Mono', monospace; font-size: 0.55rem; letter-spacing: 0.3em; color: var(--cyan); opacity: 0.5; margin-bottom: 0.5rem; }
.sb-logo { font-family: 'Inter', sans-serif; font-size: 1.6rem; font-weight: 900; letter-spacing: -0.03em; line-height: 1; }
.sb-logo .l1 { color: #fff; }
.sb-logo .l2 { background: linear-gradient(90deg, var(--cyan), var(--purple)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.sb-sub { font-family: 'JetBrains Mono', monospace; font-size: 0.58rem; color: var(--text3); letter-spacing: 0.1em; margin-top: 0.4rem; }
 
.sb-sec {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.52rem;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: var(--text3);
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border);
    margin: 1.5rem 0 0.75rem;
}
 
.ag-row { display: flex; align-items: center; gap: 0.75rem; padding: 0.6rem 0; border-bottom: 1px solid rgba(255,255,255,0.02); }
 
.ag-icon {
    width: 30px; height: 30px;
    border-radius: 8px;
    background: rgba(0,255,255,0.06);
    border: 1px solid rgba(0,255,255,0.12);
    display: flex; align-items: center; justify-content: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.58rem; font-weight: 700;
    color: var(--cyan); flex-shrink: 0;
    text-shadow: 0 0 8px var(--cyan);
}
 
.ag-name { font-family: 'Inter', sans-serif; font-size: 0.82rem; font-weight: 600; color: rgba(255,255,255,0.75); }
.ag-role { font-family: 'JetBrains Mono', monospace; font-size: 0.58rem; color: var(--text3); margin-top: 0.1rem; }
 
.run-card { background: rgba(0,255,255,0.02); border: 1px solid var(--border); border-radius: 8px; padding: 0.6rem 0.75rem; margin-bottom: 0.4rem; }
.run-id { font-family: 'JetBrains Mono', monospace; font-size: 0.6rem; color: var(--cyan); opacity: 0.7; }
.run-ts { font-family: 'JetBrains Mono', monospace; font-size: 0.55rem; color: var(--text3); margin-top: 0.15rem; }
 
.stack-row { display: flex; align-items: center; gap: 0.6rem; padding: 0.4rem 0; border-bottom: 1px solid rgba(255,255,255,0.02); }
.s-diamond { width: 5px; height: 5px; background: transparent; border: 1px solid var(--cyan); transform: rotate(45deg); flex-shrink: 0; opacity: 0.5; }
.s-text { font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: var(--text3); }
 
.stButton > button {
    background: linear-gradient(135deg, rgba(0,255,255,0.1), rgba(138,43,226,0.1)) !important;
    color: var(--cyan) !important;
    border: 1px solid rgba(0,255,255,0.3) !important;
    border-radius: 10px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 500 !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.1em !important;
    padding: 0.65rem 2rem !important;
    transition: all 0.2s ease !important;
    text-shadow: 0 0 15px var(--cyan) !important;
    box-shadow: 0 0 20px rgba(0,255,255,0.08), inset 0 1px 0 rgba(0,255,255,0.1) !important;
}
 
.stButton > button:hover {
    background: linear-gradient(135deg, rgba(0,255,255,0.18), rgba(138,43,226,0.18)) !important;
    border-color: var(--cyan) !important;
    box-shadow: 0 0 30px rgba(0,255,255,0.2), 0 0 60px rgba(138,43,226,0.1) !important;
    transform: translateY(-1px) !important;
}
 
textarea {
    background: transparent !important;
    border: none !important;
    color: rgba(255,255,255,0.8) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.88rem !important;
    line-height: 1.8 !important;
    caret-color: var(--cyan) !important;
}
 
div[data-testid="stCodeBlock"] {
    border: 1px solid var(--border2) !important;
    border-radius: 12px !important;
    background: rgba(0,0,0,0.5) !important;
}
 
div[data-testid="stSpinner"] p {
    color: var(--cyan) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.1em !important;
    text-shadow: 0 0 10px var(--cyan) !important;
}
</style>
 
<div class='scanline'></div>
 
<svg class='neural-bg' xmlns='http://www.w3.org/2000/svg'>
    <defs>
        <radialGradient id='ng1' cx='50%' cy='50%' r='50%'>
            <stop offset='0%' stop-color='#00ffff' stop-opacity='0.6'/>
            <stop offset='100%' stop-color='#00ffff' stop-opacity='0'/>
        </radialGradient>
        <radialGradient id='ng2' cx='50%' cy='50%' r='50%'>
            <stop offset='0%' stop-color='#8a2be2' stop-opacity='0.6'/>
            <stop offset='100%' stop-color='#8a2be2' stop-opacity='0'/>
        </radialGradient>
    </defs>
    <g opacity='0.3'>
        <line x1='10%' y1='20%' x2='30%' y2='45%' stroke='url(#ng1)' stroke-width='0.5'><animate attributeName='opacity' values='0.2;0.8;0.2' dur='4s' repeatCount='indefinite'/></line>
        <line x1='30%' y1='45%' x2='60%' y2='25%' stroke='url(#ng2)' stroke-width='0.5'><animate attributeName='opacity' values='0.8;0.2;0.8' dur='3s' repeatCount='indefinite'/></line>
        <line x1='60%' y1='25%' x2='85%' y2='60%' stroke='url(#ng1)' stroke-width='0.5'><animate attributeName='opacity' values='0.3;0.9;0.3' dur='5s' repeatCount='indefinite'/></line>
        <line x1='85%' y1='60%' x2='70%' y2='85%' stroke='url(#ng2)' stroke-width='0.5'><animate attributeName='opacity' values='0.6;0.2;0.6' dur='4s' repeatCount='indefinite'/></line>
        <line x1='15%' y1='70%' x2='45%' y2='80%' stroke='url(#ng1)' stroke-width='0.5'><animate attributeName='opacity' values='0.4;0.9;0.4' dur='6s' repeatCount='indefinite'/></line>
        <line x1='45%' y1='80%' x2='60%' y2='25%' stroke='url(#ng2)' stroke-width='0.5'><animate attributeName='opacity' values='0.2;0.7;0.2' dur='3.5s' repeatCount='indefinite'/></line>
        <circle cx='10%' cy='20%' r='3' fill='#00ffff'><animate attributeName='opacity' values='0.3;1;0.3' dur='4s' repeatCount='indefinite'/></circle>
        <circle cx='30%' cy='45%' r='3' fill='#8a2be2'><animate attributeName='opacity' values='1;0.3;1' dur='3s' repeatCount='indefinite'/></circle>
        <circle cx='60%' cy='25%' r='3' fill='#00ffff'><animate attributeName='opacity' values='0.5;1;0.5' dur='5s' repeatCount='indefinite'/></circle>
        <circle cx='85%' cy='60%' r='3' fill='#8a2be2'><animate attributeName='opacity' values='0.3;0.9;0.3' dur='4s' repeatCount='indefinite'/></circle>
        <circle cx='15%' cy='70%' r='3' fill='#00ffff'><animate attributeName='opacity' values='0.8;0.2;0.8' dur='6s' repeatCount='indefinite'/></circle>
        <circle cx='45%' cy='80%' r='3' fill='#8a2be2'><animate attributeName='opacity' values='0.4;1;0.4' dur='3.5s' repeatCount='indefinite'/></circle>
        <circle cx='70%' cy='85%' r='3' fill='#00ffff'><animate attributeName='opacity' values='0.6;0.2;0.6' dur='5s' repeatCount='indefinite'/></circle>
    </g>
</svg>
""", unsafe_allow_html=True)
 
 
@st.cache_resource
def get_graph():
    return build_graph()
 
 
checkpointer = Checkpointer()
 
# SIDEBAR
with st.sidebar:
    st.markdown("""
    <div class='sb-logo-wrap'>
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
            <div class='ag-icon'>{code}</div>
            <div>
                <div class='ag-name'>{name}</div>
                <div class='ag-role'>{role}</div>
            </div>
        </div>""", unsafe_allow_html=True)
 
    st.markdown("<div class='sb-sec'>Run History</div>", unsafe_allow_html=True)
    runs = checkpointer.list_runs()
    if runs:
        for run in runs[:5]:
            st.markdown(f"""
            <div class='run-card'>
                <div class='run-id'>{run['id'][:22]}...</div>
                <div class='run-ts'>{run['created_at'][:16]}</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown("<div style='font-family:JetBrains Mono,monospace;font-size:0.62rem;color:rgba(0,255,255,0.2);font-style:italic;'>awaiting first run...</div>", unsafe_allow_html=True)
 
    st.markdown("<div class='sb-sec'>Technology Stack</div>", unsafe_allow_html=True)
    for s in [
        "LLaMA 3.3 70B // Groq",
        "LangGraph // DAG Engine",
        "Tavily // Web Search",
        "SQLite // State Persistence",
        "AST // Sandbox Execution"
    ]:
        st.markdown(f"<div class='stack-row'><div class='s-diamond'></div><div class='s-text'>{s}</div></div>", unsafe_allow_html=True)
 
# STATUS BAR
st.markdown(f"""
<div class='status-bar'>
    <div class='status-dot'><div class='dot green'></div> SYSTEM ONLINE</div>
    <div>// AGENTFLOW v1.0.0</div>
    <div>LLM: LLAMA-3.3-70B</div>
    <div>AGENTS: 4 ACTIVE</div>
    <div>{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
</div>
""", unsafe_allow_html=True)
 
# HERO
st.markdown("""
<div class='hero'>
    <div class='hero-sys'>// ADVANCED INTELLIGENCE ORCHESTRATION SYSTEM</div>
    <div class='hero-title'>
        <span class='t1'>Agent</span>
        <span class='t2'>Flow</span>
    </div>
    <div class='hero-version'>v1.0.0 // BUILD 2026.03 // CYBER-NOIR EDITION</div>
    <div class='hero-desc'>
        A stateful multi-agent orchestration engine. Input any task — the DAG decomposes it,
        agents research, code, and verify autonomously.
        <span class='online-pill'><span class='dot green'></span>ALL SYSTEMS NOMINAL</span>
    </div>
</div>
""", unsafe_allow_html=True)
 
# PIPELINE
st.markdown("""
<div class='pipeline'>
    <div class='p-node'><div class='p-accent'></div>
        <div class='p-idx'>01 // SUPERVISOR</div>
        <div class='p-name'>Orchestrate</div>
        <div class='p-role'>Decomposes task into subtasks, routes to agents via DAG</div>
    </div>
    <div class='p-node'><div class='p-accent'></div>
        <div class='p-idx'>02 // RESEARCHER</div>
        <div class='p-name'>Research</div>
        <div class='p-role'>Live web intelligence via Tavily Search API</div>
    </div>
    <div class='p-node'><div class='p-accent'></div>
        <div class='p-idx'>03 // EXECUTOR</div>
        <div class='p-name'>Execute</div>
        <div class='p-role'>Writes & runs sandboxed Python via AST validator</div>
    </div>
    <div class='p-node'><div class='p-accent'></div>
        <div class='p-idx'>04 // REVIEWER</div>
        <div class='p-name'>Verify</div>
        <div class='p-role'>QA check, hallucination filter, final verified output</div>
    </div>
</div>
""", unsafe_allow_html=True)
 
# TERMINAL INPUT
st.markdown("""
<div class='terminal-wrap'>
    <div class='terminal-header'>
        <div class='t-dot r'></div>
        <div class='t-dot y'></div>
        <div class='t-dot g'></div>
        <div class='t-title'>agentflow@system:~$ task_input</div>
    </div>
    <div class='terminal-body'>
        <div class='t-prompt'>ENTER TASK DIRECTIVE</div>
    </div>
</div>
""", unsafe_allow_html=True)
 
task = st.text_area(
    "",
    placeholder="Example: Research the top AI breakthroughs in 2026, analyze key patterns, and write a Python script to compute trend scores...",
    height=120,
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
 
    with st.spinner("// PIPELINE ACTIVE — SUPERVISOR -> RESEARCHER -> EXECUTOR -> REVIEWER"):
        try:
            final_state = graph.invoke(initial_state)
            checkpointer.save(run_id, {k: v for k, v in final_state.items() if k != "messages"})
 
            st.markdown(f"""
            <div style='font-family:JetBrains Mono,monospace;font-size:0.6rem;color:rgba(0,255,255,0.3);
                 margin:2rem 0 1.5rem;padding:0.75rem 1rem;background:rgba(0,255,255,0.02);
                 border:1px solid rgba(0,255,255,0.08);border-radius:8px;'>
                // EXECUTION COMPLETE &nbsp; RUN_ID: {run_id} &nbsp;
                AGENTS: 4 &nbsp; STATUS: SUCCESS
            </div>""", unsafe_allow_html=True)
 
            if final_state.get("plan"):
                st.markdown(f"""
                <div class='r-card'>
                    <div class='r-header'>
                        <div class='r-tag'>01 - Supervisor - Execution Plan</div>
                        <div class='r-ts'>PLAN GENERATED</div>
                    </div>
                    <div class='r-body'>{final_state['plan']}</div>
                </div>""", unsafe_allow_html=True)
 
            if final_state.get("research"):
                st.markdown(f"""
                <div class='r-card'>
                    <div class='r-header'>
                        <div class='r-tag'>02 - Researcher - Intelligence Report</div>
                        <div class='r-ts'>WEB SEARCH COMPLETE</div>
                    </div>
                    <div class='r-body'>{final_state['research'][:2500].replace(chr(10), '<br>')}</div>
                </div>""", unsafe_allow_html=True)
 
            if final_state.get("code"):
                st.markdown("""
                <div class='r-card'>
                    <div class='r-header'>
                        <div class='r-tag'>03 - Executor - Generated Code</div>
                        <div class='r-ts'>SANDBOXED</div>
                    </div>
                </div>""", unsafe_allow_html=True)
                st.code(final_state["code"], language="python")
 
            if final_state.get("code_output"):
                st.markdown(f"""
                <div class='r-card'>
                    <div class='r-header'>
                        <div class='r-tag'>03 - Executor - Runtime Output</div>
                        <div class='r-ts'>EXECUTION COMPLETE</div>
                    </div>
                    <div class='r-body' style='font-family:JetBrains Mono,monospace;font-size:0.82rem;'>
                        {final_state['code_output'].replace(chr(10), '<br>')}
                    </div>
                </div>""", unsafe_allow_html=True)
 
            if final_state.get("final_answer"):
                st.markdown(f"""
                <div class='final-wrap'>
                    <div class='final-glow1'></div>
                    <div class='final-glow2'></div>
                    <div class='final-label'>04 - REVIEWER - VERIFIED FINAL OUTPUT</div>
                    <div class='final-body'>{final_state['final_answer'].replace(chr(10), '<br>')}</div>
                </div>""", unsafe_allow_html=True)
 
            if final_state.get("error"):
                st.error(f"// ERROR: {final_state['error']}")
 
        except Exception as e:
            st.error(f"// PIPELINE ERROR: {str(e)}")
 
elif run_btn:
    st.warning("// INPUT REQUIRED: Enter a task directive before executing.")