""" WebSocket Server """
import logging

from injector import inject, singleton
from tornado.httpserver import HTTPServer
from tornado.web import Application

from slack_server_mock.actor.actor import Actor
from slack_server_mock.servers.websocket import handler
from slack_server_mock.settings.settings import Settings

LOGGER = logging.getLogger(__name__)


@singleton
class SlackWebSocketServer():
    """ Mock Implementation of the Slack WebSocket server """
    @inject
    def __init__(self, settings: Settings, actor: Actor) -> None:
        self._port = settings.slack_server.websocket_port
        self._actor = actor
        ws_app = Application(
            [
                (r"/link", handler.SlackWebSocketHandler),
            ]
        )
        self._ws_server = HTTPServer(ws_app)

    def run(self):
        """ Start the HTTP Server """
        LOGGER.info("WebSocket server running on port %i", self._port)
        self._ws_server.listen(self._port)

    def stop(self):
        """ Stop the HTTP Server """
        self._ws_server.stop()
        LOGGER.info("WebSocket server shutdown")
