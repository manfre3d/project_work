import re
from booking_routes import (
    handle_get_all_bookings,
    handle_get_booking_by_id,
    handle_create_booking,
    handle_update_booking,
    handle_delete_booking
)
from user_routes import (
    handle_login,
    handle_get_all_users,
    handle_get_user_by_id,
    handle_create_user,
    handle_update_user,
    handle_delete_user
)
def parse_path(path):
    parts = path.strip("/").split("/")
    if len(parts) == 1:
        resource = parts[0]
        return (resource, None)  # es: ("bookings", None)
    elif len(parts) == 2 and parts[1].isdigit():
        resource = parts[0]
        resource_id = parts[1]
        return (resource, resource_id)
    return (None, None)

def route_request(handler, method):
    resource, resource_id = parse_path(handler.path)

    if resource == "bookings":
        if resource_id is None:
            # Rotta /bookings
            if method == "GET":
                handle_get_all_bookings(handler)
            elif method == "POST":
                handle_create_booking(handler)
            else:
                handle_404(handler)
        else:
            # Rotta /bookings/<id>
            if method == "GET":
                handle_get_booking_by_id(handler, resource_id)
            elif method == "PUT":
                handle_update_booking(handler, resource_id)
            elif method == "DELETE":
                handle_delete_booking(handler, resource_id)
            else:
                handle_404(handler)
        return

    # --- blocco: /login ---
    if resource == "login":
        # Solo POST /login
        if method == "POST":
            handle_login(handler)
        else:
            handle_404(handler)
        return
    
    if resource == "users":
        if resource_id is None:
            # Rotta /users
            if method == "GET":
                handle_get_all_users(handler)
            elif method == "POST":
                    handle_create_user(handler)
            else:
                handle_404(handler)
        else:
            # Rotta /users/<id>
            if method == "GET":
                handle_get_user_by_id(handler, resource_id)
            if method == "PUT":
                handle_update_user(handler, resource_id)
            elif method == "DELETE":
                handle_delete_user(handler, resource_id)
            else:
                handle_404(handler)
        return    

    handle_404(handler)


def handle_404(handler):
    handler.send_response(404)
    handler.send_header("Content-Type", "application/json")
    handler.end_headers()
    handler.wfile.write(b'{"error": "Not found"}')
