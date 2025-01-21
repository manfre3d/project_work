import json
from db import get_connection
from utility.utility import (
    set_headers
)
from utility.booking_utility import (
    get_service_capacity,
    check_availability,
    save_booking,
    validate_booking_data,
)

def handle_get_all_bookings(handler, authenticated_user):
    """
    GET /bookings - Ritorna tutte le prenotazioni per admin o solo quelle
    dell'utente corrente se non è un admin.
    """

    user_id = authenticated_user["id"]
    role = authenticated_user["role"]

    with get_connection() as conn:
        c = conn.cursor()

        if role == "admin":
            # recupera tutte le prenotazioni presenti per tutti gli utenti se l'utente è un admin
            c.execute("""
                SELECT b.id, b.user_id, b.service_id, b.start_date, b.end_date, b.status, b.total_price,
                    s.name AS service_name, s.description AS service_description,
                    u.username AS user_name
                FROM bookings b
                JOIN services s ON b.service_id = s.id
                JOIN users u ON b.user_id = u.id
            """)
        else:
            # recupera solo le prenotazioni dell'utente corrente con ruolo user
            c.execute("""
                SELECT b.id, b.user_id, b.service_id, b.start_date, b.end_date, b.status, b.total_price,
                    s.name AS service_name, s.description AS service_description
                FROM bookings b
                JOIN services s ON b.service_id = s.id
                WHERE b.user_id = ?
            """, (user_id,))

        rows = c.fetchall()

    results = []
    for row in rows:
        results.append({
            "id": row["id"],
            "user_id": row["user_id"],
            "username": row["user_name"] if "user_name" in row.keys() else None,
            "service_id": row["service_id"],
            "service_name": row["service_name"],
            "service_description": row["service_description"],
            "start_date": row["start_date"],
            "end_date": row["end_date"],
            "status": row["status"],
            "total_price": row["total_price"]
        })

    response_data = json.dumps(results).encode("utf-8")
    set_headers(handler, 200, response_data)
    handler.wfile.write(response_data)
    
