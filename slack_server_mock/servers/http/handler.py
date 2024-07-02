""" HTTP Handler """
from datetime import datetime
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler
import json
import logging
import re
from urllib.parse import urlparse, parse_qs

from slack_server_mock.actor.actor import Actor
from slack_server_mock.injector.di import global_injector
from slack_server_mock.settings.settings import Settings


class SlackHTTPHandler(SimpleHTTPRequestHandler):
    """ Mock Implementation of the handler for the Slack HTTP server """
    protocol_version = "HTTP/1.1"
    default_request_version = "HTTP/1.1"
    logger = logging.getLogger(__name__)

    pattern_for_language = re.compile("python/(\\S+)", re.IGNORECASE)
    pattern_for_package_identifier = re.compile("slackclient/(\\S+)")

    def _is_valid_user_agent(self):
        user_agent = self.headers["User-Agent"]
        return self.pattern_for_language.search(user_agent) and self.pattern_for_package_identifier.search(user_agent)

    def _is_valid_token(self):
        if self.path.startswith("oauth"):
            return True
        return "Authorization" in self.headers and (
            str(self.headers["Authorization"]).startswith("Bearer xoxb-")
            or str(self.headers["Authorization"]).startswith("Bearer xapp-")
        )

    def _set_common_headers(self):
        self.send_header("content-type", "application/json;charset=utf-8")
        self.send_header("connection", "close")
        self.end_headers()

    _invalid_auth = {
        "ok": False,
        "error": "invalid_auth",
    }

    _not_found = {
        "ok": False,
        "error": "test_data_not_found",
    }

    def _parse_request_body(self):
        content_len = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_len)
        request_body = None
        if post_body:
            try:
                post_body = post_body.decode("utf-8")
                if post_body.startswith("{"):
                    request_body = json.loads(post_body)
                else:
                    request_body = {k: v[0] for k, v in parse_qs(post_body).items()}
            except UnicodeDecodeError:
                pass
        else:
            parsed_path = urlparse(self.path)
            if parsed_path and parsed_path.query:
                request_body = {k: v[0] for k, v in parse_qs(parsed_path.query).items()}
        return request_body

    def _handle_authorized_request(self):
        request_body = self._parse_request_body()
        match self.path:
            case "/auth.test":
                body = {
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
            case "/apps.connections.open":
                port = global_injector.get(Settings).websocket_server.port
                body = {
                    "ok": True,
                    "url": f"ws://0.0.0.0:{port}/link",
                }
            case "/api.test":
                if request_body:
                    body = {"ok": True, "args": request_body}
            case "/chat.postMessage":
                global_injector.get(Actor).message_received(request_body['text'])
                ts = datetime.timestamp(datetime.now())
                body = {
                    "ok": True,
                    "channel": request_body['channel'],
                    "ts": ts,
                    "message": {
                        "text": request_body['text'],
                        "type": "message",
                        "ts": ts
                    }
                }
            case _:
                body = self._not_found
        return body

    def _handle(self):
        try:
            if self._is_valid_token() and self._is_valid_user_agent():
                body = self._handle_authorized_request()
            else:
                body = self._invalid_auth
            self.send_response(HTTPStatus.OK)
            self._set_common_headers()
            self.wfile.write(json.dumps(body).encode("utf-8"))
        except Exception as e:
            self.logger.error(str(e), exc_info=True)
            raise

    def do_GET(self):
        """ Handle GET requests """
        self._handle()

    def do_POST(self):  # pylint:disable=C0103
        """ Handle POST requests """
        self._handle()
