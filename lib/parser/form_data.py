from urllib.parse import parse_qs

def parser(body, options):
    
    if isinstance(body, list):
        _body = {}
        content_type = options.get("Content-Type")
        if content_type is not None:
            boundary = "--" + content_type[1].replace("boundary=", "")
            name, value = "", ""
            body = b"\r\n".join(body).split(b"\r\n")
            bufferize = False
            mime = ""
            filename = ""
            for i, token in enumerate(body):
                is_last_item = i == len(body) - 1
                if is_last_item and bufferize and value:
                    value.append(token)

                if not token or token == boundary.encode() or is_last_item:
                    if bufferize:
                        name = name or "file"
                        value = {
                            "filename": filename,
                            "mimetype": mime,
                            "data": b"\r\n".join(value)

                        }
                    bufferize = False
                    if not is_last_item:
                        continue

                if name and value and not bufferize:

                    _body.update({
                        name: value
                    })
                    if is_last_item:
                        break
                    name, value, filename, mime = "", "", "", ""

                if bufferize and not value:
                    value = []

                if b"Content-Disposition" in token:
                    disposition, content = token.split(b": ")
                    type, *name_text = content.split(b"; ")
                    if len(name_text) == 1:
                        name = b"".join(name_text).decode().replace('name="', '').replace('"', '')
                    if len(name_text) > 1:
                        args = parse_qs(b"&".join(name_text).decode())
                        name = args.get("name", [''])[0].replace('"', '')
                        filename = args.get("filename", [''])[0].replace('"', '')
                    continue

                if b"Content-Type" in token:
                    key, mime = token.split(b": ")
                    mime = mime.decode()
                    bufferize = True
                    continue

                if bufferize:
                    value.append(token)
                    continue

                value = token.decode()
                
    return _body