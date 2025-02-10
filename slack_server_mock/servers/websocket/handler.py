import logging

from tornado.websocket import WebSocketHandler

from slack_server_mock.actor.actor import Actor
from slack_server_mock.injector.di import global_injector

LOGGER = logging.getLogger(__name__)


# Define WebSocket handler
class SlackWebSocketHandler(WebSocketHandler):
    def open(self):
        LOGGER.info("WebSocket opened")
        global_injector.get(Actor).app_connected(self)

    def on_message(self, message):
        LOGGER.info("Received message:", message)

    def on_close(self):
        LOGGER.info("WebSocket closed")
        global_injector.get(Actor).app_disconnected()
