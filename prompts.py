"""
prompts.py — All Claude prompt templates for the AI Interview Chatbot.
Centralised here so they are easy to tune without touching logic files.
"""

# ──────────────────────────────────────────────────────────────────────────────
# QUESTION GENERATION
# ──────────────────────────────────────────────────────────────────────────────

QUESTION_GENERATION_PROMPT = """Generate a single {difficulty} level technical interview question about "{topic}" for a {role} candidate.

Difficulty guidelines:
- Easy   : Definitions, basic concepts, simple examples (suitable for juniors)
- Medium : Applied knowledge, trade-offs, design decisions (mid-level)
- Hard   : Complex scenarios, optimisation, system-level thinking (senior)

Previously asked questions — do NOT repeat these:
{previous_questions}

Rules:
• Ask exactly ONE question
• Be specific and unambiguous
• Do NOT include the answer or any hints
• Do NOT number the question or add a preamble

Return only the question text."""


# ──────────────────────────────────────────────────────────────────────────────
# ANSWER EVALUATION
# ──────────────────────────────────────────────────────────────────────────────

EVALUATION_PROMPT = """You are an expert senior technical interviewer evaluating a candidate's answer.

Interview context:
- Role        : {role}
- Topic       : {topic}
- Difficulty  : {difficulty}

Question asked:
{question}

Candidate's answer:
{answer}

Evaluate thoroughly. Return a JSON object with EXACTLY this structure (no extra text):
{{
    "score": <integer 1-10>,
    "brief_verdict": "<one-sentence overall assessment>",
    "strengths": [
        "<specific strength 1>",
        "<specific strength 2>"
    ],
    "missing_concepts": [
        "<important concept not mentioned>",
        "<another gap if any>"
    ],
    "detailed_feedback": "<3-4 sentences of constructive, specific feedback>",
    "ideal_answer": "<comprehensive model answer covering all key points a strong candidate should mention>",
    "should_follow_up": <true | false>,
    "follow_up_question": "<a follow-up that probes deeper, or null>"
}}

Scoring rubric:
  1-2 : Completely wrong or no meaningful content
  3-4 : Major misconceptions, missing core concepts
  5-6 : Basic understanding but significant gaps
  7-8 : Good answer with minor omissions
  9-10: Excellent — comprehensive, shows mastery

IMPORTANT: Return ONLY the JSON object, nothing else."""


# ──────────────────────────────────────────────────────────────────────────────
# HINTS
# ──────────────────────────────────────────────────────────────────────────────

HINT_PROMPT = """A candidate is struggling with the following interview question and needs a hint.

Topic      : {topic}
Difficulty : {difficulty}
Question   : {question}

Write a helpful hint that:
1. Points toward the right approach without revealing the answer
2. Mentions one key concept or keyword to think about
3. Is encouraging and supportive
4. Is no more than 2-3 sentences long

Return only the hint text — no preamble, no labels."""


# ──────────────────────────────────────────────────────────────────────────────
# MCQ GENERATION
# ──────────────────────────────────────────────────────────────────────────────

MCQ_GENERATION_PROMPT = """Generate a {difficulty} level multiple-choice question about "{topic}" for a {role} candidate.

Previously asked questions — do NOT repeat:
{previous_questions}

Return ONLY a valid JSON object with EXACTLY this structure (no markdown, no extra text):
{{
    "question": "<clear question text>",
    "options": {{
        "A": "<option A — 1 sentence max>",
        "B": "<option B — 1 sentence max>",
        "C": "<option C — 1 sentence max>",
        "D": "<option D — 1 sentence max>"
    }},
    "correct": "<single letter: A, B, C, or D>",
    "explanation": "<2-3 sentences: why the correct answer is right and what's wrong with the closest distractor>"
}}

Rules:
• Exactly one correct answer
• All 3 wrong options must be plausible — no obviously silly distractors
• Easy: definitions and basic recall
• Medium: application and trade-offs
• Hard: nuanced edge cases and system-level thinking
• For Behavioral topic: make it a scenario MCQ with 4 response strategies

Return ONLY the JSON object."""


# ──────────────────────────────────────────────────────────────────────────────
# FOLLOW-UP QUESTION
# ──────────────────────────────────────────────────────────────────────────────

FOLLOW_UP_PROMPT = """Generate a follow-up interview question based on the candidate's previous answer.

Topic            : {topic}
Difficulty       : {difficulty}
Original question: {previous_question}
Candidate answer : {previous_answer}
Key gaps noted   : {missing_concepts}

The follow-up should:
• Probe deeper into something the candidate touched on, OR address a key gap
• Be at {difficulty} level or slightly higher
• Feel like a natural continuation of the conversation

Return ONLY the follow-up question text."""


# ──────────────────────────────────────────────────────────────────────────────
# SESSION SUMMARY
# ──────────────────────────────────────────────────────────────────────────────

SESSION_SUMMARY_PROMPT = """Generate a comprehensive interview session debrief for a candidate.

Session details:
- Target role       : {role}
- Topic covered     : {topic}
- Questions answered: {questions_count}
- Average score     : {avg_score}/10
- Score trend       : {score_trend}

Question-by-question performance:
{qa_history}

Provide a professional debrief using this exact structure:

## Overall Performance
[2-3 sentences assessing the session as a whole]

## Key Strengths Demonstrated
- [Strength 1 with a concrete example from the session]
- [Strength 2]
- [Strength 3]

## Areas for Improvement
- [Area 1 with specific, actionable advice]
- [Area 2]
- [Area 3]

## Recommended Study Topics
- [Topic 1 — what to review and why]
- [Topic 2]
- [Topic 3]

## Interview Readiness
[Final verdict: "Strong Candidate 🏆", "Needs More Preparation 📚", or "Keep Practising 🔄" — with a brief explanation]

Be specific, actionable, and encouraging throughout."""


# ──────────────────────────────────────────────────────────────────────────────
# WELCOME MESSAGE TEMPLATES
# ──────────────────────────────────────────────────────────────────────────────

WELCOME_MESSAGE = """👋 Welcome to your **{topic}** interview session!

**Your Setup:**
- 🎯 Role       : {role}
- 📚 Topic      : {topic}
- ⚡ Difficulty : {difficulty}
- 🎮 Mode       : {mode}

{mode_instructions}

I'll ask questions one at a time and give you detailed feedback after each answer.

💡 **Quick commands:**
- Type `hint` → get a clue without the answer
- Type `skip` → move to the next question
- Click **End Session** in the sidebar for your full debrief

Let's go! Here is your first question:"""

PRACTICE_MODE_INSTRUCTIONS = (
    "📝 **Practice Mode** — No time pressure. Focus on understanding and learning."
)

MOCK_MODE_INSTRUCTIONS = (
    "⏱️ **Mock Interview Mode** — You have **{time_limit} minute(s)** per question. "
    "Simulate real interview conditions and answer under pressure!"
)
