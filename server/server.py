import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from routes import route_request
from db import init_db
from utility.utility import _set_headers

class MyHandler(BaseHTTPRequestHandler):
    server_version = "CustomHTTPServer"
    sys_version = ""
    protocol_version = "HTTP/1.1"

    def do_OPTIONS(self):
        """Gestisci le richieste preflight per CORS."""
        _set_headers(self, 200)
        

    def do_GET(self):
        """Gestisci le richieste GET."""
        if self.path.startswith("/frontend") or self.path == "/" or self.path.endswith((".html", ".css", ".js")):
            self.serve_static_file()
        else:
            # altrimenti instrada come richiesta API
            route_request(self, "GET")

    def serve_static_file(self):
        """Serve file statici dalla cartella 'frontend'."""
        base_path = os.path.join(os.getcwd(), "frontend")
        requested_path = self.path.lstrip("/")  # Rimuovi il prefisso "/"

        # serve index.html di default se la richiesta punta a una directory o root
        if requested_path == "" or requested_path == "frontend" or requested_path.endswith("/"):
            requested_path = os.path.join(requested_path, "index.html")
        
        file_path = os.path.join(base_path, requested_path)

        # verifica se il file esiste
        if os.path.isfile(file_path):
            self.send_response(200)
            # determina il Content-Type in base all'estensione del file
            if file_path.endswith(".html"):
                content_type = "text/html"
            elif file_path.endswith(".css"):
                content_type = "text/css"
            elif file_path.endswith(".js"):
                content_type = "application/javascript"
            else:
                content_type = "application/octet-stream"

            self.send_header("Content-Type", content_type)
            with open(file_path, "rb") as f:
                file_content = f.read()
                # lunghezza del contenuto del file
                self.send_header("Content-Length", str(len(file_content)))  
                self.end_headers()
                self.wfile.write(file_content)
        else:
            # se il file non esiste, restituisci un 404
            error_response = json.dumps({"error": "File non trovato"}).encode("utf-8")
            
            _set_headers(self, 404,error_response)
            self.wfile.write(error_response)


    def do_POST(self):
        """Gestisci le richieste POST."""
        route_request(self, "POST")

    def do_PUT(self):
        """Gestisci le richieste PUT."""
        route_request(self, "PUT")

    def do_DELETE(self):
        """Gestisci le richieste DELETE."""
        route_request(self, "DELETE")

def run_server(port=8000):
    """Avvia il server."""
    init_db()
    server_address = ("", port)
    httpd = HTTPServer(server_address, MyHandler)
    print(f"Server in esecuzione sulla porta {port}...")
    try:
        # resta in ascolto finché non arriva un KeyboardInterrupt
        httpd.serve_forever()  
    except KeyboardInterrupt:
        print("\nRicevuto Ctrl + C: chiusura del server...")
    finally:
        httpd.shutdown()
        httpd.server_close()
        print("Server terminato correttamente.")
        sys.exit(0)
if __name__ == "__main__":
    run_server()
