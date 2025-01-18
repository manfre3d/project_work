import json
from db import get_connection
from authentication import verify_authentication
from utility.utility import set_headers
from user_routes import authenticate


def handle_get_all_services(handler):
    """
    GET /services - Ritorna tutti i servizi dal DB.
    """

    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT id, name, description, capacity, price, active
            FROM services
        """)
        rows = c.fetchall()

    results = []
    for row in rows:
        results.append({
            "id": row["id"],
            "name": row["name"],
            "description": row["description"],
            "capacity": row["capacity"],
            "price": row["price"],
            "active": bool(row["active"])
        })

    response_data = json.dumps(results).encode("utf-8")
    set_headers(handler, 200, response_data)
    handler.wfile.write(response_data)


def handle_get_service_by_id(handler, service_id):
    """
    GET /services/<id> - Ritorna il singolo servizio, se esiste.
    """
    try:
        service_id = int(service_id)
    except ValueError:
        error_response = json.dumps({"error": "Invalid ID"}).encode("utf-8")
        set_headers(handler, 400, error_response)
        handler.wfile.write(error_response)
        return

    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT id, name, description, capacity, price, active
            FROM services
            WHERE id = ?
        """, (service_id,))
        row = c.fetchone()

    if row:
        result = {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "capacity": row[3],
            "price": row[4],
            "active": bool(row[5])
        }
        response_data = json.dumps(result).encode("utf-8")
        set_headers(handler, 200, response_data)
        handler.wfile.write(response_data)
    else:
        error_response = json.dumps({"error": "Service not found"}).encode("utf-8")
        set_headers(handler, 404, error_response)
        handler.wfile.write(error_response)


def handle_create_service(handler):
    """
    POST /services - Crea un nuovo servizio nel DB.
    Body JSON: {"name":"...", "description":"...", "capacity":..., "price":..., "active":1/0}
    """
    content_length = int(handler.headers.get("Content-Length", 0))
    body = handler.rfile.read(content_length).decode("utf-8")

    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        error_response = json.dumps({"error": "Invalid JSON"}).encode("utf-8")
        set_headers(handler, 400, error_response)
        handler.wfile.write(error_response)
        return

    name = data.get("name", "")
    description = data.get("description", "")
    capacity = data.get("capacity", 0)
    price = data.get("price", 0.0)
    # se non è specificato, il servizio è attivo di default
    # active = 1 altrimenti 0
    active = data.get("active", 1)  

    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO services (name, description, capacity, price, active)
            VALUES (?, ?, ?, ?, ?)
        """, (name, description, capacity, price, active))
        conn.commit()
        new_id = c.lastrowid

    new_service = {
        "id": new_id,
        "name": name,
        "description": description,
        "capacity": capacity,
        "price": price,
        "active": bool(active)
    }
    response_data = json.dumps(new_service).encode("utf-8")

    set_headers(handler, 201, response_data)
    handler.wfile.write(response_data)


def handle_update_service(handler, service_id):
    """
    PUT /services/<id> - Aggiorna i campi di un servizio.
    """
    try:
        service_id = int(service_id)
    except ValueError:
        error_response = json.dumps({"error": "Invalid ID"}).encode("utf-8")
        set_headers(handler, 400, error_response)
        handler.wfile.write(error_response)
        return

    content_length = int(handler.headers.get("Content-Length", 0))
    body = handler.rfile.read(content_length).decode("utf-8")

    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        error_response = json.dumps({"error": "Invalid JSON"}).encode("utf-8")
        set_headers(handler, 400, error_response)
        handler.wfile.write(error_response)
        return

    name = data.get("name", None)
    description = data.get("description", None)
    capacity = data.get("capacity", None)
    price = data.get("price", None)
    active = data.get("active", None)

    with get_connection() as conn:
        c = conn.cursor()
        #check per vedere se il servizio richiesto esiste
        c.execute("""
            SELECT id, name, description, capacity, price, active
            FROM services
            WHERE id = ?
        """, (service_id,))
        row = c.fetchone()
        if not row:
            error_response = json.dumps({"error": "Service not found"}).encode("utf-8")
            set_headers(handler, 404, error_response)
            handler.wfile.write(error_response)
            return

        existing_id, existing_name, existing_desc, existing_cap, existing_price, existing_active = row

        updated_name = name if name is not None else existing_name
        updated_desc = description if description is not None else existing_desc
        updated_cap = capacity if capacity is not None else existing_cap
        updated_price = price if price is not None else existing_price
        updated_active = active if active is not None else existing_active

        c.execute("""
            UPDATE services
            SET name = ?, description = ?, capacity = ?, price = ?, active = ?
            WHERE id = ?
        """, (updated_name, updated_desc, updated_cap, updated_price, updated_active, service_id))
        conn.commit()

    updated_service = {
        "id": service_id,
        "name": updated_name,
        "description": updated_desc,
        "capacity": updated_cap,
        "price": updated_price,
        "active": bool(updated_active)
    }
    response_data = json.dumps(updated_service).encode("utf-8")
    set_headers(handler, 200, response_data)
    handler.wfile.write(response_data)


def handle_delete_service(handler, service_id):
    """
    DELETE /services/<id> - Elimina il servizio dal DB (soft delete or real delete).
    """
    try:
        service_id = int(service_id)
    except ValueError:
        error_response = json.dumps({"error": "Invalid ID"}).encode("utf-8")
        set_headers(handler, 400, error_response)
        handler.wfile.write(error_response)
        return

    with get_connection() as conn:
        c = conn.cursor()
        # check se il servizio esiste
        c.execute("SELECT id FROM services WHERE id = ?", (service_id,))
        row = c.fetchone()
        if not row:
            error_response = json.dumps({"error": "Service not found"}).encode("utf-8")
            set_headers(handler, 404, error_response)
            handler.wfile.write(error_response)
            return

        # procediamo con la delete del servizio
        c.execute("DELETE FROM services WHERE id = ?", (service_id,))
        conn.commit()

    response_data = json.dumps({"message": f"Service {service_id} deleted"}).encode("utf-8")
    set_headers(handler, 200, response_data)
    handler.wfile.write(response_data)

