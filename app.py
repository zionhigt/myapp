def app(api=None):
    if api is not None:
        class Application:
            def __init__(self, api):
                self.api = api
                self.api.expose("./public", "/")

            @api.post("/data")
            def data(req, res):
                if req.body.get("file") is not None:
                    data_file = req.body["file"].pop("data")

                    with open("./" + req.body["file"]["filename"], "wb") as file:
                        file.write(data_file)
                if req.body.get("file_1") is not None:
                    data_file_1 = req.body["file_1"].pop("data")

                    with open("./" + req.body["file_1"]["filename"], "wb") as file_1:
                        file_1.write(data_file_1)
                res.with_status(201).sendjson({
                    "data-receive": req.body
                })

            @api.get("/redirect")
            def redirect(req, res):
                res.redirect("/public/9")


            @api.get(["/public/:user"])
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
                return res.with_status(200).sendjson(data)
            
        return Application(api)