""" HTTP Server """
from injector import inject, singleton
from tornado.httpserver import HTTPServer
from tornado.web import Application


from slack_server_mock.injector.di import global_injector
from slack_server_mock.settings.settings import Settings
from slack_server_mock.servers.http import handler


@singleton
class SlackHTTPServer():
    """ Mock Implementation of the Slack HTTP server """
    @inject
    def __init__(self, settings: Settings) -> None:
        self._port = settings.http_server.port
        app = Application(
            [
                (r"/auth.test", handler.AuthTestHandler),
                (r"/apps.connections.open", handler.AppsConnectionsOpenHandler),
                (r"/api.test", handler.ApiTestHandler),
                (r"/chat.postMessage", handler.ChatPostMessageHandler)
            ]
        )
        self._http_server = HTTPServer(app)

    def run(self):
        """ Start the HTTP Server """
        print(f"HTTP server running on port {self._port}")
        self._http_server.listen(self._port)

    def stop(self):
        """ Stop the HTTP Server """
        self._http_server.stop()
        print("HTTP server shutdown")


def start_http_server():
    """ Static method for starting the HTTP Server """
    global_injector.get(SlackHTTPServer).run()


def stop_http_server():
    """ Static method for stopping the HTTP Server """
    global_injector.get(SlackHTTPServer).stop()
