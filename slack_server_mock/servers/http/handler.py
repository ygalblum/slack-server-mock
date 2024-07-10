""" HTTP Handler """
from datetime import datetime
import re

from tornado.web import RequestHandler

from slack_server_mock.actor.actor import Actor
from slack_server_mock.injector.di import global_injector
from slack_server_mock.slack_server.slack_server import SlackServer
from slack_server_mock.servers.base_http_handlers import load_json_from_body
from slack_server_mock.settings.settings import Settings


class BaseSlackHandler(RequestHandler):  # pylint: disable=W0223
    """ Base class for all Slack HTTP Handlers """
    pattern_for_language = re.compile("python/(\\S+)", re.IGNORECASE)
    pattern_for_package_identifier = re.compile("slackclient/(\\S+)")

    _invalid_auth = {
        "ok": False,
        "error": "invalid_auth",
    }

    def _is_valid_user_agent(self):
        user_agent = self.request.headers["User-Agent"]
        return self.pattern_for_language.search(user_agent) and self.pattern_for_package_identifier.search(user_agent)

    def _is_valid_token(self):
        if self.request.path.startswith("oauth"):
            return True
        auth = self.request.headers.get("Authorization")
        return auth and (str(auth).startswith("Bearer xoxb-") or str(auth).startswith("Bearer xapp-"))

    def _validate_request(self, func):
        def wrapper(*args, **kwargs):
            if self._is_valid_token() and self._is_valid_user_agent():
                self.set_header("content-type", "application/json;charset=utf-8")
                self.set_header("connection", "close")
                func(*args, **kwargs)
            else:
                self.write(self._invalid_auth)
        return wrapper

    def _is_request_valid(self) -> bool:
        if self._is_valid_token() and self._is_valid_user_agent():
            self.set_header("content-type", "application/json;charset=utf-8")
            self.set_header("connection", "close")
            return True
        self.write(self._invalid_auth)
        return False


class AuthTestHandler(BaseSlackHandler):  # pylint: disable=W0223
    """ Handler for auth.test endpoint"""

    def post(self):
        """ Handle post request """
        if self._is_request_valid():
            self.write(
                {
                    "ok": True,
                    "url": "https://xyz.slack.com/",
                    "team": "Testing Workspace",
                    "user": "bot-user",
                    "team_id": "T111",
                    "user_id": "W11",
                    "bot_id": "B111",
                    "enterprise_id": "E111",
                    "is_enterprise_install": False,
                }
            )


class AppsConnectionsOpenHandler(BaseSlackHandler):  # pylint: disable=W0223
    """ Handler for apps.connection.open endpoint """

    def post(self):
        """ Handle post request """
        if self._is_request_valid():
            port = global_injector.get(Settings).slack_server.websocket_port
            self.write(
                {
                    "ok": True,
                    "url": f"ws://{self.request.host_name}:{port}/link",
                }
            )


class ApiTestHandler(BaseSlackHandler):  # pylint: disable=W0223
    """ Handler for api.test endpoint """

    def post(self):
        """ Handle post request """
        if self._is_request_valid():
            data = load_json_from_body(self)
            if not data:
                return
            self.write({"ok": True, "args": data})


class ChatPostMessageHandler(BaseSlackHandler):  # pylint: disable=W0223
    """ Handler for chat.postMessage endpoint """

    def post(self):
        """ Handle post request """
        if self._is_request_valid():
            data = load_json_from_body(self)
            if not data:
                return

            global_injector.get(Actor).message_received(data['text'])
            ts = datetime.timestamp(datetime.now())
            self.write(
                {
                    "ok": True,
                    "channel": data['channel'],
                    "ts": ts,
                    "message": {
                        "text": data['text'],
                        "type": "message",
                        "ts": ts
                    }
                }
            )


class ConversationsListHandler(BaseSlackHandler):  # pylint: disable=W0223
    """ Handler for conversations.list endpoint """
    def _handle(self):
        self.write(
            {
                "ok": True,
                "channels": global_injector.get(SlackServer).channels
            }
        )

    def get(self):
        """ Handle GET request """
        self._handle()

    def post(self):
        """ Handle POST request.
            While the documentation states that this is a GET command, the SDK calls PUT
        """
        self._handle()


class ConversationsJoinHandler(BaseSlackHandler):  # pylint: disable=W0223
    """ Handler for conversations.join endpoint """
    def post(self):
        """ Handle POST request """
        if not self._is_request_valid():
            return

        arg = self.request.body.decode("utf-8").split('=')
        if not (len(arg) == 2 and arg[0] == "channel"):
            self.set_status(400)
            self.write({"error": "Invalid argument"})
            return

        channels = [
            channel for channel in global_injector.get(SlackServer).channels if channel['id'] == arg[1]
        ]
        if len(channels) == 0:
            self.write({"ok": False, "error": "channel_not_found"})
        else:
            self.write({"ok": True, "channel": channels[0]})
