""" Slack Mock Server """
import json
import logging
import pathlib

from injector import inject, singleton

from slack_server_mock.injector.di import global_injector
from slack_server_mock.settings.settings import Settings
from slack_server_mock.servers.http.server import SlackHTTPServer
from slack_server_mock.servers.websocket.server import SlackWebSocketServer

LOGGER = logging.getLogger(__name__)


@singleton
class SlackServer():
    """ Class to hold and manage all Slack server related objects and operations """
    @inject
    def __init__(
        self,
        settings: Settings,
        http_server: SlackHTTPServer,
        websocket_server: SlackWebSocketServer
    ) -> None:
        self._http_server = http_server
        self._websocket_server = websocket_server
        self._channels = self._load_channels(settings.slack_server.channels_path)
        self._response_data = self._load_response_data(pathlib.Path(settings.slack_server.response_data_path))

    @property
    def channels(self):
        """ Return the channels list """
        return self._channels

    @property
    def response_data(self):
        """ Return the mock response data """
        return self._response_data

    def start(self):
        """ Start the Slack server """
        self._websocket_server.run()
        self._http_server.run()

    def stop(self):
        """ Stop the Slack server """
        self._http_server.stop()
        self._websocket_server.stop()

    @staticmethod
    def _load_channels(path: str):
        channels = []
        if path:
            path = pathlib.Path(path)
            if path.exists():
                with path.open("r", encoding="utf-8") as f:
                    channels = json.load(f)
        if not isinstance(channels, list):
            raise ValueError("The content of the channels file is not a JSON array")
        return channels

    @staticmethod
    def _load_response_data(path: pathlib.Path):
        response_data = {}
        if path:
            path = pathlib.Path(path)
            if path.exists():
                for file in path.glob("**/*.json"):
                    endpoint = str(file.parent).split('/', maxsplit=10)[-1]
                    if endpoint not in response_data:
                        response_data[endpoint] = {}
                    with file.open("r", encoding="utf-8") as f:
                        response_data[endpoint][file.stem] = json.load(f)
                    LOGGER.info('Loaded Endpoint %s: %s', endpoint, file.stem)
        return response_data


def start_slack_server():
    """ Start the Slack server """
    global_injector.get(SlackServer).start()


def stop_slack_server():
    """ Stop the Slack server """
    global_injector.get(SlackServer).stop()
