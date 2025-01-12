import json
import sqlite3
from db import get_connection
from utility.utility import (
    _set_headers
)
import bcrypt


def handle_login(handler):
    """
    POST /login
    JSON: {"username":"...","password":"..."}
    Verifica l'utente e controlla l'hash della password
    """
    content_length = int(handler.headers.get("Content-Length", 0))
    body = handler.rfile.read(content_length).decode("utf-8")

    try:
        data = json.loads(body)
        username = data["username"]
        password = data["password"]
    except (json.JSONDecodeError, KeyError):
        error_bytes = json.dumps({"error": "JSON non valido o campi mancanti"}).encode("utf-8")
        _set_headers(handler, 400, error_bytes)
        handler.wfile.write(error_bytes)
        return

    # 1) Cerchiamo l'utente in base a 'username'
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT id, username, password, email
            FROM users
            WHERE username = ?
        """, (username,))  # NOT password
        row = c.fetchone()

    if row is None:
        # Se l'utente non esiste
        error_response = json.dumps({"error": "Utente inesistente"}).encode("utf-8")
        _set_headers(handler, 401, error_response)
        handler.wfile.write(error_response)
        return

    user_id, db_username, db_hashed_pw, email = row

    # 2) Verifica password con bcrypt
    #    db_hashed_pw = hash salvato (stringa tipo "$2b$12$...")
    if bcrypt.checkpw(password.encode("utf-8"), db_hashed_pw.encode("utf-8")):
        # Password corretta
        user_obj = {
            "id": user_id,
            "username": db_username,
            "email": email,
            "message": "Login effettuato con successo"
        }
        response_data = json.dumps(user_obj).encode("utf-8")
        _set_headers(handler, 200, response_data)
        handler.wfile.write(response_data)
    else:
        # Password errata
        error_response = json.dumps({"error": "Username o password errati"}).encode("utf-8")
        _set_headers(handler, 401, error_response)
        handler.wfile.write(error_response)

def handle_get_all_users(handler):
    """GET /users - Ritorna tutti gli utenti."""
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT id, username, password, email FROM users")
        rows = c.fetchall()
    
    results = []
    for row in rows:
        results.append({
            "id": row[0],
            "username": row[1],
            "password": row[2],  
            "email": row[3]
        })

    response_data = json.dumps(results).encode("utf-8")

    _set_headers(handler, 200, response_data)
    handler.wfile.write(response_data)

def handle_get_user_by_id(handler, user_id):
    """GET /users/<id> - Ritorna il singolo utente se esiste."""
    try:
        user_id = int(user_id)
    except ValueError:
        error_response = json.dumps({"error": "ID non valido"}).encode("utf-8")
        _set_headers(handler, 400, error_response)
        handler.wfile.write(error_response)
        return
    
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT id, username, password, email FROM users WHERE id = ?", (user_id,))
        row = c.fetchone()
    
    if row:
        result = {
            "id": row[0],
            "username": row[1],
            "password": row[2],  
            "email": row[3]
        }
        response_data = json.dumps(result).encode("utf-8")

        _set_headers(handler, 200, response_data)
        handler.wfile.write(response_data)
    else:
        error_response = json.dumps({"error": "User non trovato"}).encode("utf-8")
        _set_headers(handler, 404, error_response)
        handler.wfile.write(error_response)
    

def handle_create_user(handler):
    """POST /users - Crea un nuovo utente nel DB."""
    content_length = int(handler.headers.get("Content-Length", 0))
    body = handler.rfile.read(content_length).decode("utf-8")
    
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        error_response = json.dumps({"error": "JSON non valido"}).encode("utf-8")
        _set_headers(handler, 400, error_response)
        handler.wfile.write(error_response)
        return

    # dati utente
    username = data.get("username", "")
    # password in chiaro
    password = data.get("password", "")
    email = data.get("email", "")

    # Hash password tramite bcrypt
    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    with get_connection() as conn:
        c = conn.cursor()
        try:
            c.execute("""
                INSERT INTO users (username, password, email)
                VALUES (?, ?, ?)
            """, (username, hashed_pw, email))
            conn.commit()
            new_id = c.lastrowid
        except sqlite3.IntegrityError as e:
            # Se viola UNIQUE su username o email
            error_response = json.dumps({"error": f"Violazione di unicità: {str(e)}"}).encode("utf-8")
            _set_headers(handler, 400, error_response)
            handler.wfile.write(error_response)
            return
    
    new_user = {
        "id": new_id,
        "username": username,
        "email": email
    }
    response_data = json.dumps(new_user).encode("utf-8")

    _set_headers(handler, 201, response_data)
    handler.wfile.write(response_data)

def handle_update_user(handler, user_id):
    """PUT /users/<id> - Aggiorna i campi di un utente (username, password, email)."""
    try:
        user_id = int(user_id)
    except ValueError:
        error_response = json.dumps({"error": "ID non valido"}).encode("utf-8")
        _set_headers(handler, 400, error_response)
        handler.wfile.write(error_response)
        return
    
    content_length = int(handler.headers.get("Content-Length", 0))
    body = handler.rfile.read(content_length).decode("utf-8")

    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        error_response = json.dumps({"error": "JSON non valido"}).encode("utf-8")
        _set_headers(handler, 400, error_response)
        handler.wfile.write(error_response)
        return

    # campi aggiornabili
    username = data.get("username", None)
    new_password = data.get("password", None)  # se presente, lo hashiamo
    email = data.get("email", None)

    with get_connection() as conn:
        c = conn.cursor()
        # Verifichiamo se l'utente esiste
        c.execute("SELECT id, username, password, email FROM users WHERE id = ?", (user_id,))
        row = c.fetchone()
        if not row:
            error_response = json.dumps({"error": "Utente non trovato"}).encode("utf-8")
            _set_headers(handler, 404, error_response)
            handler.wfile.write(error_response)
            return

        existing_id, existing_username, existing_hashed_pw, existing_email = row

        # Se i campi non sono presenti nel JSON, manteniamo quelli esistenti
        updated_username = username if username is not None else existing_username
        updated_email = email if email is not None else existing_email

        # Se la password è presente, la hashiamo con bcrypt; altrimenti, manteniamo l'hash esistente
        if new_password is not None and len(new_password) > 0:
            hashed_pw = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        else:
            hashed_pw = existing_hashed_pw

        # TENTIAMO l'aggiornamento nel DB
        try:
            c.execute("""
                UPDATE users
                SET username = ?, password = ?, email = ?
                WHERE id = ?
            """, (updated_username, hashed_pw, updated_email, user_id))
            conn.commit()
        except sqlite3.IntegrityError as e:
            # Se scatta errore di UNIQUE su username o email
            error_response = json.dumps({"error": f"Violazione di unicità: {str(e)}"}).encode("utf-8")
            _set_headers(handler, 400, error_response)
            handler.wfile.write(error_response)
            return

    updated_user = {
        "id": user_id,
        "username": updated_username,
        "email": updated_email,
        # Non mostrare la password in chiaro
        # "password": hashed_pw 
    }
    response_data = json.dumps(updated_user).encode("utf-8")
    _set_headers(handler, 200, response_data)
    handler.wfile.write(response_data)

def handle_delete_user(handler, user_id):
    """DELETE /users/<id> - Elimina l'utente dal DB."""
    try:
        user_id = int(user_id)
    except ValueError:
        error_response = json.dumps({"error": "Invalid ID"}).encode("utf-8")
        _set_headers(handler, 400, error_response)
        handler.wfile.write(error_response)
        return

    with get_connection() as conn:
        c = conn.cursor()
        # Controlliamo se l'utente esiste
        c.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        row = c.fetchone()
        if not row:
            error_response = json.dumps({"error": "User not found"}).encode("utf-8")
            _set_headers(handler, 404, error_response)
            handler.wfile.write(error_response)
            return

        c.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
    response_data = json.dumps({"message": f"User {user_id} deleted"}).encode("utf-8")
    _set_headers(handler, 200, response_data)
    handler.wfile.write(response_data)
