""" HTTP Server """
from injector import inject, singleton
from tornado.web import Application


from slack_server_mock.settings.settings import Settings
from slack_server_mock.servers.base_http_server import BaseHTTPServer


@singleton
class SlackHTTPServer(BaseHTTPServer):
    """ Mock Implementation of the Slack HTTP server """
    @inject
    def __init__(self, settings: Settings) -> None:
        from slack_server_mock.servers.http import handler  # pylint: disable=C0415

        app = Application(
            [
                (r"/auth.test", handler.AuthTestHandler),
                (r"/apps.connections.open", handler.AppsConnectionsOpenHandler),
                (r"/api.test", handler.ApiTestHandler),
                (r"/chat.postMessage", handler.ChatPostMessageHandler),
                (r"/chat.postEphemeral", handler.ChatPostEphemeralHandler),
                (r"/conversations.history", handler.ConversationsHistoryHandler),
                (r"/conversations.info", handler.ConversationsInfoHandler),
                (r"/conversations.join", handler.ConversationsJoinHandler),
                (r"/conversations.list", handler.ConversationsListHandler),
                (r"/conversations.replies", handler.ConversationsRepliesHandler),
                (r"/users.info", handler.UsersInfoHandler),
            ]
        )
        super().__init__(app, settings.slack_server.http_port)
