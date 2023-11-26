def data_ctrl(api):

    @api.post("/data")
    def data(req, res):
        if isinstance(req.body, dict):
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
