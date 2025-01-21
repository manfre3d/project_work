from datetime import datetime

from db import get_connection


def validate_booking_data(data):
    """valida i dati della prenotazione e converte le date. Non effettua controlli, 
    sull'user_id perché può essere fornito o estratto dalla sessione."""
    required_fields = ["service_id", "start_date", "end_date"]

    # verifica che tutti i campi richiesti ("service_id", "start_date", "end_date") siano presenti
    for field in required_fields:
        if not data.get(field):
            return {"error": f"Campo obbligatorio mancante: {field}"}

    try:
        start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
        end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()
        
        today = datetime.now().date()
        # verifica se la data è precedente a quella odierna
        if start_date < today:
            return {"error": "La data di inizio non può essere precedente alla data odierna"}
        # verifica se la data di inizio è successiva a quella di fine
        if start_date > end_date:
            return {"error": "La data di inizio deve essere precedente alla data di fine"}
        return {"start_date": start_date, "end_date": end_date}
    except ValueError:
        return {"error": "Formato data non valido. Utilizzare YYYY-MM-DD"}


def get_service_capacity(service_id):
    """Recupera la disponibilita'/capacita' del servizio dal database."""
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT capacity FROM services WHERE id = ?", (service_id,))
        service_row = c.fetchone()
        return service_row["capacity"] if service_row else None

def check_availability(service_id, start_date, end_date, capacity_requested, service_capacity, exclude_booking_id=None):
    """Verifica la disponibilità del servizio per il periodo selezionato, escludendo una prenotazione specifica se necessario."""
    with get_connection() as conn:
        c = conn.cursor()

        query = """
            SELECT SUM(capacity_requested) as total_booked
            FROM bookings
            WHERE service_id = ? AND (
                (start_date <= ? AND end_date > ?) OR
                (start_date < ? AND end_date >= ?)
            )
        """
        params = [service_id, end_date, start_date, end_date, start_date]

        # viene aggiunta la verifica per escludere una prenotazione specifica
        # se exclude_booking_id è valorizzato
        if exclude_booking_id is not None:
            query += " AND id != ?"
            params.append(exclude_booking_id)

        c.execute(query, params)
        total_booked = c.fetchone()["total_booked"] or 0

    return total_booked + capacity_requested <= service_capacity

def save_booking(user_id, service_id, start_date, end_date, capacity_requested, status):
    """Salva la prenotazione nel database e restituisce l'ID della nuova prenotazione."""
    try:
        with get_connection() as conn:
            c = conn.cursor()
            
            c.execute("SELECT price FROM services WHERE id = ?", (service_id,))
            service = c.fetchone()
            if not service:
                return None

            daily_price = service["price"]
            num_days = (end_date - start_date).days + 1
            total_price = daily_price * num_days * capacity_requested
            
            
            c.execute("""
                INSERT INTO bookings (user_id, service_id, start_date, end_date, capacity_requested, status, total_price)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, service_id, start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d"), capacity_requested, status, total_price))
            conn.commit()
            return c.lastrowid
    except sqlite3.IntegrityError:
        return None
