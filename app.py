def app(api=None):
    if api is not None:
        class Application:
            def __init__(self, api):
                self.api = api
                self.api.expose("./public", "/")

            
            @api.get(["/public", "/public/:user"])
            @api.middleware("security.auth.check_user")
            def public(req, res):
                user = req.params.get("user")
                if user is None:
                    data = {
                        "message": "Called without params" 
                    }
                else:
                    data = {
                        "context": {},
                        "user" : {
                            "id": user
                        }
                    }
                return res.with_status(201).sendjson(data)
            
        return Application(api)