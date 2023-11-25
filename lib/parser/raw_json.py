import json

def parser(body, options):
    if body:
        try:
            return json.loads("".join(body))
        except json.decoder.JSONDecodeError:
            return {}
