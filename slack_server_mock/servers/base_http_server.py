"""Base HTTP Server """
import logging

from tornado.httpserver import HTTPServer
from tornado.web import Application

LOGGER = logging.getLogger(__name__)


class BaseHTTPServer():
    """ Mock Implementation of the Slack HTTP server """
    def __init__(self, app: Application, port: int) -> None:
        self._http_server = HTTPServer(app)
        self._port = port

    def run(self):
        """ Start the HTTP Server """
        LOGGER.info('HTTP server running on port %i', self._port)
        self._http_server.listen(self._port)

    def stop(self):
        """ Stop the HTTP Server """
        self._http_server.stop()
        LOGGER.info('HTTP server on port %i shutdown', self._port)
