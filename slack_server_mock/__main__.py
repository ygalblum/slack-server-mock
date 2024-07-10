""" Application """
import tornado

from slack_server_mock.servers.actor.server import start_actor_server, stop_actor_server
from slack_server_mock.slack_server.slack_server import start_slack_server, stop_slack_server


start_slack_server()
start_actor_server()
try:
    tornado.ioloop.IOLoop.current().start()
except KeyboardInterrupt:
    print("Shutting down")
finally:
    stop_actor_server()
    stop_slack_server()
