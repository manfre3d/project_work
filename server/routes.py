
def route_request(handler, method):
    path = handler.path



    # Se nessuna rotta corrisponde, 404
    handle_404(handler)

def handle_404(handler):
    handler.send_response(404)
    handler.send_header("Content-Type", "application/json")
    handler.end_headers()
    handler.wfile.write(b'{"error": "Not found"}')
