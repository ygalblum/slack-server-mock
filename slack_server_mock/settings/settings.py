""" Settings for the application """
from typing import Literal

from pydantic import BaseModel, Field

from slack_server_mock.settings.settings_loader import load_active_settings


class HttpServer(BaseModel):
    port: int = Field(
        8888,
        description="HTTP Server Listening port"
    )


class WebSocketServer(BaseModel):
    port: int = Field(
        3001,
        description="HTTP Server Listening port"
    )


class Settings(BaseModel):
    http_server: HttpServer
    websocket_server: WebSocketServer

# This is visible just for DI or testing purposes.
# Use dependency injection or `settings()` method instead.
unsafe_settings = load_active_settings()

# This is visible just for DI or testing purposes.
# Use dependency injection or `settings()` method instead.
unsafe_typed_settings = Settings(**unsafe_settings)
