import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from routes import route_request
from db import init_db
from utility.utility import set_headers
from socketserver import ThreadingMixIn

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    """Server HTTP che supporta il multi-threading."""
    # quando il server è terminato chiude i thread 
    daemon_threads = True

class MyHandler(BaseHTTPRequestHandler):
    server_version = "CustomHTTPServer"
    sys_version = ""
    protocol_version = "HTTP/1.1"

    def do_OPTIONS(self):
        """Gestisce le richieste OPTIONS. 
        Utilizzato per la preflight CORS."""
        set_headers(self, 200)

    def do_GET(self):
        """Gestisce le richieste GET. E inoltre serve file statici del front end."""
        # serve/fornisce i file statici dalla cartella 'frontend'        
        if self.path.startswith("/frontend") or self.path == "/" or self.path.endswith(
            (".html", ".css", ".js", ".png", ".jpg", ".jpeg", ".ico", ".svg")):
            self.serve_static_file()
        else:
            # gestione di richieste API
            route_request(self, "GET")

    def serve_static_file(self):
        """Serve i file statici dalla cartella 'frontend'."""
        # costruisce il percorso per recuperare il file richiesto
        base_path = os.path.join(os.getcwd(), "frontend")
        requested_path = self.path.lstrip("/") 

        # log per debug
        print(f"Richiesta file statico: {requested_path}")

        # restituisce l'index.html di default se viene richiesta la root
        if not requested_path or requested_path.endswith("/"):
            requested_path = os.path.join(requested_path, "index.html")

        # costruisce il percorso completo del file
        file_path = os.path.join(base_path, requested_path)
        print(f"Percorso completo: {file_path}")

        # verifica se il file esiste
        if os.path.isfile(file_path):
            try:
                self._read_and_send_file(file_path)
            except Exception as e:
                print(f"Errore durante il caricamento del file statico: {e}")
                error_response = json.dumps({"error": "Errore interno del server"}).encode("utf-8")
                set_headers(self, 500, error_response )
                self.wfile.write(error_response)
        else:
            print(f"File non trovato: {file_path}")
            error_response = json.dumps({"error": "File non trovato"}).encode("utf-8")
            set_headers(self, 404, error_response )
            # todo: inserire nel metodo set_headers self.wfile.write(***) visto che passo il parametro response_data
            self.wfile.write(error_response)

    def _read_and_send_file(self, file_path):
        """Serve un singolo file statico."""
        with open(file_path, "rb") as f:
            file_content = f.read()

        content_type = self._get_content_type(file_path)
        set_headers(self, 200, file_content,content_type)
        self.wfile.write(file_content);
        print(f"File statico servito: {file_path}")

    def _get_content_type(self, file_path):
        """restituisce in base all'estensione del file il Content-Type."""
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
        elif file_path.endswith(".ico"):
            return "image/x-icon"
        return "application/octet-stream"

    def do_POST(self):
        """Gestisce le richieste POST."""
        route_request(self, "POST")

    def do_PUT(self):
        """Gestisce le richieste PUT."""
        route_request(self, "PUT")

    def do_DELETE(self):
        """Gestisce le richieste DELETE."""
        route_request(self, "DELETE")

def run_server(port=8000):
    """Avvia il server multi-threaded."""
    init_db()
    server_address = ("0.0.0.0", port)
    httpd = ThreadingHTTPServer(server_address, MyHandler)
    print(f"Server multi-threaded in esecuzione sulla porta {port}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nRicevuto Ctrl + C: chiusura del server...")
    finally:
        httpd.shutdown()
        httpd.server_close()
        print("Server terminato correttamente.")

if __name__ == "__main__":
    run_server()
