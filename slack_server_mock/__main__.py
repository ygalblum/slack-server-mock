""" Application """
import tornado

from slack_server_mock.servers.http.server import start_http_server, stop_http_server
from slack_server_mock.servers.websocket.server import start_websocket_server, stop_websocket_server


start_websocket_server()
start_http_server()
try:
    tornado.ioloop.IOLoop.current().start()
except KeyboardInterrupt:
    print("Shutting down")
finally:
    stop_http_server()
    stop_websocket_server()
