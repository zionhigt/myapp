import json

def parser(body, options):
    if body:
        try:
            return json.loads(b"".join(body).decode())
        except json.decoder.JSONDecodeError:
            return {}
