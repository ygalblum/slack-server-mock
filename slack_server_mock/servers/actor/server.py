""" Actor HTTP Server """
from injector import inject, singleton
from tornado.web import Application


from slack_server_mock.injector.di import global_injector
from slack_server_mock.settings.settings import Settings
from slack_server_mock.servers.base_http_server import BaseHTTPServer
from slack_server_mock.servers.actor import handler


@singleton
class ActorHTTPServer(BaseHTTPServer):
    """ Mock Implementation of the Slack HTTP server """
    @inject
    def __init__(self, settings: Settings) -> None:
        app = Application(
            [
                (r"/connected", handler.ConnectedHandler),
                (r"/message", handler.MessageHandler),
            ]
        )
        super().__init__(app, settings.actor.port)


def start_actor_server():
    """ Static method for starting the HTTP Server """
    global_injector.get(ActorHTTPServer).run()


def stop_actor_server():
    """ Static method for stopping the HTTP Server """
    global_injector.get(ActorHTTPServer).stop()
