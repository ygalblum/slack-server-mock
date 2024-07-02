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


class Actor(BaseModel):
    input_file: str = Field(
        "./input.json",
        description="Input file containing message to send to the application"
    )
    output_file: str = Field(
        "./output.json",
        description="Output file to store the messages received from the application"
    )


class Settings(BaseModel):
    http_server: HttpServer
    websocket_server: WebSocketServer
    actor: Actor

# This is visible just for DI or testing purposes.
# Use dependency injection or `settings()` method instead.
unsafe_settings = load_active_settings()

# This is visible just for DI or testing purposes.
# Use dependency injection or `settings()` method instead.
unsafe_typed_settings = Settings(**unsafe_settings)
