from http.server import BaseHTTPRequestHandler, HTTPServer
from routes import route_request
from db import init_db

class MyHandler(BaseHTTPRequestHandler):
    server_version = "CustomHTTPServer"
    sys_version = ""
    protocol_version = "HTTP/1.1"

    def do_OPTIONS(self):
        """Handle browser preflight requests (CORS)"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

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
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
