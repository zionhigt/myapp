def check_user(req, res, next):
    authorized_users = [
        "5",
        "6",
        "7",
        "8",
        "9",
    ]

    user_id = req.params.get("user")
    if user_id is not None and user_id in authorized_users:
        req.params.update({
            "auth": True
        })
        next()
    else:
        res.with_status(403).sendtext("Unauthorized")