
class HTTPException(Exception):
    pass

class HTTPError(HTTPException):
    def __init__(self, status_code, message):
        super(HTTPError, self).__init__(message)
        self.message = message
        self.status_code = status_code

    def serve_http(self, request, response):
        response.status_int = self.status_code
        response.write(self.message)

class HTTPNotFound(HTTPError):
    def __init__(self, message="404 Not Found", status_code=404):
        super(HTTPNotFound, self).__init__(status_code, message)