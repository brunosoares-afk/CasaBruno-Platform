import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "fred_conversations.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

PROFILE_UPDATE_EVERY = 4  # turns do usuário entre atualizações de perfil
RECENT_TURNS_LIMIT = 6


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person TEXT NOT NULL,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS profiles (
            person TEXT PRIMARY KEY,
            summary TEXT,
            turn_count INTEGER NOT NULL DEFAULT 0,
            updated_at TEXT
        )
        """
    )
    return conn


def log_turn(person: str, role: str, message: str):
    if not person or not message:
        return
    conn = _connect()
    try:
        conn.execute(
            "INSERT INTO conversations (person, role, message, created_at) VALUES (?, ?, ?, ?)",
            (person, role, message, datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
    finally:
        conn.close()


def get_recent_turns(person: str, limit: int = RECENT_TURNS_LIMIT):
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT role, message FROM conversations WHERE person = ? ORDER BY id DESC LIMIT ?",
            (person, limit),
        ).fetchall()
        return list(reversed(rows))
    finally:
        conn.close()


def get_profile(person: str):
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT summary, turn_count FROM profiles WHERE person = ?",
            (person,),
        ).fetchone()
        if row:
            return {"summary": row[0], "turn_count": row[1]}
        return {"summary": None, "turn_count": 0}
    finally:
        conn.close()


def _increment_turn_count(person: str) -> int:
    conn = _connect()
    try:
        conn.execute(
            """
            INSERT INTO profiles (person, summary, turn_count, updated_at)
            VALUES (?, NULL, 1, ?)
            ON CONFLICT(person) DO UPDATE SET turn_count = turn_count + 1
            """,
            (person, datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
        row = conn.execute(
            "SELECT turn_count FROM profiles WHERE person = ?", (person,)
        ).fetchone()
        return row[0] if row else 0
    finally:
        conn.close()


def save_profile_summary(person: str, summary: str):
    conn = _connect()
    try:
        conn.execute(
            """
            INSERT INTO profiles (person, summary, turn_count, updated_at)
            VALUES (?, ?, 0, ?)
            ON CONFLICT(person) DO UPDATE SET summary = excluded.summary, updated_at = excluded.updated_at
            """,
            (person, summary, datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
    finally:
        conn.close()


def register_turn_and_maybe_summarize(person: str, user_message: str, fred_message: str, summarizer):
    """Registra a pergunta+resposta e, a cada N turnos, pede pro LLM
    atualizar o resumo de perfil da pessoa. `summarizer` é uma função
    (person, old_summary, recent_turns) -> novo resumo (str)."""

    log_turn(person, "user", user_message)
    log_turn(person, "fred", fred_message)

    turn_count = _increment_turn_count(person)

    if turn_count > 0 and turn_count % PROFILE_UPDATE_EVERY == 0:
        try:
            profile = get_profile(person)
            recent = get_recent_turns(person, limit=PROFILE_UPDATE_EVERY * 2)
            new_summary = summarizer(person, profile.get("summary"), recent)
            if new_summary:
                save_profile_summary(person, new_summary)
        except Exception:
            pass
