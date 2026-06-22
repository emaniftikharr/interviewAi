"""
utils.py — Helper functions for formatting, scoring, and timing.
"""

import time


# ──────────────────────────────────────────────────────────────────────────────
# SCORE HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def get_score_emoji(score: int) -> str:
    """Return an emoji indicator for the given score."""
    if score >= 9:
        return "🌟"
    elif score >= 7:
        return "✅"
    elif score >= 5:
        return "🟡"
    elif score >= 3:
        return "⚠️"
    return "❌"


def get_score_color(score: int) -> str:
    """Return a hex colour string for the given score (used in inline CSS)."""
    if score >= 8:
        return "#00C851"   # green
    elif score >= 6:
        return "#FF8C00"   # orange
    elif score >= 4:
        return "#FF6600"   # dark-orange
    return "#FF4444"       # red


def get_score_label(score: int) -> str:
    """Return a short text label for the given score."""
    labels = {
        10: "Perfect!",
        9: "Excellent",
        8: "Great",
        7: "Good",
        6: "Above Average",
        5: "Average",
        4: "Below Average",
        3: "Needs Work",
        2: "Poor",
        1: "Very Poor",
        0: "No Answer",
    }
    return labels.get(score, "N/A")


def get_performance_badge(avg_score: float) -> tuple[str, str]:
    """Return (badge_label, hex_colour) based on the session average score."""
    if avg_score >= 8.5:
        return "🏆 Outstanding Candidate", "#FFD700"
    elif avg_score >= 7.0:
        return "⭐ Strong Candidate", "#00C851"
    elif avg_score >= 5.5:
        return "📈 Developing — Keep Practising", "#FF8C00"
    elif avg_score >= 4.0:
        return "📚 Needs More Preparation", "#FF6600"
    return "🔄 Keep Learning — Don't Give Up!", "#FF4444"


# ──────────────────────────────────────────────────────────────────────────────
# DIFFICULTY / TOPIC ICONS
# ──────────────────────────────────────────────────────────────────────────────

def get_difficulty_emoji(difficulty: str) -> str:
    return {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}.get(difficulty, "⚪")


def get_topic_emoji(topic: str) -> str:
    return {
        # Software Engineer
        "Data Structures":             "🗂️",
        "Algorithms":                  "⚙️",
        "Object-Oriented Programming": "🧱",
        "Complexity Analysis":         "📈",
        "System Design":               "🏗️",
        "Databases":                   "🗄️",
        "Networking & Web":            "🌐",
        "Version Control (Git)":       "🌿",
        "Testing":                     "🧪",
        "Operating Systems":           "💻",
        "Behavioral":                  "🎤",
        # AI/ML Engineer
        "Machine Learning":            "🤖",
        "Deep Learning":               "🧠",
        "Natural Language Processing": "💬",
        "Computer Vision":             "👁️",
        "Mathematics for ML":          "📐",
        "Data Preprocessing":          "🔧",
        "Model Evaluation & Metrics":  "📊",
        "Python & ML Libraries":       "🐍",
        "MLOps":                       "⚗️",
        # Backend Engineer
        "APIs & REST":                 "🔌",
        "Caching & Performance":       "⚡",
        "Authentication & Security":   "🔒",
        "Message Queues":              "📨",
        "Microservices":               "🔀",
        # Full Stack Engineer
        "Frontend Development":        "🎨",
        "Backend Development":         "🖥️",
        "Web Security":                "🛡️",
        "Performance Optimization":    "🚀",
        # Data Scientist
        "Statistics & Probability":    "📊",
        "Data Wrangling & EDA":        "🔍",
        "SQL & Databases":             "🗄️",
        "Python for Data Science":     "🐍",
        "Data Visualization":          "📉",
        "Feature Engineering":         "⚗️",
        "Big Data Tools":              "🌊",
        # Systems Engineer
        "Networking & Protocols":      "🌐",
        "C/C++ Programming":           "⚙️",
        "Memory Management":           "🧩",
        "Concurrency & Threads":       "🔀",
        "Embedded Systems":            "💾",
        "Performance & Profiling":     "📈",
        # DevOps Engineer
        "CI/CD Pipelines":             "🔄",
        "Containerization (Docker/K8s)":"🐳",
        "Cloud Platforms":             "☁️",
        "Infrastructure as Code":      "📝",
        "Networking & Security":       "🔐",
        "Monitoring & Observability":  "👀",
        "Scripting & Automation":      "🤖",
    }.get(topic, "📚")


