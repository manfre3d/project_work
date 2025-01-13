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

        # aggiungi log per il percorso richiesto
        print(f"Richiesta file statico: {requested_path}")

        # serve index.html di default se la richiesta punta a una directory o root
        if requested_path == "" or requested_path.endswith("/"):
            requested_path = os.path.join(requested_path, "index.html")

        # costruisce il percorso assoluto del file richiesto
        file_path = os.path.join(base_path, requested_path)

        # verifica se il file esiste
        if os.path.isfile(file_path):
            try:
                with open(file_path, "rb") as f:
                    file_content = f.read()

                self.send_response(200)

                # determina il content-type in base all'estensione del file
                content_type = self._get_content_type(file_path)
                self.send_header("Content-Type", content_type)

                # lunghezza del contenuto del file
                self.send_header("Content-Length", str(len(file_content)))
                self.end_headers()
                self.wfile.write(file_content)
                print(f"Servito file statico: {file_path}")

            except Exception as e:
                print(f"Errore durante il caricamento del file statico: {e}")
                error_response = json.dumps({"error": "Errore interno del server"}).encode("utf-8")
                self._send_error(500, error_response)
        else:
            # se il file non esiste, restituisci un 404
            print(f"File non trovato: {file_path}")
            error_response = json.dumps({"error": "File non trovato"}).encode("utf-8")
            self._send_error(404, error_response)

    def _get_content_type(self, file_path):
        """Determina il Content-Type in base all'estensione del file."""
        if file_path.endswith(".html"):
            return "text/html"
        elif file_path.endswith(".css"):
            return "text/css"
        elif file_path.endswith(".js"):
            return "application/javascript"
        elif file_path.endswith(".png"):
            return "image/png"
        elif file_path.endswith(".jpg") or file_path.endswith(".jpeg"):
            return "image/jpeg"
        elif file_path.endswith(".gif"):
            return "image/gif"
        elif file_path.endswith(".svg"):
            return "image/svg+xml"
        elif file_path.endswith(".ico"):
            return "image/x-icon"
        return "application/octet-stream"

    def _send_error(self, code, message):
        """Invia un messaggio di errore al client."""
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(message)))
        self.end_headers()
        self.wfile.write(message)


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
