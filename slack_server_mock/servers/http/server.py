""" HTTP Server """
from http.server import HTTPServer

from injector import inject, singleton

from slack_server_mock.injector.di import global_injector
from slack_server_mock.settings.settings import Settings
from slack_server_mock.servers.http.handler import SlackHTTPHandler


@singleton
class SlackHTTPServer():
    """ Mock Implementation of the Slack HTTP server """
    @inject
    def __init__(self, settings: Settings) -> None:
        self._port = settings.http_server.port
        self._httpd = HTTPServer(('', self._port), SlackHTTPHandler)

    def run(self):
        """ Start the HTTP Server """
        print("HTTP server running on port 8888")
        self._httpd.serve_forever()
        print("HTTPD server saying goodbye")

    def stop(self):
        """ Stop the HTTP Server """
        self._httpd.shutdown()


def start_http_server():
    """ Static method for starting the HTTP Server """
    global_injector.get(SlackHTTPServer).run()


def stop_http_server():
    """ Static method for stopping the HTTP Server """
    global_injector.get(SlackHTTPServer).stop()
