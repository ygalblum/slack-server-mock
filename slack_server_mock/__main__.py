""" Application """
import logging
import os

import tornado

from slack_server_mock.servers.actor.server import start_actor_server, stop_actor_server
from slack_server_mock.slack_server.slack_server import start_slack_server, stop_slack_server

LOGGER = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.DEBUG if os.environ.get('DEBUG') else logging.INFO,
    format='%(asctime)s - %(name)42s - %(levelname)7s - %(message)s')
start_slack_server()
start_actor_server()
try:
    tornado.ioloop.IOLoop.current().start()
except KeyboardInterrupt:
    LOGGER.info("Shutting down")
finally:
    stop_actor_server()
    stop_slack_server()
