import json
from urllib.parse import urlparse, parse_qs
from utility.session import get_session_id, get_user_id_from_session

def set_headers(
    handler, code=200,
    response_data=b'',
    content_type="application/json",
    extra_headers=None, 
    origin="http://localhost:8000"):
    handler.send_response(code)
    handler.send_header("Access-Control-Allow-Origin", origin)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Accept", content_type)
    handler.send_header("Access-Control-Allow-Credentials", 
                        "true")
    handler.send_header("Access-Control-Allow-Methods",
                        "GET, POST, PUT, DELETE, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers",
                        "Content-Type, Authorization")
    if extra_headers:
        for header, value in extra_headers.items():
            handler.send_header(header, value)
    
    content_length = str(len(response_data))
    handler.send_header("Content-Length", content_length)
    handler.end_headers()
    

def parse_path(path):
    # separa il percorso principale dai parametri di query
    parsed_url = urlparse(path)
    path_without_query = parsed_url.path.strip("/")
    parts = path_without_query.split("/")

    if len(parts) == 1:
        resource = parts[0]
        return resource, None  
    elif len(parts) == 2 and parts[1].isdigit():
        resource = parts[0]
        resource_id = parts[1]
        return resource, resource_id
    return None, None



def parse_query(path):
    # analizza i parametri di query e restituisce un dizionario
    parsed_url = urlparse(path)
    return {k: v[0] for k, v in parse_qs(parsed_url.query).items()}


def verify_session(handler):
    # verifica se l'utente è loggato
        # ottieni il session_id
    session_id = get_session_id(handler)
    if not session_id:
        error_response = json.dumps({"error": "Sessione non valida o non fornita"}).encode("utf-8")
        set_headers(handler, 401, error_response)
        handler.wfile.write(error_response)
        return

    # verifica l'utente associato alla sessione
    user_id = get_user_id_from_session(session_id)
    if not user_id:
        error_response = json.dumps({"error": "Sessione scaduta o non valida"}).encode("utf-8")
        set_headers(handler, 401, error_response)
        handler.wfile.write(error_response)
        return

def extrapolate_user_id_from_session(handler):
    # estrai l'ID utente dalla sessione
    session_id = get_session_id(handler)
    if not session_id:
        return None
    user_id = get_user_id_from_session(session_id)
    
    if not user_id:
        return None
    
    return user_id