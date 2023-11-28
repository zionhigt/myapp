from socket import socket, AF_INET, SOCK_STREAM

from lib.http.response import Response

from lib.http.request import Request
Request = Request.get_instance

from lib.http.controller import Controller
Controller = Controller.get_instance

from lib.api import Api

from app import app

import config


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
        
    def __init__(self, host, port, app, config={}, *args, **kwargs):
        self.host = host
        self.port = port
        self.app = app
        self._max_size_request = getattr(config, "max_size_request", None)
        self._server = socket(AF_INET, SOCK_STREAM)
        self._server.bind((self.host, self.port))
        self.ctrl = Controller()
        self._controllers = {
            "GET": [],
            "POST": [],
            "OPTIONS": [],
            "HEADERS": [],
            "DELETE": [],
            "PATCH": [],
            "UPDATE": [],
            "USE": [],
        }

        self.init_api(app.api)
        self._controllers
    
    @property
    def max_size_request(self):
        if self._max_size_request is not None:
            return self._max_size_request
        return 20480000
    
    def _subcribe_controller(self, verb, routes, controller):
        if not isinstance(routes, list):
            routes = [routes]
        for route in routes:
            self.ctrl.append_children(route, verb, controller)

    def init_api(self, api):
        for ctrl in api.controllers:
            self._subcribe_controller(*ctrl)

    def dispatch(self, request):
        controller = None
        node = self.ctrl.get_node(request.route)
        if node is not None:
            if node.value is not None and node.value.get(request.verb) is not None:
                request.bind_params(list(enumerate(node.params)))
                return node.value[request.verb]
        
        return controller
    
    def listen(self, timeout=1):
        self._server.listen()
        print(f"Listening on {self.host}:{self.port}")
        client = False
        while True:
            try:
                if not client or client._closed:
                    client, origin = self._server.accept()
                # chunk's timeout
                client.settimeout(timeout)
                max_chunk = self.max_size_request
                buffer_size = 2048
                chunk = b''
                while True:
                    try:
                        _chunk = client.recv(buffer_size)
                        if not _chunk:
                            break
                        if len(chunk) < max_chunk:
                            chunk += _chunk
                        else:
                            break
                    except OSError as e:
                        if e.__str__() == "timed out":
                            break
                        
                if len(chunk):
                    response = Response(client)
                    request = Request(chunk)
                    if request is not None:
                        controller = self.dispatch(request)
                        if controller is not None:
                            if isinstance(controller, list):
                                controller = controller[0]
                            
                            controller(req=request, res=response)
                        else:
                            response.not_found()
                    else:
                        response.bad_request()
                
                client.close()


            except OSError:
                continue
            except KeyboardInterrupt:
                break
        self._server.close()


server = Server.get_instance(
    host="localhost",
    port=1337,
    app=app(Api()),
    force_port=True,
    config=config
)
server.listen()



