from threading import Thread
import time

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.web import WebClient


bot_token = "xapp-A111-222-xyz"
app_token = "xoxb-api_test"


class EchoSlackBot():  # pylint:disable=R0903
    """ Slackbot application backend """

    def __init__(self, base_url="http://localhost:8888") -> None:
        self._client = WebClient(token=bot_token, base_url=base_url)
        self._handler = SocketModeHandler(App(client=self._client), app_token)
        self._handler.app.message()(self._got_message)

    def run(self, block=False):
        """ Start the Slackbot backend application """
        if block:
            self._handler.start()
        else:
            self._handler.connect()

    def _got_message(self, message, say):
        print("Got message {}".format(message['text']))
        say(message['text'])

    def is_connected(self) -> bool:
        return self._handler.client.is_connected()

    def stop(self):
        self._handler.close()


if __name__ == "__main__":
    EchoSlackBot().run(block=True)
