class BadStatusException(Exception):
    def __init__(self, status):
        super().__init__(f"{status} is not a valid HTTP status code")