"""
app.py — AI Interview Preparation Chatbot
Full dark-theme UI: mesh-gradient bg, glassmorphism cards, SVG score rings,
animated chat bubbles, score-bar indicators, SaaS-grade welcome screen.

Run with:
    streamlit run app.py
"""

import html as _html
import os
import random
import time

import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

from evaluator import Evaluator
from interviewer import Interviewer, TOPICS, DIFFICULTIES, ROLES, ROLE_TOPICS, MOCK_TIME_LIMITS
from utils import (
    calculate_stats,
    format_time_remaining,
    get_difficulty_emoji,
    get_performance_badge,
    get_score_color,
    get_topic_emoji,
    should_decrease_difficulty,
    should_increase_difficulty,
    get_score_emoji,
    get_score_label,
)

load_dotenv()

st.set_page_config(
    page_title="InterviewAI — Technical Interview Prep",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

def _e(t) -> str:
    """Escape user/LLM content for safe HTML embedding."""
    return _html.escape(str(t or ""))


# ─────────────────────────────────────────────────────────────────────────────
#  CSS
# ─────────────────────────────────────────────────────────────────────────────

def _load_css() -> None:
    st.markdown(r"""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Reset ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

/* ════════════════════════════════════════════════════════════
   DESIGN TOKENS
════════════════════════════════════════════════════════════ */
:root {
    /* backgrounds */
    --b0: #080b12;
    --b1: #0e1320;
    --b2: #131929;
    --b3: #1a2235;
    --b4: #1f2a3d;
    --glass: rgba(255,255,255,.035);
    --glass-border: rgba(255,255,255,.07);

    /* accents */
    --violet:  #7c3aed;
    --violet2: #9333ea;
    --violet3: #a855f7;
    --indigo:  #6366f1;
    --blue:    #3b82f6;
    --cyan:    #06b6d4;

    /* semantic colours */
    --green:   #22c55e;
    --yellow:  #f59e0b;
    --orange:  #f97316;
    --red:     #ef4444;

    /* text */
    --t1: #f0f4ff;
    --t2: #94a3b8;
    --t3: #64748b;
    --t4: #475569;

    /* borders */
    --bdr: rgba(255,255,255,.08);
    --bdr2: rgba(255,255,255,.04);

    /* glow */
    --glow-v: rgba(124,58,237,.3);
    --glow-b: rgba(59,130,246,.25);

    /* radii */
    --r1: 8px;
    --r2: 14px;
    --r3: 20px;
    --r4: 28px;

    /* shadows */
    --s1: 0 2px 10px rgba(0,0,0,.5);
    --s2: 0 6px 30px rgba(0,0,0,.55);
    --s3: 0 12px 48px rgba(0,0,0,.6);
}

/* ════════════════════════════════════════════════════════════
   MESH-GRADIENT BACKGROUND
════════════════════════════════════════════════════════════ */
.stApp {
    background-color: var(--b0) !important;
    background-image:
        radial-gradient(ellipse 80% 50% at 15% 10%,  rgba(124,58,237,.12) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 85% 80%,  rgba(99,102,241,.10) 0%, transparent 55%),
        radial-gradient(ellipse 50% 60% at 50% 50%,  rgba(6,182,212,.05)  0%, transparent 60%);
    background-attachment: fixed;
}

/* ════════════════════════════════════════════════════════════
   STREAMLIT SHELL CLEANUP
════════════════════════════════════════════════════════════ */
.main .block-container {
    padding: 1rem 2.2rem 6rem !important;
    max-width: 880px !important;
}
#MainMenu, footer, header, .stDeployButton { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }

/* ════════════════════════════════════════════════════════════
   SIDEBAR
════════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: var(--b1) !important;
    border-right: 1px solid var(--bdr) !important;
}
[data-testid="stSidebar"] > div:first-child { padding: .8rem !important; }

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown p {
    font-family: Inter, sans-serif !important;
    font-size: .82rem !important;
    color: var(--t2) !important;
}
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    font-family: Inter, sans-serif !important;
    color: var(--t1) !important;
    font-size: .88rem !important;
    font-weight: 700 !important;
    letter-spacing: .04em !important;
    text-transform: uppercase !important;
}
[data-testid="stSidebar"] hr {
    border-color: var(--bdr2) !important;
    margin: .6rem 0 !important;
}
/* inputs */
[data-testid="stSidebar"] input {
    background: var(--b3) !important;
    border: 1px solid var(--bdr) !important;
    color: var(--t1) !important;
    border-radius: var(--r1) !important;
    font-family: Inter, sans-serif !important;
    font-size: .84rem !important;
}
[data-testid="stSidebar"] input:focus {
    border-color: var(--violet) !important;
    box-shadow: 0 0 0 3px var(--glow-v) !important;
    outline: none !important;
}
/* selectbox */
[data-testid="stSidebar"] .stSelectbox > div > div {
    background: var(--b3) !important;
    border: 1px solid var(--bdr) !important;
    color: var(--t1) !important;
    border-radius: var(--r1) !important;
    font-family: Inter, sans-serif !important;
    font-size: .84rem !important;
}
/* radio */
[data-testid="stSidebar"] .stRadio > div { gap: .3rem !important; }
[data-testid="stSidebar"] .stRadio label {
    font-family: Inter, sans-serif !important;
    font-size: .83rem !important;
}
/* expander */
[data-testid="stSidebar"] [data-testid="stExpander"] {
    background: var(--b3) !important;
    border: 1px solid var(--bdr) !important;
    border-radius: var(--r1) !important;
}

/* ════════════════════════════════════════════════════════════
   BUTTONS  (sidebar + main)
════════════════════════════════════════════════════════════ */
.stButton > button {
    font-family: Inter, sans-serif !important;
    font-size: .84rem !important;
    font-weight: 500 !important;
    border-radius: var(--r2) !important;
    border: 1px solid var(--bdr) !important;
    background: var(--b3) !important;
    color: var(--t2) !important;
    padding: .5rem 1rem !important;
    transition: all .18s ease !important;
    letter-spacing: .01em !important;
}
.stButton > button:hover {
    background: var(--b4) !important;
    border-color: var(--violet) !important;
    color: var(--t1) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px var(--glow-v) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--violet) 0%, var(--violet2) 100%) !important;
    border: none !important;
    color: #fff !important;
    font-weight: 600 !important;
    letter-spacing: .02em !important;
    box-shadow: 0 4px 14px var(--glow-v) !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #6d28d9 0%, #7e22ce 100%) !important;
    box-shadow: 0 6px 22px var(--glow-v) !important;
    transform: translateY(-2px) !important;
}

/* ════════════════════════════════════════════════════════════
   METRICS
════════════════════════════════════════════════════════════ */
[data-testid="stMetric"] {
    background: var(--glass) !important;
    border: 1px solid var(--bdr) !important;
    border-radius: var(--r2) !important;
    padding: .8rem 1rem !important;
    backdrop-filter: blur(8px) !important;
}
[data-testid="stMetric"] label {
    font-family: Inter, sans-serif !important;
    font-size: .7rem !important;
    color: var(--t3) !important;
    text-transform: uppercase !important;
    letter-spacing: .07em !important;
    font-weight: 600 !important;
}
[data-testid="stMetric"] [data-testid="stMetricValue"] {
    font-family: Inter, sans-serif !important;
    font-size: 1.25rem !important;
    font-weight: 800 !important;
    color: var(--t1) !important;
}

/* ════════════════════════════════════════════════════════════
   CHAT SHELL
════════════════════════════════════════════════════════════ */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: .15rem 0 !important;
    align-items: flex-start !important;
}
/* chat message avatar ring */
[data-testid="stChatMessage"] [data-testid="chatAvatarIcon-assistant"] {
    background: linear-gradient(135deg, var(--violet), var(--indigo)) !important;
    border: 2px solid rgba(124,58,237,.4) !important;
    border-radius: 50% !important;
}
[data-testid="stChatMessage"] [data-testid="chatAvatarIcon-user"] {
    background: linear-gradient(135deg, #1e40af, #3b82f6) !important;
    border: 2px solid rgba(59,130,246,.4) !important;
    border-radius: 50% !important;
}

/* ════════════════════════════════════════════════════════════
   CHAT INPUT
════════════════════════════════════════════════════════════ */
[data-testid="stChatInput"] {
    background: var(--b2) !important;
    border: 1px solid var(--bdr) !important;
    border-radius: 18px !important;
    box-shadow: var(--s2), 0 0 0 1px var(--bdr) !important;
    backdrop-filter: blur(12px) !important;
    transition: border-color .2s, box-shadow .2s !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: rgba(124,58,237,.5) !important;
    box-shadow: var(--s2), 0 0 0 3px var(--glow-v) !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: var(--t1) !important;
    font-family: Inter, sans-serif !important;
    font-size: .93rem !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: var(--t4) !important;
}

/* ════════════════════════════════════════════════════════════
   SPINNER / ALERTS
════════════════════════════════════════════════════════════ */
[data-testid="stSpinner"] p {
    font-family: Inter, sans-serif !important;
    color: var(--t2) !important;
    font-size: .85rem !important;
}
.stAlert {
    border-radius: var(--r2) !important;
    font-family: Inter, sans-serif !important;
    font-size: .85rem !important;
}

/* ════════════════════════════════════════════════════════════
   CHART
════════════════════════════════════════════════════════════ */
[data-testid="stVegaLiteChart"] canvas { filter: saturate(1.1) brightness(.95); }

/* ════════════════════════════════════════════════════════════
   ANIMATIONS
════════════════════════════════════════════════════════════ */
@keyframes fadeUp {
    from { opacity:0; transform:translateY(10px); }
    to   { opacity:1; transform:translateY(0); }
}
@keyframes shimmer {
    0%   { background-position: -200% center; }
    100% { background-position:  200% center; }
}
@keyframes pulse-ring {
    0%,100% { box-shadow: 0 0 0 0 rgba(124,58,237,.4); }
    50%      { box-shadow: 0 0 0 8px rgba(124,58,237,0); }
}
@keyframes scoreIn {
    from { stroke-dashoffset: 163; opacity:0; }
}

/* ════════════════════════════════════════════════════════════
   ── APP HEADER ──
════════════════════════════════════════════════════════════ */
.aip-header {
    text-align: center;
    padding: 1.6rem 1rem .8rem;
    position: relative;
}
.aip-header::after {
    content: '';
    display: block;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--violet), var(--indigo), transparent);
    margin-top: 1rem;
    opacity: .4;
}
.aip-logo {
    display: inline-flex;
    align-items: center;
    gap: .5rem;
    background: linear-gradient(135deg, #c084fc, #818cf8, #60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-family: Inter, sans-serif;
    font-size: 1.75rem;
    font-weight: 800;
    letter-spacing: -.03em;
    line-height: 1;
}
.aip-sub {
    font-family: Inter, sans-serif;
    font-size: .85rem;
    color: var(--t3);
    margin-top: .35rem;
    letter-spacing: .02em;
}

/* ════════════════════════════════════════════════════════════
   ── HERO / WELCOME ──
════════════════════════════════════════════════════════════ */
.hero-wrap {
    position: relative;
    border-radius: var(--r4);
    overflow: hidden;
    margin-bottom: 1.4rem;
    border: 1px solid var(--bdr);
    background: linear-gradient(140deg, #130b2e 0%, #0c1527 50%, #070e1e 100%);
    box-shadow: var(--s3), inset 0 1px 0 rgba(255,255,255,.06);
}
.hero-wrap::before {
    content: '';
    position: absolute;
    inset: 0;
    background:
        radial-gradient(ellipse 70% 60% at 10% 20%,  rgba(124,58,237,.22) 0%, transparent 55%),
        radial-gradient(ellipse 50% 50% at 90% 80%,  rgba(99,102,241,.15)  0%, transparent 55%),
        radial-gradient(ellipse 40% 40% at 50% 100%, rgba(6,182,212,.08)   0%, transparent 50%);
    pointer-events: none;
}
/* grid dots overlay */
.hero-wrap::after {
    content: '';
    position: absolute;
    inset: 0;
    background-image: radial-gradient(circle, rgba(255,255,255,.06) 1px, transparent 1px);
    background-size: 28px 28px;
    pointer-events: none;
    opacity: .5;
}
.hero-inner {
    position: relative;
    z-index: 1;
    padding: 2.8rem 2rem 2.2rem;
    text-align: center;
}
.hero-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: .4rem;
    font-family: Inter, sans-serif;
    font-size: .72rem;
    font-weight: 700;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: #c084fc;
    background: rgba(124,58,237,.12);
    border: 1px solid rgba(124,58,237,.3);
    padding: .3rem .9rem;
    border-radius: 999px;
    margin-bottom: 1.2rem;
}
.hero-eyebrow::before { content: '◆'; font-size: .6rem; }
.hero-h1 {
    font-family: Inter, sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: #fff;
    letter-spacing: -.04em;
    line-height: 1.15;
    margin-bottom: .8rem;
}
.hero-h1 span {
    background: linear-gradient(90deg, #c084fc, #818cf8, #38bdf8);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: shimmer 4s linear infinite;
}
.hero-sub {
    font-family: Inter, sans-serif;
    font-size: .95rem;
    color: var(--t2);
    line-height: 1.6;
    max-width: 500px;
    margin: 0 auto 1.6rem;
}
.hero-chips {
    display: flex;
    gap: .5rem;
    justify-content: center;
    flex-wrap: wrap;
}
.hero-chip {
    font-family: Inter, sans-serif;
    font-size: .75rem;
    font-weight: 500;
    color: var(--t2);
    background: rgba(255,255,255,.05);
    border: 1px solid var(--bdr);
    padding: .3rem .75rem;
    border-radius: 999px;
}

/* ════════════════════════════════════════════════════════════
   ── FEATURE CARDS ──
════════════════════════════════════════════════════════════ */
.fc-grid { display:grid; grid-template-columns:1fr 1fr 1fr; gap:.8rem; margin-bottom:1rem; }
.fc {
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: var(--r3);
    padding: 1.3rem 1.1rem;
    backdrop-filter: blur(12px);
    transition: transform .2s ease, border-color .2s ease, box-shadow .2s ease;
    position: relative;
    overflow: hidden;
}
.fc:hover {
    transform: translateY(-3px);
    border-color: rgba(124,58,237,.35);
    box-shadow: 0 8px 32px rgba(124,58,237,.12);
}
.fc::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--violet), var(--indigo), var(--cyan));
    opacity: 0;
    transition: opacity .2s;
}
.fc:hover::before { opacity: 1; }
.fc-icon {
    font-size: 1.6rem;
    margin-bottom: .7rem;
    display: block;
    filter: drop-shadow(0 0 8px rgba(124,58,237,.4));
}
.fc-title {
    font-family: Inter, sans-serif;
    font-size: .88rem;
    font-weight: 700;
    color: var(--t1);
    margin-bottom: .5rem;
}
.fc-list {
    font-family: Inter, sans-serif;
    font-size: .79rem;
    color: var(--t3);
    line-height: 1.8;
    list-style: none;
    padding: 0;
}
.fc-list li::before { content: '›  '; color: var(--violet3); font-weight: 700; }

/* ════════════════════════════════════════════════════════════
   ── TIPS BAR ──
════════════════════════════════════════════════════════════ */
.tips {
    background: rgba(59,130,246,.06);
    border: 1px solid rgba(59,130,246,.18);
    border-radius: var(--r2);
    padding: .7rem 1.1rem;
    text-align: center;
    font-family: Inter, sans-serif;
    font-size: .81rem;
    color: #93c5fd;
}
.tips kbd {
    background: rgba(59,130,246,.15);
    border: 1px solid rgba(59,130,246,.3);
    border-radius: 5px;
    padding: .1em .45em;
    font-family: 'JetBrains Mono', monospace;
    font-size: .76rem;
    color: #7dd3fc;
}

/* ════════════════════════════════════════════════════════════
   ── WELCOME CARD (first AI message) ──
════════════════════════════════════════════════════════════ */
.welcome-card {
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: var(--r3);
    border-top-left-radius: 4px;
    padding: 1.2rem 1.4rem;
    backdrop-filter: blur(12px);
    max-width: 94%;
    animation: fadeUp .35s ease;
    box-shadow: var(--s1);
}
.wc-brand {
    font-family: Inter, sans-serif;
    font-size: .7rem;
    font-weight: 700;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: var(--violet3);
    margin-bottom: .5rem;
    display: flex;
    align-items: center;
    gap: .35rem;
}
.wc-brand::before { content: ''; display:inline-block; width:6px; height:6px; background:var(--violet3); border-radius:50%; }
.wc-title {
    font-family: Inter, sans-serif;
    font-size: .97rem;
    font-weight: 600;
    color: var(--t1);
    margin-bottom: .7rem;
    line-height: 1.45;
}
.wc-pills { display:flex; flex-wrap:wrap; gap:.35rem; margin-bottom: .65rem; }
.pill {
    display: inline-flex;
    align-items: center;
    gap: .22rem;
    font-family: Inter, sans-serif;
    font-size: .73rem;
    font-weight: 500;
    background: var(--b4);
    border: 1px solid var(--bdr);
    color: var(--t2);
    padding: .22rem .65rem;
    border-radius: 999px;
    white-space: nowrap;
}
.wc-tip {
    font-family: Inter, sans-serif;
    font-size: .8rem;
    color: var(--t3);
    line-height: 1.55;
}
.wc-tip code {
    background: rgba(255,255,255,.06);
    border: 1px solid var(--bdr);
    border-radius: 4px;
    padding: .1em .4em;
    font-family: 'JetBrains Mono', monospace;
    font-size: .75rem;
    color: var(--t2);
}

/* ════════════════════════════════════════════════════════════
   ── QUESTION BUBBLE ──
════════════════════════════════════════════════════════════ */
.q-bubble {
    background: linear-gradient(135deg, #16093a 0%, #1a1248 60%, #0f1735 100%);
    border: 1px solid rgba(124,58,237,.28);
    border-radius: var(--r3);
    border-top-left-radius: 4px;
    padding: 1.2rem 1.4rem;
    max-width: 94%;
    box-shadow: var(--s1), 0 0 0 1px rgba(124,58,237,.1);
    animation: fadeUp .3s ease;
    position: relative;
    overflow: hidden;
}
.q-bubble::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(167,139,250,.4), transparent);
}
.q-meta {
    display: flex;
    align-items: center;
    gap: .45rem;
    margin-bottom: .7rem;
}
.q-badge {
    display: inline-flex;
    align-items: center;
    gap: .28rem;
    font-family: Inter, sans-serif;
    font-size: .69rem;
    font-weight: 800;
    letter-spacing: .09em;
    text-transform: uppercase;
    padding: .22rem .7rem;
    border-radius: 999px;
}
.q-badge-main {
    background: rgba(124,58,237,.2);
    border: 1px solid rgba(124,58,237,.4);
    color: #c084fc;
}
.q-badge-follow {
    background: rgba(59,130,246,.15);
    border: 1px solid rgba(59,130,246,.35);
    color: #93c5fd;
}
.q-badge-skip {
    background: rgba(100,116,139,.12);
    border: 1px solid rgba(100,116,139,.25);
    color: var(--t3);
    font-size: .68rem;
}
.q-text {
    font-family: Inter, sans-serif;
    font-size: 1.02rem;
    font-weight: 500;
    color: #e2e8f0;
    line-height: 1.65;
}

/* ════════════════════════════════════════════════════════════
   ── USER BUBBLE ──
════════════════════════════════════════════════════════════ */
.user-outer {
    display: flex;
    justify-content: flex-end;
    width: 100%;
}
.user-bubble {
    background: linear-gradient(135deg, var(--violet) 0%, #9333ea 100%);
    border-radius: var(--r3);
    border-bottom-right-radius: 4px;
    padding: .9rem 1.15rem;
    max-width: 78%;
    font-family: Inter, sans-serif;
    font-size: .92rem;
    font-weight: 400;
    color: #fff;
    line-height: 1.6;
    box-shadow: var(--s1), 0 4px 20px rgba(124,58,237,.35);
    animation: fadeUp .28s ease;
    word-break: break-word;
}

/* ════════════════════════════════════════════════════════════
   ── HINT BUBBLE ──
════════════════════════════════════════════════════════════ */
.hint-bubble {
    background: linear-gradient(135deg, #052e16 0%, #0a2318 100%);
    border: 1px solid rgba(34,197,94,.22);
    border-radius: var(--r3);
    border-top-left-radius: 4px;
    padding: 1rem 1.3rem;
    max-width: 94%;
    box-shadow: var(--s1);
    animation: fadeUp .3s ease;
}
.hint-hd {
    display: flex;
    align-items: center;
    gap: .4rem;
    font-family: Inter, sans-serif;
    font-size: .7rem;
    font-weight: 800;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: #4ade80;
    margin-bottom: .5rem;
}
.hint-dot { width:7px; height:7px; background:#22c55e; border-radius:50%; animation: pulse-ring 2s infinite; }
.hint-text {
    font-family: Inter, sans-serif;
    font-size: .9rem;
    color: #86efac;
    line-height: 1.65;
}

/* ════════════════════════════════════════════════════════════
   ── EVALUATION CARD ──
════════════════════════════════════════════════════════════ */
.ev-card {
    background: var(--b2);
    border: 1px solid var(--bdr);
    border-radius: var(--r3);
    border-top-left-radius: 4px;
    overflow: hidden;
    max-width: 97%;
    box-shadow: var(--s2);
    animation: fadeUp .35s ease;
}

/* header strip */
.ev-head {
    display: flex;
    align-items: center;
    gap: 1.1rem;
    padding: 1.1rem 1.4rem;
    background: linear-gradient(135deg, var(--b3), var(--b2));
    border-bottom: 1px solid var(--bdr);
    position: relative;
    overflow: hidden;
}
.ev-head::before {
    content:'';
    position:absolute; top:0; left:0; right:0; height:2px;
    /* color set inline from Python */
}

/* SVG score ring */
.score-wrap {
    flex-shrink: 0;
    position: relative;
    width: 68px;
    height: 68px;
}
.score-svg { transform: rotate(-90deg); overflow: visible; }
.score-track { fill: none; stroke: rgba(255,255,255,.06); stroke-width: 5; }
.score-arc {
    fill: none;
    stroke-width: 5;
    stroke-linecap: round;
    animation: scoreIn .9s cubic-bezier(.4,0,.2,1) forwards;
}
.score-label {
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    pointer-events: none;
}
.score-num {
    font-family: Inter, sans-serif;
    font-size: 1.25rem;
    font-weight: 800;
    line-height: 1;
}
.score-den {
    font-family: Inter, sans-serif;
    font-size: .6rem;
    color: var(--t3);
    line-height: 1;
}

/* verdict block */
.ev-verdict { flex: 1; min-width: 0; }
.ev-q-tag {
    font-family: Inter, sans-serif;
    font-size: .69rem;
    font-weight: 700;
    letter-spacing: .09em;
    text-transform: uppercase;
    color: var(--t4);
    margin-bottom: .25rem;
}
.ev-label {
    font-family: Inter, sans-serif;
    font-size: .88rem;
    font-weight: 700;
    margin-bottom: .2rem;
}
.ev-short {
    font-family: Inter, sans-serif;
    font-size: .85rem;
    color: var(--t2);
    line-height: 1.4;
}

/* score bar */
.sbar-wrap {
    padding: .55rem 1.4rem;
    background: var(--b1);
    border-bottom: 1px solid var(--bdr2);
    display: flex;
    align-items: center;
    gap: .8rem;
}
.sbar-bg {
    flex: 1;
    height: 5px;
    background: rgba(255,255,255,.06);
    border-radius: 999px;
    overflow: hidden;
}
.sbar-fill {
    height: 100%;
    border-radius: 999px;
    transition: width .8s cubic-bezier(.4,0,.2,1);
}
.sbar-pct {
    font-family: Inter, sans-serif;
    font-size: .72rem;
    font-weight: 600;
    color: var(--t3);
    white-space: nowrap;
    min-width: 2.5rem;
    text-align: right;
}

/* sections */
.ev-body { padding: 1rem 1.4rem; display:flex; flex-direction:column; gap:.85rem; }
.ev-sec h5 {
    font-family: Inter, sans-serif;
    font-size: .7rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: .09em;
    margin-bottom: .45rem;
    display: flex;
    align-items: center;
    gap: .35rem;
}
.ev-sec h5::after { content:''; flex:1; height:1px; background:var(--bdr2); }
.ev-sec ul {
    font-family: Inter, sans-serif;
    font-size: .86rem;
    line-height: 1.75;
    padding-left: 1.1rem;
    margin: 0;
}
.ev-sec p {
    font-family: Inter, sans-serif;
    font-size: .87rem;
    line-height: 1.7;
    margin: 0;
}
.sec-strengths h5 { color: #4ade80; }
.sec-strengths ul { color: #86efac; }
.sec-gaps h5 { color: #f87171; }
.sec-gaps ul { color: #fca5a5; }
.sec-feedback h5 { color: #60a5fa; }
.sec-feedback p { color: #93c5fd; }

/* model answer box */
.model-box {
    background: linear-gradient(135deg, rgba(124,58,237,.06), rgba(99,102,241,.06));
    border: 1px solid rgba(124,58,237,.18);
    border-radius: var(--r2);
    padding: .9rem 1.1rem;
}
.model-box h5 {
    font-family: Inter, sans-serif;
    font-size: .7rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: .09em;
    color: var(--violet3);
    margin-bottom: .45rem;
    display: flex;
    align-items: center;
    gap: .35rem;
}
.model-box h5::after { content:''; flex:1; height:1px; background:rgba(124,58,237,.15); }
.model-box p {
    font-family: Inter, sans-serif;
    font-size: .86rem;
    color: #d8b4fe;
    line-height: 1.7;
    margin: 0;
}

/* special notices */
.ev-notice {
    display: flex;
    align-items: flex-start;
    gap: .5rem;
    padding: .5rem .8rem;
    border-radius: var(--r1);
    font-family: Inter, sans-serif;
    font-size: .81rem;
    line-height: 1.5;
}
.ev-notice-time {
    background: rgba(239,68,68,.07);
    border: 1px solid rgba(239,68,68,.2);
    color: #fca5a5;
}
.ev-notice-diff {
    background: rgba(245,158,11,.06);
    border: 1px solid rgba(245,158,11,.2);
    color: #fde68a;
}

/* footer */
.ev-foot {
    padding: .5rem 1.4rem;
    background: var(--b1);
    border-top: 1px solid var(--bdr2);
    font-family: Inter, sans-serif;
    font-size: .73rem;
    color: var(--t4);
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.ev-foot-dot { width:6px; height:6px; border-radius:50%; display:inline-block; }

/* ════════════════════════════════════════════════════════════
   ── SESSION SUMMARY ──
════════════════════════════════════════════════════════════ */
.sum-card {
    background: var(--b2);
    border: 1px solid var(--bdr);
    border-radius: var(--r4);
    overflow: hidden;
    animation: fadeUp .4s ease;
    box-shadow: var(--s3);
    max-width: 97%;
}
.sum-head {
    background: linear-gradient(140deg, #130b2e 0%, #0c1527 100%);
    padding: 2rem 1.8rem 1.6rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    border-bottom: 1px solid var(--bdr);
}
.sum-head::before {
    content:'';
    position:absolute; inset:0;
    background: radial-gradient(ellipse 70% 60% at 50% 0%, rgba(124,58,237,.3) 0%, transparent 60%);
    pointer-events:none;
}
.sum-head::after {
    content:'';
    position:absolute; inset:0;
    background-image: radial-gradient(circle, rgba(255,255,255,.04) 1px, transparent 1px);
    background-size: 24px 24px;
    pointer-events:none;
}
.sum-badge {
    position: relative; z-index:1;
    font-family: Inter, sans-serif;
    font-size: 1.25rem;
    font-weight: 800;
    color: #fff;
    margin-bottom: .4rem;
}
.sum-stats {
    position: relative; z-index:1;
    font-family: Inter, sans-serif;
    font-size: .88rem;
    color: var(--t2);
    margin-bottom: .9rem;
}
.sum-score-row {
    position: relative; z-index:1;
    display: flex;
    justify-content: center;
    gap: .4rem;
    flex-wrap: wrap;
}
.sum-score-pill {
    font-family: Inter, sans-serif;
    font-size: .78rem;
    font-weight: 600;
    padding: .25rem .65rem;
    border-radius: 999px;
    border: 1px solid var(--bdr);
    background: rgba(255,255,255,.05);
    color: var(--t1);
}
.sum-body {
    padding: 1.3rem 1.6rem;
    font-family: Inter, sans-serif;
    font-size: .88rem;
    color: var(--t2);
    line-height: 1.75;
}
.sum-body h2 {
    font-size: .95rem;
    font-weight: 700;
    color: var(--t1);
    margin: 1.1rem 0 .3rem;
    display: flex;
    align-items: center;
    gap: .4rem;
}
.sum-body h2::after { content:''; flex:1; height:1px; background:var(--bdr2); }
.sum-body h3 { font-size: .88rem; font-weight: 600; color: var(--t1); margin: .8rem 0 .2rem; }
.sum-body ul { padding-left: 1.2rem; }
.sum-body li { margin-bottom: .25rem; }
.sum-body strong { color: var(--t1); font-weight: 600; }
.sum-body p { margin: .3rem 0; }

/* ════════════════════════════════════════════════════════════
   ── SIDEBAR MINI-DASHBOARD ──
════════════════════════════════════════════════════════════ */
.sb-logo {
    text-align: center;
    padding: .6rem 0 .3rem;
}
.sb-logo-text {
    font-family: Inter, sans-serif;
    font-size: 1.05rem;
    font-weight: 800;
    letter-spacing: -.02em;
    background: linear-gradient(135deg, #c084fc, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.sb-logo-sub {
    font-family: Inter, sans-serif;
    font-size: .68rem;
    color: var(--t4);
    text-transform: uppercase;
    letter-spacing: .09em;
    margin-top: .1rem;
}
.sb-stat {
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: var(--r2);
    padding: .65rem .85rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: .35rem;
    backdrop-filter: blur(8px);
}
.sb-stat-label {
    font-family: Inter, sans-serif;
    font-size: .73rem;
    color: var(--t3);
    font-weight: 500;
}
.sb-stat-val {
    font-family: Inter, sans-serif;
    font-size: .82rem;
    font-weight: 700;
    color: var(--t1);
}
.sb-info-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: .28rem 0;
    border-bottom: 1px solid var(--bdr2);
    font-family: Inter, sans-serif;
    font-size: .8rem;
}
.sb-info-key  { color: var(--t4); }
.sb-info-val  { color: var(--t2); font-weight: 500; }

/* timer widget */
.timer-widget {
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: var(--r2);
    padding: .65rem .9rem;
    text-align: center;
    backdrop-filter: blur(8px);
    margin: .4rem 0;
}
.timer-lbl {
    font-family: Inter, sans-serif;
    font-size: .67rem;
    text-transform: uppercase;
    letter-spacing: .09em;
    color: var(--t4);
    margin-bottom: .2rem;
}
.timer-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.55rem;
    font-weight: 700;
    line-height: 1;
}
.tg { color: var(--green); }
.ty { color: var(--yellow); }
.tr { color: var(--red); }

/* ════════════════════════════════════════════════════════════
   ── ACTION BUTTONS (hint / skip) ──
════════════════════════════════════════════════════════════ */
.action-row { display:flex; gap:.5rem; margin-bottom:.5rem; }

/* ════════════════════════════════════════════════════════════
   ── MCQ COMPONENTS ──
════════════════════════════════════════════════════════════ */

/* Options list inside question bubble */
.mcq-options { display:flex; flex-direction:column; gap:.45rem; margin-top:.85rem; }
.mcq-opt {
    display: flex;
    align-items: flex-start;
    gap: .65rem;
    background: rgba(255,255,255,.03);
    border: 1px solid rgba(255,255,255,.07);
    border-radius: var(--r1);
    padding: .6rem .85rem;
    font-family: Inter, sans-serif;
    font-size: .88rem;
    color: var(--t2);
    line-height: 1.5;
    transition: border-color .15s;
}
.mcq-ltr {
    flex-shrink: 0;
    width: 22px; height: 22px;
    border-radius: 50%;
    background: rgba(124,58,237,.15);
    border: 1px solid rgba(124,58,237,.3);
    color: #c084fc;
    font-size: .72rem;
    font-weight: 800;
    display: flex; align-items: center; justify-content: center;
    font-family: Inter, sans-serif;
}

/* MCQ result card */
.mcq-result {
    background: var(--b2);
    border: 1px solid var(--bdr);
    border-radius: var(--r3);
    border-top-left-radius: 4px;
    overflow: hidden;
    max-width: 97%;
    box-shadow: var(--s2);
    animation: fadeUp .35s ease;
}
.mcq-result-head {
    display: flex;
    align-items: center;
    gap: .9rem;
    padding: .9rem 1.3rem;
    border-bottom: 1px solid var(--bdr);
}
.mcq-verdict-icon {
    font-size: 1.8rem;
    flex-shrink: 0;
    filter: drop-shadow(0 0 8px currentColor);
}
.mcq-verdict-text h4 {
    font-family: Inter, sans-serif;
    font-size: .95rem;
    font-weight: 700;
    margin: 0 0 .15rem;
}
.mcq-verdict-text p {
    font-family: Inter, sans-serif;
    font-size: .82rem;
    color: var(--t3);
    margin: 0;
}
.mcq-options-review {
    padding: .8rem 1.3rem;
    display: flex;
    flex-direction: column;
    gap: .4rem;
    border-bottom: 1px solid var(--bdr2);
}
.mcq-opt-correct {
    background: rgba(34,197,94,.08);
    border: 1px solid rgba(34,197,94,.3);
    border-radius: var(--r1);
    padding: .55rem .85rem;
    display: flex; gap:.6rem; align-items:flex-start;
    font-family: Inter, sans-serif;
    font-size: .87rem;
    color: #bbf7d0;
}
.mcq-opt-wrong {
    background: rgba(239,68,68,.07);
    border: 1px solid rgba(239,68,68,.25);
    border-radius: var(--r1);
    padding: .55rem .85rem;
    display: flex; gap:.6rem; align-items:flex-start;
    font-family: Inter, sans-serif;
    font-size: .87rem;
    color: #fecaca;
}
.mcq-opt-neutral {
    background: rgba(255,255,255,.02);
    border: 1px solid rgba(255,255,255,.05);
    border-radius: var(--r1);
    padding: .55rem .85rem;
    display: flex; gap:.6rem; align-items:flex-start;
    font-family: Inter, sans-serif;
    font-size: .87rem;
    color: var(--t4);
}
.mcq-opt-ltr {
    flex-shrink: 0;
    width: 20px; height: 20px;
    border-radius: 50%;
    font-size: .68rem;
    font-weight: 800;
    display: flex; align-items:center; justify-content:center;
    font-family: Inter, sans-serif;
}
.ltr-correct { background:#16a34a; color:#fff; }
.ltr-wrong   { background:#dc2626; color:#fff; }
.ltr-neutral { background:rgba(255,255,255,.06); color:var(--t4); }
.mcq-explanation {
    padding: .8rem 1.3rem;
    font-family: Inter, sans-serif;
    font-size: .86rem;
    color: #93c5fd;
    line-height: 1.65;
    border-bottom: 1px solid var(--bdr2);
}
.mcq-explanation strong { color: #60a5fa; }
.mcq-score-bar {
    padding: .55rem 1.3rem;
    background: var(--b1);
    display: flex; align-items:center; gap:.8rem;
}

/* ════════════════════════════════════════════════════════════
   ── END SCREEN RESTART ──
════════════════════════════════════════════════════════════ */
.end-tip {
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: var(--r2);
    padding: .65rem 1rem;
    text-align: center;
    font-family: Inter, sans-serif;
    font-size: .82rem;
    color: var(--t3);
    backdrop-filter: blur(8px);
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────

def _init_state() -> None:
    defaults = {
        "page": "home",
        "phase": "setup",
        "selected_topic": TOPICS[0],
        "theme": "dark",
        "font_size": "Normal",
        "compact_mode": False,
        "messages": [],
        "current_question": None,
        "question_number": 0,
        "is_follow_up": False,
        "role": ROLES[0],
        "topic": TOPICS[0],
        "difficulty": "Medium",
        "mode": "Practice Mode",
        "adaptive_difficulty": True,
        "scores": [],
        "qa_history": [],
        "timer_start": None,
        "time_limit": 180,
        "interviewer": None,
        "evaluator": None,
        "api_key": os.getenv("GROQ_API_KEY", ""),
        # MCQ
        "question_type": "MCQ",          # "MCQ" | "Open-ended"
        "current_mcq_data": None,        # {question, options, correct, explanation}
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ─────────────────────────────────────────────────────────────────────────────
#  API
# ─────────────────────────────────────────────────────────────────────────────

def _init_api(api_key: str) -> bool:
    if not api_key:
        return False
    st.session_state.interviewer = Interviewer(api_key)
    st.session_state.evaluator = Evaluator(api_key)
    return True

def _ensure_api() -> bool:
    return st.session_state.interviewer is not None or _init_api(st.session_state.api_key)


# ─────────────────────────────────────────────────────────────────────────────
#  INTERVIEW FLOW  (all logic identical to original)
# ─────────────────────────────────────────────────────────────────────────────

def _start_interview() -> None:
    ss = st.session_state
    ss.messages, ss.scores, ss.qa_history = [], [], []
    ss.question_number, ss.current_question, ss.is_follow_up = 0, None, False
    ss.current_mcq_data = None
    ss.phase = "active"
    if ss.mode == "Mock Interview":
        ss.time_limit = MOCK_TIME_LIMITS[ss.difficulty]

    ss.messages.append({
        "role": "assistant", "type": "welcome",
        "role_label": ss.role, "topic": ss.topic,
        "difficulty": ss.difficulty, "mode": ss.mode,
        "question_type": ss.question_type,
    })
    ss.question_number = 1
    ss.timer_start = time.time()

    if ss.question_type == "MCQ":
        mcq = ss.interviewer.generate_mcq(
            topic=ss.topic, difficulty=ss.difficulty,
            role=ss.role, previous_questions=[],
        )
        ss.current_mcq_data = mcq
        ss.current_question = mcq["question"]
        ss.messages.append({
            "role": "assistant", "type": "question_mcq",
            "content": mcq["question"], "options": mcq["options"],
            "question_num": 1,
        })
    else:
        first_q = ss.interviewer.generate_question(
            topic=ss.topic, difficulty=ss.difficulty, role=ss.role, previous_questions=[]
        )
        ss.current_question = first_q
        ss.messages.append({
            "role": "assistant", "type": "question",
            "content": first_q, "question_num": 1, "is_follow_up": False,
        })


def _handle_hint() -> None:
    if not st.session_state.current_question:
        return
    with st.spinner("💡 Generating hint…"):
        hint = st.session_state.evaluator.get_hint(
            question=st.session_state.current_question,
            topic=st.session_state.topic,
            difficulty=st.session_state.difficulty,
        )
    st.session_state.messages.append({"role": "assistant", "type": "hint", "content": hint})


def _handle_skip() -> None:
    ss = st.session_state
    prev_qs = [qa["question"] for qa in ss.qa_history]
    if ss.current_question:
        prev_qs.append(ss.current_question)
    with st.spinner("⏭️ Generating next question…"):
        new_q = ss.interviewer.generate_question(
            topic=ss.topic, difficulty=ss.difficulty,
            role=ss.role, previous_questions=prev_qs,
        )
    ss.current_question, ss.is_follow_up = new_q, False
    ss.question_number += 1
    ss.timer_start = time.time()
    ss.messages.append({
        "role": "assistant", "type": "question",
        "content": new_q, "question_num": ss.question_number,
        "is_follow_up": False, "skipped": True,
    })


def _evaluate_and_respond(user_answer: str) -> None:
    ss = st.session_state
    question = ss.current_question
    if not question:
        return

    time_exceeded = (
        ss.mode == "Mock Interview"
        and ss.timer_start is not None
        and (time.time() - ss.timer_start) > ss.time_limit
    )

    with st.spinner("🔍 Analysing your answer…"):
        evaluation = ss.evaluator.evaluate_answer(
            question=question, answer=user_answer,
            topic=ss.topic, difficulty=ss.difficulty, role=ss.role,
        )

    score = evaluation.get("score", 0)
    ss.scores.append(score)
    ss.qa_history.append({
        "question": question, "answer": user_answer, "score": score,
        "evaluation": evaluation, "question_num": ss.question_number,
        "is_follow_up": ss.is_follow_up,
    })

    diff_note = ""
    if ss.adaptive_difficulty and len(ss.scores) >= 3:
        idx = DIFFICULTIES.index(ss.difficulty)
        if should_increase_difficulty(ss.scores) and idx < len(DIFFICULTIES) - 1:
            ss.difficulty = DIFFICULTIES[idx + 1]
            diff_note = f"🔥 Strong performance — difficulty raised to <strong>{_e(ss.difficulty)}</strong>."
        elif should_decrease_difficulty(ss.scores) and idx > 0:
            ss.difficulty = DIFFICULTIES[idx - 1]
            diff_note = f"📉 Adjusted difficulty to <strong>{_e(ss.difficulty)}</strong> to build confidence."

    ss.messages.append({
        "role": "assistant", "type": "evaluation",
        "score": score, "evaluation": evaluation,
        "question_num": ss.question_number,
        "time_exceeded": time_exceeded, "diff_note": diff_note,
    })

    wants_follow_up = evaluation.get("should_follow_up", False)
    follow_up_q = evaluation.get("follow_up_question")

    if wants_follow_up and follow_up_q and score >= 4:
        ss.current_question = follow_up_q
        ss.question_number += 1
        ss.is_follow_up = True
        ss.timer_start = time.time()
        ss.messages.append({
            "role": "assistant", "type": "question",
            "content": follow_up_q,
            "question_num": ss.question_number, "is_follow_up": True,
        })
    else:
        prev_qs = [qa["question"] for qa in ss.qa_history]
        with st.spinner("⚡ Preparing next question…"):
            new_q = ss.interviewer.generate_question(
                topic=ss.topic, difficulty=ss.difficulty,
                role=ss.role, previous_questions=prev_qs,
            )
        ss.current_question, ss.is_follow_up = new_q, False
        ss.question_number += 1
        ss.timer_start = time.time()
        ss.messages.append({
            "role": "assistant", "type": "question",
            "content": new_q, "question_num": ss.question_number, "is_follow_up": False,
        })


def _end_session() -> None:
    ss = st.session_state
    if not ss.qa_history:
        ss.phase = "ended"
        ss.page = "results"
        ss.messages.append({"role": "assistant", "type": "summary",
                             "summary_text": "No questions were answered.", "scores": [], "total": 0, "avg": 0})
        return
    with st.spinner("📊 Generating your session debrief…"):
        summary = ss.interviewer.generate_session_summary(
            role=ss.role, topic=ss.topic, qa_history=ss.qa_history
        )
    avg = sum(ss.scores) / len(ss.scores)
    badge, _ = get_performance_badge(avg)
    ss.messages.append({
        "role": "assistant", "type": "summary",
        "summary_text": summary, "badge": badge,
        "scores": ss.scores[:], "total": len(ss.scores), "avg": avg,
    })
    ss.phase = "ended"
    ss.page = "results"


def _process_input(text: str) -> None:
    text = text.strip()
    if not text:
        return
    st.session_state.messages.append({"role": "user", "type": "answer", "content": text})
    lower = text.lower()
    if lower in {"hint", "give me a hint", "help", "clue", "i need a hint"}:
        _handle_hint()
    elif lower in {"skip", "next", "pass", "next question", "skip this"}:
        _handle_skip()
    else:
        _evaluate_and_respond(text)


def _process_mcq_answer(option_letter: str) -> None:
    """Handle a user's MCQ option selection."""
    ss = st.session_state
    mcq = ss.current_mcq_data
    if not mcq:
        return

    correct    = mcq["correct"]
    options    = mcq["options"]
    is_correct = option_letter == correct
    score      = 10 if is_correct else 2
    chosen_text = options.get(option_letter, "")

    # User bubble
    ss.messages.append({
        "role": "user", "type": "mcq_answer",
        "content": f"{option_letter}) {chosen_text}",
        "option": option_letter,
    })

    # Record in history (lightweight evaluation for summary)
    ss.scores.append(score)
    ss.qa_history.append({
        "question": mcq["question"],
        "answer": f"{option_letter}) {chosen_text}",
        "score": score,
        "evaluation": {
            "score": score,
            "brief_verdict": "Correct!" if is_correct else f"Wrong — correct was {correct}",
            "strengths": ["Selected the correct answer"] if is_correct else [],
            "missing_concepts": [] if is_correct else [f"Review: {mcq['explanation']}"],
            "detailed_feedback": mcq["explanation"],
            "ideal_answer": f"{correct}) {options.get(correct, '')}",
            "should_follow_up": False,
            "follow_up_question": None,
        },
        "question_num": ss.question_number,
        "is_follow_up": False,
    })

    # Adaptive difficulty
    diff_note = ""
    if ss.adaptive_difficulty and len(ss.scores) >= 3:
        idx = DIFFICULTIES.index(ss.difficulty)
        if should_increase_difficulty(ss.scores) and idx < len(DIFFICULTIES) - 1:
            ss.difficulty = DIFFICULTIES[idx + 1]
            diff_note = f"🔥 Difficulty raised to <strong>{_e(ss.difficulty)}</strong>."
        elif should_decrease_difficulty(ss.scores) and idx > 0:
            ss.difficulty = DIFFICULTIES[idx - 1]
            diff_note = f"📉 Difficulty adjusted to <strong>{_e(ss.difficulty)}</strong>."

    ss.messages.append({
        "role": "assistant", "type": "mcq_result",
        "is_correct": is_correct,
        "score": score,
        "chosen": option_letter,
        "correct": correct,
        "options": options,
        "explanation": mcq["explanation"],
        "question_num": ss.question_number,
        "diff_note": diff_note,
    })

    _next_mcq()


def _next_mcq() -> None:
    """Generate the next MCQ question after an answer."""
    ss = st.session_state
    prev_qs = [qa["question"] for qa in ss.qa_history]
    with st.spinner("⚡ Loading next question…"):
        mcq = ss.interviewer.generate_mcq(
            topic=ss.topic, difficulty=ss.difficulty,
            role=ss.role, previous_questions=prev_qs,
        )
    ss.current_mcq_data = mcq
    ss.current_question = mcq["question"]
    ss.question_number += 1
    ss.timer_start = time.time()
    ss.messages.append({
        "role": "assistant", "type": "question_mcq",
        "content": mcq["question"], "options": mcq["options"],
        "question_num": ss.question_number,
    })


def _handle_skip_mcq() -> None:
    """Skip current MCQ and load a new one."""
    ss = st.session_state
    prev_qs = [qa["question"] for qa in ss.qa_history]
    if ss.current_question:
        prev_qs.append(ss.current_question)
    with st.spinner("⏭️ Loading next question…"):
        mcq = ss.interviewer.generate_mcq(
            topic=ss.topic, difficulty=ss.difficulty,
            role=ss.role, previous_questions=prev_qs,
        )
    ss.current_mcq_data = mcq
    ss.current_question = mcq["question"]
    ss.question_number += 1
    ss.timer_start = time.time()
    ss.messages.append({
        "role": "assistant", "type": "question_mcq",
        "content": mcq["question"], "options": mcq["options"],
        "question_num": ss.question_number, "skipped": True,
    })


# ─────────────────────────────────────────────────────────────────────────────
#  SCORE HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _score_colour(s: int) -> str:
    if s >= 8: return "#22c55e"
    if s >= 6: return "#f59e0b"
    if s >= 4: return "#f97316"
    return "#ef4444"

def _score_glow(s: int) -> str:
    if s >= 8: return "rgba(34,197,94,.25)"
    if s >= 6: return "rgba(245,158,11,.25)"
    if s >= 4: return "rgba(249,115,22,.25)"
    return "rgba(239,68,68,.25)"

def _svg_ring(score: int, size: int = 64) -> str:
    """Build an SVG donut ring that fills to score/10."""
    r   = 26
    cx  = cy = size // 2
    circ = 2 * 3.14159 * r          # ≈ 163.4
    fill = circ * (score / 10)
    gap  = circ - fill
    colour = _score_colour(score)
    return (
        f'<svg class="score-svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
        f'<circle class="score-track" cx="{cx}" cy="{cy}" r="{r}"/>'
        f'<circle class="score-arc" cx="{cx}" cy="{cy}" r="{r}" '
        f'stroke="{colour}" '
        f'stroke-dasharray="{fill:.1f} {gap:.1f}" '
        f'style="filter:drop-shadow(0 0 6px {colour}80)"/>'
        f'</svg>'
    )


def _copy_button(text: str) -> None:
    """Render a JS clipboard copy button for the question text."""
    safe = text.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
    components.html(f"""
<button id="cpbtn" onclick="
  navigator.clipboard.writeText(`{safe}`)
    .then(() => {{
      this.innerHTML = '✓ Copied!';
      this.style.color = '#4ade80';
      this.style.borderColor = 'rgba(74,222,128,.35)';
      setTimeout(() => {{
        this.innerHTML = '📋 Copy Question';
        this.style.color = '#64748b';
        this.style.borderColor = 'rgba(255,255,255,.12)';
      }}, 2000);
    }})
    .catch(() => {{ this.innerHTML = '❌ Failed'; }});
" style="
  background:transparent;
  border:1px solid rgba(255,255,255,.12);
  color:#64748b;
  font-size:.73rem;
  font-family:Inter,sans-serif;
  padding:.28rem .75rem;
  border-radius:6px;
  cursor:pointer;
  margin-top:.35rem;
  transition:all .15s;
  line-height:1.4;
">📋 Copy Question</button>
""", height=42)


# ─────────────────────────────────────────────────────────────────────────────
#  MESSAGE RENDERERS
# ─────────────────────────────────────────────────────────────────────────────

def _render_welcome_msg(msg: dict) -> None:
    mode_icon = "⏱️" if msg.get("mode") == "Mock Interview" else "📝"
    di = get_difficulty_emoji(msg.get("difficulty", "Medium"))
    ti = get_topic_emoji(msg.get("topic", ""))
    st.markdown(f"""
<div class="welcome-card">
  <div class="wc-brand">AI Interviewer · InterviewAI</div>
  <div class="wc-title">Welcome! I'm your AI technical interviewer.<br>
    Let's begin your <strong style="color:#c084fc;">{_e(msg.get('topic',''))}</strong> session.
  </div>
  <div class="wc-pills">
    <span class="pill">🎯 {_e(msg.get('role_label',''))}</span>
    <span class="pill">{ti} {_e(msg.get('topic',''))}</span>
    <span class="pill">{di} {_e(msg.get('difficulty',''))}</span>
    <span class="pill">{mode_icon} {_e(msg.get('mode',''))}</span>
  </div>
  <div class="wc-tip">
    I'll ask questions one at a time and give detailed scored feedback after each answer.<br>
    Type <code>hint</code> for a clue · <code>skip</code> to move on ·
    click <strong>End Session</strong> in the sidebar for your full debrief.
  </div>
</div>
""", unsafe_allow_html=True)


def _render_question_msg(msg: dict) -> None:
    qn   = msg.get("question_num", "")
    is_fu = msg.get("is_follow_up", False)
    skip  = msg.get("skipped", False)
    text  = _e(msg.get("content", ""))

    if is_fu:
        badge = f'<span class="q-badge q-badge-follow">🔍 Follow-up · Q{qn}</span>'
    else:
        badge = f'<span class="q-badge q-badge-main">❓ Question {qn}</span>'

    skip_note = ""
    if skip:
        skip_note = '<span class="q-badge q-badge-skip">⏭️ Skipped</span>'

    st.markdown(f"""
<div class="q-bubble">
  <div class="q-meta">{badge}{skip_note}</div>
  <p class="q-text">{text}</p>
</div>
""", unsafe_allow_html=True)
    _copy_button(msg.get("content", ""))


def _render_user_msg(msg: dict) -> None:
    st.markdown(f"""
<div class="user-outer">
  <div class="user-bubble">{_e(msg.get('content',''))}</div>
</div>
""", unsafe_allow_html=True)


def _render_hint_msg(msg: dict) -> None:
    st.markdown(f"""
<div class="hint-bubble">
  <div class="hint-hd"><div class="hint-dot"></div>Hint</div>
  <div class="hint-text">{_e(msg.get('content',''))}</div>
</div>
""", unsafe_allow_html=True)


def _render_evaluation_msg(msg: dict) -> None:
    ev      = msg.get("evaluation", {})
    score   = msg.get("score", 0)
    qn      = msg.get("question_num", "")
    colour  = _score_colour(score)
    glow    = _score_glow(score)
    label   = get_score_label(score)
    emoji   = get_score_emoji(score)
    ring    = _svg_ring(score)
    verdict = _e(ev.get("brief_verdict") or "")
    pct     = score * 10

    strengths = ev.get("strengths") or []
    gaps      = ev.get("missing_concepts") or []
    s_html = "".join(f"<li>{_e(s)}</li>" for s in strengths) or "<li>None specifically identified.</li>"
    g_html = "".join(f"<li>{_e(g)}</li>" for g in gaps) or "<li>Nothing major missing — well done!</li>"
    feedback = _e(ev.get("detailed_feedback") or "")
    ideal    = _e(ev.get("ideal_answer") or "N/A")

    time_html = ""
    if msg.get("time_exceeded"):
        time_html = '<div class="ev-notice ev-notice-time">⏰ Time limit exceeded — aim to be more concise in a real interview.</div>'

    diff_html = ""
    if msg.get("diff_note"):
        diff_html = f'<div class="ev-notice ev-notice-diff">⚡ Adaptive: {msg["diff_note"]}</div>'

    st.markdown(f"""
<div class="ev-card">

  <!-- header strip accent -->
  <div style="height:2px;background:linear-gradient(90deg,{colour},{colour}80,transparent);
              box-shadow:0 0 12px {glow};"></div>

  <!-- head: ring + verdict -->
  <div class="ev-head">
    <div class="score-wrap">
      {ring}
      <div class="score-label">
        <span class="score-num" style="color:{colour};">{score}</span>
        <span class="score-den">/10</span>
      </div>
    </div>
    <div class="ev-verdict">
      <div class="ev-q-tag">Question {qn} · {emoji} {label}</div>
      <div class="ev-label" style="color:{colour};">{label}</div>
      <div class="ev-short">{verdict}</div>
    </div>
  </div>

  <!-- score bar -->
  <div class="sbar-wrap">
    <div class="sbar-bg">
      <div class="sbar-fill" style="width:{pct}%;background:linear-gradient(90deg,{colour}cc,{colour});"></div>
    </div>
    <span class="sbar-pct" style="color:{colour};">{score}/10</span>
  </div>

  <!-- body -->
  <div class="ev-body">
    <div class="ev-sec sec-strengths">
      <h5>✅ Strengths</h5>
      <ul>{s_html}</ul>
    </div>
    <div class="ev-sec sec-gaps">
      <h5>🔍 Concepts to Review</h5>
      <ul>{g_html}</ul>
    </div>
    <div class="ev-sec sec-feedback">
      <h5>💬 Detailed Feedback</h5>
      <p>{feedback}</p>
    </div>
    <div class="model-box">
      <h5>📖 Model Answer</h5>
      <p>{ideal}</p>
    </div>
    {time_html}
    {diff_html}
  </div>

  <div class="ev-foot">
    <span>Q{qn} · Score recorded</span>
    <span><span class="ev-foot-dot" style="background:{colour};
      box-shadow:0 0 6px {colour};"></span></span>
  </div>
</div>
""", unsafe_allow_html=True)


def _render_question_mcq(msg: dict) -> None:
    qn   = msg.get("question_num", "")
    skip = msg.get("skipped", False)
    text = _e(msg.get("content", ""))
    options: dict = msg.get("options", {})

    badge = f'<span class="q-badge q-badge-main">🔢 MCQ · Question {qn}</span>'
    skip_note = '<span class="q-badge q-badge-skip">⏭️ Skipped</span>' if skip else ""

    opts_html = "".join(
        f'<div class="mcq-opt">'
        f'  <span class="mcq-ltr">{_e(letter)}</span>'
        f'  <span>{_e(opt_text)}</span>'
        f'</div>'
        for letter, opt_text in options.items()
    )

    st.markdown(f"""
<div class="q-bubble">
  <div class="q-meta">{badge}{skip_note}</div>
  <p class="q-text">{text}</p>
  <div class="mcq-options">{opts_html}</div>
</div>
""", unsafe_allow_html=True)
    _copy_button(msg.get("content", ""))


def _render_mcq_result(msg: dict) -> None:
    is_correct  = msg.get("is_correct", False)
    score       = msg.get("score", 0)
    chosen      = msg.get("chosen", "")
    correct     = msg.get("correct", "")
    options     = msg.get("options", {})
    explanation = _e(msg.get("explanation", ""))
    qn          = msg.get("question_num", "")
    diff_note   = msg.get("diff_note", "")
    colour      = _score_colour(score)
    pct         = score * 10

    verdict_icon = "✅" if is_correct else "❌"
    verdict_head = "Correct Answer!" if is_correct else "Incorrect"
    verdict_sub  = f"You chose {chosen} · Correct answer: {correct}" if not is_correct else f"You chose {chosen} — well done!"

    # Options review
    review_rows = ""
    for letter, opt_text in options.items():
        is_c = letter == correct
        is_w = letter == chosen and not is_correct
        if is_c:
            css, ltr_css, icon = "mcq-opt-correct", "ltr-correct", "✓"
        elif is_w:
            css, ltr_css, icon = "mcq-opt-wrong", "ltr-wrong", "✗"
        else:
            css, ltr_css, icon = "mcq-opt-neutral", "ltr-neutral", letter
        review_rows += (
            f'<div class="{css}">'
            f'<span class="mcq-opt-ltr {ltr_css}">{icon}</span>'
            f'<span>{_e(opt_text)}</span>'
            f'</div>'
        )

    diff_html = (f'<div class="ev-notice ev-notice-diff" style="margin:.6rem 1.3rem;">⚡ {diff_note}</div>'
                 if diff_note else "")

    st.markdown(f"""
<div class="mcq-result">
  <div style="height:2px;background:linear-gradient(90deg,{colour},{colour}80,transparent);
              box-shadow:0 0 10px {_score_glow(score)};"></div>
  <div class="mcq-result-head">
    <div class="mcq-verdict-icon" style="color:{colour};">{verdict_icon}</div>
    <div class="mcq-verdict-text">
      <h4 style="color:{colour};">{verdict_head}</h4>
      <p>{verdict_sub}</p>
    </div>
  </div>
  <div class="mcq-options-review">{review_rows}</div>
  <div class="mcq-explanation"><strong>💡 Explanation:</strong> {explanation}</div>
  <div class="mcq-score-bar">
    <div class="sbar-bg" style="flex:1;">
      <div class="sbar-fill" style="width:{pct}%;background:linear-gradient(90deg,{colour}cc,{colour});"></div>
    </div>
    <span class="sbar-pct" style="color:{colour};">{score}/10</span>
  </div>
  {diff_html}
</div>
""", unsafe_allow_html=True)


def _render_summary_msg(msg: dict) -> None:
    total = msg.get("total", 0)
    avg   = msg.get("avg", 0.0)
    badge = msg.get("badge", "")
    text  = msg.get("summary_text", "")
    scores = msg.get("scores", [])

    if not total:
        st.markdown(f'<div class="hint-bubble"><div class="hint-text">{_e(text)}</div></div>',
                    unsafe_allow_html=True)
        return

    pills = "".join(
        f'<span class="sum-score-pill" style="color:{_score_colour(s)};'
        f'border-color:{_score_colour(s)}40;">{get_score_emoji(s)} {s}</span>'
        for s in scores
    )
    st.markdown(f"""
<div class="sum-card">
  <div class="sum-head">
    <div class="sum-badge">{_e(badge)}</div>
    <div class="sum-stats">{total} questions · Average <strong style="color:#c084fc;">{avg:.1f}/10</strong></div>
    <div class="sum-score-row">{pills}</div>
  </div>
  <div class="sum-body">{text}</div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  CHAT DISPATCHER
# ─────────────────────────────────────────────────────────────────────────────

def _render_chat() -> None:
    for msg in st.session_state.messages:
        role  = msg["role"]
        mtype = msg.get("type", "")
        avatar = "🤖" if role == "assistant" else "👤"
        with st.chat_message(role, avatar=avatar):
            if role == "user":
                _render_user_msg(msg)
            elif mtype == "welcome":
                _render_welcome_msg(msg)
            elif mtype == "question":
                _render_question_msg(msg)
            elif mtype == "question_mcq":
                _render_question_mcq(msg)
            elif mtype == "evaluation":
                _render_evaluation_msg(msg)
            elif mtype == "mcq_result":
                _render_mcq_result(msg)
            elif mtype == "hint":
                _render_hint_msg(msg)
            elif mtype == "summary":
                _render_summary_msg(msg)
            else:
                st.markdown(msg.get("content", ""))


# ─────────────────────────────────────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────

def _render_sidebar() -> None:
    ss = st.session_state
    with st.sidebar:
        st.markdown("""
<div class="sb-logo">
  <div class="sb-logo-text">🎯 InterviewAI</div>
  <div class="sb-logo-sub">AI-Powered · Adaptive · Real-time</div>
</div>
""", unsafe_allow_html=True)
        st.divider()

        # ── Appearance ────────────────────────────────────────────────────────
        with st.expander("🎨 Appearance", expanded=False):
            theme_icon = "🌙" if ss.theme == "dark" else "☀️"
            theme_label = "Switch to Light Mode" if ss.theme == "dark" else "Switch to Dark Mode"
            if st.button(f"{theme_icon} {theme_label}", use_container_width=True):
                ss.theme = "light" if ss.theme == "dark" else "dark"
                st.rerun()

            ss.font_size = st.select_slider(
                "Text Size", ["Small", "Normal", "Large"],
                value=ss.get("font_size", "Normal"),
            )
            ss.compact_mode = st.toggle(
                "Compact Layout", value=ss.get("compact_mode", False),
                help="Tighter spacing for more content on screen",
            )

        st.divider()
        _sidebar_active()


def _sidebar_setup() -> None:
    st.markdown("### 🎮 Setup")

    role = st.selectbox("Target Role", ROLES)
    topic_sel = st.selectbox(
        "Topic Area",
        [f"{get_topic_emoji(t)} {t}" for t in TOPICS],
    )
    topic = topic_sel.split(" ", 1)[1]
    difficulty = st.select_slider("Difficulty", DIFFICULTIES, value="Medium")
    st.caption(f"{get_difficulty_emoji(difficulty)} **{difficulty}** selected")

    question_type = st.radio(
        "Question Type",
        ["MCQ", "Open-ended"],
        index=0,
        help="MCQ: multiple choice  |  Open-ended: type your answer",
    )

    mode = st.radio(
        "Mode",
        ["Practice Mode", "Mock Interview"],
        help="Practice: relaxed  |  Mock: timed per question",
    )
    adaptive = st.toggle("🔄 Adaptive Difficulty", value=True)
    st.divider()

    if st.button("🚀 Start Interview", type="primary", use_container_width=True):
        ss = st.session_state
        ss.role, ss.topic, ss.difficulty = role, topic, difficulty
        ss.mode, ss.adaptive_difficulty = mode, adaptive
        ss.question_type = question_type
        _ensure_api()
        with st.spinner("Preparing your interview…"):
            _start_interview()
        ss.page = "interview"
        st.rerun()

    st.divider()
    if st.button("🎲 Random Question", use_container_width=True):
        ss = st.session_state
        ss.role, ss.topic, ss.difficulty = role, topic, difficulty
        ss.mode, ss.adaptive_difficulty = "Practice Mode", adaptive
        ss.question_type = question_type
        _ensure_api()
        with st.spinner("Generating question…"):
            _start_interview()
        ss.page = "interview"
        st.rerun()


def _sidebar_active() -> None:
    ss = st.session_state
    stats = calculate_stats(ss.scores)

    st.markdown("### 📊 Progress")
    c1, c2 = st.columns(2)
    c1.metric("Questions", stats["total"])
    c2.metric("Avg Score", f"{stats['average']}/10" if stats["total"] else "—")
    c1.metric("Best", f"{stats['highest']}/10"  if stats["total"] else "—")
    c2.metric("Trend", stats["trend"])

    if ss.scores:
        st.markdown(
            '<p style="font-family:Inter,sans-serif;font-size:.7rem;color:var(--t4);'
            'text-transform:uppercase;letter-spacing:.07em;margin:.6rem 0 .2rem;">Score history</p>',
            unsafe_allow_html=True,
        )
        st.line_chart({"Score": ss.scores}, height=80, use_container_width=True)

    st.divider()
    st.markdown("### 🎯 Session")

    rows = [
        ("Role", ss.role),
        ("Topic", f"{get_topic_emoji(ss.topic)} {ss.topic}"),
        ("Difficulty", f"{get_difficulty_emoji(ss.difficulty)} {ss.difficulty}"),
        ("Mode", ss.mode),
    ]
    for key, val in rows:
        st.markdown(
            f'<div class="sb-info-row">'
            f'<span class="sb-info-key">{key}</span>'
            f'<span class="sb-info-val">{val}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Mock timer
    if ss.mode == "Mock Interview" and ss.timer_start and ss.phase == "active":
        remaining, t_str = format_time_remaining(ss.timer_start, ss.time_limit)
        ratio = remaining / ss.time_limit
        cls = "tg" if ratio > .5 else "ty" if ratio > .25 else "tr"
        st.divider()
        st.markdown(f"""
<div class="timer-widget">
  <div class="timer-lbl">⏱️ Time Remaining</div>
  <div class="timer-val {cls}">{t_str}</div>
</div>
""", unsafe_allow_html=True)
        if remaining == 0:
            st.error("⏰ Time's up!")

    st.divider()

    with st.expander("🔧 Change Settings"):
        role_topics = ROLE_TOPICS.get(ss.role, TOPICS)
        new_ts = st.selectbox(
            "Topic",
            [f"{get_topic_emoji(t)} {t}" for t in role_topics],
            index=role_topics.index(ss.topic) if ss.topic in role_topics else 0,
            key="_ct",
        )
        new_topic = new_ts.split(" ", 1)[1]
        new_diff  = st.select_slider("Difficulty", DIFFICULTIES, value=ss.difficulty, key="_cd")
        if st.button("Apply", use_container_width=True):
            ss.topic, ss.difficulty = new_topic, new_diff
            st.success(f"Updated → {new_topic} · {new_diff}")

    st.divider()

    if ss.phase == "active":
        if st.button("🏁 End Session", use_container_width=True):
            _end_session(); st.rerun()
    else:
        if st.button("🔄 New Interview", type="primary", use_container_width=True):
            ss.page = "setup"; st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
#  THEME  &  APPEARANCE
# ─────────────────────────────────────────────────────────────────────────────

_FONT_SCALE = {"Small": ".82rem", "Normal": ".93rem", "Large": "1.05rem"}

def _apply_theme() -> None:
    ss = st.session_state
    theme   = ss.get("theme", "dark")
    fs      = _FONT_SCALE.get(ss.get("font_size", "Normal"), ".93rem")
    compact = ss.get("compact_mode", False)
    pad     = ".6rem 1rem" if compact else "1rem 1.4rem"

    light_vars = ""
    if theme == "light":
        light_vars = """
    --b0: #f0f4ff;
    --b1: #e6edff;
    --b2: #dce6ff;
    --b3: #cdd9ff;
    --b4: #bfceff;
    --glass: rgba(255,255,255,.75);
    --glass-border: rgba(99,102,241,.2);
    --t1: #0f172a;
    --t2: #1e293b;
    --t3: #475569;
    --t4: #64748b;
    --bdr: rgba(0,0,0,.11);
    --bdr2: rgba(0,0,0,.06);
    --glow-v: rgba(124,58,237,.18);
    --glow-b: rgba(59,130,246,.15);"""

    light_app = ""
    if theme == "light":
        light_app = """
.stApp {
    background-color: #f0f4ff !important;
    background-image:
        radial-gradient(ellipse 80% 50% at 15% 10%,  rgba(124,58,237,.07) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 85% 80%,  rgba(99,102,241,.05) 0%, transparent 55%),
        radial-gradient(ellipse 50% 60% at 50% 50%,  rgba(6,182,212,.03)  0%, transparent 60%);
}
[data-testid="stSidebar"] {
    background: #e6edff !important;
    border-right: 1px solid rgba(0,0,0,.1) !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown p { color: #334155 !important; }
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3          { color: #0f172a !important; }
[data-testid="stSidebar"] input       { background: #dce6ff !important; color: #0f172a !important; }
[data-testid="stChatInput"]           { background: #dce6ff !important; border-color: rgba(0,0,0,.12) !important; }
[data-testid="stChatInput"] textarea  { color: #0f172a !important; }

/* ── question bubble ── */
.q-bubble  { background: linear-gradient(135deg,#e8eeff,#f0f4ff) !important;
             border-color: rgba(99,102,241,.2) !important; }
.q-text    { color: #1e293b !important; }
.q-badge   { color: #4338ca !important; }

/* ── evaluation card ── */
.ev-card   { background: #ffffff !important; border-color: rgba(0,0,0,.1) !important; }
.ev-head   { background: linear-gradient(135deg,#f1f5ff,#ffffff) !important;
             border-color: rgba(0,0,0,.08) !important; }
.ev-q-tag  { color: #64748b !important; }
.ev-short  { color: #334155 !important; }
.sbar-bg   { background: rgba(0,0,0,.08) !important; }
.sbar-pct  { color: #475569 !important; }
.ev-body   { background: #ffffff !important; }

/* strengths — dark green */
.sec-strengths h5 { color: #15803d !important; }
.sec-strengths ul { color: #166534 !important; }

/* gaps — dark red */
.sec-gaps h5 { color: #dc2626 !important; }
.sec-gaps ul { color: #991b1b !important; }

/* feedback — dark blue */
.sec-feedback h5 { color: #1d4ed8 !important; }
.sec-feedback p  { color: #1e3a8a !important; }

/* model answer — dark purple */
.model-box { background: rgba(124,58,237,.06) !important;
             border-color: rgba(124,58,237,.2) !important; }
.model-box h5 { color: #6d28d9 !important; }
.model-box p  { color: #4c1d95 !important; }

/* ev footer */
.ev-foot { background: #f1f5ff !important; color: #64748b !important;
           border-color: rgba(0,0,0,.06) !important; }

/* ── hint bubble ── */
.hint-bubble { background: #f0fdf4 !important;
               border-color: rgba(34,197,94,.3) !important; }
.hint-hd     { color: #15803d !important; }
.hint-text   { color: #14532d !important; }
.hint-dot    { background: #16a34a !important; box-shadow: none !important; }

/* ── MCQ question bubble ── */
.mcq-opt     { background: rgba(99,102,241,.06) !important;
               border-color: rgba(99,102,241,.2) !important; }
.mcq-ltr     { background: rgba(99,102,241,.15) !important; color: #4338ca !important; }

/* ── MCQ result card ── */
.mcq-result  { background: #ffffff !important; border-color: rgba(0,0,0,.1) !important; }
.mcq-result-head { background: #f8faff !important; border-color: rgba(0,0,0,.07) !important; }
.mcq-verdict-text h4 { color: inherit !important; }
.mcq-verdict-text p  { color: #475569 !important; }
.mcq-explanation     { color: #1e3a8a !important; border-color: rgba(0,0,0,.06) !important; }
.mcq-explanation strong { color: #1d4ed8 !important; }
.mcq-opt-correct { background: rgba(21,128,61,.08) !important;
                   border-color: rgba(21,128,61,.3) !important; color: #14532d !important; }
.mcq-opt-wrong   { background: rgba(185,28,28,.06) !important;
                   border-color: rgba(185,28,28,.25) !important; color: #7f1d1d !important; }
.mcq-opt-neutral { background: rgba(0,0,0,.03) !important;
                   border-color: rgba(0,0,0,.08) !important; color: #475569 !important; }
.mcq-score-bar   { background: #f1f5ff !important; }

/* ── session summary ── */
.sum-card  { background: #ffffff !important; border-color: rgba(0,0,0,.1) !important; }
.sum-head  { background: linear-gradient(140deg,#ede9fe,#e8eeff) !important; }
.sum-body  { color: #1e293b !important; }

/* ── notice banners ── */
.ev-notice-time { background: rgba(220,38,38,.06) !important;
                  border-color: rgba(220,38,38,.2) !important; color: #991b1b !important; }
.ev-notice-diff { background: rgba(180,83,9,.06) !important;
                  border-color: rgba(180,83,9,.2) !important; color: #92400e !important; }

/* ── hero / feature cards ── */
.hero-wrap  { background: linear-gradient(140deg,#e8eeff 0%,#ede9fe 50%,#f0f4ff 100%) !important; }
.hero-h1    { color: #0f172a !important; }
.hero-sub   { color: #334155 !important; }
.fc         { background: rgba(255,255,255,.7) !important; }
"""

    st.markdown(f"""<style>
:root {{ {light_vars} }}
{light_app}
.ev-body {{ padding: {pad} !important; }}
[data-testid="stChatInput"] textarea,
.q-text, .ev-sec p, .ev-sec ul, .hint-text, .model-box p {{
    font-size: {fs} !important;
}}
</style>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  PAGE HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _hide_sidebar() -> None:
    st.markdown(
        "<style>[data-testid='stSidebar']{display:none!important;}"
        ".main .block-container{max-width:1000px!important;padding-left:3rem!important;"
        "padding-right:3rem!important;}</style>",
        unsafe_allow_html=True,
    )


def _render_home_page() -> None:
    ss = st.session_state

    # ── Top nav bar: brand left, theme toggle right ───────────────────────────
    nav_l, nav_r = st.columns([6, 1])
    with nav_l:
        st.markdown(
            '<div style="font-family:Inter,sans-serif;font-size:1.1rem;font-weight:800;'
            'background:linear-gradient(90deg,#c084fc,#818cf8);-webkit-background-clip:text;'
            '-webkit-text-fill-color:transparent;background-clip:text;padding:.4rem 0;">🎯 InterviewAI</div>',
            unsafe_allow_html=True,
        )
    with nav_r:
        icon = "☀️" if ss.theme == "dark" else "🌙"
        if st.button(icon, help="Toggle dark / light mode", use_container_width=True):
            ss.theme = "light" if ss.theme == "dark" else "dark"
            st.rerun()

    st.markdown("""
<style>
/* ── Home page specific ─────────────────────────────────────── */
.hp-root {
    max-width: 860px;
    margin: 0 auto;
    padding: 2.5rem 1rem 4rem;
    font-family: Inter, sans-serif;
}

/* brand pill */
.hp-pill {
    display: inline-flex; align-items: center; gap: .45rem;
    font-size: .72rem; font-weight: 700; letter-spacing: .1em;
    text-transform: uppercase; color: #a78bfa;
    background: rgba(124,58,237,.1);
    border: 1px solid rgba(124,58,237,.25);
    padding: .32rem 1rem; border-radius: 999px;
    margin-bottom: 1.6rem;
}
.hp-pill-dot { width:6px; height:6px; border-radius:50%; background:#a78bfa;
               box-shadow:0 0 6px #a78bfa; }

/* headline */
.hp-h1 {
    font-size: clamp(2rem, 5vw, 3.2rem);
    font-weight: 800; line-height: 1.13;
    letter-spacing: -.04em; color: var(--t1);
    margin-bottom: .9rem;
}
.hp-h1 .grad {
    background: linear-gradient(100deg, #c084fc 0%, #818cf8 45%, #38bdf8 100%);
    background-size: 200% auto;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: shimmer 5s linear infinite;
}
.hp-sub {
    font-size: 1.05rem; color: var(--t2); line-height: 1.7;
    max-width: 560px; margin: 0 auto 2rem;
}

/* stats row */
.hp-stats {
    display: flex; justify-content: center; gap: 2.5rem;
    margin-bottom: 2.5rem; flex-wrap: wrap;
}
.hp-stat { text-align: center; }
.hp-stat-n {
    font-size: 2rem; font-weight: 800; line-height: 1;
    background: linear-gradient(135deg, #c084fc, #818cf8);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hp-stat-l {
    font-size: .75rem; font-weight: 600; letter-spacing: .07em;
    text-transform: uppercase; color: var(--t3); margin-top: .2rem;
}

/* divider line */
.hp-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--violet), var(--indigo), transparent);
    opacity: .25; margin: 2.2rem 0;
}

/* feature cards */
.hp-cards { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin-bottom: 2.2rem; }
.hp-card {
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: 20px;
    padding: 1.5rem 1.2rem 1.3rem;
    backdrop-filter: blur(14px);
    position: relative; overflow: hidden;
    transition: transform .2s, box-shadow .2s, border-color .2s;
}
.hp-card:hover {
    transform: translateY(-4px);
    border-color: rgba(124,58,237,.35);
    box-shadow: 0 12px 36px rgba(124,58,237,.12);
}
.hp-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    opacity: 0; transition: opacity .2s;
}
.hp-card:hover::before { opacity: 1; }
.hp-card-c1::before { background: linear-gradient(90deg, #7c3aed, #6366f1); }
.hp-card-c2::before { background: linear-gradient(90deg, #0ea5e9, #06b6d4); }
.hp-card-c3::before { background: linear-gradient(90deg, #f59e0b, #f97316); }
.hp-card-icon {
    font-size: 2rem; margin-bottom: .75rem; display: block;
    filter: drop-shadow(0 2px 8px rgba(124,58,237,.3));
}
.hp-card-title {
    font-size: 1rem; font-weight: 700; color: var(--t1);
    margin-bottom: .5rem; letter-spacing: -.01em;
}
.hp-card-desc {
    font-size: .84rem; color: var(--t2); line-height: 1.65; margin: 0;
}
.hp-card-tags {
    display: flex; flex-wrap: wrap; gap: .35rem; margin-top: .9rem;
}
.hp-tag {
    font-size: .69rem; font-weight: 600; letter-spacing: .04em;
    color: var(--t3); background: var(--bdr2);
    border: 1px solid var(--bdr); border-radius: 999px;
    padding: .18rem .6rem;
}

/* topic chips */
.hp-topics { display:flex; flex-wrap:wrap; gap:.5rem; justify-content:center; margin-bottom:2.4rem; }
.hp-topic {
    font-size: .78rem; font-weight: 500; color: var(--t2);
    background: var(--glass); border: 1px solid var(--bdr);
    padding: .32rem .8rem; border-radius: 999px;
    backdrop-filter: blur(8px);
    transition: border-color .18s, color .18s;
}
.hp-topic:hover { border-color: var(--violet); color: var(--t1); }

/* how it works */
.hp-steps { display:grid; grid-template-columns:1fr 1fr 1fr 1fr; gap:.9rem; margin-bottom:2.2rem; }
.hp-step {
    text-align:center; padding:.9rem .5rem;
    background:var(--glass); border:1px solid var(--bdr);
    border-radius:16px; backdrop-filter:blur(10px);
}
.hp-step-n {
    width:32px; height:32px; border-radius:50%;
    background:linear-gradient(135deg,var(--violet),var(--indigo));
    font-size:.82rem; font-weight:800; color:#fff;
    display:flex; align-items:center; justify-content:center;
    margin:0 auto .6rem;
    box-shadow: 0 4px 12px rgba(124,58,237,.35);
}
.hp-step-t { font-size:.82rem; font-weight:600; color:var(--t1); margin-bottom:.2rem; }
.hp-step-d { font-size:.75rem; color:var(--t3); line-height:1.5; }

@media(max-width:640px) {
    .hp-cards { grid-template-columns:1fr; }
    .hp-steps { grid-template-columns:1fr 1fr; }
    .hp-stats { gap:1.5rem; }
}
</style>

<div class="hp-root">

  <!-- brand pill -->
  <div style="text-align:center;">
    <span class="hp-pill"><span class="hp-pill-dot"></span>AI Interview Coach</span>
  </div>

  <!-- headline -->
  <div style="text-align:center;">
    <h1 class="hp-h1">
      Ace Your Next<br>
      <span class="grad">Technical Interview</span>
    </h1>
    <p class="hp-sub">
      Your personal AI interviewer asks real questions, scores every answer out of 10,
      identifies your gaps, and gives expert model answers — all in real time.
    </p>
  </div>

  <!-- stats -->
  <div class="hp-stats">
    <div class="hp-stat"><div class="hp-stat-n">7</div><div class="hp-stat-l">Target Roles</div></div>
    <div class="hp-stat"><div class="hp-stat-n">50+</div><div class="hp-stat-l">Topics Covered</div></div>
    <div class="hp-stat"><div class="hp-stat-n">10</div><div class="hp-stat-l">Score per Answer</div></div>
    <div class="hp-stat"><div class="hp-stat-n">2</div><div class="hp-stat-l">Practice Modes</div></div>
  </div>

  <div class="hp-divider"></div>

  <!-- feature cards -->
  <div class="hp-cards">
    <div class="hp-card hp-card-c1">
      <span class="hp-card-icon">🎯</span>
      <div class="hp-card-title">Role-Tailored Questions</div>
      <p class="hp-card-desc">Questions matched to your target role and seniority — from Software Engineer to DevOps.</p>
      <div class="hp-card-tags">
        <span class="hp-tag">7 Roles</span><span class="hp-tag">3 Difficulty Levels</span><span class="hp-tag">Adaptive</span>
      </div>
    </div>
    <div class="hp-card hp-card-c2">
      <span class="hp-card-icon">📊</span>
      <div class="hp-card-title">Instant Scored Feedback</div>
      <p class="hp-card-desc">Every answer scored 1–10 with strengths, gaps, detailed feedback, and a model answer.</p>
      <div class="hp-card-tags">
        <span class="hp-tag">Score Ring</span><span class="hp-tag">Model Answer</span><span class="hp-tag">Follow-ups</span>
      </div>
    </div>
    <div class="hp-card hp-card-c3">
      <span class="hp-card-icon">🏆</span>
      <div class="hp-card-title">Full Session Debrief</div>
      <p class="hp-card-desc">End each session with a complete performance report, study recommendations, and readiness verdict.</p>
      <div class="hp-card-tags">
        <span class="hp-tag">Trend Chart</span><span class="hp-tag">Study Plan</span><span class="hp-tag">MCQ + Open</span>
      </div>
    </div>
  </div>

  <!-- how it works -->
  <div style="text-align:center;margin-bottom:1.1rem;">
    <span style="font-family:Inter,sans-serif;font-size:.7rem;font-weight:700;letter-spacing:.1em;
                 text-transform:uppercase;color:var(--t3);">How it works</span>
  </div>
  <div class="hp-steps">
    <div class="hp-step"><div class="hp-step-n">1</div><div class="hp-step-t">Pick Your Role</div><div class="hp-step-d">Choose from 7 engineering roles</div></div>
    <div class="hp-step"><div class="hp-step-n">2</div><div class="hp-step-t">Select a Topic</div><div class="hp-step-d">Topics tailored to that role</div></div>
    <div class="hp-step"><div class="hp-step-n">3</div><div class="hp-step-t">Answer Questions</div><div class="hp-step-d">MCQ or open-ended, timed or relaxed</div></div>
    <div class="hp-step"><div class="hp-step-n">4</div><div class="hp-step-t">Get Your Report</div><div class="hp-step-d">Full debrief with scores and tips</div></div>
  </div>

  <!-- topics preview -->
  <div style="text-align:center;margin-bottom:.85rem;">
    <span style="font-family:Inter,sans-serif;font-size:.7rem;font-weight:700;letter-spacing:.1em;
                 text-transform:uppercase;color:var(--t3);">Topics available</span>
  </div>
  <div class="hp-topics">
    <span class="hp-topic">🗂️ Data Structures</span>
    <span class="hp-topic">⚙️ Algorithms</span>
    <span class="hp-topic">🧠 Deep Learning</span>
    <span class="hp-topic">☁️ Cloud Platforms</span>
    <span class="hp-topic">🗄️ Databases</span>
    <span class="hp-topic">🏗️ System Design</span>
    <span class="hp-topic">🐳 Docker / K8s</span>
    <span class="hp-topic">📊 Statistics</span>
    <span class="hp-topic">🔌 APIs & REST</span>
    <span class="hp-topic">🧱 OOP</span>
    <span class="hp-topic">💬 NLP</span>
    <span class="hp-topic">🔄 CI/CD</span>
    <span class="hp-topic">💻 Operating Systems</span>
    <span class="hp-topic">🎤 Behavioral</span>
    <span class="hp-topic">+ many more…</span>
  </div>

</div>
""", unsafe_allow_html=True)

    # CTA button — Streamlit native so it actually works
    _, col, _ = st.columns([1, 2, 1])
    with col:
        if st.button("🚀  Get Started", type="primary", use_container_width=True):
            st.session_state.page = "setup"
            st.rerun()


def _render_setup_page() -> None:
    ss = st.session_state

    # Top nav
    back_col, title_col, theme_col = st.columns([1, 4, 1])
    with back_col:
        if st.button("← Home"):
            ss.page = "home"; st.rerun()
    with theme_col:
        icon = "☀️" if ss.theme == "dark" else "🌙"
        if st.button(icon, key="_setup_theme", help="Toggle dark / light mode", use_container_width=True):
            ss.theme = "light" if ss.theme == "dark" else "dark"
            st.rerun()

    st.markdown("""
<div style="text-align:center;padding:1rem 0 1.5rem;">
  <div class="aip-logo" style="font-size:1.5rem;">⚙️ Setup Your Interview</div>
  <div class="aip-sub">Choose your role, topic and style — then hit Start.</div>
</div>
""", unsafe_allow_html=True)

    # ── Role ──────────────────────────────────────────────────────────────────
    st.markdown("#### 🎯 Target Role")
    role_idx = ROLES.index(ss.get("role", ROLES[0])) if ss.get("role") in ROLES else 0
    role = st.selectbox("Target Role", ROLES, index=role_idx, label_visibility="collapsed")

    # Reset selected topic when role changes
    role_topics = ROLE_TOPICS[role]
    if ss.selected_topic not in role_topics:
        ss.selected_topic = role_topics[0]

    # ── Topic grid ────────────────────────────────────────────────────────────
    st.markdown(f"#### 📚 Choose Topic  <span style='font-size:.75rem;color:var(--t3);font-weight:400;'>— {len(role_topics)} topics for {role}</span>", unsafe_allow_html=True)
    COLS = 4
    for row_start in range(0, len(role_topics), COLS):
        row_topics = role_topics[row_start: row_start + COLS]
        cols = st.columns(COLS)
        for col, topic in zip(cols, row_topics):
            with col:
                is_sel = (ss.selected_topic == topic)
                label = f"{get_topic_emoji(topic)} {topic}"
                if st.button(label, key=f"tp_{topic}",
                             type="primary" if is_sel else "secondary",
                             use_container_width=True):
                    ss.selected_topic = topic
                    st.rerun()

    # ── Difficulty ────────────────────────────────────────────────────────────
    st.markdown("#### ⚡ Difficulty")
    difficulty = st.select_slider("Difficulty", DIFFICULTIES,
                                  value=ss.difficulty, label_visibility="collapsed")
    st.caption(f"{get_difficulty_emoji(difficulty)} **{difficulty}** selected")

    # ── Question type + Mode ──────────────────────────────────────────────────
    col_qt, col_mode = st.columns(2)
    with col_qt:
        st.markdown("#### 🔢 Question Type")
        question_type = st.radio(
            "Question Type", ["MCQ", "Open-ended"],
            index=0 if ss.question_type == "MCQ" else 1,
            label_visibility="collapsed",
            help="MCQ: multiple choice  |  Open-ended: type your answer",
        )
    with col_mode:
        st.markdown("#### 🎮 Mode")
        mode = st.radio(
            "Mode", ["Practice Mode", "Mock Interview"],
            index=0 if ss.mode == "Practice Mode" else 1,
            label_visibility="collapsed",
            help="Practice: relaxed  |  Mock: timed per question",
        )

    adaptive = st.toggle("🔄 Adaptive Difficulty", value=ss.adaptive_difficulty)

    # ── Start buttons ─────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 Start Interview", type="primary", use_container_width=True):
            ss.role         = role
            ss.topic        = ss.selected_topic
            ss.difficulty   = difficulty
            ss.mode         = mode
            ss.adaptive_difficulty = adaptive
            ss.question_type = question_type
            _ensure_api()
            with st.spinner("Preparing your interview…"):
                _start_interview()
            ss.page = "interview"
            st.rerun()
    with c2:
        if st.button("🎲 Random Topic", use_container_width=True):
            rand_role_topics = ROLE_TOPICS[role]
            rand_topic       = random.choice(rand_role_topics)
            ss.selected_topic = rand_topic
            ss.role         = role
            ss.topic        = rand_topic
            ss.difficulty   = random.choice(DIFFICULTIES)
            ss.mode         = "Practice Mode"
            ss.adaptive_difficulty = adaptive
            ss.question_type = question_type
            _ensure_api()
            with st.spinner("Generating question…"):
                _start_interview()
            ss.page = "interview"
            st.rerun()


def _render_results_page() -> None:
    ss = st.session_state

    # Nav bar
    st.markdown("""
<div class="aip-header">
  <div class="aip-logo">🏆 Session Results</div>
  <div class="aip-sub">Your interview debrief</div>
</div>
""", unsafe_allow_html=True)

    c1, _, c3, c_theme = st.columns([1, 3, 1, 1])
    with c1:
        if st.button("🏠 Home"):
            ss.page = "home"; st.rerun()
    with c3:
        if st.button("🔄 New Interview", type="primary"):
            ss.page = "setup"; st.rerun()
    with c_theme:
        icon = "☀️" if ss.theme == "dark" else "🌙"
        if st.button(icon, key="_res_theme", help="Toggle dark / light mode", use_container_width=True):
            ss.theme = "light" if ss.theme == "dark" else "dark"
            st.rerun()

    st.markdown("")

    # Find and render the summary card
    summary_msg = next(
        (m for m in reversed(ss.messages) if m.get("type") == "summary"), None
    )
    if summary_msg:
        _render_summary_msg(summary_msg)
    else:
        st.info("No summary available.")

    # Per-question breakdown
    if ss.qa_history:
        st.markdown("### 📋 Question Breakdown")
        for i, qa in enumerate(ss.qa_history):
            ev = qa.get("evaluation", {})
            score = qa.get("score", 0)
            label = get_score_label(score)
            emoji = get_score_emoji(score)
            with st.expander(f"{emoji} Q{i+1} — Score {score}/10 · {label} — {qa['question'][:70]}…"):
                _render_evaluation_msg({
                    "evaluation": ev,
                    "score": score,
                    "question_num": i + 1,
                    "time_exceeded": False,
                    "diff_note": "",
                })

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔄 Start New Interview", type="primary", use_container_width=True):
            ss.page = "setup"; st.rerun()
    with c2:
        if st.button("🏠 Back to Home", use_container_width=True):
            ss.page = "home"; st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
#  WELCOME SCREEN  (used by home page)
# ─────────────────────────────────────────────────────────────────────────────

def _render_welcome_screen() -> None:
    st.markdown("""
<div class="hero-wrap">
  <div class="hero-inner">
    <div class="hero-eyebrow">AI-Powered · Adaptive · Real-time Feedback</div>
    <h2 class="hero-h1">Ace Your Next<br><span>Technical Interview</span></h2>
    <p class="hero-sub">
      Your personal AI interviewer asks questions, scores your answers out of 10,
      identifies gaps, and provides expert model answers — all in real time.
    </p>
    <div class="hero-chips">
      <span class="hero-chip">💻 Operating Systems</span>
      <span class="hero-chip">🌳 DSA</span>
      <span class="hero-chip">🤖 AI / ML</span>
      <span class="hero-chip">⚡ Instant feedback</span>
      <span class="hero-chip">🔄 Adaptive difficulty</span>
      <span class="hero-chip">🏆 Session debrief</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    cards = [
        ("💻", "3 Topics", ["Operating Systems", "Data Structures & Algorithms", "Artificial Intelligence / ML"]),
        ("🎮", "Two Modes",  ["Practice — learn without pressure", "Mock Interview — timed questions", "Adaptive difficulty auto-adjusts"]),
        ("📊", "Smart Feedback", ["Score out of 10 per answer", "Strengths & missing concepts", "Expert model answer", "Dynamic follow-up questions"]),
    ]
    cols = st.columns(3)
    for col, (icon, title, items) in zip(cols, cards):
        with col:
            li = "".join(f"<li>{i}</li>" for i in items)
            st.markdown(f"""
<div class="fc">
  <span class="fc-icon">{icon}</span>
  <div class="fc-title">{title}</div>
  <ul class="fc-list">{li}</ul>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div class="tips" style="margin-top:.8rem;">
  💡 During the interview: press <kbd>hint</kbd> for a clue &nbsp;·&nbsp;
  <kbd>skip</kbd> to move on &nbsp;·&nbsp;
  click <strong>End Session</strong> in the sidebar for your full debrief
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  INPUT BAR
# ─────────────────────────────────────────────────────────────────────────────

def _render_input_bar() -> None:
    ss = st.session_state

    if ss.question_type == "MCQ":
        # ── MCQ mode: show A/B/C/D option buttons ──────────────────────────
        mcq = ss.current_mcq_data
        if mcq and mcq.get("options"):
            opts = mcq["options"]
            letters = list(opts.keys())

            # Two rows of 2 buttons
            r1c1, r1c2 = st.columns(2)
            r2c1, r2c2 = st.columns(2)
            btn_cols = [r1c1, r1c2, r2c1, r2c2]

            for col, letter in zip(btn_cols, letters):
                label = f"**{letter})** {opts[letter]}"
                with col:
                    if st.button(label, key=f"mcq_opt_{letter}",
                                 use_container_width=True):
                        _process_mcq_answer(letter)
                        st.rerun()

        # Skip still available for MCQ
        st.markdown("<div style='margin-top:.3rem'></div>", unsafe_allow_html=True)
        if st.button("⏭️ Skip Question", use_container_width=True):
            _handle_skip_mcq(); st.rerun()
    else:
        # ── Open-ended mode: original hint/skip + text input ───────────────
        c1, c2 = st.columns(2)
        with c1:
            if st.button("💡 Get Hint", use_container_width=True):
                _handle_hint(); st.rerun()
        with c2:
            if st.button("⏭️ Skip Question", use_container_width=True):
                _handle_skip(); st.rerun()

        answer = st.chat_input("Type your answer here…  (or type 'hint' / 'skip')")
        if answer:
            _process_input(answer); st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
#  END SCREEN
# ─────────────────────────────────────────────────────────────────────────────

def _render_end_screen() -> None:
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔄 Start New Interview", type="primary", use_container_width=True):
            st.session_state.phase = "setup"; st.rerun()
    with c2:
        st.markdown(
            '<div class="end-tip">📜 Scroll up to read your full debrief</div>',
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    _load_css()
    _init_state()
    _apply_theme()

    if st.session_state.api_key and not st.session_state.interviewer:
        _init_api(st.session_state.api_key)

    page = st.session_state.get("page", "home")

    if page == "home":
        _hide_sidebar()
        _render_home_page()

    elif page == "setup":
        _hide_sidebar()
        _render_setup_page()

    elif page == "interview":
        st.markdown("""
<div class="aip-header">
  <div class="aip-logo">🎯 InterviewAI</div>
  <div class="aip-sub">Technical Interview Practice · AI-Powered · Adaptive</div>
</div>
""", unsafe_allow_html=True)
        _render_sidebar()
        _render_chat()
        if st.session_state.phase == "active":
            _render_input_bar()

    elif page == "results":
        _hide_sidebar()
        _render_results_page()


if __name__ == "__main__":
    main()
