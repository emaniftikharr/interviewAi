"""
history.py — SQLite-based session persistence for InterviewAI.
"""
import json
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path("interviewai_history.db")


def _conn() -> sqlite3.Connection:
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init_db() -> None:
    """Create tables on first run."""
    with _conn() as c:
        c.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            role       TEXT    NOT NULL,
            topic      TEXT    NOT NULL,
            difficulty TEXT    NOT NULL,
            mode       TEXT    NOT NULL,
            avg_score  REAL    NOT NULL,
            total_qs   INTEGER NOT NULL,
            scores     TEXT    NOT NULL,
            created_at TEXT    NOT NULL
        )""")
        c.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL REFERENCES sessions(id),
            q_num      INTEGER NOT NULL,
            question   TEXT    NOT NULL,
            answer     TEXT    NOT NULL,
            score      INTEGER NOT NULL,
            evaluation TEXT    NOT NULL
        )""")
        c.commit()


def save_session(role: str, topic: str, difficulty: str, mode: str,
                 scores: list, qa_history: list) -> int:
    """Persist a completed session; return its new ID."""
    avg = round(sum(scores) / len(scores), 2) if scores else 0.0
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    with _conn() as c:
        cur = c.execute(
            "INSERT INTO sessions (role,topic,difficulty,mode,avg_score,total_qs,scores,created_at)"
            " VALUES (?,?,?,?,?,?,?,?)",
            (role, topic, difficulty, mode, avg, len(scores), json.dumps(scores), now),
        )
        sid = cur.lastrowid
        for qa in qa_history:
            c.execute(
                "INSERT INTO questions (session_id,q_num,question,answer,score,evaluation)"
                " VALUES (?,?,?,?,?,?)",
                (sid, qa.get("question_num", 0), qa["question"],
                 qa["answer"], qa["score"], json.dumps(qa.get("evaluation", {}))),
            )
        c.commit()
    return sid


def load_sessions(limit: int = 50) -> list[dict]:
    """Return recent sessions, newest first."""
    with _conn() as c:
        rows = c.execute(
            "SELECT * FROM sessions ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


def get_topic_stats() -> list[dict]:
    """Return avg score grouped by (topic, difficulty) for the heatmap."""
    with _conn() as c:
        rows = c.execute("""
            SELECT topic, difficulty,
                   ROUND(AVG(avg_score), 1) AS avg,
                   COUNT(*) AS sessions
            FROM sessions
            GROUP BY topic, difficulty
        """).fetchall()
    return [dict(r) for r in rows]


def delete_session(session_id: int) -> None:
    with _conn() as c:
        c.execute("DELETE FROM questions WHERE session_id = ?", (session_id,))
        c.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        c.commit()
