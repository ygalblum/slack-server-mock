""" Application """
import asyncio

from slack_server_mock.servers.http.server import start_http_server, stop_http_server
from slack_server_mock.servers.websocket.server import start_websocket_server


loop = asyncio.new_event_loop()
websocket_server_task = loop.create_task(start_websocket_server())    
loop.run_in_executor(None, start_http_server)
try:
    loop.run_forever()
except KeyboardInterrupt:
    print("Shutting down servers")
finally:
    print("Canceling websockettask")
    websocket_server_task.cancel()
    print("Waiting for WebSocket server to stop")
    loop.run_until_complete(websocket_server_task)
    stop_http_server()
    print("Closing loop")
    loop.close()
    print("Done")
# global_injector.get(Server).run()
