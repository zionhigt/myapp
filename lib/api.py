from os import path, scandir

    
class Api:
    def __init__(self):
        self.controllers = []

    def get(self, route):
        def wrapper(ctrl):
            self.controllers.append(("GET", route, ctrl))
        return wrapper
    
    def post(self, route):
        def wrapper(ctrl):
            self.controllers.append(("POST", route, ctrl))
        return wrapper
    
    def expose(self, _path, alias):
        if not path.exists(_path) or not path.isdir(_path):
            raise Exception("Not found the folder to expose")
        
        def exposer(req, res):
            file_path = path.join(_path, path.relpath(req.route, alias))
            return res.with_status(200).sendfile(file_path)
        
        for file in scandir(_path):
            aliased_path = path.join(alias, file.name)
            if path.isdir(file.path):
                self.expose(file.path, aliased_path)
            self.controllers.append(("GET", aliased_path, exposer))
    
    def _import(self, path):
        try:
            nss = list(enumerate(path.split(".")))
            ns = ".".join([j for i, j in nss[:-1]])
            mod = __import__(ns)
            sub = mod
            for child in nss[1:]:
                sub = getattr(sub, child[1], None)
            methode = sub
            if methode is None:
                raise ImportError
            return methode
        
        except ImportError:
            print(path + " : cannot be imported")

    def middleware(self, ns):
        _middle = self._import(ns)
        def wrapper(fn):
            def wrap(req, res):
                def next():
                    return fn(req, res)
                _middle(req, res, next)
            return wrap
        return wrapper