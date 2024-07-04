""" Actor HTTP Server """
from tornado.httpserver import HTTPServer
from tornado.web import Application


class BaseHTTPServer():
    """ Mock Implementation of the Slack HTTP server """
    def __init__(self, app: Application, port: int) -> None:
        self._http_server = HTTPServer(app)
        self._port = port

    def run(self):
        """ Start the HTTP Server """
        print(f"HTTP server running on port {self._port}")
        self._http_server.listen(self._port)

    def stop(self):
        """ Stop the HTTP Server """
        self._http_server.stop()
        print("HTTP server shutdown")
