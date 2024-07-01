from http.server import HTTPServer

from injector import inject, singleton

from slack_server_mock.injector.di import global_injector
from slack_server_mock.settings.settings import Settings
from slack_server_mock.servers.http.handler import MockHandler


@singleton
class Server():
    @inject
    def __init__(self, settings: Settings) -> None:
        self._port = settings.http_server.port
        self._httpd = HTTPServer(('', self._port), MockHandler)

    def run(self):
        print("HTTP server running on port 8888")
        self._httpd.serve_forever()
        print("HTTPD server saying goodbye")

    def stop(self):
        self._httpd.shutdown()


def start_http_server():
    global_injector.get(Server).run()


def stop_http_server():
    global_injector.get(Server).stop()