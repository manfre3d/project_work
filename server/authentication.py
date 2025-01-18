import json
from db import get_connection
from utility.utility import set_headers
from utility.session import get_user_id_from_session


def authenticate(handler):
    """Verifica la sessione dell'utente."""
    with get_connection() as conn:
        c = conn.cursor()
        cookies = handler.headers.get("Cookie")
        if not cookies:
            return None
        session_id = None
        for cookie in cookies.split(";"):
            if "session_id=" in cookie:
                session_id = cookie.strip().split("session_id=")[1]
                break
        if not session_id:
            return None
        user_id = get_user_id_from_session(session_id)
        if not user_id:
            return None
        # recuprera i dettagli dell'utente tramite l'id della sessione sfruttando la relazione delle tabelle a db
        c.execute("SELECT id, username, email, role FROM users WHERE id = ?", (user_id,))
        row = c.fetchone()
        if row:
            return {
                "id": row["id"],
                "username": row["username"],
                "email": row["email"],
                "role": row["role"]
            }
        return None

def verify_authentication(handler):
    """
    Verifica se l'utente è autenticato. Se l'autenticazione fallisce, invia una risposta di errore 401.
    Returns:
        dict: Un dizionario contenente i dettagli dell'utente autenticato se l'autenticazione ha successo.
        None: Se l'autenticazione fallisce.
    """
    
    authenticated_user = authenticate(handler)
    
    if not authenticated_user:
        error_response = json.dumps({"error": "E' necessario autenticarsi!"}).encode("utf-8")
        set_headers(handler, 401, error_response)
        handler.wfile.write(error_response)
        handler.close_connection = True
        return None
    
    return authenticated_user