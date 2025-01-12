def _set_headers(handler, code=200, response_data={},content_type="application/json"):
    handler.send_response(code)
    handler.send_header("Access-Control-Allow-Origin", "*")
    # impostazione tipo response json
    handler.send_header("Content-Type", content_type)
    # impostazione content_length
    content_length = str(len(response_data))
    handler.send_header("Content-Length", content_length) 

    handler.end_headers()
