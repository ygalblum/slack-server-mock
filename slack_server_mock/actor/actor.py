""" Slack Actor """
import asyncio
import json

from injector import inject, singleton
from websockets.server import WebSocketServerProtocol

from slack_server_mock.settings.settings import Settings


@singleton
class Actor():
    """ Slack Actor to send messages and log response """
    @inject
    def __init__(self, settings: Settings) -> None:
        self._conversation = self._load_inputs(settings.actor.input_file)
        self._output = settings.actor.output_file
        self._counter = 0
        self._websocket = None

    async def app_connected(self, websocket: WebSocketServerProtocol):
        """ Notify the actor that the application connected """
        self._websocket =  websocket
        await self._websocket.send(self._wrap_message_with_envelope(self._conversation[0]['question']))

    def message_received(self, msg: str):
        """ Notify the actor that the application sent a message """
        if self._websocket is None:
            return
        if self._counter >= len(self._conversation):
            return
        self._conversation[self._counter]['answer'] = msg
        self._counter += 1
        if self._counter < len(self._conversation):
            self._send_response()
        else:
            self._dump_conversation()

    def _send_response(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._do_send_response())
        loop.close()

    async def _do_send_response(self):
        await self._websocket.send(self._wrap_message_with_envelope(self._conversation[self._counter]['question']))

    def _dump_conversation(self):
        with open(self._output, "+w", encoding="utf-8") as f:
            json.dump(self._conversation, f)

    @staticmethod
    def _load_inputs(path: str):
        with open(path, "r", encoding="utf-8") as f:
            questions = json.load(f)
        return [{"question": q} for q in questions]

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
