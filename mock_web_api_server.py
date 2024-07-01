import asyncio
import json
import logging
import re
import threading
import time
from http import HTTPStatus
from http.server import HTTPServer, SimpleHTTPRequestHandler
from typing import Type
from unittest import TestCase
from urllib.parse import urlparse, parse_qs
from urllib.request import Request, urlopen
from aiohttp import WSMsgType, web
import sys
import websockets
from datetime import datetime


socket_mode_envelopes = [
    """{"envelope_id":"ac2cfd40-6f8c-4d5e-a1ad-646e532baa19","payload":{"token":"verification-token","team_id":"T111","api_app_id":"A111","event":{"client_msg_id":"f0582a78-72db-4feb-b2f3-1e47d66365c8","type":"message","text":"<@U111> Hi here!","user":"U222","ts":"1610241741.000200","team":"T111","channel":"C111","event_ts":"1610241741.000200","channel_type":"channel"},"type":"event_callback","event_id":"Ev111","event_time":1610241741,"authorizations":[{"enterprise_id":null,"team_id":"T111","user_id":"U333","is_bot":true,"is_enterprise_install":false}],"is_ext_shared_channel":false,"event_context":"1-message-T111-C111"},"type":"events_api","accepts_response_payload":false,"retry_attempt":0,"retry_reason":""}""",
]


class MockHandler(SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    default_request_version = "HTTP/1.1"
    logger = logging.getLogger(__name__)

    pattern_for_language = re.compile("python/(\\S+)", re.IGNORECASE)
    pattern_for_package_identifier = re.compile("slackclient/(\\S+)")

    def is_valid_user_agent(self):
        user_agent = self.headers["User-Agent"]
        return self.pattern_for_language.search(user_agent) and self.pattern_for_package_identifier.search(user_agent)

    def is_valid_token(self):
        if self.path.startswith("oauth"):
            return True
        return "Authorization" in self.headers and (
            str(self.headers["Authorization"]).startswith("Bearer xoxb-")
            or str(self.headers["Authorization"]).startswith("Bearer xapp-")
        )

    def set_common_headers(self):
        self.send_header("content-type", "application/json;charset=utf-8")
        self.send_header("connection", "close")
        self.end_headers()

    invalid_auth = {
        "ok": False,
        "error": "invalid_auth",
    }

    not_found = {
        "ok": False,
        "error": "test_data_not_found",
    }

    def _handle(self):
        try:
            if self.is_valid_token() and self.is_valid_user_agent():
                parsed_path = urlparse(self.path)

                len_header = self.headers.get("Content-Length") or 0
                content_len = int(len_header)
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
                    if parsed_path and parsed_path.query:
                        request_body = {k: v[0] for k, v in parse_qs(parsed_path.query).items()}

                body = {"ok": False, "error": "internal_error"}
                if self.path == "/auth.test":
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
                if self.path == "/apps.connections.open":
                    body = {
                        "ok": True,
                        "url": "ws://0.0.0.0:3001/link",
                    }
                if self.path == "/api.test" and request_body:
                    body = {"ok": True, "args": request_body}
                if self.path == "/chat.postMessage":
                    print(f"Got response")
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
            else:
                body = self.invalid_auth

            if not body:
                body = self.not_found

            self.send_response(HTTPStatus.OK)
            self.set_common_headers()
            self.wfile.write(json.dumps(body).encode("utf-8"))
            self.wfile.close()

        except Exception as e:
            self.logger.error(str(e), exc_info=True)
            raise

    def do_GET(self):
        self._handle()

    def do_POST(self):
        self._handle()

    def do_CONNECT(self):
        self.wfile.write("HTTP/1.1 200 Connection established\r\n\r\n".encode("utf-8"))
        self.wfile.close()

class MockServerThread(threading.Thread):

    def run(self):
        self.server = HTTPServer(("localhost", 8888), MockHandler)
        try:
            self.server.serve_forever()
        finally:
            self.server.server_close()

    def stop(self):
        self.server.shutdown()
        self.join()

def start_http_server():
    server_address = ('', 8888)
    httpd = HTTPServer(server_address, MockHandler)
    print("HTTP server running on port 8888")
    httpd.serve_forever()
    print("HTTPD server saying goodbye")


async def websocket_handler(websocket, path):
    print(f"New connection from {websocket.remote_address}")
    await websocket.send(socket_mode_envelopes[0])
    try:
        async for message in websocket:
            print(f"Received message: {message}")
            # await websocket.send(socket_mode_envelopes[0])
            # print("Done sending")
    except websockets.ConnectionClosed as e:
        print(f"Connection closed: {e}")


async def start_websocket_server():
    async with websockets.serve(websocket_handler, 'localhost', 3001):
        try:
            await asyncio.Future()  # run forever
        except asyncio.exceptions.CancelledError:
            print("Websocket server saying goodbye")

httpd = None
def start_http_server():
    global httpd
    server_address = ('', 8888)
    httpd = HTTPServer(server_address, MockHandler)
    print("HTTP server running on port 8888")
    httpd.serve_forever()
    print("HTTPD server saying goodbye")

def main():
    loop = asyncio.new_event_loop()
    websocket_server_task = loop.create_task(start_websocket_server())    

    f = loop.run_in_executor(None, start_http_server)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Shutting down servers")
    finally:
        print("Canceling websockettask")
        websocket_server_task.cancel()
        print("Waiting for WebSocket server to stop")
        loop.run_until_complete(websocket_server_task)
        httpd.shutdown()
        print("Closing loop")
        loop.close()
        print("Done")


if __name__ == "__main__":
    main()
