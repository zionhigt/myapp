from urllib.parse import urlparse, parse_qs, urlsplit


from lib.parser import (
    form_data,
    form_urlencoded as urlencoded
)

from lib.parser.options import fetch_options



class Request:

    @staticmethod
    def get_instance(*args, **kwargs):
        chunk = args[0]
        if len(args) > 1:
            chunk = kwargs.get("chunk")
        if chunk is not None:
            return Request(**Request.parse_chunk(chunk))

    @staticmethod
    def parse_chunk(chunk):
        decomposed = chunk.decode().split("\r\n\r\n")
        body = None
        headers = decomposed[0]
        if len(decomposed) > 1:
            body = decomposed[1:]
        items = headers.split()
        verb, route, proto, *options = items
        return {
            "verb": verb,
            "route": route,
            "proto": proto,
            "options": options,
            "body": body
        }
    
    def __init__(self, verb, route, proto, options, body):
        self.verb = verb
        self.route, self._params, self.query = self.parse_uri(route)
        self.params = {}
        self.proto = proto
        self.options = fetch_options(options)
        self._content_type = self._get_content_type()
        self.options.update({
            "Content-Type": self._content_type,
        })
        self.body = self.parse_body(body, self.options)

    @property
    def content_type(self):
        if self._content_type:
            content_type = self._content_type
            if isinstance(content_type, list):
                return content_type[0]
            return content_type 
    
    def _get_content_type(self):
        content_type = self.options.get("Content-Type")
        if content_type is not None:
            if isinstance(content_type, list):
                content_type = "".join(content_type)
            if ";" in content_type:
                splited = content_type.split(";")
                content_type = [i for i in splited if i]
                if len(content_type) == 1:
                    content_type = content_type[0]
        return content_type

    @property
    def parsers(self):
        return {
            "multipart/form-data": form_data.parser,
            "application/x-www-form-urlencoded": urlencoded.parser,
        }

    def _parse_body(self):
        return self.parsers.get(self.content_type, self.parsers["application/x-www-form-urlencoded"])
    
    def parse_body(self, body, options):
        if body is None:
            body = {}
        return self._parse_body()(body, options)

    def bind_params(self, params):
        if not any([i[1][0] == ":" for i in params]):
            return
        for param in params:
            if param[1][0] == ":":
                key = param[1][1:]
                value = list(filter(lambda x: x[0] == param[0], self._params))
                if len(value):
                    self.params.update({
                        key: value[0][1]
                    })

    def parse_uri(self, uri):
        parsed_url = urlparse(uri)
        splited_url = list(enumerate(["/" if not i else i for i in parsed_url.path.split("/")]))
        return (parsed_url.path, splited_url, parse_qs(parsed_url.query))
