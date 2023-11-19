from mimetypes import MimeTypes
import json
from os import path
from exceptions.http_exeptions import BadStatusException
from http_status import status_mapping



DEFAULT_HTTP = {
    '__head__': "HTTP/1.1 %s %s\r\n",
    '__header__': {
        'Content-Type': "text/html",
        "Host": "localhost",
        'Access-Control-Allow-Origin': '*'
    }
} 


class Response:
    def __init__(self, client, options=DEFAULT_HTTP):
        self.client = client
        self.options = options
        self._status = None
        self._status_text = ""
        self._content_type = "text/html"

    @property
    def content_type(self):
        return self._content_type
    
    @content_type.setter
    def content_type(self, value):
        self._content_type = value
        self.options["__header__"]["Content-Type"] = self._content_type
        return self.content_type

    @property
    def status(self):
        return f'{self._status} {self._status_text}'
    
    @status.setter
    def status(self, code):
        if not isinstance(code, int):
            try:
                code = int(code)
            except TypeError:
                raise BadStatusException()
            
        if str(code) not in status_mapping:
            raise BadStatusException()
        
        self._status = code
        self._status_text = status_mapping.get(str(code))
    
    @property
    def header(self):
        _header = ""
        header = self.options.get("__header__")
        if header is not None:
            _header = []
            for key in header:
                value = header.get(key)
                _header.append(f"{key}: {value}")
            _header = "\n".join(_header)
        return _header.encode() + b'\r\n\r\n'
    
    @property
    def head(self):
        head = ""
        _head = self.options.get("__head__")
        if _head is not None:
            head = _head % (
                    self._status,
                    self._status_text,
                )
        return head.encode()

    def with_status(self, code):
        try:
            self.status = code
            return self
        
        except BadStatusException:
            print("Unable to use this status code : " + code)

    def sendall(self, content):
        if content and isinstance(content, str):
            content = content.encode()
        res = self.head + self.header + content
        self.client.send(res)
        self.client.close()
    
    def not_found(self):
        self.content_type = "text/html"
        return self.with_status(404).sendall(
            b'<center><strong>Not found</strong></center><center><small>Dev API v 0.0.1</small></center>'
        )
    
    def sendtext(self, content):
        self.content_type = "text/plain"
        self.sendall(content.encode())

    def sendhtml(self, content):
        self.content_type = "text/html"
        self.sendall(content.encode())

    def sendjson(self, content):
        self.content_type = "application/json;charset=utf-8"
        self.sendall(json.dumps(content).encode())

    def sendfile(self, _path):
        try:
            mime = MimeTypes()
            content_type = mime.guess_type(_path)
            if len(content_type):
                content_type = content_type[0]
                self.content_type = content_type

            with open(_path, 'rb') as index:
                return self.sendall(index.read())
            
        except FileNotFoundError:
            return self.not_found()