# ──────────────────────────────────────────────────────────────────────────────
# TIMER
# ──────────────────────────────────────────────────────────────────────────────

def format_time_remaining(start_time: float, time_limit: int) -> tuple[int, str]:
    """
    Calculate remaining time.

    Returns
    -------
    (seconds_remaining, "MM:SS" string)
    """
    elapsed = int(time.time() - start_time)
    remaining = max(0, time_limit - elapsed)
    mins, secs = divmod(remaining, 60)
    return remaining, f"{mins:02d}:{secs:02d}"


# ──────────────────────────────────────────────────────────────────────────────
# STATISTICS
# ──────────────────────────────────────────────────────────────────────────────

def calculate_stats(scores: list[int]) -> dict:
    """Return a stats dict computed from a list of scores."""
    if not scores:
        return {"total": 0, "average": 0.0, "highest": 0, "lowest": 0, "trend": "N/A"}

    avg = sum(scores) / len(scores)

    # Trend: compare first half vs second half (needs ≥ 4 data points)
    if len(scores) >= 4:
        mid = len(scores) // 2
        first_avg = sum(scores[:mid]) / mid
        second_avg = sum(scores[mid:]) / (len(scores) - mid)
        if second_avg > first_avg + 0.5:
            trend = "Improving ↗"
        elif second_avg < first_avg - 0.5:
            trend = "Declining ↘"
        else:
            trend = "Stable →"
    else:
        trend = "N/A"

    return {
        "total": len(scores),
        "average": round(avg, 1),
        "highest": max(scores),
        "lowest": min(scores),
        "trend": trend,
    }


# ──────────────────────────────────────────────────────────────────────────────
# ADAPTIVE DIFFICULTY
# ──────────────────────────────────────────────────────────────────────────────

def should_increase_difficulty(scores: list[int], threshold: int = 7, window: int = 3) -> bool:
    """Return True if the last `window` scores are all >= threshold."""
    if len(scores) < window:
        return False
    return all(s >= threshold for s in scores[-window:])


def should_decrease_difficulty(scores: list[int], threshold: int = 4, window: int = 2) -> bool:
    """Return True if the last `window` scores are all <= threshold."""
    if len(scores) < window:
        return False
    return all(s <= threshold for s in scores[-window:])


# ──────────────────────────────────────────────────────────────────────────────
# FORMATTING
# ──────────────────────────────────────────────────────────────────────────────

def format_evaluation_as_markdown(evaluation: dict, question_num: int) -> str:
    """Convert an evaluation dict into a formatted markdown string for chat display."""
    score = evaluation.get("score", 0)
    emoji = get_score_emoji(score)
    label = get_score_label(score)

    strengths = evaluation.get("strengths") or []
    missing = evaluation.get("missing_concepts") or []

    strengths_text = "\n".join(f"  ✓ {s}" for s in strengths) or "  • None specifically identified."
    missing_text = "\n".join(f"  ✗ {m}" for m in missing) or "  • Nothing major missing — well done!"

    parts = [
        f"### {emoji} Feedback — Question {question_num}",
        f"**Score: {score}/10 — {label}**",
        "",
        f"📋 **Verdict:** {evaluation.get('brief_verdict', '')}",
        "",
        "**What you did well:**",
        strengths_text,
        "",
        "**Concepts to brush up on:**",
        missing_text,
        "",
        f"**Detailed Feedback:**\n{evaluation.get('detailed_feedback', '')}",
        "",
        f"**Model Answer:**\n{evaluation.get('ideal_answer', 'N/A')}",
    ]
    return "\n".join(parts)
