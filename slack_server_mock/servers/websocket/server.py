""" WebSocket Server """
from injector import inject, singleton
from tornado.httpserver import HTTPServer
from tornado.web import Application

from slack_server_mock.actor.actor import Actor
from slack_server_mock.injector.di import global_injector
from slack_server_mock.servers.websocket import handler
from slack_server_mock.settings.settings import Settings


@singleton
class SlackWebSocketServer():
    """ Mock Implementation of the Slack WebSocket server """
    @inject
    def __init__(self, settings: Settings, actor: Actor) -> None:
        self._port = settings.websocket_server.port
        self._actor = actor
        ws_app = Application(
            [
                (r"/link", handler.SlackWebSocketHandler),
            ]
        )
        self._ws_server = HTTPServer(ws_app)

    def run(self):
        """ Start the HTTP Server """
        print(f"WebSocket server running on port {self._port}")
        self._ws_server.listen(self._port)

    def stop(self):
        """ Stop the HTTP Server """
        self._ws_server.stop()
        print(f"WebSocket server shutdown")


def start_websocket_server():
    global_injector.get(SlackWebSocketServer).run()


def stop_websocket_server():
    global_injector.get(SlackWebSocketServer).stop()
