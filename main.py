from socket import socket, AF_INET, SOCK_STREAM

from lib.http.response import Response
from lib.http.request import Request

from lib.api import Api
from app import app


class Controller:
        
    def __init__(self, route, function, options={}):
        self.route, self.params = self.prepare_route(route)
        self.function = function
        self.type = "router"
        if options.get("type") is not None:
            self.type = options.get("type")
        
        self.has_alias = False
        if options.get("has_alias") is not None:
            self.type = options.get("has_alias")
    
    def match_params(self, params, self_params=None):
        if self_params is None:
            self_params = self.params

        if not isinstance(self_params, list):
            if getattr(self_params, "items", False):
                for route, self_param in self_params.items():
                    if self.match_params(params, self_param):
                        return self_param
                return False 
            
        if not len(params) or len(params) != len(self_params):
            return False
        for i, self_param in enumerate(self_params):
            compare = params[i]
            if self_param[1][0] == ":":
                self_param = compare
            if self_param != compare:
                return False
        return self_params
        
    
    def prepare_route(self, route):
        if isinstance(route, list):
            result = {}
            for r in route:
                result[r] = self.prepare_route(r)[1]
            return route, result
        
        splited_url = list(enumerate(["/" if not i else i for i in route.split("/")]))
        return route, splited_url


class Server:
    @staticmethod
    def get_instance(*args, **kwargs):
        try:
            return Server(**kwargs)
        except OSError as e:
            print(e)
            if kwargs.get("force_port", False):
                print("Increment port")
                kwargs.update({
                    "port": kwargs.get("port", 1337) + 1
                })
                return Server.get_instance(**kwargs)
            else:
                raise e
        
    def __init__(self, host, port, app, config={}):
        self.host = host
        self.port = port
        self.app = app
        self._max_size_request = config.get("max_size_request")
        self._server = socket(AF_INET, SOCK_STREAM)
        self._server.bind((self.host, self.port))
        self._controllers = {
            "GET": [],
            "POST": [],
            "OPTIONS": [],
            "HEADERS": [],
            "DELETE": [],
            "PATCH": [],
            "UPDATE": [],
        }

        self.init_api(app.api)
        self._controllers
    
    @property
    def max_size_request(self):
        if self._max_size_request is not None:
            return self._max_size_request
        return 20480000
    
    def _subcribe_controller(self, verb, route, controller):
        if self._controllers.get(verb.upper()) is not None:
            self._controllers[verb.upper()].append(Controller(route, controller))

    def init_api(self, api):
        for ctrl in api.controllers:
            self._subcribe_controller(*ctrl)

    def dispatch(self, request):
        controller = None
        controllers = self._controllers.get(request.verb.upper())
        if controllers is not None:
            for ctrl in controllers:
                match_params = ctrl.match_params(request._params)
                if match_params:
                    if isinstance(match_params, list):
                        def bind_params(req, res):
                            req.bind_params(match_params)
                            return ctrl.function(req, res)
                        
                        controller = bind_params
                    else:
                        controller = ctrl.function
                    break
        return controller
    
    def listen(self):
        self._server.listen()
        print(f"Listening on {self.host}:{self.port}")

        while True:
            try:
                client, origin = self._server.accept()
                max_chunk = self.max_size_request
                buffer_size = 2048
                chunk = b''
                while True:
                    _chunk = client.recv(buffer_size)
                    if len(chunk) < max_chunk:
                        chunk += _chunk
                        if len(_chunk) < buffer_size:
                            break
                    else:
                        break
                if len(chunk):
                    request = Request(**self.parse_request(chunk))
                    response = Response(client)
                    controller = self.dispatch(request)
                    if controller is not None:
                        controller(req=request, res=response)
                    else:
                        response.not_found()

            except OSError:
                continue
            except KeyboardInterrupt:
                break
        self._server.close()

    def parse_request(self, chunk):
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

server = Server.get_instance(host="localhost", port=1337, app=app(Api()), force_port=True)
server.listen()



