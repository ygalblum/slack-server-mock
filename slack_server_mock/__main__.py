""" Application """
import tornado

from slack_server_mock.servers.actor.server import start_actor_server, stop_actor_server
from slack_server_mock.servers.http.server import start_http_server, stop_http_server
from slack_server_mock.servers.websocket.server import start_websocket_server, stop_websocket_server


start_websocket_server()
start_http_server()
start_actor_server()
try:
    tornado.ioloop.IOLoop.current().start()
except KeyboardInterrupt:
    print("Shutting down")
finally:
    stop_actor_server()
    stop_http_server()
    stop_websocket_server()
