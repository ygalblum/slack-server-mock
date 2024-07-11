""" Slack Actor """
import datetime
import json
from typing import List, Tuple

from injector import inject, singleton
from tornado.locks import Event
from tornado import util
from tornado.websocket import WebSocketHandler, WebSocketClosedError


@singleton
class Actor():
    """ Slack Actor to send messages and log response """
    @inject
    def __init__(self) -> None:
        self._websocket = None
        self._event = Event()
        self._response = None
        self._ephemeral_messages = []

    def app_connected(self, websocket: WebSocketHandler):
        """ Notify the actor that the application connected """
        self._websocket = websocket

    def app_disconnected(self):
        """ Notify the actor that the application connected """
        self._websocket = None

    def is_app_connected(self):
        """ Check if the application is connected """
        return self._websocket is not None

    async def _wait_for_response(self, timeout: float) -> Tuple[str, List[str]]:
        if timeout < 0:
            return

        try:
            await self._event.wait(
                timeout=(None if timeout == 0 else datetime.timedelta(seconds=timeout))
            )
        except util.TimeoutError:
            # In case of timeout make sure to return ephemeral_messages that were accumulated
            pass

        response = self._response or ""
        self._response = None
        ephemeral_messages = self._ephemeral_messages
        self._ephemeral_messages = []
        return response, ephemeral_messages

    async def send_message(self, msg: str, timeout: float = 300.0) -> Tuple[str, List[str]]:
        """ Send a message to the application """
        if not self.is_app_connected():
            raise WebSocketClosedError()

        self._websocket.write_message(self._wrap_message_with_envelope(msg))

        return await self._wait_for_response(timeout=timeout)

    def message_received(self, msg: str):
        """ Notify the actor that a message was received """
        self._response = msg
        self._event.set()
        self._event.clear()

    def ephemeral_received(self, msg: str):
        """ Notify the actor that an ephemeral message was received """
        self._ephemeral_messages.append(msg)

    @staticmethod
    def _wrap_message_with_envelope(msg: str):
        return json.dumps(
            {
                "envelope_id": "ac2cfd40-6f8c-4d5e-a1ad-646e532baa19",
                "payload": {
                    "token": "verification-token",
                    "team_id": "T111",
                    "api_app_id": "A111",
                    "event": {
                        "client_msg_id": "f0582a78-72db-4feb-b2f3-1e47d66365c8",
                        "type": "message",
                        "text": msg,
                        "user": "U222",
                        "ts": "1610241741.000200",
                        "team": "T111",
                        "channel": "C111",
                        "event_ts": "1610241741.000200",
                        "channel_type": "channel"
                    },
                    "type": "event_callback",
                    "event_id": "Ev111",
                    "event_time": 1610241741,
                    "authorizations": [
                        {
                            "enterprise_id": None,
                            "team_id": "T111",
                            "user_id": "U333",
                            "is_bot": True,
                            "is_enterprise_install": False
                        }
                    ],
                    "is_ext_shared_channel": False,
                    "event_context": "1-message-T111-C111"
                },
                "type": "events_api",
                "accepts_response_payload": False,
                "retry_attempt": 0,
                "retry_reason": ""
            }
        )
