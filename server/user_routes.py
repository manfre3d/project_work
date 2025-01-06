import json
from db import get_connection
from utility import (
    _set_headers
)


def handle_login(handler):
    """
    POST /login
    Riceve JSON con {"username": "...", "password": "..."}.
    Verifica nel DB e restituisce un JSON con dati utente o errore.
    """
    # 1) Leggi il body
    content_length = int(handler.headers.get("Content-Length", 0))
    body = handler.rfile.read(content_length).decode("utf-8")
    print(body)
    # 2) Parse JSON
    try:
        data = json.loads(body)
        print(data)

        username = data["username"]
        password = data["password"]
    except (json.JSONDecodeError, KeyError):
        error_bytes = json.dumps({"error": "Invalid JSON or missing fields"}).encode("utf-8")
        _set_headers(handler, 400, error_bytes)
        handler.wfile.write(error_bytes)
        return

    # 3) Cerca nel DB
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT id, username, password, email
            FROM users
            WHERE username = ? AND password = ?
        """, (username, password))
        row = c.fetchone()

    if row:
        print (row)
        # Trovato => restituiamo i dati utente (senza password in un'app reale).
        user_id, uname, pwd, email = row
        # Esempio di risposta
        user_obj = {
            "id": user_id,
            "username": uname,
            "email": email,
            "message": "Login successful"
        }
        
        response_data = json.dumps(user_obj).encode("utf-8")
        _set_headers(handler, 200, response_data)
        handler.wfile.write(response_data)
    else:
        # Non trovato => errore 401 unauthorized
        error_response = json.dumps({"error": "Wrong username or password"}).encode("utf-8")
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
            "password": row[2],  # Da NON mostrare in chiaro in un’app reale
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
        error_response = json.dumps({"error": "Invalid ID"}).encode("utf-8")
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
            "password": row[2],  # da mascherare in produzione
            "email": row[3]
        }
        response_data = json.dumps(result).encode("utf-8")

        _set_headers(handler, 200, response_data)
        handler.wfile.write(response_data)
    else:
        error_response = json.dumps({"error": "User not found"}).encode("utf-8")
        _set_headers(handler, 404, error_response)
        handler.wfile.write(error_response)
    

def handle_create_user(handler):
    """POST /users - Crea un nuovo utente nel DB."""
    content_length = int(handler.headers.get("Content-Length", 0))
    body = handler.rfile.read(content_length).decode("utf-8")
    
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        error_response = json.dumps({"error": "Invalid JSON"}).encode("utf-8")
        _set_headers(handler, 400, error_response)
        handler.wfile.write(error_response)
        return

    username = data.get("username", "")
    password = data.get("password", "")  # da hashare in produzione
    email = data.get("email", "")

    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO users (username, password, email)
            VALUES (?, ?, ?)
        """, (username, password, email))
        conn.commit()
        new_id = c.lastrowid
    
    new_user = {
        "id": new_id,
        "username": username,
        "password": password,
        "email": email
    }
    response_data = json.dumps(new_user).encode("utf-8")

    _set_headers(handler, 201, response_data)
    handler.wfile.write(response_data)


def handle_update_user(handler, user_id):
    """PUT /users/<id> - Aggiorna i campi di un utente."""
    try:
        user_id = int(user_id)
    except ValueError:
        error_response = json.dumps({"error": "Invalid ID"}).encode("utf-8")
        _set_headers(handler, 400, error_response)
        handler.wfile.write(error_response)
        return
    
    content_length = int(handler.headers.get("Content-Length", 0))
    body = handler.rfile.read(content_length).decode("utf-8")

    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        error_response = json.dumps({"error": "Invalid ID"}).encode("utf-8")
        _set_headers(handler, 400, error_response)
        handler.wfile.write(error_response)
        return

    # campi aggiornabili
    username = data.get("username", None)
    password = data.get("password", None)
    email = data.get("email", None)

    with get_connection() as conn:
        c = conn.cursor()
        # Verifichiamo se l'utente esiste
        c.execute("SELECT id, username, password, email FROM users WHERE id = ?", (user_id,))
        row = c.fetchone()
        if not row:
            error_response = json.dumps({"error": "User not found"}).encode("utf-8")
            _set_headers(handler, 404, error_response)
            handler.wfile.write(error_response)
            return

        existing_id, existing_username, existing_password, existing_email = row
        updated_username = username if username is not None else existing_username
        updated_password = password if password is not None else existing_password
        updated_email = email if email is not None else existing_email

        c.execute("""
            UPDATE users
            SET username = ?, password = ?, email = ?
            WHERE id = ?
        """, (updated_username, updated_password, updated_email, user_id))
        conn.commit()

    updated_user = {
        "id": user_id,
        "username": updated_username,
        "password": updated_password,
        "email": updated_email
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
