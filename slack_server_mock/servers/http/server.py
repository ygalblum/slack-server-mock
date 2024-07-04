""" HTTP Server """
from injector import inject, singleton
from tornado.web import Application


from slack_server_mock.injector.di import global_injector
from slack_server_mock.settings.settings import Settings
from slack_server_mock.servers.base_http_server import BaseHTTPServer
from slack_server_mock.servers.http import handler


@singleton
class SlackHTTPServer(BaseHTTPServer):
    """ Mock Implementation of the Slack HTTP server """
    @inject
    def __init__(self, settings: Settings) -> None:
        app = Application(
            [
                (r"/auth.test", handler.AuthTestHandler),
                (r"/apps.connections.open", handler.AppsConnectionsOpenHandler),
                (r"/api.test", handler.ApiTestHandler),
                (r"/chat.postMessage", handler.ChatPostMessageHandler)
            ]
        )
        super().__init__(app, settings.http_server.port)


def start_http_server():
    """ Static method for starting the HTTP Server """
    global_injector.get(SlackHTTPServer).run()


def stop_http_server():
    """ Static method for stopping the HTTP Server """
    global_injector.get(SlackHTTPServer).stop()
