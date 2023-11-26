from urllib.parse import parse_qs


def parser(body, options):
    if isinstance(body, list):
        body = [i.decode() for i in body]
        query = "".join(body)
        _body = parse_qs(query)

        for k, v in _body.items():
            _body[k] = "".join(v)
        return _body
