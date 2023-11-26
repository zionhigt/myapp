from controllers.index import init as init_controllers

def app(api=None):
    if api is not None:
        class Application:
            def __init__(self, api):
                self.api = api
                self.api.expose("./public", "/")
                init_controllers(self.api)

            @api.get("/redirect")
            def redirect(req, res):
                res.redirect("/public/9")
            
            
        return Application(api)