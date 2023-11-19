from urllib.parse import urlparse, parse_qs, urlsplit


class Request:
    def __init__(self, verb, route, proto, options):
        self.verb = verb
        self.route, self._params, self.query = self.parse_uri(route)
        self.params = {}
        print(self.route, self.query)
        self.proto = proto
        self.options = self.fetch_options(options)
    
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

    def fetch_options(self, options):
        if isinstance(options, list):
            key = ""
            _options = {}
            value = []
            for i, data in enumerate(options):
                is_last_item = i == len(data) - 1
                if data[-1] == ":" or is_last_item:
                    if key:
                        if len(value) == 1:
                            value = value[0]
                        _options.update({key: value})
                        value = []
                    key = data[:-1]
                else:
                    value.append(data)
        return _options