import json
from db import get_connection
from utility import (
    _set_headers
)


def handle_get_all_bookings(handler):
    """GET /bookings - Ritorna tutte le prenotazioni dal DB."""
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT id, customer_name, date, service FROM bookings")
        rows = c.fetchall()  # lista di tuple, es: [(1, 'Mario', '2024-12-31', 'Taglio'), ...]

    # Convertiamo le tuple in dict
    results = []
    for row in rows:
        results.append({
            "id": row[0],
            "customer_name": row[1],
            "date": row[2],
            "service": row[3]
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
        c.execute("SELECT id, customer_name, date, service FROM bookings WHERE id = ?", (booking_id,))
        row = c.fetchone()

    if row:
        result = {
            "id": row[0],
            "customer_name": row[1],
            "date": row[2],
            "service": row[3]
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
    customer_name = data.get("customer_name", "")
    date = data.get("date", "")
    service = data.get("service", "")

    # Salvataggio nel DB
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO bookings (customer_name, date, service)
            VALUES (?, ?, ?)
        """, (customer_name, date, service))
        conn.commit()
        new_id = c.lastrowid  # ID generato

    # Costruiamo l'oggetto di risposta
    new_booking = {
        "id": new_id,
        "customer_name": customer_name,
        "date": date,
        "service": service
    }
    response_data = json.dumps(new_booking).encode("utf-8")
    _set_headers(handler, 201, response_data)
    handler.wfile.write(response_data)

def handle_update_booking(handler, booking_id):
    """PUT /bookings/<id> - Aggiorna la prenotazione indicata."""
    try:
        booking_id = int(booking_id)
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
        error_response = json.dumps({"error": "Invalid JSON"}).encode("utf-8")
        _set_headers(handler, 400, error_response)
        handler.wfile.write(error_response)
        return

    # Campi aggiornabili
    customer_name = data.get("customer_name", None)
    date = data.get("date", None)
    service = data.get("service", None)

    with get_connection() as conn:
        c = conn.cursor()
        # Prima recuperiamo la prenotazione esistente (per verificare se c'è)
        c.execute("SELECT id, customer_name, date, service FROM bookings WHERE id = ?", (booking_id,))
        row = c.fetchone()
        if not row:
            error_response = json.dumps({"error": "Booking not found"}).encode("utf-8")
            _set_headers(handler, 404, error_response)
            handler.wfile.write(error_response)
            return
        
        # Se esiste, costruiamo i campi aggiornati
        existing_id, existing_name, existing_date, existing_service = row
        updated_name = customer_name if customer_name is not None else existing_name
        updated_date = date if date is not None else existing_date
        updated_service = service if service is not None else existing_service

        c.execute("""
            UPDATE bookings
            SET customer_name = ?, date = ?, service = ?
            WHERE id = ?
        """, (updated_name, updated_date, updated_service, booking_id))
        conn.commit()

    # Rispondiamo con la prenotazione aggiornata
    updated_booking = {
        "id": booking_id,
        "customer_name": updated_name,
        "date": updated_date,
        "service": updated_service
    }
    response_data = json.dumps(updated_booking).encode("utf-8")
    _set_headers(handler, 200, response_data)
    handler.wfile.write(error_response)

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
