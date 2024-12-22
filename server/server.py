from http.server import BaseHTTPRequestHandler, HTTPServer
from routes import route_request
from db import init_db

class MyHandler(BaseHTTPRequestHandler):
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
