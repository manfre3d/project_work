import json
import sqlite3
from db import get_connection
from utility.authentication import authenticate
from utility.utility import set_headers
from utility.session import create_session, delete_session

import bcrypt

def handle_login(handler):
    """
    POST /login
    JSON: {"username":"...","password":"..."}
    Verifica l'utente e crea una sessione
    """
    print("Ricevuta richiesta di login")
    try:
        content_length = int(handler.headers.get("Content-Length", 0))
        body = handler.rfile.read(content_length).decode("utf-8")
        data = json.loads(body)
        username = data["username"]
        password = data["password"]
        print(f"Tentativo di login per l'utente: {username}")
    except (ValueError, KeyError, json.JSONDecodeError):
        print("Errore nel parsing della richiesta di login")
        error_bytes = json.dumps({"error": "JSON non valido o campi mancanti"}).encode("utf-8")
        set_headers(handler, 400, error_bytes)
        handler.wfile.write(error_bytes)
        return

    # ricerca dell'utente nel database
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT id, username, password, email, role
            FROM users
            WHERE username = ?
        """, (username,))
        row = c.fetchone()

    if row is None:
        print(f"Utente non trovato: {username}")
        error_response = json.dumps({"error": "Utente inesistente"}).encode("utf-8")
        set_headers(handler, 401, error_response)
        handler.wfile.write(error_response)
        return

    user_id, db_username, db_hashed_pw, email, role = row
    print(f"Utente trovato: {db_username}, Ruolo: {role}")

    # controllo per password, bcrypt.checkpw ritorna True se la password è corretta
    if bcrypt.checkpw(password.encode("utf-8"), db_hashed_pw.encode("utf-8")):
        print(f"Password corretta per l'utente: {username}")
        # password corretta, crea sessione nel database e la gestisce nel be
        session_id = create_session(user_id)
        print(f"Sessione creata: {session_id}")
        
        user_obj = {
            "id": user_id,
            "username": db_username,
            "email": email,
            "role": role,
            "message": "Login effettuato con successo"
        }
        response_data = json.dumps(user_obj).encode("utf-8")
        
        # header extra per Set-Cookie per passare il session_id al fe una volta
        # loggato nei cookie l'fe lo salva ed è possibile fare richieste successive 
        # al server e il resto delle richieste saranno autenticate
        
        extra_headers = {
            "Set-Cookie": f"session_id={session_id}; HttpOnly; Path=/"
        }
        
        #tramite metodo set headers impostiamo header extra necessari per passare il session_id al fe
        set_headers(handler, 200, response_data, extra_headers=extra_headers)
        handler.wfile.write(response_data)
    else:
        print(f"Password errata per l'utente: {username}")
        error_response = json.dumps({"error": "Username o password errati"}).encode("utf-8")
        set_headers(handler, 401, error_response)
        handler.wfile.write(error_response)

def handle_logout(handler):
    """POST /logout - Elimina la sessione dell'utente."""
    cookies = handler.headers.get("Cookie")
    if not cookies:
        error_response = json.dumps({"error": "Nessuna sessione attiva"}).encode("utf-8")
        set_headers(handler, 400, error_response)
        handler.wfile.write(error_response)
        return

    session_id = None
    for cookie in cookies.split(";"):
        if "session_id=" in cookie:
            session_id = cookie.strip().split("session_id=")[1]
            break

    if not session_id:
        error_response = json.dumps({"error": "Nessuna sessione attiva"}).encode("utf-8")
        set_headers(handler, 400, error_response)
        handler.wfile.write(error_response)
        return

    delete_session(session_id)

    # imposta il cookie di sessione come scaduto (normalmente si utilizza con la funzione logout)
    response_data = json.dumps({"message": "Logout effettuato con successo"}).encode("utf-8")
    extra_headers = {
        "Set-Cookie": "session_id=; HttpOnly; Path=/; Max-Age=0"
    }
    set_headers(
        handler,
        code=200,
        response_data=response_data,
        extra_headers=extra_headers
    )
    handler.wfile.write(response_data)

def handle_get_all_users(handler):
    """GET /users - Ritorna tutti gli utenti senza le password."""
    authenticated_user = authenticate(handler)
    # tramite autorizzazione, permette solo agli utenti con ruolo admin
    # di vedere tutti gli utenti
    if authenticated_user["role"] != "admin":
        error_response = json.dumps({"error": "Autorizzazione richiesta"}).encode("utf-8")
        set_headers(handler, 403, error_response)
        handler.wfile.write(error_response)
        return

    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT id, username, email, role FROM users")
        rows = c.fetchall()
    
    results = []
    for row in rows:
        results.append({
            "id": row["id"],
            "username": row["username"],
            "email": row["email"],
            "role": row["role"]
        })

    response_data = json.dumps(results).encode("utf-8")

    set_headers(handler, 200, response_data)
    handler.wfile.write(response_data)


def handle_get_user_by_id(handler, user_id):
    """GET /users/<id> - Ritorna il singolo utente se esiste."""
    try:
        user_id = int(user_id)
    except ValueError:
        error_response = json.dumps({"error": "ID non valido"}).encode("utf-8")
        set_headers(handler, 400, error_response)
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

        set_headers(handler, 200, response_data)
        handler.wfile.write(response_data)
    else:
        error_response = json.dumps({"error": "User non trovato"}).encode("utf-8")
        set_headers(handler, 404, error_response)
        handler.wfile.write(error_response)
    
