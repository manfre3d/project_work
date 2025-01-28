import json
from booking_routes import (
    handle_get_all_bookings,
    handle_get_booking_by_id,
    handle_create_booking,
    handle_update_booking,
    handle_delete_booking
)
from utility.utility import set_headers, parse_path
from user_routes import (
    handle_get_current_user,
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
from utility.authentication import verify_authentication

def route_request(handler, method):
    ''' Gestisce le richieste http provenienti da server.py
    in base al metodo HTTP e al percorso richiesto. '''
    
    # rotte publiche che non richiedono autenticazione
    public_routes = [
        ("login", "POST"),
        ("logout", "POST"),
        ("users","POST")
    ]

    # logica per analizzare il percorso della richiesta
    resource, resource_id = parse_path(handler.path)

    if (resource, method) not in public_routes:
        authenticated_user = verify_authentication(handler)
        if not authenticated_user:
            print("Autenticazione fallita!")
            return
        print(f"Utente autenticato: {authenticated_user}")
        
    # rotta per le prenotazioni
    if resource == "bookings":
        if resource_id is None:
            if method == "GET":
                handle_get_all_bookings(handler,authenticated_user)
            elif method == "POST":
                handle_create_booking(handler,authenticated_user)
            else:
                handle_404(handler)
        else:
            if method == "GET":
                handle_get_booking_by_id(handler, resource_id)
            elif method == "PUT":
                handle_update_booking(handler, authenticated_user, resource_id)
            elif method == "DELETE":
                handle_delete_booking(handler, authenticated_user, resource_id)
            else:
                handle_404(handler)
        return

    # rotta per i servizi
    if resource == "services":
        if resource_id is None:
            if method == "GET":
                handle_get_all_services(handler)
            elif method == "POST":
                handle_create_service(handler)
            else:
                handle_404(handler)
        else:
            if method == "GET":
                handle_get_service_by_id(handler, resource_id)
            elif method == "PUT":
                handle_update_service(handler, resource_id)
            elif method == "DELETE":
                handle_delete_service(handler, resource_id)
            else:
                handle_404(handler)
        return

    # rotta per il login
    if resource == "login":
        if method == "POST":
            handle_login(handler)
        else:
            handle_404(handler)
        return

    # rotta per il logout
    if resource == "logout":
        if method == "POST":
            handle_logout(handler)
        else:
            handle_404(handler)
        return

    # rotte per gli utenti
    if resource == "users":
        if resource_id is None:
            if method == "GET":
                handle_get_all_users(handler,authenticated_user)
            elif method == "POST":
                handle_create_user(handler)
            else:
                handle_404(handler)
        else:
            if method == "GET":
                handle_get_user_by_id(handler, resource_id)
            elif method == "PUT":
                handle_update_user(handler, resource_id)
            elif method == "DELETE":
                handle_delete_user(handler, resource_id)
            else:
                handle_404(handler)
        return
    
    # rotta per determinare se è presente un utente autenticato
    if resource == "current-user":
        if method == "GET":
            handle_get_current_user(handler)
        else:
            handle_404(handler)
        return
    # se la rotta non è trovata
    handle_404(handler)



def handle_404(handler):
    ''' Funzione di default per gestire le richieste HTTP per rotte non trovate. '''
    error_response = json.dumps({"error": "Rotta non trovata"}).encode("utf-8")
    set_headers(handler, 404,error_response)
    handler.wfile.write(error_response)
