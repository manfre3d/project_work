def _set_headers(handler, code=200, response_data=b'', content_type="application/json", extra_headers=None, origin="http://localhost:8000"):
    handler.send_response(code)
    handler.send_header("Access-Control-Allow-Origin", origin)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Accept", content_type)
    handler.send_header("Access-Control-Allow-Credentials", "true")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
    if extra_headers:
        for header, value in extra_headers.items():
            handler.send_header(header, value)
    
    content_length = str(len(response_data))
    handler.send_header("Content-Length", content_length)
    handler.end_headers()