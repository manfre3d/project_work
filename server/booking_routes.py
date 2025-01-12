import json
import sqlite3
from db import get_connection
from utility.utility import (
    _set_headers
)


def handle_get_all_bookings(handler):
    """GET /bookings - Ritorna tutte le prenotazioni dal DB."""
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT b.id, b.user_id, b.service_id,
                b.date, b.status,
                s.name AS service_name, s.description
            FROM bookings b
            JOIN services s ON b.service_id = s.id
        """)
        rows = c.fetchall()

        results = []
        # Convertiamo le tuple in dict
        for row in rows:
            results.append({
            "id": row[0],
            "user_id": row[1],
            "service_id": row[2],
            "date": row[3],
            "status": row[4],
            "service_name": row[5],
            "service_description": row[6],
            })



    response_data = json.dumps(results).encode("utf-8")
    _set_headers(handler, 200, response_data)
    handler.wfile.write(response_data)

def handle_get_booking_by_id(handler, booking_id):
    """GET /bookings/<id> - Ritorna la singola prenotazione, se esiste."""
    try:
        booking_id = int(booking_id)
    except ValueError:
        error_response = json.dumps({"error": "Invalid ID"}).encode("utf-8")
        _set_headers(handler, 400, error_response)
        handler.wfile.write(error_response)
        return
    
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT id, customer_name, date, service, user_id FROM bookings WHERE id = ?", (booking_id,))
        row = c.fetchone()

    if row:
        result = {
            "id": row[0],
            "customer_name": row[1],
            "date": row[2],
            "service": row[3],
            "user_id": row[4]

        }
        response_data = json.dumps(result).encode("utf-8")
        _set_headers(handler, 200, response_data)
        handler.wfile.write(response_data)
    else:
        error_response = json.dumps({"error": "Booking not found"}).encode("utf-8")
        _set_headers(handler, 404, error_response)
        handler.wfile.write(error_response)

def handle_create_booking(handler):
    """POST /bookings - Crea una nuova prenotazione nel DB."""
    content_length = int(handler.headers.get("Content-Length", 0))
    body = handler.rfile.read(content_length).decode("utf-8")
    
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        error_response = json.dumps({"error": "Invalid JSON"}).encode("utf-8")
        _set_headers(handler, 400, error_response)
        handler.wfile.write(error_response)
        return

    # Recupera campi dal body

    # customer_name = data.get("customer_name", "")
    # service = data.get("service", "")
    date = data.get("date", "")
    user_id = data.get("user_id", "")
    service_id = data.get("service_id", None)  # We'll store ID, not text
    status = data.get("status", "pending") 



    with get_connection() as conn:
        c = conn.cursor()

        # check service_id valido
        c.execute("SELECT id FROM services WHERE id = ?", (service_id,))
        service_row = c.fetchone()
        if service_row is None:
            error_response = json.dumps({"error": "Service not found"}).encode("utf-8")
            _set_headers(handler, 404, error_response)
            handler.wfile.write(error_response)
            return

        # check user_id valido
        c.execute("SELECT id, username, password, email FROM users WHERE id = ?", (user_id,))
        row = c.fetchone()
        if row is None:
            error_response = json.dumps({"error": "User non presente nella prenotazione"}).encode("utf-8")
            _set_headers(handler, 404, error_response)
            handler.wfile.write(error_response)
            return

    # Salvataggio nel DB
    try:    
        with get_connection() as conn:
            c = conn.cursor()

            c.execute("""
                INSERT INTO bookings (user_id, service_id, date, status)
                VALUES (?, ?, ?, ?)
            """, (user_id, service_id, date, status))
            conn.commit()
            new_id = c.lastrowid

    except sqlite3.IntegrityError as e:
        # Se scatta la foreign key o un vincolo di integrità
        error_response= json.dumps({"error": str(e)}).encode("utf-8") 
        print(e)          
        _set_headers(handler, 400, error_response)
        handler.wfile.write(error_response)
        return

    

    # Costruiamo l'oggetto di risposta
    new_booking = {
    "id": new_id,
    "user_id": user_id,
    "service_id": service_id,
    "date": date,
    "status": status
    }
    response_data = json.dumps(new_booking).encode("utf-8")
    _set_headers(handler, 201, response_data)
    handler.wfile.write(response_data)

def handle_update_booking(handler, booking_id):
    """
    PUT /bookings/<id> - Aggiorna la prenotazione esistente con i nuovi campi
    (service_id, status, date, user_id).
    """
    try:
        # Convertiamo booking_id in intero
        booking_id = int(booking_id)
    except ValueError:
        # Se booking_id non è un intero
        error_response = json.dumps({"errore": "ID non valido"}).encode("utf-8")
        _set_headers(handler, 400, error_response)
        handler.wfile.write(error_response)
        return

    # Leggiamo il body della richiesta
    content_length = int(handler.headers.get("Content-Length", 0))
    body = handler.rfile.read(content_length).decode("utf-8")

    # Proviamo a fare il parsing del JSON
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        error_response = json.dumps({"errore": "JSON non valido"}).encode("utf-8")
        _set_headers(handler, 400, error_response)
        handler.wfile.write(error_response)
        return

    # Recuperiamo i campi (potrebbero essere assenti o None)
    user_id = data.get("user_id", None)
    service_id = data.get("service_id", None)
    date = data.get("date", None)
    status = data.get("status", None)

    with get_connection() as conn:
        c = conn.cursor()
        # Verifichiamo se la prenotazione esiste davvero
        c.execute("""
            SELECT id, user_id, service_id, date, status
            FROM bookings
            WHERE id = ?
        """, (booking_id,))
        row = c.fetchone()

        if not row:
            # Se la prenotazione non esiste, restituiamo errore 404
            error_response = json.dumps({"errore": "Prenotazione non trovata"}).encode("utf-8")
            _set_headers(handler, 404, error_response)
            handler.wfile.write(error_response)
            return

        existing_id, existing_user_id, existing_service_id, existing_date, existing_status = row

        # Se un campo non è presente nel JSON, manteniamo il valore esistente
        updated_user_id = user_id if user_id is not None else existing_user_id
        updated_service_id = service_id if service_id is not None else existing_service_id
        updated_date = date if date is not None else existing_date
        updated_status = status if status is not None else existing_status

        # Opzionale: si possono aggiungere controlli per updated_user_id e updated_service_id,
        # ad esempio verificare se esistono utenti/servizi corrispondenti nel DB

        # Eseguiamo l'UPDATE nel database
        c.execute("""
            UPDATE bookings
            SET user_id = ?,
                service_id = ?,
                date = ?,
                status = ?
            WHERE id = ?
        """, (updated_user_id, updated_service_id, updated_date, updated_status, booking_id))
        conn.commit()

    # Creiamo l'oggetto di risposta con i campi aggiornati
    updated_booking = {
        "id": booking_id,
        "user_id": updated_user_id,
        "service_id": updated_service_id,
        "date": updated_date,
        "status": updated_status
    }

    # Convertiamo in JSON e inviamo la risposta con status 200
    response_data = json.dumps(updated_booking).encode("utf-8")
    _set_headers(handler, 200, response_data)
    handler.wfile.write(response_data)

def handle_delete_booking(handler, booking_id):
    """DELETE /bookings/<id> - Elimina la prenotazione dal DB."""
    try:
        booking_id = int(booking_id)
    except ValueError:
        error_response = json.dumps({"error": "Invalid ID"}).encode("utf-8")
        _set_headers(handler, 400, error_response)
        handler.wfile.write(error_response)
        return

    with get_connection() as conn:
        c = conn.cursor()
        # Controlliamo se la prenotazione esiste
        c.execute("SELECT id FROM bookings WHERE id = ?", (booking_id,))
        row = c.fetchone()
        if not row:
            error_response = json.dumps({"error": "Booking not found"}).encode("utf-8")
            _set_headers(handler, 404, error_response)
            handler.wfile.write(error_response)
            return

        c.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
        conn.commit()

    response_data = json.dumps({"message": f"Booking {booking_id} deleted"}).encode("utf-8")
    _set_headers(handler, 200, response_data)
    handler.wfile.write(response_data)