def handle_get_current_user(handler):
    """
    GET /current-user
    Ritorna i dettagli dell'utente autenticato in base al cookie session_id.
    """
    session_id = handler.headers.get("Cookie", "").split("session_id=")[-1].split(";")[0]
    
    if not session_id:
        error_response = json.dumps({"error": "Sessione non trovata"}).encode("utf-8")
        set_headers(handler, 401, error_response)
        print("sessione non valida")
        
        handler.wfile.write(error_response)
        return

    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT u.id, u.username, u.email, u.role
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.session_id = ?
        """, (session_id,))
        user = c.fetchone()

    if user:
        response = {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"]
        }
        response_data = json.dumps(response).encode("utf-8")
        print(response_data)
        set_headers(handler, 200, response_data)
        handler.wfile.write(response_data)
    else:
        error_response = json.dumps({"error": "Sessione non valida"}).encode("utf-8")
        print("sessione non valida")
        
        set_headers(handler, 401, error_response)
        handler.wfile.write(error_response)
        
        
def handle_create_user(handler):
    """POST /users - Crea un nuovo utente nel DB."""
    content_length = int(handler.headers.get("Content-Length", 0))
    body = handler.rfile.read(content_length).decode("utf-8")
    
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        error_response = json.dumps({"error": "JSON non valido"}).encode("utf-8")
        set_headers(handler, 400, error_response)
        handler.wfile.write(error_response)
        return

    # dati utente
    username = data.get("username", "")
    # password dell'utente prima del hashing
    password = data.get("password", "")
    email = data.get("email", "")
    
    # validazione campi
    if not username or not password or not email:
        error_response = json.dumps({"error": "Tutti i campi sono obbligatori"}).encode("utf-8")
        set_headers(handler, 400, error_response)
        handler.wfile.write(error_response)
        return

    # validazione formato della email
    if "@" not in email or "." not in email or email.index("@") > email.rindex("."):
        error_response = json.dumps({"error": "Email non valida"}).encode("utf-8")
        set_headers(handler, 400, error_response)
        handler.wfile.write(error_response)
        return

    # hashing della  password tramite l'utililizzo di bcrypt
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
            # error per gestire violazioni UNIQUE su username o email
            error_response = json.dumps({"error": f"Violazione di unicità: {str(e)}"}).encode("utf-8")
            set_headers(handler, 400, error_response)
            handler.wfile.write(error_response)
            return
    
    new_user = {
        "id": new_id,
        "username": username,
        "email": email
    }
    response_data = json.dumps(new_user).encode("utf-8")

    set_headers(handler, 201, response_data)
    handler.wfile.write(response_data)

def handle_update_user(handler, user_id):
    """PUT /users/<id> - Aggiorna i campi di un utente (username, password, email)."""
    try:
        user_id = int(user_id)
    except ValueError:
        error_response = json.dumps({"error": "ID non valido"}).encode("utf-8")
        set_headers(handler, 400, error_response)
        handler.wfile.write(error_response)
        return
    
    content_length = int(handler.headers.get("Content-Length", 0))
    body = handler.rfile.read(content_length).decode("utf-8")

    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        error_response = json.dumps({"error": "JSON non valido"}).encode("utf-8")
        set_headers(handler, 400, error_response)
        handler.wfile.write(error_response)
        return

    # campi aggiornabili dell'user
    username = data.get("username", None)
    # nuova password da aggiornare prima che venga hashata
    new_password = data.get("password", None)
    email = data.get("email", None)

    with get_connection() as conn:
        c = conn.cursor()
        # check per vedere se l'utente esiste nel db
        c.execute("SELECT id, username, password, email FROM users WHERE id = ?", (user_id,))
        row = c.fetchone()
        if not row:
            error_response = json.dumps({"error": "Utente non trovato"}).encode("utf-8")
            set_headers(handler, 404, error_response)
            handler.wfile.write(error_response)
            return

        existing_id, existing_username, existing_hashed_pw, existing_email = row

        # se i campi non sono presenti manteniamo i valori esistendi
        updated_username = username if username is not None else existing_username
        updated_email = email if email is not None else existing_email

        # processo per la password qualora presente. viene hashata con bcrypt
        # se non presente si mantiene la password esistente
        if new_password is not None and len(new_password) > 0:
            hashed_pw = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        else:
            hashed_pw = existing_hashed_pw

        # andiamo ad aggiornare il DB
        try:
            c.execute("""
                UPDATE users
                SET username = ?, password = ?, email = ?
                WHERE id = ?
            """, (updated_username, hashed_pw, updated_email, user_id))
            conn.commit()
        except sqlite3.IntegrityError as e:
            # gestiamo errori per violazioni di tipo UNIQUE su username o email
            error_response = json.dumps({"error": f"Violazione di unicità: {str(e)}"}).encode("utf-8")
            set_headers(handler, 400, error_response)
            handler.wfile.write(error_response)
            return

    updated_user = {
        "id": user_id,
        "username": updated_username,
        "email": updated_email,
        # rimosso la password per motivi di sicurezza anche se hashata
        # "password": hashed_pw 
    }
    response_data = json.dumps(updated_user).encode("utf-8")
    set_headers(handler, 200, response_data)
    handler.wfile.write(response_data)

def handle_delete_user(handler, user_id):
    """DELETE /users/<id> - Elimina l'utente dal DB."""
    try:
        user_id = int(user_id)
    except ValueError:
        error_response = json.dumps({"error": "Invalid ID"}).encode("utf-8")
        set_headers(handler, 400, error_response)
        handler.wfile.write(error_response)
        return

    with get_connection() as conn:
        c = conn.cursor()
        # check per vedere se l'utente esiste
        c.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        row = c.fetchone()
        if not row:
            error_response = json.dumps({"error": "User not found"}).encode("utf-8")
            set_headers(handler, 404, error_response)
            handler.wfile.write(error_response)
            return

        c.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
    response_data = json.dumps({"message": f"User {user_id} deleted"}).encode("utf-8")
    set_headers(handler, 200, response_data)
    handler.wfile.write(response_data)
