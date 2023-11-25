def fetch_options(options):
        _options = {}
        if isinstance(options, list):
            key = ""
            value = []
            for i, data in enumerate(options):
                if data[-1] == ":":
                    if not key:
                        key = data[:-1]
                        continue
                else:
                    value.append(data)
                    if i != len(options) - 1:
                        continue

                if len(value) == 1:
                    value = value[0]
                _options.update({key: value})
                key = data[:-1]
                value = []

        return _options
