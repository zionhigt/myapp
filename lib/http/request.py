from urllib.parse import urlparse, parse_qs, urlsplit


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
        body = ""
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
        print(self.route, self.query)
        self.proto = proto
        self.options = self.fetch_options(options)
        self.body = self.parse_body(self.options)

    def fetch_options(self, options):
        if isinstance(options, list):
            key = ""
            _options = {}
            value = []
            for i, data in enumerate(options):
                is_last_item = i == len(options) - 1
                if data[-1] == ":" or is_last_item:
                    ## Fixme : last value doesn't save
                    if key:
                        if _options.get(key) is not None:
                            value = _options.get(key) + value
                        if len(value) == 1:
                            value = value[0]
                        _options.update({key: value})
                        value = []
                    key = data[:-1]
                else:
                    value.append(data)
        return _options
    
    def parse_body(self, options):
        body = {}
        if options.get("Content-Disposition") is None:
            return body
        content = options.get("Content-Disposition")

        nxt_is_value = False
        mem_key = ""
        for row in content:
            if row[:5] == "name=":
                mem_key = row.replace('name="', "").replace('"', "")
                nxt_is_value = True
                continue
            if nxt_is_value:
                body.update({
                    mem_key: row
                })
                nxt_is_value = False
                mem_key = ""

        return body

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
        splited_url = list(enumerate(["/" if not i else i for i in uri.split("/")]))
        parsed_url = urlparse(uri)
        return (parsed_url.path, splited_url, parse_qs(parsed_url.query))
