import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from routes import route_request
from db import init_db

class MyHandler(BaseHTTPRequestHandler):
    server_version = "CustomHTTPServer"
    sys_version = ""
    protocol_version = "HTTP/1.1"

    def do_OPTIONS(self):
        """Gestisci le richieste preflight per CORS."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "http://localhost:8000")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Credentials", "true")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self):
        """Gestisci le richieste GET."""
        if self.path.startswith("/frontend") or self.path == "/" or self.path.endswith((".html", ".css", ".js")):
            self.serve_static_file()
        else:
            # Altrimenti instrada come richiesta API
            route_request(self, "GET")

    def serve_static_file(self):
        """Serve file statici dalla cartella 'frontend'."""
        base_path = os.path.join(os.getcwd(), "frontend")
        requested_path = self.path.lstrip("/")  # Rimuovi il prefisso "/"

        # Serve index.html di default se la richiesta punta a una directory o root
        if requested_path == "" or requested_path == "frontend" or requested_path.endswith("/"):
            requested_path = os.path.join(requested_path, "index.html")
        
        file_path = os.path.join(base_path, requested_path)

        # Verifica se il file esiste
        if os.path.isfile(file_path):
            self.send_response(200)
            # Determina il Content-Type in base all'estensione del file
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
                self.send_header("Content-Length", str(len(file_content)))  # Specifica la lunghezza
                self.end_headers()
                self.wfile.write(file_content)
        else:
            # Se il file non esiste, restituisci un 404
            self.send_response(404)
            response_body = b"File not found"
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(response_body)))  # Aggiungi Content-Length
            self.end_headers()
            self.wfile.write(response_body)


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
        # Resta in ascolto finché non arriva un KeyboardInterrupt
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
