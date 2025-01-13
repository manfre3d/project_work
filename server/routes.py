import json
import re
from booking_routes import (
    handle_get_all_bookings,
    handle_get_booking_by_id,
    handle_create_booking,
    handle_update_booking,
    handle_delete_booking
)
from utility.utility import _set_headers
from user_routes import (
    handle_login,
    handle_get_all_users,
    handle_get_user_by_id,
    handle_create_user,
    handle_logout,
    handle_update_user,
    handle_delete_user
)
from service_routes import (
    handle_get_all_services,
    handle_get_service_by_id,
    handle_create_service,
    handle_update_service,
    handle_delete_service
)
def parse_path(path):
    parts = path.strip("/").split("/")
    if len(parts) == 1:
        resource = parts[0]
        # es: ("bookings", None)
        return (resource, None)  
    elif len(parts) == 2 and parts[1].isdigit():
        resource = parts[0]
        resource_id = parts[1]
        return (resource, resource_id)
    return (None, None)

def route_request(handler, method):
    resource, resource_id = parse_path(handler.path)

    if resource == "services":
        if resource_id is None:
            # e.g. /services
            if method == "GET":
                handle_get_all_services(handler)
            elif method == "POST":
                handle_create_service(handler)
            else:
                handle_404(handler)
        else:
            # e.g. /services/123
            if method == "GET":
                handle_get_service_by_id(handler, resource_id)
            elif method == "PUT":
                handle_update_service(handler, resource_id)
            elif method == "DELETE":
                handle_delete_service(handler, resource_id)
            else:
                handle_404(handler)
        return

    if resource == "bookings":
        if resource_id is None:
            # rotta /bookings
            if method == "GET":
                handle_get_all_bookings(handler)
            elif method == "POST":
                handle_create_booking(handler)
            else:
                handle_404(handler)
        else:
            # rotta /bookings/<id>
            if method == "GET":
                handle_get_booking_by_id(handler, resource_id)
            elif method == "PUT":
                handle_update_booking(handler, resource_id)
            elif method == "DELETE":
                handle_delete_booking(handler, resource_id)
            else:
                handle_404(handler)
        return

    # /login
    if resource == "login":
        if method == "POST":
            handle_login(handler)
        else:
            handle_404(handler)
        return
    # /logout
    if resource == "logout":
        if method == "POST":
            handle_logout(handler)
        else:
            handle_404(handler)
        return
    
    
    # rotte per gli utenti
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
            # rotta /users/<id>
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
    error_response = json.dumps({"error": "Rotta non trovata"}).encode("utf-8")
    _set_headers(handler, 404,error_response)
    handler.wfile.write(error_response)
