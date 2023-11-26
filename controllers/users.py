def users_ctrl(api):

    @api.get("/public/users")
    def users(req, res):
        res.set_cookies("_session_id=TEST-COOKIES;")
        res.with_status(200).sendjson([
            {
                "name": 'toto',
                "age": 33
            },
            {
                "name": 'titi',
                "age": 25
            }
        ])

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