def handle_get_booking_by_id(handler, booking_id):
    """GET /bookings/<id> - Ritorna la singola prenotazione, se esiste."""
    try:
        booking_id = int(booking_id)
    except ValueError:
        error_response = json.dumps({"error": "Invalid ID"}).encode("utf-8")
        set_headers(handler, 400, error_response)
        handler.wfile.write(error_response)
        return

    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT 
                b.id, b.user_id, b.service_id, 
                b.start_date, b.end_date, b.status, b.total_price, 
                s.name AS service_name,
                u.username AS user_name
            FROM bookings b
            JOIN services s ON b.service_id = s.id
            JOIN users u ON b.user_id = u.id
            WHERE b.id = ?
        """, (booking_id,))
        row = c.fetchone()

    if row:
        result = {
            "id": row["id"],
            "user_id": row["user_id"],
            "username": row["user_name"],  
            "service_id": row["service_id"],
            "start_date": row["start_date"],
            "end_date": row["end_date"],
            "status": row["status"],
            "service_name": row["service_name"],
            "total_price": row["total_price"]
        }
        response_data = json.dumps(result).encode("utf-8")
        set_headers(handler, 200, response_data)
        handler.wfile.write(response_data)
    else:
        error_response = json.dumps({"error": "Booking not found"}).encode("utf-8")
        set_headers(handler, 404, error_response)
        handler.wfile.write(error_response)


def handle_create_booking(handler, authenticated_user):
    """Handler per POST /bookings - Crea una nuova prenotazione."""
    content_length = int(handler.headers.get("Content-Length", 0))
    body = handler.rfile.read(content_length).decode("utf-8")

    
    user_id = authenticated_user["id"]
    
    
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        _send_error(handler, 400, "JSON non valido")
        return

    # validazione e parsing dati
    validation_result = validate_booking_data(data)
    if validation_result.get("error"):
        _send_error(handler, 400, validation_result["error"])
        return

    user_id = data["user_id"] if data.get("user_id") else user_id
    service_id = data["service_id"]
    start_date = validation_result["start_date"]
    end_date = validation_result["end_date"]
    capacity_requested = data.get("capacity_requested", 1)
    status = data.get("status", "pending")

    # verifica servizio e disponibilità
    service_capacity = get_service_capacity(service_id)
    if service_capacity is None:
        _send_error(handler, 404, "Servizio non trovato")
        return

    if not check_availability(service_id, start_date, end_date, capacity_requested, service_capacity):
        _send_error(handler, 400, "Disponibilita' del servizio insufficiente per il periodo selezionato")
        return

    # salvataggio prenotazione
    new_booking_id = save_booking(user_id, service_id, start_date, end_date, capacity_requested, status)
    if new_booking_id is None:
        _send_error(handler, 400, "Errore durante il salvataggio della prenotazione")
        return

    # risposta al client
    new_booking = {
        "id": new_booking_id,
        "user_id": user_id,
        "service_id": service_id,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "capacity_requested": capacity_requested,
        "status": status,
    }
    response_data = json.dumps(new_booking).encode("utf-8")
    set_headers(handler, 201, response_data)
    handler.wfile.write(response_data)

def _send_error(handler, code, message):
    """Invia un errore al client."""
    error_response = json.dumps({"error": message}).encode("utf-8")
    set_headers(handler, code, error_response)
    handler.wfile.write(error_response)
def handle_update_booking(handler, authenticated_user, booking_id):
    """
    PUT /bookings/<id> - Aggiorna una prenotazione esistente per id.
    """
    user_id = authenticated_user["id"]
    role = authenticated_user["role"]

    try:
        booking_id = int(booking_id)
    except ValueError:
        _send_error(handler, 400, "ID non valido")
        return

    content_length = int(handler.headers.get("Content-Length", 0))
    body = handler.rfile.read(content_length).decode("utf-8")

    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        _send_error(handler, 400, "JSON non valido")
        return

    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,))
        existing_booking = c.fetchone()

    if not existing_booking:
        _send_error(handler, 404, "Prenotazione non trovata")
        return

    # controllo sul ruolo dell'utente per vedere se può modificare la prenotazione 
    # se è un admin può modificare tutte le prenotazioni, altrimenti solo le sue
    
    if existing_booking["user_id"] != user_id and role != "admin":
        _send_error(handler, 403, "Accesso negato alla prenotazione")
        return

    # aggiorna o mantieni i dati
    updated_service_id = data.get("service_id", existing_booking["service_id"])
    updated_start_date = data.get("start_date", existing_booking["start_date"])
    updated_end_date = data.get("end_date", existing_booking["end_date"])
    updated_capacity_requested = data.get("capacity_requested", existing_booking["capacity_requested"])
    updated_status = "pending" if role == "user" else data.get("status", existing_booking["status"])

    validation_result = validate_booking_data({
        "service_id": updated_service_id,
        "start_date": updated_start_date,
        "end_date": updated_end_date
    })
    if validation_result.get("error"):
        _send_error(handler, 400, validation_result["error"])
        return

    start_date = validation_result["start_date"]
    end_date = validation_result["end_date"]
    
    service_capacity = get_service_capacity(updated_service_id)
    if service_capacity is None:
        _send_error(handler, 404, "Servizio non trovato")
        return

    if not check_availability(
        updated_service_id,
        start_date,
        end_date,
        updated_capacity_requested,
        service_capacity,
        exclude_booking_id=booking_id):
        _send_error(handler, 400, "Disponibilita' del servizio insufficiente per il periodo selezionato")
        return

    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT price FROM services WHERE id = ?", (updated_service_id,))
        service = c.fetchone()
    if not service:
        _send_error(handler, 404, "Servizio non trovato")
        return

    daily_price = service["price"]
    num_days = (end_date - start_date).days + 1
    total_price = daily_price * num_days * updated_capacity_requested

    # aggiorna la prenotazione
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""
            UPDATE bookings
            SET service_id = ?, start_date = ?, end_date = ?, capacity_requested = ?, status = ?, total_price = ?
            WHERE id = ?
        """, (updated_service_id, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"),
            updated_capacity_requested, updated_status, total_price, booking_id))
        conn.commit()

    response_data = {
        "id": booking_id,
        "service_id": updated_service_id,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "capacity_requested": updated_capacity_requested,
        "status": updated_status,
        "total_price": total_price
    }
    set_headers(handler, 200, json.dumps(response_data).encode("utf-8"))
    handler.wfile.write(json.dumps(response_data).encode("utf-8"))

def handle_delete_booking(handler, authenticated_user, booking_id):
    """DELETE /bookings/<id> - Elimina una prenotazione."""
    
    role = authenticated_user["role"] 
    try:
        booking_id = int(booking_id)
    except ValueError:
        error_response = json.dumps({"error": "ID prenotazione non valido"}).encode("utf-8")
        set_headers(handler, 400, error_response)
        handler.wfile.write(error_response)
        return

    user_id = authenticated_user["id"]

    # cerca la prenotazione nel database
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT user_id
            FROM bookings
            WHERE id = ?
        """, (booking_id,))
        booking = c.fetchone()

        if not booking:
            error_response = json.dumps({"error": "Prenotazione non trovata"}).encode("utf-8")
            set_headers(handler, 404, error_response)
            handler.wfile.write(error_response)
            return

        if booking["user_id"] != user_id and role != "admin":
            error_response = json.dumps({"error": "Accesso negato alla prenotazione"}).encode("utf-8")
            set_headers(handler, 403, error_response)
            handler.wfile.write(error_response)
            return

        # elimina la prenotazione
        c.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
        conn.commit()

    success_response = {"messaggio": f"Prenotazione {booking_id} eliminata con successo"}
    set_headers(handler, 200, json.dumps(success_response).encode("utf-8"))
    handler.wfile.write(json.dumps(success_response).encode("utf-8"))
