import asyncio

from injector import inject, singleton
import websockets

from slack_server_mock.injector.di import global_injector
from slack_server_mock.settings.settings import Settings


@singleton
class SlackWebSocketServer():
    @inject
    def __init__(self, settings: Settings) -> None:
        self._port = settings.websocket_server.port

    @staticmethod
    async def websocket_handler(websocket, path):
        print(f"New connection from {websocket.remote_address}")
        # await websocket.send(socket_mode_envelopes[0])
        try:
            async for message in websocket:
                print(f"Received message: {message}")
        except websockets.ConnectionClosed as e:
            print(f"Connection closed: {e}")


    async def start_websocket_server(self):
        async with websockets.serve(self.websocket_handler, 'localhost', self._port):
            try:
                await asyncio.Future()  # run forever
            except asyncio.exceptions.CancelledError:
                print("Websocket server saying goodbye")


async def start_websocket_server():
    await global_injector.get(SlackWebSocketServer).start_websocket_server()
