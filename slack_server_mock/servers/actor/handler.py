""" Handlers for the Actor HTTP Server """
from tornado.web import RequestHandler
from tornado.websocket import WebSocketClosedError

from slack_server_mock.actor.actor import Actor
from slack_server_mock.injector.di import global_injector
from slack_server_mock.servers.base_http_handlers import load_json_from_body


class MessageHandler(RequestHandler):  # pylint: disable=W0223
    """ Handler for the message endpoint """
    async def post(self):
        """ Handle post command """
        data = load_json_from_body(self)
        if not data:
            return

        msg = data.get('message')
        if msg is None:
            self.set_status(400)
            self.write({"error": "JSON does not have a message key"})
            return

        try:
            response = await global_injector.get(Actor).send_message(msg)
        except WebSocketClosedError:
            self.set_status(400)
            self.write({"error": "The application is not connected"})
            return

        self.write({"answer": response[0], "ephemeral": response[1]})


class ConnectedHandler(RequestHandler):  # pylint: disable=W0223
    """ Handler for the connected endpoint """
    def get(self):
        """ Handle get command """
        self.write({"connected": global_injector.get(Actor).is_app_connected()})
