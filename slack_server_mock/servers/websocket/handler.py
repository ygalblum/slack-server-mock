from tornado.websocket import WebSocketHandler

from slack_server_mock.actor.actor import Actor
from slack_server_mock.injector.di import global_injector


# Define WebSocket handler
class SlackWebSocketHandler(WebSocketHandler):
    def open(self):
        print("WebSocket opened")
        global_injector.get(Actor).app_connected(self)

    def on_message(self, message):
        print("Received message:", message)

    def on_close(self):
        print("WebSocket closed")
