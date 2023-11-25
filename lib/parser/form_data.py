

def parser(body, options):
    
    if isinstance(body, list):
        _body = {}
        content_type = options.get("Content-Type")
        if content_type is not None:
            boundary = content_type[1].replace("boundary=", "")
            name, value = "", ""
            for row in body:

                for token in row.split("\r\n"):
                    if name and value:
                        _body.update({
                            name: value
                        })
                        name, value = "", ""
                    if token:
                        if token[:2] == "--":
                            continue
                        if "Content-Disposition" in token:
                            disposition, content = token.split(": ")
                            type, name_text = content.split("; ")
                            name = name_text.replace('name="', '').replace('"', '')
                            print(disposition, type, name)
                            continue
                        value = token
    return _body