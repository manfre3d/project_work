import json
import sqlite3
from db import get_connection
from utility.utility import (
    _set_headers
)
from datetime import datetime


def handle_get_all_bookings(handler):
    """GET /bookings - Ritorna tutte le prenotazioni dal DB."""
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT b.id, b.user_id, b.service_id,
                b.start_date, b.end_date, b.status,
                s.name AS service_name, s.description
            FROM bookings b
            JOIN services s ON b.service_id = s.id
        """)
        rows = c.fetchall()

    results = []
    for row in rows:
        results.append({
            "id": row["id"],
            "user_id": row["user_id"],
            "service_id": row["service_id"],
            "start_date": row["start_date"],
            "end_date": row["end_date"],
            "status": row["status"],
            "service_name": row["service_name"],
            "service_description": row["description"],
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
    """Handler per POST /bookings - Crea una nuova prenotazione."""
    content_length = int(handler.headers.get("Content-Length", 0))
    body = handler.rfile.read(content_length).decode("utf-8")

    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        _send_error(handler, 400, "JSON non valido")
        return

    # validazione e parsing dati
    validation_result = _validate_booking_data(data)
    if validation_result.get("error"):
        _send_error(handler, 400, validation_result["error"])
        return

    user_id = data["user_id"]
    service_id = data["service_id"]
    start_date = validation_result["start_date"]
    end_date = validation_result["end_date"]
    capacity_requested = data.get("capacity_requested", 1)
    status = data.get("status", "pending")

    # verifica servizio e disponibilità
    service_capacity = _get_service_capacity(service_id)
    if service_capacity is None:
        _send_error(handler, 404, "Servizio non trovato")
        return

    if not _check_availability(service_id, start_date, end_date, capacity_requested, service_capacity):
        _send_error(handler, 400, "Capacità del servizio insufficiente per il periodo selezionato")
        return

    # salvataggio prenotazione
    new_booking_id = _save_booking(user_id, service_id, start_date, end_date, capacity_requested, status)
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
    _set_headers(handler, 201, response_data)
    handler.wfile.write(response_data)
    
    
def _validate_booking_data(data):
    """Valida i dati della prenotazione e converte le date."""
    required_fields = ["user_id", "service_id", "start_date", "end_date"]
    for field in required_fields:
        if not data.get(field):
            return {"error": f"Campo obbligatorio mancante: {field}"}

    try:
        start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
        end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()
        if start_date >= end_date:
            return {"error": "La data di inizio deve essere precedente alla data di fine"}
        return {"start_date": start_date, "end_date": end_date}
    except ValueError:
        return {"error": "Formato data non valido. Utilizzare YYYY-MM-DD"}


def _get_service_capacity(service_id):
    """Recupera la capacità del servizio dal database."""
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT capacity FROM services WHERE id = ?", (service_id,))
        service_row = c.fetchone()
        return service_row["capacity"] if service_row else None


def _check_availability(service_id, start_date, end_date, capacity_requested, service_capacity):
    """Verifica la disponibilità del servizio per il periodo selezionato."""
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT SUM(capacity_requested) as total_booked
            FROM bookings
            WHERE service_id = ? AND (
                (start_date <= ? AND end_date > ?) OR
                (start_date < ? AND end_date >= ?)
            )
        """, (service_id, end_date, start_date, end_date, start_date))
        total_booked = c.fetchone()["total_booked"] or 0
        return total_booked + capacity_requested <= service_capacity


def _save_booking(user_id, service_id, start_date, end_date, capacity_requested, status):
    """Salva la prenotazione nel database e restituisce l'ID della nuova prenotazione."""
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO bookings (user_id, service_id, start_date, end_date, capacity_requested, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, service_id, start_date.strftime("%Y-%m-%d"),
                  end_date.strftime("%Y-%m-%d"), capacity_requested, status))
            conn.commit()
            return c.lastrowid
    except sqlite3.IntegrityError:
        return None


def _send_error(handler, code, message):
    """Invia un errore al client."""
    error_response = json.dumps({"errore": message}).encode("utf-8")
    _set_headers(handler, code, error_response)
    handler.wfile.write(error_response)
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
