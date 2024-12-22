import json
from db import get_connection

def _set_headers(handler, code=200, content_type="application/json"):
    handler.send_response(code)
    handler.send_header("Content-Type", content_type)
    handler.end_headers()

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

    _set_headers(handler, 200)
    handler.wfile.write(json.dumps(results).encode("utf-8"))

def handle_get_user_by_id(handler, user_id):
    """GET /users/<id> - Ritorna il singolo utente se esiste."""
    try:
        user_id = int(user_id)
    except ValueError:
        _set_headers(handler, 400)
        handler.wfile.write(json.dumps({"error": "Invalid ID"}).encode("utf-8"))
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
        _set_headers(handler, 200)
        handler.wfile.write(json.dumps(result).encode("utf-8"))
    else:
        _set_headers(handler, 404)
        handler.wfile.write(json.dumps({"error": "User not found"}).encode("utf-8"))

def handle_create_user(handler):
    """POST /users - Crea un nuovo utente nel DB."""
    content_length = int(handler.headers.get("Content-Length", 0))
    body = handler.rfile.read(content_length).decode("utf-8")
    
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        _set_headers(handler, 400)
        handler.wfile.write(json.dumps({"error": "Invalid JSON"}).encode("utf-8"))
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
    _set_headers(handler, 201)
    handler.wfile.write(json.dumps(new_user).encode("utf-8"))

def handle_update_user(handler, user_id):
    """PUT /users/<id> - Aggiorna i campi di un utente."""
    try:
        user_id = int(user_id)
    except ValueError:
        _set_headers(handler, 400)
        handler.wfile.write(json.dumps({"error": "Invalid ID"}).encode("utf-8"))
        return
    
    content_length = int(handler.headers.get("Content-Length", 0))
    body = handler.rfile.read(content_length).decode("utf-8")

    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        _set_headers(handler, 400)
        handler.wfile.write(json.dumps({"error": "Invalid JSON"}).encode("utf-8"))
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
            _set_headers(handler, 404)
            handler.wfile.write(json.dumps({"error": "User not found"}).encode("utf-8"))
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
    _set_headers(handler, 200)
    handler.wfile.write(json.dumps(updated_user).encode("utf-8"))

def handle_delete_user(handler, user_id):
    """DELETE /users/<id> - Elimina l'utente dal DB."""
    try:
        user_id = int(user_id)
    except ValueError:
        _set_headers(handler, 400)
        handler.wfile.write(json.dumps({"error": "Invalid ID"}).encode("utf-8"))
        return

    with get_connection() as conn:
        c = conn.cursor()
        # Controlliamo se l'utente esiste
        c.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        row = c.fetchone()
        if not row:
            _set_headers(handler, 404)
            handler.wfile.write(json.dumps({"error": "User not found"}).encode("utf-8"))
            return

        c.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()

    _set_headers(handler, 200)
    handler.wfile.write(json.dumps({"message": f"User {user_id} deleted"}).encode("utf-8"))
