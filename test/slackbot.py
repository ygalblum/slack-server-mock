from threading import Thread
import time

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.web import WebClient


bot_token="xapp-A111-222-xyz"
app_token="xoxb-api_test"


class KnowledgeBaseSlackBot():  # pylint:disable=R0903
    """ Slackbot application backend """

    def __init__(self) -> None:
        self._client = WebClient(token=bot_token, base_url="http://localhost:8888")
        self._handler = SocketModeHandler(App(client=self._client), app_token)
        self._handler.app.message()(self._got_message)

    def run(self):
        """ Start the Slackbot backend application """
        self._handler.start()

    def _got_message(self, message, say):
        print("Got message {}".format(message['text']))
        say("Hello right back at ya")


if __name__ == "__main__":
    bot = KnowledgeBaseSlackBot()
    t = Thread(target=bot.run)
    t.start()
    while not bot._handler.client.is_connected():
        time.sleep(1)
    # bot._handler.client.send_message("hello")
    t.join()
