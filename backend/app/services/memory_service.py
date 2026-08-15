import sqlite3
from datetime import datetime, timedelta, timezone
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
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel TEXT NOT NULL,
            text TEXT NOT NULL,
            intent_type TEXT,
            success INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            label TEXT,
            content TEXT NOT NULL,
            source TEXT NOT NULL,
            expires_at TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS preferences (
            person TEXT NOT NULL,
            key TEXT NOT NULL,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            PRIMARY KEY (person, key)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS favorite_devices (
            person TEXT PRIMARY KEY,
            entity_id TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            notified INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
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


# Preferências estruturadas (Fase 6.3) — diferente do "summary" narrativo
# do LLM em `profiles`: aqui é chave/valor explícito, pensado pra código
# ler direto (voz do TTS, unidade de temperatura, etc.), não pra virar
# texto solto no contexto do LLM.

def set_preference(person: str, key: str, value: str):
    conn = _connect()
    try:
        conn.execute(
            """
            INSERT INTO preferences (person, key, value, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(person, key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at
            """,
            (person, key, value, datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
    finally:
        conn.close()


def get_preference(person: str, key: str, default=None):
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT value FROM preferences WHERE person = ? AND key = ?",
            (person, key),
        ).fetchone()
        return row[0] if row else default
    finally:
        conn.close()


def get_all_preferences(person: str):
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT key, value FROM preferences WHERE person = ?",
            (person,),
        ).fetchall()
        return {key: value for key, value in rows}
    finally:
        conn.close()


# Dispositivo favorito (Fase 6.4) — um por pessoa, é o que "liga ela"/
# "desliga ele" usa como fallback quando não há contexto de conversa
# recente (ver PRONOUNS em intent_engine.py). Um por pessoa, não uma
# lista, pelo mesmo exemplo que motivou o pedido ("liga ela" = a TV).

def set_favorite_device(person: str, entity_id: str):
    conn = _connect()
    try:
        conn.execute(
            """
            INSERT INTO favorite_devices (person, entity_id, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(person) DO UPDATE SET entity_id = excluded.entity_id, updated_at = excluded.updated_at
            """,
            (person, entity_id, datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
    finally:
        conn.close()


def get_favorite_device(person: str):
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT entity_id FROM favorite_devices WHERE person = ?",
            (person,),
        ).fetchone()
        return row[0] if row else None
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


def log_activity(channel: str, text: str, intent_type: str | None, success: bool):
    """Registra todo comando processado pelo Fred (voz, whatsapp, web),
    independente de ter passado pelo LLM ou por um intent estruturado —
    usado só pro dashboard mostrar histórico/estatísticas, nunca deve
    impedir uma resposta de ser retornada (ver chamada em fred_service.py)."""

    if not text:
        return
    conn = _connect()
    try:
        conn.execute(
            "INSERT INTO activity (channel, text, intent_type, success, created_at) VALUES (?, ?, ?, ?, ?)",
            (channel, text[:500], intent_type, 1 if success else 0, datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
    finally:
        conn.close()


def get_recent_activity(limit: int = 10):
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT channel, text, intent_type, success, created_at FROM activity ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [
            {
                "channel": channel,
                "text": text,
                "intent_type": intent_type,
                "success": bool(success),
                "created_at": created_at,
            }
            for channel, text, intent_type, success, created_at in rows
        ]
    finally:
        conn.close()


KNOWLEDGE_STOPWORDS = {
    "qual", "quais", "quanto", "quanta", "quantos", "quantas",
    "quem", "que", "foi", "era", "é", "significa", "sobre",
    "esta", "está", "de", "da", "do", "das", "dos",
    "no", "na", "nos", "nas", "um", "uma", "e", "o", "a",
    "me", "fala", "pesquisar", "pesquisa",
}


def add_knowledge(category: str, content: str, label: str | None = None, source: str = "manual", expires_at: str | None = None):
    conn = _connect()
    try:
        now = datetime.now(timezone.utc).isoformat()
        cur = conn.execute(
            "INSERT INTO knowledge (category, label, content, source, expires_at, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (category, label, content, source, expires_at, now, now),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def list_knowledge(category: str | None = None):
    conn = _connect()
    try:
        if category:
            rows = conn.execute(
                "SELECT id, category, label, content, source, expires_at, created_at, updated_at FROM knowledge WHERE category = ? ORDER BY id DESC",
                (category,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, category, label, content, source, expires_at, created_at, updated_at FROM knowledge ORDER BY id DESC"
            ).fetchall()
        return [_knowledge_row_to_dict(row) for row in rows]
    finally:
        conn.close()


def update_knowledge(knowledge_id: int, label: str | None = None, content: str | None = None):
    conn = _connect()
    try:
        current = conn.execute(
            "SELECT label, content FROM knowledge WHERE id = ?", (knowledge_id,)
        ).fetchone()
        if not current:
            return None
        new_label = label if label is not None else current[0]
        new_content = content if content is not None else current[1]
        conn.execute(
            "UPDATE knowledge SET label = ?, content = ?, updated_at = ? WHERE id = ?",
            (new_label, new_content, datetime.now(timezone.utc).isoformat(), knowledge_id),
        )
        conn.commit()
        return knowledge_id
    finally:
        conn.close()


def delete_knowledge(knowledge_id: int):
    conn = _connect()
    try:
        conn.execute("DELETE FROM knowledge WHERE id = ?", (knowledge_id,))
        conn.commit()
    finally:
        conn.close()


def search_knowledge(query: str, limit: int = 3):
    if not query:
        return []
    words = [
        word
        for word in query.lower().split()
        if len(word) > 2 and word not in KNOWLEDGE_STOPWORDS
    ]
    if not words:
        return []

    now = datetime.now(timezone.utc).isoformat()
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT id, category, label, content, source, expires_at, created_at, updated_at "
            "FROM knowledge WHERE expires_at IS NULL OR expires_at > ?",
            (now,),
        ).fetchall()
    finally:
        conn.close()

    scored = []
    for row in rows:
        label = (row[2] or "").lower()
        content = row[3].lower()
        score = 0
        for word in words:
            if word in label:
                score += 2
            if word in content:
                score += 1
        if score > 0:
            scored.append((score, row))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [_knowledge_row_to_dict(row) for _, row in scored[:limit]]


def _knowledge_row_to_dict(row):
    return {
        "id": row[0],
        "category": row[1],
        "label": row[2],
        "content": row[3],
        "source": row[4],
        "expires_at": row[5],
        "created_at": row[6],
        "updated_at": row[7],
    }


def get_activity_stats(hours: int = 24):
    since = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT channel, COUNT(*) FROM activity WHERE created_at >= ? GROUP BY channel",
            (since,),
        ).fetchall()
        by_channel = {channel: count for channel, count in rows}
        return {
            "since_hours": hours,
            "total": sum(by_channel.values()),
            "by_channel": by_channel,
        }
    finally:
        conn.close()


def add_reminder(date: str, name: str, description: str | None = None):
    conn = _connect()
    try:
        cur = conn.execute(
            "INSERT INTO reminders (date, name, description, notified, created_at) VALUES (?, ?, ?, 0, ?)",
            (date, name, description, datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def list_reminders():
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT id, date, name, description, notified, created_at FROM reminders ORDER BY date"
        ).fetchall()
        return [_reminder_row_to_dict(row) for row in rows]
    finally:
        conn.close()


def update_reminder(reminder_id: int, date: str | None = None, name: str | None = None, description: str | None = None):
    conn = _connect()
    try:
        current = conn.execute(
            "SELECT date, name, description FROM reminders WHERE id = ?", (reminder_id,)
        ).fetchone()
        if not current:
            return None
        new_date = date if date is not None else current[0]
        new_name = name if name is not None else current[1]
        new_description = description if description is not None else current[2]
        conn.execute(
            "UPDATE reminders SET date = ?, name = ?, description = ? WHERE id = ?",
            (new_date, new_name, new_description, reminder_id),
        )
        conn.commit()
        return reminder_id
    finally:
        conn.close()


def delete_reminder(reminder_id: int):
    conn = _connect()
    try:
        conn.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
        conn.commit()
    finally:
        conn.close()


def get_due_reminders(date: str):
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT id, date, name, description, notified, created_at FROM reminders WHERE date = ? AND notified = 0",
            (date,),
        ).fetchall()
        return [_reminder_row_to_dict(row) for row in rows]
    finally:
        conn.close()


def mark_reminder_notified(reminder_id: int):
    conn = _connect()
    try:
        conn.execute("UPDATE reminders SET notified = 1 WHERE id = ?", (reminder_id,))
        conn.commit()
    finally:
        conn.close()


def _reminder_row_to_dict(row):
    return {
        "id": row[0],
        "date": row[1],
        "name": row[2],
        "description": row[3],
        "notified": bool(row[4]),
        "created_at": row[5],
    }
