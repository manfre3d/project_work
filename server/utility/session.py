import uuid
from datetime import datetime, timedelta, timezone
from db import get_connection

def create_session(user_id, duration_minutes=60):
    """Crea una nuova sessione per l'utente e ritorna l'ID di sessione."""
    session_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc)
    expires_at = created_at + timedelta(minutes=duration_minutes)
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO sessions (session_id, user_id, created_at, expires_at)
            VALUES (?, ?, ?, ?)
        """, (session_id, user_id, created_at.strftime("%Y-%m-%d %H:%M:%S"), expires_at.strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
    return session_id

def get_session_id(handler):
    """
    Estrae il session_id dai cookie dell'handler.
    handler: Oggetto handler HTTP.
    Returns: session_id (str): Il valore del session_id se presente, altrimenti None.
    """
    cookies = handler.headers.get("Cookie")
    if not cookies:
        return None

    for cookie in cookies.split(";"):
        key, _, value = cookie.strip().partition("=")
        if key == "session_id":
            return value
    return None

def get_user_id_from_session(session_id):
    """restituisce l'ID dell'utente associato alla sessione se la sessione è valida, altrimenti None."""
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT user_id, expires_at FROM sessions WHERE session_id = ?
        """, (session_id,))
        row = c.fetchone()
        if row:
            expires_at = datetime.strptime(row["expires_at"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc) < expires_at:
                return row["user_id"]
            else:
                # eliminare la sessione scaduta 
                delete_session(session_id)
        return None

def delete_session(session_id):
    """Elimina la sessione dal database."""
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""
            DELETE FROM sessions WHERE session_id = ?
        """, (session_id,))
        conn.commit()

def clean_expired_sessions():
    """Elimina tutte le sessioni scadute dal database."""
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""
            DELETE FROM sessions WHERE expires_at < ?
        """, (datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),))
        conn.commit()

