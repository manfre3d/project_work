import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from routes import route_request
from db import init_db

class MyHandler(BaseHTTPRequestHandler):
    server_version = "CustomHTTPServer"
    sys_version = ""
    protocol_version = "HTTP/1.1"

    def do_OPTIONS(self):
        """Handle browser preflight requests (CORS)"""
        print("Received OPTIONS for:", self.path)
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, content-type")
        self.end_headers()
        print("Responded OPTIONS OK")

    def do_GET(self):
        route_request(self, "GET")

    def do_POST(self):
        route_request(self, "POST")

    def do_PUT(self):
        route_request(self, "PUT")

    def do_DELETE(self):
        route_request(self, "DELETE")

def run_server(port=8000):
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
