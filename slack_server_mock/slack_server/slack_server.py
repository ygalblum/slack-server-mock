""" Slack Mock Server """
from injector import inject, singleton

from slack_server_mock.injector.di import global_injector
from slack_server_mock.servers.http.server import SlackHTTPServer
from slack_server_mock.servers.websocket.server import SlackWebSocketServer


@singleton
class SlackServer():
    """ Class to hold and manage all Slack server related objects and operations """
    @inject
    def __init__(self, http_server: SlackHTTPServer, websocket_server: SlackWebSocketServer) -> None:
        self._http_server = http_server
        self._websocket_server = websocket_server

    def start(self):
        """ Start the Slack server """
        self._websocket_server.run()
        self._http_server.run()

    def stop(self):
        """ Stop the Slack server """
        self._http_server.stop()
        self._websocket_server.stop()


def start_slack_server():
    """ Start the Slack server """
    global_injector.get(SlackServer).start()


def stop_slack_server():
    """ Stop the Slack server """
    global_injector.get(SlackServer).stop()
